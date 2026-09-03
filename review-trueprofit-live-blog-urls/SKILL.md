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

## Default review

Always report all five sections below. The absence of an element is a valid result, but only
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

### 2. Quick Recap

Report whether it exists, its number of bullets, and its location relative to the introduction
and first H2. Do not judge claims or rewrite the recap unless the user asks for content review.

### 3. Further Reading

List every Further Reading box with its linked titles and its position between surrounding
headings.

Warn only when a box sits directly above the 2nd, 3rd, 4th, or 5th article H2, excluding a
Quick Recap heading if one exists. Do not warn when it is above the first or 6th-and-later H2,
above an H3, or separated from the next H2 by ordinary body text.

Do not audit missing or duplicate internal links.

### 4. FAQ redundancy

List every FAQ question and classify it as:

- `Heading duplicate` — same main intent as an article heading;
- `Answered in body` — the body already provides the answer;
- `Partial` — related to the body but adds a meaningful sub-angle;
- `Clear` — genuinely new and useful.

For redundant questions, recommend removal or a concrete uncovered re-angle. Prefer a re-angle
when the topic is useful. Do not flag mere keyword overlap.

Present the FAQ review as a Markdown table with exactly these columns:
`FAQ`, `Classification`, and `Recommendation`. Put each FAQ question in its own row; do not
use a numbered list for this section.

If there is no FAQ component after raw verification, say so plainly.

### 5. Image alt text

Within the article scope, flag only images whose `alt` attribute is missing or empty.

- Do not evaluate whether existing alt text is well written.
- Do not flag automated images with `alt="banner cta"`.
- Do not flag lazy-loading placeholders with `alt="Loading..."`.
- Do not audit CTA eligibility, CTA placement, or tracking links unless explicitly requested.

## Optional content and factual review

Run this pass only when the user explicitly asks for content review, factual review, accuracy,
fact-checking, sources, references, benchmarks, or current information. Otherwise, do not
include a `Content and factual issues` section and do not browse for claim verification.

If the user has not said whether they want this pass, complete the five default review sections
and end by asking: `Would you also like me to check content and factual issues for this article?`
Do not run the pass until the user confirms. If the user already requested it, include it in the
same review. If the user explicitly declined it, omit it and do not ask again for that article.

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

Add `Content and factual issues` only when explicitly requested. Keep the report concise,
actionable, and advisory; do not edit the live site. When the user's preference for the optional
pass is unknown, finish with the confirmation question defined above.
