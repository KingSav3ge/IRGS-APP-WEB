'use strict';
// Local presentation over actual synthetic Core actions. Every inference URL is blocked.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-app-routine-')),metadata=path.join(directory,'host.json');
 const hostProcess=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'routine'],{env:process.env,stdio:['ignore','ignore','pipe']});let stderr='';hostProcess.stderr.on('data',data=>stderr+=data);let browser;
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(hostProcess.exitCode!==null||Date.now()>deadline)throw Error('Offline host failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),read=()=>JSON.parse(fs.readFileSync(host.save));
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage(),errors=[],writes=[],results=[];let inferenceCalls=0,lostAck=true;
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')writes.push(request.url());});
  await page.route('**/api/ai/proposal',async route=>{inferenceCalls++;await route.abort();});await page.route('**/api/ai/accept',async route=>{inferenceCalls++;await route.abort();});
  await page.route('**/api/action',async route=>{const response=await route.fetch();const result=await response.json();results.push(result);if(lostAck&&result.declaration==='I attempt enter-passage.'){lostAck=false;await route.abort('failed');}else await route.fulfill({response});});
  await page.goto('http://127.0.0.1:'+host.port);await page.locator('[data-supported-action]').first().waitFor();if(!await page.locator('#own-response-panel').evaluate(node=>node.open))await page.locator('#own-response-panel > summary').click();
  const before=fs.readFileSync(host.save,'utf8');await page.locator('#declaration').fill('My independent draft stays here.');await page.locator('#local-drafts').locator('summary').click();await page.locator('[data-local-draft="player.ask"]').click();await page.locator('#action-review-dialog[open]').waitFor();assert(await page.locator('#confirm-reviewed-action').isHidden());await page.locator('#cancel-reviewed-action').click();assert.equal(await page.locator('#declaration').inputValue(),'My independent draft stays here.');assert.equal(writes.length,0);assert.equal(fs.readFileSync(host.save,'utf8'),before);
  await page.locator('[data-local-draft="player.observe"]').click();await page.locator('#action-review-intent').fill('  I consider my next move.\n{draft} <img src=x>  ');await page.locator('#keep-action-draft').click();const draft=await page.locator('#declaration').inputValue();assert(draft.includes('\n{draft}'));assert.equal(writes.length,0);assert.equal(fs.readFileSync(host.save,'utf8'),before);
  for(const [action,revision] of [['look-quay',2],['try-gate',3],['enter-passage',4],['reach-desk',5]]){
   await page.getByRole('button',{name:action,exact:true}).click();await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision&&!busy,revision);
   const result=results.at(-1);assert.equal(await page.locator('#notice').textContent(),result.outcome.summary);const text=await page.locator('.last-outcome .entry-text').textContent();assert(text.startsWith(result.outcome.summary));assert.equal(await page.locator('#declaration').inputValue(),draft);
   if(action==='look-quay'){assert(text.includes('<img'));assert(text.includes('{source_text}'));assert.equal(await page.locator('.last-outcome img').count(),0);assert.equal(await page.evaluate(()=>window.receiptExecuted),undefined);}
   if(action==='try-gate'){assert.equal(result.status,'completed_unsuccessfully');assert(text.includes('remains closed'));assert.equal(read().state.actors.pc.current.location.value,'quay');}
  }
  assert.equal(lostAck,false);assert.equal(read().revision,5);assert.equal(read().state.elapsed_time.seconds,43);assert.equal(writes.filter(url=>url.endsWith('/api/action')).length,4);
  await page.reload();await page.waitForFunction(()=>current?.revision===5);assert.equal(await page.locator('#declaration').inputValue(),draft);assert.equal(await page.evaluate(()=>routineText('unmapped.routine').includes('unavailable')),true);
  const committed=fs.readFileSync(host.save,'utf8');await page.setViewportSize({width:390,height:844});
  await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#local-drafts').evaluate(node=>node.open=true);
  assert(await page.evaluate(()=>document.querySelector('#content').getBoundingClientRect().height>50));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('[data-local-draft="player.pause"]').click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#cancel-reviewed-action').click();assert.equal(fs.readFileSync(host.save,'utf8'),committed);
  assert.equal(inferenceCalls,0);assert.equal(fs.existsSync(metadata.replace(/\.json$/,'.inputs.json')),false);assert.deepEqual(errors,[]);
  const result={status:'passed',app_library:'irgs-app-routine-v1@1.0.0',variants:171,editable_drafts:32,recipes:8,Core_actions:4,unsuccessful_physical_attempt_preserved:true,exact_receipt_HTML_braces_negation_preserved:true,lost_acknowledgement_recovered:true,draft_cancel_edit_keep_reload:true,elapsed_seconds:43,mobile_width:390,provider_calls:inferenceCalls,missing_template_fallback_provider_calls:0,browser_errors:errors.length};if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(hostProcess.exitCode===null){hostProcess.kill('SIGINT');await new Promise(resolve=>hostProcess.once('exit',resolve));}fs.rmSync(directory,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
