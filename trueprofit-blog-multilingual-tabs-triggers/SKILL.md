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
  Highlight that is genuinely missing. Use this AFTER the English-only
  trueprofit-blog-triggers skill has prepped tab 1, whenever the user asks to add,
  fix, sync, or repair triggers in the other language tabs / ES-DE-FR tabs /
  translated versions / multilingual tabs of a blog doc, or to "do the same for
  the other languages". Edits the doc in place via the Google Docs API.
---

# TrueProfit multilingual tab trigger repair (ES / DE / FR)

A blog Google Doc has tabs: **English** (tab 1, often titled "article"), then
**Spanish**, **German** and **French** versions. The English-only
[`trueprofit-blog-triggers`](../trueprofit-blog-triggers/SKILL.md) skill preps tab 1.
This skill fixes the **three translated tabs** so the n8n multilingual publisher
picks up correct triggers in every locale.

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
- **PLACE (counts differ → tab is out of sync).** The tab was translated from an
  older English draft, so its image lines are missing/misplaced. The skill removes
  whatever stale image lines exist and **places every English image** by anchoring
  to headings: each English image sits under a heading, and the translated tab has
  the same headings in the same order, so it maps English heading → translated
  heading (by order, confirmed with **cognate keywords** that survive translation —
  `competition`~`competencia`, `organic`~`organica`, `tofu`~`tofu`, `USB`~`USB`) and
  inserts the trigger at the **end of the matched section** — right before the next
  heading (of the same or higher level), mirroring how English places each image as
  the **last paragraph of its section**, not the first one under the heading. The
  dry-run prints the heading each image lands under, with `keyword` or `ordinal`
  confidence — review it.

## What it does per language tab

| Element | Behaviour |
|---|---|
| **Image trigger** | Produces one canonical line `Image (sentence note): <url>, Alt is <alt>` per English image — **repaired** in place (counts match) or **placed** at the end of the matching translated heading's section (out of sync). `<url>` is the **English tab's Nth image URL** (same CDN file, by order); `<alt>` is the **translated** alt. |
| **Content Highlight** | **Only where there's real translated content.** A `Content Highlight` is **kept** (and `Content Highlight:` normalized to no colon) only when the next line is genuine translated highlight content — a localized formula (`=` on the next line) or a Pro tip / Note callout (keyword + colon). A `Content Highlight` carried over from translation that sits above ordinary prose (a test stub, or content the translation dropped) is treated as an **orphan and removed**. A missing `Content Highlight` is **added** above any detected formula / callout that lacks one. |
| **Quick Recap / FAQ** | **Flags only**, per tab, using localized terms. Never fabricates. |

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
and, in PLACE mode, the **heading each image lands under** with a `keyword`/`ordinal`
confidence tag — **review that mapping** before applying, especially any `ordinal`
rows (matched by position, not a shared word). PLACE mode assumes the translated
article has the same sections in the same order as English (true of a faithful
translation); if a product section is genuinely absent in a translated tab, that
image still gets anchored by order — the dry-run is where you catch it.

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
  delete orphans) and the localized add-missing-Content-Highlight recognisers
  (`LANG_TERMS`, used by `detect`).
- `scripts/place_ml.py` — the **heading-anchored placement** engine
  (`english_image_anchors`, `align_headings`, `plan_placements`) used in PLACE mode.
  Heading matching uses cognate keywords: tokens are lowercased, accent-stripped, and
  two tokens match if they share a 4-char prefix (so translated headings still align),
  with a monotonic **ordinal fallback** when there's no shared word. Each image is
  inserted at the **end of its section** (`_section_end`: before the next heading of
  the same or higher level), mirroring English.
- `scripts/gdocs_ml_triggers.py` — the orchestrator (tabs, modes, batchUpdate).
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
