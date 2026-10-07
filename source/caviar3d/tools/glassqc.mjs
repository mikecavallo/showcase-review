import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1280, height: 800 } });
await pg.route(/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/(.*)/, (r) => { const p = r.request().url().split('three@0.160.0/')[1]; const f = p.startsWith('build/') ? 'web/vendor/' + p.slice(6) : 'web/vendor/addons/' + p.replace('examples/jsm/',''); return r.fulfill({ path: f, contentType: 'text/javascript' }); });
await pg.route(/fonts\.googleapis/, r => r.fulfill({ body: '', contentType: 'text/css' }));
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8795/caviar/index.html'); await pg.waitForFunction('window.__st && window.__st.obj', null, { timeout: 120000 });
await pg.evaluate(() => document.querySelectorAll('.card')[0].click()); await pg.waitForTimeout(8000); await pg.evaluate(() => scrollTo(0, 0));
console.log('row visible', await pg.evaluate(() => !document.getElementById('glassRow').hidden), await pg.evaluate(() => document.getElementById('name').textContent));
for (const v of [13, 60, 100]) { await pg.evaluate(v => { const i = document.getElementById('glass'); i.value = v; i.dispatchEvent(new Event('input')); }, v); await pg.waitForTimeout(4000); await pg.screenshot({ path: `/tmp/claude-0/gat/glass_${v}.jpg`, type: 'jpeg', quality: 80, timeout: 120000 }); }
await b.close();
