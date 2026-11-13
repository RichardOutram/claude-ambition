const { chromium } = require('playwright-core');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve('../../prototype.html'));
await pg.evaluate("S.authed=true;S.stack=[{v:'ride',id:1}];render()");await pg.evaluate("document.getElementById('screen').scrollTop=250");await pg.waitForTimeout(200);await pg.screenshot({path:'g1.png'});
await pg.click('text=Create segment');await pg.waitForTimeout(450);await pg.screenshot({path:'g2.png'});
await pg.locator('.modal #sf button',{hasText:'gravel'}).click();await pg.locator('.modal .btn',{hasText:'Create segment'}).click();await pg.waitForTimeout(300);await pg.evaluate("document.getElementById('screen').scrollTop=250");await pg.screenshot({path:'g3.png'});
fs.writeFileSync('sheet6.html','<body style="margin:0;background:#222;display:flex;gap:6px">'+[1,2,3].map(n=>`<img src="g${n}.png" style="height:667px">`).join(''));
const p=await b.newPage({viewport:{width:1140,height:670}});await p.goto('file://'+process.cwd()+'/sheet6.html');await p.waitForTimeout(300);await p.screenshot({path:'sheet6.png'});await b.close()})();
