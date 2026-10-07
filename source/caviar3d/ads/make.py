#!/usr/bin/env python3
"""Caviar Star sale-ad generator. One sheet in, every ad out, priced from the live store.

    python3 ads/make.py                  render every active row of ads/sheet.csv (only ads whose content changed)
    python3 ads/make.py --check          read the price baked into each rendered video (MP4 metadata) and compare it
                                         with caviarstar.com right now: OK, STALE, SALE ENDED or SOLD OUT
    python3 ads/make.py --discover       print every product on sale right now as sheet rows, ready to paste in
    python3 ads/make.py --sheet URL      use a Google Sheet instead (File > Share > Publish to web > CSV link)
    python3 ads/make.py --stills-only    PNGs only, for a quick look
    python3 ads/make.py --only HANDLE    one product

Prices never live in the sheet. Every run reads price and compare-at price from the store, so an ad can only show a
price the site shows. Percentages round down. A row whose sale has ended renders without a badge or strike price
(and says so); a sold-out size is skipped. Each MP4 and PNG carries what it shows (price, was, saving, size, when it
was checked) in its metadata, which --check reads back. Platforms strip metadata on upload; it is for your files.
"""
import argparse, csv, datetime, hashlib, io, json, math, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
OUT = 'ads/out/gen'; STORE = 'https://caviarstar.com'
FORMATS = ('9x16', '4x5', '1x1')
FOOT = 'Prices as shown on caviarstar.com. Subject to change.'
STAGE_FILES = ['doc/stage/ad.html', 'web/studio.js', 'ads/render_ads.mjs']
DASH = re.compile('[‒–—―]')


def money(x):
    x = float(x); return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"


def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())


def floor_pct(price, was): return math.floor(100 * (1 - price / was) + 1e-9)


_cache = {}
def product(handle):
    """Live product from the store's public JSON: title, variants with price, compare-at and availability (cents)."""
    if handle not in _cache:
        req = urllib.request.Request(f'{STORE}/products/{handle}.js', headers={'User-Agent': 'caviarstar-ad-generator'})
        with urllib.request.urlopen(req, timeout=30) as r: _cache[handle] = json.load(r)
    return _cache[handle]


def variants(handle):
    p = product(handle)
    return [{'size': v['title'], 'price': v['price'] / 100, 'was': (v['compare_at_price'] or 0) / 100, 'available': v.get('available', True),
             'sku': v.get('sku') or ''} for v in p['variants']]


def read_sheet(src):
    if re.match(r'https?://', src):
        with urllib.request.urlopen(src, timeout=30) as r: text = r.read().decode('utf-8-sig')
    else: text = open(src, encoding='utf-8-sig').read()
    rows = [{(k or '').strip().lower(): (v or '').strip() for k, v in r.items()} for r in csv.DictReader(io.StringIO(text))]
    return [r for r in rows if r.get('handle') and not r['handle'].startswith('#')]


# sizes as people say them: "One Spoon" -> "1 spoon", "4oz" -> "4 oz"
SIZE = {'onespoon': '1 spoon', 'pairof2': '2 spoons', 'bundleof10spoons': '10 spoons', 'defaulttitle': ''}
def say_size(s, handle=''):
    if re.fullmatch(r'\d+', str(s).strip()):
        n = int(s); thing = 'spoon' if 'spoon' in handle else 'piece'
        return f'{n} {thing}' + ('s' if n > 1 else '')
    return SIZE.get(norm(s), re.sub(r'(\d)\s?oz', r'\1 oz', s))


def ensure_lid(h, force=False):
    """Jar lids print the 1 oz net weight; an ad for another size gets a copy of the lid without it (same spot on every
    Caviar Star lid). Returns the lid path for the stage, or None for products without a printed lid."""
    dst, src = f'ads/assets/{h}/lid.jpg', f'web/assets/{h}/lid.jpg'
    if os.path.exists(dst) and not force: return f'../../{dst}'
    if not os.path.exists(src): return None
    import cv2, numpy as np
    im = cv2.imread(src)
    if im.shape[:2] != (1024, 1024): return f'../../{src}'
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); S, V = hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    bgS, bgV = cv2.medianBlur(hsv[..., 1], 21).astype(int), cv2.medianBlur(hsv[..., 2], 21).astype(int)
    # printed text: thin strokes brighter than the label around them, or paler than a coloured label (salmon, paddlefish)
    text = (((V - bgV) > 35) & (S < 90)) | (((bgS - S) > 45) & ((V - bgV) > 10)) | ((bgV > 100) & (bgS > 90) & ((bgS - S) > 22) & (V >= bgV))
    y0, y1, x0, x1 = 668, 778, 420, 630
    m = np.zeros(im.shape[:2], np.uint8); m[y0:y1, x0:x1] = text[y0:y1, x0:x1] * 255
    if (m > 0).sum() < 900: return f'../../{src}'  # nothing printed there (only the label's dots)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    os.makedirs(os.path.dirname(dst), exist_ok=True); cv2.imwrite(dst, cv2.inpaint(im, m, 5, cv2.INPAINT_TELEA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    return f'../../{dst}'


def build_ad(row, today):
    """One sheet row -> the ad the stage renders, plus the facts it was built from. Raises ValueError on a bad row."""
    h = row['handle']; vs = variants(h); p = product(h)
    want = row.get('size', '')
    on_sale = [v for v in vs if v['available'] and v['was'] > v['price']]
    if want:
        v = next((v for v in vs if norm(v['size']) == norm(want)), None)
        if not v: raise ValueError(f"{h}: no size '{want}' on the site (sizes: {', '.join(x['size'] for x in vs)})")
    else:
        v = max(on_sale, key=lambda v: floor_pct(v['price'], v['was'])) if on_sale else next((v for v in vs if v['available']), vs[0])
    if not v['available']: raise ValueError(f"{h} {v['size']}: sold out on the site, skipped")
    sale = v['was'] > v['price']; pct = floor_pct(v['price'], v['was']) if sale else 0
    text = {k: DASH.sub(', ', row.get(k, '')) for k in ('headline', 'sub', 'name', 'cta', 'code')}
    for k in ('headline', 'sub'):
        if '%' in text[k] or 'up to' in text[k].lower(): raise ValueError(f"{h}: keep percentages out of the {k}; the badge carries the saving for the size shown")
    mode = (row.get('badge') or 'percent').lower()
    size = say_size(v['size'], h)
    if text['code'] and row.get('code_pct'):
        cp = int(float(row['code_pct'])); code = text['code'].upper()
        badge = ['Extra', f'{cp}%', f'code {code}']
    elif not sale or mode == 'none': badge = None
    elif mode == 'dollars': badge = ['Save', money(v['was'] - v['price']), f'on {size.lower()}' if size else '']
    else: badge = ['Save', f'{pct}%', '']
    catalog = row.get('_catalog') == 'y'
    ad = {'h': h, 'headline': text['headline'] or p['title'], 'sub': text['sub'], 'name': text['name'] or p['title'],
          'now': money(v['price']), 'was': money(v['was']) if sale else '', 'size': size, 'badge': badge,
          'cta': text['cta'] or ('Shop now' if catalog or not sale else 'Shop the sale'), 'foot': row.get('foot') or FOOT}
    if catalog: ad.update(catalog=True, badge=None, now='', was='', size='', foot=''); badge = None
    lid = ensure_lid(h)
    if lid: ad['lid'] = lid
    if row.get('dur'): ad['dur'] = max(6.0, float(row['dur']))  # the animation needs about 6 s to land
    facts = {'handle': h, 'title': p['title'], 'size': v['size'], 'sku': v['sku'], 'price': v['price'], 'was': v['was'] if sale else None,
             'pct': pct if sale else None, 'badge': ' '.join(x for x in (badge or []) if x), 'url': f'{STORE}/products/{h}', 'checked': today,
             'catalog': catalog}
    if not sale: facts['note'] = 'not on sale right now: no badge, no strike price'
    return ad, facts


def stage_key():
    m = hashlib.sha1()
    for f in STAGE_FILES: m.update(open(f, 'rb').read())
    return m.hexdigest()[:10]


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def probe(path):
    """The facts an MP4 was stamped with, or None."""
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags=comment', '-of', 'json', path], capture_output=True, text=True, check=True).stdout
        return json.loads(json.loads(out)['format']['tags']['comment'])
    except Exception: return None


def stamp(path, facts, key):
    """Write what the video shows into its metadata (no re-encode)."""
    f = dict(facts, key=key)
    desc = f"{f['title']}, {say_size(f['size'], f['handle']) or 'one size'}: {money(f['price'])}" + (f", was {money(f['was'])} (save {f['pct']}%)" if f.get('was') else '') + f". Checked on caviarstar.com {f['checked']}."
    if f.get('catalog'): desc = f"{f['title']}: catalog version, no price on screen (the platform shows the live price). Built {f['checked']}."
    tmp = path + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-c', 'copy', '-map_metadata', '-1', '-metadata', f"title={f['title']}",
                    '-metadata', f'comment={json.dumps(f, separators=(",", ":"))}', '-metadata', f'description={desc}',
                    '-metadata', 'artist=Caviar Star', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, path)


def stamp_png(path, facts, key):
    from PIL import Image, PngImagePlugin
    im = Image.open(path); info = PngImagePlugin.PngInfo(); info.add_text('Comment', json.dumps(dict(facts, key=key), separators=(',', ':')))
    im.save(path, pnginfo=info)


def png_key(path):
    try:
        from PIL import Image
        return json.loads(Image.open(path).text.get('Comment', '{}')).get('key')
    except Exception: return None


def render(jobs, stills, workers):
    if not jobs: return
    os.makedirs('ads/out/gen', exist_ok=True)
    parts = [jobs[i::workers] for i in range(workers)]; procs = []
    for i, part in enumerate(p for p in parts if p):
        jf = f'{OUT}/.jobs{i}.json'; json.dump(part, open(jf, 'w'))
        procs.append(subprocess.Popen(['node', 'ads/render_ads.mjs', jf] + (['--stills-only'] if stills else [])))
    for p in procs: p.wait()


def check(args):
    rows = []
    for fn in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
        if not fn.endswith('.mp4'): continue
        f = probe(f'{OUT}/{fn}')
        if not f: rows.append((fn, 'NO METADATA', '')); continue
        if f.get('catalog'): rows.append((fn, 'OK', 'catalog version, no price on screen')); continue
        try: v = next((v for v in variants(f['handle']) if norm(v['size']) == norm(f['size'])), None)
        except Exception as e: rows.append((fn, 'ERROR', str(e)[:60])); continue
        if not v: status, why = 'GONE', 'size no longer on the site'
        elif not v['available']: status, why = 'SOLD OUT', ''
        elif f.get('was') and v['was'] <= v['price']: status, why = 'SALE ENDED', f"now {money(v['price'])}, no compare-at price"
        elif abs(v['price'] - f['price']) > .001 or abs((v['was'] if v['was'] > v['price'] else 0) - (f.get('was') or 0)) > .001:
            status, why = 'STALE', f"video {money(f['price'])}" + (f"/{money(f['was'])}" if f.get('was') else '') + f", site {money(v['price'])}" + (f"/{money(v['was'])}" if v['was'] > v['price'] else '')
        else: status, why = 'OK', f"{money(f['price'])}" + (f", was {money(f['was'])}, save {f['pct']}%" if f.get('was') else '') + f", checked {f['checked']}"
        rows.append((fn, status, why))
    w = max([len(r[0]) for r in rows] + [10])
    for fn, s, why in rows: print(fn.ljust(w), s.ljust(11), why)
    bad = [r for r in rows if r[1] not in ('OK',)]
    print(f"\n{len(rows)} videos, {len(bad)} need attention." + (" Run python3 ads/make.py to re-render them from live prices." if bad else ''))
    return 1 if bad else 0


def discover():
    """Every product the store has on sale right now, one sheet row each (the biggest true saving pre-selected)."""
    page, out = 1, []
    while True:
        with urllib.request.urlopen(f'{STORE}/products.json?limit=250&page={page}', timeout=30) as r: ps = json.load(r)['products']
        if not ps: break
        for p in ps:
            vs = [v for v in p['variants'] if v.get('compare_at_price') and float(v['compare_at_price']) > float(v['price']) and v.get('available', True)]
            if vs:
                best = max(vs, key=lambda v: floor_pct(float(v['price']), float(v['compare_at_price'])))
                out.append({'active': 'n', 'handle': p['handle'], 'size': best['title'] if best['title'] != 'Default Title' else '', 'headline': '', 'sub': '',
                            'badge': 'percent', 'formats': '9x16 4x5 1x1', 'catalog': 'n',
                            '_info': f"{p['title']}: {'' if best['title'] == 'Default Title' else best['title'] + ' '}{money(best['price'])} was {money(best['compare_at_price'])} ({floor_pct(float(best['price']), float(best['compare_at_price']))}%)"})
        page += 1
    wr = csv.writer(sys.stdout); wr.writerow(SHEET_COLS)
    for o in out: wr.writerow([o.get(c, '') for c in SHEET_COLS])
    print('\n# ' + '\n# '.join(o['_info'] for o in out), file=sys.stderr)


SHEET_COLS = ['active', 'handle', 'size', 'headline', 'sub', 'name', 'badge', 'code', 'code_pct', 'cta', 'formats', 'catalog', 'dur', 'foot']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sheet', default='ads/sheet.csv'); ap.add_argument('--check', action='store_true'); ap.add_argument('--discover', action='store_true')
    ap.add_argument('--stills-only', action='store_true'); ap.add_argument('--only'); ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--force', action='store_true', help='re-render even if nothing changed')
    a = ap.parse_args()
    if a.check: sys.exit(check(a))
    if a.discover: return discover()
    today = datetime.date.today().isoformat(); key0 = stage_key()
    jobs, plan, problems = [], [], []
    for row in read_sheet(a.sheet):
        if row.get('active', 'y').lower() not in ('y', 'yes', '1', 'true'): continue
        if a.only and row['handle'] != a.only: continue
        fmts = [f for f in re.split(r'[\s,]+', row.get('formats') or ' '.join(FORMATS)) if f in FORMATS]
        variants_to_make = [dict(row)] + ([dict(row, _catalog='y')] if row.get('catalog', '').lower() in ('y', 'yes', '1', 'true') else [])
        for r in variants_to_make:
            try: ad, facts = build_ad(r, today)
            except ValueError as e: problems.append(str(e)); continue
            except Exception as e: problems.append(f"{r['handle']}: could not read the store ({e})"); continue
            name = f"{r['handle']}-catalog" if facts['catalog'] else f"{r['handle']}-{slug(facts['size']) or 'set'}"
            key = hashlib.sha1((key0 + json.dumps(ad, sort_keys=True)).encode()).hexdigest()[:12]
            for fmt in fmts:
                base = f'{OUT}/{name}-{fmt}'
                mp = (probe(base + '.mp4') or {}) if os.path.exists(base + '.mp4') else {}
                have = os.path.exists(base + '.png') and (a.stills_only or (mp.get('key') == key and mp.get('price') == facts['price'] and mp.get('was') == facts['was']))
                if have and png_key(base + '.png') == key and not a.force: plan.append((base, facts, key, 'unchanged')); continue
                for ext in ('.png', '.mp4'):
                    if os.path.exists(base + ext): os.remove(base + ext)
                jobs.append({'id': f'gen/{name}', 'format': fmt, 'ad': ad}); plan.append((base, facts, key, 'render'))
    print(f"{len(jobs)} to render, {sum(1 for p in plan if p[3] == 'unchanged')} unchanged.")
    render(jobs, a.stills_only, max(1, a.workers))
    manifest = []
    for base, facts, key, what in plan:
        if what == 'render':
            if os.path.exists(base + '.png'): stamp_png(base + '.png', facts, key)
            if os.path.exists(base + '.mp4'): stamp(base + '.mp4', facts, key)
        manifest.append(dict(facts, file=os.path.basename(base), rendered=what == 'render' and os.path.exists(base + '.png')))
    json.dump(manifest, open(f'{OUT}/manifest.json', 'w'), indent=1)
    with open(f'{OUT}/manifest.csv', 'w', newline='') as fh:
        wr = csv.writer(fh); wr.writerow(['file', 'product', 'size', 'price', 'was', 'save', 'badge', 'checked', 'url'])
        for m in manifest: wr.writerow([m['file'], m['title'], m['size'], m['price'], m['was'] or '', f"{m['pct']}%" if m['pct'] else '', m['badge'], m['checked'], m['url']])
    for m in manifest:
        if m['catalog']: print(f"  {m['file']:<58} {'catalog version, no price on screen'}"); continue
        print(f"  {m['file']:<58} {money(m['price']):>8} {('was ' + money(m['was'])) if m['was'] else '':<12} {m['badge'] or 'no badge'}")
    if problems: print('\nSkipped:\n  ' + '\n  '.join(problems))


if __name__ == '__main__': main()
