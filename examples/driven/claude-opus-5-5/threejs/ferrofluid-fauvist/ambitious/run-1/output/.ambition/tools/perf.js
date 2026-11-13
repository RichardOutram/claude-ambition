// Real-clock frame timing: rAF interval stats over 6 s at CPU throttle 1x and 4x.
// usage: node perf.js file.html [w h dpr]
const puppeteer = require('puppeteer-core');
const path = require('path');
const [file, w = 1280, h = 800, dpr = 2] = process.argv.slice(2);
(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--use-angle=metal', '--ignore-gpu-blocklist', '--enable-gpu'],
  });
  for (const rate of [1, 4]) {
    const page = await browser.newPage();
    await page.setViewport({ width: +w, height: +h, deviceScaleFactor: +dpr });
    const cdp = await page.createCDPSession();
    await cdp.send('Emulation.setCPUThrottlingRate', { rate });
    await page.goto('file://' + path.resolve(file), { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 1500));
    const s = await page.evaluate(() => new Promise(res => {
      const d = []; let last = performance.now(); const end = last + 6000;
      const f = (t) => { d.push(t - last); last = t; if (t < end) requestAnimationFrame(f); else res(d); };
      requestAnimationFrame(f);
    }));
    s.sort((a, b) => a - b);
    const q = p => s[Math.min(s.length - 1, Math.floor(p * s.length))].toFixed(1);
    console.log(`cpu x${rate}: ${s.length} frames in 6s (${(s.length / 6).toFixed(1)} fps)  p50 ${q(.5)}ms  p95 ${q(.95)}ms  p99 ${q(.99)}ms  max ${s[s.length - 1].toFixed(1)}ms  >25ms: ${s.filter(x => x > 25).length}`);
    await page.close();
  }
  await browser.close();
})();
