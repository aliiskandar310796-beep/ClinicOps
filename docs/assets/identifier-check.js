/* ClinicOps identifier check: structure only. Runs in this tab; nothing is sent anywhere and nothing is stored.
   Rules: SRN shape CC-(MF|AR|IM|PR)-9 digits; B- prefix as a legacy-style signal (ClinicOps derived screening rule); numeric GS1 Mod-10. */
(function () {
  'use strict';
  const roles = {MF: 'Manufacturer', AR: 'Authorised representative', IM: 'Importer', PR: 'System and procedure pack producer'};
  function gs1Valid(v) {
    const d = v.replace(/\D/g, '');
    if (d.length < 2) return null;
    const body = d.slice(0, -1), check = Number(d.slice(-1));
    let total = 0;
    [...body].reverse().forEach((c, i) => { total += Number(c) * (i % 2 === 0 ? 3 : 1); });
    return ((10 - (total % 10)) % 10) === check;
  }
  function assess(raw) {
    const v = String(raw).trim(), upper = v.toUpperCase();
    if (!v) return 'Enter an identifier first.';
    const srn = upper.match(/^([A-Z]{2})-(MF|AR|IM|PR)-(\d{9})$/);
    if (srn) return 'Type: SRN-shaped identifier\nCountry code: ' + srn[1] + '\nRole: ' + srn[2] + ' \u2014 ' + roles[srn[2]] + '\n\nStructural decoding only. This does not verify actor status or device responsibility.';
    if (upper.startsWith('B-')) return 'Type: EUDAMED legacy-style identifier signal\nLegacy screen: yes\n\nClinicOps derived screening rule: the B-prefix is useful for identifying a legacy-style registration path. Do not treat the downstream SS(C)P-link consequence as a directly quoted Commission rule.';
    const compact = v.replace(/[\s-]/g, '');
    if (/^\d+$/.test(compact)) return 'Type: numeric UDI candidate\nGS1 Mod-10 valid: ' + gs1Valid(compact) + '\n\nResolve against EUDAMED before drawing regulatory conclusions.';
    return 'Identifier candidate not recognised by the local structural rules. Resolve against EUDAMED before drawing regulatory conclusions.';
  }
  const input = document.getElementById('idc-value'), btn = document.getElementById('idc-check'), out = document.getElementById('idc-result');
  if (!input || !btn || !out) return;
  btn.addEventListener('click', () => { out.textContent = assess(input.value); });
  input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); btn.click(); } });
})();
