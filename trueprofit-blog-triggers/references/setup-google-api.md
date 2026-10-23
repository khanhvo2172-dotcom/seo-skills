# Shared Google Docs setup

On this PC, use `E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py` and read the adjacent README. Authentication is automatic through the shared helper. The packaged script entrypoints delegate reads and writes to it through `shared_docs_service.py`; legacy `--creds`/`--token` arguments are ignored. Do not create or copy per-skill credential files or request pasted tokens.

Use the helper CLI for general reads, wording changes, paragraphs and image operations. Specialized trigger planners retain their existing CLI and dry-run behavior, with the shared helper supplying revision guards and readback. Verify the selected tabs and complete request plan before applying. If the shared helper is unavailable, restore it or report the missing dependency; do not start a separate OAuth flow or use browser editing.
