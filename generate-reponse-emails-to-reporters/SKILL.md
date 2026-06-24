---
name: generate-reponse-emails-to-reporters
description: Generate concise, reporter-ready email replies for PR opportunities, especially HARO, MentionMatch, Qwoted, or similar requests. Use when Codex needs to draft, refine, summarize, or create a response email from reporter questions, source notes, brand references, TrueProfit articles, customer examples, or expert quotes.
---

# Generate Reporter Response Emails

## Overview

Use this skill to turn reporter requests into concise, usable email replies. Default to a friendly, direct partner tone similar to Ahrefs: clear answers, little fluff, practical examples, and no stiff PR language.

When the opportunity is for TrueProfit, write from Khanh unless the user names another sender. Introduce Harry Chu as the founder/source when the pitch needs an expert. Position TrueProfit as the #1 profit tracking app for Shopify stores, with a 5.0 rating from 770+ reviews and 70,000+ merchants, helping merchants track true profit after costs such as COGS, shipping, ad spend, transaction fees, discounts, refunds, taxes, and app fees.

When pitching AI/SMB/productivity topics, focus on TrueProfit MCP: Shopify merchants can connect store and profit data to LLMs like ChatGPT or Codex, then use AI's reasoning to analyze store performance and make better decisions. Do not position TrueProfit as a foundation-model or generic AI company. Position it as a Shopify profit analytics app that gives AI the complete, current business context needed for useful analysis.

## Workflow

1. Identify the reporter, publication, deadline, request title, target source type, questions, and submission email if available.
2. Use the user's provided links, article notes, and requested angle as the primary source of truth. If links are provided but not already summarized, browse or scrape them when current/source accuracy matters.
3. Draft the email with a short intro, then answers under each reporter question.
4. Before the answers, include a short attribution line when requested, such as: `Here are some insights from our CEO, Harry Chu:`
5. Include one concrete customer-style example per question when the user asks for examples.
6. Keep examples believable and varied. Do not start every example with the same phrase.
7. When pitching Harry, add his social links near the end unless the user asks for a shorter reply.
8. End with a simple signoff. Do not over-explain the brand unless the pitch needs it.
9. When the user approves the copy and asks to make or create the draft, create it directly in Gmail when Gmail is connected. Preserve the approved recipient, subject, and body. Create a draft only; never send it unless the user explicitly asks to send it.

## Default Email Structure

Use this shape unless the user asks for another format:

```text
Subject: Re: [request topic]

Hi [Reporter Name],

I am Khanh from TrueProfit, and I would like to introduce Harry Chu, founder of TrueProfit, as a source for your story.

TrueProfit is the #1 profit tracking app for Shopify stores, with a 5.0 rating from 770+ reviews and 70,000+ merchants. It helps ecommerce merchants track real profit after COGS, shipping, ad spend, transaction fees, discounts, refunds, taxes, and other costs.

Here are some insights from our CEO, Harry Chu:

**1. [Reporter question]**

[Direct answer in 1-2 short paragraphs.]

Example: [Concrete customer-style example.]

...

Best,

Harry Chu's contact information:
- Linkedin: https://www.linkedin.com/in/harry-chu-trueprofit/
- Youtube: https://www.youtube.com/@HarryChu-TrueProfit/shorts
- Website: https://trueprofit.io/author/harry-chu

```

## Answer Style

- Answer the question directly in the first sentence.
- Open with a hook that directly addresses the reporter's central topic. Do not lead with a narrower TrueProfit qualification; use that as the following sentence.
- Prefer practical actions over generic advice.
- Use `profit`, `margin`, `unit economics`, `net profit`, `average order profit`, `COGS`, `shipping`, `refunds`, `returns`, `CAC`, `LTV`, and `net profit on ad spend` when relevant.
- Keep paragraphs short. Most answers should be 60-120 words including the example.
- Avoid inflated PR phrasing such as `game-changing`, `revolutionary`, `unlock`, `seamless`, or `robust`.
- Do not claim exact customer outcomes unless the user provides exact numbers.
- If examples are illustrative rather than verified case studies, phrase them as anonymized customer examples, not public case studies.

## TrueProfit Angles

Use these recurring recommendations when they fit the reporter's question:

- Increase profitability by improving order economics, not by cutting staff or lowering quality.
- Scale products with the highest net margin, not only the highest revenue.
- Track hidden cost leaks beyond basic P&L lines: returns, refunds, chargebacks, shipping by region, payment processing, Shopify fees, POS fees, app fees, discounts, taxes, packaging, support time, and vendor changes.
- Once ecommerce stores scale, use specialized profit and expense tracking software instead of spreadsheets.
- Make pricing decisions from true order cost and customer value, not competitor prices alone.
- Use pricing tools such as bundles, subscriptions, free-shipping thresholds, value-based pricing, selective discounts, and margin-aware promotions.
- Separate revenue growth from profit growth before scaling ad spend, inventory, fulfillment, apps, or headcount.
- Avoid cost cuts that create second-order losses, such as cheaper suppliers causing returns, understaffing causing burnout, or turning off profitable campaigns because they have lower revenue.

## TrueProfit MCP / AI Angle

Use this angle for AI, SMB productivity, AI decision-making, store analytics, or workflow questions:

- AI helps SMBs most when it becomes a decision layer on top of trusted business data, not just a generic writing or automation tool.
- Emphasize that AI recommendations are only as useful as the business-performance data behind them. For acquisition or growth topics, mention accurate profit, cost, customer, product, and campaign data before describing what AI can recommend.
- For stories about winning customers, a preferred hook pattern is: `AI is helping businesses win more customers, but its recommendations are only as good as the business data behind them.` Follow it by explaining that complete performance data helps AI identify who to target, what to promote, and where to invest marketing budget.
- Prefer a short paragraph followed by bullets when explaining TrueProfit MCP. Avoid writing one dense plain-text paragraph when the pitch includes multiple example questions or use cases.
- Use this default phrasing for AI scaling, SMB decision-making, productivity, or "scale smarter" requests:

```text
Harry can speak to how AI is helping SMBs make better business decisions, not just move faster. With TrueProfit MCP, Shopify merchants can connect their store and profit data to LLMs like ChatGPT or Codex, then ask plain-English questions such as:

- Which products are actually profitable?
- Why did my margin drop this week?
- Which campaigns should I scale or pause?
- What hidden costs are eating into profit?
- Which products look strong by revenue but weak by net margin?
```

- After the bullet list, explain that MCP gives AI complete business context across Shopify, ad platforms, shipping apps, payment processors, and spreadsheets.
- Mention practical outputs when relevant: financial analysis, dashboards, product margin comparisons, campaign performance reviews, net profit explanations, and decisions around pricing, inventory, discounts, and ad spend.
- With TrueProfit MCP, Shopify merchants can connect store and profit data to LLMs like ChatGPT or Codex and ask plain-English questions such as:
  - Which products are actually profitable?
  - Why did my margin drop this week?
  - Which campaigns should I scale or pause?
  - What hidden costs are eating into profit?
- The core point: many SMBs already have the data, but it is scattered across Shopify, ad platforms, shipping apps, payment processors, and spreadsheets. MCP gives AI the right context so merchants can use its reasoning ability to analyze store performance and make better decisions faster.
- For AI/SMB pitches, include one short illustrative ecommerce example unless the user asks for a shorter email.

Example:

```text
Example: A Shopify fashion merchant might see that one product has the highest revenue, but once AI reviews COGS, return rate, shipping cost, discounts, and ad spend, it may show that a lower-revenue product has better average order profit. Instead of scaling the biggest seller, the merchant can shift budget toward the product with stronger unit economics.
```

## Harry Chu Links

When introducing Harry Chu as the source, include these links near the end:

```text
Harry's social links:
Website: https://trueprofit.io/author/harry-chu
LinkedIn: https://www.linkedin.com/in/harry-chu-trueprofit/
YouTube: https://www.youtube.com/@HarryChu-TrueProfit/shorts
```

## Example Phrasing

Vary customer example openers:

- `One of our customers, a Shopify [category] store, ...`
- `Another merchant, a [category] brand, ...`
- `A Shopify [category] merchant we worked with ...`
- `One ecommerce [category] brand ...`
- `A [category] customer ...`
- `Another Shopify [category] store ...`

Example pattern:

```text
Example: Another merchant, a travel accessories store, had one backpack generating much more revenue than a small travel pouch. But after shipping costs and return rates, the pouch had higher average order profit and was easier to bundle. Scaling the pouch improved profit faster than pushing the higher-revenue product.
```

## Quality Check

Before finalizing:

- Confirm every reporter question is answered.
- Confirm the opening hook directly answers the reporter's topic before introducing the TrueProfit-specific profitability angle.
- Confirm every requested example exists and uses varied wording.
- Confirm the intro uses the user's preferred phrasing, especially names and titles.
- Confirm TrueProfit proof points are included when useful: #1 profit tracking app for Shopify stores, 5.0 rating, 770+ reviews, and 70,000+ merchants.
- Confirm Harry Chu's links are included when Harry is introduced as the source.
- Confirm examples do not overclaim or invent precise metrics.
- Confirm the email can be sent as-is, with only sender name/signature needing replacement if unknown.
- If the user requested a Gmail draft, confirm it was created but not sent.
