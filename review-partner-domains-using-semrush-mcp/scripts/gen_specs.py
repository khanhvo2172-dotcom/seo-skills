"""Build the exact Semrush `resource_organic_unique` call specs for each partner domain.

Usage: python gen_specs.py <out_dir> domain1.com domain2.com ...
Writes <out_dir>/specs_<domain>.json and prints notes (domain-name guard, filter-limit problems).

Rules:
- Exclusion chain: keyword N includes `url contains kN` and excludes every earlier keyword, so each
  page is billed once. Its own negatives are excluded on its call only.
- Pass A: traffic > 0. Pass B: traffic = 0, sorted by keyword count desc, fetched one row at a time
  (the runner keeps rows with more than min_keywords_zero_traffic keywords).
- Domain-name guard: Semrush `url contains` matches the FULL URL including the domain, so a keyword
  found in the domain is replaced by word-start variants ('/k', '-k') that don't occur in the domain
  and moved to the end of the chain so no other keyword excludes it. Negatives that occur in the
  domain are dropped for that domain.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, 'config.json'), encoding='utf-8'))
KW, NEG = CFG['keywords'], CFG['negatives']
MAX_FILTERS = 25


def clean_domain(d):
    d = d.lower().strip()
    for p in ('https://', 'http://', 'www.'):
        if d.startswith(p):
            d = d[len(p):]
    return d.strip('/')


def f(sign, value):
    return {"sign": sign, "field": "url", "operation": "contains", "value": value}


def build(dom):
    dom = clean_domain(dom)
    host = f"https://www.{dom}/ https://{dom}/"
    hit = [k for k in KW if k in dom]
    order = [k for k in KW if k not in hit] + hit
    notes, units = [], []  # units: (keyword, include value, negatives)
    for k in order:
        negs = [n for n in NEG.get(k, []) if n not in host]
        dropped = [n for n in NEG.get(k, []) if n in host]
        if dropped:
            notes.append(f"negatives {dropped} for '{k}' appear in the domain name -> dropped")
        if k in hit:
            vs = [v for v in ('/' + k, '-' + k) if v not in host]
            # topic negatives (no k inside, e.g. 'migration') stay; trap negatives (k inside, e.g.
            # 'recommend') stay only if a word-start variant could still match them (e.g. 'non-profit')
            negs = [n for n in negs if k not in n or any(v in n or v in '/' + n or v in '-' + n for v in vs)]
            notes.append(f"'{k}' is in the domain name -> runs last as {vs}; "
                         f"slugs starting with '{k}' right after a slash may be missed")
            units += [(k, v, negs) for v in vs]
        else:
            units.append((k, k, negs))
    calls = []
    for i, (k, v, negs) in enumerate(units):
        base = [f('+', v)] + [f('-', n) for n in negs] + [f('-', u[1]) for u in units[:i]]
        cap = CFG['caps'].get(k, CFG['default_cap'])
        if len(base) + 1 > MAX_FILTERS:
            notes.append(f"call '{v}' needs {len(base) + 1} filters > {MAX_FILTERS} -> SPLIT REQUIRED before running")
        common = {"target": dom, "database": CFG['database']}
        calls.append({
            "keyword": k, "match": v, "cap": cap,
            "passA": {**common, "display_sort": "traffic_desc", "display_limit": cap,
                      "display_filter": base + [{"sign": "+", "field": "traffic", "operation": "greater_than", "value": 0}]},
            "passB": {**common, "display_sort": "keywords_count_desc", "display_limit": 1,
                      "display_filter": base + [{"sign": "-", "field": "traffic", "operation": "greater_than", "value": 0}]},
        })
    return dom, calls, notes


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for d in sys.argv[2:]:
        dom, calls, notes = build(d)
        json.dump(calls, open(os.path.join(out, f'specs_{dom}.json'), 'w', encoding='utf-8'), indent=1)
        mx = max(len(c['passA']['display_filter']) for c in calls)
        print(f"{dom}: {len(calls)} keyword calls, max {mx} filters")
        for n in notes:
            print('  NOTE:', n)
