// Captures what a reviewer needs to judge a page or an animation, the same way for every arm.
// Runs inside the bench VM or container: node capture.mjs <site-dir> <page> <out-dir> <seconds> [walk.json]
// With a walk file (the example's **Walk:** from PROMPTS.md, parsed by ab.py), it also clicks through that fixed
// path in real time and screenshots each step into walk.json. Seconds 0 skips the frames and does only the walk.
// Time is virtual and stepped at 60 fps, so frame t=4s really is 4 seconds into the animation,
// however fast or slow the renderer is. Writes frames, a seam score and console errors to out-dir.
// The page plays one whole loop before the frames are taken, so trails and other effects that build up
// over time have the same history at both ends of the seam check. Frame t=4s is 4 seconds into loop 2.
// Playwright comes from /node: the full package in the container, playwright-core in the macOS VM, where the
// installed Chrome is used (CAPTURE_CHANNEL=chrome) so WebGL runs on the GPU.
const { chromium } = await import(process.env.PLAYWRIGHT || "/node/node_modules/playwright/index.mjs");
import { PNG } from "/node/node_modules/pngjs/lib/png.js";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const [site, page, out, secondsArg, walkFile] = process.argv.slice(2);
const seconds = Number(secondsArg ?? 10);
const walk = walkFile ? JSON.parse(fs.readFileSync(walkFile, "utf8")) : null;
const STEP = 1;  // seconds between frames
const TICK = 1000 / 60;  // virtual ms per rendered frame: what a page sees in a real browser, so pages that adapt their quality to frame time stay at full quality
const VIEWS = { desktop: { width: 1280, height: 800, deviceScaleFactor: 1 },
                phone: { width: 390, height: 844, deviceScaleFactor: 1, isMobile: true, hasTouch: true } };  // 1x: layout and motion, at a quarter of the pixels; crispness is checked live
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
                ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
                ".glsl": "text/plain", ".wasm": "application/wasm" };

const server = http.createServer((req, res) => {
  const file = path.join(site, decodeURIComponent(new URL(req.url, "http://x").pathname));
  // Chrome asks for a favicon the page never named; a 404 there would count as a page error.
  if (req.url === "/favicon.ico" && !fs.existsSync(file)) { res.writeHead(204); return res.end(); }
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

const channel = process.env.CAPTURE_CHANNEL;
const browser = await chromium.launch({ ...(channel ? { channel } : {}), args: ["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const report = { url: page, seconds, views: {} };
fs.mkdirSync(out, { recursive: true });
// Both sizes at once: software rendering is CPU-bound and the container has cores to spare.
if (seconds > 0) await Promise.all(Object.entries(VIEWS).map(async ([name, view]) => {
  const ctx = await browser.newContext({ viewport: { width: view.width, height: view.height }, ...view });
  const p = await ctx.newPage();
  const errors = [];
  p.on("console", m => m.type() === "error" && errors.push(m.text().slice(0, 300)));
  p.on("pageerror", e => errors.push(String(e).slice(0, 300)));
  // Virtual time: the page's clocks read a time we step in 1/60 s increments, while real animation
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
    // Half a tick past the second: a sample exactly on the loop boundary can land a rounding error either
    // side of it, where some pages have a float edge a real viewer never hits.
    await p.evaluate(ms => window.__advanceTo(ms), (seconds + t) * 1000 + TICK / 2);
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

// The walk: the same fixed path on every version, in real time (no virtual clock), one screenshot per step.
// A click step tries each alternative in turn and clicks the first visible control whose name contains it.
async function findControl(p, alts) {
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  for (const alt of alts) {
    const re = new RegExp(esc(alt), "i");
    const pools = [...["button", "link", "tab", "menuitem", "radio", "option"].map(role => p.getByRole(role, { name: re })), p.getByText(re)];
    for (const loc of pools) {
      const n = Math.min(await loc.count(), 25);
      for (let i = 0; i < n; i++) {
        const el = loc.nth(i);
        if (await el.isVisible().catch(() => false)) return { el, alt };
      }
    }
  }
  return null;
}
if (walk) {
  const view = VIEWS[walk.view] || VIEWS.desktop;
  const ctx = await browser.newContext({ viewport: { width: view.width, height: view.height }, ...view });
  const p = await ctx.newPage();
  const errors = [];
  p.on("console", m => m.type() === "error" && errors.push(m.text().slice(0, 300)));
  p.on("pageerror", e => errors.push(String(e).slice(0, 300)));
  p.on("dialog", d => d.accept().catch(() => {}));
  await p.goto(url, { waitUntil: "domcontentloaded" });
  await p.waitForTimeout(2500);
  const steps = [];
  const shot = async (i, step, did) => {
    const file = `walk-${String(i).padStart(2, "0")}.png`;
    fs.writeFileSync(path.join(out, file), await p.screenshot());
    steps.push({ i, label: step.label, did, file });
  };
  await shot(0, { label: "Opened" }, "opened");
  for (const [k, step] of walk.steps.entries()) {
    let did = "";
    try {
      if (step.click) {
        const clicked = [];
        for (let n = 0; n < (step.times || 1); n++) {
          const hit = await findControl(p, step.click);
          if (!hit) break;
          await hit.el.scrollIntoViewIfNeeded().catch(() => {});
          await hit.el.click({ timeout: 2500 }).catch(() => hit.el.click({ force: true, timeout: 2500 }));
          clicked.push(`“${hit.alt}”`);
          await p.waitForTimeout(600);
        }
        if (!clicked.length) { steps.push({ i: k + 1, label: step.label, did: "not in this version", file: null }); continue; }
        did = `clicked ${clicked.join(", then ")}`;
      } else if (step.key) {
        for (let n = 0; n < step.times; n++) { await p.keyboard.press(step.key); await p.waitForTimeout(250); }
        did = `pressed ${step.key}${step.times > 1 ? ` ×${step.times}` : ""}`;
      } else if (step.scroll) {
        await p.mouse.wheel(0, view.height * 0.9);
        did = "scrolled one screen";
      } else if (step.wait) {
        await p.waitForTimeout(step.wait * 1000);
        did = `waited ${step.wait} s`;
      }
    } catch (err) {
      did = `failed: ${String(err).split("\n")[0].slice(0, 120)}`;
    }
    await p.waitForTimeout(900);  // let transitions finish
    await shot(k + 1, step, did);
  }
  fs.writeFileSync(path.join(out, "walk.json"), JSON.stringify({ view: walk.view, steps, errors }, null, 2));
  await ctx.close();
}
await browser.close();
server.close();
if (seconds > 0) fs.writeFileSync(path.join(out, "capture.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(Object.fromEntries(Object.entries(report.views).map(([k, v]) => [k, { moving: v.moving, seam: v.seam, errors: v.errors.length }]))));
