#!/usr/bin/env python3
"""Stage the sale-ads page: <pub>/ads/ with index.html, ads.json, JPG stills and web-size videos.
    python3 ads/build_page.py <pub dir>"""
import json, os, subprocess, sys
from PIL import Image
pub = sys.argv[1]; out = f'{pub}/ads'; os.makedirs(f'{out}/img', exist_ok=True); os.makedirs(f'{out}/vid', exist_ok=True)
META = json.load(open('ads/data/ads_meta.json')); COPY = {p['handle']: p for p in json.load(open('ads/data/copy_final.json'))['products']}
coll = json.load(open('ads/data/copy_final.json'))['collection']
B = {b['handle']: b for b in json.load(open('ads/data/brief.json'))}
LIVE = json.load(open('ads/data/copy_live.json'))  # copy rewritten to match the offer each ad shows
FORMATS = [('9x16', 'Stories, Reels, TikTok', 1080, 1920), ('4x5', 'Feed', 1080, 1350), ('1x1', 'Square feed', 1080, 1080)]
def money(x): x = float(x); return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"
ads, files = [], ['ads.json']
for m in META:
    h = m['handle']; ad = m['ad']
    if h in COPY:
        p = COPY[h]; variants = [p['final']] + p['alternates']
        copy = next((v for v in variants if v['onimage_headline'] == ad['headline']), p['final'])
        rows = [{'size': r['size'].replace('oz', ' oz').replace('Default Title', 'Plate and spoon set'), 'price': money(r['price']), 'was': money(r['was'])} for r in B[h]['sale_variants']]
        title, url = B[h]['title'], B[h]['url']
    else:
        copy = coll['copy']; rows = [{'size': f"{i['label']} {i['size']}", 'price': money(i['price']), 'was': money(i['was'])} for i in ad['items']]
        title, url = 'Caviar on sale (collection)', 'https://caviarstar.com/'
    entry = {'id': h, 'title': title, 'url': url, 'headline': ad['headline'], 'sub': ad['sub'], 'badge': ' '.join(x for x in ad['badge'] if x),
             'rows': rows, 'copy': {k: LIVE.get(h, {}).get(k, copy.get(k, '')) for k in ('meta_primary', 'meta_headline', 'meta_description', 'tiktok_caption', 'story_hook')}, 'formats': []}
    for fmt, use, W, H in FORMATS:
        png = f'ads/out/{h}-{fmt}.png'
        if not os.path.exists(png): continue
        im = Image.open(png).convert('RGB'); im.thumbnail((720, 1280)); im.save(f'{out}/img/{h}-{fmt}.jpg', quality=84); files.append(f'img/{h}-{fmt}.jpg')
        f = {'fmt': fmt, 'use': use, 'img': f'img/{h}-{fmt}.jpg', 'w': W, 'h': H}
        mp4 = f'ads/out/{h}-{fmt}.mp4'
        if os.path.exists(mp4):
            dst = f'{out}/vid/{h}-{fmt}.mp4'
            if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(mp4):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', dst], check=True)
            f['vid'] = f'vid/{h}-{fmt}.mp4'; files.append(f['vid'])
        entry['formats'].append(f)
    ads.append(entry)
import shutil; shutil.copy('ads/page.html', f'{out}/index.html')
json.dump({'ads': ads, 'asof': 'October 6, 2026'}, open(f'{out}/ads.json', 'w'), separators=(',', ':'))
json.dump(files, open(f'{out}/_files.json', 'w'))
print(len(ads), 'ads,', len(files), 'files,', sum(os.path.getsize(f'{out}/{f}') for f in files) // 1_000_000, 'MB')
