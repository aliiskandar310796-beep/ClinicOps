// axe-core sweep. Automated axe finds only a subset of WCAG issues; it is NOT proof of conformance.
// Env: QA_WIDTHS=1440,390  QA_SCHEMES=light,dark  QA_ONLY=...
const { BASE, OUT, urls, list, slug, pool, browserType, fs, path } = require('./lib.cjs');
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js', { paths: [__dirname] }), 'utf8');
const WIDTHS = list('QA_WIDTHS', ['1440', '390']).map(Number), SCHEMES = list('QA_SCHEMES', ['light', 'dark']);
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'];
(async () => {
  const browser = await browserType().launch();
  const jobs = []; for (const u of urls()) for (const w of WIDTHS) for (const s of SCHEMES) jobs.push({ u, w, s });
  const res = [];
  await pool(jobs, 4, async ({ u, w, s }) => {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, colorScheme: s });
    const page = await ctx.newPage();
    const r = { url: u, width: w, scheme: s, violations: [], incomplete: 0 };
    try {
      await page.goto(BASE + u, { waitUntil: 'load' });
      await page.waitForTimeout(400);
      await page.evaluate(axeSrc);
      const a = await page.evaluate(t => axe.run(document, { runOnly: { type: 'tag', values: t } }), TAGS);
      r.incomplete = a.incomplete.length;
      r.axe = a.testEngine.version;
      r.violations = a.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
        targets: v.nodes.slice(0, 5).map(n => ({ target: n.target.join(' '), summary: (n.failureSummary || '').split('\n').slice(1, 3).join(' ').slice(0, 200) })) }));
    } catch (e) { r.error = String(e).slice(0, 200); }
    await ctx.close(); res.push(r);
  });
  await browser.close();
  res.sort((a, b) => (a.url + a.width + a.scheme).localeCompare(b.url + b.width + b.scheme));
  fs.writeFileSync(path.join(OUT, 'a11y.json'), JSON.stringify({ tags: TAGS, results: res }, null, 1));
  const byRule = {};
  for (const r of res) for (const v of r.violations) { const k = v.id; (byRule[k] ||= { impact: v.impact, help: v.help, nodes: 0, where: new Set(), ex: [] });
    byRule[k].nodes += v.nodes; byRule[k].where.add(r.url + ' @' + r.width + '/' + r.scheme); if (byRule[k].ex.length < 3) byRule[k].ex.push(v.targets[0]); }
  const order = { critical: 0, serious: 1, moderate: 2, minor: 3 };
  let md = `# axe-core report\n\n> Automated axe checks cover only a subset of WCAG 2.x/2.2 criteria. A clean run is **not** proof of WCAG conformance; manual keyboard, screen-reader and content review are still required.\n\nTags: ${TAGS.join(', ')} | pages x viewports x schemes: ${res.length} | axe ${(res[0] || {}).axe}\n\n`;
  const total = res.reduce((n, r) => n + r.violations.length, 0);
  md += `Total rule violations (page-configs): **${total}**; errors during run: ${res.filter(r => r.error).length}\n\n`;
  md += '## By rule\n\n| Rule | Impact | Nodes | Page-configs | Example |\n|---|---|---|---|---|\n';
  for (const [id, x] of Object.entries(byRule).sort((a, b) => order[a[1].impact] - order[b[1].impact] || b[1].nodes - a[1].nodes))
    md += `| ${id} | ${x.impact} | ${x.nodes} | ${x.where.size} | \`${(x.ex[0] || {}).target || ''}\` |\n`;
  md += '\n## By page\n\n';
  for (const r of res) if (r.violations.length || r.error) md += `- ${r.url} @${r.width}/${r.scheme}: ${r.error || r.violations.map(v => `${v.id}(${v.nodes})`).join(', ')}\n`;
  fs.writeFileSync(path.join(OUT, 'a11y.md'), md);
  console.log(`a11y: ${total} violations across ${res.length} configs; ${Object.keys(byRule).length} distinct rules`);
  process.exit(total || res.some(r => r.error) ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
