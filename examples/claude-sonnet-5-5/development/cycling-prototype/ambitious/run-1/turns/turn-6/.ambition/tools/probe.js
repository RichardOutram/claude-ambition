const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:375,height:667}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
const fresh=async()=>{await pg.goto('file://'+path.resolve(process.argv[2]));await pg.evaluate("S.authed=true;render()")};
let f=0;const t=(c,m)=>{console.log((c?'PASS ':'FAIL ')+m);if(!c)f++};
// 1 immediate finish
await fresh();await pg.evaluate("S.tab='record';render();startRide()");await pg.evaluate("finishRide()");
let txt=await pg.evaluate(()=>document.querySelector('.modal')?.textContent||'');
t(!/0:30:00|14\.8 km/.test(txt),'finishing instantly does not invent a 30-min/14.8 km ride');
// 2 challenge completion
await fresh();await pg.evaluate("S.challenges[0].val=148;S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=6;S.rec.elev=40");
const xp0=await pg.evaluate(()=>S.me.xp);await pg.evaluate("finishRide()");await pg.locator('text=Save & share').click();await pg.waitForTimeout(600);
txt=await pg.evaluate(()=>document.body.innerText);const xp1=await pg.evaluate(()=>S.me.xp);
t(/Challenge complete/i.test(txt),'completing "Weekly 150 km" is announced');
t(xp1-xp0>=300+48,`challenge XP (+300) granted (xp ${xp0}->${xp1})`);
// 3 streak card
await pg.evaluate("closeModal();go('feed')");txt=await pg.evaluate(()=>document.querySelector('.screen').innerText);
t(!/Ride before Sunday/.test(txt),'feed streak card no longer says "ride before Sunday" after riding');
// 4 level up ordering
await fresh();await pg.evaluate("S.me.xp=1995;S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=4;S.rec.elev=20");await pg.evaluate("finishRide()");await pg.locator('text=Save & share').click();await pg.waitForTimeout(700);
const n=await pg.evaluate(()=>document.querySelectorAll('.modal').length);txt=await pg.evaluate(()=>document.querySelector('.modal:last-child').innerText);
t(n===1&&/Level 5/.test(txt),`level-up appears inside the single summary sheet (modals=${n})`);
// 5 reset / free in settings
await fresh();await pg.evaluate("openSettings()");txt=await pg.evaluate(()=>document.querySelector('.modal').innerText);
t(/Reset demo/i.test(txt),'Settings has a Reset demo control (phone riders have no side panel)');
// 6 price label
await pg.evaluate("closeModal();openPaywall()");txt=await pg.evaluate(()=>document.querySelector('.modal').innerText);
t(/example pricing/i.test(txt),'paywall labels prices as examples');
t(errs.length===0,'no errors '+errs.join());
await b.close();process.exit(f?1:0)})();
