#!/usr/bin/env python3
"""One file per product for publishing: relief -> pack.webp (colour+alpha | height), jar -> pack.jpg (caviar | lid),
posters -> web/posters/<h>.webp (angle a | angle b). Embeds the small JSON into web/catalog.json."""
import json, os
from PIL import Image
spec = json.load(open('work/spec.json'))
cat = json.load(open('web/catalog.json'))
os.makedirs('web/posters', exist_ok=True)
for it in cat:
    h = it['h']; k = spec[h]['kind']; a = f'web/assets/{h}'
    it['packed'] = True
    for key in ('flat', 'swing'):
        if key in spec[h]: it[key] = spec[h][key]
        else: it.pop(key, None)
    if k == 'lathe':
        it['profile'] = [[round(r, 4), round(y, 4)] for r, y in json.load(open(f'{a}/profile.json'))['profile']]
    elif k == 'relief':
        cut = Image.open(f'{a}/cut.webp').convert('RGBA'); hm = Image.open(f'{a}/height.png').convert('L').resize(cut.size)
        pk = Image.new('RGBA', (cut.width * 2, cut.height), (0, 0, 0, 0)); pk.paste(cut, (0, 0))
        pk.paste(Image.merge('RGBA', (hm, hm, hm, Image.new('L', hm.size, 255))), (cut.width, 0))
        pk.save(f'{a}/pack.webp', quality=86, method=5)
        it['aspect'] = json.load(open(f'{a}/relief.json'))['aspect']
    elif k == 'jar':
        d = Image.open(f'{a}/disc.jpg').convert('RGB').resize((1024, 1024)); l = Image.open(f'{a}/lid.jpg').convert('RGB').resize((1024, 1024))
        pk = Image.new('RGB', (2048, 1024)); pk.paste(d, (0, 0)); pk.paste(l, (1024, 0)); pk.save(f'{a}/pack.jpg', quality=86)
        it['color'] = json.load(open(f'{a}/jar.json'))['color']
    pa, pb = f'work/posters/{h}-a.png', f'work/posters/{h}-b.png'
    if os.path.exists(pb):
        A = Image.open(pa).convert('RGB').resize((480, 480)); B = Image.open(pb).convert('RGB').resize((480, 480))
        P = Image.new('RGB', (960, 480)); P.paste(A, (0, 0)); P.paste(B, (480, 0)); P.save(f'web/posters/{h}.webp', quality=80, method=5)
json.dump(cat, open('web/catalog.json', 'w'), separators=(',', ':'))
print('packed', len(cat), os.path.getsize('web/catalog.json') // 1024, 'KB catalog')
