# -*- coding: utf-8 -*-
"""
Detection engine for the TrueProfit blog-trigger skill.

This module is deliberately FREE of any Google API dependency so it can be unit
tested on synthetic input. It takes a flat, ordered list of "blocks" (one per
paragraph of the doc's first tab) and decides which CMS trigger lines to insert.

A block is a dict:
    { "kind": "text" | "image", "text": str, "start": int, "end": int }
where `start`/`end` are the Google Docs character indices of that paragraph
(used by the caller to build insertText requests). For pure-logic tests the
indices can be anything monotonic.

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

# An Image trigger that already exists in the doc (so we don't duplicate it).
RE_EXISTING_IMAGE_TRIGGER = re.compile(r"^\s*Image\b[^:]*:\s*https?://", re.I)

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


def detect(blocks, base_slug=None, image_map=None):
    """
    Analyse the first tab's blocks and return a plan.

    Image triggers can be generated two ways:
      - base_slug (str): auto-number by image order with an empty alt, i.e.
        https://be.trueprofit.io/uploads/<base_slug>-<n>.webp.
      - image_map (list of (url, alt)): an explicit, ordered list - image #1 gets
        entry 1, image #2 entry 2, and so on, each with its own URL and alt text.
        Takes precedence over base_slug when provided.

    Returns dict:
      {
        "insertions": [ {index, text, reason}, ... ],
        "quick_recap_present": bool,
        "faq_present": bool,
        "image_count": int,
        "image_triggers_added": int,
        "notes": [str, ...],
      }
    """
    insertions = []
    notes = []

    quick_recap_present = any(
        b["kind"] == "text" and RE_QUICK_RECAP.search(_clean(b["text"])) for b in blocks
    )
    faq_present = any(
        b["kind"] == "text" and RE_FAQ.search(_clean(b["text"])) for b in blocks
    )

    image_count = 0
    image_triggers_added = 0

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

        # ---- Content Highlight: Pro tip / Note callouts ----
        if RE_PRO_TIP.match(text) or RE_NOTE.match(text):
            prev = _prev_nonempty(blocks, i)
            if prev is not None and RE_CONTENT_HIGHLIGHT.match(_clean(prev["text"])):
                notes.append("Callout already has a Content Highlight - skipped.")
            else:
                label = "Pro tip" if RE_PRO_TIP.match(text) else "Note"
                insertions.append(
                    {
                        "index": b["start"],
                        "text": CONTENT_HIGHLIGHT_LABEL + "\n",
                        "reason": "%s callout -> Content Highlight" % label,
                    }
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
        "notes": notes,
    }


def _index_of(blocks, block):
    for idx, b in enumerate(blocks):
        if b is block:
            return idx
    return -1
