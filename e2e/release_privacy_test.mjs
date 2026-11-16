// ClinicOps release test for the privacy claim (plenum lens 20 A3, lens 28 R5, lens 30 section 4).
//
// What it measures, and therefore the most the site may claim in its "what leaves your browser"
// notes and in the privacy notice:
//   PART 1, every URL in docs/sitemap.xml, loaded in a fresh browser context:
//     - zero requests to any origin other than the site's own (pages, scripts, workers, frames)
//     - no Set-Cookie response header on any response, no cookie in the context, document.cookie empty
//     - localStorage, sessionStorage, IndexedDB, CacheStorage and service workers empty after load
//     - a meta Content-Security-Policy with connect-src 'none', default-src 'self' and no
//       'unsafe-inline' / 'unsafe-eval' in script-src, plus <meta name="referrer" content="no-referrer">
//     - no Content-Security-Policy violation and no uncaught page error on load
//   PART 2, three scripted journeys with a spy on Storage.setItem:
//     - Scanner: save a mapping profile -> only the allow-listed localStorage key is written
//     - Change Surface Mapper -> assessment intake, and Readiness Score -> assessment intake:
//       only the allow-listed sessionStorage keys are written, the intake page removes the key as it
//       reads it, no cookie is set, no request leaves the origin, and no Referer header is sent
//
// It does NOT measure what a visitor types into every tool, nor GitHub's own server logs. The
// site copy is worded to match: "on load" for part 1, named journeys for part 2.
//
// Run:  E2E_BASE_URL=http://localhost:8103 node e2e/release_privacy_test.mjs   (serve docs/ first)
// Against production (also checks the real GitHub Pages response headers):
//       E2E_BASE_URL=https://clinicops.dk node e2e/release_privacy_test.mjs
import { chromium } from "playwright";
import fs from "fs";

const BASE = (process.env.E2E_BASE_URL || "http://localhost:8103").replace(/\/$/, "");
const ORIGIN = new URL(BASE).origin;
const ROOT = new URL("../", import.meta.url).pathname;
const LOCAL_ALLOW = new Set(["clinicops.scanner.mappingProfiles"]);
const SESSION_ALLOW = new Set(["clinicops.handoff", "clinicops.readiness.handoff"]);

const failures = [];
const pass = (name, cond, detail = "") => {
  if (!cond) failures.push(name + (detail ? " :: " + detail : ""));
  console.log(cond ? "PASS" : "FAIL", "-", name, cond ? "" : detail);
};

const sitemap = fs.readFileSync(ROOT + "docs/sitemap.xml", "utf8");
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname);
pass("sitemap lists pages", urls.length >= 30, `found ${urls.length}`);

const SPY = () => {
  const proto = Storage.prototype;
  const orig = proto.setItem;
  proto.setItem = function (key, value) {
    try { window.__recordStorage(this === window.localStorage ? "local" : "session", String(key)); } catch (_) { /* binding not ready */ }
    return orig.call(this, key, value);
  };
  document.addEventListener("securitypolicyviolation", (e) => {
    try { window.__recordViolation(`${e.violatedDirective} ${e.blockedURI}`); } catch (_) { /* binding not ready */ }
  });
};

async function newContext(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  const log = { external: [], cookiesHeaders: [], violations: [], pageErrors: [], writes: [], referers: [] };
  await context.exposeFunction("__recordStorage", (area, key) => log.writes.push({ area, key }));
  await context.exposeFunction("__recordViolation", (text) => log.violations.push(text));
  await context.addInitScript(SPY);
  context.on("request", (r) => {
    const u = r.url();
    if (/^(data|blob|about):/.test(u)) return;
    if (new URL(u).origin !== ORIGIN) log.external.push(u);
    if (r.isNavigationRequest()) log.referers.push({ url: u, referer: r.headers()["referer"] || "" });
  });
  context.on("response", async (resp) => {
    try {
      const headers = await resp.allHeaders();
      if (headers["set-cookie"]) log.cookiesHeaders.push(resp.url());
    } catch (_) { /* response disposed during navigation */ }
  });
  context.on("page", (page) => {
    page.on("pageerror", (e) => log.pageErrors.push(String(e).slice(0, 160)));
    page.on("console", (m) => { if (/Content Security Policy/i.test(m.text())) log.violations.push(m.text().slice(0, 160)); });
  });
  return { context, log };
}

const storageSnapshot = (page) =>
  page.evaluate(async () => {
    const idb = indexedDB.databases ? (await indexedDB.databases()).length : 0;
    const caches_ = window.caches ? (await caches.keys()).length : 0;
    const sw = navigator.serviceWorker ? (await navigator.serviceWorker.getRegistrations()).length : 0;
    return {
      local: Object.keys(localStorage),
      session: Object.keys(sessionStorage),
      cookie: document.cookie,
      idb,
      caches: caches_,
      sw,
    };
  });

const browser = await chromium.launch({ headless: true });
try {
  // ---- PART 1: every sitemap URL, fresh context each -----------------------------------------
  for (const path of urls) {
    const { context, log } = await newContext(browser);
    const page = await context.newPage();
    const response = await page.goto(BASE + path, { waitUntil: "load" });
    await page.waitForTimeout(300);
    const label = path === "/" ? "/" : path;
    pass(`${label} loads`, !!response && response.status() < 400, response ? String(response.status()) : "no response");
    pass(`${label} requests only its own origin`, log.external.length === 0, log.external.join(" | "));
    pass(`${label} receives no Set-Cookie header`, log.cookiesHeaders.length === 0, log.cookiesHeaders.join(" | "));
    const snap = await storageSnapshot(page);
    const cookies = await context.cookies();
    pass(`${label} has no cookies`, cookies.length === 0 && snap.cookie === "", JSON.stringify(cookies.map((c) => c.name)));
    pass(`${label} has empty local and session storage after load`, snap.local.length === 0 && snap.session.length === 0, JSON.stringify(snap));
    pass(`${label} has no IndexedDB, CacheStorage or service worker`, snap.idb === 0 && snap.caches === 0 && snap.sw === 0, JSON.stringify(snap));
    const csp = (await page.locator('meta[http-equiv="Content-Security-Policy"]').first().getAttribute("content").catch(() => null)) || "";
    const scriptSrc = (csp.split(";").map((d) => d.trim()).find((d) => d.startsWith("script-src ")) || "");
    pass(`${label} declares connect-src 'none' and default-src 'self'`, csp.includes("connect-src 'none'") && csp.includes("default-src 'self'"), csp.slice(0, 120));
    pass(`${label} script-src has no unsafe-inline or unsafe-eval`, !!scriptSrc && !/'unsafe-(inline|eval)'/.test(scriptSrc), scriptSrc.slice(0, 160));
    const referrer = await page.locator('meta[name="referrer"]').first().getAttribute("content").catch(() => null);
    pass(`${label} sends no referrer`, referrer === "no-referrer", String(referrer));
    pass(`${label} has no CSP violation or page error on load`, log.violations.length === 0 && log.pageErrors.length === 0, [...log.violations, ...log.pageErrors].join(" | "));
    await context.close();
  }

  // ---- PART 2a: Scanner mapping profile (localStorage allow-list) ----------------------------
  {
    const { context, log } = await newContext(browser);
    const page = await context.newPage();
    await page.goto(BASE + "/integrity-scanner.html", { waitUntil: "load" });
    await page.click("#modeB");
    await page.setInputFiles("#b_file", ROOT + "examples/scanner-fixtures/clean.csv");
    await page.waitForFunction(() => document.getElementById("b_parseinfo").textContent.length > 0, null, { timeout: 8000 });
    await page.fill("#prof_name", "release-test-profile");
    await page.click("#prof_save");
    await page.waitForTimeout(300);
    const snap = await storageSnapshot(page);
    const localWrites = log.writes.filter((w) => w.area === "local").map((w) => w.key);
    pass("scanner profile save writes localStorage", localWrites.length > 0, JSON.stringify(log.writes));
    pass("scanner writes only allow-listed localStorage keys", localWrites.every((k) => LOCAL_ALLOW.has(k)), localWrites.join(","));
    pass("scanner leaves only allow-listed localStorage keys", snap.local.every((k) => LOCAL_ALLOW.has(k)), snap.local.join(","));
    pass("scanner writes no sessionStorage", log.writes.every((w) => w.area === "local") && snap.session.length === 0, JSON.stringify(snap.session));
    pass("scanner journey: no external request, cookie or CSP violation",
      log.external.length === 0 && log.cookiesHeaders.length === 0 && (await context.cookies()).length === 0 && log.violations.length === 0,
      [...log.external, ...log.violations].join(" | "));
    await context.close();
  }

  // ---- PART 2b: Change Surface Mapper -> intake (sessionStorage handoff) ---------------------
  {
    const { context, log } = await newContext(browser);
    const page = await context.newPage();
    await page.goto(BASE + "/change-surface-mapper.html", { waitUntil: "load" });
    await page.selectOption("#workstream", "regulatory-integrity");
    await page.fill("#change-title", "Release test change");
    await page.fill("#source-ref", "Release test reference");
    await page.fill("#change-summary", "Synthetic summary used only by the release test.");
    await page.click("#load");
    await Promise.all([page.waitForURL(/assessment-intake/), page.click("#scope")]);
    await page.waitForLoadState("load");
    await page.waitForTimeout(300);
    const snap = await storageSnapshot(page);
    const sessionWrites = log.writes.filter((w) => w.area === "session").map((w) => w.key);
    pass("mapper handoff writes the allow-listed sessionStorage key", sessionWrites.length > 0 && sessionWrites.every((k) => SESSION_ALLOW.has(k)), sessionWrites.join(","));
    pass("mapper handoff writes no localStorage", log.writes.every((w) => w.area === "session"), JSON.stringify(log.writes));
    pass("intake removes the handoff key as it reads it", snap.session.length === 0, snap.session.join(","));
    const carried = await page.locator("#context").inputValue().catch(() => "");
    pass("intake received the carried summary locally", /Change Surface Mapper/.test(carried), carried.slice(0, 80));
    const nav = log.referers.filter((r) => r.url.includes("assessment-intake"));
    pass("handoff navigation sends no Referer header", nav.length > 0 && nav.every((r) => r.referer === ""), JSON.stringify(nav));
    pass("mapper journey: no external request, cookie or CSP violation",
      log.external.length === 0 && log.cookiesHeaders.length === 0 && (await context.cookies()).length === 0 && log.violations.length === 0,
      [...log.external, ...log.violations].join(" | "));
    await context.close();
  }

  // ---- PART 2c: Readiness Score -> intake (sessionStorage handoff; page is unlisted, still served) ----
  {
    const { context, log } = await newContext(browser);
    const page = await context.newPage();
    await page.goto(BASE + "/readiness-score.html", { waitUntil: "load" });
    for (const select of await page.locator("#readiness-form select").all()) {
      await select.selectOption({ index: 1 });
    }
    await page.click('#readiness-form button[type="submit"]');
    await Promise.all([page.waitForURL(/assessment-intake/), page.click("#continue-brief")]);
    await page.waitForLoadState("load");
    await page.waitForTimeout(300);
    const snap = await storageSnapshot(page);
    const sessionWrites = log.writes.filter((w) => w.area === "session").map((w) => w.key);
    pass("readiness handoff writes the allow-listed sessionStorage key", sessionWrites.length > 0 && sessionWrites.every((k) => SESSION_ALLOW.has(k)), sessionWrites.join(","));
    pass("readiness handoff writes no localStorage", log.writes.every((w) => w.area === "session"), JSON.stringify(log.writes));
    pass("intake removes the readiness handoff key as it reads it", snap.session.length === 0, snap.session.join(","));
    pass("readiness journey: no external request, cookie or CSP violation",
      log.external.length === 0 && log.cookiesHeaders.length === 0 && (await context.cookies()).length === 0 && log.violations.length === 0,
      [...log.external, ...log.violations].join(" | "));
    await context.close();
  }
} finally {
  await browser.close();
}
console.log(failures.length ? `\nFAILED: ${failures.length}\n${failures.join("\n")}` : "\nRESULT: all passed");
process.exit(failures.length ? 1 : 0);
