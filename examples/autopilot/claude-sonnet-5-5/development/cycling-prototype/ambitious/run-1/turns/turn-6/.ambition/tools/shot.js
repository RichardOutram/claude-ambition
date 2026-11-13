const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve('../../prototype.html'));
await pg.evaluate("S.authed=true;S.me.xp=1995;S.challenges[0].val=148;S.tab='record';render();startRide();S.rec.sec=600;S.rec.km=6;S.rec.elev=40");
await pg.evaluate("finishRide()");await pg.locator('text=Save & share').click();await pg.waitForTimeout(400);await pg.screenshot({path:'c1.png'});
await pg.evaluate("closeModal();go('feed')");await pg.screenshot({path:'c2.png'});
require('fs').writeFileSync('sheet3.html','<body style="margin:0;background:#222;display:flex;gap:6px"><img src="c1.png" style="height:667px"><img src="c2.png" style="height:667px">');
const p=await b.newPage({viewport:{width:760,height:670}});await p.goto('file://'+process.cwd()+'/sheet3.html');await p.waitForTimeout(300);await p.screenshot({path:'sheet3.png'});await b.close()})();
