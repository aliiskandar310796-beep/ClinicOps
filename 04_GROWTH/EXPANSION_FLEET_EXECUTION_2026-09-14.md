# ClinicOps expansion fleet execution — 2026-09-14

## Mission

Run three adjacent-market validation lanes in parallel while preserving one ClinicOps operating spine:

1. Clinical Trial / Site Change Integrity (`trialops`)
2. Medical-Device Quality / QMS Change Integrity (`qualityops`)
3. Clinical AI Governance Evidence Operations (`clinical-ai-ops`)

This is an execution program, not a declaration that any adjacent lane is validated. Public state remains E1 until real buyer evidence is captured privately.

## Fleet model

ClinicOps does not create a second permanent agent fleet. The existing canonical agents are assigned temporary lane responsibilities so knowledge, controls and delivery primitives remain shared.

| Function | Temporary fleet responsibility | Required output |
| --- | --- | --- |
| Regulatory Evidence Steward | Source and date control | Primary-source pack; bounded claims; unresolved interpretation list |
| Opportunity Architect | Commercial packaging | One sellable entry offer; buyer hypothesis; recurring-revenue hypothesis |
| Customer Discovery Agent | Market validation | Discovery questions; target profile; E4/E5/E6 evidence capture path |
| Visibility Architect | Public acquisition | One coherent public surface; no thin-page factory; distribution hooks |
| Portfolio Operator | Delivery design | Evidence packet structure; owner routing; closure definition |
| Release Sentinel | Resilience / release gate | Claim, privacy, scope, automation and human-authority checks |

No lane may invent buyer evidence. Prospect identities, direct emails, commercial replies and E4+ evidence remain private.

## Execution topology: parallel discovery/scoring lanes converge at Opportunity Architect

**Approved 2026-09-23.** The fleet previously ran the six functions above as an implicit fixed serial chain per lane (Regulatory Evidence Steward, then Visibility Architect, then Opportunity Architect, then Release Sentinel, with Customer Discovery Agent and Portfolio Operator slotted into the same queue). An architecture review modeled on sparse, parallel biological sensory pathways converging on one associative decision point found that most of that ordering was a scheduling habit, not a data dependency. Opportunity Architect already reads from multiple upstream outputs to produce one packaged offer, so it already functions as a convergence point; the stages feeding it should not have to wait on each other serially unless one stage's required output is genuinely another stage's required input.

Reviewing each function's required output against what the next function actually consumes:

- **Regulatory Evidence Steward stays a hard upstream prerequisite (serial, first).** Its required output — the primary-source pack, bounded claims and unresolved-interpretation list — is a genuine input dependency for every other function. No lane may build a public surface, validate demand, design delivery or package an offer against claims that have not yet been bounded; this is a claim-safety dependency, not a habit, and it is unchanged by this proposal.
- **Visibility Architect, Customer Discovery Agent and Portfolio Operator are mutually independent once Evidence Steward's bounded claims exist, and now run as a parallel discovery/scoring group.** None of their required outputs is an input to either of the other two:
  - Visibility Architect's public surface and distribution hooks are built from the bounded claims, not from Customer Discovery's target profile or Portfolio Operator's evidence-packet design.
  - Customer Discovery Agent's discovery questions, target profile and E4/E5/E6 capture path are derived from the bounded claims and the lane's name-fit criteria (see `CLINICOPS_EXPANSION_ARCHITECTURE_2026-09-14.md`), not from the public surface or the delivery design.
  - Portfolio Operator's evidence-packet structure, owner routing and closure definition reuse the shared product spine below and the bounded claims; they do not require the finished public surface or discovery questions to be drafted.
  There was no documented reason for these three to queue behind one another, so they now start as soon as Evidence Steward's output for that lane is available and proceed concurrently.
- **Opportunity Architect converges the parallel group (unchanged role, now an explicit convergence gate).** Its required output — one sellable entry offer, buyer hypothesis and recurring-revenue hypothesis — genuinely draws on all three parallel outputs (distribution hooks, validated target profile/evidence path, and delivery boundary). Opportunity Architect must therefore wait for the parallel group's outputs, but not for any ordering among them, and does not itself need to run before them.
- **Release Sentinel stays serial and last (unchanged).** Its checks (claim, privacy, scope, automation, human-authority) are run against the converged, packaged offer. There is nothing to gate until Opportunity Architect has converged the parallel outputs, so this dependency is real and this stage is not parallelized.

Net effect: the pipeline changes from four/six sequential handoffs to `Evidence Steward -> {Visibility Architect, Customer Discovery Agent, Portfolio Operator run concurrently} -> Opportunity Architect (convergence) -> Release Sentinel (gate)`. Lane-level parallelism (TrialOps / QualityOps / Clinical AI Ops running side by side) is unchanged and unaffected by this change; this is a within-lane stage-ordering change only. The machine-readable version of this topology is recorded in `04_GROWTH/expansion_lanes.json` under `opportunity_pipeline`.

## Shared product spine

Every lane must reuse the same primitives:

`approved evidence -> observation -> deterministic signal -> accountable owner -> human decision -> closure record`

The reusable packet fields are:

- event/change identifier;
- approved reference/source and provenance;
- affected records/surfaces/systems;
- observed state and evidence reference;
- explicit uncertainty / unresolved authority;
- responsible owner;
- human decision or required review;
- implementation/closure evidence;
- timestamps/version identifiers;
- reproducible export or review packet.

This means ClinicOps develops one evidence-control engine and multiple evidence schemas/presets, not multiple unrelated products.

## Lane 1 — TrialOps

### Evidence signal

Primary sources establish a current operating transition rather than a generic market-size claim:

- European Commission: from 31 January 2025 onward all clinical trials in the EU/EEA must be conducted under the Clinical Trials Regulation using CTIS.
- EMA: ICH E6(R3) Principles and Annex 1 became effective in the EU on 23 July 2025; the framework emphasizes fit-for-purpose, risk-proportionate trial conduct and reliable records/data.

### Entry offer

**Trial Change Integrity Review**

Bounded pilot envelope:

- one protocol amendment, safety communication, consent update, vendor/process change or other sponsor-approved change event;
- 1–3 approved source records;
- 3–8 affected operational surfaces selected by the buyer;
- named sponsor/CRO/site decision owners;
- output: propagation matrix, evidence references, unresolved queue, owner routing and closure packet.

ClinicOps does not decide medical, ethical, safety or regulatory acceptability.

### Validation questions

- Where does one approved trial change have to propagate today?
- Which handoffs are reconstructed manually across sponsor/CRO/site teams?
- What evidence is hardest to prove later?
- What is the consequence of a missed or delayed propagation step?
- Who owns budget for fixing the reconciliation burden?
- Would a fixed-scope review of one real change be useful enough to price or procure?

### Recurring hypothesis

Only after paid/repeated delivery: amendment-impact register maintenance, periodic study evidence review, training acknowledgement propagation review, or partner white-label packets.

## Lane 2 — QualityOps / QMSR

### Evidence signal

FDA states that the Quality Management System Regulation became effective on 2 February 2026, amending 21 CFR part 820 and incorporating ISO 13485:2016 by reference. FDA also changed its device-inspection process on that date.

### Entry offer

**QMS Change Integrity Review**

Bounded pilot envelope:

- one approved quality-system change, CAPA action, procedure change, supplier change or QMSR transition topic;
- 1–3 approved source records;
- 3–8 affected SOP/training/supplier/design/manufacturing records selected by the buyer;
- named quality-system decision owner;
- output: propagation matrix, evidence gaps, owner queue and closure packet.

ClinicOps does not certify QMS compliance, audit readiness or regulatory acceptability.

### Validation questions

- Which quality changes generate the most manual cross-record checking?
- Where do training, SOP, supplier and implementation evidence drift apart?
- What gets rebuilt before an inspection or audit?
- Which repeated check is expensive enough to outsource or maintain continuously?
- Is the buyer seeking advice, evidence assembly, execution coordination or all three?

### Recurring hypothesis

Only after repeated paid delivery: SOP/training drift review, supplier evidence register maintenance, periodic quality-change packet review, or white-label evidence operations for RA/QA consultancies.

## Lane 3 — Clinical AI Ops

### Evidence signal

- The EU AI Act is in progressive application; Commission enforcement powers and Article 50 transparency obligations apply from 2 August 2026, while high-risk timelines differ by system category and extend later.
- ISO/IEC 42001:2023 specifies requirements for establishing, implementing, maintaining and continually improving an AI management system and highlights traceability, transparency and reliability.

These sources justify operational evidence work, not a claim that ClinicOps can determine AI Act classification or compliance.

### Entry offer

**Clinical AI Evidence Review**

Bounded pilot envelope:

- one clinical/diagnostic/care workflow using or evaluating AI;
- system/vendor/intended-use and owner inventory;
- supplied policy, vendor and implementation evidence selected by the buyer;
- change/human-oversight decision map;
- output: evidence register, unresolved questions, owner routing and review packet.

ClinicOps does not determine clinical safety, legal status, medical-device classification, AI Act classification or compliance.

### Validation questions

- Can the organization identify every AI-enabled clinical workflow and accountable owner?
- What vendor/model/workflow changes require reassessment today?
- Which evidence is stored outside the team that owns the decision?
- Is human oversight documented as an operational process or only as policy text?
- What recurring review would prevent evidence reconstruction during procurement, assurance or incident review?

### Recurring hypothesis

Only after repeated paid delivery: AI-system register maintenance, vendor/model change review and periodic governance evidence packets.

## Comparative decision rule

The three lanes are compared on buyer evidence, not market hype.

| Dimension | TrialOps | QualityOps | Clinical AI Ops |
| --- | --- | --- | --- |
| ClinicOps name fit | Very high | High | High when clinically scoped |
| Reuse of current primitives | Very high | Very high | High |
| Current primary-source trigger | CTR/CTIS + E6(R3) | QMSR effective 2026 | AI Act application + AI governance standards |
| Existing ClinicOps credibility transfer | Medium-high | Very high | Medium |
| Recurring-change potential | Very high | Very high | Very high |
| Interpretation / domain boundary risk | High | Medium-high | Very high |
| Default action | Test now | Test now | Test now, narrow scope |

The winner is not the lane with the highest theoretical TAM. It is the lane that first reaches repeated E5 pain plus E6 commercial commitment and then E7 activation with acceptable delivery economics and control burden.

## Validation threshold per lane

Do not call a lane validated until all occur:

1. at least three qualified conversations in that lane;
2. at least two independent confirmations of the same repeated reconciliation/change-control pain;
3. at least one concrete commercial signal: priced-scope request, proposed pilot, procurement step or identifiable budget owner;
4. before productizing/automating the paid workflow, at least one activated paid pilot or equivalent E7 evidence.

If ten qualified lane conversations produce no E6 signal, change buyer/problem/offer/distribution before building more functionality.

## Commercial ladder

**Free acquisition:** public evidence method + browser-local tools + synthetic examples.

**Active entry:** one bounded Change Integrity Review.

**Expansion:** remediation/implementation coordination after the buyer identifies authoritative values and decision owners.

**Recurring:** periodic evidence/register/change maintenance only after repeated need is demonstrated.

**Low-touch product:** preset/template/software workflow only after a repeated paid task has stable inputs, deterministic checks and a clear human-review boundary.

## Resilience controls

- Keep lane knowledge source-dated and distinguish primary rule, observation, derivation and hypothesis.
- Never let regulatory change invalidate the entire business: source rules are adapters around the shared evidence-control core.
- Keep public market state at E1; E4+ evidence is private.
- Fail closed on unresolved source authority or decision ownership.
- No generic healthcare compliance claims.
- No patient-identifiable data in public/browser-local acquisition surfaces.
- No automation of a lane merely because a workflow can be coded.
- Preserve the current MDR/EUDAMED revenue path while adjacent lanes are tested.
- Retire or redesign a lane when evidence fails rather than accumulating zombie products.

## Current execution state

- Brand expansion architecture: deployed.
- Tier-1 machine-readable registry and promotion gates: implemented in `04_GROWTH/expansion_lanes.json`.
- Public multi-lane acquisition surface: implemented in the companion expansion execution PR.
- Browser-local scope intake: expanded for TrialOps, QualityOps and Clinical AI Ops in the companion expansion execution PR.
- External validation: must be recorded privately from real outreach/conversations; no public artifact may manufacture E4+ evidence.
- Fleet execution topology: changed 2026-09-23 from an implicit fixed serial chain to parallel discovery/scoring lanes (Visibility Architect, Customer Discovery Agent, Portfolio Operator) converging at Opportunity Architect, with Regulatory Evidence Steward and Release Sentinel unchanged as the upstream prerequisite and final release gate respectively. See "Execution topology" above and `opportunity_pipeline` in `04_GROWTH/expansion_lanes.json`.
