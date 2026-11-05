const { chromium } = require('D:/gpt/tools/agent-skills/herk-edit-kit/repo/node_modules/playwright');
const path = require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'D:/gpt/2026-11-04/jian/work/ironman-hyperframes/tools/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const out=path.resolve('outputs/jjk-edge-v17/evidence/v02-type');
 for(const mode of ['slam','twin','ribbon','orbit']){
  await page.goto('file:///'+path.join(out,`preview-${mode}.html`).replaceAll('\\','/'));
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>window.tl.seek(.42));
  await page.screenshot({path:path.join(out,`preview-${mode}.png`)});
  if(mode==='orbit'){
   await page.evaluate(()=>window.tl.seek(.0416667));
   await page.screenshot({path:path.join(out,'preview-orbit-entry.png')});
  }
 }
 await browser.close();
})();
