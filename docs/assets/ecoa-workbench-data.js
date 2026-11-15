/* ClinicOps eCOA delivery workbench content 1.0.0 (2026-11-14).
   Static reference content only: checklists, the seeded risk register, the
   change-surface rule table and the fictional example. Every item names its
   basis. "method" means a ClinicOps working practice, not a rule stated by a
   regulator or a publication. */
(function (root) {
  'use strict';

  const BASIS = {
    regulation: 'Regulation',
    guidance: 'Regulatory guidance',
    consensus: 'Consensus best practice',
    'peer-reviewed': 'Peer-reviewed study',
    framework: 'Project-management framework',
    industry: 'Industry source',
    method: 'ClinicOps method'
  };

  /* Filled from the source register at the foot of the page (SOURCES). */
  const SOURCES = {};

  const STAGES = [
    {id: 'starting-up', label: 'Starting up', process: 'Starting up a project', gate: 'brief'},
    {id: 'initiation', label: 'Initiation', process: 'Initiating a project', gate: 'initiation'},
    {id: 'specification', label: 'Specification and licensing', process: 'Controlling a stage · Managing product delivery', gate: 'freeze'},
    {id: 'build', label: 'Build, translation and screenshots', process: 'Controlling a stage · Managing product delivery', gate: 'screens'},
    {id: 'uat', label: 'User acceptance testing', process: 'Managing product delivery', gate: 'uat'},
    {id: 'go-live', label: 'Go-live decision', process: 'Managing a stage boundary · Directing a project', gate: 'golive'},
    {id: 'maintenance', label: 'Live study and controlled change', process: 'Controlling a stage', gate: 'handover'},
    {id: 'closeout', label: 'Closeout', process: 'Closing a project', gate: 'closeout'}
  ];

  const PRINCIPLES = [
    ['Ensure continued business justification', 'The business case is re-confirmed at every gate, not only at the start.'],
    ['Learn from experience', 'Lessons are logged while the study runs and read before the next one starts.'],
    ['Define roles, responsibilities and relationships', 'Sponsor, provider, translation vendor, sites and assurance each hold a named role.'],
    ['Manage by stages', 'Specification, build, testing, go-live and closeout are separate stages with a decision between them.'],
    ['Manage by exception', 'Each tolerance has a limit; inside it the project manager acts, outside it the board decides.'],
    ['Focus on products', 'The plan is a list of instrument-language versions, each with its own acceptance evidence.'],
    ['Tailor to suit the project', 'A two-instrument single-country study uses fewer rows, not a different method.']
  ];

  const TOLERANCES = [
    ['time', 'Time', 'e.g. go-live no later than 10 working days after the planned date'],
    ['cost', 'Cost', 'e.g. change orders within an agreed share of the eCOA budget'],
    ['scope', 'Scope', 'e.g. no instrument or language removed without a board decision'],
    ['quality', 'Quality', 'e.g. no open critical finding at the testing exit'],
    ['risk', 'Risk', 'e.g. no high-exposure risk without an owner and a response'],
    ['benefits', 'Benefits', 'e.g. completion at the primary timepoint not below the agreed minimum'],
    ['sustainability', 'Sustainability', 'e.g. provisioned devices returned and reused or recycled']
  ];

  const BUSINESS_CASE = [
    ['reasons', 'Reasons', 'Why these outcome assessments are collected electronically in this study, and what the data must support.'],
    ['options', 'Options considered', 'Provisioned devices, participants’ own devices, site tablets, paper back-up; and why this option.'],
    ['benefits', 'Expected benefits (measurable)', 'For example: time-stamped entries at the primary timepoint; analysable data for the planned endpoint.'],
    ['disbenefits', 'Expected dis-benefits', 'For example: participant burden, device logistics, start-up time.'],
    ['timescale', 'Timescale', 'First participant date and the eCOA go-live it depends on.'],
    ['costs', 'Costs and who carries them', 'Provider fees, licences, translations, devices, helpdesk.'],
    ['risks', 'Major risks', 'The three risks that would change the decision to proceed.'],
    ['justification', 'Continued justification (update at each gate)', 'Is the case above still true? Who confirmed it, and when?']
  ];

  const ROLES = [
    ['Executive', 'Sponsor study lead accountable for the business case and the go-live decision.'],
    ['Senior user', 'Those who will use the data and the system: outcomes research, data management, biostatistics, site and participant representation.'],
    ['Senior supplier', 'Those who deliver: the eCOA provider, the translation and linguistic validation vendor, the CRO where it delivers.'],
    ['Project manager', 'Runs the stages day to day inside the tolerances the board has set.'],
    ['Project assurance', 'Independent of the project manager: sponsor quality assurance, independent testing and review.'],
    ['Change authority', 'Authorises changes inside delegated limits; everything beyond goes to the board.'],
    ['Team manager', 'Provider project lead, translation lead, device logistics lead.'],
    ['Project support', 'Keeps the registers, the plan and the document versions.']
  ];

  const item = (id, label, why, basis, src) => ({id, label, why, basis, src: src || []});

  const CHECKLISTS = {
    brief: {
      title: 'Project brief',
      stage: 'Starting up a project',
      groups: [{title: 'Before the provider is briefed', items: [
        item('b01', 'Outcome-assessment schedule extracted from the protocol', 'Instrument, version, who reports (participant, clinician, observer), timepoints and completion windows.', 'method'),
        item('b02', 'Role of each instrument in the analysis recorded', 'Primary, key secondary or exploratory: effort follows what matters most to participant safety and to the reliability of results.', 'guidance', ['ich-e6r3']),
        item('b03', 'Countries and languages listed for every instrument', 'Including the source-language version. Each instrument-language pair becomes one product on the plan.', 'consensus', ['ispor-tca', 'isoqol-etrans']),
        item('b04', 'Electronic-use licence position checked with each copyright holder', 'Asked before the build is specified: whether electronic use is permitted, on what terms, and who reviews the screens.', 'industry', ['cpath-2019']),
        item('b05', 'Existing translations and existing electronic-version evidence identified', 'What already exists decides how much new evidence the migration needs.', 'consensus', ['ispor-2023']),
        item('b06', 'Device approach decided in outline', 'Provisioned devices, participants’ own devices or both, with a route for participants who have no suitable device.', 'guidance', ['ema-cs#A5.1.3', 'eu-dct#5', 'byod-2022']),
        item('b07', 'Executive, senior user and senior supplier named', 'See Organising. A go-live decision needs someone accountable for it.', 'framework', ['prince2']),
        item('b08', 'Outline business case written', 'What the data must support: the planned endpoint, a labelling claim, a health technology assessment dossier (where instrument properties and translations are appraised), safety follow-up.', 'framework', ['prince2', 'htacg-outcomes#5.1–5.3', 'dmc-methods#5']),
        item('b09', 'First participant date and its dependency on go-live stated', 'If go-live slips, which milestone moves and who needs to know.', 'method'),
        item('b10', 'Lessons from earlier studies read', 'The lessons log is an input to the brief, not only an output of closeout.', 'framework', ['prince2'])
      ]}]
    },
    initiation: {
      title: 'Project initiation',
      stage: 'Initiating a project',
      groups: [{title: 'Controls agreed before the build stage is authorised', items: [
        item('i01', 'Data flow documented from the participant’s device to the sponsor database', 'Where the first permanent record sits, every transfer on the way, and who controls each copy.', 'guidance', ['ich-e6r3#Annex 1, 4.2', 'dkma-dct']),
        item('i02', 'Written agreement sets out sponsor, provider and CRO responsibilities for the system', 'Including who holds the data, who can change configuration, and who answers inspectors.', 'guidance', ['ich-e6r3#Annex 1, 3.6']),
        item('i03', 'Provider system assessment on file', 'The sponsor keeps oversight of delegated activities; the provider’s validation evidence is reviewed, not assumed.', 'guidance', ['ich-e6r3#Annex 1, 3.9', 'ema-cs#A2.1']),
        item('i04', 'Quality approach: product descriptions with acceptance criteria', 'For the design specification, each screenshot set, the testing pack, training material and the data transfer.', 'framework', ['prince2']),
        item('i05', 'Risk register baselined', 'Seeded risks reviewed, owners named, responses agreed. See Risk.', 'guidance', ['ich-e6r3']),
        item('i06', 'Change control approach agreed', 'Who assesses a change, who authorises it, and when re-testing is required.', 'consensus', ['cpath-uat']),
        item('i07', 'Data change request process agreed', 'How a correction to participant-entered data is requested, justified, authorised by the investigator and recorded.', 'guidance', ['ema-cs#6.1.4, A5.1.1.4', 'cpath-dcr']),
        item('i08', 'Communication approach agreed', 'Which report goes to whom, how often, and the escalation route when a tolerance is threatened.', 'framework', ['prince2']),
        item('i09', 'Tolerances set by the board', 'For time, cost, scope, quality, risk, benefits and sustainability. See Business case.', 'framework', ['prince2']),
        item('i10', 'Stage plan with decision points', 'Specification sign-off, testing exit, go-live and closeout each end with a recorded decision.', 'framework', ['prince2']),
        item('i11', 'Data protection roles and cross-border transfers assessed', 'By the sponsor’s data protection function; the participant information describes the electronic collection.', 'regulation', ['gdpr']),
        item('i13', 'Digital and decentralised elements described where the country asks for them', 'In Denmark, for example: in the cover letter with the trial-specific risk assessment, in the protocol and in the participant information.', 'guidance', ['dkma-dct#2.6', 'eu-dct']),
        item('i12', 'End-of-study data delivery to sites planned now', 'Format, timing and who confirms receipt. Leaving this to closeout is how sites lose access before they hold a copy.', 'guidance', ['ema-cs#6.6'])
      ]}]
    },
    freeze: {
      title: 'Design freeze readiness',
      stage: 'Managing a stage boundary',
      groups: [{title: 'Before the specification is signed', items: [
        item('f01', 'Every assessment in the protocol schedule has an entry in the design specification', 'Run the schedule reconciliation under Plans and resolve every row that is not aligned.', 'method'),
        item('f02', 'Nothing in the specification lies outside the protocol or the contracted scope', 'Or it is covered by an agreed change order.', 'method'),
        item('f03', 'Protocol version behind the specification recorded', 'Designing from a draft protocol is a risk both parties agree to in writing, with its cost and time consequences.', 'method'),
        item('f04', 'Completion windows, reminders and missed-entry behaviour specified for each instrument', 'Including what a participant sees after a window has closed.', 'method'),
        item('f05', 'Respondent, device mode and languages specified for each instrument', 'One line per instrument-language product on the plan.', 'method'),
        item('f06', 'Source-language screens reviewed by the copyright holder where the licence requires it', 'Before localisation starts: a change to the source after that point repeats every language.', 'method'),
        item('f07', 'Site workflow walked through with a site', 'What staff do in this system and in the other systems they use at the same visit.', 'method'),
        item('f08', 'Participant-facing wording frozen', 'Any later change to on-screen text re-opens screenshots, translations and ethics submissions.', 'method'),
        item('f09', 'Data transfer agreement drafted', 'Format, frequency and method; every transfer needed during the study is named in advance.', 'guidance', ['ema-cs#6.1.2']),
        item('f10', 'Specification signed by both parties; date recorded as the design freeze', 'The signed version is the reference for testing.', 'method'),
        item('f11', 'Changes after the freeze follow change control', 'Impact, cost and time are assessed and authorised before anyone commits to the change.', 'framework', ['prince2'])
      ]}]
    },
    screens: {
      title: 'Screenshot and migration review',
      stage: 'Managing product delivery',
      perLanguage: true,
      groups: [
        {title: 'A. Fidelity to the approved translation', items: [
          item('s01', 'Screen text matches the approved translation item by item', 'Wording, order and emphasis (bold, underline, capitals). Compare against the licensed text, not against the source language.', 'consensus', ['cpath-migration', 'ispor-tca']),
          item('s02', 'Instrument title, version and copyright notice shown as the licence requires', 'The licence terms decide where and how; record the clause.', 'method'),
          item('s03', 'Instructions and recall period visible wherever the paper version relies on them', 'On paper they sit above every item. On a small screen they can scroll out of view.', 'method'),
          item('s04', 'Response options complete, in the same order and direction, with unchanged anchors', 'Including numeric labels and the wording at each end of a scale.', 'consensus', ['cpath-migration']),
          item('s05', 'Layout changes from paper are listed as migration changes', 'For example one item per screen, a scroll list replacing a grid. Each is named so its evidence need can be judged.', 'consensus', ['cpath-migration', 'ispor-2023'])
        ]},
        {title: 'B. Danish, Swedish and Norwegian rendering', items: [
          item('s06', 'National characters render correctly in every font weight and in capitals', 'æ ø å and Æ Ø Å (Danish, Norwegian); å ä ö and Å Ä Ö (Swedish). Check headings, buttons and reminders, not only item text.', 'method'),
          item('s07', 'No truncated or overflowing text at the smallest supported screen and with enlarged system font', 'Long compound words are the usual cause: they do not break where an English phrase would.', 'method'),
          item('s08', 'Line breaks do not separate a negation or a qualifier from what it modifies', 'A line ending in “ikke” or “inte”, or a scale anchor split over two lines, can change how an item is read.', 'method'),
          item('s09', 'Dates, decimals and clock follow the convention agreed for the country', 'For example day-month-year in Denmark and Norway, year-month-day commonly in Sweden; decimal comma; 24-hour clock; week starting Monday.', 'method'),
          item('s10', 'Norwegian written standard confirmed', 'Bokmål or Nynorsk, matching the licensed translation.', 'method'),
          item('s11', 'Form of address consistent with the approved translation throughout', 'The same choice in instrument text and in system text.', 'method'),
          item('s12', 'System text is translated, reviewed and consistent with the instrument’s terminology', 'Buttons, error messages, reminders, log-in and alarm text are read by the participant too, and are rarely part of the licensed translation.', 'method'),
          item('s13', 'No mixed-language screen', 'No source-language fallback strings in menus, pickers, validation messages or notifications.', 'method')
        ]},
        {title: 'C. Behaviour visible on the screens', items: [
          item('s14', 'Skipping, going back and leaving an item unanswered behave as the design specification says', 'And as the instrument allows: a forced answer where the paper version permits a blank is a change.', 'method'),
          item('s15', 'Prompts and checks do not steer the participant toward an answer', 'A check may ask for completion or flag an impossible value; it should not suggest what the value ought to be.', 'method'),
          item('s16', 'Scales drawn to the copyright holder’s electronic specification', 'Length, orientation, anchors and markers of visual analogue and numeric rating scales.', 'method')
        ]},
        {title: 'D. Sign-off', items: [
          item('s17', 'Reviewer is a native speaker with relevant clinical background; name and date recorded', 'The review is a proofreading step of the translation process carried into the electronic version.', 'consensus', ['ispor-tca', 'isoqol-etrans']),
          item('s18', 'Every finding logged with its screenshot reference and closed against a new screenshot', 'A finding is closed by evidence, not by a statement that it was fixed.', 'method'),
          item('s19', 'Copyright-holder review obtained where the licence requires it', 'Record who reviewed, which screenshot set, and when.', 'method'),
          item('s20', 'Final screenshot set version-locked and referenced in testing and in ethics submissions', 'So that the version tested, the version submitted and the version participants see are the same.', 'method')
        ]}
      ]
    },
    uat: {
      title: 'User acceptance testing: plan and exit',
      stage: 'Managing product delivery',
      groups: [{title: 'Plan, execution and exit', items: [
        item('u01', 'Test plan approved', 'Scope, entry and exit criteria, roles, environment, device list, and how findings are graded.', 'consensus', ['cpath-uat']),
        item('u02', 'Testing is run by the sponsor or its designee, not by the provider’s staff', 'A CRO or a testing vendor can be the designee. The sponsor side writes the scripts; tester training is recorded.', 'consensus', ['cpath-uat']),
        item('u03', 'Entry criteria met', 'Provider’s own validation complete; the sponsor-approved requirements document is in the testers’ hands.', 'consensus', ['cpath-uat']),
        item('u04', 'Scripts trace to the approved requirements and expected results are written before execution', 'A script whose expected result is written after the run records what the system did, not what it should do.', 'consensus', ['cpath-uat']),
        item('u05', 'At least two weeks planned, assuming more than one round', 'Findings need a fix and a re-test; a single compressed round passes defects into the live study.', 'consensus', ['cpath-uat']),
        item('u06', 'Approach to schedules and completion windows agreed with the provider', 'How time is advanced in the test environment to exercise late, missed and out-of-window entries.', 'method'),
        item('u07', 'Each supported device type and operating-system version covered', 'Including the minimum specification for participants’ own devices.', 'method'),
        item('u08', 'Data followed end to end', 'Entries made on the device are found unchanged in the site view and in the transfer file.', 'guidance', ['ema-cs#6.1.2']),
        item('u09', 'Findings logged with a severity band; re-tests recorded', 'Kept as a findings log with a summary of issues and resolutions. No open critical finding at exit.', 'consensus', ['cpath-uat']),
        item('u10', 'Summary report signed by the sponsor before release to production', 'With the approval form, and archived with the study records. The acceptance stays with the sponsor.', 'guidance', ['ema-cs#A2.6–A2.7', 'cpath-uat']),
        item('u11', 'Later changes re-enter change control and testing', 'A change after go-live is built and tested outside production, then tested by the sponsor side before release. Nothing is tested in the live system.', 'consensus', ['cpath-uat'])
      ]}]
    },
    golive: {
      title: 'Go-live readiness',
      stage: 'Managing a stage boundary',
      groups: [{title: 'Evidence the board needs to authorise go-live', items: [
        item('g01', 'Current design specification signed', 'Version and date recorded.', 'method'),
        item('g02', 'Every instrument-language product is ready on the plan', 'Or the board has accepted a named exception.', 'framework', ['prince2']),
        item('g03', 'Testing summary report signed; open findings assessed', 'See Quality.', 'consensus', ['cpath-uat']),
        item('g04', 'Ethics and regulatory approvals cover the participant-facing material in each country', 'Including the screens or their description where the country asks for them.', 'method'),
        item('g05', 'Site training complete and recorded; participant material available in each language', 'See the training checklist.', 'guidance', ['ema-cs#5.3']),
        item('g06', 'Devices available; onboarding route for participants’ own devices; fallback route', 'Stock at sites, or instructions and minimum specification, plus what happens when neither works.', 'guidance', ['ema-cs#A5.1.3, A5.1.1.5']),
        item('g07', 'Helpdesk live in the required languages and hours', 'Tested with a real call or message per language.', 'method'),
        item('g08', 'Data transfer specification agreed and a test transfer checked', 'Structure, timing, and a comparison of transferred values against entries.', 'guidance', ['ema-cs#6.1.2']),
        item('g09', 'Access roles confirmed, including investigator access to their own participants’ data', 'From the first entry, not from the first monitoring visit.', 'guidance', ['ema-cs#6.6, A5.1.1.3', 'dkma-dct#4.2']),
        item('g10', 'Downtime procedure agreed', 'What participants and sites do if the system is unavailable, and how that is recorded.', 'guidance', ['ema-cs#A5.1.1.6']),
        item('g11', 'Business case re-confirmed', 'See Business case: continued justification.', 'framework', ['prince2']),
        item('g12', 'Board authorisation recorded', 'Who decided, on what evidence, on what date.', 'framework', ['prince2'])
      ]}]
    },
    training: {
      title: 'Site and participant training',
      stage: 'Controlling a stage',
      groups: [{title: 'Before and during the live study', items: [
        item('t01', 'Site staff trained before the first participant; record kept', 'Covering set-up, the site view, alerts and the data change request route.', 'guidance', ['ema-cs#5.3']),
        item('t02', 'Participant training covers when, how and what if', 'When to complete; how to correct an answer before saving; what to do after a missed entry, a lost device or a new phone; who to contact.', 'guidance', ['ema-cs#5.3']),
        item('t03', 'Material is in the participant’s language and in plain words', 'With screenshots that match the released build.', 'method'),
        item('t04', 'Separate instructions for caregivers or observers where they report', 'An observer reports what they see, not what they think the participant feels.', 'method'),
        item('t05', 'Access needs considered', 'Enlarged text, contrast, motor and cognitive demands; an alternative for participants who cannot use the device.', 'method'),
        item('t06', 'Participants told that the log-in is personal', 'Entries have to be attributable to the person who made them.', 'guidance', ['ema-cs#4.5']),
        item('t07', 'Completion reviewed with the participant at visits', 'Sites see completion early enough to act, and retraining is recorded.', 'method')
      ]}]
    },
    handover: {
      title: 'Handover to the live-study team',
      stage: 'Managing a stage boundary',
      groups: [{title: 'Before the start-up team stands down', items: [
        item('h01', 'Guidance for the live-study team written', 'Configuration summary, known limitations, contacts and where the registers are kept.', 'method'),
        item('h02', 'Open risks, issues and decisions transferred with named owners', 'Nothing is left with a person who is leaving the project.', 'framework', ['prince2']),
        item('h03', 'Change request route explained', 'Who raises a change to the live system, who signs it, and when re-testing is needed.', 'consensus', ['cpath-uat']),
        item('h04', 'Helpdesk briefed on the study before the first participant', 'Languages, devices, escalation tiers and study-specific answers.', 'method'),
        item('h05', 'Languages and countries still to be released are listed with due dates', 'Each tied to the first participant date in that country.', 'method'),
        item('h06', 'Data transfer schedule confirmed after the test transfer', 'Frequency, recipients and who reconciles each transfer.', 'guidance', ['ema-cs#6.1.2']),
        item('h07', 'Completion monitoring owner named and first review date set', 'See Progress.', 'method'),
        item('h08', 'Start-up lessons logged before the team disperses', 'See the lessons log.', 'framework', ['prince2'])
      ]}]
    },
    closeout: {
      title: 'Closeout and archiving',
      stage: 'Closing a project',
      groups: [{title: 'Before access is removed', items: [
        item('c01', 'Last entries received; open data change requests resolved or documented', 'See Issues.', 'consensus', ['cpath-dcr']),
        item('c02', 'Final transfer reconciled against counts in the system', 'Participants, forms and records, by site.', 'guidance', ['ema-cs#6.1.2']),
        item('c03', 'Each investigator holds a complete copy of their participants’ data, with audit trail, before access ends', 'Receipt confirmed by the site.', 'guidance', ['ema-cs#6.6']),
        item('c04', 'Decommissioning sequence agreed; devices returned or wiped', 'Nothing is switched off before the copies and the archive are confirmed.', 'guidance', ['ema-cs#6.12, A5.1.3.4']),
        item('c05', 'Archive readable for the retention period, with audit trail and metadata', 'And a route for inspectors to reach it.', 'guidance', ['ema-cs#6.11']),
        item('c06', 'Licences closed out as their terms require', 'End-of-study notices, return or destruction of instrument files.', 'method'),
        item('c07', 'Lessons report and end project report written', 'Build weeks, review rounds and findings recorded as numbers the next study can plan with.', 'framework', ['prince2'])
      ]}]
    }
  };

  const RISKS = [
    {id: 'R01', title: 'Electronic-use licence not in place when the build starts', cause: 'Licences are agreed per study and often per language; terms for electronic use differ by copyright holder.', effect: 'Build or screenshot review waits; first participant date moves.', response: 'Open licensing at the brief; track per instrument-language; escalate at the time tolerance.', basis: 'industry', src: ['cpath-2019']},
    {id: 'R02', title: 'Translation or linguistic validation finishes after the build needs it', cause: 'New language versions need the full translation process; added countries arrive late.', effect: 'Languages go live in waves or screens are built on draft text.', response: 'Plan per language as its own product; do not build on unapproved text.', basis: 'consensus', src: ['ispor-tca']},
    {id: 'R03', title: 'Screenshot review takes more rounds than planned', cause: 'Rendering defects, copyright-holder turnaround, late design changes.', effect: 'Testing starts on unapproved screens or is compressed.', response: 'Agree turnaround with reviewers; use the review checklist from the first set.', basis: 'method', src: []},
    {id: 'R04', title: 'Testing window compressed', cause: 'Upstream slippage with a fixed first-participant date.', effect: 'Findings pass into the live study and return as urgent changes.', response: 'Protect the planned duration; make exit criteria a board tolerance.', basis: 'consensus', src: ['cpath-uat']},
    {id: 'R05', title: 'Protocol amendment after go-live changes instruments, schedule or languages', cause: 'Most protocols are amended at least once.', effect: 'Re-licensing, re-translation, re-testing, retraining; sites run different versions for a period.', response: 'Use the change-surface check under Issues for every amendment; record which participants saw which version.', basis: 'peer-reviewed', src: ['tufts-amend']},
    {id: 'R06', title: 'Participants’ own devices unsupported, or an operating-system update breaks the app', cause: 'Device and operating-system variety outside the sponsor’s control.', effect: 'Missed entries; participants excluded by the device they own.', response: 'Publish a minimum specification; keep a provisioned fallback; watch release notes.', basis: 'guidance', src: ['ema-cs#A5.1.3']},
    {id: 'R07', title: 'Provisioned devices delayed or unusable at site', cause: 'Customs, stock, connectivity contracts, chargers and adapters by country.', effect: 'Sites cannot start participants on time.', response: 'Ship ahead of site activation; hold buffer stock; confirm connectivity per country.', basis: 'method', src: []},
    {id: 'R08', title: 'Completion falls at the timepoints that matter most', cause: 'Burden, reminders that do not fit daily life, no feedback to sites; reasons for missing entries rarely recorded.', effect: 'Missing data in the analysis of the planned endpoint.', response: 'Set a completion tolerance per key timepoint; review by site, language and device type.', basis: 'peer-reviewed', src: ['krepper-2026']},
    {id: 'R09', title: 'Participant-entered data changed without the investigator’s authorisation', cause: 'Data change requests handled as a provider or sponsor task.', effect: 'The investigator no longer controls the source data; inspection finding.', response: 'Agree the request process at initiation; log every request with its authorisation.', basis: 'guidance', src: ['ema-cs#6.1.4, A5.1.1.4', 'cpath-dcr']},
    {id: 'R10', title: 'Data transfer errors found late', cause: 'Specification agreed after go-live; no test transfer compared with entries.', effect: 'Rework before database lock; doubt about derived endpoints.', response: 'Agree the specification and check a test transfer before go-live.', basis: 'guidance', src: ['ema-cs#6.1.2']},
    {id: 'R11', title: 'Sites lose access before they hold a copy of their data', cause: 'Decommissioning scheduled by contract end, not by confirmed delivery.', effect: 'Investigator cannot meet retention duties.', response: 'Sequence closeout: copies confirmed, then archive confirmed, then access removed.', basis: 'guidance', src: ['ema-cs#6.6']},
    {id: 'R12', title: 'Provider platform release alters approved screens', cause: 'Shared platform updated across studies.', effect: 'Live screens differ from the approved screenshot set.', response: 'Require release notes and impact statement; re-check affected screens per language.', basis: 'method', src: []},
    {id: 'R13', title: 'Ethics submission made with screens or translations that later change', cause: 'Submission deadlines ahead of final screenshots.', effect: 'Resubmission, or participants see material that was not reviewed.', response: 'Submit version-locked sets; track submitted version per country.', basis: 'method', src: []},
    {id: 'R14', title: 'Helpdesk not reachable in the participant’s language or hours', cause: 'Central helpdesk in one time zone and one language.', effect: 'Device problems become missed entries.', response: 'Test each language line before go-live; monitor first-response time.', basis: 'method', src: []},
    {id: 'R15', title: 'Delivery depends on one person', cause: 'Small teams; knowledge held in mailboxes.', effect: 'Absence stops decisions and loses history.', response: 'Keep registers current; name a deputy for the project manager and for assurance.', basis: 'framework', src: ['prince2']},
    {id: 'R17', title: 'Electronic collection planned after the protocol is final', cause: 'Instruments and visit schedules chosen without checking licences, translations or electronic workflow.', effect: 'Compressed build; schedules that do not fit how participants and sites work.', response: 'Review instruments and schedule during protocol design; brief the provider early.', basis: 'method', src: []},
    {id: 'R18', title: 'Site burden from disconnected systems', cause: 'Workflow designed around sponsor processes; separate log-ins and duplicate entry at the same visit.', effect: 'Training load, errors, missed baseline entries.', response: 'Walk the visit workflow with a site before the design freeze.', basis: 'method', src: []},
    {id: 'R19', title: 'Mixed-version data after a mid-study change', cause: 'Change released by country or site over a period; versions not recorded per entry.', effect: 'Reconciliation work before analysis; scores that cannot be pooled.', response: 'Record the version against each entry; plan the cut-over per participant.', basis: 'method', src: []},
    {id: 'R16', title: 'Clock changes and travel shift diary windows', cause: 'Daylight-saving changes; participants crossing time zones.', effect: 'Entries recorded outside the window or duplicated.', response: 'Specify where the app takes its time from and how windows behave; test it; tell participants what to expect.', basis: 'guidance', src: ['ema-cs#A5.1.3.1']}
  ];

  const SURFACES = {
    licence: 'Licence scope and terms',
    translation: 'Translations and linguistic validation',
    specification: 'Design specification',
    screenshots: 'Screenshot sets (per language)',
    licensor: 'Copyright-holder screen review',
    uat: 'Testing scripts and re-test',
    site_training: 'Site training',
    participant_material: 'Participant training material',
    ethics: 'Ethics and regulatory submissions of participant-facing material',
    transfer: 'Data transfer specification and test transfer',
    devices: 'Device logistics and supported-device list',
    helpdesk: 'Helpdesk scripts and language cover',
    analysis: 'Statistical analysis and endpoint derivation notes',
    versions: 'Version record: which participants saw which version'
  };

  const s = (id, why) => ({id, why});
  const CHANGE_RULES = [
    {id: 'ct-01', label: 'Instrument added', surfaces: [s('licence', 'A new instrument needs its own electronic-use licence.'), s('translation', 'Each study language needs an approved version.'), s('specification', 'New screens and schedule entries.'), s('screenshots', 'A new set per language.'), s('licensor', 'Where the licence requires screen review.'), s('uat', 'New scripts; regression on shared functions.'), s('site_training', 'Sites need to know what participants now complete.'), s('participant_material', 'Instructions change.'), s('ethics', 'Participant-facing content changes.'), s('transfer', 'New variables in the transfer.'), s('analysis', 'New endpoint or covariate handling.'), s('versions', 'Participants enrolled earlier may not have it at baseline.')]},
    {id: 'ct-02', label: 'Instrument removed', surfaces: [s('licence', 'Licence may need to be closed or amended.'), s('specification', 'Schedule and screens removed.'), s('uat', 'Regression: nothing else depended on it.'), s('site_training', 'Sites told what stops.'), s('participant_material', 'Instructions change.'), s('ethics', 'Participant-facing content changes.'), s('transfer', 'Variables end; structure may change.'), s('analysis', 'Planned analyses lose data from a date.'), s('versions', 'Record the date collection stopped per participant.')]},
    {id: 'ct-03', label: 'Instrument wording, recall period or response options changed', surfaces: [s('licence', 'A new version may need new permission.'), s('translation', 'Every language version changes with the source.'), s('specification', 'Screen text and logic.'), s('screenshots', 'New sets per language.'), s('licensor', 'Where the licence requires screen review.'), s('uat', 'Affected screens re-tested in each language.'), s('participant_material', 'If instructions quote the instrument.'), s('ethics', 'Participant-facing content changes.'), s('analysis', 'Scores before and after may not be comparable.'), s('versions', 'Which version each entry was made on.')]},
    {id: 'ct-04', label: 'Visit schedule, timing or completion window changed', surfaces: [s('specification', 'Schedule, alarms and window logic.'), s('uat', 'Window behaviour re-tested, including participants mid-study.'), s('site_training', 'Sites schedule against the new timing.'), s('participant_material', 'When to complete changes.'), s('ethics', 'Burden on participants changes.'), s('transfer', 'Visit labels or derived flags may change.'), s('analysis', 'Window definitions feed the analysis.'), s('versions', 'Participants cross from old to new schedule.')]},
    {id: 'ct-05', label: 'Country or language added', surfaces: [s('licence', 'Licences are often per country or language.'), s('translation', 'New language versions, or confirmation that an existing one fits the country.'), s('screenshots', 'A new set per added language.'), s('licensor', 'Where the licence requires screen review.'), s('uat', 'Language-specific checks; devices used in the country.'), s('site_training', 'Sites in the new country need training in their own language.'), s('participant_material', 'New language.'), s('ethics', 'National submission.'), s('devices', 'Supply, connectivity and supported devices in the country.'), s('helpdesk', 'Language and hours.')]},
    {id: 'ct-06', label: 'Population changed (for example age range, or observer reporting added)', surfaces: [s('licence', 'A different version of the instrument may be needed.'), s('translation', 'Age-specific or observer versions per language.'), s('specification', 'Who completes what.'), s('screenshots', 'New versions per language.'), s('uat', 'Respondent-specific paths are new and have not been tested.'), s('site_training', 'Who is trained to do what.'), s('participant_material', 'Separate caregiver or observer instructions.'), s('ethics', 'New participant group.'), s('analysis', 'Respondent type affects interpretation.')]},
    {id: 'ct-07', label: 'Device approach changed (own device, provisioned device, supported systems)', surfaces: [s('specification', 'Supported devices and layouts.'), s('screenshots', 'Rendering on the added screen sizes.'), s('uat', 'Each added device type and operating system.'), s('site_training', 'Onboarding steps change.'), s('participant_material', 'Set-up instructions change.'), s('ethics', 'What participants are asked to use.'), s('devices', 'Stock, returns, minimum specification.'), s('helpdesk', 'New set-up questions.')]},
    {id: 'ct-08', label: 'Alerts, checks or branching logic changed', surfaces: [s('specification', 'Logic defined before it is built.'), s('screenshots', 'If prompts or messages are new text.'), s('translation', 'New messages need translating and review.'), s('uat', 'Each branch and boundary value.'), s('site_training', 'If site alerts change.'), s('transfer', 'If derived flags are transferred.'), s('analysis', 'If eligibility or endpoint derivation depends on the logic.')]},
    {id: 'ct-09', label: 'Data transfer or endpoint derivation changed', surfaces: [s('specification', 'Only if collection changes too.'), s('transfer', 'Specification version and a new test transfer.'), s('uat', 'End-to-end check of transferred values.'), s('analysis', 'Derivation documented with its effective date.')]},
    {id: 'ct-10', label: 'Provider platform release during the live study', surfaces: [s('specification', 'Provider impact statement against the study configuration.'), s('screenshots', 'Affected screens re-checked per language.'), s('uat', 'Regression in proportion to the impact.'), s('devices', 'Supported operating systems may change.'), s('helpdesk', 'Told what participants will notice.'), s('versions', 'Release date recorded against entries.')]}
  ];

  const UAT_AREAS = [
    {id: 'a01', scope: 'device', label: 'Set-up and log-in', objective: 'Activation, log-in, lock-out and re-set behave as specified on this device.'},
    {id: 'a02', scope: 'instrument-timepoint', label: 'Schedule and completion window', objective: 'The instrument opens and closes at the specified times; late and missed entries behave as specified.'},
    {id: 'a03', scope: 'instrument', label: 'Screen content against approved screenshots', objective: 'Each screen matches the approved screenshot set for this instrument.'},
    {id: 'a04', scope: 'instrument', label: 'Navigation, skipping and going back', objective: 'Movement between items and unanswered items behave as specified.'},
    {id: 'a05', scope: 'instrument', label: 'Entry ranges, checks and branching', objective: 'Boundary values, checks and every branch produce the specified result.'},
    {id: 'a06', scope: 'device', label: 'Reminders and alarms', objective: 'Reminders fire at the specified times and stop when the entry is complete.'},
    {id: 'a07', scope: 'device', label: 'Offline entry and synchronisation', objective: 'Entries made without connection are kept and sent once, with their original time.'},
    {id: 'a08', scope: 'device', label: 'Clock and time-zone change', objective: 'A changed device clock or time zone produces the specified behaviour and record.'},
    {id: 'a09', scope: 'language', label: 'Language-specific smoke check', objective: 'One complete entry in this language; system text and messages appear in the language.'},
    {id: 'a10', scope: 'device', label: 'Display with enlarged system font', objective: 'Text remains complete and controls usable at the largest supported font size.'},
    {id: 'a11', scope: 'once', label: 'Site view and alerts', objective: 'Site users see the specified data and alerts for their own participants only.'},
    {id: 'a12', scope: 'once', label: 'Audit trail of an entry', objective: 'Who, what and when are recorded for an entry and for a correction made before saving.'},
    {id: 'a13', scope: 'once', label: 'Data change request route', objective: 'A requested correction is authorised, applied and recorded as the process says.'},
    {id: 'a14', scope: 'instrument', label: 'End-to-end data check', objective: 'Values entered for this instrument are found unchanged in the transfer file.'},
    {id: 'a15', scope: 'once', label: 'Device replacement and end of participation', objective: 'A replaced device continues the schedule; a completed or withdrawn participant is deactivated.'}
  ];

  const KPIS = [
    {name: 'Go-live slip against plan', unit: 'working days', direction: 'max'},
    {name: 'Change requests after the design freeze', unit: 'count', direction: 'max'},
    {name: 'Open critical testing findings at exit', unit: 'count', direction: 'max'},
    {name: 'Findings first seen after go-live', unit: 'count', direction: 'max'},
    {name: 'Screenshot review rounds per language', unit: 'rounds', direction: 'max'},
    {name: 'Data change request cycle time', unit: 'working days', direction: 'max'},
    {name: 'Helpdesk first response', unit: 'hours', direction: 'max'},
    {name: 'Transfer reconciliation discrepancies', unit: 'count', direction: 'max'},
    {name: 'Completion at the primary timepoint', unit: '%', direction: 'min'}
  ];

  /* Fictional example. Every name below is invented for demonstration. */
  const EXAMPLE = {
    schema: 'clinicops-ecoa-workbench/1',
    study: {name: 'NYR-204 (fictional)', reference: 'Nyrelia Bio, invented for demonstration', stage: 'build', first_participant: '2027-03-01'},
    business_case: {
      reasons: 'Daily symptom diary is the primary endpoint; entries must be time-stamped within the evening window.',
      options: 'Participants’ own phones with a provisioned fallback. Paper rejected: entry time cannot be shown.',
      benefits: 'Completion at week 12 at or above the agreed minimum; no entries outside the window in the analysis set.',
      disbenefits: 'Start-up time for licences and three Nordic language versions.',
      timescale: 'Go-live four weeks before the first participant.',
      costs: 'Provider build, two licences, three language versions, fallback devices.',
      risks: 'Licence for the fatigue scale; Norwegian version; testing window.',
      justification: 'Confirmed at specification sign-off by the Executive.'
    },
    tolerances: {time: 'Go-live no later than 10 working days after plan', cost: 'Change orders within the agreed contingency', scope: 'No instrument or language removed without a board decision', quality: 'No open critical finding at testing exit', risk: 'No high-exposure risk without owner and response', benefits: 'Week-12 completion not below 85%', sustainability: 'Fallback devices returned and reused'},
    organisation: [
      {role: 'Executive', name: 'Study lead (fictional)', organisation: 'Nyrelia Bio', reports: 'Highlight report, every two weeks'},
      {role: 'Senior user', name: 'Outcomes research lead (fictional)', organisation: 'Nyrelia Bio', reports: 'Highlight report; screenshot sign-off requests'},
      {role: 'Senior supplier', name: 'Provider delivery lead (fictional)', organisation: 'Example eCOA Provider', reports: 'Checkpoint report, weekly'},
      {role: 'Project assurance', name: 'Independent reviewer (fictional)', organisation: 'Independent', reports: 'Stage-end review'}
    ],
    products: [
      {instrument: 'Example Symptom Diary (ESD-7)', version: '2.0', holder: 'Example University', language: 'Danish (Denmark)', licence: 'done', translation: 'done', screenshots: 'in progress', licensor_signoff: 'not started', submission: 'in progress', na_reason: '', owner: 'Translation lead', due: '2027-01-11', notes: 'Round 2: truncation on item 4.'},
      {instrument: 'Example Symptom Diary (ESD-7)', version: '2.0', holder: 'Example University', language: 'Swedish (Sweden)', licence: 'done', translation: 'done', screenshots: 'in progress', licensor_signoff: 'done', submission: 'done', na_reason: '', owner: 'Translation lead', due: '2027-01-11', notes: 'Holder signed off round 1; item 6 changed in round 2.'},
      {instrument: 'Example Symptom Diary (ESD-7)', version: '2.0', holder: 'Example University', language: 'Norwegian Bokmål (Norway)', licence: 'done', translation: 'blocked', screenshots: 'not started', licensor_signoff: 'not started', submission: 'not started', na_reason: '', owner: 'Translation lead', due: '2027-01-11', notes: 'No existing version; full translation process needed.'},
      {instrument: 'Example Fatigue Scale (EFS)', version: '1.1', holder: 'Example Foundation', language: 'Danish (Denmark)', licence: 'in progress', translation: 'done', screenshots: 'done', licensor_signoff: 'not started', submission: 'not started', na_reason: '', owner: 'Project manager', due: '2027-01-18', notes: 'Existing Danish version; licence request open.'},
      {instrument: 'Example Fatigue Scale (EFS)', version: '1.1', holder: 'Example Foundation', language: 'English (source)', licence: 'in progress', translation: 'not applicable', screenshots: 'in progress', licensor_signoff: 'not applicable', submission: 'not started', na_reason: '', owner: 'Project manager', due: '2027-01-18', notes: ''}
    ],
    risks: [
      {id: 'R01', title: 'Electronic-use licence not in place when the build starts', probability: 'high', impact: 'high', owner: 'Project manager', response: 'Weekly contact with Example Foundation; escalate at the time tolerance.', state: 'open'},
      {id: 'R02', title: 'Translation or linguistic validation finishes after the build needs it', probability: 'medium', impact: 'high', owner: 'Translation lead', response: 'Norwegian version planned as its own product with its own due date.', state: 'open'},
      {id: 'R04', title: 'Testing window compressed', probability: 'medium', impact: 'medium', owner: '', response: '', state: 'open'}
    ],
    issues: [
      {id: 'I-001', type: 'problem or concern', title: 'Norwegian written standard not stated in the licence', raised: '2026-11-10', owner: 'Translation lead', state: 'open', decision: ''},
      {id: 'I-002', type: 'request for change', title: 'Sponsor asks to add a week-6 fatigue assessment after the design freeze', raised: '2026-11-12', owner: 'Project manager', state: 'open', decision: ''},
      {id: 'I-003', type: 'assumption', title: 'Swedish version can be used unchanged in Finland', raised: '2026-11-03', owner: 'Outcomes research lead', state: 'open', decision: ''}
    ],
    schedule: [],
    surfaces: [],
    defects: [
      {id: 'F-001', script: 'UAT-004', description: 'Evening window closes one hour early after clock change', band: 'critical', state: 'open', retest: ''},
      {id: 'F-002', script: 'UAT-011', description: 'Reminder text in English on the Danish build', band: 'major', state: 'open', retest: ''},
      {id: 'F-003', script: 'UAT-002', description: 'Spacing on the log-in screen', band: 'minor', state: 'closed', retest: 'Passed on build 0.9.3'}
    ],
    changes: [{id: 'DCR-001', site: 'Site 01 (fictional)', requested: '2026-11-12', what: 'Entry made under the wrong participant', authorised_by: '', state: 'open', evidence: ''}],
    kpis: [
      {name: 'Go-live slip against plan', unit: 'working days', direction: 'max', target: '0', tolerance: '10', actual: '6'},
      {name: 'Change requests after the design freeze', unit: 'count', direction: 'max', target: '0', tolerance: '2', actual: '1'},
      {name: 'Open critical testing findings at exit', unit: 'count', direction: 'max', target: '0', tolerance: '0', actual: '1'},
      {name: 'Screenshot review rounds per language', unit: 'rounds', direction: 'max', target: '2', tolerance: '3', actual: '2'},
      {name: 'Completion at the primary timepoint', unit: '%', direction: 'min', target: '90', tolerance: '85', actual: ''}
    ],
    counts: [
      {group: 'Site 01 · Danish · own device', expected: '140', completed: '131'},
      {group: 'Site 01 · Danish · provisioned', expected: '56', completed: '44'},
      {group: 'Site 02 · Swedish · own device', expected: '112', completed: '106'}
    ],
    completion_minimum: '85',
    lessons: [{date: '2026-11-05', stage: 'Specification and licensing', what: 'Licence request for the fatigue scale opened three weeks after the brief', effect: 'Screens reviewed ahead of the licence', next_time: 'Open every licence request in the starting-up stage'}],
    uat_scripts: [],
    checklists: {
      brief: {b01: {state: 'confirmed', note: ''}, b02: {state: 'confirmed', note: ''}, b03: {state: 'confirmed', note: ''}, b04: {state: 'open', note: 'Fatigue scale holder has not replied.'}},
      'screens:Danish': {s06: {state: 'confirmed', note: ''}, s07: {state: 'open', note: 'Item 4 truncated at 320 px.'}}
    }
  };

  const ISSUE_TYPES = ['problem or concern', 'request for change', 'off-specification', 'assumption', 'decision'];

  const api = {ISSUE_TYPES, BASIS, SOURCES, STAGES, PRINCIPLES, TOLERANCES, BUSINESS_CASE, ROLES, CHECKLISTS, RISKS, SURFACES, CHANGE_RULES, UAT_AREAS, KPIS, EXAMPLE};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ClinicOpsEcoaData = api;
})(typeof globalThis === 'object' ? globalThis : this);
