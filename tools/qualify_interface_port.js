'use strict';
// Real local host, temporary synthetic saves, no provider or external asset access.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');
(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-interface-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'shared'],{env:process.env,stdio:['ignore','ignore','pipe']});
 let hostError='',browser;child.stderr.on('data',data=>hostError+=data);
 const reportPath=process.argv[2],screenshots=process.argv[3];if(screenshots)fs.mkdirSync(screenshots,{recursive:true});
 try{
  const deadline=Date.now()+20000;while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Interface host failed: '+hostError);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),originals=host.contexts.map(context=>({path:context.save,bytes:fs.readFileSync(context.save,'utf8')}));
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),errors=[],external=[],posts=[],assets=[];let providerCalls=0;
  const origin='http://127.0.0.1:'+host.port;
  await page.route('**/*',async route=>{const request=route.request();if(!request.url().startsWith(origin+'/')){external.push(request.url());return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(request.url())){providerCalls++;return route.abort();}return route.continue();});
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')posts.push({url:request.url(),body:request.postDataJSON()});});
  page.on('response',response=>{if(/\.(woff2|jpg|css|js)$/.test(response.url()))assets.push({url:response.url().slice(origin.length),status:response.status()});});
  const screenshot=async name=>{if(screenshots){await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(screenshots,name+'.png')});}};
  const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.goto(origin);await page.waitForFunction(()=>typeof current!=='undefined'&&!loadingCampaign);await page.locator('[data-view="home"]').click();await screenshot('home-desktop');
  await page.locator('#home-library').click();await page.waitForSelector('.catalogue-card');assert.equal(await page.locator('.catalogue-card').count(),44);await screenshot('library-desktop');
  await page.locator('[data-catalogue-type="short_story"]').click();assert.equal(await page.locator('.catalogue-card').count(),18);await page.locator('#catalogue-reset').click();assert.equal(await page.locator('.catalogue-card').count(),44);
  await page.locator('.catalogue-discovery').evaluate(node=>node.scrollIntoView());await screenshot('concepts-desktop');
  await page.locator('.kira-guide [data-inspect-world]').click();await page.locator('#inspect-dialog[open]').waitFor();assert.equal(await page.locator('#inspect-dialog [data-start-entry]').count(),0);await page.locator('#close-inspector').click();
  await page.locator('[data-resume-campaign="'+host.id+'"]').click();await page.waitForFunction(id=>current?.id===id&&view==='story'&&!loadingCampaign,host.id);
  const layout=await page.evaluate(()=>Object.fromEntries(['context-panel','content','play-tools'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return[id,{x:r.x,width:r.width}]})));
  assert(layout['context-panel'].x<layout.content.x&&layout.content.x<layout['play-tools'].x);await screenshot('play-desktop');
  await page.locator('[data-reading-size="22"]').click();assert.equal(await page.evaluate(()=>preferences.fontSize),22);await page.locator('[data-reading-paper]').click();await page.reload();await page.waitForFunction(()=>current&&!loadingCampaign);assert.equal(await page.evaluate(()=>preferences.fontSize),22);
  await page.setViewportSize({width:390,height:844});await fits();await screenshot('play-mobile');
  await page.locator('#toggle-context').click();await page.locator('#toggle-tools').click();assert.equal(await page.locator('body').evaluate(node=>node.classList.contains('context-open')),false);assert.equal(await page.locator('#toggle-context').getAttribute('aria-expanded'),'false');await screenshot('tools-mobile');
  await page.keyboard.press('Escape');assert.equal(await page.locator('#toggle-tools').getAttribute('aria-expanded'),'false');assert.equal(await page.evaluate(()=>document.activeElement.id),'toggle-tools');
  assert.equal(posts.length,0);for(const original of originals)assert.equal(fs.readFileSync(original.path,'utf8'),original.bytes);
  await page.setViewportSize({width:1568,height:1000});await page.locator('[data-view="content-library"]').click();await page.waitForSelector('.catalogue-card');await page.locator('.historical-campaign [data-catalogue-preview="MC-01"]').click();
  await page.locator('#catalogue-start-select').selectOption('hyw-1415');await page.locator('#inspect-dialog [data-start-entry="hyw-1415"]').click();await page.locator('#create-dialog[open]').waitFor();
  await page.locator('#campaign-name').fill('Interface qualification fixture');await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===1&&!historicalLoading);await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===2&&!startingLoading);
  await page.locator('#new-character-name').fill('Will atte Wode');await page.locator('#new-character-background').fill('A user-declared background, retained for review.');await page.locator('[data-character-detail="guided"]').click();await page.locator('#character-origin').fill('A declared origin');await page.locator('[data-character-detail="quick"]').click();assert.equal(await page.locator('#new-character-background').inputValue(),'A user-declared background, retained for review.');await screenshot('character-desktop');
  await page.setViewportSize({width:390,height:844});assert(await page.locator('#create-dialog').evaluate(node=>node.scrollWidth<=node.clientWidth));await screenshot('character-mobile');
  await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===3);assert.equal(posts.length,0);await page.locator('#create-submit').click();await page.waitForFunction(()=>current?.name==='Interface qualification fixture'&&!busy&&!document.querySelector('#create-dialog').open);
  assert.equal(posts.length,1);assert(posts[0].url.endsWith('/api/create'));assert.equal(posts[0].body.character.name,'Will atte Wode');const created=await page.evaluate(()=>({id:current.id,revision:current.revision}));
  await page.setViewportSize({width:1568,height:1000});await screenshot('historical-play-desktop');await page.reload();await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,created.id);assert.equal(await page.evaluate(()=>current.revision),created.revision);
  for(const original of originals)assert.equal(fs.readFileSync(original.path,'utf8'),original.bytes);
  assert.equal(providerCalls,0);assert.deepEqual(external,[]);assert.deepEqual(errors,[]);assert(assets.some(asset=>asset.url.endsWith('.woff2')));assert(assets.some(asset=>asset.url==='/historical-landscape.jpg'));assert(assets.every(asset=>asset.status===200));assert(!(await page.content()).includes('PRIVATE_EVALUATOR_MARKER'));
  const report={status:'passed',desktop_width:1568,mobile_width:390,concepts:44,reading_preferences_survive_reload:true,drawers_escape_and_focus:true,reviewed_character_creation:true,posts_before_explicit_creation:0,explicit_creations:1,original_fixture_saves_unchanged:true,local_assets_only:true,provider_calls:providerCalls,browser_errors:errors.length,layout,assets};
  if(reportPath)fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,assets:assets.length}));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
