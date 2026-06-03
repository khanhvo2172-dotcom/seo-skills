# SEO Skills for Claude Code

> A collection of [Claude Code](https://claude.ai/code) skills for SEO content localization, digital PR screening, reporter response drafting, guest post content, link exchange email briefings, and YouTube community seeding - built for TrueProfit's ecommerce marketing workflow.

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-blueviolet?logo=anthropic)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/Skills-7-brightgreen)](#skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Skills

### `compare-content-between-ggdocs-live-url`
Compares a TrueProfit Google Docs article tab against its live `trueprofit.io` blog URL to detect content, link, data benchmark, FAQ, formatting, and section ordering differences.

**Triggers when you say:** *"compare doc vs live"*, *"check if the live page matches the doc"*, *"any differences between doc and URL"*, *"is the content synced"*

**What it does:**
- Reads the specific Google Docs tab or matching year-versioned content
- Compares only the live article body, excluding site chrome and author bio
- Checks H1, intros, headings, body text, links, benchmarks, Further Reading, FAQs, CTAs, and formatting
- Handles TrueProfit callout block extraction limits and raw HTML verification
- Returns `No` when synced, or a structured differences table when mismatches exist

---

### `trueprofit-blog-localization`
Translates TrueProfit blog markdown files into **Spanish (Spain)**, **German (Germany)**, and **French (France)** with locale-aware formatting rules, currency conversion, and Google Docs-friendly output.

**Triggers when you say:** *"translate this article"*, *"localize to ES/DE/FR"*, *"produce Spanish/German/French version"*

**What it does:**
- Reads any `.md` blog file you upload
- Outputs `_ES.md`, `_DE.md`, `_FR.md` files ready for Google Docs
- Applies locale-specific number/currency formatting (comma vs. period, EUR spacing)
- Preserves all Markdown structure: headings, tables, links, CTAs, image placeholders
- Keeps brand names in English (TrueProfit, Shopify, AliExpress, etc.)
- Runs a QA checklist after each delivery

---

### `browse-emails-to-find-opportunites`
Screens emails from **HARO**, **MentionMatch**, and **Qwoted** to surface PR opportunities that fit TrueProfit's positioning as a Shopify profit analytics SaaS.

**Triggers when you say:** *"scan my PR emails"*, *"find HARO opportunities"*, *"check Qwoted/MentionMatch"*

**What it does:**
- Reads Gmail threads from all three platforms via Gmail MCP
- Scores each opportunity as High-fit / Conditional / Skip with clear reasoning
- Suggests pitch angles only for genuinely relevant opportunities
- Applies strict brand-fit rules (skips CPA/accounting, consumer finance, unrelated verticals)
- Returns a ranked summary - no raw email noise

**Strong-fit topics:** ecommerce profitability, Shopify merchant analytics, profit/margin tracking, ROAS vs. POAS, shipping cost impact, AI + merchant data via MCP.

---

### `generate-reponse-emails-to-reporters`
Drafts concise, reporter-ready response emails for PR opportunities using TrueProfit positioning, source notes, requested angles, and customer-style examples.

**Triggers when you say:** *"generate a response email"*, *"draft reporter reply"*, *"write the MentionMatch/Qwoted/HARO response"*

**What it does:**
- Turns reporter questions into a ready-to-send email
- Positions Harry Chu as Founder/CEO of TrueProfit when relevant
- Keeps a concise, friendly, Ahrefs-style partner tone
- Adds practical ecommerce profitability advice and concrete anonymized customer examples
- Checks that every reporter question is answered before finalizing

---

### `summarize-email-thread`
Searches Gmail for email threads related to a link exchange partner and produces a structured briefing with the partner, agreement, link placement status, last contact date, and recommended next action.

**Triggers when you say:** *"what did we agree with X"*, *"catch me up on X"*, *"what is the status with X"*, *"I got a reply from X"*

**What it does:**
- Searches Gmail by domain, email address, subject keyword, or partner name
- Reads full thread bodies instead of relying on snippets
- Extracts agreed URLs, anchor text, placement context, link type, and status
- Classifies status as completed, active, pending, stalled, or exchange agreed
- Returns a concise briefing before you reply to a partner

---

### `trueprofit-guest-post`
Generates TrueProfit guest post sections, blurbs, app listing entries, and link exchange content that matches a partner page's style and structure.

**Triggers when you say:** *"write a section for X"*, *"generate guest post for Y"*, *"create content for our partner"*, *"write a TrueProfit blurb"*

**What it does:**
- Collects content type, heading, pricing, rating, angle, and target URL requirements
- Requires a partner content sample so the output matches the existing page style
- Uses a fixed TrueProfit brand reference for features, pricing, rating, and URLs
- Matches tone, heading format, bullet style, link style, length, and closing pattern
- Outputs ready-to-paste markdown without inventing unsupported claims

---

### `youtube-seeding-comments-generate`
Generates **realistic YouTube seeding comments** for Shopify/ecommerce topics in both unbranded and TrueProfit-branded batches.

**Triggers when you say:** *"generate YouTube comments"*, *"create seeding comments"*, *"write YouTube comments for [keyword]"*

**Input format:**
```text
Keyword / Target Audience / Total count / Branded count / Direction / Issues / Seeding Direction
```

**What it does:**
- Writes comments that read like real different users - varied rhythm, Reddit-style tone
- Groups output as UNBRANDED and BRANDED (detected by TrueProfit mention, not formula)
- Follows TrueProfit voice rules: problem described first, brand as solution, never a brag
- No hashtags, no emojis, no em dashes, no bullet points inside comments
- Pure Markdown numbered list output, no preamble

---

## Repository Layout

Each skill is stored as a folder with `SKILL.md` at its root:

```text
skill-name/
+-- SKILL.md
+-- scripts/
+-- references/
+-- assets/
```

Supporting folders are optional. For example, `generate-reponse-emails-to-reporters` includes an `agents/` folder.

---

## Installation

### Option 1 - Clone and install

```bash
git clone https://github.com/khanhvo2172-dotcom/seo-skills.git
cd seo-skills
```

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills
cp -R trueprofit-blog-localization ~/.claude/skills/
cp -R browse-emails-to-find-opportunites ~/.claude/skills/
cp -R generate-reponse-emails-to-reporters ~/.claude/skills/
cp -R summarize-email-thread ~/.claude/skills/
cp -R trueprofit-guest-post ~/.claude/skills/
cp -R youtube-seeding-comments-generate ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force trueprofit-blog-localization "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force browse-emails-to-find-opportunites "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force generate-reponse-emails-to-reporters "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force summarize-email-thread "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force trueprofit-guest-post "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force youtube-seeding-comments-generate "$env:USERPROFILE\.claude\skills\"
```

### Option 2 - Manual

Download or copy any skill folder into `~/.claude/skills/<skill-name>/`. The folder must contain `SKILL.md` at its root.

---

## Usage

Once installed, invoke any skill by typing `/` in Claude Code:

| Command | Description |
|---|---|
| `/trueprofit-blog-localization` | Translate blog articles to ES/DE/FR |
| `/browse-emails-to-find-opportunites` | Screen PR opportunity emails |
| `/generate-reponse-emails-to-reporters` | Draft reporter response emails |
| `/summarize-email-thread` | Brief link exchange partner email history |
| `/trueprofit-guest-post` | Generate partner-style TrueProfit guest post content |
| `/youtube-seeding-comments-generate` | Generate YouTube seeding comments |

Skills are available globally across all Claude Code sessions after installation.

---

## Requirements

| Skill | Requirements |
|---|---|
| `trueprofit-blog-localization` | Claude Code |
| `browse-emails-to-find-opportunites` | Claude Code + Gmail MCP |
| `generate-reponse-emails-to-reporters` | Claude Code |
| `summarize-email-thread` | Claude Code + Gmail MCP |
| `trueprofit-guest-post` | Claude Code |
| `youtube-seeding-comments-generate` | Claude Code |

---

## About TrueProfit

[TrueProfit](https://trueprofit.io) is a Shopify profit analytics app that helps merchants track real profit - net of COGS, ad spend, shipping, transaction fees, refunds, and taxes - at the order, product, and channel level.

---

## License

MIT
