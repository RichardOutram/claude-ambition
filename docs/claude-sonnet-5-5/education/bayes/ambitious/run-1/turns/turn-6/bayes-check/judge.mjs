import { spawn } from 'node:child_process'; import fs from 'node:fs';
import { fileURLToPath } from 'node:url'; import path from 'node:path';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const HTML=process.env.BAYES_HTML||path.resolve(HERE,'../bayes.html');
const FIRST=process.env.BAYES_FIRST||path.resolve(HERE,'../.ambition/first/bayes.html');
const CHROME=process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const V={ first:{path:FIRST,r:{prev:'prior',sens:'sens',fpr:'fpr'},stage:''},
          final:{path:HTML,r:{prev:'prev-r',sens:'sens-r',fpr:'fpr-r'},stage:'#stage=3'} };
const proc=spawn(CHROME,['--headless=new','--disable-gpu','--remote-debugging-port=9340','--user-data-dir=/tmp/bayes-judge','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9340/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const pend=new Map(),errs=[];ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend.has(d.id)){pend.get(d.id)(d);pend.delete(d.id)}else if(d.method==='Runtime.exceptionThrown')errs.push('x')};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)throw new Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value};
await send('Runtime.enable');
const load=async(v,w=1280,scheme='light',hash)=>{errs.length=0;
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:900,deviceScaleFactor:1,mobile:w<500});
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:scheme}]});
  await send('Page.navigate',{url:'file://'+encodeURI(V[v].path)+(hash??V[v].stage)}); await sleep(450); await send('Page.reload'); await sleep(700)};
const setR=(v,k,val)=>ev(`(()=>{const e=document.getElementById('${V[v].r[k]}');e.value=${val};e.dispatchEvent(new Event('input',{bubbles:true}))})()`);
const rows=[]; const R=(check,first,final)=>{rows.push([check,first,final]);};

// 1 no external deps + single file
for(const v of['first','final']){ const t=fs.readFileSync(V[v].path,'utf8'); V[v].ext=(t.match(/(src|href)\s*=\s*["']https?:|url\(\s*["']?https?:|@import|<link[^>]+stylesheet|<script[^>]+src=/gi)||[]).length; V[v].bytes=t.length; }
R('external dependencies (want 0)',V.first.ext,V.final.ext);
R('file size (KB)',(V.first.bytes/1024).toFixed(1),(V.final.bytes/1024).toFixed(1));
// 2 sliders + live update + correctness grid
const exact=(p,s,f)=>{p/=100;s/=100;f/=100;const pe=p*s+(1-p)*f;return pe?100*p*s/pe:null};
for(const v of['first','final']){
  await load(v); V[v].nR=await ev(`document.querySelectorAll('input[type=range]').length`);
  let maxErr=0,n=0,bad=0;
  for(const p of[0.1,1,5,20,50,90]) for(const s of[1,50,90,99]) for(const f of[0,0.5,5,10,50,100]){
    await setR(v,'prev',p);await setR(v,'sens',s);await setR(v,'fpr',f);
    const t=await ev(`document.getElementById('post').textContent`); const got=parseFloat(t), ex=exact(p,s,f); n++;
    if(isNaN(got)||ex===null){bad++;continue} const tol=Math.max(0.06,ex*0.006); const e=Math.abs(got-ex); maxErr=Math.max(maxErr,e); if(e>tol)bad++;
  }
  V[v].grid=`${n-bad}/${n} within rounding (max err ${maxErr.toFixed(3)} pts)`;
}
R('number of range sliders (want 3)',V.first.nR,V.final.nR);
R('posterior vs exact maths, 144 settings',V.first.grid,V.final.grid);
// 3 extremes via sliders: no NaN
for(const v of['first','final']){ await load(v); let bad=0; for(const [p,s,f] of [[0,0,0],[100,100,100],[0,100,0],[100,0,100],[0,0,100],[100,100,0]]){await setR(v,'prev',p);await setR(v,'sens',s);await setR(v,'fpr',f); if(/NaN|Infinity|undefined/.test(await ev('document.body.innerText')))bad++;} V[v].nan=bad+' of 6 extreme settings show NaN/undefined'; }
R('slider extremes',V.first.nan,V.final.nan);
// 4 jargon before formula, beginner opening
for(const v of['first','final']){ await load(v,1280,'light',v==='final'?'#stage=0':''); const t=(await ev('document.body.innerText')).toLowerCase(); const hits=['prior','posterior','likelihood','p(h','p(e','conditional','bayes'].filter(w=>t.includes(w)); V[v].jargon=hits.length?hits.join(', '):'none'; V[v].q1=t.includes('1 in 100')?'yes':'no'; V[v].guess=await ev(`document.querySelectorAll('button').length`)>6?'yes':'—'; }
R('jargon in the first screen-load text',V.first.jargon,V.final.jargon);
R('opens with the 1-in-100 question',V.first.q1,V.final.q1);
// 5 layout overflow at widths
for(const v of['first','final']){ const o=[]; for(const w of[320,375,414,768,1280,1920]){await load(v,w); const sw=await ev(`Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)`); if(sw>w+1)o.push(`${w}px(+${sw-w})`);} V[v].overflow=o.length?o.join(' '):'none'; }
R('horizontal overflow at 320/375/414/768/1280/1920',V.first.overflow,V.final.overflow);
// 6 contrast scan
const CONTRAST=`(()=>{
 const parse=s=>{let m=s.match(/rgba?\\(([^)]+)\\)/);if(m){const a=m[1].split(/[ ,\\/]+/).map(Number);return [a[0],a[1],a[2],a.length>3?a[3]:1]}
  m=s.match(/color\\(srgb ([^)]+)\\)/);if(m){const a=m[1].split(/[ \\/]+/).map(Number);return [a[0]*255,a[1]*255,a[2]*255,a.length>3?a[3]:1]} return [0,0,0,0]};
 const over=(f,b)=>{const a=f[3];return [f[0]*a+b[0]*(1-a),f[1]*a+b[1]*(1-a),f[2]*a+b[2]*(1-a),1]};
 const bg=el=>{const chain=[];for(let e=el;e;e=e.parentElement){const c=parse(getComputedStyle(e).backgroundColor);if(c[3]>0)chain.push(c);if(c[3]>=1)break}
   let base=[255,255,255,1]; for(let i=chain.length-1;i>=0;i--) base=over(chain[i],base); return base};
 const L=c=>{const f=x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
 const out=[];
 document.querySelectorAll('body *').forEach(el=>{
  const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1); if(!own)return;
  const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')return; const r=el.getBoundingClientRect(); if(r.width===0||r.height===0)return;
  if(el.closest('[style*="-9999px"]')) return; if(el.disabled||el.closest('button:disabled'))return;
  const isSvg=el instanceof SVGElement; const fg=parse(isSvg?cs.fill:cs.color);
  const b=bg(el); const f=over(fg,b); const l1=L(f),l2=L(b); const cr=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
  const fs=parseFloat(cs.fontSize)*(isSvg?(el.ownerSVGElement.getBoundingClientRect().width/el.ownerSVGElement.viewBox.baseVal.width):1), bold=parseInt(cs.fontWeight)>=700;
  const need=(fs>=24||(fs>=18.66&&bold))?3:4.5; if(cr<need)out.push(el.tagName.toLowerCase()+'.'+(el.className&&el.className.baseVal===undefined?el.className:'')+' "'+el.textContent.trim().slice(0,28)+'" '+cr.toFixed(2)+'<'+need);
 });
 return JSON.stringify(out)})()`;
for(const v of['first','final']){ V[v].contrast={}; for(const sch of['light','dark']){ await load(v,1280,sch); V[v].contrast[sch]=JSON.parse(await ev(CONTRAST)); } }
const fmtC=v=>`light ${V[v].contrast.light.length} / dark ${V[v].contrast.dark.length} failing text elements`;
R('WCAG text contrast failures (want 0)',fmtC('first'),fmtC('final'));
// 7 interaction cost
for(const v of['first','final']){ await load(v); const ms=await ev(`(()=>{const e=document.getElementById('${V[v].r.prev}');const t=performance.now();for(let i=0;i<200;i++){e.value=(i%90)+0.5;e.dispatchEvent(new Event('input',{bubbles:true}))}return (performance.now()-t)/200})()`); V[v].ms=ms.toFixed(2)+' ms per slider update'; }
R('slider drag cost (want < 16 ms)',V.first.ms,V.final.ms);
R('JS errors during run',errs.length,errs.length);
console.log('\n'.padEnd(2)+['CHECK'.padEnd(52),'FIRST VERSION'.padEnd(46),'CURRENT'].join(' | '));
for(const [c,a,b] of rows) console.log(c.padEnd(52)+' | '+String(a).padEnd(46)+' | '+b);
for(const v of['first','final']) for(const s of['light','dark']) if(V[v].contrast[s].length){console.log(`\n[${v} ${s}] contrast failures:`);V[v].contrast[s].slice(0,12).forEach(x=>console.log('  '+x));}
ws.close();proc.kill();
