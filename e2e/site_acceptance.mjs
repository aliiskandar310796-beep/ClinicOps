import { chromium } from "playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const WIDTHS = [320, 375, 390, 768, 1024, 1440];
const PAGES = [
  "/", "/services.html", "/integrity-scanner.html", "/tools.html",
  "/evidence-change-control-pack.html", "/about.html", "/contact.html",
  "/assessment-intake.html?workstream=integrity-review", "/privacy-notice/",
];
const LOCAL_UTILITIES = [
  "/identifier-check.html", "/integrity-check.html", "/change-surface-mapper.html",
  "/regulatory-change-impact.html", "/technical-file-consistency.html", "/ecoa-delivery-workbench.html",
  "/readiness-score.html", "/integrity-economics.html",
  "/danish-pv-literature-register.html", "/sdea-clause-checker.html",
  "/danish-dhpc-checker.html",
];
const failures = [];
const pass = (name, cond, detail = "") => {
  if (!cond) failures.push(name + (detail ? " :: " + detail : ""));
  console.log((cond ? "PASS" : "FAIL"), "-", name, detail || "");
};

const browser = await chromium.launch({ headless: true });
try {
  for (const width of WIDTHS) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", e => pageErrors.push(String(e)));

    for (const path of PAGES) {
      const response = await page.goto(BASE + path, { waitUntil: "load" });
      pass(`[${width}] ${path} loads`, !!response && response.status() < 400, response ? String(response.status()) : "no response");
      pass(`[${width}] ${path} has one H1`, await page.locator("h1").count() === 1);
      pass(`[${width}] ${path} has skip navigation`, await page.locator('a.skip-link[href="#main"]').count() === 1);
      const size = await page.evaluate(() => ({
        scroll: document.documentElement.scrollWidth,
        client: document.documentElement.clientWidth,
      }));
      pass(`[${width}] ${path} no page-level horizontal overflow`, size.scroll <= size.client + 2, `${size.scroll}/${size.client}`);
    }

    await page.goto(BASE + "/", { waitUntil: "load" });
    pass(`[${width}] homepage buyer explanation visible`, await page.getByText("ClinicOps works on those two", { exact: false }).isVisible());
    pass(`[${width}] homepage free CTA visible`, await page.getByRole("link", { name: "Open the eCOA workbench" }).first().isVisible());
    pass(`[${width}] homepage paid CTA visible`, await page.getByRole("link", { name: "Scope a review", exact: true }).first().isVisible());
    const ctaBox = await page.getByRole("link", { name: "Open the eCOA workbench" }).first().boundingBox();
    pass(`[${width}] homepage free CTA remains tappable`, !!ctaBox && ctaBox.height >= 40, ctaBox ? String(ctaBox.height) : "missing");

    pass(`[${width}] no uncaught page errors`, pageErrors.length === 0, pageErrors.join(" | "));
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    for (const path of LOCAL_UTILITIES) {
      const reqs = [];
      const handler = req => reqs.push({ url: req.url(), method: req.method(), post: req.postData() || "" });
      page.on("request", handler);
      await page.goto(BASE + path, { waitUntil: "load" });
      await page.waitForTimeout(50);
      page.off("request", handler);
      const bad = reqs.filter(r => !r.url.startsWith(BASE + "/") || r.method !== "GET" || r.post);
      pass(`[privacy] ${path} load is same-origin GET only`, bad.length === 0, bad.slice(0, 2).map(x => x.method + " " + x.url).join(" | "));
    }
    await context.close();
  }

  {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      permissions: ["clipboard-read", "clipboard-write"],
    });
    const page = await context.newPage();
    await page.goto(BASE + "/assessment-intake.html?workstream=integrity-review&src=qa&campaign=acceptance&segment=ra", { waitUntil: "load" });
    pass("[intake] workstream preset resolved", await page.locator("#workstream").inputValue() === "Regulatory Change Integrity Review");
    pass("[intake] preset sets the door", await page.locator("#door").inputValue() === "devices");
    {
      const extra = await context.newPage();
      await extra.goto(BASE + "/assessment-intake.html?workstream=ctis", { waitUntil: "load" });
      pass("[intake] eCOA preset lands on the eCOA door, not Other / mixed", await extra.locator("#door").inputValue() === "ecoa" && await extra.locator("#workstream").inputValue() === "CTIS submission timing");
      await extra.goto(BASE + "/assessment-intake.html?door=denmark", { waitUntil: "load" });
      pass("[intake] door parameter reveals only that door's workstreams", await extra.locator("#workstream-field").isVisible() && await extra.locator("#workstream option:not([disabled]):not([hidden])").count() > 1 && !(await extra.locator("#workstream optgroup[data-door=devices]").isVisible()));
      await extra.close();
    }
    pass("[intake] only four fields are required", await page.locator("#brief-form select[required], #brief-form input[required]:not([type=checkbox]), #brief-form textarea[required]").count() === 4);
    for (const id of ["org", "timing"]) await page.selectOption("#" + id, { index: 1 });
    await page.fill("#name", "Exempla & Co. A/S");
    await page.fill("#notes", "One controlled change — Danish æøå; apostrophe O'Reilly & quoted values.");
    await page.check("#safe");

    const interactions = [];
    page.on("request", req => interactions.push({ url: req.url(), method: req.method(), post: req.postData() || "" }));
    const before = interactions.length;
    await page.click("#preview");
    const preview = await page.locator("#output").textContent();
    pass("[intake] preview includes clean attribution labels", /Source: qa/.test(preview) && /Campaign: acceptance/.test(preview) && /Segment: ra/.test(preview));
    pass("[intake] preview preserves punctuation and Danish text", /Exempla & Co\. A\/S/.test(preview) && /æøå/.test(preview) && /O'Reilly/.test(preview));
    pass("[intake] preview states nothing sent", /Nothing has been sent/.test(await page.locator("#status").textContent()));
    await page.click("#copy");
    pass("[intake] copy remains local", /Nothing has been sent/.test(await page.locator("#status").textContent()));
    pass("[intake] preview shows the target address and subject", /info@clinicops\.dk/.test(await page.locator("#target").textContent()) && /ClinicOps scope/.test(await page.locator("#subject").textContent()));
    await page.fill("#notes", "æøå ".repeat(200));
    await page.fill("#constraints", "æøå ".repeat(125));
    await page.click('button[type=submit]');
    await page.waitForFunction(() => /too long for a reliable email link/.test(document.getElementById("status").textContent), null, { timeout: 2000 }).catch(() => {});
    pass("[intake] an over-long brief is copied instead of opened as a mailto link", /too long for a reliable email link/.test(await page.locator("#status").textContent()));
    const after = interactions.slice(before);
    pass("[intake] preview/copy make no network request", after.length === 0, after.map(x => x.method + " " + x.url).join(" | "));
    await context.close();
  }
} finally {
  await browser.close();
}

console.log(`RESULT: ${failures.length ? "FAIL" : "PASS"} (${failures.length} failures)`);
if (failures.length) {
  for (const failure of failures) console.error(" -", failure);
  process.exit(1);
}
