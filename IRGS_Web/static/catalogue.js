'use strict';
// Product previews are out-of-character reference. Creation uses the existing
// reviewed entry workflows; a concept record supplies no simulation authority.
const CATALOGUE_TYPES={short_story:'Short Story',curated:'Curated Campaign',full:'Full Campaign',major:'Major Campaign',grand:'Grand Campaign',simulation_system:'Curated Simulation System'};
const CATALOGUE_SETTINGS={historical:'Historical',historical_inspired:'Historically inspired',contemporary_realism:'Contemporary realism',fictional:'Original fiction',fantasy:'Fantasy',science_fiction:'Science fiction',variable:'Configurable'};
const CATALOGUE_ERAS={ancient:'Ancient',medieval:'Medieval',early_modern:'Early modern',modern:'Modern',future:'Future',variable:'Multiple / unspecified'};
const CATALOGUE_SLATES={launch:'Launch target',future:'Future campaign',system:'Independent system'};
const CATALOGUE_STATUS={planned:'Planned',in_development:'In Development'};
let catalogueData=null,catalogueFilters={search:'',type:'',setting:'',era:'',genre:'',slate:'',availability:''};

function catalogueSelect(key,title,values){
  return `<label>${title}<select id="catalogue-${key}"><option value="">All</option>${Object.entries(values).map(([value,text])=>`<option value="${esc(value)}"${catalogueFilters[key]===value?' selected':''}>${esc(text)}</option>`).join('')}</select></label>`;
}
function campaignCatalogueMarkup(data){
  catalogueData=data;
  const portfolio=data.portfolio,counts=portfolio.counts;
  const genres=[...new Set(portfolio.entries.flatMap(e=>e.genres))].sort();
  return `<section class="catalogue-intro" aria-labelledby="catalogue-title"><span class="eyebrow">THE IRGS CAMPAIGN PORTFOLIO · v${esc(portfolio.version)}</span><h2 id="catalogue-title">Many worlds.<br>A place for your story.</h2><p>Explore personal stories, living communities and worlds that span civilizations.</p><div class="catalogue-totals"><span><strong>${esc(counts.launch)}</strong> launch targets</span><span><strong>${esc(counts.future)}</strong> future campaigns</span><span><strong>${esc(counts.systems)}</strong> simulation system</span><span><strong>${esc(counts.total)}</strong> concepts</span></div><p class="note">Launch targets describe the portfolio, not released games. ${esc(counts.free_launch_stories)} Short Stories are proposed to be free at launch. Settings and features remain working concepts.</p></section>
  ${catalogueAvailableMarkup(data)}
  <section class="catalogue-discovery" aria-labelledby="catalogue-browse-title"><div class="catalogue-section-heading"><div><span class="eyebrow">FIND AN EXPERIENCE</span><h3 id="catalogue-browse-title">Browse the catalogue</h3></div><button id="catalogue-reset" type="button" class="quiet">Reset filters</button></div>
  <div class="catalogue-filters"><label class="catalogue-search">Search titles, places, periods or roles<input id="catalogue-search" type="search" placeholder="Japan, merchant, 1700…" value="${esc(catalogueFilters.search)}"></label>${catalogueSelect('type','Campaign type',CATALOGUE_TYPES)}${catalogueSelect('setting','Setting',CATALOGUE_SETTINGS)}${catalogueSelect('era','Period',CATALOGUE_ERAS)}${catalogueSelect('genre','Genre',Object.fromEntries(genres.map(g=>[g,g])))}${catalogueSelect('slate','Portfolio',CATALOGUE_SLATES)}${catalogueSelect('availability','Availability',{available:'Available slice',upcoming:'Upcoming & in development'})}</div>
  <p id="catalogue-result-count" class="note" role="status" aria-live="polite"></p><div id="catalogue-results" class="catalogue-grid"></div></section>`;
}
function catalogueAvailableMarkup(data){
  const entries=data.portfolio.entries.filter(e=>e.available_slice);
  return `<section class="catalogue-available-section" aria-labelledby="catalogue-available-title"><span class="eyebrow">AVAILABLE TO PLAY</span><h3 id="catalogue-available-title">Start with a development slice</h3><p class="note">These reviewed starts offer limited mechanics. The complete campaigns remain in development.</p><div class="catalogue-available-grid">${entries.map(e=>`<article class="panel"><span class="eyebrow">${esc(e.catalogue_id)}</span><h3>${esc(e.current_display_title||e.title)}</h3><p>${esc(e.catalogue_id==='CSS-01'?'A fictional household founding story in Greywater Reach.':'Reviewed historical character starts, with optional authored local openings.')}</p><button type="button" class="primary" data-catalogue-preview="${esc(e.catalogue_id)}">Review available start</button></article>`).join('')||'<p class="note">No verified starting slice is currently available.</p>'}</div></section>`;
}
function filteredCatalogueEntries(){
  const f=catalogueFilters,terms=f.search.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  return (catalogueData?.portfolio?.entries||[]).filter(entry=>
    (!f.type||entry.campaign_type===f.type)&&(!f.setting||entry.setting_kind===f.setting)&&(!f.era||entry.era===f.era)&&
    (!f.genre||entry.genres.includes(f.genre))&&(!f.slate||entry.slate===f.slate)&&
    (!f.availability||(f.availability==='available'?entry.available_slice:!entry.available_slice))&&
    terms.every(term=>[entry.catalogue_id,entry.title,entry.current_display_title,entry.tagline,entry.geography,entry.period,entry.setting,entry.perspectives,...entry.genres,...entry.synopsis,...entry.featured_systems].filter(Boolean).join(' ').toLocaleLowerCase().includes(term)));
}
function catalogueCard(entry){
  const type=Object.hasOwn(CATALOGUE_TYPES,entry.campaign_type)?entry.campaign_type:'short_story';
  return `<article class="catalogue-card catalogue-${type}"><div class="catalogue-cover" aria-hidden="true"><span>${esc(entry.catalogue_id)}</span><span class="catalogue-cover-mark">${esc({short_story:'I',curated:'II',full:'III',major:'IV',grand:'V',simulation_system:'◇'}[type])}</span><span>${esc(CATALOGUE_TYPES[type])}</span></div><div class="catalogue-card-body"><div class="catalogue-card-meta"><span class="eyebrow">${esc(CATALOGUE_SLATES[entry.slate])}</span><span class="badge">${esc(CATALOGUE_STATUS[entry.development_status]||'Preview')}</span></div><h3>${esc(entry.title)}</h3><p class="catalogue-tagline">${esc(entry.tagline)}</p><p class="note">${esc(entry.geography)} · ${esc(entry.period)}</p><div class="catalogue-genres">${entry.genres.slice(0,3).map(g=>`<span>${esc(g)}</span>`).join('')}</div>${entry.available_slice?'<p class="catalogue-available">A limited playable slice is available</p>':'<p class="note">Preview only · unreleased</p>'}<button type="button" class="quiet" data-catalogue-preview="${esc(entry.catalogue_id)}" aria-label="Preview ${esc(entry.title)}">Explore preview <span aria-hidden="true">→</span></button></div></article>`;
}
function renderCatalogueResults(){
  if(!$('#catalogue-results'))return;
  const entries=filteredCatalogueEntries();
  $('#catalogue-result-count').textContent=`${entries.length} of ${catalogueData.portfolio.entries.length} concepts · previews do not start a campaign`;
  $('#catalogue-results').innerHTML=entries.length?entries.map(catalogueCard).join(''):'<div class="empty catalogue-no-results"><h3>No matching concepts</h3><p>Try a different period, place or role, or reset the filters.</p></div>';
  document.querySelectorAll('[data-catalogue-preview]').forEach(button=>button.onclick=()=>inspectCatalogueConcept(button.dataset.cataloguePreview));
}
function bindCampaignCatalogue(){
  for(const key of Object.keys(catalogueFilters)){
    const control=$('#catalogue-'+key);if(!control)continue;
    control[key==='search'?'oninput':'onchange']=()=>{catalogueFilters[key]=control.value;renderCatalogueResults();};
  }
  $('#catalogue-reset').onclick=()=>{for(const key of Object.keys(catalogueFilters)){catalogueFilters[key]='';$('#catalogue-'+key).value='';}renderCatalogueResults();$('#catalogue-search').focus();};
  renderCatalogueResults();
}
function catalogueCurrentAccess(entry){
  // Match only the three existing canonical discovery identities. Never treat
  // availability, a title, pricing or a concept's status as permission to launch.
  const identity={'MC-01':'hundred-years-war','GC-01':'world-of-kira','CSS-01':'rise'}[entry.catalogue_id];
  const current=(catalogueData.campaigns||[]).find(c=>c.id===identity);
  if(!current)return '<p class="reference-note">Preview only. A playable starting state is not available for this concept.</p>';
  if(entry.catalogue_id==='MC-01'){
    const starts=libraryEntries({campaigns:[current]}).filter(e=>e.ready===true&&verifiedLibraryEntry(e));
    const options=starts.length>1?`<label>Choose a dated start<select id="catalogue-start-select">${historicalEntryOptions(starts,current.periods,current.featured_years||[])}</select></label><div id="catalogue-start-review"><p class="note">Select a year, then review its starting reference and character options.</p></div>`:starts.map(catalogueStartMarkup).join('');
    return '<h3>Available today</h3><p>The full Major Campaign is in development. Reviewed starts and the optional authored openings have bounded capabilities.</p>'+options+(starts.length?'':'<p class="note">No verified start is currently available.</p>');
  }
  if(entry.catalogue_id==='CSS-01'){
    const ready=current.kind==='settlement_system'&&(current.templates||[]).some(t=>t.id==='R00'&&t.ready===true);
    return '<h3>Available today · The Rise of... You</h3><p>A clearly fictional R00 founding slice supports reviewed households, permission, supplies and bounded settlement work. The eight design families and full configurable system remain in development.</p>'+(ready?'<button type="button" class="primary" data-rise-setup>Review a fictional founding story</button>':'<p class="note">No reviewed founding start is currently available.</p>');
  }
  return '<h3>Available today · world guide</h3><p>Read the adopted world reference and map keys. A playable Kira starting snapshot is not available.</p>'+(current.reference_id==='world-of-kira'?'<button type="button" class="quiet" data-inspect-world="world-of-kira">Read the Kira world guide</button>':'');
}
function catalogueStartMarkup(entry){
  return `<p>${esc(entry.year)} · ${esc(entry.title)}</p><div class="buttons"><button type="button" class="quiet" data-inspect-entry="${esc(entry.id)}">Read ${esc(entry.year)} starting reference</button><button type="button" class="primary" data-start-entry="${esc(entry.id)}">Review ${esc(entry.year)} playthrough</button></div>`;
}
function cataloguePreviewMarkup(entry){
  const dependencies=entry.content_dependencies;
  return `<article class="catalogue-preview"><span class="eyebrow">${esc(entry.catalogue_id)} · ${esc(CATALOGUE_TYPES[entry.campaign_type])}</span><div class="catalogue-preview-heading"><h3>${esc(entry.title)}</h3><span class="badge">${esc(CATALOGUE_STATUS[entry.development_status])}</span></div><p class="catalogue-preview-tagline">${esc(entry.tagline)}</p><p class="reference-note">Working concept · unreleased. The experiences and systems below describe the intended campaign. Only the existing starts explicitly listed here can be reviewed for play.</p><div class="catalogue-preview-facts"><div><small>SETTING</small><p>${esc(entry.setting)}</p></div><div><small>PORTFOLIO</small><p>${esc(CATALOGUE_SLATES[entry.slate])}</p></div><div><small>GENRES</small><p>${esc(entry.genres.join(' · '))}</p></div><div><small>LAUNCH ACCESS</small><p>${entry.availability.launch_target_access==='free'?'Proposed free Short Story at launch':'To be announced'} · no entitlement granted</p></div></div>${entry.synopsis.map(p=>`<p>${esc(p)}</p>`).join('')}<h3>Proposed perspectives</h3><p>${esc(entry.perspectives)}</p><h3>The intended experience</h3><p>${esc(entry.core_experiences)}</p><h3>Campaign scope</h3><p>${esc(entry.scope)}</p>${entry.configuration?`<h3>Proposed configuration</h3><p>${esc(entry.configuration)}</p>`:''}<h3>Featured systems · planned for this concept</h3><div class="catalogue-genres">${entry.featured_systems.map(s=>`<span>${esc(s)}</span>`).join('')}</div><section class="catalogue-current-access">${catalogueCurrentAccess(entry)}</section><details class="catalogue-development"><summary>Development requirements & provenance</summary><p>${esc(dependencies.core)}</p><p>${esc(dependencies.foundation)}</p><p>${esc(dependencies.specific_review)}</p><p>${esc(entry.readiness.verification)}</p><p>Before release: approve the concept, establish its setting and player entries, integrate the shared simulation, populate the world, implement the scenario, verify continuity and recovery, then approve publication.</p><p class="note">Catalogue design v${esc(entry.version)} · working proposal. Source section ${esc(entry.provenance.section)} in ${esc(entry.provenance.source)}. Preview approval is separate from release approval. Covers are typographic placeholders.</p></details></article>`;
}
function inspectCatalogueConcept(identity){
  if(view!=='content-library')return;
  const entry=catalogueData?.portfolio?.entries.find(e=>e.catalogue_id===identity);if(!entry)return;
  ++inspectorRequest;
  $('#inspect-title').textContent='Campaign preview · out of character';
  $('#inspect-content').innerHTML=cataloguePreviewMarkup(entry);
  if(!$('#inspect-dialog').open)$('#inspect-dialog').showModal();
  const select=$('#catalogue-start-select');
  if(select)select.onchange=()=>{const start=approvedEntries.get(select.value);$('#catalogue-start-review').innerHTML=start?catalogueStartMarkup(start):'<p class="note">Choose a dated start to continue.</p>';bindLibraryControls();};
  bindLibraryControls();
}
