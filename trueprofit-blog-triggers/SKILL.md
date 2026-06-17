---
name: trueprofit-blog-triggers
description: >-
  Recheck a TrueProfit blog Google Doc and add the CMS "highlight triggers" the
  n8n publishing workflow needs before a post can be built: a Content Highlight
  label above formulas and Pro tip/Note callouts, and Image trigger lines with
  auto-numbered be.trueprofit.io CDN URLs - and it reports whether the Quick
  Recap and FAQ sections exist. Use this whenever the user asks to "check",
  "prep", "recheck", "add triggers to", or "get ready for publish" a blog Google
  Doc, mentions Content Highlight / Quick Recap / FAQ / Image triggers / sentence
  notes, gives a Google Docs link for the TrueProfit blog pipeline, or is about
  to push a doc through the n8n blog automation. Edits the doc in place via the
  Google Docs API, first tab only. Prefer this skill over editing the doc by hand
  or eyeballing the triggers.
---

# TrueProfit blog trigger prep

Blog drafts live in Google Docs. Before the n8n workflow can turn a doc into a
WordPress post, the doc has to contain plain-text **trigger lines** that tell the
parser where the special CMS blocks go. This skill rechecks a doc's **first tab**
and adds the triggers that are missing, so the author doesn't have to remember
the exact syntax.

It does the mechanical, easy-to-forget parts. It deliberately does **not**
invent editorial content (it won't write a Quick Recap or FAQ for you) — it just
tells you when those are missing so you can write them.

## What it adds vs. flags

| Element | Behaviour |
|---|---|
| **Content Highlight** | **Adds** a `Content Highlight` label line above qualifying content (see rules below). |
| **Image** | **Adds** an `Image (sentence note): <url>, Alt is "<alt>"` line **above** each embedded image. URL+alt come from either a base slug (auto-numbered, blank alt) or an explicit per-image list. |
| **Quick Recap** | **Flags only.** If the first tab has no Quick Recap, it tells you — it does not write one. |
| **FAQ** | **Flags only.** Same — reports missing, never fabricates Q&A. |

The reason Quick Recap and FAQ are flag-only is that they need real editorial
judgement (which points to summarise, which questions matter). Formulas, callouts
and image URLs are mechanical, so those are safe to automate.

## How to run it

The skill is a Python script over the Google Docs API. Run everything from this
skill's `scripts/` directory. First time in a new environment, do the **one-time
setup** in [references/setup-google-api.md](references/setup-google-api.md)
(install the libs, supply credentials, authorize).

**Credentials** are looked up in this order, so the skill works both locally and
in a fresh session that has no files:

1. `GOOGLE_TOKEN_JSON` env var — your authorized-user token JSON (the portable
   path; set this in Claude.ai / any new environment and you're done).
2. A `token.json` file next to the script (written automatically after a local
   authorization, reused on later runs).
3. `GOOGLE_CLIENT_SECRET_JSON` env var or a `credentials.json` file — used only
   for the first-time interactive OAuth that mints the token.

The Google account behind the token needs **edit access** to the doc.

You always need two things from the user:

1. The **Google Doc** (URL or ID).
2. **How to name the images** — one of two modes (ask which, if unclear):

   **Mode A — base slug (auto-number, blank alt).** One slug drives every image
   URL, numbered by order, alt left empty. Good for a fresh article where the
   images will be uploaded as `<slug>-1.webp`, `<slug>-2.webp`, …

   ```bash
   python gdocs_triggers.py --doc "<DOC>" --base-slug "marginal-benefit-vs-marginal-cost" --dry-run
   ```

   **Mode B — explicit URL + alt list.** The user supplies a list where each line
   is a full image URL and its alt text, one per image **in document order**.
   Save the pasted list to a text file (one `url<TAB>alt` per line) and pass it:

   ```
   https://be.trueprofit.io/uploads/V1-2.webp        Large preview
   https://be.trueprofit.io/uploads/mushroom-lamp.png Mushroom lamp
   ...
   ```
   ```bash
   python gdocs_triggers.py --doc "<DOC>" --image-list "images.txt" --dry-run
   ```

   The two modes are mutually exclusive. In Mode B, image #1 takes line 1, image
   #2 line 2, and so on — order matters. If the list length doesn't match the
   number of images in the doc, the dry-run prints a **WARNING** and you should
   re-check the order before applying. Alt text may contain spaces/hyphens but
   should avoid `"`, `(`, `)` (the n8n parser stops alt at those characters).

**Always dry-run first** so the user can see the full plan (and verify the image
mapping) before the doc changes. If it looks right, re-run without `--dry-run`.

The dry run prints: Quick Recap / FAQ presence, images found, and every planned
insertion with its reason. If it looks right, run the same command **without**
`--dry-run` to apply the edits in place.

The script is **idempotent** — triggers already present are detected and skipped,
so re-running a doc won't create duplicates. That makes a dry-run → review →
apply loop safe.

### Resetting (re-do triggers cleanly)

If a doc has triggers from an older run that you want to regenerate (e.g. to move
image triggers or restyle them), use `--reset` to remove every skill-added
trigger line, then run normally to re-create them:

```bash
python gdocs_triggers.py --doc "<DOC>" --reset            # remove all triggers (add --dry-run to preview)
python gdocs_triggers.py --doc "<DOC>" --base-slug "<slug>"  # re-create them fresh
```

## Detection rules (the important part)

These mirror exactly what the n8n Transform Content parser looks for, so a
trigger this skill adds is one the publisher will actually pick up. The logic
lives in `scripts/detect_triggers.py` and is covered by `scripts/test_detect.py`
(run `python test_detect.py` to verify after any change).

### Content Highlight — Formula

Trigger when a line **contains the word "formula"** (anywhere — a bare `Formula`
heading, an inline lead-in like `…net profit margin formula:`, or a mid-sentence
phrase like `The standard marginal cost formula is straightforward:`) **and** the
next non-empty line contains an **`=`**. The skill inserts a `Content Highlight`
label between that line and the formula line:

```
The standard marginal cost formula is straightforward:      The standard marginal cost formula is straightforward:
Marginal Cost = Change in Total Cost ÷ Change in Quantity   -->   Content Highlight
                                                                  Marginal Cost = Change in Total Cost ÷ Change in Quantity
```

The **`=` on the following line is the real discriminator** — it's what keeps
prose from triggering. So this does NOT fire (no `=` underneath):

```
Definition and Formula
In economics, marginal benefit is the maximum amount a consumer is willing...
```

(The next line has no `=` — so nothing is added.)

### Content Highlight — Pro tip / Note callouts

Trigger on a line starting with **`Pro tip`** (colon optional) or **`Note:`**
(colon required, so ordinary prose like "Note that…" is left alone). Insert a
`Content Highlight` label above it:

```
Pro tip: Use our profit margin tool   -->   Content Highlight
                                            Pro tip: Use our profit margin tool
```

### Image

For every embedded image in the first tab, in order, add a trigger line
**immediately above** it:

```
Image (sentence note): <url>, Alt is "<alt>"
```

The `<url>` and `<alt>` come from whichever mode is in use:

- **Mode A (`--base-slug`):** `<url>` =
  `https://be.trueprofit.io/uploads/<base-slug>-<n>.webp` with `<n>` incrementing
  per image (1, 2, 3 …), and `<alt>` empty.
- **Mode B (`--image-list`):** `<url>` and `<alt>` are taken from the Nth line of
  the supplied list for the Nth image.

The `(sentence note)` text is a literal placeholder for the author to replace
with a real caption later. An image that already has an `Image: …` line on
**either** side of it (above or below) is left untouched, so re-runs never
duplicate.

### Plain-text guarantee

Every trigger line this skill writes — both the `Content Highlight` labels and
the `Image (sentence note): …` lines — is forced to **normal body text**
(`NORMAL_TEXT`, bold/italic/underline cleared). Inserted text otherwise inherits
the style at the insertion point, so a label dropped above a heading could come
out heading-sized or bold. The script re-reads the doc after inserting and
normalizes every trigger line.

## After running

Report back to the user, concisely:

- What was added (count of Content Highlight labels, count of image triggers,
  with the numbered URLs).
- Whether **Quick Recap** and **FAQ** are present or missing — and if missing,
  remind them to add those manually before publishing.
- Any skipped items (already-triggered images, callouts that already had a
  highlight).

## Scope and assumptions

- **First tab only.** Multi-tab docs (e.g. a "Final" tab plus drafts) are common;
  only the first tab is rechecked, matching the English publishing workflow.
- The signed-in Google account needs **edit access** to the doc.
- This skill is about *trigger syntax*, not translation or content. For ES/DE/FR
  versions see the separate localization workflow.
