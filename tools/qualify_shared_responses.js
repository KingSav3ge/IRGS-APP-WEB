'use strict';
// Independently initialized real Core adapters, one App contract, no AI config.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-shared-responses-')),metadata=path.join(folder,'host.json');
 const processHost=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'shared'],{env:process.env,stdio:['ignore','ignore','pipe']});let hostError='';processHost.stderr.on('data',data=>hostError+=data);let browser;
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(processHost.exitCode!==null||Date.now()>deadline)throw Error('Shared fixture host failed: '+hostError);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata));browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage(),errors=[],posts=[],results=[],lookups=[];let providerCalls=0;const discarded=new Set();
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')posts.push(request.postDataJSON());if(request.url().includes('/api/action-result/'))lookups.push(request.url());});
  await page.route('**/api/ai/proposal',async route=>{providerCalls++;await route.abort();});await page.route('**/api/ai/accept',async route=>{providerCalls++;await route.abort();});
  const forward=async route=>{const response=await route.fetch(),result=await response.json();results.push(result);if(response.status()===200&&!discarded.has(result.campaign_id)){discarded.add(result.campaign_id);await route.abort('failed');}else await route.fulfill({response});};
  await page.route('**/api/action',forward);await page.route('**/api/rise/action',forward);await page.goto('http://127.0.0.1:'+host.port);
  const evidence=[];
  for(const context of host.contexts){
   await page.locator('[data-view="story"]').first().click();await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(context.id);await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);
   const contract=await page.evaluate(()=>current.local_responses);assert.equal(contract.schema_version,1);assert.equal(contract.scope.actor_id,context.actor);assert.equal(contract.catalog_library.id,'irgs-response-depot-v1');assert.equal(contract.engine_runtime,true);assert.deepEqual(new Set(contract.drafts.map(draft=>draft.source)),new Set(['catalog','engine']));
   assert.equal(await page.evaluate(()=>current.assistance.available),false);const before=fs.readFileSync(context.save,'utf8'),postCount=posts.length;
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#declaration').fill('Independent '+context.name+' draft.');await page.locator('#local-drafts').evaluate(node=>node.open=true);
   await page.locator('[data-local-draft="catalog:player.look_around"]').click();await page.locator('#action-review-dialog[open]').waitFor();assert(await page.locator('#confirm-reviewed-action').isHidden());await page.locator('#cancel-reviewed-action').click();assert.equal(await page.locator('#declaration').inputValue(),'Independent '+context.name+' draft.');
   const engineDraft=contract.drafts.find(draft=>draft.source==='engine');await page.locator('[data-local-draft="'+engineDraft.id+'"]').click();await page.locator('#action-review-intent').fill('My editable '+context.name+' intention.');await page.locator('#keep-action-draft').click();const draft=await page.locator('#declaration').inputValue();assert.equal(posts.length,postCount);assert.equal(fs.readFileSync(context.save,'utf8'),before);
   let revision=context.revision;const zeroSpans=[];
   for(const action of context.actions){
    if(context.name==='settlement')await page.locator('[data-rise-action="'+action+'"]').click();else await page.getByRole('button',{name:action,exact:true}).click();
    await page.locator('#confirm-reviewed-action').click();revision++;await page.waitForFunction(revision=>current?.revision===revision&&!busy,revision);
    const result=results.at(-1),presentation=result.presentation;assert.equal(presentation.actor_id,context.actor);assert.equal(presentation.catalog_library.id,'irgs-response-depot-v1');assert.equal(presentation.engine_library.id,'irgs-engine-routine-responses-v1');assert.equal(await page.locator('.last-outcome .entry-text').textContent(),presentation.text);assert(presentation.text.startsWith(result.outcome.summary));assert.equal(await page.locator('#notice').textContent(),result.outcome.summary);assert.equal(await page.locator('#declaration').inputValue(),draft);
    if(action==='try-gate'){assert.equal(result.status,'completed_unsuccessfully');assert(presentation.text.includes('remains closed'));}
    if(context.name==='settlement'){assert.equal(result.elapsed_time.duration_seconds,undefined);if(result.elapsed_time.seconds===0)zeroSpans.push(action);}
   }
   const save=JSON.parse(fs.readFileSync(context.save));assert.equal(save.revision,revision);assert.equal(save.state.elapsed_time.seconds,context.elapsed);const committed=fs.readFileSync(context.save,'utf8');
   await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);await page.locator('#own-response-panel').evaluate(node=>node.open=true);assert.equal(await page.locator('#declaration').inputValue(),draft);
   await page.locator('#local-drafts').evaluate(node=>node.open=true);await page.locator('[data-local-draft="catalog:player.wait"]').click();await page.evaluate(()=>{location.hash='#/world';});await page.waitForFunction(()=>view==='world');assert(!(await page.locator('#action-review-dialog').evaluate(node=>node.open)));assert.equal(fs.readFileSync(context.save,'utf8'),committed);
   evidence.push({adapter:context.name,committed_actions:context.actions.length,elapsed_seconds:context.elapsed,zero_action_spans:zeroSpans,local_drafts_non_submitting:true,lost_acknowledgement_recovered:true,stale_navigation_fenced:true,reload_preserves_draft:true});
  }
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.equal(discarded.size,2);assert(lookups.length>=2);assert.equal(posts.length,9);assert.equal(providerCalls,0);assert.equal(fs.existsSync(metadata.replace(/\.json$/,'.inputs.json')),false);assert.deepEqual(errors,[]);assert(!JSON.stringify([posts,results,await page.content()]).includes('PRIVATE_EVALUATOR_MARKER'));
  const report={status:'passed',contexts:evidence,common_response_schema:1,catalog_library:'irgs-response-depot-v1',engine_library:'irgs-engine-routine-responses-v1',provider_configured:false,provider_calls:providerCalls,browser_errors:errors.length,mobile_width:390};if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{if(browser)await browser.close();if(processHost.exitCode===null){processHost.kill('SIGINT');await new Promise(resolve=>processHost.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
