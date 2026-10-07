// node tools/jarposters.mjs <outdir> <handles...> : two 480px stills per product (t = 0 and 2.5), joined into the 960x480 card poster by the caller, for the gallery cards
import { chromium } from 'playwright';
import fs from 'fs';
const [, , outdir, ...hs] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
fs.mkdirSync(outdir, { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 480, height: 480 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8790/render.html?w=480&h=480'); await pg.waitForFunction('window.ready');
for (const h of hs) {
  await pg.evaluate(s => window.loadProduct(s), Object.assign({ handle: h, period: 10 }, spec[h]));
  for (const [k, t] of [['a', 0], ['b', 2.5]]) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: `${outdir}/${h}-${k}.png` }); }
  console.log(h);
}
await b.close();
