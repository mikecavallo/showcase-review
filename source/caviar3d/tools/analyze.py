#!/usr/bin/env python3
"""Decide how each product becomes 3D, pick its best photo, and extract what the 3D builder needs.

kind:
  jar    caviar / roe shot top-down in a glass jar -> procedural glass jar filled with that caviar, branded lid
  tin    Caviar Star "OT" tins -> procedural black-and-gold tin
  lathe  bottles, jars, cans, round servers -> lathe-turned from the photo silhouette, wrapped in the photo
  relief everything else (spoons, shells, truffles, fish, gift sets) -> inflated mesh from the cutout

Writes work/spec.json and, per product, work/asset/<handle>/{tex.png, profile.json, disc.png}.
  python3 tools/analyze.py [handle ...]
"""
import glob, json, math, os, re, sys
import numpy as np, cv2
from PIL import Image

P = json.load(open('src/products.json'))
OVR = json.load(open('tools/overrides.json')) if os.path.exists('tools/overrides.json') else {}

NOT_JAR = re.compile(r'spoon|server|cloche|key|gift|box|bag|dish|palette|plate|fork|bowl|tin\b|tins\b', re.I)
LATHE = re.compile(r'\boil\b|vinegar|balsamic|glaze|juice|sauce|paste|butter|honey|flour|mustard|sherry|vincotto|saba|'
                   r'breakings|peelings|whole black summer|carpaccio|escargots|cheese|lobster oil|squid ink|pearls|cloche|'
                   r'insulated|top bowl|roll top|glass caviar serving|shot-glass', re.I)


def kind_of(p):
    t = p['title']
    if p['handle'] in OVR and 'kind' in OVR[p['handle']]: return OVR[p['handle']]['kind']
    if '"OT"' in t or 'OT Gift' in t: return 'tin'
    if re.search(r'caviar|roe|tobiko', t, re.I) and not NOT_JAR.search(t): return 'jar'
    if re.search(r'gift box|gift bag|decorative box|gift certificate|chocolate', t, re.I): return 'relief'
    if LATHE.search(t) and not re.search(r'spoon|fork|slicer|sea salt', t, re.I): return 'lathe'
    return 'relief'


def comps(alpha):
    a = (alpha > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(a, 8)
    areas = sorted([st[i, cv2.CC_STAT_AREA] for i in range(1, n)], reverse=True)
    tot = sum(areas) or 1
    big = [x for x in areas if x > tot * 0.04]
    return len(big), (areas[0] / tot if areas else 0)


def symmetry(alpha):
    a = (alpha > 128)
    rows = np.where(a.any(1))[0]
    if len(rows) < 20: return 0, None
    L, R = [], []
    for y in rows:
        xs = np.where(a[y])[0]; L.append(xs[0]); R.append(xs[-1])
    L, R = np.array(L, float), np.array(R, float)
    c = (L + R) / 2; w = (R - L)
    # a turned object has a steady centre line; score = how little the centre wanders vs the width
    return float(1 - np.clip(np.std(c) / (np.median(w) + 1e-6), 0, 1)), (rows, L, R)


def cropped(handle, idx):
    """True when the product runs off the edge of the source photo (a close-up), so the cutout has a chopped side."""
    fs = glob.glob(f"src/img/{handle}/{idx:02d}.*")
    if not fs: return False
    im = Image.open(fs[0]).convert('RGB'); im.thumbnail((400, 400)); a = np.asarray(im).astype(np.int16)
    bg = np.median(np.concatenate([a[:4, :4].reshape(-1, 3), a[:4, -4:].reshape(-1, 3), a[-4:, :4].reshape(-1, 3), a[-4:, -4:].reshape(-1, 3)]), 0)
    far = lambda e: (np.abs(e - bg).sum(-1) > 60).mean()
    return max(far(a[0]), far(a[-1]), far(a[:, 0]), far(a[:, -1])) > 0.06


def pick(p, kind):
    best = None
    for f in sorted(glob.glob(f"work/cut/{p['handle']}/*.png")):
        im = Image.open(f); a = np.array(im.getchannel('A'))
        h, w = a.shape
        if h < 80 or w < 40: continue
        nc, dom = comps(a)
        sym, _ = symmetry(a)
        fill = (a > 128).mean()
        s = 0.0
        if kind == 'lathe': s = 2 * sym + (1.2 if nc == 1 else 0) + 0.6 * dom + 0.3 * min(h / w, 4) / 4
        elif kind == 'jar': s = 1.0 * (1 - abs(w / h - 1)) + 0.5 * fill + (0.5 if nc == 1 else 0)
        else: s = (1.0 if nc == 1 else 0.3) + 0.5 * dom + 0.3 * fill
        s += 0.15 * min(1, (h * w) / 6e5)
        idx = int(os.path.basename(f)[:2])
        s -= 0.04 * idx  # the store's first photo is usually the hero
        if kind == 'relief' and cropped(p['handle'], idx): s -= 1.5  # never a photo that cuts the product off
        if best is None or s > best[0]: best = (s, f, sym, nc)
    if p['handle'] in OVR and 'img' in OVR[p['handle']]:
        f = f"work/cut/{p['handle']}/{OVR[p['handle']]['img']:02d}.png"
        best = (9, f, 0, 0)
    return best


def lathe_profile(im, out):
    a = np.array(im.getchannel('A')).astype(np.float32)
    # keep only the largest component so a second bottle in the shot does not widen the profile
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8), 8)
    if n > 2:
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        x, y, w, h = st[k, :4]
        im = im.crop((x, y, x + w, y + h)); a = np.array(im.getchannel('A')).astype(np.float32)
        m = (lab[y:y + h, x:x + w] == k)
        a = a * m
        arr = np.array(im); arr[..., 3] = a.astype(np.uint8); im = Image.fromarray(arr)
    H, W = a.shape
    rows = np.arange(H); L = np.full(H, np.nan); R = np.full(H, np.nan)
    for y in rows:
        xs = np.where(a[y] > 128)[0]
        if len(xs): L[y], R[y] = xs[0], xs[-1] + 1
    ok = ~np.isnan(L)
    c = np.nanmedian((L + R) / 2)
    r = np.where(ok, np.maximum(c - L, R - c), 0)  # symmetric radius about the median centre
    r = np.where(ok, np.minimum(r, np.nan_to_num((R - L) / 2) * 1.06 + 1), 0)
    # smooth, sample 120 rows
    k = max(3, H // 120) | 1
    r = cv2.GaussianBlur(r.reshape(-1, 1), (1, k), 0).ravel()
    ys = np.linspace(0, H - 1, 140).astype(int)
    prof = [[float(r[y] / H), float(1 - y / H)] for y in ys]  # radius, height as fractions of image height
    # wrap texture: unwrap front half by sampling x = c + r sin(theta)
    img = np.array(im.convert('RGBA')).astype(np.float32)
    TW, TH = 1024, min(1024, int(1024 * H / max(W, 1)))
    TH = max(256, TH)
    tex = np.zeros((TH, TW, 4), np.float32)
    th = (np.arange(TW) + .5) / TW * 2 * np.pi - np.pi  # -pi..pi, 0 = facing camera
    for j in range(TH):
        y = int(j / TH * H)
        rr = r[y]
        if rr <= 0: continue
        front = np.abs(th) <= np.pi / 2
        s = np.where(front, np.sin(th), np.sin(np.pi - np.abs(th)) * np.sign(th) * -1)
        x = np.clip(c + rr * s * 0.995, 0, W - 1)
        x0 = np.floor(x).astype(int); x1 = np.minimum(x0 + 1, W - 1); f = (x - x0)[:, None]
        tex[j] = img[y, x0] * (1 - f) + img[y, x1] * f
    # back half: the mirrored front, softened and dimmed so text never reads backwards
    back = ~(np.abs(th) <= np.pi / 2)
    blur = cv2.GaussianBlur(tex, (0, 0), 9)
    tex[:, back] = blur[:, back] * np.array([.82, .82, .82, 1])
    tex[..., 3] = 255
    Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8)).convert('RGB').save(out + '/tex.jpg', quality=88)
    json.dump({'profile': prof, 'aspect': W / H}, open(out + '/profile.json', 'w'))
    im.save(out + '/cut.webp', quality=88, method=6)


def jar_disc(im, out):
    # find the round glass jar seen from above; keep the caviar inside the rim
    rgb = np.array(im.convert('RGB')); a = np.array(im.getchannel('A'))
    H, W = a.shape
    cnts, _ = cv2.findContours((a > 128).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    (cx, cy), R = cv2.minEnclosingCircle(c)
    # caviar sits inside the glass wall: pick the radius where the mean saturation/darkness settles
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]; d = np.hypot(xx - cx, yy - cy) / R
    prof = []
    for t in np.linspace(.4, 1, 31):
        ring = (d > t - .02) & (d < t + .02)
        prof.append(g[..., 1][ring].mean() if ring.any() else 0)
    prof = np.array(prof); inner = .4
    base = prof[:8].mean()
    for t, v in zip(np.linspace(.4, 1, 31), prof):
        if v < base * .72: break
        inner = t
    r_in = max(.55, min(.9, inner - .02)) * R
    S = 1024
    M = np.float32([[S / (2 * r_in), 0, S / 2 - cx * S / (2 * r_in)], [0, S / (2 * r_in), S / 2 - cy * S / (2 * r_in)]])
    disc = cv2.warpAffine(rgb, M, (S, S), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    Image.fromarray(disc).save(out + '/disc.jpg', quality=90)
    # the caviar's average colour, for the jar wall and pearls
    yy, xx = np.mgrid[0:S, 0:S]; m = np.hypot(xx - S / 2, yy - S / 2) < S * .45
    col = disc[m].mean(0) / 255
    json.dump({'rin': r_in / R, 'color': col.tolist()}, open(out + '/jar.json', 'w'))


def relief_prep(im, out):
    a = np.array(im.getchannel('A'))
    H, W = a.shape
    s = min(1, 1400 / max(H, W)); im = im.resize((max(1, int(W * s)), max(1, int(H * s))), Image.LANCZOS)
    # pull the edge in a pixel and bleed edge colour into the transparent area, so texture filtering at the
    # silhouette never picks up the old white background (the light fringe on cutouts)
    arr = np.array(im).astype(np.float32); a = cv2.erode(arr[..., 3], np.ones((3, 3), np.uint8))
    rgb, w = arr[..., :3] * (a[..., None] / 255), a / 255
    fill = rgb.copy(); acc = w.copy()
    for sg in (2, 6, 18):
        num = cv2.GaussianBlur(rgb, (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)[..., None]
        m = (acc < 0.5)[..., None]; fill = np.where(m & (den > 1e-3), num / np.maximum(den, 1e-3), fill); acc = np.maximum(acc, (den[..., 0] > 1e-3).astype(np.float32))
    out_rgb = np.where((w > 0.5)[..., None], arr[..., :3], fill)
    im = Image.fromarray(np.dstack([np.clip(out_rgb, 0, 255), a]).astype(np.uint8), 'RGBA')
    a = np.array(im.getchannel('A'))
    d = cv2.distanceTransform((a > 128).astype(np.uint8), cv2.DIST_L2, 5)
    dm = d.max() or 1
    h = np.sqrt(np.clip(d / dm, 0, 1))  # rounded bulge
    h = cv2.GaussianBlur(h, (0, 0), 2)
    Image.fromarray((h * 255).astype(np.uint8)).save(out + '/height.png')
    im.save(out + '/cut.webp', quality=88, method=6)
    json.dump({'aspect': im.width / im.height}, open(out + '/relief.json', 'w'))


def main():
    handles = set(sys.argv[1:])
    spec = json.load(open('work/spec.json')) if os.path.exists('work/spec.json') else {}
    for p in P:
        h = p['handle']
        if handles and h not in handles: continue
        if not glob.glob(f'work/cut/{h}/*.png'): continue
        k = kind_of(p)
        b = pick(p, k)
        if not b: continue
        out = f'web/assets/{h}'; os.makedirs(out, exist_ok=True)
        im = Image.open(b[1]).convert('RGBA')
        try:
            if k == 'lathe': lathe_profile(im, out)
            elif k == 'jar': jar_disc(im, out)
            if k in ('relief', 'tin', 'jar'): relief_prep(im, out)
        except Exception as e:
            print('fail', h, e); k = 'relief'; relief_prep(im, out)
        v = p['variants'][0]
        spec[h] = {'title': p['title'], 'kind': k, 'img': b[1], 'sym': round(b[2], 3), 'price': v['price'],
                   'available': any(x.get('available') for x in p['variants']), 'url': f"https://caviarstar.com/products/{h}"}
        for key in ('flat', 'swing'):
            if key in OVR.get(h, {}): spec[h][key] = OVR[h][key]
        print(k.ljust(6), h)
    json.dump(spec, open('work/spec.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
