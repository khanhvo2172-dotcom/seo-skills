---
name: browse-emails-to-find-opportunites
description: "Read personal emails from 3 platforms HARO, MentionMatch & Qwoted to find relevant opportunities for TrueProfit"
---

# SEO / Digital PR Opportunity Screening Context

## Brand
TrueProfit is a Shopify profit analytics SaaS/app. It helps Shopify merchants understand real profit by tracking revenue, COGS, shipping, ad spend, transaction fees, discounts, refunds, taxes, and other ecommerce costs.

TrueProfit is **not**:
- An AI company
- A foundation-model company
- A CPA/accounting firm
- A personal finance advisory brand

TrueProfit can discuss:
- Shopify/ecommerce profit analytics
- Ecommerce margins, contribution margin, order-level profit
- Small business/ecommerce cost visibility
- Shopify merchant operations
- Reporting, analytics, dashboards, attribution, P&L visibility
- How merchants use AI tools with their store/profit data
- TrueProfit’s MCP feature, which connects merchant store/profit data to LLMs such as Claude and ChatGPT

## Opportunity Screening Preference

Only prioritize PR/source opportunities when they clearly match TrueProfit’s expertise.

### Strong-fit topics
- Ecommerce profitability
- Shopify merchant analytics
- Ecommerce finance operations
- Profit tracking, margin tracking, cost tracking
- Shipping cost impact on ecommerce margins
- Checkout/conversion topics where TrueProfit can add a profitability angle
- ROAS vs POAS/profit-based ad decisions
- Inventory/product profitability
- B2B ecommerce if the angle includes conversion, fulfillment, cost-to-serve, or margins
- Small business commerce tools if the angle connects to sales, payments, fees, reporting, or profitability

### Conditional-fit topics
AI opportunities are only relevant if the angle is about:
- Merchants using AI with Shopify/store/profit data
- AI reliability when LLMs analyze business/ecommerce data
- AI assistants connected to source-of-truth commerce data
- TrueProfit’s MCP feature connecting merchant data to Claude/ChatGPT
- Examples/experience from merchants using AI to ask questions like:
  - “Which products are actually profitable?”
  - “Why did my margin drop this week?”
  - “Which campaigns should I scale?”
  - “What costs are hurting profit?”

When pitching AI topics, never position TrueProfit as an AI/model company. Position it as:
> A Shopify profit analytics app that helps merchants connect store/profit data to LLMs like Claude and ChatGPT via MCP. TrueProfit does not build foundation models, but can share experience from merchants using AI on top of ecommerce financial data.

### Weak / skip topics
Skip or deprioritize opportunities that ask for:
- CPA, accountant, bookkeeper, or financial planner credentials unless an actual qualified expert is available
- Consumer personal finance tips
- General AI model-building expertise
- MLOps/model benchmarking unless the angle allows real-world ecommerce AI usage
- Healthcare, politics, luxury, parenting, restaurants, legal, travel, unrelated consumer products
- Generic entrepreneur/founder commentary unless ecommerce/SaaS/profitability angle is clear

## Important Preference Learned

A request like:
- “CPA to comment on AI-assisted bookkeeping tools for small businesses”

is **close topically** but should be skipped if it specifically requires a CPA, because TrueProfit is a SaaS app and does not have CPA credentials.

A request like:
- “Enterprise AI reliability, hallucinations, edge cases, production evaluation”

is only maybe relevant if framed narrowly around merchants using AI with Shopify/profit data via MCP. Otherwise treat as not a clean fit.

## Preferred Evaluation Output

For each batch of HARO/Qwoted/MentionMatch emails, summarize:
1. High-fit opportunities
2. Maybe/conditional opportunities
3. Skip opportunities
4. Why each fits or does not fit
5. Suggested pitch angle only for genuinely relevant opportunities

Do not over-recommend borderline opportunities. Be strict.

## Drafting Follow-up Emails

When the user asks to draft, write, refine, or prepare a response email for any opportunity found by this skill, also use the `generate-reponse-emails-to-reporters` skill.

Carry forward the opportunity context from the email scan:
- Reporter name, publication, deadline, title, target source type, and submission email when available.
- The reporter's exact question or request.
- The fit classification and recommended TrueProfit angle.
- Any user-specified angle or wording preference.

For TrueProfit AI/SMB/productivity opportunities, instruct the response skill to use the TrueProfit MCP angle: Shopify merchants connect store and profit data to LLMs like ChatGPT or Codex, then use AI for financial analysis, dashboards, product and campaign decisions, margin investigation, and hidden-cost analysis. Prefer a short paragraph plus bullets for example questions instead of a dense plain-text paragraph.

## Example Good Pitch Angle: AI Reliability

> TrueProfit is a Shopify profit analytics app that lets merchants connect store/profit data to LLMs like Claude and ChatGPT via MCP. We do not build foundation models, but we see how merchants use AI on top of ecommerce financial data and where reliability issues appear in real workflows. In ecommerce analytics, the biggest reliability issue is not only hallucinated text; it is whether the model has complete, current, structured business data such as orders, refunds, ad spend, shipping costs, COGS, transaction fees, discounts, and taxes. Without those inputs, an AI assistant can give confident but misleading recommendations.

## Example Good Pitch Angle: Shipping Costs

> Shipping cost increases hurt ecommerce brands twice: first through direct margin compression, and second through behavioral changes such as higher cart abandonment when merchants pass costs to customers. The mistake many merchants make is looking only at revenue or ROAS. A shipping increase can turn a high-revenue product, region, or campaign unprofitable unless merchants track profit at the order, product, and channel level.

## Example Good Pitch Angle: Checkout / Conversion

> Faster checkout improves conversion, but the real metric ecommerce teams should watch is profitable conversion. Reducing checkout friction can lift order volume, but merchants still need to understand payment fees, shipping costs, discounts, refunds, and product-level COGS to know whether those extra conversions are actually profitable.

## Email Source Context

The user uses Gmail MCP to search/read emails from:
- HARO
- Qwoted
- MentionMatch

When asked to scan emails:
- Ask users the exact date ranges.
- Read only unread messages unless the user explicitly asks for all messages.
- Use Gmail search with `is:unread` and exclude trash/spam.
- Read relevant messages.
- Ignore previously reviewed opportunities if user asks.
- Avoid raw operational detail; provide ranked summaries.
