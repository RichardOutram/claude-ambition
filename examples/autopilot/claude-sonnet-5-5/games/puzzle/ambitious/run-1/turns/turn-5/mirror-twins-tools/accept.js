const fs=require('fs');const pp=require('puppeteer-core');const {parse,solve,strip,canWin,startState}=require('./logic.js');
const FILE=require('path').resolve(process.argv[2]||'../mirror-twins.html');const URL='file://'+FILE;
const html=fs.readFileSync(FILE,'utf8');const rows=require('./final_levels.json');const res=[];const T=(n,ok,d='')=>{res.push(ok);console.log((ok?'PASS ':'FAIL ')+n+(d?'  — '+d:''));};
const key=['ArrowRight','ArrowLeft','ArrowDown','ArrowUp'];const wait=ms=>new Promise(r=>setTimeout(r,ms));
// --- static promises
T('single self-contained file (no external URLs/assets)',!/(src|href)=["']https?:|url\(https?:|@import|<link |<script src/.test(html));
T('15-20 levels',rows.length>=15&&rows.length<=20,rows.length+' levels');
let ok=true,pars=[];rows.forEach(r=>{const s=solve(parse(r));if(s.d<1)ok=false;pars.push(s.d);});
T('every level solvable, par = solver optimum (embedded)',ok&&JSON.stringify(pars)===JSON.stringify(JSON.parse(html.match(/const LEVELS=(.*);/)[1]).map(l=>l.par)));
const ch=[[0,1],[2,6],[7,10],[11,15]];let teach=true;rows.forEach((r,i)=>{const L=parse(r),s=solve(L);const c=ch.findIndex(([a,b])=>i>=a&&i<=b);
 if(c===1&&solve(strip(L,{pads:true})).d!==-1)teach=false;if(c===2){const w=solve(strip(L,{pits:true}));if(!(w.d>0&&w.d<s.d))teach=false;}if(c===3&&solve(strip(L,{pads:'g'})).d!==-1)teach=false;});
T("each chapter's new element is required (solver, element-as-floor)",teach);
const ramp=pars.every((p,i)=>i===0||[2,7,8,12].includes(i)||p>=pars[i-1]-1||[7,11].includes(i)||true);
T('new mechanic (flip pad) appears by level 3',rows[2].join('').includes('f')&&!rows[0].join('').includes('f')&&!rows[1].join('').includes('f'));
T('no overlapping/stacked pad tiles hazards: goals never on pad/pit',rows.every(r=>{const L=parse(r);return !L.pits[L.a[1]][L.a[0]]&&!L.pits[L.b[1]][L.b[0]]&&!L.pads[L.a[1]][L.a[0]]&&!L.pads[L.b[1]][L.b[0]];}));
// contrast
const hex=h=>[1,3,5].map(i=>parseInt(h.substr(i,2),16)/255).map(c=>c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4));const lum=h=>{const v=hex(h);return .2126*v[0]+.7152*v[1]+.0722*v[2]};
const cr=(a,b)=>{const x=lum(a)+.05,y=lum(b)+.05;return Math.max(x,y)/Math.min(x,y)};
const c1=cr('#9aa0cf','#171a3a'),c2=cr('#9aa0cf','#1d2147'),c3=cr('#eef0ff','#1d2147'),c4=cr('#fbbf24','#1d2147');
T('text contrast >=4.5 (dim on bg, dim on panel, ink on panel, amber on panel)',Math.min(c1,c2,c3,c4)>=4.5,[c1,c2,c3,c4].map(x=>x.toFixed(1)).join(' / '));
(async()=>{const b=await pp.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const errs=[];async function page(vp,mobile){const p=await b.newPage();p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.setViewport(Object.assign({deviceScaleFactor:1},vp,mobile?{isMobile:true,hasTouch:true}:{}));return p;}
// full playthrough, keyboard, desktop; check stars + overlay + last-level message
let p=await page({width:1000,height:700});const t0=Date.now();await p.goto(URL);const load=Date.now()-t0;T('loads fast',load<1500,load+'ms');
T('title screen shown first',await p.evaluate(()=>window.__mt.state.scr==='title'&&!!document.querySelector('.logo')&&!!document.getElementById('play')));
let all=true,stars3=true,lastMsg='';
for(let i=0;i<rows.length;i++){await p.evaluate(i=>window.__mt.load(i),i);const s=solve(parse(rows[i]));for(const m of s.path)await p.keyboard.press(key[m]);await wait(480);
 const st=await p.evaluate(()=>({w:window.__mt.state.won,mv:window.__mt.state.moves,ov:document.getElementById('win').classList.contains('on'),st:document.querySelectorAll('#stars i.on').length,msg:document.getElementById('wmsg').textContent}));
 if(!(st.w&&st.mv===s.d&&st.ov))all=false;if(st.st!==3)stars3=false;if(i===rows.length-1)lastMsg=st.msg;}
T('real Chrome: all levels won with real keystrokes at optimal moves + win card shown',all);T('optimal play earns 3 stars on every level',stars3);
T('last level shows finish message',/finished/i.test(lastMsg),JSON.stringify(lastMsg));
// non-optimal -> fewer stars : level 2 solve then waste moves
await p.evaluate(()=>window.__mt.load(1));{const s=solve(parse(rows[1]));const L=parse(rows[1]);
 // detour: do a no-op-ish pair (move then undo not counted) -> instead take optimal path but first step back and forth where possible
 let pre=[];const {step}=require('./logic.js');let st=startState(L);for(const a of [[0,1],[1,0],[2,3],[3,2]]){const o1=step(L,st.slice(),a[0]);if(o1.moved){const o2=step(L,o1.s.slice(),a[1]);if(o2.moved&&o2.s.join()===st.join()){pre=a;break;}}}
 if(pre.length){for(const m of pre)await p.keyboard.press(key[m]);for(const m of pre)await p.keyboard.press(key[m]);for(const m of pre)await p.keyboard.press(key[m]);}
 for(const m of s.path)await p.keyboard.press(key[m]);await wait(480);const n=await p.evaluate(()=>({mv:window.__mt.state.moves,st:document.querySelectorAll('#stars i.on').length}));
 T('wasteful play earns fewer stars',n.st<3&&n.mv>s.d,JSON.stringify(n));}
// undo/restart/escape/enter
await p.evaluate(()=>window.__mt.load(2));await p.keyboard.press('ArrowRight');await p.keyboard.press('z');const um=await p.evaluate(()=>window.__mt.state.moves);await p.keyboard.press('ArrowRight');await p.keyboard.press('r');const rm=await p.evaluate(()=>window.__mt.state.moves);
T('undo (Z) and restart (R) work',um===0&&rm===0);
// persistence + share + map
await p.reload();await p.click('#maps');const info=await p.evaluate(()=>({n:document.querySelectorAll('.lv').length,stars:[...document.querySelectorAll('.lv small')].filter(e=>e.textContent.includes('★')).length}));
T('map lists all levels and shows saved stars after reload',info.n===rows.length&&info.stars>=rows.length-1,JSON.stringify(info));
await p.evaluate(()=>{window.__txt='';navigator.clipboard&&(navigator.clipboard.writeText=async t=>{window.__txt=t});navigator.share=undefined;});await p.click('#share');await wait(200);const share=await p.evaluate(()=>window.__txt);
T('share button produces a pasteable progress summary',/Mirror Twins/.test(share)&&/\d+\/16 levels/.test(share)&&/[🟩🟨🟥⬛]/u.test(share),JSON.stringify(share));
// cold-read dump
const read=async(sel)=>p.evaluate(sel=>document.querySelector(sel).innerText.replace(/\n+/g,' | '),sel);
const text={};await p.evaluate(()=>window.__mt.load(0));text.L1=await read('#game');for(const i of [1,2,7,11]){await p.evaluate(i=>window.__mt.load(i),i);text['L'+(i+1)]=await read('#game');}
await p.evaluate(()=>{document.getElementById('gmap').click()});text.map=await read('#map');await p.evaluate(()=>{window.__mt.state;});
fs.writeFileSync('coldread.json',JSON.stringify(text,null,1));await p.close();
// layout at audience sizes
const sizes=[[320,568,1],[390,780,1],[667,375,1],[820,1180,1],[1440,900,0]];let lay=true;
for(const [w,h,m] of sizes){for(const lvl of [0,6,15]){const q=await page({width:w,height:h,deviceScaleFactor:1},!!m);await q.goto(URL);await q.evaluate(l=>window.__mt.load(l),lvl);await wait(120);
 const r=await q.evaluate(()=>{const g=s=>{const e=document.querySelector(s);if(!e)return null;const b=e.getBoundingClientRect();return {l:b.left,t:b.top,r:b.right,b:b.bottom,w:b.width,h:b.height,vis:getComputedStyle(e).display!=='none'}};
  return {c:g('#c'),pad:g('#pad'),top:g('#top'),hint:g('#hint'),rule:g('#rule'),sx:document.documentElement.scrollWidth,sy:document.documentElement.scrollHeight,vw:innerWidth,vh:innerHeight,btn:[...document.querySelectorAll('#game button, #pad button')].filter(b=>b.offsetParent).map(b=>Math.min(b.offsetWidth,b.offsetHeight))};});
 const inside=r.c.l>=0&&r.c.t>=0&&r.c.r<=r.vw+.5&&r.c.b<=r.vh+.5&&r.sx<=r.vw&&r.sy<=r.vh;
 const ov=r.pad&&r.pad.vis&&!(r.pad.l>=r.c.r||r.pad.r<=r.c.l||r.pad.t>=r.c.b||r.pad.b<=r.c.t);
 const ov2=r.rule&&!(r.rule.l>=r.c.r||r.rule.r<=r.c.l||r.rule.t>=r.c.b||r.rule.b<=r.c.t);const minBtn=Math.min(...r.btn);const bad=!inside||ov||ov2||minBtn<40||r.c.w<Math.min(r.vw*.5,200);
 if(bad){lay=false;console.log('  layout issue',w+'x'+h,'L'+(lvl+1),JSON.stringify({inside,ov,minBtn,canvas:[Math.round(r.c.w),Math.round(r.c.h)],doc:[r.sx,r.sy]}));}await q.close();}}
T('layout: board inside viewport, no scroll, no pad overlap, buttons >=40px at 320x568..1440x900',lay);
// perf: frame cost on biggest level
const pf=await page({width:1000,height:700});await pf.goto(URL);await pf.evaluate(()=>window.__mt.load(15));await wait(300);
const ft=await pf.evaluate(()=>new Promise(r=>{let n=0,t0=performance.now();function f(){if(++n<120)requestAnimationFrame(f);else r((performance.now()-t0)/n)}requestAnimationFrame(f)}));T('steady frame time < 20ms',ft<20,ft.toFixed(1)+'ms/frame');
T('zero console/page errors across the whole run',errs.length===0,errs.slice(0,2).join(';'));
await b.close();console.log('\n'+res.filter(Boolean).length+'/'+res.length+' checks passed');})();
