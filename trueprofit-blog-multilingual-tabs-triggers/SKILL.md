---
name: trueprofit-blog-multilingual-tabs-triggers
description: >-
  Fix the TrueProfit CMS "highlight triggers" in the Spanish, German and French
  tabs of a blog Google Doc, using the already-triggered English (first) tab as
  the source of truth. Translated tabs carry trigger lines over from translation
  but stale - old/test image URLs & alts, image triggers split across two lines,
  and "Content Highlight:" with a colon. This skill REPAIRS them: reformats each
  image line to the canonical one-line form with the matching English URL and a
  translated alt, normalizes Content Highlight labels, and adds any Content
  Highlight that is genuinely missing. Also bulk-localizes internal
  trueprofit.io/blog links and Shopify app utm_campaign tags in the three
  language tabs via update_links.py. Use this AFTER the English-only
  trueprofit-blog-triggers skill has prepped tab 1, whenever the user asks to add,
  fix, sync, or repair triggers in the other language tabs / ES-DE-FR tabs /
  translated versions / multilingual tabs of a blog doc, or to "do the same for
  the other languages", or to "update/localize the internal links". Edits the doc
  in place via the Google Docs API.
---

# TrueProfit multilingual tab trigger repair + link localization (ES / DE / FR)

A blog Google Doc has tabs: **English** (tab 1, often titled "article"), then
**Spanish**, **German** and **French** versions. The English-only
[`trueprofit-blog-triggers`](../trueprofit-blog-triggers/SKILL.md) skill preps tab 1.
This skill does two things to the **three translated tabs**:

1. **Repair / place CMS triggers** — so the n8n multilingual publisher picks up
   correct `Image (sentence note):` and `Content Highlight` lines in every locale.
2. **Localize internal links** (via `update_links.py`) — rewrites `trueprofit.io/blog/<slug>`
   links and Shopify app `utm_campaign` tags for each language.

**Run the English skill first.** This skill reads the English tab's image triggers
to learn the shared image URLs (in order), so tab 1 must already be triggered.

## Two image modes: repair vs. placement

Translated tabs are produced by translating the English markdown, so they may
arrive with trigger lines **already present but stale** (image triggers split
across two lines, old/test URLs & alts, `Content Highlight:` with a colon), and
they have **no embedded image objects**. The skill auto-picks per tab, per the
image-trigger-line count vs. the English image count:

- **REPAIR (counts match).** The tab carries one image-trigger line per English
  image, in order — repair each in place: rewrite to canonical form, swap in the
  English URL by order, translate the alt, drop the stale second URL line.
- **PLACE (counts differ → tab is out of sync).** The tab is missing its trigger
  lines (or they were reset). The skill removes whatever stale lines exist and
  **mirrors the English tab**: every English image — and every English Content
  Highlight — is placed at the **same paragraph position** as English. For each
  English image it (1) maps the image's English heading → the translated heading (by
  order, confirmed with **cognate keywords** that survive translation —
  `competition`~`competencia`, `organic`~`organica`, `tofu`~`tofu`, `USB`~`USB`),
  then (2) inserts the trigger **after the translated paragraph at the same ordinal**
  — i.e. after the translated equivalent of the English paragraph it follows, *not*
  grouped at the section end. Pure paragraph counting drifts when a language merges
  or splits a paragraph, so within a small window around the expected ordinal it
  picks the translated paragraph whose **content best matches** the English anchor
  paragraph (cognate-token overlap), falling back to the ordinal. An image whose
  English heading only matches a **closing-region** heading (Final Thoughts / FAQ),
  by ordinal *or* a coincidental keyword, is redirected to the **end of the body**
  (e.g. a closing CTA lands before Final Thoughts, never inside the FAQ). The dry-run
  prints, per image, the translated heading and the paragraph it lands after, with
  `keyword` / `ordinal` / `fallback` confidence, plus **STRUCTURE WARNINGS** for any
  anchor not confirmed by a shared heading keyword — review them.

## What it does per language tab

| Element | Script | Behaviour |
|---|---|---|
| **Image trigger** | `gdocs_ml_triggers.py` | Produces one canonical line `Image (sentence note): <url>, Alt is <alt>` per English image — **repaired** in place (counts match) or **placed at the same paragraph position as English** (out of sync). `<url>` is the **English tab's Nth image URL** (same CDN file, by order); `<alt>` is the **translated** alt. |
| **Content Highlight** | `gdocs_ml_triggers.py` | **REPAIR (counts match):** a `Content Highlight` is **kept** (and `Content Highlight:` normalized to no colon) only when the next line is genuine translated highlight content — a localized formula (`=` on the next line) or a callout (Pro tip / Note / **Your Takeaway** keyword + colon); one sitting above ordinary prose is an **orphan and removed**, and a missing one is **added** above any detected formula / callout. **PLACE (out of sync):** Content Highlights are **mirrored from English** — wherever English has a `Content Highlight` above a paragraph, one is placed above the translated equivalent of that paragraph (same paragraph-ordinal anchoring, snapping to the translated callout label). This keeps every editorial highlight — Your Takeaway, Pro tip, Note, formula — in parity with English without per-language guesswork. |
| **Quick Recap / FAQ** | `gdocs_ml_triggers.py` | **Flags only**, per tab, using localized terms. Never fabricates. |
| **Blog links** | `update_links.py` | Rewrites `https://trueprofit.io/blog/<slug>` → `https://trueprofit.io/<lang>/blog/<slug>` for every slug in the `MULTILINGUAL_SLUGS` list. Links to slugs not in the list are left untouched and logged. Already-localized links are skipped. |
| **Shopify app links** | `update_links.py` | Prefixes `utm_campaign` on `apps.shopify.com/trueprofit` links: `utm_campaign=foo` → `utm_campaign=es-foo` / `de-foo` / `fr-foo`. Skips links where the prefix is already present. |

Trigger **labels stay in English** in every tab (`Content Highlight`,
`Image (sentence note):`, `Alt is`) because the n8n parser keys on them — only the
**alt text** is translated.

## How to run it

Run everything from this skill's `scripts/` directory. Auth is identical to the
English skill (`GOOGLE_TOKEN_JSON` env var → `token.json` → first-time OAuth); see
[references/setup-google-api.md](references/setup-google-api.md). The English
skill's token works here.

### Step 1 — see the English images (what to translate)

```bash
python gdocs_ml_triggers.py --doc "<DOC>" --dump-en
```

Lists the English tab's image URLs and English alts, in document order, plus which
tab mapped to each language (**check that mapping**).

### Step 2 — translate the alts (you, the agent)

Translate each English alt into ES / DE / FR following the TrueProfit localization
conventions (see `trueprofit-blog-localization`: faithful translation, brand names
kept in English, no em dashes). Avoid `"`, `(`, `)` in alt text — the n8n parser
stops alt at those characters. Save `alts.json`:

```json
{
  "es": ["alt es para imagen 1", "alt es para imagen 2"],
  "de": ["alt de für Bild 1", "alt de für Bild 2"],
  "fr": ["alt fr pour image 1", "alt fr pour image 2"]
}
```

One entry per image **in document/English order**. A language with fewer entries
falls back to the English alt for the rest (the run prints a note). If there are no
images, skip `alts.json` — the Content Highlight repairs still run.

### Step 3 — dry-run, review, apply

```bash
python gdocs_ml_triggers.py --doc "<DOC>" --alts alts.json --dry-run   # preview all 3 tabs
python gdocs_ml_triggers.py --doc "<DOC>" --alts alts.json             # apply
```

Limit to one language with `--lang es` (repeatable: `--lang es --lang fr`).

The dry-run prints, per tab: how many image trigger lines and Content Highlight
lines it found (vs the English image count), Quick Recap / FAQ presence, and every
planned change (`replace` / `insert`) with its reason.

**Always dry-run first.** The header shows each tab's `image mode` (REPAIR or PLACE)
and, in PLACE mode, the translated heading **and the paragraph each image lands
after**, with a `keyword`/`ordinal`/`fallback` confidence tag — **review that
mapping** before applying, especially any `ordinal` rows (matched by position, not a
shared word) and the **STRUCTURE WARNINGS** block (any anchor not confirmed by a
shared heading keyword — the tell-tale of an English/translated heading mismatch).
PLACE mode assumes the translated article has the same sections, in the same order,
with the same paragraph breaks as English (true of a faithful translation); paragraph
drift from a merge/split is auto-corrected by content match, but the dry-run is where
you catch a genuinely missing or reordered section.

### Step 4 — localize internal links (optional but recommended)

After the triggers are applied, run `update_links.py` to rewrite internal links in
the language tabs:

```bash
python update_links.py --doc "<DOC>" --dry-run   # preview all changes
python update_links.py --doc "<DOC>"             # apply
```

**What it rewrites:**

| Link type | Change |
|---|---|
| `https://trueprofit.io/blog/<slug>` | Becomes `https://trueprofit.io/es/blog/<slug>` (or `/de/`, `/fr/`) — only if the slug is in the hardcoded `MULTILINGUAL_SLUGS` list (~29 slugs). Slugs not in the list are skipped and logged. |
| `https://apps.shopify.com/trueprofit?…utm_campaign=<val>…` | Becomes `utm_campaign=es-<val>` (or `de-`, `fr-`). |

Both operations are **idempotent** — already-localized links (`/es/blog/…` or `utm_campaign=es-…`) are silently skipped.

**Tab matching:** `update_links.py` identifies language tabs by exact title match
(`"Spanish Version"`, `"German Version"`, `"French Version"`). Tabs not carrying
one of those exact titles are ignored. If the doc uses different tab names, the
script will report 0 updates — check that the tab titles match exactly.

**Updating the slug list:** `MULTILINGUAL_SLUGS` is a Python `set` inside
`update_links.py`. To add a new localized blog post, add its slug (the part after
`/blog/`) to that set and commit the file.

## Idempotent & plain-text

- **Idempotent.** A line already in canonical form is detected and skipped — re-runs
  make no change.
- **Plain text.** Every repaired/added trigger line is forced to `NORMAL_TEXT` with
  bold/italic/underline cleared, per tab, after editing.
- Edits are applied **descending by position** (replace = delete range + insert), so
  indices stay valid within each tab.

### Resetting

```bash
python gdocs_ml_triggers.py --doc "<DOC>" --reset --dry-run   # preview removals
python gdocs_ml_triggers.py --doc "<DOC>" --reset             # remove canonical triggers from ES/DE/FR tabs
```

`--reset` only touches the language tabs, never the English tab, and removes
canonical trigger lines (single-line `Image (sentence note): http…` and
`Content Highlight`). Run a normal pass first if the tab still has the stale
two-line form, so they become canonical and removable.

## How tabs are identified

Tabs are matched by **full language name** in the title (case-insensitive contains):
`english`, `spanish`/`español`, `german`/`deutsch`, `french`/`français`. Bare
2-letter codes are deliberately NOT used (e.g. "en" hides inside "fr**en**ch"). If a
title doesn't match (the English tab is often titled "article"), it falls back to
**position** (tab 0 = en, 1 = es, 2 = de, 3 = fr). The dump/dry-run header prints the
final mapping and the full tab list — check it before applying.

## How the code is organized

- `scripts/detect_ml.py` — image repair planner (`plan_repairs`,
  `parse_existing_triggers`), the Content-Highlight planner (`plan_ch`: keep backed,
  delete orphans) and the localized recognisers (`LANG_TERMS` / `compile_recognisers`,
  used by `detect`) — `callout` now also covers **Your Takeaway**-style labels, and a
  `final_thoughts` recogniser feeds the end-of-body fallback.
- `scripts/place_ml.py` — the **paragraph-anchored, English-mirroring placement**
  engine used in PLACE mode. `english_image_anchors` / `english_ch_anchors` record,
  per image / Content Highlight, the heading it sits under, the **body-paragraph
  ordinal** it follows/labels, and that paragraph's text. `align_headings` maps
  English → translated headings by cognate keywords (tokens lowercased, accent-
  stripped, matched on a shared 4-char prefix; monotonic ordinal fallback).
  `plan_placements` / `plan_ch_placements` then insert each trigger at the **same
  paragraph ordinal**, using `choose_anchor` (cognate-token overlap in a ±2 window) to
  correct translation drift; CH placement snaps to the translated callout label.
  `body_end_index` is the closing-region landmark for the CTA fallback.
- `scripts/gdocs_ml_triggers.py` — the orchestrator (tabs, modes, structure-warning
  guard, batchUpdate).
- `scripts/update_links.py` — standalone link-localization script. Walks every text
  run in the ES / DE / FR tabs, rewrites `trueprofit.io/blog/<slug>` links to their
  localized equivalent for slugs in `MULTILINGUAL_SLUGS`, and prefixes `utm_campaign`
  values on `apps.shopify.com/trueprofit` links. Matches tabs by exact title
  (`"Spanish Version"`, `"German Version"`, `"French Version"`). Applies changes in
  batches of 400 (Docs API limit is 500). Run independently after the trigger step;
  supports `--dry-run`.
- `scripts/test_detect_ml.py` — `python test_detect_ml.py` runs the whole suite
  (detection, repair, placement, and request-builder ordering regressions).

Add-missing-Content-Highlight detection rules:

- **Formula:** the localized formula word (`fórmula`/`Formel`/`formule`) **anywhere**
  in a line whose **next line contains `=`** (the `=` is the real discriminator, so
  culinary "fórmulas de tofu" or a footnote legend like "* Estimado = …" don't fire).
- **Callouts:** localized Pro tip / Note keyword **+ colon** (French space-before-colon
  allowed), so prose never triggers.

Repairing a carried-over `Content Highlight:` line doesn't need these — it just strips
the colon. Detection only adds a Content Highlight that's missing entirely.

## Scope and assumptions

- Operates on the **ES / DE / FR tabs**; the **English tab is read-only** (source of
  the shared image URLs and their heading anchors, by order).
- PLACE mode assumes the translated article keeps the **same sections in the same
  order** as English (true of `trueprofit-blog-localization` output and of any faithful
  translation). It anchors to **headings**, so the products must be real headings in
  both tabs (they are, in TrueProfit listicles). Review the dry-run's placement table.
- The signed-in Google account needs **edit access** to the doc.
