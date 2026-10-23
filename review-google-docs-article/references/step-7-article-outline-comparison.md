# Step 7 - Compare the full article structure with the outline

## Purpose and scope

Use the outline as the baseline for heading and structure review. Detect missing or
incorrect parts in the finished article rather than proposing a new preferred outline.
Compare the selected article tab (usually Final) with the corresponding outline tab.
This pass is report-only; do not edit either tab without explicit authorization.

## Read the two tabs separately

- Honor the user's article and outline tab selections. If the article tab is explicitly
  named, resolve that title to its exact tab ID rather than trusting a conflicting URL.
- If no outline tab is specified, inspect tab names to locate a unique `Outline`,
  `Insights & outline`, or equivalent tab. Read only its identifiable article outline;
  research notes, references, alternative drafts, and rejected heading options are not
  the approved outline. Use the latest outline explicitly approved by the user.
- If the baseline is ambiguous, ask which outline to use and continue factual and
  other independent checks. If unavailable, report this comparison as incomplete;
  never invent the baseline or silently compare to an unrelated draft.
- Use the shared helper's `dump --tab <resolved-title-or-id>` separately for each tab, preserving links and table cells. Use its module interface for exact structure when needed. Never concatenate tabs or edit a sibling tab.

## Compare structure and coverage

1. Extract the outline's H1, H2, and H3 hierarchy in order, including the expected FAQ
   questions and any explicit section requirements (such as a comparison table).
   Recognize literal `H2:` / `H3:` labels and indented outline bullets even when they
   are not formatted as Google Docs headings.
2. Extract the full article's actual headings, order, and parent-child relationships.
   Distinguish a missing heading from text present with the wrong paragraph style.
3. Map every outlined section to the article, then check for:
   - Missing headings, subsections, FAQs, or explicitly required content blocks.
   - Wrong heading text or topic, incorrect heading level/parent, or incorrect order.
   - Additional or duplicate sections not present in the outline. Account for later
     user-approved changes before calling an addition a mismatch.
   - A matching heading with an empty, placeholder, incomplete, or off-topic body.
     Read the section to confirm that it actually delivers the outlined intent.
   - Required content placed under the wrong heading or merged into another section.
     Report where the content exists, rather than falsely calling it absent.
4. Normalize spacing, punctuation, and numbering only to help match headings. Quote
   exact outline and article wording in findings. Distinguish harmless wording/typo
   differences from a changed question, meaning, or required scope.
5. Do not treat normal article scaffolding (meta description, introduction, Quick
   Recap, References, Further Reading, CTA markers) as an unauthorized section solely
   because the outline omits it. Apply the existing checks for those elements.
   Do not suggest removing outline-approved headings just for stylistic preference.
   Keep the existing FAQ redundancy review separate and advisory; this comparison
   does not authorize cutting FAQs or change the other checks.

## Report in chat

Identify both tab names/IDs and the outline used. Give a concise overall match status,
then list actual discrepancies:

| Outline heading / required part | Article location / actual heading | Issue | Recommended correction |
|---|---|---|---|

Issue types: Missing, Wrong heading/topic, Wrong level/parent, Wrong order, Extra,
Duplicate, Missing heading style, or Incomplete/off-topic coverage. Recommend restoring
alignment with the outline, not a replacement structure. Include precise location and
wording so the author can apply the correction. If the structure and coverage match,
say so without inventing issues. Keep factual corrections in Step 6 with source evidence.
