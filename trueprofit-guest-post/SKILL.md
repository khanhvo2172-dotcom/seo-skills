---
name: trueprofit-guest-post
description: "Generates guest post content for TrueProfit to be inserted into a partner's page. Use this skill whenever the user wants to write a TrueProfit section, blurb, heading entry, or any content placement for a link exchange partner's article or blog. Triggers include: 'write a section for X', 'generate guest post for Y', 'create content for our partner', 'write a TrueProfit blurb for Z's page', 'draft content for link exchange'."
---

# TrueProfit Guest Post Generator

## Purpose

Generate guest post content for TrueProfit that matches a partner website's style, structure, and tone, ready to paste directly into their article.

---

## TrueProfit Brand Reference

<!-- BRAND:START -->
_This section is the shared TrueProfit brand context. It is auto-generated from `_brand/trueprofit-brand.md`. To change any fact, edit that master file and run `node _brand/sync-brand.js`; do not edit between the BRAND markers by hand._

### What TrueProfit is
TrueProfit is the #1 Net Profit Analytics Platform built for Shopify and ecommerce merchants. It consolidates revenue, costs, products, and marketing performance into one unified dashboard, showing net profit at every level: storewide, by product, and by ad channel.

### Core value proposition
- Shows real net profit after all costs, not just revenue or gross profit
- Catches profit leaks early so merchants can fix them fast
- Helps merchants scale winners and cut what is not profitable
- Turns complex store data into simple, actionable, profit-focused insights

### Key features (use selectively based on angle and context)
- Real-time net profit dashboard
- Net profit visibility at every level: storewide, by product, by ad channel
- Automatic cost tracking: COGS, ad spend, shipping fees, transaction fees, custom costs
- Profit-based product analytics and attribution
- Complete P&L reporting (weekly and monthly)
- Customer lifetime value (CLV)
- Custom metrics and KPIs
- Marketing attribution (profit-first, not ROAS-first)
- MCP connection (connects merchant store data to LLMs like ChatGPT, Claude, Gemini)
- Mobile app

### TrueProfit pricing
- 14-day free trial
- Basic: $35/month (300 orders, $0.30/extra, max $300 surcharge)
- Advanced: $60/month (600 orders, $0.20/extra, max $500 surcharge)
- Ultimate (Recommended): $100/month (1,500 orders, $0.10/extra, max $700 surcharge)
- Enterprise: $200/month (3,500 orders, $0.07/extra, max $1,000 surcharge)

### Proof and social proof
- Rating: 5.0/5 (800+ reviews on the Shopify App Store)
- 70,000+ merchants

### Verified benchmark data (use these exact figures; never fabricate or substitute)
- Shopify seller income distribution: about 60% of new Shopify stores make under $1,000/month, roughly 20% reach $10,000 or more per month, and the top 10% earn $100,000 or more per month.
- Dropshipping income by experience level (TrueProfit analysis of 1,200+ stores): beginners $0 to $2,000/month, intermediate $2,000 to $10,000/month, advanced $10,000 to $50,000+/month. First sale usually within 7 to 14 days; reaching $5,000 to $10,000/month typically takes 6 to 12 months.
- Dropshipping margins: a gross margin of 65 to 70% is favorable; a net margin of 15 to 25% is the strong benchmark after all costs.
- Any other statistic or benchmark must come from published TrueProfit data. If you do not have a verified TrueProfit figure, leave the stat out rather than inventing one.

### Referenced platform pricing (Shopify, US, 2026)
When content cites Shopify plan prices, use US pricing and give a concrete number for every tier, never a vague descriptor, and always state the billing cycle:
- Basic: $39/month ($29 billed annually)
- Grow: $105/month ($79 annually)
- Advanced: $399/month ($299 annually)
- Shopify Plus: from $2,300/month

### Competitor comparison (leader-approved; use these exact figures and positioning, never invent competitor pricing or capabilities)
When comparing TrueProfit to other analytics tools, use this table as the canonical reference. Add or drop rows to fit the content, but keep the data consistent with it.

|  | Shopify Reports | Triple Whale | Lifetimely | TrueProfit |
| :- | :- | :- | :- | :- |
| Starting price | Included in Shopify plan | $219/mo | $79/mo | $35/mo |
| Net profit tracking | No | Partial | Yes | Thorough |
| Real-time P&L | No | No | Yes | Yes |
| Profit by product | No | No | Yes | Yes |
| Profit by ad channel | No | Yes | Yes | Yes |
| Built for dropshipping | No | No | No | Yes |
| Primary focus | Revenue & orders | Ad attribution & creative | Customer LTV & cohorts | Net profit & net margins |

Positioning notes: Triple Whale is built for DTC brands focused on ad attribution and creative analytics; Lifetimely is oriented around customer lifetime value and cohort analysis; TrueProfit starts from net profit and is purpose-built for Shopify dropshippers and profit-first merchants.

### Author and spokesperson — Harry Chu
Harry Chu is the founder and CEO of TrueProfit. Introduce him as the expert source or author byline when a story needs a named person.
- Website: https://trueprofit.io/author/harry-chu
- LinkedIn: https://www.linkedin.com/in/harry-chu-trueprofit/
- X: https://x.com/harryprofitguy
- YouTube: https://www.youtube.com/@HarryChu-TrueProfit/shorts

### Key URLs
- Homepage: https://trueprofit.io/
- Shopify App: https://apps.shopify.com/trueprofit/

### TrueProfit brand channels
- Facebook: https://www.facebook.com/trueprofit.io
- X (Twitter): https://x.com/trueprofit_io
- Discord: https://discord.com/invite/AsA3m7zNqy
- YouTube: https://www.youtube.com/@trueprofit
- LinkedIn: https://www.linkedin.com/company/trueprofit
<!-- BRAND:END -->

---

## Workflow

### Step 1 - Ask content type

Ask all questions at once in a single numbered list. The user answers all in one reply.

1. What type of content? (full app listing section / short blurb / single sentence / other)
2. Numbered heading? If yes, what number? (or no)
3. Any angle to emphasise? (e.g. dropshipping, marketing attribution, MCP, or general)
4. Which URL to link? (homepage / Shopify App / other, default is homepage)

Once answered, move to Step 2.

### Step 2 - Ask for partner content sample

Ask the user to paste a sample section from the partner's page covering a *different* tool or app on the same page. This is used purely as a style, tone, structure, and formatting reference.

> "Please paste a sample section from the partner's page so I can match their style and format exactly."

If the sample is very short (1-2 sentences), ask for another section from the same page for better structure reference.

### Step 3 - Analyse the sample

From the pasted sample, extract and match:
- **Tone**: formal, casual, conversational, technical, enthusiastic
- **Structure**: hook, definition, or problem-first opening
- **Heading format**: bold, numbered, H3, plain text
- **Feature list style**: bold label + colon, plain bullets, numbered list, or no list
- **Link style**: hyperlinked product name, or inline hyperlink on descriptive text
- **Length**: approximate word count
- **Pricing**: table vs prose vs omitted, include pricing in output only if the sample includes it
- **Rating**: included or omitted, include rating in output only if the sample includes it
- **Closing**: CTA, summary sentence, or just the feature list

### Step 4 - Generate content

Write the TrueProfit section matching the partner's style exactly. Follow these rules:

- Never invent features, stats, or claims not in the Brand Reference above
- Always hyperlink "TrueProfit" to https://trueprofit.io on first mention (or the specific URL the user requested)
- Match the partner's heading numbering style if they use numbered lists
- Use the same bullet format as the partner
- Match approximate section length from the sample
- Match the opening structure from the sample
- Do not use em dashes; use commas, colons, or semicolons instead

### Step 5 - Deliver as plain markdown

Output the content as plain markdown text inline in the conversation, no artifact, no file.

After delivering, ask:
> "Want me to adjust the tone, length, or emphasis on any specific feature?"

---

## Edge Cases

- **No sample provided**: Ask again. Style matching is required, do not generate without a reference sample.
- **Partner page has no feature list**: Generate a prose-only section without bullets.
- **User wants multiple variants**: Generate 2 versions (e.g. one shorter, one with pricing) and let them pick.
