// node build/render_reel.mjs <w> <h> <out.mp4>  (video only)
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
const [, , w = '1080', h = '1920', out = 'build/reel-9x16.mp4'] = process.argv;
const W = +w, H = +h, FPS = 24;
const R = JSON.parse(fs.readFileSync('build/reel.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: W, height: H } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto(`http://localhost:8791/doc/stage/reel.html?w=${W}&h=${H}`); await pg.waitForFunction('window.ready');
await pg.evaluate(r => window.loadReel(r), R);
const N = Math.round(R.dur * FPS);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out]);
for (let i = 0; i < N; i++) {
  await pg.evaluate(t => window.renderAt(t), i / FPS);
  const buf = await pg.screenshot({ type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: W, height: H } });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 120 === 0) console.log('frame', i, '/', N);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await b.close(); console.log('done', out);
