// 1:1 device-pixel crops of the same frame from several files, side by side. usage: node crop.js out.png dpr frame a.html b.html
const puppeteer = require('puppeteer-core'); const path = require('path');
const [out, dpr, frame, ...files] = process.argv.slice(2);
const CLOCK = `(() => { let now = 0; let cbs = []; performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } }; })();`;
(async () => {
  const br = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal'] });
  const imgs = [];
  for (const f of files) {
    const p = await br.newPage(); await p.setViewport({ width: 1280, height: 800, deviceScaleFactor: +dpr });
    await p.evaluateOnNewDocument(CLOCK); await p.goto('file://' + path.resolve(f));
    await p.evaluate(t => { __vc.set(t); __vc.flush(); }, (+frame + 0.24) * 1000 / 12);
    imgs.push([path.basename(path.dirname(f)) + '/' + path.basename(f), await p.screenshot({ encoding: 'base64', clip: { x: 440, y: 300, width: 330, height: 200 } })]);
    await p.close();
  }
  const s = await br.newPage(); await s.setViewport({ width: 1400, height: 50 });
  await s.setContent(`<body style="margin:0;background:#111;color:#eee;font:12px monospace;display:flex;gap:6px">` + imgs.map(([l, b]) => `<figure style="margin:0"><img src="data:image/png;base64,${b}" style="width:${330 * +dpr}px;image-rendering:pixelated"><figcaption>${l}</figcaption></figure>`).join('') + '</body>');
  await s.screenshot({ path: out, fullPage: true }); await br.close();
})();
