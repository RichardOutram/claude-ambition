const { chromium } = require('playwright-core');const path=require('path');
const file=path.resolve(process.argv[2]);
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:420,height:880}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('file://'+file);let f=0;const t=(c,m)=>{console.log((c?'PASS ':'FAIL ')+m);if(!c)f++};
const modal=async()=>(await pg.locator('.modal').count())>0;
await pg.evaluate("S.authed=true;render()");
await pg.locator('.hdr .chip').first().click();t(await modal(),'notification chip opens sheet');await pg.evaluate("closeModal()");
t((await pg.locator('.hdr .chip').first().textContent()).trim()==='🔔','unread badge clears');
await pg.locator('text=↗ Share').first().click();t(await modal(),'Share opens sheet');
await pg.locator('text=Copy link').click();t(!(await modal())&&await pg.locator('.toast').count()>0,'Share action gives feedback');
await pg.evaluate("go('clubs')");await pg.locator('text=+ New').click();t(await modal(),'+ New opens form');
await pg.locator('text=Create club (free)').click();t(await pg.locator('text=Sunday Spinners').count()>0,'new club appears in list');
await pg.evaluate("go('profile')");await pg.locator('text=⚙️').click();t(await modal(),'settings gear opens sheet');
await pg.locator('.modal .chip').nth(1).click();t((await pg.locator('.modal .chip').nth(1).textContent())==='Off','settings toggle works');
await pg.evaluate("closeModal()");
await pg.locator('text=Free · what is Pro?').click();t(await modal(),'Pro explainer opens');await pg.evaluate("closeModal()");
await pg.evaluate("S.rec.sec=60;S.rec.km=5;S.rec.elev=50;finishRide()");await pg.locator('text=Save & share').click();
await pg.locator('text=See my challenges').click();t(await pg.locator('text=Weekly 150 km').count()>0&&!(await modal()),'post-ride CTA lands on challenges');
t(errs.length==0,'no errors '+errs.join());
// contact sheet
const shots=[];for(const [n,js] of [['feed',"S.tab='feed';S.stack=[];render()"],['record',"S.tab='record';S.stack=[];render()"],['challenges',"S.tab='challenges';S.stack=[];render()"],['profile',"S.tab='profile';S.stack=[];render()"]]){await pg.evaluate(js);await pg.waitForTimeout(100);await pg.locator('.phone').screenshot({path:`s-${n}.png`});}
await b.close();process.exit(f?1:0)})();
