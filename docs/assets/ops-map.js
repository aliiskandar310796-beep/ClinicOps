/* ClinicOps clinical operations workflow map: DOM layer. All logic lives in ops-map-core.js.
   No network, no cookies and nothing is kept between visits. State lives in the URL hash and in the
   file the user exports. */
(() => {
  'use strict';
  const C = window.ClinicOpsOpsMapCore;
  const data = window.ClinicOpsOpsMapData;
  if (!C || !data) return;
  const $ = (id) => document.getElementById(id);
  const cards = Array.prototype.slice.call(document.querySelectorAll('article.step'));
  const bySlug = Object.create(null);
  data.steps.forEach((s) => { bySlug[s.slug] = s; });

  let state = C.normaliseState(C.parseHash(location.hash, data), data);
  let trace = C.emptyTrace();
  let selfWrite = false;

  const statusLine = $('steps-status'), traceStatus = $('trace-status');
  function say(el, msg) { if (el) el.textContent = msg; }

  /* ---------- filters ---------- */
  function pressed(btn, on) { btn.setAttribute('aria-pressed', on ? 'true' : 'false'); }

  function apply() {
    document.querySelectorAll('[data-overlay-btn]').forEach((b) => pressed(b, b.getAttribute('data-overlay-btn') === state.overlay));
    document.querySelectorAll('[data-lane-btn]').forEach((b) => pressed(b, b.getAttribute('data-lane-btn') === state.lane));
    let shown = 0;
    cards.forEach((card) => {
      const step = bySlug[card.getAttribute('data-step')];
      const vis = !!step && C.stepVisible(step, state);
      card.hidden = !vis;
      if (!vis) return;
      shown++;
      card.querySelectorAll('[data-overlay]').forEach((el) => { if (el !== card) el.hidden = !C.overlayVisible(el.getAttribute('data-overlay'), state.overlay); });
    });
    document.querySelectorAll('[data-phase-section]').forEach((sec) => {
      sec.hidden = !sec.querySelector('article.step:not([hidden])');
    });
    $('empty-note').hidden = shown !== 0;
    say(statusLine, 'Showing ' + shown + ' of ' + data.steps.length + ' steps.');
    cards.forEach((card) => card.classList.toggle('is-target', card.getAttribute('data-step') === state.step));
  }

  function writeHash() {
    const h = C.buildHash(state);
    selfWrite = true;
    const url = location.pathname + location.search + h;
    try { history.replaceState(null, '', url); } catch (e) { /* hash only is fine */ }
    selfWrite = false;
  }

  function set(patch, opts) {
    state = C.normaliseState(Object.assign({}, state, patch), data);
    apply();
    writeHash();
    if (opts && opts.scroll && state.step) goToStep(state.step);
  }

  function goToStep(slug) {
    const el = $('step-' + slug);
    if (!el || el.hidden) return;
    el.scrollIntoView({block: 'start'});
    el.setAttribute('tabindex', '-1');
    el.focus({preventScroll: true});
  }

  document.querySelectorAll('[data-overlay-btn]').forEach((b) => b.addEventListener('click', () => set({overlay: b.getAttribute('data-overlay-btn'), step: ''})));
  document.querySelectorAll('[data-lane-btn]').forEach((b) => b.addEventListener('click', () => set({lane: b.getAttribute('data-lane-btn'), step: ''})));

  // Card anchors keep the view and mark the step in the hash.
  document.querySelectorAll('a.step-anchor').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    const slug = a.getAttribute('href').replace('#step-', '');
    set({step: slug}, {scroll: true});
  }));

  window.addEventListener('hashchange', () => {
    if (selfWrite) return;
    const h = location.hash;
    if (/^#phase-/.test(h)) return; // plain phase anchors are handled by the browser
    state = C.normaliseState(C.parseHash(h, data), data);
    apply();
    if (state.step) goToStep(state.step);
  });

  /* ---------- trace ---------- */
  function mountTrace() {
    cards.forEach((card) => {
      const slug = card.getAttribute('data-step');
      const slot = card.querySelector('[data-trace-slot]');
      if (!slot) return;
      const selId = 'trace-status-' + slug, noteId = 'trace-note-' + slug;
      const selLabel = document.createElement('label'); selLabel.setAttribute('for', selId); selLabel.textContent = 'My status';
      const sel = document.createElement('select'); sel.id = selId; sel.setAttribute('data-trace-status', slug);
      [{id: '', label: 'Not set'}].concat(C.TRACE_STATUSES).forEach((o) => {
        const opt = document.createElement('option'); opt.value = o.id; opt.textContent = o.label; sel.appendChild(opt);
      });
      const noteLabel = document.createElement('label'); noteLabel.setAttribute('for', noteId); noteLabel.textContent = 'My note (no participant data)';
      const note = document.createElement('input'); note.id = noteId; note.type = 'text'; note.maxLength = C.NOTE_MAX; note.autocomplete = 'off';
      note.setAttribute('data-trace-note', slug);
      const a = document.createElement('div'); a.appendChild(selLabel); a.appendChild(sel);
      const b = document.createElement('div'); b.appendChild(noteLabel); b.appendChild(note);
      slot.appendChild(a); slot.appendChild(b);
      sel.addEventListener('change', () => { C.setTrace(trace, slug, {status: sel.value}); say(traceStatus, 'Trace updated in this page only. Export it to keep it.'); });
      note.addEventListener('input', () => { C.setTrace(trace, slug, {note: note.value}); });
    });
  }

  function paintTrace() {
    cards.forEach((card) => {
      const slug = card.getAttribute('data-step');
      const t = trace[slug] || {status: '', note: ''};
      const sel = card.querySelector('[data-trace-status]'), note = card.querySelector('[data-trace-note]');
      if (sel) sel.value = t.status;
      if (note) note.value = t.note;
    });
  }

  function download(name, mime, text) {
    const blob = new Blob([text], {type: mime});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const model = () => ({trace, label: $('trace-label').value, overlay: state.overlay});

  $('export-json').addEventListener('click', () => {
    download('ops-map-trace.json', 'application/json', C.toJSON(model(), data, new Date().toISOString()));
    say(traceStatus, 'JSON downloaded to your device. Nothing left your browser.');
  });
  $('export-csv').addEventListener('click', () => {
    download('ops-map-trace.csv', 'text/csv;charset=utf-8', C.toCSV(model(), data));
    say(traceStatus, 'CSV downloaded to your device. Nothing left your browser.');
  });
  $('trace-clear').addEventListener('click', () => {
    trace = C.emptyTrace(); $('trace-label').value = ''; paintTrace();
    say(traceStatus, 'Trace cleared. Nothing is stored between visits.');
  });
  $('import-file').addEventListener('change', () => {
    const input = $('import-file'), file = input.files && input.files[0];
    if (!file) return;
    if (file.size > C.IMPORT_MAX_BYTES) { say(traceStatus, 'That file is larger than a trace needs and was not read.'); input.value = ''; return; }
    file.text().then((text) => {
      const r = C.parseImport(text, data);
      if (!r.ok) { say(traceStatus, 'Not imported. ' + r.error); return; }
      trace = r.trace; $('trace-label').value = r.label; paintTrace();
      set({overlay: r.overlay, step: ''});
      say(traceStatus, 'Imported ' + r.applied + ' step' + (r.applied === 1 ? '' : 's') + (r.ignored ? '; ' + r.ignored + ' entr' + (r.ignored === 1 ? 'y' : 'ies') + ' not recognised and skipped' : '') + '. Nothing left your browser.');
    }).catch(() => say(traceStatus, 'Not imported. The file could not be read.')).finally(() => { input.value = ''; });
  });

  /* ---------- start ---------- */
  mountTrace();
  $('map-controls').hidden = false;
  $('map-tools').hidden = false;
  apply();
  if (state.step) goToStep(state.step);
})();
