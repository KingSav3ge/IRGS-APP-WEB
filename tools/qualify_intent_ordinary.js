'use strict';
// Empty temporary store; ordinary reviewed creation in two real campaign contexts.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
const hostCode=`import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'IRGS_Web'))
from server import make_server
folder=Path(sys.argv[2]);server=make_server(0,folder/'saves')
(folder/'host.json').write_text(json.dumps({'port':server.server_port}))
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()`;
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'worldward-ordinary-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B','-c',hostCode,path.resolve(__dirname,'..'),folder],{stdio:['ignore','ignore','pipe']});let stderr='',browser;child.stderr.on('data',data=>stderr+=data);
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Host failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const origin='http://127.0.0.1:'+JSON.parse(fs.readFileSync(metadata)).port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],external=[],contexts=[];let providers=0;
  page.on('pageerror',error=>errors.push(error.message));await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url)){providers++;return route.abort();}return route.continue();});
  async function reviewedAction(action,words){
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);await page.locator('#declaration').fill(words);
   const cap=await page.evaluate(id=>current.intent_control.capabilities.find(item=>item.action.action_id===id)?.capability_id,action);assert(cap);
   await page.locator('#intent-capability').selectOption(cap);const revision=await page.evaluate(()=>current.revision);
   await page.locator('#review-intent').click();await page.locator('#action-review-dialog[open]').waitFor();
   assert.equal(await page.locator('#action-review-intent').inputValue(),words);assert((await page.locator('#action-review-description').innerText()).includes(action));
   await page.locator('#cancel-reviewed-action').click();assert.equal(await page.evaluate(()=>current.revision),revision);await page.locator('#recover-intent-review').click();
   await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(revision=>current?.revision===revision+1&&!busy,revision);
   const result=await page.evaluate(()=>current.completed_actions.at(-1));assert.equal(result.status,'completed_successfully');assert.equal(result.declaration,words);
   assert.equal(await page.locator('#declaration').inputValue(),words);const saved=await page.evaluate(()=>({id:current.id,revision:current.revision}));
   await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,saved.id);assert.equal(await page.evaluate(()=>current.revision),saved.revision);assert.deepEqual(await page.evaluate(()=>current.completed_actions.at(-1)),result);
   await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert(await page.evaluate(()=>{const v=document.querySelector('#reading-scroll'),feed=document.querySelector('#story-feed'),decision=document.querySelector('.story-decisions'),composer=document.querySelector('#own-response-panel');return v.contains(feed)&&v.contains(composer)&&feed.getBoundingClientRect().bottom<=decision.getBoundingClientRect().top+1&&decision.getBoundingClientRect().bottom<=composer.getBoundingClientRect().top+1;}));
   contexts.push({action,normal_reviewed_creation:true,review_cancel_no_effect:true,actual_commit:true,exact_words:true,retained_draft:true,reload:true,mobile_width:390});await page.setViewportSize({width:1568,height:1000});
  }
  await page.goto(origin);await page.waitForFunction(()=>token&&features.length);assert.equal(fs.readdirSync(path.join(folder,'saves')).filter(name=>name.endsWith('.json')).length,0);
  await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');await page.locator('.historical-campaign [data-catalogue-preview="MC-01"]').click();await page.locator('#catalogue-start-select').selectOption('hyw-1415');await page.locator('#inspect-dialog [data-start-entry="hyw-1415"]').click();
  await page.locator('#campaign-name').fill('Ordinary authored intent');await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===1&&!historicalLoading);await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===2&&!startingLoading);await page.locator('#new-character-name').fill('Ordinary fictional person');await page.locator('#character-opening').selectOption('quay-delivery-v1');await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===3&&!startCheckLoading);await page.locator('#create-submit').click();await page.waitForFunction(()=>current?.name==='Ordinary authored intent'&&!busy);
  await reviewedAction('look-quay','I carefully inspect the quay.');
  await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');await page.locator('#catalogue-current-starts > summary').click();await page.locator('[data-rise-setup]').click();await page.locator('#rise-form').waitFor();
  for(const [key,value] of Object.entries({name:'Ordinary Rise intent',founder_name:'Founder',household_name:'Founder household',settlement_name:'Reviewed clearing'}))await page.locator('#rise-form [name="'+key+'"]').fill(value);
  await page.locator('#rise-form [name="permission"]').selectOption('held');await page.locator('#rise-form button[type="submit"]').click();await page.locator('#rise-confirm').check();await page.locator('#rise-create').click();await page.waitForFunction(()=>current?.name==='Ordinary Rise intent'&&!busy);
  await reviewedAction('inspect','I look over the household supplies.');
  assert.equal(providers,0);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);const result={status:'passed',contexts,provider_calls:0,browser_errors:0,external_requests:0};if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
