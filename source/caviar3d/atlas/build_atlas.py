#!/usr/bin/env python3
"""Merge the research into atlas/web/atlas.json for the page, and stage the page's files.
    python3 atlas/build_atlas.py <publish dir>
Inputs: atlas/research/{products,species,guide}.json, atlas/build/colors.json, web/catalog.json, work/spec.json."""
import json, os, re, shutil, sys
R = 'atlas/research'
P = json.load(open(f'{R}/products.json'))
SP = json.load(open(f'{R}/species.json')) if os.path.exists(f'{R}/species.json') else {'species': [], 'hybrids': []}
G = json.load(open(f'{R}/guide.json'))
COL = json.load(open('atlas/build/colors.json'))
CAT = {c['h']: c for c in json.load(open('web/catalog.json'))}
SPEC = json.load(open('work/spec.json'))

# map pins: one per place the store names (coordinates placed by hand from the named region)
ORIGINS = [
    ('Sacramento, California', 'Sacramento', 38.58, -121.49, ['classic-california-white-sturgeon-caviar', 'royal-california-white-sturgeon-caviar', 'supreme-california-white-sturgeon-caviar'], dict(dx=-9, anchor='end')),
    ('Alaska and the North Pacific', 'Alaska', 60.5, -151.0, ['american-salmon-caviar', 'smoked-american-salmon-caviar'], dict(dx=-9, anchor='end')),
    ('Great Lakes', 'Great Lakes', 45.0, -84.5, ['golden-whitefish-roe', 'smoked-golden-whitefish-caviar'], dict(dx=9, dy=-6)),
    ('Missouri and Mississippi rivers', 'Mississippi', 38.6, -90.2, ['american-hackleback-sturgeon-caviar'], dict(dx=-9, dy=-4, anchor='end')),
    ('Mississippi and White rivers, Arkansas', 'Arkansas', 34.0, -91.1, ['american-paddlefish-caviar'], dict(dx=-9, dy=6, anchor='end')),
    ('Baton Rouge, Louisiana', 'Louisiana', 30.45, -91.19, ['american-bowfin-caviar'], dict(dx=-9, dy=12, anchor='end')),
    ('Clearwater, Florida', 'Florida', 27.97, -82.8, ['bottarga-dried-and-cured-mullet-roe'], dict(dx=9, dy=10)),
    ('North Fork, Long Island', 'Long Island', 41.0, -72.5, ['white-escargot-snail-caviar'], dict(dx=9, dy=2)),
    ('Spain', 'Spain', 40.2, -3.7, ['tuna-bottarga-dried-and-cured-tuna-fish-roe'], dict(dx=-9, dy=6, anchor='end')),
    ('France', 'France', 45.0, 0.6, ['caviar-house-prunier-osetra-caviar', 'bourbon-barrel-smoked-trout-roe', 'rainbow-trout-roe'], dict(dx=-9, dy=-6, anchor='end')),
    ('Near Parma, Italy', 'Italy', 44.8, 10.33, ['classic-italian-white-sturgeon-caviar'], dict(dx=2, dy=16, anchor='middle')),
    ('Germany', 'Germany', 51.2, 10.4, ['dieckmann-hansen-reserve-german-osetra-caviar', 'albino-almas-caviar'], dict(dx=-9, dy=-5, anchor='end')),
    ('Warmia, Poland', 'Poland', 53.8, 20.5, ['lyna-polska-siberian-caviar', 'lyna-polska-royal-osetra-caviar'], dict(dx=9, dy=-4)),
    ('Romania', 'Romania', 45.9, 24.97, ['beluga-sterlet-bester-hybrid'], dict(dx=9, dy=2)),
    ('Bulgaria', 'Bulgaria', 42.7, 25.5, ['beluga-sevruga-hybrid'], dict(dx=9, dy=12)),
    ('Kibbutz Dan, Israel', 'Israel', 33.24, 35.65, ['karat-israeli-osetra-caviar'], dict(dx=9, dy=8)),
    ('Thousand Island Lake, Zhejiang', 'Thousand Island Lake', 29.6, 119.0, ['dynasty-royal-osetra-caviar', 'golden-dynasty-imperial-osetra-caviar', 'golden-dynasty-imperial-kaluga-hybrid-caviar'], dict(dx=-9, dy=10, anchor='end')),
    ('China (farm not named)', 'China', 36.0, 110.0, ['amber-dynasty-royal-kaluga-caviar', 'dynasty-siberian-caviar'], dict(dx=-9, dy=-2, anchor='end')),
    ('Northern China', 'Amur', 46.0, 127.5, ['dynasty-imperial-amur-sturgeon-caviar'], dict(dx=9, dy=-2)),
    ('Taiwan', 'Taiwan', 23.7, 121.0, ['genki-tobiko-caviar-flying-fish-roe'], dict(dx=9, dy=8)),
]
where = {h: o[0] for o in ORIGINS for h in o[4]}
missing = [p['handle'] for p in P if p['handle'] not in where]
assert not missing, missing

# species id per product: compare the Latin binomials named on both sides
BIN = lambda t: set(re.findall(r'\b([A-Z][a-z]+ [a-z]{3,})\b', t or ''))
SPECIES_BINS = [(s['id'], BIN(s['latin']) | BIN(s.get('taxonomy_note', '')) if False else BIN(s['latin'])) for s in SP.get('species', [])]
HYBRID_BINS = [(s['id'], BIN(s.get('parents', ''))) for s in SP.get('hybrids', [])]
def species_of(p):
    lat = p['species_latin'] or ''; b = BIN(lat)
    if '×' in lat or ' x ' in lat:
        for sid, hb in HYBRID_BINS:
            if hb and hb == b: return sid
        return None
    for sid, sb in SPECIES_BINS:
        if sb & b: return sid
    low = lat.lower()
    for key in ('exocoet', 'cornu', 'thunnus', 'mugil'):
        if key in low:
            return next((s['id'] for s in SP.get('species', []) if key in (s['latin'] + ' ' + s.get('family', '') + ' ' + s.get('common', '')).lower()), None)
    return None

def grain_cat(p):
    g = (p.get('grain_label') or '').lower()
    if re.search(r'exceptionally large|xxl|large|generous|plump|larger', g): return 'large'
    if 'small' in g: return 'small'
    if 'medium' in g: return 'medium'
    return None
def flv(p, *words): f = (p.get('flavor') or '').lower(); return any(w in f for w in words)
KIND_LABEL = {'sturgeon caviar': 'Sturgeon caviar', 'hybrid sturgeon caviar': 'Hybrid sturgeon caviar', 'roe': 'Roe', 'cured roe': 'Cured roe (bottarga)', 'snail caviar': 'Snail caviar'}
GROUP = lambda p: 'sturgeon' if 'sturgeon' in p['kind'] else ('cured' if p['kind'] == 'cured roe' else ('snail' if 'snail' in p['kind'] else ('paddlefish' if 'Polyodon' in (p['species_latin'] or '') else 'roe')))

spec_by = {s['id']: s for s in SP.get('species', []) + SP.get('hybrids', [])}
def rng(e):
    if isinstance(e, (int, float)): return [e, e]
    if isinstance(e, list) and e and all(isinstance(x, (int, float)) for x in e): return [min(e), max(e)]
    return None
def egg_range(sid):
    s = spec_by.get(sid) or {}
    r = rng(s.get('egg_diameter_mm'))
    if r or 'parents' not in s: return r
    # a hybrid with no published figure: the span of its two parents
    pr = [rng(x.get('egg_diameter_mm')) for x in SP.get('species', []) if BIN(x['latin']) & BIN(s['parents'])]
    pr = [x for x in pr if x]
    return [min(x[0] for x in pr), max(x[1] for x in pr)] if len(pr) == 2 else None

prods = []
for p in P:
    h = p['handle']; c = CAT[h]; sid = species_of(p)
    gm = p.get('grain_size_mm'); src = 'product'
    if isinstance(gm, list): gm = round(sum(gm) / len(gm), 2)
    if gm is None:
        er = egg_range(sid)
        if er:  # the species' typical egg size, pushed toward the top or bottom by the store's own grain words
            gc = grain_cat(p); t = {'large': .8, 'medium': .5, 'small': .2}.get(gc, .5)
            gm = round(er[0] + (er[1] - er[0]) * t, 2); src = 'species'
    avail = any(s.get('available') for s in p.get('sizes') or []) if p.get('sizes') else c['a']
    short = re.sub(r'\s*(Caviar|Roe)\b.*$', '', p['title']).strip() or p['title']
    short = re.sub(r'\s*\(.*?\)', '', short)
    prods.append({
        'h': h, 'title': p['title'], 'short': short if len(short) > 3 else p['title'], 'kind': p['kind'], 'kindLabel': KIND_LABEL.get(p['kind'], p['kind']),
        'group': GROUP(p), 'species': sid, 'species_latin': p['species_latin'], 'species_common': p['species_common'],
        'origin': ', '.join(x for x in [p.get('origin_region'), p.get('origin_country')] if x) if p.get('origin_region') and p.get('origin_country') and p['origin_country'] not in (p.get('origin_region') or '') else (p.get('origin_region') or p.get('origin_country')),
        'place': where[h], 'producer': p.get('producer'), 'wild': p.get('wild_or_farmed'),
        'grain_mm': gm, 'grain_src': src, 'grain_label': p.get('grain_label'), 'grain_cat': grain_cat(p),
        'color_words': p.get('color'), 'flavor': p.get('flavor'), 'texture': p.get('texture'), 'smoked': bool(p.get('smoked')),
        'sizes': p.get('sizes'), 'ppg': p.get('price_per_gram_usd'), 'quote': p.get('store_quote'), 'url': f'https://caviarstar.com/products/{h}',
        'available': avail, 'color': COL[h], 'k': SPEC[h]['kind'],
        'three': {k: c[k] for k in ('aspect', 'profile', 'color', 'flat', 'swing') if k in c},
        # quiz attributes
        'f_buttery': flv(p, 'butter', 'cream', 'mild', 'delicate', 'smooth'), 'f_nutty': flv(p, 'nut'),
        'f_briny': flv(p, 'brin', 'sea', 'ocean', 'salt'), 'f_bold': flv(p, 'earth', 'smok', 'spice', 'bold', 'robust', 'intense') or bool(p.get('smoked')),
        'sturgeon': 'sturgeon' in p['kind'], 'american_wild': (p.get('wild_or_farmed') == 'wild' and (p.get('origin_country') or '').startswith('USA')),
        'redgold': p['kind'] == 'roe' and not 'Polyodon' in (p['species_latin'] or '') and not 'Amia' in (p['species_latin'] or ''),
        'osetra_kaluga': bool(re.search(r'gueldenstaedtii|dauricus|huso', p['species_latin'] or '')),
        'quizable': p['kind'] not in ('cured roe',),
    })
byh = {p['h']: p for p in prods}

# species plates: attach products, normalise numbers
species = []
for s in SP.get('species', []) + [dict(h, common=h.get('common'), latin=h.get('parents', ''), hybrid=True) for h in SP.get('hybrids', [])]:
    sold = [p['h'] for p in prods if p['species'] == s['id']]
    iu = s.get('iucn_status') or {}
    if isinstance(iu, dict): code, yr = iu.get('code'), iu.get('assessed')
    else:
        code = next((c for c in ('CR', 'EN', 'VU', 'NT', 'LC', 'DD') if re.search(rf'\b{c}\b', iu)), None); m = re.search(r'(19|20)\d\d', iu); yr = m.group(0) if m else None
    mat = s.get('female_age_at_maturity_years')
    if isinstance(mat, (int, float)): mat = [mat, mat]
    species.append({'id': s['id'], 'common': s.get('common'), 'latin': s.get('latin'), 'hybrid': s.get('hybrid', False),
                    'native_range': s.get('native_range') or s.get('why_farmed'), 'map_points': s.get('map_points'),
                    'max_length_m': s.get('max_length_m'), 'maturity': mat if isinstance(mat, list) and all(isinstance(x, (int, float)) for x in mat) else None,
                    'egg': egg_range(s['id']), 'iucn_code': code if not s.get('hybrid') else 'HY', 'iucn_year': yr,
                    'one_fact': s.get('one_fact') or s.get('why_farmed'), 'products': sold, 'parent_of': []})
# a pure species that only reaches the shop through a hybrid still gets its plate, as a parent
for hy in SP.get('hybrids', []):
    hp = next((x for x in species if x['id'] == hy['id']), None)
    if not hp or not hp['products']: continue
    for x in species:
        if not x['hybrid'] and BIN(x['latin']) & BIN(hy.get('parents', '')): x['parent_of'].append(hy['id'])
# biggest, oldest fish first; species with no product in the shop are dropped on the page
species.sort(key=lambda s: (-(s['max_length_m'] or 0)))

def year_title(t):
    m = re.match(r'^(Today|\d{4})\s*:\s*(.*)$', t)
    return (m.group(1), m.group(2)) if m else ('', t)
hist = []
for h in G['history_market']:
    y, t = year_title(h['title']); hist.append({'year': y or '·', 'title': t, 'text': h['text'], 'source': h.get('source')})

def rule(attr, op, value, w): return {'attr': attr, 'op': op, 'value': value, 'w': w}
QUIZ = [
    {'q': 'What would you like to spend per ounce?', 'options': [
        {'label': 'Under $40', 'rules': [rule('ppg', '<', 1.41, 3)]},
        {'label': '$40 to $100', 'rules': [rule('ppg', 'between', [1.41, 3.53], 3)]},
        {'label': '$100 to $140', 'rules': [rule('ppg', 'between', [3.53, 4.94], 3)]},
        {'label': '$140 and up', 'rules': [rule('ppg', '>', 4.94, 3)]}]},
    {'q': 'Which taste sounds best?', 'options': [
        {'label': 'Buttery and mild', 'rules': [rule('f_buttery', '=', True, 2), rule('f_bold', '=', True, -1)]},
        {'label': 'Nutty and complex', 'rules': [rule('f_nutty', '=', True, 2)]},
        {'label': 'Briny, like the sea', 'rules': [rule('f_briny', '=', True, 2)]},
        {'label': 'Bold, earthy or smoky', 'rules': [rule('f_bold', '=', True, 2)]}]},
    {'q': 'What kind of pearl do you like?', 'options': [
        {'label': 'Big, with a firm pop', 'rules': [rule('grain_cat', '=', 'large', 2)]},
        {'label': 'Medium and creamy', 'rules': [rule('grain_cat', '=', 'medium', 2)]},
        {'label': 'Small and delicate', 'rules': [rule('grain_cat', '=', 'small', 2)]},
        {'label': 'No preference', 'rules': []}]},
    {'q': 'What is it for?', 'options': [
        {'label': 'A gift', 'rules': [rule('sturgeon', '=', True, 1.5), rule('ppg', '>', 2.7, 1)]},
        {'label': 'A party', 'rules': [rule('ppg', '<', 2.2, 1.5), rule('group', 'in', ['sturgeon', 'paddlefish'], 1)]},
        {'label': 'A special dinner', 'rules': [rule('osetra_kaluga', '=', True, 1.5), rule('grain_cat', 'in', ['large', 'medium'], .5)]},
        {'label': 'Everyday and cooking', 'rules': [rule('group', 'in', ['roe', 'paddlefish'], 1.5), rule('ppg', '<', 1.41, 1)]}]},
    {'q': 'Which roe are you after?', 'options': [
        {'label': 'Sturgeon caviar', 'rules': [rule('sturgeon', '=', True, 3)]},
        {'label': 'American wild', 'rules': [rule('american_wild', '=', True, 3)]},
        {'label': 'Bright red and gold roes', 'rules': [rule('redgold', '=', True, 3)]},
        {'label': 'Surprise me', 'rules': []}]},
]
for p in prods: p['featuredBoost'] = (0 if p['available'] else -4) + (0.3 if p['h'] == 'golden-dynasty-imperial-kaluga-hybrid-caviar' else 0)

n_species = len({p['species'] for p in prods if p['species']})
countries = sorted({(p.get('origin_country') or '').split(',')[0].strip() for p in P if p.get('origin_country')})
pts = [p['grain_mm'] for p in prods if p['grain_mm']]
atlas = {
    'products': prods, 'species': species, 'speciesById': {s['id']: s for s in species},
    'origins': [{'label': o[0], 'short': o[1], 'lat': o[2], 'lon': o[3], 'products': o[4], **o[5]} for o in ORIGINS],
    'kinds': [{'id': 'sturgeon', 'label': 'Sturgeon'}, {'id': 'paddlefish', 'label': 'Paddlefish'}, {'id': 'roe', 'label': 'Salmon, trout and other roe'},
              {'id': 'cured', 'label': 'Bottarga'}, {'id': 'snail', 'label': 'Snail'}],
    'magnification': 9,  # chart pixels per millimetre
    'featured': 'golden-dynasty-imperial-kaluga-hybrid-caviar',
    'starters': ['golden-dynasty-imperial-osetra-caviar', 'american-paddlefish-caviar', 'american-salmon-caviar', 'lyna-polska-siberian-caviar'],
    'stats': [{'v': str(len(prods)), 'k': 'caviars and roes'}, {'v': str(len(countries)), 'k': 'countries'},
              {'v': str(n_species or len({p['species_latin'] for p in P})), 'k': 'species'}, {'v': f"{min(pts):g}–{max(pts):g} mm" if pts else '', 'k': 'pearl sizes'}],
    'quiz': QUIZ,
    'guide': {'serving': G['serving'], 'storage': G['storage'], 'words': G['words'], 'history_market': hist, 'caviar_star': G['caviar_star']},
    'links': [{'label': 'Shop Caviar Star', 'url': 'https://caviarstar.com/'},
              {'label': 'All 181 products in 3D', 'url': 'https://claude.ai/artifact/87AaN98Wi4vRq3A3uLWzBQ', 'ghost': True},
              {'label': 'The documentary', 'url': 'https://claude.ai/artifact/2wJNc9cizoLPydpDtW6P2d', 'ghost': True}],
    'credit': 'A concept by an independent designer for Caviar Star and Great Atlantic Trading. Facts come from caviarstar.com, the producers named, the IUCN Red List, CITES, the US Fish and Wildlife Service, FAO and published research; sources sit under each note. Grain sizes marked "species typical" use the species range where the shop gives no figure. Prices as listed on October 6, 2026. Not an official Caviar Star page.',
}
out = sys.argv[1] if len(sys.argv) > 1 else 'atlas/web'
os.makedirs(out, exist_ok=True)
json.dump(atlas, open(f'{out}/atlas.json', 'w'), separators=(',', ':'), ensure_ascii=False)
# page assets: the page, studio, brand textures, land map, posters and the 3D packs for the caviars
shutil.copy('atlas/web/index.html', f'{out}/index.html') if os.path.abspath(out) != os.path.abspath('atlas/web') else None
shutil.copy('web/studio.js', f'{out}/studio.js')
os.makedirs(f'{out}/brand', exist_ok=True)
for f in ('tin-lid.jpg', 'kaluga-disc.jpg'): shutil.copy(f'web/brand/{f}', f'{out}/brand/{f}')
shutil.copy('node_modules/world-atlas/land-110m.json', f'{out}/land-110m.json')
os.makedirs(f'{out}/posters', exist_ok=True)
files = ['index.html', 'atlas.json', 'studio.js', 'brand/tin-lid.jpg', 'brand/kaluga-disc.jpg', 'land-110m.json']
for p in prods:
    shutil.copy(f"web/posters/{p['h']}.webp", f"{out}/posters/{p['h']}.webp"); files.append(f"posters/{p['h']}.webp")
    for f in ('pack.jpg', 'pack.webp'):
        s = f"web/assets/{p['h']}/{f}"
        if os.path.exists(s):
            os.makedirs(f"{out}/assets/{p['h']}", exist_ok=True); shutil.copy(s, f"{out}/assets/{p['h']}/{f}"); files.append(f"assets/{p['h']}/{f}")
json.dump(files, open(f'{out}/_files.json', 'w'))
print('atlas', len(prods), 'products', len(species), 'species,', sum(1 for p in prods if p['grain_src'] == 'species'), 'species-typical grains,', len(files), 'files')
