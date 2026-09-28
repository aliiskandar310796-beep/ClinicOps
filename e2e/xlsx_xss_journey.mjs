// Regression journey for the workbook XML reader (docs/integrity-scanner.html,
// parseXLSX/extract in the portfolio-scan pane): prove that HTML/script payloads
// smuggled inside an .xlsx workbook's sheet name, header row and cell values can
// never reach the DOM as live markup, only as inert escaped text — anywhere the
// tool surfaces workbook-derived content (mapping panel, sheet picker, exception
// queue, workbench grid, HTML export). Added after a CodeQL DOM-XSS alert on the
// workbook XML reader; see BUILD_NOTES/2026-09-28-reconciliation-assessment.md.
import { chromium } from "playwright";
import fs from "node:fs";

const BASE = process.env.E2E_BASE_URL || "http://localhost:8103";
const results = [];
const ok = (name, cond, detail = "") => {
  results.push([cond ? "PASS" : "FAIL", name, detail]);
  if (!cond) process.exitCode = 1;
};

// Three distinct payloads, one per injection point, so a failure pinpoints which
// workbook part (sheet name / header / cell value) reached the DOM unescaped.
const RAW_CELL = "<img src=x onerror=alert(1)>";
const RAW_SHEET = "<img src=x onerror=alert(2)>";
const RAW_HEADER = "<img src=x onerror=alert(3)>";

const browser = await chromium.launch();
const t0 = Date.now();
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const pageErrors = [];
  const dialogs = [];
  page.on("pageerror", (e) => pageErrors.push(String(e).slice(0, 200)));
  page.on("dialog", async (d) => {
    dialogs.push(d.message());
    await d.dismiss().catch(() => {});
  });

  await page.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });
  await page.click("#modeB");
  await page.setInputFiles("#b_file", new URL("./fixtures/xss-payload.xlsx", import.meta.url).pathname);
  await page.waitForTimeout(800);

  const pinfo = await page.textContent("#b_parseinfo");
  ok("malicious workbook still parses (payload is data, not a crash)", /rows.*columns parsed locally/.test(pinfo), pinfo.slice(0, 160));

  // Sheet picker: only one sheet, so the wrapper is hidden, but the <option> text
  // still exists in the DOM and must carry the sheet-name payload as inert text.
  const sheetOptionText = await page.locator("#b_sheet option").first().textContent();
  ok("sheet-name payload preserved verbatim as text (not silently dropped)", sheetOptionText.includes("onerror=alert(2)"), sheetOptionText);

  // Mapping panel: the malicious header value must appear as an <option>'s text,
  // never break out into a new element or attribute.
  const mapOptionsText = await page.locator("#b_maprows option").allTextContents();
  ok("malicious header text present in mapping options as inert text", mapOptionsText.some((t) => t.includes(RAW_HEADER)));

  await page.click("#b_run");
  await page.waitForTimeout(900);
  ok("scan completed despite malicious content", /Portfolio scan/.test(await page.textContent("#summary")));

  // The payload cell value is the authoritative reference in this fixture, so it
  // surfaces as an "expected" value in the results table/grid, not the queue's
  // object label — either way it must reach the visible page as inert text,
  // proving the tool renders it faithfully rather than silently dropping it.
  const bodyText = await page.locator("body").innerText();
  ok("cell-value payload reaches the visible page as text", bodyText.includes("onerror=alert(1)"), bodyText.slice(0, 200));

  const html = await page.content();
  ok("no live <img> element was created from any of the three payloads", (await page.$$eval("img", (els) => els.length)) === 0);
  for (const [label, raw] of [["cell value", RAW_CELL], ["sheet name", RAW_SHEET], ["header row", RAW_HEADER]]) {
    ok(`${label} payload is HTML-escaped in the served DOM, not a live tag`, !html.includes(raw) && html.includes(raw.replace(/</g, "&lt;").replace(/>/g, "&gt;")));
  }

  // HTML export packet: same guarantee must hold for the file an operator emails onward.
  const [dl] = await Promise.all([page.waitForEvent("download", { timeout: 8000 }), page.click("#x_html")]);
  const reportHtml = fs.readFileSync(await dl.path(), "utf8");
  ok("HTML export escapes the cell-value payload", !reportHtml.includes(RAW_CELL) && reportHtml.includes("&lt;img"));

  ok("no onerror/script payload ever executed (no dialog fired)", dialogs.length === 0, dialogs.join(" | "));
  ok("no page JS errors", pageErrors.length === 0, pageErrors.join(" | "));
} finally {
  await browser.close();
}

const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
for (const [s, n, d] of results) console.log(s, "-", n, d ? "::" + d : "");
const fails = results.filter((r) => r[0] === "FAIL").length;
console.log(`RESULT: ${results.length - fails}/${results.length} passed in ${elapsed}s (workbook XML reader XSS regression)`);
if (fails) process.exit(1);
