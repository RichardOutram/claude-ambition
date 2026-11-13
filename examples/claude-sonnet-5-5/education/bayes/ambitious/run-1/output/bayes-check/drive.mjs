import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url'; import path from 'node:path';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const HTML=process.env.BAYES_HTML||path.resolve(HERE,'../bayes.html');
const FIRST=process.env.BAYES_FIRST||path.resolve(HERE,'../.ambition/first/bayes.html');
const CHROME=process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const CH=CHROME;
const URL_='file://'+encodeURI(HTML);
const proc=spawn(CH,['--headless=new','--disable-gpu','--remote-debugging-port=9333','--user-data-dir=/tmp/bayes-cdp-profile','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let list; for(let i=0;i<50;i++){ try{ list=await (await fetch('http://127.0.0.1:9333/json')).json(); if(list.length) break;}catch{} await sleep(200); }
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
const state=()=>ev(`JSON.stringify({post:document.getElementById('post').textContent,story:document.getElementById('story').textContent,stage:document.getElementById('dots').getAttribute('class'),prev:document.getElementById('prev-n').value,sens:document.getElementById('sens-n').value,fpr:document.getElementById('fpr-n').value,
 cnt:Object.fromEntries(['tp','fn','fp','tn'].map(k=>[k,document.querySelectorAll('circle.g-'+k).length])),formula:getComputedStyle(document.getElementById('formulaSec')).display})`).then(JSON.parse);
const bad=async()=>/NaN|Infinity|undefined|null/.test(await txt());
const typeInto=async(idn,val)=>{await ev(`(()=>{const e=document.getElementById('${idn}');e.focus();e.select();})()`);await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Backspace',code:'Backspace',windowsVirtualKeyCode:8});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Backspace',code:'Backspace',windowsVirtualKeyCode:8}); if(val!=='') await send('Input.insertText',{text:val}); await sleep(80);};
const blur=()=>ev(`document.activeElement.blur()`);
const click=sel=>ev(`document.querySelector('${sel}').click()`);

let s=await state();
T('initial: stage 0, formula hidden, 1000 dots',s.stage==='stage0'&&s.formula==='none'&&Object.values(s.cnt).reduce((a,b)=>a+b)===1000,JSON.stringify(s));
T('definition of "accurate" shown', (await txt()).includes('catches 90 of every 100 sick people'));
for(let i=0;i<3;i++) await click('#next'); await sleep(150); s=await state();
T('stage 3 shows 8.33% and unlocks formula',s.post==='8.33%'&&s.formula==='block'&&s.stage==='stage3',JSON.stringify(s));
T('counts 9/1/99/891',JSON.stringify(s.cnt)==='{"tp":9,"fn":1,"fp":99,"tn":891}',JSON.stringify(s.cnt));
// real typing
await typeInto('prev-n','50'); s=await state(); T('typing prevalence 50 -> 90%',s.post==='90%',s.post+' '+s.prev);
await typeInto('prev-n','0'); s=await state(); T('typing 0 -> 0% , no NaN',s.post==='0%'&&!(await bad()),s.post);
await typeInto('prev-n','100'); s=await state(); T('typing 100 -> 100%',s.post==='100%'&&!(await bad()),s.post);
await typeInto('prev-n','150'); s=await state(); T('typing 150 clamps to 100',s.post==='100%',s.post); await blur(); s=await state(); T('blur tidies box to 100',s.prev==='100',s.prev);
await typeInto('prev-n','-5'); await blur(); s=await state(); T('typing -5 -> 0 after blur',s.prev==='0',s.prev);
await typeInto('prev-n',''); s=await state(); T('empty box: no crash/NaN, state kept',!(await bad())&&s.post!=='' ,JSON.stringify(s.post)); await blur(); s=await state(); T('empty box restored on blur',s.prev==='0',s.prev);
await typeInto('prev-n','abc'); s=await state(); T('letters ignored, no NaN',!(await bad())); await blur();
await typeInto('prev-n','0.1'); await typeInto('sens-n','99'); await typeInto('fpr-n','1'); s=await state(); T('rare+precise (0.1/99/1) ≈ 9%',s.post==='9.02%'||s.post==='9%'||/^9\./.test(s.post),s.post);
await typeInto('fpr-n','0'); await typeInto('sens-n','0'); s=await state(); T('nobody positive -> n/a, no NaN',s.post==='n/a'&&!(await bad()),s.post);
// keyboard on slider
await typeInto('prev-n','1'); await typeInto('sens-n','90'); await typeInto('fpr-n','10'); await blur();
await ev(`document.getElementById('prev-r').focus()`);
for(let i=0;i<5;i++){await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});}
s=await state(); T('slider arrow keys raise prevalence 1 -> 1.5 and box follows',parseFloat(s.prev)===1.5,s.prev);
// presets
await ev(`[...document.querySelectorAll('#presets button')].find(b=>b.textContent.includes('common')).click()`); s=await state();
T('preset "common" -> 90% and boxes synced',s.post==='90%'&&s.prev==='50',JSON.stringify(s));
await ev(`[...document.querySelectorAll('#presets button')].find(b=>b.textContent.includes('useless')).click()`); s=await state();
T('useless test -> posterior equals prior 10%',s.post==='10%',s.post);
// guess
await click('.guesses button[data-g="10"]'); T('guess 10 feedback',(await ev(`document.getElementById('gfeed').textContent`)).includes('8%'));
await click('.guesses button[data-g="90"]'); T('guess 90 feedback',(await ev(`document.getElementById('gfeed').textContent`)).includes('A very common answer'));
// hover highlight with real mouse
await ev(`document.querySelector('#presets button').click()`);
await ev(`document.querySelector('#f1 .term').scrollIntoView({block:'center'})`); await sleep(100);
const r=JSON.parse(await ev(`(()=>{const b=document.querySelector('#f1 .term').getBoundingClientRect();return JSON.stringify({x:b.x+b.width/2,y:b.y+b.height/2})})()`));
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:r.x,y:r.y}); await sleep(120);
const dim=await ev(`document.querySelectorAll('circle.dim').length`), hl=await ev(`document.querySelectorAll('circle.hl').length`);
T('hover numerator: 9 dots lit, 991 dimmed',hl===9&&dim===991,`hl=${hl} dim=${dim}`);
await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:5,y:5}); await sleep(120);
T('mouse leaves: nothing dimmed',(await ev(`document.querySelectorAll('circle.dim').length`))===0);
// back button & stage cycle
for(let i=0;i<3;i++) await click('#back'); s=await state(); T('Back returns to stage 0, Back disabled',s.stage==='stage0'&&await ev(`document.getElementById('back').disabled`));
T('no JS errors during run',errors.length===0,errors.join('|'));
console.log(`\n${pass} passed, ${fail} failed`);
ws.close(); proc.kill(); process.exit(fail?1:0);
