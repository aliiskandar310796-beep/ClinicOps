const {test} = require('node:test');
const assert = require('node:assert/strict');
const L = require('../docs/assets/coa-leadtime-core.js');

const P = (o) => Object.assign({instrument: 'Instrument A', language: 'Danish', licence_weeks: '', translation_weeks: '', screenshot_rounds: '', signoff_weeks: ''}, o);

test('LT01 PERT weights the likely value', () => {
  assert.equal(L.pert([2, 4, 6]), 4);
  assert.ok(Math.abs(L.pert([8, 12, 16]) - 12) < 1e-9);
  assert.equal(L.pick([1, 2, 9], 'optimistic'), 1);
  assert.equal(L.pick([1, 2, 9], 'pessimistic'), 9);
});

test('LT02 dates are validated strictly and arithmetic is in whole days', () => {
  assert.ok(L.isoDate('2027-02-28'));
  assert.equal(L.isoDate('2027-02-30'), null);
  assert.equal(L.isoDate('27-02-01'), null);
  assert.equal(L.isoDate(''), null);
  assert.equal(L.addWeeks(L.isoDate('2027-01-04'), 2).toISOString().slice(0, 10), '2027-01-18');
  assert.equal(L.weeksBetween(L.isoDate('2027-01-04'), L.isoDate('2027-01-18')), 2);
});

test('LT03 a product takes the slower of licence and translation+screenshots, then sign-off', () => {
  const D = L.resolve(L.DEFAULTS, null);
  const w = L.productWeeks(P({}), 'expected', D);
  assert.equal(w.licence, 4);
  assert.equal(w.translation, 12);
  assert.equal(w.screenshots, 2);
  assert.ok(Math.abs(w.total - (14 + L.pert([1, 1, 2]))) < 1e-9);
  assert.equal(w.driver, 'translation and screenshot review');
  const slowLicence = L.productWeeks(P({licence_weeks: '30'}), 'expected', D);
  assert.equal(slowLicence.driver, 'licence');
  assert.ok(Math.abs(slowLicence.total - (30 + L.pert([1, 1, 2]))) < 1e-9);
});

test('LT04 zero means already done and blank means default', () => {
  const D = L.resolve(L.DEFAULTS, null);
  const done = L.productWeeks(P({licence_weeks: '0', translation_weeks: '0', screenshot_rounds: '0'}), 'expected', D);
  assert.equal(done.licence, 0);
  assert.equal(done.translation, 0);
  assert.equal(done.screenshots, 0);
  assert.ok(Math.abs(done.total - L.pert([1, 1, 2])) < 1e-9);
});

test('LT05 plan needs a kick-off date and at least one product', () => {
  assert.ok(L.plan({kickoff: '', products: [P({})]}).errors.length);
  assert.ok(L.plan({kickoff: '2027-01-04', products: []}).errors.length);
  assert.ok(L.plan({kickoff: '2027-01-04', products: [{instrument: '', language: ''}]}).errors.length);
});

test('LT06 scenarios are ordered and ready date is latest of build and slowest product plus testing', () => {
  const r = L.plan({kickoff: '2027-01-04', target: '', products: [P({}), P({language: 'Swedish', translation_weeks: '20'})]});
  const o = r.scenarios.optimistic.weeks, e = r.scenarios.expected.weeks, p = r.scenarios.pessimistic.weeks;
  assert.ok(o < e && e < p, [o, e, p].join());
  assert.equal(r.scenarios.expected.set_by, 'language versions');
  assert.equal(r.products.filter(x => x.critical).length, 1);
  assert.equal(r.products.find(x => x.critical).language, 'Swedish');
  assert.equal(r.scenarios.expected.status, 'no target');
});

test('LT07 build can set the date when languages are fast', () => {
  const r = L.plan({kickoff: '2027-01-04', products: [P({licence_weeks: '0', translation_weeks: '0', screenshot_rounds: '0', signoff_weeks: '0'})]});
  assert.equal(r.scenarios.expected.set_by, 'study build');
});

test('LT08 submission can set the date and target comparison reports slack', () => {
  const r = L.plan({kickoff: '2027-01-04', target: '2027-03-01', durations: {submission: [30, 30, 30]}, products: [P({})]});
  assert.equal(r.scenarios.expected.set_by, 'submission');
  assert.equal(r.scenarios.expected.status, 'late');
  assert.ok(r.scenarios.expected.slack_weeks < 0);
  const ok = L.plan({kickoff: '2027-01-04', target: '2028-01-01', products: [P({})]});
  assert.equal(ok.scenarios.pessimistic.status, 'on time');
  assert.ok(ok.scenarios.pessimistic.slack_weeks > 0);
});

test('LT09 sensitivity shows what dropping each language would save, largest first', () => {
  const r = L.plan({kickoff: '2027-01-04', products: [P({}), P({language: 'Finnish', translation_weeks: '30'}), P({language: 'Swedish'})]});
  assert.equal(r.sensitivity.length, 3);
  assert.equal(r.sensitivity[0].language, 'Finnish');
  assert.ok(r.sensitivity[0].weeks_saved > 0);
  assert.equal(r.sensitivity[2].weeks_saved, 0);
  assert.equal(L.plan({kickoff: '2027-01-04', products: [P({})]}).sensitivity.length, 0);
});

test('LT10 invalid duration overrides fall back to the published ranges', () => {
  const D = L.resolve(L.DEFAULTS, {licence: [6, 4, 2], build: [1, 'x', 3], uat: [1, 2, 3]});
  assert.deepEqual(D.licence.weeks, L.DEFAULTS.licence.weeks);
  assert.deepEqual(D.build.weeks, L.DEFAULTS.build.weeks);
  assert.deepEqual(D.uat.weeks, [1, 2, 3]);
});

test('LT11 CSV is formula-safe; workspace validation rejects bad shapes', () => {
  const r = L.plan({kickoff: '2027-01-04', products: [P({instrument: '=SUM(1)'})]});
  assert.ok(L.toCSV(r).split('\n')[1].startsWith("'=SUM(1)"));
  assert.deepEqual(L.validateWorkspace({schema: L.SCHEMA, products: []}), []);
  assert.ok(L.validateWorkspace({schema: 'x', products: []}).length);
  assert.ok(L.validateWorkspace({schema: L.SCHEMA, products: new Array(301).fill({})}).length);
});

test('LT12 module has no network, storage or eval', () => {
  const src = require('node:fs').readFileSync(require('node:path').join(__dirname, '../docs/assets/coa-leadtime-core.js'), 'utf8');
  assert.ok(!/fetch\(|XMLHttpRequest|localStorage|sessionStorage|eval\(|new Function|document\./.test(src));
});

test('LT13 per-row CSV carries dates; scenarios CSV and ICS match the result', () => {
  const r = L.plan({kickoff: '2027-01-04', target: '2027-06-01', products: [P({}), P({language: 'Finnish', translation_weeks: '30'})]});
  const rows = L.toCSV(r).trim().split('\n');
  assert.equal(rows.length, 3);
  const head = rows[0].split(',');
  assert.ok(head.includes('ready_date_expected') && head.includes('licence_date'));
  const finnish = rows[2].split(',');
  assert.equal(finnish[head.indexOf('ready_date_expected')], r.products[1].ready.expected);
  assert.equal(finnish[head.indexOf('licence_date')], '2027-02-01'); // 4 weeks after 2027-01-04
  const sc = L.toScenariosCSV(r).trim().split('\n');
  assert.equal(sc.length, 1 + 3 + r.sensitivity.length);
  assert.ok(sc[2].startsWith('scenario,expected,' + r.scenarios.expected.date + ','));
  assert.ok(!/'-/.test(L.toScenariosCSV(r)), 'negative slack must not be quoted as text');
  const ics = L.toICS(r, '20261116T000000Z');
  assert.equal((ics.match(/BEGIN:VEVENT/g) || []).length, 5);
  assert.ok(ics.includes('DTSTART;VALUE=DATE:20270104') && ics.includes('DTSTART;VALUE=DATE:20270601'));
  assert.ok(ics.includes('DTSTART;VALUE=DATE:' + r.scenarios.expected.date.replace(/-/g, '')));
  assert.ok(ics.endsWith('END:VCALENDAR\r\n'));
});

test('LT14 ready dates equal kick-off plus the product weeks', () => {
  const r = L.plan({kickoff: '2027-01-04', products: [P({licence_weeks: '0', translation_weeks: '0', screenshot_rounds: '0', signoff_weeks: '0'})]});
  assert.equal(r.products[0].ready.expected, '2027-01-04');
  const d = L.plan({kickoff: '2027-01-04', products: [P({licence_weeks: '2', translation_weeks: '10', screenshot_rounds: '2', signoff_weeks: '1'})]});
  assert.equal(d.products[0].language_date, '2027-03-29'); // 12 weeks
  assert.equal(d.products[0].ready.expected, '2027-04-05'); // 12 + 1 weeks
});

test('LT14 share-safe summary has counts, weeks and the driver, and no instrument, language or date', () => {
  const r = L.plan({kickoff: '2027-01-04', target: '2027-06-01', products: [P({instrument: 'Confidential Scale', language: 'Finnish', translation_weeks: '30'}), P({instrument: 'Other Diary', language: 'Danish'})]});
  const s = L.shareSummary(r);
  assert.match(s, /Rows: 2 instrument-language versions, 2 instruments, 2 languages/);
  assert.match(s, /optimistic \/ expected \/ pessimistic\): [\d.]+ \/ [\d.]+ \/ [\d.]+/);
  assert.match(s, /held up by: (licence|translation and screenshot review)/);
  for (const leak of ['Confidential', 'Finnish', 'Danish', 'Diary', '2027', 'Scale']) assert.ok(!s.includes(leak), leak);
  assert.equal(L.shareSummary({errors: ['x'], scenarios: {}, products: []}), '');
});
