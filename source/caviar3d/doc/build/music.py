#!/usr/bin/env python3
"""A quiet ambient score: slow pad chords with a soft piano-like pluck, generated (no samples).
  python3 build/music.py <seconds> <out.wav>"""
import sys, numpy as np, soundfile as sf
SR = 44100
secs = float(sys.argv[1]); out = sys.argv[2]
N = int(SR * secs); t = np.arange(N) / SR
rng = np.random.default_rng(7)
def note(f): return 440 * 2 ** ((f - 69) / 12)
# D minor color: Dm9, Bbmaj7, Fadd9, Cadd9 (midi), 8 s each
chords = [[50, 57, 62, 65, 69, 76], [46, 53, 58, 62, 65, 69], [41, 53, 57, 60, 65, 67], [48, 55, 60, 62, 67, 71]]
L = np.zeros(N); R = np.zeros(N)
seg = 8.0
for k in range(int(secs / seg) + 2):
    ch = chords[k % 4]; t0 = k * seg
    s0 = int(max(0, (t0 - 2) * SR)); s1 = int(min(N, (t0 + seg + 3) * SR))
    if s0 >= N: break
    tt = t[s0:s1] - t0
    env = np.clip((tt + 2) / 3.5, 0, 1) * np.clip((seg + 3 - tt) / 3.5, 0, 1)
    env = env * env * (3 - 2 * env)
    for j, m in enumerate(ch):
        f = note(m)
        det = 1 + rng.uniform(-0.002, 0.002)
        sig = (np.sin(2 * np.pi * f * det * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt + 1.3) + 0.12 * np.sin(2 * np.pi * 3 * f * tt + .7))
        sig *= 0.5 + 0.5 * np.sin(2 * np.pi * (0.07 + 0.013 * j) * tt + j)  # slow shimmer
        pan = (j / (len(ch) - 1)) * 0.8 + 0.1
        a = env * sig * (0.06 if m > 55 else 0.08)
        L[s0:s1] += a * (1 - pan); R[s0:s1] += a * pan
    # a soft pluck on the chord's fifth every other bar
    if k % 2 == 0:
        f = note(ch[3] + 12); p0 = int((t0 + 1.0) * SR); p1 = min(N, p0 + int(4 * SR))
        if p0 < N:
            pt = t[p0:p1] - t[p0]
            pl = np.sin(2 * np.pi * f * pt) * np.exp(-pt * 1.3) * 0.05
            L[p0:p1] += pl * .6; R[p0:p1] += pl * .4
# gentle lowpass + simple stereo reverb (comb delays)
from scipy.signal import lfilter
L = lfilter([0.12], [1, -0.88], L); R = lfilter([0.12], [1, -0.88], R)
for d, g in [(0.031, .35), (0.047, .3), (0.071, .25), (0.113, .2)]:
    n = int(d * SR); L[n:] += g * R[:-n]; R[n:] += g * L[:-n]
mx = max(np.abs(L).max(), np.abs(R).max()) or 1
fade = np.minimum(1, np.minimum(t / 4, (secs - t) / 6))
st = np.stack([L, R], 1) / mx * 0.5 * fade[:, None]
sf.write(out, st.astype(np.float32), SR)
print('music', secs)
