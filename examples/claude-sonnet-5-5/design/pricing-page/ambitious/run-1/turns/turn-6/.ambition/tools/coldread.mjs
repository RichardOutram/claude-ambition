import puppeteer from 'puppeteer-core';
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const p = await b.newPage();
await p.setViewport({ width: 1280, height: 800 });
await p.goto('file://' + process.argv[2]);
await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
console.log(await p.evaluate(() => document.body.innerText.replace(/\n{2,}/g, '\n')));
await b.close();
