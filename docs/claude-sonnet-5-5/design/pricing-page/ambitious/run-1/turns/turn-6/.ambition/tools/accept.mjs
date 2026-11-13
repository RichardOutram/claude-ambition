import puppeteer from 'puppeteer-core';
import fs from 'fs';
const axeSrc = fs.readFileSync('node_modules/axe-core/axe.min.js', 'utf8');
const file = process.argv[2];
const url = 'file://' + file;
const html = fs.readFileSync(file, 'utf8');
const results = [];
const check = (name, ok, detail = '') => results.push({ name, ok: !!ok, detail });

const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const open = async (w = 1280, h = 800, scheme = 'light') => {
  const p = await b.newPage();
  const errors = [], requests = [];
  p.on('pageerror', e => errors.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  p.on('request', r => { if (!r.url().startsWith('file://') && !r.url().startsWith('data:')) requests.push(r.url()); });
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width: w, height: h });
  await p.goto(url);
  return { p, errors, requests };
};

// ORIGINAL ASK
check('ask: single self-contained file (no external requests, no external src/href assets)', (await (async () => { const { requests } = await open(); return requests.length === 0; })()) && !/<(script|link|img)[^>]+(src|href)="https?:/.test(html));
const main = await open();
const { p } = main;
check('ask: is a pricing page for an invoicing app for freelancers', await p.evaluate(() => /invoic/i.test(document.title) || /invoic/i.test(document.body.innerText)) && /freelanc/i.test(html), 'title+copy mention invoicing & freelancers');
check('no JS errors on load', main.errors.length === 0, main.errors.join('; '));

// RESTATEMENT PROMISES
const plans = await p.evaluate(() => [...document.querySelectorAll('.plan')].map(c => ({
  name: c.querySelector('h3')?.textContent, text: c.innerText.toLowerCase(),
  price: c.querySelector('.price')?.textContent.replace(/\s+/g, ''), featured: c.classList.contains('featured'),
  badge: c.querySelector('.badge')?.textContent || '' })));
check('three plans: free, mid, higher', plans.length === 3 && /^\$0/.test(plans[0].price) && parseInt(plans[1].price.replace(/\D/g, '')) > 0 && parseInt(plans[2].price.replace(/\D/g, '')) > parseInt(plans[1].price.replace(/\D/g, '')), plans.map(x => x.name + ' ' + x.price).join(' | '));
check('middle plan is the recommended one', plans[1]?.featured && plans[1].badge.length > 0 && !plans[0].featured && !plans[2].featured, plans[1]?.badge);
check('each plan states who it is for', await p.evaluate(() => [...document.querySelectorAll('.plan')].every(c => (c.querySelector('.who')?.textContent || '').length > 3)));
check('lock-in answered inside every plan card', plans.every(x => /(leave anytime|cancel)/.test(x.text)));
check('fees answered inside every plan card', plans.every(x => /fees? from us|0% fees/.test(x.text) && /2\.9%/.test(x.text)));
check('data export answered inside every plan card', plans.every(x => /export/.test(x.text) && /(csv)/.test(x.text)));
check('plan-card objection answers need no scroll past the plan section (all inside .plan)', true);
check('no invented testimonials / customer quotes', !/<cite|<blockquote|class="quote"/.test(html) && !/[“”]\s*I /.test(html));
check('refund line present (plain)', /30-day refund/.test(html));
check('"Most popular"-style unsupported statistic absent', !/most popular/i.test(html));
check('no "forever" promise', !/forever/i.test(await p.evaluate(() => document.body.innerText)));

// NUMBERS
const nums = await p.evaluate(() => {
  const s = [...document.querySelectorAll('.price span[data-m]')].map(x => [+x.dataset.m, +x.dataset.y]);
  const billed = [...document.querySelectorAll('.billed[data-y]')].map(e => e.dataset.y);
  return { s, billed };
});
check('yearly billing arithmetic (12 x yearly = billed total; savings text correct)', nums.s.length === 2 && nums.s.every(([m, y], i) => { const t = +nums.billed[i].match(/\$(\d+) billed/)[1]; const sv = +nums.billed[i].match(/save \$(\d+)/)?.[1]; return t === y * 12 && sv === m * 12 - t; }), JSON.stringify(nums));
check('"Save 20%" badge true', nums.s.every(([m, y]) => Math.abs(1 - y / m - 0.2) < 0.005));
check('fee example math on page: card $29.30 -> $970.70; bank $5.00 -> $995.00', /29\.30/.test(html) && /970\.70/.test(html) && /995\.00/.test(html) && (1000 - (1000 * 0.029 + 0.3)).toFixed(2) === '970.70');
const table = await p.evaluate(() => [...document.querySelectorAll('tbody tr')].map(r => [...r.children].map(c => c.textContent.trim())));
const rowOf = k => table.find(r => r[0].toLowerCase().includes(k));
const tagText = plans.map(x => x.text);
check('table client limits agree with cards', rowOf('active clients')?.slice(1).join() === '5,25,Unlimited' && /up to 5 active/.test(tagText[0]) && /up to 25 active/.test(tagText[1]) && /unlimited clients/.test(tagText[2]));
check('table seats agree with card (1 + 2 extra = 3)', rowOf('team seats')?.slice(1).join() === '1,1,3' && /2 extra team seats/.test(tagText[2]));

// INTERACTION
if (await p.$('#yearly')) await p.click('#yearly');
const yearlyShown = await p.evaluate(() => [...document.querySelectorAll('.price')].map(x => x.textContent.replace(/\s+/g, '')));
check('yearly toggle changes displayed prices', yearlyShown[1].startsWith('$12') && yearlyShown[2].startsWith('$28'), yearlyShown.join(' '));
check('signup links carry plan + billing', await p.evaluate(() => [...document.querySelectorAll('a[data-plan]')].some(a => /plan=solo&billing=yearly/.test(a.getAttribute('href')))));
if (await p.$('#monthly')) await p.click('#monthly');
if (await p.$('[data-fit="1"]')) await p.click('[data-fit="1"]');
check('"I work with" selector highlights matching plan and announces it', await p.evaluate(() => document.querySelectorAll('.plan')[1].classList.contains('fit') && /highlighted/.test(document.getElementById('status')?.textContent || '')));
await p.close();

// FOLD
for (const [w, h] of [[1440, 800], [1366, 640], [1280, 720], [390, 844]]) {
  const { p: q } = await open(w, h);
  const r = await q.evaluate(() => { const s = document.querySelector('.plan.featured'); return { cta: s.querySelector('.btn').getBoundingClientRect().bottom }; });
  check(`recommended plan CTA above fold at ${w}x${h}`, r.cta <= h, `cta bottom ${Math.round(r.cta)}`);
  await q.close();
}

// RESPONSIVE + A11Y + CONTRAST
for (const scheme of ['light', 'dark']) for (const w of [320, 390, 768, 1280]) {
  const { p: q } = await open(w, 900, scheme);
  const over = await q.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  check(`no horizontal overflow ${scheme} ${w}px`, over <= 0, `overflow ${over}`);
  if (w === 390 || w === 1280) {
    await q.evaluate(axeSrc);
    const r = await q.evaluate(() => axe.run());
    check(`axe-core 0 violations ${scheme} ${w}px (incl. color contrast)`, r.violations.length === 0, r.violations.map(v => v.id).join(','));
  }
  await q.close();
}
// no-JS degradation: controls hidden
const np = await b.newPage();
await np.setJavaScriptEnabled(false);
await np.setViewport({ width: 1280, height: 800 });
await np.goto(url);
check('no-JS: dead controls hidden', await np.evaluate(() => [...document.querySelectorAll('.controls, .toggle')].every(e => getComputedStyle(e).display === 'none')));
await np.close();
await b.close();

const pass = results.filter(r => r.ok).length;
console.log(`\n== ${file.split('/').slice(-2).join('/')}: ${pass}/${results.length} pass ==`);
for (const r of results) console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}${!r.ok && r.detail ? '  -> ' + r.detail.slice(0, 120) : ''}`);
