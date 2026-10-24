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
function routineOutcome(result,{elapsed=false,next=false}={}){
  const text=result?.outcome?.summary;
  if(typeof text!=='string')return routineText('result.saved');
  if(!['completed_successfully','completed_unsuccessfully'].includes(result.status))return text;
  const event={actor:result.actor??current?.actor_id??'local-user',campaign:result.campaign_id??current?.id,
    revision:result.revision??current?.revision,ref:result.receipt?.event_id??result.request_id??'public:committed-result'};
  const contexts={'receipt.exact':routineFrame('receipt.exact',{receipt_text:text},event)};
  const seconds=result.elapsed_time?.duration_seconds;
  if(elapsed&&Number.isSafeInteger(seconds)&&seconds>=0)contexts['elapsed.action']=routineFrame('elapsed.action',{elapsed_seconds:seconds},event);
  if(next)contexts['decision.next']=routineFrame('decision.next',{},event);
  const recipe=contexts['elapsed.action']?'result.elapsed':next?'result.next':'result.exact';
  try{return AppResponses.composeRecipe(recipe,contexts);}catch{return text;}
}
function renderRoutineDrafts(player){
  const region=$('#local-drafts');
  region.hidden=!player||!current?.actor_id||current.character_available===false;
  if(region.hidden)return;
  const campaign=current.id,actor=current.actor_id,revision=current.revision,request=campaignRequest;
  const disabled=busy||current.pending_declaration||transportPending||soloAttempt||!current.capabilities?.can_declare;
  $('#local-draft-options').innerHTML=AppResponses.library.families.filter(family=>family.role==='draft').map(family=>'<button type="button" class="quiet" data-local-draft="'+esc(family.id)+'" '+(disabled?'disabled':'')+'>'+esc(family.title)+'</button>').join('');
  document.querySelectorAll('[data-local-draft]').forEach(button=>button.onclick=()=>{
    if(current?.id!==campaign||current?.actor_id!==actor||current?.revision!==revision||campaignRequest!==request||$('#campaign').value!==campaign||workspaceMode!=='player'||view!=='story'||busy||disabled)return;
    reviewRoutineDraft(button.dataset.localDraft);
  });
}
function reviewRoutineDraft(id){
  const definition=AppResponses.library.families.find(family=>family.id===id&&family.role==='draft');
  if(!definition)return;
  invalidateActionReview();
  soloReview={source:'local-draft',campaign:current?.id,actor:current?.actor_id,revision:current?.revision,request:campaignRequest,
    id,text:routineText(id)};
  if(!reviewActionValid()){invalidateActionReview();return;}
  $('#action-review-title').textContent=definition.title;
  $('#action-review-description').textContent='These are starting words for your own response. They establish no facts, permission, elapsed time or outcome.';
  $('#action-review-intent').value=soloReview.text;$('#action-review-dialog').showModal();syncActionReview();
}
