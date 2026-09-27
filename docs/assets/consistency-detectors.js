// Field detectors for the Technical File Consistency Check's upload path.
// Purely pattern/label matching over text pdf.js already extracted locally
// (see pdf-extract.js) — no AI, no network call, nothing sent anywhere. Each
// detector looks for a bilingual (English/Danish) label near the start of a
// line and captures what follows it on that line, then hands the raw
// capture to the *same* type-specific plausibility check the page's own
// normalizers use, so a value that doesn't look like its field (e.g. a
// "shelf life" hit with no digit in it) is downgraded or dropped rather than
// silently trusted.
//
// Every match carries a confidence tier ("strong" | "weak"), never a bare
// value: "strong" means an unambiguous, field-specific label matched
// ("Basic UDI-DI:", "Intended purpose:"); "weak" means either a
// shorter/generic label that could collide with unrelated text ("Class:",
// "Version:") or a strong-label match whose captured value failed its own
// plausibility check. A field with no match at all is left out of the
// result entirely — never filled with an empty guess — exactly like a field
// nobody typed into by hand.
(function (global) {
 "use strict";
 const RE=(...alts)=>new RegExp("(?:"+alts.join("|")+")\\s*[:\\-–—]?\\s*([^\\n]{1,200})","i");

 // {re, conf} tried in order; first match for a field wins.
 const DETECTORS={
  device_trade_name:[
   {re:RE("device\\s+trade\\s*name","trade\\s*name","product\\s*name","device\\s*name"),conf:"strong"},
   {re:RE("model\\s+designation","handelsnavn","produktnavn"),conf:"weak"}],
  model_ref:[
   {re:RE("model\\s*/?\\s*catalogue\\s*(?:/|\\s*)?\\s*(?:number|no\\.?|ref(?:erence)?)","catalogue\\s*(?:number|no\\.?)","reference\\s*number","article\\s*number","katalognummer","referencenummer","varenummer"),conf:"strong"},
   {re:RE("model","ref\\.?","modelnummer"),conf:"weak"}],
  basic_udi_di:[
   {re:RE("basic\\s+udi-?di","basis\\s+udi-?di"),conf:"strong"}],
  udi_di:[
   {re:/(?<!basic\s)(?<!basis\s)\budi-?di\b\s*[:\-–—]?\s*([^\n]{1,200})/i,conf:"strong"},
   {re:/\b((?:\(01\))?\d{14})\b/,conf:"weak"}],
  intended_purpose:[
   {re:RE("intended\\s+purpose","intended\\s+use","tilsigtet\\s+anvendelse|tilsigtede\\s+anvendelse"),conf:"strong"}],
  risk_class:[
   {re:RE("risk\\s+class(?:ification)?","risikoklasse"),conf:"strong"},
   {re:RE("class(?:ification)?\\b","klasse\\b"),conf:"weak"}],
  manufacturer:[
   {re:RE("legal\\s+manufacturer","manufacturer\\s+legal\\s+name","fabrikant","producent"),conf:"strong"},
   {re:RE("manufacturer\\b"),conf:"weak"}],
  shelf_life:[
   {re:RE("shelf\\s*life","expiry\\s+period","validity\\s+period","holdbarhed"),conf:"strong"},
   {re:RE("use\\s+by","udløbsdato"),conf:"weak"}],
  storage:[
   {re:RE("storage\\s*(?:&|and)?\\s*handling\\s*conditions?","storage\\s+conditions?","store\\s+between","opbevaringsforhold","opbevares"),conf:"strong"}],
  sterility:[
   {re:RE("sterilization\\s+method","sterilisation\\s+method","sterility\\s+status","sterilitet"),conf:"strong"},
   {re:RE("\\bsterility\\b","\\bsteril(?:t|itet)?\\b"),conf:"weak"}],
  single_use:[
   {re:RE("single\\s+use\\s+statement","reprocessing\\s+statement","for\\s+single\\s+use\\s+only","engangsbrug"),conf:"strong"},
   {re:RE("single\\s+use\\b","reusable\\b","genanvendelig"),conf:"weak"}],
  contraindications:[
   {re:RE("contraindications?","kontraindikation(?:er)?"),conf:"strong"}],
  software_version:[
   {re:RE("software\\s+version","sw\\s+version","softwareversion"),conf:"strong"},
   {re:RE("\\bversion\\b","\\brev(?:ision)?\\.?\\b"),conf:"weak"}]
 };

 function cleanValue(raw){
  let v=String(raw||"").replace(/\s+/g," ").trim().replace(/[.;,]+$/,"");
  if(v.length>160)v=v.slice(0,160).trim();
  return v;
 }
 function hasDigit(v){return /\d/.test(v)}

 // Downgrades or drops a match whose shape doesn't fit its declared type —
 // fail-closed, mirroring the page's own comparison logic rather than a
 // second, disconnected notion of "looks right."
 function plausibility(fieldType,mod10,value,conf){
  if(fieldType==="identifier"){
   const stripped=value.replace(/[^0-9A-Za-z]/g,"");
   if(stripped.length<6)return null;
   if(mod10&&!/^\(?01\)?\d{14}$/.test(value.replace(/\s/g,""))&&!/^\d{14}$/.test(stripped))return{value,conf:"weak"};
   return{value,conf};
  }
  if(fieldType==="duration"){
   if(!hasDigit(value))return null;
   return{value,conf};
  }
  return{value,conf};
 }

 // detectFields(text, FIELDS) -> {fieldId: {value, confidence, pattern}}
 // FIELDS is the page's own field-definition array, so type/mod10 checks
 // stay driven by the one place those are already defined.
 function detectFields(text,FIELDS){
  const out={};
  if(!text)return out;
  for(const f of FIELDS){
   const dets=DETECTORS[f.id];
   if(!dets)continue;
   for(const d of dets){
    const m=d.re.exec(text);
    if(!m||!m[1])continue;
    const cleaned=cleanValue(m[1]);
    if(!cleaned)continue;
    const checked=plausibility(f.type,f.mod10,cleaned,d.conf);
    if(!checked)continue;
    out[f.id]={value:checked.value,confidence:checked.conf};
    break;
   }
  }
  return out;
 }

 global.ClinicOpsConsistencyDetectors={detectFields};
})(window);
