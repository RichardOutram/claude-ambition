// Outside checks: solver teaching checks + real Chrome playthrough of every level via keyboard
const fs=require('fs');const {parse,solve,strip}=require('./logic.js');const pp=require('puppeteer-core');
const rows=require('./final_levels.json');const names=['Mirror','Flip','Pits','Axis'];const ch=[[0,1],[2,6],[7,10],[11,15]];
let bad=0;
rows.forEach((r,i)=>{const L=parse(r),s=solve(L);const c=ch.findIndex(([a,b])=>i>=a&&i<=b);let note='';
 if(c===1){const w=solve(strip(L,{pads:true}));note='no-pads='+w.d;if(w.d!==-1)bad++;}
 if(c===2){const w=solve(strip(L,{pits:true}));note='no-pits='+w.d;if(!(w.d>0&&w.d<s.d))bad++;}
 if(c===3){const w=solve(strip(L,{pads:'g'}));note='no-g='+w.d;if(w.d!==-1)bad++;}
 console.log(String(i+1).padStart(2),names[c].padEnd(6),'par',String(s.d).padStart(2),'optimal solutions',s.count,note);});
console.log('teaching-check failures:',bad);
(async()=>{const b=await pp.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const errs=[];const pg=await b.newPage();pg.on('pageerror',e=>errs.push(e.message));pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await pg.setViewport({width:1000,height:760});await pg.goto('file:///Volumes/My Shared Files/work/mirror-twins.html');
const key=['ArrowRight','ArrowLeft','ArrowDown','ArrowUp'];let fail=0;
for(let i=0;i<rows.length;i++){await pg.evaluate(i=>window.__mt.load(i),i);const s=solve(parse(rows[i]));
 for(const m of s.path){await pg.keyboard.press(key[m]);}
 await new Promise(r=>setTimeout(r,60));
 const st=await pg.evaluate(()=>({won:window.__mt.state.won,moves:window.__mt.state.moves,stars:document.querySelectorAll('#stars i.on').length}));
 const ok=st.won&&st.moves===s.d;if(!ok)fail++;console.log('browser L'+(i+1),ok?'WON':'FAIL',JSON.stringify(st));}
console.log('browser failures:',fail,'console errors:',errs.length,errs.slice(0,3));await b.close();})();
