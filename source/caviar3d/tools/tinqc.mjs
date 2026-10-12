// Tin caviar QC: node tools/tinqc.mjs <outdir> <tag> handle...  renders the turntable angles plus a top view and a close-up
import { chromium } from 'playwright';
import fs from 'fs';
const [, , outDir, tag, ...hs] = process.argv;
const spec = JSON.parse(fs.readFileSync('work/spec.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 900, height: 900 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
await pg.goto('http://127.0.0.1:8790/render.html?w=900&h=900'); await pg.waitForFunction('window.ready');
for (const h of hs) {
  const s = Object.assign({ handle: h }, spec[h]);
  await pg.evaluate(s => window.loadProduct(s), s);
  for (const t of [0, 2.2]) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: `${outDir}/${h}-${tag}-t${t}.png` }); }
  // top view and a low close-up of the caviar, camera placed by hand
  for (const [name, el, dist, yaw] of [['top', 1.45, 1.0, 0.25], ['close', 0.55, 0.62, 0.25], ['low', 0.22, 0.75, 0.25]]) {
    await pg.evaluate(([el, dist, yaw]) => {
      const st = window.studio; st.render(0); st.obj.rotation.y = yaw;
      const box = new st.renderer.constructor === undefined ? null : null;
      const d = st.cam.userData.d * dist, ty = st.h * 0.62;
      st.cam.position.set(0, ty + d * Math.sin(el), d * Math.cos(el)); st.cam.lookAt(0, st.h * 0.42, 0);
      st.renderer.render(st.scene, st.cam);
    }, [el, dist, yaw]);
    await pg.screenshot({ path: `${outDir}/${h}-${tag}-${name}.png` });
  }
}
await b.close();
