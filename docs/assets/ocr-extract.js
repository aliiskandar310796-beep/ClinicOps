// Self-hosted Tesseract.js OCR — an explicit, opt-in fallback for PDFs
// pdf-extract.js reports as having no usable text layer (scanned/image-only
// documents). Nothing here makes a network call beyond this origin: the
// Tesseract engine (WASM), its worker script and the English trained-data
// file are vendored at vendor/tesseract/ and loaded from this origin only —
// see docs/vendor/README.md for versions, licenses and hashes.
//
// OCR is real client-side computation, seconds per page rather than the
// near-instant text-layer read pdf-extract.js does, and the ~5MB engine +
// language data only download on first use. For both reasons this never
// runs automatically: a caller only reaches this module because a person
// explicitly chose to try OCR after being told a document has no text layer
// and what trying OCR costs (time, a one-time download). Per the site's
// existing confidence-tier convention, an OCR-derived value is always
// weaker evidence than a text-layer match — misread characters (1/I, 0/O)
// are a different failure mode than "label not found," so callers should
// mark OCR results at their own, more conservative tier rather than folding
// them into "strong"/"weak" from pattern matching on clean extracted text.
(function (global) {
 "use strict";
 const MAX_OCR_PAGES=20; // OCR is far slower per page than text-layer reading; a lower, separate cap.

 let tesseractReady=null;
 function loadTesseract(){
  if(global.Tesseract)return Promise.resolve(global.Tesseract);
  if(tesseractReady)return tesseractReady;
  tesseractReady=new Promise((res,rej)=>{
   const s=document.createElement("script");
   s.src="vendor/tesseract/tesseract.min.js";
   s.onload=()=>res(global.Tesseract);
   s.onerror=()=>rej(new Error("Could not load the local OCR engine. Nothing was uploaded; enter values manually instead."));
   document.head.appendChild(s);
  }).catch(e=>{tesseractReady=null;throw e});
  return tesseractReady;
 }

 let workerPromise=null;
 async function getWorker(onProgress){
  if(workerPromise)return workerPromise;
  const Tesseract=await loadTesseract();
  workerPromise=Tesseract.createWorker("eng",1,{
   workerPath:"vendor/tesseract/worker.min.js",
   corePath:"vendor/tesseract/tesseract-core-lstm.js",
   langPath:"vendor/tesseract",
   gzip:true,
   // tesseract.js defaults to wrapping workerPath in a Blob (`importScripts("<workerPath>")`
   // inside a blob: URL) so a worker script can be loaded cross-origin from a CDN. That wrapping
   // is exactly wrong for self-hosting: it makes the worker's own location a blob: URL, and the
   // vendored core script then can't resolve its sibling .wasm file with a plain relative path
   // against that blob: URL. Loading worker.min.js directly (same-origin here, so no CORS need)
   // keeps the worker's location the real vendor/tesseract/ URL and fixes that resolution.
   workerBlobURL:false,
   logger:onProgress||function(){}
  }).catch(e=>{workerPromise=null;throw new Error("Could not start the local OCR engine: "+(e&&e.message?e.message:e))});
  return workerPromise;
 }

 async function pageToCanvas(page,scale){
  const viewport=page.getViewport({scale:scale||2});
  const canvas=document.createElement("canvas");
  canvas.width=Math.ceil(viewport.width);
  canvas.height=Math.ceil(viewport.height);
  const ctx=canvas.getContext("2d");
  await page.render({canvasContext:ctx,viewport:viewport}).promise;
  return canvas;
 }

 // ocrPdfDoc(doc, {onProgress, maxPages, scale}) -> {text, pages, truncated, pageCount}
 // doc is an already-open pdf.js document (see pdf-extract.js's
 // openPdfDocument) — the caller owns it and destroys it when done; this
 // does not call doc.destroy() itself, matching that ownership convention.
 async function ocrPdfDoc(doc,opts){
  opts=opts||{};
  const maxPages=Math.max(1,Math.min(opts.maxPages||MAX_OCR_PAGES,MAX_OCR_PAGES));
  const pageCount=doc.numPages;
  const truncated=pageCount>maxPages;
  const n=Math.min(pageCount,maxPages);
  const worker=await getWorker(opts.onProgress);
  const pages=[];
  for(let i=1;i<=n;i++){
   if(opts.onProgress)opts.onProgress({status:`reading page ${i} of ${n} (OCR)`,progress:n?(i-1)/n:0});
   const page=await doc.getPage(i);
   let text="",confidence=null;
   try{
    const canvas=await pageToCanvas(page,opts.scale);
    const res=await worker.recognize(canvas);
    text=(res&&res.data&&res.data.text)||"";
    confidence=res&&res.data&&typeof res.data.confidence==="number"?res.data.confidence:null;
   }catch(_){/* one bad page should not fail the whole document */}
   pages.push({index:i,text,confidence});
   try{page.cleanup()}catch(_){}
  }
  return{text:pages.map(p=>p.text).join("\n\n"),pages,truncated,pageCount};
 }

 // Convenience wrapper: opens the File itself via the shared pdf-extract.js
 // loader (so OCR reuses the exact same validation/guardrail path a
 // text-layer read uses) rather than duplicating that logic here.
 async function ocrPdfFile(file,opts){
  if(!global.ClinicOpsPdfExtract||!global.ClinicOpsPdfExtract.openPdfDocument){
   throw new Error("The local PDF reader must be loaded before OCR can run.");
  }
  const doc=await global.ClinicOpsPdfExtract.openPdfDocument(file);
  try{return await ocrPdfDoc(doc,opts)}
  finally{try{doc.destroy()}catch(_){}}
 }

 global.ClinicOpsOcrExtract={ocrPdfDoc,ocrPdfFile,MAX_OCR_PAGES};
})(window);
