import {chromium} from 'playwright'; import {PNG} from 'pngjs';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const diff=(A,B)=>{const x=PNG.sync.read(A).data,y=PNG.sync.read(B).data;let s=0;for(let i=0;i<x.length;i+=4)s+=Math.abs(x[i]-y[i])+Math.abs(x[i+1]-y[i+1])+Math.abs(x[i+2]-y[i+2]);return +(s/(x.length/4*3)).toFixed(3);};
async function open(q){const p=await b.newPage({viewport:{width:640,height:360}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
 await p.goto('file://'+process.argv[2]+q);await p.waitForTimeout(1200);
 p.raf=()=>p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))); p.errs=errs; return p;}
// 1) noise floor with DOM overlays hidden
let p=await open('?still');
await p.addStyleTag({content:'#bar,#hint{display:none}'});
const shots=[];for(const ms of [0,0.2,0.4]){await p.evaluate(m=>window.__set(m),ms);await p.raf();shots.push(await p.screenshot());}
console.log('noise floor, overlays hidden (0 vs 0.2ms, 0.2 vs 0.4ms):',diff(shots[0],shots[1]),diff(shots[1],shots[2]));
// 2) click shockwave: same time & pointer, with and without a click
async function run(click){const p=await open('');
 await p.evaluate(()=>window.__set(3500));await p.raf();
 await p.mouse.move(420,200);for(let i=0;i<6;i++){await p.evaluate(m=>window.__set(m),3500+i*30);await p.raf();}
 if(click){await p.mouse.down();await p.mouse.up();}
 for(let i=0;i<14;i++){await p.evaluate(m=>window.__set(m),3700+i*30);await p.raf();}
 const s=await p.screenshot();console.log(click?'click':'noclick','errors',JSON.stringify(p.errs));return s;}
const a=await run(false),c=await run(true);
console.log('click vs no click frame difference (noise floor ~3):',diff(a,c));
const fs=await import('fs');fs.writeFileSync(process.argv[3],c);
await b.close();
