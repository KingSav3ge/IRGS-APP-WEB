'use strict';
// Normal canonical host, EMPTY temporary store, actual reviewed UI starts.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
const hostCode=`
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'IRGS_Web'))
from server import make_server
folder=Path(sys.argv[2])
server=make_server(0,folder/'saves')
(folder/'host.json').write_text(json.dumps({'port':server.server_port}))
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()
`;
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-start-readiness-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B','-c',hostCode,path.resolve(__dirname,'..'),folder],{stdio:['ignore','ignore','pipe']});
 let hostError='',browser;child.stderr.on('data',data=>hostError+=data);
 const shots=process.argv[3];if(shots)fs.mkdirSync(shots,{recursive:true});
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Empty-store host failed: '+hostError);await new Promise(resolve=>setTimeout(resolve,50));}
  const origin='http://127.0.0.1:'+JSON.parse(fs.readFileSync(metadata)).port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],posts=[],external=[],contexts=[];let providerCalls=0;
  page.on('pageerror',error=>errors.push(error.message));
  page.on('request',request=>{if(request.method()==='POST')posts.push({url:request.url(),body:request.postDataJSON()});});
  await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url)){providerCalls++;return route.abort();}return route.continue();});
  const count=()=>fs.readdirSync(path.join(folder,'saves')).filter(name=>name.endsWith('.json')).length;
  const snapshot=()=>page.evaluate(()=>({id:current.id,revision:current.revision,actor:current.actor_id,character:current.character,scene:current.scene,elapsed:current.elapsed_time,readiness:current.play_readiness}));
  const fits=async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));if(await page.locator('#create-dialog').isVisible())assert(await page.locator('#create-dialog').evaluate(node=>node.scrollWidth<=node.clientWidth));};
  const shot=async name=>{if(shots)await page.screenshot({path:path.join(shots,name+'.png')});};
  async function setup(name){
   await page.setViewportSize({width:1568,height:1000});await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');
   await page.locator('.historical-campaign [data-catalogue-preview="MC-01"]').click();await page.locator('#catalogue-start-select').selectOption('hyw-1415');await page.locator('#inspect-dialog [data-start-entry="hyw-1415"]').click();
   await page.locator('#campaign-name').fill(name);await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===1&&!historicalLoading);await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===2&&!startingLoading);
  }
  async function review(){await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===3&&!startCheckLoading);}
  async function create(name){await page.locator('#create-submit').click();await page.waitForFunction(name=>current?.name===name&&!busy&&!document.querySelector('#create-dialog').open,name);return snapshot();}
  async function reload(saved){await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,saved.id);assert.equal((await snapshot()).revision,saved.revision);}
  await page.goto(origin);await page.waitForFunction(()=>token&&features.length);assert.equal(count(),0);

  await setup('Cancelled readiness');await page.locator('#new-character-name').fill('Uncreated human');
  const unavailable=async route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:'Selected source is temporarily unavailable. Retry review.'})});
  await page.route('**/api/starting-preview?*',unavailable);await page.locator('#setup-next').click();await page.waitForFunction(()=>!startCheckLoading&&document.querySelector('#create-error').textContent.includes('source'));
  assert.equal(await page.evaluate(()=>wizardStep),2);assert.equal(count(),0);await page.unroute('**/api/starting-preview?*',unavailable);
  await review();assert(await page.locator('#create-submit').isDisabled());await fits();await shot('declaration-review-mobile');
  await page.locator('#confirm-declaration-start').check();await page.locator('#setup-back').click();await page.locator('#new-character-name').fill('Changed human');await review();assert(await page.locator('#create-submit').isDisabled());
  await page.locator('#cancel-create').click();assert.equal(count(),0);assert.equal(posts.length,0);

  await setup('Existing John 1415');await page.locator('#character-kind').selectOption('existing');
  const john=await page.evaluate(()=>startingCharacters().find(row=>row.name==='John of Lancaster').id);await page.locator('#starting-character').selectOption(john);
  await review();assert.equal(await page.evaluate(()=>reviewSelection.readiness.status),'declaration_only');assert(await page.locator('#create-submit').isDisabled());assert.equal(count(),0);
  await page.locator('#confirm-declaration-start').check();
  let dropCreation=true;const creationReplies=[];
  const creationRoute=async route=>{creationReplies.push(route.request().postDataJSON());const response=await route.fetch();if(dropCreation){dropCreation=false;await route.abort('failed');}else await route.fulfill({response});};
  await page.route('**/api/create',creationRoute);await page.locator('#create-submit').click();await page.waitForFunction(()=>!busy&&reviewSelection?.recovery===true);
  assert.equal(count(),1);const existing=await create('Existing John 1415');assert.deepEqual(creationReplies[1],creationReplies[0]);await page.unroute('**/api/create',creationRoute);
  assert.equal(existing.actor,john);assert.equal(existing.scene.location,null);assert.equal(existing.readiness.status,'declaration_only');assert.equal(existing.readiness.action_count,0);
  await fits();await shot('existing-john-mobile');await reload(existing);assert.equal((await snapshot()).scene.location,null);
  assert(!(await page.locator('#play-tools-content').innerText()).includes('choose a listed action'));
  await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#declaration').fill('I look around and ask where I am.');await page.locator('#send-declaration').click();await page.waitForFunction(()=>Boolean(current?.pending_declaration)&&!busy);
  assert.equal(await page.evaluate(()=>current.pending_declaration.status),'declared_not_resolved');const pending=await snapshot();await reload(pending);await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#withdraw-action').click();await page.waitForFunction(()=>current&&!current.pending_declaration&&!busy);
  assert.equal((await snapshot()).elapsed,existing.elapsed);contexts.push({name:'existing_john_1415',status:'declaration_only',new_engine_initializer_delivered:false,lost_creation_ack_recovered:true,unresolved_intent_reload_withdraw:true});

  await setup('Deliberate reference');await page.locator('#new-character-name').fill('Reference human');await page.locator('#new-character-background').fill('I claim a castle; this is testimony.');await review();
  assert.equal(await page.evaluate(()=>reviewSelection.readiness.status),'declaration_only');await page.locator('#confirm-declaration-start').check();const reference=await create('Deliberate reference');assert.equal(reference.scene.location,null);
  assert.equal(await page.evaluate(()=>current.inventory.length),0);assert(await page.evaluate(()=>current.evidence.some(item=>item.assertion==='I claim a castle; this is testimony.'&&item.status==='testimony')));await reload(reference);
  contexts.push({name:'new_human_reference',status:'declaration_only',explicit_choice:true,background_is_testimony:true});

  await setup('Authored human');await page.locator('#new-character-name').fill('Authored human');await page.locator('#character-opening').selectOption('quay-delivery-v1');await review();
  assert.equal(await page.evaluate(()=>reviewSelection.readiness.status),'supported_slice');assert(await page.locator('#declaration-start-consent').isHidden());const preview=await page.evaluate(()=>reviewSelection.readiness);
  const authored=await create('Authored human');assert.equal(authored.scene.location,preview.scene.location);assert.deepEqual(authored.scene,preview.scene);assert.equal(authored.readiness.action_count,preview.action_count);
  const requests=[],receipts=[];let dropAction=true;
  const actionRoute=async route=>{requests.push(route.request().postDataJSON());const response=await route.fetch();receipts.push(await response.json());if(dropAction){dropAction=false;await route.abort('failed');}else await route.fulfill({response});};await page.route('**/api/action',actionRoute);
  const beforeAction=posts.length;await page.locator('[data-supported-action]').first().click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#cancel-reviewed-action').click();assert.equal(posts.length,beforeAction);
  await page.locator('[data-supported-action]').first().click();await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,authored.revision);
  const after=await snapshot();assert.equal(after.elapsed.seconds,20);const received=await page.evaluate(()=>current.completed_actions.at(-1));assert.deepEqual(received,receipts[0]);
  await reload(after);assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),received);const replay=await page.request.post(origin+'/api/action',{headers:{'X-IRGS-Token':await page.evaluate(()=>token)},data:requests[0]});assert.deepEqual(await replay.json(),received);
  assert.equal(JSON.parse(fs.readFileSync(path.join(folder,'saves',after.id+'.json'))).revision,after.revision);await fits();await shot('authored-human-mobile');
  contexts.push({name:'new_human_authored',status:'supported_slice',received_result_retained:true,lost_action_ack_recovered:true,replay_same_receipt:true,elapsed_seconds:20});

  await page.setViewportSize({width:1568,height:1000});await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');
  await page.locator('#catalogue-current-starts > summary').click();await page.locator('[data-rise-setup]').click();await page.locator('#rise-form').waitFor();
  for(const [key,value] of Object.entries({name:'Readiness R00',founder_name:'Founder',household_name:'Founder household',settlement_name:'Reviewed clearing'}))await page.locator('#rise-form [name="'+key+'"]').fill(value);
  await page.locator('#rise-form [name="permission"]').selectOption('held');await page.locator('#rise-form button[type="submit"]').click();await page.locator('#rise-confirm').check();await page.locator('#rise-create').click();await page.waitForFunction(()=>current?.name==='Readiness R00'&&!busy);
  assert.equal(await page.evaluate(()=>current.play_readiness.status),'supported_slice');
  for(const action of ['walk_clearing','found','build','wait_hour','wait_hour']){const revision=await page.evaluate(()=>current.revision);await page.locator('[data-rise-action="'+action+'"]').click();await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,revision);}
  const rise=await snapshot();assert.equal(await page.evaluate(()=>current.settlement.elapsed_seconds),3900);const riseReceipt=await page.evaluate(()=>current.completed_actions.at(-1));await reload(rise);assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),riseReceipt);await fits();await shot('rise-mobile');
  contexts.push({name:'R00_regression',status:'supported_slice',confirmed_actions:5,elapsed_seconds:3900,received_result_retained:true});

  await setup('Henry default reference');await page.locator('#character-kind').selectOption('existing');await page.locator('#starting-character').selectOption('HYW-HENRY-V');
  assert.equal(await page.locator('#existing-character-opening').inputValue(),'');await review();
  assert.equal(await page.evaluate(()=>reviewSelection.readiness.engine_review.selected_mode.status),'declaration_only');assert(await page.locator('#create-submit').isDisabled());
  await page.locator('#confirm-declaration-start').check();const henryDefault=await create('Henry default reference');assert.equal(henryDefault.readiness.action_count,0);assert.equal(henryDefault.scene.location,null);assert.equal(henryDefault.elapsed,null);
  assert.equal(await page.evaluate(()=>current.start_context.civil_time.current_calendar_binding),false);await reload(henryDefault);await fits();await shot('henry-default-mobile');
  contexts.push({name:'existing_henry_default',status:'declaration_only',opening_not_added_automatically:true,received_initial_day:true});

  await setup('Henry explicit observation');await page.locator('#character-kind').selectOption('existing');await page.locator('#starting-character').selectOption('HYW-HENRY-V');
  assert.equal(await page.locator('#existing-character-opening option').count(),2);await page.locator('#existing-character-opening').selectOption('henry-1415-embarkation-v1');
  await page.locator('#starting-character').selectOption('HYW-JOHN-BEDFORD');assert.equal(await page.locator('#existing-character-opening').inputValue(),'');assert(await page.locator('#existing-opening-section').isHidden());
  await page.locator('#starting-character').selectOption('HYW-HENRY-V');assert.equal(await page.locator('#existing-character-opening').inputValue(),'');
  await page.locator('#existing-character-opening').selectOption('henry-1415-embarkation-v1');await review();
  assert.equal(await page.evaluate(()=>reviewSelection.readiness.engine_review.schema_version),'irgs-start-readiness-1');
  assert.equal(await page.evaluate(()=>reviewSelection.readiness.engine_review.selected_mode.mode_id),'henry-1415-embarkation-v1');
  assert((await page.locator('#setup-review').innerText()).includes('EXPLICIT SOURCED STARTING CONTEXT'));assert(!(await page.locator('#setup-review').innerText()).includes('AUTHORISED FICTIONAL OPENING'));
  const henryPreview=await page.evaluate(()=>reviewSelection.readiness);assert.equal(henryPreview.action_count,1);assert(await page.locator('#declaration-start-consent').isHidden());
  dropCreation=true;creationReplies.length=0;await page.route('**/api/create',creationRoute);await page.locator('#create-submit').click();await page.waitForFunction(()=>!busy&&reviewSelection?.recovery===true);
  const henry=await create('Henry explicit observation');await page.unroute('**/api/create',creationRoute);assert.deepEqual(creationReplies[0],creationReplies[1]);assert.equal(creationReplies[0].character.opening_id,'henry-1415-embarkation-v1');
  assert.equal(henry.actor,'HYW-HENRY-V');assert.equal(henry.scene.scope,'sourced_setting_with_selected_simulation_observation_rule');assert.equal(henry.scene.location,henryPreview.scene.location);assert.deepEqual(henry.elapsed,{axis:'selected-historical-observation-seconds',seconds:0});
  assert.deepEqual(await page.evaluate(()=>current.supported_actions.map(item=>item.action_id)),['observe-embarkation']);assert.equal(await page.evaluate(()=>current.inventory.length),0);
  const initialCivil=await page.evaluate(()=>current.start_context.civil_time);assert.equal(initialCivil.date,'1415-08-11');assert.equal(initialCivil.calendar,'julian');assert.equal(initialCivil.precision,'day');assert.equal(initialCivil.time,null);assert.equal(initialCivil.opening_hour,null);assert.equal(initialCivil.current_calendar_binding,false);
  const firstPrompt=await page.evaluate(()=>current.opening.blocks.find(item=>item.kind==='first_decision').text);assert(firstPrompt.includes('Observe the embarkation setting'));assert(!/dispatch|deliver|move|travel/i.test(firstPrompt));
  dropAction=true;requests.length=0;receipts.length=0;await page.locator('[data-supported-action]').click();await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,henry.revision);
  const henryAfter=await snapshot(),henryReceipt=await page.evaluate(()=>current.completed_actions.at(-1));assert.deepEqual(henryAfter.elapsed,{axis:'selected-historical-observation-seconds',seconds:20});assert.deepEqual(henryReceipt,receipts[0]);
  assert.equal(henryReceipt.elapsed_time.axis,'selected-historical-observation-seconds');assert.equal(henryReceipt.elapsed_time.duration_seconds,20);assert.deepEqual(await page.evaluate(()=>current.start_context.civil_time),initialCivil);
  assert((await page.locator('.opening-elapsed').innerText()).includes('20 seconds'));assert(/received initial checkpoint/i.test(await page.locator('#context-content').innerText()));
  const token=await page.evaluate(()=>token),header={'X-IRGS-Token':token},henrySave=path.join(folder,'saves',henry.id+'.json');const savedHenry=fs.readFileSync(henrySave,'utf8');
  for(const url of ['/api/playthrough/'+henry.id+'?actor_id=HYW-JOHN-BEDFORD','/api/action-result/'+henry.id+'/'+requests[0].request_id+'?actor_id=HYW-JOHN-BEDFORD'])assert.equal((await page.request.get(origin+url,{headers:header})).status(),403);
  const changed=await page.request.post(origin+'/api/action',{headers:header,data:{...requests[0],text:'Changed after execution'}});assert.equal(changed.status(),400);assert.equal(fs.readFileSync(henrySave,'utf8'),savedHenry);
  await reload(henryAfter);assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),henryReceipt);assert.equal(fs.readFileSync(henrySave,'utf8'),savedHenry);
  await fits();await page.locator('#own-response-panel').evaluate(node=>node.open=false);await shot('henry-explicit-mobile');await page.locator('#toggle-context').click();await shot('henry-clock-mobile');await page.keyboard.press('Escape');
  await page.setViewportSize({width:1568,height:1000});await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#delete-campaign').click();await page.locator('#delete-form .primary').click();await page.waitForFunction(id=>!busy&&current?.id!==id,henry.id);
  await page.locator('#play-tools-content [data-preview-view="trash"]').click();await page.locator('[data-restore="'+henry.id+'"]').click();await page.waitForFunction(id=>current?.id===id&&!busy&&!loadingCampaign,henry.id);
  assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),henryReceipt);assert.deepEqual(await page.evaluate(()=>current.start_context.civil_time),initialCivil);assert.equal(fs.readFileSync(henrySave,'utf8'),savedHenry);
  const restoredReplay=await page.request.post(origin+'/api/action',{headers:header,data:requests[0]});assert.deepEqual(await restoredReplay.json(),henryReceipt);assert.equal(fs.readFileSync(henrySave,'utf8'),savedHenry);
  const evaluatorState=JSON.parse(savedHenry).state;for(const key of ['stocks','capacities','orders','obligations'])assert.deepEqual(evaluatorState[key],{});
  assert.deepEqual(Object.keys(evaluatorState.actors['HYW-HENRY-V'].current),['location']);assert.equal(evaluatorState.campaign_time.day,0);
  contexts.push({name:'existing_henry_explicit',status:'supported_slice',engine_contract:'irgs-start-readiness-1',actor_bound_choice:true,changed_actor_clears_choice:true,lost_creation_ack_recovered:true,lost_action_ack_recovered:true,elapsed_axis:'selected-historical-observation-seconds',elapsed_seconds:20,initial_julian_day:'1415-08-11',opening_hour:null,current_calendar_binding:false,no_dispatch_or_courier_actions:true,actor_boundaries:true,changed_replay_rejected:true,reload_and_restore_preserve_exact_bytes:true,restored_original_result_replay:true});

  assert.equal(count(),6);assert.equal(providerCalls,0);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const report={status:'passed',initial_campaigns:0,final_campaigns:6,cancel_and_selection_changes_create_nothing:true,source_unavailable_stays_unconfirmed:true,mobile_width:390,contexts,provider_calls:providerCalls,browser_errors:errors.length,external_requests:external.length,posts:posts.map(item=>item.url.slice(origin.length))};
  if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
