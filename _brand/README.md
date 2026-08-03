# Shared TrueProfit brand context

`trueprofit-brand.md` is the **single source of truth** for TrueProfit facts (identity, features, pricing, proof stats, benchmark data, Shopify platform pricing, competitor comparison, Harry Chu bio + links, URLs, brand channels).

## How it works

Each participating skill has a `## TrueProfit Brand Reference` section with the master content injected between markers:

```
<!-- BRAND:START -->
...generated from trueprofit-brand.md...
<!-- BRAND:END -->
```

The facts live **physically inside each SKILL.md**, so skills stay self-contained and portable — there is no runtime dependency on this folder.

## Updating a fact

1. Edit `trueprofit-brand.md`.
2. Run:

   ```bash
   node _brand/sync-brand.js
   ```

3. Commit the changed skill files.

## Adding a skill to shared context

Give the skill a `## TrueProfit Brand Reference` heading followed by a `---` rule (or paste the two BRAND markers directly), add its folder name to `TARGETS` in `sync-brand.js`, and re-run. The first run replaces the placeholder section with the markers; later runs just refresh the text between them (idempotent).

## Currently wired

- `trueprofit-guest-post`
- `trueprofit-guest-post-full-article`
