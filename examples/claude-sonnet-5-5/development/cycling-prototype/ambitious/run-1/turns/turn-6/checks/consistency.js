// node consistency.js <html>: displayed numbers must agree with each other
const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:(process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')});
const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve(process.argv[2]));let f=0;
const t=(c,m)=>{console.log((c?'PASS ':'FAIL ')+m);if(!c)f++};
await pg.evaluate("S.authed=true;render()");
const bad=await pg.evaluate(()=>S.rides.filter(r=>{const [h,m,s]=r.time.split(':').map(Number);const hrs=h+m/60+s/3600;return Math.abs(r.km/hrs-r.spd)/r.spd>0.01}).map(r=>r.title));
t(bad.length==0,'avg speed = distance/time for seeded rides '+bad.join());
// record a ride for real, 8 ticks
await pg.evaluate("S.tab='record';render();startRide()");await pg.waitForTimeout(4300);
const live=await pg.evaluate(()=>({km:+document.querySelector('#bk').textContent,t:document.querySelector('#bt').textContent,xp:+document.querySelector('#bx').textContent}));
console.log('after ~8s:',JSON.stringify(live));
t(live.km>2&&live.km<6,'4 s of demo ride gives a plausible distance (2-6 km)');
await pg.evaluate("finishRide()");const xp0=await pg.evaluate(()=>S.me.xp);
const sum=await pg.evaluate(()=>[...document.querySelectorAll('.modal .lb b')].map(e=>+e.textContent));
await pg.locator('text=Save & share').click();
const lines=await pg.evaluate(()=>[...document.querySelectorAll('.modal .lb b')].map(e=>+e.textContent.replace('+','')));
const head=await pg.evaluate(()=>+document.querySelector('.modal h2').textContent.replace(/[^0-9]/g,''));
t(lines.length==3&&lines.reduce((a,c)=>a+c,0)===head,`XP breakdown ${lines.join('+')} = headline ${head}`);
await pg.waitForTimeout(500);const xp1=await pg.evaluate(()=>S.me.xp);t(xp1-xp0===head,`profile XP rose by exactly the headline (${xp0}->${xp1})`);
const seg=await pg.evaluate(()=>document.querySelector('.modal').textContent.includes('River Road Sprint'));
const lb=await pg.evaluate(()=>S.segments[1].lb.findIndex(r=>r[0]==='Alex Rider')+1);
t(!seg||lb===2,'segment rank shown (2nd) matches leaderboard rank '+lb);
await b.close();process.exit(f?1:0)})();
