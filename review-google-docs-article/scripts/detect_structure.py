# -*- coding: utf-8 -*-
"""
Structure checks for the review-google-docs-article skill (Steps 2 & 3).

Pure logic, NO Google API dependency, so it can be unit tested on synthetic
input. Given a flat, ordered list of paragraph "blocks" from the article's first
tab, it:

  - counts Heading 2 sections, EXCLUDING "Quick Recap" (a structural summary,
    not a body section); the FAQ heading is a normal H2 and counts;
  - plans a CTA image trigger above a "[cta]" marker, but only when the article
    has MORE than 5 counted H2s (short articles get a warning instead);
  - warns when a "Further Reading" block sits directly above the 2nd-5th H2.

This is a deliberate, self-contained COPY of the CTA / Further-Reading logic that
also lives in the trueprofit-blog-triggers skill. It is kept separate on purpose
so the review skill can evolve independently, and it carries two differences the
review workflow wants:
  1. Quick Recap is excluded from the H2 count and the FR ordinal numbering.
  2. Further-Reading list items are detected by their LIST BULLET, not only by a
     literal "http" in the text - real docs hyperlink the items, so the visible
     text is the anchor text with no URL in it.

A block is a dict:
    { "kind": "text"|"image", "text": str, "start": int, "end": int,
      "level": int, "is_list": bool }
`start`/`end` are Google Docs character indices; `level` is the heading level
(2 for HEADING_2, 0 for body); `is_list` is True for a bulleted/numbered list
item. For pure-logic tests, indices can be any monotonic ints and `is_list` may
be omitted (treated as False).
"""

import re

# --- CTA image ---------------------------------------------------------------
# The CTA image is a fixed shared asset that links to the Shopify app listing,
# tagged with the article's main keyword (utm_campaign).
CTA_IMAGE_URL = "https://be.trueprofit.io/uploads/app-listing-CTA-3.webp"
CTA_IMAGE_ALT = "TrueProfit CTA"
CTA_LINK_TEMPLATE = (
    "https://apps.shopify.com/trueprofit"
    "?utm_source=trueprofit.io&utm_medium=blog&utm_campaign={campaign}"
)
# "Link is" comes BEFORE "Alt is" on purpose: the n8n parser reads the alt to the
# end of the line, so a link placed after the alt would be swallowed into it.
CTA_TRIGGER_TEMPLATE = "Image (sentence note): {url}, Link is {link}, Alt is {alt}"
# A CTA image only belongs in a long-enough article, measured in counted H2
# sections: MORE than this many, or no CTA.
CTA_MIN_H2 = 5

RE_CTA_MARKER = re.compile(r"\[\s*cta\s*\]", re.I)

# --- Further Reading ---------------------------------------------------------
RE_FURTHER_READING = re.compile(r"^\s*further\s+reading\b", re.I)
# Warn only for these H2 ordinals (Quick Recap excluded from the numbering).
FR_WARN_H2_ORDINALS = (2, 3, 4, 5)

# --- Recognisers -------------------------------------------------------------
RE_QUICK_RECAP = re.compile(r"^\s*Quick\s+Recap\b", re.I)
# Matches the n8n parser's FAQ heading rule: ends in FAQ/FAQs, or the full phrase.
RE_FAQ = re.compile(r"(?:FAQs?\s*:?\s*$|frequently\s+asked\s+questions)", re.I)
# An Image trigger already present in the doc (so we never add a second CTA line).
RE_EXISTING_IMAGE_TRIGGER = re.compile(r"^\s*Image\b[^:]*:\s*https?://", re.I)


def _clean(text):
    # Google Docs uses U+00A0 (non-breaking space) liberally; normalise and trim.
    return (text or "").replace(chr(0x00A0), " ").strip()


def _next_nonempty_at(blocks, i):
    """(position, block) of the next block with content after i, or (-1, None)."""
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        if b["kind"] == "image" or _clean(b["text"]):
            return j, b
        j += 1
    return -1, None


def _prev_nonempty(blocks, i):
    """The previous non-empty block before i, or None."""
    j = i - 1
    while j >= 0:
        if _clean(blocks[j]["text"]):
            return blocks[j]
        j -= 1
    return None


def _fr_block_end(blocks, i):
    """
    Position of the LAST block belonging to the Further Reading block that starts
    at i - the trailing run of reading-list items under the label.

    Items are recognised by their LIST BULLET (`is_list`) OR a literal http URL in
    the text (older plain-text docs). Blank lines inside the run are tolerated.
    Recognising the bullet is the fix for hyperlinked lists: their visible text is
    the anchor text, so there is no "http" to match.
    """
    last = i
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        t = _clean(b["text"])
        if b["kind"] == "text" and not t:
            j += 1
            continue
        if b["kind"] == "text" and (b.get("is_list") or "http" in t.lower()):
            last = j
            j += 1
            continue
        break
    return last


def _h2_positions(blocks):
    """
    Positions of the counted Heading 2 paragraphs, in document order. Quick Recap
    is a structural summary, not a body section, so it is EXCLUDED from both the
    count and the ordinal numbering. FAQ is a normal H2 and counts.
    """
    return [
        i
        for i, b in enumerate(blocks)
        if b.get("level") == 2
        and _clean(b["text"])
        and not RE_QUICK_RECAP.search(_clean(b["text"]))
    ]


def detect(blocks, cta_campaign=None):
    """
    Analyse the first tab's blocks and return a plan:
      {
        "insertions": [ {index, text, reason}, ... ],   # CTA line(s) to insert
        "quick_recap_present": bool,
        "faq_present": bool,
        "h2_count": int,          # Quick Recap excluded, FAQ counted
        "cta_markers": int,
        "cta_added": int,
        "warnings": [str, ...],
        "notes": [str, ...],
      }
    `cta_campaign` is the utm_campaign value (main-keyword slug) for the CTA link.
    """
    insertions = []
    warnings = []
    notes = []

    quick_recap_present = any(
        b["kind"] == "text" and RE_QUICK_RECAP.search(_clean(b["text"])) for b in blocks
    )
    faq_present = any(
        b["kind"] == "text" and RE_FAQ.search(_clean(b["text"])) for b in blocks
    )

    h2_pos = _h2_positions(blocks)
    h2_count = len(h2_pos)

    cta_markers = 0
    cta_added = 0

    # ---- CTA image: "[cta]" marker -> fixed image + linked Shopify listing -----
    for i, b in enumerate(blocks):
        if b["kind"] != "text":
            continue
        text = _clean(b["text"])
        if not text or not RE_CTA_MARKER.search(text):
            continue
        cta_markers += 1
        prevb = _prev_nonempty(blocks, i)
        if prevb is not None and RE_EXISTING_IMAGE_TRIGGER.search(_clean(prevb["text"])):
            notes.append("CTA marker already has an image trigger above it - skipped.")
        elif h2_count <= CTA_MIN_H2:
            warnings.append(
                "CTA image NOT added: the article has only %d Heading 2 section(s) "
                "(Quick Recap excluded, FAQ counted). A CTA image needs more than %d - "
                "decide manually whether this article should carry one."
                % (h2_count, CTA_MIN_H2)
            )
        elif not cta_campaign:
            warnings.append(
                "CTA image qualifies (%d H2s) but no main-keyword slug was supplied for "
                "utm_campaign. Re-run with the confirmed keyword." % h2_count
            )
        else:
            link = CTA_LINK_TEMPLATE.format(campaign=cta_campaign)
            line = CTA_TRIGGER_TEMPLATE.format(url=CTA_IMAGE_URL, link=link, alt=CTA_IMAGE_ALT)
            insertions.append(
                {
                    "index": b["start"],
                    "text": line + "\n",
                    "reason": "CTA image trigger (utm_campaign: %s)" % cta_campaign,
                }
            )
            cta_added += 1

    # ---- Further Reading placement (warn only, never edited) -------------------
    for i, b in enumerate(blocks):
        if b["kind"] != "text" or not RE_FURTHER_READING.match(_clean(b["text"])):
            continue
        j, nxt = _next_nonempty_at(blocks, _fr_block_end(blocks, i))
        if nxt is None or nxt.get("level") != 2:
            continue
        ordinal = h2_pos.index(j) + 1 if j in h2_pos else 0
        if ordinal in FR_WARN_H2_ORDINALS:
            warnings.append(
                'Further Reading block sits directly above H2 #%d ("%s") - it reads as '
                "belonging to that heading instead of the section it was written for. "
                "Move it up inside the previous section." % (ordinal, _clean(nxt["text"])[:70])
            )

    return {
        "insertions": insertions,
        "quick_recap_present": quick_recap_present,
        "faq_present": faq_present,
        "h2_count": h2_count,
        "cta_markers": cta_markers,
        "cta_added": cta_added,
        "warnings": warnings,
        "notes": notes,
    }
