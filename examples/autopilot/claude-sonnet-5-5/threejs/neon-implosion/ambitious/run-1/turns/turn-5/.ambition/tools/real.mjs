import {chromium} from 'playwright';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:800,height:450}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.argv[2]+'?still');
const range=await p.evaluate(()=>{const g=document.createElement('canvas').getContext('webgl2');return [...g.getParameter(g.ALIASED_POINT_SIZE_RANGE)]});
console.log('point size range (this headless GPU):',range);
const t0=Date.now(),out=[];
for(let i=0;i<24;i++){out.push([((Date.now()-t0)/1000).toFixed(1),await p.evaluate(()=>parseFloat(document.getElementById('bar').style.width).toFixed(1))]);await p.waitForTimeout(500);}
console.log('real clock (s since load, bar % of loop):',out.map(x=>x.join(':')).join(' '));
console.log('errors',JSON.stringify(errs));await b.close();
