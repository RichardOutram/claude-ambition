import puppeteer from 'puppeteer-core';
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
let allOk = true;
for (const [w, h, need] of [[1366, 640, 'promises'], [375, 667, 'cta'], [390, 844, 'cta'], [1280, 720, 'promises']]) {
  const p = await b.newPage();
  await p.setViewport({ width: w, height: h });
  await p.goto('file://' + process.argv[2]);
  const r = await p.evaluate(() => {
    const s = document.querySelector('.plan.featured');
    const lis = [...s.querySelectorAll('.promises li')];
    return { cta: s.querySelector('.btn').getBoundingClientRect().bottom, promises: lis.at(-1).getBoundingClientRect().bottom };
  });
  const val = need === 'promises' ? r.promises : r.cta;
  const ok = val <= h;
  allOk &&= ok;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${w}x${h}: need ${need} bottom <= ${h}; cta=${Math.round(r.cta)} last promise=${Math.round(r.promises)}`);
  await p.close();
}
await b.close();
console.log(allOk ? 'STRETCH MET' : 'STRETCH NOT MET');
