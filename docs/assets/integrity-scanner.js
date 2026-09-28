// Regulatory Integrity Scanner page logic. Extracted from an inline <script> (2026-09-28)
// so the 45 KB of code no longer sits on the mobile critical path; loaded with `defer`
// after assets/reconciliation.js, in document order. Browser-local: nothing is uploaded.
(()=>{"use strict";const $=id=>document.getElementById(id),T=v=>String(v??""),tr=v=>T(v).trim(),esc=v=>T(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
let last=null,runEpoch=0,matrixRead=0,portfolioRead=0;
const RE=window.ClinicOpsReconciliation;
const BOUNDARY="Deterministic comparison aid only; statuses are bounded operator signals (aligned / mismatch signal / missing evidence / conflicting evidence / unresolved / not applicable / requires qualified review), not compliance determinations. Source authority, materiality and disposition stay with the accountable qualified owner. Browser-local: nothing entered or imported is transmitted or stored.";
const STCLS={"aligned":"stAligned","mismatch signal":"stMismatch","missing evidence":"stMissing","conflicting evidence":"stConflict","requires qualified review":"stReview","not applicable":"stNA","unresolved":"stReview"};
function stCell(s){return `<td class="st ${STCLS[s]||""}">${esc(s)}</td>`}
// ---------- shared result rendering (plain table + Tabulator workbench) ----------
let table=null,gridReady=null,rowsStore=[];
function ensureGrid(){if(window.Tabulator)return Promise.resolve(true);if(gridReady)return gridReady;
 gridReady=new Promise(res=>{const l=document.createElement("link");l.rel="stylesheet";l.href="vendor/tabulator-6.5.3.min.css";document.head.appendChild(l);
 const sc=document.createElement("script");sc.src="vendor/tabulator-6.5.3.min.js";sc.onload=()=>res(!!window.Tabulator);sc.onerror=()=>res(false);document.head.appendChild(sc)});return gridReady}
const tf=c=>{const v=c.getValue();return document.createTextNode(v==null||v===""?"—":String(v))};
function statusFmt(c){const v=String(c.getValue()||"");const sp=document.createElement("span");sp.className="st "+(STCLS[v]||"");sp.textContent=v;return sp}
function applyFilters(){if(!table)return;const q=($("wb_search").value||"").toLowerCase(),st=$("wb_status").value;
 table.setFilter((d)=>{if(st&&d.status!==st)return false;if(!q)return true;
  return ["object","field","expected","observed","status","evidence","owner","next_action","note"].some(k=>String(d[k]??"").toLowerCase().includes(q))})}
function buildGrid(rows){
 if(table){try{table.destroy()}catch(_){/*noop*/}table=null}
 table=new Tabulator("#grid",{data:rows,layout:"fitColumns",height:rows.length>9?480:null,reactiveData:false,
  selectableRows:true,placeholder:"No findings in the current filter.",
  columns:[
   {formatter:"rowSelection",titleFormatter:"rowSelection",hozAlign:"center",headerSort:false,width:44,frozen:true},
   {title:"Object / record",field:"object",formatter:tf,minWidth:150},
   {title:"Field",field:"field",formatter:tf,minWidth:110},
   {title:"Expected",field:"expected",formatter:tf,minWidth:90},
   {title:"Observed",field:"observed",formatter:tf,minWidth:90},
   {title:"Status",field:"status",formatter:statusFmt,minWidth:130},
   {title:"Evidence",field:"evidence",formatter:tf,minWidth:100},
   {title:"Owner",field:"owner",editor:"input",formatter:tf,minWidth:110},
   {title:"Next action",field:"next_action",editor:"input",formatter:tf,minWidth:180},
   {title:"Review state",field:"review_state",editor:"list",editorParams:{values:["open","in review","closed with evidence"]},formatter:tf,minWidth:110},
   {title:"Reviewer note",field:"note",editor:"input",formatter:tf,minWidth:120},
   {title:"Closure evidence",field:"closure_evidence",editor:"input",formatter:tf,minWidth:160},
  ]});
 try{const ed=table.modules&&table.modules.edit;if(ed&&!ed._guarded){const o=ed.clearEditor.bind(ed);ed.clearEditor=(...a)=>{try{return o(...a)}catch(_){/*cell element already recycled by virtual scrolling*/}};ed._guarded=true}}catch(_){/*noop*/}
 table.on("cellEdited",cell=>{const d=cell.getData(),r=rowsStore[d._i];if(!r)return;
  try{const patch={[cell.getField()]:cell.getValue()},next=RE.review({...r,[cell.getField()]:cell.getOldValue()},patch);Object.assign(r,next);cell.getRow().update(next);wbMsg("");syncReviewForm()}
  catch(e){r[cell.getField()]=cell.getOldValue();cell.restoreOldValue();wbMsg(e.message)}});
 $("wb_toolbar").hidden=false;$("plainwrap").hidden=true;$("rows").innerHTML=plainRows(rows);
 table.on("tableBuilt",()=>{const g=$("wb_group").value;if(g)table.setGroupBy(g);applyFilters()});
}
function plainRows(shown){return shown.length?shown.map(r=>`<tr><td>${esc(r.object)}</td><td>${esc(r.field)}</td><td>${esc(r.expected??"—")}</td><td>${esc(r.observed??"—")}</td>${stCell(r.status)}<td>${esc(r.evidence||"—")}</td><td>${esc(r.owner||"—")}</td><td>${esc(r.next_action||"none")}</td></tr>`).join(""):`<tr><td colspan="8" class="muted">No comparable rows.</td></tr>`}
function renderPlain(rows){
 const shown=rows.filter(r=>r.status!=="not applicable");
 $("rows").innerHTML=plainRows(shown);
 $("plainwrap").hidden=false;$("wb_toolbar").hidden=true;$("grid").innerHTML="";
}
function render(mode,rows,meta){
 const epoch=++runEpoch;
 rows.forEach((r,i)=>{r._i=i;if(!r.id)r.id="finding-"+(i+1);if(!r.review_state)r.review_state="open";if(r.note==null)r.note=""});
 rowsStore=rows;
 const counts={aligned:0,"mismatch signal":0,"missing evidence":0,"conflicting evidence":0,"requires qualified review":0,"not applicable":0,unresolved:0};
 for(const r of rows)counts[r.status]=(counts[r.status]||0)+1;
 $("mAligned").textContent=counts.aligned;$("mMismatch").textContent=counts["mismatch signal"]+counts["conflicting evidence"];$("mMissing").textContent=counts["missing evidence"];$("mReview").textContent=counts["requires qualified review"]+counts.unresolved;
 const shown=rows.filter(r=>r.status!=="not applicable");
 const exceptions=rows.filter(r=>r.status!=="aligned"&&r.status!=="not applicable");
 $("queue").innerHTML=exceptions.length?exceptions.map(r=>`<li><strong>${esc(r.object)} — ${esc(r.field)}</strong>: ${esc(r.status)}. ${esc(r.next_action)}${r.owner?` <span class="muted">(owner: ${esc(r.owner)})</span>`:' <span class="muted">(assign an owner)</span>'}</li>`).join(""):`<li class="muted">No exceptions in the entered scope. Keep the export as the evidence row for this verification.</li>`;
 const bad=counts["mismatch signal"]+counts["conflicting evidence"],miss=counts["missing evidence"],rev=counts["requires qualified review"]+counts.unresolved;
 const badge=$("badge");
 if(bad){badge.textContent="MISMATCH SIGNALS";badge.className="badge hold";$("resultTitle").textContent="Exceptions to adjudicate"}
 else if(miss||rev){badge.textContent="INCOMPLETE";badge.className="badge review";$("resultTitle").textContent=miss?"Evidence incomplete":"Qualified review needed"}
 else{badge.textContent="NO ENTERED DIFFERENCE";badge.className="badge ok";$("resultTitle").textContent="No difference in the entered scope"}
 $("summary").textContent=`${mode==="A"?"Single-change check":mode==="C"?"Evidence matrix":"Portfolio scan"}: ${shown.length} comparisons — ${counts.aligned} aligned, ${bad} mismatch/conflict signals, ${miss} missing evidence, ${rev} for qualified review.`;
 last={tool:"clinicops-regulatory-integrity-scanner",tool_version:"1.3",rules_version:RE.VERSION,mode:mode==="A"?"single-change":mode==="C"?"evidence-matrix":"portfolio-scan",generated_at:new Date().toISOString(),...meta,findings:rows,summary:{...counts},boundary:BOUNDARY};
 $("review_row").innerHTML=rows.map((r,i)=>`<option value="${i}">${esc(r.object)} — ${esc(r.field)} (${esc(r.status)})</option>`).join("");syncReviewForm();
 $("packet_info").textContent="Rule version "+RE.VERSION+". SHA-256 fingerprints are generated on export.";
 const visible=shown.map(r=>({...r}));
 ensureGrid().then(ok=>{if(epoch!==runEpoch||!last)return;if(ok)buildGrid(visible);else renderPlain(rows)});
 try{$("resultTitle").scrollIntoView({block:"start",behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"})}catch(_){/*noop*/}
}
function dl(name,content,type){const b=new Blob([content],{type}),u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(u)}
async function exportPacket(){if(!last)return null;const epoch=runEpoch,p=JSON.parse(JSON.stringify(last));p.input_sha256=await RE.sha256(p.input_snapshot);const sealed=await RE.seal(p);if(epoch!==runEpoch||!last)return null;$("packet_info").textContent=`Input SHA-256: ${sealed.input_sha256} · Packet SHA-256: ${sealed.packet_sha256}`;return sealed}
$("x_json").onclick=async()=>{try{const p=await exportPacket();if(p)dl("clinicops-integrity-scan.json",JSON.stringify(p,null,2)+"\n","application/json")}catch(e){$("packet_info").textContent=e.message}};
$("x_html").onclick=async()=>{try{const p=await exportPacket();if(!p)return;const cols=["object","field","expected","observed","status","evidence","owner","next_action","review_state","closure_evidence","closed_at","note"];const html='<!doctype html><html lang="en"><meta charset="utf-8"><title>ClinicOps review packet</title><style>body{font:16px system-ui;margin:2rem}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #bbb;padding:.5rem;text-align:left;overflow-wrap:anywhere}p{overflow-wrap:anywhere}</style><h1>ClinicOps review packet</h1><p>'+esc(p.boundary)+'</p><p>Self-reported review dispositions; no authenticated approval or independent evidence verification.</p><p>Rules: '+esc(p.rules_version)+' · Compared: '+esc(p.generated_at)+'</p><p>Input SHA-256: '+p.input_sha256+'</p><p>JSON packet SHA-256: '+p.packet_sha256+'</p><table><thead><tr>'+cols.map(c=>'<th>'+esc(c.replaceAll('_',' '))+'</th>').join('')+'</tr></thead><tbody>'+p.findings.map(r=>'<tr>'+cols.map(c=>'<td>'+esc(r[c]??'—')+'</td>').join('')+'</tr>').join('')+'</tbody></table></html>';dl("clinicops-review-report.html",html,"text/html")}catch(e){$("packet_info").textContent=e.message}};
const CSV_HEAD=["object","field","expected","observed","status","evidence","owner","next_action","review_state","note","closure_evidence","closed_at"];
function csvOf(rows){const q=RE.csvCell;return CSV_HEAD.join(",")+"\n"+rows.map(r=>CSV_HEAD.map(h=>q(r[h])).join(",")).join("\n")+"\n"}
$("x_csv").onclick=()=>{if(!last)return;dl("clinicops-integrity-exceptions.csv",csvOf(rowsStore.filter(r=>r.status!=="aligned"&&r.status!=="not applicable")),"text/csv")};
function wbMsg(t){$("wb_msg").textContent=t}
$("wb_export_sel").onclick=()=>{if(!table)return;const sel=table.getSelectedData();if(!sel.length){wbMsg("No rows selected. Tick the checkbox on one or more rows (or the header checkbox) first.");return}wbMsg("");dl("clinicops-integrity-selected.csv",csvOf(sel.map(d=>rowsStore[d._i]||d)),"text/csv")};
$("wb_apply_owner").onclick=()=>{if(!table)return;const v=tr($("wb_owner").value);if(!v){wbMsg("Enter an owner name first.");return}const selRows=table.getSelectedRows();if(!selRows.length){wbMsg("No rows selected. Tick the checkbox on one or more rows (or the header checkbox) first.");return}wbMsg(`Owner set on ${selRows.length} row(s).`);selRows.forEach(row=>{row.update({owner:v});const d=row.getData();if(rowsStore[d._i])rowsStore[d._i].owner=v})};
$("wb_search").addEventListener("input",applyFilters);$("wb_status").addEventListener("change",applyFilters);
$("wb_group").addEventListener("change",()=>{if(table){const g=$("wb_group").value;g?table.setGroupBy(g):table.setGroupBy(false)}});
$("x_copy").onclick=async()=>{if(!last)return;const s=last.summary;const ex=last.findings.filter(r=>r.status!=="aligned"&&r.status!=="not applicable");const text=[`ClinicOps integrity scan (${last.mode})`,`Aligned: ${s.aligned} | Mismatch signals: ${s["mismatch signal"]+s["conflicting evidence"]} | Missing evidence: ${s["missing evidence"]} | Qualified review: ${s["requires qualified review"]+s.unresolved}`,"Exception queue:",...ex.map((r,i)=>`${i+1}. ${r.object} — ${r.field}: ${r.status}. ${r.next_action}${r.owner?` (owner: ${r.owner})`:""}`),`Boundary: ${BOUNDARY}`].join("\n");try{await navigator.clipboard.writeText(text)}catch(_){}};
// Print: show the plain findings table (prints fully and fits A4) instead of the virtualised grid.
window.addEventListener("beforeprint",()=>{if(table)$("rows").innerHTML=plainRows(rowsStore.filter(r=>r.status!=="not applicable"))});
// ---------- Mode switching ----------
function setMode(m){$("modeA").setAttribute("aria-pressed",m==="A");$("modeB").setAttribute("aria-pressed",m==="B");$("paneA").hidden=m!=="A";$("paneB").hidden=m!=="B";$("modeC").setAttribute("aria-pressed",m==="C");$("paneC").hidden=m!=="C";invalidate("Run the selected mode to create a new review packet.")}
$("modeA").onclick=()=>setMode("A");$("modeB").onclick=()=>setMode("B");$("modeC").onclick=()=>setMode("C");
function invalidate(message="Inputs changed. Run the comparison again before exporting."){
 ++runEpoch;last=null;rowsStore=[];if(table){table.destroy();table=null}$("grid").innerHTML="";$("rows").innerHTML='<tr><td colspan="8">'+esc(message)+'</td></tr>';$("plainwrap").hidden=false;$("wb_toolbar").hidden=true;
 $("summary").textContent=message;$("badge").textContent="NOT RUN";$("badge").className="badge";$("resultTitle").textContent="Scan result";$("queue").innerHTML='<li>No current review packet.</li>';$("packet_info").textContent="";$("review_row").innerHTML="";$("review_message").textContent="";for(const id of ["mAligned","mMismatch","mMissing","mReview"])$(id).textContent="0";
}
for(const id of ["paneA","paneB","paneC"]){$(id).addEventListener("input",()=>invalidate());$(id).addEventListener("change",()=>invalidate())}
function syncReviewForm(){const r=rowsStore[Number($("review_row").value)];if(!r)return;for(const[k,id]of [["owner","review_owner"],["next_action","review_action"],["closure_evidence","review_evidence"],["note","review_note"],["review_state","review_state"]])$(id).value=r[k]|| (k==="review_state"?"open":"")}
$("review_row").onchange=syncReviewForm;
$("review_save").onclick=()=>{if(!last)return;const i=Number($("review_row").value),r=rowsStore[i];try{const next=RE.review(r,{owner:tr($("review_owner").value),next_action:tr($("review_action").value),closure_evidence:tr($("review_evidence").value),note:tr($("review_note").value),review_state:$("review_state").value});Object.assign(r,next);if(table){const found=table.getRows().find(x=>x.getData()._i===i);if(found)found.update({...r})}$("rows").innerHTML=plainRows(rowsStore);$("review_message").textContent="Review disposition saved locally. Export to retain it."}catch(e){$("review_message").textContent=e.message}};
const matrixExample={source:{id:"fictional-source",description:"Fictional trade-name change",fields:{tradeName:"Exempla Flow X",basicUdiDi:"FIC-BASIC-001"},evidence:{id:"FIC-CHG-42",sourceName:"Fictional approved change",pageOrSection:"section 2"}},surfaces:[{id:"register",name:"Fictional register export"},{id:"ifu",name:"Fictional IFU"},{id:"sscp",name:"Fictional SS(C)P"},{id:"label",name:"Fictional label"}],scope:[{surfaceId:"register",field:"tradeName"},{surfaceId:"ifu",field:"tradeName"},{surfaceId:"sscp",field:"tradeName"},{surfaceId:"label",field:"tradeName"},{surfaceId:"register",field:"basicUdiDi"}],observations:[{surfaceId:"register",field:"tradeName",observed:"Exempla Flow X",evidence:"Fictional export row 1"},{surfaceId:"ifu",field:"tradeName",observed:"Exempla Flow",evidence:"Fictional IFU page 1"},{surfaceId:"label",field:"tradeName",observed:"Exempla Flow X",evidence:"Fictional artwork C"},{surfaceId:"register",field:"basicUdiDi",observed:"FIC-BASIC-001",evidence:"Fictional export row 1"}],owners:{ifu:"Document Control",sscp:"Regulatory Affairs"}};
$("c_example").onclick=()=>{matrixRead++;invalidate();$("c_input").value=JSON.stringify(matrixExample,null,2);$("fictionalNote").hidden=false;$("c_message").textContent="Fictional sample loaded. Five declared checks: three aligned, one mismatch and one missing observation."};
$("c_choose").onclick=()=>$("c_file").click();
$("c_file").onchange=async e=>{const read=++matrixRead;invalidate();const f=e.target.files?.[0];e.target.value="";if(!f)return;try{if(f.size>5000000)throw new Error("Use a matrix JSON file smaller than 5 MB.");const contents=await f.text();if(read!==matrixRead)return;invalidate();$("c_input").value=contents;$("fictionalNote").hidden=true;$("c_message").textContent="File read locally. Compare to validate the matrix."}catch(err){$("c_message").textContent=err.message}};
$("c_input").addEventListener("input",()=>{matrixRead++});
$("c_run").onclick=async()=>{matrixRead++;invalidate();const epoch=runEpoch;try{if($("c_input").value.length>5000000)throw new Error("Use a matrix smaller than 5 MB.");const input=JSON.parse($("c_input").value),result=await RE.compare(input);if(epoch!==runEpoch)return;render("C",result.findings,{input_snapshot:result.input_snapshot,input_sha256:result.input_sha256,scope_policy:result.scope_policy});$("c_message").textContent=result.scope_policy}catch(e){if(epoch===runEpoch){$("c_message").textContent="Cannot compare: "+e.message;invalidate("Matrix validation failed. Correct the input and run again.")}}};

// ---------- MODE A: single change ----------
const A_DEFAULT=[["IFU","IFU-12","","Document Control"],["EUDAMED export","IFU-11","","Regulatory Affairs"],["SS(C)P","","",""],["Label / artwork","IFU-12","",""]];
$("a_records").innerHTML=A_DEFAULT.map((d,j)=>{const i=j+1;return `<div class="record"><div class="record-head"><strong>Record ${i}</strong><label class="scope"><input id="as${i}" type="checkbox" aria-label="Record ${i} in scope" checked> in scope</label></div><div class="field"><label for="an${i}">Record / surface</label><input id="an${i}" value="${esc(d[0])}"></div><div class="field"><label for="av${i}">Observed value</label><input id="av${i}" value="${esc(d[1])}" placeholder="enter observation"></div><div class="field"><label for="ae${i}">Evidence reference</label><input id="ae${i}" value="${esc(d[2])}" placeholder="file, section, export date, ticket…"></div><div class="field"><label for="ao${i}">Owner if review is needed</label><input id="ao${i}" value="${esc(d[3])}" placeholder="role or team"></div></div>`}).join("");
function aNorm(v,m){const s=tr(v);return m==="relaxed"?s.replace(/\s+/g," ").toLowerCase():m==="exact"?T(v):s}
function aRun(){
 invalidate();
 const field=tr($("a_field").value)||"Declared field",ref=T($("a_ref").value),mode=$("a_mode").value,refev=tr($("a_refev").value)||null,change=tr($("a_change").value)||null;
 if(!tr(ref)){$("badge").textContent="REFERENCE NEEDED";$("badge").className="badge hold";$("resultTitle").textContent="Reference needed";$("summary").textContent="Choose an approved reference before interpreting downstream records.";return}
 const rn=aNorm(ref,mode),rows=[];
 for(let i=1;i<=4;i++){
  const inScope=$(`as${i}`).checked,name=tr($(`an${i}`).value)||`Record ${i}`,obs=T($(`av${i}`).value),ev=tr($(`ae${i}`).value)||null,owner=tr($(`ao${i}`).value)||null;
  let status,next;
  if(!inScope){status="not applicable";next="none"}
  else if(!tr(obs)){status="missing evidence";next="Obtain an observation with an evidence reference before interpreting propagation."}
  else if(aNorm(obs,mode)===rn){status="aligned";next=ev?"none":"Attach or cite the observation evidence for the closure record."}
  else{status="mismatch signal";next="Reconcile against the approved reference and record the disposition through change control."}
  rows.push({object:name,field,expected:ref,observed:obs||null,status,evidence:ev,owner,next_action:next});
 }
 if(!refev)rows.push({object:$("a_reflabel").value||"Approved reference",field,expected:ref,observed:ref,status:"requires qualified review",evidence:null,owner:null,next_action:"Attach or cite evidence for the approved reference itself."});
 if(!rows.some(r=>r.status!=="not applicable"&&r.status!=="requires qualified review")){invalidate("No downstream records are in scope. Declare at least one record before comparing.");return}
 const snapshot={field,reference:{value:ref,evidence:refev,label:$("a_reflabel").value},change,rule:mode,records:rows.map(r=>({...r}))};
 render("A",rows,{input_snapshot:snapshot,change_id:change,reference:{label:tr($("a_reflabel").value)||"Approved reference",value:ref,evidence_ref:refev},comparison_rule:mode});
}
$("a_run").onclick=()=>{$("fictionalNote").hidden=true;aRun()};
$("a_example").onclick=()=>{$("a_field").value="IFU revision";$("a_ref").value="IFU-12";$("a_reflabel").value="Approved ECO";$("a_refev").value="ECO-2026-041 §3.2";$("a_change").value="CHG-2417";$("a_mode").value="trim";
 [["IFU","IFU-12","DMS/IFU-12.pdf rev 12","Document Control"],["EUDAMED export","IFU-11","Export 2026-09-14 row 188","Regulatory Affairs"],["SS(C)P","IFU-12","SSCP-v7 §1.1","Regulatory Affairs"],["Label / artwork","IFU-12","ART-8812 rev C","Artwork Control"]].forEach((v,j)=>{const i=j+1;$(`as${i}`).checked=true;$(`an${i}`).value=v[0];$(`av${i}`).value=v[1];$(`ae${i}`).value=v[2];$(`ao${i}`).value=v[3]});
 $("fictionalNote").hidden=false;aRun()};
$("a_clear").onclick=()=>{invalidate("Observations cleared. Run again after entering evidence.");for(let i=1;i<=4;i++){$(`av${i}`).value="";$(`ae${i}`).value="";$(`ao${i}`).value=""}$("a_refev").value="";$("fictionalNote").hidden=true};
// ---------- MODE B: portfolio scan (device/UDI reconciliation v1) ----------
const OBJECTS=[["basic_udi_di","Basic UDI-DI"],["udi_di","UDI-DI"],["trade_name","Device trade name"],["model_ref","Model / catalogue no."],["risk_class","Risk class"],["manufacturer_srn","Manufacturer SRN"],["ar_srn","AR SRN"],["emdn","EMDN code"],["certificate_no","Certificate number"],["sscp_ref","SS(C)P reference"],["doc_version","Document version"],["language","Language"],["record_status","Record status"],["source_system","Source system"],["source_role","Source role (authoritative / observed)"],["evidence_ref","Evidence reference"],["evidence_date","Evidence date / as-of"],["owner","Accountable owner"]];
const COMPARE_FIELDS=["trade_name","model_ref","risk_class","manufacturer_srn","ar_srn","emdn","certificate_no","sscp_ref","doc_version"];
let bData=null;
function parseCSV(text){
 const rows=[];let row=[],cell="",q=false;
 for(let i=0;i<text.length;i++){const c=text[i];
  if(q){if(c==='"'){if(text[i+1]==='"'){cell+='"';i++}else q=false}else cell+=c}
  else if(c==='"')q=true;
  else if(c===","){row.push(cell);cell=""}
  else if(c==="\n"||c==="\r"){if(c==="\r"&&text[i+1]==="\n")i++;row.push(cell);cell="";if(row.length>1||tr(row[0]))rows.push(row);row=[]}
  else cell+=c}
 if(cell.length||row.length){row.push(cell);if(row.length>1||tr(row[0]))rows.push(row)}
 if(!rows.length)return null;
 const headers=rows[0].map(h=>tr(h));
 const warnings=[];
 const dups=[...new Set(headers.filter((h,i)=>headers.indexOf(h)!==i))];
 if(dups.length)warnings.push(`Duplicate column header(s): ${dups.map(d=>'"'+d+'"').join(", ")}. Only the last column of each name is read; rename them in the source file so no value is silently dropped.`);
 const ragged=rows.slice(1).map((r,i)=>r.length!==headers.length?i+2:0).filter(Boolean);
 if(ragged.length)warnings.push(`${ragged.length} row(s) do not have ${headers.length} cells (file rows ${ragged.slice(0,8).join(", ")}${ragged.length>8?", …":""}). Missing cells are treated as empty and extra cells are ignored; check the source file.`);
 if(headers.length===1&&/[;\t|]/.test(headers[0]))warnings.push("Only one column was detected. The file looks semicolon-, tab- or pipe-delimited; this tool reads comma-separated CSV. Re-save it as comma-separated CSV (or XLSX) and parse again.");
 if(rows.length===1)warnings.push("The file has a header row but no data rows, so there is nothing to compare.");
 return{headers,warnings,rows:rows.slice(1).map(r=>{const o={};headers.forEach((h,i)=>o[h]=tr(r[i]??""));return o})}
}
function parseInput(text){
 const t=tr(text);if(!t)return null;
 if(t[0]==="["||t[0]==="{"){try{let j=JSON.parse(t);if(!Array.isArray(j))j=[j];const headers=[...new Set(j.flatMap(o=>Object.keys(o)))];return{headers,rows:j.map(o=>{const r={};headers.forEach(h=>r[h]=tr(T(o[h]??"")));return r})}}catch(e){return{error:"JSON parse failed: "+e.message}}}
 return parseCSV(t)||{error:"No rows found"};
}
const GUESS={basic_udi_di:/basic/i,udi_di:/^(?!.*basic).*udi/i,trade_name:/trade|device.*name|product.*name/i,model_ref:/model|catalog(?:ue)?|article|^ref(?:erence)?(?:_?(?:no|number|nr))?$/i,risk_class:/class/i,manufacturer_srn:/(manufacturer|mf).*srn|^srn$/i,ar_srn:/ar.*srn|authori/i,emdn:/emdn|nomencl/i,certificate_no:/cert/i,sscp_ref:/sscp|ssp/i,doc_version:/version|revision|rev\b/i,language:/lang/i,record_status:/status/i,source_system:/system|source(?!.*role)(?!.*url)(?!.*date)/i,source_role:/role/i,evidence_ref:/evidence(?!.*date)|url|link|proof/i,evidence_date:/date|as.?of/i,owner:/owner|responsible/i};
function showMapping(){
 $("b_maprows").innerHTML=OBJECTS.map(([id,label])=>{
  const guess=bData.headers.find(h=>GUESS[id]&&GUESS[id].test(h))||"";
  return `<div class="maprow"><label for="map_${id}" style="margin:0">${esc(label)}</label><select id="map_${id}"><option value="">— not present —</option>${bData.headers.map(h=>`<option${h===guess?" selected":""}>${esc(h)}</option>`).join("")}</select></div>`}).join("");
 $("b_parseinfo").textContent=`Parsed ${bData.rows.length} rows × ${bData.headers.length} columns locally. Map the columns that exist; unmapped objects are skipped, never guessed. Mapping "Source role" lets the scan compare observed records against your declared authoritative source instead of only flagging differences.`;
 const warns=[...(bData.warnings||[])];
 if(bData.headers.some(h=>h.includes("\uFFFD"))||bData.rows.some(r=>Object.values(r).some(v=>v.includes("\uFFFD"))))warns.push("Some characters could not be decoded (shown as �). The file is probably not UTF-8 (for example Windows-1252 or Latin-1). Re-save it as UTF-8 CSV or XLSX so names such as æ, ø and å are compared correctly.");
 if(warns.length)$("b_parseinfo").textContent+=" Check before running: "+warns.join(" ");
 $("b_mapping").hidden=false;
 try{profRefresh()}catch(_){/*not yet defined*/}
}
$("b_input").addEventListener("input",()=>{portfolioRead++;bData=null;$("b_mapping").hidden=true});
$("b_choose").onclick=()=>$("b_file").click();
let bXW=null,bXName="";
async function handleXlsx(f){
 const read=++portfolioRead;invalidate();
 $("b_parseinfo").textContent="Parsing workbook locally…";$("b_mapping").hidden=false;$("b_maprows").innerHTML="";bData=null;
 try{
  const buf=await f.arrayBuffer();
  const workbook=await parseXLSX(buf);if(read!==portfolioRead)return;bXW=workbook;bXName=f.name;
  const sel=$("b_sheet");sel.innerHTML=bXW.sheets.map((n,i)=>`<option value="${i}">${esc(n)}</option>`).join("");
  $("b_sheetwrap").hidden=bXW.sheets.length<2;
  await extractSheet(0);
 }catch(e){if(read!==portfolioRead)return;bXW=null;$("b_sheetwrap").hidden=true;$("b_parseinfo").textContent="Could not read this workbook: "+(e&&e.message?e.message:e)+" Nothing was uploaded; the file was only read locally. Exporting the sheet as CSV also works."}
}
async function extractSheet(i){
 const read=++portfolioRead,workbook=bXW;bData=null;invalidate("Reading the selected worksheet. Wait before running the scan.");
 let r;try{r=await workbook.extract(i)}catch(e){if(read===portfolioRead)$("b_parseinfo").textContent="Could not read worksheet: "+e.message;return}if(read!==portfolioRead)return;
 bData={headers:r.headers,rows:r.rows};
 showMapping();
 $("b_parseinfo").textContent=`Workbook "${bXName}", sheet "${bXW.sheets[i]}": ${r.rows.length} rows × ${r.headers.length} columns parsed locally.`+(r.formulas?` ${r.formulas} formula cell(s) use their cached values — formulas are never evaluated.`:"")+(r.datesConverted?` ${r.datesConverted} Excel date serial(s) in date-named columns converted to ISO dates.`:"")+" Nothing was uploaded. Map the columns that exist; mapping \"Source role\" lets the scan compare observed records against your declared authoritative source.";
}
$("b_sheet").addEventListener("change",async ev=>{if(bXW)await extractSheet(parseInt(ev.target.value,10)||0)});
$("b_file").onchange=async ev=>{const read=++portfolioRead;bData=null;invalidate();const f=ev.target.files?.[0];if(!f)return;ev.target.value="";
 if(/\.xlsx$/i.test(f.name)){await handleXlsx(f);return}
 if(/\.xls$/i.test(f.name)){$("b_parseinfo").textContent="Legacy .xls (BIFF) is not supported — save the sheet as .xlsx or CSV first.";$("b_mapping").hidden=false;$("b_maprows").innerHTML="";bData=null;return}
 bXW=null;$("b_sheetwrap").hidden=true;const contents=await f.text();if(read!==portfolioRead)return;$("b_input").value=contents;$("b_parse").click()};
// ---- minimal fail-closed XLSX reader: ZIP + DecompressionStream + DOMParser.
// Reads cached cell values only; formulas are counted, never evaluated.
// Guardrails: 60MB file, 400 zip entries, 90MB per entry / 150MB total expanded, 20k rows.
async function parseXLSX(buf){
 const size=buf.byteLength;if(size<100)throw new Error("File too small to be a workbook.");
 if(size>60*1024*1024)throw new Error("File exceeds the 60 MB local guardrail.");
 const dv=new DataView(buf),td=new TextDecoder();
 let eocd=-1;const scanStart=Math.max(0,size-65557);
 for(let i=size-22;i>=scanStart;i--){if(dv.getUint32(i,true)===0x06054b50){eocd=i;break}}
 if(eocd<0)throw new Error("Not a valid .xlsx (zip directory not found).");
 const count=dv.getUint16(eocd+10,true),cdOff=dv.getUint32(eocd+16,true);
 if(count>400)throw new Error("Workbook has too many internal parts (guardrail).");
 const entries={};let p=cdOff,totalUnc=0;
 for(let i=0;i<count;i++){
  if(dv.getUint32(p,true)!==0x02014b50)throw new Error("Corrupt zip central directory.");
  const method=dv.getUint16(p+10,true),csize=dv.getUint32(p+20,true),usize=dv.getUint32(p+24,true),
   nlen=dv.getUint16(p+28,true),elen=dv.getUint16(p+30,true),clen=dv.getUint16(p+32,true),
   lho=dv.getUint32(p+42,true),name=td.decode(new Uint8Array(buf,p+46,nlen));
  totalUnc+=usize;
  if(usize>90*1024*1024||totalUnc>150*1024*1024)throw new Error("Workbook expands beyond local guardrails (possible zip bomb).");
  entries[name]={method,csize,lho};p+=46+nlen+elen+clen;
 }
 async function readEntry(name){const e=entries[name];if(!e)return null;
  const nlen=dv.getUint16(e.lho+26,true),elen=dv.getUint16(e.lho+28,true);
  const start=e.lho+30+nlen+elen,comp=new Uint8Array(buf,start,e.csize);
  if(e.method===0)return td.decode(comp);
  if(e.method!==8)throw new Error("Unsupported compression method in workbook.");
  if(typeof DecompressionStream==="undefined")throw new Error("This browser lacks DecompressionStream — export the sheet as CSV instead.");
  const out=await new Response(new Blob([comp]).stream().pipeThrough(new DecompressionStream("deflate-raw"))).arrayBuffer();
  if(out.byteLength>90*1024*1024)throw new Error("Workbook entry expands beyond guardrail.");
  return td.decode(out)}
 const dp=new DOMParser();
 const parseXml=(x,what)=>{const d=dp.parseFromString(x,"application/xml");if(d.getElementsByTagName("parsererror").length)throw new Error("Malformed XML in "+what+".");return d};
 const wbXml=await readEntry("xl/workbook.xml");if(!wbXml)throw new Error("No xl/workbook.xml — not an Excel workbook.");
 const wb=parseXml(wbXml,"workbook");
 const rels={};const relsXml=await readEntry("xl/_rels/workbook.xml.rels");
 if(relsXml){for(const r of parseXml(relsXml,"workbook relationships").getElementsByTagName("Relationship"))rels[r.getAttribute("Id")]=r.getAttribute("Target")}
 const RNS="http://schemas.openxmlformats.org/officeDocument/2006/relationships";
 const sheets=[...wb.getElementsByTagName("sheet")].map(sh=>({name:sh.getAttribute("name")||"Sheet",rid:sh.getAttributeNS(RNS,"id")||sh.getAttribute("r:id")}));
 if(!sheets.length)throw new Error("Workbook contains no sheets.");
 let shared=[];const ssXml=await readEntry("xl/sharedStrings.xml");
 if(ssXml){shared=[...parseXml(ssXml,"shared strings").getElementsByTagName("si")].map(si=>[...si.getElementsByTagName("t")].map(t=>t.textContent).join(""))}
 const exSerial=n=>{const ms=Math.round((n-25569)*86400000);const d=new Date(ms);return isFinite(ms)?d.toISOString().slice(0,10):String(n)};
 async function extract(idx){
  let target=rels[sheets[idx].rid]||("worksheets/sheet"+(idx+1)+".xml");
  target=target.startsWith("/")?target.slice(1):(target.startsWith("xl/")?target:"xl/"+target);
  const xml=await readEntry(target);if(!xml)throw new Error("Worksheet part missing: "+target);
  const sh=parseXml(xml,"worksheet");
  const rowsRaw=[];let formulas=0,maxc=0;
  const rowEls=sh.getElementsByTagName("row");
  if(rowEls.length>20001)throw new Error("More than 20,000 rows — split the export (local guardrail).");
  for(const r of rowEls){const cells={};
   for(const c of r.getElementsByTagName("c")){
    const ref=c.getAttribute("r")||"",m=/^([A-Z]+)/.exec(ref);if(!m)continue;
    let col=0;for(const ch of m[1])col=col*26+(ch.charCodeAt(0)-64);col--;
    if(c.getElementsByTagName("f").length)formulas++;
    const t=c.getAttribute("t")||"n";let v="";
    if(t==="inlineStr"){const is=c.getElementsByTagName("is")[0];v=is?[...is.getElementsByTagName("t")].map(x=>x.textContent).join(""):""}
    else{const ve=c.getElementsByTagName("v")[0];const raw=ve?ve.textContent:"";
     v=t==="s"?(shared[parseInt(raw,10)]??""):t==="b"?(raw==="1"?"TRUE":"FALSE"):raw}
    cells[col]=String(v);if(col+1>maxc)maxc=col+1}
   rowsRaw.push(cells)}
  const hi=rowsRaw.findIndex(rr=>Object.values(rr).some(x=>String(x).trim()));
  if(hi<0)throw new Error("Sheet is empty.");
  const headers=[];for(let cix=0;cix<maxc;cix++)headers.push(String(rowsRaw[hi][cix]??"").trim()||("column_"+(cix+1)));
  const dateCols=headers.map((h,cix)=>/date|as.?of/i.test(h)?cix:-1).filter(x=>x>=0);
  let datesConverted=0;
  const data=rowsRaw.slice(hi+1).filter(rr=>Object.values(rr).some(x=>String(x).trim())).map(rr=>{
   const o={};headers.forEach((h,cix)=>{let v=String(rr[cix]??"").trim();
    if(dateCols.includes(cix)&&/^\d{5}(\.\d+)?$/.test(v)){const n=parseFloat(v);if(n>20000&&n<80000){v=exSerial(n);datesConverted++}}
    o[h]=v});return o});
  return{headers,rows:data,formulas,datesConverted}}
 return{sheets:sheets.map(x=>x.name),extract}}
$("b_parse").onclick=()=>{portfolioRead++;invalidate();bXW=null;$("b_sheetwrap").hidden=true;const r=parseInput($("b_input").value);if(!r||r.error){$("b_parseinfo").textContent=r?r.error:"Nothing to parse.";$("b_mapping").hidden=false;$("b_maprows").innerHTML="";bData=null;return}bData=r;showMapping()};
function ident(v){return T(v).trim().replace(/^\(01\)\s*/,"").replace(/[^0-9A-Za-z]/g,"").toUpperCase()}
function mod10ok(d){let s=0;for(let i=0;i<13;i++)s+=parseInt(d[i],10)*(i%2===0?3:1);return((10-(s%10))%10)===parseInt(d[13],10)}
const CLASSVOCAB=new Set(["i","is","im","ir","iia","iib","iii","a","b","c","d"]);
function normVal(id,v){if(id==="udi_di"||id==="basic_udi_di")return ident(v);if(id==="risk_class")return v.toLowerCase().replace(/\bclass\b|\bklasse\b|\s+/g,"");return v.normalize("NFKC").replace(/\s+/g," ").trim().toLowerCase()}
function bRun(){
 invalidate();
 if(!bData){$("b_parseinfo").textContent="Parse the data first.";return}
 const map={};for(const[id]of OBJECTS){const v=$(`map_${id}`)?.value;if(v)map[id]=v}
 const get=(r,id)=>map[id]?tr(r[map[id]]):null;
 const fl=id=>OBJECTS.find(o=>o[0]===id)[1];
 const rows=[];
 const label=(r,i)=>{const sys=get(r,"source_system");const t=get(r,"trade_name")||get(r,"udi_di")||`Row ${i+2}`;return sys?`${t} [${sys}]`:t};
 const roleOf=r=>{if(!map.source_role)return null;const v=(get(r,"source_role")||"").toLowerCase();return v?(/^auth/.test(v)?"authoritative":"observed"):null};
 // per-row presence & structure checks
 bData.rows.forEach((r,i)=>{
  const obj=label(r,i),owner=get(r,"owner")||null,ev=get(r,"evidence_ref")||null,evd=get(r,"evidence_date")||null;
  for(const[id,fname]of OBJECTS){
   if(!map[id]||["owner","evidence_ref","evidence_date","source_role","source_system","record_status"].includes(id))continue;
   const v=tr(r[map[id]]);
   if(!v){rows.push({object:obj,field:fname,expected:"value present",observed:null,status:"missing evidence",evidence:ev,owner,next_action:"Obtain the value or record why it is not applicable for this record."});continue}
   if(id==="udi_di"){const d=ident(v);if(/^\d{14}$/.test(d)&&!mod10ok(d))rows.push({object:obj,field:fname,expected:"valid GS1 check digit",observed:v,status:"mismatch signal",evidence:ev,owner,next_action:"Verify the UDI-DI against the issuing-agency record; correct through change control."})}
   if(id==="risk_class"){const c=normVal(id,v);if(!CLASSVOCAB.has(c))rows.push({object:obj,field:fname,expected:"recognised class notation",observed:v,status:"requires qualified review",evidence:ev,owner,next_action:"Confirm the class notation with the regulatory owner; unrecognised vocabulary is never auto-corrected."})}
  }
  if(map.evidence_ref&&!ev)rows.push({object:obj,field:"Evidence reference",expected:"evidence reference present",observed:null,status:"missing evidence",evidence:null,owner,next_action:"Attach or cite the evidence source for this record."});
  if(map.evidence_date&&!evd)rows.push({object:obj,field:"Evidence date / as-of",expected:"evidence date present",observed:null,status:"missing evidence",evidence:ev,owner,next_action:"Record when this evidence was exported or observed — comparisons without an as-of date are not defensible."});
 });
 // value alignment
 if(map.basic_udi_di){
  const groups={};
  bData.rows.forEach((r,i)=>{const k=ident(r[map.basic_udi_di]||"");if(!k)return;(groups[k]=groups[k]||[]).push({r,i})});
  for(const[k,members]of Object.entries(groups)){
   const gname=`Basic UDI-DI ${k}`;
   if(map.source_role){
    const auth=members.filter(m=>roleOf(m.r)==="authoritative"),obs=members.filter(m=>roleOf(m.r)!=="authoritative");
    if(!auth.length){rows.push({object:gname,field:"Authoritative source",expected:"one declared authoritative record",observed:"none declared",status:"unresolved",evidence:null,owner:null,next_action:"Declare which source system is authoritative for this Basic UDI-DI before differences can be dispositioned."});continue}
    for(const fid of COMPARE_FIELDS){
     if(!map[fid])continue;
     const refVals=[...new Set(auth.map(m=>normVal(fid,tr(m.r[map[fid]]||""))).filter(Boolean))];
     if(refVals.length>1){rows.push({object:gname,field:fl(fid),expected:"one authoritative value",observed:auth.map(m=>tr(m.r[map[fid]])).filter(Boolean).join(" vs "),status:"conflicting evidence",evidence:null,owner:null,next_action:"Authoritative sources disagree — resolve the source of truth with the accountable owner before downstream comparison."});continue}
     if(!refVals.length)continue;
     const refShown=auth.map(m=>tr(m.r[map[fid]])).find(Boolean);
     for(const m of obs){
      const v=tr(m.r[map[fid]]||"");if(!v)continue;
      const ok=normVal(fid,v)===refVals[0];
      rows.push({object:label(m.r,m.i),field:fl(fid),expected:refShown,observed:v,status:ok?"aligned":"mismatch signal",evidence:get(m.r,"evidence_ref"),owner:get(m.r,"owner"),next_action:ok?"none":"Reconcile the observed record against the authoritative value and record the disposition through change control."});
     }
    }
   }else{
    for(const fid of COMPARE_FIELDS){
     if(!map[fid])continue;
     const vals={};members.forEach(m=>{const v=tr(m.r[map[fid]]||"");if(v)(vals[normVal(fid,v)]=vals[normVal(fid,v)]||[]).push(v)});
     const keys=Object.keys(vals);
     if(keys.length>1)rows.push({object:gname,field:fl(fid),expected:"one value per Basic UDI-DI",observed:keys.map(k2=>vals[k2][0]).join(" vs "),status:"conflicting evidence",evidence:null,owner:null,next_action:"No source role declared, so neither value can be treated as the reference. Identify the controlled source of truth and align every divergent record."});
     else if(keys.length===1&&members.length>1)rows.push({object:gname,field:fl(fid),expected:vals[keys[0]][0],observed:vals[keys[0]][0],status:"aligned",evidence:null,owner:null,next_action:"none"});
    }
   }
  }
 }
 // duplicate UDI-DI within the same system/role
 if(map.udi_di){const seen={};bData.rows.forEach((r,i)=>{const d=ident(r[map.udi_di]);if(!d)return;const key=d+"|"+(get(r,"source_system")||"")+"|"+(roleOf(r)||"");(seen[key]=seen[key]||[]).push(i)});
  for(const[key,idx]of Object.entries(seen))if(idx.length>1){const d=key.split("|")[0];rows.push({object:`UDI-DI ${d}`,field:"Duplicate records",expected:"one record per UDI-DI per source",observed:`${idx.length} rows (${idx.map(i=>i+2).join(", ")})`,status:"conflicting evidence",evidence:null,owner:null,next_action:"Determine which record is current; merge or retire duplicates through change control."})}}
 render("B",rows,{input_snapshot:{rows:bData.rows,mapping:map,worksheet:bXW?bXW.sheets[Number($("b_sheet").value)||0]:null},row_count:bData.rows.length,mapped_objects:Object.keys(map)});
 if(!rows.length){const badge=$("badge");badge.textContent="NOTHING COMPARED";badge.className="badge review";$("resultTitle").textContent="Nothing was compared";
  $("summary").textContent=!bData.rows.length?"The file has no data rows, so nothing was compared. This is not a result about your records.":"No comparisons could be made from the mapped columns (map Basic UDI-DI plus at least one field to compare, and check the file has values). This is not a result about your records.";
  $("queue").innerHTML='<li class="muted">Nothing was compared, so there is no queue.</li>';last=null}
}
// ---- local mapping profiles (convenience configuration, not regulatory evidence) ----
const PROF_KEY="clinicops.scanner.mappingProfiles";
function profRead(){try{return JSON.parse(localStorage.getItem(PROF_KEY)||"{}")||{}}catch(_){return{}}}
function profWrite(o){try{localStorage.setItem(PROF_KEY,JSON.stringify(o))}catch(_){/*storage unavailable*/}}
function profRefresh(){const o=profRead();const sel=$("prof_list");const cur=sel.value;
 sel.innerHTML='<option value="">— saved profiles —</option>'+Object.keys(o).sort().map(n=>`<option${n===cur?" selected":""}>${esc(n)}</option>`).join("")}
function currentMap(){const m={};for(const[id]of OBJECTS){const v=$(`map_${id}`)?.value;if(v)m[id]=v}return m}
$("prof_save").onclick=()=>{const n=tr($("prof_name").value);if(!n||!bData)return;const o=profRead();const now=new Date().toISOString();
 o[n]={name:n,schema_version:1,created:o[n]?.created||now,updated:now,source_system:n,map:currentMap()};profWrite(o);profRefresh();$("prof_list").value=n};
$("prof_apply").onclick=()=>{invalidate();const n=$("prof_list").value;if(!n||!bData)return;const p=profRead()[n];if(!p||!p.map)return;
 for(const[id]of OBJECTS){const el=$(`map_${id}`);if(!el)continue;const want=p.map[id]||"";el.value=bData.headers.includes(want)?want:""}};
$("prof_delete").onclick=()=>{const n=$("prof_list").value;if(!n)return;const o=profRead();delete o[n];profWrite(o);profRefresh()};
$("prof_export").onclick=()=>{dl("clinicops-mapping-profiles.json",JSON.stringify({tool:"clinicops-regulatory-integrity-scanner",kind:"mapping-profiles",schema_version:1,exported_at:new Date().toISOString(),profiles:profRead()},null,2)+"\n","application/json")};
$("prof_import").onclick=()=>$("prof_file").click();
$("prof_file").onchange=async ev=>{const f=ev.target.files?.[0];ev.target.value="";if(!f)return;
 try{const j=JSON.parse(await f.text());const inc=j&&j.kind==="mapping-profiles"&&j.profiles?j.profiles:null;if(!inc)throw 0;
  const o=profRead();for(const[n,p]of Object.entries(inc)){if(p&&p.map&&typeof p.map==="object")o[String(n).slice(0,80)]={name:String(n).slice(0,80),schema_version:1,created:p.created||new Date().toISOString(),updated:new Date().toISOString(),map:Object.fromEntries(Object.entries(p.map).filter(([k,v])=>typeof v==="string").slice(0,64))}}
  profWrite(o);profRefresh()}catch(_){$("b_parseinfo").textContent="That file is not a ClinicOps mapping-profile export."}};
try{profRefresh()}catch(_){/*noop*/}
$("b_run").onclick=()=>{$("fictionalNote").hidden=true;bRun()};
$("b_example").onclick=()=>{
 $("b_input").value=[
"basic_udi_di,udi_di,trade_name,model,risk_class,manufacturer_srn,certificate_no,source_system,source_role,evidence_ref,evidence_date,owner",
"FICBU0AAX01,09506000134352,Exempla Flow Monitor,EX-100,IIb,DK-MF-000099999,CERT-1001,RIM,authoritative,RIM export r441,2026-09-10,RA Ops",
"FICBU0AAX01,09506000134352,Exempla Flow Monitor,EX-100,IIb,DK-MF-000099999,CERT-1001,EUDAMED,observed,Public record extract,2026-09-12,RA Ops",
"FICBU0AAX02,09506000134369,Exempla Flow Monitor Pro,EX-200,IIb,DK-MF-000099999,CERT-1001,RIM,authoritative,RIM export r441,2026-09-10,RA Ops",
"FICBU0AAX02,09506000134369,Exempla Flow Monitor Plus,EX-200,IIb,DK-MF-000099999,CERT-1001,EUDAMED,observed,Public record extract,2026-09-12,RA Ops",
"FICBU0AAX03,09506000134390,Exempla Sense Patch,EX-300,Class 2b,DK-MF-000099999,CERT-1002,Label register,observed,Row 44,,QA",
"FICBU0AAX04,09506000134412,Exempla Dose Assist,EX-500,IIb,DK-MF-000099999,CERT-1003,RIM,authoritative,RIM export r441,2026-09-10,RA Ops"].join("\n");
 const r=parseInput($("b_input").value);bData=r;showMapping();$("fictionalNote").hidden=false;bRun();
};
})();
