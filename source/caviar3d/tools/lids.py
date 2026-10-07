#!/usr/bin/env python3
"""Per-product jar lids: the real Caviar Star star lid with the product's own name in place of KALUGA CAVIAR.
Third-party brands get a plain black lid. -> web/assets/<handle>/lid.jpg"""
import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
NAMES = {
 'classic-california-white-sturgeon-caviar': 'WHITE STURGEON CAVIAR', 'dynasty-siberian-caviar': 'SIBERIAN CAVIAR',
 'albino-almas-caviar': 'ALBINO STERLET', 'beluga-sevruga-hybrid': 'BELUGA SEVRUGA', 'classic-italian-white-sturgeon-caviar': 'WHITE STURGEON CAVIAR',
 'smoked-american-salmon-caviar': 'SMOKED SALMON ROE', 'beluga-sterlet-bester-hybrid': 'BELUGA BESTER CAVIAR', 'white-escargot-snail-caviar': 'SNAIL CAVIAR',
 'supreme-california-white-sturgeon-caviar': 'WHITE STURGEON CAVIAR', 'smoked-golden-whitefish-caviar': 'SMOKED WHITEFISH ROE',
 'dynasty-imperial-amur-sturgeon-caviar': 'AMUR STURGEON CAVIAR', 'amber-dynasty-royal-kaluga-caviar': 'KALUGA CAVIAR',
 'dynasty-royal-osetra-caviar': 'OSETRA CAVIAR', 'golden-dynasty-imperial-osetra-caviar': 'IMPERIAL OSETRA',
 'royal-california-white-sturgeon-caviar': 'WHITE STURGEON CAVIAR', 'golden-whitefish-roe': 'GOLDEN WHITEFISH ROE',
 'american-salmon-caviar': 'SALMON ROE', 'american-bowfin-caviar': 'BOWFIN ROE', 'american-hackleback-sturgeon-caviar': 'HACKLEBACK CAVIAR',
 'american-paddlefish-caviar': 'PADDLEFISH CAVIAR', 'rainbow-trout-roe': 'RAINBOW TROUT ROE', 'bourbon-barrel-smoked-trout-roe': 'SMOKED TROUT ROE',
 'golden-dynasty-imperial-kaluga-hybrid-caviar': 'KALUGA CAVIAR',
}
PLAIN = ['dieckmann-hansen-reserve-german-osetra-caviar', 'caviar-house-prunier-osetra-caviar', 'genki-tobiko-caviar-flying-fish-roe',
         'lyna-polska-royal-osetra-caviar', 'lyna-polska-siberian-caviar', 'karat-israeli-osetra-caviar']
base = cv2.imread('web/brand/lid-kaluga.jpg'); S = base.shape[0]
hsv = cv2.cvtColor(base, cv2.COLOR_BGR2HSV)
mask = np.zeros((S, S), np.uint8)
for (x0, y0, x1, y1) in [(322, 458, 700, 532), (474, 672, 584, 746)]:
    reg = (hsv[y0:y1, x0:x1, 2] > 105) & (hsv[y0:y1, x0:x1, 1] < 140)
    mask[y0:y1, x0:x1] = reg.astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
clean = cv2.inpaint(base, mask, 9, cv2.INPAINT_TELEA)
cv2.imwrite('web/brand/lid-blank.jpg', clean, [cv2.IMWRITE_JPEG_QUALITY, 90])
font = ImageFont.truetype('tools/oswald.woff2', 80)
for h, name in NAMES.items():
    im = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im)
    size = 74
    while size > 30:
        font = ImageFont.truetype('tools/oswald.woff2', size)
        w = d.textlength(name, font=font)
        if w < 400: break
        size -= 4
    d.text((511, 494), name, font=font, fill=(233, 226, 196), anchor='mm')
    os.makedirs(f'web/assets/{h}', exist_ok=True); im.save(f'web/assets/{h}/lid.jpg', quality=90)
# plain lid
pl = np.full((S, S, 3), (16, 15, 17), np.uint8)
yy, xx = np.mgrid[0:S, 0:S]; d = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
pl[(d > 0.9) & (d < 0.92)] = (60, 110, 150)
for h in PLAIN:
    os.makedirs(f'web/assets/{h}', exist_ok=True); cv2.imwrite(f'web/assets/{h}/lid.jpg', pl)
print('lids', len(NAMES), len(PLAIN))
