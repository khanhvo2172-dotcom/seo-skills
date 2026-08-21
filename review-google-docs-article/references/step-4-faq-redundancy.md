# Step 4 — FAQ redundancy

**Goal:** make sure the FAQ section earns its place. An FAQ should answer a
*net-new* long-tail question — something a reader still wonders after the body,
not a restatement of a section that's already there. This check is **report-only**
and **model-driven** (no script): it needs judgment about *intent*, not string
matching.

Read the article from **the tab in the URL only** — you likely already have it from Step 1's
`scripts/dump_tab.py` dump. Never read the whole document (sibling tabs like an `n8n flow` draft
would leak in); if you need to re-read, run `dump_tab.py --doc "<url with ?tab=...>"`.

## What to flag

For every question in the FAQ section, flag it when **either** holds:

1. **Duplicates a heading's main intent.** A heading and an FAQ are asking the same
   core thing. Example: a heading **"Best Perfume Dropshipping Suppliers"** and an
   FAQ **"What are the best perfume suppliers?"** — same intent, so the FAQ is
   redundant with the section.
2. **Already answered in the body.** Even with no matching heading, the article's
   prose already answers the question somewhere. Example: an FAQ *"Do customers
   reorder perfume?"* when a subsection already argues repeat purchases are the
   whole advantage.

Judge **intent and answer**, not keywords. Two items can share words but ask
different things (a "how to *choose* a supplier" heading vs. an FAQ "do I need a
*license*?" are not duplicates). Conversely, they can duplicate with no shared
words.

**Don't over-flag.** If the FAQ adds something genuinely new — a concrete number,
an edge case, a distinct sub-angle the body doesn't cover — it's pulling its
weight. Mark those **partial** (note the related section) rather than flagging them
as redundant, so the user can decide.

## How to run it

1. Locate the FAQ section (usually the last H2, titled `FAQ`/`FAQs` or
   "Frequently Asked Questions"). List its questions in order.
2. List the article's headings (H2 and H3) with a one-word sense of each one's
   main intent.
3. For each FAQ question, decide: heading-duplicate (rule 1), answered-in-body
   (rule 2), partial, or clear (keep).
4. Report a table:

   | FAQ question | Overlap type | Duplicates / answered by | Recommendation |
   |---|---|---|---|

   - **Overlap type**: `Heading duplicate` / `Answered in body` / `Partial` / `Clear`.
   - **Duplicates / answered by**: the exact heading or section.
   - **Recommendation**: `Remove`, or `Re-angle to <a specific uncovered
     sub-question>`. Prefer re-angling over deletion when the topic still deserves
     an FAQ but the current phrasing just mirrors the body — suggest a concrete
     narrower question the article does **not** already answer.

5. If nothing is redundant, say so plainly — a clean FAQ is a valid result.

Keep it advisory: you never edit the Doc in this step; the author applies the
rewrites.
