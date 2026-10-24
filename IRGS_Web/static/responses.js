'use strict';
// A local text formatter, never an action executor or provider router.
const AppResponses=(()=>{
  const own=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
  const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
  const require=(condition,message)=>{if(!condition)throw new Error('App responses: '+message);};
  const nonempty=value=>typeof value==='string'&&value.trim().length>0;
  const id=value=>typeof value==='string'&&/^[a-z][a-z0-9_.-]{0,95}$/.test(value);
  const fields=(value,keys)=>object(value)&&Object.keys(value).every(key=>keys.includes(key))&&keys.every(key=>own(value,key));
  function placeholders(template){
    require(nonempty(template)&&template.length<=20000,'invalid clause');
    const slots=[...template.matchAll(/\{([a-z][a-z0-9_]*)\}/g)].map(match=>match[1]);
    require(!/[{}]/.test(template.replace(/\{([a-z][a-z0-9_]*)\}/g,'')),'format expressions are forbidden');
    return slots;
  }
  function validateLibrary(data){
    require(object(data)&&data.schema_version===1&&data.language==='en'&&id(data.id)&&nonempty(data.version),'invalid library');
    require(Array.isArray(data.families)&&data.families.length>0&&Array.isArray(data.recipes),'missing families/recipes');
    const ids=new Set();
    for(const family of data.families){
      require(id(family.id)&&!ids.has(family.id),'duplicate/invalid family');ids.add(family.id);
      require(['system','draft'].includes(family.role)&&id(family.state)&&id(family.fact),'invalid role/state/fact');
      require(['host_status','actor_view','committed_receipt','player_request'].includes(family.source_kind),'invalid source kind');
      require(family.role!=='draft'||family.source_kind==='player_request','draft source');
      require(object(family.slots)&&Object.entries(family.slots).every(([key,type])=>/^[a-z][a-z0-9_]*$/.test(key)&&['text','label','integer'].includes(type)),'invalid slots');
      require(Array.isArray(family.variants)&&family.variants.length>0&&family.variants.length<=16,'missing variants');
      for(const variant of family.variants){
        const slots=new Set(placeholders(variant));
        require(slots.size===Object.keys(family.slots).length&&[...slots].every(key=>own(family.slots,key)),'undeclared/missing slots');
      }
      if(family.id==='receipt.exact')require(family.source_kind==='committed_receipt'&&family.variants.every(text=>text==='{receipt_text}'),'receipt must remain exact');
    }
    const recipes=new Set();
    for(const recipe of data.recipes){
      require(id(recipe.id)&&!recipes.has(recipe.id),'duplicate/invalid recipe');recipes.add(recipe.id);
      require(Array.isArray(recipe.required)&&recipe.required.length>0&&Array.isArray(recipe.optional),'invalid recipe');
      const parts=[...recipe.required,...recipe.optional];
      require(parts.length<=8&&new Set(parts).size===parts.length&&parts.every(key=>ids.has(key)),'unknown/duplicate recipe family');
      if(recipe.id.startsWith('result.'))require(recipe.required.includes('receipt.exact'),'committed recipe requires exact receipt');
    }
    return data;
  }
  function freeze(value){if(object(value)||Array.isArray(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
  const library=freeze(validateLibrary(APP_RESPONSE_DATA));
  const families=new Map(library.families.map(family=>[family.id,family]));
  const recipes=new Map(library.recipes.map(recipe=>[recipe.id,recipe]));
  function family(id){require(families.has(id),'unknown family');return families.get(id);}
  function checkContext(definition,context){
    require(fields(context,['actor_id','snapshot_id','source_ref','source_kind','state','values']),'invalid context fields');
    for(const key of ['actor_id','snapshot_id','source_ref'])require(nonempty(context[key])&&context[key].length<=512,'missing scope/source');
    require(context.source_kind===definition.source_kind&&context.state===definition.state,'source/state mismatch');
    require(object(context.values)&&Object.keys(context.values).length===Object.keys(definition.slots).length,'invalid slot fields');
    for(const [key,type] of Object.entries(definition.slots)){
      require(own(context.values,key),'missing slot');const value=context.values[key];
      require(type==='integer'?Number.isSafeInteger(value)&&value>=0:typeof value==='string'&&value.length<=(type==='label'?500:100000),'invalid slot value');
    }
  }
  function ordinal(seed){let hash=2166136261;for(const char of seed){hash^=char.codePointAt(0);hash=Math.imul(hash,16777619);}return hash>>>0;}
  function render(id,context,variant){
    const definition=family(id);checkContext(definition,context);
    // Stable for the same actor/source/family, even after re-render or reload.
    // No personalized rendered text or context is cached or sent anywhere.
    const selected=variant===undefined?ordinal(JSON.stringify([library.version,library.language,id,context.actor_id,context.source_ref]))%definition.variants.length:variant;
    require(Number.isInteger(selected)&&selected>=0&&selected<definition.variants.length,'invalid variant');
    return definition.variants[selected].replace(/\{([a-z][a-z0-9_]*)\}/g,(_,key)=>String(context.values[key]));
  }
  function compose(parts){
    require(Array.isArray(parts)&&parts.length>0&&parts.length<=8,'invalid composition');
    let scope=null,role=null;const ids=new Set(),claims=new Map(),values=new Map();
    for(const part of parts){
      const definition=family(part.family);checkContext(definition,part.context);
      const key=JSON.stringify([part.context.actor_id,part.context.snapshot_id]);
      if(scope===null){scope=key;role=definition.role;}
      require(key===scope&&role===definition.role,'mixed actor/snapshot/role');
      require(!ids.has(part.family),'duplicate family');ids.add(part.family);
      const source=JSON.stringify([part.context.source_kind,part.context.source_ref]);
      const fact=source+':'+definition.fact;
      require(!claims.has(fact)||claims.get(fact)===part.context.state,'contradictory state');claims.set(fact,part.context.state);
      for(const [name,value] of Object.entries(part.context.values)){
        const key=source+':'+name;require(!values.has(key)||values.get(key)===value,'conflicting source value');values.set(key,value);
      }
    }
    require(role!=='draft'||parts.length===1,'drafts cannot be combined into a decision');
    return parts.map(part=>render(part.family,part.context,part.variant)).join('\n');
  }
  function composeRecipe(id,contexts,variants={}){
    require(recipes.has(id)&&object(contexts)&&object(variants),'unknown recipe');
    const recipe=recipes.get(id),order=[...recipe.required,...recipe.optional];
    require(recipe.required.every(key=>own(contexts,key))&&Object.keys(contexts).every(key=>order.includes(key)),'missing/foreign recipe facts');
    require(Object.keys(variants).every(key=>own(contexts,key)),'foreign variant');
    return compose(order.filter(key=>own(contexts,key)).map(key=>({family:key,context:contexts[key],variant:variants[key]})));
  }
  return Object.freeze({library,render,compose,composeRecipe,ordinal,validateLibrary});
})();
