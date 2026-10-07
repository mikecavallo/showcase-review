#!/usr/bin/env python3
"""Stage the gallery artifact (packed: one file per product + one poster per product). Prints files maps split
into publish batches of <=250 files: caviar-files-<n>.json"""
import json, os, shutil, sys
PUB = sys.argv[1]; root = os.path.join(PUB, 'caviar')
spec = json.load(open('work/spec.json'))
files = {}
def put(src, rel):
    dst = os.path.join(root, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst); files[rel] = 'caviar/' + rel
os.makedirs(root, exist_ok=True)
shutil.copy2('web/gallery.html', os.path.join(root, 'index.html'))
put('web/studio.js', 'studio.js'); put('web/catalog.json', 'catalog.json')
for f in ['tin-lid.jpg', 'kaluga-disc.jpg']: put(f'web/brand/{f}', f'brand/{f}')
for h, s in spec.items():
    k = s['kind']
    if k == 'lathe': put(f'web/assets/{h}/tex.jpg', f'assets/{h}/tex.jpg')
    elif k == 'relief': put(f'web/assets/{h}/pack.webp', f'assets/{h}/pack.webp')
    elif k == 'jar': put(f'web/assets/{h}/pack.jpg', f'assets/{h}/pack.jpg')
    if os.path.exists(f'web/posters/{h}.webp'): put(f'web/posters/{h}.webp', f'posters/{h}.webp')
items = list(files.items())
for n in range(0, len(items), 240):
    json.dump(dict(items[n:n + 240]), open(os.path.join(PUB, f'caviar-files-{n // 240}.json'), 'w'))
tot = sum(os.path.getsize(os.path.join(PUB, v)) for v in files.values())
print(len(files), 'files', round(tot / 1e6, 1), 'MB', (len(items) + 239) // 240, 'batches')
