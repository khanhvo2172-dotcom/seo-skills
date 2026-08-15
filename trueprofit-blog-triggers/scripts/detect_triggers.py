# -*- coding: utf-8 -*-
"""
Detection engine for the TrueProfit blog-trigger skill.

This module is deliberately FREE of any Google API dependency so it can be unit
tested on synthetic input. It takes a flat, ordered list of "blocks" (one per
paragraph of the doc's first tab) and decides which CMS trigger lines to insert.

A block is a dict:
    { "kind": "text" | "image", "text": str, "start": int, "end": int,
      "level": int }
where `start`/`end` are the Google Docs character indices of that paragraph
(used by the caller to build insertText requests) and `level` is the heading
level (2 for HEADING_2, 0 for body text). For pure-logic tests the indices can
be anything monotonic and `level` may be omitted.

The planned insertions are returned as a list of:
    { "index": int, "text": str, "reason": str }
`index` is the Docs character index at which to insert `text`. The caller is
responsible for sorting these descending before applying them (so earlier
insertions don't shift later indices).
"""

import re

# --- Trigger label strings, kept identical to what the n8n parser recognises ---
CONTENT_HIGHLIGHT_LABEL = "Content Highlight"
IMAGE_TRIGGER_TEMPLATE = "Image (sentence note): {url}, Alt is {alt}"
IMAGE_URL_TEMPLATE = "https://be.trueprofit.io/uploads/{slug}-{n}.webp"

# --- CTA image ---------------------------------------------------------------
# Authors mark the intended CTA slot with a "[cta]" note. The image itself is a
# fixed shared asset, and it must carry a link to the Shopify app listing tagged
# with the article's main keyword.
#
# The doc carries a TRIGGER LINE, not markup: n8n turns it into the Gutenberg
# <!-- wp:image --> block on the CMS side. Keep the doc plain.
#
# NOTE on field order: "Link is" comes BEFORE "Alt is" on purpose. Alt parsing
# runs to the end of the line, so putting the link last would make the alt read
# "TrueProfit CTA, Link is https://..." instead of "TrueProfit CTA".
CTA_IMAGE_URL = "https://be.trueprofit.io/uploads/app-listing-CTA.webp"
CTA_IMAGE_ALT = "TrueProfit CTA"
CTA_LINK_TEMPLATE = (
    "https://apps.shopify.com/trueprofit"
    "?utm_source=trueprofit.io&utm_medium=blog&utm_campaign={campaign}"
)
CTA_TRIGGER_TEMPLATE = "Image (sentence note): {url}, Link is {link}, Alt is {alt}"
# A CTA image only belongs in a long-enough article. "Long enough" is measured in
# Heading 2 sections, FAQ included: MORE than this many, or no CTA.
CTA_MIN_H2 = 5

# The author's CTA placeholder, e.g. a line reading "[cta]".
RE_CTA_MARKER = re.compile(r"\[\s*cta\s*\]", re.I)

# --- Further Reading --------------------------------------------------------
# A "Further Reading" line followed by a list of URLs. It should live INSIDE a
# section, not immediately before the next H2 - a block that sits directly above
# the 2nd-5th H2 reads as belonging to the heading below it instead of the
# section it was written for.
RE_FURTHER_READING = re.compile(r"^\s*further\s+reading\b", re.I)
FR_WARN_H2_ORDINALS = (2, 3, 4, 5)

# --- Recognisers -------------------------------------------------------------
# Quick Recap / FAQ: presence-only. We match what the n8n Transform Content node
# treats as a trigger, so "present" means "the publishing workflow will pick it
# up", not merely "the words appear somewhere".
RE_QUICK_RECAP = re.compile(r"^\s*Quick\s+Recap\b", re.I)
# A line ENDING in FAQ/FAQs (e.g. "... Low Competition FAQs"), matching the n8n
# parser's /FAQs?\s*$/i exactly - the heading often carries the article name in
# front of "FAQs", so anchoring at the start would miss real FAQ sections.
RE_FAQ = re.compile(r"(?:FAQs?\s*:?\s*$|frequently\s+asked\s+questions)", re.I)

# A line that CONTAINS the word "formula" anywhere - catches a bare "Formula"
# heading, inline lead-ins like "...net profit margin formula:", AND mid-sentence
# phrases like "The standard marginal cost formula is straightforward:".
# The real discriminator is the "=" on the following line (checked below), so
# prose that mentions "formula" but isn't followed by an equation is left alone.
RE_FORMULA_HEADING = re.compile(r"\bformula\b", re.I)

# Callout openers that should become a Content Highlight. "Pro tip" is a clear
# callout phrase so a colon is optional; "Note" is a common prose opener
# ("Note that...") so we require a colon to avoid false positives.
RE_PRO_TIP = re.compile(r"^\s*pro\s*tip\b", re.I)
RE_NOTE = re.compile(r"^\s*note\s*:", re.I)
RE_YOUR_TAKEAWAY = re.compile(r"^\s*your\s+takeaway\s*:", re.I)

# An Image trigger that already exists in the doc (so we don't duplicate it).
RE_EXISTING_IMAGE_TRIGGER = re.compile(r"^\s*Image\b[^:]*:\s*https?://", re.I)

# Raw Gutenberg image markup. The doc should never contain this - the CMS builds
# it from the trigger line - but one run of this skill briefly wrote it, so the
# pattern stays so --reset can clean those docs up.
RE_CTA_BLOCK = re.compile(
    r"(^\s*<!--\s*/?wp:image\b|^\s*<figure\s+class=\"wp-block-image)", re.I
)

# Already-present Content Highlight label (dedup guard).
RE_CONTENT_HIGHLIGHT = re.compile(r"^\s*Content\s+Highlight\b", re.I)


def _clean(text):
    # Normalise non-breaking spaces (Google Docs uses U+00A0 liberally) and trim.
    return (text or "").replace(chr(0x00A0), " ").strip()


def _next_text_block(blocks, i):
    """Return the next non-empty text block after index i, or None."""
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        if b["kind"] == "text" and _clean(b["text"]):
            return b
        j += 1
    return None


def _prev_nonempty(blocks, i):
    """Return the previous non-empty block before index i, or None."""
    j = i - 1
    while j >= 0:
        b = blocks[j]
        if _clean(b["text"]):
            return b
        j -= 1
    return None


def _next_nonempty_at(blocks, i):
    """Return (position, block) of the next block with content after i, or (-1, None)."""
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        if b["kind"] == "image" or _clean(b["text"]):
            return j, b
        j += 1
    return -1, None


def _fr_block_end(blocks, i):
    """
    Return the position of the LAST block belonging to the Further Reading block
    that starts at position i - i.e. the trailing run of reading-list entries
    under the "Further Reading" label. Blank lines inside the run are tolerated.

    An entry is a LIST ITEM (the usual shape: hyperlinked article titles as
    bullets) or a line whose visible text is a bare URL. Bullets matter because
    these lists rarely show the URL as text - the link hides behind the title -
    so scanning for "http" alone finds nothing and the block looks one line long.

    A link-bearing line that is NOT a bullet does not count: body prose in these
    articles is full of inline internal links, and absorbing it would run the
    block past the end of the reading list.
    """
    last = i
    j = i + 1
    while j < len(blocks):
        b = blocks[j]
        t = _clean(b["text"])
        if b["kind"] == "text" and not t:
            j += 1
            continue
        is_entry = b["kind"] == "text" and b.get("level", 0) == 0 and (
            b.get("bullet") or t.lower().startswith("http")
        )
        if is_entry:
            last = j
            j += 1
            continue
        break
    return last


def _h2_positions(blocks):
    """Positions of the Heading 2 paragraphs, in document order (FAQ included)."""
    return [
        i
        for i, b in enumerate(blocks)
        if b.get("level") == 2 and _clean(b["text"])
    ]


def detect(blocks, base_slug=None, image_map=None, cta_campaign=None):
    """
    Analyse the first tab's blocks and return a plan.

    Image triggers can be generated two ways:
      - base_slug (str): auto-number by image order with an empty alt, i.e.
        https://be.trueprofit.io/uploads/<base_slug>-<n>.webp.
      - image_map (list of (url, alt)): an explicit, ordered list - image #1 gets
        entry 1, image #2 entry 2, and so on, each with its own URL and alt text.
        Takes precedence over base_slug when provided.

    cta_campaign (str) is the utm_campaign value (the article's main keyword
    slug) used when a "[cta]" marker qualifies for a CTA image trigger.

    Returns dict:
      {
        "insertions": [ {index, text, reason}, ... ],
        "quick_recap_present": bool,
        "faq_present": bool,
        "image_count": int,
        "image_triggers_added": int,
        "h2_count": int,
        "cta_markers": int,
        "cta_added": int,
        "warnings": [str, ...],
        "notes": [str, ...],
      }
    """
    insertions = []
    notes = []
    warnings = []

    quick_recap_present = any(
        b["kind"] == "text" and RE_QUICK_RECAP.search(_clean(b["text"])) for b in blocks
    )
    faq_present = any(
        b["kind"] == "text" and RE_FAQ.search(_clean(b["text"])) for b in blocks
    )

    h2_pos = _h2_positions(blocks)
    h2_count = len(h2_pos)

    image_count = 0
    image_triggers_added = 0
    cta_markers = 0
    cta_added = 0

    for i, b in enumerate(blocks):
        text = _clean(b["text"])

        # ---- Images: number by document order, skip ones already triggered ----
        if b["kind"] == "image":
            image_count += 1
            # An image counts as "already triggered" if an Image: line sits on
            # EITHER side of it. We now place the trigger ABOVE the image, but a
            # doc processed by an older version may have it below - checking both
            # sides means a re-run never produces a duplicate.
            prevb = _prev_nonempty(blocks, i)
            nxtb = _next_text_block(blocks, i)
            already = (
                (prevb is not None and RE_EXISTING_IMAGE_TRIGGER.search(_clean(prevb["text"])))
                or (nxtb is not None and RE_EXISTING_IMAGE_TRIGGER.search(_clean(nxtb["text"])))
            )
            if already:
                notes.append(
                    "Image #%d already has a trigger line - skipped." % image_count
                )
                continue
            if image_map is not None:
                # Explicit list: image N uses the Nth entry's url + alt.
                if image_count - 1 < len(image_map):
                    url, alt = image_map[image_count - 1]
                else:
                    notes.append(
                        "Image #%d has no entry in the image list - skipped." % image_count
                    )
                    continue
            else:
                url = IMAGE_URL_TEMPLATE.format(slug=base_slug, n=image_count)
                alt = ""
            # rstrip drops the trailing space when alt is empty (base-slug mode),
            # so the line reads "...Alt is" rather than "...Alt is ".
            line = IMAGE_TRIGGER_TEMPLATE.format(url=url, alt=alt).rstrip()
            # Insert as a new paragraph immediately ABOVE the image (at the image
            # paragraph's start index).
            reason = "Image #%d trigger (%s)" % (image_count, url)
            if alt:
                reason += ' | alt: "%s"' % alt
            insertions.append(
                {
                    "index": b["start"],
                    "text": line + "\n",
                    "reason": reason,
                }
            )
            image_triggers_added += 1
            continue

        if b["kind"] != "text" or not text:
            continue

        # ---- CTA image: "[cta]" marker -> fixed image + linked Shopify listing --
        if RE_CTA_MARKER.search(text):
            cta_markers += 1
            prevb = _prev_nonempty(blocks, i)
            prevt = _clean(prevb["text"]) if prevb is not None else ""
            if RE_CTA_BLOCK.search(prevt) or RE_EXISTING_IMAGE_TRIGGER.search(prevt):
                notes.append("CTA marker already has an image trigger above it - skipped.")
            elif h2_count <= CTA_MIN_H2:
                warnings.append(
                    "CTA image NOT added: the article has only %d Heading 2 section(s) "
                    "(FAQ counted). A CTA image needs more than %d - decide manually "
                    "whether this article should carry one." % (h2_count, CTA_MIN_H2)
                )
            elif not cta_campaign:
                warnings.append(
                    "CTA image NOT added: no utm_campaign value supplied. Re-run with "
                    "--cta-campaign <main-keyword-slug>."
                )
            else:
                link = CTA_LINK_TEMPLATE.format(campaign=cta_campaign)
                line = CTA_TRIGGER_TEMPLATE.format(
                    url=CTA_IMAGE_URL, link=link, alt=CTA_IMAGE_ALT
                )
                insertions.append(
                    {
                        "index": b["start"],
                        "text": line + "\n",
                        "reason": "CTA image trigger (utm_campaign: %s)" % cta_campaign,
                    }
                )
                cta_added += 1
            continue

        # ---- Content Highlight: Formula line followed by a line with "=" ----
        if RE_FORMULA_HEADING.search(text):
            nxt = _next_text_block(blocks, i)
            if nxt and "=" in nxt["text"]:
                before_formula = _prev_nonempty(blocks, _index_of(blocks, nxt))
                already_ch = before_formula is not None and RE_CONTENT_HIGHLIGHT.match(
                    _clean(before_formula["text"])
                )
                if already_ch:
                    notes.append("Formula already has a Content Highlight - skipped.")
                else:
                    insertions.append(
                        {
                            "index": nxt["start"],
                            "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                            "reason": "Formula -> Content Highlight",
                        }
                    )
            continue

        # ---- Content Highlight: Pro tip / Note / Your Takeaway callouts ----
        if RE_PRO_TIP.match(text) or RE_NOTE.match(text) or RE_YOUR_TAKEAWAY.match(text):
            prev = _prev_nonempty(blocks, i)
            if prev is not None and RE_CONTENT_HIGHLIGHT.match(_clean(prev["text"])):
                notes.append("Callout already has a Content Highlight - skipped.")
            else:
                label = "Pro tip" if RE_PRO_TIP.match(text) else "Your Takeaway" if RE_YOUR_TAKEAWAY.match(text) else "Note"
                insertions.append(
                    {
                        "index": b["start"],
                        "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                        "reason": "%s callout -> Content Highlight" % label,
                    }
                )

    # ---- Further Reading placement (warn only, never edited) ----------------
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

    # Loud warning if an explicit image list doesn't line up with the images.
    if image_map is not None and len(image_map) != image_count:
        notes.append(
            "WARNING: image list has %d entr%s but the doc has %d image(s) - "
            "they must be in the same order. Review the mapping before applying."
            % (len(image_map), "y" if len(image_map) == 1 else "ies", image_count)
        )

    return {
        "insertions": insertions,
        "quick_recap_present": quick_recap_present,
        "faq_present": faq_present,
        "image_count": image_count,
        "image_triggers_added": image_triggers_added,
        "h2_count": h2_count,
        "cta_markers": cta_markers,
        "cta_added": cta_added,
        "warnings": warnings,
        "notes": notes,
    }


def _index_of(blocks, block):
    for idx, b in enumerate(blocks):
        if b is block:
            return idx
    return -1
