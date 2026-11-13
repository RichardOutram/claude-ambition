const {parse,step,solve,startState,isWin}=require('./logic.js');const rows=require('./final_levels.json');
const k=s=>s.join(',');
rows.forEach((r,i)=>{const L=parse(r);const s0=startState(L);
 // forward reachable
 const seen=new Map([[k(s0),s0]]);let q=[s0];const edges=new Map();
 while(q.length){const n=[];for(const s of q){const outs=[];for(let m=0;m<4;m++){const o=step(L,s.slice(),m);if(!o.moved)continue;outs.push(o.s);const kk=k(o.s);if(!seen.has(kk)){seen.set(kk,o.s);n.push(o.s);}}edges.set(k(s),outs.map(k));}q=n;}
 // can-win set via reverse closure
 const rev=new Map();for(const [a,bs] of edges)for(const b of bs){if(!rev.has(b))rev.set(b,[]);rev.get(b).push(a);}
 const win=[...seen.values()].filter(s=>isWin(L,s)).map(k);const can=new Set(win);let st=[...win];
 while(st.length){const x=st.pop();for(const p of rev.get(x)||[])if(!can.has(p)){can.add(p);st.push(p);}}
 const dead=seen.size-can.size;
 // is each twin needed? solve with A frozen goal-check only: does optimal require both to move? count twin that never moves in optimal path
 const sol=solve(L);let s=s0.slice(),moveA=0,moveB=0;for(const m of sol.path){const o=step(L,s.slice(),m);if(o.s[0]!==s[0]||o.s[1]!==s[1])moveA++;if(o.s[2]!==s[2]||o.s[3]!==s[3])moveB++;s=o.s;}
 // near-par solutions: count win states reachable within par+ceil(.4par) by DP on exact length
 const lim=Math.ceil(sol.d*1.4);let cur=new Map([[k(s0),1]]);let ways=0;
 for(let d=1;d<=lim;d++){const nx=new Map();for(const [kk,c] of cur){const s=kk.split(',').map(Number);if(isWin(L,s)){}for(let m=0;m<4;m++){const o=step(L,s.slice(),m);if(!o.moved)continue;const k2=k(o.s);nx.set(k2,(nx.get(k2)||0)+c);}}cur=nx;if(d>=sol.d)for(const [kk,c] of cur)if(isWin(L,kk.split(',').map(Number)))ways+=c;}
 // double-flip: optimal path step where both twins land on pads simultaneously
 let dbl=0;s=s0.slice();for(const m of sol.path){const o=step(L,s.slice(),m);if(o.flips===2)dbl++;s=o.s;}
 // random-walk solve rate (500 walks x 400 moves)
 let rw=0;for(let w=0;w<500;w++){let t=s0.slice();for(let n=0;n<400;n++){const o=step(L,t.slice(),Math.floor(Math.random()*4));if(o.moved)t=o.s;if(isWin(L,t)){rw++;break;}}}
 console.log(String(i+1).padStart(2),'par',sol.d,'states',seen.size,'softlock',dead,'movesA/B',moveA+'/'+moveB,'solutions<=1.4par',ways,'doubleflip',dbl,'random400',rw+'/500');});
