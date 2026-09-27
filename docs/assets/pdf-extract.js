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

 // Returns {text, pageCount, pagesWithText, noTextLayer, truncated}.
 // noTextLayer:true means pdf.js found no text on any page — almost always
 // a scanned/image-only PDF, which this reads but cannot OCR (that is a
 // separate, not-yet-built phase); callers should say so plainly rather than
 // show an auto-fill pass that silently found nothing.
 async function extractPdfText(file){
  if(!file)throw new Error("No file given.");
  if(!/\.pdf$/i.test(file.name)&&file.type&&file.type!=="application/pdf")throw new Error("This tool currently reads PDF files only. Convert or export the document as a PDF, or enter its values manually.");
  if(file.size>MAX_BYTES)throw new Error(`File exceeds the ${(MAX_BYTES/1024/1024)|0} MB local guardrail (${(file.size/1024/1024).toFixed(1)} MB). Split or compress the PDF, or enter values manually.`);
  const buf=await file.arrayBuffer();
  const head=new Uint8Array(buf.slice(0,5));
  let headStr="";for(let i=0;i<head.length;i++)headStr+=String.fromCharCode(head[i]);
  if(headStr!=="%PDF-")throw new Error("This does not look like a PDF file (missing %PDF header). Nothing was uploaded.");
  const pdfjsLib=await loadPdfjs();
  let doc;
  try{doc=await pdfjsLib.getDocument({data:buf,isEvalSupported:false,disableFontFace:true,useSystemFonts:false}).promise}
  catch(e){throw new Error("Could not parse this PDF locally: "+(e&&e.message?e.message:e)+". It may be encrypted, password-protected or corrupted — enter values manually instead.")}
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

 global.ClinicOpsPdfExtract={extractPdfText,MAX_BYTES,MAX_PAGES,MAX_CHARS};
})(window);
