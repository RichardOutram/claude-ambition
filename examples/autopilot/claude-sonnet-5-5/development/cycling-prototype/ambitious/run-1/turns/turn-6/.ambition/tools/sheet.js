const { chromium } = require('playwright-core');const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const p=await b.newPage({viewport:{width:1480,height:760}});
fs.writeFileSync('sheet.html','<body style="margin:0;background:#222;display:flex;gap:6px">'+['feed','record','challenges','profile'].map(n=>`<img src="s-${n}.png" style="height:750px">`).join(''));
await p.goto('file://'+process.cwd()+'/sheet.html');await p.waitForTimeout(400);await p.screenshot({path:'sheet.png'});await b.close()})();
