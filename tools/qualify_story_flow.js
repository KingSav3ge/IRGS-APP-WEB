'use strict';
// Actual isolated host plus optional read-only known-view presentation replay.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');

(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-story-flow-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'shared'],{stdio:['ignore','ignore','pipe']});
 let hostError='',browser;child.stderr.on('data',data=>hostError+=data);
 const reportPath=process.argv[2],screenshots=process.argv[3];if(screenshots)fs.mkdirSync(screenshots,{recursive:true});
 try{
  const deadline=Date.now()+20000;
  while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Story host failed: '+hostError);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),origin='http://127.0.0.1:'+host.port;
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],external=[],writes=[],evidence=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',async route=>{const request=route.request(),url=request.url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url))throw Error('Unexpected provider request');if(request.method()==='POST')writes.push(url);return route.continue();});
  async function checkFlow(){
   const flow=await page.evaluate(()=>{
    const area=document.querySelector('#reading-scroll'),feed=document.querySelector('#story-feed'),decision=document.querySelector('.story-decisions'),composer=document.querySelector('#own-response-panel');
    const entries=storyDisplayEntries(),ids=[...feed.children].filter(node=>node.classList.contains('feed-entry')).map(node=>node.id);
    return {ids,expected:entries.map(entry=>'entry-'+entry.id),positions:entries.map(storySequence).filter(Number.isSafeInteger),folded:!!feed.closest('details'),singleViewport:area.contains(feed)&&area.contains(composer),
     contentOverflow:getComputedStyle(document.querySelector('#content')).overflowY,composerOverflow:getComputedStyle(composer).overflowY,
     lastBottom:feed.getBoundingClientRect().bottom,choicesTop:decision.getBoundingClientRect().top,choicesBottom:decision.getBoundingClientRect().bottom,composerTop:composer.getBoundingClientRect().top,
     horizontalOverflow:document.documentElement.scrollWidth>innerWidth,background:getComputedStyle(feed).backgroundColor,border:getComputedStyle(feed).borderWidth};
   });
   assert.deepEqual(flow.ids,flow.expected);assert.deepEqual(flow.positions,[...flow.positions].sort((a,b)=>a-b));
   assert.equal(flow.folded,false);assert(flow.singleViewport);assert.equal(flow.contentOverflow,'visible');assert.equal(flow.composerOverflow,'visible');
   assert(flow.lastBottom<=flow.choicesTop+1);assert(flow.choicesBottom<=flow.composerTop+1);assert.equal(flow.horizontalOverflow,false);
   assert.equal(flow.background,'rgba(0, 0, 0, 0)');assert.equal(flow.border,'0px');return flow;
  }
  const capture=async name=>{if(screenshots){await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(screenshots,name+'.png')});}};
  await page.goto(origin);await page.waitForFunction(()=>current&&!loadingCampaign);
  for(const context of host.contexts){
   await page.locator('[data-view="story"]').first().click();await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(context.id);
   await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);
   const draft='My independent unsent '+context.name+' response.';await page.locator('#declaration').fill(draft);
   const before=fs.readFileSync(context.save,'utf8'),writesBefore=writes.length;
   const selector=context.name==='settlement'?'[data-rise-action="'+context.actions[0]+'"]':'[data-supported-action="0"]';
   await page.locator(selector).click();await page.locator('#action-review-dialog[open]').waitFor();await page.locator('#cancel-reviewed-action').click();
   assert.equal(writes.length,writesBefore);assert.equal(fs.readFileSync(context.save,'utf8'),before);
   await page.locator(selector).click();await page.locator('#action-review-dialog[open]').waitFor();
   const revision=await page.evaluate(()=>current.revision);await page.locator('#confirm-reviewed-action').click();await page.waitForFunction(value=>current?.revision===value+1&&!busy,revision);
   assert.equal(writes.length,writesBefore+1);assert.equal(await page.locator('#declaration').inputValue(),draft);
   const original=fs.readFileSync(context.save,'utf8');const desktop=await checkFlow();
   await page.locator('#declaration').scrollIntoViewIfNeeded();await capture(context.name+'-response-desktop');
   await page.setViewportSize({width:390,height:844});await checkFlow();await page.locator('#declaration').scrollIntoViewIfNeeded();await capture(context.name+'-response-mobile');
   await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);
   assert.equal(await page.locator('#declaration').inputValue(),draft);assert.equal(fs.readFileSync(context.save,'utf8'),original);await checkFlow();
   await page.setViewportSize({width:1568,height:1000});
   evidence.push({context:context.name,entries:desktop.ids.length,chronological:true,choices_and_composer_below_tale:true,one_reading_viewport:true,review_cancel_no_effect:true,one_confirmed_commit:true,draft_and_reload_preserved:true,widths:[1568,390]});
  }
  let replay=null;
  if(process.argv[4]){
   const known=JSON.parse(fs.readFileSync(process.argv[4],'utf8')),original=JSON.stringify(known),writesBefore=writes.length;
   const saved=host.contexts.map(context=>fs.readFileSync(context.save,'utf8'));
   await page.evaluate(data=>{workspaceMode='player';view='story';current=data;loadingCampaign=false;document.querySelector('#declaration').value='';render();},known);
   const desktop=await checkFlow();assert.equal(await page.locator('#story-feed .player_declaration').count(),1);
   await page.locator('#reading-scroll').evaluate(node=>node.scrollTop=0);await capture('known-view-story-beginning');
   await page.locator('#declaration').scrollIntoViewIfNeeded();await capture('known-view-latest-desktop');
   await page.setViewportSize({width:390,height:844});await checkFlow();await page.locator('#declaration').scrollIntoViewIfNeeded();await capture('known-view-latest-mobile');
   assert.equal(await page.evaluate(()=>JSON.stringify(current)),original);assert.equal(writes.length,writesBefore);
   host.contexts.forEach((context,index)=>assert.equal(fs.readFileSync(context.save,'utf8'),saved[index]));
   replay={mode:'read_only_browser_projection',entries:desktop.ids.length,oldest_to_newest:true,includes_pending_declaration:true,projection_unchanged:true,save_loaded_or_modified:false,post_requests:0};
  }
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  const report={status:'passed',contexts:evidence,known_view_replay:replay,browser_errors:0,provider_calls:0,external_requests:0,user_saves_opened:false};
  if(reportPath)fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
