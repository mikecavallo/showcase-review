// node tools/hero.mjs <handle> <out.jpg> [w h t]: one still from the studio at time t
import { chromium } from 'playwright';
import fs from 'fs';
const [, , h, out, w = '1000', hh = '625', t = '1.6'] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: +w, height: +hh } });
await pg.goto(`http://localhost:8790/render.html?w=${w}&h=${hh}`); await pg.waitForFunction('window.ready');
await pg.evaluate(s => window.loadProduct(s), Object.assign({ handle: h, period: 10 }, spec[h]));
await pg.evaluate(t => window.renderAt(t), +t);
await pg.screenshot({ path: out, type: 'jpeg', quality: 86 });
await b.close();
