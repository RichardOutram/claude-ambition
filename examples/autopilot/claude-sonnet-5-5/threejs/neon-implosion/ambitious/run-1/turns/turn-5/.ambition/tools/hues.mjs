import {chromium} from 'playwright'; import {PNG} from 'pngjs';
function hueStats(im){const d=im.data,bins=new Array(12).fill(0);let sat=0,n=0,vivid=0;
 for(let i=0;i<d.length;i+=4){const r=d[i],g=d[i+1],b=d[i+2],mx=Math.max(r,g,b),mn=Math.min(r,g,b);
  if(mx>128){sat+=(mx-mn)/mx;n++;}
  if(mx>77&&(mx-mn)/mx>.35){let h;const dl=mx-mn;if(mx===r)h=((g-b)/dl+6)%6;else if(mx===g)h=(b-r)/dl+2;else h=(r-g)/dl+4;bins[Math.min(11,Math.floor(h*2))]++;vivid++;}}
 return {sat:n?sat/n:0,bins:vivid>200?bins.filter(c=>c/vivid>.03).length:0,bd:bins.map(c=>vivid?Math.round(c/vivid*100):0).join(',')};}
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
for(const [name,file,q] of [['pre7 q1',process.argv[2],''],['new q1',process.argv[3],'&q=1'],['new q1.5',process.argv[3],'&q=1.5']]){
  const ctx=await b.newContext({viewport:{width:320,height:180}});const p=await ctx.newPage();
  await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
  await p.goto('file://'+file+'?still'+q);await p.addStyleTag({content:'#bar,#hint{display:none}'});await p.waitForTimeout(1500);
  const res=[];for(const t of [8.7,9.0]){await p.evaluate(m=>window.__set(m),((t-8.7)%10+10)%10*1000);await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   const h=hueStats(PNG.sync.read(await p.screenshot()));res.push(`t=${t}: bins ${h.bins} sat ${h.sat.toFixed(2)} [${h.bd}]`);}
  console.log(name.padEnd(9),res.join(' | '));await ctx.close();}
await b.close();
