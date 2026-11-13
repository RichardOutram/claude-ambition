// node redteam.js <html>: break/misuse checks
const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:(process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')});
const pg=await b.newPage({viewport:{width:375,height:667}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
const fresh=async()=>{await pg.goto('file://'+path.resolve(process.argv[2]));await pg.evaluate("S.authed=true;render()")};
let f=0;const t=(c,m)=>{console.log((c?'PASS ':'FAIL ')+m);if(!c)f++};
const txt=sel=>pg.evaluate(s=>document.querySelector(s)?.innerText||'',sel);
// 1 HTML injection via comment, ride title, club name
await fresh();await pg.evaluate("push('ride',1)");await pg.fill('#cin','<img src=x onerror="window.__x=1">hi');await pg.click('text=Send');await pg.waitForTimeout(150);
t(await pg.evaluate(()=>window.__x)===undefined&&(await txt('.screen')).includes('<img src=x'),'comment text is shown literally, not executed');
await fresh();await pg.evaluate("go('clubs')");await pg.click('text=+ New');await pg.fill('#cn','<b onmouseover=1>X</b>');await pg.click('text=Create club (free)');
t(!(await pg.evaluate(()=>!!document.querySelector('.screen b[onmouseover]'))),'club name cannot inject markup');
await fresh();await pg.evaluate("S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=3;S.rec.elev=10");await pg.evaluate("finishRide()");await pg.fill('#rt','<u id=pwn>t</u>');await pg.click('text=Save & share');await pg.waitForTimeout(300);await pg.evaluate("closeModal()");
t(!(await pg.evaluate(()=>!!document.getElementById('pwn'))),'ride title cannot inject markup');
// 2 very long names do not break layout
await fresh();await pg.evaluate("go('clubs')");await pg.click('text=+ New');await pg.evaluate("document.querySelector('#cn').removeAttribute('maxlength')");await pg.fill('#cn','W'.repeat(120));await pg.click('text=Create club (free)');await pg.waitForTimeout(100);
t(!(await pg.evaluate(()=>document.documentElement.scrollWidth>innerWidth||document.querySelector('.screen').scrollWidth>document.querySelector('.screen').clientWidth)),'120-char club name does not overflow horizontally');
t((await pg.evaluate(()=>document.querySelector('#cn')===null)),'(club form closed)');
// 3 discard needs confirmation and Keep restores
await fresh();await pg.evaluate("S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=3;S.rec.elev=10");await pg.evaluate("finishRide()");await pg.click('text=Discard');
t(/can.t be recovered/.test(await txt('.modal'))&&(await pg.evaluate(()=>S.rides.length))===4,'Discard asks for confirmation first');
await pg.click('text=Keep ride');t((await txt('.modal')).includes('Save & share'),'Keep ride returns to the summary');
// 4 privacy zone off warns
await fresh();await pg.evaluate("openSettings()");await pg.locator('.modal .chip').first().click();
t(/home/i.test(await txt('.modal'))&&(await pg.evaluate(()=>S.set.zone))===true,'turning off privacy zone warns first and is not yet off');
// 5 paywall discloses price after trial + has Not now
await pg.evaluate("closeModal();openPaywall()");const pw=await txt('.modal');
t(/then \$5\.99/i.test(pw)&&/cancel/i.test(pw),'paywall states price after trial and how to cancel');t(/Not now/.test(pw),'paywall has an explicit Not now');
// 6 sign out blocked while recording
await fresh();await pg.evaluate("S.tab='record';render();startRide();go('profile')");await pg.click('text=Sign out');
t((await pg.evaluate(()=>S.authed))===true,'cannot sign out mid-ride');
// 7 safety copy
await pg.evaluate("S.rec.state='idle';clearInterval(S.rec.timer);S.stack=[{v:'segment',id:2}];render()");t(/public roads/i.test(await txt('.screen')),'segment screen carries a public-road safety note');
await pg.evaluate("explain('streak')");t(/rest|sick|injured/i.test(await txt('.modal')),'streak explainer says rest is OK');
// 8 session log: taps, milestones, pauses, no typed text
await fresh();await pg.evaluate("S.authed=false;render()");await pg.locator('.phone').getByRole('button',{name:'Sign in',exact:true}).click();await pg.locator('.phone').getByText('Look around first').click();
await pg.evaluate("go('record')");await pg.getByRole('button',{name:'Start ride'}).click();await pg.waitForTimeout(2500);await pg.evaluate("S.rec.sec=600;S.rec.km=3");await pg.evaluate("finishRide()");await pg.fill('#rt','SECRETTITLE');await pg.click('text=Save & share');await pg.click('text=See my challenges');
await pg.evaluate("openSettings()");await pg.click('text=Session log');const lg=await txt('.modal');
t(/signed in/.test(lg)&&/ride started/.test(lg)&&/ride saved/.test(lg)&&/challenges viewed/.test(lg),'session log has core-loop milestones');
t(/Core loop/.test(lg)&&/startRide|Start/.test(lg),'session log has total time and taps');
t(!/SECRETTITLE/.test(lg),'session log contains no typed text');
// 9 next-up on summary
await fresh();await pg.evaluate("S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=3;S.rec.elev=10");await pg.evaluate("finishRide()");await pg.click('text=Save & share');
t(/Next up/.test(await txt('.modal')),'post-ride sheet shows Next up');
t(errs.length===0,'no page errors '+errs.join());
await b.close();process.exit(f?1:0)})();
