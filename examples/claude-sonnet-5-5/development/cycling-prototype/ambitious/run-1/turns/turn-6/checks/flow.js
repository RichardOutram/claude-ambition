// Usage: node flow.js <path-to-html>
// Cold-start click-through of the core loop using real clicks on visible text only.
const { chromium } = require('playwright-core');
const path = require('path');
const file = path.resolve(process.argv[2]);
const CHROME = process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
let fails = 0;
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  const page = await browser.newPage({ viewport: { width: 420, height: 880 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await page.goto('file://' + file);
  const phone = page.locator('.phone');
  const has = async t => (await phone.getByText(t, { exact: false }).count()) > 0;
  const click = async (t, opt = {}) => { await phone.getByText(t, { exact: opt.exact ?? false }).first().click(); await page.waitForTimeout(120); };

  ok(await has('Sign in'), 'cold start shows sign in');
  await click('Sign in', { exact: true });
  ok(await has('What do you ride'), 'onboarding appears');
  ok(await has('Start my first ride'), 'onboarding offers Start my first ride');
  await click('Look around first');
  ok(await has('Feed'), 'lands on feed');
  const xp0 = await page.evaluate(() => S.me.xp);
  const rides0 = await page.evaluate(() => S.rides.length);
  await phone.locator('.tab.rec').click();
  ok(await has('Start ride'), 'record screen with Start ride');
  await phone.getByRole('button',{name:'Start ride'}).click();await page.waitForTimeout(120);
  await page.waitForTimeout(3200);
  ok((await phone.locator('#bt').textContent()) !== '0:00:00', 'timer is ticking');
  await click('Finish');
  ok(await has('Ride complete'), 'finish shows summary');
  await click('Save & share');
  ok(await has('XP'), 'XP award shown');
  ok(await has('Badge unlocked'), 'badge unlock shown');
  await page.waitForTimeout(500);
  await page.evaluate(() => closeModal());
  const xp1 = await page.evaluate(() => S.me.xp);
  ok(xp1 > xp0, `XP increased (${xp0} -> ${xp1})`);
  ok((await page.evaluate(() => S.rides.length)) === rides0 + 1, 'ride added to feed');
  await click('Challenges');
  ok(await has('Weekly 150 km'), 'challenge visible');
  const prog = await page.evaluate(() => S.challenges[0].val);
  ok(prog > 96, `challenge progress updated (96 -> ${prog.toFixed ? prog.toFixed(1) : prog})`);
  ok(errs.length === 0, `no console errors (${errs.join('; ')})`);
  await browser.close();
  process.exit(fails ? 1 : 0);
})();
