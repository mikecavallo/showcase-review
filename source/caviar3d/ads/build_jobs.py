#!/usr/bin/env python3
"""ads/data/copy_final.json + brief.json -> ads/jobs.json (render jobs) and ads/data/ads_meta.json (copy + facts per ad)."""
import json, math, re
C = json.load(open('ads/data/copy_final.json')); B = {b['handle']: b for b in json.load(open('ads/data/brief.json'))}
fl = lambda r: math.floor(100 * (1 - r['price'] / r['was']) + 1e-9)
def money(x): x = float(x); return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"
oz = lambda s: re.sub(r'(\d)\s?oz', r'\1 oz', s)
SIZE = {'1': '1 spoon', '2': '2 spoons', '10': '10 spoons', 'One Spoon': '1 spoon', 'Pair of 2': '2 spoons', 'Bundle of 10 Spoons': '10 spoons', 'Default Title': ''}  # the product name already says what is in the box
# QC round 2: every badge states the saving on the size shown; heroes are the sizes with the strongest true saving
HERO = {'mother-of-pearl-spoon-3-5': '10', 'amber-dynasty-royal-kaluga-caviar': '4oz', 'royal-california-white-sturgeon-caviar': '2oz',
        'smoked-golden-whitefish-caviar': '4oz', 'shell-caviar-spoon-with-abalone-inlay': 'One Spoon'}
FOOT = 'Prices on caviarstar.com as of Oct 6, 2026'
# QC round 1: distinct headline, badge and price line per ad; no repeated names or numbers
OVR = {
  'dynasty-siberian-caviar': {'badge': 'dollars', 'headline': 'Elegant. Buttery.', 'sub': 'Soft pearls that melt on the palate'},
  'amber-dynasty-royal-kaluga-caviar': {'sub': 'Chocolate brown to dark amber, mild briny finish'},
  'royal-california-white-sturgeon-caviar': {'headline': 'Nutty. Clean. Creamy.', 'sub': 'Deep amber to dark gold pearls'},
  'dynasty-royal-osetra-caviar': {'headline': 'Nutty. Buttery. Pop.', 'sub': 'Amber Osetra, perfectly briny'},
  'mother-of-pearl-spoon-3-5': {'headline': 'Set the Caviar Table', 'sub': 'Hand cut nacre spoons that protect the flavor', 'size': 'Set of 10', 'name': 'Mother of Pearl Spoons, 3.5 inch'},
}
LIDS = {h: f'../../ads/assets/{h}/lid.jpg' for h in ['american-hackleback-sturgeon-caviar', 'dynasty-royal-osetra-caviar', 'classic-california-white-sturgeon-caviar',
        'smoked-golden-whitefish-caviar', 'dynasty-siberian-caviar', 'amber-dynasty-royal-kaluga-caviar', 'royal-california-white-sturgeon-caviar']}
jobs, meta = [], []
for p in C['products']:
    h = p['handle']; rows = B[h]['sale_variants']; f = p['final']
    hv = HERO.get(h, p['hero_variant']).replace(' ', '').lower()
    hero = next((r for r in rows if r['size'].replace(' ', '').lower() == hv), rows[0])
    pct, mx = fl(hero), max(fl(r) for r in rows)
    o = OVR.get(h, {})
    up = mx - pct >= 8 or 'up to' in (o.get('headline', f['onimage_headline']) + ' ' + o.get('sub', f['onimage_sub'])).lower()
    name = B[h]['title'].replace('Shell Plate Spoon SET', 'Shell Plate and Spoon Set')
    o = OVR.get(h, {}); size = o.get('size', SIZE.get(hero['size'], oz(hero['size'])))
    best = max(rows, key=fl); bsize = SIZE.get(best['size'], oz(best['size']))
    if o.get('badge') == 'dollars': badge = ['Save', money(hero['was'] - hero['price']), 'on ' + size.lower()]
    else: badge = ['Save', f'{pct}%', '']
    txt = (o.get('headline', f['onimage_headline']) + ' ' + o.get('sub', f['onimage_sub'])).lower()
    assert 'up to' not in txt and '%' not in txt, (h, txt)  # percentages live only in the badge, tied to the shown size
    ad = {'h': h, 'headline': o.get('headline', f['onimage_headline']), 'sub': o.get('sub', f['onimage_sub']), 'name': o.get('name', name), 'now': money(hero['price']), 'was': money(hero['was']),
          'size': size, 'badge': badge, 'cta': 'Shop the sale', 'foot': FOOT}
    if h in LIDS: ad['lid'] = LIDS[h]
    for fmt in ('1x1', '4x5', '9x16'): jobs.append({'id': h, 'format': fmt, 'ad': ad})
    meta.append({'handle': h, 'url': B[h]['url'], 'ad': ad, 'hero_row': hero, 'all_rows': rows, 'max_floor_pct': mx, 'copy': f, 'alternates': p['alternates']})
SHORT = {'amber-dynasty-royal-kaluga-caviar': 'Kaluga Hybrid', 'dynasty-siberian-caviar': 'Siberian', 'royal-california-white-sturgeon-caviar': 'Royal White',
         'classic-california-white-sturgeon-caviar': 'Classic White', 'dynasty-royal-osetra-caviar': 'Royal Osetra', 'american-hackleback-sturgeon-caviar': 'Hackleback'}
items = []
for h, short in SHORT.items():
    rows = B[h]['sale_variants']
    first = max(rows, key=fl) if h == 'amber-dynasty-royal-kaluga-caviar' else next((r for r in rows if fl(r) >= 10), max(rows, key=fl))
    items.append({'h': h, 'label': short, 'size': oz(first['size']), 'price': first['price'], 'was': first['was'], 'lid': LIDS.get(h)})
up = max(fl(r) for h in SHORT for r in B[h]['sale_variants'])
coll = C['collection']
cad = {'items': items, 'headline': coll['copy']['onimage_headline'], 'sub': f'Up to {up}% off sturgeon caviar', 'badge': ['Save up to', f'{up}%', ''], 'cta': 'Shop the sale', 'foot': FOOT}
for fmt in ('1x1', '4x5', '9x16'): jobs.append({'id': 'caviar-sale-collection', 'format': fmt, 'ad': cad})
meta.append({'handle': 'caviar-sale-collection', 'url': 'https://caviarstar.com/', 'ad': cad, 'copy': coll['copy'], 'up_to': up})
json.dump(jobs, open('ads/jobs.json', 'w'), indent=1); json.dump(meta, open('ads/data/ads_meta.json', 'w'), indent=1)
print(len(jobs), 'jobs')
for m in meta: a = m['ad']; print(m['handle'][:30].ljust(30), a['headline'], '|', a['sub'], '|', a.get('now'), a.get('was'), a.get('size'), '| badge', ' '.join(a['badge']))
