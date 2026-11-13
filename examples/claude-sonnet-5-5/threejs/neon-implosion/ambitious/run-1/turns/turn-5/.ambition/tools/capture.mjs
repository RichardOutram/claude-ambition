// usage: node capture.mjs <html> <T0offset> <outdir> <query> <t1,t2,...> [W H]
import {chromium} from 'playwright';
import fs from 'fs';
const [html, off, outdir, query, times, W='640', H='360'] = process.argv.slice(2);
fs.mkdirSync(outdir, {recursive: true});
const browser = await chromium.launch({channel: 'chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const page = await browser.newPage({viewport: {width: +W, height: +H}, deviceScaleFactor: 1});
const errs = [];
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
await page.addInitScript(() => { let n = 0; performance.now = () => n; window.__set = ms => { n = ms; }; });
await page.goto('file://' + html + (query ? '?' + query : ''));
const raf2 = () => page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
await page.addStyleTag({content:'#bar,#hint{display:none}'});
await page.waitForTimeout(1500);
await raf2();
for (const t of times.split(',').map(Number)) {
  // loop time t (seconds) -> clock value; new version has T0 offset, tStart = 0
  const now = (((t - +off) % 10) + 10) % 10;
  await page.evaluate(ms => window.__set(ms), now * 1000);
  await raf2();
  await page.screenshot({path: `${outdir}/t${t.toFixed(4)}.png`});
}
console.log('console errors:', JSON.stringify(errs));
await browser.close();
