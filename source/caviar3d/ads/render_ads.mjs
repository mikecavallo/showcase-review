// node ads/render_ads.mjs <jobs.json> [--stills-only] : renders each job {id, format, ad} to ads/out/<id>-<format>.png (+ .mp4, 8 s @ 24 fps)
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const stillsOnly = process.argv.includes('--stills-only');
const DIMS = { '1x1': [1080, 1080], '4x5': [1080, 1350], '9x16': [1080, 1920] }, FPS = 24;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const j of jobs) for (let attempt = 0; attempt < 2; attempt++) { try {
  const [W, H] = DIMS[j.format]; const base = `ads/out/${j.id}-${j.format}`;
  if (fs.existsSync(base + '.png') && (stillsOnly || fs.existsSync(base + '.mp4'))) break;
  const pg = await b.newPage({ viewport: { width: W, height: H } }); pg.setDefaultTimeout(90000);
  pg.on('pageerror', e => console.log('PAGEERROR', j.id, e.message));
  await pg.goto('http://localhost:8791/doc/stage/ad.html'); await pg.waitForFunction('window.ready');
  await pg.evaluate(a => window.loadAd(a), Object.assign({ format: j.format }, j.ad));
  const D = j.ad.dur || 8, t0 = Date.now();
  await pg.evaluate(t => window.renderAt(t), D - .4);
  await pg.screenshot({ path: base + '.png', clip: { x: 0, y: 0, width: W, height: H } });
  if (!stillsOnly) {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', base + '.part.mp4']);
    for (let i = 0; i < D * FPS; i++) {
      await pg.evaluate(t => window.renderAt(t), i / FPS);
      const buf = await pg.screenshot({ type: 'jpeg', quality: 93, clip: { x: 0, y: 0, width: W, height: H } });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); fs.renameSync(base + '.part.mp4', base + '.mp4');
  }
  console.log(j.id, j.format, ((Date.now() - t0) / 1000).toFixed(0) + 's'); await pg.close(); break;
} catch (e) { console.log('RETRY', j.id, j.format, e.message.split('\n')[0]); } }
await b.close();
