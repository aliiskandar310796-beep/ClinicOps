// Synthetic regression journey for the approved-source matrix and review packets.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),E=require('../docs/assets/reconciliation.js');
const browser=await chromium.launch();
const base=process.env.E2E_BASE_URL||'http://localhost:8103';
try {
 const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
 await page.goto(base+'/integrity-scanner.html');
 await page.click('#modeC');await page.click('#c_example');await page.click('#c_run');
 await page.waitForSelector('#grid .tabulator-row');
 assert.match(await page.textContent('#summary'),/5 comparisons — 3 aligned, 1 mismatch\/conflict signals, 1 missing evidence/);
 const download=async selector=>{const wait=page.waitForEvent('download');await page.click(selector);return fs.readFile(await (await wait).path(),'utf8')};
 const packet=JSON.parse(await download('#x_json'));
 assert.equal(packet.input_sha256,await E.sha256(packet.input_snapshot));
 const {packet_sha256,...rest}=packet;assert.equal(packet_sha256,await E.sha256(rest));
 await page.click('summary:has-text("Record a review disposition")');
 await page.selectOption('#review_row','1');await page.selectOption('#review_state','closed with evidence');await page.click('#review_save');
 assert.match(await page.textContent('#review_message'),/Closing requires/);
 await page.fill('#review_evidence','Fictional ECO 43 §2');await page.fill('#review_owner','Fictional QA');await page.fill('#review_note','<img src=x onerror=alert(1)>');await page.click('#review_save');
 const closed=JSON.parse(await download('#x_json'));assert.equal(closed.findings[1].review_state,'closed with evidence');assert.equal(closed.findings[1].status,'mismatch signal');assert.ok(closed.findings[1].closed_at);assert.notEqual(closed.packet_sha256,packet.packet_sha256);
 const html=await download('#x_html');assert.ok(html.includes('&lt;img'));assert.ok(!html.includes('<img src=x'));assert.ok(html.includes(closed.packet_sha256));
 await page.fill('#c_input','{bad');await page.click('#c_run');assert.match(await page.textContent('#summary'),/validation failed/);assert.equal(await page.locator('#grid .tabulator-row').count(),0);
 await page.click('#modeA');await page.click('#a_example');await page.selectOption('#a_mode','exact');await page.fill('#av1',' IFU-12 ');await page.click('#a_run');assert.equal((JSON.parse(await download('#x_json'))).findings[0].status,'mismatch signal');
 await page.fill('#a_ref','');await page.click('#a_run');assert.match(await page.textContent('#summary'),/Choose an approved reference/);assert.equal(await page.locator('#grid .tabulator-row').count(),0);
 await page.setViewportSize({width:390,height:844});await page.click('#modeC');await page.click('#c_example');await page.click('#c_run');await page.waitForSelector('#grid .tabulator-row');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth));
 assert.deepEqual(errors,[]);assert.ok(requests.every(r=>r.method==='GET'&&r.url.startsWith(base+'/')));
 console.log('PASS matrix → exception queue → guarded closure → hash verification → JSON/HTML exports; exact comparison, invalidation, mobile and network checks.');
} finally {await browser.close()}
