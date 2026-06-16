# -*- coding: utf-8 -*-
"""Unit tests for detect_triggers.detect() - no Google API needed.

Run:  python test_detect.py
"""
from detect_triggers import detect


def blk(kind, text, start, end):
    return {"kind": kind, "text": text, "start": start, "end": end}


def text_blocks(*texts):
    """Build sequential text blocks with synthetic but monotonic indices."""
    out = []
    idx = 1
    for t in texts:
        kind = "image" if t == "<IMG>" else "text"
        body = "" if t == "<IMG>" else t
        end = idx + max(len(body), 1) + 1
        out.append(blk(kind, body, idx, end))
        idx = end
    return out


def run(name, cond):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    return cond


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

    print()
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
