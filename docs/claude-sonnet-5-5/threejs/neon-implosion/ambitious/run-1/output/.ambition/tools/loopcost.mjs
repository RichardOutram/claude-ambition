// mean + per-phase software-render cost across the loop. usage: node loopcost.mjs <html> <q...>
import {chromium} from 'playwright';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const T=[0.5,1.5,2.5,3.5,4.5,5.5,6.2,6.8,7.3,7.8,8.1,8.3,8.45,8.6,8.8,9.0,9.3,9.6];
for(const q of process.argv.slice(3)){
  const ctx=await b.newContext({viewport:{width:640,height:360}});const p=await ctx.newPage();
  await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
  await p.goto('file://'+process.argv[2]+'?still&q='+q);await p.waitForTimeout(2500);
  const ms=[];
  for(const t of T){const now=((t-8.7)%10+10)%10*1000;
    const t0=Date.now();
    for(let i=0;i<4;i++){await p.evaluate(m=>window.__set(m),now);await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
    ms.push((Date.now()-t0)/8);}
  const mean=ms.reduce((a,x)=>a+x,0)/ms.length;
  console.log('q='+q,'mean ms/frame',mean.toFixed(1),'| worst',Math.max(...ms).toFixed(1),'| by phase',T.map((t,i)=>t+':'+ms[i].toFixed(0)).join(' '));
  await ctx.close();}
await b.close();
