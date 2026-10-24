'use strict';
// Presentation only. Use the public binding, never campaign names or hidden state.
function presentationTheme(binding={}){
  const genres=['military','roman','fantasy','paf','shinobi','space','settlement'];
  const genre=genres.includes(binding.genre_id)?binding.genre_id:'base';
  const campaign=binding.campaign_profile==='rise'?'rise':binding.scenario_id==='hundred-years-war'?'hundred-years-war':binding.campaign_profile==='ast'?'ast':'';
  return {genre,campaign};
}
function applyPresentationTheme(){
  // Application-wide pages keep the base identity even with a campaign loaded.
  const active=current&&!loadingCampaign&&(['story','world','chronicle','creator'].includes(view));
  const theme=presentationTheme(active?current.binding:undefined);
  document.body.dataset.genre=theme.genre;
  document.body.dataset.campaignTheme=theme.campaign;
}
