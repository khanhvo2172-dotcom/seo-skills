# -*- coding: utf-8 -*-
"""
Add TrueProfit CMS "highlight triggers" to a blog Google Doc (first tab only).

What it does, end to end:
  1. Authenticates to the Google Docs API (OAuth desktop flow, token cached).
  2. Reads the document WITH tab content and isolates the FIRST tab.
  3. Flattens that tab's paragraphs into ordered blocks (text + image markers).
  4. Runs the pure-logic detector (detect_triggers.detect) to plan insertions:
       - Content Highlight before a Formula line (heading "Formula" + next
         line containing "="), and before "Pro tip"/"Note:" callouts.
       - Image (sentence note) lines with auto-numbered be.trueprofit.io URLs.
  5. Reports whether Quick Recap and FAQ sections exist (it does NOT add them -
     per the workflow, those are flagged for you to handle manually).
  6. Applies the insertions via batchUpdate (unless --dry-run).

Usage:
    python gdocs_triggers.py --doc <DOC_ID_OR_URL> --base-slug <slug> [--dry-run]

Setup (one time): see ../references/setup-google-api.md
"""
import argparse
import json
import os
import re
import sys

from detect_triggers import (
    detect,
    _clean,
    RE_CONTENT_HIGHLIGHT,
    RE_EXISTING_IMAGE_TRIGGER,
)

SCOPES = ["https://www.googleapis.com/auth/documents"]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CREDS = os.path.join(HERE, "credentials.json")
DEFAULT_TOKEN = os.path.join(HERE, "token.json")


def doc_id_from(value):
    """Accept a bare ID or any Google Docs URL and return the document ID."""
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

    # Credentials can come from (in order): the GOOGLE_TOKEN_JSON env var, a
    # token.json file, or - first time only - an interactive OAuth flow using
    # GOOGLE_CLIENT_SECRET_JSON / credentials.json. The env-var path makes the
    # skill portable to a fresh session (e.g. Claude.ai) that has no local files:
    # paste your authorized-user token JSON into GOOGLE_TOKEN_JSON and go.
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
        # Best-effort cache so we don't refresh every run; ignore read-only FS.
        try:
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        except OSError:
            pass
    return build("docs", "v1", credentials=creds)


def first_tab(document):
    """
    Return (body_content, tab_id) for the first tab.

    The modern Docs API nests content under tabs[].documentTab.body. Older docs
    (or the API without tab support) expose body directly with no tab id.
    """
    tabs = document.get("tabs")
    if tabs:
        tab = tabs[0]
        tab_id = tab.get("tabProperties", {}).get("tabId")
        body = tab.get("documentTab", {}).get("body", {})
        return body.get("content", []), tab_id
    return document.get("body", {}).get("content", []), None


def flatten(content):
    """
    Turn a body 'content' list into ordered blocks the detector understands:
        { kind: 'text'|'image', text, start, end }
    Only top-level paragraphs are considered (tables/TOC are skipped - triggers
    never live inside those).
    """
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
        # A paragraph that holds an image and no meaningful text is an image block.
        if has_image and not text.strip():
            blocks.append({"kind": "image", "text": "", "start": start, "end": end})
        else:
            blocks.append({"kind": "text", "text": text, "start": start, "end": end})
    return blocks


def build_requests(insertions, tab_id):
    """
    Build insertText requests.

    Two rules keep the indices valid and the order correct:
      - MERGE insertions that share an index into a single request, concatenating
        their text in document order. Separate same-index inserts would be
        reversed by the API (each insert pushes the previous one right), which
        scrambles cases like an image trigger AND a Content Highlight both
        landing exactly where an image meets a callout.
      - Apply groups DESCENDING by index so an earlier insertion never shifts the
        index of one still to be applied.
    """
    from collections import OrderedDict

    grouped = OrderedDict()
    for ins in insertions:  # insertions arrive in document order
        grouped.setdefault(ins["index"], []).append(ins["text"])

    reqs = []
    for index in sorted(grouped.keys(), reverse=True):
        location = {"index": index}
        if tab_id:
            location["tabId"] = tab_id
        reqs.append({"insertText": {"location": location, "text": "".join(grouped[index])}})
    return reqs


def trigger_paragraphs(blocks):
    """
    The trigger LABEL lines this skill owns: a standalone "Content Highlight"
    paragraph, and any "Image (sentence note): http..." line. These are the lines
    we keep as plain text and the ones --reset removes.
    """
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


def normalize_styles(service, did):
    """
    Force every trigger line to plain body text. Inserted text inherits the style
    at the insertion point, so a Content Highlight dropped above a heading - or an
    image trigger next to styled content - can come out bold or heading-sized.
    Re-fetch (indices have shifted after inserts), find the trigger lines, and
    reset paragraph style to NORMAL_TEXT and clear bold/italic/underline.
    Returns the number of trigger lines normalized.
    """
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    content, tab_id = first_tab(document)
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


def reset_triggers(service, did, blocks, tab_id, dry_run):
    """
    Remove every trigger line this skill added (Content Highlight labels + Image
    trigger lines), so a fresh run re-creates them in the current style/position.
    """
    targets = trigger_paragraphs(blocks)
    if not targets:
        print("No existing triggers to remove.")
        return 0
    print("Trigger lines to remove (%d):" % len(targets))
    for b in targets:
        print("  @%-7d %s" % (b["start"], _clean(b["text"])[:80]))
    if dry_run:
        print("\n--dry-run: nothing removed.")
        return 0
    # Delete bottom-up so earlier deletions don't shift later ranges.
    reqs = [
        {"deleteContentRange": {"range": _range(b, tab_id)}}
        for b in sorted(targets, key=lambda x: x["start"], reverse=True)
    ]
    service.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
    print("\nRemoved %d trigger line(s)." % len(targets))
    return 0


def parse_image_list(path):
    """
    Parse an explicit image list: one image per non-empty line, formatted as
        <url><whitespace/tab><alt text>
    The URL is the first whitespace-delimited token; everything after it (trimmed)
    is the alt text. A line with only a URL gets an empty alt. Returns a list of
    (url, alt) tuples, in order, to map onto the document's images.
    """
    out = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            url = parts[0].strip()
            alt = parts[1].strip() if len(parts) > 1 else ""
            out.append((url, alt))
    return out


def main():
    ap = argparse.ArgumentParser(description="Add CMS triggers to a blog Google Doc (first tab).")
    ap.add_argument("--doc", required=True, help="Google Doc ID or URL")
    ap.add_argument("--base-slug", help='Auto-number image URLs from this slug, empty alt (mode A). Mutually exclusive with --image-list.')
    ap.add_argument("--image-list", help='Path to a file of "<url><tab><alt>" lines mapped to images in order (mode B). Mutually exclusive with --base-slug.')
    ap.add_argument("--dry-run", action="store_true", help="Show the plan without editing the doc")
    ap.add_argument("--reset", action="store_true", help="Remove all skill-added trigger lines (then re-run normally to re-create them)")
    ap.add_argument("--creds", default=DEFAULT_CREDS, help="Path to OAuth client secrets json")
    ap.add_argument("--token", default=DEFAULT_TOKEN, help="Path to cached token json")
    args = ap.parse_args()

    did = doc_id_from(args.doc)
    service = get_service(args.creds, args.token)
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    content, tab_id = first_tab(document)
    blocks = flatten(content)
    title = document.get("title", "(untitled)")

    if args.reset:
        print("Document : %s\nTab      : %s\n" % (title, tab_id or "(single-tab doc)"))
        return reset_triggers(service, did, blocks, tab_id, args.dry_run)

    # ---- Choose image mode: base-slug auto-number OR explicit url+alt list ----
    if args.base_slug and args.image_list:
        sys.exit("Use either --base-slug OR --image-list, not both.")
    if args.image_list:
        image_map = parse_image_list(args.image_list)
        if not image_map:
            sys.exit("Image list is empty: %s" % args.image_list)
        plan = detect(blocks, image_map=image_map)
    elif args.base_slug:
        base_slug = args.base_slug.strip().lower()
        if not re.match(r"^[a-z0-9-]+$", base_slug):
            sys.exit("base-slug should be lowercase letters, numbers and hyphens only: %r" % base_slug)
        plan = detect(blocks, base_slug=base_slug)
    else:
        sys.exit("Provide --base-slug or --image-list (or --reset).")

    # ---- Report -------------------------------------------------------------
    print("Document : %s" % title)
    print("Tab      : %s" % (tab_id or "(single-tab doc)"))
    print("Paragraphs scanned: %d  |  images found: %d" % (len(blocks), plan["image_count"]))
    print()

    print("Quick Recap : %s" % ("present" if plan["quick_recap_present"] else "MISSING - add it manually"))
    print("FAQ         : %s" % ("present" if plan["faq_present"] else "MISSING - add it manually"))
    print()

    if plan["notes"]:
        print("Notes:")
        for n in plan["notes"]:
            print("  - %s" % n)
        print()

    if not plan["insertions"]:
        print("No new triggers to add. (Content Highlight / Image triggers already present or none matched.)")
        return 0

    print("Planned insertions (%d):" % len(plan["insertions"]))
    for ins in sorted(plan["insertions"], key=lambda x: x["index"]):
        print("  @%-7d %s" % (ins["index"], ins["reason"]))
    print()

    if args.dry_run:
        print("--dry-run: nothing written.")
        return 0

    requests = build_requests(plan["insertions"], tab_id)
    service.documents().batchUpdate(documentId=did, body={"requests": requests}).execute()
    print("Applied %d insertion(s) to '%s'." % (len(requests), title))
    # Force all trigger lines (new + any pre-existing) to plain body text.
    n = normalize_styles(service, did)
    print("Normalized %d trigger line(s) to normal text." % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
