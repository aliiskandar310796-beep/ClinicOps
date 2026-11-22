const {test} = require('node:test');
const assert = require('node:assert/strict');
const C = require('../docs/assets/ops-map-core.js');
const data = require('../docs/assets/ops-map-data.js');

const slugs = data.steps.map((s) => s.slug);

test('OM01 data: 6 phases, 12 lanes, unique slugs, every lane and phase known', () => {
  assert.equal(data.phases.length, 6);
  assert.equal(data.lanes.length, 12);
  assert.equal(new Set(slugs).size, slugs.length);
  const lanes = new Set(data.lanes.map((l) => l.id)), phases = new Set(data.phases.map((p) => p.id));
  data.steps.forEach((s) => {
    assert.ok(phases.has(s.phase), s.slug);
    assert.ok(s.lanes.length > 0 && s.lanes.every((l) => lanes.has(l)), s.slug);
    assert.ok(['drug', 'device', 'both'].includes(s.overlay), s.slug);
  });
});

test('OM02 hash: default state gives an empty hash, and round-trips a full state', () => {
  assert.equal(C.buildHash(C.defaultState()), '');
  const state = {overlay: 'device', lane: 'safety', step: 'device-adverse-event-reporting'};
  const hash = C.buildHash(state);
  assert.equal(hash, '#overlay=device&lane=safety&step=device-adverse-event-reporting');
  assert.deepEqual(C.parseHash(hash, data), state);
});

test('OM03 hash: unknown values are dropped, never trusted', () => {
  const s = C.parseHash('#overlay=nope&lane=%3Cscript%3E&step=__proto__&x=1&overlay', data);
  assert.deepEqual(s, C.defaultState());
  assert.deepEqual(C.parseHash('#overlay=drug&lane=safety&step=missing-step', data), {overlay: 'drug', lane: 'safety', step: ''});
  assert.deepEqual(C.parseHash('#overlay=%E0%A4%A', data), C.defaultState()); // malformed escape
});

test('OM04 hash: the plain card anchor #step-<slug> selects that step', () => {
  assert.deepEqual(C.parseHash('#step-susar-reporting', data), {overlay: 'both', lane: 'all', step: 'susar-reporting'});
  assert.deepEqual(C.parseHash('#step-nonsense', data), C.defaultState());
  assert.deepEqual(C.parseHash('#phase-p2', data), C.defaultState());
});

test('OM05 filter: overlay and lane decide which steps show', () => {
  const drug = C.visibleSteps(data, {overlay: 'drug', lane: 'all', step: ''}).map((s) => s.slug);
  const device = C.visibleSteps(data, {overlay: 'device', lane: 'all', step: ''}).map((s) => s.slug);
  assert.ok(drug.includes('susar-reporting') && !device.includes('susar-reporting'));
  assert.ok(device.includes('device-application') && !drug.includes('device-application'));
  assert.ok(drug.includes('route-and-regime') && device.includes('route-and-regime'));
  assert.equal(C.visibleSteps(data, C.defaultState()).length, data.steps.length);
  const safety = C.visibleSteps(data, {overlay: 'both', lane: 'safety', step: ''});
  assert.ok(safety.length > 0 && safety.every((s) => s.lanes.includes('safety')));
});

test('OM06 overlayVisible: a fact tagged for one regime hides under the other', () => {
  assert.equal(C.overlayVisible('device', 'drug'), false);
  assert.equal(C.overlayVisible('drug', 'drug'), true);
  assert.equal(C.overlayVisible('both', 'device'), true);
  assert.equal(C.overlayVisible('drug', 'both'), true);
});

test('OM07 normaliseState: a linked step that the filter hides relaxes the filter', () => {
  const n = C.normaliseState({overlay: 'device', lane: 'safety', step: 'susar-reporting'}, data);
  assert.equal(n.step, 'susar-reporting');
  assert.equal(n.overlay, 'both');
  assert.equal(n.lane, 'all');
  const keep = C.normaliseState({overlay: 'drug', lane: 'safety', step: 'susar-reporting'}, data);
  assert.deepEqual(keep, {overlay: 'drug', lane: 'safety', step: 'susar-reporting'});
  assert.equal(C.normaliseState({overlay: 'both', lane: 'all', step: 'gone'}, data).step, '');
});

test('OM08 trace: set, clear and sanitise', () => {
  const t = C.emptyTrace();
  C.setTrace(t, 'susar-reporting', {status: 'settled'});
  C.setTrace(t, 'susar-reporting', {note: '  needs\u0007 sign-off \n  by Friday  '});
  assert.deepEqual(t['susar-reporting'], {status: 'settled', note: 'needs sign-off by Friday'});
  C.setTrace(t, 'susar-reporting', {status: 'bogus'});
  assert.equal(t['susar-reporting'].status, '');
  C.setTrace(t, 'susar-reporting', {note: ''});
  assert.equal(t['susar-reporting'], undefined);
  C.setTrace(t, 'route-and-regime', {note: 'x'.repeat(500)});
  assert.equal(t['route-and-regime'].note.length, C.NOTE_MAX);
});

test('OM09 export then import round-trips; boundary and schema are in the file', () => {
  const t = C.emptyTrace();
  C.setTrace(t, 'susar-reporting', {status: 'open', note: 'check RSI'});
  C.setTrace(t, 'device-application', {status: 'na'});
  const text = C.toJSON({trace: t, label: 'Fictional study', overlay: 'drug'}, data, '2026-11-16T10:00:00.000Z');
  const doc = JSON.parse(text);
  assert.equal(doc.schema, C.TRACE_SCHEMA);
  assert.equal(doc.map_version, data.version);
  assert.match(doc.decision_boundary, /Planning aid, not advice/);
  assert.equal(doc.exported_at, '2026-11-16T10:00:00.000Z');
  assert.equal(doc.trace.length, 2);
  const r = C.parseImport(text, data);
  assert.equal(r.ok, true);
  assert.equal(r.applied, 2);
  assert.equal(r.ignored, 0);
  assert.equal(r.label, 'Fictional study');
  assert.equal(r.overlay, 'drug');
  assert.deepEqual(r.trace['susar-reporting'], {status: 'open', note: 'check RSI'});
});

test('OM10 import: rejects the wrong schema, non-JSON, empty and oversize input', () => {
  assert.equal(C.parseImport('', data).ok, false);
  assert.equal(C.parseImport('{not json', data).ok, false);
  assert.equal(C.parseImport('[]', data).ok, false);
  assert.equal(C.parseImport(JSON.stringify({schema: 'other', trace: []}), data).ok, false);
  assert.equal(C.parseImport(JSON.stringify({schema: C.TRACE_SCHEMA}), data).ok, false);
  assert.equal(C.parseImport('x'.repeat(C.IMPORT_MAX_BYTES + 1), data).ok, false);
});

test('OM11 import: unknown steps, bad statuses and prototype keys are skipped and counted', () => {
  const doc = {
    schema: C.TRACE_SCHEMA,
    label: '<img src=x onerror=alert(1)>',
    overlay: 'sideways',
    trace: [
      {slug: 'susar-reporting', status: 'settled', note: 'ok'},
      {slug: '__proto__', status: 'settled', note: 'x'},
      {slug: 'constructor', status: 'open'},
      {slug: 'not-a-step', status: 'open'},
      {slug: 'route-and-regime', status: 'weird', note: ''},
      'garbage',
      null
    ]
  };
  const r = C.parseImport(JSON.stringify(doc), data);
  assert.equal(r.ok, true);
  assert.equal(r.applied, 1);
  assert.equal(r.ignored, 6);
  assert.equal(r.overlay, 'both');
  assert.equal(Object.getPrototypeOf(r.trace), null);
  assert.equal(r.trace['__proto__'], undefined);
  assert.equal(({}).polluted, undefined);
  assert.equal(r.trace['route-and-regime'], undefined);
  assert.ok(r.label.length <= C.LABEL_MAX);
});

test('OM12 CSV: boundary row first, one row per step, spreadsheet formulas neutralised', () => {
  const t = C.emptyTrace();
  C.setTrace(t, 'susar-reporting', {status: 'settled', note: '=HYPERLINK("http://x","y")'});
  C.setTrace(t, 'route-and-regime', {note: '+1+1'});
  const csv = C.toCSV({trace: t, label: ''}, data);
  const lines = csv.trim().split('\r\n');
  assert.match(lines[0], /^"Planning aid, not advice/);
  assert.equal(lines[1], 'Slug,Step,Phase,Lanes,Regime,My status,My note');
  assert.ok(csv.includes('"\'=HYPERLINK(""http://x"",""y"")"'));
  assert.ok(csv.includes(",'+1+1"));
  assert.equal(lines.length, 2 + data.steps.length);
  assert.ok(csv.includes('susar-reporting'));
  assert.equal(C.csvCell('a,b'), '"a,b"');
});
