import puppeteer from 'puppeteer-core';
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const url = 'file:///Volumes/My Shared Files/work/pricing.html';
const out = '/Volumes/My Shared Files/work/.ambition/render/';
async function shot(name, w, h, scheme, clip) {
  const p = await b.newPage();
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width: w, height: h });
  await p.goto(url);
  await p.screenshot({ path: out + name, clip: { x: 0, y: clip[0], width: w, height: clip[1] } });
  await p.close();
}
await shot('j_desk_light.png', 1280, 900, 'light', [380, 1250]);
await shot('j_desk_dark.png', 1280, 900, 'dark', [1500, 1250]);
await shot('j_mob_light.png', 390, 900, 'light', [560, 1250]);
await shot('j_mob_dark.png', 390, 900, 'dark', [1900, 1250]);
await b.close();
