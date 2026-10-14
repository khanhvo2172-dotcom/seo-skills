"""Find and strip AI-assistant tracking params (e.g. ?utm_source=chatgpt.com) from
links in ONE tab of a Google Doc. Dry-run by default; --apply edits the Doc.

Only a utm_source whose value names an AI tool is removed; every other query
param (including our own utm_source=trueprofit.io) is kept. Scans paragraphs and
table cells, and also deletes the param if it was pasted as visible text.
"""
import argparse
import re
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from review_structure import get_service, doc_id_from, DEFAULT_CREDS, DEFAULT_TOKEN
from dump_tab import tab_id_from_url

AI_TOKENS = r"chatgpt|openai|claude|anthropic|perplexity|gemini|bard|copilot|deepseek|grok|you\.com|phind|meta\.ai"
AI = re.compile(AI_TOKENS, re.I)
TEXT_PARAM = re.compile(r"[?&]utm_source=[^\s&)\]]*(?:%s)[^\s&)\]]*" % AI_TOKENS, re.I)


def clean_url(url):
    parts = urlsplit(url)
    if not parts.query:
        return url
    q = parse_qsl(parts.query, keep_blank_values=True)
    kept = [(k, v) for k, v in q if not (k.lower() == "utm_source" and AI.search(v))]
    if len(kept) == len(q):
        return url
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment))


def text_runs(content):
    for el in content:
        if "paragraph" in el:
            for pe in el["paragraph"].get("elements", []):
                if "textRun" in pe:
                    yield pe
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    yield from text_runs(cell.get("content", []))
        elif "tableOfContents" in el:
            yield from text_runs(el["tableOfContents"].get("content", []))


def all_tabs(tabs):
    for t in tabs or []:
        yield t
        yield from all_tabs(t.get("childTabs"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--doc", required=True, help="Google Doc URL (with ?tab=t.xxx) or ID")
    ap.add_argument("--tab", help="Tab id; defaults to the URL's tab= param, else first tab")
    ap.add_argument("--apply", action="store_true", help="Write the fixes (default: dry-run)")
    ap.add_argument("--creds", default=DEFAULT_CREDS)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    did = doc_id_from(args.doc)
    want = args.tab or tab_id_from_url(args.doc)
    s = get_service(args.creds, args.token)
    doc = s.documents().get(documentId=did, includeTabsContent=True).execute()
    tabs = list(all_tabs(doc.get("tabs")))
    tab = next((t for t in tabs if t["tabProperties"]["tabId"] == want), None)
    if tab is None:
        tab = tabs[0]
        print("WARNING: tab %r not found; fell back to first tab." % want)
    tid = tab["tabProperties"]["tabId"]
    body = tab["documentTab"]["body"]["content"]

    reqs, report = [], []
    for pe in text_runs(body):
        start, end = pe["startIndex"], pe["endIndex"]
        tr = pe["textRun"]
        text = tr.get("content", "")
        url = ((tr.get("textStyle") or {}).get("link") or {}).get("url")
        ops = []
        if url:
            new = clean_url(url)
            if new != url:
                ops.append({"updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end, "tabId": tid},
                    "textStyle": {"link": {"url": new}}, "fields": "link"}})
                if text.strip():
                    report.append("LINK  [%s]\n      %s\n   -> %s" % (text.strip()[:70], url, new))
        for m in reversed(list(TEXT_PARAM.finditer(text))):
            ops.append({"deleteContentRange": {"range": {
                "startIndex": start + m.start(), "endIndex": start + m.end(), "tabId": tid}}})
            report.append("TEXT  delete visible %r in %r" % (m.group(0), text.strip()[:70]))
        if ops:
            reqs.append((start, ops))

    print("Document : %s" % doc.get("title"))
    print("Tab      : %s [%s]" % (tab["tabProperties"].get("title"), tid))
    print("AI tracking params found: %d link run(s)/text hit(s)" % len(reqs))
    for r in report:
        print("  " + r)
    if not reqs:
        return 0
    if not args.apply:
        print("\n--dry-run (default): nothing written. Re-run with --apply to strip.")
        return 0
    # Descending index order so text deletions don't shift earlier ranges.
    flat = [op for _, ops in sorted(reqs, key=lambda x: -x[0]) for op in ops]
    s.documents().batchUpdate(documentId=did, body={"requests": flat}).execute()
    print("\nAPPLIED %d request(s)." % len(flat))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
