/* ClinicOps COA type finder and inventory rules 1.0.0. No network, storage or document inference.
   The four type names follow the usual regulatory taxonomy (patient-, observer- and clinician-reported
   outcomes and performance outcomes). The questions only sort a described assessment into a type; they do
   not judge whether an instrument is fit for a trial endpoint. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const SCHEMA = 'clinicops-coa-inventory/1';

  const TYPES = {
    PRO: {
      name: 'Patient-reported outcome (PRO)',
      who: 'The participant, about their own health or experience.',
      note: 'The answer is recorded as given, without interpretation by a clinician or anyone else.'
    },
    ObsRO: {
      name: 'Observer-reported outcome (ObsRO)',
      who: 'A parent, caregiver or other observer who is not a health professional, about what they can see.',
      note: 'Signs, events or behaviours that can be seen; no medical judgement is needed to report them.'
    },
    ClinRO: {
      name: 'Clinician-reported outcome (ClinRO)',
      who: 'A trained health professional, using clinical judgement.',
      note: 'Needs professional training to interpret what is seen, so rater training and consistency matter.'
    },
    PerfO: {
      name: 'Performance outcome (PerfO)',
      who: 'The participant carries out a standardised task; the result is measured or scored.',
      note: 'A task done under set conditions, scored by an administrator or measured by the task itself.'
    }
  };
  const TYPE_KEYS = Object.keys(TYPES);

  const REPORTERS = {
    participant: 'The participant answers about themselves',
    observer: 'A caregiver or other non-professional reports what they observe',
    clinician: 'A trained health professional rates, using clinical judgement',
    task: 'The participant performs a standardised task that is scored or measured'
  };

  const MODES = ['participant’s own device', 'provisioned device', 'site tablet', 'web link', 'telephone (IVR)', 'paper', 'interview, site staff', 'other'];
  const ROLES = ['primary', 'key secondary', 'secondary', 'exploratory', 'safety', 'screening'];
  const LICENCE = ['not checked', 'requested', 'granted', 'not required', 'not available'];
  const DEFAULT_RESPONDENT = {PRO: 'participant', ObsRO: 'observer', ClinRO: 'clinician', PerfO: 'task'};

  const text = v => typeof v === 'string' && v.trim().length > 0;
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

  /* Q1 decides the type. Q2 and Q3 only raise flags: they catch descriptions that do not fit the answer given. */
  function classify(a) {
    const out = {type: null, reasons: [], flags: [], complete: false};
    if (!a || !own(REPORTERS, a.reporter)) { out.flags.push('Choose who provides the information.'); return out; }
    const map = {participant: 'PRO', observer: 'ObsRO', clinician: 'ClinRO', task: 'PerfO'};
    out.type = map[a.reporter];
    out.reasons.push(REPORTERS[a.reporter] + ' → ' + TYPES[out.type].name + '.');
    if (a.reporter === 'participant' && a.interpreted === 'yes') {
      out.flags.push('If a clinician interprets or edits the participant’s answer, it is no longer a pure patient report. Consider ClinRO, or record the answer unchanged.');
    }
    if (a.reporter === 'observer' && a.judgement === 'yes') {
      out.flags.push('If the observer needs clinical judgement to report, the assessment is closer to a clinician report. Check who is qualified to give it.');
    }
    if (a.reporter === 'clinician' && a.judgement === 'no') {
      out.flags.push('A clinician report normally needs clinical judgement. If only visible events are counted, an observer report may fit better.');
    }
    if (a.reporter === 'task' && a.scored === 'no') {
      out.flags.push('A performance outcome needs a defined task and a defined way of scoring or measuring it.');
    }
    if (a.reporter === 'participant' && a.child === 'yes') {
      out.flags.push('For young children a caregiver often reports instead. Check whether the instrument has an observer version and an age range for self-report.');
    }
    out.complete = true;
    return out;
  }

  /* What each type asks of the delivery team. Planning prompts, not requirements. */
  const IMPLICATIONS = {
    PRO: [
      'Device and access: whose device, who supplies it, what if the participant has none.',
      'Language and reading level: every language needs a licensed, validated version and a screen check.',
      'Recall period and timing window: the schedule must match what the instrument asks about.',
      'Missing data: decide who is reminded, when, and what happens to a late entry.'
    ],
    ObsRO: [
      'Who may report: define the observer, and what happens if a different person reports.',
      'Training and instructions for the observer, in their language.',
      'Record who reported each entry, so analysis can tell reporters apart.',
      'Burden on the observer, who is also often a caregiver.'
    ],
    ClinRO: [
      'Rater qualification and training before the first rating, with a record kept.',
      'Consistency between raters and sites: decide how it is checked.',
      'Who may rate, and what happens when the usual rater is absent.',
      'Source and audit trail: where the rating is first recorded.'
    ],
    PerfO: [
      'Standard conditions: space, equipment, instructions, number of attempts.',
      'Administrator training, and a script so every site gives the same instructions.',
      'Device or equipment calibration, if the task is measured by a device.',
      'Time of day, rest and practice effects: record what the protocol requires.'
    ]
  };

  function emptyRow() {
    return {concept: '', role: '', instrument: '', version: '', type: '', respondent: '', mode: '', recall: '', languages: '', licence: 'not checked', training: ''};
  }

  /* Checks one inventory row against itself. Findings are prompts to look again, never a verdict. */
  function checkRow(row) {
    const f = [];
    const add = (level, msg) => f.push({level, msg});
    if (!text(row.concept)) add('gap', 'Concept of interest is empty: say what the assessment is meant to capture.');
    if (!text(row.instrument)) add('gap', 'Instrument is empty.');
    if (!TYPE_KEYS.includes(row.type)) add('gap', 'Type is not chosen.');
    else {
      if (text(row.respondent) && row.respondent !== DEFAULT_RESPONDENT[row.type]) {
        add('check', 'Respondent “' + row.respondent + '” does not usually go with ' + row.type + ' (expected ' + DEFAULT_RESPONDENT[row.type] + ').');
      }
      if ((row.type === 'ClinRO' || row.type === 'PerfO') && row.mode === 'participant’s own device') {
        add('check', row.type + ' is not completed by the participant alone on their own device. Check the mode.');
      }
      if ((row.type === 'PRO' || row.type === 'ObsRO') && !text(row.recall)) {
        add('gap', 'Recall period is empty. The schedule has to match it.');
      }
      if (row.type === 'ClinRO' && !text(row.training)) {
        add('gap', 'Rater training is empty. ClinRO ratings depend on trained raters.');
      }
    }
    if (!text(row.role)) add('gap', 'Role in the study (primary, secondary, exploratory) is empty.');
    if (!text(row.mode)) add('gap', 'Mode of administration is empty.');
    if (!text(row.languages)) add('gap', 'Languages are empty.');
    if (!text(row.version)) add('gap', 'Instrument version is empty. A different version is a different instrument for licensing and translation.');
    if (row.licence === 'not checked' && text(row.instrument)) add('check', 'Licence not checked for ' + row.instrument + '.');
    if (row.licence === 'not available') add('block', 'No licence available. The instrument cannot be used electronically until this is resolved.');
    if (row.role === 'primary' && TYPE_KEYS.includes(row.type) && row.licence !== 'granted' && row.licence !== 'not required') {
      add('check', 'Primary assessment without a granted licence: this one sets the critical path.');
    }
    return f;
  }

  function summarise(rows) {
    const by = {PRO: 0, ObsRO: 0, ClinRO: 0, PerfO: 0, unset: 0};
    let gaps = 0, checks = 0, blocks = 0;
    rows.forEach(r => {
      by[TYPE_KEYS.includes(r.type) ? r.type : 'unset'] += 1;
      checkRow(r).forEach(x => { if (x.level === 'gap') gaps++; else if (x.level === 'check') checks++; else blocks++; });
    });
    const languages = new Set();
    rows.forEach(r => String(r.languages || '').split(/[,;\n]/).map(s => s.trim()).filter(Boolean).forEach(l => languages.add(l.toLowerCase())));
    return {rows: rows.length, by_type: by, gaps, checks, blocks, languages: Array.from(languages).sort(),
      instrument_language_products: rows.reduce((n, r) => n + String(r.languages || '').split(/[,;\n]/).map(s => s.trim()).filter(Boolean).length, 0)};
  }

  const csvCell = v => {
    let s = v === null || v === undefined ? '' : String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  const COLUMNS = ['concept', 'role', 'instrument', 'version', 'type', 'respondent', 'mode', 'recall', 'languages', 'licence', 'training'];
  function toCSV(rows) {
    const lines = [COLUMNS.concat(['findings']).map(csvCell).join(',')];
    rows.forEach(r => lines.push(COLUMNS.map(c => csvCell(r[c])).concat(csvCell(checkRow(r).map(x => x.level + ': ' + x.msg).join(' | '))).join(',')));
    return lines.join('\n') + '\n';
  }

  function validateWorkspace(w) {
    const errs = [];
    if (!w || typeof w !== 'object' || Array.isArray(w)) return ['Not a workspace file.'];
    if (w.schema !== SCHEMA) errs.push('Unexpected schema.');
    if (!Array.isArray(w.rows)) errs.push('rows must be a list.');
    else if (w.rows.length > 500) errs.push('Too many rows (limit 500).');
    else w.rows.forEach((r, i) => {
      if (!r || typeof r !== 'object' || Array.isArray(r)) errs.push('Row ' + (i + 1) + ' is not an object.');
      else COLUMNS.forEach(c => { if (own(r, c) && typeof r[c] !== 'string') errs.push('Row ' + (i + 1) + ': ' + c + ' must be text.'); });
    });
    return errs;
  }

  const api = {VERSION, SCHEMA, TYPES, TYPE_KEYS, REPORTERS, MODES, ROLES, LICENCE, COLUMNS, IMPLICATIONS, DEFAULT_RESPONDENT,
    classify, emptyRow, checkRow, summarise, toCSV, csvCell, validateWorkspace};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsCoaFinder = api;
})(typeof globalThis === 'object' ? globalThis : this);
