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

For every agreed link placement (both ours and theirs), extract:

| Field | What to look for |
|---|---|
| URL | The page where the link is placed |
| Anchor text | The exact clickable text agreed |
| Status | Whether the link is published or not yet published |
| Link type | dofollow, nofollow, or unknown |
| Placement & added content | Exact before/after sentence, the added sentence, the anchor, and the target page specified in the email |

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

Present the briefing in this format. Notes on the layout:
- **Do NOT include a Summary section** unless the user explicitly asks for one.
- **Do NOT include a Key notes section** unless the user explicitly asks for one.
- The placements **table stays lean** - it does NOT contain the "Placement & added content" column. Each row is numbered and the full placement detail goes in the section below the table.
- **Group placements: list all "Ours" rows first, then all "Theirs" rows.** Number them sequentially (1, 2, 3...) in that grouped order, and keep the same numbering in the details section.

---

**Partner:** [Name] | [Domain(s)] | [Email]
**Status:** [Status]
**Last contact:** [Date] | [N] thread(s) found

**Link placements**

| # | Side | URL | Anchor text | Target Page | Status | Link type |
|---|---|---|---|---|---|---|
| 1 | Ours (on their site) | [URL] | [anchor] | Target URL (my website's URL that receives the backlink) | Published / Not yet published | dofollow / nofollow / unknown |
| 2 | Ours (on their site) | [URL] | [anchor] | Target URL | Published / Not yet published | dofollow / nofollow / unknown |
| 3 | Theirs (on our site) | [URL] | [anchor] | Target URL (their website's URL that receives the backlink) | Published / Not yet published | dofollow / nofollow / unknown |

List every agreed placement as its own numbered row - do not summarise or truncate.

**Placement & added content (details)**

For each numbered placement, restate the full request in this structure (use `Before:` or `After:` depending on what the email specified; include only the fields that apply):

**#1 - [Ours/Theirs] on [domain]** *(Status; add any caveat, e.g. "dofollow agreed only after moving off the pillar page")*
- Page to insert link: [full URL of the page where the link sits]
- Before / After: [exact existing sentence the link is anchored next to]
- Add: [the exact new sentence/content to be inserted]
- Anchor: [exact anchor text]
- Target page: [full URL that receives the backlink]

(Repeat the block for #2, #3, ... in the same grouped Ours-then-Theirs order.)

**Placements still under negotiation:** If a placement isn't settled - the two sides proposed different pages/anchors/content and no final version was agreed - show BOTH versions under the same numbered block, each as its own labelled sub-block with its own status. Use italic sub-headings like *Your original suggestion (sent [date]):* and *Their counter-proposal (sent [date] - awaiting your yes):*, and give each the full `Page to insert link / Before-After / Add / Anchor / Target page` structure. Note the status on each (e.g. "Declined by publisher - listicle requires 2:1"). Do not silently drop the superseded version - the user needs to see what was offered and why it changed.

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
