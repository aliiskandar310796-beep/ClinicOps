/* ClinicOps COA type finder and inventory: page behaviour. Everything stays in this browser tab.
   No network call and no browser storage; work is kept only in the file the user exports. */
(function () {
  'use strict';
  const C = window.ClinicOpsCoaFinder;
  const $ = id => document.getElementById(id);
  let rows = [];
  let current = null;

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
  const say = msg => { $('status').textContent = msg; };
  function download(name, content, type) {
    const a = h('a', {href: URL.createObjectURL(new Blob([content], {type})), download: name});
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  /* ---------- step 1: which type ---------- */
  function readAnswers() {
    const picked = document.querySelector('input[name=reporter]:checked');
    return {
      reporter: picked ? picked.value : '',
      interpreted: $('q-interpreted').value, judgement: $('q-judgement').value,
      scored: $('q-scored').value, child: $('q-child').value
    };
  }
  function showFollowUps(reporter) {
    ['interpreted', 'judgement', 'scored', 'child'].forEach(k => { $('w-' + k).hidden = true; });
    if (reporter === 'participant') { $('w-interpreted').hidden = false; $('w-child').hidden = false; }
    if (reporter === 'observer' || reporter === 'clinician') $('w-judgement').hidden = false;
    if (reporter === 'task') $('w-scored').hidden = false;
  }
  function renderResult() {
    const a = readAnswers();
    showFollowUps(a.reporter);
    const box = $('result');
    box.replaceChildren();
    current = C.classify(a);
    if (!current.type) { box.append(h('p', {class: 'muted'}, 'Choose who provides the information to see the type.')); $('add-from-finder').disabled = true; return; }
    $('add-from-finder').disabled = false;
    const t = C.TYPES[current.type];
    box.append(...[
      h('p', {class: 'result-type'}, h('strong', null, current.type), ' ', t.name.replace(/ \(.*\)/, '')),
      h('p', null, h('strong', null, 'Who reports. '), t.who),
      h('p', null, t.note),
      current.flags.length ? h('div', {class: 'callout'}, h('strong', null, 'Look again. '), current.flags.map(f => h('span', null, f + ' '))) : null,
      h('h3', null, 'What it asks of the delivery team'),
      h('ul', null, C.IMPLICATIONS[current.type].map(x => h('li', null, x)))
    ].filter(Boolean));
  }

  /* ---------- step 2: inventory ---------- */
  const COLS = [
    {key: 'concept', label: 'Concept of interest', type: 'text'},
    {key: 'role', label: 'Role in study', type: 'select', options: C.ROLES},
    {key: 'instrument', label: 'Instrument', type: 'text'},
    {key: 'version', label: 'Version', type: 'text'},
    {key: 'type', label: 'Type', type: 'select', options: C.TYPE_KEYS},
    {key: 'respondent', label: 'Respondent', type: 'select', options: ['participant', 'observer', 'clinician', 'task']},
    {key: 'mode', label: 'Mode', type: 'select', options: C.MODES},
    {key: 'recall', label: 'Recall period', type: 'text'},
    {key: 'languages', label: 'Languages (comma-separated)', type: 'text'},
    {key: 'licence', label: 'Electronic-use licence', type: 'select', options: C.LICENCE, required: true},
    {key: 'training', label: 'Rater / administrator training', type: 'text'}
  ];
  function cell(col, row, idx) {
    let el;
    const label = col.label + ', row ' + (idx + 1);
    if (col.type === 'select') {
      el = h('select', {'aria-label': label});
      if (!col.required) el.append(h('option', {value: ''}, '—'));
      col.options.forEach(o => el.append(h('option', {value: o}, o)));
      el.value = row[col.key] || (col.required ? col.options[0] : '');
    } else {
      el = h('input', {'aria-label': label, type: 'text', autocomplete: 'off'});
      el.value = row[col.key] || '';
    }
    const update = () => { row[col.key] = el.value; renderFindings(); };
    el.addEventListener('input', update); el.addEventListener('change', update);
    return h('td', null, el);
  }
  const LEVEL = {gap: ['missing', 'st-warn'], check: ['check', 'st-warn'], block: ['blocked', 'st-hold']};
  function renderInventory() {
    const body = $('inv-body');
    body.replaceChildren();
    rows.forEach((row, i) => {
      body.append(h('tr', null, COLS.map(c => cell(c, row, i)),
        h('td', null, h('button', {type: 'button', class: 'btn secondary-btn', 'aria-label': 'Remove row ' + (i + 1), onclick: () => { rows.splice(i, 1); renderInventory(); }}, 'Remove'))));
    });
    $('inv-empty').hidden = rows.length > 0;
    $('inv-wrap').hidden = rows.length === 0;
    renderFindings();
  }
  function renderFindings() {
    const s = C.summarise(rows);
    $('summary').textContent = rows.length
      ? rows.length + ' assessment' + (rows.length === 1 ? '' : 's') + ' (PRO ' + s.by_type.PRO + ', ObsRO ' + s.by_type.ObsRO + ', ClinRO ' + s.by_type.ClinRO + ', PerfO ' + s.by_type.PerfO +
        (s.by_type.unset ? ', no type ' + s.by_type.unset : '') + '). ' + s.instrument_language_products + ' instrument-language version' + (s.instrument_language_products === 1 ? '' : 's') +
        ' to license, translate and test across ' + s.languages.length + ' language' + (s.languages.length === 1 ? '' : 's') + '. Open prompts: ' + s.gaps + ' missing, ' + s.checks + ' to check, ' + s.blocks + ' blocked.'
      : '';
    const list = $('findings');
    list.replaceChildren();
    rows.forEach((row, i) => {
      C.checkRow(row).forEach(f => {
        const [word, cls] = LEVEL[f.level];
        list.append(h('li', null, h('span', {class: 'st ' + cls}, word), ' ', h('strong', null, (row.instrument || 'Row ' + (i + 1)) + ': '), f.msg));
      });
    });
    $('findings-wrap').hidden = list.children.length === 0;
  }
  function addRow(over) {
    if (rows.length >= 500) { say('Limit of 500 rows reached.'); return false; }
    rows.push(Object.assign(C.emptyRow(), over || {}));
    renderInventory();
    return true;
  }

  const EXAMPLE = [
    {concept: 'Pain intensity', role: 'primary', instrument: 'Pain rating scale (example)', version: '1.0', type: 'PRO', respondent: 'participant', mode: 'provisioned device', recall: '24 hours', languages: 'English, Danish', licence: 'requested', training: ''},
    {concept: 'Sleep disturbance', role: 'secondary', instrument: 'Caregiver sleep diary (example)', version: '2.1', type: 'ObsRO', respondent: 'observer', mode: 'web link', recall: '', languages: 'English, Danish', licence: 'granted', training: ''},
    {concept: 'Overall disease severity', role: 'key secondary', instrument: 'Clinician global rating (example)', version: '1.0', type: 'ClinRO', respondent: 'clinician', mode: 'site tablet', recall: '', languages: 'English', licence: 'not checked', training: ''},
    {concept: 'Walking capacity', role: 'exploratory', instrument: 'Timed walk test (example)', version: '1.0', type: 'PerfO', respondent: 'task', mode: 'interview, site staff', recall: '', languages: 'English, Danish', licence: 'not required', training: 'Site script and demonstration'}
  ];

  /* ---------- wiring ---------- */
  document.querySelectorAll('input[name=reporter], .follow select').forEach(el => el.addEventListener('change', renderResult));
  $('add-from-finder').addEventListener('click', () => {
    if (!current || !current.type) return;
    addRow({type: current.type, respondent: C.DEFAULT_RESPONDENT[current.type]});
    say('Row added to the inventory below.');
    $('inventory').scrollIntoView({block: 'start'});
  });
  $('add-blank').addEventListener('click', () => { if (addRow()) say('Blank row added.'); });
  $('load-example').addEventListener('click', () => { rows = EXAMPLE.map(r => Object.assign(C.emptyRow(), r)); renderInventory(); say('Fictional example loaded: four assessments, one of each type. The names are placeholders, not real instruments.'); });
  $('clear').addEventListener('click', () => { rows = []; renderInventory(); say('Cleared.'); });
  $('export-csv').addEventListener('click', () => {
    if (!rows.length) { say('Nothing to export yet.'); return; }
    download('coa-inventory.csv', C.toCSV(rows), 'text/csv'); say('CSV downloaded. Findings are in the last column.');
  });
  $('export-json').addEventListener('click', () => {
    download('coa-inventory.json', JSON.stringify({schema: C.SCHEMA, rows}, null, 2), 'application/json'); say('Workspace file downloaded.');
  });
  $('import').addEventListener('change', async e => {
    const file = e.target.files[0]; e.target.value = '';
    if (!file) return;
    if (file.size > 1000000) { say('That file is too large for a workspace file.'); return; }
    try {
      const data = JSON.parse(await file.text());
      const errs = C.validateWorkspace(data);
      if (errs.length) { say('Not imported: ' + errs[0]); return; }
      rows = data.rows.map(r => Object.assign(C.emptyRow(), r));
      renderInventory(); say('Imported ' + rows.length + ' row' + (rows.length === 1 ? '' : 's') + '.');
    } catch (err) { say('Not imported: the file is not valid JSON.'); }
  });

  renderResult();
  renderInventory();
})();
