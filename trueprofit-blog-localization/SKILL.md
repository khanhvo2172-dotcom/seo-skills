---
name: trueprofit-blog-localization
description: Translates TrueProfit blog articles into Spanish (Spain), German (Germany), and French (France) for ecommerce/Shopify content. Use this skill whenever the user uploads a markdown blog file and asks for translation, localization, or asks to produce ES/DE/FR versions of a TrueProfit article. Also use when the user asks to fix, correct, or re-deliver any previously translated localization file.
---

# TrueProfit Blog Localization (ES / DE / FR)

Translates TrueProfit blog markdown files into three locales: Spanish (Spain), German (Germany), French (France). Delivers Google Docs–friendly Markdown files.

---

## Workflow

1. Read the uploaded `.md` file fully via bash `cat`
2. Identify which languages are requested (default: all three)
3. Apply all rules below to each language
4. Output one `.md` file per language, named `<original_filename>_ES.md`, `_DE.md`, `_FR.md`
5. Save to `/mnt/user-data/outputs/` and call `present_files`
6. Post a brief QA summary of rules applied

---

## Core Translation Rules (apply to every article, every language)

### 1. Translation only — no rewriting or restructuring
Translate meaning faithfully. Do not reorder sections, add new content, or remove anything.

### 2. Preserve structure exactly
All Markdown formatting must be identical to the source: heading levels (`#`, `##`, `###`), bullet points, bold, tables, blockquotes, CTAs, emojis, image placeholders (`![][image1]`), and plain-URL Further Reading links.

### 3. Links
- Inline hyperlinks: keep slug unchanged, translate anchor text, embed inline in translated body
- Further Reading plain URLs: leave entirely unchanged (no anchor text to translate)

### 4. FAQs
Translate fully, including H3 headings.

### 5. Google Docs–friendly Markdown output
Standard Markdown only. No HTML tags.

### 6. Capitalization
Mirror the source exactly. If source uses Title Case for a heading, use it in the target language too.

### 7. Special bolding
Always bold these terms when they appear (in any language):
- **Gross Profit Margin:**
- **Entry Cost:**
- **Scalability:**

### 8. Currency conversion
- **Shopify fees article only**: convert USD → EUR, show EUR only (no USD)
- **All other articles**: keep USD amounts as-is; add EUR in parentheses using `EUR = USD ÷ 1.1894`, rounded sensibly
- Locale number formatting:

| Locale | Decimal | Thousands | % spacing |
|--------|---------|-----------|-----------|
| ES | comma `€2,69` | period `€84.076` | no space `60%` |
| DE | comma `€2,69` | period `€84.076` | space `60 %` |
| FR | comma `€2,69` | space `€84 076` | space `60 %` |

### 9. No em dashes
Never use `—` in any language. Replace with comma, colon, or semicolon depending on context.

### 10. "2026" freshness signals
Insert minimally where natural (e.g., in H1 if source has it). Do not add more than the source contains.

---

## Additional Rules

- **Brand names in English always**: TrueProfit, Shopify, AliExpress, Amazon, TikTok, Meta, Etsy, Canva, Printify, SaaS, POD, FMCG, etc.
- **Internal editorial comments** (e.g., Vietnamese text): exclude entirely from output
- **Images**: skip image files; preserve image placeholder syntax (`![][image1]`) and any Figma/image links unchanged
- **SEO edits**: only when explicitly requested by the user

---

## Output Efficiency

- **Small corrections** (user points out a specific missed link, em dash, currency): deliver only the corrected paragraph(s) in all three languages — do not regenerate full documents
- **Substantial changes** (source paragraph updated, section added): regenerate full affected document(s)

---

## QA Checklist (post in chat after delivering files)

After delivering, briefly confirm:
- [ ] All inline links embedded with translated anchor text
- [ ] No em dashes in any file
- [ ] Brand names in English
- [ ] Currency handled correctly for article type
- [ ] % spacing correct per locale
- [ ] Structure/headings/tables identical to source
- [ ] Special bolding applied where applicable
- [ ] "2026" signals present if in source
- [ ] Vietnamese/editorial comments excluded
