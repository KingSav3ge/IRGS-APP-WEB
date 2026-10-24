'use strict';
// Offline synthetic Engine fixture. Requires Playwright + Chromium, no live AI.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-solo-browser-')),metadata=path.join(temporary,'host.json');
 const hostProcess=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata],{env:process.env,stdio:['ignore','ignore','pipe']});
 let hostErrors='';hostProcess.stderr.on('data',data=>hostErrors+=data);
 let browser;
 try{
  const deadline=Date.now()+15000;while(!fs.existsSync(metadata)){if(hostProcess.exitCode!==null||Date.now()>deadline)throw Error('Offline host did not start: '+hostErrors);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),read=()=>JSON.parse(fs.readFileSync(host.save));
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage(),errors=[],writes=[],lookups=[];let dropNext=true;
  await page.route('**/api/ai/accept',async route=>{const response=await route.fetch();if(dropNext&&response.status()===200){dropNext=false;await route.abort('failed');}else await route.fulfill({response});});
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')writes.push({url:request.url(),body:request.postDataJSON()});if(request.url().includes('/api/action-result/'))lookups.push(request.url());});
  await page.goto('http://127.0.0.1:'+host.port);await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(host.id);await page.locator('[data-supported-action]').first().waitFor();await page.locator('#own-response-panel').evaluate(node=>node.open=true);
  const before=fs.readFileSync(host.save,'utf8'),intent='  I take the passage.\nCarefully.  ';
  await page.locator('#declaration').fill(intent);await page.locator('#review-assisted-action').click();await page.locator('#action-review-dialog[open]').waitFor();assert.equal(await page.locator('#action-review-intent').inputValue(),intent);assert.equal(fs.readFileSync(host.save,'utf8'),before);
  await page.locator('#cancel-reviewed-action').click();assert.equal(fs.readFileSync(host.save,'utf8'),before);
  await page.locator('#review-assisted-action').click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#action-review-intent').fill('I change my plan.');assert(await page.locator('#confirm-reviewed-action').isDisabled());await page.locator('#cancel-reviewed-action').click();assert.equal(fs.readFileSync(host.save,'utf8'),before);assert.equal(await page.locator('#declaration').inputValue(),intent);
  await page.locator('#declaration').fill('PROVIDER_DENIED');await page.locator('#review-assisted-action').click();await page.waitForFunction(()=>document.querySelector('#assistance-state').textContent.includes('provider_denied'));assert.equal(fs.readFileSync(host.save,'utf8'),before);assert.equal(await page.locator('#declaration').inputValue(),'PROVIDER_DENIED');await page.locator('#cancel-assisted-action').click();
  for(const [words,revision,action] of [[intent,2,'enter-passage'],['I approach the receiving desk.',3,'reach-desk']]){
   await page.locator('#declaration').fill(words);await page.locator('#review-assisted-action').click();await page.locator('#action-review-dialog[open]').waitFor();assert((await page.locator('#action-review-description').textContent()).includes(action));await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(expected=>document.querySelector('#saved').textContent.includes('revision '+expected),revision);assert.equal(read().revision,revision);assert.equal(await page.locator('#declaration').inputValue(),words);
  }
  assert.equal(dropNext,false);assert(lookups.length>=1);assert.equal(writes.filter(item=>item.url.endsWith('/api/ai/accept')).length,2);assert.equal(read().state.elapsed_time.seconds,35);assert.equal(read().state.actors.pc.current.location.value,'desk');
  await page.locator('#declaration').fill('WAIT_FOR_NAVIGATION');const delayed=page.waitForResponse(response=>response.url().endsWith('/api/ai/proposal'));await page.locator('#review-assisted-action').click();await page.locator('[data-view="world"]').first().click();await delayed;await page.waitForTimeout(1200);assert(!(await page.locator('#action-review-dialog').evaluate(node=>node.open)));assert.equal(read().revision,3);
  await page.reload();assert.equal(read().revision,3);assert.equal(errors.length,0,errors.join('\n'));
  const inputs=JSON.parse(fs.readFileSync(metadata.replace(/\.json$/,'.inputs.json')));assert.equal(inputs.length,6);for(const publicValue of [inputs,writes,await page.content()])assert(!JSON.stringify(publicValue).includes('PRIVATE_EVALUATOR_MARKER'));
  const result={status:'passed',fixture:'Engine authored-scene synthetic fixture; Catalog R00 proposal path unsupported',two_consecutive_core_actions:2,offline_provider_calls:inputs.length,live_provider_calls:0,editable_exact_intent:true,cancel_and_edit_no_effect:true,provider_denied_no_effect:true,lost_acknowledgement_recovered:true,late_navigation_fenced:true,elapsed_seconds:35,browser_errors:errors.length};
  if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{
  if(browser)await browser.close();
  if(hostProcess.exitCode===null){hostProcess.kill('SIGINT');await new Promise(resolve=>hostProcess.once('exit',resolve));}
  fs.rmSync(temporary,{recursive:true,force:true});
 }
})().catch(error=>{console.error(error);process.exitCode=1;});
