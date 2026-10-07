#!/usr/bin/env python3
"""Snapshot for the in-browser Ad Studio (adstudio.html).

    python3 tools/adstudio_data.py           write adstudio-data.json at the project root

Every catalog product the 3D Studio can render (web/catalog.json, packed assets), with what Studio.load needs, a `lid`
flag (a jar lid with the printed net weight removed exists at ads/assets/<h>/lid.jpg), its sizes and prices from the live
store (https://caviarstar.com/products/<h>.js: title, price and compare-at price in cents, available), the date of that
snapshot, an onSale flag (any available size with a compare-at price above its price) and the default copy from
ads/sheet.csv where the product has a row.

The page fetches live prices itself whenever it can; this snapshot is its fallback (offline, or a sandbox that blocks
caviarstar.com) and its "On sale now" list. Re-run it whenever prices change, then republish the page.
"""
import concurrent.futures as cf, csv, datetime, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = 'https://caviarstar.com'
OUT = os.path.join(ROOT, 'adstudio-data.json')


def renderable(it):
    """True when the packed assets Studio.load reads for this product are on disk."""
    a = os.path.join(ROOT, 'web/assets', it['h'])
    k = it['k']
    if k == 'tin': return os.path.exists(os.path.join(ROOT, 'web/brand/tin-lid.jpg'))
    if k == 'jar': return os.path.exists(os.path.join(a, 'pack.jpg')) and bool(it.get('color'))
    if k == 'lathe': return os.path.exists(os.path.join(a, 'tex.jpg')) and (bool(it.get('profile')) or os.path.exists(os.path.join(a, 'profile.json')))
    return os.path.exists(os.path.join(a, 'pack.webp')) and bool(it.get('aspect'))  # relief


def live(h):
    """The store's public product JSON; retries when the store asks us to slow down (429) or hiccups (5xx)."""
    for attempt in range(4):
        try:
            req = urllib.request.Request(f'{STORE}/products/{h}.js', headers={'User-Agent': 'caviarstar-adstudio-snapshot'})
            with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 3: raise
            time.sleep(2 * 2 ** attempt)


def sheet_rows():
    path = os.path.join(ROOT, 'ads/sheet.csv')
    if not os.path.exists(path): return {}
    rows = {}
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        r = {(k or '').strip().lower(): (v or '').strip() for k, v in r.items()}
        h = r.get('handle', '')
        if not h or h.startswith('#') or h in rows: continue
        rows[h] = {k: r[k] for k in ('size', 'headline', 'sub', 'name', 'badge', 'code', 'code_pct', 'cta') if r.get(k)}
    return rows


def main():
    cat = json.load(open(os.path.join(ROOT, 'web/catalog.json')))
    items = [it for it in cat if renderable(it)]
    skipped = [it['h'] for it in cat if not renderable(it)]
    copy = sheet_rows()
    try:   # a product the store cannot answer for now keeps its last snapshot, dated
        prev = json.load(open(OUT)); prev = {e['h']: dict(e, vdate=e.get('vdate') or prev['date']) for e in prev['products'] if e.get('v')}
    except Exception: prev = {}
    snap, errors = {}, {}
    with cf.ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(live, it['h']): it['h'] for it in items}
        for f in cf.as_completed(futs):
            h = futs[f]
            try: snap[h] = f.result()
            except Exception as e: errors[h] = str(e)[:80]
    out = []
    for it in items:
        h, p = it['h'], snap.get(it['h'])
        e = {'h': h, 't': (p or {}).get('title') or it['t'], 'k': it['k'], 'c': it['c'], 'packed': True}
        if it.get('color'): e['color'] = [round(x, 4) for x in it['color']]
        if it.get('aspect'): e['aspect'] = round(it['aspect'], 5)
        if it.get('flat'): e['flat'] = True
        # lathe profiles are left out on purpose (the bulk of catalog.json): Studio.load reads web/assets/<h>/profile.json
        if it['k'] == 'jar' and os.path.exists(os.path.join(ROOT, f'ads/assets/{h}/lid.jpg')): e['lid'] = True
        if p:
            # [size title, price cents, compare-at cents (0 = none), available 1/0]
            e['v'] = [[v['title'], int(v['price']), int(v.get('compare_at_price') or 0), 1 if v.get('available', True) else 0] for v in p['variants']]
            e['sale'] = any(v[3] and v[2] > v[1] for v in e['v'])
        elif h in prev and 'HTTP Error 404' not in errors.get(h, ''):
            e['v'], e['sale'], e['vdate'] = prev[h]['v'], prev[h]['sale'], prev[h]['vdate']
        else:
            e['v'], e['sale'] = [], False
            e['err'] = 'not found on the store' if 'HTTP Error 404' in errors.get(h, '') else 'store not reachable when the snapshot was taken'
        if h in copy: e['copy'] = copy[h]
        out.append(e)
    out.sort(key=lambda e: e['t'].lower())
    data = {'date': datetime.date.today().isoformat(), 'store': STORE, 'products': out}
    with open(OUT, 'w') as fh: json.dump(data, fh, separators=(',', ':'), ensure_ascii=False)
    on = sum(1 for e in out if e['sale'])
    print(f"{OUT}: {len(out)} products, {on} on sale now, {len(errors)} not priced, {os.path.getsize(OUT) // 1024} KB")
    if skipped: print('  not renderable (assets missing):', ', '.join(skipped))
    for h, msg in sorted(errors.items()): print(f'  {h}: {msg}' + (f' (kept prices from {prev[h]["vdate"]})' if h in prev and 'HTTP Error 404' not in msg else ''))
    missing_copy = [h for h in copy if h not in snap]
    if missing_copy: print('  sheet rows without a renderable, priced product:', ', '.join(missing_copy))
    return 0 if len(errors) < len(items) else 1


if __name__ == '__main__': sys.exit(main())
