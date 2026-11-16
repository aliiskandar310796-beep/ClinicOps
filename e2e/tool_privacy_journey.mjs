import { chromium } from "playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const TOOLS = [
  "change-surface-mapper", "ctis-clock", "identifier-check", "integrity-check", "integrity-scanner",
  "regulatory-change-impact", "technical-file-consistency", "ecoa-delivery-workbench",
  "coa-type-finder", "ecoa-lead-time-planner", "ecoa-visit-burden", "danish-dhpc-checker",
  "danish-pv-literature-register", "sdea-clause-checker", "readiness-score", "integrity-economics",
];
const failures = [];
const pass = (name, cond, detail = "") => {
  if (!cond) failures.push(name + (detail ? " :: " + detail : ""));
  console.log((cond ? "PASS" : "FAIL"), "-", name, detail || "");
};

const origin = new URL(BASE).origin;
const browser = await chromium.launch({ headless: true });
try {
  for (const slug of TOOLS) {
    const context = await browser.newContext({ viewport: { width: 1024, height: 800 } });
    const page = await context.newPage();
    const external = [];
    const violations = [];
    page.on("request", r => {
      const u = r.url();
      if (/^(data|blob|about):/.test(u)) return;
      if (new URL(u).origin !== origin) external.push(u);
    });
    page.on("console", m => { if (/Content Security Policy/i.test(m.text())) violations.push(m.text().slice(0, 160)); });
    const response = await page.goto(`${BASE}/${slug}.html`, { waitUntil: "load" });
    pass(`${slug} loads`, !!response && response.status() < 400);
    const csp = await page.locator('meta[http-equiv="Content-Security-Policy"]').getAttribute("content");
    pass(`${slug} declares connect-src 'none'`, !!csp && csp.includes("connect-src 'none'"));
    pass(`${slug} makes no external request`, external.length === 0, external.join(" | "));
    pass(`${slug} has no CSP violation on load`, violations.length === 0, violations.join(" | "));
    await context.close();
  }
} finally {
  await browser.close();
}
console.log(failures.length ? `\nFAILED: ${failures.length}` : "\nRESULT: all passed");
process.exit(failures.length ? 1 : 0);
