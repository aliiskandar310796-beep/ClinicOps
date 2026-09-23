// Lighthouse lab run. Lab data != field data: LCP/CLS here are simulated-throttle lab values;
// TBT is a lab PROXY for responsiveness. INP is a field metric and is NOT measured here.
const { BASE, OUT, fs, path } = require('./lib.cjs');
const PAGES = (process.env.QA_PERF_PAGES || '/,/services.html,/integrity-scanner.html,/transition-map-sample/').split(',');
const T = { lcp: 2500, cls: 0.1 };
(async () => {
  const lighthouse = (await import('lighthouse')).default;
  const chromeLauncher = require('chrome-launcher');
  const chromePath = require('playwright').chromium.executablePath();
  const rows = [];
  for (const form of ['mobile', 'desktop']) for (const u of PAGES) {
    const chrome = await chromeLauncher.launch({ chromePath, chromeFlags: ['--headless=new', '--no-sandbox'] });
    try {
      const flags = { port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: ['performance'] };
      const cfg = form === 'desktop' ? (await import('lighthouse/core/config/desktop-config.js')).default : undefined;
      const r = await lighthouse(BASE + u, flags, cfg);
      const a = r.lhr.audits;
      rows.push({ url: u, form, score: Math.round(r.lhr.categories.performance.score * 100), lcp: a['largest-contentful-paint'].numericValue, cls: a['cumulative-layout-shift'].numericValue, tbt: a['total-blocking-time'].numericValue, fcp: a['first-contentful-paint'].numericValue, bytes: a['total-byte-weight'].numericValue });
    } catch (e) { rows.push({ url: u, form, error: String(e).slice(0, 200) }); }
    await chrome.kill();
  }
  fs.writeFileSync(path.join(OUT, 'perf.json'), JSON.stringify(rows, null, 1));
  let md = `# Lighthouse (lab) report\n\n> Lab data, single run on a local static server (no CDN/TLS/network latency variance). It is NOT field data (CrUX/RUM). TBT is a lab proxy for responsiveness; **INP is a field-only metric and is not measured here.** Targets: LCP <= 2.5s, CLS <= 0.1.\n\n| Page | Form | Perf | LCP s | CLS | TBT ms | FCP s | KB | Verdict |\n|---|---|---|---|---|---|---|---|---|\n`;
  let bad = 0;
  for (const r of rows) {
    if (r.error) { md += `| ${r.url} | ${r.form} | error: ${r.error} |||||||\n`; bad++; continue; }
    const ok = r.lcp <= T.lcp && r.cls <= T.cls; if (!ok) bad++;
    md += `| ${r.url} | ${r.form} | ${r.score} | ${(r.lcp / 1000).toFixed(2)} | ${r.cls.toFixed(3)} | ${Math.round(r.tbt)} | ${(r.fcp / 1000).toFixed(2)} | ${Math.round(r.bytes / 1024)} | ${ok ? 'pass' : 'FAIL'} |\n`;
  }
  fs.writeFileSync(path.join(OUT, 'perf.md'), md);
  console.log(md);
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
