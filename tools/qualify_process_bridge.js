'use strict';
// Real Chromium, two actual Core process kinds; temporary synthetic saves only.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-process-browser-')),metadata=path.join(folder,'host.json');
 const hostProcess=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'processes'],{stdio:['ignore','ignore','pipe']});let stderr='',browser;hostProcess.stderr.on('data',data=>stderr+=data);
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(hostProcess.exitCode!==null||Date.now()>deadline)throw Error('Process fixture failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata));browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage(),errors=[],prepared=[],executed=[],lookups=[],evidence=[];let providerCalls=0;
  const lostPrepare=new Set(),lostExecute=new Set();
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.url().includes('/api/action-result/'))lookups.push(request.url());});
  await page.route('**/api/ai/proposal',async route=>{providerCalls++;await route.abort();});await page.route('**/api/ai/accept',async route=>{providerCalls++;await route.abort();});
  await page.route('**/api/process/prepare',async route=>{const response=await route.fetch(),packet=await response.json();assert.equal(response.status(),200);prepared.push(packet);if(!lostPrepare.has(packet.campaign_id)){lostPrepare.add(packet.campaign_id);await route.abort('failed');}else await route.fulfill({response});});
  await page.route('**/api/process/execute',async route=>{const response=await route.fetch(),packet=await response.json();assert.equal(response.status(),200);executed.push(packet);if(!lostExecute.has(packet.campaign_id)){lostExecute.add(packet.campaign_id);await route.abort('failed');}else await route.fulfill({response});});
  await page.goto('http://127.0.0.1:'+host.port);
  for(const context of host.contexts){
   await page.locator('[data-view="story"]').first().click();await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(context.id);await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);
   assert.equal(await page.evaluate(()=>current.assistance.available),false);assert.equal(await page.evaluate(()=>current.process_control.engine_schema),'irgs-phase-capabilities-1');assert(await page.locator('[data-process-start]').count()>0);
   await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert(await page.locator('.process-controls').isVisible());await page.setViewportSize({width:1280,height:900});
   const before=fs.readFileSync(context.save,'utf8');let revision=context.revision;
   // Lost prepare response is recovered after a real reload, without a new ID.
   const optionIndex=await page.evaluate(action=>current.process_control.start_options.findIndex(row=>row.action_id===action),context.name==='work'?'build':'look-quay');assert(optionIndex>=0);await page.locator('[data-process-start="'+optionIndex+'"]').click();await page.waitForFunction(()=>!busy);assert.equal(fs.readFileSync(context.save,'utf8'),before);
   const first=prepared.at(-1);await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);await page.locator('#recover-process-review').click();await page.locator('#action-review-dialog[open]').waitFor();assert.equal(await page.locator('#action-review-intent').inputValue(),first.intention);
   await page.locator('#cancel-reviewed-action').click();assert.equal(executed.length,evidence.reduce((sum,item)=>sum+item.committed_phases,0));assert.equal(fs.readFileSync(context.save,'utf8'),before);
   await page.locator('#recover-process-review').click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#confirm-reviewed-action').click();revision++;await page.waitForFunction(revision=>current?.revision===revision&&!busy,revision);assert.equal(executed.at(-1).process.phase_id,first.phase_id);
   for(const [command,seconds] of context.commands){
    if(seconds!==null)await page.locator('[data-process-seconds]').fill(String(seconds));
    await page.locator('[data-command="'+command+'"]').click();await page.locator('#action-review-dialog[open]').waitFor();
    const checkpoint=fs.readFileSync(context.save,'utf8'),phase=prepared.at(-1);assert.equal(phase.command,command);if(seconds!==null)assert.equal(phase.details.seconds,seconds);assert.equal(fs.readFileSync(context.save,'utf8'),checkpoint);
    await page.locator('#confirm-reviewed-action').click();revision++;await page.waitForFunction(revision=>current?.revision===revision&&!busy,revision);
    const result=executed.at(-1);assert.equal(result.process.phase_id,phase.phase_id);assert.equal(result.process.phase_intention,phase.intention);assert.equal(await page.locator('.last-outcome p').textContent(),result.presentation.text);assert.equal(result.process.actor,context.actor);assert.deepEqual(result.presentation.render_usage,{provider_calls:0,model_tokens:0});
    if(command==='resume')assert.equal(result.process.worked_seconds,0);
   }
   const save=JSON.parse(fs.readFileSync(context.save));assert.equal(save.state.elapsed_time.seconds,context.elapsed);assert.equal(save.revision,revision);assert.equal(executed.at(-1).process.status,'completed');assert.equal(await page.locator('[data-command="advance"]').count(),0);
   const committed=fs.readFileSync(context.save,'utf8');await page.locator('[data-command="inspect"]').click();await page.locator('#action-review-dialog[open]').waitFor();await page.evaluate(()=>location.hash='#/world');await page.waitForFunction(()=>view==='world');assert.equal(await page.locator('#action-review-dialog').evaluate(node=>node.open),false);assert.equal(fs.readFileSync(context.save,'utf8'),committed);
   evidence.push({kind:context.name,committed_phases:context.commands.length+1,start_selected_from_engine:true,elapsed_seconds:context.elapsed,prepare_reload_recovered:true,cancel_does_not_execute:true,lost_commit_ack_recovered:true,phase_identity_preserved:true,pause_resume:true,stale_navigation_fenced:true});
  }
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.equal(lostPrepare.size,2);assert.equal(lostExecute.size,2);assert(lookups.length>=2);assert.equal(providerCalls,0);assert.deepEqual(errors,[]);assert(!JSON.stringify([prepared,executed,await page.content()]).includes('PRIVATE_EVALUATOR_MARKER'));
  const result={status:'passed',contexts:evidence,provider_configured:false,provider_calls:providerCalls,browser_errors:errors.length,mobile_width:390};if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(hostProcess.exitCode===null){hostProcess.kill('SIGINT');await new Promise(resolve=>hostProcess.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
