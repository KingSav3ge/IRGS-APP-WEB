'use strict';
// Presentation port of the user-supplied Emergent preview. Every record here
// comes from the existing local host; these controls supply no simulation rules.
function previewIcon(kind){
  const paths={arrow:'M5 19 19 5M5 5h14v14',download:'M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4',book:'M12 5v16M3 3l9 2 9-2v16l-9 2-9-2Z',clock:'M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',person:'M4 21v-3a8 8 0 0 1 16 0v3M16 6a4 4 0 1 1-8 0 4 4 0 0 1 8 0'};
  return `<svg class="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="${paths[kind]||paths.arrow}"/></svg>`;
}
function previewJourneyShelf(){
  const campaigns=Array.isArray(campaignSummaries)?campaignSummaries:[];
  return `<section class="journey-shelf" aria-labelledby="journey-shelf-title"><div class="journey-shelf-heading"><h3 id="journey-shelf-title">Your stories</h3><div class="journey-tabs"><span aria-current="page">Active</span><button type="button" class="text-link" data-preview-view="trash">Trash</button></div></div><div class="journey-grid">${campaigns.map(campaign=>`<article class="journey-card"><span class="journey-portrait" aria-hidden="true">${esc(String(campaign.name||'?').trim().charAt(0).toUpperCase())}</span><div><h4>${esc(campaign.name)}</h4><p class="note">Saved campaign${Number.isSafeInteger(campaign.revision)?' · revision '+esc(campaign.revision):''}</p><button type="button" class="text-link" data-resume-campaign="${esc(campaign.id)}">Continue story ${previewIcon('arrow')}</button></div></article>`).join('')||'<div class="journey-empty"><p>Your first story is waiting to be written.</p><span>Choose a reviewed starting point below.</span></div>'}</div></section>`;
}
function bindPreviewJourneys(){
  document.querySelectorAll('[data-preview-view]').forEach(button=>button.onclick=()=>changeView(button.dataset.previewView));
  document.querySelectorAll('[data-resume-campaign]').forEach(button=>button.onclick=async()=>{
    if(busy||loadingCampaign)return;
    const navigation=inspectorRequest,mode=workspaceMode;
    try{const loaded=await openCampaign(button.dataset.resumeCampaign);if(loaded&&navigation===inspectorRequest&&mode===workspaceMode)changeView('story');}
    catch(error){notice(error.message,true);}
  });
}
function renderPreviewSaves(){
  $('#content').innerHTML=`<section class="library-page-heading"><span class="eyebrow">YOUR SAVED WORLDS</span><h2>Every story has<br>a place to return to.</h2><p>Continue a saved campaign or recover a journey from Trash.</p></section>${previewJourneyShelf()}<section class="save-explanation"><h3>Your progress, kept.</h3><p>Accepted actions and their original results are saved together. Returning to a story keeps its recorded consequences.</p><button class="quiet" type="button" data-preview-view="trash">Open Campaign Trash</button></section>`;
  bindPreviewJourneys();
}
function renderPreviewHome(){
  $('#content').innerHTML=`<section class="preview-landing" aria-labelledby="landing-title"><div class="landing-story"><p class="eyebrow">INTERACTIVE ROLEPLAYING GAME SYSTEMS</p><p class="landing-era">1415 · BEFORE DEPARTURE</p><h2 id="landing-title">The Lancastrian<br>Invasion</h2><p class="landing-line">A moment in history. A life to make your own. What comes next is yours to attempt.</p><span class="landing-rule" aria-hidden="true"></span><p class="art-caption">Illustrative landscape · campaign reference</p></div><div class="landing-invitation"><a class="landing-wordmark" href="#/home"><span aria-hidden="true">⬡</span> IRGS</a><h3>Do you have a journey to return to? Or are you setting about your first?</h3><p>Your world, kept on this device.</p><div class="landing-actions"><button id="home-library" type="button" class="primary">Begin a story</button><button id="home-resume" type="button" class="quiet">${current?'Return to your story':'Your saved stories'}</button></div></div><a class="landing-scroll" href="#what-irgs-does">SCROLL · WHAT IRGS DOES ${previewIcon('download')}</a></section><section id="what-irgs-does" class="landing-features"><article>${previewIcon('person')}<h3>Your own character</h3><p>Choose a reviewed starting point and find your place in its world.</p></article><article>${previewIcon('arrow')}<h3>Choices with consequences</h3><p>Review a listed action, confirm your attempt, and keep its actual outcome.</p></article><article>${previewIcon('book')}<h3>A lasting chronicle</h3><p>Return to the events, testimony and records your character has received.</p></article><article>${previewIcon('arrow')}<h3>Pick up your story</h3><p>Continue a saved world, with its history and unfinished decisions intact.</p></article></section><footer class="landing-colophon"><p>“Nothing beyond this moment has been decided.”</p><span>IRGS · LOCAL SOLO · CORE 3.3</span></footer>`;
  $('#home-library').onclick=()=>changeView('content-library');
  $('#home-resume').onclick=()=>changeView(current?'story':'saves');
}
function previewInventoryMarkup(){
  const inventory=current.settlement?current.settlement.inventory:current.inventory||current.world?.inventory;
  const items=rows(inventory);
  return items.length?`<ul class="side-record-list">${items.map(item=>`<li>${esc(item.name||item.item||item.material||item.title||item.id||'Recorded item')}${Number.isFinite(item.quantity)?` <span>× ${esc(item.quantity)}</span>`:Number.isFinite(item.qty)?` <span>× ${esc(item.qty)}</span>`:''}</li>`).join('')}</ul>`:'<p class="note">No belongings are established in this view.</p>';
}
function renderPreviewContext(){
  if(!current){$('#context-content').innerHTML='<p class="note">Open a story to see your character and received records.</p>';return;}
  const character=current.character,known=rows(current.known_actors).filter(actor=>actor.id!==character?.id);
  const initials=String(character?.name||'?').trim().split(/\s+/).slice(0,2).map(part=>Array.from(part)[0]).join('').toUpperCase();
  const conditions=character?.current||{},orders=rows(current.orders),obligations=rows(current.world?.obligations);
  $('#context-content').innerHTML=`<section class="character-card"><div class="character-identity"><div class="character-sigil" aria-hidden="true">${esc(initials)}</div><div><h2>${esc(character?.name||'Choose a character')}</h2><p>${esc(character?.species||'Your saved world')}</p></div></div></section><section class="world-clock-card"><h3 class="eyebrow">World clock</h3><p class="world-clock-value">${previewIcon('clock')} ${esc(displayTime()||'Time not established')}</p>${current.campaign_time?.calendar?`<p class="clock-precision">${esc(label(current.campaign_time.calendar))} calendar${current.campaign_time.precision?' · '+esc(current.campaign_time.precision)+' precision':''}</p>`:''}${current.scene?.location?`<p class="character-place"><span aria-hidden="true">⌖</span> ${esc(valueText(current.scene.location))}</p>`:''}</section>${Object.keys(conditions).length?`<section class="character-current"><h3 class="eyebrow">Character records</h3>${facts(conditions)}</section>`:''}<section><h3 class="eyebrow">Inventory</h3>${previewInventoryMarkup()}<button class="text-link" type="button" data-inspect="inventory">Inspect belongings</button></section>${known.length?`<section><h3 class="eyebrow">Known figures</h3><ul class="known-figures">${known.map(actor=>`<li><strong>${esc(actor.name||actor.id)}</strong>${actor.role?`<small>${esc(actor.role)}</small>`:''}</li>`).join('')}</ul></section>`:''}${orders.length?`<section><h3 class="eyebrow">Received orders</h3>${orders.map(order=>`<p>${esc(order.content||order.text||order.description||'Received order')}<small>${order.executed?'Recorded as executed':'Received · not yet executed'}</small></p>`).join('')}</section>`:''}${obligations.length?`<section><h3 class="eyebrow">Your commitments</h3>${obligations.map(item=>`<p>${esc(item.description||item.title||item.id)}<small>${esc(item.status||'status unknown')}</small></p>`).join('')}</section>`:''}<div class="character-links"><button type="button" class="quiet" data-inspect="character">Character details</button><button type="button" class="quiet" data-inspect="map">Known places</button></div>`;
  bindInspectors();
}
function previewReadingControls(){
  return `<div class="quick-reading" aria-label="Reading preferences"><span aria-hidden="true">T</span>${[['S',16],['M',18],['L',22]].map(([title,size])=>`<button type="button" data-reading-size="${size}" aria-label="${title==='S'?'Small':title==='M'?'Medium':'Large'} reading text" aria-pressed="${preferences.fontSize===size}">${title}</button>`).join('')}<button type="button" data-reading-paper aria-label="Switch reading surface" title="Switch reading surface">${preferences.theme==='parchment'?'Paper':preferences.theme==='light'?'Light':'Dark'}</button></div>`;
}
function previewRecentText(entry){
  const text=String(entry.text??entry.declaration??entry.assertion??'');
  // The received record may contain the user's structured background account.
  // Keep its testimony status visible without putting serialization in the sidebar.
  try{const record=JSON.parse(text);if(record?.schema_version===1&&record.kind==='character_background')return 'Your background account was recorded as testimony.';}catch{}
  return text.slice(0,180);
}
function renderPreviewTools(){
  const target=$('#play-tools-content');if(!target)return;
  const active=current&&!loadingCampaign&&workspaceMode==='player'&&['story','world','chronicle'].includes(view);
  $('#play-tools').hidden=!active;$('#toggle-tools').hidden=!active;
  $('#preview-owner-name').textContent=workspaceMode==='creator'?'Creator workspace':current?.character?.name||'Local Solo';
  $('#preview-owner-initial').textContent=workspaceMode==='creator'?'C':String(current?.character?.name||'L').charAt(0).toUpperCase();
  document.querySelectorAll('[data-preview-feature]').forEach(button=>{button.hidden=!features.some(feature=>feature.id===button.dataset.previewFeature&&featureAllowed(feature));button.onclick=()=>navigateFeature(button.dataset.previewFeature);});
  const reading=$('#story-reading-controls');if(reading)reading.innerHTML=previewReadingControls();
  if(!active){target.innerHTML='';document.body.classList.remove('tools-open');return;}
  const recent=storyEntries().slice(-5).reverse(),assistance=current.assistance;
  target.innerHTML=`<section class="tools-section"><h3 class="eyebrow">Your reading room</h3><p class="tools-intro">Make room for the story.</p><button type="button" class="quiet wide" data-open-reading>Reading settings ${previewIcon('arrow')}</button></section><section class="tools-section"><h3 class="eyebrow">Optional assistance</h3><div class="assistance-badge"><span class="dot" aria-hidden="true"></span>${assistance?.available===true?'Available for reviewed requests':'Local responses'}</div><p class="note">${assistance?.available===true?'Review a proposal in your response composer before accepting an action.':'Read your saved results and choose a listed action. No model is needed for local play.'}</p></section><section class="tools-section"><h3 class="eyebrow">Saves &amp; your story</h3><p class="note">Accepted actions and results are saved together.</p><button type="button" class="quiet wide" data-preview-export>Export known view ${previewIcon('download')}</button><button type="button" class="text-link" data-preview-view="saves">${previewIcon('arrow')} Your saved journeys</button><button type="button" class="text-link" data-preview-view="chronicle">${previewIcon('book')} Open the full Chronicle</button><button type="button" class="text-link" data-preview-view="trash">Recover a story from Trash</button></section><section class="tools-section"><h3 class="eyebrow">Recent chronicle</h3>${recent.length?`<ol class="recent-chronicle">${recent.map(entry=>`<li><span>${esc(entry.title||label(entry.kind||'record'))}</span><p>${esc(previewRecentText(entry))}</p></li>`).join('')}</ol>`:'<p class="note">The records you receive will appear here.</p>'}</section>`;
  bindPreviewJourneys();
  document.querySelectorAll('[data-open-reading]').forEach(button=>button.onclick=openSettings);
  document.querySelectorAll('[data-preview-export]').forEach(button=>button.onclick=()=>$('#export').click());
  document.querySelectorAll('[data-reading-size]').forEach(button=>button.onclick=()=>{preferences.fontSize=Number(button.dataset.readingSize);applyPreferences();renderPreviewTools();});
  document.querySelectorAll('[data-reading-paper]').forEach(button=>button.onclick=()=>{preferences.theme=preferences.theme==='dark'?'parchment':preferences.theme==='parchment'?'light':'dark';applyPreferences();renderPreviewTools();});
}
function syncPreviewCharacter(){
  const name=$('#new-character-name')?.value.trim()||'Your character',species=$('#new-character-species')?.value.trim()||'human';
  const box=$('#character-portrait-name');if(!box)return;
  const kind=$('#character-kind').value,existing=kind!=='new',person=rows(startingOptions?.characters||startingOptions?.entities?.characters).find(item=>item.id===(kind==='faction'?$('#faction-representative').value:$('#starting-character').value));
  const title=existing?(person?.name||'A reviewed character'):name;
  box.textContent=title;$('#character-portrait-monogram').textContent=String(title).charAt(0).toUpperCase();
  $('#character-preview-kind').textContent=existing?'Existing character':'A new character';$('#character-preview-species').textContent=existing?'Reviewed character records':species;
  document.querySelectorAll('[data-new-character-note]').forEach(item=>item.hidden=existing);
}
function bindPreviewControls(){
  $('#preview-account').onclick=()=>$('#toggle-nav').click();
  $('#toggle-tools').onclick=()=>{document.body.classList.remove('context-open');$('#toggle-context').setAttribute('aria-expanded','false');const open=document.body.classList.toggle('tools-open');$('#toggle-tools').setAttribute('aria-expanded',String(open));if(open)$('#close-tools').focus();};
  $('#close-tools').onclick=()=>{document.body.classList.remove('tools-open');$('#toggle-tools').setAttribute('aria-expanded','false');$('#toggle-tools').focus();};
  document.querySelectorAll('[data-character-detail]').forEach(button=>button.onclick=()=>{const guided=button.dataset.characterDetail==='guided';$('#guided-background').open=guided;document.querySelectorAll('[data-character-detail]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));if(guided)$('#character-origin').focus();});
  for(const id of ['new-character-name','new-character-species'])$('#'+id).addEventListener('input',syncPreviewCharacter);
}
