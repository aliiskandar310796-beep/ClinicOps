/* ClinicOps visit burden estimator: page behaviour. Everything stays in this browser tab.
   No network call and no browser storage; work is kept only in the file the user exports. */
(function () {
  'use strict';
  const B = window.ClinicOpsBurden;
  const $ = id => document.getElementById(id);
  const state = {instruments: [], visits: [], diaries: []};
  let last = null;

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
  const say = m => { $('status').textContent = m; };
  function download(name, content, type) {
    const a = h('a', {href: URL.createObjectURL(new Blob([content], {type})), download: name});
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  const SECTIONS = {
    instruments: {cols: [['name', 'Instrument', 'e.g. Pain rating scale'], ['minutes', 'Minutes to complete', 'your figure'], ['items', 'Items', 'optional']], label: 'instrument'},
    visits: {cols: [['name', 'Visit', 'e.g. Baseline'], ['week', 'Study week', '0'], ['instruments', 'Instruments (separate with ;)', 'e.g. Pain rating scale; Symptom diary']], label: 'visit'},
    diaries: {cols: [['instrument', 'Instrument', 'must match the list'], ['per_week', 'Times per week', '7'], ['from_week', 'First week', '1'], ['to_week', 'Last week', '12']], label: 'diary'}
  };

  function renderSection(key) {
    const sec = SECTIONS[key], body = $('rows-' + key), wrap = $('wrap-' + key);
    body.replaceChildren();
    state[key].forEach((row, i) => {
      body.append(h('tr', null,
        sec.cols.map(c => {
          const el = h('input', {type: 'text', autocomplete: 'off', placeholder: c[2], 'aria-label': c[1] + ', ' + sec.label + ' ' + (i + 1)});
          if (['minutes', 'items', 'week', 'per_week', 'from_week', 'to_week'].includes(c[0])) el.setAttribute('inputmode', 'decimal');
          el.value = row[c[0]] || '';
          el.addEventListener('input', () => { row[c[0]] = el.value; recompute(); });
          return h('td', null, el);
        }),
        h('td', null, h('button', {type: 'button', class: 'btn secondary-btn', 'aria-label': 'Remove ' + sec.label + ' ' + (i + 1), onclick: () => { state[key].splice(i, 1); renderSection(key); recompute(); }}, 'Remove'))));
    });
    wrap.hidden = state[key].length === 0;
    $('empty-' + key).hidden = state[key].length > 0;
  }
  const renderAll = () => Object.keys(SECTIONS).forEach(renderSection);

  function recompute() {
    const out = $('out'); out.replaceChildren(); last = null;
    const input = {instruments: state.instruments, visits: state.visits, diaries: state.diaries,
      caps: {minutes_per_visit: $('cap-visit').value, items_per_visit: $('cap-items').value, minutes_per_week: $('cap-week').value}};
    const r = B.estimate(input);
    if (r.errors.length) { out.append(h('p', {class: 'muted'}, r.errors.join(' '))); return; }
    last = r;
    const t = r.totals;
    out.append(
      h('h3', null, 'Totals'),
      h('p', null, h('strong', null, t.hours + ' hours'), ' (' + t.minutes + ' min) across ' + t.weeks_covered + ' study week' + (t.weeks_covered === 1 ? '' : 's') + ' and ' + t.visits + ' visit' + (t.visits === 1 ? '' : 's') + '.',
        t.peak_visit ? ' Heaviest visit: ' + t.peak_visit + ', ' + t.peak_visit_minutes + ' min.' : '',
        t.peak_week !== null ? ' Heaviest week: week ' + t.peak_week + ', ' + t.peak_week_minutes + ' min.' : ''));
    if (r.flags.length) {
      out.append(h('h3', null, 'Findings'),
        h('ul', {class: 'plain'}, r.flags.map(f => h('li', null, h('span', {class: 'st ' + (f.level === 'over' ? 'st-hold' : f.level === 'gap' ? 'st-warn' : 'st-na'), style: 'margin-right:.6em'}, f.level === 'over' ? 'over limit' : f.level), f.msg))));
    }
    out.append(h('h3', null, 'By visit'),
      h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': 'Minutes by visit, scrollable table'},
        h('table', null, h('thead', null, h('tr', null, ['Visit', 'Week', 'Minutes', 'Items'].map(x => h('th', {scope: 'col'}, x)))),
          h('tbody', null, r.visits.map(v => h('tr', null, h('td', null, v.name), h('td', null, v.week === null ? '—' : v.week), h('td', null, v.minutes), h('td', null, v.items)))))));
    if (r.weeks.length) {
      const max = Math.max.apply(null, r.weeks.map(w => w.minutes)) || 1;
      out.append(h('h3', null, 'By study week'),
        h('div', {class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': 'Minutes by study week, scrollable table'},
          h('table', null, h('thead', null, h('tr', null, ['Week', 'Visit min', 'Diary min', 'Total min', ''].map(x => h('th', {scope: 'col'}, x)))),
            h('tbody', null, r.weeks.map(w => h('tr', null, h('td', null, w.week), h('td', null, w.visit_minutes), h('td', null, w.diary_minutes), h('td', null, w.minutes),
              h('td', {'aria-hidden': 'true'}, h('span', {class: 'bar', style: 'display:inline-block;height:10px;background:var(--accent);border-radius:2px;width:' + Math.max(2, Math.round(w.minutes / max * 160)) + 'px'}))))))));
    }
  }

  const EXAMPLE = {
    instruments: [{name: 'Pain rating scale (example)', minutes: '1', items: '1'}, {name: 'Symptom questionnaire (example)', minutes: '6', items: '20'}, {name: 'Daily diary (example)', minutes: '2', items: '5'}],
    visits: [{name: 'Screening', week: '-2', instruments: 'Pain rating scale (example)'}, {name: 'Baseline', week: '0', instruments: 'Pain rating scale (example); Symptom questionnaire (example)'},
      {name: 'Week 4', week: '4', instruments: 'Pain rating scale (example); Symptom questionnaire (example)'}, {name: 'Week 12', week: '12', instruments: 'Pain rating scale (example); Symptom questionnaire (example)'}],
    diaries: [{instrument: 'Daily diary (example)', per_week: '7', from_week: '-1', to_week: '12'}]
  };

  Object.keys(SECTIONS).forEach(k => $('add-' + k).addEventListener('click', () => { if (state[k].length >= 300) { say('Limit of 300 rows reached.'); return; } state[k].push({}); renderSection(k); }));
  ['cap-visit', 'cap-items', 'cap-week'].forEach(id => $(id).addEventListener('input', recompute));
  $('load-example').addEventListener('click', () => {
    state.instruments = EXAMPLE.instruments.map(x => Object.assign({}, x)); state.visits = EXAMPLE.visits.map(x => Object.assign({}, x)); state.diaries = EXAMPLE.diaries.map(x => Object.assign({}, x));
    ['cap-visit', 'cap-items', 'cap-week'].forEach(id => { $(id).value = ''; });
    renderAll(); recompute(); say('Fictional example loaded. The minutes are made up for the demonstration; use your own.');
  });
  $('clear').addEventListener('click', () => { state.instruments = []; state.visits = []; state.diaries = []; ['cap-visit', 'cap-items', 'cap-week'].forEach(id => { $(id).value = ''; }); renderAll(); recompute(); say('Cleared.'); });
  $('export-csv').addEventListener('click', () => { if (!last) { say('Add at least one instrument first.'); return; } download('visit-burden.csv', B.toCSV(last), 'text/csv'); say('CSV downloaded.'); });
  $('export-json').addEventListener('click', () => {
    download('visit-burden.json', JSON.stringify({schema: B.SCHEMA, caps: {minutes_per_visit: $('cap-visit').value, items_per_visit: $('cap-items').value, minutes_per_week: $('cap-week').value}, instruments: state.instruments, visits: state.visits, diaries: state.diaries}, null, 2), 'application/json'); say('Workspace file downloaded.');
  });
  $('import').addEventListener('change', async e => {
    const file = e.target.files[0]; e.target.value = '';
    if (!file) return;
    if (file.size > 1000000) { say('That file is too large for a workspace file.'); return; }
    try {
      const data = JSON.parse(await file.text());
      const errs = B.validateWorkspace(data);
      if (errs.length) { say('Not imported: ' + errs[0]); return; }
      ['instruments', 'visits', 'diaries'].forEach(k => { state[k] = data[k].map(x => Object.assign({}, x)); });
      const c = data.caps && typeof data.caps === 'object' ? data.caps : {};
      $('cap-visit').value = c.minutes_per_visit || ''; $('cap-items').value = c.items_per_visit || ''; $('cap-week').value = c.minutes_per_week || '';
      renderAll(); recompute(); say('Imported.');
    } catch (err) { say('Not imported: the file is not valid JSON.'); }
  });
  renderAll(); recompute();
})();
