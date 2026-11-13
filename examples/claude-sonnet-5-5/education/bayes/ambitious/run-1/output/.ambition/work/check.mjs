import fs from 'node:fs';
const html = fs.readFileSync(process.argv[2],'utf8');
const src = html.split('// ===== MODEL-START')[1].split('// ===== MODEL-END')[0].replace(/^[^\n]*\n/,'');
const { model, counts, fmtPct, clampPct, resolve } = new Function(src + '; return {model,counts,fmtPct,clampPct,resolve};')();

// independent reference: exact rational arithmetic via BigInt (values are in units of 1/1000 %)
const U = 100000n; // percent*1000 -> denominator 100*1000
const vals = [0,0.05,0.1,0.5,1,2,5,10,25,50,75,90,95,99,99.9,100];
let n=0, bad=[], nulls=0;
for(const p of vals) for(const s of vals) for(const f of vals){
  n++;
  const P=BigInt(Math.round(p*1000)), S=BigInt(Math.round(s*1000)), F=BigInt(Math.round(f*1000));
  const num = S*P*1000n;                       // sens*prev   (scaled by 1e5*1e5... keep same scale as den)
  const den = S*P*1000n + F*(100000n-P)*1000n; // sens*prev + fpr*(1-prev)
  const m = model(p,s,f), c = counts(m,1000);
  const sum = c.tp+c.fn+c.fp+c.tn;
  const err = (msg)=>bad.push(`${p}/${s}/${f}: ${msg}`);
  if(sum!==1000) err('counts sum '+sum);
  for(const k of ['tp','fn','fp','tn']){ if(!Number.isInteger(c[k])||c[k]<0) err('bad count '+k+'='+c[k]); if(Math.abs(c[k]-m[k]*1000)>=1) err('count off '+k); }
  if(den===0n){ nulls++; if(m.post!==null) err('expected null posterior'); }
  else{
    const ref = Number(num*10n**15n/den)/1e15;
    if(m.post===null||Math.abs(m.post-ref)>1e-12) err(`posterior ${m.post} vs ${ref}`);
  }
  if(m.post!==null){ const R=resolve(m), Q=R.c.tp+R.c.fp;
    if(!(Q>0)) err('resolve: no positives at N='+R.N);
    else if(Math.abs(R.c.tp/Q-m.post)>0.015) err(`resolve: counts say ${R.c.tp/Q} vs exact ${m.post} (N=${R.N})`);
    if(R.c.tp+R.c.fn+R.c.fp+R.c.tn!==R.N) err('resolve: counts do not sum to N'); }
  const strs=[fmtPct(m.post??0),fmtPct(m.s),fmtPct(m.pH),fmtPct(m.f),fmtPct(m.pE),fmtPct(1-m.pH)];
  if(strs.some(t=>/NaN|Infinity|undefined|e[+-]/.test(t))) err('format '+strs);
}
// bad input robustness
for(const v of ['',' ','abc',NaN,Infinity,-5,150,null,undefined]){ const m=model(v,v,v); if(!isFinite(m.pE)) bad.push('input '+v); }
// real-world published-style cases the page must get right (scaled crowd when rare)
const real=[['mammography',1,90,9,9.17],['HIV low-risk',0.01,99.9,0.01,49.98],['newborn',0.0067,99,0.1,6.22],['tiny',0.04,90,1,3.48],['1-in-10M',0.00001,99,0.5,0.0002]];
for(const [n,p,s,f,ex] of real){ const m=model(p,s,f),R=resolve(m),Q=R.c.tp+R.c.fp;
  const shown=100*R.c.tp/Q; const ok=Q>0&&Math.abs(shown-100*m.post)<=0.5+1e-9;
  console.log(`${ok?'ok  ':'FAIL'} ${n}: exact ${(100*m.post).toPrecision(4)}% | crowd ${R.N}: ${R.c.tp} of ${Q}${R.low?' (zoomed out)':''}`); if(!ok) bad.push('real '+n); }
// headline example
const h=model(1,90,10); const hc=counts(h,1000);
console.log('headline', fmtPct(h.post), hc);
console.log(`combos=${n} nullPosterior=${nulls} failures=${bad.length}`);
console.log(bad.slice(0,10).join('\n'));
process.exit(bad.length?1:0);
