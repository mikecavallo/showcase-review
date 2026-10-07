#!/usr/bin/env python3
"""Cut a product off a plain white background by colour distance (for photos where rembg keeps only the label).
    python3 tools/whitecut.py <handle> <idx>  -> overwrites work/cut/<handle>/<idx>.png"""
import sys, glob, numpy as np, cv2
from PIL import Image
h, idx = sys.argv[1], int(sys.argv[2])
src = glob.glob(f'src/img/{h}/{idx:02d}.*')[0]
rgb = np.asarray(Image.open(src).convert('RGB')).astype(np.int16)
m = (np.abs(rgb - 252).max(-1) > 14).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); m = (lab == k).astype(np.uint8)
# fill interior holes (white labels inside the object)
ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 1); m = m | (1 - ff)
m = cv2.erode(m, np.ones((3, 3), np.uint8))
a = cv2.GaussianBlur(m.astype(np.float32) * 255, (0, 0), 1.2)
x, y, w, hh = cv2.boundingRect(m)
out = np.dstack([rgb.astype(np.uint8), a.astype(np.uint8)])[y:y + hh, x:x + w]
Image.fromarray(out, 'RGBA').save(f'work/cut/{h}/{idx:02d}.png'); print(h, idx, w, hh)
