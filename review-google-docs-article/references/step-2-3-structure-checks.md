# Steps 2 & 3 — Structure checks (CTA image + Further Reading placement)

Both checks read **the tab named in the URL** (`review_structure.py` reads the
`?tab=t.xxxx` param; pass the full URL, or add `--tab t.xxxx`). It never reads
sibling tabs. Step 2 (CTA) is the one place in this whole skill that **edits the
Doc in place**; Step 3 (Further Reading) is report-only.

Auth is the same OAuth setup as the `trueprofit-blog-triggers` skill — see that
skill's `references/setup-google-api.md`. Provide credentials via the
`GOOGLE_TOKEN_JSON` env var or a local `scripts/token.json` (git-ignored); the
first run otherwise falls back to an OAuth flow using `scripts/credentials.json`.
The signed-in Google account needs **edit access** to the Doc to apply the CTA.

## Step 2 — CTA image

Authors mark where the call-to-action image should go with a plain `[cta]` line.
Whether that slot should actually carry the CTA image depends on how substantial
the article is, measured in **Heading-2 sections**:

- **Count H2s, EXCLUDING "Quick Recap"** (it's a structural summary, not a body
  section). **FAQ counts** as an H2.
- **≤ 5 H2 → warn**, don't insert. The article may be too light to carry the CTA;
  the author decides.
- **> 5 H2 → insert** a CTA image trigger immediately above the `[cta]` marker:
  ```
  Image (sentence note): https://be.trueprofit.io/uploads/app-listing-CTA-3.webp, Link is https://apps.shopify.com/trueprofit?utm_source=trueprofit.io&utm_medium=blog&utm_campaign=<main-keyword>, Alt is TrueProfit CTA
  ```
  `Link is` comes **before** `Alt is` on purpose — the n8n parser reads the alt to
  the end of the line, so a link after the alt would be swallowed into it.

**Main keyword (`utm_campaign`).** Derive a kebab-case slug from the article and
**confirm it with the user before applying** (their choice). Good sources, in
order: an existing `apps.shopify.com/trueprofit?...utm_campaign=<slug>` link
already in the body (reuse that exact slug for consistency); else the article
title / target keyword lowercased and hyphenated. Never invent one silently.

The insertion is **idempotent** — if an `Image: …` trigger already sits above the
`[cta]` marker, it's skipped.

## Step 3 — Further Reading placement (report-only)

A "Further Reading" block is a label line followed by a short list of links. It
should live **inside** the section it was written for, not stranded right before
the next big heading.

- **Warn** when a Further Reading block sits **directly above the 2nd, 3rd, 4th,
  or 5th H2** (ordinals counted with Quick Recap excluded). There it reads as
  belonging to the heading below it.
- **Don't warn** when it's above the 1st or the 6th-and-later H2, above an **H3**,
  or when ordinary body text sits between it and the next H2.

The block's list items are detected by their **list bullet**, so it works whether
the links are plain-text URLs or hyperlinks (anchor text with the URL hidden in
the link attribute — the common case). This is deliberately more robust than a
literal "http" text match, which misses every hyperlinked list.

## How to run it

Always dry-run first (the default), show the user, then apply the CTA if wanted.

```bash
# from scripts/ — report only (no edits), includes both checks.
# Pass the FULL doc URL so the ?tab=t.xxxx is honored (or add --tab t.xxxx):
python review_structure.py --doc "<DOC_URL_WITH_?tab=...>" --cta-campaign "<main-keyword>"

# apply just the CTA insertion (after the user confirms the keyword):
python review_structure.py --doc "<DOC_URL_WITH_?tab=...>" --cta-campaign "<main-keyword>" --apply
```

The header line prints the resolved tab (`Tab : <title> [t.xxxx]`); if it warns
that the tab wasn't found and it fell back to the first tab, stop and confirm the
correct tab with the user before trusting the results.

Report to the user, concisely:
- Quick Recap / FAQ presence; the H2 count.
- CTA: qualifies or not; if it qualifies, the exact line and the `utm_campaign`
  slug to confirm; whether it was applied.
- Every Further Reading warning (which H2 it sits above), or "none".

Run `python test_detect_structure.py` after any change to `detect_structure.py`
to confirm the CTA gate, Quick-Recap exclusion, and Further-Reading rules still
hold.
