---
name: review-google-docs-article
description: >-
  Review a TrueProfit Google Docs article before publishing. Use for article QA,
  internal/external links and citations, CTA images, Further Reading formatting
  and placement, FAQ redundancy, AI tracking params, or fact-checking sentences
  marked [Inference], [Speculation], or [Unverified]. Compare the full article
  structure with its outline tab and prioritize factual accuracy. Review the selected
  article tab, using its outline tab only as the structure baseline. Produce
  recommendations, with the existing authorized exceptions
  for CTA insertion, Further Reading formatting, AI tracking-param cleanup, and
  removal of verified sentence tags.
---

# Review a TrueProfit Google Docs Article

This skill runs a structured pre-publish QA review of a TrueProfit blog article that lives
in a Google Doc. The review is deliberately **modular** — each step is a self-contained QA
pass with its own reference file. Steps 1-7 cover links, CTA image, Further Reading,
FAQ redundancy, AI tracking params, fact verification, and article-versus-outline
structure comparison. Prioritize factual accuracy and departures from the outline;
avoid unsolicited stylistic restructuring. Future steps slot in the same way.

## Shared Google Docs access on this PC

Use `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` for Docs reads and writes; read its adjacent README first. Use `tabs` and a tab-specific `dump` for review. The packaged planners use `scripts/shared_docs_service.py` to call the same helper for authentication, revision-guarded writes and readback; do not create separate OAuth tokens or one-off Docs API scripts, and do not edit through the browser. For operations beyond the CLI, use the documented `gdocs.read`/`gdocs.guarded_batch` module interface with explicit tab IDs. Inspect a dry run before applying and verify the intended text/styles/links afterward; on a conflict, reread and recompute the plan.

## How to run a review

1. Default to **all available steps** unless the user specifies a subset. Compare
   the article with the outline first (Step 7), prioritize fact verification (Step 6),
   then run the other checks in their existing order (1 -> 2 -> 3 -> 4 -> 5).
2. For each requested step, open its reference file and follow it exactly.
3. Deliver findings as a **report in chat**, focusing detail only on items requiring
   review, a decision, or an edit. For each actionable item, give its location, the
   exact problematic text or missing part, why it matters, supporting evidence where
   relevant, and a concrete correction. Prioritize factual issues and outline gaps.
4. Summarize everything that passed in a short paragraph or compact checklist, with
   useful counts. Do not enumerate correct sentences, sound advice, passing links,
   matching headings, or FAQs that should simply be kept. An exhaustive audit trail
   is provided only if the user explicitly requests it. Keep unresolved verification
   limits visible; an unchecked item is not a pass.
5. This reporting rule overrides reference-file instructions to show every checked
   item or a separate section/table for each clean step. Use the references' detailed
   tables only for actionable findings. Perform all selected checks just as thoroughly;
   link, CTA, Further Reading, FAQ, and tracking checks remain unchanged. Step 6
   automatically removes tags only from fully verified sentences; unresolved tags
   remain until verified, including by the user when their confirmation is needed.

## Available steps

| # | Step | Reference file | What it checks |
|---|------|----------------|----------------|
| 1 | Internal & External Links | `references/step-1-internal-external-links.md` | Missing internal-link opportunities (with anchor-text proposals), duplicate links to remove, and external-reference accuracy (benchmark matching + DR≥65 authority + broken links) |
| 2 | CTA image | `references/step-2-3-structure-checks.md` | Whether a `[cta]` marker qualifies for the CTA image (> 5 H2, Quick Recap excluded, FAQ counted) and, if so, **inserts** the CTA image trigger; warns on short articles |
| 3 | Further Reading format + placement | `references/step-2-3-structure-checks.md` | **Auto-fixes** every block to a `Further Reading:` label plus separate link lines, preserving the user's plain-URL format (`scripts/fix_further_reading.py`), then warns when a block sits directly above the 2nd–5th H2 (report-only) |
| 4 | FAQ redundancy | `references/step-4-faq-redundancy.md` | Flags FAQ questions that duplicate a heading's intent or are already answered in the body (report-only, model-driven) |
| 5 | AI tracking params | `references/step-5-ai-tracking-params.md` | Detects **and removes** AI-tool `utm_source` params (chatgpt, claude, perplexity, gemini, …) from every link in the tab, incl. tables; keeps all other params |
| 6 | Fact verification | `references/step-6-marked-sentence-fact-check.md` | Verifies all marked sentences and material factual claims across the article against sources; reports actionable findings and automatically removes only verified sentence tags, preserving the sentences; keeps unresolved tags |
| 7 | Article structure vs. outline | `references/step-7-article-outline-comparison.md` | Compares the full article with its outline tab to detect missing sections, wrong headings or hierarchy/order, extra sections, and content that fails to deliver the outlined topic (report-only) |

Steps 2 and 3 share one pass over the doc's headings, so `scripts/review_structure.py`
runs both together. Steps 4, 6, and 7 require model judgment; Step 6 also requires source
research. Run Step 6 for a full review or a fact-check request even if the internal-link
check is skipped or no internal-link candidate list is available. The bracketed labels
are sentence notes in the selected tab, not instructions to review sibling tabs.

> **Adding a step later:** write `references/step-N-<name>.md` describing that pass, then add
> a row to the table above and a line to the "How to run" default order. Keep each step's
> heavy detail in its own reference file so this orchestrator stays short.

## Inputs the user must provide

- **Google Doc URL** — list tabs and honor the user's explicit article selection; otherwise prefer **Final**. A `tab=t.0` link usually points to the outline. Read the outline separately only for Step 7. Use the shared helper's existing access; do not make a private document public just to read it.
- **Outline tab** *(Step 7)* - use the user-named outline tab or locate the unique
  outline section in a tab such as `Outline` or `Insights & outline`. Confirm if
  multiple candidate outlines exist or none is identifiable; continue independent
  checks meanwhile. See Step 7 for selecting the outline without mixing tab content.
- **URLs to check** — the candidate internal links, one per line, in the format
  `https://www.trueprofit.io/blog/some-page | Page title`. The title after `|` is optional
  but helps judge relevance. This is the list Step 1 compares against the doc.
- **Must-have URLs** *(Step 1, optional)* — a subset of links that *must* be present. Paste
  into the app's `Must-have URLs` box; matching rows come back flagged `⭐ Must-have` and are
  treated as must-insert (not subject to the selective judgment).
- **Main keyword** *(Step 2 only)* — a kebab-case slug for the CTA link's `utm_campaign`.
  Don't ask up front: derive it from the doc and **confirm with the user** (see Step 2).

If a step's required input is missing, ask for it before running that step.

## Ground rules for every step

- **Review only the selected article tab; read its outline tab solely for Step 7.** A TrueProfit blog doc almost
  always has **sibling tabs** beside the article (an `n8n flow` draft, an `Insights & outline`
  notes tab, AI-research dumps). These are separate tabs, **not** scratch content inside the
  article, and must never be flagged as "delete these blocks." The Drive reader
  (`read_file_content`) concatenates *every tab* into one blob — do **not** use it for this skill.
  Read article text with the shared helper's `dump --tab Final` or the resolved exact ID. It preserves links, tables and image markers. Read the outline separately for Step 7. Never concatenate tabs or flag outline notes as article content.
- For comment-led review/revision, read every paginated thread, quoted anchor and reply, including resolved threads, before planning edits. Map each requirement to an edit or explicit preserve/no-change decision, respect newer user edits and exclusions, and verify each disposition. Do not claim comments were resolved merely because content was edited.
- **Advisory by default; four exceptions.** Every step produces *recommendations* the user
  applies themselves — **except Step 2's CTA insertion**, **Step 3a's Further Reading
  separate-link formatting**, **Step 5's AI-param removal**, and **Step 6's verified-tag
  removal**, which edit the Doc in place.
  Step 3a (`scripts/fix_further_reading.py`) is pre-authorized: dry-run, apply, re-verify. For Step 2 (`scripts/review_structure.py`), always dry-run and
  show the plan first; only `--apply` after the user confirms (especially the `utm_campaign`
  keyword). Step 5 (`scripts/strip_ai_utm.py`) is pre-authorized: dry-run, apply, re-verify. Never claim an edit was
  made unless the apply run actually succeeded.
  Step 6 tag removal is pre-authorized after verification: plan exact tag-only
  deletions, apply to the selected article tab, and read back to verify. Keep tags on
  any sentence needing user verification, pending explicit confirmation. Do not
  rewrite the sentence or remove uncertainty words from its prose.
- **Be selective, not exhaustive.** For opportunities (like missing links), recommend only
  what genuinely makes the content more valuable or better for SEO. Quality over coverage.
- **Show your reasoning.** For every recommendation, say *why* (SEO value, relevance,
  accuracy, authority) so the user can trust or overrule it quickly.
