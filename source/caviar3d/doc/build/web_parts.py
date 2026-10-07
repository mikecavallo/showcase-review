"""Package a finished video for the web: re-encode, split into parts that fit an artifact's file limit,
and write per-part captions plus a manifest the player page reads.

    python3 tools/web_parts.py --video out/X.mp4 --timing build/timing.json --srt out/X.srt --out out/web/x [--max-mb 14]

Keyframes are forced at every scene start, so parts split cleanly on scene boundaries.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path


def ts(sec):
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", lines[1])
        if not m:
            continue
        g = list(map(int, m.groups()))
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        cues.append((a, b, "\n".join(lines[2:])))
    return cues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--timing", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-mb", type=float, default=14.0)
    ap.add_argument("--crf", type=int, default=24)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    timing = json.loads(Path(args.timing).read_text())
    segs = timing["segments"]
    starts = [s["start"] for s in segs]

    # 1) web encode with a keyframe at every segment start
    web = out / "_web.mp4"
    kf = ",".join(f"{t:.3f}" for t in starts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
                    "-maxrate", "1800k", "-bufsize", "3600k", "-pix_fmt", "yuv420p", "-force_key_frames", kf,
                    "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-movflags", "+faststart", str(web)], check=True)

    # 2) per-segment byte sizes, measured from packets
    pk = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "packet=pts_time,size", "-of", "csv=p=0", str(web)],
                        capture_output=True, text=True, check=True).stdout.split()
    sizes = [0.0] * len(segs)
    for line in pk:
        t, sz = line.split(",")[:2]
        if t in ("", "N/A"):
            continue
        k = max(i for i, s in enumerate(starts) if s <= float(t) + 1e-3) if float(t) >= starts[0] else 0
        sizes[k] += int(sz)

    # 3) greedy-pack whole segments into parts under the limit
    limit = args.max_mb * 1e6
    groups, cur, acc = [], [], 0.0
    for i, sz in enumerate(sizes):
        if cur and acc + sz > limit:
            groups.append(cur)
            cur, acc = [], 0.0
        cur.append(i)
        acc += sz
    if cur:
        groups.append(cur)

    cues = parse_srt(Path(args.srt).read_text())
    total = timing["total"]
    parts = []
    for p, g in enumerate(groups):
        a = segs[g[0]]["start"]
        b = segs[g[-1]]["start"] + segs[g[-1]]["dur"] if g[-1] < len(segs) - 1 else total
        name = f"part{p + 1}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", str(web), "-t", f"{b - a:.3f}", "-c", "copy",
                        "-avoid_negative_ts", "make_zero", "-movflags", "+faststart", str(out / name)], check=True)
        vtt = ["WEBVTT", ""]
        for (ca, cb, txt) in cues:
            if cb <= a or ca >= b:
                continue
            vtt += [f"{ts(max(0, ca - a))} --> {ts(min(b, cb) - a)}", txt, ""]
        (out / f"part{p + 1}.vtt").write_text("\n".join(vtt))
        mb = (out / name).stat().st_size / 1e6
        parts.append({"src": name, "vtt": f"part{p + 1}.vtt", "start": round(a, 3), "dur": round(b - a, 3), "mb": round(mb, 1)})
        print(f"{name}: {len(g)} segments, {(b - a) / 60:.1f} min, {mb:.1f} MB")
    web.unlink()

    scenes = []
    for s in segs:
        scenes.append({"id": s["id"], "kind": s["kind"], "chapter": s.get("chapterNum"), "chapterTitle": s.get("chapterTitle", ""),
                       "heading": s.get("heading", ""), "t": round(s["start"], 3)})
    (out / "manifest.json").write_text(json.dumps({"total": round(total, 3), "parts": parts, "scenes": scenes}, indent=1))


if __name__ == "__main__":
    main()
