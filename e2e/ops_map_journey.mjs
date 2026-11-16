import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const PAGE = "/clinical-operations-workflow-map";
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};
const browser = await chromium.launch({ headless: true });
const tmp = mkdtempSync(join(tmpdir(), "opsmap-"));

async function open(path, viewport = { width: 1280, height: 900 }, extra = {}) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce", acceptDownloads: true, ...extra });
  const page = await context.newPage();
  const problems = [], external = [], requests = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => {
    const u = r.url();
    requests.push(u);
    if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u);
  });
  page.on("dialog", d => { problems.push("dialog: " + d.message()); d.dismiss(); });
  await page.goto(BASE + path, { waitUntil: "load" });
  return { context, page, problems, external, requests };
}
async function download(page, selector) {
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click(selector)]);
  const p = join(tmp, dl.suggestedFilename());
  await dl.saveAs(p);
  return { name: dl.suggestedFilename(), text: readFileSync(p, "utf8"), path: p };
}
const visible = (page, slug) => page.locator(`#step-${slug}`).isVisible();
const pressed = (page, sel) => page.locator(sel).getAttribute("aria-pressed");

try {
  // Layout, accessibility and network cleanliness in both colour schemes and at phone width.
  for (const scheme of ["light", "dark"]) {
    for (const width of [320, 1280]) {
      const { context, page, problems, external } = await open(PAGE, { width, height: 900 }, { colorScheme: scheme });
      const label = `[${scheme} ${width}]`;
      note((await page.locator("h1").count()) === 1, label + " one h1");
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      note(overflow <= 0, label + " no horizontal overflow", String(overflow));
      const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
      const bad = r.violations.filter(v => ["serious", "critical"].includes(v.impact || ""));
      note(bad.length === 0, label + " axe", bad.map(v => `${v.id}(${v.nodes.length})`).join(", "));
      note(external.length === 0 && problems.length === 0, label + " no external requests or console problems", [...external, ...problems].join(" | "));
      await context.close();
    }
  }

  // Without JavaScript the whole map is on the page and the phase links work.
  {
    const { context, page } = await open(PAGE, { width: 1280, height: 900 }, { javaScriptEnabled: false });
    const n = await page.locator("article.step").count();
    note(n >= 30, "no-JS: every step is in the page", String(n));
    note(await page.locator("article.step[hidden]").count() === 0, "no-JS: no step is hidden");
    note(await page.locator("#map-controls").isHidden(), "no-JS: filter controls stay hidden");
    note((await page.locator(".phase-strip a").count()) === 6, "no-JS: six phase links");
    note((await page.locator("section.phase").count()) === 6, "no-JS: six phase sections");
    await context.close();
  }

  // Filtering, hash state, and the keyboard path.
  {
    const { context, page, problems, external } = await open(PAGE);
    note(await page.locator("#map-controls").isVisible(), "controls appear with JavaScript");
    const total = await page.locator("article.step").count();
    note(/Showing \d+ of \d+ steps/.test(await page.locator("#steps-status").innerText()), "status line reports the count");

    await page.click('[data-overlay-btn="device"]');
    note(page.url().endsWith("#overlay=device"), "device overlay writes the hash", page.url());
    note(await pressed(page, '[data-overlay-btn="device"]') === "true", "device button is pressed");
    note(!(await visible(page, "susar-reporting")) && (await visible(page, "device-application")), "drug-only step hides, device step shows");
    const halt = page.locator("#step-halt-or-early-termination");
    note((await halt.locator('.fact[data-overlay="drug"]').isHidden()) && (await halt.locator('.fact[data-overlay="device"]').isVisible()), "a step with both regimes shows only the device clock");

    await page.click('[data-lane-btn="safety"]');
    note(page.url().endsWith("#overlay=device&lane=safety"), "lane adds to the hash", page.url());
    const shownSafety = await page.locator("article.step:not([hidden])").count();
    note(shownSafety > 0 && shownSafety < total, "lane filter narrows the list", String(shownSafety));
    note(await page.locator('section.phase[data-phase-section="p1"]').isHidden(), "a phase with no match is hidden");

    await page.click('[data-overlay-btn="both"]');
    await page.click('[data-lane-btn="all"]');
    note(page.url().split("#")[1] === undefined || page.url().endsWith("#"), "defaults clear the hash", page.url());
    note((await page.locator("article.step:not([hidden])").count()) === total, "all steps back");

    await page.click('[data-lane-btn="patients"]');
    note((await page.locator("article.step:not([hidden])").count()) >= 1, "every lane has at least one step");

    // Keyboard: a filter button is reachable and toggles with Enter.
    await page.focus('[data-overlay-btn="drug"]');
    await page.keyboard.press("Enter");
    note(await pressed(page, '[data-overlay-btn="drug"]') === "true", "keyboard Enter sets the filter");
    note(external.length === 0 && problems.length === 0, "filter journey: no external requests or console problems", [...external, ...problems].join(" | "));
    await context.close();
  }

  // A shared link opens in the stated state; the plain card anchor works too.
  {
    const { context, page } = await open(PAGE + "#overlay=device&lane=safety&step=device-adverse-event-reporting");
    note(await pressed(page, '[data-overlay-btn="device"]') === "true" && await pressed(page, '[data-lane-btn="safety"]') === "true", "shared hash restores both filters");
    note(await visible(page, "device-adverse-event-reporting"), "linked step is visible");
    note((await page.locator("#step-device-adverse-event-reporting").getAttribute("class")).includes("is-target"), "linked step is marked");
    note(await page.locator("#step-device-adverse-event-reporting .not-shown").first().innerText().then(t => /No figure shown: not verified at primary source/.test(t)), "device safety day counts say Not shown");
    await context.close();
  }
  {
    const { context, page } = await open(PAGE + "#overlay=device&lane=safety&step=susar-reporting");
    note(await visible(page, "susar-reporting"), "a linked step the filters would hide still opens");
    note(await pressed(page, '[data-overlay-btn="both"]') === "true" && await pressed(page, '[data-lane-btn="all"]') === "true", "filters relax for a linked step");
    await context.close();
  }
  {
    const { context, page } = await open(PAGE + "#step-urgent-safety-measures");
    note(await visible(page, "urgent-safety-measures"), "plain #step-<slug> anchor opens the step");
    await context.close();
  }
  {
    const { context, page } = await open(PAGE + "#overlay=%3Cscript%3E&lane=zzz&step=__proto__");
    note(await pressed(page, '[data-overlay-btn="both"]') === "true" && (await page.locator("article.step:not([hidden])").count()) > 30, "a malformed hash falls back to the default view");
    await context.close();
  }

  // Trace, export, clear, import. Nothing is stored and nothing is sent.
  {
    const { context, page, problems, external, requests } = await open(PAGE);
    await page.fill("#trace-label", "Fictional study");
    await page.selectOption("#trace-status-susar-reporting", "settled");
    await page.fill("#trace-note-susar-reporting", "=HYPERLINK(\"http://example.invalid\")");
    await page.selectOption("#trace-status-route-and-regime", "open");

    const json = await download(page, "#export-json");
    let parsed = null; try { parsed = JSON.parse(json.text); } catch {}
    note(parsed && parsed.schema === "clinicops-ops-map-trace/1" && Array.isArray(parsed.trace) && parsed.trace.length === 2, "JSON export has schema and two entries");
    note(parsed && /Planning aid, not advice/.test(parsed.decision_boundary || ""), "JSON export carries the decision boundary");
    note(parsed && parsed.label === "Fictional study", "JSON export carries the label");

    const csv = await download(page, "#export-csv");
    note(csv.name.endsWith(".csv") && /Planning aid, not advice/.test(csv.text.split("\r\n")[0]), "CSV export starts with the boundary");
    note(csv.text.includes("'=HYPERLINK("), "CSV export neutralises a formula in a note");
    note(csv.text.trim().split("\r\n").length > 30, "CSV export has a row per step");

    await page.click("#trace-clear");
    note((await page.inputValue("#trace-status-susar-reporting")) === "" && (await page.inputValue("#trace-note-susar-reporting")) === "", "clear empties the trace");

    await page.setInputFiles("#import-file", json.path);
    await page.waitForFunction(() => /Imported 2 steps/.test(document.getElementById("trace-status").textContent));
    note((await page.inputValue("#trace-status-susar-reporting")) === "settled", "import restores the status");
    note((await page.inputValue("#trace-note-route-and-regime")) === "" && (await page.inputValue("#trace-status-route-and-regime")) === "open", "import restores a status-only entry");
    note((await page.inputValue("#trace-label")) === "Fictional study", "import restores the label");

    const bad = join(tmp, "bad.json");
    writeFileSync(bad, JSON.stringify({ schema: "something-else", trace: [] }));
    await page.setInputFiles("#import-file", bad);
    await page.waitForFunction(() => /Not imported/.test(document.getElementById("trace-status").textContent));
    note((await page.inputValue("#trace-status-susar-reporting")) === "settled", "a rejected file leaves the trace as it was");

    const hostile = join(tmp, "hostile.json");
    writeFileSync(hostile, JSON.stringify({ schema: "clinicops-ops-map-trace/1", label: "<img src=x onerror=alert(1)>", trace: [
      { slug: "__proto__", status: "settled", note: "x" }, { slug: "no-such-step", status: "open" },
      { slug: "serious-breach", status: "open", note: "<b>bold</b>" }] }));
    await page.setInputFiles("#import-file", hostile);
    await page.waitForFunction(() => /Imported 1 step/.test(document.getElementById("trace-status").textContent));
    note(/2 entries not recognised/.test(await page.locator("#trace-status").innerText()), "unknown entries are skipped and counted");
    note((await page.locator("#step-serious-breach b").count()) === 0 && (await page.inputValue("#trace-note-serious-breach")) === "<b>bold</b>", "notes are text, not markup");
    note((await page.evaluate(() => ({}).settled)) === undefined, "no prototype pollution");

    const storage = await page.evaluate(() => ({ local: Object.keys(window.localStorage).length, session: Object.keys(window.sessionStorage).length, cookie: document.cookie }));
    note(storage.local === 0 && storage.session === 0 && storage.cookie === "", "nothing is stored: no local or session storage, no cookies", JSON.stringify(storage));
    note(external.length === 0 && requests.every(u => u.startsWith(BASE) || u.startsWith("blob:") || u.startsWith("data:")), "no request left the origin", external.join(" | "));
    note(problems.length === 0, "trace journey: no console problems", problems.join(" | "));
    await context.close();
  }

  // Static content checks: every clock shows its source, article, review date, and limits are reachable.
  {
    const { context, page } = await open(PAGE);
    const facts = await page.locator(".fact-clock").count();
    const refs = await page.locator(".fact-clock .fact-ref").allInnerTexts();
    note(facts >= 15 && refs.every(t => /CO-CLM-\d{4}/.test(t) && /Review due \d{4}-\d{2}-\d{2}/.test(t)), "every clock shows its claim id and review date", String(facts));
    note((await page.locator("details.claim").count()) >= 15, "registered wording and limits are in the page");
    note((await page.locator('a[href^="mailto:info@clinicops.dk"]').count()) > 30, "each step has a report-a-mistake link");
    note(!/27 May 2027/.test(await page.locator("#step-device-coordinated-assessment").innerText()), "the superseded 27 May 2027 date is not shown on the step");
    await context.close();
  }
} catch (e) {
  failures.push("journey crashed: " + e.message);
  console.error(e);
}
await browser.close();
if (failures.length) { console.error("\nRESULT: FAIL\n- " + failures.join("\n- ")); process.exit(1); }
console.log("\nRESULT: PASS (0 failures)");
