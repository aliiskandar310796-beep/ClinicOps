/* ClinicOps Change Surface Mapper: optional "language versions and deliverables" dimension 1.0.0 (2026-11-16).
   Pure functions on text the user typed. No network, no storage, no document inference.
   The lists are the user's own: the mapper does not decide which language versions or deliverables a change reaches. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const MAX_LANGUAGES = 30;
  const MAX_LANGUAGE_LENGTH = 40;
  const MAX_NOTE_LENGTH = 400;

  /* Neutral deliverable types. A change "may touch" any of these; none is presumed to be required. */
  const DELIVERABLES = [
    {id: 'label', label: 'Label or artwork'},
    {id: 'ifu', label: 'Instructions for use, including electronic'},
    {id: 'patient-card', label: 'Patient or implant card'},
    {id: 'field-notice', label: 'Field safety notice or customer letter'},
    {id: 'participant-material', label: 'Participant-facing material (information, screens, diaries)'},
    {id: 'training', label: 'Training or site material'},
    {id: 'registry', label: 'Registry or public data entry'},
    {id: 'web', label: 'Website or digital content'},
    {id: 'other', label: 'Other (describe in the note)'}
  ];
  const BY_ID = Object.fromEntries(DELIVERABLES.map(d => [d.id, d]));

  const BOUNDARY = 'Language versions and deliverables are as entered by the user. The mapper does not decide which language versions or deliverables a change reaches or whether any must change.';

  /* "da-DK, sv-SE; nb-NO" or one per line -> unique, trimmed, capped list. Case-insensitive de-duplication keeps the first spelling. */
  function parseLanguages(text) {
    const seen = new Set();
    const list = [];
    let truncated = false;
    String(text == null ? '' : text).split(/[,;\n\r]+/).forEach(raw => {
      let item = raw.replace(/\s+/g, ' ').trim();
      if (!item) return;
      if (item.length > MAX_LANGUAGE_LENGTH) { item = item.slice(0, MAX_LANGUAGE_LENGTH).trim(); truncated = true; }
      const key = item.toLowerCase();
      if (seen.has(key)) return;
      if (list.length >= MAX_LANGUAGES) { truncated = true; return; }
      seen.add(key);
      list.push(item);
    });
    return {list, truncated};
  }

  /* Known deliverable ids only, in catalogue order, no duplicates. */
  function normaliseDeliverables(ids) {
    const wanted = new Set(Array.isArray(ids) ? ids.map(String) : []);
    return DELIVERABLES.filter(d => wanted.has(d.id));
  }

  /* Returns null when the user entered nothing, so an unused dimension leaves the brief unchanged. */
  function languageDimension(input) {
    const src = input || {};
    const langs = parseLanguages(src.languages);
    const deliverables = normaliseDeliverables(src.deliverables);
    const note = String(src.note == null ? '' : src.note).trim().slice(0, MAX_NOTE_LENGTH);
    if (!langs.list.length && !deliverables.length && !note) return null;
    const both = langs.list.length > 0 && deliverables.length > 0;
    return {
      languages: langs.list,
      languages_truncated: langs.truncated,
      deliverables: deliverables.map(d => ({id: d.id, label: d.label})),
      combinations_to_confirm: both ? langs.list.length * deliverables.length : null,
      note,
      basis: BOUNDARY
    };
  }

  /* Lines appended to the plain-text brief. Empty when there is no dimension. */
  function summaryLines(dim) {
    if (!dim) return [];
    const lines = ['', 'Language versions and deliverables (as entered, optional):'];
    lines.push('- Language versions: ' + (dim.languages.length ? dim.languages.join(', ') : 'none listed'));
    lines.push('- Deliverables that may be touched: ' + (dim.deliverables.length ? dim.deliverables.map(d => d.label).join('; ') : 'none ticked'));
    if (dim.combinations_to_confirm !== null) {
      lines.push('- Combinations to confirm: ' + dim.languages.length + ' language versions x ' + dim.deliverables.length + ' deliverables = ' + dim.combinations_to_confirm + ' (each needs an owner and a decision)');
    } else {
      lines.push('- Combinations to confirm: list at least one language version and tick at least one deliverable to see them');
    }
    if (dim.languages_truncated) lines.push('- Note: the language list was shortened to the first ' + MAX_LANGUAGES + ' entries or ' + MAX_LANGUAGE_LENGTH + ' characters each.');
    if (dim.note) lines.push('- Note: ' + dim.note);
    return lines;
  }

  /* Returns a new packet; the original is not modified. The field is absent when unused. */
  function attach(packet, dim) {
    if (!dim) return packet;
    return Object.assign({}, packet, {language_versions: dim});
  }

  const api = {VERSION, MAX_LANGUAGES, MAX_LANGUAGE_LENGTH, MAX_NOTE_LENGTH, DELIVERABLES, BOUNDARY,
    parseLanguages, normaliseDeliverables, languageDimension, summaryLines, attach, byId: id => BY_ID[id] || null};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ChangeSurfaceCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
