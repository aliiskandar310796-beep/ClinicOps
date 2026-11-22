/* ClinicOps licence and translation lead-time planner: page behaviour. Everything stays in this browser tab.
   No network call and no browser storage; work is kept only in the file the user exports. */
(function () {
  'use strict';
  const L = window.ClinicOpsLeadTime;
  const $ = id => document.getElementById(id);
  let products = [];
  let durations = {};
  let lastResult = null;

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
  const wk = n => (Math.round(n * 10) / 10) + ' wk';

  const COLS = [
    {key: 'instrument', label: 'Instrument', ph: 'e.g. Pain rating scale'},
    {key: 'language', label: 'Language', ph: 'e.g. Danish'},
    {key: 'licence_weeks', label: 'Licence: weeks left', ph: 'default', num: true},
    {key: 'translation_weeks', label: 'Translation: weeks left', ph: 'default', num: true},
    {key: 'screenshot_rounds', label: 'Screenshot rounds left', ph: 'default', num: true},
    {key: 'signoff_weeks', label: 'Sign-off: weeks left', ph: 'default', num: true}
  ];

  function renderRows() {
    const body = $('rows');
    body.replaceChildren();
    products.forEach((p, i) => {
      body.append(h('tr', null, COLS.map(c => {
        const el = h('input', {type: 'text', autocomplete: 'off', 'aria-label': c.label + ', row ' + (i + 1), placeholder: c.ph});
        if (c.num) el.setAttribute('inputmode', 'decimal');
        el.value = p[c.key] || '';
        el.addEventListener('input', () => { p[c.key] = el.value; recompute(); });
        return h('td', null, el);
      }), h('td', null, h('button', {type: 'button', class: 'btn secondary-btn', 'aria-label': 'Remove row ' + (i + 1), onclick: () => { products.splice(i, 1); renderRows(); recompute(); }}, 'Remove'))));
    });
    $('rows-wrap').hidden = products.length === 0;
    $('rows-empty').hidden = products.length > 0;
  }

  function renderDurations() {
    const box = $('durations');
    box.replaceChildren();
    Object.keys(L.DEFAULTS).forEach(k => {
      const d = L.DEFAULTS[k];
      const cur = durations[k] || d.weeks;
      const mk = (idx, name) => {
        const el = h('input', {type: 'text', inputmode: 'decimal', 'aria-label': d.label + ', ' + name, value: String(cur[idx])});
        el.addEventListener('input', () => {
          const vals = [0, 1, 2].map(j => Number(document.querySelector('[data-dur="' + k + j + '"]').value));
          if (vals.every(v => isFinite(v) && v >= 0) && vals[0] <= vals[1] && vals[1] <= vals[2]) durations[k] = vals; else delete durations[k];
          recompute();
        });
        el.setAttribute('data-dur', k + idx);
        return h('td', null, el);
      };
      box.append(h('tr', null, h('th', {scope: 'row'}, d.label), mk(0, 'optimistic'), mk(1, 'likely'), mk(2, 'pessimistic'), h('td', {class: 'small muted'}, d.note)));
    });
  }

  function recompute() {
    const out = $('out');
    out.replaceChildren();
    lastResult = null;
    const r = L.plan({kickoff: $('kickoff').value, target: $('target').value, durations, products});
    if (r.errors.length) { out.append(h('p', {class: 'muted'}, r.errors.join(' '))); return; }
    lastResult = r;
    const rows = L.SCENARIOS.map(s => {
      const x = r.scenarios[s];
      const cls = x.status === 'late' ? 'st-hold' : x.status === 'on time' ? 'st-ok' : 'st-na';
      return h('tr', null,
        h('th', {scope: 'row'}, s),
        h('td', null, x.date), h('td', null, wk(x.weeks)), h('td', null, x.set_by),
        h('td', null, x.slack_weeks === null ? '—' : (x.slack_weeks >= 0 ? x.slack_weeks + ' wk before target' : Math.abs(x.slack_weeks) + ' wk after target')),
        h('td', null, h('span', {class: 'st ' + cls}, x.status)));
    });
    out.append(
      h('h3', null, 'Earliest first-participant-in date'),
      h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': 'Scenario dates, scrollable table'},
        h('table', null, h('thead', null, h('tr', null, ['Scenario', 'Ready date', 'From kick-off', 'Set by', 'Against target', 'Status'].map(t => h('th', {scope: 'col'}, t)))), h('tbody', null, rows))),
      h('p', {class: 'small muted'}, 'Calendar weeks. National holidays and the Danish summer and winter breaks are not modelled. Ready means language versions signed off and testing finished; go-live, site activation and device logistics are not included.'),
      h('h3', null, 'By instrument and language (expected case)'),
      h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': 'Per-product weeks, scrollable table'},
        h('table', null, h('thead', null, h('tr', null, ['Instrument', 'Language', 'Licence', 'Translation', 'Screenshots', 'Sign-off', 'Total', 'Driver'].map(t => h('th', {scope: 'col'}, t)))),
          h('tbody', null, r.products.map(p => h('tr', null,
            h('td', null, p.instrument || '—', p.critical ? h('span', {class: 'st st-warn', style: 'margin-left:.6em'}, 'critical') : null), h('td', null, p.language || '—'),
            h('td', null, wk(p.licence)), h('td', null, wk(p.translation)), h('td', null, wk(p.screenshots) .replace(' wk', ' rounds')), h('td', null, wk(p.signoff)), h('td', null, wk(p.total)), h('td', null, p.driver)))))));
    if (r.sensitivity.length) {
      out.append(h('h3', null, 'If one version left the first wave'),
        h('p', {class: 'small muted'}, 'Expected-case ready date without each row. A row that saves nothing is not on the critical path.'),
        h('ul', {class: 'plain'}, r.sensitivity.map(s => h('li', null, h('strong', null, (s.instrument || 'Row') + ' · ' + (s.language || '—') + ': '), s.weeks_saved > 0 ? 'saves ' + wk(s.weeks_saved) + ' (ready ' + s.date + ')' : 'no change'))));
    }
  }

  const EXAMPLE = {
    kickoff: '2027-02-01', target: '2027-06-01',
    products: [
      {instrument: 'Pain rating scale (example)', language: 'English', licence_weeks: '0', translation_weeks: '0', screenshot_rounds: '1', signoff_weeks: ''},
      {instrument: 'Pain rating scale (example)', language: 'Danish', licence_weeks: '', translation_weeks: '', screenshot_rounds: '', signoff_weeks: ''},
      {instrument: 'Pain rating scale (example)', language: 'Swedish', licence_weeks: '', translation_weeks: '', screenshot_rounds: '', signoff_weeks: ''},
      {instrument: 'Symptom diary (example)', language: 'Danish', licence_weeks: '2', translation_weeks: '14', screenshot_rounds: '', signoff_weeks: ''},
      {instrument: 'Symptom diary (example)', language: 'Finnish', licence_weeks: '2', translation_weeks: '', screenshot_rounds: '', signoff_weeks: ''}
    ]
  };

  ['kickoff', 'target'].forEach(id => $(id).addEventListener('input', recompute));
  $('add').addEventListener('click', () => { if (products.length >= 300) { say('Limit of 300 rows reached.'); return; } products.push({}); renderRows(); });
  $('load-example').addEventListener('click', () => {
    $('kickoff').value = EXAMPLE.kickoff; $('target').value = EXAMPLE.target;
    products = EXAMPLE.products.map(p => Object.assign({}, p)); durations = {};
    renderRows(); renderDurations(); recompute();
    say('Fictional example loaded. The instruments are placeholders; the blank cells use the published ranges below.');
  });
  $('reset-durations').addEventListener('click', () => { durations = {}; renderDurations(); recompute(); say('Durations reset to the published ranges.'); });
  $('clear').addEventListener('click', () => { products = []; durations = {}; $('kickoff').value = ''; $('target').value = ''; renderRows(); renderDurations(); recompute(); say('Cleared.'); });
  $('export-csv').addEventListener('click', () => {
    if (!lastResult) { say('Enter a kick-off date and at least one row first.'); return; }
    download('lead-time-plan.csv', L.toCSV(lastResult), 'text/csv'); say('CSV downloaded.');
  });
  $('export-scenarios').addEventListener('click', () => {
    if (!lastResult) { say('Enter a kick-off date and at least one row first.'); return; }
    download('lead-time-scenarios.csv', L.toScenariosCSV(lastResult), 'text/csv'); say('Scenario CSV downloaded.');
  });
  $('export-ics').addEventListener('click', () => {
    if (!lastResult) { say('Enter a kick-off date and at least one row first.'); return; }
    download('lead-time-plan.ics', L.toICS(lastResult, new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z'), 'text/calendar'); say('Calendar file downloaded. Dates are all-day events.');
  });
  $('export-share').addEventListener('click', async () => {
    if (!lastResult) { say('Enter a kick-off date and at least one row first.'); return; }
    const text = L.shareSummary(lastResult);
    try { await navigator.clipboard.writeText(text); say('Share-safe summary copied: counts and weeks only, no names or dates. Paste it into a question or a scope brief. Nothing has been sent.'); }
    catch (err) { say('Copy was blocked by the browser. Select and copy this instead: ' + text.replace(/\n/g, ' ')); }
  });
  $('export-json').addEventListener('click', () => {
    download('lead-time-plan.json', JSON.stringify({schema: L.SCHEMA, kickoff: $('kickoff').value, target: $('target').value, durations, products}, null, 2), 'application/json'); say('Workspace file downloaded.');
  });
  $('import').addEventListener('change', async e => {
    const file = e.target.files[0]; e.target.value = '';
    if (!file) return;
    if (file.size > 1000000) { say('That file is too large for a workspace file.'); return; }
    try {
      const data = JSON.parse(await file.text());
      const errs = L.validateWorkspace(data);
      if (errs.length) { say('Not imported: ' + errs[0]); return; }
      products = data.products.map(p => Object.assign({}, p));
      durations = data.durations && typeof data.durations === 'object' && !Array.isArray(data.durations) ? data.durations : {};
      $('kickoff').value = typeof data.kickoff === 'string' ? data.kickoff : ''; $('target').value = typeof data.target === 'string' ? data.target : '';
      renderRows(); renderDurations(); recompute(); say('Imported ' + products.length + ' row' + (products.length === 1 ? '' : 's') + '.');
    } catch (err) { say('Not imported: the file is not valid JSON.'); }
  });

  /* Work lives only in this tab: warn before it is lost, until it has been exported or cleared. */
  let dirty = false;
  const markDirty = () => { dirty = products.length > 0; };
  document.addEventListener('input', markDirty);
  ['export-json', 'clear'].forEach(id => $(id).addEventListener('click', () => { dirty = false; }));
  window.addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });

  renderRows(); renderDurations(); recompute();
})();
