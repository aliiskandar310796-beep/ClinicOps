// Shared helpers for the QA scripts. Run with NODE_PATH=$(npm root -g) so global Playwright resolves.
const fs = require('fs'), path = require('path');
const BASE = process.env.QA_BASE_URL || 'http://127.0.0.1:8102';
const OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
function noindexPages() {
  const root = path.join(__dirname, '..', 'docs'), out = [];
  const walk = d => fs.readdirSync(d, { withFileTypes: true }).forEach(e => {
    const f = path.join(d, e.name);
    if (e.isDirectory()) { if (e.name !== 'vendor' && e.name !== 'assets') walk(f); return; }
    if (!e.name.endsWith('.html') || e.name === '404.html') return;
    const h = fs.readFileSync(f, 'utf8');
    if (!/<meta name="robots" content="[^"]*noindex/.test(h) || /http-equiv="refresh"/i.test(h)) return;
    const rel = path.relative(root, f).split(path.sep).join('/');
    out.push(rel === 'index.html' ? '/' : rel.endsWith('/index.html') ? '/' + rel.slice(0, -10) : '/' + rel.replace(/\.html$/, ''));
  });
  walk(root);
  return out.sort();
}
function urls() {
  const xml = fs.readFileSync(path.join(__dirname, '..', 'docs', 'sitemap.xml'), 'utf8');
  const locs = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map(m => m[1].replace(/^https?:\/\/clinicops\.dk/, ''));
  // QA covers every page a visitor can reach, not only the indexed ones: the
  // noindex support utilities (calculators, checkers, intake) still ship.
  const all = [...new Set([...locs, ...noindexPages(), '/404.html'])];
  const only = process.env.QA_ONLY; // optional comma list of path substrings
  return only ? all.filter(u => only.split(',').some(s => u.includes(s))) : all;
}
const list = (v, d) => (process.env[v] ? process.env[v].split(',').map(s => s.trim()) : d);
const slug = u => (u.replace(/^\/|\/$/g, '').replace(/[\/.]/g, '_') || 'home');
async function pool(items, n, fn) {
  let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) { const it = items[i++]; await fn(it); } }));
}
function browserType() {
  const pw = require('playwright');
  const name = process.env.QA_BROWSER || 'chromium';
  return pw[name];
}
module.exports = { BASE, OUT, urls, list, slug, pool, browserType, fs, path };
