# -*- coding: utf-8 -*-
from gdocs_ml_triggers import get_service, doc_id_from, resolve_tabs, flatten, DEFAULT_CREDS, DEFAULT_TOKEN
from detect_ml import _clean, _is_image_start

DOC="1UVTgZP4cgrAGlwtKxTlZ_kr5TpGk8r1hfvv_1E1kipA"
svc=get_service(DEFAULT_CREDS, DEFAULT_TOKEN)
doc=svc.documents().get(documentId=doc_id_from(DOC), includeTabsContent=True).execute()
tabs=resolve_tabs(doc)
def desc(b):
    if b is None: return "(none)"
    t=_clean(b["text"])
    if b.get("level",0) and t: return "H%d:%s" % (b["level"], t[:40])
    if _is_image_start(t): return "IMG"
    return "prose:%s" % (t[:40] if t else "(blank)")
for lang in ["es","de","fr"]:
    title,tid,content=tabs[lang]
    blocks=flatten(content)
    print("\n===== %s =====" % lang)
    bad=0
    for i,b in enumerate(blocks):
        t=_clean(b["text"])
        if not _is_image_start(t): continue
        prev=blocks[i-1] if i>0 else None
        nxt=blocks[i+1] if i+1<len(blocks) else None
        prev_is_heading = prev is not None and prev.get("level",0) and _clean(prev["text"])
        slug=t.split("/")[-1].split(",")[0][:22]
        flag = "  <-- TOP OF SECTION (under heading)" if prev_is_heading else ""
        if prev_is_heading: bad+=1
        print("  %-24s prev=[%s] next=[%s]%s" % (slug, desc(prev), desc(nxt), flag))
    print("  images under-heading (bad): %d / 12" % bad)
