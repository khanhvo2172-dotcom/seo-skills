---
name: review-trueprofit-live-blog-urls
description: Reviews live TrueProfit blog articles for heading structure, Quick Recap placement, Further Reading placement, FAQ redundancy, and genuinely missing image alt text. Use when the user asks to review, check, or QA one or more live trueprofit.io/blog URLs. It asks whether the user wants the optional content and factual accuracy pass when they have not already specified a preference.
---

# Review TrueProfit Live Blog URLs

Review the published article itself. Do not compare it with a Google Doc unless the user
explicitly requests a comparison.

## Scope

- Start at the article H1.
- End immediately before the author bio identified by `div.wrap-bio`.
- Include the FAQ component even when it is streamed into a placeholder immediately before
  the author bio.
- Exclude navigation, byline/profile chrome, newsletter forms, sidebar elements, author bio,
  Related Blogs, footer, and other site chrome.
- Review only the live URL or URLs provided by the user.

## Required extraction method

TrueProfit pages use streamed React components. Markdown extraction commonly omits Quick
Recap, Further Reading, FAQs, notes, examples, and highlighted boxes. Raw HTML may place the
resolved component payload after the article even though a `template` placeholder locates it
inside the article.

1. Fetch the page as readable markdown to inspect the main article.
2. Fetch and inspect the raw HTML before concluding that any custom component is absent.
3. Reconstruct streamed placeholders before applying the article boundary:
   - A placeholder such as `template id="B:0"` marks the component's true location.
   - Its resolved payload is normally under a later element such as `div id="S:0"`.
   - Treat the contents of `S:0` as if they appear at `B:0`; repeat for every matching number.
4. Only after reconstruction, evaluate the content from H1 through the pre-author-bio boundary.

Prefer `scripts/extract_live_article.py <URL>` for this extraction. If the script cannot run,
perform the same raw-HTML verification manually. Never infer absence from markdown alone.

Cross-check the extracted arrays against the reconstructed article. FAQ headings may use
`Frequently Asked Question(s)` instead of `FAQs`, and questions may lack a special CSS class.
An empty array is not proof of absence when the article still contains the relevant component.
Inspect its questions and answers manually if necessary. Confirm that the author-bio boundary
was found before reporting a complete audit.

## Default review

Always report all six sections below. The absence of an element is a valid result, but only
after raw-HTML verification.

### 1. Heading structure

Check:

- exactly one article H1;
- H1-H6 hierarchy and skipped or orphaned levels;
- complete and correctly ordered numbered headings;
- headings used at a reasonable semantic depth;
- materially repetitive headings that target the same intent.

Suggest replacements only for unreasonable or repetitive headings. Do not provide general
grammar or copy edits.

Check semantic nesting, not only heading levels: an H3 must belong under its parent H2.
For example, report-navigation instructions do not belong under a formula-only H2; recommend
an appropriate H2 or a move to a relevant section. Check every independently numbered group.
A short overview followed by a detailed section is not automatically redundant.

Flag conflicting years between the H1 and other headings, including FAQ headings, as a heading
consistency issue. Do not treat a suggested year alignment as factual verification or assume
that changing the year alone updates the answer. Ignore extraction-only spacing artifacts
unless they are confirmed in the rendered heading.

### 2. Quick Recap

Report whether it exists, its number of bullets, and its location relative to the introduction
and first H2. Do not judge claims or rewrite the recap unless the user asks for content review.
An explicit request for a replacement recap also authorizes that narrow rewrite; base it on
the current article rather than a generic template.

### 3. Further Reading

List every Further Reading box with its linked titles and its position between surrounding
headings.

Use a Markdown table with `Box`, `Links`, `Placement`, and `Assessment` columns.
Count H2s in the current live article, not a proposed revised outline. Verify whether ordinary
body text separates a box from the next heading; the extractor's nearest-heading fields alone
do not establish that the box is directly above that heading.

Warn only when a box sits directly above the 2nd, 3rd, or 5th article H2, excluding a
Quick Recap heading if one exists. The 4th H2 is intentionally excluded — do NOT warn when a
box sits directly above the 4th H2 (this is commonly the "Final Thoughts" conclusion). Also do
not warn when it is above the first, 4th, or 6th-and-later H2, above an H3, or separated from
the next H2 by ordinary body text.

Do not audit missing or duplicate internal links.

### 4. FAQ redundancy

List every FAQ question and classify it as:

- `Heading duplicate` — same main intent as an article heading;
- `Answered in body` — the body already provides the answer;
- `Partial` — related to the body but adds a meaningful sub-angle;
- `Clear` — genuinely new and useful.

For redundant questions, recommend removal or a concrete uncovered re-angle. Prefer a re-angle
when the topic is useful. Do not flag mere keyword overlap.

Compare each complete FAQ answer with the body, not just its question. A platform-specific or
technical sub-angle may be `Partial` or `Clear` even if it shares keywords with a main heading.
Do not recommend an alternative already covered elsewhere. A `Clear` classification or
`Keep` recommendation concerns redundancy only; it does not endorse factual or legal accuracy.

Present the FAQ review as a Markdown table with exactly these columns:
`FAQ`, `Classification`, and `Recommendation`. Put each FAQ question in its own row; do not
use a numbered list for this section.

Always give each FAQ question its own row — including in concise or multi-article reviews and
in any confirm-first removal proposal. Never collapse a cluster into a single grouped bullet
and never use a numbered list for FAQ redundancy. Use a per-question Markdown table whose
columns are a grouping label (`Cluster` or `Issue`), the verbatim `Question`, and a
`Recommendation` (`Keep (primary)` / `Cut — <reason>`). Shared membership in a duplicate group
is expressed by repeating the same grouping label down the rows, not by merging rows. For a
multi-article review, use one such table per article under that article's heading. For example:

| Cluster | Question | Recommendation |
|---|---|---|
| "GRR vs NRR" | What is the difference between GRR and NRR? | Keep (primary) |
| "GRR vs NRR" | What is the difference between gross and net revenue retention? | Cut — duplicates the row above |

Keep every question quoted verbatim from the live article. Whenever a question duplicates a
heading's intent, name the exact duplicated heading(s) in the `Recommendation` cell — the H1,
an H2, or an H3, quoted verbatim (e.g. `Cut — duplicates H2 "What Is Revenue?"`). A question
that merely restates the article's own core thesis (the H1 topic) is a duplicate too: cut it
and cite the H1/relevant H2s, do not keep it as a within-cluster "primary".

Always recommend `Cut` for any question that duplicates a heading (H1/H2/H3) or the article's
core content intent — even if it is the first question or the one you would otherwise call
"primary". Never keep a heading/intent duplicate as a within-cluster primary. Reserve
`Keep (primary)` ONLY for pure sibling clusters, where several questions near-duplicate each
other but none maps to a heading or the page thesis — then keep one and cut the rest.

If there is no FAQ component after raw verification, say so plainly.

### 5. Image alt text

Within the article scope, flag only images whose `alt` attribute is missing or empty.

- Do not evaluate whether existing alt text is well written.
- Do not flag automated images with `alt="banner cta"`.
- Do not flag lazy-loading placeholders with `alt="Loading..."`.
- Do not audit CTA eligibility, CTA placement, or tracking links unless explicitly requested.
- Always ignore these site chrome images regardless of their `alt` value; never list,
  count, or report them. Match by a substring of the image `src` filename, so Next.js
  content-hash variants (e.g. `banner-cta-1.d9324038.webp`) still count:
  - `banner-cta-1` (Next.js CTA banner, e.g. `/_next/static/media/banner-cta-1.<hash>.webp`)
  - `banner-cta-2` (Next.js CTA banner, e.g. `/_next/static/media/banner-cta-2.<hash>.webp`)
  - `icon_toc` (Next.js Table-of-Contents icon, e.g. `/_next/static/media/icon_toc.<hash>.webp`)
  - `img_blog_cta` (blog CTA image, e.g. `https://be.trueprofit.io/uploads/img_blog_cta.webp`)
- Always ignore author-avatar images in the byline. These vary per author, so identify
  them by their container rather than a filename: any image inside a byline/profile block
  whose class contains `written-by` or `meta-info` (e.g. `https://be.trueprofit.io/uploads/hang-1.jpg`
  next to "Written by: <author>"). Do not include any ignored image in the image count.

Identify each missing-alt image by its section or nearby heading. When asked to create alt
text, inspect the actual image instead of inferring its content from a filename or nearby copy.
Give the suggested alt text as plain, copyable lines in article order, without `alt="..."`
wrappers, quotation marks, numbering, or extra commentary when the user asks for alt text only.
If an image cannot be inspected, say so rather than inventing a description.

### 6. Ordered vs unordered lists

Within the article scope, flag every ordered list (`<ol>`, e.g. `<ol class="wp-block-list">`).
Ordered lists auto-render as `1. 2. 3.` numbering, which is only correct for a genuine
sequence (steps, ranked items, a countdown). When the list is really a set of parallel,
non-sequential items — typically each `<li>` opening with a bold label followed by a
definition, such as Gross profit / Operating profit / Net profit — the numbering is
misleading and the list should be an unordered list (`<ul>`).

- Only `<ol>` triggers this check. Ignore `<ul>` lists entirely; they are already unordered.
- For each `<ol>` found, report its nearby heading, its item count, and whether the items are
  bold-label/definition-style. Recommend switching to `<ul>` when the items are not a true
  ordered sequence; leave it as `<ol>` when the order is meaningful (numbered steps, rankings).
- If there are no `<ol>` lists in scope after verification, say so plainly (e.g. "No ordered
  lists — all lists are `<ul>`.").

The extractor reports these under `ordered_lists`. An empty array means every list in scope is
already `<ul>`, which needs no action.

## Optional content and factual review

Run this pass only when the user explicitly asks for content review, factual review, accuracy,
fact-checking, sources, references, benchmarks, or current information. Otherwise, do not
include a `Content and factual issues` section and do not browse for claim verification.

If the user has not said whether they want this pass, complete the six default review sections
and end by asking: `Would you also like me to check content and factual issues for this article?`
Do not run the pass until the user confirms. If the user already requested it, include it in the
same review. If the user explicitly declined it, omit it and do not ask again for that article.

For a continuing series of "Next" URL reviews, carry forward the user's established preference
to exclude content and factual issues until they change it; do not repeat the confirmation
question for every URL. Do not infer authorization for fact-checking from "next", "review",
or a request for structural QA. A request limited to one article or one rewrite does not
automatically enable factual review for subsequent articles.

When requested, read and follow [references/content-factual-review.md](references/content-factual-review.md).

## Excluded by default

- Google Doc comparison
- missing or duplicate internal-link opportunities
- general copy, grammar, punctuation, or style corrections
- external-reference or benchmark verification
- CTA-image eligibility and CTA tracking-link review
- a generic `Priority findings` section

## Response format

Lead with the live URL reviewed and whether the optional content/factual pass was included.
Use these headings in this order:

1. `Heading structure`
2. `Quick Recap`
3. `Further Reading`
4. `FAQ redundancy`
5. `Image alt text`
6. `Ordered vs unordered lists`

Add `Content and factual issues` only when explicitly requested. Keep the report concise,
actionable, and advisory; do not edit the live site. When the user's preference for the optional
pass is unknown, finish with the confirmation question defined above.

### Embedding article links (CMS, not the public URL)

When a review lists articles by name — the per-article detail sections of a multi-article
review, and any place a specific article title is referenced — embed a link on each article
title, and link to the **CMS** copy, not the public URL. `be.trueprofit.io` is the headless
WordPress backend behind the public `trueprofit.io` site. Derive the CMS link by swapping the
host and adding a trailing slash:

- public: `https://trueprofit.io/blog/<slug>`
- CMS:    `https://be.trueprofit.io/blog/<slug>/`

Example: `## 2. [gross-sales-vs-net-sales](https://be.trueprofit.io/blog/gross-sales-vs-net-sales/)`.
The CMS page renders the same article (verified: matching `<title>`), so it is safe to embed.
A summary/overview table may still use the public URL, but detail listings use the CMS link.

## Applying fixes to the CMS

The user has authorized direct fixes to the CMS for two finding types, and confirm-first for
two others. Do not apply anything before a review has been shown.

**Auto-apply (no confirmation needed each time; still report exactly what changed):**

- **Missing image alt text** — inspect the actual image, write alt from its real content
  (not the filename), and set it. Do not touch images that already have alt.
  - Exception: a TrueProfit **app-store CTA banner** — an image wrapped in a link to
    `apps.shopify.com/trueprofit` (e.g. `image-4-1024x431.webp`, `image-1024x431.webp`,
    `track-net-profit-using-trueprofit-shopify-app-4.webp`) — does not need a described alt.
    When its alt is empty, set it to exactly `TrueProfit CTA` rather than describing the image.
- **Ordered list that should be unordered** (the section-6 finding) — convert the Gutenberg
  block from ordered to unordered, both the block comment and the tag:
  - before: `<!-- wp:list {"ordered":true} -->` + `<ol class="wp-block-list">` … `</ol>`
  - after:  `<!-- wp:list -->` + `<ul class="wp-block-list">` … `</ul>`
  Change only the wrapper (`ol`→`ul`) and drop `{"ordered":true}`; leave every `<li>` /
  `wp:list-item` untouched. Only convert lists flagged in the review (parallel/definition-style
  items), never a genuine numbered sequence.
- **Empty list-block artifact** — remove any Gutenberg list block whose list element has no
  items (a leftover from content migrated into numbered paragraphs). Delete the whole block:
  the opening `<!-- wp:list ... -->` comment, the empty `<ol class="wp-block-list"></ol>` or
  `<ul class="wp-block-list"></ul>` tag, and the closing `<!-- /wp:list -->` comment, plus the
  surrounding blank line. Only remove blocks whose list is genuinely empty (no `<li>` /
  `wp:list-item`); never touch a list that has items.

**Confirm first (present the proposed change and wait for a clear yes before editing):**

- **FAQ redundancy** — removals / re-angles.
- **Heading structure** — renames, level fixes, the `::` typo, Quick-Recap-as-heading skips.
- **Further Reading placement** — moving/removing a mis-placed box. Never edit directly;
  present the proposed solution and wait for a clear yes.

### Access mechanism (direct WordPress REST from this session)

`be.trueprofit.io` is headless WordPress; blog posts are the custom post type `blog`. Claude
edits the CMS DIRECTLY from the session via `curl`/`requests` — no n8n bridge needed.

**Credential** — a WP Application Password lives in the local file `C:\Users\khanhvv\.claude\.wp-cms-auth`,
one line, format `khanhvv:<app_password>` (username is `khanhvv`, id 15 — NOT the email). Read it
at runtime, never print it, keep it out of any repo. Never accept the password pasted into chat;
if it ever is, tell the user to revoke and reissue it. (An n8n-held credential also exists —
"WP Basic Auth - TrueProfit CMS", n8n id `o3q4G8lkXQA27d7m`, used by reference workflow
`Zi70b1dVQBqhEm3W` — but the local-file direct path is what Claude uses.)

**Read** raw Gutenberg blocks (needs auth): `GET /wp-json/wp/v2/blog/<id>?context=edit` → `content.raw`.
Unauthenticated `GET /wp-json/wp/v2/blog/<id>` returns only `content.rendered` (no `<!-- wp:list -->`
block comments) and cannot be used to edit blocks.

**Write**: `POST /wp-json/wp/v2/blog/<id>` with `{ "content": "<full updated content.raw>" }`, Basic
Auth from the file. Always send the COMPLETE `content.raw` with only the targeted change applied
(ACF blocks such as `acf/quickrecap`, `acf/faqfeature`, `acf/articleslisting`, and `tableberg/*`
tables are stored as block comments in that same content — preserve them verbatim).

**Verify** — Cloudflare caches the `wp-json` GET, so a plain re-GET can return stale content and
look like the write failed. Confirm the write from the POST response body, or with a cache-busting
GET (`?context=edit&_cb=<timestamp>`, expect `cf-cache-status: MISS`).

**Post id** — from the public page's shortlink (`rel=shortlink`, `?p=<id>`) or the REST
`rel=alternate` link. Verify the id maps to the right slug before writing.

**Always read the CMS source before editing.** The public `trueprofit.io` page lags the CMS
(Next.js/Cloudflare cache), so a review run against the public page can show issues already fixed
at the source. Re-check each finding against `content.raw` and only edit what is genuinely still
present there. The public page stays stale until the site revalidates.
