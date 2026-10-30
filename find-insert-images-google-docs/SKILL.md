---
name: find-insert-images-google-docs
description: Find real app screenshots, product photos and marketing campaign examples for articles; insert or replace them in Google Docs and write natural contextual captions. Use for article image sourcing, section-by-section examples and caption revisions. Generated illustrations use the existing illustration workflow.
---

# Find and Insert Article Images

Source authentic examples that support an article, then complete any authorized Google Docs insertion and caption work. This skill captures Khanh's approved workflow for TrueProfit articles on this PC.

## Read the article and preserve scope

- Read the shared memory index and relevant image/caption memories. Read the current guide at `E:\.trueprofit-claude-codex\shared\tools\gdocs\README.md` before a Docs operation.
- Use the shared `gdocs.py` helper for **all** Docs reads and edits. No browser edits or one-off Docs API scripts. Browser tools are appropriate for source websites and screenshots.
- List tabs and read the live article. The default article tab is **Final**; a `tab=t.0` link usually points to the outline. Honor an explicitly requested different tab.
- Build an image-to-heading map from the requested sections. Follow the user's heading selection/count; do not add images to budget, measurement or FAQs merely because they exist. Read each section before choosing an example.
- Inventory existing images and captions. Reuse approved assets and preserve prior corrections, including replacements. A request to add descriptions to existing images does not require sourcing or uploading them again.
- A sourcing-only request produces images, sources and useful caption suggestions. Insert when requested or already authorized in the conversation; no redundant confirmation. A request to create this skill does not authorize a live article edit.
- Save task assets under `E:\.trueprofit-claude-codex\workspaces\<task>\`, or continue the existing task folder. Preserve originals and prior approved versions.

## Choose a source that matches the example

| Article need | Preferred evidence |
|---|---|
| Introduce an app/tool | Screenshot its official homepage, relevant feature page or Shopify App Store listing. |
| Show a product | A clean manufacturer/retailer product photo without a watermark or visible logo. Choose another photo when unsuitable. |
| Explain a marketing strategy/campaign | The actual campaign creative, email, landing page or a useful screenshot/still from the named campaign. |
| Explain a concept that needs an original diagram | Use the existing illustration-generation workflow when requested; do not present generated work as an authentic campaign screenshot. |

Search the web and open the source page to establish what the image actually represents. Prefer official brands, agencies or app listings; reputable campaign archives and editorial sources are also useful. Record the source page separately from the direct image URL. Inspect the campaign/year, product, feature and offer rather than relying on an image-search caption.

Brand identity can be necessary in app/campaign examples; the product-photo no-logo preference is not a blanket ban on campaign branding. Avoid added watermarks. For videos, prefer official stills or original-resolution thumbnails and accurately identify later uploads; do not label a modern thumbnail as an untouched historical master frame.

Keep screenshots focused on the relevant page or creative, with readable content and no obstructing consent dialogs, unrelated menus, personal data or playback controls. Do not bypass access restrictions. If the direct download fails, try a legitimate source-page screenshot or another source.

## Check the actual asset

- **Horizontal images: at least 800 pixels wide. Vertical images: at least 600 pixels tall.** These are native source dimensions, not the size displayed in Google Docs. Do not enlarge an undersized image to make it pass. No separate square-image minimum was specified; choose a clear, suitably sized original.
- Save and inspect each selected file with an image viewer. Check relevance, text readability, cropping, watermark/logo rules and dimensions. Reject blurry or misleading material even when its dimensions pass.
- Use [scripts/check_images.py](scripts/check_images.py) to check saved dimensions, minimums and Google Docs format/size limits. It imports only the local helper's image-header reader; it makes no network or Docs calls. Example: `python -X utf8 <skill>/scripts/check_images.py <image1.png> <image2.jpg>`.
- Google Docs accepts PNG, JPEG and GIF; convert WebP to PNG before insertion. Follow current image-tool instructions when an edit is needed. Preserve the source and avoid manipulating actual campaign content into a misleading example.
- Store each image's exact heading, filename, source page, asset URL or screenshot provenance, original dimensions, contextual description, separate alt suggestion and insertion state in a task manifest. Add object ID and private Drive copy after insertion. A simple JSON record is sufficient; no copied source HTML or credentials in the skill package.

## Write context for readers

For caption work, read [references/contextual-captions.md](references/contextual-captions.md). Explain the campaign/story, the offer or product role, and why the image belongs in this section. Usually one concise sentence is enough. Do not just list visible objects and colors; keep that separate for alt text.

Native dimensions alone do not establish sharpness. Inspect detail and legibility at the intended article width; a larger screenshot of a blurry source does not restore detail. Choose a sharper native frame/source. Each screenshot should teach a distinct part of the task; explain separate field views or omit a redundant view when authorized. Prefer current authentic interfaces where recency matters, without relabeling an old source.

Captions are conditional: omit a description that merely repeats the neighboring instruction under a self-explanatory tool/dashboard image. Assess attribution separately and retain required Source credits. Preserve pending human caption deletions as suggestions unless their acceptance is authorized.

Keep historical and adapted examples accurate: a Black Friday email used as a Christmas-format example must be labeled Black Friday; an old delivery deadline is a historical example; a January thank-you discount is not automatically exclusive to Christmas purchasers. Avoid unsupported claims about sales, conversions or campaign success.

## Insert, replace or revise in the same Doc

Read [references/docs-operations.md](references/docs-operations.md) for the tested helper recipes relevant to the operation.

- Default placement: **at the end of the corresponding section**, before its next heading or Further Reading. An explicit sentence/heading placement overrides the default. Keep H2 and nested H3 image mappings distinct.
- Prefer this order: **image → natural contextual description → linked `Source: X` credit**. The description and source can share one paragraph when that matches the article; otherwise use a separate clean paragraph before the source. Preserve existing formatting and attribution when editing captions.
- Use `gdocs.py insert-image` for local assets. It automatically keeps a copy in Khanh's Drive under **TrueProfit Doc Images/<doc title>**, embeds it, then makes the Drive copy private again. Never use public file hosts, manual Drive uploads or browser insertion.
- Confirm the helper's Drive token exists without reading or printing it. If missing or the Drive step fails, stop that insertion and ask Khanh to run `gdocs.py auth-drive`; do not use the helper's public-host fallback.
- Start around **400 pt wide** for article examples unless the user/layout calls for another size; preserve proportions. This is a working default, not the pixel minimum. Check tall portraits for sensible page fit.
- Every write needs a successful dry run first. Inspect the plan, then apply. The user's insertion instruction supplies authorization; a dry run is not another user approval step.
- On a revision conflict, reread live state and rebuild the affected plan. After a timeout/uncertain write, inspect the Doc before retrying to avoid duplicates. Stop on failed readback/Drive verification and report the actual state.
- For a replacement, use the helper's image-object replacement support and update the affected description/source. Preserve other images, prose and sections.

## Verify and report

Use a fresh helper dump after the writes. Verify expected image/caption counts, each heading-to-image placement and exact description/source; compare against the baseline after removing only the intended additions or replacements. Preserve unrelated text, headings, tables, links, other tabs and existing image IDs. Review the helper's per-write checks and private-again Drive confirmation. Do not claim rendered-page inspection unless it occurred.

Report completion concisely with the Doc link, number of images/captions completed and any material limitation. Include the automatic Drive copy/folder link when inserting local images. For sourcing-only work, provide accessible image/preview links and original dimensions, with direct source-page attribution. A gallery or ZIP is useful for several images when it helps delivery, not mandatory for a single edit.

Update existing shared project memory with completion state and preserve new user corrections before the final answer. Do not publish to the CMS, add unrelated triggers or modify another article unless requested.

## Preferred TrueProfit dashboard

For TrueProfit in-app dashboard examples, use Khanh’s selected official asset: `https://be.trueprofit.io/uploads/trueprofit-dashboard-1-1.webp` (native 1810 × 869). Convert WebP to PNG without resizing for Google Docs, then use the shared helper’s private Drive insertion/replacement workflow. Inspect the asset before captioning; describe its actual revenue/net-profit/cost comparison, not a previous negative-profit example, and identify demo figures accurately. This preference concerns authentic dashboard examples, not explanatory illustrations.
