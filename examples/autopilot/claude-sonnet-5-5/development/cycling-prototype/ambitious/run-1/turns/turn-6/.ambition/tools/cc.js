const { chromium } = require('playwright-core');const path=require('path');const fs=require('fs');
const axeSrc=fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
const S={auth:`S.authed=false;render()`,feed:`S.authed=true;S.tab='feed';S.stack=[];render()`,ride:`S.authed=true;S.stack=[{v:'ride',id:1}];render()`,club:`S.authed=true;S.tab='clubs';S.stack=[{v:'club',id:1}];render()`,profile:`S.authed=true;S.tab='profile';S.stack=[];render()`,record:`S.authed=true;S.tab='record';S.stack=[];render()`,clubs:`S.authed=true;S.tab='clubs';S.stack=[];render()`};
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});const seen=new Set();
for(const [n,js] of Object.entries(S)){const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+path.resolve(process.argv[2]));await pg.evaluate(js);await pg.addScriptTag({content:axeSrc});
const r=await pg.evaluate(()=>axe.run('.phone',{runOnly:['color-contrast']}));
r.violations.forEach(v=>v.nodes.forEach(nd=>{const d=nd.any[0].data;const k=`${d.fgColor} on ${d.bgColor} ${d.contrastRatio} (${d.fontSize}) "${(nd.html.match(/>([^<]{2,20})/)||[])[1]}"`;if(!seen.has(k)){seen.add(k);console.log(n+': '+k)}}));await pg.close()}
await b.close()})();
