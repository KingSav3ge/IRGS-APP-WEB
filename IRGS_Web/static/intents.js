'use strict';
// Engine-supplied capabilities; selecting words never silently selects an action.
function intentReviewKey(){return current?.actor_id?`irgs-intent-review:${current.id}:${current.actor_id}`:null;}
function syncIntentControls(){
 const panel=$('#intent-tools'),select=$('#intent-capability'),button=$('#review-intent'),recover=$('#recover-intent-review');
 if(!panel||!select||!button||!recover)return;
 const packet=current?.intent_control,player=workspaceMode==='player'&&view==='story'&&current?.actor_id&&packet?.schema_version==='irgs-shared-runtime-1';
 panel.hidden=!player;if(!player)return;
 const scope=current.id+':'+current.actor_id+':'+packet.view_token;
 if(select.dataset.scope!==scope){
  select.dataset.scope=scope;select.innerHTML='<option value="">Choose an action to review…</option>'+(packet.capabilities||[]).map(cap=>`<option value="${esc(cap.capability_id)}">${esc(cap.title)}${cap.operation_id==='record_player_action'?' · unresolved':''}</option>`).join('');select.value='';
 }
 const blocked=busy||loadingCampaign||Boolean(transportPending)||Boolean(soloAttempt)||Boolean(current.pending_declaration)||current.character_available===false;
 button.disabled=blocked||!select.value||!$('#declaration').value.trim()||$('#declaration').value.length>4096;
 recover.hidden=!readLocal(intentReviewKey());recover.disabled=blocked;
}
function validIntentReview(review){
 const packet=current?.intent_control,cap=review.packet.capability;
 return !soloAttempt&&packet?.view_token===review.packet.view_token&&review.packet.actor===current.actor_id&&
  ['prepared','save_failed'].includes(review.packet.status)&&packet.capabilities.some(item=>item.capability_id===cap.capability_id&&item.operation_id===cap.operation_id&&JSON.stringify(item.action)===JSON.stringify(cap.action));
}
function showIntentReview(packet,request){
 if(['completed_successfully','completed_unsuccessfully','declared_not_resolved'].includes(packet.status)){
  writeLocal(intentReviewKey(),null);return finishAction({endpoint:'intent/execute',body:{id:packet.campaign_id,actor:packet.actor}},packet);
 }
 if(!['prepared','save_failed'].includes(packet.status)){writeLocal(intentReviewKey(),null);notice('This reviewed response is '+String(packet.status)+'. Review it again.',true);syncIntentControls();return;}
 soloReview={source:'intent',campaign:current.id,actor:current.actor_id,revision:packet.revision,request,text:packet.intention,id:packet.request_id,packet};
 if(!reviewActionValid()){soloReview=null;notice('This reviewed response is stale. Reload and review again.',true);return;}
 const cap=packet.capability,action=Object.entries(cap.action||{}).map(([key,value])=>key+': '+String(value)).join(' · ');
 const received=(current.settlement?.actions||[]).find(item=>item.id===cap.action?.action_id)||(current.supported_actions||[]).find(item=>item.action_id===cap.action?.action_id);
 const place=current.settlement?.location||current.scene?.location;
 $('#action-review-title').textContent='Review: '+cap.title;
 $('#action-review-description').textContent='Character: '+(current.character?.name||current.actor_id)+' · Place: '+(typeof place==='string'?place:'Not supplied')+'. Selected operation: '+cap.operation_id+(action?' · '+action:'')+'. Sources: '+(cap.source_refs||[]).join(', ')+'. '+(cap.operation_id==='record_player_action'?'This records unresolved intent; it does not resolve an action.':(received?.description||'No further timing or requirements were supplied for review.')+' Core checks current control, location, rules and resources when submitted.');
 $('#action-review-intent').value=packet.intention;$('#action-review-dialog').showModal();syncActionReview();
}
async function prepareIntent(){
 if(busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current?.actor_id||current.pending_declaration||transportPending||soloAttempt)return;
 const selected=$('#intent-capability').value,cap=current.intent_control?.capabilities.find(item=>item.capability_id===selected),words=$('#declaration').value;
 if(!cap||!words.trim())return;
 const campaign=current.id,actor=current.actor_id,request=campaignRequest,storage=intentReviewKey();
 const body={id:campaign,actor,revision:current.revision,view_token:current.intent_control.view_token,
  request_id:crypto.randomUUID(),intention:words,capability_id:cap.capability_id};
 invalidateActionReview();stashDraft();writeLocal(storage,{body});setBusy(true);let packet;
 try{packet=await api('intent/prepare',body,{creator:false});}catch(error){notice(error.message,true);}finally{setBusy(false);}
 if(current?.id===campaign&&current?.actor_id===actor&&campaignRequest===request){if(packet)showIntentReview(packet,request);syncIntentControls();}
}
async function recoverIntentReview(){
 if(busy||transportPending||soloAttempt||workspaceMode!=='player'||view!=='story')return;
 const saved=readLocal(intentReviewKey()),request=campaignRequest;if(!saved?.body)return;
 const body=saved.body;setBusy(true);let packet;
 try{try{packet=await api('intent/status',{id:body.id,actor:body.actor,request_id:body.request_id},{creator:false});}
  catch(error){if(error.status!==400&&error.status!==404)throw error;packet=await api('intent/prepare',body,{creator:false});}}
 catch(error){notice(error.message,true);}finally{setBusy(false);}
 if(current?.id===body.id&&current?.actor_id===body.actor&&campaignRequest===request&&packet)showIntentReview(packet,request);
}
function keepIntentDraft(){
 $('#declaration').value=$('#action-review-intent').value;stashDraft();writeLocal(intentReviewKey(),null);invalidateActionReview();syncComposer();focusOwnResponse();notice('Your edited response is kept. Review it again before submitting.');
}
async function submitIntent(review){
 if(current?.id!==review.campaign||current?.actor_id!==review.actor||!validIntentReview(review))return;
 writeLocal(intentReviewKey(),null);stashDraft();const pending={endpoint:'intent/execute',body:{id:review.campaign,actor:review.actor,request_id:review.packet.request_id,explicitly_accepted:true}};storeTransport(pending);await deliverAction(pending);
}
function bindIntentControls(){
 $('#review-intent').onclick=prepareIntent;$('#recover-intent-review').onclick=recoverIntentReview;
 $('#intent-capability').onchange=syncIntentControls;
}
