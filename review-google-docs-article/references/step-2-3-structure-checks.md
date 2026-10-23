# Steps 2 & 3 — Structure checks (CTA image + Further Reading placement)

Both checks read the resolved article tab. Pass `--tab <resolved-id>` after listing tabs with the shared helper; honor an explicit selector, otherwise prefer Final. An implicit URL `t.0` usually denotes the outline and does not override that default. Missing explicit selectors fail. Step 2 inserts an authorized CTA; Step 3a normalizes malformed reading blocks. Placement remains report-only.

The packaged planners use the shared gdocs.py helper through `shared_docs_service.py`. Read the shared helper README; do not create per-skill tokens or separate OAuth scripts.

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

## Step 3 — Further Reading format (auto-fix) + placement (report-only)

### 3a. Format — label and separate link lines (auto-fix)

Use a simple label followed by each link on its own line; preserve the user's edited plain-URL format and do not create a table:

```
Further Reading:
https://trueprofit.io/blog/example-a
https://trueprofit.io/blog/example-b
```

Writers often paste it as `Further Reading: [Link A]` on one line, use soft line breaks (Shift+Enter), bullet the
label itself, or drop the colon. `scripts/fix_further_reading.py` fixes all of
these: it splits each link onto its own line, deletes leftover separators between
links (spaces, commas, `|`, dashes, soft breaks), removes a bullet from the label,
adds the missing colon. Existing separate plain lines are already valid; bullets are optional and must not be forced onto them. Links,
anchor text and text styles are untouched.

This fix is **pre-authorized** (no confirmation needed). Run it **before** the
placement check; placement detection accepts plain URLs and existing linked bullets:

```bash
python fix_further_reading.py --doc "<DOC_URL_WITH_?tab=...>"           # dry-run: list blocks
python fix_further_reading.py --doc "<DOC_URL_WITH_?tab=...>" --apply   # fix them
python fix_further_reading.py --doc "<DOC_URL_WITH_?tab=...>"           # verify: expect 0
```

Report how many blocks were fixed per doc (or "already formatted"). Never claim a
fix unless the apply run printed `APPLIED` and the verify run shows 0. Note the
link count per fixed block. If it differs from what you saw earlier in the
session, say so: the docs are often edited live by writers.

### 3b. Placement (report-only)

A "Further Reading" block is a label line followed by a short list of links. It
should live **inside** the section it was written for, not stranded right before
the next big heading.

- **Warn** when a Further Reading block sits **directly above the 2nd, 3rd, 4th,
  or 5th H2** (ordinals counted with Quick Recap excluded). There it reads as
  belonging to the heading below it.
- **Don't warn** when it's above the 1st or the 6th-and-later H2, above an **H3**,
  or when ordinary body text sits between it and the next H2.

The block's items are detected by a plain URL or an existing **list bullet**, so it works whether
the links are plain-text URLs or hyperlinks (anchor text with the URL hidden in
the link attribute — the common case). This is deliberately more robust than a
literal "http" text match, which misses every hyperlinked list.

## How to run it

Run 3a's `fix_further_reading.py --apply` first. Then, for the CTA and placement
checks, always dry-run first (the default), show the user, then apply the CTA if wanted.

```bash
# from scripts/ — report only (no edits), includes both checks.
# Pass the FULL doc URL so the ?tab=t.xxxx is honored (or add --tab t.xxxx):
python review_structure.py --doc "<DOC_URL_WITH_?tab=...>" --cta-campaign "<main-keyword>"

# apply just the CTA insertion (after the user confirms the keyword):
python review_structure.py --doc "<DOC_URL_WITH_?tab=...>" --cta-campaign "<main-keyword>" --apply
```

The header line prints the resolved tab (`Tab : <title> [t.xxxx]`); if a requested tab is missing or ambiguous, stop and clarify the correct tab before running.

Report to the user, concisely:
- Quick Recap / FAQ presence; the H2 count.
- CTA: qualifies or not; if it qualifies, the exact line and the `utm_campaign`
  slug to confirm; whether it was applied.
- Every Further Reading warning (which H2 it sits above), or "none".

Run `python test_detect_structure.py` after any change to `detect_structure.py`
to confirm the CTA gate, Quick-Recap exclusion, and Further-Reading rules still
hold.
