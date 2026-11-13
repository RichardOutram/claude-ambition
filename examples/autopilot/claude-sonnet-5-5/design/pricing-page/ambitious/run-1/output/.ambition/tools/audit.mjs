import puppeteer from 'puppeteer-core';
import fs from 'fs';
const axeSrc = fs.readFileSync('node_modules/axe-core/axe.min.js', 'utf8');
const url = 'file://' + process.argv[2];
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
for (const scheme of ['light', 'dark']) for (const w of [320, 390, 768, 1280]) {
  const p = await b.newPage();
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width: w, height: 900 });
  await p.goto(url);
  const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  let line = `${scheme} ${w}px overflow=${over}`;
  if (w === 390 || w === 1280) {
    await p.evaluate(axeSrc);
    const r = await p.evaluate(() => axe.run());
    line += ` axe violations=${r.violations.length}`;
    for (const v of r.violations) line += `\n   - ${v.id}: ${v.help} (${v.nodes.length} nodes) e.g. ${v.nodes[0].target}`;
  }
  console.log(line);
  await p.close();
}
const p = await b.newPage();
await p.goto(url);
const out = await p.evaluate(() => {
  const spans = [...document.querySelectorAll('.price span[data-m]')].map(s => [+s.dataset.m, +s.dataset.y]);
  const billed = [...document.querySelectorAll('.billed[data-y]')].map(e => +e.dataset.y.replace(/\D/g, ''));
  return { spans, billed };
});
out.spans.forEach(([m, y], i) => console.log(`monthly $${m}, yearly $${y}/mo, billed $${out.billed[i]} -> expected ${y * 12}, discount ${(100 - 100 * y / m).toFixed(1)}%`));
console.log('card fee on 1000:', (1000 * 0.029 + 0.30).toFixed(2), ' ach:', Math.min(1000 * 0.008, 5).toFixed(2));
await b.close();
