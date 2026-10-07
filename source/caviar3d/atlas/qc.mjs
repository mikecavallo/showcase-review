// node atlas/qc.mjs : screenshots of the staged atlas at desktop and phone width, with CDN scripts served locally
import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const D = '/tmp/claude-0/gat/d3pkg';
for (const [w, h, n] of [[1440, 900, 'wide'], [390, 844, 'phone']]) {
  const pg = await b.newPage({ viewport: { width: w, height: h } });
  pg.on('pageerror', e => console.log(n, 'PAGEERROR', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log(n, 'console', m.text()); });
  await pg.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/d3\//, r => r.fulfill({ path: `${D}/d3-7.9.0/dist/d3.min.js`, contentType: 'text/javascript' }));
  await pg.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/topojson\//, r => r.fulfill({ path: `${D}/topojson-3.0.2/dist/topojson.min.js`, contentType: 'text/javascript' }));
  await pg.route(/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/(.*)/, r => { const p = r.request().url().split('three@0.160.0/')[1]; const f = p.startsWith('build/') ? '/home/user/caviar3d/web/vendor/' + p.slice(6) : '/home/user/caviar3d/web/vendor/addons/' + p.replace('examples/jsm/', ''); return r.fulfill({ path: f, contentType: 'text/javascript' }); });
  await pg.route(/fonts\.googleapis/, r => r.fulfill({ body: '', contentType: 'text/css' }));
  if (!process.env.WITH3D) await pg.route(/studio\.js/, r => r.abort());
  await pg.goto('http://localhost:8795/atlas/index.html'); await pg.waitForTimeout(n === 'wide' ? 12000 : 6000);
  console.log(n, 'scrollWidth', await pg.evaluate(() => document.documentElement.scrollWidth), 'height', await pg.evaluate(() => document.documentElement.scrollHeight));
  if (n === 'wide') {
    for (const [sel, name] of [['#top', 'hero'], ['#scale', 'scale'], ['#species', 'species'], ['#quiz', 'quiz'], ['#serve', 'serve'], ['#history', 'history']]) {
      await pg.evaluate(s => document.querySelector(s).scrollIntoView(), sel); await pg.waitForTimeout(name === 'quiz' ? 6000 : 800);
      await pg.screenshot({ path: `/tmp/claude-0/gat/atlas_${name}.jpg`, type: 'jpeg', quality: 75, timeout: 120000 });
    }
  } else await pg.screenshot({ path: `/tmp/claude-0/gat/atlas_phone.jpg`, type: 'jpeg', quality: 70, fullPage: true, timeout: 120000 });
}
await b.close();
