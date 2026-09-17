(function(root){
  'use strict';
  const refusal="I don’t have verified information to answer that accurately, and I don’t want to mislead you.";
  const normalize=s=>String(s).toLowerCase().normalize('NFKC').replace(/\bcustous\b|\bcustas\b/g,'custos').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
  const validDate=s=>typeof s==='string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s));
  function sourceOK(s,topic,today){
    if(!s || s.status!=='approved' || !s.title || !s.publisher || !s.excerpt || !(s.section || s.page) || !validDate(s.verifiedOn) || !validDate(s.reviewDue) || s.verifiedOn>today || s.reviewDue<today || !s.scope?.includes(topic))return false;
    try{const u=new URL(s.url);return u.protocol==='https:' && !u.username && !u.password && ((s.authority==='official-government' && /(^|\.)gov\.jm$/.test(u.hostname)) || (s.authority==='authorised-hjpa' && u.hostname==='hanoverjpa.com'));}catch{return false;}
  }
  function audit(kb,today){
    return kb.records.map(r=>{
      const conflict=!!r.factKey && kb.records.some(x=>x.id!==r.id && x.status==='approved' && x.factKey===r.factKey && x.value!==r.value && (!x.effectiveTo || !r.effectiveFrom || x.effectiveTo>=r.effectiveFrom) && (!r.effectiveTo || !x.effectiveFrom || r.effectiveTo>=x.effectiveFrom));
      const evidence=r.sourceIds?.length>0 && r.sourceIds.every(id=>sourceOK(kb.sources.find(s=>s.id===id),r.topic,today));
      return {id:r.id,topic:r.topic,status:conflict?'conflict':r.status!=='approved'?r.status:!evidence?'blocked-evidence':!r.answer?'blocked-empty':'approved',temporalStatus:r.temporalStatus,note:r.note||''};
    });
  }
  function answer(query,kb,today=new Date().toISOString().slice(0,10)){
    const q=normalize(query), blocked=reason=>({direct:refusal,followup:reason,sources:[],auditStatus:'blocked',actions:[]});
    if(/^(hi|hello|hey|thanks|thank you)$/.test(q))return {direct:'Hello! I’m Gia. I use reviewed records and show my evidence. What would you like to check?',sources:[],auditStatus:'interface'};
    if(q==='source audit' || q==='audit status')return {direct:'Source audit — approval means reviewed evidence, not a guarantee of permanent accuracy.',bullets:audit(kb,today).map(r=>`${r.id}: ${r.status} · ${r.temporalStatus}`),sources:[],auditStatus:'interface'};
    // Exact approved question aliases only: no fuzzy entity scores, scraped prose or language-model fallback.
    const matches=kb.records.filter(r=>r.aliases?.some(a=>normalize(a)===q));
    if(matches.length!==1)return blocked(matches.length?'The question matches more than one record. Please specify the role or topic.':'Try a specific question, or select one of the reviewed questions below. I cannot safely infer an answer from keywords.');
    const r=matches[0],state=audit(kb,today).find(x=>x.id===r.id);
    if(state.status!=='approved')return blocked(state.status==='conflict'?'The records disagree. An authorised reviewer must resolve the conflict before I answer.':`This topic is ${state.status}; it needs source review before I can give factual guidance.`);
    if(r.temporalStatus==='current' && (!validDate(r.effectiveFrom)||r.effectiveFrom>today||(r.effectiveTo&&r.effectiveTo<today)))return blocked('The record is outside its confirmed effective period.');
    return {direct:r.answer,recordId:r.id,auditStatus:'approved',sources:r.sourceIds.map(id=>kb.sources.find(s=>s.id===id)).sort((a,b)=>a.rank-b.rank).map(s=>({document:s.title,publisher:s.publisher,url:s.url,heading:s.section,page:s.page,published:s.published,updated:s.updated,verifiedOn:s.verifiedOn,reviewDue:s.reviewDue,temporalStatus:r.temporalStatus,authority:s.authority,auditStatus:'approved'})),actions:[]};
  }
  root.GiaLocked=Object.freeze({answer,audit,normalize,refusal});
})(typeof window!=='undefined'?window:globalThis);
