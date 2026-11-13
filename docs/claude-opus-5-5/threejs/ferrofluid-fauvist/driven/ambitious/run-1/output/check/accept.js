// Acceptance test: every promise in the ask + restatement, run identically on any version.
// usage: node check/accept.js [file.html] [--sheet out.png]   (default file: ferrofluid-zoetrope.html)
// Chrome path: $CHROME_PATH, else the macOS default.
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const file = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : path.join(__dirname, '..', 'ferrofluid-zoetrope.html');
const sheetOut = process.argv.includes('--sheet') ? process.argv[process.argv.indexOf('--sheet') + 1] : null;

const CLOCK = `(() => {
  let now = 0; let cbs = [];
  performance.now = () => now;
  window.requestAnimationFrame = cb => { cbs.push(cb); return cbs.length; };
  window.__vc = { set(t){ now = t; }, flush(){ const l = cbs; cbs = []; l.forEach(cb => cb(now)); } };
  const orig = HTMLCanvasElement.prototype.getContext; window.__gls = [];
  HTMLCanvasElement.prototype.getContext = function(t, o){ const c = orig.call(this, t, o); if (/webgl/.test(t) && c) __gls.push(c); return c; };
})();`;

// image analysis helpers, run inside a page
const ANALYSE = `async (b64, mode, extra) => {
  const im = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + b64; });
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
  const x = c.getContext('2d'); x.drawImage(im, 0, 0);
  const d = x.getImageData(0, 0, c.width, c.height).data;
  if (mode === 'pixels') return Array.from(d);
  const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  if (mode === 'cells') {
    const G = 4, cw = c.width / G, ch = c.height / G, cells = new Array(16).fill(0);
    for (let y = 0; y < c.height; y++) for (let xx = 0; xx < c.width; xx++) { const k = (y * c.width + xx) * 4;
      cells[Math.floor(y / ch) * G + Math.floor(xx / cw)] += 0.2126 * lin(d[k]) + 0.7152 * lin(d[k+1]) + 0.0722 * lin(d[k+2]); }
    return cells.map(v => v / (cw * ch));
  }
  if (mode === 'hue') {
    let o = 0, v = 0, n = d.length / 4;
    for (let k = 0; k < d.length; k += 4) {
      const r = d[k] / 255, g = d[k+1] / 255, b = d[k+2] / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b), s = mx ? (mx - mn) / mx : 0;
      if (mx - mn < 1e-6) continue;
      let h = mx === r ? ((g - b) / (mx - mn)) % 6 : mx === g ? (b - r) / (mx - mn) + 2 : (r - g) / (mx - mn) + 4; h = (h * 60 + 360) % 360;
      if (h >= 10 && h <= 45 && s > 0.55 && mx > 0.45) o++;
      if (h >= 250 && h <= 300 && s > 0.45 && mx > 0.25) v++;
    }
    return { orange: o / n, violet: v / n };
  }
  if (mode === 'region') { // mean luminance of a rect + diff vs another image
    const [x0, y0, w, h] = extra; let s = 0;
    for (let y = y0; y < y0 + h; y++) for (let xx = x0; xx < x0 + w; xx++) { const k = (y * c.width + xx) * 4; s += 0.2126 * lin(d[k]) + 0.7152 * lin(d[k+1]) + 0.0722 * lin(d[k+2]); }
    return s / (w * h);
  }
}`;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--use-angle=metal', '--ignore-gpu-blocklist', '--enable-gpu'],
  });
  const R = []; const add = (group, name, pass, detail) => R.push({ group, name, pass, detail });
  const open = async (w, h, dpr, o = {}) => {
    const p = await browser.newPage(); p.errs = [];
    p.on('pageerror', e => p.errs.push(e.message));
    p.on('console', m => { if (m.type() === 'error') p.errs.push(m.text()); });
    await p.setViewport({ width: w, height: h, deviceScaleFactor: dpr, hasTouch: !!o.touch, isMobile: !!o.touch });
    if (o.media) await p.emulateMediaFeatures(o.media);
    await p.evaluateOnNewDocument(CLOCK);
    await p.goto('file://' + path.resolve(file), { waitUntil: 'load' });
    return p;
  };
  const go = (p, f, sub = 0.24) => p.evaluate(t => { __vc.set(t); __vc.flush(); }, (f + sub) * 1000 / 12);
  const shot = p => p.screenshot({ encoding: 'base64' });
  const an = (p, b64, mode, extra) => p.evaluate(eval(ANALYSE), b64, mode, extra);
  const diff = async (p, a, b) => { const [x, y] = [await an(p, a, 'pixels'), await an(p, b, 'pixels')]; let n = 0;
    for (let i = 0; i < x.length; i += 4) if (Math.max(Math.abs(x[i]-y[i]), Math.abs(x[i+1]-y[i+1]), Math.abs(x[i+2]-y[i+2])) > 2) n++; return n; };

  // --- the original ask ---
  const src = fs.readFileSync(file, 'utf8');
  const localRefs = (src.match(/(?:src|href)="(?!https?:|data:|#)[^"]+"/g) || []);
  add('ask', 'single web page (no local dependencies)', localRefs.length === 0, `${localRefs.length} local refs`);
  add('ask', 'three.js', /three(\.min)?\.js/.test(src) && /THREE\./.test(src), 'loads three.js and uses THREE');

  const d = await open(1280, 800, 1);
  add('ask', 'no page errors', d.errs.length === 0, d.errs.join('; ') || 'none');
  const frames = []; for (let f = 0; f < 150; f++) { await go(d, f); if (f === 30 || f === 150 - 1 + 1) {} if ([30].includes(f)) frames.a = await shot(d); }
  await go(d, 150); const b150 = await shot(d);
  const seam = await diff(d, frames.a, b150);
  add('ask', '10 s loop is seamless (frame 30 vs 150)', seam === 0, `${seam} px differ`);
  // loop length: frame 30 vs 30+60 should differ (it is not a shorter loop)
  await go(d, 90); const b90 = await shot(d); const half = await diff(d, frames.a, b90);
  add('ask', 'loop is genuinely 10 s (not shorter)', half > 1000, `frame 30 vs 90: ${half} px differ`);

  // zoetrope: the image holds within a frame, changes between frames
  await go(d, 60, 0.1); const h1 = await shot(d); await go(d, 60, 0.9);
  const h2 = await d.screenshot({ encoding: 'base64' });
  await go(d, 61, 0.1); const h3 = await shot(d);
  const holdDiff = await diff(d, h1, h2), stepDiff = await diff(d, h2, h3);
  add('ask', 'zoetrope frames: image changes between frames', stepDiff > 5000, `between frames ${stepDiff} px; within a frame ${holdDiff} px (drum/shutter only)`);

  // orange + violet in every frame
  let minO = 1, minV = 1;
  for (let f = 24; f < 144; f += 10) { await go(d, f); const h = await an(d, await shot(d), 'hue'); minO = Math.min(minO, h.orange); minV = Math.min(minV, h.violet); }
  add('ask', 'orange AND violet in every frame (min share, 12 frames)', minO > 0.05 && minV > 0.05, `orange ≥ ${(minO * 100).toFixed(1)}%, violet ≥ ${(minV * 100).toFixed(1)}%`);

  // pointer guidance: response within one zoetrope frame, local to the pointer
  const u = await open(1280, 800, 1); const g = await open(1280, 800, 1);
  for (let f = 0; f <= 40; f++) { await go(u, f); await go(g, f); }
  await g.mouse.move(380, 560);
  await go(u, 41); await go(g, 41);
  const [su, sg] = [await shot(u), await shot(g)];
  const respond = await diff(u, su, sg);
  add('ask', 'pointer response within ONE zoetrope frame', respond > 2000, `${respond} px changed at the next frame`);
  for (let f = 42; f <= 50; f++) { await go(u, f); await go(g, f); }
  const pu = await shot(u), pg = await shot(g);
  const near = Math.abs(await an(u, pg, 'region', [300, 480, 160, 140]) - await an(u, pu, 'region', [300, 480, 160, 140]));
  add('ask', 'magnet is pulled to the pointer (local change under cursor)', near > 0.002, `Δ mean luminance under cursor ${near.toFixed(4)}`);
  await g.mouse.down(); for (let f = 51; f <= 54; f++) await go(g, f); const pressed = await shot(g); await g.mouse.up();
  const pDiff = await diff(g, pg, pressed);
  add('ask', 'press = pull harder', pDiff > 2000, `${pDiff} px changed`);
  for (let f = 55; f <= 160; f++) await go(g, f);
  for (let f = 51; f <= 160; f++) await go(u, f);
  const back = await diff(u, await shot(u), await shot(g));
  add('ask', 'loop returns to exact after interaction', back === 0, `${back} px differ at frame 160`);

  await u.close(); await g.close();
  // touch
  const t = await open(390, 844, 1, { touch: true }), tu = await open(390, 844, 1);
  await t.bringToFront();
  for (let f = 0; f <= 30; f++) { await go(t, f); await go(tu, f); }
  await t.touchscreen.touchStart(120, 560); for (let f = 31; f <= 36; f++) { await go(t, f); await go(tu, f); }
  const tDiff = await diff(t, await shot(t), await shot(tu)); await t.touchscreen.touchEnd(); await t.close(); await tu.close();
  add('ask', 'touch (tap) steers the magnet', tDiff > 2000, `${tDiff} px changed`);

  // --- restatement promises ---
  // photosensitive safety
  const ps = await open(640, 400, 1); const L = [];
  for (let f = 0; f < 150; f++) for (const sub of [0.02, 0.5]) { await go(ps, f, sub); L.push(await an(ps, await shot(ps), 'cells')); }
  let maxStep = 0; const fl = [];
  for (let c = 0; c < 16; c++) { let ld = 0; for (let i = 1; i < L.length; i++) { const dd = L[i][c] - L[i-1][c]; maxStep = Math.max(maxStep, Math.abs(dd));
    if (Math.abs(dd) >= 0.1) { const s = Math.sign(dd); if (ld && s !== ld) fl.push(i / 24); ld = s; } } }
  fl.sort((a, b) => a - b); let worst = 0; for (const x of fl) worst = Math.max(worst, fl.filter(y => y >= x && y < x + 1).length);
  add('promise', 'WCAG 2.3.1 general flash: ≤ 3 flashes / s', worst <= 3, `max regional step ${maxStep.toFixed(3)}, worst ${worst}/s`);

  const rm = await open(1280, 800, 1, { media: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  let rmMax = 0; for (let f = 0; f < 60; f++) { await go(rm, f, 0.02); rmMax = Math.max(rmMax, ...(await rm.evaluate(() => [...document.querySelectorAll('#flash,#shutter,#slits')].map(e => +getComputedStyle(e).opacity || 0)))); }
  add('promise', 'reduced motion: no flash / shutter flicker', rmMax === 0, `max overlay opacity ${rmMax}`);

  // render cost at audience sizes
  for (const [w, h, dpr] of [[1280, 800, 2], [1920, 1080, 2], [2560, 1440, 2], [390, 844, 3]]) {
    const p = await open(w, h, dpr); await go(p, 0);
    const ms = await p.evaluate(() => { const gl = __gls[0], px = new Uint8Array(4), t = [];
      for (let f = 30; f < 102; f++) { __vc.set((f + .02) * 1000 / 12); const b = Date.now(); __vc.flush(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); t.push(Date.now() - b); }
      t.sort((a, b) => a - b); return { p50: t[36], p90: t[64] }; });
    add('promise', `render ≤ 16 ms p50 @ ${w}x${h}@${dpr}`, ms.p50 <= 16, `p50 ${ms.p50} ms, p90 ${ms.p90} ms`);
    await p.close();
  }

  // reveal (technique on show)
  const rv = await open(1280, 800, 1); for (let f = 0; f <= 40; f++) await go(rv, f); const r0 = await shot(rv);
  await rv.keyboard.press('f'); await go(rv, 40, 0.6); const r1 = await shot(rv);
  const rvd = await diff(rv, r0, r1);
  add('promise', 'technique overlay (F) reveals the field', rvd > 2000, `${rvd} px changed`);

  // layout & legibility at phone width
  const ph = await open(390, 844, 2); await go(ph, 30);
  const lay = await ph.evaluate(() => {
    const over = document.documentElement.scrollWidth > innerWidth;
    const hud = [...document.querySelectorAll('#hud > *')].filter(e => getComputedStyle(e).display !== 'none').map(e => e.getBoundingClientRect());
    let overlap = false; for (let i = 0; i < hud.length; i++) for (let j = i + 1; j < hud.length; j++) { const a = hud[i], b = hud[j];
      if (a.width && b.width && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom) overlap = true; }
    const off = hud.some(r => r.right > innerWidth + 1 || r.left < -1);
    return { over, overlap, off };
  });
  add('promise', 'phone 390px: no h-scroll, HUD inside & not overlapping', !lay.over && !lay.overlap && !lay.off, JSON.stringify(lay));
  // HUD contrast: butter text vs the pixels behind the frame counter
  const hb = await ph.evaluate(() => { const e = document.querySelector('#hud span, #frame'); const r = e.getBoundingClientRect(); e.style.visibility = 'hidden'; return [r.left, r.top, r.width, r.height].map(Math.round); });
  const bgShot = await ph.screenshot({ encoding: 'base64' });
  const bgL = await an(ph, bgShot, 'region', hb.map(v => v * 2));
  const txt = 0.2126 * Math.pow(1, 2.4) + 0.7152 * Math.pow((0xd9 / 255 + .055) / 1.055, 2.4) + 0.0722 * Math.pow((0xa8 / 255 + .055) / 1.055, 2.4);
  const cr = (txt + 0.05) / (bgL + 0.05);
  add('promise', 'HUD text contrast ≥ 4.5:1', cr >= 4.5, `${cr.toFixed(1)}:1`);

  // accessibility
  const a11y = await d.evaluate(() => ({ label: !!document.querySelector('canvas[aria-label]'), btn: !!document.querySelector('button'), touch: getComputedStyle(document.body).touchAction }));
  add('promise', 'canvas has an accessible description', a11y.label, '');
  add('promise', 'no touch scroll-trap (vertical pan allowed)', /pan-y|auto/.test(a11y.touch), `touch-action: ${a11y.touch}`);

  for (const r of R) console.log(`${r.pass ? 'PASS' : 'FAIL'}  [${r.group}] ${r.name} — ${r.detail}`);
  console.log(`\n${R.filter(r => r.pass).length}/${R.length} passed`);
  process.exitCode = R.every(r => r.pass) ? 0 : 1;

  if (sheetOut) {
    const tiles = [];
    for (let f = 24; f < 144; f += 10) { await go(d, f); tiles.push(['f' + f, await shot(d), 240]); }
    for (const f of [30, 70, 110]) { await go(ph, f); tiles.push(['phone f' + f, await shot(ph), 112]); }
    const html = `<body style="margin:0;background:#111;color:#eee;font:11px monospace;display:flex;flex-wrap:wrap;gap:3px;padding:3px;width:1500px">` +
      tiles.map(([l, s, w]) => `<figure style="margin:0"><img src="data:image/png;base64,${s}" style="width:${w}px;display:block"><figcaption>${l}</figcaption></figure>`).join('') + `</body>`;
    const sp = await browser.newPage(); await sp.setViewport({ width: 1506, height: 50 });
    await sp.setContent(html, { waitUntil: 'load' }); await sp.screenshot({ path: sheetOut, fullPage: true });
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
