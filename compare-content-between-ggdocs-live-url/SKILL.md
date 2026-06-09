---
name: compare-content-between-ggdocs-live-url
description: Compares the content of a TrueProfit blog article between its Google Docs source and its live URL on trueprofit.io. Use this skill whenever the user asks to compare, diff, check, or detect differences between a Google Doc tab and a live blog page. Also trigger when the user says things like "check if the live page matches the doc", "any differences between doc and URL", "compare doc vs live", "is the content synced", or provides a pair of Google Docs URL plus trueprofit.io blog URL. This skill covers text, links, data benchmarks, FAQs, formatting, and section ordering comparisons.
---

# Compare Content Between Google Docs and Live URL

## Required inputs

Use this skill when the user provides:

- A Google Docs URL, optionally with a `?tab=t.xxxx` parameter.
- A live TrueProfit blog URL, usually `https://trueprofit.io/blog/...`.

Optionally use an uploaded raw HTML file, usually named like `view-source_*.html`, to verify callout block content that markdown extraction misses.

## Workflow

### 1. Fetch the Google Doc source

Read the Google Doc content with the available Google Drive file-reading tool, using the file ID from the Docs URL.

- Compare only the specific tab or section the user shared.
- If the Docs URL includes `?tab=t.xxxx`, treat that tab as the source of truth.
- If there are multiple content versions such as `Content 2025`, `Content 2026`, localized tabs, research, SERP, or outline tabs, ignore unrelated tabs.
- If no tab is explicit but the live URL or title implies a year, choose the content version matching the live article year.

### 2. Fetch the live article

Fetch the live TrueProfit URL as markdown when possible.

Compare only the article body:

- Start at the H1 heading.
- End just before the author bio section, identified in HTML as `div class="style_wrap-bio__oleBA wrap-bio"`.
- Include the FAQ section.
- Exclude navigation, header menus, footer, related blogs, sidebar CTAs, newsletter signup, and other site chrome.

### 3. Account for markdown extraction limits

TrueProfit custom styled callout blocks are often present in raw HTML but missing from markdown extraction. These include Note, Example, Notice, Tip, Quick Recap, and highlighted summary boxes.

- If the Google Doc has Quick Recap or callout content missing from live markdown, check the uploaded raw HTML before reporting it as missing.
- If raw HTML is available, search it for the exact callout text, nearby headings, and relevant link targets.
- If no raw HTML is available, report likely callout issues as: `Likely present in a callout block on the live page; raw HTML is needed to confirm exact wording.`
- Do not mark callout content as missing with high confidence unless raw HTML confirms it is absent.

### 4. Compare systematically

Check these elements in order:

1. Meta description, when available in both sources.
2. H1 title.
3. Intro paragraphs, including links.
4. Quick Recap or summary box.
5. H2/H3 section headings, hierarchy, and order.
6. Body text within each section.
7. Internal links, including anchor text and target URL.
8. Data benchmarks. Always include these in the result table, even when identical. Cover margin percentages, AOV, per-product metrics, cost ranges, pricing data, and numerical claims or statistics.
9. Further Reading or related links blocks, including URL, anchor text, and order.
10. FAQs. Always include these in the result table, even when identical. Check count, question text, and answer text.
11. CTA sections, TrueProfit product mentions, and Shopify app links.
12. Formatting differences such as bold, italic, punctuation, em dashes, commas, and semicolons.

Do not report automated in-article image/banner CTAs as differences. Skip empty-anchor or image-wrapped Shopify App Store links added by the live site, especially URLs using `utm_campaign=in-blog-banner-*`, unless the user explicitly asks to audit CTAs or tracking links.

### 5. Handle structural rewrites

If the live URL is fundamentally different from the Google Doc, do not force a line-by-line diff.

- State clearly: `Major structural rewrite detected` or `This is a completely different article`.
- Summarize high-level differences such as title, product count, section structure, and FAQ coverage.
- Ask whether the user wants a detailed comparison or whether the rewrite was expected.

### 6. Apply known comparison rules

- Localized Spanish, German, and French articles may convert USD to EUR. Treat this as expected unless the conversion math is wrong.
- If the doc says one year and the live page says another year throughout, report it once as a bulk year update instead of listing every occurrence.
- Always verify Further Reading order; order differences matter.
- Flag em dash versus comma, semicolon, or other punctuation changes as punctuation differences.
- Flag bold or italic differences as formatting differences when visible in the sources.

## Output

If no differences exist, respond exactly:

```text
No
```

If differences exist, present a table:

| # | Section | Google Docs | Live URL | Type |
|---|---------|-------------|----------|------|
| 1 | Location | What the doc says | What the live page says | Text / Link / Punctuation / Formatting / Missing / Order / No difference |

Always include these rows, even when they match:

- `Data benchmarks (margins, AOV, etc.)`
- `FAQs ([N] Q&A pairs)`

After the table, list any items that need raw HTML verification separately.
