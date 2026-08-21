# -*- coding: utf-8 -*-
"""
Dump the plain text (with hyperlinks + heading levels) of ONE tab of a TrueProfit
blog Google Doc - the tab named in the URL's `tab=` parameter.

WHY THIS EXISTS: the Drive reader (read_file_content) concatenates *every tab* of
a doc into one text blob, so sibling tabs (an "n8n flow" draft, "Insights &
outline" notes, etc.) look like trailing scratch inside the article. They are not
- they are separate tabs. This script reads the ONE tab you point it at and
nothing else, so link/FAQ/benchmark analysis never sees another tab's content.

Output is compact Markdown-ish text:
  - headings as #/##/###/#### by level
  - list items prefixed with "- "
  - links rendered inline as [anchor](url) so external-reference checks see URLs
  - a "[cta]" marker is preserved verbatim

Usage:
    python dump_tab.py --doc <DOC_URL_OR_ID> [--tab t.xxxx] [--out path.md]

If --tab is omitted it is taken from the --doc URL's `tab=` parameter; if neither
is present it falls back to the first tab (and says so). Auth mirrors
review_structure.py (GOOGLE_TOKEN_JSON -> token.json -> credentials.json OAuth).
"""
import argparse
import re
import sys

from review_structure import (
    get_service, doc_id_from, heading_level, DEFAULT_CREDS, DEFAULT_TOKEN,
)


def tab_id_from_url(value):
    """Pull the tab id out of a Google Docs URL (?tab=t.xxx or #tab=t.xxx)."""
    m = re.search(r"[?&#]tab=(t\.[A-Za-z0-9]+)", value or "")
    return m.group(1) if m else None


def _iter_tabs(document):
    """Yield (tab_id, title, body_content) for every tab, depth-first."""
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
    """Return (tab_id, title, body_content) for the requested tab.

    Matches the given tab_id; if not found (or None), returns the first tab and
    reports the fallback so the caller can warn.
    """
    all_tabs = list(_iter_tabs(document))
    if tab_id:
        for tid, title, body in all_tabs:
            if tid == tab_id:
                return tid, title, body, False
    first = all_tabs[0]
    return first[0], first[1], first[2], bool(tab_id)  # fell_back if a tab_id was asked for


def render_para(para):
    level = heading_level(para)
    is_list = para.get("bullet") is not None
    parts = []
    for pe in para.get("elements", []):
        if "textRun" in pe:
            tr = pe["textRun"]
            txt = tr.get("content", "")
            link = (tr.get("textStyle", {}) or {}).get("link", {}) or {}
            url = link.get("url")
            if url and txt.strip():
                # keep trailing whitespace/newline outside the link
                stripped = txt.strip("\n")
                trailing = txt[len(txt.rstrip("\n")):]
                parts.append("[%s](%s)%s" % (stripped, url, trailing))
            else:
                parts.append(txt)
        elif "inlineObjectElement" in pe:
            parts.append("{image}")
    text = "".join(parts).rstrip("\n")
    if not text.strip():
        return ""
    if level:
        return "#" * level + " " + text
    if is_list:
        return "- " + text
    return text


def main():
    ap = argparse.ArgumentParser(description="Dump one tab of a blog Google Doc as text.")
    ap.add_argument("--doc", required=True, help="Google Doc ID or URL (URL may carry ?tab=t.xxx)")
    ap.add_argument("--tab", help="Tab id (t.xxxx). Defaults to the --doc URL's tab= param, else first tab.")
    ap.add_argument("--out", help="Write to this file instead of stdout.")
    ap.add_argument("--creds", default=DEFAULT_CREDS)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    args = ap.parse_args()

    tab_id = args.tab or tab_id_from_url(args.doc)
    did = doc_id_from(args.doc)
    service = get_service(args.creds, args.token)
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()

    tid, title, body, fell_back = select_tab(document, tab_id)

    header = [
        "# DOC: %s" % document.get("title", "(untitled)"),
        "# TAB: %s%s" % (title or "(untitled tab)", (" [%s]" % tid) if tid else ""),
    ]
    if fell_back:
        header.append("# WARNING: requested tab %r not found; fell back to first tab." % tab_id)
    header.append("")

    lines = []
    prev_blank = False
    for el in body:
        para = el.get("paragraph")
        if not para:
            if el.get("table"):
                lines.append("{table}")
            continue
        line = render_para(para)
        if not line:
            if not prev_blank:
                lines.append("")
            prev_blank = True
            continue
        lines.append(line)
        prev_blank = False

    out = "\n".join(header + lines).rstrip() + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print("Wrote %d chars for tab '%s' to %s" % (len(out), title or tid or "first", args.out))
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
