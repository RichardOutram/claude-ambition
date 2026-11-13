function parse(rows){const H=rows.length,W=rows[0].length;const L={W,H,walls:[],pits:[],pads:[]};
for(let y=0;y<H;y++){L.walls.push([]);L.pits.push([]);L.pads.push([]);for(let x=0;x<W;x++){const c=rows[y][x];
L.walls[y][x]=c==='#';L.pits[y][x]=c==='x';L.pads[y][x]=(c==='f'||c==='g')?c:null;
if(c==='A')L.A=[x,y];if(c==='B')L.B=[x,y];if(c==='a')L.a=[x,y];if(c==='b')L.b=[x,y];}}return L;}
const DIRS=[[1,0],[-1,0],[0,1],[0,-1]];
function blocked(L,x,y){return x<0||y<0||x>=L.W||y>=L.H||L.walls[y][x];}
function startState(L){return [L.A[0],L.A[1],L.B[0],L.B[1],-1,1];}
// returns {s,moved,fell,flips} ; s = [ax,ay,bx,by,sx,sy]
function step(L,s,d){const dx=DIRS[d][0],dy=DIRS[d][1];
let ax=s[0],ay=s[1],bx=s[2],by=s[3],sx=s[4],sy=s[5],flips=0;
const bdx=sx*dx,bdy=sy*dy;
let nax=ax+dx,nay=ay+dy,nbx=bx+bdx,nby=by+bdy;
const am=!blocked(L,nax,nay),bm=!blocked(L,nbx,nby);
if(!am){nax=ax;nay=ay;}if(!bm){nbx=bx;nby=by;}
if(!am&&!bm)return {s,moved:false,fell:false,flips:0};
if((am&&L.pits[nay][nax])||(bm&&L.pits[nby][nbx]))return {s,moved:false,fell:true,flips:0};
const ns=[nax,nay,nbx,nby,sx,sy];
for(const [m,x,y] of [[am,nax,nay],[bm,nbx,nby]]){if(!m)continue;const p=L.pads[y][x];
if(p==='f'){ns[4]=-ns[4];flips++;}else if(p==='g'){ns[5]=-ns[5];flips++;}}
return {s:ns,moved:true,fell:false,flips};}
function isWin(L,s){return s[0]===L.a[0]&&s[1]===L.a[1]&&s[2]===L.b[0]&&s[3]===L.b[1];}
// BFS: shortest length, number of shortest solutions, one path
function solve(L){const k=s=>s.join(',');const s0=startState(L);
const dist=new Map([[k(s0),0]]),cnt=new Map([[k(s0),1]]),par=new Map();let layer=[s0],d=0,found=null,total=0;
while(layer.length&&!found&&d<80){const next=[];
for(const s of layer){for(let m=0;m<4;m++){const r=step(L,s.slice(),m);if(!r.moved)continue;const kk=k(r.s);
if(!dist.has(kk)){dist.set(kk,d+1);cnt.set(kk,0);par.set(kk,[k(s),m]);next.push(r.s);}
if(dist.get(kk)===d+1){cnt.set(kk,cnt.get(kk)+cnt.get(k(s)));}}}
d++;layer=next;const wins=next.filter(s=>isWin(L,s));
if(wins.length){found=wins;for(const w of wins)total+=cnt.get(k(w));}}
if(!found)return {d:-1,count:0,path:[]};
const path=[];let kk=k(found[0]);while(par.has(kk)){const [pk,m]=par.get(kk);path.push(m);kk=pk;}
return {d,count:total,path:path.reverse()};}
function strip(L,o){const C=Object.assign({},L);C.pads=L.pads.map(r=>r.map(p=>o.pads&&(o.pads===true||o.pads.includes(p))?null:p));
C.pits=L.pits.map(r=>r.map(p=>o.pits?false:p));return C;}
if(typeof module!=='undefined')module.exports={parse,step,solve,strip,startState,isWin,DIRS};
// true if a win is reachable from state s (forward BFS; state spaces here are small)
function canWin(L,s0){const k=s=>s.join(',');const seen=new Set([k(s0)]);const q=[s0];
while(q.length){const s=q.pop();if(isWin(L,s))return true;for(let m=0;m<4;m++){const o=step(L,s,m);if(!o.moved)continue;const kk=k(o.s);if(!seen.has(kk)){seen.add(kk);q.push(o.s);}}}return false;}
if(typeof module!=='undefined')module.exports.canWin=canWin;
