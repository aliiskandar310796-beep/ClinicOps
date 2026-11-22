import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};
const browser = await chromium.launch({ headless: true });
const tmp = mkdtempSync(join(tmpdir(), "ctis-"));

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
async function download(page, selector) {
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click(selector)]);
  const p = join(tmp, dl.suggestedFilename());
  await dl.saveAs(p);
  return { name: dl.suggestedFilename(), text: readFileSync(p, "utf8") };
}

try {
  for (const scheme of ["light", "dark"]) {
    for (const width of [320, 1280]) {
      const { context, page, problems, external } = await open("/ctis-clock", { width, height: 900 }, { colorScheme: scheme });
      const label = `[${scheme} ${width}] /ctis-clock`;
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

  {
    const { context, page, problems, external } = await open("/ctis-clock");
    note(await page.locator("#result").isHidden(), "result hidden before input");
    await page.fill("#submission", "2027-03-01");
    await page.click("button[type=submit]");
    await page.waitForSelector("#result:not([hidden])");
    const txt = await page.locator("#result").innerText();
    note(/Decision/i.test(txt) && /2027/.test(txt), "plain submission gives dates", txt.slice(0, 120));
    const ics = await download(page, "#export-ics");
    note(ics.name.endsWith(".ics") && ics.text.includes("BEGIN:VCALENDAR") && ics.text.includes("BEGIN:VEVENT"), "ics export valid shape", ics.name);
    const csv = await download(page, "#export-csv");
    note(csv.name.endsWith(".csv") && csv.text.split("\n").length > 3, "csv export has rows", csv.name);
    const json = await download(page, "#export-json");
    let parsed = null; try { parsed = JSON.parse(json.text); } catch {}
    note(parsed && parsed.result && Array.isArray(parsed.result.milestones) && parsed.schema, "json export parses with schema and milestones");
    await page.click("#clear");
    note(await page.locator("#result").isHidden(), "clear hides result");
    await page.click("#load-example");
    await page.waitForSelector("#result:not([hidden])");
    note(true, "fictional example loads");
    note(external.length === 0 && problems.length === 0, "no external requests or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }
} catch (e) {
  failures.push("journey crashed: " + e.message);
  console.error(e);
}
await browser.close();
if (failures.length) { console.error("\nRESULT: FAIL\n- " + failures.join("\n- ")); process.exit(1); }
console.log("\nRESULT: PASS (0 failures)");
