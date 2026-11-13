import {PNG} from 'pngjs'; import fs from 'fs';
const d=process.argv[2];
const ld=t=>PNG.sync.read(fs.readFileSync(`${d}/t${t.toFixed(4)}.png`)).data;
const diff=(a,b)=>{const x=ld(a),y=ld(b);let s=0;for(let i=0;i<x.length;i+=4)s+=Math.abs(x[i]-y[i])+Math.abs(x[i+1]-y[i+1])+Math.abs(x[i+2]-y[i+2]);return s/(x.length/4*3);};
const pairs=[['SEAM 9.9833->0.0',9.9833,0],['9.9667->9.9833',9.9667,9.9833],['0.0->0.0167',0,.0167],['2.0->2.0167',2,2.0167],['5.0->5.0167',5,5.0167],['8.0->8.0167',8,8.0167],['8.6->8.6167',8.6,8.6167],['9.5->9.5167',9.5,9.5167]];
for(const [n,a,b] of pairs) console.log(n.padEnd(20),diff(a,b).toFixed(3));
