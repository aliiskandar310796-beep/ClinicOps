import { chromium } from "playwright";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const PAGES = [
  "/", "/services.html", "/integrity-scanner.html", "/tools.html",
  "/evidence-change-control-pack.html", "/about.html", "/contact.html",
  "/assessment-intake.html?workstream=integrity-review",
];
const failures = [];
const browser = await chromium.launch({ headless: true });

try {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await context.addInitScript(() => {
    window.__clinicopsPerf = { cls: 0, lcp: 0 };
    try {
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) window.__clinicopsPerf.cls += entry.value;
        }
      }).observe({ type: "layout-shift", buffered: true });
    } catch (_) {}
    try {
      new PerformanceObserver(list => {
        const entries = list.getEntries();
        if (entries.length) window.__clinicopsPerf.lcp = entries[entries.length - 1].startTime;
      }).observe({ type: "largest-contentful-paint", buffered: true });
    } catch (_) {}
  });
  const page = await context.newPage();

  for (const path of PAGES) {
    const errors = [];
    page.removeAllListeners("pageerror");
    page.on("pageerror", e => errors.push(String(e)));
    await page.goto(BASE + path, { waitUntil: "load" });
    await page.waitForTimeout(250);
    const m = await page.evaluate(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const resources = performance.getEntriesByType("resource");
      const origin = location.origin;
      return {
        loadMs: nav ? nav.loadEventEnd - nav.startTime : 0,
        dclMs: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
        totalBytes: resources.reduce((n, r) => n + (r.transferSize || r.encodedBodySize || 0), 0),
        resources: resources.length,
        thirdParty: resources.filter(r => {
          try { return new URL(r.name).origin !== origin; } catch (_) { return true; }
        }).map(r => r.name),
        cls: window.__clinicopsPerf?.cls || 0,
        lcp: window.__clinicopsPerf?.lcp || 0,
        externalScripts: [...document.scripts].map(s => s.src).filter(Boolean).filter(src => new URL(src).origin !== origin),
      };
    });

    const checks = [
      ["load < 2500ms on local runner", m.loadMs < 2500, `${m.loadMs.toFixed(1)}ms`],
      ["DOMContentLoaded < 2000ms", m.dclMs < 2000, `${m.dclMs.toFixed(1)}ms`],
      ["resource payload < 1.5 MiB", m.totalBytes < 1.5 * 1024 * 1024, `${Math.round(m.totalBytes / 1024)} KiB`],
      ["resource count < 40", m.resources < 40, String(m.resources)],
      ["CLS <= 0.10", m.cls <= 0.10, m.cls.toFixed(4)],
      ["LCP <= 2500ms when reported", !m.lcp || m.lcp <= 2500, `${m.lcp.toFixed(1)}ms`],
      ["no third-party runtime resources", m.thirdParty.length === 0, m.thirdParty.slice(0, 2).join(" | ")],
      ["no third-party scripts", m.externalScripts.length === 0, m.externalScripts.join(" | ")],
      ["no page errors", errors.length === 0, errors.join(" | ")],
    ];
    for (const [name, ok, detail] of checks) {
      console.log(ok ? "PASS -" : "FAIL -", path, name, detail);
      if (!ok) failures.push(`${path}: ${name} (${detail})`);
    }
  }
  await context.close();
} finally {
  await browser.close();
}

console.log(`RESULT: ${failures.length ? "FAIL" : "PASS"} (${failures.length} failures)`);
if (failures.length) {
  for (const f of failures) console.error(" -", f);
  process.exit(1);
}
