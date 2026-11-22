/* ClinicOps CTIS initial-application clock 1.0.0. No network, storage or document inference.
   Date arithmetic on a user-entered submission date and the durations in Regulation (EU) No 536/2014
   Articles 5 to 8, as read from the Official Journal text and the EMA CTIS Sponsor Handbook (7 July 2026).
   Calendar days. Day 0 is the submission date. A planning aid, not legal advice. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const SCHEMA = 'clinicops-ctis-clock/1';

  /* Statutory durations in calendar days (Reg 536/2014). Every one can be read in SOURCES. */
  const DAYS = {
    validation: 10,          // Art 5(2): RMS validation period
    validationRfiSponsor: 10, // Art 5(3): sponsor response, at most
    validationRfiRms: 5,     // Art 5(3): RMS decision after the response
    partIAssessment: 26,     // Art 6(5): draft assessment report
    partIReview: 12,         // Art 6(5): coordinated review by Member States
    partIConsolidation: 7,   // Art 6(5): consolidation
    partIRfiSponsor: 12,     // Art 6(7): sponsor response, at most
    partIRfiReview: 12,      // Art 6(7)
    partIRfiConsolidation: 7, // Art 6(7)
    atmpExtension: 50,       // Art 6(7): expert consultation, ATMP and Annex point 1 products
    partII: 45,              // Art 7(1)
    partIIRfiSponsor: 12,    // Art 7(1): sponsor response, at most
    partIIRfiMs: 19,         // Art 7(1): Member State completion, at most
    decision: 5              // Art 8(1)
  };

  const SOURCES = [
    {id: 'reg536', label: 'Regulation (EU) No 536/2014, Articles 5 to 8', url: 'https://eur-lex.europa.eu/eli/reg/2014/536/oj'},
    {id: 'handbook', label: 'EMA CTIS Sponsor Handbook, section 3.1 (7 July 2026)', url: 'https://www.ema.europa.eu/en/human-regulatory-overview/research-development/clinical-trials-human-medicines/clinical-trials-information-system-ctis-online-support'},
    {id: 'reg1182', label: 'Regulation (EEC, Euratom) No 1182/71, Article 3 (weekends and holidays)', url: 'https://eur-lex.europa.eu/eli/reg/1971/1182/oj'}
  ];

  const DAY_MS = 86400000;

  function isoDate(s) {
    if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    const d = new Date(s + 'T00:00:00Z');
    return !isNaN(d) && d.toISOString().slice(0, 10) === s ? d : null;
  }
  function fmt(d) { return d.toISOString().slice(0, 10); }
  function plus(d, n) { return new Date(d.getTime() + n * DAY_MS); }
  function between(a, b) { return Math.round((b.getTime() - a.getTime()) / DAY_MS); }

  /* Winter clock stop: 23 December to 7 January inclusive do not count. 22 December and 8 January count. */
  function inWinterStop(d) {
    const m = d.getUTCMonth(), day = d.getUTCDate();
    return (m === 11 && day >= 23) || (m === 0 && day <= 7);
  }

  /* n counting days after start (start itself is Day 0 and is not counted). */
  function addCounting(start, n, winter) {
    let d = start, c = 0;
    while (c < n) {
      d = plus(d, 1);
      if (!(winter && inWinterStop(d))) c++;
    }
    return d;
  }

  function isNonWorking(d, holidays, winter) {
    const w = d.getUTCDay();
    return w === 0 || w === 6 || holidays.has(fmt(d)) || (winter && inWinterStop(d));
  }
  function roll(d, holidays, winter) {
    let x = d;
    while (isNonWorking(x, holidays, winter)) x = plus(x, 1);
    return x;
  }

  function normalise(opts) {
    const o = opts || {};
    const errors = [];
    const submission = isoDate(o.submission);
    if (!submission) errors.push('Enter the submission date as a valid date.');
    const holidays = new Set();
    (Array.isArray(o.holidays) ? o.holidays : []).forEach((h) => {
      if (isoDate(h)) holidays.add(h); else errors.push('Holiday "' + String(h).slice(0, 20) + '" is not a valid date.');
    });
    return {
      errors, submission, holidays,
      validationRfi: !!o.validationRfi, partIRfi: !!o.partIRfi, partIIRfi: !!o.partIIRfi, atmp: !!o.atmp,
      winter: o.winterStop !== false, rollForward: o.rollForward !== false
    };
  }

  /* The longest case with these switches, ignoring weekends, holidays and the winter stop. */
  function nominalDays(o) {
    const v = DAYS.validation + (o.validationRfi ? DAYS.validationRfiSponsor + DAYS.validationRfiRms : 0);
    const p1base = DAYS.partIAssessment + DAYS.partIReview + DAYS.partIConsolidation;
    const p1 = p1base + (o.atmp ? DAYS.atmpExtension : 0) +
      (o.partIRfi ? DAYS.partIRfiSponsor + DAYS.partIRfiReview + DAYS.partIRfiConsolidation : 0);
    const p2 = DAYS.partII + (o.partIIRfi ? DAYS.partIIRfiSponsor + DAYS.partIIRfiMs : 0);
    return v + Math.max(p1, p2) + DAYS.decision;
  }

  function plan(opts) {
    const n = normalise(opts);
    if (n.errors.length) return {ok: false, errors: n.errors};
    const step = (from, days) => {
      const raw = addCounting(from, days, n.winter);
      return n.rollForward ? roll(raw, n.holidays, n.winter) : raw;
    };
    const ms = [];
    const add = (id, label, date, note) => ms.push({id, label, date: fmt(date), day: between(n.submission, date), note: note || ''});
    add('submit', 'Application submitted (Day 0)', n.submission);

    let validation = step(n.submission, DAYS.validation);
    if (n.validationRfi) {
      add('val-rfi', 'Validation: request for information issued', validation, 'Latest date the reporting Member State asks.');
      const sponsor = step(validation, DAYS.validationRfiSponsor);
      add('val-resp', 'Validation: sponsor response due', sponsor, 'At most ' + DAYS.validationRfiSponsor + ' days; a missed deadline lapses the application in all Member States.');
      validation = step(sponsor, DAYS.validationRfiRms);
    }
    add('validated', 'Validation date', validation, 'Assumes the application is notified as valid on the last day. Parts I and II both run from this date.');

    const a = step(validation, DAYS.partIAssessment);
    add('p1-draft', 'Part I: draft assessment report', a);
    const b = step(a, DAYS.partIReview);
    add('p1-review', 'Part I: coordinated review ends', b);
    let p1 = step(b, DAYS.partIConsolidation);
    add('p1-cons', 'Part I: consolidation ends', p1, 'Reporting date if there is no extension or request for information.');
    if (n.atmp) {
      p1 = step(p1, DAYS.atmpExtension);
      add('p1-atmp', 'Part I: expert-consultation extension ends', p1, 'Up to ' + DAYS.atmpExtension + ' days, for advanced-therapy products and products listed in the Annex to Regulation (EC) No 726/2004.');
    }
    if (n.partIRfi) {
      const sp = step(p1, DAYS.partIRfiSponsor);
      add('p1-rfi-resp', 'Part I: sponsor response due', sp, 'Planning assumption: the request is issued when the assessment above ends. At most ' + DAYS.partIRfiSponsor + ' days.');
      const rv = step(sp, DAYS.partIRfiReview);
      add('p1-rfi-review', 'Part I: review of the response ends', rv);
      p1 = step(rv, DAYS.partIRfiConsolidation);
      add('p1-final', 'Part I: final consolidation ends', p1);
    }

    let p2 = step(validation, DAYS.partII);
    add('p2-end', 'Part II: assessment ends', p2, 'Each Member State assesses Part II for its own country, in parallel with Part I.');
    if (n.partIIRfi) {
      const sp2 = step(p2, DAYS.partIIRfiSponsor);
      add('p2-rfi-resp', 'Part II: sponsor response due', sp2, 'Planning assumption: the request is issued when the assessment above ends. At most ' + DAYS.partIIRfiSponsor + ' days.');
      p2 = step(sp2, DAYS.partIIRfiMs);
      add('p2-final', 'Part II: assessment completed', p2, 'Member State has at most ' + DAYS.partIIRfiMs + ' days after the response.');
    }

    const later = p1.getTime() >= p2.getTime() ? p1 : p2;
    const decision = step(later, DAYS.decision);
    add('decision', 'Decision due', decision, DAYS.decision + ' days after the later of the Part I reporting date and the end of Part II.');

    ms.sort((x, y) => (x.date < y.date ? -1 : x.date > y.date ? 1 : 0));
    return {
      ok: true, schema: SCHEMA, version: VERSION, milestones: ms,
      decisionDate: fmt(decision), totalDays: between(n.submission, decision),
      nominalDays: nominalDays(n),
      assumptions: {winterStop: n.winter, rollForward: n.rollForward, holidays: Array.from(n.holidays).sort()}
    };
  }

  function csvCell(v) {
    let s = String(v == null ? '' : v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function toCSV(result) {
    if (!result || !result.ok) return '';
    const rows = [['Date', 'Day', 'Milestone', 'Note']].concat(result.milestones.map((m) => [m.date, m.day, m.label, m.note]));
    return rows.map((r) => r.map(csvCell).join(',')).join('\r\n') + '\r\n';
  }

  function icsEscape(s) { return String(s).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n'); }
  function toICS(result, name) {
    if (!result || !result.ok) return '';
    const stamp = '20260101T000000Z';
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ClinicOps//CTIS clock ' + VERSION + '//EN', 'CALSCALE:GREGORIAN'];
    result.milestones.forEach((m, i) => {
      const d = isoDate(m.date), next = plus(d, 1);
      lines.push('BEGIN:VEVENT', 'UID:ctis-clock-' + m.date.replace(/-/g, '') + '-' + i + '@clinicops.dk', 'DTSTAMP:' + stamp,
        'DTSTART;VALUE=DATE:' + m.date.replace(/-/g, ''), 'DTEND;VALUE=DATE:' + fmt(next).replace(/-/g, ''),
        'SUMMARY:' + icsEscape((name ? name + ': ' : '') + m.label),
        'DESCRIPTION:' + icsEscape('Planning aid, not legal advice. Check the current rules. ' + (m.note || '')), 'END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    return lines.join('\r\n') + '\r\n';
  }

  const api = {VERSION, SCHEMA, DAYS, SOURCES, isoDate, inWinterStop, addCounting, roll, nominalDays, plan, toCSV, toICS, csvCell};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsCtisClock = api;
})(typeof globalThis === 'object' ? globalThis : this);
