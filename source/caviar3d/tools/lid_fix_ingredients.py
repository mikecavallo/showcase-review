#!/usr/bin/env python3
"""Regenerate the generated lids of non-sturgeon products without the "INGREDIENTS: STURGEON ROE AND SEA SALT" line.
Fits the text arc to the white letter pixels themselves, then inpaints only those letters (and the word PERISHABLE: so
no fragment is left), leaving the gold dot field alone.   python3 tools/lid_fix_ingredients.py"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
NAMES = {'smoked-golden-whitefish-caviar': 'SMOKED WHITEFISH ROE', 'golden-whitefish-roe': 'GOLDEN WHITEFISH ROE', 'smoked-american-salmon-caviar': 'SMOKED SALMON ROE',
         'american-bowfin-caviar': 'BOWFIN ROE', 'rainbow-trout-roe': 'RAINBOW TROUT ROE', 'bourbon-barrel-smoked-trout-roe': 'SMOKED TROUT ROE'}
blank = cv2.imread('web/brand/lid-blank.jpg'); hsv = cv2.cvtColor(blank, cv2.COLOR_BGR2HSV)
yy, xx = np.mgrid[0:1024, 0:1024]
# the rim text runs on a ring 340 to 370 px from the lid centre; the ingredients line and the word PERISHABLE:
# span roughly 8 o'clock to 1 o'clock
r = np.hypot(xx - 512, yy - 512); ang = np.degrees(np.arctan2(yy - 512, xx - 512))
sector = (r > 328) & (r < 382) & ((ang <= -112.5) | (ang >= 172))
m = cv2.dilate((sector & (hsv[..., 2] > 95) & (hsv[..., 1] < 70)).astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(blank, m, 6, cv2.INPAINT_TELEA)
print('masked', int(m.sum() / 255))
for h, name in NAMES.items():
    im = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im); size = 74
    while size > 30:
        font = ImageFont.truetype('tools/oswald.woff2', size)
        if d.textlength(name, font=font) < 400: break
        size -= 4
    d.text((511, 494), name, font=font, fill=(233, 226, 196), anchor='mm'); im.save(f'web/assets/{h}/lid.jpg', quality=90)
Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)).crop((0, 0, 1024, 620)).resize((820, 496)).save('/tmp/claude-0/gat/lidfix.jpg')
