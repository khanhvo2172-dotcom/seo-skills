# Step 6 - Fact verification

## Scope and inputs

Double-check every sentence bearing `[Inference]`, `[Speculation]`, or `[Unverified]`
in the selected article tab. These are inline notes, not Google Docs tab names. Honor
an explicitly selected tab such as Final; never expand to sibling tabs for this pass.
Only the Google Doc and selected tab are required. An internal-link candidate list,
a linked citation, or a DR result is not required to run this check.

Run this pass by default in a full article review and whenever the user requests fact
or data accuracy. A separate request to skip internal links does not skip this pass.
A marker means the claim needs review, not that it is automatically false.

Factual accuracy is the main review priority. In addition to all marked sentences,
read the full article (including tables and FAQs) for material factual claims: numbers,
benchmarks, calculations, dates, pricing/fees, feature availability, eligibility,
platform setup instructions, metric definitions, product claims, and causal or
comparative assertions. Verify these even when unmarked; prioritize claims whose
inaccuracy would change a merchant's decision. Do not limit verification to cited
sentences or spend this pass redesigning an outline that the article follows.
The outline is a structure baseline, not proof that its factual claims are true.

## Find the claims

1. Read the selected tab with the shared helper's `dump --tab <resolved-title-or-id>`, preserving links and table cells. For exact structure, use `gdocs.read` and `gdocs.pick_tab` from the same helper. Do not call a flattened all-tabs reader.
2. Find all three labels case-insensitively, including labels in table cells, bullets,
   FAQs, and labels split across text runs. Join text runs within each paragraph or
   cell before scanning. Recognize both prefix and suffix notes. A standalone note
   applies to the adjacent sentence it clearly annotates; if ambiguous, report the
   candidate wording and ask for clarification rather than guessing its scope.
3. Record the original marker, exact sentence, and heading or table location. Review
   each marked sentence; split compound claims when their evidence or verdict differs.
   Read adjacent context to avoid misinterpreting qualifications. A label on a paragraph
   can introduce several sentences: assess every claim it clearly covers.
4. Inventory the material unmarked claims as well. Apply the same source and calculation
   checks below; mark the Note column as `Unmarked` for these findings.

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

Report only claims requiring review, clarification, evidence, or an edit. Use one row
per actionable sentence (or distinct subclaim when necessary); omit individually
verified claims and sound advice/examples requiring no change:

| Location | Note | Exact sentence / claim | Evidence and source | Verdict | Recommended action / wording |
|---|---|---|---|---|---|

Verdicts: **Verified**, **Partly supported**, **Contradicted**, **Unverified**, or
**Advice/opinion**. Explain the evidence briefly. For inference/speculation that remains
uncertain, use Partly supported or Unverified and name the uncertainty. Recommend
specific corrected wording and a citation, or explain what evidence is still needed.
For a contradiction, show both the draft's value/claim and the source's correction.

Still check every marked sentence and material unmarked claim. Summarize passing
results concisely, such as "36 marked sentences checked; no factual corrections
needed; worked-example calculations verified." Do not print a sentence-by-sentence
pass table, duplicate all sound advice, or list correct calculations unless needed
to explain an actionable issue. Include verdict counts only when useful.

If there are no labels, say "No [Inference], [Speculation], or [Unverified] notes found
in the selected tab." This does not skip material unmarked-claim verification or
certify every sentence. Report actionable unmarked findings with the same columns.
State material source-access or coverage limitations separately from passed checks;
never imply that an unchecked claim has been verified. Provide the full per-sentence
audit trail only when the user explicitly asks for it.

## Remove verified tags in the Google Doc

This is a **pre-authorized edit**: after verification, remove `[Inference]`,
`[Speculation]`, or `[Unverified]` from the verified sentence in the selected article
tab. Keep the sentence itself exactly as written. No extra confirmation is needed
for this tag-only cleanup. All sentence rewrites and factual corrections remain
advisory unless separately authorized.

- Remove a tag only when the **entire sentence or block it annotates** has been
  verified. Evidence for premises alone, plausible inference, reasonable advice,
  hypothetical input values, or a prediction is not proof of a factual outcome.
  A verified calculation verifies its arithmetic, not invented business inputs.
  A sentence explicitly describing a hypothetical example can be verified as such
  without treating the example as observed merchant data.
- Keep the tag when evidence is partial, conflicting, inaccessible, outdated, or
  absent, when the sentence requires a rewrite to become accurate, or when user
  confirmation/internal data is needed. Mere acceptance as advice/opinion does not
  qualify automatically. Mark these as needing user review and retain the tag until
  the user verifies the specific sentence. Silence or elapsed time is not verification.
- If the user explicitly verifies a sentence, record that user-supplied confirmation
  as its basis and remove that sentence's tag. Do not describe user confirmation as
  independent external verification or clear other unrelated tags.
- If a tag covers several sentences or claims, remove it only after all are cleared.
  For an ambiguous standalone note, keep it pending scope clarification.
- Remove only the tag token and directly adjacent redundant spaces needed to keep
  spacing natural. Preserve every sentence, uncertainty qualifier such as "may" or
  "could", link, heading, table, formatting, and all unrelated content. Do not replace
  the tag with other visible text or add a citation to the Doc without authorization.
- Make an allowlist of the exact verified sentences/tags and their verification basis.
  Re-read the live tab before editing, use exact paragraph/text-run indices including
  table cells, and plan tag-only ranges. Never globally replace all three labels.
  Use the shared helper's targeted `replace` after a dry run, or `gdocs.guarded_batch` for tag-only deletions in descending index order with the selected tab ID. If the text or revision changed, refresh and recompute the plan.
- Read back after applying: verify the intended tags are gone, sentence text and links
  are preserved, and every unresolved tag remains. Re-running must not remove more
  tags without new verification. If writing fails or edit access is absent, report
  the unapplied cleanup; do not claim the tags were removed.

In chat, give only a short cleanup count (removed versus retained for user review),
then detail the unresolved claims that need attention under the reporting rules above.
Do not print a long list of verified sentences just because their tags were removed.
