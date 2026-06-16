# -*- coding: utf-8 -*-
"""Unit tests for detect_ml.detect() - no Google API needed.

Run:  python test_detect_ml.py
"""
from detect_ml import detect, parse_existing_triggers, plan_repairs, plan_ch
from place_ml import english_image_anchors, plan_placements, heading_score, align_headings, headings


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

    # ---- Heading-anchored placement (out-of-sync translated tab) -----------
    ok &= run("cognate: competition~competencia", heading_score("Low Competition", "baja competencia") >= 1)
    ok &= run("cognate: organic~organica", heading_score("Organic Fruit", "fruta organica") >= 1)
    ok &= run("cognate: lamps~lamparas", heading_score("Mushroom Lamps", "Lamparas de setas") >= 1)
    ok &= run("cognate: no false match socks/calcetines", heading_score("Fuzzy Socks", "Calcetines esponjosos") == 0)

    en = seq(
        (2, "What Is a Profitable Niche with Low Competition?"),
        (0, "Image (sentence note): https://x/intro-1.webp, Alt is Large preview"),
        (2, "10 Profitable Niches with Low Competition"),
        (3, "Sustainable Mushroom Lamps"),
        (0, "Image (sentence note): https://x/mushroom-2.webp, Alt is Mushroom lamp"),
        (3, "Organic Dried Fruit Slices"),
        (0, "Image (sentence note): https://x/organic-3.webp, Alt is Organic snacks"),
        (3, "Natural-fiber Fuzzy Socks"),
        (0, "Image (sentence note): https://x/socks-4.webp, Alt is Fuzzy socks"),
        (3, "Frozen Smoothie Cups"),
        (0, "Image (sentence note): https://x/smoothie-5.webp, Alt is Smoothie cups"),
        (0, "Image (sentence note): https://x/dashboard-6.webp, Alt is Dashboard"),
    )
    anchors = english_image_anchors(en)
    ok &= run("anchors: 6 images found", len(anchors) == 6)
    ok &= run("anchors: dashboard offset=1 under smoothie heading",
              anchors[5]["offset"] == 1 and anchors[4]["h_order"] == anchors[5]["h_order"])

    # Prose between headings + a trailing FAQ heading, so "end of section"
    # (before the next heading) is distinct from "right after the heading".
    tr = seq(
        (1, "10 nichos rentables con baja competencia"),
        (2, "Resumen rapido"),
        (0, "Texto de resumen."),
        (2, "Que es un nicho rentable con baja competencia?"),
        (0, "Un nicho es un segmento de mercado."),
        (2, "10 nichos rentables con baja competencia en 2026"),
        (3, "Lamparas de setas sostenibles"),
        (0, "Las lamparas de setas son tendencia."),
        (3, "Rodajas de fruta organica deshidratada"),
        (0, "La fruta deshidratada vende bien."),
        (3, "Calcetines esponjosos de fibra natural"),
        (0, "Los calcetines son comodos."),
        (3, "Vasos de smoothie congelado"),
        (0, "Los smoothies congelados gustan."),
        (2, "Preguntas frecuentes"),
    )
    tr_alts = ["Vista previa", "Lampara de setas", "Fruta organica", "Calcetines", "Vasos smoothie", "Panel"]
    place = plan_placements(tr, anchors, tr_alts, [a["alt"] for a in anchors])
    ok &= run("place: 6 images placed", place["placed"] == 6)

    th = {h["text"]: h for h in headings(tr)}
    rev = {r["n"]: r for r in place["review"]}
    ok &= run("place: intro -> '¿Que es...' heading", rev[1]["tr_heading"].startswith("Que es"))
    ok &= run("place: mushroom -> 'Lamparas...' (keyword)", rev[2]["tr_heading"].startswith("Lamparas") and rev[2]["how"] == "keyword")
    ok &= run("place: socks -> 'Calcetines...' (ordinal fallback ok)", rev[4]["tr_heading"].startswith("Calcetines"))
    ok &= run("place: smoothie -> 'Vasos de smoothie'", rev[5]["tr_heading"].startswith("Vasos"))

    def op_for(slug):
        return [o for o in place["ops"] if slug in o["text"]][0]

    # Each image lands at the END of its section = the start of the NEXT heading
    # (not th["end"], which would be right under its own heading).
    ok &= run("place: mushroom at section end (before 'Rodajas' heading)",
              op_for("mushroom-2")["start"] == th["Rodajas de fruta organica deshidratada"]["start"])
    ok &= run("place: organic at section end (before 'Calcetines' heading)",
              op_for("organic-3")["start"] == th["Calcetines esponjosos de fibra natural"]["start"])
    # smoothie (#5) and dashboard (#6) both land at the end of the smoothie section,
    # i.e. right before the trailing FAQ heading, sharing one insert index.
    smoothie_op = op_for("smoothie-5")
    dash_op = op_for("dashboard-6")
    ok &= run("place: smoothie & dashboard share the section-end index (before FAQ)",
              smoothie_op["start"] == dash_op["start"] == th["Preguntas frecuentes"]["start"])
    ok &= run("place: image is NOT inserted right under its own heading",
              op_for("mushroom-2")["start"] != th["Lamparas de setas sostenibles"]["end"])
    ok &= run("place: op text canonical with translated alt",
              smoothie_op["text"] == "Image (sentence note): https://x/smoothie-5.webp, Alt is Vasos smoothie\n")

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
