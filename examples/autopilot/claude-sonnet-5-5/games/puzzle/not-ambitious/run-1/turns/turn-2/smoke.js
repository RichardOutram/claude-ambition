const fs=require('fs');
const html=fs.readFileSync("/Volumes/My Shared Files/work/mirror-twins/index.html",'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const mk=()=>new Proxy(function(){},{get:(t,k)=>k==='classList'?{add(){},remove(){},contains(){return false}}:k==='style'?{}:k===Symbol.toPrimitive?()=>0:mk(),apply:()=>mk(),set:()=>true});
const ls={};const handlers={};
const doc={getElementById:()=>mk(),createElement:()=>mk()};
let frames=0;
const g={document:doc,localStorage:{getItem:k=>ls[k]||null,setItem:(k,v)=>ls[k]=v},innerWidth:900,innerHeight:800,devicePixelRatio:1,performance:{now:()=>Date.now()},
 requestAnimationFrame:f=>{if(frames++<50)f();},addEventListener:(e,f)=>handlers[e]=f,AudioContext:function(){throw 1}};
new Function(...Object.keys(g),js)(...Object.values(g));
// simulate keypresses incl. level 1 solve
for(const k of ['ArrowRight','ArrowDown','ArrowLeft','z','r'])handlers.keydown({key:k,preventDefault(){}});
console.log('ok, frames',frames);
