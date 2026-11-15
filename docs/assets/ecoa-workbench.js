/* ClinicOps eCOA delivery workbench: page behaviour. Everything stays in this
   browser tab. No network call, no browser storage: the only way work is
   kept is the workspace file the user exports. */
(function () {
  'use strict';
  const C = window.ClinicOpsEcoaCore;
  const D = window.ClinicOpsEcoaData;
  let W = C.emptyWorkspace();
  let dirty = false;
  const components = [];
  let screensComponent = null;
  const $ = id => document.getElementById(id);

  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    if (attrs) for (const k of Object.keys(attrs)) {
      const v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat()) {
      if (kid === null || kid === undefined) continue;
      el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }
  const today = () => {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  };
  const say = msg => { $('status').textContent = msg; };
  const touch = () => { dirty = true; };
  function download(name, content, type) {
    const blob = new Blob([content], {type});
    const a = h('a', {href: URL.createObjectURL(blob), download: name});
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  const slug = s => String(s || 'study').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'study';
  const button = (label, onclick, cls) => h('button', {type: 'button', class: 'btn ' + (cls || 'secondary-btn'), onclick}, label);
  const STATUS_CLASS = {
    ready: 'st-ok', aligned: 'st-ok', 'within tolerance': 'st-ok', closed: 'st-ok', 'closed with evidence': 'st-ok', low: 'st-ok',
    blocked: 'st-hold', exception: 'st-hold', high: 'st-hold', 'below tolerance': 'st-hold', 'mismatch signal': 'st-hold', 'conflicting evidence': 'st-hold',
    'requires qualified review': 'st-warn', unresolved: 'st-warn', 'tolerance threatened': 'st-warn', medium: 'st-warn', 'missing evidence': 'st-warn',
    'in progress': 'st-na', 'not started': 'st-na', 'no data': 'st-na', 'no tolerance set': 'st-na', 'not rated': 'st-na', open: 'st-na', 'not applicable': 'st-na', 'no expected entries': 'st-na'
  };

  /* ---------- generic editable register ---------- */
  function control(col, row, label, onchange) {
    let el;
    if (col.type === 'select') {
      el = h('select', {'aria-label': label});
      const options = col.options.includes(row[col.key] || '') || !row[col.key] ? col.options : col.options.concat([row[col.key]]);
      if (!col.required) el.append(h('option', {value: ''}, '—'));
      for (const o of options) el.append(h('option', {value: o}, o));
      el.value = row[col.key] || (col.required ? col.options[0] : '');
      if (col.required && !row[col.key]) row[col.key] = col.options[0];
    } else if (col.type === 'area') {
      el = h('textarea', {'aria-label': label, rows: '2'});
      el.value = row[col.key] || '';
    } else {
      el = h('input', {'aria-label': label, type: col.type === 'date' ? 'date' : 'text', autocomplete: 'off'});
      if (col.type === 'number') el.setAttribute('inputmode', 'decimal');
      el.value = row[col.key] || '';
    }
    el.addEventListener('input', () => { row[col.key] = el.value; touch(); });
    el.addEventListener('change', () => { row[col.key] = el.value; touch(); onchange(el); });
    return el;
  }
  function register(mountId, key, columns, opts) {
    const mount = $(mountId);
    const derived = columns.filter(c => c.type === 'derived');
    function refresh() {
      mount.querySelectorAll('tr[data-i]').forEach(tr => {
        const row = W[key][Number(tr.dataset.i)];
        for (const col of derived) {
          const cell = tr.querySelector('[data-derived="' + col.key + '"]');
          const r = col.compute(row);
          cell.replaceChildren(h('span', {class: 'st ' + (STATUS_CLASS[r.text] || 'st-na')}, r.text), r.note ? h('span', {class: 'note'}, r.note) : null);
        }
      });
      if (opts.summary) opts.summary();
    }
    function render() {
      const rows = W[key];
      const head = h('tr', null, columns.map(c => h('th', {scope: 'col'}, c.label)), opts.fixed ? null : h('th', {scope: 'col'}, h('span', {class: 'vh'}, 'Remove')));
      const body = h('tbody', null, rows.map((row, i) => h('tr', {'data-i': String(i)},
        columns.map(col => h('td', {'data-label': col.label},
          col.type === 'derived' ? h('div', {'data-derived': col.key}) :
          col.type === 'static' ? h('span', null, row[col.key] || '') :
          control(col, row, col.label + ', row ' + (i + 1), el => { if (opts.onChange) opts.onChange(row, col, el); refresh(); }))),
        opts.fixed ? null : h('td', {'data-label': 'Remove'}, h('button', {type: 'button', class: 'btn secondary-btn small-btn', 'aria-label': 'Remove row ' + (i + 1),
          onclick: () => { W[key].splice(i, 1); touch(); render(); }}, 'Remove')))));
      const table = h('table', {class: 'reg', style: 'min-width:' + (opts.width || 900) + 'px'}, h('caption', {class: 'vh'}, opts.label), h('thead', null, head), body);
      const csvColumns = columns.map(c => ({key: c.key, label: c.label}));
      const actions = h('div', {class: 'tool-actions'},
        opts.fixed ? null : button('Add row', () => { W[key].push(Object.assign({}, opts.blank ? opts.blank() : {})); touch(); render(); }),
        button('Download CSV', () => {
          const out = W[key].map(row => { const r = Object.assign({}, row); for (const col of derived) { const d = col.compute(row); r[col.key] = d.text + (d.note ? ' — ' + d.note : ''); } return r; });
          download('ecoa-' + key + '-' + slug(W.study.name) + '.csv', '﻿' + C.toCSV(out, csvColumns), 'text/csv');
          say(opts.label + ' downloaded. Nothing left your browser.');
        }),
        (opts.buttons || []).map(b => button(b[0], b[1])));
      mount.replaceChildren(
        rows.length ? h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': opts.label + ', scrollable table'}, table)
          : h('p', {class: 'muted small'}, opts.empty || 'No rows yet.'),
        actions);
      refresh();
    }
    const api = {render, refresh};
    components.push(api);
    return api;
  }

  /* ---------- generic checklist ---------- */
  function sourceLinks(item) {
    const out = [h('span', {class: 'badge neutral'}, D.BASIS[item.basis])];
    for (const ref of item.src) {
      const [id, section] = ref.split('#');
      const label = (D.SOURCES[id] ? D.SOURCES[id].short : id) + (section ? ', ' + section : '');
      out.push(h('a', {href: '#src-' + id}, label));
    }
    return out;
  }
  function checklist(mountId, listId, keyFn) {
    const mount = $(mountId);
    const def = D.CHECKLISTS[listId];
    const items = def.groups.flatMap(g => g.items);
    const stateKey = () => (keyFn ? keyFn() : listId);
    const summaryEl = h('p', {class: 'status gate-line'});
    function summarise() {
      const s = C.checklistSummary(items, W.checklists[stateKey()]);
      summaryEl.textContent = s.confirmed + ' of ' + s.total + ' confirmed · ' + s.open + ' open' + (s.na ? ' · ' + s.na + ' not applicable' : '') +
        (s.na_without_reason ? ' (' + s.na_without_reason + ' without a reason, counted as open)' : '') + (s.complete ? ' · complete' : '');
      refreshGates();
    }
    function render() {
      const key = stateKey();
      const state = () => { W.checklists[key] = W.checklists[key] || {}; return W.checklists[key]; };
      const blocks = def.groups.map(g => h('div', null, def.groups.length > 1 ? h('h4', null, g.title) : null, g.items.map(item => {
        const cur = (W.checklists[key] || {})[item.id] || {state: 'open', note: ''};
        const sel = h('select', {'aria-label': 'State: ' + item.label}, ['open', 'confirmed', 'not applicable'].map(o => h('option', {value: o}, o)));
        sel.value = cur.state;
        const note = h('input', {type: 'text', 'aria-label': 'Note or evidence reference: ' + item.label, placeholder: 'Evidence reference or reason', autocomplete: 'off'});
        note.value = cur.note || '';
        const save = () => { state()[item.id] = {state: sel.value, note: note.value}; touch(); summarise(); };
        sel.addEventListener('change', save); note.addEventListener('change', save);
        return h('div', {class: 'chk'}, h('div', null, h('strong', null, item.label), h('p', null, item.why), h('p', {class: 'basis'}, sourceLinks(item))), h('div', {class: 'chk-ctl'}, sel, note));
      })));
      const actions = h('div', {class: 'tool-actions'}, button('Download checklist (.txt)', () => {
        const st = W.checklists[key] || {};
        let out = def.title.toUpperCase() + (keyFn ? ' — ' + key.split(':')[1] : '') + '\nStudy: ' + (W.study.name || '[study]') + ' · Date: ' + today() + ' · PRINCE2 process: ' + def.stage + '\n';
        for (const g of def.groups) { out += '\n' + g.title + '\n'; for (const it of g.items) { const c = st[it.id] || {state: 'open', note: ''}; out += '  [' + (c.state === 'confirmed' ? 'x' : c.state === 'not applicable' ? '-' : ' ') + '] ' + it.label + (c.note ? '\n      Note: ' + c.note : '') + '\n'; } }
        out += '\n' + summaryEl.textContent + '\nThis checklist structures recorded information. It is not a compliance determination.\n';
        download('ecoa-' + listId + '-' + slug(W.study.name) + '.txt', out, 'text/plain');
        say(def.title + ' downloaded. Nothing left your browser.');
      }));
      mount.replaceChildren(summaryEl, ...blocks, actions);
      summarise();
    }
    const api = {render, refresh: summarise};
    components.push(api);
    if (listId === 'screens') screensComponent = api;
    return api;
  }

  /* ---------- simple bound fields ---------- */
  function fields(mountId, defs, target, area) {
    const mount = $(mountId);
    const api = {render() {
      mount.replaceChildren(...defs.map(([key, label, hint]) => {
        const id = mountId + '-' + key;
        const el = area ? h('textarea', {id, rows: '2', placeholder: hint}) : h('input', {id, type: 'text', placeholder: hint, autocomplete: 'off'});
        el.value = target()[key] || '';
        el.addEventListener('input', () => { target()[key] = el.value; touch(); });
        return h('div', {class: 'field'}, h('label', {for: id}, label), el);
      }));
    }, refresh() {}};
    components.push(api);
    return api;
  }

  /* ---------- gates overview ---------- */
  function gateRows() {
    const rows = [];
    for (const listId of Object.keys(D.CHECKLISTS)) {
      const def = D.CHECKLISTS[listId];
      const items = def.groups.flatMap(g => g.items);
      const keys = def.perLanguage ? Object.keys(W.checklists).filter(k => k.startsWith(listId + ':')) : [listId];
      for (const key of (keys.length ? keys : [listId + ':—'])) {
        rows.push({listId, label: def.title + (def.perLanguage ? ' — ' + key.split(':')[1] : ''), process: def.stage, summary: C.checklistSummary(items, W.checklists[key])});
      }
    }
    return rows;
  }
  function refreshGates() {
    const rows = gateRows();
    const mount = $('gates');
    if (mount) mount.replaceChildren(h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': 'Checklist and gate overview, scrollable table'},
      h('table', null, h('thead', null, h('tr', null, ['Checklist', 'PRINCE2 process', 'Confirmed', 'Open', 'State'].map(t => h('th', {scope: 'col'}, t)))),
        h('tbody', null, rows.map(r => h('tr', null, h('td', null, r.label), h('td', null, r.process), h('td', {class: 'num'}, r.summary.confirmed + ' / ' + r.summary.total), h('td', {class: 'num'}, String(r.summary.open + r.summary.na_without_reason)),
          h('td', null, h('span', {class: 'st ' + (r.summary.complete ? 'st-ok' : 'st-na')}, r.summary.complete ? 'complete' : 'open'))))))));
    const stage = D.STAGES.find(s => s.id === W.study.stage) || D.STAGES[0];
    const hint = $('stage-hint');
    if (stage.gate) {
      const gate = rows.filter(r => r.listId === stage.gate);
      hint.textContent = 'PRINCE2 process: ' + stage.process + '. Gate for this stage: ' + gate.map(g => g.label + ' (' + g.summary.confirmed + ' of ' + g.summary.total + ' confirmed)').join('; ') + '.';
    } else hint.textContent = 'PRINCE2 process: ' + stage.process + '.';
  }

  /* ---------- summaries ---------- */
  function cards(mountId, list) {
    $(mountId).replaceChildren(...list.map(([label, value]) => h('div', {class: 'sum-card'}, h('strong', null, String(value)), h('span', {class: 'muted small'}, label))));
  }
  function planSummary() {
    const p = C.planSummary(W.products, today());
    cards('plan-sum', [['Products', p.total], ['Ready', p.by_status.ready], ['Blocked', p.by_status.blocked],
      ['To review or resolve', p.by_status['requires qualified review'] + p.by_status.unresolved], ['Past due', p.late]]);
    const waiting = C.STEPS.filter(s => p.waiting_at[s]).map(s => C.STEP_LABELS[s] + ': ' + p.waiting_at[s]);
    $('plan-wait').textContent = p.total ? (waiting.length ? 'Next step waiting — ' + waiting.join(' · ') + '.' : 'No product is waiting on a step.') : '';
  }
  function defectSummary() {
    const d = C.defectSummary(W.defects);
    cards('defect-sum', [['Open critical', d.open.critical], ['Open major', d.open.major], ['Open minor', d.open.minor], ['Closed', d.closed]]);
    $('defect-exit').textContent = !d.total ? '' : d.exit_blocked
      ? 'Testing exit is held: ' + (d.open.critical ? d.open.critical + ' critical finding(s) open' : '') + (d.open.critical && d.unbanded ? '; ' : '') + (d.unbanded ? d.unbanded + ' finding(s) without a severity band' : '') + '. The exit decision stays with the sponsor.'
      : 'No open critical finding. The exit decision stays with the sponsor.';
  }
  function riskSummary() {
    const open = W.risks.filter(r => r.state !== 'closed');
    const ex = b => open.filter(r => C.exposure(r.probability, r.impact) === b).length;
    cards('risk-sum', [['Open risks', open.length], ['High exposure', ex('high')], ['Medium', ex('medium')], ['Without an owner', open.filter(r => !String(r.owner || '').trim()).length]]);
  }
  function kpiSummary() {
    const st = W.kpis.map(C.kpiStatus);
    const n = s => st.filter(x => x === s).length;
    cards('kpi-sum', [['Exceptions', n('exception')], ['Threatened', n('tolerance threatened')], ['Within tolerance', n('within tolerance')], ['No data or tolerance', n('no data') + n('no tolerance set')]]);
  }
  function completionSummary() {
    const rows = W.counts.map(r => ({group: r.group, expected: Number(r.expected) || 0, completed: Number(r.completed) || 0}));
    const c = C.completion(rows, W.completion_minimum);
    $('completion-total').textContent = rows.length ? 'All groups: ' + c.total.completed + ' of ' + c.total.expected + ' expected entries completed' + (c.total.rate === null ? '' : ' (' + c.total.rate + '%)') + '. Groups below tolerance: ' + c.below + '.' : '';
  }
  function countRow(row) {
    const e = Number(row.expected), c = Number(row.completed);
    if (!Number.isFinite(e) || !Number.isFinite(c) || String(row.expected).trim() === '' || String(row.completed).trim() === '') return {text: 'no data'};
    if (c > e || e < 0 || c < 0) return {text: 'unresolved', note: 'Completed exceeds expected, or a count is negative.'};
    const r = C.completion([{group: row.group, expected: e, completed: c}], W.completion_minimum).rows[0];
    return {text: r.flag, note: r.rate === null ? '' : r.rate + '%'};
  }

  /* ---------- components ---------- */
  const R = {};
  function build() {
    fields('study-fields', [['name', 'Study name or code', 'e.g. ABC-123'], ['reference', 'Sponsor or internal reference', 'Optional']], () => W.study, false);
    fields('bc-fields', D.BUSINESS_CASE, () => W.business_case, true);
    fields('tol-fields', D.TOLERANCES, () => W.tolerances, false);
    checklist('cl-brief', 'brief');

    R.org = register('reg-org', 'organisation', [
      {key: 'role', label: 'PRINCE2 role', type: 'select', options: D.ROLES.map(r => r[0]), required: true},
      {key: 'name', label: 'Name', type: 'text'}, {key: 'organisation', label: 'Organisation', type: 'text'},
      {key: 'reports', label: 'Receives (report, frequency)', type: 'text'}], {label: 'Organisation and communication register', width: 760});
    checklist('cl-initiation', 'initiation');

    const stepCol = s => ({key: s, label: C.STEP_LABELS[s], type: 'select', options: C.STEP_STATES, required: true});
    R.products = register('reg-products', 'products', [
      {key: 'instrument', label: 'Instrument', type: 'text'}, {key: 'version', label: 'Version', type: 'text'},
      {key: 'holder', label: 'Copyright holder', type: 'text'}, {key: 'language', label: 'Language (country)', type: 'text'}]
      .concat(C.STEPS.map(stepCol)).concat([
        {key: 'na_reason', label: 'Reason if not applicable', type: 'text'}, {key: 'owner', label: 'Owner', type: 'text'},
        {key: 'due', label: 'Due', type: 'date'},
        {key: 'status', label: 'Status', type: 'derived', compute: row => { const r = C.productStatus(row, today());
          return {text: r.status, note: [r.next_step && r.status !== 'requires qualified review' ? 'Next: ' + C.STEP_LABELS[r.next_step] : '', r.messages.join(' '), r.late ? 'Past due by ' + Math.abs(r.days_to_due) + ' day(s).' : ''].filter(Boolean).join(' ')}; }},
        {key: 'notes', label: 'Notes', type: 'area'}]),
      {label: 'Instrument-language plan', width: 1900, summary: planSummary, empty: 'No products yet. Add one row per instrument and language, or load the fictional example.'});
    R.schedule = register('reg-schedule', 'schedule', [
      {key: 'instrument', label: 'Instrument', type: 'static'}, {key: 'timepoint', label: 'Timepoint', type: 'static'},
      {key: 'protocol_window', label: 'Protocol window', type: 'static'}, {key: 'specification_window', label: 'Specification window', type: 'static'},
      {key: 'state', label: 'Status', type: 'derived', compute: row => ({text: row.status || 'unresolved', note: row.detail})},
      {key: 'owner', label: 'Owner', type: 'text'}, {key: 'resolution', label: 'Resolution and evidence', type: 'text'}],
      {label: 'Schedule reconciliation', width: 1100, fixed: true, empty: 'No comparison run yet.'});
    checklist('cl-freeze', 'freeze');

    checklist('cl-screens', 'screens', () => 'screens:' + $('screen-lang').value);
    checklist('cl-uat', 'uat');
    R.scripts = register('reg-scripts', 'uat_scripts', [
      {key: 'id', label: 'Script', type: 'static'}, {key: 'area', label: 'Area', type: 'static'}, {key: 'objective', label: 'Objective', type: 'static'},
      {key: 'instrument', label: 'Instrument', type: 'static'}, {key: 'timepoint', label: 'Timepoint', type: 'static'},
      {key: 'device', label: 'Device', type: 'static'}, {key: 'language', label: 'Language', type: 'static'},
      {key: 'requirement_ref', label: 'Specification reference', type: 'text'}, {key: 'expected_result', label: 'Expected result (write before running)', type: 'area'},
      {key: 'result', label: 'Result', type: 'select', options: ['not run', 'pass', 'fail', 'blocked'], required: true},
      {key: 'tester', label: 'Tester', type: 'text'}, {key: 'evidence', label: 'Evidence reference', type: 'text'}],
      {label: 'Testing script skeleton', width: 1900, fixed: true, empty: 'No scripts generated yet.'});
    R.defects = register('reg-defects', 'defects', [
      {key: 'id', label: 'Finding', type: 'text'}, {key: 'script', label: 'Script', type: 'text'}, {key: 'description', label: 'Description', type: 'area'},
      {key: 'band', label: 'Severity band', type: 'select', options: C.DEFECT_BANDS}, {key: 'state', label: 'State', type: 'select', options: ['open', 'fixed, awaiting re-test', 'closed'], required: true},
      {key: 'retest', label: 'Re-test evidence', type: 'text'}],
      {label: 'Testing findings log', width: 1000, summary: defectSummary, blank: () => ({id: 'F-' + String(W.defects.length + 1).padStart(3, '0'), state: 'open'})});
    checklist('cl-training', 'training');

    R.risks = register('reg-risks', 'risks', [
      {key: 'id', label: 'ID', type: 'text'}, {key: 'title', label: 'Risk', type: 'area'},
      {key: 'probability', label: 'Probability', type: 'select', options: C.BANDS}, {key: 'impact', label: 'Impact', type: 'select', options: C.BANDS},
      {key: 'exposure', label: 'Exposure', type: 'derived', compute: row => ({text: C.exposure(row.probability, row.impact)})},
      {key: 'owner', label: 'Owner', type: 'text'}, {key: 'response', label: 'Response', type: 'area'},
      {key: 'state', label: 'State', type: 'select', options: ['open', 'closed'], required: true}],
      {label: 'Risk register', width: 1200, summary: riskSummary, blank: () => ({state: 'open'}),
        buttons: [['Add the seeded risks', () => {
          const have = new Set(W.risks.map(r => r.id));
          const add = D.RISKS.filter(r => !have.has(r.id)).map(r => ({id: r.id, title: r.title, probability: '', impact: '', owner: '', response: r.response, state: 'open'}));
          W.risks.push(...add); touch(); R.risks.render(); say(add.length + ' seeded risk(s) added. Rate each one for this study; none is pre-rated.');
        }]]});

    R.issues = register('reg-issues', 'issues', [
      {key: 'id', label: 'ID', type: 'text'}, {key: 'type', label: 'Type', type: 'select', options: D.ISSUE_TYPES, required: true},
      {key: 'title', label: 'Issue, assumption or decision', type: 'area'}, {key: 'raised', label: 'Raised', type: 'date'},
      {key: 'owner', label: 'Owner', type: 'text'}, {key: 'state', label: 'State', type: 'select', options: ['open', 'closed'], required: true},
      {key: 'decision', label: 'Decision and who made it', type: 'area'}],
      {label: 'Issue register', width: 1100, blank: () => ({id: 'I-' + String(W.issues.length + 1).padStart(3, '0'), state: 'open', raised: today()})});
    R.surfaces = register('reg-surfaces', 'surfaces', [
      {key: 'change_ref', label: 'Change', type: 'static'}, {key: 'label', label: 'Surface the change should reach', type: 'static'},
      {key: 'why', label: 'Why', type: 'static'},
      {key: 'machine', label: 'Status', type: 'derived', compute: row => ({text: row.review_state === 'closed with evidence' ? 'closed with evidence' : row.review_state === 'not applicable' ? 'not applicable' : 'missing evidence'})},
      {key: 'owner', label: 'Owner', type: 'text'}, {key: 'evidence', label: 'Closure evidence', type: 'text'},
      {key: 'review_state', label: 'Review state', type: 'select', options: ['open', 'closed with evidence', 'not applicable'], required: true},
      {key: 'reason', label: 'Reason if not applicable', type: 'text'}],
      {label: 'Change surface queue', width: 1500, empty: 'No change mapped yet.',
        onChange: (row, col, el) => {
          if (col.key !== 'review_state') return;
          try { C.closeSurface(row, {}); } catch (err) { row.review_state = 'open'; el.value = 'open'; say('Not changed: ' + err.message + '.'); }
        }});
    R.changes = register('reg-changes', 'changes', [
      {key: 'id', label: 'Request', type: 'text'}, {key: 'site', label: 'Site', type: 'text'}, {key: 'requested', label: 'Requested', type: 'date'},
      {key: 'what', label: 'What and why', type: 'area'}, {key: 'authorised_by', label: 'Authorised by (investigator)', type: 'text'},
      {key: 'state', label: 'State', type: 'select', options: ['open', 'closed'], required: true}, {key: 'evidence', label: 'Audit-trail reference', type: 'text'},
      {key: 'check', label: 'Check', type: 'derived', compute: row => row.state !== 'closed' ? {text: 'open'}
        : (String(row.authorised_by || '').trim() ? {text: 'closed'} : {text: 'requires qualified review', note: 'Closed without a recorded investigator authorisation.'})}],
      {label: 'Data change request log', width: 1200, blank: () => ({id: 'DCR-' + String(W.changes.length + 1).padStart(3, '0'), state: 'open', requested: today()})});

    R.kpis = register('reg-kpis', 'kpis', [
      {key: 'name', label: 'Measure', type: 'text'}, {key: 'unit', label: 'Unit', type: 'text'},
      {key: 'direction', label: 'Limit type', type: 'select', options: ['max', 'min'], required: true},
      {key: 'target', label: 'Target', type: 'number'}, {key: 'tolerance', label: 'Tolerance limit', type: 'number'}, {key: 'actual', label: 'Actual', type: 'number'},
      {key: 'status', label: 'Status', type: 'derived', compute: row => ({text: C.kpiStatus(row)})}],
      {label: 'Tolerances and measures', width: 1000, summary: kpiSummary, blank: () => ({direction: 'max'}),
        buttons: [['Add the standard measures', () => {
          const have = new Set(W.kpis.map(k => k.name));
          const add = D.KPIS.filter(k => !have.has(k.name)).map(k => Object.assign({target: '', tolerance: '', actual: ''}, k));
          W.kpis.push(...add); touch(); R.kpis.render(); say(add.length + ' measure(s) added. Targets and limits are yours to set with the board; none is pre-filled.');
        }]]});
    R.counts = register('reg-counts', 'counts', [
      {key: 'group', label: 'Group (site, language, device type)', type: 'text'}, {key: 'expected', label: 'Expected entries', type: 'number'},
      {key: 'completed', label: 'Completed entries', type: 'number'}, {key: 'rate', label: 'Completion', type: 'derived', compute: countRow}],
      {label: 'Completion monitor', width: 760, summary: completionSummary});
    checklist('cl-golive', 'golive');
    checklist('cl-handover', 'handover');
    checklist('cl-closeout', 'closeout');
    R.lessons = register('reg-lessons', 'lessons', [
      {key: 'date', label: 'Date', type: 'date'}, {key: 'stage', label: 'Stage', type: 'select', options: D.STAGES.map(s => s.label)},
      {key: 'what', label: 'What happened', type: 'area'}, {key: 'effect', label: 'Effect (days, rounds, findings)', type: 'area'}, {key: 'next_time', label: 'What to do next time', type: 'area'}],
      {label: 'Lessons log', width: 1100, blank: () => ({date: today()})});
  }

  function renderAll() {
    $('stage').value = D.STAGES.some(s => s.id === W.study.stage) ? W.study.stage : D.STAGES[0].id;
    $('fpi').value = W.study.first_participant || '';
    $('completion-min').value = W.completion_minimum || '';
    for (const c of components) c.render();
    refreshGates();
    $('report').textContent = 'No report built yet.';
  }

  /* ---------- tabs ---------- */
  function tabs() {
    const list = Array.from(document.querySelectorAll('[role="tab"]'));
    const select = (tab, focus) => {
      for (const t of list) {
        const on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        $(t.getAttribute('aria-controls')).hidden = !on;
      }
      if (focus) tab.focus();
    };
    list.forEach((tab, i) => {
      tab.addEventListener('click', () => select(tab, false));
      tab.addEventListener('keydown', e => {
        const move = {ArrowRight: 1, ArrowLeft: -1}[e.key];
        if (move) { e.preventDefault(); select(list[(i + move + list.length) % list.length], true); }
        else if (e.key === 'Home') { e.preventDefault(); select(list[0], true); }
        else if (e.key === 'End') { e.preventDefault(); select(list[list.length - 1], true); }
      });
    });
    select(list[0], false);
  }

  /* ---------- wiring ---------- */
  function wire() {
    for (const s of D.STAGES) $('stage').append(h('option', {value: s.id}, s.label));
    $('stage').addEventListener('change', () => { W.study.stage = $('stage').value; touch(); refreshGates(); });
    $('fpi').addEventListener('change', () => { W.study.first_participant = $('fpi').value; touch(); });
    $('completion-min').addEventListener('change', () => { W.completion_minimum = $('completion-min').value; touch(); R.counts.refresh(); });

    $('load-example').addEventListener('click', () => { W = C.validateWorkspace(JSON.parse(JSON.stringify(D.EXAMPLE))); dirty = false; renderAll(); say('Fictional example loaded. Every name in it is invented for demonstration.'); });
    $('clear').addEventListener('click', () => { W = C.emptyWorkspace(); dirty = false; renderAll(); say('Workspace cleared.'); });
    $('export').addEventListener('click', () => {
      const out = Object.assign({}, W, {tool_version: C.VERSION, exported_on: today()});
      download('ecoa-workspace-' + slug(W.study.name) + '.json', JSON.stringify(out, null, 2) + '\n', 'application/json');
      dirty = false; say('Workspace file downloaded. Keep it where your study records belong; this page stores nothing.');
    });
    $('import').addEventListener('change', () => {
      const file = $('import').files[0];
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) { say('Not imported: the file is larger than 5 MB.'); $('import').value = ''; return; }
      const reader = new FileReader();
      reader.onload = () => {
        try { W = C.validateWorkspace(JSON.parse(String(reader.result))); dirty = false; renderAll(); say('Workspace imported from ' + file.name + '. Nothing was uploaded.'); }
        catch (err) { say('Not imported: ' + err.message + '.'); }
        $('import').value = '';
      };
      reader.onerror = () => say('Not imported: the file could not be read.');
      reader.readAsText(file);
    });

    $('screen-lang').addEventListener('change', () => screensComponent.render());

    $('reconcile').addEventListener('click', () => {
      const a = C.parseSchedule($('sched-protocol').value), b = C.parseSchedule($('sched-spec').value);
      const errors = a.errors.map(e => 'Protocol ' + e).concat(b.errors.map(e => 'Specification ' + e));
      if (errors.length) { say('Not compared: ' + errors.slice(0, 3).join('; ') + (errors.length > 3 ? '; and ' + (errors.length - 3) + ' more' : '') + '.'); return; }
      if (!a.rows.length) { say('Not compared: paste the protocol schedule first.'); return; }
      const r = C.reconcileSchedule(a.rows, b.rows);
      W.schedule = r.findings.map(f => Object.assign({owner: '', resolution: ''}, f)); touch(); R.schedule.render();
      say('Schedule compared: ' + (r.counts.aligned || 0) + ' aligned, ' + (r.total - (r.counts.aligned || 0)) + ' to resolve. The comparison does not decide which side is right.');
    });

    $('uat-from-plan').addEventListener('click', () => {
      const uniq = k => Array.from(new Set(W.products.map(p => String(p[k] || '').trim()).filter(Boolean)));
      $('uat-instruments').value = uniq('instrument').join('\n'); $('uat-languages').value = uniq('language').join('\n');
      say('Instruments and languages copied from the plan.');
    });
    $('uat-generate').addEventListener('click', () => {
      const lines = id => $(id).value.split(/\r?\n/);
      try {
        const r = C.uatScripts({instruments: lines('uat-instruments'), timepoints: lines('uat-timepoints'), devices: lines('uat-devices'), languages: lines('uat-languages')}, D.UAT_AREAS);
        W.uat_scripts = r.rows; touch(); R.scripts.render();
        $('uat-coverage').textContent = r.coverage.scripts + ' draft scripts. Coverage rule: schedule tests for every instrument at every timepoint on the first device; content, navigation, checks and data tests once per instrument; device tests once per device mode; one smoke check per language. Testing every combination would be ' + r.coverage.full_cross_product + ' scripts. Add combinations your risk assessment calls for.';
        say('Script skeleton generated. Expected results are blank on purpose: write them from the signed specification before running.');
      } catch (err) { say('Not generated: ' + err.message + '.'); }
    });

    const types = $('change-types');
    D.CHANGE_RULES.forEach(rule => types.append(h('label', {class: 'check'}, h('input', {type: 'checkbox', value: rule.id}), ' ' + rule.label)));
    $('map-change').addEventListener('click', () => {
      const ids = Array.from(types.querySelectorAll('input:checked')).map(i => i.value);
      const ref = $('change-ref').value.trim();
      if (!ids.length) { say('Not mapped: tick at least one type of change.'); return; }
      if (!ref) { say('Not mapped: give the change a reference, for example the amendment number.'); return; }
      const hits = C.changeImpact(ids, D.CHANGE_RULES, D.SURFACES);
      W.surfaces.push(...hits.map(x => ({change_ref: ref, surface: x.surface, label: x.label, why: x.triggers.map(t => t.why).join(' '), owner: '', evidence: '', review_state: 'open', reason: ''})));
      touch(); R.surfaces.render();
      say(hits.length + ' surface(s) queued for ' + ref + '. Each stays open until it has an owner and closure evidence, or a reason it does not apply.');
    });

    $('paste-counts').addEventListener('click', () => {
      const r = C.parseCounts($('counts-raw').value);
      if (r.errors.length) { say('Not added: ' + r.errors.slice(0, 3).join('; ') + '.'); return; }
      W.counts.push(...r.rows.map(x => ({group: x.group, expected: String(x.expected), completed: String(x.completed)})));
      $('counts-raw').value = ''; touch(); R.counts.render(); say(r.rows.length + ' group(s) added.');
    });

    let report = '';
    $('build-report').addEventListener('click', () => {
      const stage = D.STAGES.find(s => s.id === W.study.stage) || D.STAGES[0];
      report = C.highlightReport(W, {today: today(), stageLabel: stage.label, checklists: gateRows().map(g => ({label: g.label, summary: g.summary}))});
      $('report').textContent = report; $('copy-report').disabled = false; $('dl-report').disabled = false;
      say('Highlight report built. Nothing left your browser.');
    });
    $('copy-report').addEventListener('click', () => navigator.clipboard.writeText(report).then(() => say('Report copied.'), () => say('Copy failed; select the text instead.')));
    $('dl-report').addEventListener('click', () => { download('ecoa-highlight-report-' + slug(W.study.name) + '.txt', report, 'text/plain'); say('Report downloaded.'); });
    $('dl-raid').addEventListener('click', () => {
      const rows = W.risks.map(r => ({kind: 'risk', id: r.id, title: r.title, rating: C.exposure(r.probability, r.impact), owner: r.owner, state: r.state, note: r.response}))
        .concat(W.issues.map(i => ({kind: i.type || 'issue', id: i.id, title: i.title, rating: '', owner: i.owner, state: i.state, note: i.decision})));
      download('ecoa-raid-log-' + slug(W.study.name) + '.csv', '﻿' + C.toCSV(rows, [['kind', 'Kind'], ['id', 'ID'], ['title', 'Title'], ['rating', 'Exposure'], ['owner', 'Owner'], ['state', 'State'], ['note', 'Response or decision']].map(([key, label]) => ({key, label}))), 'text/csv');
      say('Risks, assumptions, issues and decisions downloaded as one log.');
    });

    window.addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
  }

  function start() {
    const roles = $('roles');
    D.ROLES.forEach(([role, what]) => roles.append(h('tr', null, h('th', {scope: 'row'}, role), h('td', null, what))));
    const seeded = $('seeded-risks');
    D.RISKS.forEach(r => seeded.append(h('tr', null, h('th', {scope: 'row'}, r.id), h('td', null, h('strong', null, r.title), h('p', {class: 'small'}, 'Cause: ' + r.cause + ' Effect: ' + r.effect), h('p', {class: 'basis'}, sourceLinks(r))), h('td', null, r.response))));
    const principles = $('principles');
    D.PRINCIPLES.forEach(([p, how]) => principles.append(h('tr', null, h('th', {scope: 'row'}, p), h('td', null, how))));
    document.querySelectorAll('tr[id^="src-"]').forEach(tr => {
      D.SOURCES[tr.id.slice(4)] = {short: tr.getAttribute('data-short') || tr.id.slice(4)};
    });
    wire();
    build();
    tabs();
    renderAll();
  }
  document.addEventListener('DOMContentLoaded', start);
})();
