// Challenge tests against the real page. usage: node challenge.js <file.html> <sheet.png> [--novariant <file>]
const puppeteer = require('puppeteer-core');
const path = require('path');
const [file, sheetOut, variant] = process.argv.slice(2);

const CLOCK = `(() => {
  let now = 0; let cbs = [];
  performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } };
  const orig = HTMLCanvasElement.prototype.getContext;
  window.__gls = [];
  HTMLCanvasElement.prototype.getContext = function(type, o){ const c = orig.call(this, type, o); if (/webgl/.test(type) && c) __gls.push(c); return c; };
})();`;

const LUM = `async (b64s) => {
  const out = [];
  for (const s of b64s) {
    const i = await new Promise(r => { const im = new Image(); im.onload = () => r(im); im.src = 'data:image/png;base64,' + s; });
    const c = document.createElement('canvas'); c.width = i.width; c.height = i.height;
    const x = c.getContext('2d'); x.drawImage(i, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height).data;
    const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const G = 4, cw = c.width / G, ch = c.height / G, cells = new Array(G * G).fill(0);
    for (let y = 0; y < c.height; y++) for (let xx = 0; xx < c.width; xx++) {
      const k = (y * c.width + xx) * 4;
      cells[Math.floor(y / ch) * G + Math.floor(xx / cw)] += 0.2126 * lin(d[k]) + 0.7152 * lin(d[k+1]) + 0.0722 * lin(d[k+2]);
    }
    out.push(cells.map(v => v / (cw * ch)));
  }
  return out;
}`;
const DIFF = `async (a, b) => {
  const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
  const [ia, ib] = await Promise.all([load(a), load(b)]);
  const c = document.createElement('canvas'); c.width = ia.width; c.height = ia.height;
  const x = c.getContext('2d');
  x.drawImage(ia, 0, 0); const da = x.getImageData(0, 0, c.width, c.height).data;
  x.clearRect(0, 0, c.width, c.height); x.drawImage(ib, 0, 0); const db = x.getImageData(0, 0, c.width, c.height).data;
  let n = 0; for (let i = 0; i < da.length; i += 4) if (Math.max(Math.abs(da[i]-db[i]), Math.abs(da[i+1]-db[i+1]), Math.abs(da[i+2]-db[i+2])) > 2) n++;
  return n;
}`;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--use-angle=metal', '--ignore-gpu-blocklist', '--enable-gpu'],
  });
  const open = async (f, w, h, dpr, media) => {
    const p = await browser.newPage();
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.setViewport({ width: w, height: h, deviceScaleFactor: dpr, hasTouch: false });
    if (media) await p.emulateMediaFeatures(media);
    await p.evaluateOnNewDocument(CLOCK);
    await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    p.errs = errs; return p;
  };
  const go = (p, frame, sub = 0.24) => p.evaluate((t) => { __vc.set(t); __vc.flush(); }, (frame + sub) * 1000 / 12);
  const shot = p => p.screenshot({ encoding: 'base64' });
  const tiles = [];

  // 1+2. pointer: idle vs pointer vs pressed; then return to exactness after idling
  {
    const idle = await open(file, 1280, 800, 1);
    for (let f = 0; f <= 30; f++) await go(idle, f);
    const idle30 = await shot(idle); tiles.push(['idle f30', idle30]);
    const p = await open(file, 1280, 800, 1);
    for (let f = 0; f <= 24; f++) await go(p, f);
    await p.mouse.move(330, 560);
    for (let f = 25; f <= 30; f++) await go(p, f);
    tiles.push(['pointer at lower-left f30', await shot(p)]);
    await p.mouse.down();
    for (let f = 31; f <= 33; f++) await go(p, f);
    tiles.push(['pressed f33', await shot(p)]);
    await p.mouse.up();
    // idle ~6 s, then compare to a never-touched session at the same frame
    for (let f = 34; f <= 120 + 30; f++) await go(p, f);
    const after = await shot(p);
    const n = await idle.evaluate(eval(DIFF), idle30, after);
    console.log(`[2] after interaction + idle, frame 30 of next loop vs untouched: ${n} differing px`);
    // touch
    const t = await browser.newPage();
    await t.setViewport({ width: 390, height: 844, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
    await t.evaluateOnNewDocument(CLOCK);
    await t.goto('file://' + path.resolve(file), { waitUntil: 'load' });
    for (let f = 0; f <= 20; f++) await go(t, f);
    const before = await shot(t);
    await t.touchscreen.touchStart(100, 600);
    for (let f = 21; f <= 26; f++) await go(t, f);
    const touched = await shot(t);
    await t.touchscreen.touchEnd();
    const tIdle = await open(file, 390, 844, 1);
    for (let f = 0; f <= 26; f++) await go(tIdle, f);
    console.log(`[1] touch at (100,600): differs from untouched by ${await t.evaluate(eval(DIFF), await shot(tIdle), touched)} px`);
    console.log(`[1] page errors: ${JSON.stringify([...idle.errs, ...p.errs])}`);
    await Promise.all([idle.close(), p.close(), t.close(), tIdle.close()]);
  }

  // 6. reveal
  {
    const p = await open(file, 1280, 800, 1);
    for (let f = 0; f <= 30; f++) await go(p, f);
    await p.keyboard.press('f'); await go(p, 30, 0.5);
    tiles.push(['reveal (F)', await shot(p)]);
    await p.close();
  }

  // 7. reduced motion
  {
    const p = await open(file, 1280, 800, 1, [{ name: 'prefers-reduced-motion', value: 'reduce' }]);
    const r = [];
    for (let f = 0; f < 120; f++) { await go(p, f, 0.02); r.push(await p.evaluate(() => ['flash','shutter'].map(id => { const e = document.getElementById(id); return e ? getComputedStyle(e).opacity : 'n/a'; }))); }
    console.log(`[7] reduced motion: max flash opacity ${Math.max(...r.map(x => +x[0]))}, max shutter ${Math.max(...r.map(x => +x[1]))}`);
    await p.close();
  }

  // 4. photosensitivity: mean relative luminance at frame start (shutter dip) and mid-frame
  {
    const p = await open(file, 640, 400, 1);
    const shots = [];
    for (let f = 0; f < 120; f++) for (const sub of [0.02, 0.5]) { await go(p, f, sub); shots.push(await shot(p)); }
    const L = await p.evaluate(eval(LUM), shots);
    // WCAG 2.3.1: a flash = a pair of opposing changes of >= 0.1 relative luminance (absolute), darker state < 0.8
    let maxAbs = 0, flashes = [];
    for (let cell = 0; cell < 16; cell++) {
      let lastDir = 0, lastT = -1;
      for (let i = 1; i < L.length; i++) {
        const d = L[i][cell] - L[i-1][cell]; maxAbs = Math.max(maxAbs, Math.abs(d));
        if (Math.abs(d) >= 0.1) { const dir = Math.sign(d); if (lastDir && dir !== lastDir) flashes.push(i / 24); lastDir = dir; }
      }
    }
    flashes.sort((a, b) => a - b);
    let worst = 0; for (const t of flashes) worst = Math.max(worst, flashes.filter(u => u >= t && u < t + 1).length);
    console.log(`[4] max per-region luminance step ${maxAbs.toFixed(3)} (WCAG threshold 0.100); flashes counted: ${flashes.length}; worst in any 1 s: ${worst} (limit 3)`);
    await p.close();
  }

  // 3. render cost (CPU+GPU, synchronised by a 1px readPixels) at several pixel counts
  for (const [w, h, dpr] of [[1280, 800, 1], [1280, 800, 2], [2560, 1440, 2], [390, 844, 3]]) {
    const p = await open(file, w, h, dpr);
    await go(p, 0);
    const ms = await p.evaluate(async () => {
      const gl = __gls[0]; const px = new Uint8Array(4); const t = [];
      for (let f = 1; f <= 24; f++) {
        __vc.set((f + 0.02) * 1000 / 12);
        const b = Date.now();
        __vc.flush(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        t.push(Date.now() - b);
      }
      t.sort((x, y) => x - y); return { p50: t[12], max: t[23] };
    }).catch(e => ({ err: e.message }));
    console.log(`[3] ${w}x${h}@${dpr} (${(w*h*dpr*dpr/1e6).toFixed(1)} Mpx): render+sync p50 ${ms.p50} ms, max ${ms.max} ms ${ms.err || ''}`);
    await p.close();
  }

  // 5. is the hidden window ever visible? diff against a variant with the window removed
  if (variant) {
    const a = await open(file, 1280, 800, 2), b = await open(variant, 1280, 800, 2);
    let total = 0, frames = 0;
    for (let f = 0; f < 120; f += 10) {
      await go(a, f); await go(b, f);
      const n = await a.evaluate(eval(DIFF), await shot(a), await shot(b));
      total += n; if (n > 0) frames++;
    }
    console.log(`[5] window visible: ${frames}/12 sampled frames, mean ${(total / 12).toFixed(0)} device px per frame (of 4.1M)`);
    await a.close(); await b.close();
  }

  // sheet
  const html = `<body style="margin:0;background:#111;color:#eee;font:12px monospace;display:flex;gap:4px;padding:4px">` +
    tiles.map(([l, s]) => `<figure style="margin:0"><img src="data:image/png;base64,${s}" style="width:420px;display:block"><figcaption>${l}</figcaption></figure>`).join('') + `</body>`;
  const sp = await browser.newPage();
  await sp.setViewport({ width: 4 + tiles.length * 424, height: 50 });
  await sp.setContent(html, { waitUntil: 'load' });
  await sp.screenshot({ path: sheetOut, fullPage: true });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
