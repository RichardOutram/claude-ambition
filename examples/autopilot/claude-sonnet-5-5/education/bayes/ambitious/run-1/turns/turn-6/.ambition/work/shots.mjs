import { spawn } from 'node:child_process'; import fs from 'node:fs';
const proc=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--remote-debugging-port=9336','--user-data-dir=/tmp/bayes-cdp-shots','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9336/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const p=new Map();ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&p.has(d.id)){p.get(d.id)(d);p.delete(d.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;p.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>(await send('Runtime.evaluate',{expression:e,returnByValue:true})).result.result.value;
const shot=async(name,w,h,hash,top,bottom)=>{
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:w<500});
  await send('Page.navigate',{url:'file:///Volumes/My%20Shared%20Files/work/bayes.html'+hash}); await sleep(500); await send('Page.reload'); await sleep(900);
  const r=JSON.parse(await ev(`JSON.stringify([document.querySelector('${top}').getBoundingClientRect().top+scrollY,document.querySelector('${bottom}').getBoundingClientRect().bottom+scrollY])`));
  const s=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:r[0]-8,width:w,height:r[1]-r[0]+16,scale:1}});
  fs.writeFileSync(name,Buffer.from(s.result.data,'base64'));
};
await shot('r5_desk.png',1000,1000,'#prev=1&sens=90&fpr=10&stage=3','.play','.play');
await shot('r5_phone.png',390,900,'#prev=1&sens=90&fpr=10&stage=3','#challenge','#safety');
ws.close();proc.kill();
