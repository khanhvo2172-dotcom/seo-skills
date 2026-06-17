# -*- coding: utf-8 -*-
"""
Add TrueProfit CMS "highlight triggers" to the TRANSLATED tabs (Spanish / German
/ French) of a blog Google Doc, mirroring the already-triggered English tab.

Precondition: run the English-only `trueprofit-blog-triggers` skill first so tab 1
(English) already has its Image / Content Highlight triggers. This skill treats
that English tab as the source of truth for image URLs, then re-detects each
language tab in its own language and inserts the matching triggers.

What it does, end to end:
  1. Authenticates to the Google Docs API (same auth as the English skill).
  2. Reads the doc WITH all tab content, locates the English tab and the three
     language tabs (by tab title; positional fallback).
  3. Reads the English tab's existing "Image (sentence note): <url>, Alt is <alt>"
     lines -> the ordered list of image URLs (+ English alts) shared across langs.
  4. For each language tab:
       - builds image triggers ABOVE each image using the English URL (same CDN
         file) and the TRANSLATED alt (from --alts, see below),
       - re-detects formulas (localized word + "=" on next line) and callouts
         (localized Pro tip / Note table) -> Content Highlight labels,
       - reports whether Quick Recap / FAQ exist (localized; flag-only),
       - applies via batchUpdate (unless --dry-run) and forces every trigger line
         to plain body text.

Translated alts: image alt text is editorial, so it is supplied by the caller
(the agent) rather than guessed in code. Two ways:
  --alts alts.json   where alts.json = {"es": [...], "de": [...], "fr": [...]},
                     one alt per image in document order.
If a language has no entry (or fewer than the image count), this falls back to
the English alt for the missing ones and prints a note.

Discover what to translate with:  python gdocs_ml_triggers.py --doc <DOC> --dump-en

Usage:
    python gdocs_ml_triggers.py --doc <DOC> --dump-en
    python gdocs_ml_triggers.py --doc <DOC> --alts alts.json --dry-run
    python gdocs_ml_triggers.py --doc <DOC> --alts alts.json
    python gdocs_ml_triggers.py --doc <DOC> --lang es --alts alts.json
    python gdocs_ml_triggers.py --doc <DOC> --reset --dry-run

Setup (one time): see ../references/setup-google-api.md
"""
import argparse
import json
import os
import sys

from detect_ml import (
    detect,
    plan_repairs,
    plan_ch,
    parse_existing_triggers,
    LANG_TERMS,
    _clean,
    RE_CONTENT_HIGHLIGHT,
    RE_EXISTING_IMAGE_TRIGGER,
)
from place_ml import english_image_anchors, plan_placements

SCOPES = ["https://www.googleapis.com/auth/documents"]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CREDS = os.path.join(HERE, "credentials.json")
DEFAULT_TOKEN = os.path.join(HERE, "token.json")

LANGS = ["es", "de", "fr"]

# How to recognise each tab by its title. First match wins; falls back to
# position (tab 0 = en, 1 = es, 2 = de, 3 = fr) only when no title matches.
# Use FULL language names only - bare 2-letter codes are unsafe as substrings
# (e.g. "en" hides inside "frENch", "de" inside ... ), which would mis-map tabs.
TAB_TITLE_HINTS = {
    "en": ["english"],
    "es": ["spanish", "español", "espanol", "español"],
    "de": ["german", "deutsch"],
    "fr": ["french", "français", "francais", "français"],
}
POSITIONAL = {0: "en", 1: "es", 2: "de", 3: "fr"}


def doc_id_from(value):
    if "/d/" in value:
        value = value.split("/d/", 1)[1].split("/")[0]
    return value.strip()


def get_service(creds_path, token_path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit(
            "Missing Google libraries. Install them first:\n"
            "  pip install -r requirements.txt\n"
            "(see ../references/setup-google-api.md)"
        )

    creds = None
    token_env = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_env:
        creds = Credentials.from_authorized_user_info(json.loads(token_env), SCOPES)
    elif os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_env = os.environ.get("GOOGLE_CLIENT_SECRET_JSON")
            if client_env:
                flow = InstalledAppFlow.from_client_config(json.loads(client_env), SCOPES)
            elif os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            else:
                sys.exit(
                    "No Google credentials found. Provide one of:\n"
                    "  - GOOGLE_TOKEN_JSON env var (authorized-user token), or\n"
                    "  - a token.json file next to this script, or\n"
                    "  - GOOGLE_CLIENT_SECRET_JSON / credentials.json for first-time OAuth.\n"
                    "See references/setup-google-api.md."
                )
            creds = flow.run_local_server(port=0)
        try:
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        except OSError:
            pass
    return build("docs", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Tab handling
# ---------------------------------------------------------------------------
def iter_tabs(document):
    """
    Yield (title, tab_id, content) for every tab, flattening one level of nested
    child tabs. Order follows the document's tab order.
    """
    def emit(tab):
        props = tab.get("tabProperties", {})
        tab_id = props.get("tabId")
        title = props.get("title", "")
        body = tab.get("documentTab", {}).get("body", {})
        yield (title, tab_id, body.get("content", []))
        for child in tab.get("childTabs", []) or []:
            for item in emit(child):
                yield item

    tabs = document.get("tabs")
    if tabs:
        for tab in tabs:
            for item in emit(tab):
                yield item
    else:
        # Legacy single-body doc - no tabs at all.
        yield ("(single tab)", None, document.get("body", {}).get("content", []))


def resolve_tabs(document):
    """
    Return {lang: (title, tab_id, content)} for en/es/de/fr.

    Match by title hint first; for any language still unmatched, fall back to the
    positional default (tab 0=en, 1=es, 2=de, 3=fr). A language stays absent if
    neither resolves.
    """
    tabs = list(iter_tabs(document))
    found = {}
    used_ids = set()

    for lang, hints in TAB_TITLE_HINTS.items():
        for title, tab_id, content in tabs:
            if tab_id in used_ids:
                continue
            low = (title or "").lower()
            if any(h in low for h in hints):
                found[lang] = (title, tab_id, content)
                used_ids.add(tab_id)
                break

    for pos, lang in POSITIONAL.items():
        if lang in found:
            continue
        if pos < len(tabs):
            title, tab_id, content = tabs[pos]
            if tab_id not in used_ids:
                found[lang] = (title, tab_id, content)
                used_ids.add(tab_id)
    return found


def _heading_level(para):
    """Return 1..6 for a HEADING_n paragraph style, else 0."""
    style = para.get("paragraphStyle", {}).get("namedStyleType", "")
    if style.startswith("HEADING_"):
        try:
            return int(style.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            return 0
    return 0


def flatten(content):
    blocks = []
    for el in content:
        para = el.get("paragraph")
        if not para:
            continue
        start = el.get("startIndex")
        end = el.get("endIndex")
        if start is None or end is None:
            continue
        text_parts = []
        has_image = False
        for pe in para.get("elements", []):
            if "textRun" in pe:
                text_parts.append(pe["textRun"].get("content", ""))
            if "inlineObjectElement" in pe:
                has_image = True
        text = "".join(text_parts)
        level = _heading_level(para)
        if has_image and not text.strip():
            blocks.append({"kind": "image", "text": "", "start": start, "end": end, "level": level})
        else:
            blocks.append({"kind": "text", "text": text, "start": start, "end": end, "level": level})
    return blocks


def english_image_triggers(blocks):
    """
    Pull the ordered (url, alt) pairs from the English tab's existing
    "Image (sentence note): <url>, Alt is <alt>" lines. This is the shared image
    list every language tab reuses (same CDN URL; alt gets translated).
    """
    out = []
    for b in blocks:
        t = _clean(b["text"])
        if not RE_EXISTING_IMAGE_TRIGGER.search(t):
            continue
        # t looks like: Image (sentence note): https://...webp, Alt is <alt>
        after_colon = t.split(":", 1)[1].strip() if ":" in t else t
        url = after_colon.split(",", 1)[0].strip()
        alt = ""
        marker = "Alt is"
        idx = t.find(marker)
        if idx != -1:
            alt = t[idx + len(marker):].strip()
        out.append((url, alt))
    return out


# ---------------------------------------------------------------------------
# Request building (per tab)
# ---------------------------------------------------------------------------
def build_requests(insertions, tab_id):
    from collections import OrderedDict

    grouped = OrderedDict()
    for ins in insertions:
        grouped.setdefault(ins["index"], []).append(ins["text"])

    reqs = []
    for index in sorted(grouped.keys(), reverse=True):
        location = {"index": index}
        if tab_id:
            location["tabId"] = tab_id
        reqs.append({"insertText": {"location": location, "text": "".join(grouped[index])}})
    return reqs


def build_repair_requests(ops, tab_id):
    """
    Turn repair / placement / delete ops into Docs requests.

    Each op has a "start" and is one of:
      - REPLACE : "end" > "start" AND "text"  -> delete [start,end), insert text at start
      - DELETE  : "end" > "start" AND no text -> delete [start,end)
      - INSERT  : no "end" (or end<=start), "text" -> insert text at start

    Pure INSERT ops that share the same start are MERGED, concatenating their text
    in document (list) order - otherwise the API would reverse them (each insert
    pushes the previous one right). Everything is applied DESCENDING by start so an
    earlier edit never shifts the index of one still to come; at an equal start a
    delete is emitted before an insert.
    """
    from collections import OrderedDict

    replaces, deletes = [], []
    merged_inserts = OrderedDict()  # start -> concatenated text, in document order
    for op in ops:
        has_range = op.get("end") is not None and op["end"] > op["start"]
        has_text = bool(op.get("text"))
        if has_range and has_text:
            replaces.append(op)
        elif has_range:
            deletes.append(op)
        elif has_text:
            merged_inserts[op["start"]] = merged_inserts.get(op["start"], "") + op["text"]

    # One action per position: (start, kind, payload). kind: 'del' | 'ins'
    actions = []
    for op in replaces:
        actions.append((op["start"], "del", (op["start"], op["end"])))
        actions.append((op["start"], "ins", op["text"]))
    for op in deletes:
        actions.append((op["start"], "del", (op["start"], op["end"])))
    for start, text in merged_inserts.items():
        actions.append((start, "ins", text))

    # Descending by start. At an equal start the DELETE must execute before the
    # INSERT (otherwise the delete eats the just-inserted text). Requests run in
    # array order, so with reverse=True we give 'del' the higher secondary key.
    actions.sort(key=lambda a: (a[0], 1 if a[1] == "del" else 0), reverse=True)

    reqs = []
    for start, kind, payload in actions:
        if kind == "del":
            s, e = payload
            rng = {"startIndex": s, "endIndex": e}
            if tab_id:
                rng["tabId"] = tab_id
            reqs.append({"deleteContentRange": {"range": rng}})
        else:
            loc = {"index": start}
            if tab_id:
                loc["tabId"] = tab_id
            reqs.append({"insertText": {"location": loc, "text": payload}})
    return reqs


def trigger_paragraphs(blocks):
    out = []
    for b in blocks:
        t = _clean(b["text"])
        if not t:
            continue
        if t.lower() == "content highlight" or RE_EXISTING_IMAGE_TRIGGER.search(t):
            out.append(b)
    return out


def _range(b, tab_id):
    rng = {"startIndex": b["start"], "endIndex": b["end"]}
    if tab_id:
        rng["tabId"] = tab_id
    return rng


def tab_content_by_id(document, tab_id):
    for _title, tid, content in iter_tabs(document):
        if tid == tab_id:
            return content
    return []


def normalize_styles(service, did, tab_id):
    """Force every trigger line in ONE tab to plain body text. Re-fetches first."""
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    content = tab_content_by_id(document, tab_id)
    targets = trigger_paragraphs(flatten(content))
    if not targets:
        return 0
    reqs = []
    for b in targets:
        reqs.append({
            "updateParagraphStyle": {
                "range": _range(b, tab_id),
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType",
            }
        })
        reqs.append({
            "updateTextStyle": {
                "range": _range(b, tab_id),
                "textStyle": {"bold": False, "italic": False, "underline": False},
                "fields": "bold,italic,underline",
            }
        })
    service.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
    return len(targets)


def reset_tab(service, did, blocks, tab_id, label, dry_run):
    targets = trigger_paragraphs(blocks)
    if not targets:
        print("  [%s] no existing triggers to remove." % label)
        return 0
    print("  [%s] trigger lines to remove (%d):" % (label, len(targets)))
    for b in targets:
        print("      @%-7d %s" % (b["start"], _clean(b["text"])[:80]))
    if dry_run:
        return 0
    reqs = [
        {"deleteContentRange": {"range": _range(b, tab_id)}}
        for b in sorted(targets, key=lambda x: x["start"], reverse=True)
    ]
    service.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
    print("      removed %d." % len(targets))
    return len(targets)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def load_alts(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for lang in LANGS:
        vals = data.get(lang) or []
        out[lang] = [str(v).strip() for v in vals]
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Mirror English-tab triggers into the ES/DE/FR tabs of a blog Google Doc."
    )
    ap.add_argument("--doc", required=True, help="Google Doc ID or URL")
    ap.add_argument("--alts", help="Path to alts.json = {\"es\":[...],\"de\":[...],\"fr\":[...]} (translated image alts, in document order)")
    ap.add_argument("--lang", action="append", choices=LANGS,
                    help="Limit to one or more languages (default: all three). Repeatable.")
    ap.add_argument("--dump-en", action="store_true",
                    help="Print the English tab's image list (URL + alt) and section presence, then exit. Use it to know what alts to translate.")
    ap.add_argument("--dry-run", action="store_true", help="Show the plan without editing the doc")
    ap.add_argument("--reset", action="store_true", help="Remove skill-added trigger lines from the language tabs")
    ap.add_argument("--creds", default=DEFAULT_CREDS, help="Path to OAuth client secrets json")
    ap.add_argument("--token", default=DEFAULT_TOKEN, help="Path to cached token json")
    args = ap.parse_args()

    langs = args.lang or LANGS
    did = doc_id_from(args.doc)
    service = get_service(args.creds, args.token)
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    title = document.get("title", "(untitled)")
    tabs = resolve_tabs(document)

    print("Document : %s" % title)
    print("All tabs  : %s" % " | ".join(
        (t or "(untitled)") for t, _id, _c in iter_tabs(document)) or "(none)")
    for lang in ["en"] + LANGS:
        if lang in tabs:
            print("  %s tab : %s" % (lang, tabs[lang][0] or "(untitled tab)"))
        else:
            print("  %s tab : NOT FOUND" % lang)
    print()

    if "en" not in tabs:
        sys.exit("Could not find an English tab - cannot read the shared image URLs.")
    en_blocks = flatten(tabs["en"][2])
    en_images = english_image_triggers(en_blocks)

    if args.dump_en:
        print("English image triggers (%d) - translate the alt for each language:" % len(en_images))
        for i, (url, alt) in enumerate(en_images, 1):
            print("  %2d. %s" % (i, url))
            print("      alt(en): %s" % (alt or "(empty)"))
        print()
        print("Build alts.json like:")
        print('  {"es": [%s], "de": [...], "fr": [...]}'
              % ", ".join('"..."' for _ in en_images))
        return 0

    # ---- Reset across language tabs ----
    if args.reset:
        total = 0
        for lang in langs:
            if lang not in tabs:
                print("  [%s] tab not found - skipped." % lang)
                continue
            _t, tab_id, content = tabs[lang]
            total += reset_tab(service, did, flatten(content), tab_id, lang, args.dry_run)
        print("\n%s%d trigger line(s) across %d tab(s)."
              % ("(dry-run) would remove " if args.dry_run else "Removed ", total, len(langs)))
        return 0

    alts = load_alts(args.alts)
    en_urls = [u for u, _a in en_images]
    en_alts = [a for _u, a in en_images]
    en_anchors = english_image_anchors(en_blocks)  # for placement mode
    if en_images and not alts and not args.dry_run:
        print("NOTE: no --alts given; image alts will copy the English alt. "
              "Pass --alts alts.json for translated alt text.\n")

    grand = {"img": 0, "ch": 0}
    for lang in langs:
        name = LANG_TERMS[lang]["name"]
        if lang not in tabs:
            print("== %s (%s): tab NOT FOUND - skipped ==\n" % (name, lang))
            continue
        _t, tab_id, content = tabs[lang]
        blocks = flatten(content)
        translated_alts = alts.get(lang, [])

        # Content Highlight handling (Option B): keep/normalize a carried-over CH
        # only when it is backed by real translated content; delete orphan CHs; and
        # add a CH above any genuinely-detected formula/callout that lacks one.
        rep = plan_repairs(blocks, en_urls, translated_alts, en_alts)
        chrep = plan_ch(blocks, lang)               # normalize backed + delete orphans
        add = detect(blocks, lang, image_map=None)  # add missing CH + QR/FAQ report
        ch_ops = list(chrep["ops"])
        ch_ops += [
            {"start": ins["index"], "text": ins["text"], "reason": "add missing " + ins["reason"]}
            for ins in add["insertions"]
        ]

        E, T = len(en_urls), rep["image_units"]
        placement = None
        if E > 0 and T != E:
            # OUT OF SYNC: carried-over image lines don't match English (stale tab).
            # Remove them and PLACE every English image by heading anchor instead.
            placement = plan_placements(blocks, en_anchors, translated_alts, en_alts)
            stale = [u for u in parse_existing_triggers(blocks) if u["kind"] == "image"]
            image_ops = [{"start": u["start"], "end": u["end"]} for u in stale] + placement["ops"]
            image_mode = "PLACE by heading (tab is out of sync: %d existing vs %d English)" % (T, E)
        else:
            # IN SYNC: repair the carried-over image lines by order.
            image_ops = [o for o in rep["ops"] if o["text"].lstrip().startswith("Image")]
            image_mode = "REPAIR by order"

        ops = image_ops + ch_ops

        print("== %s (%s) | tab: %s ==" % (name, lang, _t or tab_id))
        print("   paragraphs: %d | image trigger lines: %d (vs %d English) | Content Highlight lines: %d"
              % (len(blocks), T, E, rep["ch_units"]))
        print("   image mode : %s" % image_mode)
        print("   Content Highlight: keep %d backed, remove %d orphan(s), add %d detected"
              % (chrep["kept"], chrep["deleted"], len(add["insertions"])))
        print("   Quick Recap: %s | FAQ: %s" % (
            "present" if add["quick_recap_present"] else "MISSING (add manually)",
            "present" if add["faq_present"] else "MISSING (add manually)",
        ))
        if E > 0 and not translated_alts:
            print("   NOTE: no translated alts for %s; image alts copy the English alt." % lang)
        for note in rep["notes"] if placement is None else placement["notes"]:
            print("   - %s" % note)

        if placement is not None:
            print("   Image placement (review the heading each image lands under):")
            for r in placement["review"]:
                print("      #%-2d %-44s -> %s [%s]"
                      % (r["n"], r["url"].rsplit("/", 1)[-1], r["tr_heading"][:46], r["how"]))

        if not ops:
            print("   Nothing to repair, place or add (already canonical).\n")
            continue

        if args.dry_run:
            n_img = len(placement["ops"]) if placement is not None else len([o for o in image_ops if o.get("text")])
            print("   Planned: %d image change(s) + %d Content Highlight change(s). --dry-run: nothing written.\n"
                  % (n_img, len(ch_ops)))
            continue

        requests = build_repair_requests(ops, tab_id)
        service.documents().batchUpdate(documentId=did, body={"requests": requests}).execute()
        n = normalize_styles(service, did, tab_id)
        grand["img"] += placement["placed"] if placement is not None else rep["image_repaired"]
        grand["ch"] += len(ch_ops)
        print("   Applied %d change(s); normalized %d trigger line(s).\n" % (len(requests), n))

    if not args.dry_run:
        print("Done. Placed/repaired %d image trigger(s) and %d Content Highlight change(s) across the language tabs."
              % (grand["img"], grand["ch"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
