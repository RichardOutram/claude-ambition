const {parse,solve,strip}=require('./logic.js');const rows=require('./final_levels.json');
const ch=[[0,1],[2,6],[7,10],[11,15]];
const chap=i=>ch.findIndex(([a,b])=>i>=a&&i<=b);
function reqOk(rowsArr,i){const L=parse(rowsArr),s=solve(L);if(s.d<1)return false;const c=chap(i);
 if(c===1)return solve(strip(L,{pads:true})).d===-1;
 if(c===2){const w=solve(strip(L,{pits:true}));return w.d>0&&w.d<s.d;}
 if(c===3)return solve(strip(L,{pads:'g'})).d===-1;return true;}
const objs=r=>{const o=[];for(let y=1;y<r.length-1;y++)for(let x=1;x<r[0].length-1;x++)if('#fgx'.includes(r[y][x]))o.push([x,y]);return o;};
const without=(r,[x,y])=>r.map((row,j)=>j===y?row.slice(0,x)+'.'+row.slice(x+1):row);
function measure(r){const base=solve(parse(r));const o=objs(r);let load=0;const slack=[];
 for(const p of o){const s=solve(parse(without(r,p)));const lb=s.d!==base.d||s.count>base.count;if(lb)load++;else slack.push(p);}
 return {n:o.length,load,slack,base};}
const before=[],after=[],out=[];
rows.forEach((r,i)=>{const m=measure(r);before.push(m);let cur=r;
 for(let guard=0;guard<40;guard++){const mm=measure(cur);if(!mm.slack.length)break;let done=false;
  for(const p of mm.slack){const cand=without(cur,p);if(reqOk(cand,i)){cur=cand;done=true;break;}}if(!done)break;}
 const m2=measure(cur);after.push(m2);out.push(cur);
 console.log(String(i+1).padStart(2),'objects',m.n,'load-bearing',m.load,'->',m2.n,m2.load,'par',m.base.d,'->',m2.base.d,'solutions',m.base.count,'->',m2.base.count);});
const sum=a=>a.reduce((x,m)=>x+m.n,0),lb=a=>a.reduce((x,m)=>x+m.load,0);
console.log('BEFORE load-bearing',lb(before)+'/'+sum(before),' AFTER',lb(after)+'/'+sum(after));
require('fs').writeFileSync('pruned_levels.json',JSON.stringify(out));
