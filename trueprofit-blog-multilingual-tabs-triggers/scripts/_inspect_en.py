# -*- coding: utf-8 -*-
import sys
from gdocs_ml_triggers import get_service, doc_id_from, resolve_tabs, flatten, DEFAULT_CREDS, DEFAULT_TOKEN
from detect_ml import _clean, _is_image_start

DOC="1UVTgZP4cgrAGlwtKxTlZ_kr5TpGk8r1hfvv_1E1kipA"
svc=get_service(DEFAULT_CREDS, DEFAULT_TOKEN)
doc=svc.documents().get(documentId=doc_id_from(DOC), includeTabsContent=True).execute()
tabs=resolve_tabs(doc)
for lang in ["en"]:
    title, tid, content = tabs[lang]
    blocks=flatten(content)
    print("=== %s tab: %s ===" % (lang, title))
    for b in blocks:
        t=_clean(b["text"])
        if b.get("level",0) and t:
            print("H%d  %s" % (b["level"], t[:60]))
        elif _is_image_start(t):
            print("    IMG  %s" % t[:90])
