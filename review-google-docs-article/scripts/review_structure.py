# -*- coding: utf-8 -*-
"""
Structure review for a TrueProfit blog Google Doc (first tab) - Steps 2 & 3 of
the review-google-docs-article skill.

Reports, for the selected article tab (normally Final):
  - Quick Recap / FAQ presence.
  - Heading-2 count (Quick Recap excluded, FAQ counted).
  - CTA image: whether a "[cta]" marker qualifies (> 5 H2). If it does and a
    main-keyword slug is given, it PLANS the CTA image trigger; with --apply it
    inserts that line above the marker (the only in-place edit this script makes).
  - Further Reading placement warnings (2nd-5th H2). Report-only, never edited.

Default is a DRY RUN (report only). Pass --apply to write the CTA line.

Usage:
    python review_structure.py --doc <DOC_ID_OR_URL> [--cta-campaign <slug>] [--apply]

Auth and guarded transport use the shared gdocs.py helper. The signed-in
account needs edit access to apply changes.
"""
import argparse
import json
import os
import re
import sys

from detect_structure import detect, CTA_IMAGE_URL

SCOPES = ["https://www.googleapis.com/auth/documents"]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CREDS = os.path.join(HERE, "credentials.json")
DEFAULT_TOKEN = os.path.join(HERE, "token.json")


def doc_id_from(value):
    if "/d/" in value:
        value = value.split("/d/", 1)[1].split("/")[0]
    return value.strip()


def get_service(creds_path=None, token_path=None):
    """Compatibility arguments are ignored; authentication belongs to shared gdocs.py."""
    from shared_docs_service import SharedDocsService
    return SharedDocsService()


def tab_id_from_url(value):
    """Pull the tab id out of a Google Docs URL (?tab=t.xxx or #tab=t.xxx)."""
    m = re.search(r"[?&#]tab=(t\.[A-Za-z0-9]+)", value or "")
    return m.group(1) if m else None


def _iter_tabs(document):
    """Yield (tab_id, title, body_content) for every tab, depth-first (incl. child tabs)."""
    def walk(tab):
        props = tab.get("tabProperties", {})
        body = tab.get("documentTab", {}).get("body", {}).get("content", [])
        yield (props.get("tabId"), props.get("title", ""), body)
        for child in tab.get("childTabs", []) or []:
            yield from walk(child)

    tabs = document.get("tabs")
    if tabs:
        for tab in tabs:
            yield from walk(tab)
    else:  # legacy single-body doc
        yield (None, document.get("title", ""), document.get("body", {}).get("content", []))


def select_tab(document, tab_id):
    """Resolve an exact ID/title, preferring Final only without a selector."""
    tabs = list(_iter_tabs(document))
    if tab_id:
        matches = [t for t in tabs if t[0] == tab_id or t[1] == tab_id]
        if len(matches) != 1:
            raise ValueError("Requested tab is missing or ambiguous: %r" % tab_id)
        tid, title, body = matches[0]
    else:
        finals = [t for t in tabs if t[1].strip().lower() == "final"]
        if len(finals) > 1:
            raise ValueError("Final article tab is ambiguous.")
        tid, title, body = finals[0] if finals else tabs[0]
        if not finals and any(word in title.lower() for word in ("outline", "research", "notes")):
            raise ValueError("No article tab identified; name the intended source explicitly.")
    return tid, title, body, False


def first_tab(document):
    """(body_content, tab_id) for the first tab. Kept for callers that want tab 0."""
    tid, _title, body, _fb = select_tab(document, None)
    return body, tid


def heading_level(para):
    style = para.get("paragraphStyle", {}).get("namedStyleType", "") or ""
    m = re.match(r"^HEADING_(\d+)$", style)
    return int(m.group(1)) if m else 0


def flatten(content):
    """
    Turn body 'content' into ordered blocks:
        { kind, text, start, end, level, is_list }
    `is_list` is True when the paragraph is a bullet/numbered list item (the
    paragraph carries a `bullet` property) - the signal used to detect the items
    of a hyperlinked Further Reading list.
    """
    blocks = []
    for el in content:
        para = el.get("paragraph")
        if not para:
            continue
        start, end = el.get("startIndex"), el.get("endIndex")
        if start is None or end is None:
            continue
        level = heading_level(para)
        is_list = para.get("bullet") is not None
        text_parts, has_image = [], False
        for pe in para.get("elements", []):
            if "textRun" in pe:
                text_parts.append(pe["textRun"].get("content", ""))
            if "inlineObjectElement" in pe:
                has_image = True
        text = "".join(text_parts)
        if has_image:
            blocks.append({"kind": "image", "text": "", "start": start, "end": end,
                           "level": level, "is_list": is_list})
            if text.strip():
                blocks.append({"kind": "text", "text": text, "start": start, "end": end,
                               "level": level, "is_list": is_list})
        else:
            blocks.append({"kind": "text", "text": text, "start": start, "end": end,
                           "level": level, "is_list": is_list})
    return blocks


def _range(start, end, tab_id):
    rng = {"startIndex": start, "endIndex": end}
    if tab_id:
        rng["tabId"] = tab_id
    return rng


def normalize_cta_line(service, did, want_tab=None):
    """Force the inserted CTA line to plain body text (it inherits the marker's
    style otherwise). Re-fetch, find the CTA image trigger line, reset its style."""
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    tab_id, _title, content, _fb = select_tab(document, want_tab)
    reqs = []
    for b in flatten(content):
        if b["kind"] == "text" and CIMG_RE.search(b["text"] or ""):
            reqs.append({"updateParagraphStyle": {
                "range": _range(b["start"], b["end"], tab_id),
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType"}})
            reqs.append({"updateTextStyle": {
                "range": _range(b["start"], b["end"], tab_id),
                "textStyle": {"bold": False, "italic": False, "underline": False},
                "fields": "bold,italic,underline"}})
    if reqs:
        service.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
    return len(reqs) // 2


CIMG_RE = re.compile(r"^\s*Image\b[^:]*:\s*%s" % re.escape(CTA_IMAGE_URL), re.I)


def main():
    ap = argparse.ArgumentParser(description="Structure review for a blog Google Doc (first tab).")
    ap.add_argument("--doc", required=True, help="Google Doc ID or URL (URL may carry ?tab=t.xxx)")
    ap.add_argument("--tab", help="Tab id (t.xxxx). Defaults to the --doc URL's tab= param, otherwise Final (URL t.0 is treated as an outline link). Explicit selectors must resolve.")
    ap.add_argument("--cta-campaign", help="utm_campaign slug (article main keyword) for the CTA link")
    ap.add_argument("--apply", action="store_true", help="Insert the CTA line (default is a dry-run report)")
    ap.add_argument("--creds", default=DEFAULT_CREDS)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    args = ap.parse_args()

    campaign = (args.cta_campaign or "").strip().lower() or None
    if campaign and not re.match(r"^[a-z0-9-]+$", campaign):
        sys.exit("cta-campaign should be lowercase letters, numbers and hyphens only: %r" % campaign)

    did = doc_id_from(args.doc)
    want_tab = args.tab or tab_id_from_url(args.doc)
    if not args.tab and want_tab == "t.0":
        want_tab = None
    service = get_service(args.creds, args.token)
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    tab_id, tab_title, content, fell_back = select_tab(document, want_tab)
    blocks = flatten(content)
    title = document.get("title", "(untitled)")

    plan = detect(blocks, cta_campaign=campaign)

    print("Document : %s" % title)
    print("Tab      : %s%s" % (tab_title or "(single-tab doc)", (" [%s]" % tab_id) if tab_id else ""))
    if fell_back:
        print("  ! WARNING: tab %r not found in this doc; used the first tab instead." % want_tab)
    print("Quick Recap : %s" % ("present" if plan["quick_recap_present"] else "MISSING"))
    print("FAQ         : %s" % ("present" if plan["faq_present"] else "MISSING"))
    print("Heading 2s  : %d (Quick Recap excluded, FAQ counted)" % plan["h2_count"])
    if plan["cta_markers"]:
        print("CTA markers : %d found  |  %d CTA trigger(s) planned" % (plan["cta_markers"], plan["cta_added"]))
    print()

    if plan["warnings"]:
        print("Warnings:")
        for w in plan["warnings"]:
            print("  ! %s" % w)
        print()
    if plan["notes"]:
        print("Notes:")
        for n in plan["notes"]:
            print("  - %s" % n)
        print()

    if not plan["insertions"]:
        print("No CTA line to insert.")
        return 0

    print("Planned CTA insertion:")
    for ins in plan["insertions"]:
        print("  @%-7d %s" % (ins["index"], ins["reason"]))
        print("           %s" % ins["text"].strip())
    print()

    if not args.apply:
        print("--dry-run (default): nothing written. Re-run with --apply to insert.")
        return 0

    location = {"index": plan["insertions"][0]["index"]}
    if tab_id:
        location["tabId"] = tab_id
    service.documents().batchUpdate(documentId=did, body={"requests": [
        {"insertText": {"location": location, "text": plan["insertions"][0]["text"]}}
    ]}).execute()
    n = normalize_cta_line(service, did, want_tab)
    print("Applied CTA insertion to '%s' (normalized %d line to normal text)." % (title, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
