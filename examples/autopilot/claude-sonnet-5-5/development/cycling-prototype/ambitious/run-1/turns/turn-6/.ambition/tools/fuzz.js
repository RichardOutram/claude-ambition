// Stretch T2: seeded random-action fuzz with invariants. node fuzz.js <html> [seeds] [actions]
const { chromium } = require('playwright-core');const path=require('path');
const seeds=(process.argv[3]||'1,2,3').split(',').map(Number),N=+(process.argv[4]||600);
const rng=s=>()=>{s=(s*1664525+1013904223)%4294967296;return s/4294967296};
const TEXTS=['','   ','<script>alert(1)</script>','"quoted" & \'single\'','😀🚴‍♀️💥','x'.repeat(300),'0','-1','NaN','null','undefined','\\u0000'];
const SIZES=[[375,667],[390,844],[320,568],[768,900]];
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});let total=0;const bugs=[];const cov=[];
for(const seed of seeds){const R=rng(seed);const pg=await b.newPage({viewport:{width:375,height:667}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
 await pg.goto('file://'+path.resolve(process.argv[2]));const log=[];let lastXP=0;
 for(let i=0;i<N;i++){
  if(R()<0.08){try{const ph=pg.locator('.phone');await pg.evaluate("closeModal();if(S.authed){S.stack=[];S.tab='record';render()}");const st=ph.getByRole('button',{name:/Start ride/});if(await st.count()){await st.click({timeout:800});await pg.waitForTimeout(500+Math.floor(R()*900));const fb=ph.getByRole('button',{name:/Finish/});if(await fb.count()){await fb.click({timeout:800});await pg.waitForTimeout(150);const sv=ph.getByRole('button',{name:/Save/});if(await sv.count()&&R()<0.9)await sv.click({timeout:800})}}}catch(e){}log.push('MACRO ride')}
  const act=await pg.evaluate(([r,bias])=>{let els=[...document.querySelectorAll('.phone [onclick], .phone button, .phone input')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&b.height>0});if(bias){const pr=els.filter(e=>e.tagName==='BUTTON'&&!e.classList.contains('sec')&&!/Reset|Sign out|Discard|Leave/.test(e.textContent));if(pr.length)els=pr}if(!els.length)return null;const e=els[Math.floor(r*els.length)];e.setAttribute('data-fz','1');return {tag:e.tagName,txt:(e.textContent||e.placeholder||'').trim().slice(0,24)}},[R(),R()<0.45]);
  if(act){try{if(act.tag==='INPUT')await pg.locator('[data-fz="1"]').first().fill(TEXTS[Math.floor(R()*TEXTS.length)],{timeout:1500});else await pg.locator('[data-fz="1"]').first().click({timeout:1500,force:true})}catch(e){}
   await pg.evaluate(()=>document.querySelectorAll('[data-fz]').forEach(e=>e.removeAttribute('data-fz')))}
  log.push(act?act.tag+':'+act.txt:'none');
  if(R()<0.01){const [w,h]=SIZES[Math.floor(R()*SIZES.length)];await pg.setViewportSize({width:w,height:h})}
  if(R()<0.15)await pg.waitForTimeout(Math.floor(R()*400));
  const bad=await pg.evaluate((TX)=>{const o=[];let t=document.querySelector('.phone').innerText;TX.filter(x=>x.trim()).forEach(x=>{t=t.split(x).join('')});if(/NaN|undefined|\[object|Infinity/.test(t))o.push('bad text: '+(t.match(/.{0,25}(NaN|undefined|\[object|Infinity).{0,15}/)||[''])[0].replace(/\n/g,' '));if(document.documentElement.scrollWidth>innerWidth+1)o.push('horizontal overflow');
   if(!Number.isFinite(S.me.xp)||S.me.xp<0)o.push('xp '+S.me.xp);S.challenges.forEach(c=>{if(!(c.val>=0&&c.val<=c.goal))o.push('challenge '+c.name+' '+c.val)});if(!['idle','running','paused'].includes(S.rec.state))o.push('rec state '+S.rec.state);
   if(document.querySelectorAll('.modal').length>3)o.push('modals '+document.querySelectorAll('.modal').length);if(S.rec.state!=='idle'&&!S.authed)o.push('recording while signed out');if(!document.querySelector('.screen').innerHTML.trim())o.push('blank screen');return o},TEXTS);
  {const xp=await pg.evaluate(()=>S.me.xp);if(xp<lastXP&&xp!==1840)bad.push('xp decreased '+lastXP+'->'+xp);lastXP=xp}
  if(errs.length||bad.length){bugs.push({seed,i,errs:[...errs],bad,last:log.slice(-6)});errs.length=0;if(bugs.filter(x=>x.seed===seed).length>=3)break}
  total++}
 cov.push(await pg.evaluate(()=>({ridesSaved:S.rides.length-4,xpGained:S.me.xp-1840,challengesDone:S.challenges.filter(c=>c.val>=c.goal).length,pro:S.pro,clubs:S.clubs.length,badges:S.badges.length,authed:S.authed})));
 await pg.close()}
console.log('coverage per seed:',JSON.stringify(cov));console.log(`actions executed: ${total}  bugs found: ${bugs.length}`);bugs.slice(0,8).forEach(x=>console.log(JSON.stringify(x)));
await b.close();process.exit(bugs.length?1:0)})();
