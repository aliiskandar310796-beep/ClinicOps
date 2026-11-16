const {test} = require('node:test');
const assert = require('node:assert/strict');
const B = require('../docs/assets/coa-burden-core.js');

const base = () => ({
  instruments: [{name: 'A', minutes: '5', items: '10'}, {name: 'B', minutes: '3,5', items: '6'}, {name: 'Daily', minutes: '2', items: '4'}],
  visits: [{name: 'Baseline', week: '0', instruments: 'A; B'}, {name: 'Week 4', week: '4', instruments: 'A'}],
  diaries: [{instrument: 'Daily', per_week: '7', from_week: '1', to_week: '4'}],
  caps: {}
});

test('BU01 visits add minutes and items; comma decimals are accepted', () => {
  const r = B.estimate(base());
  assert.equal(r.errors.length, 0);
  assert.equal(r.visits[0].minutes, 8.5);
  assert.equal(r.visits[0].items, 16);
  assert.equal(r.visits[1].minutes, 5);
});

test('BU02 diaries add per week across their span; weeks combine visits and diaries', () => {
  const r = B.estimate(base());
  const w4 = r.weeks.find(w => w.week === 4);
  assert.equal(w4.diary_minutes, 14);
  assert.equal(w4.visit_minutes, 5);
  assert.equal(w4.minutes, 19);
  assert.equal(r.weeks.length, 5);
  assert.equal(r.totals.minutes, 8.5 + 14 * 4 + 5);
  assert.equal(r.totals.peak_week, 4);
  assert.equal(r.totals.peak_visit, 'Baseline');
});

test('BU03 limits you set are flagged, absent limits flag nothing', () => {
  assert.equal(B.estimate(base()).flags.filter(f => f.level === 'over').length, 0);
  const r = B.estimate(Object.assign(base(), {caps: {minutes_per_visit: '6', items_per_visit: '12', minutes_per_week: '15'}}));
  const over = r.flags.filter(f => f.level === 'over').map(f => f.msg).join(' | ');
  assert.match(over, /Baseline: 8.5 min is over the 6 min/);
  assert.match(over, /Baseline: 16 items is over the 12/);
  assert.match(over, /Week 4: 19 min is over the 15/);
});

test('BU04 unknown names, missing minutes and unused instruments are reported, never guessed', () => {
  const b = base();
  b.visits.push({name: 'Extra', week: '8', instruments: 'A; Nope'});
  b.instruments.push({name: 'Unused', minutes: '', items: ''});
  b.instruments.push({name: 'NoMinutes', minutes: '', items: '3'});
  b.visits.push({name: 'V3', week: '9', instruments: 'NoMinutes'});
  const msgs = B.estimate(b).flags.map(f => f.msg).join(' | ');
  assert.match(msgs, /"Nope" is not in the instrument list/);
  assert.match(msgs, /no minutes entered for NoMinutes/);
  assert.match(msgs, /Unused is in the list but is not used/);
});

test('BU05 bad numbers and impossible diaries are rejected or skipped', () => {
  const b = base(); b.instruments[0].minutes = 'abc';
  assert.ok(B.estimate(b).errors.length);
  assert.ok(B.estimate({instruments: [], visits: [], diaries: []}).errors.length);
  const d = base(); d.diaries[0].to_week = '0';
  assert.ok(B.estimate(d).flags.some(f => /before first week/.test(f.msg)));
  const m = base(); m.visits[0].week = '';
  assert.ok(B.estimate(m).flags.some(f => /study week is empty/.test(f.msg)));
});

test('BU05b negative study weeks are accepted for screening and run-in', () => {
  const b = base(); b.visits.unshift({name: 'Screening', week: '-2', instruments: 'A'}); b.diaries[0].from_week = '-1';
  const r = B.estimate(b);
  assert.equal(r.flags.filter(f => /study week|numbers/.test(f.msg)).length, 0);
  assert.equal(r.weeks[0].week, -2);
  assert.equal(r.weeks.find(w => w.week === -1).diary_minutes, 14);
  assert.equal(r.weeks.length, 7);
});

test('BU06 CSV is formula-safe and lists visits then weeks', () => {
  const b = base(); b.visits[0].name = '=Evil()';
  const csv = B.toCSV(B.estimate(b));
  const lines = csv.split('\n');
  assert.ok(lines[1].includes("'=Evil()"));
  assert.ok(lines.some(l => l.startsWith('week,4,')));
});

test('BU07 workspace validation', () => {
  assert.deepEqual(B.validateWorkspace(Object.assign({schema: B.SCHEMA}, base())), []);
  assert.ok(B.validateWorkspace({schema: 'x', instruments: [], visits: [], diaries: []}).length);
  assert.ok(B.validateWorkspace({schema: B.SCHEMA, instruments: [1], visits: [], diaries: []}).length);
});

test('BU08 module has no network, storage or eval', () => {
  const src = require('node:fs').readFileSync(require('node:path').join(__dirname, '../docs/assets/coa-burden-core.js'), 'utf8');
  assert.ok(!/fetch\(|XMLHttpRequest|localStorage|sessionStorage|eval\(|new Function|document\./.test(src));
});

test('BU-frac a visit in a fractional study week is counted in the rounded week and flagged, so totals match the by-visit table', () => {
  const r = B.estimate({instruments: [{name: 'A', minutes: '5', items: '1'}], visits: [{name: 'v', week: '1,5', instruments: 'A'}, {name: 'w', week: '2', instruments: 'A'}], diaries: [], caps: {}});
  assert.equal(r.totals.minutes, 10);
  assert.equal(r.visits.reduce((s, v) => s + v.minutes, 0), 10);
  assert.ok(r.flags.some(f => /not a whole number/.test(f.msg)));
});
