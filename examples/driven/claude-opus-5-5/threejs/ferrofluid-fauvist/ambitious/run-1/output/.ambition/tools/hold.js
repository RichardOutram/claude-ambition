// Does the 3D image hold still within a zoetrope frame? (drum + shutter overlays hidden)
const puppeteer = require('puppeteer-core'); const path = require('path');
const CLOCK = `(() => { let now = 0; let cbs = []; performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } }; })();`;
(async () => {
  const br = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal'] });
  const p = await br.newPage(); await p.setViewport({ width: 1280, height: 800 });
  await p.evaluateOnNewDocument(CLOCK); await p.goto('file://' + path.resolve(process.argv[2]));
  await p.addStyleTag({ content: '#drum,#shutter,#slits,#flash{visibility:hidden!important}' });
  const at = async t => { await p.evaluate(t => { __vc.set(t); __vc.flush(); }, t * 1000 / 12); return p.screenshot({ encoding: 'base64' }); };
  for (let f = 0; f < 60; f++) await at(f + 0.1);
  const a = await at(60.1), b = await at(60.9), c = await at(61.1);
  const n = await p.evaluate(async (x, y) => { const L = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
    const [i1, i2] = await Promise.all([L(x), L(y)]); const cv = document.createElement('canvas'); cv.width = i1.width; cv.height = i1.height; const k = cv.getContext('2d');
    k.drawImage(i1, 0, 0); const d1 = k.getImageData(0, 0, cv.width, cv.height).data; k.drawImage(i2, 0, 0); const d2 = k.getImageData(0, 0, cv.width, cv.height).data;
    let n = 0; for (let i = 0; i < d1.length; i += 4) if (Math.max(Math.abs(d1[i]-d2[i]), Math.abs(d1[i+1]-d2[i+1]), Math.abs(d1[i+2]-d2[i+2])) > 2) n++; return n; }, a, b);
  const m = await p.evaluate(async (x, y) => x === y ? 0 : 1, b, c);
  console.log(`within one frame (overlays hidden): ${n} px differ; next frame identical? ${m === 0}`); await br.close();
})();
