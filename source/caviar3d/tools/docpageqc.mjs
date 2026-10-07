import { chromium } from 'playwright';
const b = await chromium.launch();
for (const [w, h, n] of [[1440, 900, 'wide'], [390, 844, 'phone']]) {
  const pg = await b.newPage({ viewport: { width: w, height: h } });
  pg.on('pageerror', e => console.log('PAGEERROR', e.message));
  await pg.route(/fonts\.googleapis/, r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.goto('http://localhost:8795/gat-doc/index.html'); await pg.waitForTimeout(1500);
  console.log(n, 'scrollW', await pg.evaluate(() => document.documentElement.scrollWidth), 'chapters', await pg.evaluate(() => [...document.querySelectorAll('.ch')].map(x => x.textContent.trim().slice(0, 40)).join(' | ')));
  await pg.screenshot({ path: `/tmp/claude-0/gat/docpage_${n}.png`, fullPage: n === 'wide' });
}
await b.close();
