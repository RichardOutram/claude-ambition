// Pixel-compare two pages frame by frame. usage: node eq.js a.html b.html w h dpr
const puppeteer = require('puppeteer-core'); const path = require('path');
const [A, B, w = 1280, h = 800, dpr = 1] = process.argv.slice(2);
const CLOCK = `(() => { let now = 0; let cbs = []; performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } }; })();`;
(async () => {
  const br = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal', '--ignore-gpu-blocklist'] });
  const open = async f => { const p = await br.newPage(); await p.setViewport({ width: +w, height: +h, deviceScaleFactor: +dpr }); await p.evaluateOnNewDocument(CLOCK); await p.goto('file://' + path.resolve(f)); return p; };
  const a = await open(A), b = await open(B); let worst = 0;
  for (let f = 0; f < 120; f += 15) {
    const g = async p => { await p.evaluate(t => { __vc.set(t); __vc.flush(); }, (f + 0.24) * 1000 / 12); return p.screenshot({ encoding: 'base64' }); };
    const [ia, ib] = [await g(a), await g(b)];
    const n = await a.evaluate(async (x, y) => {
      const L = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
      const [p, q] = await Promise.all([L(x), L(y)]); const c = document.createElement('canvas'); c.width = p.width; c.height = p.height;
      const k = c.getContext('2d'); k.drawImage(p, 0, 0); const d1 = k.getImageData(0, 0, c.width, c.height).data; k.drawImage(q, 0, 0); const d2 = k.getImageData(0, 0, c.width, c.height).data;
      let n = 0; for (let i = 0; i < d1.length; i += 4) if (Math.max(Math.abs(d1[i]-d2[i]), Math.abs(d1[i+1]-d2[i+1]), Math.abs(d1[i+2]-d2[i+2])) > 2) n++; return n; }, ia, ib);
    worst = Math.max(worst, n);
  }
  console.log(`max differing px over 8 frames: ${worst}`); await br.close();
})();
