import { spawn } from 'node:child_process';
const proc=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--remote-debugging-port=9337','--user-data-dir=/tmp/bayes-cdp-bar','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let list;
for(let i=0;i<50;i++){try{list=await (await fetch('http://127.0.0.1:9337/json')).json();if(list.length)break}catch{}await sleep(200)}
const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let id=0;const p=new Map();ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&p.has(d.id)){p.get(d.id)(d);p.delete(d.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;p.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const ev=async e=>(await send('Runtime.evaluate',{expression:e,returnByValue:true})).result.result.value;
await send('Emulation.setDeviceMetricsOverride',{width:1000,height:900,deviceScaleFactor:1,mobile:false});
let bad=0;
for(const q of ['prev=1&sens=90&fpr=10','prev=50&sens=90&fpr=10','prev=0.01&sens=99.9&fpr=0.01','prev=100&sens=90&fpr=10','prev=1&sens=0&fpr=100','prev=0.0067&sens=99&fpr=0.1']){
  await send('Page.navigate',{url:'file:///Volumes/My%20Shared%20Files/work/bayes.html#'+q+'&stage=3'}); await sleep(400); await send('Page.reload'); await sleep(700);
  const r=JSON.parse(await ev(`(()=>{const b=document.getElementById('bar');const w=b.getBoundingClientRect().width;const kids=[...b.children].filter(c=>c.style.display!=='none').map(c=>c.getBoundingClientRect().width);return JSON.stringify({w,sum:kids.reduce((a,c)=>a+c,0)+2*Math.max(0,kids.length-1)})})()`));
  const ok=Math.abs(r.w-r.sum)<2; if(!ok)bad++; console.log(ok?'PASS':'FAIL',q,'bar',Math.round(r.w),'filled',Math.round(r.sum));
}
ws.close();proc.kill();process.exit(bad?1:0);
