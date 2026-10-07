#!/usr/bin/env python3
"""Stage the turntable library for publishing: <pub>/turntables/ plus publish batches (<=240 files, <=60 MB each).
    python3 tools/stage_turntables.py <pub dir>"""
import json, os, shutil, sys
pub = sys.argv[1]; out = f'{pub}/turntables'
for d in ('posters', 'turntable'): os.makedirs(f'{out}/{d}', exist_ok=True)
cat = json.load(open('web/catalog.json'))
OLD = os.environ.get('TT_FALLBACK', '')  # older renders to use for loops still being re-rendered
src = lambda h: f'out/turntable/{h}.mp4' if os.path.exists(f'out/turntable/{h}.mp4') else f'{OLD}/{h}.mp4'
have = [c['h'] for c in cat if os.path.exists(src(c['h']))]
shutil.copy('web/turntables.html', f'{out}/index.html')
slim = [{k: c[k] for k in ('h', 't', 'c', 'p', 'a', 'u')} for c in cat]
json.dump(slim, open(f'{out}/catalog.json', 'w'), separators=(',', ':'))
json.dump(have, open(f'{out}/turntables.json', 'w'))
files = ['catalog.json', 'turntables.json']
for h in have:
    shutil.copy(f'web/posters/{h}.webp', f'{out}/posters/{h}.webp'); shutil.copy(src(h), f'{out}/turntable/{h}.mp4')
    files += [f'posters/{h}.webp', f'turntable/{h}.mp4']
batches, cur, size = [], {}, 0
for f in files:
    s = os.path.getsize(f'{out}/{f}')
    if cur and (len(cur) >= 240 or size + s > 60e6): batches.append(cur); cur, size = {}, 0
    cur[f] = f'turntables/{f}'; size += s
if cur: batches.append(cur)
for i, b in enumerate(batches): json.dump(b, open(f'{pub}/turntables-files-{i}.json', 'w'))
print(len(have), 'turntables,', len(files), 'files,', len(batches), 'batches', [len(b) for b in batches])
