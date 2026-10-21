---
name: review-google-docs-article
description: >-
  Review a TrueProfit Google Docs article before publishing. Use for article QA,
  internal/external links and citations, CTA images, Further Reading formatting
  and placement, FAQ redundancy, AI tracking params, or fact-checking sentences
  marked [Inference], [Speculation], or [Unverified]. Review only the selected
  article tab. Produce recommendations, with the existing authorized exceptions
  for CTA insertion, Further Reading formatting, and AI tracking-param cleanup.
---

# Review a TrueProfit Google Docs Article

This skill runs a structured pre-publish QA review of a TrueProfit blog article that lives
in a Google Doc. The review is deliberately **modular** — each step is a self-contained QA
pass with its own reference file. Steps 1-6 cover links, CTA image, Further Reading,
FAQ redundancy, AI tracking params, and fact-checking marked sentences. Future steps
slot in the same way.

## How to run a review

1. Ask which step(s) the user wants if they didn't say. Default to running **all available
   steps in order** (1 -> 2 -> 3 -> 4 -> 5 -> 6).
2. For each requested step, open its reference file and follow it exactly.
3. Deliver each step's findings as a **report in chat** (not a file) using the structure the
   step defines. If running multiple steps, give one clearly-headed section per step.

## Available steps

| # | Step | Reference file | What it checks |
|---|------|----------------|----------------|
| 1 | Internal & External Links | `references/step-1-internal-external-links.md` | Missing internal-link opportunities (with anchor-text proposals), duplicate links to remove, and external-reference accuracy (benchmark matching + DR≥65 authority + broken links) |
| 2 | CTA image | `references/step-2-3-structure-checks.md` | Whether a `[cta]` marker qualifies for the CTA image (> 5 H2, Quick Recap excluded, FAQ counted) and, if so, **inserts** the CTA image trigger; warns on short articles |
| 3 | Further Reading format + placement | `references/step-2-3-structure-checks.md` | **Auto-fixes** every block to a `Further Reading:` label plus one bulleted link per line (`scripts/fix_further_reading.py`), then warns when a block sits directly above the 2nd–5th H2 (report-only) |
| 4 | FAQ redundancy | `references/step-4-faq-redundancy.md` | Flags FAQ questions that duplicate a heading's intent or are already answered in the body (report-only, model-driven) |
| 5 | AI tracking params | `references/step-5-ai-tracking-params.md` | Detects **and removes** AI-tool `utm_source` params (chatgpt, claude, perplexity, gemini, …) from every link in the tab, incl. tables; keeps all other params |
| 6 | Marked-sentence fact check | `references/step-6-marked-sentence-fact-check.md` | Double-checks every sentence marked `[Inference]`, `[Speculation]`, or `[Unverified]` against sources; reports evidence, verdicts, and suggested corrections without editing the Doc |

Steps 2 and 3 share one pass over the doc's headings, so `scripts/review_structure.py`
runs both together. Steps 4 and 6 require model judgment; Step 6 also requires source
research. Run Step 6 for a full review or a fact-check request even if the internal-link
check is skipped or no internal-link candidate list is available. The bracketed labels
are sentence notes in the selected tab, not instructions to review sibling tabs.

> **Adding a step later:** write `references/step-N-<name>.md` describing that pass, then add
> a row to the table above and a line to the "How to run" default order. Keep each step's
> heavy detail in its own reference file so this orchestrator stays short.

## Inputs the user must provide

- **Google Doc URL** — the article to review. **The URL's `tab=t.xxxx` parameter names the exact
  tab to review; that tab is the whole scope.** The doc must be readable by the link-checker app's
  Google service account, or shared as "anyone with the link can view".
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

- **Review ONLY the tab in the URL — never the whole document.** A TrueProfit blog doc almost
  always has **sibling tabs** beside the article (an `n8n flow` draft, an `Insights & outline`
  notes tab, AI-research dumps). These are separate tabs, **not** scratch content inside the
  article, and must never be flagged as "delete these blocks." The Drive reader
  (`read_file_content`) concatenates *every tab* into one blob — do **not** use it for this skill.
  Read article text with **`scripts/dump_tab.py`** (it honors the URL's `tab=` param and emits just
  that tab, with links inline as `[anchor](url)`). The structure script (`review_structure.py`) is
  already tab-scoped the same way. If a `tab=` param is missing, the scripts fall back to the first
  tab and say so — confirm the intended tab with the user rather than reviewing everything.
- **Advisory by default; three exceptions.** Every step produces *recommendations* the user
  applies themselves — **except Step 2's CTA insertion**, **Step 3a's Further Reading
  bullet formatting** and **Step 5's AI-param removal**, which edit the Doc in place.
  Step 3a (`scripts/fix_further_reading.py`) is pre-authorized: dry-run, apply, re-verify. For Step 2 (`scripts/review_structure.py`), always dry-run and
  show the plan first; only `--apply` after the user confirms (especially the `utm_campaign`
  keyword). Step 5 (`scripts/strip_ai_utm.py`) is pre-authorized: dry-run, apply, re-verify. Never claim an edit was
  made unless the apply run actually succeeded.
- **Be selective, not exhaustive.** For opportunities (like missing links), recommend only
  what genuinely makes the content more valuable or better for SEO. Quality over coverage.
- **Show your reasoning.** For every recommendation, say *why* (SEO value, relevance,
  accuracy, authority) so the user can trust or overrule it quickly.
