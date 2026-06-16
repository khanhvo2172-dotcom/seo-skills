# -*- coding: utf-8 -*-
"""
Localized detection engine for the TrueProfit *multilingual* blog-trigger skill.

This is the sibling of the English-only `detect_triggers.py`. The difference is
that the Spanish / German / French tabs of a blog doc contain TRANSLATED prose,
so the English keyword recognisers ("Formula", "Pro tip", "Note", "Quick Recap",
"FAQ") will not match. This module re-detects each tab with a per-language term
table while keeping the parts that are language-agnostic:

  - Images are objects, not words: counted by document order.
  - A formula is anchored by an "=" on the following line (math is universal);
    the localized "formula" word is only a guard.
  - The trigger LABELS themselves stay in English ("Content Highlight",
    "Image (sentence note):", "Alt is") because the n8n parser keys on them -
    only the alt TEXT is translated.

Like its sibling it is deliberately FREE of any Google API dependency so it can
be unit-tested on synthetic blocks. Block shape and return shape are identical to
`detect_triggers.detect`, so the orchestrator can treat them interchangeably.
"""

import re

# --- Trigger label strings - identical to the English skill / n8n parser -------
CONTENT_HIGHLIGHT_LABEL = "Content Highlight"
IMAGE_TRIGGER_TEMPLATE = "Image (sentence note): {url}, Alt is {alt}"

# Dedup guards - these labels are English in EVERY tab, so they need no locale.
RE_EXISTING_IMAGE_TRIGGER = re.compile(r"^\s*Image\b[^:]*:\s*https?://", re.I)
RE_CONTENT_HIGHLIGHT = re.compile(r"^\s*Content\s+Highlight\b", re.I)

# --- Per-language term tables --------------------------------------------------
# Each entry compiles into recognisers below. Terms are intentionally generous
# (multiple plausible translations) because the localization step translates
# faithfully rather than from a fixed glossary - and the dry-run lets the author
# catch anything missed. Callouts are colon-anchored (the keyword must be followed
# by ":", allowing a French space-before-colon) so ordinary prose that merely uses
# the word ("Note that...", "Un buen consejo es...") does not trigger.
LANG_TERMS = {
    "en": {
        "name": "English",
        "formula": [r"formula"],
        "callout": [r"pro\s*tip", r"note", r"tip"],
        "quick_recap": [r"quick\s+recap"],
        "faq": [r"faqs?", r"frequently\s+asked\s+questions"],
    },
    "es": {
        "name": "Spanish",
        "formula": [r"f[oó]rmula"],
        "callout": [
            r"consejo\s+profesional", r"consejo\s+pro", r"truco\s+profesional",
            r"consejo", r"truco", r"nota", r"aviso", r"importante", r"pro\s*tip",
        ],
        "quick_recap": [r"resumen\s+r[aá]pido", r"recapitulaci[oó]n\s+r[aá]pida", r"resumen"],
        "faq": [r"faqs?", r"preguntas\s+frecuentes"],
    },
    "de": {
        "name": "German",
        "formula": [r"formel"],
        "callout": [
            r"profi-?\s*tipp", r"profitipp", r"tipp", r"hinweis", r"notiz",
            r"anmerkung", r"achtung", r"wichtig", r"pro\s*tip",
        ],
        "quick_recap": [r"kurze\s+zusammenfassung", r"schnelle\s+zusammenfassung", r"zusammenfassung"],
        "faq": [r"faqs?", r"h[aä]ufig\s+gestellte\s+fragen", r"h[aä]ufige\s+fragen"],
    },
    "fr": {
        "name": "French",
        "formula": [r"formule"],
        "callout": [
            r"astuce\s+de\s+pro", r"astuce\s+pro", r"conseil\s+de\s+pro", r"conseil\s+pro",
            r"astuce", r"conseil", r"remarque", r"note", r"[aà]\s+noter", r"attention",
            r"important", r"pro\s*tip",
        ],
        "quick_recap": [r"r[eé]capitulatif\s+rapide", r"r[eé]sum[eé]\s+rapide", r"en\s+bref"],
        "faq": [r"faqs?", r"questions\s+fr[eé]quentes",
                r"questions\s+fr[eé]quemment\s+pos[eé]es", r"foire\s+aux\s+questions"],
    },
}


def _terms(lang):
    if lang not in LANG_TERMS:
        raise ValueError("Unsupported language %r (expected one of %s)"
                         % (lang, ", ".join(sorted(LANG_TERMS))))
    return LANG_TERMS[lang]


def compile_recognisers(lang):
    """Build the per-language regexes from the term table."""
    t = _terms(lang)
    formula_alt = "|".join(t["formula"])
    callout_alt = "|".join(t["callout"])
    qr_alt = "|".join(t["quick_recap"])
    faq_alt = "|".join(t["faq"])
    return {
        # A line that CONTAINS a formula word, e.g. a "Fórmula" heading or an
        # inline lead-in "...la fórmula del margen:". Unlike English (where the
        # word lands at the end), romance/German word order puts it mid-line
        # ("la formule de la marge :"), so we match anywhere. The real
        # discriminator is still the "=" on the next line, checked separately,
        # which is what keeps prose that merely names a formula from triggering.
        "formula": re.compile(r"\b(?:%s)\b" % formula_alt, re.I),
        # A callout opener: keyword at line start, then optional space + colon.
        "callout": re.compile(r"^\s*(?:%s)\s*:" % callout_alt, re.I),
        "quick_recap": re.compile(r"^\s*(?:%s)\b" % qr_alt, re.I),
        # A line ENDING in a FAQ phrase (mirrors the n8n /FAQs?\s*$/i and friends).
        "faq": re.compile(r"(?:(?:%s)\s*:?\s*$)" % faq_alt, re.I),
    }


def _clean(text):
    # Normalise non-breaking spaces (Google Docs uses U+00A0 liberally) and trim.
    return (text or "").replace(chr(0x00A0), " ").strip()


def _next_text_block(blocks, i):
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        if b["kind"] == "text" and _clean(b["text"]):
            return b
        j += 1
    return None


def _prev_nonempty(blocks, i):
    j = i - 1
    while j >= 0:
        b = blocks[j]
        if _clean(b["text"]):
            return b
        j -= 1
    return None


def _index_of(blocks, block):
    for idx, b in enumerate(blocks):
        if b is block:
            return idx
    return -1


# ===========================================================================
# Repair / realign of carried-over triggers
# ---------------------------------------------------------------------------
# In a real multilingual doc the ES/DE/FR tabs are TRANSLATIONS of the English
# markdown, which already contains the trigger lines as text. So those tabs come
# with trigger lines ALREADY PRESENT - but often stale: old/test image URLs and
# alts, the image trigger split across two lines, and "Content Highlight:" with a
# trailing colon. The translated tabs also have NO embedded image objects, so we
# can't anchor new image triggers to images - we repair the carried-over lines in
# place and map them to the English tab BY ORDER (Nth image line <- Nth English
# image URL + Nth translated alt).
# ===========================================================================

CANON_CH = "Content Highlight"

# Start of an image trigger line: the "(sentence note)" label form, or any legacy
# single-line "Image ...: http..." form.
RE_IMAGE_LABEL = re.compile(r"^\s*Image\s*\(sentence note\)", re.I)
RE_CH_ANY = re.compile(r"^\s*Content\s+Highlight\s*:?\s*$", re.I)
RE_URLISH = re.compile(r"https?://", re.I)


def _is_image_start(t):
    return bool(RE_IMAGE_LABEL.match(t) or RE_EXISTING_IMAGE_TRIGGER.search(t))


def parse_existing_triggers(blocks):
    """
    Walk the tab in order and return the carried-over trigger UNITS:
      - {"kind": "image", "start", "end", "single_line_text" or None}
        An image unit is the label line PLUS, when the URL sits on the next line
        (the stale two-line form), that following URL line - so its range covers
        both and a repair replaces the whole thing with one canonical line.
      - {"kind": "ch", "start", "end", "text"}
    Order is document order, which is how they map onto the English triggers.
    """
    units = []
    n = len(blocks)
    i = 0
    while i < n:
        b = blocks[i]
        t = _clean(b["text"])
        if _is_image_start(t):
            start, end = b["start"], b["end"]
            single = t if RE_URLISH.search(t) else None
            if single is None:
                # URL is probably on the next non-empty line - absorb it.
                j = i + 1
                while j < n and not _clean(blocks[j]["text"]):
                    j += 1
                if j < n:
                    nt = _clean(blocks[j]["text"])
                    if RE_URLISH.search(nt) and not _is_image_start(nt) and not RE_CH_ANY.match(nt):
                        end = blocks[j]["end"]
                        i = j  # consume the URL line
            units.append({"kind": "image", "start": start, "end": end, "single_line_text": single})
        elif RE_CH_ANY.match(t):
            units.append({"kind": "ch", "start": b["start"], "end": b["end"], "text": t})
        i += 1
    return units


def _image_line(url, alt):
    # rstrip drops the trailing space when alt is empty, matching the English skill.
    return ("Image (sentence note): %s, Alt is %s" % (url, alt)).rstrip()


def plan_repairs(blocks, en_image_urls, translated_alts, fallback_alts):
    """
    Build in-place repair ops for one translated tab's carried-over triggers.

    en_image_urls : ordered URLs from the English tab (the shared CDN files).
    translated_alts : this language's alt text, image order (may be short/empty).
    fallback_alts : the English alts, used when a translated alt is missing.

    Returns {"ops": [...], "notes": [...], "image_units": int, "ch_units": int,
             "image_repaired": int}. Each op is
        {"start", "end", "text", "reason"}  (end > start -> replace that range).
    No-ops (the line is already canonical) are skipped, so this is idempotent.
    """
    units = parse_existing_triggers(blocks)
    img_units = [u for u in units if u["kind"] == "image"]
    ch_units = [u for u in units if u["kind"] == "ch"]
    ops = []
    notes = []
    repaired = 0

    for k, u in enumerate(img_units):
        if k >= len(en_image_urls):
            notes.append("Image trigger #%d has no matching English image - left as-is." % (k + 1))
            continue
        url = en_image_urls[k]
        if k < len(translated_alts) and translated_alts[k]:
            alt = translated_alts[k]
        elif k < len(fallback_alts):
            alt = fallback_alts[k]
        else:
            alt = ""
        canonical = _image_line(url, alt)
        if u["single_line_text"] is not None and u["single_line_text"] == canonical:
            continue  # already correct
        ops.append({
            "start": u["start"], "end": u["end"], "text": canonical + "\n",
            "reason": "repair image #%d -> %s%s" % (k + 1, url, (" | alt: %s" % alt) if alt else ""),
        })
        repaired += 1

    if len(img_units) != len(en_image_urls):
        notes.append(
            "WARNING: %d image trigger line(s) in this tab vs %d image(s) in English. "
            "Repaired the %d that line up; the rest need manual placement - translated "
            "tabs have no embedded images to anchor new triggers to."
            % (len(img_units), len(en_image_urls), min(len(img_units), len(en_image_urls)))
        )

    # NOTE: Content Highlight handling lives in plan_ch() (Option B), not here -
    # plan_repairs only touches image trigger lines.

    return {
        "ops": ops,
        "notes": notes,
        "image_units": len(img_units),
        "ch_units": len(ch_units),
        "image_repaired": repaired,
    }


def _ch_backed(blocks, i_ch, rec):
    """
    True if the Content Highlight line at block index i_ch is backed by genuine
    translated highlight content on the next non-empty line: a localized Pro tip /
    Note callout (keyword + colon), a formula name line followed by an "=" line, or
    a line that itself carries an "=" formula. Plain prose -> not backed (orphan).
    """
    nxt = _next_text_block(blocks, i_ch)
    if nxt is None:
        return False
    nt = _clean(nxt["text"])
    if rec["callout"].match(nt):
        return True
    if rec["formula"].search(nt):
        after = _next_text_block(blocks, _index_of(blocks, nxt))
        if after and "=" in after["text"]:
            return True
    if "=" in nt:
        return True
    return False


def plan_ch(blocks, lang):
    """
    Repair carried-over Content Highlight lines (Option B). A translated tab is a
    translation of the English markdown, so it can arrive with `Content Highlight`
    lines that no longer sit above any real highlight (the English highlight was a
    test stub, or the translation is from an older draft). So:

      - KEEP (and normalize `Content Highlight:` -> `Content Highlight`) a CH only
        when the next line is genuine translated highlight content (_ch_backed).
      - DELETE an orphan CH whose following line is ordinary prose.

    Adding a CH above newly-detected formula/callout content is handled by detect();
    this function never adds, only normalizes the backed ones and removes orphans.

    Returns {"ops": [...], "kept": int, "deleted": int}. A delete op has no "text".
    """
    rec = compile_recognisers(lang)
    ops = []
    kept = deleted = 0
    for i, b in enumerate(blocks):
        t = _clean(b["text"])
        if not RE_CH_ANY.match(t):
            continue
        if _ch_backed(blocks, i, rec):
            if t != CANON_CH:
                ops.append({
                    "start": b["start"], "end": b["end"], "text": CANON_CH + "\n",
                    "reason": "normalize backed 'Content Highlight'",
                })
            kept += 1
        else:
            ops.append({
                "start": b["start"], "end": b["end"],
                "reason": "remove orphan 'Content Highlight' (next line is plain prose, "
                          "no translated highlight content)",
            })
            deleted += 1
    return {"ops": ops, "kept": kept, "deleted": deleted}


def detect(blocks, lang, image_map=None):
    """
    Analyse one translated tab's blocks and return an insertion plan.

    Parameters
    ----------
    blocks : list of {kind, text, start, end}
        The flattened paragraphs of the language tab.
    lang : "es" | "de" | "fr" (or "en")
        Selects the localized recogniser table.
    image_map : list of (url, alt) or None
        Ordered image triggers for this tab: image #N takes entry N. The URL is
        the same CDN file as the English tab (passed in by the orchestrator); the
        alt is the TRANSLATED alt. If None, no image triggers are planned (e.g.
        an article with no images, or a Content-Highlight-only pass).

    Returns the same dict shape as detect_triggers.detect().
    """
    rec = compile_recognisers(lang)
    insertions = []
    notes = []

    quick_recap_present = any(
        b["kind"] == "text" and rec["quick_recap"].search(_clean(b["text"])) for b in blocks
    )
    faq_present = any(
        b["kind"] == "text" and rec["faq"].search(_clean(b["text"])) for b in blocks
    )

    image_count = 0
    image_triggers_added = 0

    for i, b in enumerate(blocks):
        text = _clean(b["text"])

        # ---- Images: number by document order, skip ones already triggered ----
        if b["kind"] == "image":
            image_count += 1
            prevb = _prev_nonempty(blocks, i)
            nxtb = _next_text_block(blocks, i)
            already = (
                (prevb is not None and RE_EXISTING_IMAGE_TRIGGER.search(_clean(prevb["text"])))
                or (nxtb is not None and RE_EXISTING_IMAGE_TRIGGER.search(_clean(nxtb["text"])))
            )
            if already:
                notes.append("Image #%d already has a trigger line - skipped." % image_count)
                continue
            if image_map is None:
                continue
            if image_count - 1 < len(image_map):
                url, alt = image_map[image_count - 1]
            else:
                notes.append("Image #%d has no entry in the image list - skipped." % image_count)
                continue
            line = IMAGE_TRIGGER_TEMPLATE.format(url=url, alt=alt).rstrip()
            reason = "Image #%d trigger (%s)" % (image_count, url)
            if alt:
                reason += " | alt: %s" % alt
            insertions.append({"index": b["start"], "text": line + "\n", "reason": reason})
            image_triggers_added += 1
            continue

        if b["kind"] != "text" or not text:
            continue

        # ---- Content Highlight: formula line followed by a line with "=" ----
        if rec["formula"].search(text):
            nxt = _next_text_block(blocks, i)
            if nxt and "=" in nxt["text"]:
                before_formula = _prev_nonempty(blocks, _index_of(blocks, nxt))
                already_ch = before_formula is not None and RE_CONTENT_HIGHLIGHT.match(
                    _clean(before_formula["text"])
                )
                if already_ch:
                    notes.append("Formula already has a Content Highlight - skipped.")
                else:
                    insertions.append({
                        "index": nxt["start"],
                        "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                        "reason": "Formula -> Content Highlight",
                    })
            continue

        # ---- Content Highlight: localized Pro tip / Note callouts ----
        if rec["callout"].match(text):
            prev = _prev_nonempty(blocks, i)
            if prev is not None and RE_CONTENT_HIGHLIGHT.match(_clean(prev["text"])):
                notes.append("Callout already has a Content Highlight - skipped.")
            else:
                insertions.append({
                    "index": b["start"],
                    "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                    "reason": "Callout -> Content Highlight",
                })

    if image_map is not None and len(image_map) != image_count:
        notes.append(
            "WARNING: image list has %d entr%s but this tab has %d image(s) - "
            "they must be in the same order. Review the mapping before applying."
            % (len(image_map), "y" if len(image_map) == 1 else "ies", image_count)
        )

    return {
        "insertions": insertions,
        "quick_recap_present": quick_recap_present,
        "faq_present": faq_present,
        "image_count": image_count,
        "image_triggers_added": image_triggers_added,
        "notes": notes,
    }
