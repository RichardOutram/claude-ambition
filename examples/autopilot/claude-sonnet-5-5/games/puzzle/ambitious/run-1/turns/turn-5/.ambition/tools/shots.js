const pp=require('puppeteer-core'),fs=require('fs');
(async()=>{const b=await pp.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const shots=[];async function shot(name,vp,fn,mobile){const pg=await b.newPage();await pg.setViewport(Object.assign({deviceScaleFactor:1},vp,mobile?{isMobile:true,hasTouch:true}:{}));
await pg.goto('file:///Volumes/My Shared Files/work/mirror-twins.html');await fn(pg);await new Promise(r=>setTimeout(r,600));const f='/tmp/gen/'+name+'.png';await pg.screenshot({path:f});shots.push([name,f,vp]);await pg.close();}
await shot('d_title',{width:900,height:620},async p=>{});
await shot('d_game',{width:900,height:620},async p=>{await p.evaluate(()=>{localStorage.setItem('mirror-twins-v2',JSON.stringify({best:{},cur:0}));window.__mt.load(11)});await p.keyboard.press('ArrowRight');});
await shot('p_game',{width:390,height:780},async p=>{await p.evaluate(()=>window.__mt.load(6))},true);
await shot('p_map',{width:390,height:780},async p=>{await p.evaluate(()=>{const b={};for(let i=0;i<9;i++)b[i]=[2,7,6,10,13,16,17,8,12][i]+(i%3);localStorage.setItem('mirror-twins-v2',JSON.stringify({best:b,cur:9}));});await p.reload();await p.click('#maps');},true);
const html='<body style="margin:0;background:#000;display:flex;gap:8px;align-items:flex-start">'+shots.filter(s=>s[0]!=='d_game').map(s=>'<img src="file://'+s[1]+'" style="height:620px;width:auto">').join('')+'</body>';
fs.writeFileSync('/tmp/gen/sheet.html',html);const pg=await b.newPage();await pg.setViewport({width:1250,height:630});await pg.goto('file:///tmp/gen/sheet.html');await new Promise(r=>setTimeout(r,300));await pg.screenshot({path:'/tmp/gen/sheet.png'});await b.close();})();
