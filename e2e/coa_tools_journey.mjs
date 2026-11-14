import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const PAGES = ["/ecoa", "/coa-types", "/ecoa-workflow", "/coa-nordic", "/coa-type-finder", "/ecoa-lead-time-planner", "/ecoa-visit-burden"];
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};
const browser = await chromium.launch({ headless: true });
const tmp = mkdtempSync(join(tmpdir(), "coa-"));

async function open(path, viewport = { width: 1280, height: 900 }, extra = {}) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce", acceptDownloads: true, ...extra });
  const page = await context.newPage();
  const problems = [], external = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u); });
  page.on("dialog", d => { problems.push("dialog: " + d.message()); d.dismiss(); });
  await page.goto(BASE + path, { waitUntil: "load" });
  return { context, page, problems, external };
}
async function until(fn, ms = 3000) {
  const end = Date.now() + ms;
  while (Date.now() < end) { if (await fn()) return true; await new Promise(r => setTimeout(r, 50)); }
  return fn();
}
async function download(page, selector) {
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click(selector)]);
  const p = join(tmp, dl.suggestedFilename());
  await dl.saveAs(p);
  return { name: dl.suggestedFilename(), text: readFileSync(p, "utf8"), path: p };
}

try {
  // Static pages: h1, no overflow at 320, axe in light and dark, no external requests -------------
  for (const scheme of ["light", "dark"]) {
    for (const path of PAGES) {
      for (const width of [320, 1280]) {
        const { context, page, problems, external } = await open(path, { width, height: 900 }, { colorScheme: scheme });
        const label = `[${scheme} ${width}] ${path}`;
        note((await page.locator("h1").count()) === 1, label + " one h1");
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        note(overflow <= 0, label + " no horizontal overflow", String(overflow));
        if (width === 1280) {
          const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
          const bad = r.violations.filter(v => ["serious", "critical"].includes(v.impact || ""));
          note(bad.length === 0, label + " axe", bad.map(v => `${v.id}(${v.nodes.length})`).join(", "));
        }
        note(external.length === 0 && problems.length === 0, label + " no external requests or console problems", [...external, ...problems].join(" | "));
        await context.close();
      }
    }
  }

  // COA type finder -------------------------------------------------------------------------
  {
    const { context, page, problems, external } = await open("/coa-type-finder");
    await page.check("input[name=reporter][value=participant]");
    const txt = await page.locator("#result").innerText();
    note(/patient-reported/i.test(txt), "finder: participant reporter gives PRO", txt.slice(0, 80));
    await page.check("input[name=reporter][value=clinician]");
    note(/clinician-reported/i.test(await page.locator("#result").innerText()), "finder: clinician reporter gives ClinRO");
    await page.click("#load-example");
    const rows = await page.locator("#inv-body tr").count();
    note(rows >= 3, "finder: example loads rows", String(rows));
    note((await page.locator("#findings li").count()) > 0, "finder: example shows findings");
    const csv = await download(page, "#export-csv");
    note(csv.text.split("\n").length > 3, "finder: csv export has rows");
    const js = await download(page, "#export-json");
    const parsed = JSON.parse(js.text);
    note(parsed.schema === "clinicops-coa-finder/1" || typeof parsed.schema === "string", "finder: json export has schema", String(parsed.schema));
    await page.click("#clear");
    note((await page.locator("#inv-body tr").count()) === 0, "finder: clear empties inventory");
    await page.setInputFiles("#import", js.path);
    note(await until(async () => (await page.locator("#inv-body tr").count()) === rows), "finder: import round-trips the inventory");
    const bad = join(tmp, "bad.json"); writeFileSync(bad, '{"schema":"x","rows":"no"}');
    await page.setInputFiles("#import", bad);
    note(await until(async () => /not imported/i.test(await page.locator("#status").innerText())), "finder: bad file rejected with message");
    note(external.length === 0 && problems.length === 0, "finder: no external requests or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }

  // Lead-time planner -----------------------------------------------------------------------
  {
    const { context, page, problems, external } = await open("/ecoa-lead-time-planner");
    note(/kick-off/i.test(await page.locator("#out").innerText()), "planner: asks for kick-off before result");
    await page.click("#load-example");
    const out = await page.locator("#out").innerText();
    note(/optimistic/i.test(out) && /expected/i.test(out) && /pessimistic/i.test(out), "planner: three scenarios shown");
    note(/critical/i.test(out), "planner: a critical row is marked");
    note(/2027-/.test(out), "planner: dates in ISO form");
    await page.fill("#kickoff", "2027-02-01");
    const first = await page.locator("#out table").first().innerText();
    await page.locator("#rows input").nth(2).fill("30");
    const second = await page.locator("#out table").first().innerText();
    note(first !== second, "planner: changing a row recomputes the dates");
    const csv = await download(page, "#export-csv");
    note(/^instrument,language/.test(csv.text), "planner: csv header");
    const js = await download(page, "#export-json");
    await page.click("#clear");
    await page.setInputFiles("#import", js.path);
    note(await until(async () => (await page.locator("#rows tr").count()) === 5), "planner: import restores five rows");
    const evil = join(tmp, "evil.json"); writeFileSync(evil, JSON.stringify({ schema: "clinicops-leadtime/1", kickoff: "2027-02-01", target: "", products: [{ instrument: "<img src=x onerror=alert(1)>", language: "=cmd|' /C calc'!A0" }] }));
    await page.setInputFiles("#import", evil);
    await until(async () => (await page.locator("#rows tr").count()) === 1);
    note((await page.locator("#out img").count()) === 0 && (await page.locator("#rows img").count()) === 0, "planner: markup in an imported file is not rendered");
    const csv2 = await download(page, "#export-csv");
    note(csv2.text.includes("'=cmd"), "planner: formula-leading cell is neutralised in csv");
    note(external.length === 0 && problems.length === 0, "planner: no external requests, dialogs or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }

  // Burden estimator ------------------------------------------------------------------------
  {
    const { context, page, problems, external } = await open("/ecoa-visit-burden");
    await page.click("#load-example");
    const out = await page.locator("#out").innerText();
    note(/hours/.test(out) && /Heaviest week/.test(out), "burden: totals shown");
    await page.fill("#cap-week", "10");
    note(/over limit/i.test(await page.locator("#out").innerText()), "burden: weekly limit flags an over-limit week");
    await page.fill("#cap-week", "");
    note(!/over limit/i.test(await page.locator("#out").innerText()), "burden: removing the limit removes the flag");
    const csv = await download(page, "#export-csv");
    note(/^section,name_or_week/.test(csv.text), "burden: csv header");
    const js = await download(page, "#export-json");
    await page.click("#clear");
    note(/Add at least one instrument/.test(await page.locator("#out").innerText()), "burden: cleared state asks for an instrument");
    await page.setInputFiles("#import", js.path);
    note(await until(async () => (await page.locator("#rows-visits tr").count()) === 4), "burden: import restores four visits");
    const evil = join(tmp, "evil2.json"); writeFileSync(evil, JSON.stringify({ schema: "clinicops-burden/1", instruments: [{ name: "<b>x</b>", minutes: "1" }], visits: [{ name: "<img src=x onerror=alert(1)>", week: "0", instruments: "<b>x</b>" }], diaries: [] }));
    await page.setInputFiles("#import", evil);
    await until(async () => (await page.locator("#rows-visits tr").count()) === 1);
    note((await page.locator("#out img, #rows-visits img").count()) === 0, "burden: markup in an imported file is not rendered");
    note(external.length === 0 && problems.length === 0, "burden: no external requests, dialogs or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }
} finally {
  await browser.close();
}
if (failures.length) { console.error(`\n${failures.length} failure(s)`); process.exit(1); }
console.log("\ncoa tools journey passed");
