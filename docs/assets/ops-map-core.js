/* ClinicOps clinical operations workflow map, core 1.0.0. Pure logic: no DOM, network or storage.
   Filter state in the URL hash, and the browser-local "my study" trace with JSON and CSV export and JSON import.
   A planning aid, not advice. The trace is the user's own note, not a regulatory or compliance status. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const TRACE_SCHEMA = 'clinicops-ops-map-trace/1';
  const BOUNDARY = 'Planning aid, not advice. The statuses and notes in this file are your own working trace; they are not a regulatory, legal or quality status.';
  const OVERLAYS = ['both', 'drug', 'device'];
  const TRACE_STATUSES = [
    {id: 'open', label: 'Open'},
    {id: 'settled', label: 'Settled'},
    {id: 'na', label: 'Not applicable'}
  ];
  const NOTE_MAX = 300;
  const LABEL_MAX = 60;
  const IMPORT_MAX_BYTES = 200000;

  const statusIds = new Set(TRACE_STATUSES.map((s) => s.id));
  const statusLabel = Object.fromEntries(TRACE_STATUSES.map((s) => [s.id, s.label]));

  function sanitiseText(value, max) {
    let s = typeof value === 'string' ? value : '';
    // eslint-disable-next-line no-control-regex
    s = s.replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, ' ').replace(/\s+/g, ' ').trim();
    return s.length > max ? s.slice(0, max).trim() : s;
  }
  const sanitiseNote = (v) => sanitiseText(v, NOTE_MAX);
  const sanitiseLabel = (v) => sanitiseText(v, LABEL_MAX);

  function defaultState() { return {overlay: 'both', lane: 'all', step: ''}; }

  function laneIds(data) { return new Set(data.lanes.map((l) => l.id)); }
  function stepSlugs(data) { return new Set(data.steps.map((s) => s.slug)); }

  /* Reads '#overlay=device&lane=safety&step=susar-reporting'. Also accepts the plain anchors
     '#step-<slug>', so every card keeps a stable shareable link. Unknown values are dropped. */
  function parseHash(hash, data) {
    const state = defaultState();
    let h = typeof hash === 'string' ? hash : '';
    if (h.charAt(0) === '#') h = h.slice(1);
    if (!h) return state;
    if (h.indexOf('=') === -1) {
      if (h.indexOf('step-') === 0 && stepSlugs(data).has(h.slice(5))) state.step = h.slice(5);
      return state;
    }
    const lanes = laneIds(data), slugs = stepSlugs(data);
    h.split('&').forEach((pair) => {
      const i = pair.indexOf('=');
      if (i < 1) return;
      let key, value;
      try { key = decodeURIComponent(pair.slice(0, i)); value = decodeURIComponent(pair.slice(i + 1)); } catch (e) { return; }
      if (key === 'overlay' && OVERLAYS.indexOf(value) !== -1) state.overlay = value;
      else if (key === 'lane' && lanes.has(value)) state.lane = value;
      else if (key === 'step' && slugs.has(value)) state.step = value;
    });
    return state;
  }

  function buildHash(state) {
    const parts = [];
    if (state.overlay && state.overlay !== 'both') parts.push('overlay=' + encodeURIComponent(state.overlay));
    if (state.lane && state.lane !== 'all') parts.push('lane=' + encodeURIComponent(state.lane));
    if (state.step) parts.push('step=' + encodeURIComponent(state.step));
    return parts.length ? '#' + parts.join('&') : '';
  }

  function stepVisible(step, state) {
    if (state.overlay === 'drug' && step.overlay === 'device') return false;
    if (state.overlay === 'device' && step.overlay === 'drug') return false;
    if (state.lane && state.lane !== 'all' && step.lanes.indexOf(state.lane) === -1) return false;
    return true;
  }

  /* Whether a fact or note tagged with an overlay shows under the chosen regime. */
  function overlayVisible(itemOverlay, overlay) {
    if (overlay === 'both' || itemOverlay === 'both') return true;
    return itemOverlay === overlay;
  }

  function visibleSteps(data, state) { return data.steps.filter((s) => stepVisible(s, state)); }

  /* If a linked step is hidden by the filters, relax the filters rather than show nothing. */
  function normaliseState(state, data) {
    const next = {overlay: state.overlay, lane: state.lane, step: state.step};
    if (next.step) {
      const step = data.steps.find((s) => s.slug === next.step);
      if (!step) next.step = '';
      else if (!stepVisible(step, next)) {
        if (!stepVisible(step, {overlay: next.overlay, lane: 'all'})) next.overlay = 'both';
        next.lane = 'all';
      }
    }
    return next;
  }

  /* ---- trace ---- */

  function emptyTrace() { return Object.create(null); }

  function setTrace(trace, slug, patch) {
    const cur = trace[slug] || {status: '', note: ''};
    const status = patch.status !== undefined ? (statusIds.has(patch.status) ? patch.status : '') : cur.status;
    const note = patch.note !== undefined ? sanitiseNote(patch.note) : cur.note;
    if (!status && !note) delete trace[slug];
    else trace[slug] = {status, note};
    return trace;
  }

  function phaseTitle(data, id) { const p = data.phases.find((x) => x.id === id); return p ? p.title : id; }
  function laneTitle(data, id) { const l = data.lanes.find((x) => x.id === id); return l ? l.title : id; }

  function toJSON(model, data, nowIso) {
    const entries = [];
    data.steps.forEach((s) => {
      const t = model.trace[s.slug];
      if (t && (t.status || t.note)) entries.push({slug: s.slug, status: t.status, note: t.note});
    });
    return JSON.stringify({
      schema: TRACE_SCHEMA,
      tool: 'ClinicOps clinical operations workflow map',
      tool_version: VERSION,
      map_version: data.version,
      decision_boundary: BOUNDARY,
      exported_at: nowIso || '',
      label: sanitiseLabel(model.label),
      overlay: OVERLAYS.indexOf(model.overlay) !== -1 ? model.overlay : 'both',
      trace: entries
    }, null, 2);
  }

  function csvCell(v) {
    let s = String(v == null ? '' : v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function toCSV(model, data) {
    const rows = [[BOUNDARY], ['Slug', 'Step', 'Phase', 'Lanes', 'Regime', 'My status', 'My note']];
    const regime = {both: 'Drug and device', drug: 'Drug trials', device: 'Device investigations'};
    data.steps.forEach((s) => {
      const t = model.trace[s.slug] || {status: '', note: ''};
      rows.push([s.slug, s.title, phaseTitle(data, s.phase), s.lanes.map((l) => laneTitle(data, l)).join('; '),
        regime[s.overlay], t.status ? statusLabel[t.status] : '', t.note]);
    });
    return rows.map((r) => r.map(csvCell).join(',')).join('\r\n') + '\r\n';
  }

  /* Reads an exported trace. Never merges parsed objects into existing ones; unknown steps and
     statuses are dropped and counted. */
  function parseImport(text, data) {
    const fail = (msg) => ({ok: false, error: msg});
    if (typeof text !== 'string' || !text.trim()) return fail('The file is empty.');
    if (text.length > IMPORT_MAX_BYTES) return fail('The file is larger than ' + (IMPORT_MAX_BYTES / 1000) + ' kB, which is more than a trace needs.');
    let doc;
    try { doc = JSON.parse(text); } catch (e) { return fail('The file is not valid JSON.'); }
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return fail('The file is not a trace export.');
    if (doc.schema !== TRACE_SCHEMA) return fail('The file is not a trace export from this page (schema mismatch).');
    if (!Array.isArray(doc.trace)) return fail('The file has no trace list.');
    const slugs = stepSlugs(data);
    const trace = emptyTrace();
    let applied = 0, ignored = 0;
    doc.trace.forEach((entry) => {
      if (!entry || typeof entry !== 'object' || typeof entry.slug !== 'string' || !slugs.has(entry.slug)) { ignored++; return; }
      const status = typeof entry.status === 'string' && statusIds.has(entry.status) ? entry.status : '';
      const note = sanitiseNote(entry.note);
      if (!status && !note) { ignored++; return; }
      trace[entry.slug] = {status, note};
      applied++;
    });
    return {
      ok: true, trace, applied, ignored,
      label: sanitiseLabel(doc.label),
      overlay: OVERLAYS.indexOf(doc.overlay) !== -1 ? doc.overlay : 'both',
      mapVersion: typeof doc.map_version === 'string' ? doc.map_version.slice(0, 20) : ''
    };
  }

  const api = {
    VERSION, TRACE_SCHEMA, BOUNDARY, OVERLAYS, TRACE_STATUSES, NOTE_MAX, LABEL_MAX, IMPORT_MAX_BYTES,
    defaultState, parseHash, buildHash, stepVisible, overlayVisible, visibleSteps, normaliseState,
    emptyTrace, setTrace, toJSON, toCSV, csvCell, parseImport, sanitiseNote, sanitiseLabel
  };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsOpsMapCore = api;
})(typeof globalThis === 'object' ? globalThis : this);
