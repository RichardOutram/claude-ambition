import puppeteer from 'puppeteer-core';
const url = 'file://' + process.argv[2];
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
for (const [w, h] of [[1440, 800], [1280, 720], [1366, 640], [390, 844], [375, 667]]) {
  const p = await b.newPage();
  await p.setViewport({ width: w, height: h });
  await p.goto(url);
  const r = await p.evaluate(() => {
    const solo = document.querySelector('.plan.featured');
    const price = solo.querySelector('.price').getBoundingClientRect().bottom;
    const cta = solo.querySelector('.btn').getBoundingClientRect().bottom;
    const promises = solo.querySelector('.promises').getBoundingClientRect().top;
    return { price: Math.round(price), cta: Math.round(cta), promises: Math.round(promises) };
  });
  console.log(`${w}x${h}: solo price bottom=${r.price} cta bottom=${r.cta} -> ${r.cta <= h ? 'CTA above fold' : 'CTA BELOW fold'}${r.price > h ? ' (price too)' : ''}`);
  await p.close();
}
// consistency: collect every sentence about cancel/export/fees
const p = await b.newPage();
await p.goto(url);
const txt = await p.evaluate(() => document.body.innerText);
for (const k of ['cancel', 'export', 'refund', '2.9%', 'clients']) {
  const lines = txt.split('\n').filter(l => l.toLowerCase().includes(k));
  console.log(`\n[${k}] ${lines.length} mentions`);
  lines.forEach(l => console.log('  ' + l.slice(0, 140)));
}
await b.close();
