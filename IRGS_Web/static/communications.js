'use strict';
// Received attribution/terms only. No hidden roster, feasibility check or generated reply.
function communicationKey(suffix='draft'){return current?.actor_id?`irgs-communication-${suffix}:${current.id}:${current.actor_id}`:null;}
function communicationParticipant(packet,channel,recipient){return packet?.channels?.find(item=>item.channel_id===channel)?.participants.find(item=>item.actor_id===recipient);}
function communicationName(actor){return (current?.known_actors||[]).find(item=>item.id===actor)?.name||actor;}
function communicationTerms(terms){return facts({from:terms.from,to:terms.to,material:terms.material,quantity:terms.quantity,authority_reference:terms.authority_id});}
function communicationSourcesMarkup(packet){
 const sources=packet?.received_sources;if(!sources?.records?.length)return '<p class="note">No received evidence is supplied for this character.</p>';
 return `<details class="communication-sources"><summary>Received sources · ${esc(sources.total)} records${sources.truncated?' · latest records shown':''}</summary><p class="note">Original attribution and reception are separate. Testimony is not a confirmed fact or proof of current presence.</p>${sources.records.map(item=>`<article class="received-source"><h4>${esc(item.record_id)}</h4><span class="badge">${esc(item.status)}</span><p class="received-source-text">${esc(item.text)}</p>${facts({originator:item.originator||'Not supplied',source:item.source_ref||'Not supplied by this receipt',reception_source:item.receipt_source_ref,recorded_sequence:item.recorded_at,received_sequence:item.received_at,occurrence_time:item.occurrence_time??'Not established'})}</article>`).join('')}</details>`;
}
function communicationControlsMarkup(){
 if(workspaceMode!=='player'||!current?.actor_id)return '';
 const packet=current.communication_control;if(packet?.schema_version!=='irgs-communication-capabilities-1')return '';
 const participants=(packet.channels||[]).some(channel=>channel.participants.length),retained=readLocal(communicationKey('review'));
 return `<details class="panel communication-controls" ${retained||readLocal(communicationKey())?.intention?'open':''}><summary>Communication &amp; received sources</summary><p class="note">Selected local channels only. Participants come from received attribution; presence and authority are checked when you confirm. Speech time is unresolved; causal sequence is not elapsed seconds.</p>${participants?`<form id="communication-form"><label>Selected channel<select id="communication-channel">${packet.channels.map(channel=>`<option value="${esc(channel.channel_id)}">${esc(channel.channel_id)}</option>`).join('')}</select></label><label>Received participant<select id="communication-recipient"></select></label><p id="communication-attribution" class="note"></p><label>Structured command<select id="communication-command"></select></label><p id="communication-counter" class="note"></p><fieldset id="communication-terms" hidden><legend>Proposed transfer · use received references</legend><p class="note">These are proposed terms, not a stock reservation or proof of authority. Supply references you know; Core checks the actual rights and conserved goods.</p>${[['from','From account'],['to','To account'],['material','Material'],['quantity','Quantity'],['authority_id','Authority reference']].map(([key,title])=>`<label>${title}<input id="communication-term-${key}" ${key==='quantity'?'type="number" min="1" step="1" inputmode="numeric"':'type="text" maxlength="256"'}></label>`).join('')}</fieldset><label>Your exact words<textarea id="communication-intention" maxlength="4096" rows="4" required></textarea></label><p class="note">Words are testimony. Saying “I accept” under Speak accepts no offer. Choose the structured command separately.</p><button type="submit" class="quiet" id="review-communication">Review communication</button></form>`:'<p class="communication-unavailable note">No selected local participant is available from received attribution. This does not establish that nobody is present; no introduction or channel has been invented.</p>'}${(packet.offers||[]).map((offer,index)=>`<article class="received-offer"><h4>Received offer · ${esc(offer.offer_id)}</h4><p><strong>${esc(label(offer.status))}</strong> · ${esc(communicationName(offer.offerer))} → ${esc(communicationName(offer.recipient))}</p>${communicationTerms(offer.terms)}<p class="note">Last received status; current private stock and obligations are not inspected. Accept attempts the actual transfer. Decline, withdraw and supersede retain their separate meanings.</p>${facts({proposed_sequence:offer.proposed_at,received_sequence:offer.last_received_at,source:offer.source_refs.join(' · ')})}<div class="buttons">${offer.supported_commands.map(item=>`<button type="button" class="quiet" data-communication-offer="${index}" data-command="${esc(item.command)}">${esc(label(item.command))}</button>`).join('')}<button type="button" class="quiet" data-communication-receipt="${esc(offer.latest_request_id)}">Latest received message</button></div></article>`).join('')}${retained?'<button type="button" class="quiet" id="recover-communication-review">Recover reviewed communication</button><button type="button" class="quiet" id="dismiss-communication-review">Dismiss unaccepted review</button>':''}${communicationSourcesMarkup(packet)}</details>`;
}
function readCommunicationDraft(){
 const saved=readLocal(communicationKey())||{};
 return {...saved,channel_id:$('#communication-channel').value,recipient:$('#communication-recipient').value,
  command:$('#communication-command').value,intention:$('#communication-intention').value,
  terms:Object.fromEntries(['from','to','material','quantity','authority_id'].map(key=>[key,$('#communication-term-'+key).value]))};
}
function saveCommunicationDraft(){if($('#communication-form'))writeLocal(communicationKey(),readCommunicationDraft());}
function fillCommunicationDraft(saved){
 const packet=current.communication_control,channel=$('#communication-channel');
 if(packet.channels.some(item=>item.channel_id===saved.channel_id))channel.value=saved.channel_id;
 const participants=packet.channels.find(item=>item.channel_id===channel.value)?.participants||[],recipient=$('#communication-recipient');
 recipient.innerHTML=participants.map(item=>`<option value="${esc(item.actor_id)}">${esc(communicationName(item.actor_id))} · received attribution</option>`).join('');
 recipient.value=participants.some(item=>item.actor_id===saved.recipient)?saved.recipient:participants[0]?.actor_id||'';
 const participant=communicationParticipant(packet,channel.value,recipient.value),counter=packet.offers.find(item=>item.offer_id===saved.counter_to&&item.supported_commands.some(row=>row.command==='counteroffer')&&item.channel_id===channel.value&&item.offerer===recipient.value);
 const commands=[...(participant?.supported_commands||[]),...(counter?['counteroffer']:[])];
 $('#communication-command').innerHTML=commands.map(command=>`<option value="${esc(command)}">${esc(label(command))}</option>`).join('');
 $('#communication-command').value=commands.includes(saved.command)?saved.command:commands[0]||'';
 $('#communication-attribution').textContent=participant?'Received attribution from: '+participant.source_record_ids.join(', ')+'. Current presence is not certified.':'No received participant is selected.';
 $('#communication-counter').textContent=counter&&$('#communication-command').value==='counteroffer'?'Counteroffer to '+counter.offer_id+'. This proposes new terms and supersedes the original; it accepts neither.':'';
 const offering=['offer','counteroffer'].includes($('#communication-command').value);
 $('#communication-terms').hidden=!offering;
 for(const key of ['from','to','material','quantity','authority_id']){const input=$('#communication-term-'+key);input.value=saved.terms?.[key]??'';input.required=offering;input.disabled=!offering;}
 $('#communication-intention').value=saved.intention||'';
 syncCommunicationControls();
}
function syncCommunicationControls(){
 const blocked=busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||Boolean(transportPending)||Boolean(soloAttempt)||Boolean(current?.pending_declaration)||current?.character_available===false;
 document.querySelectorAll('[data-communication-offer],#review-communication,#recover-communication-review').forEach(button=>button.disabled=blocked);
 if($('#communication-form'))$('#review-communication').disabled=blocked||!$('#communication-intention').value.trim()||!$('#communication-recipient').value;
}
function validCommunicationReview(review){
 const packet=current?.communication_control,request=review.packet;
 if(soloAttempt||packet?.view_token!==request.view_token||request.actor!==current.actor_id||!['prepared','save_failed'].includes(request.status))return false;
 const participant=communicationParticipant(packet,request.channel_id,request.recipient);if(!participant)return false;
 if(['speak','offer'].includes(request.command))return participant.supported_commands.includes(request.command);
 const offer=packet.offers.find(item=>item.offer_id===(request.command==='counteroffer'?request.details.counter_to:request.details.offer_id));
 return Boolean(offer&&offer.channel_id===request.channel_id&&offer.supported_commands.some(item=>item.command===request.command)&&(request.command==='counteroffer'?participant.supported_commands.includes('offer'):offer.terms_digest===request.details.terms_digest));
}
function showCommunicationReview(packet,request){
 if(packet.status==='completed_successfully'){writeLocal(communicationKey('review'),null);return finishAction({endpoint:'communication/execute',body:{id:packet.campaign_id,actor:packet.actor}},packet);}
 if(!['prepared','save_failed'].includes(packet.status)){writeLocal(communicationKey('review'),null);notice('This reviewed communication is '+String(packet.status)+'. Review a fresh request.',true);return;}
 soloReview={source:'communication',campaign:current.id,actor:current.actor_id,revision:packet.revision,request,text:packet.intention,id:packet.request_id,packet};
 if(!reviewActionValid()){soloReview=null;notice('The reviewed communication is stale. Reload and review a fresh request.',true);return;}
 $('#action-review-title').textContent='Review communication: '+label(packet.command);
 $('#action-review-description').textContent='To '+communicationName(packet.recipient)+' via '+packet.channel_id+'. Exact words remain testimony. '+(['offer','counteroffer'].includes(packet.command)?'This proposes the reviewed terms; no transfer or acceptance occurs.':packet.command==='accept'?'This explicitly attempts the received transfer; success is fulfilled.':'Only this structured command is submitted.');
 const offer=current.communication_control.offers.find(item=>item.offer_id===packet.details.offer_id),terms=packet.details.terms||offer?.terms;
 $('#communication-reviewed-details').hidden=!terms;$('#communication-reviewed-details').innerHTML=terms?'<h3>Reviewed transfer terms</h3>'+communicationTerms(terms)+facts({offer_reference:packet.details.offer_id,counter_to:packet.details.counter_to||'None'}):'';
 $('#action-review-intent').value=packet.intention;$('#action-review-dialog').showModal();syncActionReview();
}
async function prepareCommunication(command,recipient,channel,details,intention){
 if(busy||loadingCampaign||workspaceMode!=='player'||view!=='story'||!current?.actor_id||current.pending_declaration||transportPending||soloAttempt)return;
 const campaign=current.id,actor=current.actor_id,request=campaignRequest,storage=communicationKey('review');
 const body={id:campaign,actor,revision:current.revision,view_token:current.communication_control.view_token,
  request_id:crypto.randomUUID(),command,recipient,channel_id:channel,details,intention};
 invalidateActionReview();writeLocal(storage,{body});setBusy(true);let packet;
 try{packet=await api('communication/prepare',body,{creator:false});}catch(error){notice(error.message,true);}finally{setBusy(false);}
 if(current?.id===campaign&&current?.actor_id===actor&&campaignRequest===request){if(packet)showCommunicationReview(packet,request);else renderStory();}
}
function prepareCommunicationForm(){
 saveCommunicationDraft();const draft=readCommunicationDraft();let details={};
 if(['offer','counteroffer'].includes(draft.command)){
  const value=draft.terms.quantity;if(!/^\d+$/.test(value)||!Number.isSafeInteger(Number(value))||Number(value)<=0){notice('Enter a positive whole quantity.',true);return;}
  details={terms:{...draft.terms,quantity:Number(value)},...(draft.command==='counteroffer'?{counter_to:draft.counter_to}:{})};
 }
 return prepareCommunication(draft.command,draft.recipient,draft.channel_id,details,draft.intention);
}
async function chooseCommunicationOffer(index,command){
 if(busy||transportPending||soloAttempt||current?.pending_declaration)return;
 const offer=current.communication_control?.offers[index];if(!offer?.supported_commands.some(item=>item.command===command))return;
 const other=offer.offerer===current.actor_id?offer.recipient:offer.offerer;
 if(command==='counteroffer'){
  if(!$('#communication-form'))return;saveCommunicationDraft();const saved=readLocal(communicationKey())||{};
  const draft={...saved,channel_id:offer.channel_id,recipient:other,command,counter_to:offer.offer_id,
   terms:{from:offer.terms.to,to:offer.terms.from,material:offer.terms.material,quantity:String(offer.terms.quantity),authority_id:''}};
  writeLocal(communicationKey(),draft);fillCommunicationDraft(draft);$('#communication-intention').focus();return;
 }
 const draft=readLocal(communicationKey())||{},words=draft.intention||'';
 if(!words.trim()){notice('Write your exact words in the communication form before reviewing this command.',true);$('#communication-intention')?.focus();return;}
 return prepareCommunication(command,other,offer.channel_id,{offer_id:offer.offer_id,terms_digest:offer.terms_digest},words);
}
async function recoverCommunicationReview(){
 if(busy||transportPending||soloAttempt||workspaceMode!=='player'||view!=='story')return;
 const saved=readLocal(communicationKey('review')),request=campaignRequest;if(!saved?.body)return;
 const body=saved.body;setBusy(true);let packet;
 try{try{packet=await api('communication/status',{id:body.id,actor:body.actor,request_id:body.request_id},{creator:false});}
  catch(error){if(error.status!==400&&error.status!==404)throw error;packet=await api('communication/prepare',body,{creator:false});}}
 catch(error){notice(error.message,true);}finally{setBusy(false);}
 if(current?.id===body.id&&current?.actor_id===body.actor&&campaignRequest===request&&packet)showCommunicationReview(packet,request);
}
function keepCommunicationDraft(){
 const draft=readLocal(communicationKey())||{};writeLocal(communicationKey(),{...draft,intention:$('#action-review-intent').value});writeLocal(communicationKey('review'),null);invalidateActionReview();renderStory();$('#communication-intention')?.focus();notice('Your edited communication draft is kept. Review it again before submitting.');
}
async function submitCommunication(review){
 if(current?.id!==review.campaign||current?.actor_id!==review.actor||!validCommunicationReview(review))return;
 writeLocal(communicationKey('review'),null);stashDraft();const pending={endpoint:'communication/execute',body:{id:review.campaign,actor:review.actor,request_id:review.packet.request_id,explicitly_accepted:true}};storeTransport(pending);await deliverAction(pending);
}
async function inspectCommunication(requestId){
 const campaign=current?.id,actor=current?.actor_id,request=campaignRequest,inspect=++inspectorRequest;
 $('#inspect-title').textContent='Received communication';$('#inspect-content').innerHTML='<p>Loading the received record…</p>';$('#inspect-dialog').showModal();
 try{const result=await api('communication/received/'+encodeURIComponent(campaign)+'/'+encodeURIComponent(requestId)+'?actor_id='+encodeURIComponent(actor),undefined,{creator:false});
  if(current?.id!==campaign||current?.actor_id!==actor||campaignRequest!==request||inspect!==inspectorRequest||!$('#inspect-dialog').open)return;
  $('#inspect-content').innerHTML=`<h3>${esc(label(result.status))} · original received message</h3><p class="received-source-text">${esc(result.utterance)}</p>${facts({speaker:result.actor,recipient:result.recipient,words_status:result.truth_status,recorded_sequence:result.at,received_sequence:result.received_at,elapsed_status:result.elapsed_status})}${result.terms?communicationTerms(result.terms):''}<p class="note">This original receipt does not change when a later message closes an offer.</p>`;
 }catch(error){if(inspect===inspectorRequest&&$('#inspect-dialog').open)$('#inspect-content').textContent=error.message;}
}
function bindCommunicationControls(){
 if($('#communication-form')){
  fillCommunicationDraft(readLocal(communicationKey())||{});
  $('#communication-form').onsubmit=event=>{event.preventDefault();return prepareCommunicationForm();};
  for(const id of ['communication-channel','communication-recipient','communication-command'])$('#'+id).onchange=()=>{saveCommunicationDraft();fillCommunicationDraft(readLocal(communicationKey())||{});};
  for(const id of ['communication-intention',...['from','to','material','quantity','authority_id'].map(key=>'communication-term-'+key)])$('#'+id).oninput=()=>{saveCommunicationDraft();syncCommunicationControls();};
 }
 document.querySelectorAll('[data-communication-offer]').forEach(button=>button.onclick=()=>chooseCommunicationOffer(Number(button.dataset.communicationOffer),button.dataset.command));
 document.querySelectorAll('[data-communication-receipt]').forEach(button=>button.onclick=()=>inspectCommunication(button.dataset.communicationReceipt));
 if($('#recover-communication-review'))$('#recover-communication-review').onclick=recoverCommunicationReview;
 if($('#dismiss-communication-review'))$('#dismiss-communication-review').onclick=()=>{writeLocal(communicationKey('review'),null);renderStory();};
 syncCommunicationControls();
}
