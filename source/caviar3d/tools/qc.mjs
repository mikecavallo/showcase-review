// One still per product for QC: node tools/qc.mjs outdir [handles...]
import { chromium } from 'playwright';
import fs from 'fs';
const [, , outdir, ...only] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
fs.mkdirSync(outdir, { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 480, height: 480 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8790/render.html?w=480&h=480'); await pg.waitForFunction('window.ready');
for (const h of (only.length ? only : Object.keys(spec))) {
  try {
    await pg.evaluate(s => window.loadProduct(s), Object.assign({ handle: h }, spec[h]));
    await pg.evaluate(() => window.renderAt(1.6));
    await pg.screenshot({ path: `${outdir}/${h}.jpg`, type: 'jpeg', quality: 85 });
  } catch (e) { console.log('FAIL', h, e.message.slice(0, 120)); }
}
await b.close();
