import { spawn } from 'node:child_process';
const proc=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--remote-debugging-port=9341','--user-data-dir=/tmp/bayes-cold','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9341/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const p=new Map();ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&p.has(d.id)){p.get(d.id)(d);p.delete(d.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;p.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>(await send('Runtime.evaluate',{expression:e,returnByValue:true})).result.result.value;
await send('Emulation.setDeviceMetricsOverride',{width:1000,height:900,deviceScaleFactor:1,mobile:false});
await send('Page.navigate',{url:'file:///Volumes/My%20Shared%20Files/work/bayes.html'}); await sleep(900);
console.log('=== STAGE 1 of 4 (what a cold reader sees on arrival) ===\n'+await ev('document.body.innerText'));
for(let s=1;s<=3;s++){ await ev(`document.getElementById('next').click()`); await sleep(150); console.log(`\n=== AFTER NEXT x${s}: story ===\n`+await ev(`document.getElementById('story').innerText`)); }
console.log('\n=== FULL TEXT AT END ===\n'+await ev('document.body.innerText'));
ws.close();proc.kill();
