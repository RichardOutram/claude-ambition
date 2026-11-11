// Captures what a reviewer needs to judge a page or an animation, the same way for every arm.
// Runs inside the bench container: node capture.mjs <site-dir> <page> <out-dir> <seconds>
// Time is virtual and stepped at 15 fps, so frame t=4s really is 4 seconds into the animation,
// however slow the software renderer is. Writes frames, a seam score and console errors to out-dir.
import { chromium } from "/node/node_modules/playwright/index.mjs";
import { PNG } from "/node/node_modules/pngjs/lib/png.js";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const [site, page, out, secondsArg] = process.argv.slice(2);
const seconds = Number(secondsArg || 10);
const STEP = 1;  // seconds between frames
const TICK = 1000 / 15;  // virtual ms per rendered frame: small enough for per-frame physics, half the work of 30 fps
const VIEWS = { desktop: { width: 1280, height: 800, deviceScaleFactor: 1 },
                phone: { width: 390, height: 844, deviceScaleFactor: 1, isMobile: true, hasTouch: true } };  // 1x: layout and motion, at a quarter of the pixels; crispness is checked live
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
                ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
                ".glsl": "text/plain", ".wasm": "application/wasm" };

const server = http.createServer((req, res) => {
  const file = path.join(site, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(site) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
}).listen(0);
const url = `http://127.0.0.1:${server.address().port}/${page.split("/").map(encodeURIComponent).join("/")}`;

// Percent of pixels that visibly changed between two PNG frames (by more than 40 of 255).
// Grain and particle shimmer change many pixels slightly; a jump moves things, which changes pixels a lot.
function diff(a, b) {
  const x = PNG.sync.read(a), y = PNG.sync.read(b);
  if (x.width !== y.width || x.height !== y.height) return 100;
  let changed = 0;
  for (let i = 0; i < x.data.length; i += 4)
    if ((Math.abs(x.data[i] - y.data[i]) + Math.abs(x.data[i + 1] - y.data[i + 1]) + Math.abs(x.data[i + 2] - y.data[i + 2])) / 3 > 40) changed++;
  return +(100 * changed / (x.data.length / 4)).toFixed(3);
}

const browser = await chromium.launch({ args: ["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const report = { url: page, seconds, views: {} };
fs.mkdirSync(out, { recursive: true });
// Both sizes at once: software rendering is CPU-bound and the container has cores to spare.
await Promise.all(Object.entries(VIEWS).map(async ([name, view]) => {
  const ctx = await browser.newContext({ viewport: { width: view.width, height: view.height }, ...view });
  const p = await ctx.newPage();
  const errors = [];
  p.on("console", m => m.type() === "error" && errors.push(m.text().slice(0, 300)));
  p.on("pageerror", e => errors.push(String(e).slice(0, 300)));
  // Virtual time: the page's clocks read a time we step in 1/30 s increments, while real animation
  // frames keep running so screenshots work. Anything that integrates per-frame deltas stays faithful.
  await p.addInitScript(TICK => {
    let vt = 0;
    const realRAF = window.requestAnimationFrame.bind(window), d0 = Date.now();
    performance.now = () => vt;
    Date.now = () => d0 + vt;
    window.requestAnimationFrame = cb => realRAF(() => cb(vt));
    window.__advanceTo = async target => {
      while (vt < target - 1e-3) {
        vt = Math.min(target, vt + TICK);
        await new Promise(r => realRAF(() => realRAF(r)));
      }
      vt = target;  // land exactly on the sample time: float drift would otherwise stop a hair short of it
      await new Promise(r => realRAF(() => realRAF(r)));
    };
  }, TICK);
  await p.goto(url, { waitUntil: "domcontentloaded" });
  await p.waitForTimeout(4000);  // real time, for modules and textures to arrive; virtual time stays at 0
  const frames = [];
  for (let t = 0; t <= seconds + 1e-9; t += STEP) {
    await p.evaluate(ms => window.__advanceTo(ms), t * 1000);
    const png = await p.screenshot();
    const file = `${name}-t${String(t).padStart(2, "0")}.png`;
    fs.writeFileSync(path.join(out, file), png);
    frames.push({ t, file, png });
  }
  const moving = frames.slice(1).some((f, i) => diff(frames[i].png, f.png) > 0.1);
  const steps = frames.slice(1).map((f, i) => diff(frames[i].png, f.png));
  report.views[name] = {
    frames: frames.map(f => ({ t: f.t, file: f.file })),
    moving,
    // A seamless loop ends where it began: compare the last frame with the first, against a typical step.
    seam: moving ? { first_vs_last: diff(frames[0].png, frames.at(-1).png), median_step: steps.sort((a, b) => a - b)[Math.floor(steps.length / 2)] } : null,
    errors,
  };
  await ctx.close();
}));
await browser.close();
server.close();
fs.writeFileSync(path.join(out, "capture.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(Object.fromEntries(Object.entries(report.views).map(([k, v]) => [k, { moving: v.moving, seam: v.seam, errors: v.errors.length }]))));
