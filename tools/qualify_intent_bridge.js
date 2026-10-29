'use strict';
// Real local host and synthetic selected contexts; no provider calls or user saves.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'worldward-intent-')),metadata=path.join(dir,'host.json');
 const child=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'shared'],{stdio:['ignore','ignore','pipe']});
 let stderr='',browser;child.stderr.on('data',data=>stderr+=data);
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Host failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),origin='http://127.0.0.1:'+host.port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],external=[],prepares=[],executes=[],evidence=[];
  let losePrepare=true,loseExecute=true,providers=0;
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url)){providers++;return route.abort();}return route.continue();});
  await page.route('**/api/intent/prepare',async route=>{const response=await route.fetch();prepares.push(route.request().postDataJSON());if(losePrepare){losePrepare=false;return route.abort('failed');}return route.fulfill({response});});
  await page.route('**/api/intent/execute',async route=>{const response=await route.fetch();executes.push({body:route.request().postDataJSON(),result:await response.json()});if(loseExecute){loseExecute=false;return route.abort('failed');}return route.fulfill({response});});
  await page.goto(origin);await page.waitForFunction(()=>current&&!loadingCampaign);
  for(const context of host.contexts){
   await page.locator('[data-view="story"]').first().click();await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(context.id);
   await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);
   const action=context.name==='settlement'?'inspect':'enter-passage';
   const capability=await page.evaluate(id=>current.intent_control.capabilities.find(item=>item.action.action_id===id)?.capability_id,action);
   assert(capability);const words='  I attempt '+action+'.\n<img src=x onerror="window.bad=true">  ';
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#declaration').fill(words);
   await page.locator('#intent-capability').selectOption(capability);const before=fs.readFileSync(context.save,'utf8');
   await page.locator('#review-intent').click();
   if(context.name==='authored_scene'){
    await page.locator('#recover-intent-review').waitFor({state:'visible'});assert.equal(fs.readFileSync(context.save,'utf8'),before);
    await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);await page.locator('#own-response-panel').evaluate(node=>node.open=true);
    await page.locator('#recover-intent-review').click();
   }
   await page.locator('#action-review-dialog[open]').waitFor();assert.equal(await page.locator('#action-review-intent').inputValue(),words);
   assert((await page.locator('#action-review-description').innerText()).includes(action));await page.locator('#cancel-reviewed-action').click();assert.equal(fs.readFileSync(context.save,'utf8'),before);
   await page.locator('#recover-intent-review').click();await page.locator('#action-review-dialog[open]').waitFor();
   const revision=await page.evaluate(()=>current.revision);await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,revision);
   const accepted=await page.evaluate(()=>current.completed_actions.at(-1));assert.equal(accepted.status,'completed_successfully');assert.equal(accepted.declaration,words);assert.equal(await page.locator('#declaration').inputValue(),words);assert.equal(await page.evaluate(()=>window.bad),undefined);
   const after=fs.readFileSync(context.save,'utf8');await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert(await page.evaluate(()=>document.querySelector('#reading-scroll').contains(document.querySelector('#story-feed'))&&document.querySelector('#reading-scroll').contains(document.querySelector('#own-response-panel'))));
   await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);assert.equal(fs.readFileSync(context.save,'utf8'),after);assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),accepted);
   evidence.push({context:context.name,explicit_action:action,cancel_no_effect:true,exact_words:true,commit_and_reload:true,retained_draft:true,mobile_width:390});
   await page.setViewportSize({width:1568,height:1000});
  }
  assert.equal(providers,0);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);assert.equal(prepares.length,2);assert.equal(executes.length,2);
  const result={status:'passed',contexts:evidence,lost_prepare_reload_recovered:true,lost_execute_original_result_recovered:true,provider_calls:0,browser_errors:0,external_requests:0};
  if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(dir,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
