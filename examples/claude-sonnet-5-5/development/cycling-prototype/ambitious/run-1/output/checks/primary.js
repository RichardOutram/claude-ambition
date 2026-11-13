// Stretch T1: a driver that only taps the most prominent accent button on each screen. node primary.js <html>
const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:(process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')});
const pg=await b.newPage({viewport:{width:375,height:667}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
const t0=Date.now();await pg.goto('file://'+path.resolve(process.argv[2]));let taps=0;const trail=[];
const prominent=()=>pg.evaluate(()=>{const root=document.querySelector('.modal')||document.querySelector('.screen');
 const c=[...root.querySelectorAll('button')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&!e.classList.contains('sec')&&!e.classList.contains('sm')&&!e.closest('.tabs')&&getComputedStyle(e).backgroundImage!=='none'||(r.width>0&&!e.classList.contains('sec')&&!e.classList.contains('sm')&&!e.closest('.tabs'))});
 c.sort((a,b)=>b.getBoundingClientRect().width*b.getBoundingClientRect().height-a.getBoundingClientRect().width*a.getBoundingClientRect().height);
 document.querySelectorAll('[data-pick]').forEach(x=>x.removeAttribute('data-pick'));const e=c[0];if(!e)return null;e.setAttribute('data-pick','1');return e.textContent.trim()});
let done=false;
for(let i=0;i<12&&!done;i++){
  await pg.waitForTimeout(250);
  const onChallenge=await pg.evaluate(()=>/Weekly 150 km/.test(document.querySelector('.screen').innerText)&&!document.querySelector('.modal'));
  if(onChallenge){done=true;break}
  // recording: wait until a believable ride (>=40 XP shown) before choosing Finish
  const rec=await pg.evaluate(()=>!!document.querySelector('#bx'));
  if(rec){await pg.waitForFunction(()=>+document.querySelector('#bx')?.textContent>=40,null,{timeout:15000}).catch(()=>{})}
  const label=await prominent();if(!label){trail.push('(no prominent button)');break}
  trail.push(label.slice(0,28));await pg.locator('[data-pick="1"]').first().click();taps++;
}
const ok=await pg.evaluate(()=>/Weekly 150 km/.test(document.querySelector('.screen').innerText));
const ms=Date.now()-t0;
console.log(JSON.stringify({reachedChallenge:ok,taps,wallSeconds:+(ms/1000).toFixed(1),consoleErrors:errs.length,trail}));
await b.close()})();
