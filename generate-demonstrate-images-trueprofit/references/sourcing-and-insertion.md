# Real visuals and article insertion

Apply this reference when the request includes finding existing images, taking screenshots or inserting images into an article. A full article can benefit from a mixture of real examples and generated explanatory graphics.

## Choose the source by purpose

| Section content | Preferred visual |
|---|---|
| App introduction | Screenshot the official app homepage or Shopify App Store listing |
| Product example | Find an appropriate real product image without a watermark or logo |
| Marketing strategy or campaign example | Find the actual campaign/example online and use a relevant existing image or screenshot |
| Concept, process, definition, benchmark or comparison | Generate a clear explanation using the matching TrueProfit design reference |

The no-logo preference applies to sourced product-example images. App/campaign screenshots may legitimately contain brand identity. Select a clean source rather than stripping watermarks. Use real evidence for real examples; do not fabricate an app interface or campaign screenshot.

Use browsing and available screenshot tools for authentic examples, prefer official/primary sources, and record source page URLs. Inspect each chosen image yourself. Relevance, readable content and article context matter more than merely matching a keyword.

## User-supplied document references

These URLs were supplied as examples of the desired sourcing approach; their contents were not inspected during skill creation. Open them only when useful for the current request, using the shared gdocs.py helper.

- App screenshots: https://docs.google.com/document/d/1QJf1fCpkxRkWkyQrvMXiBWZTk3_QQm2ndAlppjhANMU/edit?tab=t.0
- Product examples: https://docs.google.com/document/d/13PXdyKoaS-SOUHCsUvm1o2OHHW9_6Tl589nsjmEYbvs/edit?tab=t.ut4h3jqs487y
- Campaign examples: https://docs.google.com/document/d/176aJkJr1DLvofx5ip4Dvhokt1mRVvEEQzo02EGTsr6I/edit?tab=t.icxjojukvkkp

These are references, not default write destinations.

## Placement and insertion

When planning a whole article, use a compact placement list with the target heading, what the visual explains and the selected source/type. Do not stop at planning when the request already asks for execution.

For an authorized insertion:
1. Read `E:/.trueprofit-claude-codex/shared/tools/gdocs/README.md` and use its `gdocs.py` helper for every Docs read/edit. List tabs; prefer **Final** for the article unless explicitly selected otherwise. A `tab=t.0` link usually points to the outline. Never edit through the browser or a one-off Docs API script.
2. For sourced examples, require native width >=800 px for horizontal images or native height >=600 px for vertical images. Inspect the actual file and do not upscale a small source to pass. Use `find-insert-images-google-docs` for the detailed sourcing/caption workflow when available.
3. Insert at the corresponding section end unless a specific placement was requested. Use `gdocs.py insert-image` for local assets: it saves a copy in **TrueProfit Doc Images/<doc title>**, embeds it, and makes the retained Drive copy private again. Include the reported Drive copy/folder link. If Drive authorization is missing/fails, stop that insertion and ask for `gdocs.py auth-drive`; never use a public-host fallback or manual upload.
4. Visible captions explain the campaign/story and section relevance naturally. Keep literal visual description separate as an alt suggestion, and preserve linked source attribution. The Docs API cannot set inline-image alt text; do not claim otherwise. CMS image-trigger alt text follows the existing trigger workflow.
5. Dry-run first, inspect, then apply within existing authorization. Use atomic `--replace-image-id` or `--move-image-id` when replacing/relocating a standalone image and adjacent Source caption; inspect adjacency and the current README. If Khanh asks to compare versions, retain the original and insert the new version below it instead of replacing.
6. Verify the exact images, location, order, native proportions, surrounding text/links, other tabs and private Drive copy. After a timeout, inspect the live document before retrying; on a revision conflict, reread and replan.

If the available tool cannot embed an image, deliver the finished workspace assets plus exact placements and state that insertion remains incomplete. Do not describe a mere hyperlink or placeholder as an embedded image. Do not upload, publish or change a CMS when only a document insertion was requested.
