// Render seamless turntable loops: node tools/turntable.mjs <size> <seconds> <fps> <outdir> [handles...]
// Frames come straight off the WebGL canvas (JPEG) into ffmpeg; H.264, yuv420p, faststart.
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
const [, , size = '720', secs = '10', fps = '24', outdir = 'out/turntable', ...only] = process.argv;
const W = +size, D = +secs, F = +fps, N = Math.round(D * F);
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
fs.mkdirSync(outdir, { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: W, height: W } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto(`http://localhost:8790/render.html?w=${W}&h=${W}`); await pg.waitForFunction('window.ready');
const hs = only.length ? only : Object.keys(spec);
for (const h of hs) {
  const out = `${outdir}/${h}.mp4`;
  if (fs.existsSync(out) && fs.statSync(out).size > 10000) continue;
  const t0 = Date.now();
  await pg.evaluate(s => window.loadProduct(Object.assign({ period: 10 }, s)), Object.assign({ handle: h }, spec[h], { period: D }));
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(F), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out + '.part.mp4']);
  for (let i = 0; i < N; i++) {
    const url = await pg.evaluate(t => { window.renderAt(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92); }, i / F);
    const buf = Buffer.from(url.split(',')[1], 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  fs.renameSync(out + '.part.mp4', out);
  console.log(h, ((Date.now() - t0) / 1000).toFixed(1) + 's');
}
await b.close();
