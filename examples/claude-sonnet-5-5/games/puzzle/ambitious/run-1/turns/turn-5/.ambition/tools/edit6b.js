const fs=require('fs');let t=fs.readFileSync('template.html','utf8');
const a='#stage{padding-right:150px}';if(!t.includes(a))throw 1;t=t.replace(a,'#stage{padding:0 150px 0 130px}');fs.writeFileSync('template.html',t);
let s=fs.readFileSync('accept.js','utf8');
s=s.replace("hint:g('#hint'),","hint:g('#hint'),rule:g('#rule'),");
s=s.replace("const minBtn=","const ov2=r.rule&&!(r.rule.l>=r.c.r||r.rule.r<=r.c.l||r.rule.t>=r.c.b||r.rule.b<=r.c.t);const minBtn=");
s=s.replace("const bad=!inside||ov||","const bad=!inside||ov||ov2||");
fs.writeFileSync('accept.js',s);
