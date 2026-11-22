// Real-browser journey for the Change Surface Mapper language dimension, the twelve-step eCOA
// workflow page and the static template downloads. Run: E2E_BASE_URL=http://localhost:8103 node e2e/change_surface_journey.mjs
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};

const browser = await chromium.launch({ headless: true });

async function open(path, viewport = { width: 1280, height: 900 }) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce", acceptDownloads: true });
  const page = await context.newPage();
  const problems = [], external = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u); });
  page.on("dialog", d => { problems.push("dialog: " + d.message()); d.dismiss(); });
  await page.goto(BASE + path, { waitUntil: "load" });
  return { context, page, problems, external };
}

async function fillChange(page) {
  await page.selectOption("#workstream", "regulatory-integrity");
  await page.fill("#change-title", "Approved IFU wording changed");
  await page.fill("#source-ref", "Controlled document ref");
  await page.fill("#change-summary", "One approved sentence changed in the source text.");
}

try {
  // ---- mapper: language dimension
  {
    const { context, page, problems, external } = await open("/change-surface-mapper");
    note(await page.locator("#language-dimension legend").innerText() === "Language versions and deliverables affected (optional)", "mapper: optional language fieldset is present");
    const boxes = await page.locator("#lang-deliverables input[type=checkbox]").count();
    note(boxes === 9, "mapper: nine neutral deliverable checkboxes built from the core", String(boxes));
    await fillChange(page);
    await page.click("#load");

    // unused dimension: brief and packet unchanged
    await page.click("button[type=submit]");
    const plain = await page.locator("#output").innerText();
    note(plain.startsWith("ClinicOps Change Surface Brief") && !plain.includes("Language versions and deliverables"), "mapper: brief without the optional input has no language block");

    await page.fill("#lang-list", "da-DK, sv-SE; nb-NO, DA-dk");
    await page.check("#lang-deliverables input[value=ifu]");
    await page.check("#lang-deliverables input[value=participant-material]");
    await page.fill("#lang-note", "Delta goes to the language provider with the changed sentence.");
    await page.click("button[type=submit]");
    const out = await page.locator("#output").innerText();
    note(/Language versions: da-DK, sv-SE, nb-NO/.test(out), "mapper: languages listed and de-duplicated", out.slice(-500));
    note(/Combinations to confirm: 3 language versions x 2 deliverables = 6/.test(out), "mapper: combinations counted");
    note(/Delta goes to the language provider/.test(out), "mapper: note carried into the brief");
    note(!/must change|non-?complian|required to/i.test(out.split("Language versions and deliverables")[1] || ""), "mapper: language block wording stays neutral");

    const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#download")]);
    const stream = await dl.createReadStream();
    let body = ""; for await (const chunk of stream) body += chunk;
    const json = JSON.parse(body);
    note(json.schema_version === "1.0" && json.language_versions?.combinations_to_confirm === 6, "mapper: JSON download carries the language dimension", JSON.stringify(json.language_versions || null).slice(0, 200));
    note(json.language_versions?.deliverables?.map(d => d.id).join(",") === "ifu,participant-material", "mapper: deliverable ids in catalogue order");
    note(typeof json.language_versions?.basis === "string" && /does not decide/.test(json.language_versions.basis), "mapper: boundary statement in the JSON");

    await page.click("#reset");
    const afterReset = await page.evaluate(() => ({
      list: document.getElementById("lang-list").value, note: document.getElementById("lang-note").value,
      ticked: document.querySelectorAll("#lang-deliverables input:checked").length,
    }));
    note(afterReset.list === "" && afterReset.note === "" && afterReset.ticked === 0, "mapper: reset clears the language inputs");

    note(external.length === 0, "mapper: no external requests", external.join(" | "));
    note(problems.length === 0, "mapper: no dialogs or console problems", problems.join(" | "));
    await context.close();
  }

  // ---- axe and overflow on the changed pages, mobile and desktop
  for (const [name, viewport] of [["mobile", { width: 390, height: 844 }], ["desktop", { width: 1440, height: 1000 }]]) {
    for (const path of ["/change-surface-mapper", "/ecoa-workflow"]) {
      const { context, page, problems } = await open(path, viewport);
      const size = await page.evaluate(() => ({ s: document.documentElement.scrollWidth, c: document.documentElement.clientWidth }));
      note(size.s <= size.c + 2, `${path} [${name}]: no page-level horizontal overflow`, `${size.s}/${size.c}`);
      const result = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
      const bad = result.violations.filter(v => ["serious", "critical"].includes(v.impact));
      note(bad.length === 0, `${path} [${name}]: no serious or critical axe violations`, bad.map(v => v.id).join(","));
      note(problems.length === 0, `${path} [${name}]: no console problems`, problems.join(" | "));
      await context.close();
    }
  }

  // ---- workflow page: twelve steps, anchors, downloads
  {
    const { context, page, problems, external } = await open("/ecoa-workflow#step-test");
    const rows = await page.locator("table").first().locator("tbody tr").count();
    note(rows === 12, "workflow: twelve step rows", String(rows));
    const numbers = await page.locator("table").first().locator("tbody tr td.k").allInnerTexts();
    note(numbers.join(",") === "0,1,2,3,4,5,6,7,8,9,10,11", "workflow: steps numbered 0 to 11 in order", numbers.join(","));
    note(await page.locator("#step-test").isVisible(), "workflow: #step-test anchor resolves to the Test row");
    note(await page.locator(".hero p.meta", { hasText: "ClinicOps synthesis of published guidance, not a standard" }).count() === 1, "workflow: synthesis label is in the page header");
    const hrefs = [...new Set(await page.locator("a[download]").evaluateAll(a => a.map(x => x.getAttribute("href"))))];
    note(hrefs.length === 3, "workflow: three distinct template files linked", hrefs.join(","));
    for (const href of hrefs) {
      const res = await page.request.get(BASE + "/" + href);
      note(res.status() === 200, `workflow: ${href} downloads`, String(res.status()));
      const bytes = (await res.body()).length;
      note(bytes > 500, `workflow: ${href} is not empty`, String(bytes));
    }
    const xlsx = await page.request.get(BASE + "/" + hrefs.find(h => h.includes("uat")));
    const head = (await xlsx.body()).subarray(0, 2).toString("latin1");
    note(head === "PK", "workflow: the UAT template is a zip container");
    note(external.length === 0, "workflow: no external requests", external.join(" | "));
    note(problems.length === 0, "workflow: no dialogs or console problems", problems.join(" | "));
    await context.close();
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error("\nChange surface journey FAILED:\n- " + failures.join("\n- "));
  process.exit(1);
}
console.log("\nchange surface journey passed");
