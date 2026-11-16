const {test} = require('node:test');
const assert = require('node:assert/strict');
const C = require('../docs/assets/ctis-clock-core.js');

// Expected dates below were worked out by hand from Reg 536/2014 Arts 5-8 (calendar days, Day 0 = submission,
// weekend due dates roll to Monday, each roll delays the tasks after it).
const run = (o) => C.plan(Object.assign({winterStop: true}, o));
const at = (r, id) => r.milestones.find((m) => m.id === id).date;

test('CT01 no request for information: Mar 1 2027', () => {
  const r = run({submission: '2027-03-01'});
  assert.equal(at(r, 'validated'), '2027-03-11');
  assert.equal(at(r, 'p1-draft'), '2027-04-06');
  assert.equal(at(r, 'p1-review'), '2027-04-19'); // Apr 18 is a Sunday
  assert.equal(at(r, 'p1-cons'), '2027-04-26');
  assert.equal(at(r, 'p2-end'), '2027-04-26'); // Apr 25 is a Sunday
  assert.equal(r.decisionDate, '2027-05-03'); // May 1 is a Saturday
  assert.equal(r.totalDays, 63);
  assert.equal(r.nominalDays, 60);
});

test('CT02 winter stop: days 23 Dec to 7 Jan do not count (Dec 1 2026)', () => {
  const r = run({submission: '2026-12-01'});
  assert.equal(at(r, 'validated'), '2026-12-11');
  assert.equal(at(r, 'p1-draft'), '2027-01-22');
  assert.equal(at(r, 'p1-review'), '2027-02-03');
  assert.equal(at(r, 'p1-cons'), '2027-02-10');
  assert.equal(at(r, 'p2-end'), '2027-02-10');
  assert.equal(r.decisionDate, '2027-02-15');
});

test('CT03 validation request for information', () => {
  const r = run({submission: '2027-03-01', validationRfi: true});
  assert.equal(at(r, 'val-rfi'), '2027-03-11');
  assert.equal(at(r, 'val-resp'), '2027-03-22'); // Mar 21 is a Sunday
  assert.equal(at(r, 'validated'), '2027-03-29'); // Mar 27 is a Saturday
  assert.equal(at(r, 'p1-draft'), '2027-04-26');
  assert.equal(at(r, 'p1-review'), '2027-05-10');
  assert.equal(at(r, 'p1-cons'), '2027-05-17');
  assert.equal(at(r, 'p2-end'), '2027-05-13');
  assert.equal(r.decisionDate, '2027-05-24');
  assert.equal(r.nominalDays, 75); // 25 + 45 + 5
});

test('CT04 Part I request for information', () => {
  const r = run({submission: '2027-03-01', partIRfi: true});
  assert.equal(at(r, 'p1-rfi-resp'), '2027-05-10');
  assert.equal(at(r, 'p1-rfi-review'), '2027-05-24');
  assert.equal(at(r, 'p1-final'), '2027-05-31');
  assert.equal(r.decisionDate, '2027-06-07');
  assert.equal(r.nominalDays, 10 + 76 + 5);
});

test('CT05 Part II request for information', () => {
  const r = run({submission: '2027-03-01', partIIRfi: true});
  assert.equal(at(r, 'p2-rfi-resp'), '2027-05-10');
  assert.equal(at(r, 'p2-final'), '2027-05-31');
  assert.equal(at(r, 'p1-cons'), '2027-04-26');
  assert.equal(r.decisionDate, '2027-06-07');
});

test('CT06 advanced-therapy extension adds 50 days to Part I', () => {
  const r = run({submission: '2027-03-01', atmp: true});
  assert.equal(at(r, 'p1-atmp'), '2027-06-15');
  assert.equal(r.decisionDate, '2027-06-21'); // Jun 20 is a Sunday
  assert.equal(r.nominalDays, 10 + 95 + 5);
});

test('CT07 a listed holiday moves the due date to the next working day', () => {
  const r = run({submission: '2027-03-01', holidays: ['2027-03-11']});
  assert.equal(at(r, 'validated'), '2027-03-12');
  assert.equal(at(r, 'p1-draft'), '2027-04-07');
  assert.equal(at(r, 'p1-cons'), '2027-04-26');
  assert.equal(r.decisionDate, '2027-05-03');
});

test('CT08 submission on a Saturday still counts Day 0 as that day', () => {
  const r = run({submission: '2027-03-06'});
  assert.equal(at(r, 'validated'), '2027-03-16');
});

test('CT09 every request for information at once', () => {
  const r = run({submission: '2027-03-01', validationRfi: true, partIRfi: true, partIIRfi: true});
  assert.equal(at(r, 'validated'), '2027-03-29');
  assert.equal(at(r, 'p1-final'), '2027-06-21');
  assert.equal(at(r, 'p2-final'), '2027-06-14');
  assert.equal(r.decisionDate, '2027-06-28');
  assert.equal(r.nominalDays, 106);
});

test('CT10 invalid dates are rejected with a message', () => {
  const r = C.plan({submission: '2027-02-30'});
  assert.equal(r.ok, false);
  assert.match(r.errors[0], /valid date/);
  const h = C.plan({submission: '2027-03-01', holidays: ['nope']});
  assert.equal(h.ok, false);
});

test('CT11 winter stop boundaries', () => {
  assert.equal(C.inWinterStop(C.isoDate('2026-12-22')), false);
  assert.equal(C.inWinterStop(C.isoDate('2026-12-23')), true);
  assert.equal(C.inWinterStop(C.isoDate('2027-01-07')), true);
  assert.equal(C.inWinterStop(C.isoDate('2027-01-08')), false);
});

test('CT12 switching the winter stop off counts those days', () => {
  const r = C.plan({submission: '2026-12-01', winterStop: false});
  assert.equal(at(r, 'validated'), '2026-12-11');
  assert.equal(at(r, 'p1-draft'), '2027-01-06');
});

test('CT13 CSV neutralises formula starts and quotes commas', () => {
  assert.equal(C.csvCell('=1+1'), "'=1+1");
  assert.equal(C.csvCell('a,b'), '"a,b"');
  const csv = C.toCSV(run({submission: '2027-03-01'}));
  assert.ok(csv.startsWith('Date,Day,Milestone,Note\r\n'));
});

test('CT14 ICS has one all-day event per milestone and no external references', () => {
  const r = run({submission: '2027-03-01'});
  const ics = C.toICS(r, 'Study X');
  assert.ok(ics.startsWith('BEGIN:VCALENDAR\r\n') && ics.endsWith('END:VCALENDAR\r\n'));
  assert.equal((ics.match(/BEGIN:VEVENT/g) || []).length, r.milestones.length);
  assert.ok(ics.includes('DTSTART;VALUE=DATE:20270311'));
  assert.ok(ics.includes('DTEND;VALUE=DATE:20270312'));
  assert.ok(!/https?:/.test(ics.replace(/-\/\/ClinicOps/g, '')));
  const uids = ics.match(/UID:[^\r]+/g);
  assert.equal(new Set(uids).size, uids.length);
});
