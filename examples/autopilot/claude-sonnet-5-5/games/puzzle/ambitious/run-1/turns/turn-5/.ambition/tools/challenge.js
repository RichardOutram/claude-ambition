const pp=require('puppeteer-core');const {parse,step,startState,canWin}=require('./logic.js');const rows=require('./final_levels.json');
const URL='file:///Volumes/My Shared Files/work/mirror-twins.html';const key=['ArrowRight','ArrowLeft','ArrowDown','ArrowUp'];
(async()=>{const b=await pp.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const wait=ms=>new Promise(r=>setTimeout(r,ms));
// 1. storage blocked
let pg=await b.newPage();const errs=[];pg.on('pageerror',e=>errs.push(e.message));
await pg.evaluateOnNewDocument(()=>{Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})});
await pg.goto(URL);await pg.click('#play');await wait(100);console.log('1 storage-blocked: screen',await pg.evaluate(()=>window.__mt.state.scr),'errors',errs.length);await pg.close();
// 6 continue flow + stuck hint
pg=await b.newPage();errs.length=0;pg.on('pageerror',e=>errs.push(e.message));await pg.setViewport({width:900,height:700});await pg.goto(URL);
await pg.click('#play');await wait(50);let st=await pg.evaluate(()=>window.__mt.state);console.log('6a first play ->level',st.li+1);
for(const m of [0,0])await pg.keyboard.press(key[m]);await wait(600);
await pg.keyboard.press('Enter');await wait(100);st=await pg.evaluate(()=>window.__mt.state);console.log('6b Enter after win -> level',st.li+1);
await pg.keyboard.press('Escape');await pg.reload();await pg.click('#play');await wait(50);st=await pg.evaluate(()=>window.__mt.state);console.log('6c reload+Continue -> level',st.li+1,'(expect 3 or 2)');
// stuck: find a dead state on level 10 by BFS from start
const L=parse(rows[9]);let path=null;{const seen=new Set();let q=[[startState(L),[]]];while(q.length&&!path){const n=[];for(const [s,p] of q){for(let m=0;m<4;m++){const o=step(L,s.slice(),m);if(!o.moved)continue;const k=o.s.join();if(seen.has(k))continue;seen.add(k);const pp2=p.concat(m);if(!canWin(L,o.s)){path=pp2;break;}n.push([o.s,pp2]);}if(path)break;}q=n;}}
await pg.evaluate(()=>window.__mt.load(9));for(const m of path)await pg.keyboard.press(key[m]);await wait(100);
console.log('stuck path len',path.length,'hint:',await pg.$eval('#hint',e=>e.textContent));await pg.keyboard.press('z');await wait(50);console.log('after undo hint:',await pg.$eval('#hint',e=>e.textContent).then(t=>t.slice(0,30)));
console.log('errors',errs.length);
// 2 phone map + landscape game: measure overflow
async function phone(vp,fn,name){const p=await b.newPage();await p.setViewport(Object.assign({deviceScaleFactor:2,isMobile:true,hasTouch:true},vp));await p.goto(URL);await fn(p);await wait(400);
 const m=await p.evaluate(()=>{const r=e=>{const x=document.querySelector(e);if(!x)return null;const b=x.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)]};return {vw:innerWidth,vh:innerHeight,canvas:r('#c'),pad:r('#pad'),top:r('#top'),hint:r('#hint'),docW:document.documentElement.scrollWidth}});
 console.log(name,JSON.stringify(m));await p.screenshot({path:name+'.png'});await p.close();}
await phone({width:390,height:780},async p=>{await p.click('#maps')},'phone_map');
await phone({width:390,height:780},async p=>{await p.evaluate(()=>window.__mt.load(15))},'phone_L16');
await phone({width:667,height:375},async p=>{await p.evaluate(()=>window.__mt.load(6))},'land_L7');
await phone({width:320,height:568},async p=>{await p.evaluate(()=>window.__mt.load(6))},'small_L7');
await b.close();})();
