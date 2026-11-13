// Deterministic frame capture via a virtual clock (works on any version of the page).
// usage: node shot.js <out.png> <label=file.html>... [--w 1280 --h 800 --dpr 1 --frames 0,20,40] [--loopdiff]
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const out = argv[0];
const pages = argv.slice(1).filter(a => a.includes('=') && !a.startsWith('--')).map(a => a.split('='));
const W = +opt('w', 1280), H = +opt('h', 800), DPR = +opt('dpr', 1);
const frames = opt('frames', '0,20,40,60,80,100').split(',').map(Number);
const loopdiff = argv.includes('--loopdiff');

const CLOCK = `(() => {
  let now = 0; let cbs = [];
  performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } };
})();`;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--use-angle=metal', '--ignore-gpu-blocklist', '--enable-gpu'],
  });
  const rows = [];
  for (const [label, file] of pages) {
    const page = await browser.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
    page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await page.setViewport({ width: W, height: H, deviceScaleFactor: DPR });
    await page.evaluateOnNewDocument(CLOCK);
    await page.goto('file://' + path.resolve(file), { waitUntil: 'load' });
    const gpu = await page.evaluate(() => {
      const gl = document.createElement('canvas').getContext('webgl');
      const ext = gl && gl.getExtension('WEBGL_debug_renderer_info');
      return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
    });
    const shots = [];
    const at = async (f) => {
      await page.evaluate((t) => { __vc.set(t); __vc.flush(); }, f * 1000 / 12 + 20);
      return (await page.screenshot({ encoding: 'base64' }));
    };
    for (const f of frames) shots.push({ f, img: await at(f) });
    let diff = null;
    if (loopdiff) {
      const a = await at(30);   // after the crank-up intro
      for (let f = 31; f < 150; f++) await page.evaluate((t) => { __vc.set(t); __vc.flush(); }, f * 1000 / 12 + 20);
      const b = await at(150);
      diff = await page.evaluate(async (a, b) => {
        const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
        const [ia, ib] = await Promise.all([load(a), load(b)]);
        const c = document.createElement('canvas'); c.width = ia.width; c.height = ia.height;
        const x = c.getContext('2d');
        x.drawImage(ia, 0, 0); const da = x.getImageData(0, 0, c.width, c.height).data;
        x.clearRect(0, 0, c.width, c.height);
        x.drawImage(ib, 0, 0); const db = x.getImageData(0, 0, c.width, c.height).data;
        let n = 0, max = 0;
        for (let i = 0; i < da.length; i += 4) {
          const d = Math.max(Math.abs(da[i] - db[i]), Math.abs(da[i+1] - db[i+1]), Math.abs(da[i+2] - db[i+2]));
          if (d > 2) n++; if (d > max) max = d;
        }
        return { differingPixels: n, total: da.length / 4, maxChannelDelta: max };
      }, a, b);
    }
    console.log(JSON.stringify({ label, gpu, errors: errs, loopDiff: diff }));
    rows.push({ label, shots });
    await page.close();
  }
  // contact sheet
  const tw = +opt("tw", Math.min(360, Math.round(1440 / frames.length))), th = Math.round(tw * H / W);
  const html = `<body style="margin:0;background:#111;color:#eee;font:12px monospace">` + rows.map(r =>
    `<div style="display:flex;gap:4px;padding:4px;align-items:center"><div style="width:70px">${r.label}</div>` +
    r.shots.map(s => `<figure style="margin:0"><img src="data:image/png;base64,${s.img}" style="width:${tw}px;height:${th}px;display:block"><figcaption>f${s.f}</figcaption></figure>`).join('') +
    `</div>`).join('') + `</body>`;
  const sheet = await browser.newPage();
  await sheet.setViewport({ width: 80 + frames.length * (tw + 4), height: 50, deviceScaleFactor: 1 });
  await sheet.setContent(html, { waitUntil: 'load' });
  await sheet.screenshot({ path: out, fullPage: true });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
