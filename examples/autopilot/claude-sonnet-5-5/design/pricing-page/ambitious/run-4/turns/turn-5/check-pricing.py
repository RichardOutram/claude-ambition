#!/usr/bin/env python3
"""Check pricing.html in real headless Chrome. Usage: python3 -I check-pricing.py [page.html]
Exits 1 if any check fails. Needs Google Chrome (set CHROME to override the path)."""
import html, json, os, pathlib, re, subprocess, sys, tempfile

page = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).with_name("pricing.html")).resolve()
chrome = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

HARNESS = """<body><pre id=o>running</pre><script>
const URL_='%s', R={};
const mk=(w,h)=>{const f=document.createElement('iframe');f.src=URL_;f.style.cssText=`width:${w}px;height:${h}px;border:0`;document.body.appendChild(f);return f};
const vis=(h)=>e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=h&&r.height>0&&getComputedStyle(e).display!=='none'};
const all=(doc,sel,n,h)=>{const l=[...doc.querySelectorAll(sel)];return l.length===n&&l.every(vis(h))};
(async()=>{try{
 const d=mk(1280,800), m=mk(390,700), sleep=t=>new Promise(r=>setTimeout(r,t));
 const ready=f=>{try{return f.contentDocument.querySelector('.plan .billed[data-plan]').textContent.trim()!==''}catch(e){return false}};
 for(let i=0;i<150&&!(ready(d)&&ready(m));i++) await sleep(100);
 const dd=d.contentDocument, md=m.contentDocument;
 R['desktop: 4 worries in first screen']=all(dd,'.worry',4,800);
 R['desktop: 3 "Best for" lines in first screen']=all(dd,'.for',3,800);
 const b=[...dd.querySelectorAll('.plan .btn')].map(e=>e.getBoundingClientRect().bottom);
 R['desktop: 3 plan buttons aligned and in first screen']=b.length===3&&Math.max(...b)<=800&&Math.max(...b)-Math.min(...b)<=1;
 R['phone: 4 promise lines in first screen']=all(md,'.worries-m li',4,700);
 R['phone: 3 plan rows with prices in first screen']=all(md,'.pick a',3,700)&&[...md.querySelectorAll('.pick a')].every(e=>/[$€£]\\d/.test(e.innerText));
 R['phone: toggle and currency in first screen']=all(md,'.toggle',1,700)&&all(md,'.cur',1,700);
 R['no horizontal overflow (desktop, phone)']=dd.documentElement.scrollWidth<=d.contentWindow.innerWidth&&md.documentElement.scrollWidth<=m.contentWindow.innerWidth;
 const P=d.contentWindow.eval('PRICES'); let ok=true;
 for(const c in P) for(const per of ['monthly','yearly']){
   const sel=dd.getElementById('cur'); sel.value=c; sel.dispatchEvent(new Event('change')); dd.getElementById(per).click();
   for(const pl of ['pro','studio']){
     const [mo,yr]=P[c][pl], amt=dd.querySelector('.plan .amt[data-plan='+pl+']').textContent, bl=dd.querySelector('.plan .billed[data-plan='+pl+']').textContent;
     if(amt!==P[c].sym+(per==='yearly'?yr:mo)) ok=false;
     if(per==='yearly'&&!bl.includes('Billed '+P[c].sym+yr*12+' yearly')) ok=false;
     if(per==='monthly'&&bl!=='Billed monthly') ok=false;
   }}
 R['prices and billing text correct in every currency and period']=ok;
 R['table marks have screen-reader text']=[...dd.querySelectorAll('td.y,td.n')].every(e=>e.querySelector('.sr'));
 R['buttons, links and selects are named']=[...dd.querySelectorAll('button,a,select')].every(e=>(e.textContent.trim()||e.getAttribute('aria-label')||(e.labels&&e.labels.length)));
 R['no unbacked headline numbers (e.g. "40,000+")']=!/\\d{2,3}[,.]\\d{3}\\+/.test(dd.body.innerText);
 document.getElementById('o').textContent=JSON.stringify(R);
}catch(e){document.getElementById('o').textContent=JSON.stringify({ERROR:String(e)})}})();
</script></body>"""

with tempfile.TemporaryDirectory() as tmp:
    h = pathlib.Path(tmp, "h.html")
    h.write_text(HARNESS % page.as_uri())
    out = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--disable-web-security",
                          f"--user-data-dir={tmp}/profile", "--window-size=1300,1500", "--virtual-time-budget=30000",
                          "--dump-dom", h.as_uri()], capture_output=True, text=True, timeout=180).stdout
m = re.search(r'<pre id="o">(.*?)</pre>', out, re.S)
if not m or m.group(1) == "running":
    sys.exit("Chrome did not finish the checks. Is CHROME set correctly?")
res = json.loads(html.unescape(m.group(1)))
if "ERROR" in res:
    sys.exit("Check harness error: " + res["ERROR"])
for k, v in res.items():
    print(("PASS  " if v else "FAIL  ") + k)
todo = len(re.findall(r"PLACEHOLDER", page.read_text()))
print(f"\n{todo} PLACEHOLDER marker(s) in the page to confirm before launch (grep PLACEHOLDER).")
sys.exit(0 if all(res.values()) else 1)
