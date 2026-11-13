// node depth.js <html> : axe-core + tap-target measurement across states
const { chromium } = require('playwright-core');const path=require('path');const fs=require('fs');
const file=path.resolve(process.argv[2]);const axeSrc=fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
const STATES={auth:`S.authed=false;render()`,feed:`S.authed=true;S.tab='feed';S.stack=[];render()`,ride:`S.authed=true;S.stack=[{v:'ride',id:1}];render()`,segment:`S.authed=true;S.stack=[{v:'segment',id:1}];render()`,record:`S.authed=true;S.tab='record';S.stack=[];render()`,running:`S.authed=true;S.tab='record';S.stack=[];startRide()`,challenges:`S.authed=true;S.tab='challenges';S.stack=[];render()`,clubs:`S.authed=true;S.tab='clubs';S.stack=[];render()`,club:`S.authed=true;S.tab='clubs';S.stack=[{v:'club',id:1}];render()`,profile:`S.authed=true;S.tab='profile';S.stack=[];render()`};
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const small=[];const ax={};let hov=0;
for(const [n,js] of Object.entries(STATES)){const pg=await b.newPage({viewport:{width:375,height:667}});await pg.goto('file://'+file);await pg.evaluate(js);await pg.waitForTimeout(100);
 const r=await pg.evaluate(()=>{const o=[];document.querySelectorAll('.phone [onclick], .phone button').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&r.height&&(r.height<44||r.width<44))o.push((e.textContent||'').trim().slice(0,18)+' '+Math.round(r.width)+'x'+Math.round(r.height))});return {o,hs:document.documentElement.scrollWidth>innerWidth}});
 r.o.forEach(x=>small.push(n+': '+x));if(r.hs)hov++;
 await pg.addScriptTag({content:axeSrc});
 const res=await pg.evaluate(()=>axe.run('.phone',{runOnly:['wcag2a','wcag2aa']}));
 res.violations.forEach(v=>{ax[v.id]=ax[v.id]||{impact:v.impact,n:0,screens:new Set()};ax[v.id].n+=v.nodes.length;ax[v.id].screens.add(n)});
 await pg.close()}
console.log('Horizontal overflow screens at 375px:',hov);
console.log('Controls under 44px:',small.length);small.slice(0,60).forEach(s=>console.log('  '+s));
console.log('axe violations:');Object.entries(ax).forEach(([k,v])=>console.log(`  ${k} [${v.impact}] x${v.n} on ${[...v.screens].join(',')}`));
await b.close()})();
