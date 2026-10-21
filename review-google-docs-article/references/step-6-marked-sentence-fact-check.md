# Step 6 - Fact-check marked sentences

## Scope and inputs

Double-check every sentence bearing `[Inference]`, `[Speculation]`, or `[Unverified]`
in the selected article tab. These are inline notes, not Google Docs tab names. Honor
an explicitly selected tab such as Final; never expand to sibling tabs for this pass.
Only the Google Doc and selected tab are required. An internal-link candidate list,
a linked citation, or a DR result is not required to run this check.

Run this pass by default in a full article review and whenever the user requests fact
or data accuracy. A separate request to skip internal links does not skip this pass.
A marker means the claim needs review, not that it is automatically false.

## Find the claims

1. Read the selected tab with `scripts/dump_tab.py`, preserving inline source links.
   Also inspect table cells in that same tab through the Docs API: the current dump
   prints `{table}` instead of cell contents. Do not call a whole-document reader.
2. Find all three labels case-insensitively, including labels in table cells, bullets,
   FAQs, and labels split across text runs. Join text runs within each paragraph or
   cell before scanning. Recognize both prefix and suffix notes. A standalone note
   applies to the adjacent sentence it clearly annotates; if ambiguous, report the
   candidate wording and ask for clarification rather than guessing its scope.
3. Record the original marker, exact sentence, and heading or table location. Review
   each marked sentence; split compound claims when their evidence or verdict differs.
   Read adjacent context to avoid misinterpreting qualifications. A label on a paragraph
   can introduce several sentences: assess every claim it clearly covers.

## Verify the evidence

- Inspect any cited source, including a References list in the selected tab. Then
  browse for corroboration or a stronger source where needed. Read the supporting
  page, not just a search snippet. Prefer current official documentation, original
  research/data, or other primary sources. Link the precise supporting page.
- Check dates, geography, plan eligibility, feature availability, attribution windows,
  definitions, units, denominators, and whether a statement is a measured result,
  estimate, example, recommendation, prediction, or causal claim.
- Recalculate percentages, margins, break-even points, and other derived numbers.
  A correct calculation does not verify an unsupported input or industry benchmark.
- For `[Inference]`, verify the premises and explain whether they reasonably support
  the conclusion. Evidence for the premises alone does not make the conclusion an
  established fact. Preserve uncertainty about causation and generalization.
- For `[Speculation]`, look for evidence supporting the prediction or possibility.
  Plausibility is not verification. Recommend explicit conditional wording when the
  prediction remains uncertain, or removal if it is misleading or has no useful basis.
- For `[Unverified]`, actively seek direct evidence. If evidence is absent, conflicting,
  inaccessible, or outdated, say what could not be verified. Do not invent a source or
  infer that an unsupported claim is false simply because a search found no evidence.
- For advice or opinion, assess any factual premises and identify it as advice/opinion;
  do not label it a proven outcome.

## Report in chat

Use one row per marked sentence (or per distinct subclaim when necessary):

| Location | Note | Exact sentence / claim | Evidence and source | Verdict | Recommended action / wording |
|---|---|---|---|---|---|

Verdicts: **Verified**, **Partly supported**, **Contradicted**, **Unverified**, or
**Advice/opinion**. Explain the evidence briefly. For inference/speculation that remains
uncertain, use Partly supported or Unverified and name the uncertainty. Recommend
specific corrected wording and a citation, or explain what evidence is still needed.
For a contradiction, show both the draft's value/claim and the source's correction.

Report all marked sentences, including those verified, so coverage is reviewable.
Give the total marked sentences checked and verdict counts; distinguish sentence
counts from subclaim counts if a sentence needed multiple rows. If there are no labels,
say "No [Inference], [Speculation], or [Unverified] notes found in the selected tab."
This does not certify every unmarked claim. If the user requested a broader accuracy
review, check the additional claims too and identify that extra scope separately.

This pass is **report-only**. Leave sentences and markers in the Doc unchanged unless
the user explicitly authorizes edits. A verified claim can receive a recommendation to
replace its note with a citation, but never silently strip uncertainty labels.
