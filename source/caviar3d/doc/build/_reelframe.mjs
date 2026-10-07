import { chromium } from 'playwright';
import fs from 'fs';
const R = JSON.parse(fs.readFileSync('build/reel.json', 'utf8'));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 540, height: 960 } });
pg.on('pageerror', e => console.log('PAGEERROR', e.message));
await pg.goto('http://localhost:8791/doc/stage/reel.html?w=540&h=960'); await pg.waitForFunction('window.ready');
await pg.evaluate(r => window.loadReel(r), R);
for (const t of [5, 10, 14.5, 23, 31, 36, 40]) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: `/tmp/claude-0/gat/rf_${t}.jpg`, type: 'jpeg', quality: 80 }); }
await b.close();
