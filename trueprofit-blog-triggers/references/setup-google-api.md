# One-time Google Docs API setup

The skill edits your Google Doc through the official Google Docs API. That needs
an OAuth "desktop app" credential the first time. ~5 minutes, done once.

## 1. Install the Python libraries

From this skill's `scripts/` directory:

```bash
pip install -r requirements.txt
```

## Fastest path: just set an env var

If you already have an authorized-user token (the JSON with `token` +
`refresh_token` + `client_id` + `client_secret`), you can skip the OAuth steps
below entirely — set it as an environment variable and the skill uses it:

```bash
export GOOGLE_TOKEN_JSON='{"token": "...", "refresh_token": "...", ...}'
```

This is the recommended way to use the skill in a fresh session (e.g. Claude.ai),
where there are no local credential files. The steps below are only needed the
first time, to mint that token.

## 2. Create an OAuth client (once per Google account)

1. Go to <https://console.cloud.google.com/> and pick (or create) a project.
2. **APIs & Services → Library →** search **"Google Docs API" → Enable**.
3. **APIs & Services → OAuth consent screen:** if prompted, choose **External**,
   give it any app name, add your own email as a **Test user**, save. (You don't
   need to publish/verify it — test mode is fine for your own docs.)
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →**
   Application type **Desktop app** → Create.
5. **Download** the JSON. Save it as:
   `C:\Users\khanhvv\.claude\skills\trueprofit-blog-triggers\scripts\credentials.json`

## 3. First run authorizes the token

The first time you run `gdocs_triggers.py`, a browser window opens asking you to
sign in and grant access to "See, edit, create, and delete your Google Docs
documents." Approve it. A `token.json` is written next to the script and reused
on every later run, so you only sign in once (until the token is revoked).

## Notes & gotchas

- **Scope is `documents`** (read + write a doc you can already open). The script
  never lists or touches other files.
- **The signed-in Google account must have edit access** to the target doc.
- `credentials.json` and `token.json` are secrets — they stay local in the
  `scripts/` folder and should not be committed or shared.
- If you ever get an auth error after a long gap, delete `token.json` and run
  again to re-authorize.
- Prefer a service account instead of interactive OAuth (for unattended/batch
  use)? Create a service account, download its key as `credentials.json`-style
  json, share the doc (or its Drive folder) with the service account's email,
  and swap `InstalledAppFlow` for `google.oauth2.service_account.Credentials`.
  Ask Claude to make that change if you want it.
