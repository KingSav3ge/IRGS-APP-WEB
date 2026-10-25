'use strict';
// Starts and received commands come from Engine capabilities. No clock tick or inferred work.
function processReviewKey(){return current?.actor_id?`irgs-process-review:${current.id}:${current.actor_id}`:null;}
function processControlsMarkup(){
  if(workspaceMode!=='player'||!current?.actor_id)return '';
  const packet=current.process_control,rows=packet?.processes||[],starts=packet?.start_options||[],pending=readLocal(processReviewKey());
  if(!rows.length&&!starts.length&&!pending)return '';
  return `<section class="panel process-controls" aria-label="Your continuing processes"><h3>Your continuing processes</h3><p class="note">Last received progress. Commands check current Engine rules when confirmed; elapsed work advances only by an explicit submission.</p>${starts.length?`<div class="process-starts"><h4>Begin a continuing action</h4><p class="note">These are attempts under your selected rules. Starting schedules a process; it does not complete its work.</p>${starts.map((option,index)=>`<button type="button" class="quiet" data-process-start="${index}">Begin: ${esc(option.title)}</button>`).join('')}</div>`:''}${rows.map((item,index)=>{const r=item.received;return `<article><h4>${esc(label(r.kind))} · ${esc(label(r.status))}</h4><p>${esc(r.summary)}</p><p>${esc(r.worked_seconds)} seconds worked · ${esc(r.remaining_seconds)} seconds remaining at this receipt.</p><p class="note">${esc(r.original_intention)}</p>${item.commands.includes('advance')?`<label>Requested elapsed seconds <input type="number" min="1" step="1" inputmode="numeric" data-process-seconds="${index}" aria-label="Requested elapsed seconds"></label>`:''}<div class="buttons">${item.commands.map(command=>`<button type="button" class="quiet" data-process-command="${index}" data-command="${command}">${esc(label(command))}</button>`).join('')}</div></article>`;}).join('')}${pending?'<button type="button" class="quiet" id="recover-process-review">Recover reviewed process command</button>':''}</section>`;
}
function validProcessReview(review){
  if(soloAttempt||current?.process_control?.view_token!==review.packet.view_token)return false;
  if(review.packet.command==='start')return (current.process_control.start_options||[]).some(item=>item.capability_id===review.packet.capability_id);
  return current.process_control.processes.some(item=>item.received.process_id===review.packet.process_id&&item.commands.includes(review.packet.command));
}
function showProcessReview(packet,request){
  if(packet.status!=='prepared'&&packet.status!=='save_failed')return;
  soloReview={source:'process',campaign:current.id,actor:current.actor_id,revision:packet.revision,
    request,text:packet.intention,id:packet.process_id,packet};
  if(!reviewActionValid()){soloReview=null;notice('This reviewed process command is stale. Reload and review a fresh command.',true);return;}
  $('#action-review-title').textContent='Review process command: '+label(packet.command);
  $('#action-review-description').textContent='Confirm this exact command. Core will check current control, location and rules. A completed phase can leave the process unfinished.';
  $('#action-review-intent').value=packet.intention;$('#action-review-dialog').showModal();syncActionReview();
}
async function prepareProcessPhase(index,command){
  if(busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current?.actor_id||current.pending_declaration||transportPending||soloAttempt)return;
  const starting=command==='start',item=starting?current.process_control?.start_options?.[index]:current.process_control?.processes[index];if(!item||(!starting&&!item.commands.includes(command)))return;
  const details={};if(command==='advance'){const value=document.querySelector(`[data-process-seconds="${index}"]`).value;if(!/^\d+$/.test(value)||!Number.isSafeInteger(Number(value))||Number(value)<=0){notice('Enter a positive whole number of elapsed seconds to request.',true);return;}details.seconds=Number(value);}
  const campaign=current.id,actor=current.actor_id,request=campaignRequest,storage=processReviewKey();
  const body={id:campaign,actor,revision:current.revision,view_token:current.process_control.view_token,
    request_id:crypto.randomUUID(),command,
    ...(starting?{capability_id:item.capability_id}:{process_id:item.received.process_id,details}),
    intention:starting?`Begin: ${item.title}.`:command==='advance'?`Advance this process by ${details.seconds} seconds.`:`${label(command)} this process.`};
  invalidateActionReview();writeLocal(storage,{body});setBusy(true);let packet;
  try{packet=await api('process/prepare',body,{creator:false});}
  catch(error){notice(error.message,true);}finally{setBusy(false);}
  if(current?.id===campaign&&current?.actor_id===actor&&campaignRequest===request){if(packet)showProcessReview(packet,request);else renderStory();}
}
async function recoverProcessReview(){
  if(busy||transportPending||soloAttempt||workspaceMode!=='player'||view!=='story')return;
  const storage=processReviewKey(),saved=readLocal(storage),request=campaignRequest;if(!saved?.body)return;
  const body=saved.body;setBusy(true);let packet;
  try{packet=await api('process/status',{id:body.id,actor:body.actor,request_id:body.request_id},{creator:false});}
  catch(error){if(error.status===400)writeLocal(storage,null);notice(error.message,true);}finally{setBusy(false);}
  if(current?.id!==body.id||current?.actor_id!==body.actor||campaignRequest!==request)return;
  if(packet?.status==='completed_successfully'){writeLocal(storage,null);return finishAction({endpoint:'process/execute',body},packet);}
  if(packet?.status==='stale'||packet?.status==='rejected'){writeLocal(storage,null);notice('This phase is '+packet.status+'. Review a fresh command.',true);return;}
  if(packet)showProcessReview(packet,request);
}
function bindProcessControls(){
  document.querySelectorAll('[data-process-start]').forEach(button=>button.onclick=()=>prepareProcessPhase(Number(button.dataset.processStart),'start'));
  document.querySelectorAll('[data-process-command]').forEach(button=>button.onclick=()=>prepareProcessPhase(Number(button.dataset.processCommand),button.dataset.command));
  if($('#recover-process-review'))$('#recover-process-review').onclick=recoverProcessReview;
}
async function submitProcessPhase(review){
  if(current?.id!==review.campaign||current?.actor_id!==review.actor||!validProcessReview(review))return;
  const pending={endpoint:'process/execute',body:{id:review.campaign,actor:review.actor,
    request_id:review.packet.request_id,explicitly_accepted:true}};
  writeLocal(processReviewKey(),null);stashDraft();storeTransport(pending);await deliverAction(pending);
}
