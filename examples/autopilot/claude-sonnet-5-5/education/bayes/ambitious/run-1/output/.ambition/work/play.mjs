import { spawn } from 'node:child_process';
const CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL_='file:///Volumes/My%20Shared%20Files/work/bayes.html';
const proc=spawn(CH,['--headless=new','--disable-gpu','--remote-debugging-port=9342','--user-data-dir=/tmp/bayes-cdp-play','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let list; for(let i=0;i<50;i++){ try{ list=await (await fetch('http://127.0.0.1:9342/json')).json(); if(list.length) break;}catch{} await sleep(200); }
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let id=0; const pend=new Map(), errors=[];
ws.onmessage=m=>{const d=JSON.parse(m.data); if(d.id&&pend.has(d.id)){pend.get(d.id)(d);pend.delete(d.id);} else if(d.method==='Runtime.exceptionThrown') errors.push(d.params.exceptionDetails.text+' '+(d.params.exceptionDetails.exception?.description||'')); else if(d.method==='Runtime.consoleAPICalled'&&d.params.type==='error') errors.push('console.error');};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend.set(i,r);ws.send(JSON.stringify({id:i,method,params}));});
const ev=async expr=>{const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true}); if(r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails)); return r.result.result.value;};
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:URL_}); await sleep(800);



let pass=0,fail=0; const T=(name,ok,info='')=>{ok?pass++:fail++;console.log((ok?'PASS ':'FAIL ')+name+(ok?'':'  -> '+info));};
const stage=()=>ev(`document.getElementById('dots').getAttribute('class')`);
const lbl=()=>ev(`document.getElementById('play').textContent`);
const nav=async h=>{await send('Page.navigate',{url:URL_+h});await sleep(400);await send('Page.reload');await sleep(600);};
// A. STRETCH: one click -> full answer within 12 s (measured wall clock)
await nav('');
T('arrival: stage0, answer not shown, safety visible',(await stage())==='stage0');
const t0=Date.now(); await ev(`document.getElementById('play').click()`); const clicks=1;
let t=null; while(Date.now()-t0<20000){ if((await stage())==='stage3'){t=Date.now()-t0;break} await sleep(100); }
console.log('   time from one click to answer: '+(t===null?'never':(t/1000).toFixed(1)+' s'));
T('STRETCH: answer reached in <= 12.5 s with 1 click',t!==null&&t<=12500&&clicks===1,String(t));
T('answer shown is 8.33% and cards unlocked',(await ev(`document.getElementById('post').textContent`))==='8.33%' && (await ev(`getComputedStyle(document.getElementById('after')).display`))==='block');
T('button resets to Play when finished',(await lbl()).includes('Play it for me'));
// B. passes through every step in order, not skipping
await nav(''); const seen=[]; await ev(`document.getElementById('play').click()`);
for(let i=0;i<140;i++){ const s=await stage(); if(seen[seen.length-1]!==s) seen.push(s); if(s==='stage3')break; await sleep(100); }
T('plays steps 2 -> 3 -> 4 in order',seen.join(',')==='stage1,stage2,stage3',seen.join(','));
// C. pause
await nav(''); await ev(`document.getElementById('play').click()`); await sleep(1000);
T('label becomes Pause while playing',(await lbl()).includes('Pause'));
await ev(`document.getElementById('play').click()`); const sp=await stage(); await sleep(8000);
T('Pause stops auto-advance (stays on same step 8 s later)',(await stage())===sp&&(await lbl()).includes('Play it for me'),sp+' -> '+await stage());
// D. any manual action cancels
for(const [name,js] of [['Back click',`document.getElementById('back').click()`],['Next click',`document.getElementById('next').click()`],['slider',`(()=>{const e=document.getElementById('prev-r');e.value=5;e.dispatchEvent(new Event('input',{bubbles:true}))})()`],['preset',`document.querySelector('#presets button').click()`]]){
  await nav(''); await ev(`document.getElementById('play').click()`); await sleep(600); await ev(js); const s1=await stage(); await sleep(8000);
  T(`${name} cancels autoplay`,(await stage())===s1 && (await lbl()).includes('Play it for me'),s1+' -> '+await stage());
}
// E. replay from the end restarts at step 2
await nav('#stage=3'); await ev(`document.getElementById('play').click()`); await sleep(300);
T('Play at the end restarts from step 2',(await stage())==='stage1');
await ev(`document.getElementById('play').click()`);
// F. old path untouched: manual Next x3 still reaches the answer
await nav(''); for(let i=0;i<3;i++) await ev(`document.getElementById('next').click()`); await sleep(100);
T('fallback: 3 manual clicks still reach the answer',(await stage())==='stage3'&&(await ev(`document.getElementById('post').textContent`))==='8.33%');
T('no JS errors',errors.length===0,errors.join('|'));
console.log(`\n${pass} passed, ${fail} failed`); ws.close(); proc.kill(); process.exit(fail?1:0);
