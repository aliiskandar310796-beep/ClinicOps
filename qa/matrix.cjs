// Responsive/theme/behaviour matrix. Usage: NODE_PATH=$(npm root -g) node qa/matrix.cjs
// Env: QA_WIDTHS=1440,390  QA_SCHEMES=light  QA_ONLY=about,services  QA_BROWSER=chromium|firefox|webkit  QA_SHOTS=0
const { BASE, OUT, urls, list, slug, pool, browserType, fs, path } = require('./lib.cjs');
const WIDTHS = list('QA_WIDTHS', ['1920', '1440', '768', '390', '320']).map(Number);
const SCHEMES = list('QA_SCHEMES', ['light', 'dark']);
const SHOTS = process.env.QA_SHOTS !== '0';
const CONC = Number(process.env.QA_CONC || 4);
fs.mkdirSync(path.join(OUT, 'shots'), { recursive: true });

const inPage = () => {
  const sel = el => {
    if (!el || !el.tagName) return '';
    let s = el.tagName.toLowerCase();
    if (el.id) return s + '#' + el.id;
    const c = [...el.classList].slice(0, 2).join('.');
    return s + (c ? '.' + c : '');
  };
  const vw = window.innerWidth;
  const out = { overflow: [], nav: [], images: [], targets: [] };
  const doc = document.documentElement;
  if (doc.scrollWidth > vw) {
    out.overflowPx = doc.scrollWidth - vw;
    const seen = new Set();
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      if (r.width && r.right > vw + 1 && cs.position !== 'fixed' && cs.visibility !== 'hidden' && cs.display !== 'none') {
        // skip children of an element that already overflows (report roots)
        let p = el.parentElement, dup = false;
        while (p) { if (seen.has(p)) { dup = true; break; } p = p.parentElement; }
        if (!dup) { seen.add(el); if (out.overflow.length < 8) out.overflow.push({ sel: sel(el), right: Math.round(r.right), text: (el.textContent || '').trim().slice(0, 40) }); }
      }
    }
  }
  // clipped text in nav/header
  for (const el of document.querySelectorAll('header *, nav *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const clips = /hidden|clip|auto|scroll/.test(cs.overflowX);
    if (clips && el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0 && (el.textContent || '').trim())
      out.nav.push({ sel: sel(el), sw: el.scrollWidth, cw: el.clientWidth, scroller: /auto|scroll/.test(cs.overflowX), scrollLeft: Math.round(el.scrollLeft), text: el.textContent.trim().slice(0, 40) });
    if (cs.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) out.nav.push({ sel: sel(el), ellipsis: true, text: el.textContent.trim().slice(0, 40) });
    const r = el.getBoundingClientRect();
    if (r.width && !el.closest('nav.primary') && (el.textContent || '').trim() && el.children.length === 0 && (r.right > vw + 1 || r.left < -1) && cs.position !== 'fixed')
      out.nav.push({ sel: sel(el), offscreen: true, left: Math.round(r.left), right: Math.round(r.right), text: el.textContent.trim().slice(0, 40) });
  }
  for (const img of document.images) {
    if (!img.complete || img.naturalWidth === 0) {
      const r = img.getBoundingClientRect();
      if (img.currentSrc || img.src) out.images.push({ sel: sel(img), src: (img.currentSrc || img.src).slice(0, 120), lazy: img.loading === 'lazy' });
    }
  }
  // targets (WCAG 2.2 SC 2.5.8, 24x24; inline-in-text links exempt)
  const q = 'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[role=tab],[tabindex]:not([tabindex="-1"])';
  for (const el of document.querySelectorAll(q)) {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || el.disabled) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (r.right < 0 || r.left > vw + 1) continue; // off-canvas (e.g. skip link before focus)
    if (r.width >= 24 && r.height >= 24) continue;
    if (el.tagName === 'A' && cs.display === 'inline') {
      const p = el.closest('p,li,dd,td,h1,h2,h3,h4,figcaption,blockquote');
      if (p && (p.textContent || '').trim().length > (el.textContent || '').trim().length + 3) continue; // inline exemption
    }
    out.targets.push({ sel: sel(el), w: Math.round(r.width), h: Math.round(r.height), text: (el.textContent || el.getAttribute('aria-label') || el.value || '').trim().slice(0, 30) });
  }
  return out;
};

async function focusChecks(page, N = 15) {
  const res = { skip: null, focus: [] };
  await page.evaluate(() => { window.scrollTo(0, 0); document.activeElement && document.activeElement.blur(); });
  for (let i = 0; i < N; i++) {
    await page.keyboard.press('Tab');
    if (i === 0) await page.waitForTimeout(200);
    const info = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const cs = getComputedStyle(el), r = el.getBoundingClientRect();
      const outline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
      const shadow = cs.boxShadow && cs.boxShadow !== 'none';
      const sel = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ([...el.classList][0] ? '.' + [...el.classList][0] : '');
      return { sel, href: el.getAttribute('href'), text: (el.textContent || '').trim().slice(0, 30), outline, shadow: !!shadow,
        visible: r.width > 0 && r.height > 0 && r.bottom > 0 && r.right > 0 && r.left < innerWidth && r.top < innerHeight && cs.opacity !== '0' && cs.visibility !== 'hidden',
        outlineOffset: cs.outlineOffset };
    });
    if (!info) break; // focus left the document
    if (i === 0) res.skip = { ...info, isSkip: /skip|main|content/i.test(info.text + (info.href || '')) && (info.href || '').startsWith('#') };
    if (!info.outline && !info.shadow) res.focus.push({ stop: i + 1, sel: info.sel, text: info.text });
  }
  return res;
}

async function run() {
  const bt = browserType();
  const browser = await bt.launch();
  const pages = urls();
  const jobs = [];
  for (const u of pages) for (const w of WIDTHS) for (const s of SCHEMES) jobs.push({ u, w, s });
  const results = [];
  const t0 = Date.now();
  await pool(jobs, CONC, async ({ u, w, s }) => {
    const r = { url: u, width: w, scheme: s, errors: [], warns: [] };
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, colorScheme: s });
    const page = await ctx.newPage();
    const cons = [], reqs = [];
    const origin = new URL(BASE).origin;
    page.on('console', m => { if (m.type() === 'error') cons.push(m.text().slice(0, 200)); });
    page.on('pageerror', e => cons.push('pageerror: ' + String(e).slice(0, 200)));
    page.on('requestfailed', q => reqs.push({ url: q.url(), why: q.failure() && q.failure().errorText }));
    page.on('response', x => { if (x.status() >= 400) reqs.push({ url: x.url(), status: x.status() }); });
    try {
      const resp = await page.goto(BASE + u, { waitUntil: 'load', timeout: 30000 });
      await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
      const f = await focusChecks(page); // before any scrolling: Chrome moves the tab start point on scroll
      await page.evaluate(() => { document.activeElement && document.activeElement.blur(); scrollTo(0, 0); });
      // trigger lazy images
      await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } scrollTo(0, 0); });
      // force-load lazy images: scroll each into view and wait for it
      await page.evaluate(async () => {
        for (const im of document.images) {
          if (im.complete) continue;
          im.scrollIntoView({ block: 'center' });
          await Promise.race([new Promise(r => { im.addEventListener('load', r, { once: true }); im.addEventListener('error', r, { once: true }); }), new Promise(r => setTimeout(r, 3000))]);
        }
        scrollTo(0, 0);
      });
      await page.waitForTimeout(250);
      const status = resp && resp.status();
      if (u !== '/404.html' && status >= 400) r.errors.push({ cat: 'http', msg: 'status ' + status });
      const d = await page.evaluate(inPage);
      if (d.overflow.length || d.overflowPx) r.errors.push({ cat: 'overflow', msg: `scrollWidth exceeds viewport by ${d.overflowPx}px`, els: d.overflow });
      for (const n of d.nav) (n.scroller && !n.scrollLeft ? r.warns : r.errors).push({ cat: n.scroller ? 'nav-scroll' : 'nav-clip', ...n });
      for (const i of d.images) r.errors.push({ cat: 'image', ...i });
      for (const t of d.targets) r.warns.push({ cat: 'target-size', ...t });
      for (const c of cons) r.errors.push({ cat: 'console', msg: c });
      for (const q of reqs) {
        const ext = !q.url.startsWith(origin);
        (ext ? r.warns : r.errors).push({ cat: ext ? 'request-external' : 'request', ...q });
      }
      if (!f.skip) r.errors.push({ cat: 'skip-link', msg: 'no focusable element on first Tab' });
      else if (!f.skip.isSkip) r.errors.push({ cat: 'skip-link', msg: 'first tab stop is not a skip link (#anchor)', first: f.skip.sel + ' ' + f.skip.text });
      else if (!f.skip.visible) r.errors.push({ cat: 'skip-link', msg: 'skip link not visible on focus', sel: f.skip.sel });
      for (const x of f.focus) r.errors.push({ cat: 'focus-indicator', ...x });
      if (SHOTS) { await page.evaluate(() => scrollTo(0, 0)); await page.screenshot({ path: path.join(OUT, 'shots', `${slug(u)}__${w}__${s}.jpg`), fullPage: true, type: 'jpeg', quality: 55 }).catch(() => {}); }
    } catch (e) { r.errors.push({ cat: 'load', msg: String(e).slice(0, 200) }); }
    // reduced motion: once per url per scheme at the first width, fresh context
    await ctx.close();
    results.push(r);
  });
  // reduced motion (one context per url)
  for (const u of pages) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    const r = { url: u, width: 1440, scheme: 'reduced-motion', errors: [], warns: [] };
    try {
      await page.goto(BASE + u, { waitUntil: 'load' });
      await page.waitForTimeout(600);
      const anim = await page.evaluate(() => document.getAnimations().filter(a => a.playState === 'running').map(a => {
        const t = a.effect && a.effect.target; const n = a.animationName || a.transitionProperty || 'anim';
        return { sel: t ? t.tagName.toLowerCase() + (t.id ? '#' + t.id : '') + (t.classList[0] ? '.' + t.classList[0] : '') : '?', name: n,
          infinite: a.effect && a.effect.getComputedTiming().iterations === Infinity };
      }));
      for (const a of anim) r.errors.push({ cat: 'reduced-motion', ...a });
    } catch (e) { r.errors.push({ cat: 'load', msg: String(e).slice(0, 200) }); }
    await ctx.close(); results.push(r);
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'matrix.json'), JSON.stringify({ base: BASE, browser: process.env.QA_BROWSER || 'chromium', widths: WIDTHS, schemes: SCHEMES, results }, null, 1));
  const counts = {}, wcounts = {};
  for (const r of results) { for (const e of r.errors) counts[e.cat] = (counts[e.cat] || 0) + 1; for (const e of r.warns) wcounts[e.cat] = (wcounts[e.cat] || 0) + 1; }
  console.log(`matrix: ${jobs.length} combos + ${pages.length} reduced-motion in ${((Date.now() - t0) / 1000) | 0}s`);
  console.log('errors by category:', JSON.stringify(counts));
  console.log('warnings by category:', JSON.stringify(wcounts));
  const n = Object.values(counts).reduce((a, b) => a + b, 0);
  process.exit(n ? 1 : 0);
}
run().catch(e => { console.error(e); process.exit(2); });
