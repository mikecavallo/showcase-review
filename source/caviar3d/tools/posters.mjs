// Two stills per product for the gallery cards: node tools/posters.mjs outdir
import { chromium } from 'playwright';
import fs from 'fs';
const [, , outdir = 'work/posters'] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
fs.mkdirSync(outdir, { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 560, height: 560 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8790/render.html?w=560&h=560'); await pg.waitForFunction('window.ready');
for (const h of Object.keys(spec)) {
  if (fs.existsSync(`${outdir}/${h}-b.png`)) continue;
  await pg.evaluate(s => window.loadProduct(s), Object.assign({ handle: h, period: 10 }, spec[h]));
  for (const [k, t] of [['a', 0], ['b', 2.5]]) {
    await pg.evaluate(t => window.renderAt(t), t);
    await pg.screenshot({ path: `${outdir}/${h}-${k}.png` });
  }
  console.log(h);
}
await b.close();
