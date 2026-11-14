import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const URL_ = BASE + "/ecoa-delivery-workbench";
const TABS = ["bc", "org", "plans", "quality", "risk", "issues", "progress"];
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};

const browser = await chromium.launch({ headless: true });
const tmp = mkdtempSync(join(tmpdir(), "ecoa-"));

async function open(viewport, extra = {}) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce", acceptDownloads: true, ...extra });
  const page = await context.newPage();
  const problems = [];
  const external = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u); });
  page.on("dialog", d => { problems.push("dialog: " + d.message()); d.dismiss(); });
  await page.goto(URL_, { waitUntil: "load" });
  return { context, page, problems, external };
}

try {
  // 1. Desktop journey: every tab, example, report, exports ---------------------------------
  {
    const { context, page, problems, external } = await open({ width: 1440, height: 1000 });
    const requestsAfterLoad = [];
    page.on("request", r => requestsAfterLoad.push(r.url()));

    note((await page.locator("h1").count()) === 1, "one h1");
    note((await page.locator("[role=tab][aria-selected=true]").count()) === 1, "exactly one tab selected on load");
    note(await page.locator("#panel-bc").isVisible(), "first panel visible on load");

    await page.click("#load-example");
    note(/fictional/i.test(await page.textContent("#status")), "example loads and says it is fictional");
    note((await page.locator("#reg-products tbody tr").count()) === 5, "five example products");

    // keyboard: arrow keys move between tabs and show the matching panel
    await page.focus("#tab-bc");
    await page.keyboard.press("ArrowRight");
    note(await page.locator("#panel-org").isVisible() && !(await page.locator("#panel-bc").isVisible()), "ArrowRight activates next tab and hides the previous panel");
    await page.keyboard.press("End");
    note(await page.locator("#panel-progress").isVisible(), "End moves to the last tab");
    await page.keyboard.press("Home");
    note(await page.locator("#panel-bc").isVisible(), "Home moves to the first tab");

    for (const t of TABS) {
      await page.click("#tab-" + t);
      note(await page.locator("#panel-" + t).isVisible(), `tab ${t} shows its panel`);
      const others = await page.locator("[role=tabpanel]:visible").count();
      note(others === 1, `only one panel visible on tab ${t}`);
    }

    // plans: status derived by rules
    await page.click("#tab-plans");
    const statuses = (await page.locator("#reg-products tbody tr").allTextContents()).join(" | ");
    note(/requires qualified review/i.test(statuses) && /unresolved/i.test(statuses) && /blocked/i.test(statuses), "plan shows qualified review, unresolved and blocked");

    // schedule comparison
    await page.fill("#sched-protocol", "ESD; Daily; 18:00-23:59\nEFS; Week 12; +/- 3 days\nEFS; Baseline");
    await page.fill("#sched-spec", "ESD; Daily; 18:00-23:59\nEFS; Week 12; +/- 2 days");
    await page.click("#reconcile");
    const sched = await page.textContent("#reg-schedule");
    note(/aligned/.test(sched) && /mismatch signal/.test(sched) && /missing evidence/.test(sched), "schedule comparison reports aligned, mismatch signal, missing evidence");

    // quality: script skeleton, expected result blank
    await page.click("#tab-quality");
    await page.click("#uat-from-plan");
    await page.fill("#uat-timepoints", "Baseline\nWeek 12");
    await page.fill("#uat-devices", "Own phone iOS\nOwn phone Android");
    await page.click("#uat-generate");
    note((await page.locator("#reg-scripts tbody tr").count()) > 10, "script skeleton generated");
    note(/coverage|scripts/i.test(await page.textContent("#uat-coverage")), "coverage statement shown");

    // issues: change surface mapping, closure needs owner and evidence
    await page.click("#tab-issues");
    await page.fill("#change-ref", "Protocol amendment 2");
    await page.check("#change-types input >> nth=0");
    await page.click("#map-change");
    const surfaces = await page.locator("#reg-surfaces tbody tr").count();
    note(surfaces >= 3, "change mapping lists expected surfaces", String(surfaces));

    // progress: report
    await page.click("#tab-progress");
    await page.click("#build-report");
    const report = await page.textContent("#report");
    note(/HIGHLIGHT REPORT/.test(report) && /not a compliance determination/i.test(report), "highlight report built with boundary line");
    note(!(await page.isDisabled("#copy-report")), "copy enabled after report");
    const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#dl-raid")]);
    const csvPath = join(tmp, "raid.csv");
    await dl.saveAs(csvPath);
    const csv = readFileSync(csvPath, "utf8");
    note(csv.includes("\r\n") && !/^["]?[=+\-@]/m.test(csv.split("\r\n").slice(1).join("\r\n").replace(/"'[=+\-@]/g, "")), "CSV has CRLF and no raw formula cells");

    // export / import round trip
    const [wsDl] = await Promise.all([page.waitForEvent("download"), page.click("#export")]);
    const wsPath = join(tmp, "workspace.json");
    await wsDl.saveAs(wsPath);
    const ws = JSON.parse(readFileSync(wsPath, "utf8"));
    note(ws.schema === "clinicops-ecoa-workbench/1" && ws.products.length === 5, "exported workspace has schema and products");
    await page.click("#clear");
    note((await page.locator("#reg-products tbody tr").count()) === 0, "clear empties the plan");
    await page.setInputFiles("#import", wsPath);
    await page.waitForFunction(() => document.querySelectorAll("#reg-products tbody tr").length === 5);
    note(true, "import restores the plan");

    // hostile import: rejected, no state change, nothing executed
    const evil = join(tmp, "evil.json");
    writeFileSync(evil, JSON.stringify({ schema: "clinicops-ecoa-workbench/1", study: { name: "<img src=x onerror=window.__pwned=1>" }, risks: [{ title: "<script>window.__pwned=1</script>", probability: "high", impact: "high" }] }));
    await page.setInputFiles("#import", evil);
    await page.click("#tab-risk");
    await page.waitForTimeout(150);
    note((await page.evaluate(() => window.__pwned)) === undefined, "imported markup is never executed");
    note((await page.locator("#reg-risks img, #reg-risks script").count()) === 0, "imported markup is rendered as text");
    const bad = join(tmp, "bad.json");
    writeFileSync(bad, JSON.stringify({ schema: "something-else" }));
    await page.setInputFiles("#import", bad);
    await page.waitForFunction(() => /unsupported|could not|cannot|not imported/i.test(document.getElementById("status").textContent));
    note(/unsupported/i.test(await page.textContent("#status")), "wrong schema is refused with a message");
    const notJson = join(tmp, "x.json");
    writeFileSync(notJson, "{not json");
    await page.setInputFiles("#import", notJson);
    await page.waitForFunction(() => /json/i.test(document.getElementById("status").textContent) && !/unsupported/i.test(document.getElementById("status").textContent));
    note(/json/i.test(await page.textContent("#status")), "malformed JSON is refused with a message");

    note(external.length === 0, "no request ever leaves the origin", external.join(", "));
    note(problems.length === 0, "no console errors, warnings, dialogs or page errors", problems.join(" | "));
    const storage = await page.evaluate(() => ({ l: localStorage.length, s: sessionStorage.length, c: document.cookie }));
    note(storage.l === 0 && storage.s === 0 && storage.c === "", "nothing written to browser storage or cookies");
    await context.close();
  }

  // 2. Layout: reflow without horizontal scroll on every tab, 320 to 1440 --------------------
  for (const width of [320, 390, 768, 1024, 1440]) {
    const { context, page } = await open({ width, height: 900 });
    await page.click("#load-example");
    for (const t of TABS) {
      await page.click("#tab-" + t);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      note(overflow <= 0, `no horizontal page scroll at ${width}px on ${t}`, `overflow ${overflow}px`);
    }
    // controls reachable: no interactive element narrower than 24px target
    const tiny = await page.evaluate(() => Array.from(document.querySelectorAll("button, select, input:not([type=file]):not([type=checkbox]):not([type=radio]), textarea, a")).filter(e => e.offsetParent && !(e.tagName === "A" && e.closest("p, td, li, span, summary, .callout")) && (e.getBoundingClientRect().width < 24 || e.getBoundingClientRect().height < 24) && !e.closest(".vh")).map(e => e.id || e.tagName).slice(0, 5));
    note(tiny.length === 0, `touch targets at least 24px at ${width}px`, tiny.join(","));
    await context.close();
  }

  // 3. Accessibility: axe on every tab, with the example loaded, light and dark, 2 viewports ----
  for (const scheme of ["light", "dark"]) {
    for (const vp of [{ width: 390, height: 844 }, { width: 1440, height: 1000 }]) {
      const { context, page } = await open(vp, { colorScheme: scheme });
      await page.click("#load-example");
      for (const t of TABS) {
        await page.click("#tab-" + t);
        if (t === "progress") await page.click("#build-report");
        if (t === "quality") { await page.click("#uat-from-plan"); await page.fill("#uat-timepoints", "Baseline"); await page.fill("#uat-devices", "Phone"); await page.click("#uat-generate"); }
        const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
        const bad = r.violations.filter(v => ["serious", "critical", "moderate"].includes(v.impact || ""));
        note(bad.length === 0, `axe ${scheme} ${vp.width}px ${t}`, bad.map(v => `${v.id}(${v.nodes.length}): ${v.nodes[0]?.target}`).join("; "));
      }
      await context.close();
    }
  }

  // 4. Resilience: forced colours, 200% zoom text, no JS ---------------------------------------
  {
    const { context, page } = await open({ width: 1024, height: 800 }, { forcedColors: "active" });
    await page.click("#load-example");
    const visibleTabs = await page.locator("[role=tab]:visible").count();
    note(visibleTabs === 7, "tabs visible in forced-colours mode");
    await context.close();
  }
  {
    const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 800 } });
    const page = await context.newPage();
    await page.goto(URL_, { waitUntil: "load" });
    note(/needs JavaScript/i.test(await page.locator("noscript").first().textContent().catch(() => "") || await page.content()), "no-JS visitors are told what is needed");
    note(await page.locator("h1").isVisible(), "page content readable without JS");
    await context.close();
  }
  {
    const { context, page } = await open({ width: 640, height: 800 });
    await page.addStyleTag({ content: "html{font-size:200%!important}" });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    note(overflow <= 0, "200% text size does not force horizontal page scroll", `overflow ${overflow}px`);
    await context.close();
  }
  {
    // print: the report is what people print; nothing should throw
    const { context, page } = await open({ width: 1000, height: 800 });
    await page.click("#load-example"); await page.click("#tab-progress"); await page.click("#build-report");
    await page.emulateMedia({ media: "print" });
    note(await page.locator("#report").isVisible(), "report visible in print media");
    await context.close();
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(`\n${failures.length} check(s) failed`);
  process.exit(1);
}
console.log("\neCOA workbench journey: all checks passed");
