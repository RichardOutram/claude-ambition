const { chromium } = require('playwright-core');const fs=require('fs');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve('../../prototype.html'));
await pg.evaluate("S.authed=true;S.tab='feed';render()");await pg.screenshot({path:'t1.png'});
await pg.evaluate("S.tab='record';render();startRide()");await pg.waitForTimeout(7400);await pg.screenshot({path:'t2.png'});
await pg.evaluate("finishRide()");await pg.locator('text=Save & share').click();await pg.waitForTimeout(400);await pg.screenshot({path:'t3.png'});
await pg.evaluate("closeModal();S.tab='profile';S.stack=[];render()");await pg.evaluate("document.getElementById('screen').scrollTop=330");await pg.screenshot({path:'t4.png'});
fs.writeFileSync('sheet2.html','<body style="margin:0;background:#222;display:flex;gap:6px">'+[1,2,3,4].map(n=>`<img src="t${n}.png" style="height:667px">`).join(''));
const p=await b.newPage({viewport:{width:1500,height:670}});await p.goto('file://'+process.cwd()+'/sheet2.html');await p.waitForTimeout(300);await p.screenshot({path:'sheet2.png'});await b.close()})();
