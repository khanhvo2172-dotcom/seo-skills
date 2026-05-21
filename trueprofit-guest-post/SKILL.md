---
name: trueprofit-guest-post
description: "Generates guest post content for TrueProfit to be inserted into a partner's page. Use this skill whenever the user wants to write a TrueProfit section, blurb, heading entry, or any content placement for a link exchange partner's article or blog. Triggers include: 'write a section for X', 'generate guest post for Y', 'create content for our partner', 'write a TrueProfit blurb for Z's page', 'draft content for link exchange'."
---

# TrueProfit Guest Post Generator

## Purpose

Generate guest post content for TrueProfit that matches a partner website's style, structure, and tone, ready to paste directly into their article.

---

## TrueProfit Brand Reference

Use only the following facts. Do not invent features, pricing, or claims.

**What TrueProfit is:**
TrueProfit is the #1 Net Profit Analytics Platform built for Shopify & ecommerce merchants who want real-time, accurate, and automated profit visibility. It consolidates revenue, costs, products, and marketing performance into one unified dashboard, showing net profit at every level: storewide, by product, and by ad channel.

**Core value proposition:**
- Shows *real* net profit after all costs, not just revenue
- Catches profit leaks early so merchants can fix them fast
- Helps merchants scale winners and cut what's not profitable
- Turns complex data into simple, actionable, profit-focused insights

**Key Features (use selectively based on context):**
- Real-time net profit dashboard
- Automatic cost tracking: COGS, ad spend, shipping fees, transaction fees, custom costs
- Profit-based product analytics & attribution
- Complete P&L reporting (weekly & monthly)
- Customer lifetime value (CLV)
- Custom metrics & KPIs
- Marketing attribution (profit-first, not ROAS)
- MCP connection (connects merchant store data to LLMs like ChatGPT, Claude, Gemini)
- Mobile app

**Pricing:**
- 14-day free trial
- Basic: $35/month (300 orders, $0.30/extra, max $300 surcharge)
- Advanced: $60/month (600 orders, $0.20/extra, max $500 surcharge)
- Ultimate (Recommended): $100/month (1,500 orders, $0.10/extra, max $700 surcharge)
- Enterprise: $200/month (3,500 orders, $0.07/extra, max $1,000 surcharge)

**Rating:** 5.0/5 (770+ reviews)

**Key URLs:**
- Homepage: https://trueprofit.io/
- Shopify App: https://apps.shopify.com/trueprofit/

- Facebook: https://www.facebook.com/trueprofit.io
- X (Twitter): https://x.com/trueprofit_io
- Discord: https://discord.com/invite/AsA3m7zNqy
- YouTube: https://www.youtube.com/@trueprofit
- LinkedIn: https://www.linkedin.com/company/trueprofit

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
