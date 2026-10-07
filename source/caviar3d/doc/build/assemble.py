#!/usr/bin/env python3
"""Assemble the documentary: picture (build/video/*.mp4 in timeline order) + narration + score, plus captions.

    python3 build/assemble.py            -> build/out/Great-Atlantic-documentary.mp4, .srt, timing.json
"""
import json, re, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

B = Path('build'); OUT = B / 'out'; OUT.mkdir(exist_ok=True)
T = json.load(open(B / 'timeline.json'))
S = {s['id']: s for s in json.load(open(B / 'scenes.json'))}
SR = 48000
LEAD = 0.4  # narration starts this long after its scene

starts, t = [], 0.0
for s in T:
    starts.append(t); t += s['dur']
total = t
missing = [s['id'] for s in T if not (B / 'video' / f"{s['id']}.mp4").exists()]
if missing: raise SystemExit(f'missing scenes: {missing}')

# 1) picture
(B / 'concat.txt').write_text(''.join(f"file 'video/{s['id']}.mp4'\n" for s in T))
pic = OUT / '_picture.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(B / 'concat.txt'), '-c', 'copy', str(pic)], check=True)

# 2) narration bed
N = int((total + 1) * SR); voice = np.zeros(N, np.float32)
for s, a in zip(T, starts):
    if not s.get('audio'): continue
    x, sr = sf.read(s['audio'], dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = resample_poly(x, SR, sr).astype(np.float32)
    i = int((a + LEAD) * SR); j = min(N, i + len(x)); voice[i:j] += x[:j - i]
pk = np.abs(voice).max() or 1; voice *= 0.89 / pk  # about -1 dBFS peak

# 3) score, ducked under the voice
subprocess.run(['python3', str(B / 'music.py'), f'{total + 1:.2f}', str(B / '_music.wav')], check=True)
m, msr = sf.read(B / '_music.wav', dtype='float32')
if msr != SR: m = resample_poly(m, SR, msr, axis=0).astype(np.float32)
m = m[:N] if len(m) >= N else np.pad(m, ((0, N - len(m)), (0, 0)))
def movavg(x, n):  # centred moving average via cumulative sum (np.convolve is far too slow at this length)
    c = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)]); i = np.arange(len(x)); a = np.clip(i - n // 2, 0, len(x)); b = np.clip(i + n - n // 2, 0, len(x))
    return ((c[b] - c[a]) / np.maximum(1, b - a)).astype(np.float32)
win = int(0.05 * SR); env = np.sqrt(movavg(voice.astype(np.float64) ** 2, win))
talk = (env > 0.01).astype(np.float32)
k = int(0.6 * SR); talk = movavg(talk, k).clip(0, 1)  # soft attack and release
gain = 0.16 + (0.42 - 0.16) * (1 - talk)  # quiet bed under speech, lifts between lines and on chapter cards
mix = m * gain[:, None] + voice[:, None]
mix /= max(1.0, np.abs(mix).max() / 0.95)
sf.write(B / '_mix.wav', mix, SR)

# 4) captions: sentences timed by length across each narration clip
def stamp(x):
    h, r = divmod(x, 3600); mi, se = divmod(r, 60); return f"{int(h):02d}:{int(mi):02d}:{int(se):02d},{int(round((se % 1) * 1000)) % 1000:03d}"
cues = []
for s, a in zip(T, starts):
    if not s.get('audio'): continue
    d = sf.info(s['audio']).duration
    sents = [x.strip() for x in re.split(r'(?<=[.!?])\s+', S[s['id']]['narration']) if x.strip()]
    chunks = []
    for x in sents:  # split long sentences at commas so a cue stays readable
        if len(x) > 90 and ', ' in x:
            parts, cur = [], ''
            for p in x.split(', '):
                cur = f'{cur}, {p}' if cur else p
                if len(cur) > 45: parts.append(cur + ','); cur = ''
            if cur: parts.append(cur)
            parts[-1] = parts[-1].rstrip(',')
            chunks += parts
        else: chunks.append(x)
    L = sum(len(c) + 8 for c in chunks); u = a + LEAD
    for c in chunks:
        dd = d * (len(c) + 8) / L; cues.append((u, u + dd - 0.05, c)); u += dd
(OUT / 'Great-Atlantic-documentary.srt').write_text(''.join(f'{i + 1}\n{stamp(x)} --> {stamp(y)}\n{c}\n\n' for i, (x, y, c) in enumerate(cues)))

# 5) final
final = OUT / 'Great-Atlantic-documentary.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(pic), '-i', str(B / '_mix.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(final)], check=True)
pic.unlink()

# timing for tools/web_parts.py
segs = [{'id': s['id'], 'kind': 'scene' if not s['id'].startswith('ch') else 'card', 'start': round(a, 3), 'dur': s['dur'],
         'chapterNum': s['chapter'], 'chapterTitle': s['chapter_title'], 'heading': ''} for s, a in zip(T, starts)]
(OUT / 'timing.json').write_text(json.dumps({'total': round(total, 3), 'segments': segs}, indent=1))
print('done', final, f'{total / 60:.2f} min', len(cues), 'cues')
