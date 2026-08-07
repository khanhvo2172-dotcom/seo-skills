# -*- coding: utf-8 -*-
"""Unit tests for detect_triggers.detect() - no Google API needed.

Run:  python test_detect.py
"""
from detect_triggers import detect


def blk(kind, text, start, end, level=0, bullet=False):
    return {"kind": kind, "text": text, "start": start, "end": end,
            "level": level, "bullet": bullet}


def text_blocks(*texts):
    """
    Build sequential text blocks with synthetic but monotonic indices.

    Each item is either a string (body text, or "<IMG>" for an image) or a
    (level, text) tuple to give the paragraph a heading level - e.g. (2, "FAQ")
    for a Heading 2. Levels matter to the CTA and Further Reading checks. A
    leading "* " on a string marks the paragraph as a list item (bullet), which
    is how real reading-list entries appear.
    """
    out = []
    idx = 1
    for t in texts:
        level = 0
        if isinstance(t, tuple):
            level, t = t
        bullet = t.startswith("* ")
        if bullet:
            t = t[2:]
        kind = "image" if t == "<IMG>" else "text"
        body = "" if t == "<IMG>" else t
        end = idx + max(len(body), 1) + 1
        out.append(blk(kind, body, idx, end, level, bullet))
        idx = end
    return out


def h2s(n, start=1):
    """n Heading 2 paragraphs named A<start>..., each with a line of prose."""
    out = []
    for k in range(start, start + n):
        out.append((2, "A%d" % k))
        out.append("prose under A%d" % k)
    return out


def run(name, cond):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    return cond


# The finished Gutenberg block, byte for byte as the CMS expects it.
CTA_LINE = (
    '<!-- wp:image {"lightbox":{"enabled":false},"sizeSlug":"full",'
    '"linkDestination":"custom","align":"center"} -->\n'
    '<figure class="wp-block-image aligncenter size-full">'
    '<a href="https://apps.shopify.com/trueprofit?utm_source=trueprofit.io'
    '&amp;utm_medium=blog&amp;utm_campaign=how-to-track-dropship-expenses" rel="nofollow">'
    '<img src="https://be.trueprofit.io/uploads/app-listing-CTA-3.webp" '
    'alt="TrueProfit CTA"/></a></figure>\n'
    "<!-- /wp:image -->\n"
)


def main():
    ok = True

    # 1. Formula heading + "=" line -> Content Highlight before the formula line
    b = text_blocks("Formula", "Marginal Benefit (MB) = dTR / dQ")
    r = detect(b, "marginal-benefit-vs-marginal-cost")
    ins = r["insertions"]
    ok &= run("formula triggers one CH", len(ins) == 1 and ins[0]["text"] == "Content Highlight\n")
    ok &= run("formula CH inserted at formula-line start", ins and ins[0]["index"] == b[1]["start"])

    # 2. "Definition and Formula" + prose (no "=") -> NO trigger
    b = text_blocks("Definition and Formula", "In economics, marginal benefit is the maximum amount...")
    r = detect(b, "x")
    ok &= run("definition-and-formula does NOT trigger", len(r["insertions"]) == 0)

    # 3. "Formula" heading but next line has no "=" -> NO trigger
    b = text_blocks("Formula", "It depends on the marginal change in revenue.")
    r = detect(b, "x")
    ok &= run("formula without '=' does NOT trigger", len(r["insertions"]) == 0)

    # 3b. Inline formula lead-in ending in "formula:" + "=" line -> triggers
    b = text_blocks(
        "If you are consent, here are net profit margin formula:",
        "Net Profit Margin = (Net Profit / Net Sales) * 100%",
    )
    r = detect(b, "x")
    ok &= run("formula lead-in ('...formula:') triggers", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])

    # 3c. Mid-sentence "formula" (not at end of line) + "=" line -> triggers
    b = text_blocks(
        "The standard marginal cost formula is straightforward:",
        "Marginal Cost = Change in Total Cost (ΔTC) ÷ Change in Quantity (ΔQ)",
    )
    r = detect(b, "x")
    ok &= run("mid-sentence formula triggers CH", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])

    # 4. Pro tip callout -> Content Highlight before it
    b = text_blocks("Some intro.", "Pro tip: Use our profit margin tool")
    r = detect(b, "x")
    ok &= run("pro tip triggers CH", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])

    # 5. "Note:" callout -> trigger; "Note that..." prose -> NO trigger
    b = text_blocks("Note: margins vary by SKU.")
    r = detect(b, "x")
    ok &= run("note-colon triggers CH", len(r["insertions"]) == 1)
    b = text_blocks("Note that margins vary by SKU.")
    r = detect(b, "x")
    ok &= run("note-that prose does NOT trigger", len(r["insertions"]) == 0)

    # 5b. "Your Takeaway:" callout -> Content Highlight before it
    b = text_blocks("Some intro.", "Your Takeaway:")
    r = detect(b, "x")
    ok &= run("your-takeaway triggers CH", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])
    b = text_blocks("Your Takeaway: Lead with one hero product")
    r = detect(b, "x")
    ok &= run("your-takeaway with text triggers CH", len(r["insertions"]) == 1)
    # Already has CH -> skip
    b = text_blocks("Content Highlight", "Your Takeaway: do the thing")
    r = detect(b, "x")
    ok &= run("your-takeaway with existing CH is skipped", len(r["insertions"]) == 0)

    # 6. Images: two images -> two numbered triggers, in order, placed ABOVE
    b = text_blocks("Intro", "<IMG>", "Body text", "<IMG>", "Outro")
    r = detect(b, "marginal-benefit-vs-marginal-cost")
    ins = r["insertions"]
    ok &= run("two images -> two triggers", r["image_count"] == 2 and r["image_triggers_added"] == 2)
    img_ins = [x for x in ins if "Image (sentence note)" in x["text"]]
    ok &= run("image trigger placed ABOVE image", img_ins and img_ins[0]["index"] == b[1]["start"])
    urls = [x["text"] for x in ins if "Image (sentence note)" in x["text"]]
    ok &= run(
        "image #1 url is -1.webp",
        any("marginal-benefit-vs-marginal-cost-1.webp" in u for u in urls),
    )
    ok &= run(
        "image #2 url is -2.webp",
        any("marginal-benefit-vs-marginal-cost-2.webp" in u for u in urls),
    )
    ok &= run(
        "image trigger format exact (empty alt, no quotes)",
        any('Image (sentence note): https://be.trueprofit.io/uploads/marginal-benefit-vs-marginal-cost-1.webp, Alt is\n' == u for u in urls),
    )

    # 6b. Explicit image list (url + alt), mapped by image order
    b = text_blocks("Intro", "<IMG>", "Mid", "<IMG>", "End")
    image_map = [
        ("https://be.trueprofit.io/uploads/V1-2.webp", "Large preview"),
        ("https://be.trueprofit.io/uploads/mushroom-lamp.png", "Mushroom lamp"),
    ]
    r = detect(b, image_map=image_map)
    img_ins = [x["text"] for x in r["insertions"] if "Image (sentence note)" in x["text"]]
    ok &= run("list mode: two images mapped", len(img_ins) == 2)
    ok &= run(
        "list mode: image #1 url+alt exact (no quotes)",
        img_ins[0] == 'Image (sentence note): https://be.trueprofit.io/uploads/V1-2.webp, Alt is Large preview\n',
    )
    ok &= run(
        "list mode: image #2 url+alt exact (no quotes)",
        img_ins[1] == 'Image (sentence note): https://be.trueprofit.io/uploads/mushroom-lamp.png, Alt is Mushroom lamp\n',
    )
    ok &= run("list mode: placed above", r["insertions"][0]["index"] == b[1]["start"])

    # 6c. List shorter than image count -> extra image skipped + warning note
    b = text_blocks("<IMG>", "x", "<IMG>")
    r = detect(b, image_map=[("https://be.trueprofit.io/uploads/only-one.webp", "only one")])
    ok &= run("list mode: short list triggers only matched images", r["image_triggers_added"] == 1)
    ok &= run("list mode: count mismatch warns", any("WARNING" in n for n in r["notes"]))

    # 7. Image already triggered -> skipped, no duplicate (trigger below OR above)
    b = text_blocks("<IMG>", 'Image (sentence note): https://be.trueprofit.io/uploads/x-1.webp, Alt is ""')
    r = detect(b, "x")
    ok &= run("already-triggered image (below) skipped", r["image_triggers_added"] == 0)
    b = text_blocks('Image (sentence note): https://be.trueprofit.io/uploads/x-1.webp, Alt is ""', "<IMG>")
    r = detect(b, "x")
    ok &= run("already-triggered image (above) skipped", r["image_triggers_added"] == 0)

    # 8. Quick Recap / FAQ presence reporting
    b = text_blocks("Quick Recap", "- bullet one", "Some body", "FAQ", "Q?")
    r = detect(b, "x")
    ok &= run("quick recap detected", r["quick_recap_present"] is True)
    ok &= run("faq detected (line ending in FAQ)", r["faq_present"] is True)
    b = text_blocks("Intro", "Body", "Outro")
    r = detect(b, "x")
    ok &= run("quick recap absent", r["quick_recap_present"] is False)
    ok &= run("faq absent", r["faq_present"] is False)
    b = text_blocks("Frequently Asked Questions", "Q?")
    r = detect(b, "x")
    ok &= run("faq detected via 'Frequently Asked Questions'", r["faq_present"] is True)
    # Real-world heading carries the article name in front of "FAQs"
    b = text_blocks("Profitable Niches with Low Competition FAQs", "Q?")
    r = detect(b, "x")
    ok &= run("faq detected when heading ends in FAQs", r["faq_present"] is True)
    # ...but "FAQ" mid-sentence in prose should not count as a heading
    b = text_blocks("This section answers the FAQs that customers ask most.")
    r = detect(b, "x")
    ok &= run("faq NOT triggered mid-sentence", r["faq_present"] is False)

    # 9. Idempotency: Formula already has CH between heading and formula -> skip
    b = text_blocks("Formula", "Content Highlight", "MB = dTR / dQ")
    r = detect(b, "x")
    ok &= run("formula with existing CH is skipped", len(r["insertions"]) == 0)

    # 10. Pro tip already has CH above -> skip
    b = text_blocks("Content Highlight", "Pro tip: do the thing")
    r = detect(b, "x")
    ok &= run("pro tip with existing CH is skipped", len(r["insertions"]) == 0)

    # ---- 11. H2 counting -----------------------------------------------------
    b = text_blocks(*(h2s(5) + [(2, "Dropship Expenses FAQs"), "Q?"]))
    r = detect(b, "x")
    ok &= run("h2 count includes the FAQ heading", r["h2_count"] == 6)

    # ---- 12. CTA image: long article (>5 H2) -> trigger above the [cta] note --
    b = text_blocks(*(h2s(6) + ["[cta]"]))
    r = detect(b, cta_campaign="how-to-track-dropship-expenses")
    cta_ins = [x for x in r["insertions"] if "app-listing-CTA-3" in x["text"]]
    ok &= run("CTA added when article has 6 H2s", r["cta_added"] == 1 and len(cta_ins) == 1)
    ok &= run("CTA Gutenberg block exact", cta_ins and cta_ins[0]["text"] == CTA_LINE)
    ok &= run("CTA inserted above the [cta] marker", cta_ins and cta_ins[0]["index"] == b[-1]["start"])
    ok &= run("CTA marker counted", r["cta_markers"] == 1)
    ok &= run("no CTA warning on a long article", not any("CTA" in w for w in r["warnings"]))

    # 12b. Marker embedded in a sentence still counts
    b = text_blocks(*(h2s(6) + ["Put the [cta] banner here"]))
    r = detect(b, cta_campaign="slug")
    ok &= run("inline [cta] marker detected", r["cta_added"] == 1)

    # ---- 13. CTA image: short article (<=5 H2) -> warn, insert nothing --------
    b = text_blocks(*(h2s(5) + ["[cta]"]))
    r = detect(b, cta_campaign="how-to-track-dropship-expenses")
    ok &= run("CTA NOT added when only 5 H2s", r["cta_added"] == 0)
    ok &= run("short-article CTA warns", any("only 5 Heading 2" in w for w in r["warnings"]))
    ok &= run("short-article CTA inserts nothing", len(r["insertions"]) == 0)

    # 13b. No campaign slug -> warn rather than write a broken link
    b = text_blocks(*(h2s(6) + ["[cta]"]))
    r = detect(b)
    ok &= run("missing campaign warns", r["cta_added"] == 0 and any("utm_campaign" in w for w in r["warnings"]))

    # 13c. CTA already present (Gutenberg block) -> skipped, no duplicate
    b = text_blocks(*(h2s(6) + [
        '<!-- wp:image {"lightbox":{"enabled":false},"sizeSlug":"full","linkDestination":"custom","align":"center"} -->',
        '<figure class="wp-block-image aligncenter size-full"><a href="https://apps.shopify.com/trueprofit?utm_campaign=x" rel="nofollow"><img src="https://be.trueprofit.io/uploads/app-listing-CTA-3.webp" alt="TrueProfit CTA"/></a></figure>',
        "<!-- /wp:image -->",
        "[cta]",
    ]))
    r = detect(b, cta_campaign="slug")
    ok &= run("already-present CTA block skipped", r["cta_added"] == 0)

    # 13d. The older one-line CTA form is still recognised, so a re-run on a doc
    # processed by the previous version doesn't stack a second CTA on top of it.
    b = text_blocks(*(h2s(6) + [
        "Image (sentence note): https://be.trueprofit.io/uploads/app-listing-CTA-3.webp, Link is https://apps.shopify.com/trueprofit?utm_campaign=x, Alt is TrueProfit CTA",
        "[cta]",
    ]))
    r = detect(b, cta_campaign="slug")
    ok &= run("legacy one-line CTA skipped", r["cta_added"] == 0)

    # ---- 14. Further Reading placement --------------------------------------
    # Directly above the 2nd H2 -> warn
    b = text_blocks(
        (2, "A1"), "sentence 1", (3, "H3a"), "sentence 3",
        "Further Reading", "https://www.trueprofit.io/blog/one",
        (2, "A2"), "sentence 5",
    )
    r = detect(b, "x")
    ok &= run("FR directly above 2nd H2 warns", any("above H2 #2" in w for w in r["warnings"]))

    # Mid-section (more content after it) -> no warning
    b = text_blocks(
        (2, "A1"), (3, "H3a"), "sentence 3",
        "Further Reading", "https://www.trueprofit.io/blog/one",
        "sentence 4", (3, "H3b"), "sentence 5",
        (2, "A2"),
    )
    r = detect(b, "x")
    ok &= run("FR mid-section does NOT warn", not any("Further Reading" in w for w in r["warnings"]))

    # Directly above the 6th H2 -> outside the 2nd-5th window, no warning
    b = text_blocks(*(h2s(5) + [
        "Further Reading", "https://www.trueprofit.io/blog/one",
        (2, "A6"), "prose under A6",
    ]))
    r = detect(b, "x")
    ok &= run("FR above 6th H2 does NOT warn", not any("Further Reading" in w for w in r["warnings"]))

    # Directly above the 1st H2 -> no warning
    b = text_blocks("Intro", "Further Reading", "https://www.trueprofit.io/blog/one", (2, "A1"))
    r = detect(b, "x")
    ok &= run("FR above 1st H2 does NOT warn", not any("Further Reading" in w for w in r["warnings"]))

    # Multi-URL block: only the run of URLs belongs to it
    b = text_blocks(
        (2, "A1"), "sentence 1",
        "Further Reading", "https://a/1", "https://a/2", "https://a/3",
        (2, "A2"),
    )
    r = detect(b, "x")
    ok &= run("FR with 3 URLs above 2nd H2 warns", any("above H2 #2" in w for w in r["warnings"]))

    # Real-world shape: the entries are BULLETS whose URLs hide behind link text,
    # so there is no visible "http" to scan for.
    b = text_blocks(
        (2, "A1"), "sentence 1",
        "Further Reading:",
        "* Dropshipping for Dummies: Guide to Start Profitable in 2026",
        "* Best Dropshipping Suppliers for a Profitable Business in 2026",
        (2, "A2"), "prose under A2",
    )
    r = detect(b, "x")
    ok &= run("FR with bulleted link titles above 2nd H2 warns", any("above H2 #2" in w for w in r["warnings"]))

    # Same bulleted shape, but the next H2 is the 6th -> outside the window
    b = text_blocks(*(h2s(5) + [
        "Further Reading", "* Title one", "* Title two",
        (2, "A6"), "prose under A6",
    ]))
    r = detect(b, "x")
    ok &= run("bulleted FR above 6th H2 does NOT warn", not any("Further Reading" in w for w in r["warnings"]))

    # A single-line FR (label + inline link, no list under it) followed by an H3
    b = text_blocks(
        (2, "A1"), "sentence 1",
        "Further Reading: How to Start a Private Label Dropshipping Business in 2026?",
        (3, "H3b"), "sentence 2", (2, "A2"),
    )
    r = detect(b, "x")
    ok &= run("single-line FR above an H3 does NOT warn", not any("Further Reading" in w for w in r["warnings"]))

    # Prose (not a bullet) after the label ends the block - even if it has a link
    b = text_blocks(
        (2, "A1"), "Further Reading", "Ordinary prose with an inline link.", (2, "A2"),
    )
    r = detect(b, "x")
    ok &= run("prose after FR label ends the block (no warn)", not any("Further Reading" in w for w in r["warnings"]))

    print()
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
