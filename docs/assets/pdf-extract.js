// Self-hosted pdf.js text-layer extraction, shared by every tool that offers
// "upload a document to auto-fill this field" (Technical File Consistency
// Check first; Integrity Check and the SDEA clause checker are candidates to
// reuse this unchanged later). Nothing here makes a network call: pdf.js and
// its worker are vendored at vendor/pdfjs/ and loaded from this origin only.
// A file handed to extractPdfText() is read in this browser and never
// uploaded, stored or transmitted anywhere.
//
// Guardrails below are a resilience boundary against an oversized,
// many-page or pathological PDF freezing the tab — not a security boundary
// against a hostile file (there is no server for a hostile file to attack).
// Exceeding one throws a plain Error with a human-readable message; callers
// must catch it and fall back to manual entry, exactly as the XLSX reader in
// integrity-scanner.html already expects its callers to do.
(function (global) {
 "use strict";
 const MAX_BYTES=40*1024*1024, MAX_PAGES=200, MAX_CHARS=3000000;
 let pdfjsPromise=null;

 // pdf.js 6.3.289's page.render() path (used by ocr-extract.js to rasterize a page for OCR;
 // extractPdfText() below never calls render() and is unaffected) calls the still-very-new
 // Map/WeakMap.prototype.getOrInsertComputed (TC39 "upsert" proposal) unconditionally, with no
 // internal feature check. That method is not yet shipped in every current browser, so without
 // this small, spec-faithful polyfill, page.render() throws "... .getOrInsertComputed is not a
 // function" on those browsers — a platform gap, not something pdf.js or this vendored file
 // controls. Safe to apply unconditionally: a no-op where the method already exists natively.
 if(typeof global.Map==="function"&&typeof global.Map.prototype.getOrInsertComputed!=="function"){
  global.Map.prototype.getOrInsertComputed=function(key,callbackfn){
   if(this.has(key))return this.get(key);
   const v=callbackfn(key);this.set(key,v);return v;
  };
 }
 if(typeof global.WeakMap==="function"&&typeof global.WeakMap.prototype.getOrInsertComputed!=="function"){
  global.WeakMap.prototype.getOrInsertComputed=function(key,callbackfn){
   if(this.has(key))return this.get(key);
   const v=callbackfn(key);this.set(key,v);return v;
  };
 }

 function loadPdfjs(){
  if(pdfjsPromise)return pdfjsPromise;
  pdfjsPromise=import("../vendor/pdfjs/pdf.min.mjs").then(lib=>{
   lib.GlobalWorkerOptions.workerSrc="vendor/pdfjs/pdf.worker.min.mjs";
   return lib;
  }).catch(e=>{pdfjsPromise=null;throw new Error("Could not load the local PDF reader (pdf.js): "+(e&&e.message?e.message:e)+". Nothing was uploaded; enter values manually instead.")});
  return pdfjsPromise;
 }

 // Joins pdf.js text items into a readable string. A real line break is
 // inserted when the next item's baseline drops noticeably (a new visual
 // line on the page) or pdf.js itself marks an end-of-line, so label-anchor
 // patterns that expect "Label:" and its value on the same or next line
 // still see that structure; otherwise items are joined with a single space.
 function joinItems(items){
  let out="",lastY=null;
  for(const it of items){
   const str=it.str||"";
   if(!str){if(it.hasEOL)out+="\n";continue}
   const y=it.transform?it.transform[5]:null;
   if(lastY!==null&&y!==null&&Math.abs(y-lastY)>2)out+="\n";
   else if(out&&!/\s$/.test(out)&&!/^\s/.test(str))out+=" ";
   out+=str;
   if(it.hasEOL)out+="\n";
   lastY=y;
  }
  return out;
 }

 // Validates a File and opens it as a live pdf.js document — the shared
 // first step under both extractPdfText (text-layer reading) and OCR
 // (ocr-extract.js's opt-in fallback for scans). Returns the open document;
 // the caller owns it and must call doc.destroy() when done. Does not apply
 // the page-count guardrail itself, since text extraction and OCR have
 // different, independently-justified page caps (OCR is far slower per
 // page) — each caller checks doc.numPages against its own limit.
 async function openPdfDocument(file){
  if(!file)throw new Error("No file given.");
  if(!/\.pdf$/i.test(file.name)&&file.type&&file.type!=="application/pdf")throw new Error("This tool currently reads PDF files only. Convert or export the document as a PDF, or enter its values manually.");
  if(file.size>MAX_BYTES)throw new Error(`File exceeds the ${(MAX_BYTES/1024/1024)|0} MB local guardrail (${(file.size/1024/1024).toFixed(1)} MB). Split or compress the PDF, or enter values manually.`);
  const buf=await file.arrayBuffer();
  const head=new Uint8Array(buf.slice(0,5));
  let headStr="";for(let i=0;i<head.length;i++)headStr+=String.fromCharCode(head[i]);
  if(headStr!=="%PDF-")throw new Error("This does not look like a PDF file (missing %PDF header). Nothing was uploaded.");
  const pdfjsLib=await loadPdfjs();
  try{return await pdfjsLib.getDocument({data:buf,isEvalSupported:false,disableFontFace:true,useSystemFonts:false}).promise}
  catch(e){throw new Error("Could not parse this PDF locally: "+(e&&e.message?e.message:e)+". It may be encrypted, password-protected or corrupted — enter values manually instead.")}
 }

 // Returns {text, pageCount, pagesWithText, noTextLayer, truncated}.
 // noTextLayer:true means pdf.js found no text on any page — almost always
 // a scanned/image-only PDF. Callers should say so plainly rather than show
 // an auto-fill pass that silently found nothing, and may offer the OCR
 // fallback in ocr-extract.js as a separate, explicit, opt-in next step.
 async function extractPdfText(file){
  const doc=await openPdfDocument(file);
  const pageCount=doc.numPages;
  if(pageCount>MAX_PAGES){try{doc.destroy()}catch(_){}throw new Error(`PDF has ${pageCount} pages, over the ${MAX_PAGES}-page local guardrail. Split the file or enter values manually.`)}
  let text="",pagesWithText=0,truncated=false;
  for(let i=1;i<=pageCount;i++){
   const page=await doc.getPage(i);
   let pageText="";
   try{const content=await page.getTextContent();pageText=joinItems(content.items)}
   catch(_){/* one bad page should not fail the whole document */}
   if(pageText.trim())pagesWithText++;
   text+=pageText+"\n\n";
   try{page.cleanup()}catch(_){}
   if(text.length>MAX_CHARS){text=text.slice(0,MAX_CHARS);truncated=true;break}
  }
  try{doc.destroy()}catch(_){}
  return{text,pageCount,pagesWithText,noTextLayer:pagesWithText===0,truncated};
 }

 global.ClinicOpsPdfExtract={extractPdfText,openPdfDocument,MAX_BYTES,MAX_PAGES,MAX_CHARS};
})(window);
