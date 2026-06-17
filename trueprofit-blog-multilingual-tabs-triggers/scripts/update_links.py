# -*- coding: utf-8 -*-
"""
Update internal links in Spanish/German/French tabs of a TrueProfit blog Google Doc.

Two link types are handled:

1. trueprofit.io blog links — https://trueprofit.io/blog/<slug> (no language prefix)
   If the slug is in MULTILINGUAL_SLUGS, replaces the URL with the localized version
   (/es/, /de/, /fr/). Links not in the list are left untouched.

2. Shopify app links — https://apps.shopify.com/trueprofit?...utm_campaign=<value>...
   Prefixes the utm_campaign value with the language code (es-, de-, fr-).
   Links where utm_campaign is already prefixed are left untouched.

Usage:
    python update_links.py --doc <DOC_ID_OR_URL> [--dry-run]
"""
import argparse
import json
import os
import re
import sys
import urllib.parse

SCOPES = ["https://www.googleapis.com/auth/documents"]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CREDS = os.path.join(HERE, "credentials.json")
DEFAULT_TOKEN = os.path.join(HERE, "token.json")

LANGUAGE_TABS = {
    "Spanish Version": "/es",
    "German Version": "/de",
    "French Version": "/fr",
}

LANG_CODE = {
    "Spanish Version": "es",
    "German Version": "de",
    "French Version": "fr",
}

MULTILINGUAL_SLUGS = {
    "high-profit-margin-small-businesses",
    "average-dropshipping-income",
    "trending-dropshipping-products",
    "dropshipping-products-on-shopify",
    "best-selling-products-on-shopify",
    "apparel-profit-margin",
    "how-much-can-you-make-from-shopify",
    "is-print-on-demand-profitable",
    "how-much-does-shopify-take-per-sale",
    "best-profit-and-loss-app",
    "how-much-does-it-cost-to-start-dropshipping",
    "dropshipping-success-rate",
    "what-is-a-good-gross-profit-margin",
    "what-is-a-good-net-profit-margin",
    "what-is-a-good-roas",
    "good-operating-profit-margin",
    "net-profit",
    "gross-profit",
    "shopify-fees-calculator",
    "net-profit-margin",
    "gross-profit-margin",
    "print-on-demand-pet-products",
    "high-profit-margin-products",
    "best-dropshipping-apps-for-shopify",
    "cost-of-goods-sold",
    "print-on-demand-products",
    "high-margin-print-on-demand-products",
    "profitable-niches-with-low-competition",
    "ecommerce-profit-margins",
}

# Matches trueprofit.io/blog/<slug> with no language prefix
RE_EN_BLOG = re.compile(
    r"^(https?://(?:www\.)?trueprofit\.io)/blog/([a-z0-9-]+)(/?)(\?.*)?$",
    re.IGNORECASE,
)

# Matches apps.shopify.com/trueprofit (with any query string)
RE_SHOPIFY_APP = re.compile(
    r"^https://apps\.shopify\.com/trueprofit\b",
    re.IGNORECASE,
)


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
        sys.exit("Missing Google libraries. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

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
                sys.exit("No Google credentials found. Provide token.json next to this script.")
            creds = flow.run_local_server(port=0)
        try:
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        except OSError:
            pass
    return build("docs", "v1", credentials=creds)


def collect_links(content):
    """
    Walk all structural elements (paragraphs + table cells) and return a list of
    dicts: { start, end, url } for every text run that carries a link URL.
    """
    links = []

    def walk(elements):
        for el in elements:
            if "paragraph" in el:
                for pe in el["paragraph"].get("elements", []):
                    if "textRun" in pe:
                        url = (
                            pe["textRun"]
                            .get("textStyle", {})
                            .get("link", {})
                            .get("url")
                        )
                        if url:
                            links.append({
                                "start": pe["startIndex"],
                                "end": pe["endIndex"],
                                "url": url,
                            })
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        walk(cell.get("content", []))

    walk(content)
    return links


def main():
    ap = argparse.ArgumentParser(description="Localize internal links in ES/DE/FR doc tabs.")
    ap.add_argument("--doc", required=True, help="Google Doc ID or URL")
    ap.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    ap.add_argument("--creds", default=DEFAULT_CREDS)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    args = ap.parse_args()

    did = doc_id_from(args.doc)
    service = get_service(args.creds, args.token)

    print("Fetching document …")
    document = service.documents().get(documentId=did, includeTabsContent=True).execute()
    tabs = document.get("tabs", [])
    print("Title : %s" % document.get("title", "(untitled)"))
    print("Tabs  : %d total" % len(tabs))

    all_requests = []
    totals = {}

    for tab in tabs:
        props = tab.get("tabProperties", {})
        tab_name = props.get("title", "")
        tab_id = props.get("tabId")
        lang_prefix = LANGUAGE_TABS.get(tab_name)
        if lang_prefix is None:
            continue

        content = tab.get("documentTab", {}).get("body", {}).get("content", [])
        links = collect_links(content)

        lang_code = LANG_CODE[tab_name]  # "es", "de", "fr"
        updated_blog = 0
        updated_shopify = 0
        skipped_no_list = 0
        skipped_already_localized = 0

        print("\n--- %s (tabId=%s) ---" % (tab_name, tab_id))

        for lnk in links:
            url = lnk["url"]

            # ── Shopify app links ──────────────────────────────────────────
            if RE_SHOPIFY_APP.match(url):
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
                new_params = []
                modified = False
                for k, v in params:
                    if k == "utm_campaign":
                        if v.startswith(lang_code + "-"):
                            # Already prefixed — skip this link
                            break
                        new_params.append((k, lang_code + "-" + v))
                        modified = True
                    else:
                        new_params.append((k, v))
                else:
                    if modified:
                        new_url = urllib.parse.urlunparse(
                            parsed._replace(query=urllib.parse.urlencode(new_params))
                        )
                        print("  UPDATE @%d: %s" % (lnk["start"], url))
                        print("          -> %s" % new_url)
                        all_requests.append({
                            "updateTextStyle": {
                                "range": {
                                    "startIndex": lnk["start"],
                                    "endIndex": lnk["end"],
                                    "tabId": tab_id,
                                },
                                "textStyle": {"link": {"url": new_url}},
                                "fields": "link",
                            }
                        })
                        updated_shopify += 1
                    else:
                        skipped_already_localized += 1
                continue

            # ── trueprofit.io blog links ───────────────────────────────────

            # Already has a language prefix? Skip silently.
            if re.search(r"trueprofit\.io/(es|de|fr)/", url, re.IGNORECASE):
                skipped_already_localized += 1
                continue

            m = RE_EN_BLOG.match(url)
            if not m:
                continue  # not a trueprofit.io/blog/* link at all

            slug = m.group(2).lower()
            if slug not in MULTILINGUAL_SLUGS:
                print("  SKIP (not in list): %s" % url)
                skipped_no_list += 1
                continue

            # Reconstruct URL preserving trailing slash and query string
            trailing_slash = m.group(3)
            query = m.group(4) or ""
            new_url = "%s%s/blog/%s%s%s" % (m.group(1), lang_prefix, slug, trailing_slash, query)

            print("  UPDATE @%d: %s" % (lnk["start"], url))
            print("          -> %s" % new_url)

            all_requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": lnk["start"],
                        "endIndex": lnk["end"],
                        "tabId": tab_id,
                    },
                    "textStyle": {"link": {"url": new_url}},
                    "fields": "link",
                }
            })
            updated_blog += 1

        totals[tab_name] = {
            "updated_blog": updated_blog,
            "updated_shopify": updated_shopify,
            "skipped_no_list": skipped_no_list,
            "already_localized": skipped_already_localized,
        }

    print("\n=== Summary ===")
    for tab_name, t in totals.items():
        print("  %-22s  blog: %d | shopify: %d | skipped (not in list): %d | already localized: %d"
              % (tab_name, t["updated_blog"], t["updated_shopify"], t["skipped_no_list"], t["already_localized"]))
    print("  Total requests: %d" % len(all_requests))

    if not all_requests:
        print("\nNothing to update.")
        return 0

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    # Apply in batches of 400 (API limit is 500)
    BATCH = 400
    for i in range(0, len(all_requests), BATCH):
        chunk = all_requests[i : i + BATCH]
        service.documents().batchUpdate(
            documentId=did, body={"requests": chunk}
        ).execute()
        print("Applied requests %d–%d." % (i + 1, i + len(chunk)))

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
