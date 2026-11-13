const fs=require('fs');const {parse,solve}=require('./logic.js');
const rows=require('./final_levels.json');
const levels=rows.map((r,i)=>{const s=solve(parse(r));if(s.d<0)throw new Error('unsolvable '+i);return {rows:r,par:s.d};});
const logic=fs.readFileSync('./logic.js','utf8');
let t=fs.readFileSync('./template.html','utf8').replace('__LOGIC__',()=>logic).replace('__LEVELS__',()=>JSON.stringify(levels));
fs.writeFileSync('../../mirror-twins.html',t);console.log(levels.map(l=>l.par).join(' '));
