---
name: outline-generate-trueprofit
description: >-
  Build TrueProfit SEO article outlines for Shopify merchants with a strict
  three-stage workflow: Insights from keyword intent and SERP evidence, Area to
  Win from competitor coverage, then an audience-confirmed lean outline in the
  team's Coverage-line format. Use whenever the user gives a main keyword for a
  new TrueProfit/Shopify blog post, pastes ranking URLs or AI Overview text for
  an outline, asks for "insights", "area to win", an "outline", or a content
  brief for a trueprofit.io blog article, or asks to put an outline into a
  Google Doc "insights & outline" tab, even if they don't name this skill.
  Not for reviewing existing outlines (use review-outline-google-docs-file) or
  writing the full article.
---

# Generate TrueProfit SEO Outlines

Act as an SEO content strategist for TrueProfit, writing for Shopify merchants and ecommerce owners. TrueProfit is a real-time net profit analytics app for Shopify; its articles exist to rank and to help merchants make profitable decisions, not to advertise.

The work runs in three stages. Each stage needs the user's input before the next, because the user supplies the evidence (SERP data) and owns the angle decision. Never skip ahead, and never write the article.

Before Stage 3, read `references/team-lessons.md`: it holds the reviewer corrections that past outlines kept receiving, and following it up front saves a review round.

## Before outlining: target audience and evidence

Read the document's existing target-audience data first. If absent, ask Khanh to confirm the intended audience at the start, before building the outline. Do not substitute the generic TrueProfit audience or infer an audience from the keyword as confirmation. A clear audience confirmation already supplied for this topic in the current conversation satisfies the requirement; do not ask again. Research may continue while awaiting the answer, but outline drafting must wait.

Khanh's **Google Search** URL list and **AIO / AI Mode top URLs** list are complementary: the latter contains additional URLs appearing in AI Overview or AI Mode answers that are not already listed under Google Search. Combine the lists and read each distinct page once. Do not ask for Google Search URLs to be repeated under AIO / AI Mode, or infer that an omitted URL did not appear in an AI answer. A blank additional-URL list can mean there are no extra URLs; it does not by itself establish missing evidence. Preserve the supplied categories when recording sources.

## Stage 1: Insights (keyword intent plus SERP evidence)

Input: the main keyword, supplied AI Overview and AI Mode answers, and the combined ranking URLs. Read the available answer text and ranking pages before filling Insights. If only a keyword is available, request the SERP material needed to complete Insights rather than presenting a keyword-only interpretation as the finished section. If an AI answer is unavailable, state that limitation and use the available evidence without inventing it.

1. Read each distinct ranking URL's headings and main content. If a fetch fails, try an available alternate reader and disclose any page that remains inaccessible; do not guess its coverage.
2. Compare the keyword's likely intent with the questions, formats, audiences and information emphasized across the AI answers and ranking pages.

Output a section titled **Insights**: exactly one short, practical paragraph synthesizing the primary search intent, what searchers actually want, the information they expect, and the content type that best satisfies that need (list, tutorial, comparison, review, benchmark, checklist or definition). End the paragraph with a one-sentence job-to-be-done, such as "Help a Shopify merchant compare dropshipping apps and choose tools that fit their workflow." Base it on the keyword intent, AIO, AI Mode and ranking URLs together, not the keyword alone. Distinguish observed search intent from an audience that still needs Khanh's confirmation.

Check titles and slugs in `https://trueprofit.io/blog.xml`. If an existing trueprofit.io article targets the same main keyword or primary intent, say so and ask Khanh before outlining. Overlap on one sub-keyword or section only needs a cross-link in the outline.

Then stop before Area to Win unless the user has already requested that stage. Do not ask for evidence already supplied in the document or conversation.

## Stage 2: Choose the Area to Win section (needs SERP evidence)

Use the evidence read for Insights and any new ranking URLs, AI Overview / AI Mode text, screenshots or notes supplied afterward. Read new sources as needed; reuse the existing analysis instead of refetching unchanged pages. Note what the pages and AI answers cover, who they address, and which concrete merchant decisions they leave unresolved.

Choose one specific, executable angle to deliver through a real H2 or H3 inside the outline. The section must:
- address a real decision or need of Shopify merchants;
- clearly differ from what competitors cover, rather than "more information";
- avoid a generic SEO angle and forced TrueProfit promotion (profit is often the natural angle, but only when the topic supports it).

When this stage is requested separately, propose the actual merchant-facing heading tagged `(area to win)` and one concise `Coverage:` line, then wait for confirmation or an instruction to proceed. A request to "build the outline" or "paste it into the doc" counts as confirmation. In the completed outline or Google Doc, place this heading and its coverage in the outline itself. Do not create a separate `Area to Win` section or competitor-gap paragraph outside the outline. This supersedes the earlier standalone-paragraph format (Khanh, October 27, 2026).

## Stage 3: Outline

Build only after target-audience data is present in the document or Khanh has confirmed it for this topic. Build from: the keyword, the evidence-based Insights, the target audience, the Stage 2 SERP analysis, the confirmed Area to Win, and the important topics competitors cover.

### Sizing

Articles are 1,500–2,000 **words** and are drafted with the outline locked: every heading becomes body text, and the first two H2s after the intro get the most depth. So:
- Put the core search intent in the first two H2s; the Area to Win is the key differentiation, usually one H2 (or one H2 per idea type) tagged `(area to win)`.
- Aim for about 4–6 core H2s. Merge or cut anything that overlaps; every heading must earn its place.
- Listicles: each item is its own numbered H2 (`H2. 1. ...`), typically 6–10 items for a 2,000-word ceiling. A comparison or summary table H2 can open the list. Product/business-idea listicles need a summary table. For "best X" keywords, help merchants decide rather than multiplying categories.
- Tool/app roundups: choose apps by the keyword's intent and the reader's needs. Each app's Coverage line names the per-app parts: short positioning, Key Features relevant to the intent, verified Pricing, Best For, and Customer Sentiment only when reliable review patterns exist. Place TrueProfit where profit tracking complements the other tools, never first by default and never as a substitute for a category it doesn't replace.
- FAQs: 1–3, only questions the body does not already answer and that are not obvious.
- Include a TrueProfit-related point only where it genuinely fits (usually the profitability/measurement section).
- End with Final Thoughts.

### Format

Start with `## Outline`. Use this hierarchy, giving each heading one short `Coverage:` line (what the section must cover). Use a couple of bullets instead only when a heading truly needs a short list (such as steps).

```
## Outline
### H1. [Natural title targeting the main keyword]
Writer note: [optional, cross-cutting guidance, e.g. how to evaluate every idea]
### H2. [Section]
Coverage: ...
#### H3. [Subsection]
Coverage: ...
### H2. [Differentiating section] (area to win)
Coverage: ...
### H2. FAQs
#### H3. [Question]?
Answer coverage: ...
### H2. Final Thoughts
Coverage: [the next action for the merchant, without repeating the article]
```

Organize headings around the reader's decision or task, not a keyword list. Give each heading a distinct job, and never add a heading just to fit a related keyword. Headings are natural, merchant-focused and keyword-relevant without stuffing. The H1 states the article's real value; avoid the keyword-plus-generic-descriptor or keyword-colon formula. Output only the outline in this stage, not prose.

### Self-check before sending

Run through `references/team-lessons.md` and confirm: target audience is documented or confirmed; Insights uses the supplied AI answers and combined URL evidence and ends with a job-to-be-done; the format matches the intent; no section drifts from intent; no two headings overlap; the Area to Win is a concrete heading/section within the outline with no separate analysis block; each heading delivers what it promises; no trivial FAQ; metric/benchmark/TrueProfit points follow the team rules; total size fits a 2,000-word article.

## Writing into a Google Doc

When the user asks to put the result in a Doc, write into the tab whose name contains "outline" (or the tab they name), keeping any existing content and other tabs untouched. Use the shared `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` helper for every Docs read/edit; read its adjacent README first. Use `tabs` and a separate `dump --tab <title-or-id>` per source. Do not use browser editing, a flattened all-tabs reader or a one-off Docs API script. For tables/styles or other operations beyond the CLI, use the README's `gdocs.read`/`gdocs.guarded_batch` module interface, with a fresh revision and explicit tab IDs. Dry-run or inspect the exact request plan before applying, then read back text, links, formatting and unchanged sibling tabs.

Team tab layout, top to bottom: Insights and confirmed Target audience, retaining any existing keyword table at the beginning; Top url (the ranking URLs); Outline, including the heading tagged `(area to win)`; Internal Link Suggestions and Further Reading when separately requested; pasted AI Overview / AI Mode. Never add a standalone Area to Win section outside the outline.

Styles: section titles (Insights, Outline) as Heading 2; `H1.`/`H2.` lines as Heading 3; `H3.` lines as Heading 4; Coverage, Writer note and Answer coverage lines as normal text; any bullets as real Docs bullets, never typed markers. Read the tab back and verify text and styles before reporting.

Internal-link suggestions are a separate step (`suggest-internal-links` skill or the team's internal-link workflow); offer it after the outline is accepted rather than doing it unasked.
