import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const failures = [];
const note = (ok, label, detail = "") => {
  if (ok) console.log("PASS -", label);
  else { failures.push(label + (detail ? ": " + detail : "")); console.error("FAIL -", label, detail); }
};
const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const problems = [], external = [];
  page.on("pageerror", e => problems.push("pageerror: " + e.message));
  page.on("console", m => { if (["error", "warning"].includes(m.type())) problems.push(m.type() + ": " + m.text()); });
  page.on("request", r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith("data:") && !u.startsWith("blob:")) external.push(u); });
  await page.goto(BASE + "/integrity-scanner#identifier-check", { waitUntil: "load" });
  const cases = [
    ["DK-MF-123456789", /Role: MF/],
    ["es-ar-000000123", /Role: AR/],
    ["B-ABC123", /legacy-style/i],
    ["4006381333931", /GS1 check digit \(Mod-10\): correct/],
    ["4006381333932", /GS1 check digit \(Mod-10\): incorrect/],
    ["hello", /not recognised/i],
    ["", /Enter an identifier first/]
  ];
  for (const [value, re] of cases) {
    await page.fill("#idc-value", value);
    await page.click("#idc-check");
    const txt = await page.locator("#idc-result").innerText();
    note(re.test(txt), `identifier "${value}" reads as expected`, txt.slice(0, 80));
  }
  await page.fill("#idc-value", "DK-IM-111111111");
  await page.press("#idc-value", "Enter");
  note(/Role: IM/.test(await page.locator("#idc-result").innerText()), "Enter key runs the check");
  const r = await new AxeBuilder({ page }).include("#identifier-check").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
  const bad = r.violations.filter(v => ["serious", "critical"].includes(v.impact || ""));
  note(bad.length === 0, "identifier section axe", bad.map(v => v.id).join(","));
  const stored = await page.evaluate(() => localStorage.getItem("idc") === null);
  note(stored, "nothing stored for the identifier check");
  note(external.length === 0 && problems.length === 0, "no external requests or console problems", [...external, ...problems].join(" | "));
  await context.close();
} catch (e) {
  failures.push("journey crashed: " + e.message); console.error(e);
}
await browser.close();
if (failures.length) { console.error("\nRESULT: FAIL\n- " + failures.join("\n- ")); process.exit(1); }
console.log("\nRESULT: PASS (0 failures)");
