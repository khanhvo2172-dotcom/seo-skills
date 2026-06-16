# -*- coding: utf-8 -*-
"""
Heading-anchored placement of image triggers for OUT-OF-SYNC translated tabs.

When a translated tab was made from an older English draft, its image-trigger
lines are missing or misplaced - there is nothing to "repair by order". But the
article structure still lines up: every English image sits right after a heading,
and the translated tab has the same headings in the same order (just translated).

So we place each English image trigger by:
  1. finding the heading each English image sits under (its anchor),
  2. mapping that English heading to the corresponding TRANSLATED heading - by
     order, confirmed with cognate keywords (prefix match survives translation:
     competition~competencia, organic~organica, tofu~tofu, USB~USB),
  3. inserting the canonical trigger line right after that translated heading,
     with the translated alt.

Pure module (no Google dependency) so it can be unit-tested. Operates on the same
"blocks" list the orchestrator's flatten() produces, where each block carries a
"level" (1..6 for headings, 0 otherwise).
"""

import re
import unicodedata

from detect_ml import _clean, _is_image_start, RE_URLISH, _image_line

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
    # cocktail/coctel, niche/nicho, electric/electrico, jewelry/joyeria? (no) ...
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


def headings(blocks):
    """Return [{'i','text','level','start','end'}] for every heading block, in order."""
    out = []
    for i, b in enumerate(blocks):
        lvl = b.get("level", 0)
        if lvl and _clean(b["text"]):
            out.append({"i": i, "text": _clean(b["text"]), "level": lvl,
                        "start": b["start"], "end": b["end"]})
    return out


def _parse_image_line(text):
    """From an English 'Image (sentence note): <url>, Alt is <alt>' line -> (url, alt)."""
    url, alt = "", ""
    m = RE_URLISH.search(text)
    if m:
        tail = text[m.start():]
        url = re.split(r"[\s,]", tail, 1)[0].strip()
    idx = text.lower().find("alt is")
    if idx != -1:
        alt = text[idx + len("alt is"):].strip()
    return url, alt


def english_image_anchors(en_blocks):
    """
    Walk the English tab and, for each image trigger line, record the heading it
    sits under and its offset among images under that heading.

    Returns [{'url','alt','h_text','h_level','h_order','offset'}] in document order.
    'h_order' is the heading's ordinal among ALL English headings (0-based);
    'offset' is 0 for the first image after that heading, 1 for the second, ...
    """
    anchors = []
    cur_h = None          # {'text','level','order'}
    h_order = -1
    images_since_h = 0
    for b in en_blocks:
        t = _clean(b["text"])
        if b.get("level", 0) and t:
            h_order += 1
            cur_h = {"text": t, "level": b["level"], "order": h_order}
            images_since_h = 0
            continue
        if b["kind"] == "text" and _is_image_start(t) and RE_URLISH.search(t):
            url, alt = _parse_image_line(t)
            anchors.append({
                "url": url, "alt": alt,
                "h_text": cur_h["text"] if cur_h else "",
                "h_level": cur_h["level"] if cur_h else 0,
                "h_order": cur_h["order"] if cur_h else -1,
                "offset": images_since_h,
            })
            images_since_h += 1
    return anchors


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
    # distinct anchor headings in document order
    seen = []
    for a in anchors:
        if a["h_order"] not in [h["h_order"] for h in seen]:
            seen.append({"h_order": a["h_order"], "text": a["h_text"], "level": a["h_level"]})

    for h in seen:
        best_j, best_score = None, 0
        for j in range(last + 1, len(tr_headings)):
            sc = heading_score(h["text"], tr_headings[j]["text"])
            # prefer same level on ties by giving it a slight edge
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
            # ordinal fallback: next same-level heading after last, else next heading
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
    level is <= th's level (its next sibling/parent boundary). That mirrors the
    English tab, where each image is the LAST paragraph of its section (right
    above the next heading), not the first paragraph under it. Falls back to
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


def plan_placements(tr_blocks, anchors, translated_alts, fallback_alts):
    """
    Build insert ops that place every English image trigger into the translated
    tab at the END of the mapped translated heading's section (right before the
    next heading), mirroring how the English tab positions each image.

    Returns {'ops': [...], 'review': [...], 'notes': [...], 'placed': int}.
    Each op is {'start': index, 'text': line+'\\n', 'reason': str} (pure insert).
    'review' has one row per image for the dry-run: matched heading + confidence.
    """
    tr_headings = headings(tr_blocks)
    alignment = align_headings(anchors, tr_headings)
    body_fallback = tr_blocks[-1]["start"] if tr_blocks else 1
    ops, review, notes = [], [], []
    placed = 0

    for n, a in enumerate(anchors):
        if n < len(translated_alts) and translated_alts[n]:
            alt = translated_alts[n]
        elif n < len(fallback_alts):
            alt = fallback_alts[n]
        else:
            alt = ""
        m = alignment.get(a["h_order"])
        if not m or not m["tr"]:
            notes.append("Image #%d (%s) had no translated heading to anchor to - skipped."
                         % (n + 1, a["url"]))
            review.append({"n": n + 1, "url": a["url"], "en_heading": a["h_text"],
                           "tr_heading": "(none)", "how": "unmatched", "alt": alt})
            continue
        th = m["tr"]
        line = _image_line(a["url"], alt)
        # Insert at the END of the section (right before the next heading), like
        # English. Multiple images under one heading (offset 0,1,...) all insert at
        # the same section-end index and are merged in document order by the request
        # builder, preserving their order.
        insert_at = _section_end(tr_headings, th, body_fallback)
        ops.append({"start": insert_at, "text": line + "\n",
                    "reason": "place image #%d at end of section '%s' (%s)"
                              % (n + 1, th["text"][:40], m["how"])})
        review.append({"n": n + 1, "url": a["url"], "en_heading": a["h_text"],
                       "tr_heading": th["text"], "how": m["how"], "alt": alt})
        placed += 1

    return {"ops": ops, "review": review, "notes": notes, "placed": placed}
