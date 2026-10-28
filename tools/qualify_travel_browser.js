'use strict';
// Normal reviewed R00 initialization, actual UI phase controls and Core persistence.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
const hostCode=String.raw`
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'IRGS_Web'))
from server import make_server
folder=Path(sys.argv[2])
host=make_server(0,folder/'saves',reference_config=folder/'no-personal-config.json',reference_cache=folder/'cache',solo_configuration=None)
(folder/'host.json').write_text(json.dumps({'port':host.server_port}))
try:host.serve_forever()
except KeyboardInterrupt:pass
finally:host.server_close()
`;
(async()=>{
 const root=path.resolve(__dirname,'..'),folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-travel-browser-'));
 const child=spawn('python3',['-B','-c',hostCode,root,folder],{stdio:['ignore','ignore','pipe']});
 let hostError='',browser;child.stderr.on('data',chunk=>hostError+=chunk);
 try{
  const metadata=path.join(folder,'host.json'),deadline=Date.now()+20000;
  while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Travel host unavailable: '+hostError);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),origin='http://127.0.0.1:'+host.port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[],external=[],executions=[];
  let providerCalls=0,dropExecute=false;
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url)){providerCalls++;return route.abort();}return route.continue();});
  await page.route('**/api/process/execute',async route=>{const response=await route.fetch(),result=await response.json();assert.equal(response.status(),200);executions.push({body:route.request().postDataJSON(),result});if(dropExecute){dropExecute=false;return route.abort('failed');}return route.fulfill({response});});
  const session=await (await page.request.get(origin+'/api/campaigns')).json(),headers={'X-IRGS-Token':session.token};
  async function post(endpoint,data){const response=await page.request.post(origin+'/api/'+endpoint,{headers,data});const result=await response.json();assert.equal(response.status(),200,JSON.stringify(result));return result;}
  const choices={template_id:'R00',founder_name:'Travel reviewer',household_name:'Synthetic household',settlement_name:'Synthetic camp',region_name:'Greywater Reach',date_label:'Spring, Year 1',company:'sibling',permission:'seek',supplies:'basic'};
  const review=await post('rise/preview',{choices});
  const created=await post('rise/create',{name:'Synthetic ordinary travel',choices,review_digest:review.review_digest,request_id:'browser-travel-create'});
  const file=path.join(folder,'saves',created.id+'.json'),read=()=>JSON.parse(fs.readFileSync(file,'utf8'));
  const before=read(),stocks=JSON.parse(JSON.stringify(before.state.stocks));
  await page.goto(origin);await page.waitForFunction(()=>typeof token==='string'&&!loadingCampaign);
  await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(created.id);
  await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,created.id);
  const index=await page.evaluate(()=>current.process_control.start_options.findIndex(row=>row.kind==='travel'&&row.action_id==='walk_clearing'));assert(index>=0);
  const original=fs.readFileSync(file,'utf8');
  await page.locator('[data-process-start="'+index+'"]').click();await page.locator('#action-review-dialog[open]').waitFor();
  assert.equal(fs.readFileSync(file,'utf8'),original);await page.locator('#cancel-reviewed-action').click();assert.equal(fs.readFileSync(file,'utf8'),original);
  async function confirm(){await page.locator('#action-review-dialog[open]').waitFor();const revision=await page.evaluate(()=>current.revision);await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(value=>current?.revision===value+1&&!busy,revision);return executions.at(-1).result;}
  await page.locator('[data-process-start="'+index+'"]').click();const started=await confirm();
  assert.equal(started.process.kind,'travel');assert.equal(started.process.status,'active');
  assert.equal(read().state.stock_accounts['founder-home'].site,'route:commons-clearing');assert.deepEqual(read().state.stocks,stocks);
  assert.equal(await page.locator('[data-process-command][data-command="cancel"]').count(),0);
  async function command(name,seconds){if(seconds!==undefined)await page.locator('[data-process-seconds]').fill(String(seconds));await page.locator('[data-process-command][data-command="'+name+'"]').click();return confirm();}
  dropExecute=true;const partial=await command('advance',100);assert.equal(partial.process.worked_seconds,100);assert.equal(read().state.elapsed_time.seconds,100);
  assert.equal((await command('pause')).process.status,'paused');assert.equal(await page.locator('[data-process-command][data-command="cancel"]').count(),0);
  await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,created.id);assert.equal(await page.evaluate(()=>current.process_control.processes[0].received.status),'paused');
  assert.equal((await command('resume')).process.status,'active');
  const arrived=await command('advance',1000),state=read().state;
  assert.equal(arrived.process.status,'completed');assert.equal(arrived.process.elapsed_total,300);assert.equal(state.elapsed_time.seconds,300);
  assert.equal(state.actors.founder.current.location,'clearing');assert.equal(state.actors.rowan.current.location,'clearing');assert.equal(state.stock_accounts['founder-home'].site,'clearing');assert.deepEqual(state.stocks,stocks);
  const saved=fs.readFileSync(file,'utf8'),last=executions.at(-1),replay=await post('process/execute',last.body);assert.deepEqual(replay,last.result);assert.equal(fs.readFileSync(file,'utf8'),saved);
  const startReplay=await post('process/execute',executions[0].body);assert.deepEqual(startReplay,started);assert.equal(startReplay.process.status,'active');assert.equal(fs.readFileSync(file,'utf8'),saved);
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert(await page.locator('.process-controls').isVisible());
  await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,created.id);assert.equal(await page.evaluate(()=>current.process_control.processes[0].received.status),'completed');assert.equal(fs.readFileSync(file,'utf8'),saved);
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);assert.equal(providerCalls,0);
  const result={status:'passed',context:'ordinary_R00_phased_travel',review_does_not_commit:true,cancelled_review_has_no_effect:true,partial_pause_resume_arrival:true,household_and_stock_location_conserved:true,stock_quantities_conserved:true,travel_cancel_not_advertised:true,elapsed_seconds:300,lost_commit_ack_recovered:true,immutable_original_start_receipt:true,duplicate_final_result_once:true,reload_continuation:true,mobile_width:390,provider_calls:0,browser_errors:0,external_requests:0};
  if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
