const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const C = require('../docs/assets/change-surface-core.js');

const basePacket = () => ({schema_version: '1.0', asset: 'ClinicOps Change Surface Mapper', surfaces: [{surface: 'IFU', status: 'affected'}], counts: {affected: 1}});

test('CS01 languages are split on commas, semicolons and new lines, trimmed and de-duplicated case-insensitively', () => {
  const r = C.parseLanguages(' da-DK, sv-SE;nb-NO\nDA-dk\r\n  fi   FI ,, ');
  assert.deepEqual(r.list, ['da-DK', 'sv-SE', 'nb-NO', 'fi FI']);
  assert.equal(r.truncated, false);
  assert.deepEqual(C.parseLanguages('').list, []);
  assert.deepEqual(C.parseLanguages(null).list, []);
  assert.deepEqual(C.parseLanguages(undefined).list, []);
});

test('CS02 the language list and each entry are capped, and truncation is reported', () => {
  const many = Array.from({length: 45}, (_, i) => 'L' + i).join(',');
  const r = C.parseLanguages(many);
  assert.equal(r.list.length, C.MAX_LANGUAGES);
  assert.equal(r.truncated, true);
  const long = C.parseLanguages('x'.repeat(100));
  assert.equal(long.list[0].length, C.MAX_LANGUAGE_LENGTH);
  assert.equal(long.truncated, true);
});

test('CS03 only known deliverable ids survive, in catalogue order, without duplicates', () => {
  const d = C.normaliseDeliverables(['web', 'ifu', 'ifu', 'bogus', '<script>']);
  assert.deepEqual(d.map(x => x.id), ['ifu', 'web']);
  assert.deepEqual(C.normaliseDeliverables(null), []);
  assert.deepEqual(C.normaliseDeliverables('ifu'), []);
});

test('CS04 an unused dimension is null, adds no lines and leaves the packet untouched', () => {
  assert.equal(C.languageDimension(), null);
  assert.equal(C.languageDimension({languages: '  ', deliverables: [], note: ' '}), null);
  assert.deepEqual(C.summaryLines(null), []);
  const p = basePacket();
  const out = C.attach(p, null);
  assert.equal(out, p);
  assert.equal('language_versions' in out, false);
});

test('CS05 combinations to confirm is languages x deliverables, and only when both are given', () => {
  const both = C.languageDimension({languages: 'da-DK, sv-SE, nb-NO', deliverables: ['ifu', 'label']});
  assert.equal(both.combinations_to_confirm, 6);
  assert.deepEqual(both.deliverables.map(d => d.id), ['label', 'ifu']);
  const onlyLangs = C.languageDimension({languages: 'da-DK'});
  assert.equal(onlyLangs.combinations_to_confirm, null);
  const onlyDeliverables = C.languageDimension({deliverables: ['web']});
  assert.equal(onlyDeliverables.combinations_to_confirm, null);
  assert.deepEqual(onlyDeliverables.languages, []);
});

test('CS06 the note is trimmed and capped, and the boundary statement is carried', () => {
  const d = C.languageDimension({note: '  ' + 'n'.repeat(900) + '  '});
  assert.equal(d.note.length, C.MAX_NOTE_LENGTH);
  assert.equal(d.basis, C.BOUNDARY);
  assert.match(C.BOUNDARY, /does not decide which language versions or deliverables a change reaches/);
});

test('CS07 attach returns a new packet and does not mutate the original', () => {
  const p = basePacket();
  const dim = C.languageDimension({languages: 'da-DK', deliverables: ['ifu']});
  const out = C.attach(p, dim);
  assert.notEqual(out, p);
  assert.equal('language_versions' in p, false);
  assert.equal(out.language_versions.combinations_to_confirm, 1);
  assert.equal(out.schema_version, '1.0');
  assert.deepEqual(out.surfaces, p.surfaces);
});

test('CS08 the brief lists languages, deliverables and combinations in neutral wording', () => {
  const dim = C.languageDimension({languages: 'da-DK, sv-SE', deliverables: ['ifu', 'participant-material'], note: 'Delta goes to the language provider'});
  const text = C.summaryLines(dim).join('\n');
  assert.match(text, /Language versions: da-DK, sv-SE/);
  assert.match(text, /Instructions for use, including electronic/);
  assert.match(text, /Combinations to confirm: 2 language versions x 2 deliverables = 4/);
  assert.match(text, /Note: Delta goes to the language provider/);
  assert.doesNotMatch(text, /must|required|non-?complian|violation/i);
});

test('CS09 a half-filled dimension says what is missing instead of inventing a count', () => {
  const text = C.summaryLines(C.languageDimension({languages: 'da-DK'})).join('\n');
  assert.match(text, /Deliverables that may be touched: none ticked/);
  assert.match(text, /list at least one language version and tick at least one deliverable/);
  assert.doesNotMatch(text, /= \d/);
});

test('CS10 the page loads the core, keeps its privacy contract and builds the checkboxes from the catalogue', () => {
  const html = fs.readFileSync(path.join(__dirname, '..', 'docs', 'change-surface-mapper.html'), 'utf8');
  assert.match(html, /<script src="assets\/change-surface-core\.js"><\/script>/);
  assert.match(html, /id="lang-list"/);
  assert.match(html, /CS\.DELIVERABLES\.map/);
  assert.match(html, /schema_version:"1\.0"/);
  const core = fs.readFileSync(path.join(__dirname, '..', 'docs', 'assets', 'change-surface-core.js'), 'utf8');
  for (const banned of ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'WebSocket', 'localStorage', 'sessionStorage']) {
    assert.equal(core.includes(banned), false, banned);
    assert.equal(html.includes(banned) && banned !== 'sessionStorage', false, banned);
  }
});
