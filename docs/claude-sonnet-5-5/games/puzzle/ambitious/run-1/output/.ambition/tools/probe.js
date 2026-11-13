const p=require('puppeteer-core');(async()=>{const b=await p.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const pg=await b.newPage();await pg.goto('file:///Volumes/My Shared Files/work/mirror-twins.html');console.log(await pg.title(), await pg.$eval('#lv',e=>e.textContent));await b.close();})().catch(e=>{console.log('ERR',e.message)})
