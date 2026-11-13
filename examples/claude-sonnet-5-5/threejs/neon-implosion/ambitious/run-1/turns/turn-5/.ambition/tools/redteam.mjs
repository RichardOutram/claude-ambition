import {chromium} from 'playwright'; import {PNG} from 'pngjs';
const url='file://'+process.argv[2];
const sw=['--use-angle=swiftshader','--enable-unsafe-swiftshader'];
const lin=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);};
const lum=buf=>{const d=PNG.sync.read(buf).data;let s=0;for(let i=0;i<d.length;i+=4)s+=.2126*lin(d[i])+.7152*lin(d[i+1])+.0722*lin(d[i+2]);return s/(d.length/4);};
const b=await chromium.launch({channel:'chrome',args:sw});
for(const rm of [false,true]){
  const ctx=await b.newContext({viewport:{width:320,height:180},reducedMotion:rm?'reduce':'no-preference'});
  const p=await ctx.newPage();
  await p.addInitScript(()=>{let n=0;performance.now=()=>n;window.__set=m=>{n=m};});
  await p.goto(url+'?still');await p.addStyleTag({content:'#bar,#hint{display:none}'});await p.waitForTimeout(1200);
  const raf=()=>p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const L=[];
  for(let i=0;i<=16;i++){const t=8.2+i*(1/30);await p.evaluate(ms=>window.__set(ms),(t-8.5+10)%10*1000);await raf();L.push(lum(await p.screenshot()));}
  let mj=0;for(let i=1;i<L.length;i++)mj=Math.max(mj,Math.abs(L[i]-L[i-1]));
  console.log(rm?'REDUCED MOTION':'NORMAL        ','peak rel. luminance',Math.max(...L).toFixed(3),'| min',Math.min(...L).toFixed(3),'| biggest 1/30s step',mj.toFixed(3),'\n   series',L.map(x=>x.toFixed(2)).join(' '));
  await ctx.close();
}
// CDN blocked
{const p=await b.newPage();await p.route('**/unpkg.com/**',r=>r.abort());await p.goto(url);await p.waitForTimeout(1500);
 console.log('CDN blocked ->',JSON.stringify((await p.innerText('body')).replace(/\s+/g,' ').slice(0,90)),'| cursor hidden:',await p.evaluate(()=>document.documentElement.classList.contains('live')));await p.close();}
await b.close();
// WebGL unavailable
const b2=await chromium.launch({channel:'chrome',args:['--disable-3d-apis','--disable-gpu']});
{const p=await b2.newPage();await p.goto(url);await p.waitForTimeout(2500);
 console.log('WebGL off   ->',JSON.stringify((await p.innerText('body')).replace(/\s+/g,' ').slice(0,90)),'| cursor hidden:',await p.evaluate(()=>document.documentElement.classList.contains('live')));}
await b2.close();
