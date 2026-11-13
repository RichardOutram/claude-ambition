import {chromium} from 'playwright'; import {PNG} from 'pngjs';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
async function run(q){const p=await b.newPage({viewport:{width:640,height:360}});
 await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
 await p.goto('file://'+process.argv[2]+q);await p.addStyleTag({content:'#bar,#hint{display:none}'});await p.waitForTimeout(1300);
 const raf=()=>p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 for(let i=0;i<40;i++){await p.evaluate(m=>window.__set(m),3500+i*40);const a=i/39;await p.mouse.move(70+a*260,300+Math.sin(a*6.28)*22);await raf();}
 return PNG.sync.read(await p.screenshot());}
const A=await run(''),B=await run('?still');
let sx=0,sy=0,sw=0,minx=1e9,maxx=0,miny=1e9,maxy=0;
for(let y=0;y<360;y++)for(let x=0;x<640;x++){const i=(y*640+x)*4;const d=Math.abs(A.data[i]-B.data[i])+Math.abs(A.data[i+1]-B.data[i+1])+Math.abs(A.data[i+2]-B.data[i+2]);if(d>60){sx+=x*d;sy+=y*d;sw+=d;minx=Math.min(minx,x);maxx=Math.max(maxx,x);miny=Math.min(miny,y);maxy=Math.max(maxy,y);}}
console.log('diff centroid',(sx/sw).toFixed(0),(sy/sw).toFixed(0),'bbox',minx,maxx,miny,maxy,'(pointer path x 70-330, y 278-322)');
await b.close();
