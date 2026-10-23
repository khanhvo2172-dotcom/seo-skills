"""Run the packaged Docs planners through Khanh's shared gdocs helper.

No credentials are loaded here. Legacy service-shaped calls are retained so the
pure detectors and request builders keep their established behavior.
"""
import copy
import importlib.util
from pathlib import Path

HELPER = Path("E:/.trueprofit-claude-codex/shared/tools/gdocs/gdocs.py")


def load_helper():
    if not HELPER.is_file():
        raise RuntimeError("Shared gdocs.py is unavailable; restore the shared helper, not a separate OAuth setup.")
    spec = importlib.util.spec_from_file_location("khanh_shared_gdocs", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Call:
    def __init__(self, action):
        self.action = action

    def execute(self):
        return self.action()


def tabs_by_id(doc):
    found = {}
    def visit(tabs):
        for tab in tabs:
            found[tab["tabProperties"]["tabId"]] = tab.get("documentTab", {})
            visit(tab.get("childTabs", []))
    visit(doc.get("tabs", []))
    return found


class SharedDocsService:
    def __init__(self, helper=None):
        self.helper = helper if helper is not None else load_helper()
        self.snapshots = {}

    def documents(self):
        return self

    def get(self, documentId, includeTabsContent=True):
        def read():
            doc = self.helper.read(documentId)
            self.snapshots[documentId] = copy.deepcopy(doc)
            return doc
        return Call(read)

    def batchUpdate(self, documentId, body):
        def apply():
            before = self.snapshots.get(documentId)
            if before is None or not before.get("revisionId"):
                raise RuntimeError("A fresh shared-helper read is required before writing.")
            requests = body.get("requests", [])
            if not requests:
                return {}
            before_tabs = tabs_by_id(before)
            touched = set()
            # These planners only edit existing text/styles in named tabs.
            allowed = {"insertText", "deleteContentRange", "updateTextStyle",
                       "updateParagraphStyle", "createParagraphBullets", "deleteParagraphBullets"}
            for request in requests:
                if len(request) != 1 or next(iter(request)) not in allowed:
                    raise RuntimeError("Unsupported planner request; use the shared helper directly.")
                operation = next(iter(request.values()))
                target = operation.get("range", operation.get("location", {}))
                tid = target.get("tabId")
                if before_tabs and tid not in before_tabs:
                    raise RuntimeError("Every request must name an existing target tab.")
                touched.add(tid)
            # A failed/uncertain write must never leave a reusable cached revision.
            self.snapshots.pop(documentId, None)
            result = self.helper.guarded_batch(documentId, before["revisionId"], requests)
            after = self.helper.read(documentId)
            # Docs returns the post-write revision in writeControl.requiredRevisionId.
            # https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate
            applied_revision = result.get("writeControl", {}).get("requiredRevisionId")
            if not applied_revision or after.get("revisionId") != applied_revision:
                raise RuntimeError("Write outcome or readback revision changed; inspect the Doc and replan before continuing.")
            after_tabs = tabs_by_id(after)
            if set(before_tabs) != set(after_tabs) or any(
                before_tabs[tid] != after_tabs[tid] for tid in before_tabs if tid not in touched
            ):
                self.snapshots.pop(documentId, None)
                raise RuntimeError("Readback found an unrelated tab change; inspect the live Doc before continuing.")
            self.snapshots[documentId] = copy.deepcopy(after)
            return result
        return Call(apply)
