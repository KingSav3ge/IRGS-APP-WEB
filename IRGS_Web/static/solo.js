'use strict';
let soloReview=null,assistanceStatusRequest=0,soloAttempt=null,soloGeneration=0;

function reviewActionValid(){
  if(!soloReview||!soloReview.actor||busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current||$('#campaign').value!==current.id||current.id!==soloReview.campaign||current.actor_id!==soloReview.actor||current.revision!==soloReview.revision||campaignRequest!==soloReview.request||current.pending_declaration||transportPending||current.character_available===false)return false;
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
  $('#confirm-reviewed-action').disabled=!exact||soloReview.edited===true;
  $('#keep-action-draft').disabled=!$('#action-review-intent').value.trim();
  if(soloReview.source==='proposal'){$('#action-review-state').textContent=exact?'The proposal selects '+soloReview.id+'. Compare this action with your intention. Confirming executes the selected action; provider interpretation can be wrong.':'Editing invalidates this proposal. Keep these words as a draft and request a new review.';if(!exact){soloReview.edited=true;cancelSoloAttempt();}return;}
  $('#action-review-state').textContent=exact?'Nothing is submitted until you confirm. The action may fail when its current requirements are checked.':'Your edited words are an unsent draft. Keep them in your response, or restore the listed wording to confirm this exact action. Different freeform intent remains unresolved.';
}
function keepReviewedDraft(){
  if(!reviewActionValid())return invalidateActionReview();
  const draft=$('#action-review-intent').value;if(!draft.trim())return;
  $('#declaration').value=draft;stashDraft();invalidateActionReview();syncComposer();focusOwnResponse();
  notice('Your words are in the editable response. Nothing has been submitted.');
}
async function confirmReviewedAction(){
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
  $('#assistance-state').textContent=soloAttempt?(soloAttempt.status==='pending'?'Review requested. Nothing has been executed.':soloAttempt.status==='unknown'?'The proposal response is uncertain. Check the saved request; this does not start another provider attempt.':soloAttempt.status==='proposal_ready'?'Proposal ready for your review. Nothing has been executed.':'Assistance unavailable ('+(soloAttempt.result?.code||'unavailable')+'). Your draft is retained. Cancel this request before trying another.'):(current?.assistance?.message||'AI assistance is not connected. Listed actions remain available; freeform declarations remain unresolved.');
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
