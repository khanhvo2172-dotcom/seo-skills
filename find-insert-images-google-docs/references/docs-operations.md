# Tested operations with the shared Docs helper

Read the current `E:\.trueprofit-claude-codex\shared\tools\gdocs\README.md` first; it is authoritative for CLI behavior. The examples below show the image/caption choices specific to this workflow. Invoke the helper through structured subprocess arguments where possible, avoiding shell interpolation of captions, Unicode or URLs.

In these examples `$gdocs` is a PowerShell variable:

```powershell
$gdocs = 'E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py'
python -X utf8 $gdocs tabs DOC_ID
python -X utf8 $gdocs dump DOC_ID --tab Final --indices --out before.md
```

Read the live content and object IDs. The article normally lives in Final, not the outline tab named by a `t.0` link.

## Insert an image and contextual caption

Use a unique snippet in the final paragraph of the relevant section, or the exact next heading. Do not choose a generic sentence occurring in several sections.

```powershell
python -X utf8 $gdocs insert-image DOC_ID --tab Final --after 'Unique final paragraph text' --image 'E:\path\example.png' --width-pt 400 --caption 'Natural campaign context. Source: Publisher' --caption-link-text 'Publisher' --caption-url 'https://example.com/campaign'
```

Inspect the dry run, then repeat the same command with `--apply`. The caption link text must occur in the caption and only its intended source label should be linked. Keep captions passed to `--caption` in one paragraph; do not insert raw newlines into it.

The local-image upload must use the helper's Drive workflow. Check only token existence:

```powershell
Test-Path 'E:\.trueprofit-claude-codex\shared\tools\gdocs\.drive-token.json'
```

If absent or Drive upload fails, stop and ask Khanh to run `gdocs.py auth-drive`. Never print/copy the token or permit a fallback to public file hosts. After success, capture `drive_copy`, `drive_folder` and `sharing: private again`. Keep the Drive file; it is the article's image archive.

## Add descriptions to images already in the Doc

For an image followed by a source-only paragraph, combine the description and source in one centered caption when supported by the current helper. For a brief that explicitly requests separate paragraphs, a clean description can be inserted immediately before the source:

```powershell
python -X utf8 $gdocs insert-paragraph DOC_ID --tab Final --before-text 'Source: Unique Brand' --text 'Natural context explaining this example.'
```

Dry-run, inspect, then apply. Verify the source is immediately below the intended image before using it as an anchor. If a brand/source is repeated, do not guess an occurrence; choose another supported unique anchor or extend the shared helper safely. Never fall back to browser edits or a one-off Docs API script.

If a contextual description already exists, revise that text rather than adding a duplicate. The helper's `replace` command accepts a JSON list:

```json
[
  {"find": "Existing description sentence.", "replace": "Revised natural context sentence."}
]
```

```powershell
python -X utf8 $gdocs replace DOC_ID --tab Final --edits caption-edits.json
```

Inspect the plan and repeat with `--apply`. Match only the unlinked description; do not span into the linked source name, another style run or a newline. The helper refuses matches that cross formatting boundaries.

## Caption alignment and source-link overrides

Center the caption paragraph beneath the intended image. Keep the description and `Source: Publisher` on the same paragraph unless the current brief asks otherwise. A single paragraph may wrap naturally; do not shrink the text to force one visual line.

The insertion CLI has no caption-alignment option. For formatting beyond the CLI, use the shared helper's `read` / `guarded_batch` module interface, explicit tab IDs and a fresh revision. Limit `updateParagraphStyle` to the actual caption paragraph with `alignment: CENTER`; do not center adjacent article prose or labels drawn inside the image. Inspect the request plan before applying and verify the paragraph style afterward.

Retain a linked source by default, with only its label linked. For an explicit request to remove source hyperlinks, omit `--caption-url` and `--caption-link-text` on new insertions. For existing credits, clear only the requested source text's link through the helper's guarded write; keep the source name, description and other article links. Preserve the original URL in task notes. When combining existing description/source paragraphs, preserve any source link that the user has not asked to remove.

## Replace a small or unsuitable image

Get the image's object ID from a fresh `dump --indices`, then use the paragraph immediately above the image:

```powershell
python -X utf8 $gdocs insert-image DOC_ID --tab Final --after 'Unique paragraph immediately above the image' --replace-image-id kix.OBJECT_ID --image 'E:\path\larger-example.png' --width-pt 400 --caption 'Updated contextual description. Source: Publisher' --caption-link-text 'Publisher' --caption-url 'https://example.com/campaign'
```

The existing image must be standalone and immediately after the anchor. Alternatively, use `--before-heading` or `--before-text` immediately after the old image and optional Source caption when another image is immediately above it; consult the current README. The helper replaces the old image and an immediately adjacent Source caption in one guarded batch. **It does not automatically remove a separate descriptive paragraph between image and source.** Inspect adjacency first: when such a paragraph exists, update it/source separately through supported operations or make a focused reusable helper improvement before replacing. Avoid leaving stale context or duplicate credits.

Dry-run first. Verify the old object is gone, the new one occupies the intended section, the new source/caption are correct and unrelated images are preserved. Keep the original local file/version and existing private Drive archive; do not delete them as cleanup.

## Move or compare existing images

For a relocation, use `insert-image --move-image-id kix.OBJECT_ID` with the original asset, caption and destination anchor. Dry-run first; the shared helper moves the standalone image and adjacent Source caption atomically. Do not combine move and replace options. If the user asks for a visual comparison, keep the approved image and insert the revision below it instead.

## Verify the exact change

Read a fresh helper dump after the writes. For description additions, remove only the expected new description paragraphs from the readback and compare to the baseline; the remaining article should match. For replacements or revisions, construct the expected result from the approved changes. Compare image counts/IDs, heading mapping, caption paragraph alignment, description/source adjacency, source-link presence or explicitly requested removal, and table content as appropriate.

Review `text_ok`, `image_ok`, `links_ok` and `other_tabs_unchanged` for insertions, or `text_matches_plan` and `link_urls_unchanged` for replacements of wording. Do not retry a timed-out write blindly. Snapshot logs are in `shared/tools/gdocs/logs/`; task-specific manifests, before/after dumps and completed-state records help prevent duplicate insertions on continuation.
