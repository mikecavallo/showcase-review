// Render documentary scenes to mp4 (video only): node build/render_doc.mjs [sceneIds...]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
const only = process.argv.slice(2);
const TL = JSON.parse(fs.readFileSync('build/timeline.json', 'utf8'));
const FPS = 24; fs.mkdirSync('build/video', { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
await pg.goto('http://localhost:8791/doc/stage/stage.html'); await pg.waitForFunction('window.ready');
for (const sc of TL) {
  if (only.length && !only.includes(sc.id)) continue;
  const out = `build/video/${sc.id}.mp4`;
  if (!only.length && fs.existsSync(out)) continue;
  const t0 = Date.now();
  await pg.evaluate(s => window.loadScene(s), sc);
  const fade = sc.id === '0.1' ? [1.2, 0] : sc.id === '8.2' ? [0, 1.5] : [0, 0];
  await pg.evaluate(f => { window.sceneFade = f; }, fade);
  const N = Math.round(sc.dur * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out + '.part.mp4']);
  for (let i = 0; i < N; i++) {
    await pg.evaluate(([t, i]) => window.renderAt(t, i), [i / FPS, i]);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  fs.renameSync(out + '.part.mp4', out);
  console.log(sc.id, N, 'frames', ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
await b.close();
