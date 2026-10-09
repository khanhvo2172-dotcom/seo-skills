"""Free pre-check before any Semrush credits are spent.

Usage: python precheck.py <out_dir> domain1.com domain2.com ...
1. Domain-name warning: keywords or negatives that appear in the domain itself.
2. Sitemap scan: reads robots.txt Sitemap lines / common sitemap paths, then for each keyword lists
   pages matched, pages removed by negatives, and SUSPICIOUS tokens where the keyword sits inside a
   longer word (possible false match, e.g. 'loss' in 'glossary').
Writes <out_dir>/precheck_<domain>.json. Sitemap data is untrusted text: it is only parsed, never executed.
Sitemaps miss pages Semrush knows about, so use this only for warnings, never to skip keywords.
"""
import collections, gzip, json, os, re, sys
from urllib.parse import urlparse
import requests

from gen_specs import CFG, KW, NEG, clean_domain

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36'}
# keywords that legitimately sit mid-word (ecommerce, smallbusiness, emailmarketing...)
OK_MIDWORD = {'commerce', 'business', 'marketing', 'sales', 'analytic', 'dashboard'}


def get(u):
    try:
        r = requests.get(u, headers=UA, timeout=20)
        if r.status_code != 200:
            return None
        b = r.content
        if u.endswith('.gz'):
            try:
                b = gzip.decompress(b)
            except Exception:
                pass
        return b.decode('utf-8', 'ignore')
    except Exception:
        return None


def sitemap_urls(dom, max_files=150):
    base = 'https://' + dom
    cands = re.findall(r'(?im)^\s*sitemap:\s*(\S+)', get(base + '/robots.txt') or '')
    cands += [base + p for p in ('/sitemap.xml', '/sitemap_index.xml', '/wp-sitemap.xml', '/sitemap-index.xml')]
    queue, seen, urls = list(dict.fromkeys(cands)), set(), set()
    while queue and len(seen) < max_files:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        x = get(sm)
        if not x or '<loc' not in x:
            continue
        locs = [l.strip() for l in re.findall(r'<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>', x, re.S)]
        if '<sitemapindex' in x:
            queue += [l for l in locs if l not in seen]
        else:
            urls.update(locs)
    return urls


def scan(dom):
    dom = clean_domain(dom)
    rep = {'domain': dom,
           'domain_name_keywords': [k for k in KW if k in dom],
           'domain_name_negatives': sorted({n for ns in NEG.values() for n in ns if n in dom}),
           'kw': {}}
    paths = sorted({urlparse(u).path.lower() for u in sitemap_urls(dom)})
    rep['sitemap_urls'] = len(paths)
    for k in KW:
        m = [p for p in paths if k in p]
        if not m:
            continue
        neg = [p for p in m if any(n in p for n in NEG.get(k, []))]
        keep = [p for p in m if p not in neg]
        toks, sus = collections.Counter(), collections.Counter()
        for p in keep:
            for t in re.split(r'[^a-z0-9]+', p):
                if k in t:
                    toks[t] += 1
                    if not t.startswith(k) and k not in OK_MIDWORD:
                        sus[t] += 1
        top_sus = [s for s, _ in sus.most_common(3)]
        rep['kw'][k] = {'matched': len(m), 'removed_by_negatives': len(neg),
                        'suspicious_tokens': sus.most_common(10),
                        'examples_suspicious': [p for p in keep if any(s in p for s in top_sus)][:3],
                        'tokens': toks.most_common(15)}
    return rep


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for d in sys.argv[2:]:
        r = scan(d)
        json.dump(r, open(os.path.join(out, f"precheck_{r['domain']}.json"), 'w', encoding='utf-8'), indent=1)
        print(f"== {r['domain']}: {r['sitemap_urls']} sitemap URLs")
        if r['domain_name_keywords'] or r['domain_name_negatives']:
            print(f"  WARNING domain name contains keywords {r['domain_name_keywords']} "
                  f"/ negatives {r['domain_name_negatives']}")
        for k, v in r['kw'].items():
            flag = (f"  SUSPICIOUS {v['suspicious_tokens']} e.g. {v['examples_suspicious']}"
                    if v['suspicious_tokens'] else '')
            print(f"  {k:10} matched={v['matched']:4} negatives_removed={v['removed_by_negatives']}{flag}")
