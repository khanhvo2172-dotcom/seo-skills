# Step 5 — AI tracking params in links

**Goal:** writers draft with AI tools, and links copied from them often carry the
tool's tracking param, e.g. `https://help.shopify.com/...?utm_source=chatgpt.com`.
These must never be published. This step **detects and removes** them — it is
pre-authorized cleanup (the user asked for removal to be automatic), so it edits
the Doc in place.

## What counts

- A `utm_source` query param whose value names an AI tool: chatgpt, openai,
  claude, anthropic, perplexity, gemini, bard, copilot, deepseek, grok, you.com,
  phind, meta.ai (case-insensitive; `chatgpt.com`, `claude.ai`, etc. all match).
- Checked in **link URLs** (paragraphs *and* table cells) and as **visible text**
  (e.g. a literal `?utm_source=chatgpt.com` pasted into the anchor or body).
- **Only that one param is removed.** Every other param stays — in particular our
  own `utm_source=trueprofit.io&utm_medium=blog&utm_campaign=...` on CTA/app links
  is not an AI param and must be left intact. If the AI param was the only one,
  the `?` goes too.

## How to run it

```bash
# from scripts/ — pass the FULL doc URL so ?tab=t.xxxx is honored
python strip_ai_utm.py --doc "<DOC_URL_WITH_?tab=...>"           # dry-run: list hits
python strip_ai_utm.py --doc "<DOC_URL_WITH_?tab=...>" --apply   # strip them
python strip_ai_utm.py --doc "<DOC_URL_WITH_?tab=...>"           # re-run: expect 0
```

Run the dry-run, then `--apply` straight away (no confirmation needed), then the
dry-run again to verify zero remain. If the header warns the tab fell back to the
first tab, stop and confirm the tab first.

## Report

One table per doc that had hits — anchor text, before → after URL (dedupe repeated
links; a link split across several text runs is one link). Docs with no hits: one
line, "no AI tracking params." Never claim a removal unless the `--apply` run
printed `APPLIED` and the verify run shows 0.
