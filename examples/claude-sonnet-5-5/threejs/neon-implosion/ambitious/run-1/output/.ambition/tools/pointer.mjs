import {chromium} from 'playwright';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:960,height:540}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>m.type()==='error'&&errs.push(m.text()));
await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
await p.goto('file://'+process.argv[2]);
const raf=()=>p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
await p.waitForTimeout(1200);
// loop time ~2s (calm): clock = 2-8.5+10 = 3.5s
const base=3500;
for(let i=0;i<40;i++){
  await p.evaluate(ms=>window.__set(ms),base+i*40);
  const a=i/39; await p.mouse.move(250+a*460, 270+Math.sin(a*6.28)*110);
  await raf();
}
await p.screenshot({path:process.argv[3]});
console.log('errors',JSON.stringify(errs));await b.close();
