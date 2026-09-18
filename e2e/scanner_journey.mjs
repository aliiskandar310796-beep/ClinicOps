// ClinicOps E2E — the operator journey the product is judged by (Master Directive §67/§75):
// homepage → solution → scanner → data in → minimal mapping → reconciliation →
// useful exception queue → export. Runs against production (or E2E_BASE_URL).
// Non-gating: this complements unit tests and the deploy smoke; it exists to catch
// journey-level breakage and to keep an honest time-to-first-useful-queue number.
import { chromium } from "playwright";

const BASE = process.env.E2E_BASE_URL || "https://clinicops.dk";
const results = [];
const ok = (name, cond, detail = "") => {
  results.push([cond ? "PASS" : "FAIL", name, detail]);
  if (!cond) process.exitCode = 1;
};

// Fictional fixture with Danish characters and deliberate defects:
// row 3 trade name drifts from the authoritative row (æ/ø preserved),
// row 4 has no evidence date.
const FIXTURE = [
  "basic_udi_di,udi_di,trade_name,risk_class,source_system,source_role,evidence_ref,evidence_date,owner",
  "FICBUE2E01,09506000134352,Blåbær Åndedrætsmonitor,IIb,RIM,authoritative,RIM export r9,2026-09-15,RA Ops",
  "FICBUE2E01,09506000134352,Blåbær Åndedrætsmonitor,IIb,EUDAMED,observed,Public extract,2026-09-16,RA Ops",
  "FICBUE2E01,09506000134352,Blaabær Åndedrætsmonitor,IIb,Label register,observed,Row 12,,QA",
].join("\n");

// Local/container runs can set E2E_PROXY and E2E_CHROMIUM; CI needs neither.
const browser = await chromium.launch({
  proxy: process.env.E2E_PROXY ? { server: process.env.E2E_PROXY } : undefined,
  executablePath: process.env.E2E_CHROMIUM || undefined,
});
const t0 = Date.now();
try {
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e).slice(0, 160)));

  // 1. homepage → solution → scanner
  await page.goto(BASE.startsWith("file:") ? BASE + "/index.html" : BASE + "/", { waitUntil: "load" });
  ok("homepage states the job", (await page.textContent("h1")).includes("EUDAMED"));
  await page.click('nav.primary a:has-text("Solution")');
  ok("solution page is flagship-first", (await page.textContent("h1")).includes("Regulatory Change Integrity Review"));
  await page.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });

  // 2. import → map → run
  await page.click("#modeB");
  await page.fill("#b_input", FIXTURE);
  await page.click("#b_parse");
  ok("columns auto-mapped", (await page.textContent("#b_parseinfo")).includes("Parsed 3 rows"));
  await page.click("#b_run");
  const summary = await page.textContent("#summary");
  ok("reconciliation ran", /Portfolio scan/.test(summary), summary.slice(0, 120));

  // 3. useful exceptions: the seeded trade-name drift and missing date must surface
  const queue = await page.$$eval("#queue li", (ls) => ls.map((l) => l.textContent));
  ok("Danish-character mismatch surfaced", queue.some((q) => q.includes("Device trade name") && q.includes("mismatch signal")), queue.join(" | ").slice(0, 200));
  ok("missing evidence date surfaced", queue.some((q) => q.includes("Evidence date")));
  await page.waitForSelector("#grid .tabulator-row", { timeout: 15000 }).catch(() => {});
  const findingsText = (await page.textContent("#grid").catch(() => "")) || (await page.textContent("#rows"));
  ok("verbatim Danish preserved", findingsText.includes("Blåbær") && findingsText.includes("Blaabær"));

  // 4. export round-trip
  const [dl] = await Promise.all([page.waitForEvent("download", { timeout: 8000 }), page.click("#x_json")]);
  const path = await dl.path();
  const fs = await import("fs");
  const packet = JSON.parse(fs.readFileSync(path, "utf8"));
  ok("export carries findings + boundary", Array.isArray(packet.findings) && packet.findings.length > 0 && /not compliance determinations/i.test(packet.boundary || ""));

  // 4b. XLSX: real workbook fixture (Danish sheet name, date serials, formula cell)
  await page.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });
  await page.click("#modeB");
  await page.setInputFiles("#b_file", new URL("./fixtures/portfolio.xlsx", import.meta.url).pathname);
  await page.waitForTimeout(800);
  const pinfo = await page.textContent("#b_parseinfo");
  ok("xlsx parsed locally", /Portefølje.*3 rows/.test(pinfo), pinfo.slice(0, 120));
  ok("xlsx formulas never evaluated", /never evaluated/.test(pinfo));
  ok("xlsx date serials normalized", /Excel date serial/.test(pinfo));
  await page.click("#b_run");
  await page.waitForTimeout(900);
  ok("xlsx scan produced findings", /Portfolio scan/.test(await page.textContent("#summary")));
  // workbench grid interactions
  const gridRows = await page.$$eval("#grid .tabulator-row", (rs) => rs.length).catch(() => 0);
  ok("workbench grid rendered", gridRows > 0, `rows=${gridRows}`);
  await page.selectOption("#wb_status", "mismatch signal");
  await page.waitForTimeout(250);
  const filtered = await page.$$eval("#grid .tabulator-row", (rs) => rs.length).catch(() => 0);
  ok("status filter narrows the queue", filtered >= 1 && filtered < gridRows, `filtered=${filtered}`);
  await page.selectOption("#wb_status", "");
  await page.click('#grid .tabulator-header input[type="checkbox"]');
  await page.fill("#wb_owner", "RA Review Board");
  await page.click("#wb_apply_owner");
  const [dsel] = await Promise.all([page.waitForEvent("download", { timeout: 8000 }), page.click("#wb_export_sel")]);
  const selCsv = (await import("fs")).readFileSync(await dsel.path(), "utf8");
  ok("bulk owner lands in selected export", selCsv.includes("RA Review Board") && selCsv.includes("review_state"));

  // 5. keyboard reaches the mode switch; no JS errors anywhere
  await page.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });
  let focusHit = false;
  for (let i = 0; i < 25 && !focusHit; i++) {
    await page.keyboard.press("Tab");
    focusHit = await page.evaluate(() => document.activeElement && document.activeElement.id === "modeA");
  }
  ok("mode switch keyboard-reachable", focusHit);

  // 6. mobile: same journey renders without horizontal scroll
  const m = await (await browser.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });
  const ovf = await m.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok("no mobile overflow on scanner", ovf <= 0, `overflow ${ovf}px`);

  ok("no page JS errors", pageErrors.length === 0, pageErrors.join(" | "));
} finally {
  await browser.close();
}

const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
for (const [s, n, d] of results) console.log(s, "-", n, d ? "::" + d : "");
const fails = results.filter((r) => r[0] === "FAIL").length;
console.log(`RESULT: ${results.length - fails}/${results.length} passed in ${elapsed}s (journey incl. data → queue → export)`);
if (fails) process.exit(1);
