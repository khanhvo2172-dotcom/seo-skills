# One-time Google Docs API setup

This skill edits your Google Doc through the official Google Docs API (same auth
as the English `trueprofit-blog-triggers` skill). If you already set that up, the
same `token.json` / `GOOGLE_TOKEN_JSON` works here — copy the token file into this
skill's `scripts/` folder, or just set the env var. ~5 minutes, done once.

## 1. Install the Python libraries

From this skill's `scripts/` directory:

```bash
pip install -r requirements.txt
```

## Fastest path: just set an env var

If you already have an authorized-user token (the JSON with `token` +
`refresh_token` + `client_id` + `client_secret`), skip the OAuth steps below —
set it as an environment variable and the skill uses it:

```bash
export GOOGLE_TOKEN_JSON='{"token": "...", "refresh_token": "...", ...}'
```

This is the recommended way in a fresh session (e.g. Claude.ai), where there are
no local credential files. The steps below are only needed the first time, to
mint that token.

## 2. Create an OAuth client (once per Google account)

1. Go to <https://console.cloud.google.com/> and pick (or create) a project.
2. **APIs & Services → Library →** search **"Google Docs API" → Enable**.
3. **APIs & Services → OAuth consent screen:** if prompted, choose **External**,
   give it any app name, add your own email as a **Test user**, save.
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →**
   Application type **Desktop app** → Create.
5. **Download** the JSON and save it as `scripts/credentials.json`.

## 3. First run authorizes the token

The first run opens a browser to grant access to "See, edit, create, and delete
your Google Docs documents." Approve it; a `token.json` is written next to the
script and reused on every later run.

## Notes & gotchas

- **Scope is `documents`** (read + write a doc you can already open).
- **The signed-in Google account must have edit access** to the target doc.
- `credentials.json` and `token.json` are secrets — they stay local in `scripts/`
  and must not be committed or shared.
- If you get an auth error after a long gap, delete `token.json` and run again.
