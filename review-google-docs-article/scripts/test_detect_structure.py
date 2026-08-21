# -*- coding: utf-8 -*-
"""Unit tests for detect_structure. Run: python test_detect_structure.py"""

from detect_structure import detect, CTA_IMAGE_URL


def _t(text, level=0, is_list=False):
    return {"kind": "text", "text": text, "start": 0, "end": 0, "level": level, "is_list": is_list}


def _img():
    return {"kind": "image", "text": "", "start": 0, "end": 0, "level": 0}


def _blocks_with_indices(blocks):
    # Assign monotonic indices so insertion indices are meaningful/distinct.
    for n, b in enumerate(blocks):
        b["start"] = n * 100
        b["end"] = n * 100 + 50
    return blocks


def h2(text):
    return _t(text, level=2)


def li(text):
    """A hyperlinked reading-list item: bulleted, anchor text only (no http)."""
    return _t(text, level=0, is_list=True)


PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok   %s" % name)
    else:
        FAIL += 1
        print("  FAIL %s" % name)


def test_quick_recap_excluded_from_count():
    blocks = _blocks_with_indices([
        h2("Quick Recap:"),
        h2("Section A"),
        h2("Section B"),
        h2("Section C"),
        h2("Section D"),
        h2("Article FAQs"),
    ])
    plan = detect(blocks)
    # 6 H2 paragraphs, but Quick Recap excluded -> 5 counted.
    check("quick recap excluded -> h2_count == 5", plan["h2_count"] == 5)
    check("quick recap detected present", plan["quick_recap_present"] is True)
    check("faq detected present", plan["faq_present"] is True)


def test_cta_added_when_more_than_5_h2():
    blocks = _blocks_with_indices([
        h2("Quick Recap:"),
        h2("S1"), h2("S2"), h2("S3"), h2("S4"), h2("S5"),
        h2("Article FAQs"),      # 6 counted H2 (Quick Recap excluded) -> > 5
        _t("[cta]"),
    ])
    plan = detect(blocks, cta_campaign="my-keyword")
    check("cta planned when >5 counted H2", plan["cta_added"] == 1)
    ins = plan["insertions"][0]["text"]
    check("cta line uses fixed CTA url", CTA_IMAGE_URL in ins)
    check("cta line: Link is before Alt is", ins.index("Link is") < ins.index("Alt is"))
    check("cta line carries utm_campaign", "utm_campaign=my-keyword" in ins)
    check("cta line alt is TrueProfit CTA", "Alt is TrueProfit CTA" in ins)


def test_cta_warns_when_5_or_fewer():
    blocks = _blocks_with_indices([
        h2("Quick Recap:"),
        h2("S1"), h2("S2"), h2("S3"), h2("S4"),
        h2("Article FAQs"),      # 5 counted H2 -> not > 5
        _t("[cta]"),
    ])
    plan = detect(blocks, cta_campaign="my-keyword")
    check("no cta when exactly 5 counted H2", plan["cta_added"] == 0)
    check("short-article warning emitted", any("only 5" in w for w in plan["warnings"]))


def test_cta_idempotent():
    blocks = _blocks_with_indices([
        h2("S1"), h2("S2"), h2("S3"), h2("S4"), h2("S5"), h2("S6"),
        _t("Image (sentence note): %s, Link is x, Alt is TrueProfit CTA" % CTA_IMAGE_URL),
        _t("[cta]"),
    ])
    plan = detect(blocks, cta_campaign="k")
    check("cta not re-added when trigger already above marker", plan["cta_added"] == 0)


def test_fr_hyperlinked_above_3rd_h2_warns():
    # Reading-list items are hyperlinked (is_list, no http in text).
    blocks = _blocks_with_indices([
        h2("S1 (1st)"),
        h2("S2 (2nd)"),
        _t("Further Reading:"),
        li("Some Article Title"),
        li("Another Article Title"),
        h2("S3 (3rd)"),          # FR sits directly above the 3rd H2 -> warn
    ])
    plan = detect(blocks)
    check("hyperlinked FR above 3rd H2 warns", any("H2 #3" in w for w in plan["warnings"]))


def test_fr_above_6th_h2_no_warn():
    blocks = _blocks_with_indices([
        h2("S1"), h2("S2"), h2("S3"), h2("S4"), h2("S5"),
        _t("Further Reading:"),
        li("Title A"),
        h2("S6"),                # 6th H2 -> outside 2..5 -> no warn
    ])
    plan = detect(blocks)
    check("FR above 6th H2 does not warn", not any("Further Reading" in w for w in plan["warnings"]))


def test_fr_above_h3_no_warn():
    blocks = _blocks_with_indices([
        h2("S1"), h2("S2"),
        _t("Further Reading: One Link", is_list=False),
        _t("Step 2", level=3),   # next is an H3, not H2 -> no warn
    ])
    plan = detect(blocks)
    check("FR above H3 does not warn", not any("Further Reading" in w for w in plan["warnings"]))


def test_fr_with_body_paragraph_between_no_warn():
    blocks = _blocks_with_indices([
        h2("S1"), h2("S2"),
        _t("Further Reading:"),
        li("Title A"),
        li("Title B"),
        _t("This is a normal closing paragraph, not part of the list."),
        h2("S3"),                # body text between FR and H2 -> no warn
    ])
    plan = detect(blocks)
    check("FR with body paragraph before H2 does not warn",
          not any("Further Reading" in w for w in plan["warnings"]))


if __name__ == "__main__":
    for fn in [
        test_quick_recap_excluded_from_count,
        test_cta_added_when_more_than_5_h2,
        test_cta_warns_when_5_or_fewer,
        test_cta_idempotent,
        test_fr_hyperlinked_above_3rd_h2_warns,
        test_fr_above_6th_h2_no_warn,
        test_fr_above_h3_no_warn,
        test_fr_with_body_paragraph_between_no_warn,
    ]:
        print(fn.__name__)
        fn()
    print("\n%d passed, %d failed" % (PASS, FAIL))
    raise SystemExit(1 if FAIL else 0)
