/* ClinicOps reconciliation rules 1.0.0. No network, storage or document inference. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const STATUSES = ['aligned', 'mismatch signal', 'missing evidence', 'conflicting evidence', 'unresolved', 'not applicable', 'requires qualified review'];
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const text = v => typeof v === 'string' && v.trim().length > 0;
  const object = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  function canonical(v) {
    if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
    if (object(v)) return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
    return JSON.stringify(v);
  }
  async function sha256(v) {
    if (!root.crypto?.subtle) throw new Error('SHA-256 is unavailable. Use a secure browser context; no substitute fingerprint will be generated.');
    const bytes = new TextEncoder().encode(canonical(v));
    return Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
  }
  function normalize(v, rule = 'exact') {
    if (!text(v)) return null;
    if (rule === 'trim') return v.trim();
    if (rule === 'relaxed') return v.trim().replace(/\s+/g, ' ').toLowerCase();
    return v;
  }
  function evidenceLabel(e) {
    if (text(e)) return e;
    if (!object(e)) return null;
    return [e.sourceName, e.pageOrSection, e.id].filter(text).join(' · ') || null;
  }
  function validate(input) {
    const fail = m => { throw new Error(m); };
    if (!object(input) || !object(input.source) || !text(input.source.id) || !object(input.source.fields)) fail('Provide source.id and a source.fields object.');
    const fields = Object.keys(input.source.fields);
    if (!fields.length || fields.length > 100) fail('Declare between 1 and 100 approved fields.');
    for (const f of fields) if (!text(f) || !(input.source.fields[f] === null || typeof input.source.fields[f] === 'string')) fail('Approved field values must be text or null.');
    if (!Array.isArray(input.surfaces) || !input.surfaces.length || input.surfaces.length > 1000) fail('Declare between 1 and 1,000 surfaces.');
    const ids = new Set();
    for (const s of input.surfaces) {
      if (!object(s) || !text(s.id) || !text(s.name) || ids.has(s.id)) fail('Every surface needs a unique id and a name.');
      ids.add(s.id);
    }
    if (!Array.isArray(input.observations) || input.observations.length > 20000) fail('Provide an observations array with at most 20,000 entries.');
    if (input.owners != null && (!object(input.owners) || Object.entries(input.owners).some(([k,v]) => !ids.has(k) || typeof v !== 'string'))) fail('Owners must map declared surface IDs to text.');
    if (input.rules != null && (!object(input.rules) || Object.entries(input.rules).some(([k,v]) => !own(input.source.fields,k) || !['exact','trim','relaxed','qualified'].includes(v)))) fail('Rules must map declared fields to exact, trim, relaxed or qualified.');
    const key = (s,f) => JSON.stringify([s,f]);
    const checks = input.scope === undefined ? input.surfaces.flatMap(s => fields.map(field => ({surfaceId:s.id,field}))) : input.scope;
    if (!Array.isArray(checks) || !checks.length || checks.length > 20000) fail('Declare 1–20,000 scope checks; use an explicit scope for a large matrix.');
    const scoped = new Map();
    for (const c of checks) {
      if (!object(c) || !ids.has(c.surfaceId) || !own(input.source.fields,c.field)) fail('Scope contains an unknown surface or field.');
      const k = key(c.surfaceId,c.field);
      if (scoped.has(k)) fail('Duplicate scope check.');
      if (c.applicable !== undefined && typeof c.applicable !== 'boolean') fail('Scope applicable must be true or false.');
      if (c.applicable === false && !text(c.reason)) fail('An explicit not-applicable check needs a reason.');
      scoped.set(k,c);
    }
    for (const o of input.observations) {
      if (!object(o) || !scoped.has(key(o.surfaceId,o.field))) fail('Every observation must reference a declared in-scope surface and field.');
      if (!(o.observed === null || typeof o.observed === 'string')) fail('Observed values must be text or null; numeric identifiers must be quoted.');
      if (own(o,'expected') && !(o.expected === null || typeof o.expected === 'string')) fail('Expected values must be text or null.');
      if (o.evidence != null && !(text(o.evidence) || (object(o.evidence) && text(o.evidence.id) && text(o.evidence.sourceName)))) fail('Evidence needs id and sourceName, or a text reference.');
    }
    return checks;
  }
  async function compare(input) {
    // Snapshot once: later form edits cannot change what this run compared.
    input = JSON.parse(JSON.stringify(input));
    const checks = validate(input), observations = new Map(), surfaces = new Map(input.surfaces.map(s => [s.id,s]));
    for (const o of input.observations) {
      const k = JSON.stringify([o.surfaceId,o.field]);
      if (!observations.has(k)) observations.set(k,[]);
      observations.get(k).push(o);
    }
    const findings = checks.map(c => {
      const evidence = observations.get(JSON.stringify([c.surfaceId,c.field])) || [];
      const expected = input.source.fields[c.field], rule = input.rules?.[c.field] || 'exact';
      const norm = v => normalize(v, rule);
      const distinct = new Set(evidence.map(o => norm(o.observed)).filter(v => v !== null));
      let status, action;
      if (c.applicable === false) { status='not applicable'; action=c.reason; }
      else if (norm(expected) === null) { status='unresolved'; action='Obtain an approved source value before interpreting this check.'; }
      else if (evidence.some(o => own(o,'expected') && norm(o.expected) !== norm(expected))) { status='conflicting evidence'; action='The supplied expected value disagrees with the approved source. Resolve the reference; no override was accepted.'; }
      else if (distinct.size > 1) { status='conflicting evidence'; action='Resolve conflicting observations with the accountable owner.'; }
      else if (!evidence.length || evidence.some(o => norm(o.observed) === null)) { status='missing evidence'; action='Obtain the missing observation and its evidence reference.'; }
      else if (rule === 'qualified') { status='requires qualified review'; action='Qualified review is required for this field; text equality does not establish semantic equivalence.'; }
      else if (norm(evidence[0].observed) !== norm(expected)) { status='mismatch signal'; action='Reconcile against the approved source and record the disposition.'; }
      else if (!evidenceLabel(input.source.evidence) || evidence.some(o => !evidenceLabel(o.evidence))) { status='requires qualified review'; action='Values match, but source or observation provenance is missing. Attach evidence before closing.'; }
      else { status='aligned'; action='none'; }
      return {id:'check-'+encodeURIComponent(JSON.stringify([c.surfaceId,c.field])),surfaceId:c.surfaceId,object:surfaces.get(c.surfaceId).name,field:c.field,sourceValue:expected,expected,observed:evidence.length === 1 ? evidence[0].observed : evidence.length ? evidence.map(o=>o.observed).join(' | ') : null,status,comparison_rule:rule,evidence:evidence.map(o=>evidenceLabel(o.evidence)).filter(Boolean).join(' | ')||null,observations:evidence,source_evidence:input.source.evidence||null,owner:input.owners?.[c.surfaceId]||null,next_action:action,review_state:'open',closure_evidence:null,closed_at:null};
    });
    return {rules_version:VERSION,input_snapshot:input,input_sha256:await sha256(input),findings,scope_policy:input.scope === undefined?'All declared fields on all declared surfaces. Narrow scope explicitly where appropriate.':'Explicit field/surface pairs; omitted pairs were not checked.'};
  }
  function review(row, patch, at = new Date().toISOString()) {
    const next = {...row,...patch};
    if (!['open','in review','closed with evidence'].includes(next.review_state)) throw new Error('Unknown review state.');
    if (next.review_state === 'closed with evidence' && (!text(next.owner) || !text(next.closure_evidence))) throw new Error('Closing requires an accountable owner and a closure evidence reference.');
    next.closed_at = next.review_state === 'closed with evidence' ? (row.closed_at || at) : null;
    return next;
  }
  function csvCell(v) {
    let s = String(v ?? '');
    if (/^[\s\u0000-\u001f]*[=+@-]/.test(s)) s = "'" + s;
    return '"' + s.replaceAll('"','""') + '"';
  }
  async function seal(packet) {
    const copy = JSON.parse(JSON.stringify(packet));
    delete copy.packet_sha256;
    for (const row of copy.findings) review(row, {});
    copy.packet_sha256 = await sha256(copy);
    return copy;
  }
  const api = {VERSION,STATUSES,canonical,sha256,normalize,evidenceLabel,validate,compare,review,csvCell,seal};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsReconciliation = api;
})(typeof globalThis === 'object' ? globalThis : this);
