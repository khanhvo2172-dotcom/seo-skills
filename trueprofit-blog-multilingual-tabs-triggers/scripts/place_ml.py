# -*- coding: utf-8 -*-
"""
Paragraph-anchored placement of image triggers and Content Highlights for
OUT-OF-SYNC translated tabs (PLACE mode).

When a translated tab is missing its trigger lines (or had them reset), there is
nothing to "repair by order". But the article structure still lines up with the
English tab: a faithful translation keeps the same sections, in the same order,
with the same paragraph breaks. So we MIRROR the English tab:

  1. For every English image, record the heading it sits under and HOW MANY body
     paragraphs precede it within that section (its paragraph ordinal), plus the
     text of the paragraph it follows (its anchor paragraph).
  2. Map that English heading to the corresponding TRANSLATED heading - by order,
     confirmed with cognate keywords (prefix match survives translation:
     competition~competencia, organic~organica, tofu~tofu, USB~USB).
  3. Inside the translated section, place the image AFTER the body paragraph at
     the same ordinal. Pure paragraph counting drifts when a language merges or
     splits a paragraph, so we pick - within a small window around the expected
     ordinal - the translated paragraph whose CONTENT best matches the English
     anchor paragraph (cognate-token overlap), falling back to the ordinal.

Content Highlights are mirrored the same way (a CH sits ABOVE the paragraph it
labels, so it anchors to the FOLLOWING paragraph and inserts before it). This
keeps every editorial highlight - "Your Takeaway", Pro tip, Note, formula - in
parity with English without per-language keyword tables.

Pure module (no Google dependency) so it can be unit-tested. Operates on the same
"blocks" list flatten() produces, where each block carries a "level" (1..6 for
headings, 0 otherwise), "kind", "text", "start", "end".
"""

import re
import unicodedata

from detect_ml import (_clean, _is_image_start, RE_URLISH, _image_line,
                       RE_CH_ANY, CONTENT_HIGHLIGHT_LABEL, compile_recognisers)

# Tokens this short or in this set carry no matching signal across languages.
_STOP = {
    # english
    "the", "a", "an", "and", "or", "of", "for", "with", "to", "in", "on", "your",
    "you", "is", "are", "what", "how", "why", "low", "high", "best", "top", "new",
    # romance / german function words
    "el", "la", "los", "las", "un", "una", "de", "del", "y", "o", "con", "para",
    "por", "en", "que", "es", "como", "der", "die", "das", "und", "mit", "fur",
    "von", "le", "les", "des", "du", "et", "avec", "pour", "comment", "baja",
    "alta", "con", "sin",
}


def _strip_accents(s):
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _tokens(text):
    text = _strip_accents((text or "").lower())
    raw = re.split(r"[^a-z0-9]+", text)
    return [t for t in raw if t and t not in _STOP and (len(t) >= 3 or t.isdigit())]


def _cognate(a, b):
    """True if two tokens are the same word across languages (or a number/loanword)."""
    if a == b:
        return True
    # numbers must match exactly (handled above); otherwise compare a shared prefix.
    if a.isdigit() or b.isdigit():
        return False
    n = min(len(a), len(b))
    if n < 4:
        return False
    # a 4+ char shared prefix catches organic/organica, competition/competencia,
    # cocktail/coctel, niche/nicho, electric/electrico ...
    return a[:4] == b[:4]


def heading_score(en_text, tr_text):
    """How many English heading tokens have a cognate in the translated heading."""
    et = _tokens(en_text)
    tt = _tokens(tr_text)
    score = 0
    for e in et:
        if any(_cognate(e, t) for t in tt):
            score += 1
    return score


# An English paragraph and its translation share content tokens (numbers, brand
# and loan words, cognate roots); this counts that overlap, the same signal used
# to confirm heading matches. Used to correct paragraph drift.
para_score = heading_score


def headings(blocks):
    """Return [{'i','text','level','start','end'}] for every heading block, in order."""
    out = []
    for i, b in enumerate(blocks):
        lvl = b.get("level", 0)
        if lvl and _clean(b["text"]):
            out.append({"i": i, "text": _clean(b["text"]), "level": lvl,
                        "start": b["start"], "end": b["end"]})
    return out


def _is_body(b):
    """A body paragraph: non-empty text, not a heading / image trigger / Content Highlight."""
    if b.get("kind") != "text":
        return False
    t = _clean(b["text"])
    if not t or b.get("level", 0):
        return False
    return not _is_image_start(t) and not RE_CH_ANY.match(t)


def _parse_image_line(text):
    """From an English 'Image (sentence note): <url>, Alt is <alt>' line -> (url, alt)."""
    url, alt = "", ""
    m = RE_URLISH.search(text)
    if m:
        tail = text[m.start():]
        url = re.split(r"[\s,]", tail, maxsplit=1)[0].strip()
    idx = text.lower().find("alt is")
    if idx != -1:
        alt = text[idx + len("alt is"):].strip()
    return url, alt


def choose_anchor(en_text, tr_bodies, expected_idx):
    """Pick the translated body paragraph that best matches the English anchor
    paragraph, searching a small window around the expected ordinal. Falls back
    to the expected index when nothing scores. Returns (index, score, moved)."""
    if not tr_bodies:
        return expected_idx, 0, False
    expected_idx = max(0, min(expected_idx, len(tr_bodies) - 1))
    lo = max(0, expected_idx - 2)
    hi = min(len(tr_bodies) - 1, expected_idx + 2)
    best_i, best_s = expected_idx, -1
    for j in range(lo, hi + 1):
        s = para_score(en_text, _clean(tr_bodies[j]["text"]))
        # tie-break toward the expected ordinal (prefer no move on a tie)
        if s > best_s or (s == best_s and abs(j - expected_idx) < abs(best_i - expected_idx)):
            best_i, best_s = j, s
    if best_s <= 0:
        best_i = expected_idx
    return best_i, best_s, best_i != expected_idx


def english_image_anchors(en_blocks):
    """
    Walk the English tab and, for each image trigger line, record the heading it
    sits under, how many body paragraphs precede it in that section, and the text
    of the paragraph it follows.

    Returns [{'url','alt','h_text','h_level','h_order','offset','body_ordinal',
    'anchor_text'}] in document order. 'h_order' is the heading's ordinal among ALL
    English headings (0-based); 'offset' is 0 for the first image after that heading;
    'body_ordinal' is the number of body paragraphs before the image in its section
    (so the image is placed AFTER the body paragraph at that ordinal); 'anchor_text'
    is that preceding paragraph's text ("" when the image sits right under a heading).
    """
    anchors = []
    cur_h = None
    h_order = -1
    images_since_h = 0
    body_count = 0
    last_body = ""
    for b in en_blocks:
        t = _clean(b["text"])
        if b.get("level", 0) and t:
            h_order += 1
            cur_h = {"text": t, "level": b["level"], "order": h_order}
            images_since_h = 0
            body_count = 0
            last_body = ""
            continue
        if b["kind"] == "text" and _is_image_start(t) and RE_URLISH.search(t):
            url, alt = _parse_image_line(t)
            anchors.append({
                "url": url, "alt": alt,
                "h_text": cur_h["text"] if cur_h else "",
                "h_level": cur_h["level"] if cur_h else 0,
                "h_order": cur_h["order"] if cur_h else -1,
                "offset": images_since_h,
                "body_ordinal": body_count,
                "anchor_text": last_body,
            })
            images_since_h += 1
            continue
        if b["kind"] == "text" and t and not RE_CH_ANY.match(t):
            body_count += 1
            last_body = t
    return anchors


def english_ch_anchors(en_blocks):
    """
    Walk the English tab and, for each Content Highlight line, record the heading
    it sits under and the paragraph it labels (the next body paragraph). The CH is
    placed ABOVE the translated equivalent of that paragraph.

    Returns [{'h_text','h_level','h_order','before_ordinal','anchor_text'}], where
    'before_ordinal' is the 1-based ordinal of the labeled paragraph in its section.
    """
    out = []
    cur_h = None
    h_order = -1
    body_count = 0
    n = len(en_blocks)
    for i, b in enumerate(en_blocks):
        t = _clean(b["text"])
        if b.get("level", 0) and t:
            h_order += 1
            cur_h = {"text": t, "level": b["level"], "order": h_order}
            body_count = 0
            continue
        if RE_CH_ANY.match(t):
            nxt_text = ""
            for k in range(i + 1, n):
                bk = en_blocks[k]
                tk = _clean(bk["text"])
                if bk.get("level", 0) and tk:
                    break  # next heading - the CH has no labeled paragraph in-section
                if bk["kind"] == "text" and tk and not _is_image_start(tk) and not RE_CH_ANY.match(tk):
                    nxt_text = tk
                    break
            out.append({
                "h_text": cur_h["text"] if cur_h else "",
                "h_level": cur_h["level"] if cur_h else 0,
                "h_order": cur_h["order"] if cur_h else -1,
                "before_ordinal": body_count + 1,
                "anchor_text": nxt_text,
            })
            continue
        if b["kind"] == "text" and t and not _is_image_start(t) and not RE_CH_ANY.match(t):
            body_count += 1
    return out


def align_headings(anchors, tr_headings):
    """
    Map each distinct English anchor heading (by its h_order) to a translated
    heading, monotonically and in order. For each English anchor heading we scan
    the translated headings AFTER the last match for the best cognate score,
    preferring the same level; if nothing scores, we fall back to the next
    same-level heading (ordinal), then the next heading of any level.

    Returns {h_order: {'tr': <tr_heading or None>, 'score': int, 'how': str}}.
    """
    result = {}
    last = -1
    seen = []
    for a in anchors:
        if a["h_order"] not in [h["h_order"] for h in seen]:
            seen.append({"h_order": a["h_order"], "text": a["h_text"], "level": a["h_level"]})

    for h in seen:
        best_j, best_score = None, 0
        for j in range(last + 1, len(tr_headings)):
            sc = heading_score(h["text"], tr_headings[j]["text"])
            if tr_headings[j]["level"] == h["level"]:
                sc_eff = sc * 2 + 1 if sc else 0
            else:
                sc_eff = sc * 2
            if sc_eff > best_score:
                best_score, best_j = sc_eff, j
        if best_j is not None and best_score > 0:
            result[h["h_order"]] = {"tr": tr_headings[best_j], "score": best_score, "how": "keyword"}
            last = best_j
        else:
            cand = None
            for j in range(last + 1, len(tr_headings)):
                if tr_headings[j]["level"] == h["level"]:
                    cand = j
                    break
            if cand is None and last + 1 < len(tr_headings):
                cand = last + 1
            if cand is not None:
                result[h["h_order"]] = {"tr": tr_headings[cand], "score": 0, "how": "ordinal"}
                last = cand
            else:
                result[h["h_order"]] = {"tr": None, "score": 0, "how": "unmatched"}
    return result


def _section_end(tr_headings, th, body_fallback):
    """
    Index marking the END of th's section = the start of the next heading whose
    level is <= th's level (its next sibling/parent boundary). Falls back to
    body_fallback when th is the last such section.
    """
    after = False
    for h in tr_headings:
        if h["i"] == th["i"] and h["start"] == th["start"]:
            after = True
            continue
        if after and h["level"] <= th["level"]:
            return h["start"]
    return body_fallback


def section_bodies(blocks, th):
    """Ordered body paragraphs inside th's section (until the next heading whose
    level <= th's level)."""
    out = []
    for k in range(th["i"] + 1, len(blocks)):
        b = blocks[k]
        if b.get("level", 0) and _clean(b["text"]):
            if b["level"] <= th["level"]:
                break
            continue  # a deeper sub-heading - not a body paragraph
        if _is_body(b):
            out.append(b)
    return out


def body_end_index(tr_blocks, lang):
    """Document index that marks the end of the article body = the start of the
    'Final Thoughts' / FAQ region. Used as a fallback anchor for images whose
    English heading has no translated counterpart (e.g. a closing CTA)."""
    if not tr_blocks:
        return 1
    rec = compile_recognisers(lang) if lang else None
    hs = headings(tr_blocks)
    if rec is not None:
        for h in hs:
            if rec.get("final_thoughts") and rec["final_thoughts"].search(h["text"]):
                return h["start"]
        for h in hs:
            if rec["faq"].search(h["text"]):
                return h["start"]
    return tr_blocks[-1]["start"]


def plan_placements(tr_blocks, anchors, translated_alts, fallback_alts, lang=None):
    """
    Build insert ops that place every English image into the translated tab at the
    SAME paragraph position as English (after the matching translated paragraph),
    using cognate-based drift correction.

    Returns {'ops','review','notes','warnings','placed'}. Each op is a pure insert
    {'start','text','reason'}. 'review' has one row per image for the dry-run;
    'warnings' flags any non-keyword heading match or out-of-range ordinal.
    """
    tr_headings = headings(tr_blocks)
    alignment = align_headings(anchors, tr_headings)
    body_fallback = body_end_index(tr_blocks, lang)
    ops, review, notes, warnings = [], [], [], []
    placed = 0

    for n, a in enumerate(anchors):
        if n < len(translated_alts) and translated_alts[n]:
            alt = translated_alts[n]
        elif n < len(fallback_alts):
            alt = fallback_alts[n]
        else:
            alt = ""
        line = _image_line(a["url"], alt)
        m = alignment.get(a["h_order"])
        how = m["how"] if m else "unmatched"

        if not m or not m["tr"]:
            ops.append({"start": body_fallback, "text": line + "\n",
                        "reason": "place image #%d at end of body (no translated heading)" % (n + 1)})
            review.append({"n": n + 1, "url": a["url"], "en_heading": a["h_text"],
                           "tr_heading": "(end of body)", "how": "fallback", "para": ""})
            warnings.append("image #%d ('%s') had no translated heading - placed at end of body"
                            % (n + 1, a["h_text"][:30]))
            placed += 1
            continue

        th = m["tr"]
        if how != "keyword":
            warnings.append("image #%d anchored to '%s' by %s (no shared keyword) - verify the "
                            "English and translated headings line up" % (n + 1, th["text"][:30], how))
        if th["start"] >= body_fallback:
            # The matched heading is in the closing Final Thoughts / FAQ region -
            # whether by ordinal fallback or a coincidental keyword (e.g. an English
            # "...Store Performance" heading matching a translated "...Stores?" FAQ).
            # A body image (e.g. a closing CTA) belongs at the end of the body, not
            # buried inside the FAQ.
            ops.append({"start": body_fallback, "text": line + "\n",
                        "reason": "place image #%d at end of body (matched a closing-region heading)" % (n + 1)})
            review.append({"n": n + 1, "url": a["url"], "en_heading": a["h_text"],
                           "tr_heading": "(end of body)", "how": "fallback", "para": ""})
            if how == "keyword":
                warnings.append("image #%d keyword-matched the closing-region heading '%s' - "
                                "placed at end of body instead" % (n + 1, th["text"][:30]))
            placed += 1
            continue
        bodies = section_bodies(tr_blocks, th)
        ordn = a["body_ordinal"]
        if ordn <= 0:
            insert_at = th["end"]
            para = "(under heading)"
        elif bodies:
            idx, _score, _moved = choose_anchor(a["anchor_text"], bodies, ordn - 1)
            insert_at = bodies[idx]["end"]
            para = _clean(bodies[idx]["text"])[:50]
        else:
            insert_at = _section_end(tr_headings, th, body_fallback)
            para = "(section end)"
            warnings.append("image #%d: section '%s' has no body paragraphs - placed at section end"
                            % (n + 1, th["text"][:30]))
        ops.append({"start": insert_at, "text": line + "\n",
                    "reason": "place image #%d after paragraph %d of '%s'"
                              % (n + 1, ordn, th["text"][:30])})
        review.append({"n": n + 1, "url": a["url"], "en_heading": a["h_text"],
                       "tr_heading": th["text"], "how": how, "para": para})
        placed += 1

    return {"ops": ops, "review": review, "notes": notes, "warnings": warnings, "placed": placed}


def plan_ch_placements(tr_blocks, ch_anchors, lang=None):
    """
    Mirror the English tab's Content Highlights into the translated tab: insert a
    'Content Highlight' label ABOVE the translated equivalent of each labeled
    paragraph, anchored by paragraph ordinal with cognate drift correction.

    Returns {'ops','review','notes','warnings','placed'}. Each op is a pure insert
    of 'Content Highlight\\n' at the labeled paragraph's start.
    """
    tr_headings = headings(tr_blocks)
    alignment = align_headings(ch_anchors, tr_headings)
    rec = compile_recognisers(lang) if lang else None
    ops, review, notes, warnings = [], [], [], []
    placed = 0

    for n, a in enumerate(ch_anchors):
        m = alignment.get(a["h_order"])
        if not m or not m["tr"]:
            warnings.append("Content Highlight #%d ('%s') had no translated heading - skipped"
                            % (n + 1, a["h_text"][:30]))
            continue
        th = m["tr"]
        bodies = section_bodies(tr_blocks, th)
        if not bodies:
            warnings.append("Content Highlight #%d: section '%s' has no body paragraphs - skipped"
                            % (n + 1, th["text"][:30]))
            continue
        exp = max(0, min(a["before_ordinal"] - 1, len(bodies) - 1))
        # A Content Highlight labels a callout (Your Takeaway / Pro tip / Note). The
        # translation may split "Label: text" into a bare "Label:" line plus the text
        # on the next line; cognate scoring would prefer the text, so snap to the
        # callout LABEL line when one is in the window. Otherwise fall back to cognate.
        idx = None
        lo, hi = max(0, exp - 2), min(len(bodies) - 1, exp + 2)
        if rec is not None:
            cands = [j for j in range(lo, hi + 1) if rec["callout"].match(_clean(bodies[j]["text"]))]
            if cands:
                idx = min(cands, key=lambda j: (abs(j - exp), j))
        if idx is None and "=" in (a["anchor_text"] or ""):
            # The English CH labels a FORMULA ("X = ..."). Formula terms rarely
            # cognate across languages (German compounds share no prefix with the
            # English), so token scoring can drift onto a nearby further-reading
            # line whose URL slug coincidentally carries English words. The "="
            # is the universal discriminator (same rule detect_ml uses), so snap
            # to the in-window translated line that carries an "=" and is not a URL.
            fcands = [j for j in range(lo, hi + 1)
                      if "=" in _clean(bodies[j]["text"])
                      and not RE_URLISH.search(_clean(bodies[j]["text"]))]
            if fcands:
                idx = min(fcands, key=lambda j: (abs(j - exp), j))
        if idx is None:
            idx, _score, _moved = choose_anchor(a["anchor_text"], bodies, exp)
        target = bodies[idx]
        ops.append({"start": target["start"], "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                    "reason": "Content Highlight above '%s'" % (_clean(target["text"])[:40])})
        review.append({"n": n + 1, "tr_heading": th["text"], "how": m["how"],
                       "para": _clean(target["text"])[:50]})
        placed += 1

    return {"ops": ops, "review": review, "notes": notes, "warnings": warnings, "placed": placed}
