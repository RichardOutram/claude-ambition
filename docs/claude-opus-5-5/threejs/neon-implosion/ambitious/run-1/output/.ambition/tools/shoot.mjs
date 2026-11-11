// Usage: node shoot.mjs <index.html> <outDir> [sheet.png]
// Needs playwright resolvable (set PW_DIR to a dir with node_modules/playwright, default /tmp/shot).
import { createRequire } from 'module';
import path from 'path';
import fs from 'fs';
const require = createRequire(path.join(process.env.PW_DIR || '/tmp/shot', 'x.js'));
const { chromium } = require('playwright');

const [html, outDir, sheetArg] = process.argv.slice(2);
if (!html || !outDir) { console.error('usage: node shoot.mjs <index.html> <outDir> [sheet.png]'); process.exit(1); }
const sheet = sheetArg || path.join(path.dirname(path.resolve(outDir)), path.basename(path.resolve(outDir)) + '_sheet.png');
fs.mkdirSync(outDir, { recursive: true });
const url = 'file://' + path.resolve(html);
const times = (process.env.TIMES || '0,2,4,5,5.6,5.9,6.05,6.3,7,8.5,9.3,9.999').split(',').map(Number);

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const errors = [];
async function shot(t, w, h, file) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(`[${m.type()} t=${t}] ${m.text()}`); });
  page.on('pageerror', e => errors.push(`[pageerror t=${t}] ${e.message}`));
  await page.goto(`${url}?t=${t}`);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
  await page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n > 8 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
  await page.screenshot({ path: file });
  await page.close();
}
const files = [];
for (const t of times) { const f = path.join(outDir, `t${t}.png`); await shot(t, 1280, 720, f); files.push([t, f]); }
for (const t of [1, 7]) await shot(t, 390, 844, path.join(outDir, `mobile_t${t}.png`));

// contact sheet + seam diff, computed in a browser canvas
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
const imgs = files.map(([t, f]) => ({ t, src: 'data:image/png;base64,' + fs.readFileSync(f).toString('base64') }));
const res = await page.evaluate(async (imgs) => {
  const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
  const L = await Promise.all(imgs.map(o => load(o.src)));
  const cw = 480, ch = 270, cols = 4, rows = Math.ceil(L.length / cols);
  const c = document.createElement('canvas'); c.width = cw * cols; c.height = ch * rows;
  const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, c.width, c.height);
  L.forEach((im, i) => { const x = (i % cols) * cw, y = Math.floor(i / cols) * ch; g.drawImage(im, x, y, cw, ch);
    g.font = 'bold 20px monospace'; g.fillStyle = '#fff'; g.fillText('t=' + imgs[i].t, x + 8, y + 24); });
  const px = im => { const k = document.createElement('canvas'); k.width = im.width; k.height = im.height; const kg = k.getContext('2d'); kg.drawImage(im, 0, 0); return kg.getImageData(0, 0, im.width, im.height).data; };
  const i0 = imgs.findIndex(o => o.t === 0), i1 = imgs.findIndex(o => o.t === 9.999);
  let seam = null;
  if (i0 >= 0 && i1 >= 0) { const a = px(L[i0]), b = px(L[i1]); let s = 0, n = 0; for (let i = 0; i < a.length; i += 4) for (let k = 0; k < 3; k++) { s += Math.abs(a[i + k] - b[i + k]); n++; } seam = s / n; }
  return { sheet: c.toDataURL('image/png'), seam };
}, imgs);
fs.writeFileSync(sheet, Buffer.from(res.sheet.split(',')[1], 'base64'));
await browser.close();
console.log(`seam mean abs diff (t0 vs t9.999): ${res.seam?.toFixed(3)} /255`);
console.log(`console errors/warnings: ${errors.length}`); errors.forEach(e => console.log('  ' + e));
console.log(`sheet: ${sheet}`);
