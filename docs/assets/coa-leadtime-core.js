/* ClinicOps licence and translation lead-time planner rules 1.0.0. No network, storage or document inference.
   Date arithmetic on user-entered dates and durations. The default durations are published planning ranges from
   vendors, language-service providers and one small survey; they are not benchmarks and every one can be changed. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const SCHEMA = 'clinicops-leadtime/1';

  /* weeks: [optimistic, likely, pessimistic] */
  const DEFAULTS = {
    licence: {label: 'Electronic-use licence', weeks: [2, 4, 6],
      note: 'Published ranges: 2 to 4 weeks before kick-off (one eCOA provider), up to 6 weeks (a licensing distributor), up to 4 weeks for 9 of 12 developers surveyed. One sponsor reported 12 weeks.'},
    translation: {label: 'Translation and linguistic validation, per language', weeks: [8, 12, 16],
      note: 'Published ranges: 8 to 16 weeks (a language provider). Done at the same time as the build, a survey found it added about 2 weeks to 8 to 10 weeks.'},
    screenshots: {label: 'Screenshot review rounds', weeks: [1, 2, 3],
      note: 'Rounds, not weeks. A survey reported an average of 2 review rounds (range 1 to 3); one distributor reported that 32% of projects needed 3 or more. Each round is taken as 1 week here (ClinicOps assumption).'},
    signoff: {label: 'Copyright-holder sign-off after screenshots', weeks: [1, 1, 2],
      note: 'ClinicOps assumption. No published figure was found.'},
    build: {label: 'Study build, kick-off to UAT-ready', weeks: [6, 8, 12],
      note: 'Published ranges: 6 to 8 weeks for design and build (one provider); 12 to 16 weeks from kick-off to go-live (another); a standard 12-week deployment (a third). Those include testing, so this is set lower.'},
    uat: {label: 'User acceptance testing cycle', weeks: [2, 3, 4],
      note: 'Consortium recommendation: allow at least a 2-week cycle, with more than one round possible.'},
    submission: {label: 'Ethics or regulatory submission of participant materials', weeks: [0, 0, 0],
      note: 'No default. Enter your own estimate; it runs alongside the work above and can set the date.'}
  };
  const SCENARIOS = ['optimistic', 'expected', 'pessimistic'];

  const num = v => (v === '' || v === null || v === undefined) ? null : Number(v);
  const isNum = v => typeof v === 'number' && isFinite(v) && v >= 0;
  const pert = w => (w[0] + 4 * w[1] + w[2]) / 6;
  /* Scenario value of a three-point estimate. */
  function pick(w, scenario) { return scenario === 'optimistic' ? w[0] : scenario === 'pessimistic' ? w[2] : pert(w); }

  function isoDate(s) {
    if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    const d = new Date(s + 'T00:00:00Z');
    return isNaN(d) || d.toISOString().slice(0, 10) !== s ? null : d;
  }
  function addWeeks(d, weeks) { return new Date(d.getTime() + Math.round(weeks * 7) * 86400000); }
  const fmt = d => d.toISOString().slice(0, 10);
  function weeksBetween(a, b) { return Math.round(((b - a) / 86400000) / 7 * 10) / 10; }

  /* A user value of 0 means "already done". Blank means "use the default". */
  function stepWeeks(override, key, scenario, defaults) {
    const o = num(override);
    if (o !== null) return isNum(o) ? o : 0;
    return pick(defaults[key].weeks, scenario);
  }

  /* Weeks from kick-off until this product has its signed-off, reviewed language version. */
  function productWeeks(p, scenario, defaults) {
    const licence = stepWeeks(p.licence_weeks, 'licence', scenario, defaults);
    const translation = stepWeeks(p.translation_weeks, 'translation', scenario, defaults);
    const shotsOverride = num(p.screenshot_rounds);
    const rounds = shotsOverride !== null ? (isNum(shotsOverride) ? shotsOverride : 0) : pick(defaults.screenshots.weeks, scenario);
    const signoff = stepWeeks(p.signoff_weeks, 'signoff', scenario, defaults);
    const screens = translation + rounds;
    const driver = licence >= screens ? 'licence' : 'translation and screenshot review';
    return {licence, translation, screenshots: rounds, signoff, total: Math.max(licence, screens) + signoff, driver};
  }

  function resolve(defaults, overrides) {
    const out = {};
    Object.keys(defaults).forEach(k => {
      const o = overrides && overrides[k];
      out[k] = {label: defaults[k].label, note: defaults[k].note,
        weeks: Array.isArray(o) && o.length === 3 && o.every(isNum) && o[0] <= o[1] && o[1] <= o[2] ? o : defaults[k].weeks};
    });
    return out;
  }

  /* Ready date for each scenario: the latest of the study build and the slowest product, plus testing; the
     submission runs alongside and can set the date by itself. */
  function plan(input) {
    const res = {errors: [], scenarios: {}, products: [], sensitivity: []};
    const kick = isoDate(input && input.kickoff);
    if (!kick) res.errors.push('Enter the kick-off date.');
    const products = (input && Array.isArray(input.products) ? input.products : []).filter(p => p && (String(p.instrument || '').trim() || String(p.language || '').trim()));
    if (!products.length) res.errors.push('Add at least one instrument and language.');
    if (res.errors.length) return res;
    const defaults = resolve(DEFAULTS, input.durations);
    const target = isoDate(input.target);

    function readyFor(list, scenario) {
      const per = list.map(p => productWeeks(p, scenario, defaults));
      const slowest = per.reduce((m, x, i) => x.total > m.total ? Object.assign({index: i}, x) : m, Object.assign({index: -1}, {total: 0}));
      const build = pick(defaults.build.weeks, scenario);
      const uat = pick(defaults.uat.weeks, scenario);
      const submission = pick(defaults.submission.weeks, scenario);
      const content = Math.max(build, slowest.total);
      const ready = Math.max(content + uat, submission);
      return {per, slowest, build, uat, submission, content, ready, setBy: submission > content + uat ? 'submission' : (slowest.total >= build ? 'language versions' : 'study build')};
    }

    SCENARIOS.forEach(s => {
      const r = readyFor(products, s);
      const date = addWeeks(kick, r.ready);
      res.scenarios[s] = {weeks: Math.round(r.ready * 10) / 10, date: fmt(date), set_by: r.setBy,
        slack_weeks: target ? weeksBetween(date, target) : null, status: target ? (date <= target ? 'on time' : 'late') : 'no target'};
    });
    const exp = readyFor(products, 'expected');
    res.products = products.map((p, i) => Object.assign({instrument: p.instrument || '', language: p.language || ''}, exp.per[i], {critical: i === exp.slowest.index}));
    if (products.length > 1) {
      products.forEach((p, i) => {
        const rest = products.filter((_, j) => j !== i);
        const r = readyFor(rest, 'expected');
        const saved = Math.round((exp.ready - r.ready) * 10) / 10;
        res.sensitivity.push({instrument: p.instrument || '', language: p.language || '', weeks_saved: saved, date: fmt(addWeeks(kick, r.ready))});
      });
      res.sensitivity.sort((a, b) => b.weeks_saved - a.weeks_saved);
    }
    return res;
  }

  const csvCell = v => {
    let s = v === null || v === undefined ? '' : String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  function toCSV(result) {
    const lines = [['instrument', 'language', 'licence_weeks', 'translation_weeks', 'screenshot_rounds', 'signoff_weeks', 'total_weeks_expected', 'driver', 'on_critical_path'].join(',')];
    result.products.forEach(p => lines.push([p.instrument, p.language, p.licence, p.translation, p.screenshots, p.signoff, Math.round(p.total * 10) / 10, p.driver, p.critical ? 'yes' : ''].map(csvCell).join(',')));
    return lines.join('\n') + '\n';
  }

  function validateWorkspace(w) {
    const errs = [];
    if (!w || typeof w !== 'object' || Array.isArray(w)) return ['Not a workspace file.'];
    if (w.schema !== SCHEMA) errs.push('Unexpected schema.');
    if (!Array.isArray(w.products)) errs.push('products must be a list.');
    else if (w.products.length > 300) errs.push('Too many rows (limit 300).');
    else w.products.forEach((p, i) => { if (!p || typeof p !== 'object' || Array.isArray(p)) errs.push('Row ' + (i + 1) + ' is not an object.'); });
    return errs;
  }

  const api = {VERSION, SCHEMA, DEFAULTS, SCENARIOS, pert, pick, isoDate, addWeeks, weeksBetween, productWeeks, resolve, plan, toCSV, csvCell, validateWorkspace};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsLeadTime = api;
})(typeof globalThis === 'object' ? globalThis : this);
