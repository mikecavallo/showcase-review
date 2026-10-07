// Render stills of products: node tools/snap.mjs out.png handle1 handle2 ... (t=1.5)
import { chromium } from 'playwright';
import fs from 'fs';
const [, , out, ...hs] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 720, height: 720 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
await pg.goto('http://localhost:8790/render.html?w=720&h=720'); await pg.waitForFunction('window.ready');
let i = 0;
for (const h of hs) {
  const s = Object.assign({ handle: h }, spec[h]);
  await pg.evaluate(s => window.loadProduct(s), s);
  for (const t of [0, 2.2]) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: out.replace('.png', `-${i}-${t}.png`) }); }
  i++;
}
await b.close();
