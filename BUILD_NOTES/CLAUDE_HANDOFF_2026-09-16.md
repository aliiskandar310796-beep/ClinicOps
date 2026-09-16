# Claude handoff — ClinicOps

Date: 2026-09-16

This handoff exists so any new operator or model can continue from the current ClinicOps state without re-inventing the recent work. Read `AGENTS.md`, `AGENT_STATE.md`, `CLAIM_RULES.md`, and the current production site/repository before acting.

## 1. Current company position

Public positioning to preserve:

**ClinicOps — Denmark market access and evidence-controlled clinical operations. Danish base. EU-wide scope. English-first international delivery, with Danish translation/localisation/validation where the Danish market requires it.**

ClinicOps is to be presented as a real active Denmark-based, EU-wide clinical/life-sciences operations company. Do not present it as a personal consultancy, an experiment, or a collection of public tests.

The public service architecture is:

1. Denmark / MedTech Market Access
2. Regulatory Integrity
3. TrialOps
4. QualityOps
5. Clinical AI Operations
6. Lab & Diagnostic Operations
7. Clinic Operations
8. Controlled Medical Content & Localisation

The evidence-control pattern is:

`approved source -> declared downstream surfaces -> reconciliation -> accountable human owner -> reviewable closure`

Machine-generated signals are evidence aids only. They are never clinical, regulatory, legal, safety, quality, release, or compliance conclusions.

## 2. Production state

The main launch was merged through PR #64, **Activate balanced seven-segment ClinicOps portfolio**.

Production `main` currently points to:

`4badf54c47922ef0be5e73ab18d739ce63c571a3`

That release introduced the Denmark-to-EU public architecture, including:

- redesigned homepage and global navigation;
- `docs/services.html`;
- `docs/denmark-market-access.html`;
- `docs/clinical-operations.html`;
- `docs/expert-network.html`;
- `docs/primary-sources.html`;
- harmonised About, Contact, Research, Tools, sitemap and `llms.txt`;
- Denmark/EU and evidence-loop visual assets;
- internal expert-network governance;
- portfolio and resilience controls;
- hardened outbound admission controls;
- preservation of the existing MedTech products/tools/research assets.

The release passed the full branch CI and Integrity Gate before merge. The GitHub Pages deployment for the release also reported success.

## 3. Known open hotfix — complete this first

There is one unfinished hotfix branch:

`chatgpt/intake-routing-hotfix-20260915`

Current branch head:

`3d3abac726a0629c8c7227e42de29c3c7f717d57`

It is 4 commits ahead of `main` and changes only:

- `docs/assessment-intake.html`
- `tests/test_assessment_intake_deeplink_contract.py`

The hotfix does two things:

1. Adds the missing `denmark-market-access` intake preset and harmonises the intake page with the production navigation/design system.
2. Adds a regression contract that scans every public `assessment-intake.html?workstream=...` deep link and fails when any public CTA points to a missing preset.

**Required next sequence:**

- inspect current diff against latest `main`;
- run the full repository test suite and both CI/Integrity workflows;
- open a small hotfix PR;
- merge only after green gates;
- verify GitHub Pages redeployment;
- verify the live origin directly in a browser, not only through a cached search result;
- re-check the Denmark Market Access CTA and all other public `?workstream=` routes after deployment.

Do not claim this hotfix is live until the deployed origin is observed.

## 4. Public messaging rules

Do not put these internal ideas on buyer-facing pages or social profiles:

- testing / not yet validated / still proving;
- fleet mechanics or capacity percentages;
- discovery/validation language that makes ClinicOps look provisional;
- internal evidence grades;
- private commercial evidence;
- agent orchestration details.

Do preserve these boundaries:

- missing public metadata is not a compliance finding;
- a public-record signal is not a legal/regulatory conclusion;
- manufacturer, authorised representative, importer and PRRC duties remain with the responsible legal actors;
- human clinical/regulatory/safety/quality/release decisions remain with qualified accountable owners.

Future public copy should use the active-company architecture above, not older emails/pages that described ClinicOps as "testing" a workflow.

## 5. Expert-network model

ClinicOps uses a **controlled project-based associate network / private vetted bench**.

Possible project contributors include independent clinical researchers, life-science/MDR/clinical-trial consultants, Danish physicians, nurses and other specialists where the project needs them.

Do not imply that people are employees, officers, medical directors, authorised representatives, standing clinical decision-makers or sources of borrowed authority unless that relationship is formally established.

Keep the private registry consent-based and verify, where relevant:

- credentials / authorisation;
- conflicts;
- availability;
- compensation;
- insurance;
- confidentiality / IP / GDPR terms;
- project role boundaries;
- representation rights;
- public-name consent.

Direct patient-care work is a separate governance lane and must not be inferred from the ordinary project network.

## 6. Outbound and acquisition controls

The user wants high-agency acquisition and broad distribution, but acquisition must remain controlled and reputationally safe.

Important operating rule: **all ClinicOps outreach is sent only from `info@clinicops.dk` through Outlook.** Do not use Gmail or another sender for ClinicOps outreach.

Treat "many fleets" as many bounded acquisition cells, content/distribution motions and opportunity searches — not as uncontrolled bulk email.

The current outbound controller is in:

`src/clinicops_os/outbound_control.py`

It is designed to fail closed around:

- daily cold-send ceilings;
- Denmark cold-outreach restrictions;
- unknown jurisdiction/domain risk;
- prior-domain contact / deduplication;
- private permanent suppressions;
- freshness/completeness of the outbound snapshot.

Respect the private suppression/DNC state; do not copy prospect lists, mailbox histories or private CRM data into the public repository.

Do not bypass the controller just because a connector can technically send more mail.

Acquisition should be multi-channel: partner/referral motions, expert-network relationships, industry communities, useful public research, tools, targeted social content, direct warm outreach and tightly controlled cold outreach.

## 7. LinkedIn and social harmonisation — still outstanding

The website has moved ahead of the LinkedIn surfaces. The next operator should harmonise the founder profile, ClinicOps company page, featured links, visuals and posting programme with the live architecture.

### Personal LinkedIn profile

Target headline:

**Founder, ClinicOps | Denmark market access & evidence-controlled clinical operations | MedTech, trials, quality & clinical AI**

Target About direction:

> ClinicOps is a Denmark-based, EU-wide clinical and life-sciences operations company. We help teams move regulated changes and market-entry work through controlled evidence chains — from source requirement to localisation or operational implementation to accountable human review.
>
> Current work spans Denmark market access, regulatory integrity, EUDAMED, SS(C)P and Class III / implantable transition, plus TrialOps, QualityOps, Clinical AI Operations, Lab & Diagnostic Operations, Clinic Operations and controlled medical content/localisation.
>
> The operating model is evidence-controlled: approved source -> declared downstream surfaces -> reconciliation -> accountable human owner -> reviewable closure. Machine outputs support the evidence chain; they do not replace clinical, regulatory, legal, safety or quality authority.
>
> Danish base. EU-wide scope. English-first international delivery, with Danish localisation/validation where the market requires it.
>
> clinicops.dk | info@clinicops.dk

Use an Experience entry for ClinicOps that describes the company and scope, rather than implying that every delivery task is personally performed by the founder.

Featured links should point to the current high-value surfaces, preferably:

- `https://clinicops.dk/denmark-market-access.html`
- `https://clinicops.dk/clinical-operations.html`
- `https://clinicops.dk/tools.html`
- one strong public research/example page.

### ClinicOps LinkedIn company page

Target tagline:

**Denmark market access & evidence-controlled clinical operations. Danish base. EU-wide scope.**

Target About direction:

ClinicOps is a Denmark-based, EU-wide clinical and life-sciences operations company. We support evidence-controlled market access and clinical operations across MedTech, regulatory integrity, clinical trials, quality systems, clinical AI, labs/diagnostics, clinic operations and controlled medical content/localisation.

For Denmark market entry, the workflow is source-led: identify the applicable Danish/EU requirement, reconcile the controlled source package, localise where required, preserve terminology/version evidence and route closure to the accountable reviewer or legal actor.

ClinicOps does not replace manufacturers, authorised representatives, importers, PRRCs, sponsors, investigators or other legally accountable roles. Machine outputs are operational evidence signals, not compliance or clinical verdicts.

**Danish base. EU-wide scope.**

Suggested specialties:

`Denmark Market Access, EU MDR, EUDAMED, SS(C)P, Regulatory Integrity, TrialOps, QualityOps, Clinical AI Operations, Lab Operations, Clinic Operations, Medical Content, Medical Localisation`

### Visuals

Use the restrained Scandinavian clinical-tech visual language already present on the site:

- whitespace and structured evidence-flow motifs;
- Denmark-to-EU / evidence-chain cues;
- real workflow concepts rather than futuristic AI imagery;
- no neon robots, synthetic clinicians or generic sci-fi dashboards.

Create/update the founder banner and company-page banner only after checking current LinkedIn dimensions and the rendered crop in the live browser.

### Launch/post sequence

Build the first social sequence around the new site rather than generic promotion:

1. **ClinicOps repositioning** — Denmark market access + evidence-controlled clinical operations; explain the source -> evidence -> owner model.
2. **Denmark market access** — practical post on Danish market documents/localisation and how ClinicOps structures the handoff.
3. **Regulatory integrity** — demonstrate one existing tool or specimen and clearly separate evidence signal from compliance judgment.
4. **Clinical operations** — explain the six operational lanes without claiming clinical authority.
5. **Controlled localisation** — approved English/source -> Danish localisation -> terminology/version reconciliation -> reviewer validation.
6. **Project expert network** — describe the governed independent network without inflating headcount or authority.
7. Continue with primary-source explainers, useful tools, concrete workflow observations and research findings.

Every post should have one useful takeaway and a natural link to the relevant ClinicOps page. Avoid repetitive sales-only posts.

Do not claim that a profile/page/post was updated until the live LinkedIn page has been re-opened and verified.

## 8. Browser/social connector reality

The installed LinkedIn connector available to the prior operator was useful for lookup, not profile editing. Profile/page edits therefore require an authenticated browser session or another connector that explicitly supports LinkedIn writes.

A social scheduling connector is installed, but do not assume LinkedIn publishing is connected: verify the network connection first. If not connected, ask the user to connect the LinkedIn account/page and then continue without re-planning the whole programme.

Never ask for or store account passwords in the repository.

## 9. QA / risk surveillance

The user explicitly wants continuous attention to inconsistencies, bugs, misrepresentation and operational risk.

Do not solve that by creating hundreds of redundant agents or jobs. Reuse the existing repository agents under `.github/agents/` and create bounded checks that produce evidence.

Minimum recurring review areas:

- **production integrity:** CI, Integrity Gate, Pages deployment, live-origin rendering, metadata, sitemap, broken links;
- **buyer-journey integrity:** every CTA/intake preset, contact path, tool handoff and conversion route;
- **claims/source integrity:** current Danish/EU primary sources, claim/reference links, stale regulatory dates, wording drift;
- **brand consistency:** website, LinkedIn founder profile, company page, outbound templates, research and tools all describe the same active company;
- **outbound safety:** sender, deduplication, jurisdiction rules, private suppressions and daily cold ceiling;
- **authority boundaries:** no automated clinical/legal/regulatory/safety/quality verdicts and no borrowed expert authority;
- **commercial learning:** capture replies, meetings, referrals and paid work as private evidence, then rebalance effort based on observed evidence rather than vanity activity.

A separate attempt to add another hourly monitoring automation hit the account's active-task limit. Do not assume an additional risk-watch task exists. Prefer reusing or replacing an existing automation if the user wants a persistent monitor.

## 10. Working style for the next operator

Be high-agency, but do not trade resilience for activity volume.

- Fetch latest `main` before writing.
- Reconcile concurrent Claude/ChatGPT changes; never overwrite another active branch blindly.
- Use small PRs for production changes.
- Fix root causes and add regression contracts where possible.
- Run the entire relevant gate before merge.
- Verify the live surface after deployment.
- Keep buyer-facing language simple and company-level; keep internal mechanics private.
- Preserve every existing useful product, research page, example and tool unless there is a concrete reason to remove it.
- Prefer multi-channel organic visibility and useful public artifacts over spam volume.

### Immediate priority order

1. Finish and merge the intake hotfix branch with full green validation and live-origin verification.
2. Re-audit the live site for stale public language, broken buyer journeys, source drift and metadata issues.
3. Harmonise the founder LinkedIn profile and ClinicOps company page with the public architecture above; verify live rendering.
4. Establish the first coherent LinkedIn/company-page post sequence and connect scheduling only if the network is actually authorised.
5. Continue controlled acquisition from `info@clinicops.dk` only, using the repository outbound guardrails and private deduplication/suppression data.
6. Maintain recurring risk/brand/claims/buyer-journey surveillance without agent sprawl.

When uncertain, choose evidence provenance, reversible execution and accurate representation over speed or apparent scale.
