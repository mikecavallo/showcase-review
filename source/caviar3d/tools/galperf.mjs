import fs from 'fs';
import { chromium } from 'playwright';
const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 1440, height: 900 } });
await pg.route(/cdn\.jsdelivr\.net\/npm\/three@0\.160\.0\/(.*)/, (r) => { const p = r.request().url().split('three@0.160.0/')[1]; const f = p.startsWith('build/') ? 'web/vendor/' + p.slice(6) : 'web/vendor/addons/' + p.replace('examples/jsm/',''); return r.fulfill({ path: f, contentType: 'text/javascript' }); });
await pg.route(/fonts\.googleapis/, r => r.fulfill({ body: '', contentType: 'text/css' }));
await pg.addInitScript(() => { window.requestAnimationFrame = () => 0; });
pg.on('pageerror', e => console.log('PAGEERROR', e.message)); pg.on('console', m => console.log('console', m.text()));
await pg.goto('http://localhost:8795/caviar/index.html'); await pg.waitForTimeout(8000); console.log(await pg.evaluate(() => [!!window.__st, !!(window.__st && window.__st.obj)])); await pg.waitForFunction('window.__st && window.__st.obj', null, { timeout: 60000 });
for (const i of process.argv.slice(2).map(Number)) {
  const r = await pg.evaluate(async i => { const items = await (await fetch('catalog.json')).json(); const it = items[i]; const st = window.__st;
    let a = performance.now(); await st.load(Object.assign({}, it, { handle: it.h, kind: it.k, title: it.t, period: 10 }), './assets'); const lt = performance.now() - a;
    st.renderer.preserveDrawingBuffer; const gl = st.renderer.getContext(); const px = new Uint8Array(4);
    a = performance.now(); st.render(0.5); gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px); const f1 = performance.now() - a;
    a = performance.now(); st.render(1.0); gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px); const f2 = performance.now() - a;
    return [it.h, it.k, Math.round(lt), Math.round(f1), Math.round(f2), st.renderer.domElement.toDataURL('image/jpeg', .85)]; }, i);
  const d = r.pop(); fs.writeFileSync(`/tmp/claude-0/gat/pk_${i}.jpg`, Buffer.from(d.split(',')[1], 'base64')); console.log(r.join(' '));
}
await b.close();
