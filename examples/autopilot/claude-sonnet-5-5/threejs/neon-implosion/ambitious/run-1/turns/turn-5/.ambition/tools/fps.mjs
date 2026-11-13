import {chromium} from 'playwright';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
for(const q of process.argv.slice(3)){
  const ctx=await b.newContext({viewport:{width:640,height:360}});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+process.argv[2]+'?still&q='+q);await p.waitForTimeout(2500);
  const r=await p.evaluate(()=>new Promise(res=>{let k=0;const t0=performance.now();const f=()=>{k++;if(performance.now()-t0>4000)res(k/4);else requestAnimationFrame(f);};f();}));
  const n=await p.evaluate(()=>window.__neon.particles);
  console.log('q='+q,'particles',n,'fps',r.toFixed(1),'frame ms',(1000/r).toFixed(1),errs.length?errs:'');await ctx.close();}
await b.close();
