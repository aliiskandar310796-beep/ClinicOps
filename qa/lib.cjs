// Shared helpers for the QA scripts. Run with NODE_PATH=$(npm root -g) so global Playwright resolves.
const fs = require('fs'), path = require('path');
const BASE = process.env.QA_BASE_URL || 'http://127.0.0.1:8102';
const OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
function urls() {
  const xml = fs.readFileSync(path.join(__dirname, '..', 'docs', 'sitemap.xml'), 'utf8');
  const locs = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map(m => m[1].replace(/^https?:\/\/clinicops\.dk/, ''));
  const all = [...new Set([...locs, '/404.html'])];
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
