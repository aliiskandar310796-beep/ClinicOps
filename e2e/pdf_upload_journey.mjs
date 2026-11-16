import { chromium } from "playwright";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Regression guard for the meta CSP on tool pages: reading a PDF in the browser
// must still work (vendored pdf.js, same-origin worker) with connect-src 'none'.
const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const here = path.dirname(fileURLToPath(import.meta.url));
const PDF = path.resolve(here, "../docs/specimen-register/ClinicOps_Regulatory_Integrity_Specimen_Register_v1.5.pdf");
const failures = [];
const pass = (name, cond, detail = "") => {
  if (!cond) failures.push(name + (detail ? " :: " + detail : ""));
  console.log((cond ? "PASS" : "FAIL"), "-", name, detail || "");
};

const browser = await chromium.launch({ headless: true });
try {
  const page = await (await browser.newContext()).newPage();
  const violations = [];
  const external = [];
  const origin = new URL(BASE).origin;
  page.on("console", m => { if (/Content Security Policy/i.test(m.text())) violations.push(m.text().slice(0, 200)); });
  page.on("request", r => { const u = r.url(); if (!/^(data|blob|about):/.test(u) && new URL(u).origin !== origin) external.push(u); });
  await page.goto(`${BASE}/sdea-clause-checker.html`, { waitUntil: "load" });
  await page.setInputFiles("#pdfFile", PDF);
  await page.waitForFunction(() => {
    const ta = document.querySelector("textarea");
    return ta && ta.value.trim().length > 200;
  }, null, { timeout: 60000 }).then(() => pass("PDF text is extracted into the text box", true)).catch(() => pass("PDF text is extracted into the text box", false, "timed out"));
  pass("no CSP violation while reading a PDF", violations.length === 0, violations.join(" | "));
  pass("no external request while reading a PDF", external.length === 0, external.join(" | "));
} finally {
  await browser.close();
}
console.log(failures.length ? `\nFAILED: ${failures.length}` : "\nRESULT: all passed");
process.exit(failures.length ? 1 : 0);
