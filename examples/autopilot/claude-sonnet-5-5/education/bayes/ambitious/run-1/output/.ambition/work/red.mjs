import { spawn } from 'node:child_process';
const CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL_='file:///Volumes/My%20Shared%20Files/work/bayes.html';
const proc=spawn(CH,['--headless=new','--disable-gpu','--remote-debugging-port=9335','--user-data-dir=/tmp/bayes-cdp-red','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let list; for(let i=0;i<50;i++){ try{ list=await (await fetch('http://127.0.0.1:9335/json')).json(); if(list.length) break;}catch{} await sleep(200); }
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
const txt=()=>ev('document.body.innerText');
const nav=async h=>{await send('Page.navigate',{url:URL_+h});await sleep(500);await send('Page.reload');await sleep(600);};
const key=async(k,code,vk)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key:k,code,windowsVirtualKeyCode:vk});await send('Input.dispatchKeyEvent',{type:'keyUp',key:k,code,windowsVirtualKeyCode:vk});};
const typeInto=async(idn,val)=>{await ev(`(()=>{const e=document.getElementById('${idn}');e.focus();e.select();})()`);await key('Backspace','Backspace',8); if(val!=='') await send('Input.insertText',{text:val}); await sleep(60);};
const nonsense=async()=>/NaN|Infinity|undefined|\bnull\b/.test(await txt());
// 1 injection via URL hash
await nav('#prev=<img src=x onerror=window.__x=1>&sens=<script>window.__x=2</script>&fpr=%3Cb%3E&stage=<svg onload=window.__x=3>');
T('hash injection: nothing executes',(await ev('window.__x===undefined')),'executed');
T('hash injection: page still sane',!(await nonsense()) && (await ev(`document.querySelectorAll('circle').length`))===1000);
// 2 extreme typed values
await nav('#stage=3');
for(const v of ['1e999','1e-999','0.0000000001','99.99999999','--5','5-','.','1,5','   ','٣','1e2','+7','0x10']){
  await typeInto('prev-n',v); await typeInto('sens-n',v); await typeInto('fpr-n',v);
  const bad=await nonsense(), n=await ev(`document.querySelectorAll('circle').length`);
  T(`extreme input ${JSON.stringify(v)}: no NaN, 1000 dots`,!bad&&n===1000,String(bad));
}
await ev(`document.activeElement.blur()`);
// 3 all 8 corners via hash, all stages
let cornerOK=true,cornerInfo='';
for(const p of [0,100]) for(const s of [0,100]) for(const f of [0,100]) for(const g of [0,1,2,3]){
  await nav(`#prev=${p}&sens=${s}&fpr=${f}&stage=${g}`);
  const t=await txt(), n=await ev(`document.querySelectorAll('circle').length`);
  if(/NaN|Infinity|undefined|\bnull\b/.test(t)||n!==1000){cornerOK=false;cornerInfo+=` ${p}/${s}/${f}/${g}`}
}
T('8 corners x 4 stages: no NaN, always 1000 dots',cornerOK,cornerInfo);
// 4 rapid clicking
await nav('#stage=0');
for(let i=0;i<300;i++) await ev(`document.getElementById('${i%2?'back':'next'}').click()`);
T('300 rapid Next/Back clicks: no errors',errors.length===0,errors.join('|'));
// 5 keyboard-only reachability
await nav('#stage=3');
const focusables=await ev(`[...document.querySelectorAll('button,input,[tabindex="0"]')].filter(e=>!e.disabled&&e.offsetParent!==null).length`);
await ev(`document.body.focus();document.activeElement.blur()`);
const seen=new Set(); for(let i=0;i<focusables+5;i++){ await key('Tab','Tab',9); seen.add(await ev(`(()=>{const e=document.activeElement;return e.id||e.textContent.slice(0,25)||e.tagName})()`)); }
T(`keyboard Tab reaches all ${focusables} controls`,seen.size>=focusables-1,`reached ${seen.size}`);
// 6 challenge + explain
await nav('#prev=50&sens=90&fpr=10&stage=3');
T('challenge shows success at 50%',(await ev(`document.getElementById('chal').textContent`)).startsWith('Yes'));
await nav('#prev=1&sens=90&fpr=10&stage=3');
T('challenge not yet at default',(await ev(`document.getElementById('chal').textContent`)).startsWith('Not yet'));
await nav('#prev=0&sens=0&fpr=0&stage=3'); T('challenge handles nobody-positive',(await ev(`document.getElementById('chal').textContent`)).includes('nothing to judge'));
for(const [e,w] of [[0,'Not quite. Even'],[1,"Yes, that's the whole idea"],[2,'Not quite. A positive']]){ await ev(`document.querySelector('#eopts button[data-e="${e}"]').click()`); T('explain option '+e,(await ev(`document.getElementById('efeed').textContent`)).startsWith(w)); }
// 7 content checks: safety note present, annotation shown
T('safety note present',(await txt()).includes('This isn\'t medical advice'));
await nav('#prev=1&sens=90&fpr=10&stage=3');
T('dot annotation says 108',(await ev(`document.getElementById('annot').textContent`)).includes('108')&&(await ev(`getComputedStyle(document.getElementById('annot')).display`))!=='none');
await nav('#prev=1&sens=90&fpr=10&stage=1'); T('annotation hidden before step 4',(await ev(`getComputedStyle(document.getElementById('annot')).display`))==='none');
// 8 spoiler gating (cold-read finding): answer must not appear before step 4
await nav('#stage=0');
T('no spoiler: challenge/explain/summary hidden at step 1',(await ev(`getComputedStyle(document.getElementById('after')).display`))==='none' && !(await ev(`document.body.innerText`)).includes('8.33%') );
await nav('#stage=2'); T('still hidden at step 3',(await ev(`getComputedStyle(document.getElementById('after')).display`))==='none');
await nav('#stage=3'); T('revealed at step 4',(await ev(`getComputedStyle(document.getElementById('after')).display`))==='block');
T('safety card always visible',(await ev(`getComputedStyle(document.getElementById('safety')).display`))!=='none');
T('no JS errors across red-team run',errors.length===0,errors.join('|'));
console.log(`\n${pass} passed, ${fail} failed`); ws.close(); proc.kill(); process.exit(fail?1:0);
