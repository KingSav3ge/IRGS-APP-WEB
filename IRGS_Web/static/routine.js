'use strict';
const responseViewSession=crypto.randomUUID();
function routineFrame(id,values={},event={}){
  const definition=AppResponses.library.families.find(family=>family.id===id);
  if(!definition)throw new Error('Unknown App response');
  return {actor_id:event.actor??current?.actor_id??'local-user',
    snapshot_id:JSON.stringify([responseViewSession,event.campaign??current?.id??'host',event.actor??current?.actor_id??'local-user',event.revision??current?.revision??0,campaignRequest,workspaceMode]),
    source_ref:event.ref??('app:'+String(event.campaign??current?.id??'host')+':'+id),
    source_kind:definition.source_kind,state:definition.state,values};
}
function routineText(id,values={},event={},variant){
  try{return AppResponses.render(id,routineFrame(id,values,event),variant);}
  catch{return AppResponses.render('ui.unavailable',routineFrame('ui.unavailable'),0);}
}
function routineRecipe(id,values={},event={}){
  try{
    const recipe=AppResponses.library.recipes.find(recipe=>recipe.id===id);
    if(!recipe)throw new Error('Unknown App recipe');
    const shared={...event,ref:event.ref??('app:'+String(current?.id??'host')+':'+id)};
    const ids=[...recipe.required,...recipe.optional.filter(key=>Object.prototype.hasOwnProperty.call(values,key))];
    return AppResponses.composeRecipe(id,Object.fromEntries(ids.map(key=>[key,routineFrame(key,values[key]??{},shared)])));
  }catch{return routineText('ui.unavailable');}
}
function routineOutcome(result,{elapsed=false,next=false,presentation=false}={}){
  const text=result?.outcome?.summary;
  if(typeof text!=='string')return routineText('result.saved');
  if(!['completed_successfully','completed_unsuccessfully'].includes(result.status))return text;
  const prepared=result.presentation;
  if(presentation&&prepared?.format==='plain_text'&&prepared.actor_id===result.actor&&prepared.source_ref===result.receipt?.event_id&&typeof prepared.text==='string'&&prepared.text.startsWith(text))return prepared.text;
  const event={actor:result.actor??current?.actor_id??'local-user',campaign:result.campaign_id??current?.id,
    revision:result.revision??current?.revision,ref:result.receipt?.event_id??result.request_id??'public:committed-result'};
  const contexts={'receipt.exact':routineFrame('receipt.exact',{receipt_text:text},event)};
  const seconds=result.elapsed_time?.duration_seconds;
  if(elapsed&&Number.isSafeInteger(seconds)&&seconds>=0)contexts['elapsed.action']=routineFrame('elapsed.action',{elapsed_seconds:seconds},event);
  if(next)contexts['decision.next']=routineFrame('decision.next',{},event);
  const recipe=contexts['elapsed.action']?'result.elapsed':next?'result.next':'result.exact';
  try{return AppResponses.composeRecipe(recipe,contexts);}catch{return text;}
}
function availableRoutineDrafts(){
  const own=AppResponses.library.families.filter(family=>family.role==='draft').map(family=>({id:family.id,title:family.title,text:routineText(family.id)}));
  const packet=current?.local_responses,scope=packet?.scope;
  if(packet?.schema_version!==1||scope?.campaign_id!==current?.id||scope?.actor_id!==current?.actor_id||scope?.revision!==current?.revision||typeof scope.view_id!=='string'||!Array.isArray(packet.drafts))return own;
  const seen=new Set(own.map(draft=>draft.id));
  for(const draft of packet.drafts.slice(0,64)){
    if(!draft||typeof draft.id!=='string'||!['catalog','engine'].includes(draft.source)||!draft.id.startsWith(draft.source+':')||seen.has(draft.id)||typeof draft.title!=='string'||typeof draft.text!=='string'||!draft.text.trim()||draft.requires_explicit_submission!==true||draft.automatic_execution!==false)continue;
    seen.add(draft.id);own.push({...draft,projection_view:scope.view_id});
  }
  return own;
}
function renderRoutineDrafts(player){
  const region=$('#local-drafts');
  region.hidden=!player||!current?.actor_id||current.character_available===false;
  if(region.hidden)return;
  const campaign=current.id,actor=current.actor_id,revision=current.revision,request=campaignRequest;
  const disabled=busy||current.pending_declaration||transportPending||soloAttempt||!current.capabilities?.can_declare;
  $('#local-draft-options').innerHTML=availableRoutineDrafts().map(family=>'<button type="button" class="quiet" data-local-draft="'+esc(family.id)+'" '+(disabled?'disabled':'')+'>'+esc(family.title)+'</button>').join('');
  document.querySelectorAll('[data-local-draft]').forEach(button=>button.onclick=()=>{
    if(current?.id!==campaign||current?.actor_id!==actor||current?.revision!==revision||campaignRequest!==request||$('#campaign').value!==campaign||workspaceMode!=='player'||view!=='story'||busy||disabled)return;
    reviewRoutineDraft(button.dataset.localDraft);
  });
}
function reviewRoutineDraft(id){
  const definition=availableRoutineDrafts().find(family=>family.id===id);
  if(!definition)return;
  invalidateActionReview();
  soloReview={source:'local-draft',campaign:current?.id,actor:current?.actor_id,revision:current?.revision,request:campaignRequest,
    id,text:definition.text,projection_view:definition.projection_view};
  if(!reviewActionValid()){invalidateActionReview();return;}
  $('#action-review-title').textContent=definition.title;
  $('#action-review-description').textContent='These are starting words for your own response. They establish no facts, permission, elapsed time or outcome.';
  $('#action-review-intent').value=soloReview.text;$('#action-review-dialog').showModal();syncActionReview();
}
