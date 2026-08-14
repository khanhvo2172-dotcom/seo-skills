---
name: trueprofit-blog-triggers
description: >-
  Recheck a TrueProfit blog Google Doc and add the CMS "highlight triggers" the
  n8n publishing workflow needs before a post can be built: a Content Highlight
  label above formulas and Pro tip/Note callouts, Image trigger lines with
  auto-numbered be.trueprofit.io CDN URLs, and a linked CTA image above a [cta]
  marker - and it reports whether the Quick Recap and FAQ sections exist and
  whether any Further Reading block is mis-placed. Use this whenever the user
  asks to "check", "prep", "recheck", "add triggers to", or "get ready for
  publish" a blog Google Doc, mentions Content Highlight / Quick Recap / FAQ /
  Image triggers / sentence notes / CTA image / Further Reading placement, gives
  a Google Docs link for the TrueProfit blog pipeline, or is about to push a doc
  through the n8n blog automation. Edits the doc in place via the Google Docs
  API, first tab only. Prefer this skill over editing the doc by hand or
  eyeballing the triggers.
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
| **CTA image** | **Adds** an image trigger above a `[cta]` marker — fixed URL and alt, plus a `Link is` to the Shopify app listing tagged with the article's main keyword — **but only when the article has more than 5 Heading 2 sections** (FAQ counted). A shorter article gets a **warning** and nothing is inserted. |
| **Quick Recap** | **Flags only.** If the first tab has no Quick Recap, it tells you — it does not write one. |
| **FAQ** | **Flags only.** Same — reports missing, never fabricates Q&A. |
| **Further Reading** | **Flags only.** Warns when a Further Reading block sits directly above the 2nd–5th Heading 2 (it reads as belonging to the heading below it). Never moved automatically. |

The reason Quick Recap, FAQ and Further Reading are flag-only is that they need
real editorial judgement (which points to summarise, which questions matter,
which section a reading list belongs to). Formulas, callouts, image URLs and the
CTA image are mechanical, so those are safe to automate.

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

You always need these from the user:

1. The **Google Doc** (URL or ID).
2. **Whether the doc has a CTA image, and where.** Many articles end with a
   fixed call-to-action image (e.g. `https://be.trueprofit.io/uploads/<slug>-N.webp`
   with alt `TrueProfit CTA`) that should keep its own fixed URL/alt rather than
   following the same naming rule as the other images. Ask this **before**
   picking a naming mode — if there's a CTA image, its URL+alt is fixed and the
   position (usually last) should be excluded from the base-slug/alt-rule
   pattern applied to the rest.

   A `[cta]` **marker line** in the doc is handled automatically (see the CTA
   rule below) — it's an author note, not an embedded image, so it never
   consumes a slot in the image list.

   Other recurring branded screenshots follow the same "fixed URL/alt, not
   part of the naming rule" pattern — e.g. the TrueProfit dashboard screenshot:
   `https://be.trueprofit.io/uploads/trueprofit-dashboard-1-1.webp` with alt
   `TrueProfit Revamp Live Profit Dashboard`. If the user names a known
   recurring image like this, use its fixed URL/alt directly instead of
   applying a base-slug or asking them to re-supply it.

   Only treat an image as one of these recurring branded assets when the user
   **explicitly says so**. An alt string that merely contains the word
   "dashboard" is not enough — use the per-image URL from the naming rule.
3. **How to name the images** — one of two modes (ask which, if unclear):

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

   **Generating alt text yourself (Mode B, when the user gives a rule instead of
   literal text).** Often the user gives a *rule* rather than the exact alt
   strings — e.g. "alt is the app name in each heading 3 plus 'homepage'", or
   "each image demonstrates its heading 3 topic, generate the alt". When you
   have to generate the wording (not just plug in a name), ask **which style**
   they want, since this changes the output a lot:

   - **Formula** — a fixed template applied mechanically, e.g. `<name> homepage`
     for every image. Good when the rule already fully determines the string.
   - **Contextual/natural** — a distinct, naturally-worded sentence per image
     that reflects what the heading/section is actually about, e.g. instead of
     repeating "Demonstration of <heading text> using AI" verbatim for every
     image, vary the verb/phrasing per topic ("Demonstration of automating
     supplier sourcing and order fulfillment using AI" vs "Demonstration of
     handling customer service using AI"). Avoid restating the heading text
     unchanged — rephrase it naturally.

   If unclear which the user wants, ask before generating the full list — it's
   much cheaper than generating, applying, then reset + regenerating.

   The two modes are mutually exclusive. In Mode B, image #1 takes line 1, image
   #2 line 2, and so on — order matters. If the list length doesn't match the
   number of images in the doc, the dry-run prints a **WARNING** and you should
   re-check the order before applying. Alt text may contain spaces/hyphens but
   should avoid `"`, `(`, `)` (the n8n parser stops alt at those characters).
4. **The article's main keyword slug** — only needed when the doc has a `[cta]`
   marker, because it becomes the CTA link's `utm_campaign` value. Pass it with
   `--cta-campaign`; it defaults to `--base-slug` when that's given, so in
   Mode A you usually don't have to supply anything extra.

   ```bash
   python gdocs_triggers.py --doc "<DOC>" --image-list "images.txt" \
     --cta-campaign "how-to-track-dropship-expenses" --dry-run
   ```

**Always dry-run first** so the user can see the full plan (and verify the image
mapping) before the doc changes. If it looks right, re-run without `--dry-run`.

The dry run prints: Quick Recap / FAQ presence, the Heading 2 count, images
found, any warnings (short-article CTA, mis-placed Further Reading, image-list
mismatch), and every planned insertion with its reason. If it looks right, run
the same command **without** `--dry-run` to apply the edits in place.

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

### Content Highlight — Pro tip / Note / Your Takeaway callouts

Trigger on a line starting with **`Pro tip`** (colon optional), **`Note:`**
(colon required, so ordinary prose like "Note that…" is left alone), or
**`Your Takeaway:`** (colon required). Insert a `Content Highlight` label above
it:

```
Pro tip: Use our profit margin tool   -->   Content Highlight
                                            Pro tip: Use our profit margin tool

Your Takeaway: Lead with one hero     -->   Content Highlight
                                            Your Takeaway: Lead with one hero
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

### CTA image

Authors mark where the call-to-action banner should go with a **`[cta]`** note
(anywhere on the line — a bare `[cta]` or `Put the [cta] banner here` both
count). It's a text marker, not an embedded image, so it never consumes a slot
in the `--image-list`.

**Length gate first.** Count the **Heading 2** paragraphs in the first tab, with
the FAQ heading counted as one. If the article has **5 or fewer**, the skill
**inserts nothing and warns** — a CTA banner in a short article is a judgement
call for the author. Only with **more than 5** H2s does it add the trigger above
the marker:

```
Image (sentence note): https://be.trueprofit.io/uploads/app-listing-CTA-3.webp, Link is https://apps.shopify.com/trueprofit?utm_source=trueprofit.io&utm_medium=blog&utm_campaign=<main-keyword>, Alt is TrueProfit CTA
[cta]
```

Fixed parts: the image URL `https://be.trueprofit.io/uploads/app-listing-CTA-3.webp`
and the alt `TrueProfit CTA`. Only `utm_campaign` varies — it's the article's
main keyword slug (e.g. `dropship-skincare`), from `--cta-campaign` or, failing
that, `--base-slug`. With neither, the skill warns instead of writing a link with
a missing campaign tag.

**`Link is` comes before `Alt is` on purpose.** Alt parsing runs to the end of
the line, so with the link last the alt would come out as
`TrueProfit CTA, Link is https://…`. Keeping alt last leaves it exactly
`TrueProfit CTA`.

**Never put raw markup in the doc.** The Google Doc carries the trigger line; the
CMS block is n8n's job. For reference, the same CTA lands in WordPress as:

```
<!-- wp:image {"lightbox":{"enabled":false},"sizeSlug":"full","linkDestination":"custom","align":"center"} -->
<figure class="wp-block-image aligncenter size-full"><a href="https://apps.shopify.com/trueprofit?utm_source=trueprofit.io&amp;utm_medium=blog&amp;utm_campaign=<main-keyword>" rel="nofollow"><img src="https://be.trueprofit.io/uploads/app-listing-CTA-3.webp" alt="TrueProfit CTA"/></a></figure>
<!-- /wp:image -->
```

That is the **output** contract, not doc input. `--reset` will strip such markup
if it ever ends up in a doc.

### Further Reading placement (warn only)

A **Further Reading** line plus the run of URLs under it should sit *inside* the
section it belongs to. When the block is the **last thing before the next H2**,
it reads as an introduction to that heading instead. The skill warns when a
Further Reading block sits directly above the **2nd, 3rd, 4th or 5th** H2 —
those are the positions where it changes how the section is read. Nothing is
moved; it's a note for the author.

```
H2 #1: A1                      H2 #1: A1
  sentence 1                     sentence 1
  H3                             H3
    sentence 3                     sentence 3
    Further Reading  <- fine       Further Reading
  H3                               https://…
    sentence 5                 H2 #2: A2        <- WARNING: the block above
  Further Reading  <- WARNING                      belongs to A1, not A2
H2 #2: A2
```

A block that's followed by more prose, another H3, or the 1st / 6th-and-later H2
is left alone.

### Plain-text guarantee

Every trigger line this skill writes — the `Content Highlight` labels, the
`Image (sentence note): …` lines and the CTA line — is forced to **normal body
text** (`NORMAL_TEXT`, bold/italic/underline cleared). Inserted text otherwise
inherits the style at the insertion point, so a label dropped above a heading
could come out heading-sized or bold. The script re-reads the doc after
inserting and normalizes every trigger line.

## After running

Report back to the user, concisely:

- What was added (count of Content Highlight labels, count of image triggers
  with the numbered URLs, and whether the CTA image trigger went in).
- Whether **Quick Recap** and **FAQ** are present or missing — and if missing,
  remind them to add those manually before publishing.
- Any **warnings**: a `[cta]` marker in a ≤5-H2 article (nothing inserted), a
  Further Reading block sitting directly above the 2nd–5th H2, or an image-list
  count mismatch.
- Any skipped items (already-triggered images, callouts that already had a
  highlight).

## Scope and assumptions

- **First tab only.** Multi-tab docs (e.g. a "Final" tab plus drafts) are common;
  only the first tab is rechecked, matching the English publishing workflow.
- The signed-in Google account needs **edit access** to the doc.
- This skill is about *trigger syntax*, not translation or content. For ES/DE/FR
  versions see the separate localization workflow.
