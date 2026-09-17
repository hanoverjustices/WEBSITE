const {chromium}=require('playwright'),path=require('path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage();
 await page.route('https://**/*',r=>r.abort());
 await page.goto('file://'+path.resolve(__dirname,'../index.html'),{waitUntil:'domcontentloaded'});
 await page.evaluate(()=>toggleGia(true));
 await page.locator('#chatInput').fill('who is the custous of hanover');await page.locator('#chatInput').press('Enter');
 await page.waitForTimeout(600);
 const answer=await page.locator('#chatlog .msg.bot').last().innerText();
 assert.match(answer,/Lennox Anderson-Jackson/);assert.match(answer,/historical/);assert.match(answer,/Published: 2025-07-31/);
 assert.equal(await page.locator('#chatlog .gia-citation a').count(),1);
 await page.locator('#chatInput').fill('who is the president');await page.locator('#chatInput').press('Enter');await page.waitForTimeout(600);
 assert.match(await page.locator('#chatlog .msg.bot').last().innerText(),/don’t have verified information/);
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.locator('#chatInput').isVisible(),true);
 console.log('PASS browser chat: Custos typo, historical label, citation metadata/link, unverified President refusal, mobile input visible');
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
