// node tools/texdump.mjs <handle> <outdir> : dumps the drawn caviar textures of one product and a still of it
import { chromium } from 'playwright'; import fs from 'fs';
const [h, out] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1080, height: 1080 } }); pg.on('pageerror', e => console.log('ERR', e.message)); pg.setDefaultTimeout(120000);
await pg.goto('http://localhost:8791/doc/stage/ad.html'); await pg.waitForFunction('window.ready');
await pg.evaluate(h => window.loadAd({ format: '1x1', h, headline: '', sub: '', name: '', now: '', was: '', size: '', badge: null, cta: '', foot: '' }), h);
await pg.evaluate(() => window.renderAt(7.6));
const urls = await pg.evaluate(() => {
  const res = [], seen = new Set();
  globalThis.__lastStudio.scene.traverse(o => { const m = o.material; if (!m) return; for (const k of ['map', 'bumpMap']) { const t = m[k]; if (t && t.image instanceof HTMLCanvasElement && t.image.width >= 1024 && !seen.has(t.image)) { seen.add(t.image); res.push([k, t.image.width, t.image.height, t.image.toDataURL('image/jpeg', .9)]); } } });
  return res;
});
for (const [k, w, hh, u] of urls) fs.writeFileSync(`${out}/${h}-${k}-${w}x${hh}.jpg`, Buffer.from(u.split(',')[1], 'base64'));
await pg.screenshot({ path: `${out}/${h}-still.png` });
console.log(urls.map(u => u.slice(0, 3).join(' ')).join('\n')); await b.close();
