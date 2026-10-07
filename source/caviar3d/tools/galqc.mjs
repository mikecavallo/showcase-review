import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1440, height: 900 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message)); pg.on('console', m => { if (m.type()==='error') console.log('console', m.text()); });
await pg.route(/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/(.*)/, (r) => { const p = r.request().url().split('three@0.160.0/')[1]; const f = p.startsWith('build/') ? 'web/vendor/' + p.slice(6) : 'web/vendor/addons/' + p.replace('examples/jsm/',''); return r.fulfill({ path: f, contentType: 'text/javascript' }); });
await pg.route(/fonts\.googleapis/, r => r.fulfill({ body: '', contentType: 'text/css' }));
pg.on('requestfailed', r => console.log('FAIL', r.url()));
await pg.goto('http://localhost:8795/caviar/index.html'); await pg.waitForTimeout(9000);
await pg.screenshot({ path: '/tmp/claude-0/gat/gal1.png' });
await pg.mouse.wheel(0, 1100); await pg.waitForTimeout(2500);
await pg.screenshot({ path: '/tmp/claude-0/gat/gal2.png' });
const cards = await pg.$$('.card'); console.log('cards', cards.length);
for (const i of [40, 120]) { await cards[i].click(); await pg.waitForTimeout(6000);
  const ms = await pg.evaluate(() => new Promise(r => { const a = performance.now(); requestAnimationFrame(() => requestAnimationFrame(() => r(performance.now() - a))); }));
  console.log('card', i, 'two frames ms', ms);
  await pg.screenshot({ path: `/tmp/claude-0/gat/gal_${i}.png`, timeout: 120000 }); }
await b.close();
