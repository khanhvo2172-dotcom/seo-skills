# -*- coding: utf-8 -*-
from gdocs_ml_triggers import get_service, doc_id_from, resolve_tabs, flatten, DEFAULT_CREDS, DEFAULT_TOKEN
from detect_ml import _clean, _is_image_start
import re

DOC="1UVTgZP4cgrAGlwtKxTlZ_kr5TpGk8r1hfvv_1E1kipA"
svc=get_service(DEFAULT_CREDS, DEFAULT_TOKEN)
doc=svc.documents().get(documentId=doc_id_from(DOC), includeTabsContent=True).execute()
tabs=resolve_tabs(doc)
RE_CH=re.compile(r"^\s*Content\s+Highlight\s*:?\s*$", re.I)
for lang in ["es","de","fr"]:
    title, tid, content = tabs[lang]
    blocks=flatten(content)
    print("\n==================== %s tab: %s ====================" % (lang, title))
    for idx,b in enumerate(blocks):
        t=_clean(b["text"])
        if b.get("level",0) and t:
            print("H%d  %s" % (b["level"], t[:55]))
        elif _is_image_start(t):
            print("    IMG  %s" % t[:85])
        elif RE_CH.match(t):
            nxt = _clean(blocks[idx+1]["text"]) if idx+1 < len(blocks) else ""
            print("    >>CH<< [%s]   next-line: %s" % (t, nxt[:60]))
