---
name: generate-reponse-emails-to-reporters
description: Generate concise, reporter-ready email replies for PR opportunities, especially HARO, MentionMatch, Qwoted, or similar requests. Use when Codex needs to draft, refine, summarize, or create a response email from reporter questions, source notes, brand references, TrueProfit articles, customer examples, or expert quotes.
---

# Generate Reporter Response Emails

## Overview

Use this skill to turn reporter requests into concise, usable email replies. Default to a friendly, direct partner tone similar to Ahrefs: clear answers, little fluff, practical examples, and no stiff PR language.

When the opportunity is for TrueProfit, position Harry Chu as Founder/CEO and TrueProfit as a Shopify profit analytics app that helps merchants track true profit after costs such as COGS, shipping, ad spend, transaction fees, discounts, refunds, taxes, and app fees.

## Workflow

1. Identify the reporter, publication, deadline, request title, target source type, questions, and submission email if available.
2. Use the user's provided links, article notes, and requested angle as the primary source of truth. If links are provided but not already summarized, browse or scrape them when current/source accuracy matters.
3. Draft the email with a short intro, then answers under each reporter question.
4. Before the answers, include a short attribution line when requested, such as: `Here are some insights from our CEO, Harry Chu:`
5. Include one concrete customer-style example per question when the user asks for examples.
6. Keep examples believable and varied. Do not start every example with the same phrase.
7. End with a simple signoff. Do not over-explain the brand unless the pitch needs it.

## Default Email Structure

Use this shape unless the user asks for another format:

```text
Subject: Re: [request topic]

Hi [Reporter Name],

Happy to contribute. I would like to introduce Harry Chu, Founder of TrueProfit, a Shopify profit analytics app that helps ecommerce merchants track real profit after COGS, shipping, ad spend, transaction fees, discounts, refunds, taxes, and other costs.

Here are some insights from our CEO, Harry Chu:

**1. [Reporter question]**

[Direct answer in 1-2 short paragraphs.]

Example: [Concrete customer-style example.]

...

Best,
[Sender Name]
TrueProfit
https://trueprofit.io
```

## Answer Style

- Answer the question directly in the first sentence.
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
- Confirm every requested example exists and uses varied wording.
- Confirm the intro uses the user's preferred phrasing, especially names and titles.
- Confirm examples do not overclaim or invent precise metrics.
- Confirm the email can be sent as-is, with only sender name/signature needing replacement if unknown.
