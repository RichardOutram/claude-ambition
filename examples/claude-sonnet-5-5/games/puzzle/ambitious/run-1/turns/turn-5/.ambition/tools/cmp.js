const pp=require('puppeteer-core');const wait=ms=>new Promise(r=>setTimeout(r,ms));
const F1='file:///Volumes/My Shared Files/work/.ambition/first/mirror-twins.html',F2='file:///Volumes/My Shared Files/work/mirror-twins.html';
(async()=>{const b=await pp.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
for(const [n,u] of [['first',F1],['final',F2]]){for(const [w,h] of [[320,568],[390,780],[667,375]]){const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));await p.setViewport({width:w,height:h,isMobile:true,hasTouch:true});await p.goto(u);
 if(n==='final'){await p.evaluate(()=>window.__mt.load(6));}await wait(150);
 const m=await p.evaluate(()=>{const c=document.querySelector('canvas#c');const r=c.getBoundingClientRect();const bs=[...document.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>Math.round(Math.min(b.offsetWidth,b.offsetHeight)));
 return {board:[Math.round(r.width),Math.round(r.height)],fits:r.right<=innerWidth&&r.bottom<=innerHeight,scroll:document.documentElement.scrollHeight>innerHeight||document.documentElement.scrollWidth>innerWidth,minBtn:Math.min(...bs),touchControls:!!document.getElementById('pad')};});
 console.log(n.padEnd(5),w+'x'+h,JSON.stringify(m),'errors',errs.length);await p.close();}}
// win card shot + title + phone game + landscape
const shots=[];const S=async(name,vp,fn,mob)=>{const p=await b.newPage();await p.setViewport(Object.assign({deviceScaleFactor:1},vp,mob?{isMobile:true,hasTouch:true}:{}));await p.goto(F2);await fn(p);await wait(700);await p.screenshot({path:name+'.png'});shots.push(name);await p.close();};
const {parse,solve}=require('./logic.js');const rows=require('./final_levels.json');const key=['ArrowRight','ArrowLeft','ArrowDown','ArrowUp'];
await S('j_win',{width:700,height:520},async p=>{await p.evaluate(()=>window.__mt.load(2));for(const m of solve(parse(rows[2])).path)await p.keyboard.press(key[m]);await wait(600);});
await S('j_phone',{width:390,height:700},async p=>{await p.evaluate(()=>window.__mt.load(11))},true);
await S('j_land',{width:667,height:375},async p=>{await p.evaluate(()=>window.__mt.load(9))},true);
await S('j_title',{width:390,height:700},async p=>{},true);
require('fs').writeFileSync('sheet4.html','<body style="margin:0;background:#000;display:flex;gap:6px;align-items:flex-start">'+shots.map(n=>'<img src="'+n+'.png" style="height:420px">').join('')+'</body>');
const s=await b.newPage();await s.setViewport({width:1500,height:430});await s.goto('file:///Volumes/My Shared Files/work/.ambition/tools/sheet4.html');await wait(300);await s.screenshot({path:'sheet4.png'});await b.close();})();
