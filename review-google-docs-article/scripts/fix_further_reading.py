"""Normalize every "Further Reading" block in ONE tab of a Google Doc so the label
stands alone and each link has its own line (bullets are optional):

    Further Reading: [Link A]          Further Reading:
    [Link B]                    ->         Link A
                                           Link B

Dry-run by default (lists blocks that need fixing); --apply edits the Doc.
Links, anchor text and text styles are preserved; only line breaks, separator
characters between links, and bullets change.
"""
import argparse
import re
import sys

from review_structure import get_service, doc_id_from, DEFAULT_CREDS, DEFAULT_TOKEN
from dump_tab import tab_id_from_url, select_tab

LABEL = re.compile(r"^\s*further reading\b(\s*:)?", re.I)
SEPARATOR = re.compile(r"^[\s,;|/\-–—•]*$")
BULLET_PRESET = "BULLET_DISC_CIRCLE_SQUARE"
MAX_PASSES = 60


def all_tabs(tabs):
    for t in tabs or []:
        yield t
        yield from all_tabs(t.get("childTabs"))


def chars(para):
    """[(doc_index, char, url_or_None)] for a paragraph's text runs."""
    out = []
    for pe in para.get("elements", []):
        tr = pe.get("textRun")
        if not tr:
            continue
        url = ((tr.get("textStyle") or {}).get("link") or {}).get("url")
        for i, ch in enumerate(tr.get("content", "")):
            out.append((pe["startIndex"] + i, ch, url))
    return out


def text_of(cs):
    return "".join(c for _, c, _ in cs)


def link_segments(cs):
    """Contiguous same-URL link spans, trimmed of whitespace: [(start, end)]."""
    segs, cur = [], None
    for idx, ch, url in cs:
        if url and (cur is None or cur[2] != url):
            if cur:
                segs.append(cur)
            cur = [idx, idx + 1, url]
        elif url:
            cur[1] = idx + 1
        elif cur:
            segs.append(cur)
            cur = None
    if cur:
        segs.append(cur)
    by_idx = {idx: ch for idx, ch, _ in cs}
    trimmed = []
    for s, e, _ in segs:
        while s < e and by_idx[s].isspace():
            s += 1
        while e > s and by_idx[e - 1].isspace():
            e -= 1
        if s < e:
            trimmed.append((s, e))
    return trimmed


def is_link_only(para):
    if para.get("paragraphStyle", {}).get("namedStyleType", "").startswith("HEADING"):
        return False
    cs = chars(para)
    if not any(u for _, _, u in cs):
        return False
    return bool(SEPARATOR.match("".join(c for _, c, u in cs if not u)))


def find_fix(body, tid):
    """(description, requests) for the first block needing a fix, else None."""
    return next(iter_fixes(body, tid), None)


def iter_fixes(body, tid):
    """Yield (description, requests) for each block's next needed fix step."""
    paras = [el for el in body if "paragraph" in el]
    for i, el in enumerate(paras):
        p = el["paragraph"]
        cs = chars(p)
        m = LABEL.match(text_of(cs))
        if not m:
            continue
        label_txt = text_of(cs).strip().split("\n")[0][:80]

        if p.get("bullet"):
            yield ("un-bullet label: %r" % label_txt,
                    [{"deleteParagraphBullets": {"range": {
                        "startIndex": el["startIndex"], "endIndex": el["endIndex"] - 1, "tabId": tid}}}])
            continue

        segs = link_segments(cs)
        if segs:  # links sit on the label line -> split them onto their own lines
            reqs = []
            label_end = cs[0][0] + m.end()
            bounds = [label_end] + [e for _, e in segs[:-1]]
            for (s, _), gap_start in reversed(list(zip(segs, bounds))):
                if s > gap_start:
                    reqs.append({"deleteContentRange": {"range": {
                        "startIndex": gap_start, "endIndex": s, "tabId": tid}}})
                reqs.append({"insertText": {"location": {"index": gap_start, "tabId": tid}, "text": "\n"}})
            if not m.group(1):
                reqs.append({"insertText": {"location": {"index": label_end, "tabId": tid}, "text": ":"}})
            yield ("split %d inline link(s) off label: %r" % (len(segs), label_txt), reqs)
            continue

        if not m.group(1):
            yield ("add colon to label: %r" % label_txt,
                    [{"insertText": {"location": {"index": cs[0][0] + m.end(), "tabId": tid}, "text": ":"}}])
            continue

        items = []
        for nxt in paras[i + 1:]:
            if not is_link_only(nxt["paragraph"]):
                break
            items.append(nxt)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--doc", required=True, help="Google Doc URL (with ?tab=t.xxx) or ID")
    ap.add_argument("--tab", help="Tab id; defaults to the URL's tab= param, otherwise Final")
    ap.add_argument("--apply", action="store_true", help="Write the fixes (default: dry-run)")
    ap.add_argument("--creds", default=DEFAULT_CREDS)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    did = doc_id_from(args.doc)
    want = args.tab or tab_id_from_url(args.doc)
    if not args.tab and want == "t.0":
        want = None  # ordinary outline links do not override the article default
    s = get_service(args.creds, args.token)

    def load():
        doc = s.documents().get(documentId=did, includeTabsContent=True).execute()
        tid, _title, _body, _fallback = select_tab(doc, want)
        tab = next(t for t in all_tabs(doc.get("tabs")) if t["tabProperties"]["tabId"] == tid)
        return doc, tab, False

    doc, tab, fell_back = load()
    tid = tab["tabProperties"]["tabId"]
    print("Document : %s" % doc.get("title"))
    print("Tab      : %s [%s]" % (tab["tabProperties"].get("title"), tid))
    if fell_back:
        print("WARNING: tab %r not found; fell back to first tab." % want)

    if not args.apply:
        fixes = list(iter_fixes(tab["documentTab"]["body"]["content"], tid))
        for desc, _ in fixes:
            print("  NEEDS FIX  " + desc)
        print("Further Reading blocks needing a fix: %d" % len(fixes))
        if fixes:
            print("\n--dry-run (default): nothing written. Re-run with --apply to fix.")
        return 0

    applied = 0
    for _ in range(MAX_PASSES):
        fix = find_fix(tab["documentTab"]["body"]["content"], tid)
        if not fix:
            break
        s.documents().batchUpdate(documentId=did, body={"requests": fix[1]}).execute()
        print("  FIXED  " + fix[0])
        applied += 1
        doc, tab, _ = load()
    else:
        print("WARNING: stopped after %d passes; re-run to check." % MAX_PASSES)
    print("APPLIED %d fix(es)." % applied)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
