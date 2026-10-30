'use strict';
// Ordinary reviewed starts; real Core decisions and grant controls, no provider.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
const hostCode=`import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'IRGS_Web'))
from server import make_server
folder=Path(sys.argv[2]);server=make_server(0,folder/'saves',reference_config=folder/'no-config.json',reference_cache=folder/'cache',solo_configuration=None)
(folder/'host.json').write_text(json.dumps({'port':server.server_port}))
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()`;
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'worldward-decisions-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B','-c',hostCode,path.resolve(__dirname,'..'),folder],{stdio:['ignore','ignore','pipe']});let stderr='',browser;child.stderr.on('data',data=>stderr+=data);
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Host failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const origin='http://127.0.0.1:'+JSON.parse(fs.readFileSync(metadata)).port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],external=[],posts=[];let providers=0;
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')posts.push(request.url());});
  await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\//.test(url)){providers++;return route.abort();}return route.continue();});
  const bytes=id=>fs.readFileSync(path.join(folder,'saves',id+'.json'),'utf8');
  const state=id=>JSON.parse(bytes(id)).state;
  const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  async function action(id,words,grant=false){
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#declaration').fill(words);
   const selected=await page.evaluate(action=>({id:current.id,revision:current.revision,cap:current.intent_control.capabilities.find(c=>c.action.action_id===action)?.capability_id}),id);assert(selected.cap);
   const before=bytes(selected.id);
   if(grant)await page.locator('[data-grant-intent="'+selected.cap+'"]').click();
   else{await page.locator('#intent-capability').selectOption(selected.cap);await page.locator('#review-intent').click();}
   await page.locator('#action-review-dialog[open]').waitFor();assert.equal(await page.locator('#action-review-intent').inputValue(),words);
   await page.locator('#cancel-reviewed-action').click();assert.equal(bytes(selected.id),before);assert.equal(await page.evaluate(()=>current.revision),selected.revision);
   await page.locator('#recover-intent-review').click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#confirm-reviewed-action').click();
   await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,selected.revision);
   const result=await page.evaluate(()=>current.completed_actions.at(-1));assert.equal(result.declaration,words);assert.equal(await page.locator('#declaration').inputValue(),words);
   return result;
  }
  await page.goto(origin);await page.waitForFunction(()=>token&&features.length);
  assert.equal(fs.readdirSync(path.join(folder,'saves')).filter(name=>name.endsWith('.json')).length,0);
  await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');await page.locator('.historical-campaign [data-catalogue-preview="MC-01"]').click();
  await page.locator('#catalogue-start-select').selectOption('hyw-1415');await page.locator('#inspect-dialog [data-start-entry="hyw-1415"]').click();
  await page.locator('#campaign-name').fill('Reviewed fictional worker decision');await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===1&&!historicalLoading);await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===2&&!startingLoading);
  await page.locator('#new-character-name').fill('Synthetic courier');await page.locator('#character-opening').selectOption('quay-contact-decision-v1');await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===3&&!startCheckLoading);
  assert((await page.locator('#setup-review').innerText()).includes('15'));
  await page.locator('#create-submit').click();await page.waitForFunction(()=>current?.name==='Reviewed fictional worker decision'&&!busy);
  const quay=await page.evaluate(()=>({id:current.id,actor:current.actor_id})),initial=state(quay.id);
  assert(await page.locator('#grant-intent-actions').isHidden());
  const refusal=await action('request-dispatch-help','I ask the worker to carry the dispatch.');
  assert.equal(refusal.status,'completed_successfully');assert.match(refusal.outcome.summary,/declines to take custody/i);
  assert.deepEqual(state(quay.id).stocks,initial.stocks);assert.deepEqual(state(quay.id).campaign_time,initial.campaign_time);assert.equal(state(quay.id).elapsed_time.seconds,15);
  assert(!state(quay.id).player_actor_ids.includes('FICTIONAL-QUAY-CONTACT'));
  for(const [id,words] of [['quay-passage','I take the covered passage.'],['passage-desk','I approach the delivery desk.'],['deliver-dispatch','I deliver the sealed dispatch.']])await action(id,words);
  assert.equal(state(quay.id).stocks[quay.actor].sealed_dispatch,0);assert.equal(state(quay.id).stocks['clerk-tray'].sealed_dispatch,1);assert.equal(state(quay.id).elapsed_time.seconds,115);
  const saved=bytes(quay.id),replayed=await page.evaluate(async packet=>api('intent/execute',packet,{creator:false}),{id:quay.id,actor:quay.actor,request_id:refusal.request_id,explicitly_accepted:true});
  assert.deepEqual(replayed,refusal);assert.equal(bytes(quay.id),saved);
  await page.setViewportSize({width:390,height:844});await fits();await page.setViewportSize({width:1568,height:1000});
  await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');await page.locator('#catalogue-current-starts > summary').click();await page.locator('[data-rise-setup]').click();await page.locator('#rise-form').waitFor();
  for(const [key,value] of Object.entries({name:'Reviewed grant controls',founder_name:'Synthetic founder',household_name:'Synthetic household',settlement_name:'Reviewed camp'}))await page.locator('#rise-form [name="'+key+'"]').fill(value);
  await page.locator('#rise-form [name="permission"]').selectOption('seek');await page.locator('#rise-form button[type="submit"]').click();await page.locator('#rise-confirm').check();await page.locator('#rise-create').click();await page.waitForFunction(()=>current?.name==='Reviewed grant controls'&&!busy);
  const rise=await page.evaluate(()=>({id:current.id,actor:current.actor_id}));assert.deepEqual(state(rise.id).grants,{});
  await page.locator('#own-response-panel').evaluate(node=>node.open=true);assert.equal(await page.locator('#grant-intent-actions button').count(),2);
  await page.locator('#declaration').fill('');const priorPosts=posts.length;await page.locator('#grant-intent-actions button').first().click();assert.equal(posts.length,priorPosts);assert.deepEqual(state(rise.id).grants,{});
  const stocks=state(rise.id).stocks;
  await action('request_grant','I ask for permission to establish the camp.',true);assert.equal(state(rise.id).grants.founding.status,'offered');assert.deepEqual(state(rise.id).stocks,stocks);
  await action('accept_grant','I accept the limited founding grant.',true);assert.equal(state(rise.id).grants.founding.status,'accepted');assert.deepEqual(state(rise.id).stocks,stocks);
  const draft='I will consider what to do next.';await page.locator('#declaration').fill(draft);await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,rise.id);assert.equal(await page.locator('#declaration').inputValue(),draft);
  await page.setViewportSize({width:390,height:844});await page.locator('#own-response-panel').evaluate(node=>node.open=true);await fits();
  assert(await page.evaluate(()=>document.querySelector('#reading-scroll').contains(document.querySelector('#grant-intent-actions'))));
  assert.equal(providers,0);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const result={status:'passed',ordinary_quay_creation:true,selected_worker_refusal:true,no_custody_or_consent_inferred:true,actual_conserved_delivery:true,original_refusal_replay:true,ordinary_rise_creation:true,grant_request_and_acceptance_separate:true,review_cancel_no_effect:true,empty_words_no_submission:true,exact_words_and_reload_draft:true,widths:[1568,390],provider_calls:0,browser_errors:0,external_requests:0};
  if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
