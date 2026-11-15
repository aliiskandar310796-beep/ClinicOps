const {test} = require('node:test');
const assert = require('node:assert/strict');
const C = require('../docs/assets/coa-finder-core.js');

test('CF01 reporter decides the type, nothing else does', () => {
  assert.equal(C.classify({reporter: 'participant'}).type, 'PRO');
  assert.equal(C.classify({reporter: 'observer'}).type, 'ObsRO');
  assert.equal(C.classify({reporter: 'clinician'}).type, 'ClinRO');
  assert.equal(C.classify({reporter: 'task'}).type, 'PerfO');
  assert.equal(C.classify({}).type, null);
  assert.equal(C.classify({reporter: 'robot'}).complete, false);
});

test('CF02 follow-up answers raise flags but never change the type', () => {
  const a = C.classify({reporter: 'participant', interpreted: 'yes'});
  assert.equal(a.type, 'PRO');
  assert.ok(a.flags.some(f => /interprets or edits/.test(f)));
  const b = C.classify({reporter: 'observer', judgement: 'yes'});
  assert.equal(b.type, 'ObsRO');
  assert.ok(b.flags.length === 1);
  assert.ok(C.classify({reporter: 'clinician', judgement: 'no'}).flags.length === 1);
  assert.ok(C.classify({reporter: 'task', scored: 'no'}).flags.length === 1);
  assert.equal(C.classify({reporter: 'participant', interpreted: 'no'}).flags.length, 0);
});

test('CF03 every type has implications and a respondent', () => {
  C.TYPE_KEYS.forEach(k => {
    assert.ok(C.IMPLICATIONS[k].length >= 4, k);
    assert.ok(C.DEFAULT_RESPONDENT[k], k);
  });
});

const full = (o) => Object.assign({concept: 'Pain intensity', role: 'primary', instrument: 'NRS', version: '1.0', type: 'PRO', respondent: 'participant',
  mode: 'provisioned device', recall: '24 hours', languages: 'Danish, English', licence: 'granted', training: ''}, o || {});

test('CF04 a complete consistent row has no findings', () => {
  assert.deepEqual(C.checkRow(full()), []);
});

test('CF05 gaps are named, not guessed', () => {
  const f = C.checkRow(C.emptyRow());
  const msgs = f.map(x => x.msg).join(' ');
  assert.match(msgs, /Concept of interest/);
  assert.match(msgs, /Instrument is empty/);
  assert.match(msgs, /Type is not chosen/);
  assert.match(msgs, /Languages are empty/);
});

test('CF06 type and respondent or mode mismatches are flagged for a second look', () => {
  assert.ok(C.checkRow(full({respondent: 'clinician'})).some(x => /does not usually go with PRO/.test(x.msg)));
  assert.ok(C.checkRow(full({type: 'ClinRO', respondent: 'clinician', mode: 'participant’s own device', training: 'yes'})).some(x => /not completed by the participant alone/.test(x.msg)));
  assert.ok(C.checkRow(full({type: 'ClinRO', respondent: 'clinician', mode: 'site tablet', training: ''})).some(x => /Rater training/.test(x.msg)));
  assert.ok(C.checkRow(full({recall: ''})).some(x => /Recall period/.test(x.msg)));
});

test('CF07 licence findings: unavailable blocks, primary without grant sets the critical path', () => {
  assert.ok(C.checkRow(full({licence: 'not available'})).some(x => x.level === 'block'));
  assert.ok(C.checkRow(full({licence: 'requested'})).some(x => /critical path/.test(x.msg)));
  assert.ok(!C.checkRow(full({licence: 'requested', role: 'exploratory'})).some(x => /critical path/.test(x.msg)));
  assert.ok(C.checkRow(full({licence: 'not checked'})).some(x => /Licence not checked/.test(x.msg)));
});

test('CF08 summary counts types, languages and instrument-language products', () => {
  const s = C.summarise([full(), full({type: 'ClinRO', respondent: 'clinician', mode: 'site tablet', training: 'x', languages: 'Danish; Swedish'})]);
  assert.equal(s.rows, 2);
  assert.equal(s.by_type.PRO, 1);
  assert.equal(s.by_type.ClinRO, 1);
  assert.deepEqual(s.languages, ['danish', 'english', 'swedish']);
  assert.equal(s.instrument_language_products, 4);
  assert.equal(s.blocks, 0);
});

test('CF09 CSV neutralises formula injection and quotes fields', () => {
  assert.equal(C.csvCell('=1+1'), "'=1+1");
  assert.equal(C.csvCell('@x'), "'@x");
  assert.equal(C.csvCell('a,b'), '"a,b"');
  assert.equal(C.csvCell('say "hi"'), '"say ""hi"""');
  const csv = C.toCSV([full({concept: '=HYPERLINK("x")'})]);
  assert.ok(csv.split('\n')[1].startsWith('"\'=HYPERLINK'));
  assert.ok(csv.startsWith('concept,role,instrument'));
});

test('CF10 workspace validation rejects wrong shapes and oversize files', () => {
  assert.deepEqual(C.validateWorkspace({schema: C.SCHEMA, rows: [full()]}), []);
  assert.ok(C.validateWorkspace(null).length);
  assert.ok(C.validateWorkspace({schema: 'x', rows: []}).length);
  assert.ok(C.validateWorkspace({schema: C.SCHEMA, rows: [{concept: 5}]}).length);
  assert.ok(C.validateWorkspace({schema: C.SCHEMA, rows: new Array(501).fill(full())}).length);
});

test('CF11 module has no network, storage or eval', () => {
  const src = require('node:fs').readFileSync(require('node:path').join(__dirname, '../docs/assets/coa-finder-core.js'), 'utf8');
  assert.ok(!/fetch\(|XMLHttpRequest|localStorage|sessionStorage|eval\(|new Function|document\./.test(src));
});
