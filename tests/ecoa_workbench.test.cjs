const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const C = require('../docs/assets/ecoa-workbench-core.js');
const D = require('../docs/assets/ecoa-workbench-data.js');

const TODAY = '2026-11-14';
const row = (over) => Object.assign({licence: 'not started', translation: 'not started', screenshots: 'not started', licensor_signoff: 'not started', submission: 'not started', na_reason: '', due: ''}, over);
const allDone = {licence: 'done', translation: 'done', screenshots: 'done', licensor_signoff: 'done', submission: 'done'};

// ---- Plans -------------------------------------------------------------
test('QA01 product status follows recorded states and never invents readiness', () => {
  assert.equal(C.productStatus(row({}), TODAY).status, 'not started');
  assert.equal(C.productStatus(row({licence: 'in progress'}), TODAY).status, 'in progress');
  assert.equal(C.productStatus(row({licence: 'done', translation: 'blocked'}), TODAY).status, 'blocked');
  assert.equal(C.productStatus(row(allDone), TODAY).status, 'ready');
  assert.equal(C.productStatus(row(allDone), TODAY).next_step, null);
  assert.equal(C.productStatus(row({licence: 'done'}), TODAY).next_step, 'translation');
});

test('QA01 not applicable needs a reason; all-not-applicable is unresolved', () => {
  const na = row(Object.assign({}, allDone, {translation: 'not applicable'}));
  assert.equal(C.productStatus(na, TODAY).status, 'unresolved');
  assert.equal(C.productStatus(Object.assign({}, na, {na_reason: 'Source-language version'}), TODAY).status, 'ready');
  const every = row({licence: 'not applicable', translation: 'not applicable', screenshots: 'not applicable', licensor_signoff: 'not applicable', submission: 'not applicable', na_reason: 'x'});
  assert.equal(C.productStatus(every, TODAY).status, 'unresolved');
});

test('QA01 out-of-sequence completion goes to qualified review, naming the missing prerequisite', () => {
  const r = C.productStatus(row({licensor_signoff: 'done', screenshots: 'in progress', licence: 'done'}), TODAY);
  assert.equal(r.status, 'requires qualified review');
  assert.match(r.messages.join(' '), /Copyright-holder sign-off is recorded as done before Screenshot review/);
  // an existing translation may predate the licence; a submission may precede screens
  assert.equal(C.productStatus(row({translation: 'done'}), TODAY).status, 'in progress');
  assert.equal(C.productStatus(row({submission: 'done'}), TODAY).status, 'in progress');
});

test('QA02 due dates: late only when not ready; invalid dates are ignored, not guessed', () => {
  assert.equal(C.productStatus(row({due: '2026-11-01'}), TODAY).late, true);
  assert.equal(C.productStatus(row(Object.assign({due: '2026-11-01'}, allDone)), TODAY).late, false);
  assert.equal(C.productStatus(row({due: '2026-12-01'}), TODAY).days_to_due, 17);
  assert.equal(C.productStatus(row({due: '2026-02-30'}), TODAY).days_to_due, null);
  assert.equal(C.productStatus(row({due: 'soon'}), TODAY).late, false);
  assert.equal(C.isoDate('2026-13-01'), false);
});

test('QA02 plan summary counts waiting steps and languages', () => {
  const s = C.planSummary([row({language: 'Danish'}), row(Object.assign({language: 'Danish'}, allDone)), row({language: 'Swedish', licence: 'done'})], TODAY);
  assert.equal(s.total, 3);
  assert.equal(s.by_status.ready, 1);
  assert.equal(s.waiting_at.licence, 1);
  assert.equal(s.waiting_at.translation, 1);
  assert.deepEqual(s.languages.Danish, {total: 2, ready: 1});
});

test('QA03 schedule comparison: protocol is the reference; nothing decides who is right', () => {
  const a = C.parseSchedule('ESD-7; Daily; 18:00-23:59\nEFS; Baseline\nEFS; Week 12; +/- 3 days\nPGI; Week 4; Mon\nPGI; Week 4; Mon').rows;
  const b = C.parseSchedule('esd-7 ;  daily ; 18:00-23:59\nEFS; Week 12; +/- 2 days\nEFS; Week 6\nPGI; Week 4; Mon').rows;
  const r = C.reconcileSchedule(a, b);
  const status = (i, t) => r.findings.find(f => f.instrument === i && f.timepoint === t).status;
  assert.equal(status('ESD-7', 'Daily'), 'aligned');
  assert.equal(status('EFS', 'Baseline'), 'missing evidence');
  assert.equal(status('EFS', 'Week 12'), 'mismatch signal');
  assert.equal(status('EFS', 'Week 6'), 'requires qualified review');
  assert.equal(status('PGI', 'Week 4'), 'conflicting evidence');
  assert.equal(C.reconcileSchedule([{instrument: 'A', timepoint: 'B', window: ''}], [{instrument: 'A', timepoint: 'B', window: '1h'}]).findings[0].status, 'unresolved');
  assert.equal(C.reconcileSchedule([{instrument: 'A', timepoint: 'B', window: ''}], [{instrument: 'a', timepoint: 'b', window: ''}]).findings[0].status, 'aligned');
});

test('QA03 schedule comparison normalises Danish letters and compatibility forms without folding them away', () => {
  const p = [{instrument: 'Træthed', timepoint: 'Uge 12', window: ''}];
  assert.equal(C.reconcileSchedule(p, [{instrument: 'TRÆTHED', timepoint: 'uge  12', window: ''}]).findings[0].status, 'aligned');
  assert.equal(C.reconcileSchedule(p, [{instrument: 'Traethed', timepoint: 'Uge 12', window: ''}]).findings[0].status, 'missing evidence');
});

test('QA03 schedule parsing reports bad lines instead of skipping them', () => {
  const r = C.parseSchedule('ok; Week 1\njust one cell\n;;\n');
  assert.equal(r.rows.length, 1);
  assert.equal(r.errors.length, 2);
  assert.match(r.errors[0], /line 2/);
});

// ---- Risk, issues -------------------------------------------------------
test('QA04 exposure matrix: every combination is as documented on the page', () => {
  const B = ['low', 'medium', 'high'];
  const expected = {'low,low': 'low', 'low,medium': 'low', 'low,high': 'medium', 'medium,low': 'low', 'medium,medium': 'medium', 'medium,high': 'high', 'high,low': 'medium', 'high,medium': 'high', 'high,high': 'high'};
  for (const p of B) for (const i of B) assert.equal(C.exposure(p, i), expected[p + ',' + i], p + ',' + i);
  assert.equal(C.exposure('', 'high'), 'not rated');
  assert.equal(C.exposure('high', undefined), 'not rated');
  assert.equal(C.exposure('HIGH', 'high'), 'not rated');
});

test('QA05 every change rule points only at known surfaces and carries a reason', () => {
  for (const rule of D.CHANGE_RULES) {
    assert.ok(rule.label && rule.surfaces.length, rule.id);
    for (const s of rule.surfaces) {
      assert.ok(Object.prototype.hasOwnProperty.call(D.SURFACES, s.id), rule.id + ' -> ' + s.id);
      assert.ok(s.why && s.why.length > 10, rule.id + ' ' + s.id);
    }
    assert.equal(new Set(rule.surfaces.map(s => s.id)).size, rule.surfaces.length, rule.id + ' duplicate surface');
  }
  assert.equal(new Set(D.CHANGE_RULES.map(r => r.id)).size, D.CHANGE_RULES.length);
});

test('QA05 change impact merges reasons, keeps order, starts open, and rejects unknown types', () => {
  const r = C.changeImpact(['ct-05', 'ct-03'], D.CHANGE_RULES, D.SURFACES);
  const ids = r.map(x => x.surface);
  assert.deepEqual(ids, Object.keys(D.SURFACES).filter(id => ids.includes(id)));
  assert.ok(r.every(x => x.status === 'missing evidence' && x.owner === '' && x.evidence === ''));
  assert.ok(r.find(x => x.surface === 'translation').triggers.length === 2);
  assert.throws(() => C.changeImpact(['ct-99'], D.CHANGE_RULES, D.SURFACES), /unknown change type/);
  assert.throws(() => C.changeImpact(['ct-01'], [{id: 'ct-01', label: 'x', surfaces: [{id: 'nope', why: 'x'}]}], D.SURFACES), /unknown surface/);
  assert.deepEqual(C.changeImpact([], D.CHANGE_RULES, D.SURFACES), []);
});

test('QA06 a surface closes only with owner and evidence; not applicable needs a reason', () => {
  const item = {owner: '', evidence: '', review_state: 'open'};
  assert.throws(() => C.closeSurface(item, {review_state: 'closed with evidence'}), /owner and closure evidence/);
  assert.throws(() => C.closeSurface(item, {review_state: 'closed with evidence', owner: 'QA'}), /owner and closure evidence/);
  assert.throws(() => C.closeSurface(item, {review_state: 'closed with evidence', owner: ' ', evidence: 'x'}), /owner and closure evidence/);
  assert.equal(C.closeSurface(item, {review_state: 'closed with evidence', owner: 'QA', evidence: 'ECO 4'}).review_state, 'closed with evidence');
  assert.throws(() => C.closeSurface(item, {review_state: 'not applicable'}), /reason/);
  assert.equal(C.closeSurface(item, {review_state: 'not applicable', reason: 'Country not in scope'}).reason, 'Country not in scope');
  assert.equal(item.review_state, 'open', 'input is not mutated');
});

// ---- Quality -------------------------------------------------------------
test('QA07 script skeleton: stated coverage, blank expected results, stable ids', () => {
  const r = C.uatScripts({instruments: ['A', 'B'], timepoints: ['D1', 'W12'], devices: ['iOS', 'Android'], languages: ['da', 'sv']}, D.UAT_AREAS);
  assert.equal(r.coverage.scripts, r.rows.length);
  assert.equal(new Set(r.rows.map(x => x.id)).size, r.rows.length);
  assert.ok(r.rows.every(x => x.expected_result === '' && x.result === 'not run' && x.tester === ''));
  assert.ok(r.coverage.full_cross_product > r.coverage.scripts);
  const schedule = r.rows.filter(x => x.area === 'Schedule and completion window');
  assert.equal(schedule.length, 4, 'instrument x timepoint');
  const devices = r.rows.filter(x => x.area === 'Reminders and alarms');
  assert.deepEqual(devices.map(x => x.device), ['iOS', 'Android']);
  const langs = r.rows.filter(x => x.area === 'Language-specific smoke check');
  assert.deepEqual(langs.map(x => x.language), ['da', 'sv']);
  const again = C.uatScripts({instruments: ['A', 'B'], timepoints: ['D1', 'W12'], devices: ['iOS', 'Android'], languages: ['da', 'sv']}, D.UAT_AREAS);
  assert.deepEqual(again.rows, r.rows);
});

test('QA07 script skeleton refuses empty or malformed input and trims blanks', () => {
  const ok = {instruments: ['A'], timepoints: ['T'], devices: ['D'], languages: []};
  assert.throws(() => C.uatScripts(Object.assign({}, ok, {instruments: ['  ', '']}), D.UAT_AREAS), /instrument/);
  assert.throws(() => C.uatScripts(Object.assign({}, ok, {timepoints: []}), D.UAT_AREAS), /timepoint/);
  assert.throws(() => C.uatScripts(Object.assign({}, ok, {devices: undefined}), D.UAT_AREAS), /device/);
  assert.throws(() => C.uatScripts(ok, [{id: 'x', scope: 'galaxy', label: 'x', objective: 'x'}]), /unknown coverage scope/);
  const r = C.uatScripts(Object.assign({}, ok, {instruments: [' A ', '', 'B']}), D.UAT_AREAS);
  assert.ok(r.rows.some(x => x.instrument === 'A') && r.rows.some(x => x.instrument === 'B'));
  assert.equal(r.rows[0].language, '(source language)');
});

test('QA07 testing areas are well-formed', () => {
  assert.equal(new Set(D.UAT_AREAS.map(a => a.id)).size, D.UAT_AREAS.length);
  for (const a of D.UAT_AREAS) assert.ok(a.label && a.objective && ['instrument-timepoint', 'instrument', 'device', 'language', 'once'].includes(a.scope), a.id);
});

test('QA08 findings: critical or unbanded findings hold the exit; closed ones do not', () => {
  const s = C.defectSummary([{band: 'critical', state: 'open'}, {band: 'major', state: 'open'}, {band: 'minor', state: 'closed'}, {band: '', state: 'open'}, {band: 'critical', state: 'closed'}]);
  assert.deepEqual(s.open, {critical: 1, major: 1, minor: 0});
  assert.equal(s.closed, 2);
  assert.equal(s.unbanded, 1);
  assert.equal(s.exit_blocked, true);
  assert.equal(C.defectSummary([{band: 'minor', state: 'open'}]).exit_blocked, false);
  assert.equal(C.defectSummary([]).exit_blocked, false);
});

test('QA09 checklists: not applicable without a reason stays open', () => {
  const items = [{id: 'a'}, {id: 'b'}, {id: 'c'}, {id: 'd'}];
  const s = C.checklistSummary(items, {a: {state: 'confirmed'}, b: {state: 'not applicable', note: ''}, c: {state: 'not applicable', note: 'Not in scope'}});
  assert.equal(s.confirmed, 1);
  assert.equal(s.na, 2);
  assert.equal(s.na_without_reason, 1);
  assert.equal(s.open, 1);
  assert.equal(s.complete, false);
  assert.deepEqual(s.open_items.sort(), ['b', 'd']);
  assert.equal(C.checklistSummary(items, {a: {state: 'confirmed'}, b: {state: 'confirmed'}, c: {state: 'not applicable', note: 'x'}, d: {state: 'confirmed'}}).complete, true);
  assert.equal(C.checklistSummary(items, undefined).open, 4);
});

// ---- Progress -----------------------------------------------------------
test('QA10 tolerance status for upper and lower limits, and for incomplete setups', () => {
  const max = (target, tolerance, actual) => C.kpiStatus({direction: 'max', target, tolerance, actual});
  assert.equal(max('0', '10', '0'), 'within tolerance');
  assert.equal(max('0', '10', '6'), 'tolerance threatened');
  assert.equal(max('0', '10', '10'), 'tolerance threatened');
  assert.equal(max('0', '10', '11'), 'exception');
  const min = (target, tolerance, actual) => C.kpiStatus({direction: 'min', target, tolerance, actual});
  assert.equal(min('90', '85', '92'), 'within tolerance');
  assert.equal(min('90', '85', '87'), 'tolerance threatened');
  assert.equal(min('90', '85', '84,9'), 'exception', 'decimal comma accepted');
  assert.equal(max('0', '10', ''), 'no data');
  assert.equal(max('', '10', '3'), 'no tolerance set');
  assert.equal(max('10', '5', '3'), 'no tolerance set', 'a limit tighter than its target is not accepted');
  assert.equal(min('85', '90', '88'), 'no tolerance set');
  assert.equal(C.kpiStatus({direction: 'sideways', target: '1', tolerance: '2', actual: '3'}), 'no tolerance set');
  assert.equal(max('0', '10', 'abc'), 'no data');
});

test('QA11 counts: strict parsing, honest rates, no division by zero', () => {
  const p = C.parseCounts('group, expected, completed\nSite 1, 140, 131\nSite 2; 56; 44\nbad line\nSite 4, 10, 12\nSite 5, 1.5, 1\nSite 6, -1, 0');
  assert.equal(p.rows.length, 2);
  assert.equal(p.errors.length, 4);
  const c = C.completion(p.rows.concat([{group: 'Empty', expected: 0, completed: 0}]), '90');
  assert.equal(c.rows[0].rate, 93.6);
  assert.equal(c.rows[0].flag, 'within tolerance');
  assert.equal(c.rows[1].flag, 'below tolerance');
  assert.equal(c.rows[2].flag, 'no expected entries');
  assert.equal(c.rows[2].rate, null);
  assert.equal(c.total.expected, 196);
  assert.equal(c.total.completed, 175);
  assert.equal(c.below, 1);
  assert.equal(C.completion(p.rows, '').below, 0, 'no tolerance set means nothing is flagged');
});

// ---- Export safety --------------------------------------------------------
test('QA12 spreadsheet formulas are neutralised and quotes, commas, Danish text survive', () => {
  for (const v of ['=1+2', '+cmd', '-cmd', '@SUM(A1)', ' =x', '\t=x', '\r=x', '\n@x']) assert.ok(C.csvCell(v).startsWith('"\''), JSON.stringify(v));
  assert.equal(C.csvCell('Blåbær "A", B'), '"Blåbær ""A"", B"');
  assert.equal(C.csvCell(null), '""');
  assert.equal(C.csvCell(0), '"0"');
  const csv = C.toCSV([{a: '=HYPERLINK("x")', b: 'æøå'}], [{key: 'a', label: 'A'}, {key: 'b', label: '=B'}]);
  assert.ok(csv.split('\r\n')[0].includes('"\'=B"'), 'header cells are neutralised too');
  assert.match(csv, /"'=HYPERLINK\(""x""\)"/);
  assert.ok(csv.endsWith('\r\n'));
});

// ---- Workspace file -------------------------------------------------------
test('QA13 workspace validation rejects other schemas, non-text values, oversize lists and text', () => {
  assert.throws(() => C.validateWorkspace(null), /JSON object/);
  assert.throws(() => C.validateWorkspace([]), /JSON object/);
  assert.throws(() => C.validateWorkspace({schema: 'other'}), /unsupported workspace schema/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, risks: {}}), /expected a list/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, risks: [1]}), /expected an object/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, risks: [{title: {x: 1}}]}), /only text values/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, risks: [{title: 'x'.repeat(4001)}]}), /longer than/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, risks: new Array(2001).fill({title: 'x'})}), /more than/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, checklists: {brief: {b01: {state: 'sort of'}}}}), /unknown state/);
  assert.throws(() => C.validateWorkspace({schema: C.SCHEMA, checklists: []}), /expected an object/);
});

test('QA13 workspace validation cannot be used to pollute prototypes', () => {
  const evil = JSON.parse('{"schema":"clinicops-ecoa-workbench/1","__proto__":{"polluted":"yes"},"study":{"__proto__":{"polluted":"yes"},"constructor":"x","name":"ok"},"risks":[{"__proto__":{"polluted":"yes"},"title":"t"}],"checklists":{"__proto__":{"x":{"state":"open"}},"brief":{"__proto__":{"state":"open"},"b01":{"state":"confirmed"}}}}');
  const w = C.validateWorkspace(evil);
  assert.equal(({}).polluted, undefined);
  assert.equal(w.study.name, 'ok');
  assert.equal(Object.prototype.hasOwnProperty.call(w.study, 'constructor'), false);
  assert.equal(w.checklists.brief.b01.state, 'confirmed');
  assert.equal(Object.prototype.hasOwnProperty.call(w.checklists.brief, '__proto__'), false);
});

test('QA13 the fictional example validates, round-trips and does not change when re-validated', () => {
  const w = C.validateWorkspace(JSON.parse(JSON.stringify(D.EXAMPLE)));
  const again = C.validateWorkspace(JSON.parse(JSON.stringify(w)));
  assert.deepEqual(again, w);
  assert.equal(w.products.length, 5);
  assert.ok(w.study.name.includes('fictional'));
  assert.ok(C.validateWorkspace({schema: C.SCHEMA}).products.length === 0, 'missing lists default to empty');
});

// ---- Report ----------------------------------------------------------------
test('QA14 the highlight report escalates exceptions and critical findings and says no more than recorded', () => {
  const w = C.validateWorkspace(JSON.parse(JSON.stringify(D.EXAMPLE)));
  const report = C.highlightReport(w, {today: TODAY, stageLabel: 'Build'});
  assert.match(report, /Exceptions \(escalate to the project board\): 1/);
  assert.match(report, /cannot proceed on own authority/);
  assert.match(report, /not a compliance determination/);
  assert.match(report, /107 days from report date/);
  const calm = C.validateWorkspace({schema: C.SCHEMA, study: {name: 'Empty'}});
  const calmReport = C.highlightReport(calm, {today: TODAY});
  assert.match(calmReport, /No tolerances recorded/);
  assert.match(calmReport, /None\. The stage is forecast to stay within the tolerances recorded\./);
  for (const banned of ['non-compliant', 'compliant with', 'approved for', 'safe to']) assert.ok(!report.toLowerCase().includes(banned), banned);
});

test('QA14 a report built from a blank study does not throw on any section', () => {
  const w = C.emptyWorkspace();
  assert.doesNotThrow(() => C.highlightReport(w, {today: TODAY}));
  w.risks.push({title: 'x', probability: 'high', impact: 'high', owner: '', state: 'open'});
  assert.match(C.highlightReport(w, {today: TODAY}), /NO OWNER/);
});

// ---- Content integrity ------------------------------------------------------
test('QA15 every checklist item and risk has an id, a plain reason, a valid basis and sources the page registers', () => {
  const html = fs.readFileSync(path.join(__dirname, '..', 'docs', 'ecoa-delivery-workbench.html'), 'utf8');
  const registered = new Set(Array.from(html.matchAll(/<tr id="src-([a-z0-9-]+)"/g)).map(m => m[1]));
  const seen = new Set();
  const check = (what, basis, src) => {
    assert.ok(Object.prototype.hasOwnProperty.call(D.BASIS, basis), what + ' basis ' + basis);
    for (const ref of src) assert.ok(registered.has(ref.split('#')[0]), what + ' cites unregistered source ' + ref);
    if (basis !== 'method') assert.ok(src.length > 0, what + ' claims a basis but cites no source');
    if (basis === 'method') assert.equal(src.length, 0, what + ' is method but cites a source');
  };
  for (const [listId, def] of Object.entries(D.CHECKLISTS)) {
    assert.ok(def.title && def.stage, listId);
    for (const g of def.groups) for (const it of g.items) {
      assert.ok(!seen.has(it.id), 'duplicate item id ' + it.id); seen.add(it.id);
      assert.ok(it.label.length > 8 && it.why.length > 8, it.id);
      assert.ok(!/[.]$/.test(it.label), it.id + ' label should not end with a full stop');
      check(it.id, it.basis, it.src);
    }
  }
  const riskIds = new Set();
  for (const r of D.RISKS) {
    assert.ok(!riskIds.has(r.id), 'duplicate risk id ' + r.id); riskIds.add(r.id);
    assert.ok(r.title && r.cause && r.effect && r.response, r.id);
    check(r.id, r.basis, r.src);
  }
  for (const id of registered) assert.ok(D.SOURCES !== null && id.length > 2);
});

test('QA16 every source in the register is used by something on the page or is flagged as context', () => {
  const html = fs.readFileSync(path.join(__dirname, '..', 'docs', 'ecoa-delivery-workbench.html'), 'utf8');
  const registered = Array.from(html.matchAll(/<tr id="src-([a-z0-9-]+)"/g)).map(m => m[1]);
  const used = new Set();
  for (const def of Object.values(D.CHECKLISTS)) for (const g of def.groups) for (const it of g.items) it.src.forEach(s => used.add(s.split('#')[0]));
  D.RISKS.forEach(r => r.src.forEach(s => used.add(s.split('#')[0])));
  for (const m of html.matchAll(/href="#src-([a-z0-9-]+)"/g)) used.add(m[1]);
  const context = new Set(['fda-ecsq', 'fda-pfdd']);
  for (const id of registered) {
    if (context.has(id)) {
      const row = html.match(new RegExp('<tr id="src-' + id + '"[\\s\\S]*?</tr>'))[0];
      assert.match(row, /Not mapped item by item/, id + ' is context only and must say so');
    } else assert.ok(used.has(id), 'source ' + id + ' is registered but nothing uses it');
  }
});

test('QA17 stage gates and tolerances line up with the checklists the page offers', () => {
  const ids = new Set(D.STAGES.map(s => s.id));
  assert.equal(ids.size, D.STAGES.length);
  for (const s of D.STAGES) if (s.gate) assert.ok(D.CHECKLISTS[s.gate], 'stage ' + s.id + ' gate ' + s.gate);
  assert.equal(D.TOLERANCES.length, 7);
  assert.deepEqual(D.TOLERANCES.map(t => t[0]), ['time', 'cost', 'scope', 'quality', 'risk', 'benefits', 'sustainability']);
  assert.equal(D.PRINCIPLES.length, 7);
  assert.equal(D.ROLES.length, 8);
  assert.ok(D.KPIS.every(k => ['max', 'min'].includes(k.direction)));
});

test('QA17 example data only uses states, bands and types the tool defines', () => {
  const w = C.validateWorkspace(JSON.parse(JSON.stringify(D.EXAMPLE)));
  for (const p of w.products) for (const s of C.STEPS) assert.ok(C.STEP_STATES.includes(p[s]), s + '=' + p[s]);
  for (const r of w.risks) { assert.ok(['', ...C.BANDS].includes(r.probability)); assert.ok(['', ...C.BANDS].includes(r.impact)); }
  for (const d of w.defects) assert.ok(['', ...C.DEFECT_BANDS].includes(d.band));
  for (const i of w.issues) assert.ok(D.ISSUE_TYPES.includes(i.type), i.type);
  for (const k of w.kpis) assert.ok(['max', 'min'].includes(k.direction));
  for (const id of Object.keys(w.checklists)) {
    const list = id.split(':')[0];
    const known = new Set(D.CHECKLISTS[list].groups.flatMap(g => g.items.map(i => i.id)));
    for (const item of Object.keys(w.checklists[id])) assert.ok(known.has(item), id + ' ' + item);
  }
});

test('QA18 performance: 2,000 products and 2,000 schedule lines evaluate well inside a second', () => {
  const rows = Array.from({length: 2000}, (_, i) => row({language: 'L' + (i % 7), licence: i % 3 ? 'done' : 'in progress', translation: 'done', due: '2026-12-01'}));
  let t = performance.now();
  const s = C.planSummary(rows, TODAY);
  assert.equal(s.total, 2000);
  assert.ok(performance.now() - t < 1000);
  const a = Array.from({length: 2000}, (_, i) => ({instrument: 'I' + (i % 40), timepoint: 'T' + i, window: ''}));
  t = performance.now();
  const r = C.reconcileSchedule(a, a.slice(0, 1500));
  assert.equal(r.total, 2000);
  assert.ok(performance.now() - t < 1000);
});
