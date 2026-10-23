---
name: suggest-internal-links
description: Suggest TrueProfit internal links by outline heading using the content-plan sheet, pillar hierarchy, relevant free tools and core metrics. Use for internal-link planning after outline/FAQ reviews or when adding link tables and Further Reading recommendations to Google Docs outlines.
---

# Suggest Internal Links

Create a focused internal-link plan for each requested TrueProfit outline. Map useful URLs to the existing headings, without recommending anchor text. Add 2-3 Further Reading suggestions that cover relevant pillar or sub-pillar pages missing from the body recommendations.

## Read the live sources

Use the content strategy spreadsheet:
https://docs.google.com/spreadsheets/d/1M7WrRKoFbOHdozAT5JU-ge-rQgH566yZ7FgDcWy2oGY/edit

- **Content Plan 10/2026:** match each document by its Google Docs URL, then confirm its topic/main keyword. Read **Content Themes & Pillars** and **Content Cluster**. If the user specifies another planning month, use that tab; inspect live tab names and headers rather than assuming the columns have not changed.
- **Internal Links:** read **URLs**, **Themes**, **Clusters (Fulfill)** and **Notes**. Notes identifies **Pillar Page** and **Sub Pillar Page**. Do not substitute the separate Clusters column or sx grouping for Clusters (Fulfill), or assume that the first URL in a cluster is its hub.
- **Outline document:** inspect tab metadata, including child tabs, and read the outline-containing tab. Match the linked tab when appropriate. Preserve the current H2/H3 wording, approved FAQ decisions and writer notes. Do not use a finished-article tab or flattened all-tabs export as the outline.

For the spreadsheet, use available authenticated Google connectors or an already-authorized Sheets API method. For Google Docs, Use the shared `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` helper for every Docs read/edit; read its adjacent README first. Use `tabs` and a separate `dump --tab <title-or-id>` per source. Do not use browser editing, a flattened all-tabs reader or a one-off Docs API script. For tables/styles or other operations beyond the CLI, use the README's `gdocs.read`/`gdocs.guarded_batch` module interface, with a fresh revision and explicit tab IDs. Dry-run or inspect the exact request plan before applying, then read back text, links, formatting and unchanged sibling tabs. Reuse documented local access without printing credentials or embedding credential paths/secrets in generated artifacts. If a source is inaccessible, identify the missing input and continue useful work on accessible documents; do not invent classifications or claim completed writes.

## Select and map the links

Apply this priority order:

1. Include at least one link to the topic theme's designated **Pillar Page**.
2. Include relevant designated **Sub Pillar Pages in the same cluster**. Preserve these hierarchy links when adding tools or metric references.
3. Look for useful **Sub Pillar Pages in the same theme**, including other clusters.
4. Add other closely relevant pages from other themes/clusters when they help the reader perform the heading's task.

Verify pillar labels from the live Notes column. If a theme/cluster has no designated pillar or sub-pillar, briefly flag the gap. A useful supporting article can still be selected, but do not label it a pillar or invent a hub to satisfy the hierarchy.

Map the links to actual headings, including meaningful H3s and individual FAQs. Place a link at the most specific useful heading. A parent H2 need not repeat a URL already mapped to its H3. Do not add article headings or rewrite the outline just to create placements.

Keep the plan selective:

- Recommend no link where no close match exists; do not force one URL into every heading.
- Prefer one placement per URL across the body and Further Reading. Multiple URLs under one measurement/tools heading are appropriate when they have distinct purposes.
- Use a topic-specific tool instead of a general supporting article when it better completes the task. Avoid accumulating loosely related links.
- Do not recommend anchor text or add an anchor-text column.
- Do not present unpublished drafts or guessed slugs as live destinations. Flag a future cross-link separately until its published URL is verified.
- Check selected pages load and cover the promised subject. Inspect redirects, titles and relevant content; do not rely solely on a slug or status 200. Keep frontend blog links in the form https://trueprofit.io/blog/slug, without be. or a trailing slash; preserve the supplied tool paths.

Example: Shopify competitor analysis belongs to SHOPIFY KNOWLEDGE / Shopify Growth & Marketing. The theme pillar is https://trueprofit.io/blog/what-is-shopify. The same-cluster sub-pillars are https://trueprofit.io/blog/best-selling-products-on-shopify and https://trueprofit.io/blog/shopify-marketing-strategies. Confirm this classification live before reusing it.

## Include tools and core metrics where useful

Read [references/tools-and-metrics.md](references/tools-and-metrics.md) when selecting a calculator, detector or measurement reference. It contains the user-provided URL inventory and topic-specific priorities.

Prioritize the general profit-margin calculator for relevant profit estimates, the Dropshipping/POD versions for those themes, and the ROAS calculator for advertising tracking. A calculator does not replace the relevant core-metric guide or required hierarchy link when those serve different reader needs.

For headings such as How to Measure and Improve Advertising, link to the core metrics actually discussed: ROAS, profit, CAC and other applicable metrics. Use definition/formula guides where explaining a metric, and benchmark/comparison guides only when that coverage exists. Do not insert all possible metric URLs by default. Keep optional references clearly conditional and separate from the required/default placements.

## Use Further Reading to fill hierarchy gaps

After mapping body links, identify relevant **Pillar Pages or Sub Pillar Pages not already linked there**. Suggest 2-3 for one Further Reading box, prioritizing missing hubs in the current theme/cluster, then useful hubs in other themes/clusters.

Verify every selected hub's role in Notes and explain its theme/cluster relevance briefly. Do not fill the box with ordinary supporting posts, tool links or benchmark articles merely because they are related. Those belong with the headings they support. If fewer than two suitable missing hubs exist, report the gap and suggest the justified ones rather than pad the box or repeat body URLs.

Give one sensible box placement within the planned article. This placement recommendation is distinct from where the link-plan section itself is stored in the outline document.

## Deliver in the existing outline file

For the established TrueProfit workflow, a request to suggest links for supplied outline files means put the results in those files. Honor an explicit request for chat-only recommendations. This skill does not authorize publishing or editing the CMS, changing the source spreadsheet, or rewriting article content.

In the outline-containing tab, add or update **Internal Link Suggestions**, usually after the outline/FAQs and before saved AI Overview, AI Mode or other research material. Use:

| Outline heading | Suggested internal link | Purpose and placement |
|---|---|---|
| Exact heading text | Full clickable URL, or No link recommended | Concise reason and hierarchy/tool role when relevant |

Use a separate line for each URL when a cell contains several. Keep unlinked-heading notes brief. Under **Further Reading**, provide the 2-3 full clickable URLs, each hub's verified role/theme/cluster, and the recommended article box placement. Optional metric references may be listed separately with explicit conditions; do not turn them into additional article headings.

Update existing recommendation sections in place rather than append duplicates. Keep all unrelated document text, hyperlinks, comments, tables, images and tabs intact. Use fresh tab-aware structure and the shared helper's guarded batch with the revision from a read after the last write. On a revision conflict, reread and rebuild the intended edit; do not remove the revision guard.

Read back the edited section and verify its text and hyperlink targets. Confirm the outline and research material outside the edit remain intact. Match existing formatting; inspect the rendered added pages when available and keep table rows/heading groups readable across page breaks. If rendering is unavailable, say the layout was not visually checked. Do not claim a saved edit from an unverified or failed response.

Finish with a short result linking each named document. For a batch, a small table of documents and body/Further Reading link counts is sufficient. Mention material hierarchy/access gaps without repeating the complete plan in chat.
