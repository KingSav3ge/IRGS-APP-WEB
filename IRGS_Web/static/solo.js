'use strict';
let soloReview=null,assistanceStatusRequest=0,soloAttempt=null,soloGeneration=0;

function reviewActionValid(){
  if(!soloReview||!soloReview.actor||busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current||$('#campaign').value!==current.id||current.id!==soloReview.campaign||current.actor_id!==soloReview.actor||current.revision!==soloReview.revision||campaignRequest!==soloReview.request||current.pending_declaration||transportPending||current.character_available===false)return false;
  if(soloReview.source==='local-draft')return current.capabilities?.can_declare===true&&availableRoutineDrafts().some(draft=>draft.id===soloReview.id&&draft.text===soloReview.text&&draft.projection_view===soloReview.projection_view);
  if(soloReview.source==='proposal')return (soloReview.edited||soloAttempt?.result?.proposal?.proposal_digest===soloReview.proposal.proposal_digest)&&(current.settlement?(current.settlement.actions||[]).some(action=>action.id===soloReview.id):supportedActions().some(action=>action.kind==='scene_action'&&action.action_id===soloReview.id));
  const available=soloReview.source==='rise'?current.settlement?.actions||[]:supportedActions();
  return available.some(action=>soloReview.source==='rise'?action.id===soloReview.id&&action.title===soloReview.text:action.kind===soloReview.kind&&action[action.kind==='scene_action'?'action_id':'order_id']===soloReview.id&&action.text===soloReview.text);
}
function invalidateActionReview(){invalidateSoloProposal();soloReview=null;if($('#action-review-dialog').open)$('#action-review-dialog').close();syncComposer();}
function reviewSupportedAction(action,campaign,actor,source='supported'){
  if(!action)return;invalidateActionReview();
  soloReview={source,campaign,actor,revision:current?.revision,request:campaignRequest,
    id:source==='rise'?action.id:action[action.kind==='scene_action'?'action_id':'order_id'],kind:action.kind,
    text:source==='rise'?action.title:action.text};
  if(!reviewActionValid()){soloReview=null;return;}
  $('#action-review-title').textContent=action.title||'Review your action';
  $('#action-review-description').textContent=action.description||'Review this listed action before submitting it. Availability and requirements are checked on submission.';
  $('#action-review-intent').value=soloReview.text;
  $('#action-review-dialog').showModal();syncActionReview();
}
function reviewRiseAction(id,campaign,actor){reviewSupportedAction(current?.settlement?.actions.find(action=>action.id===id),campaign,actor,'rise');}
function syncActionReview(){
  if(!soloReview)return;
  if(!reviewActionValid()){invalidateActionReview();return;}
  const exact=$('#action-review-intent').value===soloReview.text;
  const draft=soloReview.source==='local-draft';$('#confirm-reviewed-action').hidden=draft;
  if(draft){$('#confirm-reviewed-action').disabled=true;$('#keep-action-draft').disabled=!$('#action-review-intent').value.trim();$('#action-review-state').textContent=routineText('review.draft');return;}
  $('#confirm-reviewed-action').disabled=!exact||soloReview.edited===true;
  $('#keep-action-draft').disabled=!$('#action-review-intent').value.trim();
  if(soloReview.source==='proposal'){$('#action-review-state').textContent=exact?routineText('review.proposal',{action_id:soloReview.id}):routineText('review.proposal_edited');if(!exact){soloReview.edited=true;cancelSoloAttempt();}return;}
  $('#action-review-state').textContent=exact?routineRecipe('review.local'):routineText('review.edited');
}
function keepReviewedDraft(){
  if(!reviewActionValid())return invalidateActionReview();
  const draft=$('#action-review-intent').value;if(!draft.trim())return;
  if(soloReview.source==='local-draft')$('#local-drafts').open=false;
  $('#declaration').value=draft;stashDraft();invalidateActionReview();syncComposer();focusOwnResponse();
  notice(routineRecipe('draft.kept'));
}
async function confirmReviewedAction(){
  if(soloReview?.source==='local-draft')return;
  if(!reviewActionValid()||$('#action-review-intent').value!==soloReview.text)return invalidateActionReview();
  const action=soloReview;
  if(action.source==='proposal'){if(action.edited)return;soloAttempt=null;writeLocal(proposalKey(action),null);invalidateActionReview();const pending={endpoint:'ai/accept',body:{id:action.campaign,revision:action.revision,actor:action.actor,request_id:action.proposal.request_id,intention:action.text,proposal_digest:action.proposal.proposal_digest,explicitly_accepted:true}};stashDraft();storeTransport(pending);return deliverAction(pending);}
  invalidateActionReview();
  if(action.source==='rise')return submitRiseAction(action.id,action.campaign,action.actor);
  return submitSupportedAction(action.id,action.campaign,action.actor,action.kind,action.text);
}
function bindSoloControls(){
  $('#review-assisted-action').onclick=()=>requestSoloProposal(Boolean(soloAttempt));
  $('#cancel-assisted-action').onclick=()=>{invalidateActionReview();syncComposer();};
  if(typeof window!=='undefined')window.addEventListener('pagehide',()=>invalidateActionReview());
  $('#cancel-reviewed-action').onclick=invalidateActionReview;
  $('#action-review-dialog').addEventListener('cancel',invalidateActionReview);
  $('#action-review-dialog').addEventListener('close',()=>{if(!$('#action-review-dialog').open&&soloReview)invalidateActionReview();});
  $('#action-review-intent').oninput=syncActionReview;
  $('#keep-action-draft').onclick=keepReviewedDraft;
  $('#confirm-reviewed-action').onclick=confirmReviewedAction;
}
function proposalKey(action){return action?`irgs-proposal:${action.campaign||action.id}:${action.actor}`:null;}
function loadSoloAttempt(){
  const saved=current?readLocal(proposalKey({id:current.id,actor:current.actor_id})):null;
  soloAttempt=saved?.body?{body:saved.body,status:'unknown'}:null;
}
function cancelSoloAttempt(){
  const attempt=soloAttempt;soloAttempt=null;++soloGeneration;
  if(!attempt)return;
  writeLocal(proposalKey(attempt.body),null);
  const body={id:attempt.body.id,actor:attempt.body.actor,request_id:attempt.body.request_id};
  // Navigation/reload cancellation is a bounded host request, never inference.
  fetch('/api/ai/cancel',{method:'POST',headers:{'Content-Type':'application/json','X-IRGS-Token':token},body:JSON.stringify(body),keepalive:true}).catch(()=>{});
}
function invalidateSoloProposal(){cancelSoloAttempt();}
function syncAssistanceControls(){
  const player=workspaceMode==='player'&&view==='story'&&current&&!loadingCampaign;
  const available=current?.assistance?.available===true;
  const button=$('#review-assisted-action'),cancel=$('#cancel-assisted-action');
  button.hidden=!player||(!available&&!soloAttempt);cancel.hidden=!player||!soloAttempt;
  button.textContent=soloAttempt?'Check saved proposal':'Review with assistance';
  button.disabled=busy||!player||Boolean(transportPending)||Boolean(current?.pending_declaration)||current?.character_available===false||soloAttempt?.status==='pending'||(!soloAttempt&&(!$('#declaration').value.trim()||$('#declaration').value.length>4096));
  $('#assistance-state').textContent=soloAttempt?(soloAttempt.status==='pending'?routineText('proposal.pending'):soloAttempt.status==='unknown'?routineText('proposal.unknown'):soloAttempt.status==='proposal_ready'?routineText('proposal.ready'):routineText('proposal.unavailable',{code:String(soloAttempt.result?.code||'unavailable')})):(current?.assistance?.message||routineText('assistance.unconfigured'));
}
function soloReplyActive(attempt,generation){return soloAttempt===attempt&&soloGeneration===generation&&workspaceMode==='player'&&view==='story'&&!loadingCampaign&&current?.id===attempt.body.id&&current?.actor_id===attempt.body.actor&&current?.revision===attempt.body.revision&&$('#campaign').value===attempt.body.id&&$('#declaration').value===attempt.body.intention;}
async function requestSoloProposal(lookup=false){
  if(busy||workspaceMode!=='player'||view!=='story'||!current?.actor_id||transportPending||current.pending_declaration)return;
  if(!lookup){
    if(soloAttempt||!current.assistance?.available||!$('#declaration').value.trim()||$('#declaration').value.length>4096)return;
    stashDraft();soloAttempt={body:{id:current.id,revision:current.revision,actor:current.actor_id,request_id:crypto.randomUUID(),intention:$('#declaration').value},status:'pending'};
    writeLocal(proposalKey(soloAttempt.body),{body:soloAttempt.body});
  }
  const attempt=soloAttempt;if(!attempt)return;
  const generation=++soloGeneration;attempt.status='pending';syncComposer();
  try{
    const result=lookup?await api('ai/proposal-result/'+encodeURIComponent(attempt.body.id)+'/'+encodeURIComponent(attempt.body.request_id)+'?actor_id='+encodeURIComponent(attempt.body.actor)):await api('ai/proposal',attempt.body,{creator:false});
    if(!soloReplyActive(attempt,generation))return;
    if(['completed_successfully','completed_unsuccessfully'].includes(result.status)){cancelSoloAttempt();await openCampaign(attempt.body.id,{actorId:attempt.body.actor});return;}
    attempt.status=result.status;attempt.result=result;
    if(result.status==='proposal_ready'&&result.proposal?.intention===attempt.body.intention&&result.request_id===attempt.body.request_id&&result.campaign_id===attempt.body.id&&result.actor===attempt.body.actor&&result.revision===current.revision){
      const proposal=result.proposal;
      soloReview={source:'proposal',campaign:current.id,actor:current.actor_id,revision:current.revision,request:campaignRequest,id:proposal.action_id,text:proposal.intention,proposal};
      if(!reviewActionValid()){invalidateActionReview();return;}
      $('#action-review-title').textContent='Review proposed action';
      $('#action-review-description').textContent=(result.action?.text||result.action?.title||proposal.action_id)+'\nSources: '+(proposal.source_refs||[]).join(', ');
      $('#action-review-intent').value=proposal.intention;$('#action-review-dialog').showModal();syncActionReview();
    }
  }catch(error){if(soloReplyActive(attempt,generation))attempt.status='unknown';}
  finally{syncComposer();}
}
function assistanceStatusActive(){return workspaceMode==='creator'&&view==='feature:providers-models';}
let aiUsageRequest=0;
function aiUsageActive(){return workspaceMode==='creator'&&view==='feature:usage-budgets';}
function usageFacts(value,keys){return facts(Object.fromEntries(keys.map(key=>[key,value?.[key]??'Unknown'])));}
async function renderAIUsage(){
  if(!aiUsageActive())return;
  const request=++aiUsageRequest;
  $('#content').innerHTML='<section class="panel"><p>'+esc(routineText('usage.loading'))+'</p></section>';
  try{
    const result=await api('ai/usage',undefined,{creator:true});
    if(request!==aiUsageRequest||!aiUsageActive())return;
    const summary=result.summary,attempts=Array.isArray(result.attempts)?result.attempts:[];
    $('#content').innerHTML='<section class="panel"><span class="eyebrow">PROTECTED DEVELOPER RECORDS</span><h2>Usage &amp; Budgets</h2><p>Reservations are operator-defined ceiling units.</p><p>'+esc(routineRecipe('usage.local'))+'</p><p>'+esc(result.message||'Accounting unavailable.')+'</p>'+(summary?usageFacts(summary,['attempts_total','budget_units','reserved_units','held_units','known_charged_units','unknown_attempts','remaining_units','overrun_units','active_transport_slots','maximum_transport_slots','unfinished_or_in_doubt']):'<p>No assistance ledger is configured.</p>')+'<button class="quiet" id="retry-ai-usage">Refresh records</button></section>'+attempts.slice(0,50).map(attempt=>'<article class="panel"><h3>Attempt '+esc(attempt.request_id||'Unknown')+'</h3>'+usageFacts(attempt,['status','code','acceptance_recorded','reserved_units','billing_status','reviewed_charge_units','transport_state','transport_finished','usage_status'])+'<h4>Requested identity</h4>'+usageFacts(attempt.requested_identity,['developer','gateway','host','model','model_version'])+'<h4>Reported identity</h4>'+usageFacts(attempt.reported_identity,['developer','gateway','host','model','model_version'])+'<h4>Reported tokens</h4>'+usageFacts(attempt.reported_tokens,['input_tokens','output_tokens','cached_input_tokens','reasoning_tokens'])+'<p class="note">'+(attempt.billing_status==='operator_reconciled'?'Charge recorded from operator-reviewed evidence. ':'Actual charges: unknown. ')+esc(routineText('usage.read_only'))+'</p></article>').join('')+(result.has_more?'<p class="note">Showing recent attempts. Budget totals cover the entire ledger.</p>':'');
  }catch(error){
    if(request!==aiUsageRequest||!aiUsageActive())return;
    $('#content').innerHTML='<section class="panel"><h2>Accounting unavailable</h2><p>'+esc(error.message)+'</p><button class="quiet" id="retry-ai-usage">Retry records</button></section>';
  }
  $('#retry-ai-usage').onclick=renderAIUsage;
}
async function renderAssistanceStatus(){
  if(!assistanceStatusActive())return;
  const request=++assistanceStatusRequest;
  $('#content').innerHTML='<section class="panel"><p>Checking AI assistance…</p></section>';
  try{
    const result=await api('ai/status',undefined,{creator:true});
    if(request!==assistanceStatusRequest||!assistanceStatusActive())return;
    const details=result.diagnostics||{};
    $('#content').innerHTML='<section class="panel"><span class="eyebrow">DEVELOPER STATUS</span><h2>AI assistance</h2><p>'+esc(result.message||'AI assistance is unavailable.')+'</p>'+facts({status:result.status||'unavailable',provider_runtime:details.provider_runtime||'not_connected',dispatch_enabled:details.dispatch_enabled===true,model_evaluations:details.model_evaluations||'not_run'})+'<p class="note">Status inspection does not make a provider request or change a campaign. Provider setup, model qualification and live play remain separate.</p><button class="quiet" id="retry-assistance-status">Check again</button></section>';
  }catch(error){
    if(request!==assistanceStatusRequest||!assistanceStatusActive())return;
    $('#content').innerHTML='<section class="panel"><h2>AI assistance unavailable</h2><p>'+esc(error.message)+'</p><button class="quiet" id="retry-assistance-status">Retry status check</button></section>';
  }
  $('#retry-assistance-status').onclick=renderAssistanceStatus;
}
