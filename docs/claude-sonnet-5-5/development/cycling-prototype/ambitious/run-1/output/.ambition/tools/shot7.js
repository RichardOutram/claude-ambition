const { chromium } = require('playwright-core');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve('../../prototype.html'));
await pg.locator('.phone').getByRole('button',{name:'Sign in',exact:true}).click();await pg.waitForTimeout(500);await pg.screenshot({path:'h1.png'});
await pg.locator('.phone').getByRole('button',{name:/Start my first ride/}).click();await pg.waitForTimeout(2600);await pg.screenshot({path:'h2.png'});
await pg.evaluate("S.challenges[2].joined=true;S.challenges[2].val=3");await pg.locator('.phone').getByRole('button',{name:/Finish/}).click();await pg.waitForTimeout(300);await pg.locator('.phone').getByRole('button',{name:/Save/}).click();await pg.waitForTimeout(500);await pg.screenshot({path:'h3.png'});
await pg.locator('.phone').getByRole('button',{name:/See my challenges/}).click();await pg.waitForTimeout(300);await pg.screenshot({path:'h4.png'});
fs.writeFileSync('sheet7.html','<body style="margin:0;background:#222;display:flex;gap:6px">'+[1,2,3,4].map(n=>`<img src="h${n}.png" style="height:667px">`).join(''));
const p=await b.newPage({viewport:{width:1500,height:670}});await p.goto('file://'+process.cwd()+'/sheet7.html');await p.waitForTimeout(300);await p.screenshot({path:'sheet7.png'});await b.close()})();
