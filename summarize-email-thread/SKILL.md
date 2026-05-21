---
name: summarize-email-thread
description: "Searches Gmail for email threads related to a link exchange partner (by domain, email address, or subject keyword) and produces an instant briefing: who the partner is, what was agreed, current link placement status, last contact date, and the recommended next action. Use this skill whenever the user wants to look up a link exchange partner, recall email history with a partner, check the status of a link swap, or needs context before replying to a partner email. Also trigger when the user says things like 'what did we agree with X', 'catch me up on X', 'what is the status with X', or 'I got a reply from X'."
---

# Summarize Email Thread - Link Exchange Partner Briefer

## Purpose

Search Gmail for all threads related to a link exchange partner and return a structured briefing so the user can reply without re-reading full thread history.

## Required MCP

- Gmail MCP (`https://gmailmcp.googleapis.com/mcp/v1`)

---

## Workflow

### Step 1 - Identify the search query

Extract the search identifier from the user's message. It may be:
- A domain name (e.g. `ahrefs.com`, `neilpatel.com`)
- An email address (e.g. `john@example.com`)
- A subject keyword (e.g. `link exchange`, `collaboration`)
- A person's name

If unclear, ask: *"What's the partner's domain, email, or a keyword from the subject line?"*

### Step 2 - Search Gmail

Use Gmail MCP to search for threads. Use multiple search queries to maximise recall:

```text
"{domain or keyword}" link exchange
"{email}"
subject:"link" "{domain}"
```

For each relevant thread found, call `get_thread` with `messageFormat: FULL_CONTENT` to retrieve the full message bodies. Always read `plaintextBody` - never rely on `snippet` alone, as snippets are truncated and will miss critical details like anchor text, target URLs, and placement instructions.

Focus on:
- The first message (to understand the original proposal)
- The most recent 3-4 messages (to understand current status and final agreed terms)
- Any message where URLs, anchors, or placement instructions are mentioned

### Step 3 - Extract structured context

From the threads, extract:

| Field | What to look for |
|---|---|
| Partner name | Sender name or company name |
| Domain | Their website |
| Email | Their email address |
| Last contact | Date of the most recent email |
| Thread count | How many threads found |
| Status | See status definitions below |
| Next action | What we should do next |
| Key notes | Up to 4 short notable facts |

For every agreed link placement (both ours and theirs), extract:

| Field | What to look for |
|---|---|
| URL | The page where the link is placed |
| Anchor text | The exact clickable text agreed |
| Status | Whether the link is published or not yet published |
| Link type | dofollow, nofollow, or unknown |
| Placement & added content | Exact before/after sentence, table row, or heading context specified in the email |

**Multiple agreed pages:** If both sides agreed on more than 2 link placements in total, list every single one - do not summarise or truncate.

**Status definitions:**
- `completed` - Both links are confirmed live
- `exchange agreed` - Both sides have agreed on anchor text and URLs but no links placed yet
- `active` - Exchange is in progress, both sides engaged
- `pending_them` - We placed our link, waiting for them to place theirs
- `pending_us` - They placed their link, we haven't placed ours yet
- `stalled` - No reply in 2+ weeks or conversation went cold
- `unknown` - Not enough information to determine

### Step 4 - Output the briefing

Present the briefing in this format:

---

**Partner:** [Name] | [Domain] | [Email]
**Status:** [Status]
**Last contact:** [Date] | [N] thread(s) found

**Summary**
[2-3 sentences: how the relationship started, what was agreed, where things stand now]

**Link placements**

| Side | URL | Anchor text  | Target Page | Status | Link type | Placement & added content |
|---|---|---|---|---|---|
| Ours (on their site) | [URL] | [anchor] | Target URL (my website's URL that receive backlink) | Published / Not yet published | dofollow / nofollow / unknown | [exact placement instruction] |
| Theirs (on our site) | [URL] | [anchor] | Target URL (their website's URL that receive backlink) |  Published / Not yet published | dofollow / nofollow / unknown | [exact placement instruction] |

If more than 2 total placements were agreed, add a row for each one.

**Key notes**
- [note 1]
- [note 2]
...

**Next action**
[Concrete single action: e.g. "Follow up - no reply in 3 weeks", "Verify their link is still live", "Place our link on X page"]

---

### Step 5 - Offer to draft a reply

After the briefing, ask:

> "Want me to draft a reply to [partner name]?"

If yes, write a short, natural follow-up email based on the status and next action. Match the tone of the existing thread (formal/casual).

---

## Edge Cases

- **No threads found**: Say so clearly and ask if they want to try a different search term.
- **Many unrelated threads**: Filter for threads that mention "link", "exchange", "collaboration", "guest post", or contain URLs from their domain.
- **Partial information**: Fill in what's available and mark missing fields as "-". Do not guess or invent URLs or anchor text.
- **Multiple partners found**: List them briefly and ask which one to brief on.
