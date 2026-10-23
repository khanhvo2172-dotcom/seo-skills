---
name: compare-ggdocs-multilingual-tabs
description: "Compares the first tab of a Google Docs article with its multilingual tabs named Spanish Version, German Version, and French Version. Use this skill whenever the user asks to compare, diff, check, audit, or detect differences between a source Google Doc tab and localized Spanish, German, or French tabs. This skill skips translated body text comparison and focuses on link rules from compare-content-between-ggdocs-live-url, heading counts by level, FAQ counts, data benchmarks, formatting, section ordering, CTA/product mentions, and structural consistency."
---

# Compare Google Docs Multilingual Tabs

## Required inputs

Use this skill when the user provides a Google Docs URL for a TrueProfit blog article that includes:

- A first tab containing the source article.
- Three localized tabs named exactly or nearly exactly:
  - `Spanish Version`
  - `German Version`
  - `French Version`

If one of the three localized tabs is missing or renamed, report it before comparing the available tabs.

## Workflow

### 1. Fetch the Google Doc

Use `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` after reading its adjacent README: list tabs, then dump each selected tab separately. Do not use an all-tabs Drive export, browser editing or a one-off Docs API script.

- Resolve the English article source from the user's explicit selection, otherwise prefer **Final**. A `tab=t.0` link usually points to the outline. Use the first tab only when it actually contains the source article; never compare translated prose to outline notes. Below, “first tab” means this resolved English source, regardless of its position.
- Compare only against the tabs named `Spanish Version`, `German Version`, and `French Version`.
- Ignore unrelated tabs such as outlines, research, SERP notes, content briefs, CMS notes, images, or old drafts.
- Preserve each tab's heading hierarchy, link targets, ordered list structure, table rows, and FAQ blocks while extracting content.

### 2. Skip translated text comparison

Do not compare sentence text, paragraph text, or translated wording against the first tab. The Spanish, German, and French tabs are translated versions, so body text will be substantially different by design.

Skip:

- Intro paragraph wording.
- Body paragraph wording.
- FAQ question wording and answer wording.
- Translated CTA wording.
- Normal localized punctuation, quotation marks, grammar, and phrasing.

Still compare structural and factual elements:

- Link presence, anchor placement, and target URLs.
- Heading counts by level.
- FAQ counts only.
- Data benchmarks and numerical claims.
- Section presence and order.
- CTA/product mentions and Shopify app links.
- Formatting differences that are visible and meaningful.

### 3. Compare systematically

Check each localized tab against the first tab in this order:

1. Meta description presence, when available in the tabs. Do not compare translated wording.
2. H1 presence and count.
3. Intro paragraph links only.
4. Quick Recap or summary box.
5. Heading counts for each level H1-H6. Report the number of H1, H2, H3, H4, H5, and H6 headings in the first tab and in each localized tab. Flag mismatched counts by level.
6. Section order and presence. Do not compare paragraph wording inside sections.
7. Internal links: check body-text link presence, anchor text role, and target URL only. Skip Further Reading blocks entirely. Skip empty-anchor or image-wrapped Shopify App Store links added by the live site, especially URLs using `utm_campaign=in-blog-banner-*`.
8. Data benchmarks. Always include these in the result table, even when identical in meaning. Cover margin percentages, AOV, per-product metrics, cost ranges, pricing data, and numerical claims or statistics.
9. FAQs. Always include these in the result table, even when identical. Check only the total number of questions and the total number of answers. Do not check FAQ order, question wording, or answer wording.
10. Formatting differences such as bold and italic when visible in comparable structural elements. Do not flag localized punctuation differences.

### 4. Handle structural rewrites

If a localized tab is fundamentally different from the first tab, do not force a line-by-line diff.

- State clearly: `Major structural rewrite detected` or `This localized tab is a different article`.
- Summarize high-level differences such as title, section structure, product count, benchmark coverage, and FAQ coverage.
- Continue comparing the other localized tabs if possible.

### 5. Apply known comparison rules

- Localized Spanish, German, and French tabs may convert USD to EUR. Treat this as expected unless the conversion math is wrong. Do not require conversion when the localized tabs intentionally keep USD values.
- If the source tab says one year and all localized tabs say another year throughout, report it once as a bulk year mismatch.
- Do not flag ordinary translation wording or punctuation differences.
- Flag bold or italic differences as formatting differences when visible in the tabs.
- Do not report automated CMS-only image/banner CTA differences unless the user explicitly asks to audit CTAs or tracking links.

## Output

If no differences exist across all three localized tabs, respond exactly:

```text
No
```

If differences exist, present one table where each row is a comparison section and each language is a column:

| Section | English Version | Spanish Version | German Version | French Version | Note |
|---|---|---|---|---|---|
| Heading counts (H1-H6) | H1: 1, H2: 5, H3: 26, H4-H6: 0 | H2 +20; H3 -23 | H2 +1; H3 -4 | H2 +20; H3 -23 | Spanish/French product headings use H2 instead of H3. |

Use the columns as follows:

- `Section`: The compared area, such as heading counts, internal links, data benchmarks, FAQs, or section order.
- `English Version`: The first tab's full baseline value.
- `Spanish Version`, `German Version`, `French Version`: Use `Same` when the localized tab matches the English baseline for that section. When it differs, state only the direct difference instead of repeating full details. For heading counts, use concise deltas such as `H2 +20; H3 -23`, not full heading-count lists.
- `Note`: Briefly state the mismatch, `No difference`, or any uncertainty.

Always include these rows, even when they match:

- `Data benchmarks (margins, AOV, etc.)`
- `Heading counts (H1-H6)`
- `FAQs ([N] questions, [N] answers)`

After the table, list any uncertainty separately, such as unclear currency conversion, unclear link destination, or a missing/renamed localized tab.
