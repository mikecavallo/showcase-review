#!/usr/bin/env python3
"""Transcribe each narration clip and diff it against the script, to catch words the TTS voice garbles.
    python3 build/asr_check.py [ids...]  -> build/asr/report.txt"""
import json, re, sys, difflib
from faster_whisper import WhisperModel
M = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
S = json.load(open('build/scenes.json')); only = set(sys.argv[1:])
norm = lambda t: re.findall(r"[a-z0-9']+", t.lower().replace('-', ' '))
out = open('build/asr/report.txt', 'w')
for s in S:
    if only and s['id'] not in only: continue
    segs, _ = M.transcribe(f"build/audio/{s['id']}.wav", language='en', beam_size=5)
    heard = ' '.join(x.text.strip() for x in segs)
    a, b = norm(s['narration']), norm(heard)
    bad = [f"  script: {' '.join(a[i1:i2])!r}  heard: {' '.join(b[j1:j2])!r}" for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes() if op != 'equal']
    out.write(f"== {s['id']}\n{heard}\n" + '\n'.join(bad) + '\n\n'); out.flush()
    print(s['id'], len(bad), 'diffs', flush=True)
