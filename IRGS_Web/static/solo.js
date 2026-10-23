'use strict';
let soloReview=null,assistanceStatusRequest=0;

function reviewActionValid(){
  if(!soloReview||!soloReview.actor||busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current||$('#campaign').value!==current.id||current.id!==soloReview.campaign||current.actor_id!==soloReview.actor||current.revision!==soloReview.revision||campaignRequest!==soloReview.request||current.pending_declaration||transportPending||current.character_available===false)return false;
  const available=soloReview.source==='rise'?current.settlement?.actions||[]:supportedActions();
  return available.some(action=>soloReview.source==='rise'?action.id===soloReview.id&&action.title===soloReview.text:action.kind===soloReview.kind&&action[action.kind==='scene_action'?'action_id':'order_id']===soloReview.id&&action.text===soloReview.text);
}
function invalidateActionReview(){soloReview=null;if($('#action-review-dialog').open)$('#action-review-dialog').close();}
function reviewSupportedAction(action,campaign,actor,source='supported'){
  if(!action)return;
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
  $('#confirm-reviewed-action').disabled=!exact;
  $('#keep-action-draft').disabled=!$('#action-review-intent').value.trim();
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
  const action=soloReview;invalidateActionReview();
  if(action.source==='rise')return submitRiseAction(action.id,action.campaign,action.actor);
  return submitSupportedAction(action.id,action.campaign,action.actor,action.kind,action.text);
}
function bindSoloControls(){
  $('#cancel-reviewed-action').onclick=invalidateActionReview;
  $('#action-review-dialog').addEventListener('cancel',invalidateActionReview);
  $('#action-review-dialog').addEventListener('close',()=>{if(!$('#action-review-dialog').open)soloReview=null;});
  $('#action-review-intent').oninput=syncActionReview;
  $('#keep-action-draft').onclick=keepReviewedDraft;
  $('#confirm-reviewed-action').onclick=confirmReviewedAction;
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
