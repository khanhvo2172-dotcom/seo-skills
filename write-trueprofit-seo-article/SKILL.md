---
name: write-trueprofit-seo-article
description: Write a full TrueProfit SEO blog article from an approved outline, or update/audit an existing TrueProfit article with minimal, verified edits, following the content manager's writing playbook and SOP checklist. Use when asked to draft, write, expand, refresh, update or audit a trueprofit.io blog article or a Final tab in a Google Doc. Not for outlines (outline-generate-trueprofit), outline reviews (review-outline-google-docs-file), pre-publish QA (review-google-docs-article), wording-only AI cleanup (humanizer) or partner guest posts.
---

# Write or update a TrueProfit SEO article

Write for Shopify merchants, ecommerce operators and dropshippers who need to make a business decision. The article must first satisfy the reader's intent with accurate, useful guidance; search visibility comes from that. TrueProfit is real-time net profit analytics for Shopify, and it appears only where it genuinely helps the reader's task.

Pick the mode from the request:

- **Draft mode:** a new article from an approved outline.
- **Update mode:** refresh, fix, audit or improve an existing article (Doc tab or live URL).

Read `references/editorial-standard.md` before either mode. On this PC also read `E:\.trueprofit-claude-codex\shared\playbooks\README.md` and the style memories it links (practical flow, contextual TrueProfit mentions, Ahrefs models, drafting rules); they refine the standard where they don't conflict.

## Which rule wins

1. Khanh's instructions for this task and the locked or approved outline.
2. The editorial standard in this skill.
3. Older style memories and reference articles.

When a rule can't be met without breaking a higher one (for example the locked title lacks the keyword), follow the higher rule and flag the conflict in the handoff note.

## Draft mode

### 1. Before drafting

- Read the outline tab with the shared Docs helper (`E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py`, README first): keyword, confirmed target audience, Insights, Top URLs, AIO/AI Mode notes, outline, internal-link suggestions, Further Reading.
- Confirm keyword, reader, intent, format and the reader outcome. Write the job-to-be-done in one sentence for yourself. If the target audience is missing, ask Khanh first.
- Read the ranking URLs to learn expectations, not to copy structure or claims. Separate recurring SERP patterns from facts that still need verification.
- Collect primary sources for every important fact, statistic, price, feature, integration and platform policy before writing (see the sourcing rules in the standard).
- Check the outline for logical order, distinct heading jobs and missing reader questions. Don't change a locked outline; raise problems in the handoff note, and stop and ask if it conflicts with search intent or another trueprofit.io page.

### 2. Drafting format

Follow `references/drafting-format.md` (outline lock, introduction, Quick Recap, meta description, length, lists and tables, links, Content Highlight callouts, FAQs, references, roundup structure).

### 3. Write each section

- Lead with the answer or key distinction, then the reasoning, then what it means for the merchant. Include trade-offs and when the advice may not work.
- Use concrete examples, formulas or scenarios when they make a decision easier. Check every calculation and label assumptions and hypothetical numbers.
- Bring profitability in where it changes the decision, not in every section.
- Mention TrueProfit only where a section has already set up the problem it solves: reader problem, relevant capability, concrete decision. Keep it understated and accurate; a closing CTA alone can be enough.

### 4. Before delivering

Run the submit checklist in `references/editorial-standard.md` (intent, accuracy, logic, depth, voice, SEO, TrueProfit, finish). Fix what fails. Then deliver:

- Into Google Docs only when asked, normally a new tab named **Final** in the same Doc. Never overwrite an existing Final tab without reading it first and confirming with Khanh. Use the shared helper with a dry run, then read back text, heading styles, links and tables, and confirm sibling tabs are unchanged.
- Otherwise as Markdown in chat or a file under `E:\.trueprofit-claude-codex\workspaces\`.
- End with the handoff note.

## Update mode

An update is not a mandate to rewrite. Change content only where there is a clear reason.

1. Read the current version (the Doc tab via the shared helper, or the live page's article body). Read the outline tab too if one exists.
2. Identify issues in priority order: factual errors, stale pricing or features, intent mismatch, unsupported claims, missing answers to real reader questions, confusing logic, weak comparisons, sections that add no value, then voice problems.
3. Keep the existing outline and every accurate, useful section, unless the structure stops the article from satisfying intent or creates substantial overlap.
4. Make the smallest edit that fixes each problem: the specific sentence, paragraph, example, comparison or heading. Don't replace good copy to make it sound different.
5. Re-verify every claim the edit touches on official or primary sources. Check that new text doesn't duplicate another section or compete with another trueprofit.io page.
6. If performance data is part of the request, separate indexing delays from content-quality problems before blaming the copy.
7. Edit the Doc in place only when Khanh asked for edits (dry run, apply, read back). Otherwise deliver proposed edits as a compact table: location, current text, proposed text, reason, source.
8. End with the handoff note, including the sections left unchanged on purpose.

## Stop and ask Khanh

Pause and ask, rather than guess, when:

- a material claim has no reliable source and can't be safely qualified;
- official sources disagree, or pricing or feature availability is unclear;
- the outline or article conflicts with search intent or another existing trueprofit.io page;
- a requested claim would overstate TrueProfit or present it as a substitute for an unrelated tool.

## Handoff note

Keep it short, in plain language:

1. What changed.
2. Why it was necessary.
3. Facts that need confirmation.
4. Unresolved questions or source gaps.

For an update or audit, add the sections intentionally left unchanged because they are accurate and useful.
