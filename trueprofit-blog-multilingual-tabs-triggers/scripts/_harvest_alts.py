# -*- coding: utf-8 -*-
import json
from gdocs_ml_triggers import get_service, doc_id_from, resolve_tabs, flatten, english_image_triggers, DEFAULT_CREDS, DEFAULT_TOKEN

DOC="1UVTgZP4cgrAGlwtKxTlZ_kr5TpGk8r1hfvv_1E1kipA"
svc=get_service(DEFAULT_CREDS, DEFAULT_TOKEN)
doc=svc.documents().get(documentId=doc_id_from(DOC), includeTabsContent=True).execute()
tabs=resolve_tabs(doc)
en=english_image_triggers(flatten(tabs["en"][2]))
en_urls=[u for u,_ in en]
print("English URLs (%d):" % len(en_urls))
out={}
for lang in ["es","de","fr"]:
    pairs=english_image_triggers(flatten(tabs[lang][2]))
    urls=[u for u,_ in pairs]; alts=[a for _,a in pairs]
    out[lang]=alts
    ok = urls==en_urls
    print("%s: %d alts | url order matches English: %s" % (lang, len(alts), ok))
    if not ok:
        print("   en :", en_urls)
        print("   %s :" % lang, urls)
with open("_alts.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("\nSaved _alts.json")
for lang in ["es","de","fr"]:
    print("\n%s alts:" % lang)
    for i,a in enumerate(out[lang],1):
        print("  %2d. %s" % (i,a))
