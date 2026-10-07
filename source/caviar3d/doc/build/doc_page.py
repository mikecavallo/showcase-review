#!/usr/bin/env python3
"""Screening-room page for the documentary (parts from web_parts.py) plus the two 3D reels.

    python3 build/doc_page.py --dir <web dir> --gallery <url>
"""
import argparse, html, json, re
from pathlib import Path

PAGE = r"""<title>From the Docks to the Tin</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap">
<style>
/* One committed look: the brand's screening room, black and gold. */
:root {
  color-scheme: dark;
  --bg: #07080c; --panel: #0e1016; --ink: #efe8da; --muted: #a69c8a; --gold: #d9b871; --gold-deep: #9c7536;
  --line: rgba(217, 184, 113, .18);
  --display: "Cinzel", "Trajan Pro", Georgia, serif; --serif: "Cormorant Garamond", Garamond, Georgia, serif;
}
* { box-sizing: border-box; }
html, body { background: var(--bg); color: var(--ink); }
body { margin: 0; font: 500 19px/1.5 var(--serif); }
a { color: var(--gold); }
:focus-visible { outline: 1px solid var(--gold); outline-offset: 3px; }
.wrap { max-width: 1320px; margin: 0 auto; padding: clamp(28px, 6vh, 64px) clamp(16px, 4vw, 48px) 56px; display: grid; gap: 28px; }
header { display: grid; gap: 10px; justify-items: center; text-align: center; }
.kicker { font: 500 13px/1 var(--display); letter-spacing: .42em; text-transform: uppercase; color: var(--muted); }
h1 { margin: 0; font: 500 clamp(32px, 5vw, 64px)/1.06 var(--display); letter-spacing: .08em; text-wrap: balance;
  background: linear-gradient(180deg, #f6e7b8 0%, #d9b871 55%, #9c7536 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.rule { width: 220px; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.sub { margin: 0; max-width: 46em; font-style: italic; color: var(--ink); font-size: 21px; }
.meta { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
.chip { padding: 5px 14px; border: 1px solid var(--line); font: 500 12px/1.6 var(--display); letter-spacing: .18em; text-transform: uppercase; color: var(--muted); }
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 24px; align-items: start; }
.screen { position: relative; background: #000; aspect-ratio: 16 / 9; box-shadow: 0 0 0 1px var(--line), 0 30px 80px rgba(0,0,0,.6); max-width: 100%; }
video { display: block; width: 100%; height: 100%; background: #000; }
.now { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 16px; margin-top: 10px; color: var(--muted); font-size: 17px; }
.now b { color: var(--ink); font-weight: 600; }
.clock { font-variant-numeric: tabular-nums; }
aside { border: 1px solid var(--line); background: var(--panel); }
aside h2 { margin: 0; padding: 16px 18px 12px; font: 500 13px/1 var(--display); letter-spacing: .32em; text-transform: uppercase; color: var(--gold); border-bottom: 1px solid var(--line); }
.ch { display: grid; grid-template-columns: 54px 1fr; gap: 8px; width: 100%; padding: 11px 18px; border: 0; background: transparent; color: var(--ink); text-align: left; font: 500 18px/1.3 var(--serif); cursor: pointer; }
.ch .t { color: var(--muted); font-variant-numeric: tabular-nums; font-size: 15px; padding-top: 2px; }
.ch small { display: block; font: 500 11px/1.4 var(--display); letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
.ch:hover { background: rgba(217, 184, 113, .06); }
.ch[aria-current="true"] { background: rgba(217, 184, 113, .1); }
.ch[aria-current="true"] .t, .ch[aria-current="true"] small { color: var(--gold); }
.cc { margin: 12px 18px 16px; padding: 8px 14px; border: 1px solid var(--line); background: transparent; color: var(--ink); font: 500 12px/1 var(--display); letter-spacing: .2em; text-transform: uppercase; cursor: pointer; }
.cc[aria-pressed="true"] { border-color: var(--gold); color: var(--gold); }
section { display: grid; gap: 18px; padding-top: 20px; border-top: 1px solid var(--line); }
section h2 { margin: 0; font: 500 clamp(24px, 3vw, 34px)/1.1 var(--display); letter-spacing: .08em; }
section p { margin: 0; color: var(--muted); max-width: 44em; }
.reels { display: grid; grid-template-columns: minmax(0, 81fr) minmax(0, 256fr); gap: 24px; align-items: start; }
.reels figure { margin: 0; display: grid; gap: 8px; }
.reels video { box-shadow: 0 0 0 1px var(--line); }
.reels figcaption { font: 500 12px/1.4 var(--display); letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }
.cta { display: inline-block; justify-self: start; padding: 12px 22px; background: linear-gradient(180deg, #f1dc9e, #c9a35a); color: #1a1408; text-decoration: none; font: 600 13px/1 var(--display); letter-spacing: .24em; text-transform: uppercase; }
.note { margin: 0; font-size: 15px; color: var(--muted); max-width: 70em; }
@media (max-width: 960px) { .layout { grid-template-columns: 1fr; } .reels { grid-template-columns: 1fr; } .reels figure:first-child { max-width: 360px; } }
</style>

<div class="wrap">
  <header>
    <div class="kicker">Great Atlantic Trading &middot; Caviar Star</div>
    <h1>From the Docks to the Tin</h1>
    <div class="rule"></div>
    <p class="sub">The story of a family seafood business: from the cold water of Maine, through the fish markets of Japan, to a small building in Ocean Isle Beach, North Carolina, and the caviar tins that leave it every day.</p>
    <div class="meta">__CHIPS__</div>
  </header>
  <div class="layout">
    <div>
      <div class="screen"><video id="player" controls playsinline preload="metadata" poster="poster.jpg"></video></div>
      <div class="now"><span>Now playing: <b id="nowTitle">__FIRST__</b></span><span class="clock" id="clock">0:00 / __TOTAL__</span></div>
    </div>
    <aside aria-label="Chapters">
      <h2>Chapters</h2>
      <nav id="toc">__TOC__</nav>
      <button type="button" class="cc" id="cc" aria-pressed="false">Captions</button>
    </aside>
  </div>
  <section aria-labelledby="reels-h">
    <h2 id="reels-h">The collection, in motion</h2>
    <p>Two short cuts for social: every piece rendered in 3D from the shop's own photographs, lit from behind, turning on its own.</p>
    <div class="reels">
      <figure><video controls playsinline preload="metadata" loop poster="reel-9x16.jpg" src="reel-9x16.mp4" style="aspect-ratio:9/16;width:100%"></video><figcaption>Vertical &middot; 9:16 &middot; Reels, TikTok, Shorts</figcaption></figure>
      <figure><video controls playsinline preload="metadata" loop poster="reel-16x9.jpg" src="reel-16x9.mp4" style="aspect-ratio:16/9;width:100%"></video><figcaption>Landscape &middot; 16:9 &middot; Web and YouTube</figcaption></figure>
    </div>
    <a class="cta" href="__GALLERY__" target="_blank" rel="noopener">See all 181 products in 3D</a>
  </section>
  <p class="note">__NOTE__</p>
</div>

<script type="application/json" id="manifest">__MANIFEST__</script>
<script>
(function () {
  var M = JSON.parse(document.getElementById('manifest').textContent);
  var video = document.getElementById('player'), clock = document.getElementById('clock'), nowTitle = document.getElementById('nowTitle');
  var rows = Array.prototype.slice.call(document.querySelectorAll('.ch')), cur = -1;
  function fmt(s) { s = Math.max(0, Math.floor(s)); var m = Math.floor(s / 60), r = s % 60; return m + ':' + (r < 10 ? '0' : '') + r; }
  var track = video.addTextTrack ? video.addTextTrack('captions', 'English', 'en') : null;
  var ccOn = false; try { ccOn = localStorage.getItem('gat-cc') === '1'; } catch (e) {}
  var cc = document.getElementById('cc');
  function applyCC() { if (track) track.mode = ccOn ? 'showing' : 'hidden'; cc.setAttribute('aria-pressed', String(ccOn)); }
  cc.addEventListener('click', function () { ccOn = !ccOn; try { localStorage.setItem('gat-cc', ccOn ? '1' : '0'); } catch (e) {} applyCC(); });
  applyCC();
  function setTrack(i) {
    if (!track || !window.VTTCue) return;
    while (track.cues && track.cues.length) track.removeCue(track.cues[0]);
    (M.parts[i].cues || []).forEach(function (c) { track.addCue(new VTTCue(c[0], c[1], c[2])); });
  }
  function load(i, t, play) {
    var go = function () { try { video.currentTime = t; } catch (e) {} if (play) { var p = video.play(); if (p && p.catch) p.catch(function () {}); } };
    if (i !== cur) { cur = i; video.src = M.parts[i].src; setTrack(i); video.addEventListener('loadedmetadata', go, { once: true }); video.load(); }
    else go();
  }
  function seekGlobal(T, play) { for (var i = M.parts.length - 1; i >= 0; i--) if (T >= M.parts[i].start - 0.01) { load(i, Math.max(0, T - M.parts[i].start), play); return; } }
  function update() {
    if (cur < 0) return;
    var T = M.parts[cur].start + (video.currentTime || 0), k = -1;
    clock.textContent = fmt(T) + ' / ' + fmt(M.total);
    rows.forEach(function (r, j) { if (parseFloat(r.dataset.t) <= T + 0.05) k = j; });
    rows.forEach(function (r, j) { r.setAttribute('aria-current', j === k ? 'true' : 'false'); });
    if (k >= 0) nowTitle.textContent = rows[k].dataset.title;
  }
  video.addEventListener('timeupdate', update);
  video.addEventListener('ended', function () { if (cur < M.parts.length - 1) load(cur + 1, 0, true); });
  rows.forEach(function (r) { r.addEventListener('click', function () { seekGlobal(parseFloat(r.dataset.t) + 0.05, true); }); });
  load(0, 0, false); update();
})();
</script>
"""


def read_vtt(path):
    def sec(x):
        h, m, s = x.split(':'); return round(int(h) * 3600 + int(m) * 60 + float(s), 3)
    cues = []
    for block in re.split(r'\n\s*\n', path.read_text()):
        lines = block.strip().splitlines()
        if lines and '-->' in lines[0]:
            a, b = [x.strip() for x in lines[0].split('-->')]; cues.append([sec(a), sec(b), '\n'.join(lines[1:])])
    return cues


def fmt(s):
    s = int(s); return f'{s // 60}:{s % 60:02d}'


ROMAN = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight']

ap = argparse.ArgumentParser(); ap.add_argument('--dir', required=True); ap.add_argument('--gallery', required=True)
ap.add_argument('--note', default='')
a = ap.parse_args(); d = Path(a.dir); m = json.loads((d / 'manifest.json').read_text()); esc = lambda s: html.escape(s, quote=True)
toc, seen = [], set()
for s in m['scenes']:
    c = s['chapter']
    if c in seen: continue
    seen.add(c)
    title = s['chapterTitle']; kick = 'Prologue' if c == 0 else f'Chapter {ROMAN[c]}'
    toc.append(f'<button type="button" class="ch" data-t="{s["t"]}" data-title="{esc(title)}" aria-current="false"><span class="t">{fmt(s["t"])}</span>'
               f'<span><small>{kick}</small>{esc(title)}</span></button>')
chips = ''.join(f'<span class="chip">{esc(c)}</span>' for c in [f"{fmt(m['total'])} min", f'{len(seen) - 1} chapters', 'Captions'])
page = (PAGE.replace('__CHIPS__', chips).replace('__FIRST__', 'Cold open').replace('__TOTAL__', fmt(m['total'])).replace('__TOC__', ''.join(toc))
        .replace('__GALLERY__', esc(a.gallery)).replace('__NOTE__', esc(a.note))
        .replace('__MANIFEST__', json.dumps({'total': m['total'], 'parts': [dict({k: p[k] for k in ('src', 'start', 'dur')}, cues=read_vtt(d / p['vtt'])) for p in m['parts']]}).replace('</', '<\\/')))
(d / 'index.html').write_text(page); print('wrote', d / 'index.html')
