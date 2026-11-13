import { spawn } from 'node:child_process'; import fs from 'node:fs';
const proc=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--remote-debugging-port=9334','--user-data-dir=/tmp/bayes-cdp-dark','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9334/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const p=new Map();ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&p.has(d.id)){p.get(d.id)(d);p.delete(d.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;p.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
await send('Emulation.setDeviceMetricsOverride',{width:390,height:1250,deviceScaleFactor:1,mobile:true});
await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:'dark'}]});
await send('Page.navigate',{url:'file:///Volumes/My%20Shared%20Files/work/bayes.html#prev=1&sens=90&fpr=10&stage=3'}); await sleep(1200);
const r=await send('Page.captureScreenshot',{format:'png',clip:{x:0,y:620,width:390,height:630,scale:1}});
fs.writeFileSync('dark3.png',Buffer.from(r.result.data,'base64')); ws.close(); proc.kill();
