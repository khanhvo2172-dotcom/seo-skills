---
name: outline-generate-trueprofit
description: >-
  Build TrueProfit SEO article outlines for Shopify merchants with a strict
  three-stage workflow: Insights from the main keyword, Area to Win from SERP
  evidence (top URLs, Google AI Overview, AI Mode), then a lean outline in the
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

## Stage 1: Insights (keyword only)

Input: the main keyword. Analyze only the keyword.

Output a section titled **Insights**: exactly one short, practical paragraph covering the primary search intent, what searchers are actually looking for, what information they expect, and the content type that best satisfies the intent (listicle, how-to, explainer, benchmark, comparison...).

Then stop and ask for SERP evidence. If the user already pasted URLs or AI Overview text with the keyword, still deliver only Insights, say you have kept the evidence for Stage 2, and point out anything missing (for example, "you mentioned top URLs but none came through").

## Stage 2: Area to Win (needs SERP evidence)

Input: ranking URLs, Google AI Overview / AI Mode text, screenshots or notes. Treat these as the evidence base.

1. Read every ranking URL (headings and main sections). If a fetch fails (redirect loops, blocks), retry with `curl -sL` and cookies, and extract the headings. Tell the user which pages could not be read rather than guessing their content.
2. Note what each page and the AI answers cover, who they are written for, and what they skip (budgeting, timing, measurement, profitability, Shopify specifics are common gaps).

Output a section titled **Area to Win**: exactly one concise paragraph naming one specific, executable gap or angle that:
- addresses a real decision or need of Shopify merchants;
- clearly differs from what competitors cover, rather than "more information";
- is not a generic SEO angle and does not force TrueProfit in (profit is often the natural angle, but only when the topic supports it).

Keep it one paragraph even in chat, because the user pastes it into a Doc. Then stop and wait for confirmation or an instruction to proceed. A request to "build the outline" or "paste it into the doc" counts as confirmation.

## Stage 3: Outline

Build from: the keyword, the Stage 1 intent, the Stage 2 SERP analysis, the confirmed Area to Win, and the important topics competitors cover.

### Sizing

Articles are 1,500–2,000 **words** and are drafted with the outline locked: every heading becomes body text, and the first two H2s after the intro get the most depth. So:
- Put the core search intent in the first two H2s; the Area to Win is the key differentiation, usually one H2 (or one H2 per idea type) tagged `(area to win)`.
- Aim for about 4–6 core H2s. Merge or cut anything that overlaps; every heading must earn its place.
- Listicles: each item is its own numbered H2 (`H2. 1. ...`), typically 6–10 items for a 2,000-word ceiling. A comparison or summary table H2 can open the list. Product/business-idea listicles need a summary table. For "best X" keywords, help merchants decide rather than multiplying categories.
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

Headings are natural, merchant-focused and keyword-relevant without stuffing. Output only the outline in this stage, not prose.

### Self-check before sending

Run through `references/team-lessons.md` and confirm: no section drifts from intent; no two headings overlap; each heading delivers what it promises; no trivial FAQ; metric/benchmark/TrueProfit points follow the team rules; total size fits a 2,000-word article.

## Writing into a Google Doc

When the user asks to put the result in a Doc, write into the tab whose name contains "outline" (or the tab they name), keeping any existing content and other tabs untouched. Use the shared `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` helper for every Docs read/edit; read its adjacent README first. Use `tabs` and a separate `dump --tab <title-or-id>` per source. Do not use browser editing, a flattened all-tabs reader or a one-off Docs API script. For tables/styles or other operations beyond the CLI, use the README's `gdocs.read`/`gdocs.guarded_batch` module interface, with a fresh revision and explicit tab IDs. Dry-run or inspect the exact request plan before applying, then read back text, links, formatting and unchanged sibling tabs.

Team tab layout, top to bottom: Insights → Area to Win → Top url (the ranking URLs) → Outline → (Internal Link Suggestions and Further Reading, added later by the internal-link workflow) → pasted AI Overview / AI Mode.

Styles: section titles (Insights, Area to Win, Outline) as Heading 2; `H1.`/`H2.` lines as Heading 3; `H3.` lines as Heading 4; Coverage, Writer note and Answer coverage lines as normal text; any bullets as real Docs bullets, never typed markers. Read the tab back and verify text and styles before reporting.

Internal-link suggestions are a separate step (`suggest-internal-links` skill or the team's internal-link workflow); offer it after the outline is accepted rather than doing it unasked.
