#!/usr/bin/env python3
"""Narration per scene with Kokoro (af_heart). Sentence-level synthesis with natural pauses.
-> build/audio/<id>.wav and build/audio/durations.json"""
import json, re, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K = Kokoro('/opt/tts/kokoro-v1.0.onnx', '/opt/tts/voices-v1.0.bin')
SAY = [(r'(\d)\.(\d)', r'\1 point \2'), (r'\b1896\b', 'eighteen ninety-six'), (r'\bLeavitts\b', 'Levitts'), (r'\bLeavitt\b', 'Levitt'), (r'\buni\b', 'oonee'), (r'\bUni\b', 'Oonee'), (r'\bCITES\b', 'sigh-teez'),
       (r'\bNOAA\b', 'Noah'), (r'\bPrunier\b', 'Proon-yay'), (r'\bchoupique\b', 'shoe-peek'), (r'\bDeanna\b', 'Dee-anna'),
       (r'\bOcean Isle\b', 'Ocean Isle'), (r'\bBaerii\b', 'Bear-ee-eye'), (r'\bOsetra\b', 'Oh-set-ra'), (r'\bosetra\b', 'oh-set-ra')]
def say(t):
    for a, b in SAY: t = re.sub(a, b, t)
    return t
scenes = json.load(open('build/scenes.json'))
os.makedirs('build/audio', exist_ok=True)
dur = {}
SR = 24000
for s in scenes:
    out = f"build/audio/{s['id']}.wav"
    if not os.path.exists(out):
        parts = re.split(r'(?<=[.!?])\s+', s['narration'])
        chunks = []
        for p in parts:
            if not p.strip(): continue
            a, sr = K.create(say(p), voice='af_heart', speed=0.94, lang='en-us')
            chunks.append(a.astype(np.float32))
            gap = 0.42 if p.endswith('.') else 0.32
            chunks.append(np.zeros(int(sr * gap), np.float32))
        sf.write(out, np.concatenate(chunks), SR)
    d = sf.info(out).duration; dur[s['id']] = d
    print(s['id'], round(d, 1), flush=True)
json.dump(dur, open('build/audio/durations.json', 'w'), indent=1)
print('total', round(sum(dur.values()) / 60, 2), 'min')
