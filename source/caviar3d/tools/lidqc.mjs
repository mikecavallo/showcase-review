import { chromium } from 'playwright';
import fs from 'fs';
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 640, height: 640 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8790/render.html?w=640&h=640'); await pg.waitForFunction('window.ready');
for (const h of process.argv.slice(2)) {
  await pg.evaluate(s => window.loadProduct(s), Object.assign({ handle: h, period: 10 }, spec[h]));
  for (const [k, yaw] of (process.env.YAWS ? JSON.parse(process.env.YAWS) : [['front', 0.25], ['side', 1.6], ['back', 3.0]])) {
    await pg.evaluate(y => { const st = window.studio; st.free = true; st.yaw = y; st.render(0); }, yaw);
    await pg.screenshot({ path: `/tmp/claude-0/gat/lid_${h.slice(0, 12)}_${k}.jpg`, type: 'jpeg', quality: 85 });
  }
}
await b.close();
