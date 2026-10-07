import { chromium } from 'playwright';
const b = await chromium.launch(); const D = '/tmp/claude-0/gat/d3pkg';
const pg = await b.newPage({ viewport: { width: 390, height: 844 } });
await pg.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/d3\//, r => r.fulfill({ path: `${D}/d3-7.9.0/dist/d3.min.js`, contentType: 'text/javascript' }));
await pg.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/topojson\//, r => r.fulfill({ path: `${D}/topojson-3.0.2/dist/topojson.min.js`, contentType: 'text/javascript' }));
await pg.route(/fonts\.googleapis|studio\.js|jsdelivr/, r => r.abort());
await pg.goto(`http://localhost:8795/${process.argv[2] || 'atlas'}/index.html`); await pg.waitForTimeout(3000);
console.log(await pg.evaluate(() => [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > innerWidth + 1 && r.width > 0; })
  .filter(e => !e.closest('.strip')).slice(0, 12).map(e => `${e.tagName}.${e.className && e.className.baseVal === undefined ? e.className : ''}#${e.id} right=${Math.round(e.getBoundingClientRect().right)} w=${Math.round(e.getBoundingClientRect().width)}`)));
await b.close();
