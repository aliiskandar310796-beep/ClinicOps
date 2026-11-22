/* ClinicOps visit burden estimator rules 1.0.0. No network, storage or document inference.
   Adds up minutes and items the user enters, by visit and by study week. It does not know how long any
   instrument takes; every figure is the user's. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const SCHEMA = 'clinicops-burden/1';

  const text = v => typeof v === 'string' && v.trim().length > 0;
  const key = s => String(s || '').trim().toLowerCase();
  function amount(v) {
    if (v === '' || v === null || v === undefined) return null;
    const n = Number(String(v).replace(',', '.'));
    return isFinite(n) && n >= 0 && n <= 1000000 ? n : NaN;
  }
  /* Study weeks may be negative: screening is usually before baseline. */
  function weekValue(v) {
    if (v === '' || v === null || v === undefined) return null;
    const n = Number(String(v).replace(',', '.'));
    return isFinite(n) && n >= -520 && n <= 1040 ? n : NaN;
  }
  const r1 = n => Math.round(n * 10) / 10;

  function splitNames(s) { return String(s || '').split(/[;,\n]/).map(x => x.trim()).filter(Boolean); }

  /* input: {instruments:[{name,minutes,items}], visits:[{name,week,instruments:'a; b'}],
             diaries:[{instrument,per_week,from_week,to_week}], caps:{minutes_per_visit,items_per_visit,minutes_per_week}} */
  function estimate(input) {
    const out = {errors: [], flags: [], visits: [], weeks: [], totals: null};
    const inst = {};
    (input.instruments || []).forEach((i, n) => {
      if (!i || !text(i.name)) return;
      const minutes = amount(i.minutes), items = amount(i.items);
      if (Number.isNaN(minutes) || Number.isNaN(items)) out.errors.push('Instrument ' + (n + 1) + ': minutes and items must be numbers from 0 to 1,000,000.');
      inst[key(i.name)] = {name: i.name.trim(), minutes: Number.isNaN(minutes) ? null : minutes, items: Number.isNaN(items) ? null : items, used: false};
    });
    if (!Object.keys(inst).length) out.errors.push('Add at least one instrument.');
    const caps = input.caps || {};
    const capMin = amount(caps.minutes_per_visit), capItems = amount(caps.items_per_visit), capWeek = amount(caps.minutes_per_week);
    if (out.errors.length) return out;

    function sumFor(names, label) {
      let minutes = 0, items = 0, missing = [];
      names.forEach(nm => {
        const i = inst[key(nm)];
        if (!i) { out.flags.push({level: 'check', msg: label + ': "' + nm + '" is not in the instrument list.'}); return; }
        i.used = true;
        if (i.minutes === null) missing.push(i.name); else minutes += i.minutes;
        if (i.items !== null) items += i.items;
      });
      missing.forEach(m => out.flags.push({level: 'gap', msg: label + ': no minutes entered for ' + m + '; its time is counted as zero.'}));
      return {minutes, items};
    }

    const visitWeek = {};
    (input.visits || []).forEach((v, n) => {
      if (!v || (!text(v.name) && !text(v.instruments))) return;
      const label = text(v.name) ? v.name.trim() : 'Visit ' + (n + 1);
      const wk = weekValue(v.week);
      if (wk === null || Number.isNaN(wk)) { out.flags.push({level: 'gap', msg: label + ': study week is empty, not a number, or outside -520 to 1040; the visit is left out of the weekly view.'}); }
      const s = sumFor(splitNames(v.instruments), label);
      const row = {name: label, week: (wk === null || Number.isNaN(wk)) ? null : wk, minutes: r1(s.minutes), items: s.items};
      out.visits.push(row);
      if (row.week !== null) {
        const wkRounded = Math.round(row.week);
        if (wkRounded !== row.week) out.flags.push({level: 'check', msg: label + ': study week ' + row.week + ' is not a whole number; its minutes are counted in week ' + wkRounded + ' of the weekly view.'});
        visitWeek[wkRounded] = (visitWeek[wkRounded] || 0) + s.minutes;
      }
      if (capMin !== null && !Number.isNaN(capMin) && s.minutes > capMin) out.flags.push({level: 'over', msg: label + ': ' + r1(s.minutes) + ' min is over the ' + capMin + ' min limit you set.'});
      if (capItems !== null && !Number.isNaN(capItems) && s.items > capItems) out.flags.push({level: 'over', msg: label + ': ' + s.items + ' items is over the ' + capItems + ' item limit you set.'});
    });

    const diaryWeek = {};
    (input.diaries || []).forEach((d, n) => {
      if (!d || !text(d.instrument)) return;
      const label = 'Diary ' + (n + 1) + ' (' + d.instrument.trim() + ')';
      const per = amount(d.per_week), from = weekValue(d.from_week), to = weekValue(d.to_week);
      if ([per, from, to].some(x => x === null || Number.isNaN(x))) { out.flags.push({level: 'gap', msg: label + ': times per week, first week (-520 to 1040) and last week must all be numbers.'}); return; }
      if (to < from) { out.flags.push({level: 'check', msg: label + ': last week is before first week; the diary is left out.'}); return; }
      if (to - from > 520) { out.flags.push({level: 'check', msg: label + ': longer than 520 weeks; the diary is left out.'}); return; }
      if (Math.round(from) !== from || Math.round(to) !== to) out.flags.push({level: 'check', msg: label + ': weeks are not whole numbers; the diary runs from week ' + Math.round(from) + ' to week ' + Math.round(to) + '.'});
      const s = sumFor([d.instrument], label);
      for (let w = Math.round(from); w <= Math.round(to); w++) diaryWeek[w] = (diaryWeek[w] || 0) + per * s.minutes;
    });

    const all = Object.keys(visitWeek).concat(Object.keys(diaryWeek)).map(Number);
    if (all.length) {
      const first = Math.min.apply(null, all), last = Math.max.apply(null, all);
      for (let w = first; w <= last; w++) {
        const m = (visitWeek[w] || 0) + (diaryWeek[w] || 0);
        out.weeks.push({week: w, visit_minutes: r1(visitWeek[w] || 0), diary_minutes: r1(diaryWeek[w] || 0), minutes: r1(m)});
        if (capWeek !== null && !Number.isNaN(capWeek) && m > capWeek) out.flags.push({level: 'over', msg: 'Week ' + w + ': ' + r1(m) + ' min is over the ' + capWeek + ' min weekly limit you set.'});
      }
    }
    Object.keys(inst).forEach(k => { if (!inst[k].used) out.flags.push({level: 'check', msg: inst[k].name + ' is in the list but is not used at any visit or in any diary.'}); });
    const total = out.weeks.reduce((s, w) => s + w.minutes, 0);
    const peak = out.weeks.reduce((m, w) => w.minutes > m.minutes ? w : m, {week: null, minutes: 0});
    const peakVisit = out.visits.reduce((m, v) => v.minutes > m.minutes ? v : m, {name: null, minutes: 0});
    out.totals = {minutes: r1(total), hours: r1(total / 60), weeks_covered: out.weeks.length, peak_week: peak.week, peak_week_minutes: peak.minutes,
      peak_visit: peakVisit.name, peak_visit_minutes: peakVisit.minutes, visits: out.visits.length};
    return out;
  }

  const csvCell = v => {
    let s = v === null || v === undefined ? '' : String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  function toCSV(result) {
    const lines = [['section', 'name_or_week', 'visit_minutes', 'diary_minutes', 'total_minutes', 'items'].join(',')];
    result.visits.forEach(v => lines.push(['visit', v.name + (v.week === null ? '' : ' (week ' + v.week + ')'), v.minutes, '', v.minutes, v.items].map(csvCell).join(',')));
    result.weeks.forEach(w => lines.push(['week', w.week, w.visit_minutes, w.diary_minutes, w.minutes, ''].map(csvCell).join(',')));
    return lines.join('\n') + '\n';
  }

  function validateWorkspace(w) {
    const errs = [];
    if (!w || typeof w !== 'object' || Array.isArray(w)) return ['Not a workspace file.'];
    if (w.schema !== SCHEMA) errs.push('Unexpected schema.');
    ['instruments', 'visits', 'diaries'].forEach(k => {
      if (!Array.isArray(w[k])) errs.push(k + ' must be a list.');
      else if (w[k].length > 300) errs.push('Too many ' + k + ' (limit 300).');
      else if (w[k].some(x => !x || typeof x !== 'object' || Array.isArray(x))) errs.push(k + ' has a row that is not an object.');
    });
    return errs;
  }

  const api = {VERSION, SCHEMA, estimate, toCSV, csvCell, splitNames, amount, weekValue, validateWorkspace};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsBurden = api;
})(typeof globalThis === 'object' ? globalThis : this);
