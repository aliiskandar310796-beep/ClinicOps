(() => {
  'use strict';
  const C = window.ClinicOpsCtisClock;
  const $ = (id) => document.getElementById(id);
  const form = $('clock-form'), status = $('status'), result = $('result'), rows = $('rows');
  let last = null;

  function say(msg) { status.textContent = msg; }
  function readHolidays() {
    return $('holidays').value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
  }
  function options() {
    return {
      submission: $('submission').value,
      validationRfi: $('validationRfi').checked, partIRfi: $('partIRfi').checked, partIIRfi: $('partIIRfi').checked,
      atmp: $('atmp').checked, winterStop: $('winterStop').checked, holidays: readHolidays()
    };
  }
  function cell(tag, text) { const el = document.createElement(tag); el.textContent = text; return el; }
  function render(r) {
    rows.textContent = '';
    r.milestones.forEach((m) => {
      const tr = document.createElement('tr');
      tr.appendChild(cell('td', m.date)); tr.appendChild(cell('td', String(m.day)));
      tr.appendChild(cell('td', m.label)); tr.appendChild(cell('td', m.note));
      rows.appendChild(tr);
    });
    const extra = r.totalDays - r.nominalDays;
    $('summary').textContent = 'Decision due ' + r.decisionDate + ', Day ' + r.totalDays + '. The statutory periods alone give ' + r.nominalDays +
      ' days' + (extra > 0 ? '; ' + extra + ' more come from weekends, listed dates and the winter stop.' : '.');
    result.hidden = false;
  }
  function run() {
    const err = $('submission-err');
    err.textContent = '';
    const r = C.plan(options());
    if (!r.ok) {
      err.textContent = r.errors[0];
      $('submission').setAttribute('aria-invalid', 'true');
      result.hidden = true; last = null;
      say(r.errors[0]);
      return;
    }
    $('submission').removeAttribute('aria-invalid');
    last = r; render(r);
    say('Dates ready. Nothing has been sent.');
  }
  function download(name, mime, text) {
    const blob = new Blob([text], {type: mime});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function stamp() { return (last && last.milestones[0].date) || 'dates'; }

  form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
  $('load-example').addEventListener('click', () => {
    $('submission').value = '2027-03-01'; $('study').value = 'Fictional study';
    ['validationRfi', 'partIIRfi', 'atmp'].forEach((id) => { $(id).checked = false; });
    $('partIRfi').checked = true; $('winterStop').checked = true; $('holidays').value = '2027-03-29';
    run();
  });
  $('clear').addEventListener('click', () => {
    form.reset(); result.hidden = true; rows.textContent = ''; last = null; $('submission-err').textContent = '';
    say('Cleared. Nothing is stored between visits.');
  });
  $('export-ics').addEventListener('click', () => {
    if (!last) return;
    download('ctis-clock-' + stamp() + '.ics', 'text/calendar;charset=utf-8', C.toICS(last, $('study').value.trim()));
    say('Calendar file downloaded to your device.');
  });
  $('export-csv').addEventListener('click', () => {
    if (!last) return;
    download('ctis-clock-' + stamp() + '.csv', 'text/csv;charset=utf-8', C.toCSV(last));
    say('CSV downloaded to your device.');
  });
  $('export-json').addEventListener('click', () => {
    if (!last) return;
    download('ctis-clock-' + stamp() + '.json', 'application/json', JSON.stringify({schema: C.SCHEMA, options: options(), result: last}, null, 2));
    say('JSON downloaded to your device.');
  });
})();
