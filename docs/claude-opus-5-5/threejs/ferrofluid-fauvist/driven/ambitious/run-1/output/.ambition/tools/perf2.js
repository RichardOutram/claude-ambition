// render+sync timing for several files at one size. usage: node perf2.js w h dpr a.html b.html ...
const puppeteer = require('puppeteer-core'); const path = require('path');
const [w, h, dpr, ...files] = process.argv.slice(2);
const CLOCK = `(() => { let now = 0; let cbs = []; performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } };
  const o = HTMLCanvasElement.prototype.getContext; window.__gls = [];
  HTMLCanvasElement.prototype.getContext = function(t, x){ const c = o.call(this, t, x); if (/webgl/.test(t) && c) __gls.push(c); return c; }; })();`;
(async () => {
  const br = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal', '--ignore-gpu-blocklist'] });
  for (const f of files) {
    const p = await br.newPage(); await p.setViewport({ width: +w, height: +h, deviceScaleFactor: +dpr });
    await p.evaluateOnNewDocument(CLOCK); await p.goto('file://' + path.resolve(f));
    await p.evaluate(() => { __vc.set(0); __vc.flush(); });
    const r = await p.evaluate(() => { const gl = __gls[0], px = new Uint8Array(4), t = [];
      const bw = gl.drawingBufferWidth, bh = gl.drawingBufferHeight;
      for (let k = 0; k < 3; k++) for (let f = 30; f < 102; f++) { __vc.set((f + .02) * 1000 / 12); const b = performance.timeOrigin; const s = Date.now(); __vc.flush(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); t.push(Date.now() - s); }
      t.sort((a, b) => a - b); return { p50: t[108], p90: t[194], buf: bw + 'x' + bh }; });
    console.log(`${path.basename(f).padEnd(20)} buffer ${r.buf}  p50 ${r.p50} ms  p90 ${r.p90} ms`);
    await p.close();
  }
  await br.close();
})();
