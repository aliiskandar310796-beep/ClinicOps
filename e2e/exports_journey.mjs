import { chromium } from "playwright";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};
const browser = await chromium.launch({ headless: true });
const tmp = mkdtempSync(join(tmpdir(), "exp-"));

async function open(path) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce", acceptDownloads: true });
  const page = await context.newPage();
  const problems = [], external = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u); });
  page.on("dialog", d => { problems.push("dialog: " + d.message()); d.dismiss(); });
  await page.goto(BASE + path, { waitUntil: "load" });
  return { context, page, problems, external };
}
async function download(page, selector) {
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click(selector)]);
  const p = join(tmp, dl.suggestedFilename());
  await dl.saveAs(p);
  return { name: dl.suggestedFilename(), path: p, text: readFileSync(p, "utf8") };
}

try {
  // Lead-time planner: exports equal the screen -------------------------------------------------
  {
    const { context, page, problems, external } = await open("/ecoa-lead-time-planner");
    await page.click("#load-example");
    await page.waitForSelector("#out table");
    const screenDates = await page.locator("#out table").first().locator("tbody tr td:nth-child(2)").allInnerTexts();
    const sc = await download(page, "#export-scenarios");
    const scRows = sc.text.trim().split("\n");
    const scDates = scRows.slice(1, 4).map(r => r.split(",")[2]);
    note(sc.name === "lead-time-scenarios.csv" && JSON.stringify(scDates) === JSON.stringify(screenDates), "scenario CSV dates equal the screen", `${scDates} vs ${screenDates}`);
    const csv = await download(page, "#export-csv");
    const head = csv.text.split("\n")[0].split(",");
    note(head.includes("ready_date_expected") && csv.text.trim().split("\n").length === 6, "row CSV has dates and one line per row");
    const ics = await download(page, "#export-ics");
    note(ics.name.endsWith(".ics") && (ics.text.match(/BEGIN:VEVENT/g) || []).length === 5 && ics.text.includes("DTSTART;VALUE=DATE:" + screenDates[1].replace(/-/g, "")), "ics has kick-off, three scenarios and target; expected date matches screen");
    // JSON round trip
    const js = await download(page, "#export-json");
    await page.click("#clear");
    await page.setInputFiles("#import", js.path);
    await page.waitForSelector("#out table");
    const after = await page.locator("#out table").first().locator("tbody tr td:nth-child(2)").allInnerTexts();
    note(JSON.stringify(after) === JSON.stringify(screenDates), "workspace JSON round-trips to identical dates");
    note(external.length === 0 && problems.length === 0, "planner: no external requests or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }

  // DHPC checker: save, clear, load ---------------------------------------------------------------
  {
    const { context, page, problems, external } = await open("/danish-dhpc-checker");
    await page.click("#example");
    note((await page.locator("#status").innerText()).includes("Fictional example"), "example loads and announces itself");
    note(await page.locator("#A0").isChecked() && !(await page.locator("#A1").isChecked()), "example ticks the first item only");
    const saved = await download(page, "#save");
    const data = JSON.parse(saved.text);
    note(data.schema === "clinicops-dhpc/1" && data.checked.A[0] === true && data.product.includes("Examplemab"), "saved file has schema, checks and product");
    await page.reload({ waitUntil: "load" });
    note(!(await page.locator("#A0").isChecked()), "reload starts empty (nothing stored in the browser)");
    await page.setInputFiles("#load", saved.path);
    await page.waitForFunction(() => document.getElementById("status").textContent.includes("loaded"));
    note(await page.locator("#A0").isChecked() && (await page.inputValue("#prod")).includes("Examplemab") && (await page.inputValue("#due")) === "2027-03-15", "load restores checks, product and date");
    const bad = join(tmp, "bad.json"); writeFileSync(bad, JSON.stringify({ schema: "x" }));
    await page.setInputFiles("#load", bad);
    await page.waitForFunction(() => document.getElementById("status").textContent.startsWith("Not loaded"));
    note(true, "invalid file is refused with a message");
    const stored = await page.evaluate(() => localStorage.length + sessionStorage.length);
    note(stored === 0, "no browser storage used", String(stored));
    note(external.length === 0 && problems.length === 0, "dhpc: no external requests or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }
} catch (e) {
  failures.push("journey crashed: " + e.message);
  console.error(e);
}
await browser.close();
if (failures.length) { console.error("\nRESULT: FAIL\n- " + failures.join("\n- ")); process.exit(1); }
console.log("\nRESULT: PASS (0 failures)");
