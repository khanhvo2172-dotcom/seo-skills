# SEO Skills for Claude Code

> A collection of [Claude Code](https://claude.ai/code) skills for SEO content localization, digital PR screening, and YouTube community seeding — built for TrueProfit's ecommerce marketing workflow.

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-blueviolet?logo=anthropic)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/Skills-3-brightgreen)](#skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Skills

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

### `browse-emails-to-find-opportunities`
Screens emails from **HARO**, **MentionMatch**, and **Qwoted** to surface PR opportunities that fit TrueProfit's positioning as a Shopify profit analytics SaaS.

**Triggers when you say:** *"scan my PR emails"*, *"find HARO opportunities"*, *"check Qwoted/MentionMatch"*

**What it does:**
- Reads Gmail threads from all three platforms via Gmail MCP
- Scores each opportunity as High-fit / Conditional / Skip with clear reasoning
- Suggests pitch angles only for genuinely relevant opportunities
- Applies strict brand-fit rules (skips CPA/accounting, consumer finance, unrelated verticals)
- Returns a ranked summary — no raw email noise

**Strong-fit topics:** ecommerce profitability, Shopify merchant analytics, profit/margin tracking, ROAS vs. POAS, shipping cost impact, AI + merchant data via MCP.

---

### `youtube-seeding-comments-generate`
Generates **realistic YouTube seeding comments** for Shopify/ecommerce topics in both unbranded and TrueProfit-branded batches.

**Triggers when you say:** *"generate YouTube comments"*, *"create seeding comments"*, *"write YouTube comments for [keyword]"*

**Input format:**
```
Keyword / Target Audience / Total count / Branded count / Direction / Issues / Seeding Direction
```

**What it does:**
- Writes comments that read like real different users — varied rhythm, Reddit-style tone
- Groups output as UNBRANDED and BRANDED (detected by TrueProfit mention, not formula)
- Follows TrueProfit voice rules: problem described first, brand as solution, never a brag
- No hashtags, no emojis, no em dashes, no bullet points inside comments
- Pure Markdown numbered list output, no preamble

---

## Installation

### Option 1 — Clone and install

```bash
git clone https://github.com/khanhvo2172-dotcom/seo-skills.git
cd seo-skills
```

Each `.skill` file is a ZIP archive. Extract to `~/.claude/skills/<skill-name>/`.

**macOS / Linux:**
```bash
for f in *.skill; do
  name="${f%.skill}"
  mkdir -p ~/.claude/skills/"$name"
  unzip -o "$f" -d /tmp/"$name"_extract
  find /tmp/"$name"_extract -type f | xargs -I{} cp {} ~/.claude/skills/"$name"/
done
```

**Windows (PowerShell):**
```powershell
foreach ($f in Get-ChildItem *.skill) {
    $name = $f.BaseName
    New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\$name" | Out-Null
    Expand-Archive -Path $f.FullName -DestinationPath "$env:TEMP\$name" -Force
    Get-ChildItem -Recurse -File "$env:TEMP\$name" | ForEach-Object {
        Copy-Item $_.FullName "$env:USERPROFILE\.claude\skills\$name\$($_.Name)" -Force
    }
}
```

### Option 2 — Manual

Download a `.skill` file, rename it to `.zip`, extract into `~/.claude/skills/<skill-name>/`.

---

## Usage

Once installed, invoke any skill by typing `/` in Claude Code:

| Command | Description |
|---|---|
| `/trueprofit-blog-localization` | Translate blog articles to ES/DE/FR |
| `/browse-emails-to-find-opportunities` | Screen PR opportunity emails |
| `/youtube-seeding-comments-generate` | Generate YouTube seeding comments |

Skills are available globally across all Claude Code sessions after installation.

---

## Requirements

| Skill | Requirements |
|---|---|
| `trueprofit-blog-localization` | Claude Code |
| `browse-emails-to-find-opportunities` | Claude Code + Gmail MCP |
| `youtube-seeding-comments-generate` | Claude Code |

---

## About TrueProfit

[TrueProfit](https://trueprofit.io) is a Shopify profit analytics app that helps merchants track real profit — net of COGS, ad spend, shipping, transaction fees, refunds, and taxes — at the order, product, and channel level.

---

## License

MIT