#!/usr/bin/env python3
"""Cut every product photo out of its background (rembg isnet-general-use), trim, and save RGBA PNGs.
  python3 tools/cutout.py [handle ...]      -> work/cut/<handle>/NN.png
"""
import glob, os, sys, json
from PIL import Image
from rembg import new_session, remove
S = new_session('isnet-general-use')
P = json.load(open('src/products.json'))
handles = sys.argv[1:] or [p['handle'] for p in P]
for h in handles:
    os.makedirs(f'work/cut/{h}', exist_ok=True)
    for f in sorted(glob.glob(f'src/img/{h}/*')):
        out = f'work/cut/{h}/' + os.path.splitext(os.path.basename(f))[0] + '.png'
        if os.path.exists(out): continue
        im = Image.open(f).convert('RGB')
        im.thumbnail((1400, 1400))
        cut = remove(im, session=S, post_process_mask=True)
        bb = cut.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
        if bb: cut = cut.crop(bb)
        cut.save(out)
    print(h, flush=True)
