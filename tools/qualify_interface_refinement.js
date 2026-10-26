'use strict';
// Real canonical host, three supported contexts, temporary synthetic saves only.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{chromium}=require('playwright');

async function readingContrast(page){
 return page.evaluate(()=>{
  const context=document.createElement('canvas').getContext('2d');
  const rgba=color=>{context.clearRect(0,0,1,1);context.fillStyle=color;context.fillRect(0,0,1,1);return [...context.getImageData(0,0,1,1).data];};
  const luminance=rgb=>rgb.slice(0,3).map(n=>{n/=255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4;}).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);
  return [...document.querySelectorAll('.story-reading,.story-reading .eyebrow,.story-reading .note,.story-reading .quiet,.story-reading summary,.story-reading a,.opening-elapsed,.quick-reading button,.quick-reading span')].filter(node=>!node.disabled&&node.getClientRects().length).map(node=>{
   let parent=node,background;
   while(parent){background=rgba(getComputedStyle(parent).backgroundColor);if(background[3]===255)break;parent=parent.parentElement;}
   const foreground=rgba(getComputedStyle(node).color),a=luminance(foreground),b=luminance(background);
   return {element:node.tagName+'.'+node.className,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
  });
 });
}

(async()=>{
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'irgs-interface-refinement-')),metadata=path.join(folder,'host.json');
 const child=spawn('python3',['-B',path.join(__dirname,'solo_browser_host.py'),metadata,'shared'],{stdio:['ignore','ignore','pipe']});
 let stderr='',browser;child.stderr.on('data',data=>stderr+=data);
 const reportPath=process.argv[2],screenshots=process.argv[3];if(screenshots)fs.mkdirSync(screenshots,{recursive:true});
 try{
  const deadline=Date.now()+20000;
  while(!fs.existsSync(metadata)){if(child.exitCode!==null||Date.now()>deadline)throw Error('Synthetic host failed: '+stderr);await new Promise(resolve=>setTimeout(resolve,50));}
  const host=JSON.parse(fs.readFileSync(metadata)),originals=host.contexts.map(context=>({path:context.save,bytes:fs.readFileSync(context.save,'utf8')}));
  browser=await chromium.launch({executablePath:process.env.IRGS_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1568,height:1000}}),origin='http://127.0.0.1:'+host.port;
  const posts=[],errors=[],external=[],evidence=[],paletteChecks=[];let providerCalls=0;
  page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(request.method()==='POST')posts.push({url:request.url(),body:request.postDataJSON()});});
  await page.route('**/*',async route=>{const url=route.request().url();if(!url.startsWith(origin+'/')){external.push(url);return route.abort();}if(/\/api\/ai\/(proposal|accept)/.test(url)){providerCalls++;return route.abort();}return route.continue();});
  const capture=async name=>{if(screenshots){await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(screenshots,name+'.png')});}};
  const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const unchanged=()=>originals.forEach(record=>assert.equal(fs.readFileSync(record.path,'utf8'),record.bytes));
  await page.goto(origin);await page.waitForFunction(()=>current&&!loadingCampaign);

  // Review and cancellation remain separate from the only explicit creation.
  async function characterSetup(){
   await page.locator('[data-view="content-library"]').first().click();await page.waitForSelector('.catalogue-card');
   assert.equal(await page.locator('.catalogue-card').count(),44);
   await page.locator('.historical-campaign [data-catalogue-preview="MC-01"]').click();
   await page.locator('#catalogue-start-select').selectOption('hyw-1415');await page.locator('#inspect-dialog [data-start-entry="hyw-1415"]').click();
   await page.locator('#create-dialog[open]').waitFor();await page.locator('#campaign-name').fill('Interface refinement historical');
   await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===1&&!historicalLoading);
   await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===2&&!startingLoading);
   await page.locator('#new-character-name').fill('Rowan atte Wode');
   await page.locator('#new-character-background').fill('My declared background, retained for review.');
   await page.locator('[data-character-detail="guided"]').click();await page.locator('#character-origin').fill('A declared origin');
   await page.locator('[data-character-detail="quick"]').click();assert.equal(await page.locator('#new-character-background').inputValue(),'My declared background, retained for review.');
  }
  await characterSetup();await page.locator('#cancel-create').click();assert.equal(posts.length,0);unchanged();
  await characterSetup();await page.locator('#setup-next').click();await page.waitForFunction(()=>wizardStep===3);
  assert(/testimony/i.test(await page.locator('#setup-review').innerText()));assert.equal(posts.length,0);unchanged();
  await page.locator('#confirm-declaration-start').check();await page.locator('#create-submit').click();await page.waitForFunction(()=>current?.name==='Interface refinement historical'&&!busy&&!document.querySelector('#create-dialog').open);
  assert.equal(posts.length,1);assert(posts[0].url.endsWith('/api/create'));
  const created=await page.evaluate(()=>({id:current.id,revision:current.revision}));
  const createdSave=path.join(path.dirname(host.contexts[0].save),created.id+'.json'),createdBytes=fs.readFileSync(createdSave,'utf8');
  const contexts=[...host.contexts.map(context=>({name:context.name,id:context.id,save:context.save})),{name:'historical_start',id:created.id,save:createdSave}];

  for(const context of contexts){
   await page.setViewportSize({width:1568,height:1000});await page.locator('[data-view="story"]').first().click();
   await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption(context.id);
   await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);await fits();
   const before=fs.readFileSync(context.save,'utf8'),revision=await page.evaluate(()=>current.revision),surfaces=[];
   for(const [surface,size] of [['dark',18],['light',20],['parchment',22]]){
    await page.locator('[data-open-reading]').click();await page.locator('#preferences-dialog[open]').waitFor();
    await page.locator('[name="theme"]').selectOption(surface);await page.locator('[name="fontSize"]').focus();await page.keyboard.press('Home');
    for(let value=16;value<size;value++)await page.keyboard.press('ArrowRight');
    await page.locator('#close-settings').click();assert(await page.evaluate(()=>document.activeElement.matches('[data-open-reading]')));
    const toolbar=await page.evaluate(()=>({size:preferences.fontSize,surface:preferences.theme,label:document.querySelector('[data-reading-paper]').textContent,
     pressed:[...document.querySelectorAll('[data-reading-size]')].filter(node=>node.getAttribute('aria-pressed')==='true').map(node=>Number(node.dataset.readingSize)),description:document.querySelector('.quick-reading').getAttribute('aria-label')}));
    assert.equal(toolbar.size,size);assert.equal(toolbar.surface,surface);assert.equal(toolbar.label,surface==='parchment'?'Paper':surface==='light'?'Light':'Dark');
    assert.deepEqual(toolbar.pressed,[16,18,22].includes(size)?[size]:[]);assert(toolbar.description.includes(size+' px'));
    const contrast=await readingContrast(page);assert(contrast.length>0);for(const item of contrast)assert(item.ratio>=4.5,context.name+' '+surface+' '+JSON.stringify(item));
    await page.setViewportSize({width:390,height:844});await fits();
    const mobileContrast=await readingContrast(page);for(const item of mobileContrast)assert(item.ratio>=4.5,context.name+' mobile '+surface+' '+JSON.stringify(item));
    if(surface==='parchment')await capture(context.name+'-parchment-mobile');
    surfaces.push({surface,size,widths_checked:[1568,390],minimum_contrast:Math.min(...[...contrast,...mobileContrast].map(item=>item.ratio))});
    await page.setViewportSize({width:1568,height:1000});
   }
   await page.locator('[data-open-reading]').click();await page.locator('[name="fontSize"]').focus();await page.keyboard.press('End');await page.locator('#close-settings').click();
   assert.equal(await page.evaluate(()=>preferences.fontSize),26);await page.setViewportSize({width:390,height:844});await fits();
   assert(await page.locator('#content').evaluate(node=>node.scrollWidth<=node.clientWidth));await capture(context.name+'-largest-text-mobile');await page.setViewportSize({width:1568,height:1000});
   const medium=page.locator('[data-reading-size="18"]');await medium.focus();await page.keyboard.press('Enter');
   assert(await page.evaluate(()=>document.activeElement===document.querySelector('[data-reading-size="18"]')));assert.equal(await page.evaluate(()=>preferences.fontSize),18);
   const paper=page.locator('[data-reading-paper]');await paper.focus();await page.keyboard.press('Enter');
   assert(await page.evaluate(()=>document.activeElement===document.querySelector('[data-reading-paper]')));
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);const draft='My unsent '+context.name+' draft.';await page.locator('#declaration').fill(draft);
   await page.setViewportSize({width:390,height:844});await fits();await capture(context.name+'-mobile');
   await page.locator('#toggle-tools').click();await page.locator('#toggle-nav').click();
   assert(await page.evaluate(()=>document.body.classList.contains('nav-open')&&!document.body.classList.contains('tools-open')&&!document.body.classList.contains('context-open')));
   await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.id),'toggle-nav');
   await page.locator('#toggle-nav').click();await page.locator('#toggle-context').click();
   assert(await page.evaluate(()=>document.body.classList.contains('context-open')&&!document.body.classList.contains('nav-open')));
   assert.equal(await page.evaluate(()=>document.activeElement.id),'close-context');await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.id),'toggle-context');
   await page.locator('#toggle-tools').click();await page.locator('[data-open-reading]').click();await page.keyboard.press('Escape');
   assert.equal(await page.locator('#preferences-dialog').evaluate(node=>node.open),false);assert(await page.evaluate(()=>document.activeElement.matches('[data-open-reading]')));
   await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.id),'toggle-tools');
   await page.locator('#toggle-tools').click();await page.locator('#play-tools [data-preview-view="chronicle"]').click();await page.waitForFunction(()=>view==='chronicle');
   assert.equal(await page.evaluate(()=>document.activeElement.id),'content');assert.equal(await page.locator('#toggle-tools').getAttribute('aria-expanded'),'false');
   await page.locator('#tab-chronicle').focus();await page.keyboard.press('Home');assert.equal(await page.evaluate(()=>view),'story');assert.equal(await page.evaluate(()=>document.activeElement.id),'tab-story');
   await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>view),'world');assert.equal(await page.evaluate(()=>document.activeElement.id),'tab-world');
   await page.keyboard.press('End');assert.equal(await page.evaluate(()=>view),'chronicle');await page.locator('#tab-story').click();
   await page.locator('#own-response-panel').evaluate(node=>node.open=true);assert.equal(await page.locator('#declaration').inputValue(),draft);
   await page.setViewportSize({width:1568,height:1000});await capture(context.name+'-desktop');await page.reload();
   await page.waitForFunction(id=>current?.id===id&&!loadingCampaign,context.id);assert.equal(await page.evaluate(()=>current.revision),revision);
   assert.equal(await page.evaluate(()=>preferences.fontSize),18);assert.equal(await page.locator('[data-reading-paper]').textContent(),'Light');
   assert.equal(fs.readFileSync(context.save,'utf8'),before);assert.equal(posts.length,1);
   evidence.push({context:context.name,reading_surfaces:surfaces,toolbar_synchronized:true,quick_button_focus_preserved:true,maximum_size_mobile:26,exclusive_drawers:true,nested_escape_returns_focus:true,destination_focus:true,primary_tab_keyboard:true,draft_and_reload_preserved:true,save_unchanged:true});
  }

  // Synthetic palette labels qualify color portability only, not new mechanics.
  const originalPalette=await page.evaluate(()=>({genre:document.body.dataset.genre,campaign:document.body.dataset.campaignTheme}));
  for(const genre of ['military','roman','fantasy','paf','shinobi','space','settlement']){
   await page.evaluate(value=>{document.body.dataset.genre=value;document.body.dataset.campaignTheme='';},genre);
   for(const surface of ['dark','light','parchment']){
    await page.evaluate(value=>{preferences.theme=value;applyPreferences();},surface);
    const checks=await readingContrast(page);for(const item of checks)assert(item.ratio>=4.5,genre+' '+surface+' '+JSON.stringify(item));
    paletteChecks.push({genre,surface,minimum_contrast:Math.min(...checks.map(item=>item.ratio))});
   }
  }
  await page.evaluate(value=>{document.body.dataset.genre=value.genre;document.body.dataset.campaignTheme=value.campaign;},originalPalette);
  await page.locator('[data-view="saves"]').first().click();assert.equal(await page.locator('[data-resume-campaign]').count(),3);
  await page.locator('[data-preview-view="trash"]').first().click();await page.waitForFunction(()=>document.querySelector('#content').textContent.includes('Trash is empty.'));assert.equal(await page.locator('[data-restore]').count(),0);
  await page.locator('#toggle-nav').click();await page.locator('#workspace-mode').click();await page.waitForFunction(()=>workspaceMode==='creator'&&current?.state&&!loadingCampaign);
  assert.equal(await page.locator('body').getAttribute('data-mode'),'creator');await page.keyboard.press('Escape');
  await page.locator('#toggle-nav').click();await page.locator('#workspace-mode').click();await page.waitForFunction(()=>workspaceMode==='player'&&current?.mode==='player'&&!loadingCampaign);
  await page.keyboard.press('Escape');await page.locator('#campaign-management').evaluate(node=>node.open=true);await page.locator('#campaign').selectOption('');
  await page.waitForFunction(()=>current===null&&!loadingCampaign);assert.equal(await page.locator('#toggle-tools').isHidden(),true);assert.equal(await page.locator('#own-response-panel').isHidden(),true);
  await page.setViewportSize({width:390,height:844});await fits();await capture('empty-story-mobile');
  unchanged();assert.equal(fs.readFileSync(createdSave,'utf8'),createdBytes);assert.equal(posts.length,1);assert.equal(providerCalls,0);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  assert(!(await page.content()).includes('PRIVATE_EVALUATOR_MARKER'));
  const report={status:'passed',contexts:evidence,desktop_width:1568,mobile_width:390,palette_checks:paletteChecks,
   historical_setup_cancel_and_review:true,explicit_creations:1,reading_and_navigation_posts:0,empty_trash_and_story:true,creator_round_trip_read_only:true,
   original_fixture_saves_unchanged:true,local_assets_only:true,provider_calls:0,browser_errors:0};
  if(reportPath)fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,palette_checks:paletteChecks.length}));
 }finally{if(browser)await browser.close();if(child.exitCode===null){child.kill('SIGINT');await new Promise(resolve=>child.once('exit',resolve));}fs.rmSync(folder,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
