const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const f=new Function(js+';return {LEVELS,parse,solve};');
const {LEVELS,parse,solve}=f();
LEVELS.forEach((r,i)=>{
  const bad=r.some(row=>row.length!==r[0].length);
  console.log(i+1, bad?'RAGGED':'', solve(parse(r)));
});
