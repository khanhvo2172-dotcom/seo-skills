"""Offline behavioral checks for shared Docs transport and article scope."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from shared_docs_service import SharedDocsService
from fix_further_reading import find_fix
from review_structure import select_tab


def tab(tid, title, text):
    return {"tabProperties": {"tabId": tid, "title": title},
            "documentTab": {"body": {"content": [{"paragraph": {"text": text}}]}}}


def fixture():
    return {"revisionId": "r1", "tabs": [tab("t.0", "Outline", "notes"),
            tab("t.final", "Final", "article")]}


class FakeHelper:
    def __init__(self):
        self.doc = fixture()
        self.writes = []
        self.unrelated_change = False

    def read(self, did):
        return copy.deepcopy(self.doc)

    def guarded_batch(self, did, revision, requests):
        if revision != self.doc["revisionId"]:
            raise RuntimeError("revision conflict")
        self.writes.append((did, revision, copy.deepcopy(requests)))
        self.doc["revisionId"] = "r" + str(int(revision[1:]) + 1)
        self.doc["tabs"][1]["documentTab"]["body"]["content"][0]["paragraph"]["text"] += requests[0]["insertText"]["text"]
        if self.unrelated_change:
            self.doc["tabs"][0]["documentTab"]["body"]["content"].append({"changed": True})
        return {"replies": [{}], "writeControl": {"requiredRevisionId": self.doc["revisionId"]}}


def insert(tid="t.final"):
    return {"requests": [{"insertText": {"location": {"index": 1, "tabId": tid}, "text": "new"}}]}


class SharedDocsTests(unittest.TestCase):
    def setUp(self):
        self.helper = FakeHelper()
        self.service = SharedDocsService(self.helper)

    def load(self):
        return self.service.documents().get(documentId="doc", includeTabsContent=True).execute()

    def apply(self, body=None):
        return self.service.documents().batchUpdate(documentId="doc", body=body or insert()).execute()

    def test_requires_read_and_explicit_target(self):
        with self.assertRaises(RuntimeError):
            self.apply()
        self.load()
        with self.assertRaises(RuntimeError):
            self.apply(insert(None))
        with self.assertRaises(RuntimeError):
            self.apply(insert("t.missing"))
        self.assertEqual(self.helper.writes, [])

    def test_guard_and_readback_preserve_other_tab(self):
        before = self.load()
        self.apply()
        self.assertEqual(self.helper.writes[0][1], "r1")
        self.assertEqual(before["tabs"][0], self.helper.doc["tabs"][0])
        self.apply()
        self.assertEqual(self.helper.writes[1][1], "r2")

    def test_concurrent_revision_stops_before_mutation(self):
        self.load()
        self.helper.doc["revisionId"] = "r2"
        with self.assertRaisesRegex(RuntimeError, "revision conflict"):
            self.apply()
        self.assertEqual(self.helper.writes, [])

    def test_unrelated_readback_change_requires_inspection(self):
        self.load()
        self.helper.unrelated_change = True
        with self.assertRaisesRegex(RuntimeError, "unrelated tab"):
            self.apply()
        self.assertNotIn("doc", self.service.snapshots)

    def test_rejects_out_of_scope_request(self):
        self.load()
        with self.assertRaises(RuntimeError):
            self.apply({"requests": [{"deleteTab": {"tabId": "t.0"}}]})
        self.assertEqual(self.helper.writes, [])

    def test_concurrent_touched_tab_after_write_stops_next_batch(self):
        self.load()
        original = self.helper.guarded_batch
        def race(*args):
            result = original(*args)
            self.helper.doc["revisionId"] = "r3"
            return result
        self.helper.guarded_batch = race
        with self.assertRaisesRegex(RuntimeError, "readback revision"):
            self.apply()
        with self.assertRaisesRegex(RuntimeError, "fresh shared-helper read"):
            self.apply()
        self.assertEqual(len(self.helper.writes), 1)

    def test_unknown_postwrite_revision_requires_replan(self):
        self.load()
        original = self.helper.guarded_batch
        def missing(*args):
            original(*args)
            return {"replies": [{}]}
        self.helper.guarded_batch = missing
        with self.assertRaisesRegex(RuntimeError, "outcome"):
            self.apply()
        self.assertNotIn("doc", self.service.snapshots)

    def test_all_owned_adapters_are_identical(self):
        root = HERE.parents[1]
        expected = (HERE / "shared_docs_service.py").read_bytes()
        for skill in ("trueprofit-blog-triggers", "trueprofit-blog-multilingual-tabs-triggers"):
            self.assertEqual(expected, (root / skill / "scripts" / "shared_docs_service.py").read_bytes())

    def test_final_default_and_missing_explicit_tab(self):
        self.assertEqual(select_tab(fixture(), None)[0], "t.final")
        self.assertEqual(select_tab(fixture(), "t.0")[0], "t.0")
        with self.assertRaises(ValueError):
            select_tab(fixture(), "t.missing")

    def test_plain_further_reading_stays_plain(self):
        body = []
        start = 1
        for text in ("Further Reading:\n", "https://trueprofit.io/blog/a\n", "https://trueprofit.io/blog/b\n"):
            body.append({"startIndex": start, "endIndex": start + len(text),
                         "paragraph": {"elements": [{"startIndex": start, "textRun": {"content": text}}]}})
            start += len(text)
        self.assertIsNone(find_fix(body, "t.final"))
        for element in body[1:]:
            element["paragraph"]["bullet"] = {"listId": "list"}
        self.assertIsNone(find_fix(body, "t.final"))

    def test_translated_source_prefers_final_over_outline(self):
        root = HERE.parents[1]
        folder = root / "trueprofit-blog-multilingual-tabs-triggers" / "scripts"
        sys.path.insert(0, str(folder))
        spec = importlib.util.spec_from_file_location("ml_under_test", folder / "gdocs_ml_triggers.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        doc = fixture()
        doc["tabs"].append(tab("t.es", "Spanish Version", "translated"))
        self.assertEqual(module.resolve_tabs(doc)["en"][1], "t.final")
        self.assertEqual(module.resolve_tabs(doc)["es"][1], "t.es")
        doc["tabs"][2]["tabProperties"]["title"] = "ES"
        doc["tabs"].extend([tab("t.de", "DE", "german"), tab("t.fr", "FR", "french")])
        resolved = module.resolve_tabs(doc)
        self.assertEqual({lang: value[1] for lang, value in resolved.items()},
                         {"en": "t.final", "es": "t.es", "de": "t.de", "fr": "t.fr"})
        doc["tabs"].append(tab("t.other", "Spanish Version", "duplicate"))
        with self.assertRaises(ValueError):
            module.resolve_tabs(doc)


if __name__ == "__main__":
    unittest.main()
