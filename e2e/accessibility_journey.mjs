import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const PAGES = [
  "/", "/services.html", "/integrity-scanner.html", "/tools.html",
  "/regulatory-change-integrity-review.html", "/about.html", "/contact.html",
  "/assessment-intake.html?workstream=integrity-review", "/privacy-notice/",
];
const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "desktop", width: 1440, height: 1000 },
];
const failures = [];

const browser = await chromium.launch({ headless: true });
try {
  for (const vp of VIEWPORTS) {
    // reducedMotion: 'reduce' matches docs/site.css's own @media(prefers-reduced-motion:reduce)
    // block, which disables the hero's one-time opacity "rise" entrance animation entirely.
    // Without it, axe can sample the DOM mid-fade (e.g. an element at ~38% opacity blends its
    // text color toward the page background) and report a transient, sub-threshold contrast
    // that never actually reaches the user -- a test-timing race against a real, intentional,
    // already-motion-gated animation, not a static defect in the shipped page. Testing the
    // reduced-motion state is also the more conservative, accessibility-correct thing to do.
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    for (const path of PAGES) {
      await page.goto(BASE + path, { waitUntil: "load" });
      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();
      const serious = results.violations.filter(v => ["serious", "critical"].includes(v.impact || ""));
      const label = `[${vp.name}] ${path}`;
      if (serious.length) {
        failures.push({ label, serious });
        console.error("FAIL -", label, serious.map(v => `${v.id}(${v.nodes.length})`).join(", "));
      } else {
        console.log("PASS -", label, `0 serious/critical WCAG violations; ${results.violations.length} total axe findings`);
      }
    }
    await context.close();
  }
} finally {
  await browser.close();
}

if (failures.length) {
  for (const failure of failures) {
    console.error("\n" + failure.label);
    for (const v of failure.serious) {
      console.error(`  ${v.id}: ${v.help} — ${v.helpUrl}`);
      for (const node of v.nodes.slice(0, 5)) console.error("   ", node.target.join(" "), "::", node.failureSummary || "");
    }
  }
  process.exit(1);
}
console.log("RESULT: PASS (automated WCAG 2.x AA serious/critical gate)");
