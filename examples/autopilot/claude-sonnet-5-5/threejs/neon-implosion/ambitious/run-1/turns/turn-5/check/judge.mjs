// Acceptance check for ../solar-implosion.html against the first version.
// usage: npm run check   (or: node judge.mjs [new.html] [first.html])
import {chromium} from 'playwright'; import {fileURLToPath} from 'url'; import path from 'path'; import {PNG} from 'pngjs'; import fs from 'fs';
const here = path.dirname(fileURLToPath(import.meta.url)) + '/';
const [NEW = here + '../solar-implosion.html', FIRST = here + '../.ambition/first/solar-implosion.html'] = process.argv.slice(2);
const sw = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'];
const lin = v => { v /= 255; return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
const dec = b => PNG.sync.read(b);
const lumOf = im => { const d = im.data; let s = 0; for (let i = 0; i < d.length; i += 4) s += .2126 * lin(d[i]) + .7152 * lin(d[i + 1]) + .0722 * lin(d[i + 2]); return s / (d.length / 4); };
const diff = (A, B) => { const x = A.data, y = B.data; let s = 0; for (let i = 0; i < x.length; i += 4) s += Math.abs(x[i] - y[i]) + Math.abs(x[i + 1] - y[i + 1]) + Math.abs(x[i + 2] - y[i + 2]); return s / (x.length / 4 * 3); };
function hueStats(im) { // saturation of lit pixels, populated hue bins (12) among vivid pixels
  const d = im.data, bins = new Array(12).fill(0); let sat = 0, n = 0, vivid = 0;
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], g = d[i + 1], b = d[i + 2], mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    if (mx > 128) { sat += (mx - mn) / mx; n++; }
    if (mx > 77 && (mx - mn) / mx > .35) {
      let h; const dl = mx - mn;
      if (mx === r) h = ((g - b) / dl + 6) % 6; else if (mx === g) h = (b - r) / dl + 2; else h = (r - g) / dl + 4;
      bins[Math.min(11, Math.floor(h * 2))]++; vivid++;
    }
  }
  return {sat: n ? sat / n : 0, bins: vivid > 200 ? bins.filter(c => c / vivid > .03).length : 0};
}
const out = []; const rec = (name, pass, detail) => { out.push({name, pass, detail}); console.log((pass ? 'PASS ' : 'FAIL ') + name.padEnd(46) + detail); };
const errors = [];
const b = await chromium.launch({channel: 'chrome', args: sw});
async function open(file, {query = '', W = 320, H = 180, ctxOpts = {}} = {}) {
  const ctx = await b.newContext({viewport: {width: W, height: H}, ...ctxOpts});
  const p = await ctx.newPage();
  p.on('pageerror', e => errors.push(file.split('/').pop() + ': ' + e.message));
  p.on('console', m => m.type() === 'error' && errors.push(file.split('/').pop() + ': ' + m.text()));
  await p.addInitScript(() => { let n = 0; performance.now = () => n; window.__set = m => { n = m; }; });
  await p.goto('file://' + file + query); await p.addStyleTag({content: '#bar,#hint{display:none}'}); await p.waitForTimeout(1300);
  p.raf = () => p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  p.at = async (ms) => { await p.evaluate(m => window.__set(m), ms); await p.raf(); return dec(await p.screenshot()); };
  p.ctx = ctx; return p;
}
// loop time -> clock ms. new: t = now + 8.5 ; first: t = now
const T0 = +fs.readFileSync(NEW, 'utf8').match(/const T0\s*=\s*([\d.]+)/)[1];
const clockNew = t => (((t - T0) % 10) + 10) % 10 * 1000, clockFirst = t => ((t % 10) + 10) % 10 * 1000;

// ---------- static promises ----------
const src = fs.readFileSync(NEW, 'utf8');
const hosts = [...new Set([...src.matchAll(/https?:\/\/([^/"'\s]+)/g)].map(m => m[1]))];
rec('single web page, three.js', /three@/.test(src) && hosts.every(h => h === 'unpkg.com' || h === 'claude.com'), `external hosts: ${hosts.join(', ')}`);

// ---------- sweeps: both versions, same check ----------
async function sweep(file, clock, query) {
  const p = await open(file, {query}); const res = {lum: [], sat: [], bins: [], frames: {}};
  for (let i = 0; i < 100; i++) { const t = i / 10; const im = await p.at(clock(t)); const l = lumOf(im); res.lum.push(l); const h = hueStats(im); res.sat.push(h.sat); res.bins.push(h.bins); if ([8.2, 9.0].includes(+t.toFixed(1))) res.frames[t.toFixed(1)] = {im, l}; }
  await p.ctx.close(); return res;
}
const SN = await sweep(NEW, clockNew, '?still'), SF = await sweep(FIRST, clockFirst, '');
const blown = a => a.filter(x => x > .7).length, dark = a => a.filter(x => x < .01).length, avg = a => a.reduce((s, x) => s + x, 0) / a.length;
rec('no whiteout (frames >70% luminance of 100)', blown(SN.lum) <= 4 && blown(SN.lum) < blown(SF.lum), `new ${blown(SN.lum)} vs first ${blown(SF.lum)}`);
rec('never an empty/black frame (<1% luminance)', dark(SN.lum) === 0, `new ${dark(SN.lum)} vs first ${dark(SF.lum)}`);
rec('vivid neon (mean saturation of lit pixels)', avg(SN.sat) >= avg(SF.sat) && avg(SN.sat) > .25, `new ${avg(SN.sat).toFixed(2)} vs first ${avg(SF.sat).toFixed(2)}`);
rec('colourful shockwave (hue bins at 9.0s)', SN.bins[90] >= 4 && SN.bins[90] > SF.bins[90], `new ${SN.bins[90]} vs first ${SF.bins[90]}`);
rec('white-hot singularity read (brightest 8.0-8.4s)', Math.max(...SN.lum.slice(80, 85)) > .2, `new peak ${Math.max(...SN.lum.slice(80, 85)).toFixed(2)}`);
const oi = Math.round(T0 * 10) % 100, t0New = SN.lum[oi], t0First = SF.lum[0];
rec('first impression (opens lit + colourful)', t0New > .03 && SN.bins[oi] >= 3, `new first frame lum ${t0New.toFixed(2)}, bins ${SN.bins[oi]} vs first lum ${t0First.toFixed(2)}, bins ${SF.bins[0]}`);

// ---------- loop: period + seam ----------
{
  const p = await open(NEW, {query: '?still'});
  for (let i = 0; i < 80; i++) await p.raf(); // let camera parallax smoothing settle (not part of the loop)
  const A = await p.at(3000), B = await p.at(13000);
  rec('loop period is exactly 10s (3.0s vs 13.0s)', diff(A, B) < 1.0, `diff ${diff(A, B).toFixed(3)}`);
  const steps = []; for (const t of [0, 1.5, 3, 4.5, 6, 7.5, 8.3, 8.6, 9.2]) steps.push(diff(await p.at(clockNew(t)), await p.at(clockNew(t + 1 / 60))));
  const seam = diff(await p.at(clockNew(10 - 1 / 60)), await p.at(clockNew(0)));
  steps.sort((x, y) => x - y);
  rec('seamless: seam step within ordinary one-frame steps', seam <= steps[steps.length - 1], `seam ${seam.toFixed(2)} vs ordinary median ${steps[4].toFixed(2)}, max ${steps[8].toFixed(2)}`);
  await p.ctx.close();
}
// ---------- pointer: trail + bending, fades (same page, same loop phase, pointer present vs gone) ----------
async function pointerTest(file, offMs) {
  const p = await open(file, {W: 640, H: 360});
  for (let i = 0; i < 40; i++) {
    await p.evaluate(m => window.__set(m), offMs + i * 40);
    const a = i / 39; await p.mouse.move(150 + a * 340, 190 + Math.sin(a * 6.28) * 70); await p.raf();
  }
  const endMs = offMs + 39 * 40;
  const X = await p.at(endMs);                                   // pointer just moved: trail + well present
  await p.evaluate(() => document.documentElement.dispatchEvent(new Event('pointerleave')));
  const late = await p.at(endMs + 2600);                         // 2.6s later (pointer gone)
  for (let k = 1; k <= 12; k++) await p.at(endMs + k * 800);     // let well decay + trail expire
  const Y = await p.at(endMs + 10000), Y2 = await p.at(endMs + 20000); // same loop phase, clean
  const added = (A, B) => { let s = 0; for (let i = 0; i < A.data.length; i += 4) s += Math.max(0, A.data[i] - B.data[i]) + Math.max(0, A.data[i + 1] - B.data[i + 1]) + Math.max(0, A.data[i + 2] - B.data[i + 2]); return s / (A.data.length / 4 * 3); };
  const r = {now: added(X, Y), late: added(late, Y), noise: added(Y2, Y), changed: diff(X, Y)};
  await p.ctx.close(); return r;
}
const PN = await pointerTest(NEW, 3500), PF = await pointerTest(FIRST, 3500);
rec('pointer adds a glowing trail (light added vs pointer-free)', PN.now > 4 * PN.noise + 1, `+${PN.now.toFixed(2)} (noise ${PN.noise.toFixed(2)}); first version +${PF.now.toFixed(2)}`);
rec('trail fades away after the pointer leaves', PN.late < .35 * PN.now, `after 2.6s +${PN.late.toFixed(2)} (was +${PN.now.toFixed(2)})`);
rec('pointer changes the scene (orbits react)', PN.changed > 1.5, `frame diff ${PN.changed.toFixed(1)} (first ${PF.changed.toFixed(1)})`);

// ---------- reduced motion, resolution, device scaling, failure ----------
{
  const peak = async rm => { const p = await open(NEW, {query: '?still', ctxOpts: {reducedMotion: rm ? 'reduce' : 'no-preference'}}); let m = 0; for (let i = 0; i <= 10; i++) m = Math.max(m, lumOf(await p.at(clockNew(8.3 + i / 30)))); await p.ctx.close(); return m; };
  const pn = await peak(false), pr = await peak(true);
  rec('reduced-motion halves the flash', pr < pn * .5, `peak ${pn.toFixed(2)} -> ${pr.toFixed(2)}`);
  const core = async (W, H) => { const p = await open(NEW, {query: '?still', W, H}); const im = await p.at(clockNew(8.2)); await p.ctx.close(); let c = 0; const y = H >> 1; for (let x = 0; x < W; x++) { const i = (y * W + x) * 4; if ((im.data[i] + im.data[i + 1] + im.data[i + 2]) / 3 > 120) c++; } return c / Math.min(W, H); };
  const c1 = await core(640, 360), c2 = await core(1920, 1080), c3 = await core(390, 844);
  rec('climax same size on any screen (640/1920/390)', Math.max(c1, c2, c3) / Math.min(c1, c2, c3) < 1.15, `${c1.toFixed(2)} / ${c2.toFixed(2)} / ${c3.toFixed(2)} of shorter side`);
  const cnt = async mobile => { const p = await open(NEW, {query: '?still', ctxOpts: mobile ? {userAgent: 'Mozilla/5.0 (Linux; Android 13) Mobile Safari'} : {}}); const n = await p.evaluate(() => window.__neon.particles); await p.ctx.close(); return n; };
  const nd = await cnt(false), nm = await cnt(true);
  rec('particle count scales to device', nm < nd * .7, `desktop ${nd}, mobile ${nm}`);
  const p = await b.newPage(); await p.route('**/unpkg.com/**', r => r.abort()); await p.goto('file://' + NEW); await p.waitForTimeout(1500);
  const txt = (await p.innerText('body')).replace(/\s+/g, ' '); const live = await p.evaluate(() => document.documentElement.classList.contains('live'));
  rec('fails gracefully when CDN blocked', /Could not load/.test(txt) && !live, JSON.stringify(txt.slice(0, 50))); await p.close();
}
// ---------- hint contrast (cold read of the only copy) ----------
{
  const p = await open(NEW, {}); const c = await p.evaluate(() => { const h = document.getElementById('hint'); const s = getComputedStyle(h); return {color: s.color, op: +s.opacity, text: h.textContent}; });
  const [r, g, bl] = c.color.match(/\d+/g).map(Number); const bg = [2, 0, 10]; const f = [r, g, bl].map((v, i) => v * c.op + bg[i] * (1 - c.op));
  const L = a => .2126 * lin(a[0]) + .7152 * lin(a[1]) + .0722 * lin(a[2]); const ratio = (L(f) + .05) / (L(bg) + .05);
  rec('hint text contrast on the dark background >= 4.5:1', ratio >= 4.5, `${ratio.toFixed(1)}:1  "${c.text}"`); await p.ctx.close();
}
// ---------- quick frame-time (software rendering: rough only) ----------
async function fps(file, query) {
  const ctx = await b.newContext({viewport: {width: 640, height: 360}}); const p = await ctx.newPage(); await p.goto('file://' + file + query); await p.waitForTimeout(1500);
  const n = await p.evaluate(() => new Promise(r => { let k = 0; const t0 = Date.now(); const f = () => { k++; if (Date.now() - t0 > 3000) r(k / 3); else requestAnimationFrame(f); }; f(); })); await ctx.close(); return n;
}
const fn = await fps(NEW, '?still'), ff = await fps(FIRST, '');
console.log(`INFO frame rate in software rendering (rough, not a GPU number): new ${fn.toFixed(1)} fps vs first ${ff.toFixed(1)} fps`);
rec('no console/page errors', errors.length === 0, errors.length ? errors.slice(0, 3).join(' | ') : 'none');
await b.close();
console.log(`\n${out.filter(o => o.pass).length}/${out.length} checks pass`);
