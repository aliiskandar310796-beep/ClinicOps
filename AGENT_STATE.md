# ClinicOps shared agent state

Last updated: 2026-09-11 after PR #25 commercial-priority correction and privacy-surface resilience hardening.

## Canonical truth
This GitHub repository is the shared source of truth. Pull/fetch `main` before work. Local terminal state, ZIPs and chat transcripts are secondary until their changes land here. Preserve concurrent work; never force-overwrite a newer branch/file.

## Current production baseline
- `clinicops.dk` is the live GitHub Pages production site. The old GoDaddy-hosted site is retired; GoDaddy remains DNS only.
- HTTPS is enforced and GitHub Pages deploys `docs/**` through `.github/workflows/pages.yml`.
- Latest merged baseline entering this update: `4960533c7e90ab11e7077de4ff152cf8d448be4f` — **Correct commercial priority contract (#25)**.
- PRs #18–#20 added the reusable buyer-conversation → pilot playbook and first-pilot scope template while removing prospect-specific context from the public repository.
- PR #21 restored `/privacy-notice/` after the DNS/hosting cutover and linked the standard public site surface to it.
- PRs #22–#25 added a demand-resilient service ladder, cash-protecting commercial activation gate, adaptive service-entry scoring and then corrected that scoring so the Class III Transition Map Pilot is the only default `DO NOW` offer until buyer evidence activates an adjacent entry.
- This resilience update adds `/privacy-notice/` to the bounded production live-site check, makes the generated Transition Map sample privacy-visible through its renderer, and contract-tests sitemap-wide privacy discoverability plus the current no-tracking runtime promise.
- The bounded EUDAMED canary and evidence-freshness jobs remain on the current Ops Watch path.

## Production acquisition and conversion surface
The public site has 14 sitemap URLs:
- `/`
- `/about.html`
- `/assessment-intake.html`
- `/authorised-representative-portfolio-intelligence.html`
- `/class-iii-transition.html`
- `/contact.html`
- `/eudamed-transition.html`
- `/identifier-check.html`
- `/privacy-notice/`
- `/readiness-score.html`
- `/research.html`
- `/sscp-operations.html`
- `/tools.html`
- `/transition-map-sample/`

All public HTML pages are governed by production metadata/link/sitemap checks. Do not recreate duplicate `/eudamed/` or `/mdr-transition/` pillar pages that compete with the existing production pages.

### Homepage conversion path
The homepage exposes three useful levels of commitment:
1. **Request a Regulatory Intelligence Assessment** → `assessment-intake.html`.
2. **View a sanitized Transition Map sample** → `/transition-map-sample/`.
3. A direct **Scope a small pilot** mailto remains as the shortest high-intent path.

Homepage Open Graph title and description are locked to the canonical `<title>` and meta description by a regression test. Do not introduce separate social-marketing copy unless deliberately changing the canonical page copy as well.

### Browser-local assessment intake
`docs/assessment-intake.html` is a structured scoping brief builder, not a hosted form service.
- No form action or backend endpoint.
- No analytics/tracking.
- No `fetch`, XHR, `sendBeacon` or WebSocket network submission.
- User answers stay in the browser page until the user explicitly creates an email draft.
- The generated draft is opened through the user's own email client to `info@clinicops.dk`; the user decides whether to send.
- The page explicitly warns against patient-identifiable data.
- Contract: `tests/test_assessment_intake_contract.py` blocks silent network/form regressions.

Do not replace this with a third-party form endpoint or account without Ali's explicit approval.

#### Readiness Score → assessment-brief handoff (added 2026-09-10 by Claude, PR #14)
The Readiness Score result offers **Continue to the assessment brief** as its primary CTA (the direct assessment mailto remains as the secondary path). Clicking it — an explicit user action — writes a one-shot, tab-scoped `sessionStorage` payload (`clinicops.readiness.handoff`: score, band, gap list, timestamp only; never company/customer data). `assessment-intake.html` consumes and immediately deletes the key, and prefills the optional notes field only when it is empty and the payload is fresh (<1h). No network path was added on either page; behaviour is unchanged when storage is unavailable. Contracts: `tests/test_readiness_handoff_contract.py` (key agreement, one-shot consumption, no network tokens) and `conversion_quality.py` requires `readiness-score.html → assessment-intake.html`.

Do not rebuild or refactor this handoff speculatively. If either page changes, keep the handoff contract green by fixing the site, not weakening the tests.

### Sanitized Class III Transition Map sample
`docs/transition-map-sample/index.html` is public proof of the paid deliverable format.
- Generated from the same `render_client_html()` path used by the client bundle.
- Source fixture `examples/portfolio.csv` is fictional/sanitized.
- `scripts/render_public_demo.py --check` prevents the public sample from drifting from the paid renderer.
- The sample explains what a small pilot can start with and what the human-reviewed output contains.
- Its primary next step is the browser-local `assessment-intake.html`; direct email and the free Readiness Score remain available.
- The sample is linked from Tools, the homepage and the Class III transition page.
- The sample exposes `/privacy-notice/` through the renderer, so regeneration cannot silently remove that privacy path.
- The conversion contract requires the sample → assessment-intake path and the Class III page → sample/intake paths.
- Ops Watch verifies the deployed sample.

Do not put confidential client/prospect data into this sample or any public Pages artifact.

### Public privacy surface
`docs/privacy-notice/index.html` is part of the production surface and must remain reachable at `https://clinicops.dk/privacy-notice/` because prior business-development communications referenced that URL.
- It describes the current static GitHub Pages site, browser-local tools and current no-cookie/no-analytics/no-tracking posture.
- Every sitemap-listed HTML page must expose a privacy-notice path; `tests/test_privacy_surface_contract.py` enforces this dynamically from `docs/sitemap.xml`.
- The same contract blocks known tracking runtime tokens while the notice says ClinicOps runs no analytics/tracking.
- `.github/workflows/ops-watch.yml` executes `scripts/check_live_site.py`; the privacy notice is a monitored target so a repeat 404 becomes an operational failure rather than a silent legal/commercial regression.

Do not add analytics/tracking or materially change the privacy posture without Ali's explicit approval and a corresponding privacy-notice/contract update.

## Public free tools
### EUDAMED Identifier Check
- `docs/identifier-check.html`
- Browser/client-side only.
- GS1 Mod-10 validation, common SRN role decoding and B-prefix structural screening.
- B-prefix is a ClinicOps screening signal, not a compliance conclusion or quoted Commission rule.

### Transition Readiness Score
- `docs/readiness-score.html`
- Browser-only five-question operational work-plan readiness signal.
- Deterministic 0–100 result with evidence-gap explanations.
- Not a regulatory risk, compliance, legal or enforcement score.
- No live EUDAMED lookup and no browser network calls.
- Contract: `scripts/validate_readiness_page.py` plus the PR #14 handoff contract.

Keep both tools free. Monetize human-reviewed portfolio judgement, transition work planning and monitoring.

## Website resilience gates
Current CI includes:
- pytest
- Ruff
- Revenue OS experiment-contract smoke
- executable agent five-gate smoke
- Transition Readiness Score contract
- public Transition Map renderer-drift contract
- site metadata contract
- deterministic sitemap contract
- internal-link contract
- client-bundle smoke test
- custom-agent profile audit
- claim-registry audit
- claim-reference integrity
- governed website content validation
- sanitized report fixture check
- public-copy claim gate
- sitemap-wide privacy visibility / no-tracking contract

### Site metadata
`scripts/validate_site_metadata.py` + `src/clinicops_os/site_quality.py` enforce self-canonical URLs, Open Graph essentials, Twitter summary card and parseable JSON-LD. Homepage additionally requires Organization/WebSite/WebPage types.

The current favicon is a compact checkmark icon, not a proper corporate logo. Do **not** label it as the Organization `logo` merely to silence SEO tooling. No `og:image` until a proper brand/social asset is deliberately approved. `twitter:card` stays `summary` until that asset decision changes deliberately.

### Sitemap
`scripts/render_sitemap.py --check` makes `docs/sitemap.xml` deterministic from public HTML canonicals and excludes the custom 404. Adding/removing a public canonical page without updating the rendered sitemap fails CI.

### Internal links
`src/clinicops_os/link_quality.py` + `scripts/validate_internal_links.py` fail CI on broken local production links while allowing external/mailto/tel targets. Do not weaken this check to accommodate broken links; repair the links instead.

### Conversion paths
`src/clinicops_os/conversion_quality.py` + `tests/test_conversion_quality.py` protect only durable high-intent navigation contracts, not marketing copy. Current protected paths include homepage → assessment/sample, Tools → sample, Readiness Score → assessment, assessment → sample/readiness, Class III transition → assessment/sample, and public sample → assessment.

### Ops Watch
`.github/workflows/ops-watch.yml` remains bounded and read-only. It covers:
- evidence freshness;
- claim-reference integrity;
- governed-content validation;
- bounded EUDAMED reachability canary;
- live `clinicops.dk` HTTPS/content checks, including the privacy notice.

It does not publish, contact prospects, make client compliance findings or mutate third-party systems.

## Search / indexing status
GSC Wizard is configured against `https://clinicops.dk/` and the canonical production sitemap `https://clinicops.dk/sitemap.xml`.

Observed 2026-09-10:
- Live crawl confirms the GitHub production homepage, sample and assessment intake return HTTP 200, are indexable, self-canonical and expose structured data; the post-PR #16 live crawl also confirmed the Class III page and sample remain 200/indexable/self-canonical.
- Homepage is known/indexed in Search Console; most newly launched URLs are still unknown to Google immediately after the migration/deployment.
- The public Transition Map sample and assessment intake are in the GSC Wizard indexing tracker.
- `assessment-intake.html` has reported `URL is unknown to Google`; this is an indexing/discovery state, not a live-site failure.
- Do not mass-produce thin SEO pages while current production URLs are still being discovered.
- A Search Console sitemap submission of `https://clinicops.dk/sitemap.xml` should be verified manually if it has not already been submitted; changing GSC Wizard's sitemap configuration does not itself prove a Search Console sitemap submission.

Current SEO-tool warnings are non-blocking: some title/meta lengths exceed usual display guidelines, and Organization schema lacks a logo. Do not rewrite approved page copy or mislabel the favicon merely to remove these warnings.

## Executable agent layer
Do not create a second fleet. The six canonical `.github/agents/` profiles remain:
1. Regulatory Evidence Steward
2. Portfolio Operator
3. Release Sentinel
4. Opportunity Architect
5. Customer Discovery Agent
6. Visibility Architect

Executable runtime:
- `src/clinicops_os/agents.py`
- `scripts/agent_gate.py`
- sanitized fixture `examples/agent_tasks.json`
- tests `tests/test_agents.py`

Five mandatory gates:
1. Evidence check
2. Claim safety check
3. Business value check
4. Reproducibility check
5. Human review for external publication

Reuse `clinicops_eudamed.claim_guard.check_claim()` and the existing claim registry; do not introduce a parallel regulatory-claim checker.

## Claim governance and corrected regulatory thesis
- `research/claims.jsonl` is the versioned claim registry.
- `src/clinicops_eudamed/claim_guard.py` is the known-bad-phrasing guard.
- `src/clinicops_os/claim_registry.py` is the claim-status/use/review gate.
- Public regulatory copy must remain within `CO-CLM-####` evidence and allowed-use boundaries.
- Do not revive the rejected manufacturer-diligence-failure headline from the Class III census.
- In the corrected 8 Sep 2026 sample, sampled MF-role MDR Class III registrations had linked validated SS(C)P metadata; the commercial opportunity is legacy-to-MDR transition/document-operations workload, not a generic allegation about manufacturer diligence.
- Preserve MF/AR/IM/PR actor-role distinctions.
- Do not infer SS(C)P non-compliance from a missing/null public link alone.
- Do not imply an end-to-end EUDAMED audit when public/API reachability is bounded.
- Commercial priority scores are operator-triage signals, not regulatory/compliance/legal risk scores.
- EUDAMED canary correction remains `CO-CLM-0011`: the previously observed apparent page-32,000 failure boundary was not reproduced on 9 Sep 2026; treat it as a dated observation, not a stable system limit.

## Revenue OS and client delivery
Commercial loop:

`signal → evidence coverage → ranked account → smallest commercial experiment → result → learning → reusable asset → revenue`

Executable components:
- `src/clinicops_os/revenue.py` + `clinicops-revenue-rank`
- `src/clinicops_os/experiments.py` + `clinicops-experiments`
- `experiments/EXPERIMENT_LEDGER.md`
- `.github/ISSUE_TEMPLATE/experiment.yml`

### Current commercial validation threshold (EXP-001, merged in PR #15)
Do not call the core offer validated from conversations or compliments alone. Current decision rule:
1. complete three qualified portfolio conversations;
2. at least two buyers independently describe repeated portfolio reconciliation / evidence-control work addressed by the offer; and
3. at least one buyer makes a concrete commercial commitment such as asking for a priced scope, proposing a pilot, or identifying budget/approval ownership.

A stronger signal is a paid pilot followed by repeat, expansion, referral or reuse on another portfolio. If ten qualified target-buyer conversations produce no concrete willingness to sponsor a pilot, no priced-scope request and no repeated evidence of budgeted urgency, pause product expansion and change at least one of buyer, problem, offer, packaging or distribution before building more functionality.

### Current service-entry discipline (PRs #22–#25)
The Class III Transition Map Pilot is the only default `DO NOW` service entry until commercial evidence changes that decision. Adjacent service entries are experiments, not parallel launch instructions.

Activate an adjacent entry only when a qualified buyer conversation, concrete flagship objection, paid/design-partner delivery, or verified external change produces evidence for that exact workflow. Do not create outreach, pricing, public product surface or delivery work merely because an adjacent idea scores well on paper.

Before material client work begins, apply `sales/commercial-activation-gate.md`: written scope/acceptance plus an approved activation condition (upfront payment, agreed deposit/milestone, accepted PO/signed procurement commitment, or Ali-approved bounded design-partner exception). Do not consume delivery capacity on an informal “go ahead” or open-ended unpaid work.

Service-first delivery remains:

`clinicops.dk → free screening / proof sample → browser-local scope brief → controlled private intake → validation/analysis → human regulatory review → secure client bundle → feedback → Revenue OS learning`

Bundle schema `1.1` includes:
- `client_report.html`
- `portfolio_report.md`
- `portfolio_report.json`
- `intake_diagnostics.md`
- `manifest.json` with source/output hashes

Real prospect/account data and confidential client bundles stay private. Public GitHub contains only sanitized fixtures and reusable code.

## External-action boundaries
Require Ali's case-by-case approval before:
- LinkedIn publishing;
- Gumroad/pricing changes;
- creating third-party accounts or live form endpoints;
- analytics/tracking deployment.

Permanent DO_NOT_CONTACT:
- Ergomed Group
- PrimeVigilance

## Budget/resilience doctrine
ClinicOps is bootstrapped. Default to:
- low fixed cost;
- GitHub + Pages + existing domain/mail + AI leverage;
- accountable service revenue before expensive SaaS;
- automation only where repeated paid-work friction proves value;
- reinvest validated revenue into infrastructure.

Avoid expensive CRM/cloud/portal/data purchases until real paid usage proves the need.

## Coordination protocol
1. Fetch `main` first.
2. Treat GitHub `main` as canonical over chat/local state.
3. Preserve corrections, claim IDs and evidence limitations.
4. Reuse existing modules before adding parallel logic.
5. On conflict, fetch newest and merge; never force-overwrite concurrent work.
6. Use feature branches/PRs for material multi-file changes.
7. Verify newest CI before declaring code green.
8. Verify Pages deployment for `docs/**` changes.
9. Use the narrowest existing agent; expand capability before fleet size.
10. Keep private customer/prospect evidence out of the public repo.

## Highest-leverage next work
1. **Commercial validation still outranks speculative product work.** Use the live sample, Readiness Score and browser-local assessment brief in a small number of high-information conversations with ARs, regulatory consultancies and Class III/implantable manufacturers; record private buyer evidence against EXP-001.
2. Verify/submit the production sitemap in Google Search Console if not already done; then give indexing time rather than creating a large content batch.
3. Convert a qualified buyer signal into the first paid or deliberately approved design-partner Class III Transition Map using `sales/first-pilot-scope-template.md` plus `sales/commercial-activation-gate.md`; capture objections, missing intake fields, delivery friction, payment/procurement friction and willingness-to-pay privately.
4. Strengthen credibility and offer clarity only where real buyer objections show a gap. Do not invent testimonials, ROI, turnaround promises or regulatory certainty.
5. Build portal/SaaS features only when repeated paid engagements prove multi-user upload, action tracking or recurring monitoring needs.
