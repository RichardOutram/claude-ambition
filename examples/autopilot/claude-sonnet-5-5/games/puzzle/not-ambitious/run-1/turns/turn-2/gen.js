const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const {parse,solve}=new Function(js+';return {parse,solve};')();
const W=+process.argv[3]||9,H=+process.argv[4]||7,N=+process.argv[5]||20000,usePlates=process.argv[6]==='1';
const r=n=>Math.floor(Math.random()*n);
let best=[];
for(let it=0;it<N;it++){
  const g=[];for(let y=0;y<H;y++){g.push([]);for(let x=0;x<W;x++)g[y][x]=(x==0||y==0||x==W-1||y==H-1)?'#':(Math.random()<0.2?'#':'.');}
  const cells=[];for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++)cells.push([x,y]);
  const put=(ch,n=1)=>{for(let i=0;i<n;i++){const [x,y]=cells[r(cells.length)];g[y][x]=ch;}};
  // keep single-char specials unique by counting after
  put('A');put('B');put('a');put('b');put('o',r(3)+1);put('x',r(3));
  if(usePlates){put('p',1);put('=',r(2)+1);}
  const rows=g.map(row=>row.join(''));
  const flat=rows.join('');
  if(['A','B','a','b'].some(c=>flat.split(c).length!==2))continue;
  if(usePlates&&flat.split('p').length!==2)continue;
  const par=solve(parse(rows));
  if(par>=12)best.push({par,rows});
}
best.sort((a,b)=>b.par-a.par);
console.log(JSON.stringify(best.map(b=>({par:b.par,rows:b.rows})),null,0));
