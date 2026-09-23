// ClinicOps E2E - full Regulatory Integrity Scanner journey (complements scanner_journey.mjs).
// import -> column mapping (auto + manual) -> reconciliation -> exception review
// (owner / next action / review state) -> exports (machine + human readable) -> scope-request route,
// at 1440 and 390 wide, light and dark; keyboard-only completion; failure paths for bad
// fixtures; missing/conflicting evidence; export well-formedness + interpretation boundary;
// and a "nothing leaves the page" network audit. Also a first-time-user ("naive") path.
//
// Run:  E2E_BASE_URL=http://localhost:8103 node e2e/scanner_full_journey.mjs   (serve docs/ first)
// Env:  E2E_SHOTS (default /tmp/scanner-shots), E2E_PROXY, E2E_CHROMIUM as in scanner_journey.mjs.
import { chromium } from "playwright";
import fs from "fs";
import os from "os";
import path from "path";
import { execFileSync } from "child_process";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const SHOTS = process.env.E2E_SHOTS || "/tmp/scanner-shots";
const FX = new URL("../examples/scanner-fixtures/", import.meta.url).pathname;
fs.mkdirSync(SHOTS, { recursive: true });
const results = [];
const ok = (name, cond, detail = "") => {
  results.push([cond ? "PASS" : "FAIL", name, cond ? "" : detail]);
  if (!cond) process.exitCode = 1;
};
const info = (name, detail) => results.push(["INFO", name, detail]);

const browser = await chromium.launch({
  proxy: process.env.E2E_PROXY ? { server: process.env.E2E_PROXY } : undefined,
  executablePath: process.env.E2E_CHROMIUM || undefined,
});
const t0 = Date.now();
const ORIGIN = new URL(BASE).origin;
const VERDICT = /\b(non-?compliant|compliant|passes? compliance|fails? compliance|approved for|safe to)\b/i;
const BOUNDARY_RE = /not compliance determinations/i;

// ---- helpers ---------------------------------------------------------------
async function newPage(w, h, scheme) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, acceptDownloads: true });
  await ctx.grantPermissions(["clipboard-read", "clipboard-write"], { origin: ORIGIN }).catch(() => {});
  const page = await ctx.newPage();
  page.errors = [];
  page.reqs = [];
  page.on("pageerror", (e) => page.errors.push("pageerror: " + String(e).slice(0, 200)));
  page.on("console", (m) => { if (m.type() === "error") page.errors.push("console: " + m.text().slice(0, 200)); });
  page.on("request", (r) => page.reqs.push({ method: r.method(), url: r.url(), post: r.postData() }));
  return page;
}
const goScanner = async (p) => { await p.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" }); };
const info_ = (p) => p.textContent("#b_parseinfo");
async function loadFile(p, file) {
  await p.click("#modeB");
  await p.setInputFiles("#b_file", file.startsWith("/") ? file : FX + file);
  await p.waitForFunction(() => document.getElementById("b_parseinfo").textContent.length > 0, null, { timeout: 8000 });
}
async function runScan(p) {
  await p.click("#b_run");
  await p.waitForFunction(() => document.getElementById("badge").textContent !== "NOT RUN", null, { timeout: 15000 });
  await p.waitForSelector("#grid .tabulator-row, #rows tr", { timeout: 15000 }).catch(() => {});
}
const queue = (p) => p.$$eval("#queue li", (ls) => ls.map((l) => l.textContent.trim()));
const summary = (p) => p.textContent("#summary");
const saveDl = async (p, action) => {
  const [d] = await Promise.all([p.waitForEvent("download", { timeout: 10000 }), action()]);
  return fs.readFileSync(await d.path(), "utf8");
};
function parseCsv(t) { // small RFC-4180 reader for export well-formedness
  const rows = []; let r = [], c = "", q = false;
  for (let i = 0; i < t.length; i++) { const ch = t[i];
    if (q) { if (ch === '"') { if (t[i + 1] === '"') { c += '"'; i++; } else q = false; } else c += ch; }
    else if (ch === '"') q = true; else if (ch === ",") { r.push(c); c = ""; }
    else if (ch === "\n") { r.push(c); rows.push(r); r = []; c = ""; } else c += ch; }
  if (q) throw new Error("unterminated quote");
  return rows;
}
async function tabTo(p, target, max = 160) { // keyboard-only navigation; target = element id or predicate fn
  for (let i = 0; i < max; i++) {
    const hit = typeof target === "string"
      ? await p.evaluate((id) => !!document.activeElement && document.activeElement.id === id, target)
      : await p.evaluate(target);
    if (hit) return i;
    await p.keyboard.press("Tab");
  }
  return -1;
}
const focusedIs = (id) => id;
const shot = (p, name, full = false) => p.screenshot({ path: path.join(SHOTS, name + ".png"), fullPage: full });

// ---- 1. full journey, 4 viewport/scheme combinations ------------------------
const COMBOS = [["desktop-light", 1440, 900, "light"], ["desktop-dark", 1440, 900, "dark"], ["mobile-light", 390, 844, "light"], ["mobile-dark", 390, 844, "dark"]];
const allPages = [];
for (const [tag, w, h, scheme] of COMBOS) {
  const p = await newPage(w, h, scheme); allPages.push(p);
  await goScanner(p);
  ok(`[${tag}] scanner loads with boundary callout`, /does not make compliance determinations/.test(await p.textContent(".callout")));
  // import + auto mapping (messy headers)
  await loadFile(p, "messy-headers.csv");
  ok(`[${tag}] choosing a file parses it without an extra click`, /Parsed 4 rows × 15 columns/.test(await info_(p)), await info_(p));
  const auto = await p.$$eval("#b_maprows select", (ss) => Object.fromEntries(ss.map((s) => [s.id, s.value])));
  ok(`[${tag}] messy headers auto-map`, auto.map_trade_name === "Product Name" && auto.map_basic_udi_di === "Basic UDI-DI" && auto.map_udi_di === "UDI-DI" && auto.map_risk_class === "Device Class" && auto.map_source_role === "Source Role" && auto.map_evidence_date === "As-of Date" && auto.map_owner === "Owner / Responsible" && auto.map_doc_version === "Document Revision", JSON.stringify(auto));
  await runScan(p);
  ok(`[${tag}] messy file reconciles clean`, /12 aligned, 0 mismatch\/conflict signals, 0 missing evidence/.test(await summary(p)), await summary(p));
  // manual mapping: unmap certificate + remap owner away -> fewer comparisons, no owner in queue rows
  await p.selectOption("#map_certificate_no", "");
  await p.selectOption("#map_trade_name", "Extra: internal note");
  await runScan(p);
  ok(`[${tag}] manual remap changes reconciliation (unmapped cert skipped, wrong name column flagged)`, /mismatch\/conflict signals/.test(await summary(p)) && !/12 aligned/.test(await summary(p)), await summary(p));
  await p.selectOption("#map_trade_name", "Product Name");
  await p.selectOption("#map_certificate_no", "Certificate");
  // conflicting fixture -> exception review
  await loadFile(p, "conflicting.csv");
  await runScan(p);
  const q = await queue(p);
  const qs = q.join(" | ");
  ok(`[${tag}] conflicting evidence surfaced (certificate/SS(C)P/version + authoritative disagreement)`, /Certificate number.*(mismatch signal|conflicting evidence)/.test(qs) && /conflicting evidence/.test(qs) && /SS\(C\)P reference/.test(qs) && /Document version/.test(qs), qs.slice(0, 300));
  ok(`[${tag}] no declared authority routes to unresolved/qualified review`, /Authoritative source.*(unresolved|requires qualified review)/.test(qs) || /unresolved/.test(qs), qs.slice(0, 300));
  ok(`[${tag}] duplicate UDI-DI records surfaced`, /Duplicate records: conflicting evidence/.test(qs), qs.slice(0, 300));
  ok(`[${tag}] result copy never issues a compliance verdict`, !VERDICT.test(await p.textContent(".result")), (await p.textContent(".result")).slice(0, 200));
  await shot(p, `${tag}-queue`);
  // exception review: edit owner / next action / review state / note inline in the grid
  const rowsN = await p.$$eval("#grid .tabulator-row", (r) => r.length);
  const mismatchOnly = await p.$("#wb_status");
  await p.selectOption("#wb_status", "conflicting evidence");
  await p.waitForTimeout(200);
  // Tabulator virtualises columns: bring the wanted column into view (in steps) and let it settle before editing.
  const cell = async (field) => {
    const loc = p.locator(`#grid .tabulator-row:first-child .tabulator-cell[tabulator-field="${field}"]`);
    for (let x = 0; x <= 4000 && !(await loc.count()); x += 300) { await p.evaluate((sx) => { document.querySelector("#grid .tabulator-tableholder").scrollLeft = sx; }, x); await p.waitForTimeout(60); }
    await loc.scrollIntoViewIfNeeded();
    await p.waitForTimeout(120);
    return p.locator(`#grid .tabulator-row:first-child .tabulator-cell[tabulator-field="${field}"]`);
  };
  const editText = async (field, text) => {
    const c = await cell(field); await c.dblclick();
    await p.waitForSelector("#grid .tabulator-cell.tabulator-editing input", { timeout: 3000 });
    await p.keyboard.press("Control+A"); await p.keyboard.type(text); await p.keyboard.press("Enter");
    await p.waitForTimeout(120);
  };
  await editText("owner", "RA Review Board");
  await editText("next_action", "Confirm source of truth with Certification Lead");
  await editText("note", "Reviewed by RA, evidence requested");
  await (await cell("review_state")).dblclick();
  await p.waitForTimeout(150);
  const opt = p.locator(".tabulator-edit-list .tabulator-edit-list-item", { hasText: "in review" });
  if (await opt.count()) await opt.first().click(); else await p.keyboard.press("Escape");
  await p.waitForTimeout(150);
  await p.selectOption("#wb_status", "");
  ok(`[${tag}] grid has rows for review`, rowsN > 0, "rows=" + rowsN);
  // exports
  const csvText = await saveDl(p, () => p.click("#x_csv"));
  const csv = parseCsv(csvText);
  ok(`[${tag}] exception CSV well-formed with edited owner, action, state and note`, csv[0].join(",") === "object,field,expected,observed,status,evidence,owner,next_action,review_state,note" && csv.slice(1).every((r) => r.length === 10 || (r.length === 1 && r[0] === "")) && /RA Review Board/.test(csvText) && /Confirm source of truth with Certification Lead/.test(csvText) && /in review/.test(csvText) && /Reviewed by RA/.test(csvText), csvText.slice(0, 300));
  ok(`[${tag}] exception CSV excludes aligned rows`, !csv.some((r) => r[4] === "aligned"));
  const json = JSON.parse(await saveDl(p, () => p.click("#x_json")));
  ok(`[${tag}] JSON export carries boundary, tool identity, summary and findings`, BOUNDARY_RE.test(json.boundary) && /Source authority, materiality and disposition stay with the accountable qualified owner/.test(json.boundary) && json.tool === "clinicops-regulatory-integrity-scanner" && json.mode === "portfolio-scan" && json.findings.length > 0 && typeof json.summary["conflicting evidence"] === "number" && !isNaN(Date.parse(json.generated_at)));
  ok(`[${tag}] JSON findings keep reviewer edits`, json.findings.some((f) => f.owner === "RA Review Board" && f.review_state === "in review" && /Reviewed by RA/.test(f.note)));
  ok(`[${tag}] export text has no compliance verdict`, !VERDICT.test(JSON.stringify(json.findings)) && !VERDICT.test(csvText));
  await p.click("#x_copy");
  const clip = await p.evaluate(() => navigator.clipboard.readText()).catch(() => "");
  if (clip) ok(`[${tag}] reviewer summary carries boundary`, BOUNDARY_RE.test(clip) && /Exception queue:/.test(clip), clip.slice(0, 200));
  else info(`[${tag}] clipboard unavailable`, "reviewer summary copy not asserted");
  // overflow
  const ovf = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(`[${tag}] no horizontal page scroll`, ovf <= 0, ovf + "px");
  await p.locator("#queue").scrollIntoViewIfNeeded();
  await shot(p, `${tag}-review`);
  // scope request route
  await p.locator("a.cta.primary").last().scrollIntoViewIfNeeded();
  await Promise.all([p.waitForURL(/assessment-intake\.html\?workstream=integrity-review/), p.click('a.cta.primary:has-text("Scope a review")')]);
  ok(`[${tag}] scope-request route reaches intake with workstream`, (await p.textContent("h1")).length > 0 && p.url().includes("workstream=integrity-review"), p.url());
  ok(`[${tag}] no console/page errors`, p.errors.length === 0, p.errors.join(" | "));
}

// ---- 2. keyboard-only journey (desktop light) -------------------------------
{
  const p = await newPage(1440, 900, "light"); allPages.push(p);
  await goScanner(p);
  let n = await tabTo(p, focusedIs("modeB"));
  ok("[keyboard] reach portfolio mode switch", n >= 0);
  await p.keyboard.press("Enter");
  ok("[keyboard] Enter activates portfolio mode", (await p.getAttribute("#modeB", "aria-pressed")) === "true");
  n = await tabTo(p, focusedIs("b_choose"));
  ok("[keyboard] reach file chooser button", n >= 0);
  const [fc] = await Promise.all([p.waitForEvent("filechooser"), p.keyboard.press("Enter")]);
  await fc.setFiles(FX + "conflicting.csv");
  await p.waitForFunction(() => /Parsed 8 rows/.test(document.getElementById("b_parseinfo").textContent));
  n = await tabTo(p, focusedIs("map_basic_udi_di"), 30);
  ok("[keyboard] reach mapping selects", n >= 0);
  await p.keyboard.press("ArrowDown"); await p.keyboard.press("ArrowUp"); // manual change and revert via keys
  n = await tabTo(p, focusedIs("b_run"));
  ok("[keyboard] reach Run portfolio scan", n >= 0, "tabs=" + n);
  await p.keyboard.press("Enter");
  await p.waitForSelector("#grid .tabulator-row");
  ok("[keyboard] scan ran", /Portfolio scan/.test(await summary(p)));
  // grid: header checkbox reachable and toggle with Space
  n = await tabTo(p, () => { const a = document.activeElement; return a && a.tagName === "INPUT" && a.type === "checkbox" && !!a.closest("#grid"); }, 60);
  ok("[keyboard] grid selection checkbox is reachable", n >= 0, "tabs=" + n);
  if (n >= 0) {
    await p.keyboard.press("Space");
    const sel = await p.$$eval("#grid .tabulator-row.tabulator-selected", (r) => r.length);
    info("[keyboard] Space on grid checkbox selected rows", String(sel));
  }
  // bulk owner via keyboard: use toolbar
  await p.focus("#wb_search");
  n = await tabTo(p, focusedIs("wb_owner"), 10);
  ok("[keyboard] reach bulk owner field", n >= 0);
  // select all rows through the header checkbox using keyboard
  await p.focus("#grid .tabulator-header input[type=checkbox]");
  if (!(await p.$$eval("#grid .tabulator-row.tabulator-selected", (r) => r.length))) await p.keyboard.press("Space");
  await p.focus("#wb_owner");
  await p.keyboard.type("QA Keyboard Owner");
  n = await tabTo(p, focusedIs("wb_apply_owner"), 4);
  await p.keyboard.press("Enter");
  n = await tabTo(p, focusedIs("wb_export_sel"), 4);
  const selCsv = await saveDl(p, () => p.keyboard.press("Enter"));
  ok("[keyboard] bulk owner + selected export completed without a mouse", /QA Keyboard Owner/.test(selCsv) && parseCsv(selCsv)[0].length === 10, selCsv.slice(0, 200));
  ok("[keyboard] no console/page errors", p.errors.length === 0, p.errors.join(" | "));
  await shot(p, "keyboard-final");
}

// ---- 3. failure paths ---------------------------------------------------------
{
  const p = await newPage(1440, 900, "light"); allPages.push(p);
  const cases = [
    ["bad-empty.csv", /Nothing to parse/, null],
    ["bad-headers-only.csv", /Parsed 0 rows/, /no data rows/i],
    ["bad-encoding-latin1.csv", /could not be decoded|not UTF-8/, null],
    ["bad-duplicate-headers.csv", /Duplicate column header/, null],
    ["bad-ragged.csv", /do not have 14 cells/, null],
    ["bad-semicolon.csv", /semicolon/i, null],
  ];
  for (const [f, infoRe, sumRe] of cases) {
    await goScanner(p);
    await p.click("#modeB");
    if (f === "bad-empty.csv") { await p.setInputFiles("#b_file", FX + f); await p.waitForTimeout(300); }
    else await loadFile(p, f);
    const t = await info_(p);
    ok(`[fail] ${f}: understandable parse message`, infoRe.test(t), t.slice(0, 250));
    if (f !== "bad-empty.csv") {
      await runScan(p);
      const s = await summary(p), b = await p.textContent("#badge");
      ok(`[fail] ${f}: run never reports an all-clear on unusable data`, !/NO ENTERED DIFFERENCE/.test(b) || /^(?!.*0 comparisons)/.test(s), b + " | " + s);
      if (sumRe) ok(`[fail] ${f}: says no data rows / nothing compared`, sumRe.test(s) && /NOTHING COMPARED/.test(b), b + " | " + s);
    }
    ok(`[fail] ${f}: no crash / console errors`, p.errors.length === 0, p.errors.join(" | "));
  }
  // corrupt xlsx, legacy xls, bad JSON paste, single-mode missing reference
  await goScanner(p); await p.click("#modeB");
  await p.setInputFiles("#b_file", { name: "broken.xlsx", mimeType: "application/octet-stream", buffer: Buffer.from("PK\x03\x04 this is not a workbook ".repeat(8)) });
  await p.waitForFunction(() => /Could not read this workbook/.test(document.getElementById("b_parseinfo").textContent));
  ok("[fail] corrupt xlsx: message says nothing uploaded and offers CSV", /Nothing was uploaded/.test(await info_(p)) && /CSV/.test(await info_(p)));
  await p.setInputFiles("#b_file", { name: "old.xls", mimeType: "application/vnd.ms-excel", buffer: Buffer.from("x") });
  ok("[fail] legacy .xls: explained", /Legacy \.xls/.test(await info_(p)));
  await p.fill("#b_input", "[{\"a\":1,"); await p.click("#b_parse");
  ok("[fail] invalid JSON: explained", /JSON parse failed/.test(await info_(p)));
  await p.fill("#b_input", "   "); await p.click("#b_parse");
  ok("[fail] blank paste: explained", /Nothing to parse/.test(await info_(p)));
  await p.click("#modeA"); await p.fill("#a_ref", ""); await p.click("#a_run");
  ok("[fail] single-change without reference: 'Reference needed'", /Reference needed/.test(await p.textContent("#resultTitle")) && /REFERENCE NEEDED/.test(await p.textContent("#badge")));
  ok("[fail] no console/page errors across bad inputs", p.errors.length === 0, p.errors.join(" | "));
}

// ---- 4. missing-value handling + single change ---------------------------------
{
  const p = await newPage(1440, 900, "light"); allPages.push(p);
  await goScanner(p); await loadFile(p, "missing-values.csv"); await runScan(p);
  const qs = (await queue(p)).join(" | ");
  ok("[missing] blank values become missing evidence, never filled in", /Certificate number: missing evidence/.test(qs) && /SS\(C\)P reference: missing evidence/.test(qs) && /Evidence date \/ as-of: missing evidence/.test(qs) && /Evidence reference: missing evidence/.test(qs) && /Device trade name: missing evidence/.test(qs), qs.slice(0, 400));
  ok("[missing] unrecognised class routes to qualified review", /Risk class: requires qualified review/.test(qs), qs.slice(0, 400));
  ok("[missing] blank owner prompts assignment", /assign an owner/.test(qs));
  await goScanner(p); await p.click("#a_example");
  ok("[single] fictional example: mismatch surfaced with note and boundary", /mismatch signal/.test(await p.textContent("#queue")) && (await p.isVisible("#fictionalNote")) && /not compliance determinations/.test((JSON.parse(await saveDl(p, () => p.click("#x_json")))).boundary));
  // grid guards: empty selection gives a polite visible message; owner/next action reachable without sideways scroll
  await goScanner(p); await loadFile(p, "conflicting.csv"); await runScan(p); await p.waitForTimeout(600);
  await p.click("#wb_export_sel");
  ok("[review] export selected with no rows gives a status message", /No rows selected/.test(await p.textContent("#wb_msg")) && (await p.getAttribute("#wb_msg", "role")) === "status");
  await p.fill("#wb_owner", "X"); await p.click("#wb_apply_owner");
  ok("[review] assign owner with no rows gives a status message", /No rows selected/.test(await p.textContent("#wb_msg")));
  const reach = await p.evaluate(() => { const g = document.getElementById("grid").getBoundingClientRect(); return ["owner", "next_action"].map((f) => { const c = document.querySelector(`#grid .tabulator-row .tabulator-cell[tabulator-field="${f}"]`); if (!c) return false; const r = c.getBoundingClientRect(); return r.left >= g.left && r.right <= g.right + 1; }); });
  ok("[review] Owner and Next action visible at 1440 without horizontal scrolling", reach[0] && reach[1], JSON.stringify(reach));
  ok("[review] file-input hint about delimiters is visible", await p.isVisible("#b_delimhint"));
  ok("[review] no console/page errors", p.errors.length === 0, p.errors.join(" | "));
  await goScanner(p); await p.click("#a_example");
  await p.click("#a_clear"); await p.click("#a_run");
  ok("[single] cleared observations = missing evidence", /missing evidence/.test(await p.textContent("#queue")));
}

// ---- 5. large file --------------------------------------------------------------
{
  const big = path.join(os.tmpdir(), "scanner-large-" + process.pid + ".csv");
  execFileSync("python3", [FX + "generate_fixtures.py", "large", big, "2000"]);
  const p = await newPage(1440, 900, "light"); allPages.push(p);
  await goScanner(p);
  const t1 = Date.now();
  await loadFile(p, big);
  ok("[large] 2,000 rows parsed", /Parsed 2000 rows/.test(await info_(p)), await info_(p));
  await runScan(p);
  const dt = Date.now() - t1;
  ok("[large] scan + grid completes in under 15s", dt < 15000, dt + "ms");
  info("[large] import->grid time", dt + "ms");
  ok("[large] seeded drifts are found", /mismatch\/conflict signals/.test(await summary(p)) && !/ 0 mismatch\/conflict/.test(await summary(p)) && !/ 0 missing evidence/.test(await summary(p)), await summary(p));
  await p.selectOption("#wb_status", "mismatch signal"); await p.waitForTimeout(400);
  ok("[large] status filter works on large data", (await p.$$eval("#grid .tabulator-row", (r) => r.length)) > 0);
  const csv = parseCsv(await saveDl(p, () => p.click("#x_csv")));
  ok("[large] exception CSV well-formed", csv.length > 50 && csv.filter((r) => r.length > 1).every((r) => r.length === 10));
  os.platform() && fs.rmSync(big, { force: true });
  ok("[large] no console errors", p.errors.length === 0, p.errors.join(" | "));
}

// ---- 6. naive first-time user (no docs) -----------------------------------------
{
  const p = await newPage(390, 844, "light"); allPages.push(p);
  const t = Date.now(); let clicks = 0; const friction = [];
  await goScanner(p);
  // what a newcomer sees first: is there a visible way to start without owning data?
  const startVisible = await p.isVisible("#a_example");
  if (!startVisible) friction.push("no visible sample action above the fold");
  await p.click("#modeB"); clicks++;
  await p.click("#b_example"); clicks++;
  await p.waitForSelector("#grid .tabulator-row");
  await p.waitForTimeout(900);
  const inView = await p.evaluate(() => { const r = document.getElementById("resultTitle").getBoundingClientRect(); return r.top >= 0 && r.top < innerHeight; });
  if (!inView) friction.push("after running, results are below the fold (page does not scroll to them)");
  ok("[naive] running a scan brings the result into view", inView);
  const sumTxt = await summary(p);
  ok("[naive] first useful queue in 2 clicks via the fictional example", clicks === 2 && /Portfolio scan/.test(sumTxt) && (await queue(p)).length > 0);
  // own data path: choose file, run, without pressing "Parse & map"
  await p.click("#modeB");
  await p.setInputFiles("#b_file", FX + "clean.csv"); clicks++;
  await p.waitForFunction(() => /Parsed 9 rows/.test(document.getElementById("b_parseinfo").textContent));
  await p.click("#b_run"); clicks++;
  await p.waitForFunction(() => /42 aligned/.test(document.getElementById("summary").textContent));
  ok("[naive] own file -> result with no manual parse step", /NO ENTERED DIFFERENCE/.test(await p.textContent("#badge")));
  // label check: can a newcomer tell what "aligned/qualified review" mean without docs?
  const jargon = await p.$$eval(".metric small", (s) => s.map((x) => x.textContent));
  info("[naive] result vocabulary shown", jargon.join(" / "));
  // gap: empty state before any run
  await goScanner(p);
  const empty = await p.textContent("#summary");
  ok("[naive] empty state tells the user what to do", /Run a check or scan/.test(empty));
  info("[naive] time to first result", ((Date.now() - t) / 1000).toFixed(1) + "s, clicks=" + clicks);
  info("[naive] friction", friction.length ? friction.join("; ") : "none observed");
  await shot(p, "naive-mobile-result", false);
}

// ---- 7. network audit: nothing leaves the page ------------------------------------
{
  const reqs = allPages.flatMap((p) => p.reqs);
  const bad = reqs.filter((r) => r.method !== "GET" || !r.url.startsWith(ORIGIN + "/") || r.post);
  ok("[network] every request is a same-origin GET without a body", bad.length === 0, bad.slice(0, 3).map((r) => r.method + " " + r.url).join(" | "));
  const leaks = reqs.filter((r) => /FICBU|Exempla|09506000|Review%20Board|Review Board/i.test(decodeURIComponent(r.url) + (r.post || "")));
  ok("[network] no request URL/body carries file or entered content", leaks.length === 0, leaks.slice(0, 3).map((r) => r.url).join(" | "));
  info("[network] requests audited", String(reqs.length));
  const third = reqs.filter((r) => !r.url.startsWith(ORIGIN) && !r.url.startsWith("data:") && !r.url.startsWith("blob:"));
  ok("[network] no third-party origins", third.length === 0, third.slice(0, 3).map((r) => r.url).join(" | "));
}

await browser.close();
for (const [s, n, d] of results) console.log(s, "-", n, d ? "::" + d : "");
const fails = results.filter((r) => r[0] === "FAIL").length, passes = results.filter((r) => r[0] === "PASS").length;
console.log(`RESULT: ${passes}/${passes + fails} passed in ${((Date.now() - t0) / 1000).toFixed(1)}s; screenshots in ${SHOTS}`);
if (fails) process.exit(1);
