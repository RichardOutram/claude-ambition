// Usage: node audit.js <path-to-html>
// Dead-tap audit: for every screen state, click each [onclick] control (fresh page each time)
// and flag it if nothing observable changes. Also flags <button>s with no handler and console errors.
const { chromium } = require('playwright-core');
const path = require('path');
const file = path.resolve(process.argv[2]);
const CHROME = process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const STATES = {
  'auth': `S.authed=false;render()`,
  'feed': `S.authed=true;S.tab='feed';S.stack=[];render()`,
  'feed-club': `S.authed=true;S.tab='feed';S.feedFilter='Club';S.stack=[];render()`,
  'ride': `S.authed=true;S.stack=[{v:'ride',id:1}];render()`,
  'ride-pro': `S.authed=true;S.pro=true;S.stack=[{v:'ride',id:1}];render()`,
  'segment': `S.authed=true;S.stack=[{v:'segment',id:1}];render()`,
  'record-idle': `S.authed=true;S.tab='record';S.stack=[];render()`,
  'record-running': `S.authed=true;S.tab='record';S.stack=[];startRide()`,
  'challenges-active': `S.authed=true;S.tab='challenges';S.stack=[];render()`,
  'challenges-discover': `S.authed=true;S.tab='challenges';S.chTab='Discover';S.stack=[];render()`,
  'clubs': `S.authed=true;S.tab='clubs';S.stack=[];render()`,
  'club-joined': `S.authed=true;S.tab='clubs';S.stack=[{v:'club',id:1}];render()`,
  'club-joined-pro': `S.authed=true;S.pro=true;S.tab='clubs';S.stack=[{v:'club',id:1}];render()`,
  'club-notjoined': `S.authed=true;S.tab='clubs';S.stack=[{v:'club',id:2}];render()`,
  'profile': `S.authed=true;S.tab='profile';S.stack=[];render()`,
  'profile-pro': `S.authed=true;S.pro=true;S.tab='profile';S.stack=[];render()`,
};
const snap = () => document.querySelector('.phone').innerHTML.replace(/<span id="clock">[^<]*<\/span>/, '');

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  const errors = [];
  const dead = [];
  let total = 0;
  const open = async (state) => {
    const page = await browser.newPage({ viewport: { width: 500, height: 900 } });
    page.on('pageerror', e => errors.push(`${state}: ${e.message}`));
    page.on('console', m => { if (m.type() === 'error') errors.push(`${state}: console ${m.text()}`); });
    await page.goto('file://' + file);
    await page.evaluate(STATES[state]);
    return page;
  };
  for (const state of Object.keys(STATES)) {
    let page = await open(state);
    const n = await page.evaluate(() => document.querySelectorAll('.phone [onclick]').length);
    const bare = await page.evaluate(() => [...document.querySelectorAll('.phone button:not([onclick])')].map(b => b.textContent.trim()));
    bare.forEach(t => dead.push(`${state}: <button> with no handler: "${t}"`));
    await page.close();
    for (let i = 0; i < n; i++) {
      total++;
      page = await open(state);
      const label = await page.evaluate(i => {
        const el = document.querySelectorAll('.phone [onclick]')[i];
        return (el.textContent || '').trim().slice(0, 30) + ' | ' + el.getAttribute('onclick').slice(0, 50);
      }, i);
      const before = await page.evaluate(snap);
      await page.evaluate(i => document.querySelectorAll('.phone [onclick]')[i].click(), i);
      await page.waitForTimeout(60);
      const after = await page.evaluate(snap);
      if (before === after) dead.push(`${state}: DEAD "${label}"`);
      await page.close();
    }
  }
  console.log(`Clickable controls tested: ${total}`);
  console.log(`Console/page errors: ${errors.length}`); errors.forEach(e => console.log('  ' + e));
  console.log(`Dead taps: ${dead.length}`); dead.forEach(d => console.log('  ' + d));
  await browser.close();
  process.exit(dead.length || errors.length ? 1 : 0);
})();
