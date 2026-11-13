// Version-neutral cold-rider core loop at 375x667. node core.js <html>
const { chromium } = require('playwright-core');const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:(process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')});
const pg=await b.newPage({viewport:{width:375,height:667}});const errs=[];pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('file://'+path.resolve(process.argv[2]));const ph=pg.locator('.phone');let taps=0;const R={};
const tappable=async loc=>{try{const el=await loc.first().elementHandle();if(!el)return false;return await el.evaluate(e=>{e.scrollIntoView({block:'nearest'});const r=e.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;if(y>innerHeight||y<0)return false;const t=document.elementFromPoint(x,y);return !!t&&(e===t||e.contains(t)||t.contains(e))})}catch{return false}};
const tap=async(loc)=>{await loc.first().click();taps++;await pg.waitForTimeout(250)};
await tap(ph.getByRole('button',{name:'Sign in',exact:true}));
if(await ph.getByRole('button',{name:/Start my first ride/}).count()){await tap(ph.getByRole('button',{name:/Start my first ride/}))}
else{await tap(ph.getByRole('button',{name:/Let.s ride/}));await tap(ph.locator('.tab.rec'));await tap(ph.getByRole('button',{name:/Start ride/}))}
await pg.waitForTimeout(4500);
const fin=ph.getByRole('button',{name:/Finish/});
R.finishVisibleWithoutScrolling=await (async()=>{const e=await fin.first().elementHandle();return e.evaluate(e=>{const r=e.getBoundingClientRect();const t=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.bottom<=innerHeight&&(e===t||e.contains(t)||t.contains(e))})})();
await tap(fin);
const save=ph.getByRole('button',{name:/Save/});R.saveVisible=await tappable(save);
await tap(save);await pg.waitForTimeout(400);
const body=await pg.evaluate(()=>document.querySelector('.modal')?.innerText||'');
R.sawXP=/\+\d+ XP/.test(body);R.sawBadge=/Badge unlocked/i.test(body);R.explainsXP=/XP =|distance/i.test(body);
const cta=ph.locator('.modal .btn').last();R.rewardCtaVisible=await tappable(ph.locator('.modal button').filter({hasText:/challenge|Awesome/i}));
// get to challenges: prefer in-sheet CTA, else close and use tab
const ch=ph.locator('.modal button',{hasText:/challenges/i});
if(await ch.count()){await tap(ch)}else{await pg.evaluate(()=>closeModal());taps++;await tap(ph.locator('.tab',{hasText:'Challenges'}))}
await pg.waitForTimeout(200);
R.challengeScreen=/Weekly 150 km/.test(await pg.evaluate(()=>document.querySelector('.screen').innerText));
R.tapsFromSignInToChallenge=taps;R.consoleErrors=errs.length;
console.log(JSON.stringify(R));await b.close()})().catch(e=>{console.log(JSON.stringify({crashed:String(e.message).split('\n')[0]}));process.exit(0)});
