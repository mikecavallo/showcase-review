#!/usr/bin/env python3
"""Replace frame ranges of a rendered reel with re-rendered pieces (from render_reel.mjs <w> <h> <piece> <from> <to>).

    python3 build/splice_reel.py <reel.mp4> <out.mp4> <from>:<to>:<piece.mp4> [...]
Frames are counted from 0; <to> is exclusive. Re-encodes once with the reel's own settings (H.264 CRF 18, 24 fps)."""
import subprocess, sys
src, out, *parts = sys.argv[1:]
parts = sorted((int(a), int(b), p) for a, b, p in (x.split(':', 2) for x in parts))
n = int(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', src]).strip())
inputs, chains, labels, cur = ['-i', src], [], [], 0
for k, (a, b, p) in enumerate(parts, 1):
    if a > cur:
        chains.append(f'[0:v]trim=start_frame={cur}:end_frame={a},setpts=PTS-STARTPTS[s{k}]'); labels.append(f'[s{k}]')
    inputs += ['-i', p]; chains.append(f'[{k}:v]trim=end_frame={b - a},setpts=PTS-STARTPTS[p{k}]'); labels.append(f'[p{k}]'); cur = b
if cur < n:
    chains.append(f'[0:v]trim=start_frame={cur},setpts=PTS-STARTPTS[tail]'); labels.append('[tail]')
fc = ';'.join(chains) + ';' + ''.join(labels) + f'concat=n={len(labels)}:v=1:a=0[v]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[v]', '-r', '24', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], check=True)
m = int(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', out]).strip())
print(out, m, 'frames (source', n, ')'); assert m == n, 'frame count changed'
