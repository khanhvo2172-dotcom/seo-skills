# -*- coding: utf-8 -*-
"""Offline regression checks: article-tab selection must scope every write."""
import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import gdocs_triggers as prep


def paragraph(text, start=1):
    return {"startIndex": start, "endIndex": start + len(text),
            "paragraph": {"elements": [{"textRun": {"content": text}}]}}


def tab(tid, title, text, children=None):
    return {"tabProperties": {"tabId": tid, "title": title},
            "documentTab": {"body": {"content": [paragraph(text)]}},
            "childTabs": children or []}


def fixture():
    return {"title": "Article", "tabs": [
        tab("t.draft", "Draft", "Note: draft must remain untouched\n"),
        tab("t.notes", "Notes", "Research\n", [
            tab("t.final", "Final", "Note: article callout\n")])
    ]}


class FakeDocs:
    def __init__(self, document):
        self.document = document
        self.writes = []

    def documents(self):
        return self

    def get(self, **kwargs):
        return self

    def batchUpdate(self, **kwargs):
        self.writes.extend(copy.deepcopy(kwargs["body"]["requests"]))
        return self

    def execute(self):
        return copy.deepcopy(self.document)


class TabSelectionTests(unittest.TestCase):
    def invoke(self, service, *args):
        with patch.object(prep, "get_service", return_value=service), \
             patch("sys.argv", ["gdocs_triggers.py", *args]), \
             redirect_stdout(io.StringIO()):
            return prep.main()

    def test_nested_final_selected_by_exact_title(self):
        body, tid = prep.select_tab(fixture(), tab_title="Final")
        self.assertEqual(tid, "t.final")
        self.assertIn("article callout", body[0]["paragraph"]["elements"][0]["textRun"]["content"])

    def test_query_and_fragment_selectors(self):
        self.assertEqual(prep.tab_id_from_url("https://docs.google.com/document/d/doc/edit?tab=t.final#heading=h.x"), "t.final")
        self.assertEqual(prep.tab_id_from_url("https://docs.google.com/document/d/doc/edit#tab=t.final"), "t.final")

    def test_missing_and_ambiguous_selectors_fail(self):
        with self.assertRaises(ValueError):
            prep.select_tab(fixture(), tab_id="t.missing")
        doc = fixture()
        doc["tabs"].append(tab("t.other", "Final", "Other\n"))
        with self.assertRaises(ValueError):
            prep.select_tab(doc, tab_title="Final")

    def test_legacy_body_only_without_selector(self):
        doc = {"body": {"content": [paragraph("Legacy\n")]}}
        self.assertEqual(prep.first_tab(doc), (doc["body"]["content"], None))
        with self.assertRaises(ValueError):
            prep.select_tab(doc, tab_id="t.final")

    def test_url_tab_scopes_insertions(self):
        service = FakeDocs(fixture())
        self.assertEqual(self.invoke(service, "--doc", "https://docs.google.com/document/d/doc/edit?tab=t.final", "--base-slug", "article"), 0)
        inserts = [r["insertText"] for r in service.writes if "insertText" in r]
        self.assertEqual(len(inserts), 1)
        self.assertEqual(inserts[0]["location"]["tabId"], "t.final")
        self.assertEqual(inserts[0]["text"], "Content Highlight\n")

    def test_explicit_title_overrides_url_and_dry_run_does_not_write(self):
        service = FakeDocs(fixture())
        self.invoke(service, "--doc", "https://docs.google.com/document/d/doc/edit?tab=t.missing", "--tab-title", "Final", "--base-slug", "article", "--dry-run")
        self.assertEqual(service.writes, [])

    def test_normal_outline_url_defaults_to_final(self):
        doc = fixture()
        doc["tabs"][0]["tabProperties"] = {"tabId": "t.0", "title": "Outline"}
        service = FakeDocs(doc)
        self.invoke(service, "--doc", "https://docs.google.com/document/d/doc/edit?tab=t.0", "--base-slug", "article")
        self.assertTrue(service.writes)
        self.assertTrue(all(next(iter(r.values()))["range" if "range" in next(iter(r.values())) else "location"]["tabId"] == "t.final" for r in service.writes))

    def test_explicit_outline_selector_remains_explicit(self):
        doc = fixture()
        doc["tabs"][0]["tabProperties"] = {"tabId": "t.0", "title": "Outline"}
        service = FakeDocs(doc)
        self.invoke(service, "--doc", "https://docs.google.com/document/d/doc/edit?tab=t.0", "--tab", "t.0", "--base-slug", "article")
        self.assertTrue(service.writes)
        self.assertTrue(all(next(iter(r.values()))["range" if "range" in next(iter(r.values())) else "location"]["tabId"] == "t.0" for r in service.writes))

    def test_missing_tab_exits_before_writes(self):
        service = FakeDocs(fixture())
        with self.assertRaises(SystemExit):
            self.invoke(service, "--doc", "https://docs.google.com/document/d/doc/edit?tab=t.missing", "--base-slug", "article")
        self.assertEqual(service.writes, [])

    def test_style_normalization_scoped_after_refetch(self):
        doc = fixture()
        doc["tabs"][0]["documentTab"]["body"]["content"] = [paragraph("Content Highlight\n")]
        doc["tabs"][1]["childTabs"][0]["documentTab"]["body"]["content"] = [paragraph("Content Highlight\n")]
        service = FakeDocs(doc)
        self.assertEqual(prep.normalize_styles(service, "doc", "t.final"), 1)
        self.assertEqual(len(service.writes), 2)
        for request in service.writes:
            self.assertEqual(next(iter(request.values()))["range"]["tabId"], "t.final")

    def test_reset_deletes_only_selected_tab_trigger(self):
        doc = fixture()
        doc["tabs"][0]["documentTab"]["body"]["content"] = [paragraph("Content Highlight\n")]
        doc["tabs"][1]["childTabs"][0]["documentTab"]["body"]["content"] = [paragraph("Content Highlight\n")]
        service = FakeDocs(doc)
        self.invoke(service, "--doc", "doc", "--tab-title", "Final", "--reset")
        self.assertEqual(len(service.writes), 1)
        self.assertEqual(service.writes[0]["deleteContentRange"]["range"]["tabId"], "t.final")


if __name__ == "__main__":
    unittest.main()
