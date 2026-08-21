# Step 1 — Internal & External Link Review

**Goal:** turn the raw output of the "Check Internal & External Links in Google Docs" tool
into a short, high-value set of recommendations: which internal links to *add* (and how),
which duplicate links to *remove*, and whether every external reference is *accurate and
authoritative*.

You do **not** edit the Doc. You produce a chat report the user acts on.

There are three phases: **A. Get the data** (run the app), **B. Read the doc** (for context),
**C. Analyze & report**.

---

## Phase A — Run the link-checker app (browser)

The tool has no API; drive it in the browser. App URL:
`https://personal-seo-apps.streamlit.app/`

Use the browser tools (`preview_start` / `navigate`, then `read_page`, `find`, `computer`,
`form_input`). Exact steps:

1. **Open the app.** `preview_start` (or `navigate`) to `https://personal-seo-apps.streamlit.app/`.
   Streamlit Cloud puts idle apps to sleep — if you see a **"Yes, get this app back up!"**
   button, click it and wait for the app to boot (can take 30–60s).
2. **Open the feature.** In the left sidebar, click the button labeled
   **`🔗  Check Internal & External Links in Google Docs`**.
3. **Pick the source.** In the radio group, select **`📄 Google Doc`**.
4. **Fill the Doc URL.** In the field labeled **`Google Doc URL`**, enter the article's Google
   Docs URL (use `form_input` on the input's ref).
5. **Fill the candidates.** In the textarea labeled **`URLs to check — one per line`** (the
   left box), paste the user's URLs-to-check list verbatim (one `url | title` per line).
6. **Fill the must-have URLs (if any).** In the textarea labeled
   **`Must-have URLs — one per line`** (the right box), paste any links the user flagged as
   *must be present*. These are checked like the left box, are merged into the target set (so
   they surface in Missing/Duplicate even if omitted from the left box), and every matching
   result row is flagged **`⭐ Must-have`** in the tables' **`Note`** column. If the user gave
   no must-have list, leave this box empty.
7. **Run.** Click the primary button **`🔍 Check Links`**.
8. **Wait for completion.** Spinners cycle through *"Fetching document…" → "Checking URL
   status codes…" → "Checking external domain DR (Ahrefs)…"*. Typical run is ~8–20s but the
   DR fetch can be slower. Poll `read_page` until the three result sections render.
9. **Capture the three tables** (read them with `read_page` / `get_page_text`). Each table now
   carries a **`Note`** column showing **`⭐ Must-have`** on rows matching a must-have URL:
   - **`✅ All Links Found in Document`** — columns: `#`, `🔗 Link`, `💬 Anchor Text`,
     `Status Code`, `DR (Ahrefs)`, `Note`. This is the master list of links actually in the doc.
   - **`🚫 Missing Links`** — columns: `URL`, `Title`, `Status Code`, `Note`. Candidates from
     your list (and any must-haves) that are **not** in the doc yet.
   - **`🔁 Duplicate Links (> 1 occurrence)`** — columns: `URL`, `Count`, `Status Code`, `Note`.

**If "Fetching document…" errors:** the doc isn't shared with the app's service account. Tell
the user to either share the Doc with the service-account email (shown in the app's Settings
feature) or set it to "anyone with the link can view", then retry. Don't guess the tables.

> If the browser is unavailable or the app won't wake, ask the user to run the feature
> themselves and paste the three tables — the analysis in Phase C works the same either way.

---

## Phase B — Read the doc for context

Read the article's text **from the tab in the URL only** so you can propose real anchor text and
verify external claims. Use **`scripts/dump_tab.py`** — it reads just that one tab and renders
links inline as `[anchor](url)`:

```bash
python dump_tab.py --doc "<DOC_URL_WITH_?tab=...>" --out "<scratchpad>/tab.md"
```

Then read `tab.md`. **Do not use the Drive `read_file_content` tool here** — it concatenates every
tab of the doc, so sibling tabs (an `n8n flow` draft, `Insights & outline` notes) bleed in and get
mistaken for scratch. A single tab is small (~250–450 lines), so read it directly; a subagent is
only needed if a tab is unusually large. You need two things from the body:

- **Sentences and phrases** near where each *missing* link's topic is discussed — candidate
  anchor text.
- **The exact claim/number** wrapped around each *external* link — what we assert vs. what the
  source says.

---

## Phase C — Analyze & report

Produce three subsections. Be selective: recommend what adds value, not everything possible.

### C1. Missing internal links → propose insertions

**Must-have links are not optional.** Any Missing row flagged **`⭐ Must-have`** in its `Note`
column must be recommended for insertion — mark it **Priority: Must-have** and always propose a
placement (anchor preferred, Related reading only as a fallback). Never list a must-have among
the "skipped" links; if it genuinely has no natural home, say so and still place it in Related
reading, then flag that the section may need a sentence to host it.

For the remaining (non-must-have) rows, decide **necessity**: does linking this page make the
article more useful or strengthen its SEO/topical relevance? Skip links that would be forced or
off-topic — you do **not** need to place all of them.

For each link you recommend, choose one of two placements:

1. **Anchor text (preferred).** Either:
   - **Existing phrase** — you found a relevant phrase already in the content: give the exact
     phrase to hyperlink and the section it's in; or
   - **New/modified sentence** — no natural phrase exists: write a short sentence (or a small
     edit to an existing one) that introduces a natural anchor, and say where it goes.
2. **Related reading list.** For genuinely relevant links that don't fit any sentence naturally,
   recommend adding them to a "Related reading" list (create one at the end if absent).

Present as a table:

| Priority | URL | Suggested placement | Anchor text | Where / suggested sentence | Why |
|----------|-----|---------------------|-------------|----------------------------|-----|

- **Priority**: `Must-have` (⭐ rows) / High / Medium — reflect the flag first, then SEO +
  relevance value. List Must-have rows at the top.
- **Suggested placement**: `Anchor — existing phrase` / `Anchor — new sentence` / `Related reading`.
- Put the non-must-have links you deliberately skipped in a one-line note beneath the table
  (with the reason), so the user sees you considered them. Never skip a ⭐ Must-have.

### C2. Duplicate links → propose removals

For each row in **Duplicate Links (> 1 occurrence)**, the same URL is linked more than once.
Recommend keeping the **single most contextually relevant** occurrence and removing the rest
(over-linking the same URL dilutes SEO value and reads as spammy).

| URL | Count | Note | Keep occurrence in… | Remove from… | Why |
|-----|-------|------|---------------------|--------------|-----|

Use the anchor-text / section context from the doc (Phase B) to say which occurrence to keep.
A **`⭐ Must-have`** duplicate still gets dedupe advice, but it must remain present **at least
once** — keep the strongest occurrence, remove only the extras.

### C3. External links → accuracy & authority

Work from **All Links Found in Document**, taking only the **external** links (host is not
`trueprofit.io`). For each external link, check two things:

1. **Benchmark accuracy.** Find the claim/stat in our doc that cites this source (Phase B),
   `WebFetch` the source page, and confirm our number/benchmark actually matches what the
   source says. **Fetch and verify every external reference**, not just the prominent ones.
   Flag any mismatch with both values.
2. **Domain authority.** Read `DR (Ahrefs)` from the table. **DR ≥ 65 = high authority.** Flag
   every external domain with **DR < 65** and suggest replacing it with a higher-authority
   source (or dropping the claim). Reminding the user about low-authority sources is a core goal
   of this step — never skip it.

Also flag any link (internal or external) whose **`Status Code`** is not `200` (broken /
redirecting), since that's an easy publish-blocker to catch here.

| External URL | DR | Authority | Our claim | Source says | Verdict | Action |
|--------------|----|-----------|-----------|-------------|---------|--------|

- **Authority**: `✅ High (DR≥65)` or `⚠️ Low (DR<65)`.
- **Verdict**: `✅ Matches` / `❌ Mismatch` / `⚠️ Can't verify` (say why — paywall, page
  changed, stat not found).
- **Action**: concrete next step (keep / fix number to X / replace source / remove).

---

## Report structure (chat)

Deliver in chat with this shape:

```
# Link Review — <article title or doc name>

**Ran:** <N> URLs checked · <M> links found in doc · <X> missing · <Y> duplicates · <Z> external

## 1. Internal link opportunities (add)
<table from C1 + skipped-links note>

## 2. Duplicate links (remove)
<table from C2, or "None found">

## 3. External references (accuracy & authority)
<table from C3>
**⚠️ Low-authority sources (DR<65):** <bullet list, or "none">
**Broken / non-200 links:** <bullet list, or "none">

## Bottom line
<2–4 sentence summary: what to add, what to remove, what to fix before publishing>
```

Keep it scannable — the user applies these edits in the Doc by hand.
