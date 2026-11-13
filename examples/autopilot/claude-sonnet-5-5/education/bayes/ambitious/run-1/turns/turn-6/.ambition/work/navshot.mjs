import { spawn } from 'node:child_process'; import fs from 'node:fs';
const proc=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--remote-debugging-port=9343','--user-data-dir=/tmp/bayes-nav','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9343/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const p=new Map();ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&p.has(d.id)){p.get(d.id)(d);p.delete(d.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;p.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>(await send('Runtime.evaluate',{expression:e,returnByValue:true})).result.result.value;
const out=[];
for(const w of [320,375,768]){
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:900,deviceScaleFactor:1,mobile:w<500});
  await send('Page.navigate',{url:'file:///Volumes/My%20Shared%20Files/work/bayes.html'}); await sleep(400); await send('Page.reload'); await sleep(700);
  await ev(`document.getElementById('play').click()`); await sleep(500);
  const r=JSON.parse(await ev(`JSON.stringify([document.querySelector('.nav').getBoundingClientRect().top+scrollY,document.querySelector('#story').getBoundingClientRect().bottom+scrollY, Math.max(document.documentElement.scrollWidth)])`));
  const s=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:r[0]-12,width:w,height:r[1]-r[0]+24,scale:1}});
  fs.writeFileSync(`nav_${w}.png`,Buffer.from(s.result.data,'base64')); out.push(w+'px scrollWidth='+r[2]);
}
console.log(out.join('  ')); ws.close();proc.kill();
