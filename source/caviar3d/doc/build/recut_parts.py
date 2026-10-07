#!/usr/bin/env python3
"""Re-encode the web parts from the master with frame-accurate cuts at the manifest's boundaries.
    python3 build/recut_parts.py <web dir>"""
import json, subprocess, sys
from pathlib import Path
d = Path(sys.argv[1]); m = json.loads((d / 'manifest.json').read_text())
for p in m['parts']:
    out = d / p['src']; tmp = d / ('_' + p['src'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{p['start']:.3f}", '-i', 'build/out/Great-Atlantic-documentary.mp4', '-t', f"{p['dur']:.3f}",
                    '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-preset', 'medium', '-crf', '25', '-maxrate', '1800k', '-bufsize', '3600k',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-ac', '1', '-movflags', '+faststart', str(tmp)], check=True)
    tmp.replace(out)
    dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out)], capture_output=True, text=True).stdout.strip()
    p['mb'] = round(out.stat().st_size / 1e6, 1); print(p['src'], p['dur'], dur, p['mb'], 'MB', flush=True)
(d / 'manifest.json').write_text(json.dumps(m, indent=1))
