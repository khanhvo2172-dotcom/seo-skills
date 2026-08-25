# last30days-mail

A fork of the [`last30days`](https://github.com/mvanhorn/last30days-skill) skill (MIT, © Matt Van Horn) that **also folds your own email inbox in as a private, first-party source** — on top of the original multi-source research (Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, web).

Invoked as `/last30days-mail <topic>`.

## What the mail addition does

The engine is a standalone subprocess and cannot call MCP, so the mail flow is split in two:

1. **Prefetch (done by the hosting agent):** read the filter config, query Gmail via MCP for mail matching **an allowlisted sender OR a chosen label** within the run window, and write a small `mail-items.json`.
2. **Ingest (done by the engine):** pass `--mail-items <file>`; the engine loads it as a private source — date-windowed, relevance-scored against the topic, ranked **deterministically only** (inbox text never goes to a hosted reranker), and **merged into the ranked evidence clusters** (not siloed). Inbox items render as **📬 Your inbox** and must be flagged as first-party at synthesis.

## Filter config

`~/.config/last30days/mail-filter.json`:

```json
{ "senders": ["newsletter@example.com", "@somedomain.com"], "labels": ["Newsletters"], "lookback_days": 30 }
```

A message qualifies if it matches **any** sender **or** **any** label. If the file is missing, the mail source is skipped.

## Fork changes vs upstream

New: `scripts/lib/mail.py`. Modified: `scripts/lib/pipeline.py`, `scripts/last30days.py`, `scripts/lib/render.py`, `SKILL.md` (see the "MAIL PREFETCH" section). Everything else tracks upstream `last30days`.

## License

MIT, inherited from the upstream project. Original © Matt Van Horn; mail additions © TrueProfit.
