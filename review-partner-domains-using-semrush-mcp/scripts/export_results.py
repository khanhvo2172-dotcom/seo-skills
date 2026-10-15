"""Merge per-domain Semrush results into one CSV and print a cost/summary line per domain.

Usage: python export_results.py <out_dir> <csv_path>
Reads <out_dir>/result_<domain>.json files written by the runner:
  {"domain", "rows": [{"url","keywords","traffic","keyword","pass"}], "stop_rows": [...],
   "unprocessed": [...], "errors": [...]}
Credits = (kept rows + stop rows) x 10, because the MCP's per-call api_units is unreliable when
domains run in parallel. Each URL is re-tagged with ALL matching keywords, not just the one that
fetched it.
"""
import csv, glob, json, os, sys
from urllib.parse import urlparse

from gen_specs import KW

out_dir, csv_path = sys.argv[1], sys.argv[2]
w = csv.writer(open(csv_path, 'w', newline='', encoding='utf-8-sig'))
w.writerow(['Domain', 'URL', 'US Traffic', 'Organic Keywords', 'Matched keywords', 'Pass'])
for fp in sorted(glob.glob(os.path.join(out_dir, 'result_*.json'))):
    r = json.load(open(fp, encoding='utf-8'))
    seen, rows = set(), []
    for x in r.get('rows', []):
        u = urlparse(x['url'])
        key = u.netloc.lower().removeprefix('www.') + u.path.rstrip('/').lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(x)
    rows.sort(key=lambda x: (-int(x['traffic']), -int(x['keywords'])))
    for x in rows:
        p = urlparse(x['url']).path.lower()
        w.writerow([r['domain'], x['url'], x['traffic'], x['keywords'],
                    ', '.join(k for k in KW if k in p),
                    'traffic>0' if x['pass'] == 'A' else 'traffic=0, kw>5'])
    credits = (len(r.get('rows', [])) + len(r.get('stop_rows', []))) * 10
    with_traffic = sum(1 for x in rows if int(x['traffic']) > 0)
    print(f"{r['domain']}: kept={len(rows)} with_traffic={with_traffic} credits~{credits} "
          f"unprocessed={r.get('unprocessed', [])} errors={len(r.get('errors', []))}")
print('CSV:', csv_path)
