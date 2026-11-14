/* ClinicOps eCOA delivery workbench rules 1.0.0. No network, storage or document inference. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const SCHEMA = 'clinicops-ecoa-workbench/1';

  const text = v => typeof v === 'string' && v.trim().length > 0;
  const object = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

  /* ---- Plans: one instrument-language product on the critical path ---- */
  const STEPS = ['licence', 'translation', 'screenshots', 'licensor_signoff', 'submission'];
  const STEP_LABELS = {
    licence: 'Electronic-use licence',
    translation: 'Translation / linguistic validation',
    screenshots: 'Screenshot review',
    licensor_signoff: 'Copyright-holder sign-off',
    submission: 'Ethics / regulatory submission'
  };
  /* A step that consumes another step's output. An existing translation may
     predate the licence, and a submission may be made on paper versions, so
     neither has a prerequisite. Testing is a study-level gate (see Quality):
     providers differ on whether language screens are reviewed before or
     after the source build is accepted. */
  const PREREQUISITES = {
    licence: [],
    translation: [],
    screenshots: ['translation'],
    licensor_signoff: ['licence', 'screenshots'],
    submission: []
  };
  const STEP_STATES = ['not started', 'in progress', 'done', 'blocked', 'not applicable'];
  const PRODUCT_STATUSES = ['not started', 'in progress', 'blocked', 'ready', 'unresolved', 'requires qualified review'];

  function isoDate(v) {
    if (typeof v !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(v)) return false;
    const t = Date.parse(v + 'T00:00:00Z');
    return !Number.isNaN(t) && new Date(t).toISOString().slice(0, 10) === v;
  }
  function dayDiff(from, to) {
    return Math.round((Date.parse(to + 'T00:00:00Z') - Date.parse(from + 'T00:00:00Z')) / 86400000);
  }

  /* Deterministic status of one product row. The tool never decides that a
     step is acceptable; it only reports what the recorded states imply. */
  function productStatus(row, today) {
    const messages = [];
    const states = STEPS.map(s => (STEP_STATES.includes(row[s]) ? row[s] : 'not started'));
    const applicable = STEPS.filter((s, i) => states[i] !== 'not applicable');
    const state = s => states[STEPS.indexOf(s)];
    let status;
    let next = null;
    let blockedAt = null;

    if (states.includes('not applicable') && !text(row.na_reason)) {
      status = 'unresolved';
      messages.push('A step is marked not applicable without a recorded reason.');
    } else if (applicable.length === 0) {
      status = 'unresolved';
      messages.push('Every step is marked not applicable; nothing can be confirmed.');
    } else {
      const firstOpen = applicable.find(s => state(s) !== 'done') || null;
      const outOfSequence = applicable.filter(s => state(s) === 'done' &&
        PREREQUISITES[s].some(p => applicable.includes(p) && state(p) !== 'done'));
      blockedAt = applicable.find(s => state(s) === 'blocked') || null;
      if (outOfSequence.length) {
        status = 'requires qualified review';
        for (const s of outOfSequence) {
          const missing = PREREQUISITES[s].filter(p => applicable.includes(p) && state(p) !== 'done');
          messages.push(STEP_LABELS[s] + ' is recorded as done before ' + missing.map(p => STEP_LABELS[p]).join(' and ') + '.');
        }
        next = firstOpen;
      } else if (blockedAt) {
        status = 'blocked';
        next = blockedAt;
      } else if (firstOpen === null) {
        status = 'ready';
      } else if (applicable.every(s => state(s) === 'not started')) {
        status = 'not started';
        next = firstOpen;
      } else {
        status = 'in progress';
        next = firstOpen;
      }
    }

    let daysToDue = null;
    let late = false;
    if (isoDate(row.due) && isoDate(today)) {
      daysToDue = dayDiff(today, row.due);
      late = status !== 'ready' && daysToDue < 0;
    }
    return {status, next_step: next, blocked_at: blockedAt, days_to_due: daysToDue, late, messages};
  }

  function planSummary(rows, today) {
    const byStatus = Object.fromEntries(PRODUCT_STATUSES.map(s => [s, 0]));
    const waitingAt = Object.fromEntries(STEPS.map(s => [s, 0]));
    const languages = {};
    let late = 0;
    const evaluated = rows.map(row => {
      const r = productStatus(row, today);
      byStatus[r.status] += 1;
      if (r.next_step) waitingAt[r.next_step] += 1;
      if (r.late) late += 1;
      const lang = text(row.language) ? row.language.trim() : '(no language)';
      languages[lang] = languages[lang] || {total: 0, ready: 0};
      languages[lang].total += 1;
      if (r.status === 'ready') languages[lang].ready += 1;
      return {row, result: r};
    });
    const bottleneck = STEPS.reduce((best, s) => (waitingAt[s] > (best ? waitingAt[best] : 0) ? s : best), null);
    return {total: rows.length, by_status: byStatus, waiting_at: waitingAt, bottleneck, late, languages, evaluated};
  }

  /* ---- Plans: protocol schedule of assessments against the design specification ---- */
  const norm = v => String(v === null || v === undefined ? '' : v).normalize('NFKC').trim().replace(/\s+/g, ' ').toLowerCase();
  function parseSchedule(raw) {
    const rows = [];
    const errors = [];
    String(raw || '').split(/\r?\n/).forEach((line, index) => {
      if (!line.trim()) return;
      const cells = line.split(/[;\t|]/).map(c => c.trim());
      if (cells.length < 2 || !cells[0] || !cells[1]) {
        errors.push('line ' + (index + 1) + ': expected "instrument; timepoint; window (optional)"'); return;
      }
      rows.push({instrument: cells[0], timepoint: cells[1], window: cells[2] || '', line: index + 1});
    });
    return {rows, errors};
  }
  /* The protocol is the reference. Nothing here decides which side is right. */
  function reconcileSchedule(protocolRows, specRows) {
    const key = r => norm(r.instrument) + '\u0001' + norm(r.timepoint);
    const index = rows => {
      const map = new Map();
      for (const r of rows) { if (!map.has(key(r))) map.set(key(r), []); map.get(key(r)).push(r); }
      return map;
    };
    const proto = index(protocolRows);
    const spec = index(specRows);
    const findings = [];
    for (const [k, list] of proto) {
      const p = list[0];
      const hits = spec.get(k) || [];
      let status, detail;
      if (list.length > 1) { status = 'conflicting evidence'; detail = 'Listed ' + list.length + ' times in the protocol schedule.'; }
      else if (!hits.length) { status = 'missing evidence'; detail = 'In the protocol schedule; not found in the specification.'; }
      else if (hits.length > 1) { status = 'conflicting evidence'; detail = 'Listed ' + hits.length + ' times in the specification.'; }
      else if (!text(p.window) && !text(hits[0].window)) { status = 'aligned'; detail = 'Instrument and timepoint match; no window recorded on either side.'; }
      else if (!text(p.window) || !text(hits[0].window)) { status = 'unresolved'; detail = 'Window recorded on one side only.'; }
      else if (norm(p.window) === norm(hits[0].window)) { status = 'aligned'; detail = 'Instrument, timepoint and window match.'; }
      else { status = 'mismatch signal'; detail = 'Window differs.'; }
      findings.push({instrument: p.instrument, timepoint: p.timepoint, protocol_window: p.window,
        specification_window: hits.length ? hits[0].window : '', status, detail});
    }
    for (const [k, list] of spec) {
      if (proto.has(k)) continue;
      const s = list[0];
      findings.push({instrument: s.instrument, timepoint: s.timepoint, protocol_window: '', specification_window: s.window,
        status: 'requires qualified review', detail: 'In the specification; not found in the protocol schedule. Check scope and contract.'});
    }
    const counts = {};
    for (const f of findings) counts[f.status] = (counts[f.status] || 0) + 1;
    return {findings, counts, total: findings.length};
  }

  /* ---- Risk: transparent band matrix, never a hidden number ---- */
  const BANDS = ['low', 'medium', 'high'];
  function exposure(probability, impact) {
    if (!BANDS.includes(probability) || !BANDS.includes(impact)) return 'not rated';
    const p = BANDS.indexOf(probability);
    const i = BANDS.indexOf(impact);
    if (p + i >= 3) return 'high';
    if (p + i === 2) return 'medium';
    return 'low';
  }

  /* ---- Issues: which surfaces a change is expected to reach ---- */
  function changeImpact(selectedIds, rules, surfaces) {
    const known = new Set(rules.map(r => r.id));
    const unknown = selectedIds.filter(id => !known.has(id));
    if (unknown.length) throw new Error('unknown change type: ' + unknown.join(', '));
    const bySurface = new Map();
    for (const rule of rules) {
      if (!selectedIds.includes(rule.id)) continue;
      for (const hit of rule.surfaces) {
        if (!own(surfaces, hit.id)) throw new Error('rule ' + rule.id + ' names unknown surface ' + hit.id);
        if (!bySurface.has(hit.id)) bySurface.set(hit.id, []);
        bySurface.get(hit.id).push({change: rule.id, label: rule.label, why: hit.why});
      }
    }
    return Object.keys(surfaces).filter(id => bySurface.has(id)).map(id => ({
      surface: id,
      label: surfaces[id],
      triggers: bySurface.get(id),
      status: 'missing evidence',
      owner: '',
      evidence: ''
    }));
  }

  /* A change surface can only close with an owner and evidence; "not
     applicable" needs a reason. The machine status is kept alongside. */
  function closeSurface(item, patch) {
    const next = Object.assign({}, item, patch);
    if (next.review_state === 'closed with evidence' && !(text(next.owner) && text(next.evidence))) {
      throw new Error('closing a surface requires an owner and closure evidence');
    }
    if (next.review_state === 'not applicable' && !text(next.reason)) {
      throw new Error('not applicable requires a reason');
    }
    return next;
  }

  /* ---- Quality: draft UAT script skeleton with stated coverage ---- */
  function uatScripts(input, areas) {
    const list = v => (Array.isArray(v) ? v.map(x => String(x).trim()).filter(Boolean) : []);
    const instruments = list(input.instruments);
    const timepoints = list(input.timepoints);
    const devices = list(input.devices);
    const languages = list(input.languages);
    if (!instruments.length) throw new Error('at least one instrument is required');
    if (!timepoints.length) throw new Error('at least one timepoint is required');
    if (!devices.length) throw new Error('at least one device mode is required');
    const langs = languages.length ? languages : ['(source language)'];
    const rows = [];
    const add = (area, instrument, timepoint, device, language) => rows.push({
      id: 'UAT-' + String(rows.length + 1).padStart(3, '0'),
      area: area.label,
      objective: area.objective,
      instrument, timepoint, device, language,
      requirement_ref: '',
      expected_result: '',
      result: 'not run',
      tester: '',
      evidence: ''
    });
    for (const area of areas) {
      if (area.scope === 'instrument-timepoint') {
        for (const ins of instruments) for (const tp of timepoints) add(area, ins, tp, devices[0], langs[0]);
      } else if (area.scope === 'instrument') {
        for (const ins of instruments) add(area, ins, timepoints[0], devices[0], langs[0]);
      } else if (area.scope === 'device') {
        for (const dev of devices) add(area, instruments[0], timepoints[0], dev, langs[0]);
      } else if (area.scope === 'language') {
        for (const lang of langs) add(area, instruments[0], timepoints[0], devices[0], lang);
      } else if (area.scope === 'once') {
        add(area, '(all)', '(n/a)', devices[0], langs[0]);
      } else {
        throw new Error('unknown coverage scope: ' + area.scope);
      }
    }
    const coverage = {
      instruments: instruments.length, timepoints: timepoints.length,
      devices: devices.length, languages: langs.length, scripts: rows.length,
      full_cross_product: instruments.length * timepoints.length * devices.length * langs.length * areas.length
    };
    return {rows, coverage};
  }

  const DEFECT_BANDS = ['critical', 'major', 'minor'];
  function defectSummary(defects) {
    const open = Object.fromEntries(DEFECT_BANDS.map(b => [b, 0]));
    let closed = 0;
    let unbanded = 0;
    for (const d of defects) {
      const isClosed = d.state === 'closed';
      if (isClosed) { closed += 1; continue; }
      if (DEFECT_BANDS.includes(d.band)) open[d.band] += 1; else unbanded += 1;
    }
    return {open, closed, unbanded, total: defects.length,
      exit_blocked: open.critical > 0 || unbanded > 0};
  }

  /* ---- Checklists and gates ---- */
  function checklistSummary(items, states) {
    let confirmed = 0, open = 0, na = 0, naWithoutReason = 0;
    const openItems = [];
    for (const item of items) {
      const st = (states && states[item.id]) || {};
      if (st.state === 'confirmed') confirmed += 1;
      else if (st.state === 'not applicable') {
        na += 1;
        if (!text(st.note)) { naWithoutReason += 1; openItems.push(item.id); }
      } else { open += 1; openItems.push(item.id); }
    }
    return {total: items.length, confirmed, open, na, na_without_reason: naWithoutReason,
      open_items: openItems, complete: open === 0 && naWithoutReason === 0};
  }

  /* ---- Progress: tolerances and management by exception ---- */
  function toNumber(v) {
    if (typeof v === 'number') return Number.isFinite(v) ? v : null;
    if (!text(v)) return null;
    const n = Number(String(v).trim().replace(',', '.'));
    return Number.isFinite(n) ? n : null;
  }
  function kpiStatus(kpi) {
    const target = toNumber(kpi.target), tolerance = toNumber(kpi.tolerance), actual = toNumber(kpi.actual);
    if (actual === null) return 'no data';
    if (target === null || tolerance === null) return 'no tolerance set';
    if (kpi.direction !== 'max' && kpi.direction !== 'min') return 'no tolerance set';
    const worse = (a, b) => (kpi.direction === 'max' ? a > b : a < b);
    if (worse(target, tolerance)) return 'no tolerance set';
    if (worse(actual, tolerance)) return 'exception';
    if (worse(actual, target)) return 'tolerance threatened';
    return 'within tolerance';
  }

  function parseCounts(raw) {
    const rows = [];
    const errors = [];
    String(raw || '').split(/\r?\n/).forEach((line, index) => {
      if (!line.trim()) return;
      const cells = line.split(/[;\t,]/).map(c => c.trim());
      if (index === 0 && cells.length >= 3 && toNumber(cells[1]) === null && toNumber(cells[2]) === null) return;
      const expected = toNumber(cells[1]), completed = toNumber(cells[2]);
      if (cells.length < 3 || !cells[0] || expected === null || completed === null) {
        errors.push('line ' + (index + 1) + ': expected "group, expected, completed"'); return;
      }
      if (expected < 0 || completed < 0 || !Number.isInteger(expected) || !Number.isInteger(completed)) {
        errors.push('line ' + (index + 1) + ': counts must be whole numbers of zero or more'); return;
      }
      if (completed > expected) { errors.push('line ' + (index + 1) + ': completed exceeds expected'); return; }
      rows.push({group: cells[0], expected, completed});
    });
    return {rows, errors};
  }
  function completion(rows, minimumPct) {
    const min = toNumber(minimumPct);
    const pct = (c, e) => (e > 0 ? Math.round((c / e) * 1000) / 10 : null);
    const out = rows.map(r => {
      const rate = pct(r.completed, r.expected);
      return {group: r.group, expected: r.expected, completed: r.completed, rate,
        flag: rate === null ? 'no expected entries' : (min !== null && rate < min ? 'below tolerance' : 'within tolerance')};
    });
    const expected = rows.reduce((s, r) => s + r.expected, 0);
    const completed = rows.reduce((s, r) => s + r.completed, 0);
    return {rows: out, total: {expected, completed, rate: pct(completed, expected)},
      below: out.filter(r => r.flag === 'below tolerance').length};
  }

  /* ---- Export safety ---- */
  function csvCell(v) {
    let s = v === null || v === undefined ? '' : String(v);
    if (/^\s*[=+\-@]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }
  function toCSV(rows, columns) {
    const head = columns.map(c => csvCell(c.label)).join(',');
    const body = rows.map(r => columns.map(c => csvCell(r[c.key])).join(','));
    return [head].concat(body).join('\r\n') + '\r\n';
  }

  /* ---- Workspace file: the only persistence is a file the user keeps ---- */
  const LISTS = ['organisation', 'products', 'schedule', 'risks', 'issues', 'surfaces', 'defects', 'changes', 'kpis', 'counts', 'lessons', 'uat_scripts'];
  const LIMIT_ROWS = 2000;
  const LIMIT_TEXT = 4000;
  function emptyWorkspace() {
    const w = {schema: SCHEMA, tool_version: VERSION, study: {name: '', reference: '', stage: 'starting-up', first_participant: ''},
      business_case: {}, tolerances: {}, checklists: {}, completion_minimum: ''};
    for (const key of LISTS) w[key] = [];
    return w;
  }
  function cleanValue(v, path) {
    if (v === null || v === undefined) return '';
    if (typeof v === 'number' || typeof v === 'boolean') return String(v);
    if (typeof v !== 'string') throw new Error(path + ': only text values are accepted');
    if (v.length > LIMIT_TEXT) throw new Error(path + ': text longer than ' + LIMIT_TEXT + ' characters');
    return v;
  }
  function cleanRecord(rec, path) {
    if (!object(rec)) throw new Error(path + ': expected an object');
    const out = {};
    for (const key of Object.keys(rec)) {
      if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue;
      out[key] = cleanValue(rec[key], path + '.' + key);
    }
    return out;
  }
  function validateWorkspace(data) {
    if (!object(data)) throw new Error('workspace file must be a JSON object');
    if (data.schema !== SCHEMA) throw new Error('unsupported workspace schema: ' + String(data.schema));
    const w = emptyWorkspace();
    if (own(data, 'study')) Object.assign(w.study, cleanRecord(data.study, 'study'));
    if (own(data, 'business_case')) w.business_case = cleanRecord(data.business_case, 'business_case');
    if (own(data, 'tolerances')) w.tolerances = cleanRecord(data.tolerances, 'tolerances');
    if (own(data, 'completion_minimum')) w.completion_minimum = cleanValue(data.completion_minimum, 'completion_minimum');
    for (const key of LISTS) {
      if (!own(data, key)) continue;
      if (!Array.isArray(data[key])) throw new Error(key + ': expected a list');
      if (data[key].length > LIMIT_ROWS) throw new Error(key + ': more than ' + LIMIT_ROWS + ' rows');
      w[key] = data[key].map((rec, i) => cleanRecord(rec, key + '[' + i + ']'));
    }
    if (own(data, 'checklists')) {
      if (!object(data.checklists)) throw new Error('checklists: expected an object');
      for (const listId of Object.keys(data.checklists)) {
        if (listId === '__proto__' || listId === 'constructor' || listId === 'prototype') continue;
        const list = data.checklists[listId];
        if (!object(list)) throw new Error('checklists.' + listId + ': expected an object');
        w.checklists[listId] = {};
        for (const itemId of Object.keys(list)) {
          if (itemId === '__proto__' || itemId === 'constructor' || itemId === 'prototype') continue;
          const rec = cleanRecord(list[itemId], 'checklists.' + listId + '.' + itemId);
          if (!['open', 'confirmed', 'not applicable'].includes(rec.state || 'open')) {
            throw new Error('checklists.' + listId + '.' + itemId + ': unknown state');
          }
          w.checklists[listId][itemId] = {state: rec.state || 'open', note: rec.note || ''};
        }
      }
    }
    return w;
  }

  /* ---- Progress: highlight report (plain text, for the project board) ---- */
  function highlightReport(w, ctx) {
    const today = ctx.today;
    const plan = planSummary(w.products, today);
    const kpis = w.kpis.map(k => ({name: k.name, status: kpiStatus(k), actual: k.actual, unit: k.unit}));
    const exceptions = kpis.filter(k => k.status === 'exception');
    const threatened = kpis.filter(k => k.status === 'tolerance threatened');
    const risks = w.risks.map(r => ({title: r.title, exposure: exposure(r.probability, r.impact), owner: r.owner, state: r.state}))
      .filter(r => r.state !== 'closed');
    const highRisks = risks.filter(r => r.exposure === 'high');
    const defects = defectSummary(w.defects);
    const openIssues = w.issues.filter(i => i.state !== 'closed');
    const openSurfaces = w.surfaces.filter(s => s.review_state !== 'closed with evidence' && s.review_state !== 'not applicable');
    const openChanges = w.changes.filter(c => c.state !== 'closed');
    const lines = [];
    const push = s => lines.push(s);
    push('eCOA DELIVERY HIGHLIGHT REPORT');
    push('Study: ' + (text(w.study.name) ? w.study.name : '[study]') + (text(w.study.reference) ? ' (' + w.study.reference + ')' : ''));
    push('Stage: ' + (ctx.stageLabel || w.study.stage) + ' · Date: ' + today + ' · Workbench rules v' + VERSION);
    if (text(w.study.first_participant)) {
      push('First participant planned: ' + w.study.first_participant +
        (isoDate(w.study.first_participant) && isoDate(today) ? ' (' + dayDiff(today, w.study.first_participant) + ' days from report date)' : ''));
    }
    push('');
    push('1. STATUS AGAINST TOLERANCES');
    if (!kpis.length) push('  No tolerances recorded.');
    else {
      push('  Exceptions (escalate to the project board): ' + exceptions.length);
      exceptions.forEach(k => push('    [!] ' + k.name + ': ' + k.actual + ' ' + (k.unit || '')));
      push('  Tolerance threatened: ' + threatened.length);
      threatened.forEach(k => push('    [~] ' + k.name + ': ' + k.actual + ' ' + (k.unit || '')));
      push('  Within tolerance: ' + kpis.filter(k => k.status === 'within tolerance').length +
        ' · No data or no tolerance set: ' + kpis.filter(k => k.status === 'no data' || k.status === 'no tolerance set').length);
    }
    push('');
    push('2. PRODUCTS (instrument-language versions): ' + plan.total);
    PRODUCT_STATUSES.forEach(s => { if (plan.by_status[s]) push('  ' + s + ': ' + plan.by_status[s]); });
    if (plan.late) push('  Past due and not ready: ' + plan.late);
    const waiting = STEPS.filter(s => plan.waiting_at[s]).map(s => STEP_LABELS[s] + ': ' + plan.waiting_at[s]);
    if (waiting.length) push('  Waiting at — ' + waiting.join(' · '));
    const sched = w.schedule.filter(f => f.status && f.status !== 'aligned').length;
    if (w.schedule.length) push('  Schedule of assessments against specification: ' + (w.schedule.length - sched) + ' aligned, ' + sched + ' to resolve');
    push('');
    push('3. QUALITY');
    push('  Testing findings open — critical: ' + defects.open.critical + ', major: ' + defects.open.major + ', minor: ' + defects.open.minor +
      (defects.unbanded ? ', unbanded: ' + defects.unbanded : '') + ' · closed: ' + defects.closed);
    (ctx.checklists || []).forEach(c => push('  ' + c.label + ': ' + c.summary.confirmed + '/' + c.summary.total + ' confirmed, ' +
      c.summary.open + ' open' + (c.summary.na ? ', ' + c.summary.na + ' not applicable' : '')));
    push('');
    push('4. RISKS (open): ' + risks.length + ' · high exposure: ' + highRisks.length);
    highRisks.forEach(r => push('    [!] ' + r.title + (text(r.owner) ? ' — owner: ' + r.owner : ' — NO OWNER')));
    push('');
    push('5. ISSUES AND CHANGE');
    push('  Open issues: ' + openIssues.length + ' · Change surfaces without closure evidence: ' + openSurfaces.length +
      ' · Open data change requests: ' + openChanges.length);
    push('');
    const escalate = exceptions.length > 0 || defects.open.critical > 0;
    push('6. DECISION REQUESTED FROM THE PROJECT BOARD');
    push(escalate
      ? '  Exception: at least one tolerance is exceeded or a critical testing finding is open. The project manager cannot proceed on own authority.'
      : '  None. The stage is forecast to stay within the tolerances recorded.');
    push('');
    push('This report structures recorded information. It is not a compliance determination. Decisions stay with the sponsor, the investigator and their qualified staff.');
    return lines.join('\n') + '\n';
  }

  const api = {VERSION, SCHEMA, STEPS, STEP_LABELS, STEP_STATES, PRODUCT_STATUSES, BANDS, DEFECT_BANDS, LISTS,
    isoDate, productStatus, planSummary, parseSchedule, reconcileSchedule, exposure, changeImpact, closeSurface, uatScripts, defectSummary,
    checklistSummary, kpiStatus, parseCounts, completion, csvCell, toCSV, emptyWorkspace, validateWorkspace, highlightReport};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsEcoaCore = api;
})(typeof globalThis === 'object' ? globalThis : this);
