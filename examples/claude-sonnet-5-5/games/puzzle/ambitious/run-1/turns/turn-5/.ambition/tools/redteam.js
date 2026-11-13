const pp=require('puppeteer-core');const URL='file:///Volumes/My Shared Files/work/mirror-twins.html';
(async()=>{const b=await pp.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const cases={'cur out of range':{best:{},cur:99},'cur negative':{best:{},cur:-5},'best NaN/strings':{best:{0:'x',1:null,2:-3,'abc':4,99:5,3:1e9},cur:'2'},'best array':{best:[1,2],cur:0},'null':null,'string':'hi','huge':{best:{0:1},cur:0,x:'a'.repeat(1e5)}};
for(const [n,v] of Object.entries(cases)){const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.evaluateOnNewDocument(v=>localStorage.setItem('mirror-twins-v2',JSON.stringify(v)),v);await p.goto(URL);
await p.click('#play').catch(()=>{});await new Promise(r=>setTimeout(r,80));await p.click('#gmap').catch(()=>{});await new Promise(r=>setTimeout(r,80));
const s=await p.evaluate(()=>{try{return {scr:window.__mt.state.scr,li:window.__mt.state.li,share:(document.querySelector('#share').click(),document.querySelector('#toast').textContent),prog:document.querySelectorAll('.lv small').length}}catch(e){return 'ERR '+e.message}});
console.log(n.padEnd(18),errs.length?'PAGEERRORS '+errs[0]:'ok',JSON.stringify(s));await p.close();}
// key spam during animation & after win
const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));await p.goto(URL);await p.click('#play');
for(let i=0;i<300;i++)await p.keyboard.press(['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','z','r'][i%6]);
console.log('key spam errors',errs.length);await b.close();})();
