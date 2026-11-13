// usage: node sheet.mjs out.png dir1 dir2 ...  (env CW = cell width, ROWH = row height)   (one row per dir, columns = frames sorted by time)
import {chromium} from 'playwright';
import fs from 'fs';
const [out,...dirs]=process.argv.slice(2);
const rows=dirs.map(d=>fs.readdirSync(d).filter(f=>f.endsWith('.png')).sort().map(f=>({f,u:'data:image/png;base64,'+fs.readFileSync(d+'/'+f).toString('base64')})));
const cols=rows[0].length;
const html=`<body style="margin:0;background:#000;color:#9af;font:11px monospace"><div style="display:grid;grid-template-columns:repeat(${cols},${process.env.CW||320}px);gap:2px">${rows.map(r=>r.map(i=>`<div style="position:relative"><img width=${process.env.CW||320} src="${i.u}"><span style="position:absolute;left:4px;top:2px">${i.f.slice(1,-4)}s</span></div>`).join('')).join('')}</div>`;
const b=await chromium.launch({channel:'chrome'});
const p=await b.newPage({viewport:{width:cols*(+(process.env.CW||320)+2),height:rows.length*(+(process.env.ROWH||182))}});
await p.setContent(html); await p.waitForTimeout(500);
await p.screenshot({path:out}); await b.close();
