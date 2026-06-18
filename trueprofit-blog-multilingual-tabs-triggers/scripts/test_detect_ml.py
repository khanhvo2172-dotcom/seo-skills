# -*- coding: utf-8 -*-
"""Unit tests for detect_ml.detect() - no Google API needed.

Run:  python test_detect_ml.py
"""
from detect_ml import detect, parse_existing_triggers, plan_repairs, plan_ch
from place_ml import (english_image_anchors, english_ch_anchors, plan_placements,
                      plan_ch_placements, heading_score, align_headings, headings,
                      choose_anchor, body_end_index, section_bodies)


def seq(*items):
    """Build blocks from (level, text) tuples with running indices (level 0 = body)."""
    out = []
    idx = 1
    for level, text in items:
        end = idx + max(len(text), 1) + 1
        out.append({"kind": "text", "text": text, "start": idx, "end": end, "level": level})
        idx = end
    return out


def blk(kind, text, start, end):
    return {"kind": kind, "text": text, "start": start, "end": end}


def text_blocks(*texts):
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
    print("[%s] %s" % ("PASS" if cond else "FAIL", name))
    return cond


def main():
    ok = True

    # ---- Spanish ----------------------------------------------------------
    # Formula: Spanish "Fórmula" heading + "=" line -> Content Highlight above formula
    b = text_blocks("Fórmula", "Margen de beneficio neto = (Beneficio / Ventas) * 100%")
    r = detect(b, "es")
    ok &= run("es: formula triggers one CH", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])

    # Inline lead-in ending in "fórmula:" + "=" line
    b = text_blocks("Aquí está la fórmula del margen:", "Margen = Beneficio / Ventas")
    r = detect(b, "es")
    ok &= run("es: inline 'fórmula:' lead-in triggers", len(r["insertions"]) == 1)

    # Prose mentioning fórmula but no "=" on next line -> NO trigger
    b = text_blocks("Definición y fórmula", "En economía, el beneficio marginal es...")
    r = detect(b, "es")
    ok &= run("es: fórmula prose (no =) does NOT trigger", len(r["insertions"]) == 0)

    # Callout: "Consejo profesional:" -> Content Highlight above
    b = text_blocks("Texto.", "Consejo profesional: usa nuestra herramienta")
    r = detect(b, "es")
    ok &= run("es: 'Consejo profesional:' triggers CH", len(r["insertions"]) == 1 and r["insertions"][0]["index"] == b[1]["start"])

    # Callout colon required: "Consejo de un amigo" (no colon) -> NO trigger
    b = text_blocks("Un consejo de un amigo es escuchar.")
    r = detect(b, "es")
    ok &= run("es: 'consejo' mid-sentence (no colon) does NOT trigger", len(r["insertions"]) == 0)

    # Quick Recap / FAQ presence (Spanish)
    b = text_blocks("Resumen rápido", "- punto uno", "Preguntas frecuentes", "¿Q?")
    r = detect(b, "es")
    ok &= run("es: quick recap detected", r["quick_recap_present"] is True)
    ok &= run("es: faq detected (Preguntas frecuentes)", r["faq_present"] is True)

    # ---- German -----------------------------------------------------------
    b = text_blocks("Formel", "Nettogewinnmarge = (Gewinn / Umsatz) * 100 %")
    r = detect(b, "de")
    ok &= run("de: formula triggers one CH", len(r["insertions"]) == 1)

    b = text_blocks("Etwas Text.", "Profi-Tipp: Nutze unser Tool")
    r = detect(b, "de")
    ok &= run("de: 'Profi-Tipp:' triggers CH", len(r["insertions"]) == 1)

    b = text_blocks("Hinweis: Margen variieren je SKU.")
    r = detect(b, "de")
    ok &= run("de: 'Hinweis:' triggers CH", len(r["insertions"]) == 1)

    b = text_blocks("Kurze Zusammenfassung", "Häufig gestellte Fragen")
    r = detect(b, "de")
    ok &= run("de: quick recap detected", r["quick_recap_present"] is True)
    ok &= run("de: faq detected", r["faq_present"] is True)

    # ---- French -----------------------------------------------------------
    b = text_blocks("Formule", "Marge bénéficiaire nette = (Bénéfice / Ventes) * 100 %")
    r = detect(b, "fr")
    ok &= run("fr: formula triggers one CH", len(r["insertions"]) == 1)

    # French space-before-colon callout
    b = text_blocks("Du texte.", "Astuce de pro : utilisez notre outil")
    r = detect(b, "fr")
    ok &= run("fr: 'Astuce de pro :' (space-colon) triggers CH", len(r["insertions"]) == 1)

    b = text_blocks("Récapitulatif rapide", "Questions fréquentes")
    r = detect(b, "fr")
    ok &= run("fr: quick recap detected", r["quick_recap_present"] is True)
    ok &= run("fr: faq detected", r["faq_present"] is True)

    # ---- Images (language-agnostic, mapped from the shared list) -----------
    b = text_blocks("Intro", "<IMG>", "Cuerpo", "<IMG>", "Cierre")
    image_map = [
        ("https://be.trueprofit.io/uploads/niche-1.webp", "Vista previa grande"),
        ("https://be.trueprofit.io/uploads/niche-2.webp", "Lámpara hongo"),
    ]
    r = detect(b, "es", image_map=image_map)
    img_ins = [x["text"] for x in r["insertions"] if "Image (sentence note)" in x["text"]]
    ok &= run("es: two images mapped", len(img_ins) == 2)
    ok &= run("es: image #1 placed ABOVE image", r["insertions"][0]["index"] == b[1]["start"])
    ok &= run(
        "es: image #1 url+translated alt exact",
        img_ins[0] == "Image (sentence note): https://be.trueprofit.io/uploads/niche-1.webp, Alt is Vista previa grande\n",
    )

    # Image already triggered (above OR below) -> skipped
    b = text_blocks("Image (sentence note): https://be.trueprofit.io/uploads/x-1.webp, Alt is foo", "<IMG>")
    r = detect(b, "es", image_map=[("https://be.trueprofit.io/uploads/x-1.webp", "foo")])
    ok &= run("es: already-triggered image (above) skipped", r["image_triggers_added"] == 0)

    # Count mismatch warns
    b = text_blocks("<IMG>", "x", "<IMG>")
    r = detect(b, "de", image_map=[("https://be.trueprofit.io/uploads/only-one.webp", "nur eins")])
    ok &= run("de: short list adds only matched image", r["image_triggers_added"] == 1)
    ok &= run("de: count mismatch warns", any("WARNING" in n for n in r["notes"]))

    # ---- Idempotency: existing Content Highlight (English label) respected --
    b = text_blocks("Fórmula", "Content Highlight", "Margen = B / V")
    r = detect(b, "es")
    ok &= run("es: formula with existing CH is skipped", len(r["insertions"]) == 0)

    b = text_blocks("Content Highlight", "Consejo profesional: haz esto")
    r = detect(b, "es")
    ok &= run("es: callout with existing CH is skipped", len(r["insertions"]) == 0)

    # ---- Repair / realign of carried-over triggers -------------------------
    # Stale two-line image trigger (label, then URL+alt on next line) + a
    # "Content Highlight:" line, exactly like a translated tab.
    b = text_blocks(
        "Algun texto.",
        "Image (sentence note):",
        "https://be.trueprofit.io/uploads/old-1.webp (alt is “test alt”)",
        "Mas texto.",
        "Content Highlight:",
        "Consejo profesional: haz esto",
    )
    units = parse_existing_triggers(b)
    ok &= run("repair: finds 1 image + 1 ch unit", len(units) == 2 and units[0]["kind"] == "image" and units[1]["kind"] == "ch")
    ok &= run("repair: image unit absorbs the URL line",
              units[0]["start"] == b[1]["start"] and units[0]["end"] == b[2]["end"])

    rep = plan_repairs(b, ["https://be.trueprofit.io/uploads/real-1.webp"], ["Vista previa"], ["Large preview"])
    img_ops = [o for o in rep["ops"] if "Image" in o["text"]]
    ok &= run("repair: one image op", len(img_ops) == 1)
    ok &= run(
        "repair: image op uses English URL + translated alt, one line",
        img_ops[0]["text"] == "Image (sentence note): https://be.trueprofit.io/uploads/real-1.webp, Alt is Vista previa\n",
    )
    ok &= run("repair: image op replaces both old lines (range start..end)",
              img_ops[0]["start"] == b[1]["start"] and img_ops[0]["end"] == b[2]["end"])
    ok &= run("repair: plan_repairs no longer emits CH ops",
              all("Highlight" not in o.get("text", "") for o in rep["ops"]))
    ok &= run("repair: image_repaired count", rep["image_repaired"] == 1)

    # ---- Content Highlight (Option B): keep backed, delete orphan -----------
    # Backed: a "Content Highlight:" whose next line is a localized callout -> keep+normalize.
    chrep = plan_ch(b, "es")  # b still has CH: above "Consejo profesional: haz esto"
    norm = [o for o in chrep["ops"] if o.get("text", "").strip() == "Content Highlight"]
    ok &= run("ch: backed 'Content Highlight:' normalized to no-colon",
              chrep["kept"] == 1 and chrep["deleted"] == 0 and len(norm) == 1)

    # Orphan: a "Content Highlight" above plain prose -> delete (no text op).
    bo = text_blocks("Content Highlight", "Reddit y Quora son minas de oro para validar.")
    chrep = plan_ch(bo, "es")
    ok &= run("ch: orphan 'Content Highlight' deleted (range, no text)",
              chrep["deleted"] == 1 and chrep["kept"] == 0
              and len(chrep["ops"]) == 1 and "text" not in chrep["ops"][0])

    # Backed by a formula (formula word line then "=" line) -> keep, already canonical.
    bf = text_blocks("Content Highlight", "Formula", "Margen = Beneficio / Ventas")
    chrep = plan_ch(bf, "es")
    ok &= run("ch: formula-backed 'Content Highlight' kept, no op (canonical)",
              chrep["kept"] == 1 and chrep["deleted"] == 0 and len(chrep["ops"]) == 0)

    # Already-canonical single-line image -> no-op (idempotent)
    b = text_blocks(
        "Image (sentence note): https://be.trueprofit.io/uploads/real-1.webp, Alt is Vista previa",
        "<IMG-not-an-object, just text>",
    )
    rep = plan_repairs(b, ["https://be.trueprofit.io/uploads/real-1.webp"], ["Vista previa"], ["Large preview"])
    ok &= run("repair: canonical single-line image is a no-op", len(rep["ops"]) == 0)

    # Fewer image lines than English -> warns
    b = text_blocks("Image (sentence note): https://x/old-1.webp, Alt is a")
    rep = plan_repairs(b, ["https://x/real-1.webp", "https://x/real-2.webp"], [], ["a", "b"])
    ok &= run("repair: count mismatch warns", any("WARNING" in n for n in rep["notes"]))

    # ---- Cognate matching (heading + paragraph) ----------------------------
    ok &= run("cognate: competition~competencia", heading_score("Low Competition", "baja competencia") >= 1)
    ok &= run("cognate: organic~organica", heading_score("Organic Fruit", "fruta organica") >= 1)
    ok &= run("cognate: lamps~lamparas", heading_score("Mushroom Lamps", "Lamparas de setas") >= 1)
    ok &= run("cognate: no false match socks/calcetines", heading_score("Fuzzy Socks", "Calcetines esponjosos") == 0)

    # choose_anchor self-corrects a +1 drift using content overlap.
    bodies = seq((0, "Texto extra que no estaba."),
                 (0, "Las lamparas de hongo son tendencia mundial."),
                 (0, "Se venden muy bien."))
    idx, score, moved = choose_anchor("Mushroom lamps are trending worldwide.", bodies, 0)
    ok &= run("choose_anchor: corrects +1 drift to the lamparas paragraph", idx == 1 and moved is True)
    idx, score, moved = choose_anchor("Totally unrelated text.", bodies, 0)
    ok &= run("choose_anchor: no signal -> stays at expected ordinal", idx == 0 and moved is False)

    # ---- Paragraph-anchored placement (out-of-sync translated tab) ----------
    en = seq(
        (2, "Intro Heading"),
        (0, "Intro paragraph one."),
        (0, "Intro paragraph two with the secret."),
        (0, "Image (sentence note): https://x/intro-1.webp, Alt is Intro"),
        (3, "Mushroom Lamps Section"),
        (0, "Mushroom lamps are trending worldwide."),
        (0, "Image (sentence note): https://x/mushroom-2.webp, Alt is Mushroom lamp"),
        (0, "They sell very well online."),
        (0, "Content Highlight"),
        (0, "Your Takeaway: focus on one hero product."),
        (3, "Closing CTA Section"),
        (0, "Track your store performance closely."),
        (0, "Image (sentence note): https://x/cta-3.webp, Alt is CTA"),
    )
    anchors = english_image_anchors(en)
    ok &= run("anchors: 3 images found", len(anchors) == 3)
    ok &= run("anchors: img1 follows 2 body paragraphs",
              anchors[0]["body_ordinal"] == 2 and "secret" in anchors[0]["anchor_text"])
    ok &= run("anchors: img2 follows 1 body paragraph", anchors[1]["body_ordinal"] == 1)
    chs = english_ch_anchors(en)
    ok &= run("ch anchors: 1 found, labels the takeaway paragraph",
              len(chs) == 1 and chs[0]["before_ordinal"] == 3 and "Takeaway" in chs[0]["anchor_text"])

    # Translated tab: faithful but with an EXTRA paragraph in the mushroom section
    # (drift) and a closing region (Final Thoughts + FAQ) but NO CTA heading.
    tr = seq(
        (2, "Encabezado de introduccion"),
        (0, "Parrafo uno de introduccion."),
        (0, "Parrafo dos con el secreto."),
        (3, "Seccion de lamparas de hongo"),
        (0, "Texto extra que no estaba en el original."),
        (0, "Las lamparas de hongo son tendencia mundial."),
        (0, "Se venden muy bien en linea."),
        (0, "Tu conclusion: enfocate en un producto estrella."),
        (2, "Reflexiones finales"),
        (0, "En resumen, construye una marca."),
        (2, "Preguntas frecuentes"),
        (0, "Una pregunta."),
    )
    T = {b["text"]: b for b in tr}
    tr_alts = ["Intro es", "Lampara es", "CTA es"]
    place = plan_placements(tr, anchors, tr_alts, [a["alt"] for a in anchors], "es")
    ok &= run("place: 3 images placed", place["placed"] == 3)

    def op_for(slug):
        return [o for o in place["ops"] if slug in o["text"]][0]

    # img1: after the 2nd intro paragraph (the one mentioning the secret)
    ok &= run("place: img1 after 'Parrafo dos con el secreto.'",
              op_for("intro-1")["start"] == T["Parrafo dos con el secreto."]["end"])
    # img2: drift-corrected past the EXTRA paragraph onto the lamparas paragraph
    ok &= run("place: img2 drift-corrected onto the lamparas paragraph",
              op_for("mushroom-2")["start"] == T["Las lamparas de hongo son tendencia mundial."]["end"])
    ok &= run("place: img2 NOT placed after the extra paragraph",
              op_for("mushroom-2")["start"] != T["Texto extra que no estaba en el original."]["end"])
    # img3 (CTA): its English heading has no keyword match; the ordinal step lands
    # in the closing region, so it is redirected to the end of the body.
    ok &= run("place: CTA redirected to end of body (before 'Reflexiones finales')",
              op_for("cta-3")["start"] == T["Reflexiones finales"]["start"])
    ok &= run("place: CTA flagged as fallback in review",
              [r for r in place["review"] if r["n"] == 3][0]["how"] == "fallback")
    ok &= run("place: a structure warning was raised for the CTA", len(place["warnings"]) >= 1)
    ok &= run("place: op text canonical with translated alt",
              op_for("intro-1")["text"] == "Image (sentence note): https://x/intro-1.webp, Alt is Intro es\n")

    # Content Highlight mirrored above the translated takeaway (drift-corrected).
    chplace = plan_ch_placements(tr, chs, "es")
    ok &= run("ch place: 1 Content Highlight placed", chplace["placed"] == 1)
    ok &= run("ch place: above 'Tu conclusion...' paragraph",
              chplace["ops"][0]["start"] == T["Tu conclusion: enfocate en un producto estrella."]["start"]
              and chplace["ops"][0]["text"] == "Content Highlight\n")

    # body_end_index lands on the Final Thoughts heading.
    ok &= run("body_end_index: finds 'Reflexiones finales'",
              body_end_index(tr, "es") == T["Reflexiones finales"]["start"])

    # ---- CH formula snap: German formula terms don't cognate, and a nearby -----
    # further-reading line carries the English URL slug ('...net-profit'); token
    # scoring would steal the anchor onto the URL line. The '=' discriminator must
    # keep the CH above the localized formula.
    en_f = seq(
        (3, "6. Net Profit"),
        (0, "This is the total money left over after all expenses."),
        (0, "Content Highlight"),
        (0, "Net Profit = Operating Profit - (Debt Interest + Taxes)"),
    )
    chs_f = english_ch_anchors(en_f)
    de_f = seq(
        (3, "6. Nettogewinn"),
        (0, "Dies ist der Gesamtbetrag der nach Abzug aller Ausgaben bleibt."),
        (0, "Nettogewinn = Betriebsgewinn - (Schuldzinsen + Steuern)"),
        (0, "Weiterfuehrende Lektuere: https://trueprofit.io/blog/gross-profit-vs-net-profit"),
    )
    Tf = {b["text"]: b for b in de_f}
    chplace_f = plan_ch_placements(de_f, chs_f, "de")
    ok &= run("ch formula snap: 1 Content Highlight placed", chplace_f["placed"] == 1)
    ok &= run("ch formula snap: above the 'Nettogewinn =' formula line",
              chplace_f["ops"][0]["start"]
              == Tf["Nettogewinn = Betriebsgewinn - (Schuldzinsen + Steuern)"]["start"])
    ok &= run("ch formula snap: NOT above the further-reading URL line",
              chplace_f["ops"][0]["start"]
              != Tf["Weiterfuehrende Lektuere: https://trueprofit.io/blog/gross-profit-vs-net-profit"]["start"])

    # ---- REPAIR-mode CH now recognises 'takeaway' callouts -------------------
    bt = text_blocks("Texto.", "Tu conclusión: lidera con un producto héroe.")
    r = detect(bt, "es")
    ok &= run("es: 'Tu conclusión:' takeaway triggers CH", len(r["insertions"]) == 1)
    bt = text_blocks("Content Highlight", "Dein Fazit: setze auf ein Hero-Produkt.")
    chrep = plan_ch(bt, "de")
    ok &= run("de: 'Dein Fazit:' backs a Content Highlight (kept, not orphaned)",
              chrep["kept"] == 1 and chrep["deleted"] == 0)

    # ---- Request builder ordering (regression: replace must delete-then-insert) -
    from gdocs_ml_triggers import build_repair_requests
    reqs = build_repair_requests([{"start": 10, "end": 20, "text": "NEW\n"}], None)
    ok &= run("builder: replace emits delete BEFORE insert",
              "deleteContentRange" in reqs[0] and "insertText" in reqs[1]
              and reqs[0]["deleteContentRange"]["range"]["startIndex"] == 10
              and reqs[1]["insertText"]["text"] == "NEW\n")
    # Two pure inserts at the same index merge in document order
    reqs = build_repair_requests([{"start": 5, "text": "A\n"}, {"start": 5, "text": "B\n"}], None)
    ins = [r for r in reqs if "insertText" in r]
    ok &= run("builder: same-index inserts merge in document order",
              len(ins) == 1 and ins[0]["insertText"]["text"] == "A\nB\n")
    # Descending: a higher-index op's requests come before a lower-index op's
    reqs = build_repair_requests([{"start": 5, "text": "low\n"}, {"start": 50, "end": 60, "text": "hi\n"}], None)
    first_idx = reqs[0].get("deleteContentRange", reqs[0].get("insertText", {})).get("range", {}).get("startIndex")
    if first_idx is None:
        first_idx = reqs[0]["insertText"]["location"]["index"]
    ok &= run("builder: applies descending by index", first_idx == 50)

    print()
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
