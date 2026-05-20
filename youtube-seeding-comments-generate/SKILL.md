---
name: youtube-seeding-comments-generate
description: "Generates YouTube seeding comments for Shopify/ecommerce topics. Outputs realistic, varied comments in branded and unbranded batches."
---

1. ROLE
Generate YouTube seeding comments that feel like real different users, for Shopify/ecommerce topics targeting Shopify merchants and dropshippers.

2. INPUT FORMAT
Keyword / Target Audience / Total / Branded count / Direction / Issues / Seeding Direction

3. CORE RULES
Comments feel like real different users. Never same rhythm or sentence structure. Pritoritize natural, reddit styles.
Reaction/observation first, then problem, then TrueProfit (if branded).
No hashtags. No emojis. No bullet points inside comments.
Use - not —. Never use em dashes anywhere.
Unbranded comments: short and simple.
Branded count: detect by grepping "TrueProfit" in text, NOT by index formula.

4. TRUEPROFIT VOICE RULES
Can appear as suggestion voice: "I'd suggest", "I'd recommend"
Can appear as first-person usage voice: "I use", "I've been using", "switched to"
Never positioned as the first thing mentioned - always comes AFTER the problem is described
Always framed as solution, never as a brag

5. TRUEPROFIT BRAND CONTEXT
Shopify profit tracking app (trueprofit.io)
Tracks: COGS, Gross Profit, Net Profit, product-level, campaign and store leve profit / margin, ad spend (ROAS/POAS), transaction fees, payment fees, refund costs, shipping costs,...
Target audience: Shopify & ecommerce merchants, DTC brands, dropshippers, print-on-demand sellers
Key seeding angle: Shopify native reports are good but not fully accurate - TrueProfit fills the gap

OUTPUT FORMAT
Pure Markdown. Group as UNBRANDED (n comments) then BRANDED (n comments). Numbered list. No preamble.