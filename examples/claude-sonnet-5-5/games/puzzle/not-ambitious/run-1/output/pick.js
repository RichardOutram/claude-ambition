const fs=require('fs');
const html=fs.readFileSync("/Volumes/My Shared Files/work/mirror-twins/index.html",'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const {parse,solve}=new Function(js+';return {parse,solve};')();
const load=f=>JSON.parse(fs.readFileSync('/work/'+f+'.json'));
const plain=load('plain');
const plates=[...load('plates'),...load('plates2')].filter(l=>{
  const walled=l.rows.map(r=>r.replace(/=/g,'#'));
  const p=solve(parse(walled)); return p<0||p>=l.par+4;   // door matters
});
const wallCount=l=>l.rows.join('').split('#').length-1;
console.error('plates needing doors:',plates.length);
const pickNear=(arr,par,used)=>{
  const c=arr.filter(l=>Math.abs(l.par-par)<=1&&!used.has(l.rows.join()))
    .filter(l=>{const w=wallCount(l);return w>=20&&w<=34;});
  if(!c.length)return null; const l=c[Math.floor(Math.random()*c.length)]; used.add(l.rows.join()); return l;
};
const used=new Set();
const plan=[['p',10],['p',13],['n',16],['p',17],['n',20],['p',22],['n',24],['p',27],['n',30],['p',32],['n',35],['p',40]];
const out=[];
for(const [t,par] of plan){ const l=pickNear(t==='p'?plates:plain,par,used)||pickNear(t==='p'?plates:plain,par+1,used); if(l)out.push(l); else console.error('none',t,par); }
console.log(out.map(l=>' ['+l.rows.map(r=>JSON.stringify(r)).join(',\n  ')+']  // par '+l.par).join(',\n'));
