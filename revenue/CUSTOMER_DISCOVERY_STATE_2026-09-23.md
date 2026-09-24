# Customer discovery state audit — 2026-09-23

Status: read-only audit snapshot. Nothing else in the repo was modified. Scope: `revenue/`, `sales/`, `offers/`, `04_GROWTH/`, `05_CLIENT_DELIVERY/`, `00_STATE/`, `CLAIM_RULES.md`, `VALIDATION_AND_SCALABILITY_GATES.md`, `AGENTS.md`, `docs/services.html`, `docs/assessment-intake.html`, plus spot reads of `experiments/EXPERIMENT_LEDGER.md`, `03_OPERATIONS/`, `examples/revenue_accounts.csv`, `AGENT_STATE.md`. Large files (`04_GROWTH/*2026-09-14/19`, `offers/gumroad-funnel-plan.md`, several `sales/` docs) were read in part (headers, gates, key sections), not line by line.

Invariants applied: no fabricated customers/replies/deployments/credentials/testimonials/partners; E4+ needs genuine human buyer interaction with a private evidence reference; cold email ceiling 15/day; Danish-domiciled organisations never cold-emailed.

## 1. Honest evidence level

**Highest level verifiable from this repository: E3 (verified demand test delivered — execution evidence only). Confirmed E4+ buyer evidence: NONE verifiable here.**

Justification:
- E1 (external market/regulatory signal): present and public (primary-source research, specimen, claim registry).
- E2 (qualified reachable account): asserted only in private systems (a "448-row master" per `00_STATE/GOVERNANCE_BOUNDARIES.md`); no row is in the repo, so E2 is unauditable here.
- E3: outbound was sent (12 Sept sends, one confirmed delivery failure on 13 Sept). That is execution evidence, not buyer evidence.
- E4: `00_STATE/GOVERNANCE_BOUNDARIES.md` mentions a "confirmed-partner meeting" (calendar hold repaired locally, no external attendees). A scheduled meeting is not a recorded human buyer response or qualified conversation, and no private evidence reference is cited. Cannot be scored E4 on this record. If Ali holds a private record of an actual buyer/partner exchange, it must be logged with a private evidence ref before any E4 claim.
- `experiments/EXPERIMENT_LEDGER.md` EXP-001 "Result: pending", "Learning captured: pending". `04_GROWTH/EXPANSION_FLEET_EXECUTION_2026-09-14.md` says "Keep public market state at E1; E4+ evidence is private".
- Asset ledger: commercial value "UNKNOWN / E1-E3 only". Nothing is REAL-WORLD VALIDATED, REPEATABLE or SCALABLE per `VALIDATION_AND_SCALABILITY_GATES.md`. No paid engagement (E7), no delivery/payment (E8), no repeat (E9).
- COMMERCIAL-8 score cap: without E4 max 3/10; without E5 max 5/10 (`04_GROWTH/DISCOVERABILITY_COMMERCIAL_EVIDENCE_FLEETS_2026-09-19.md`).
- EXP-001 threshold status: 0 of 3 recorded qualified portfolio conversations, 0 of 2 pain confirmations, 0 of 1 commercial commitments (all as far as the repo shows).

## 2. What exists

Legend: REAL = reflects actual external-world events; TEMPLATE = structure/policy with no live data; SPEC = internal design; SYNTHETIC = fictional fixture.

### revenue/
- `revenue/README.md` — Revenue OS contract (coverage-aware account scoring, band and next-experiment labels, public-repo data rule, "not a regulatory-risk score"). SPEC. Backed by code `src/clinicops_os/revenue.py`, `tests/test_revenue.py`.
- `revenue/CLAUDE_HANDOFF.md` — instruction to build a private 3-5 account working set, run `clinicops-revenue-rank`, log experiments, report back. TEMPLATE/instruction. No output report from it exists in the repo.
- `examples/revenue_accounts.csv` — four "Example ..." rows, example.com URLs. SYNTHETIC.

### sales/
- `commercial-activation-gate.md` — internal control: written scope plus one activation condition (upfront, deposit, PO, design-partner exception) before delivery; abstention boundary; cash-evidence fields. SPEC, no live use.
- `standard-pilot-preflight.md` — fail-closed preflight (`clinicops-pilot-preflight`) fed by a private activation record. SPEC + tooling; example JSON is synthetic.
- `first-pilot-scope-template.md` — Class III Transition Map pilot scope skeleton with placeholders. TEMPLATE.
- `buyer-conversation-to-pilot-playbook.md` — 25-minute conversation structure, falsification questions. TEMPLATE.
- `outreach-operating-pack.md` — suppression gate, 15/day ceiling, 5/5/5 split, message patterns. TEMPLATE/policy.
- `global-sales-swarm.json` — 33 cells x lead quota = 99 net-new opportunities target. PLAN, no results.
- `clinical-operations-offer-pack.md`, `global-distribution-playbook.md` — adjacent-lane packs (Clinical Ops etc.). SPEC, largely superseded by 2026-09-18 narrowing.
- `integrity-gate-pilot.md` — Integrity Gate first-pilot envelope (1-3 sources, 2-6 surfaces, 3-10 fields, one reviewer, one cycle); status "ACTIVE TEST / SOFTWARE-VALIDATED / ECONOMICALLY UNVALIDATED". SPEC.
- `pilot-dry-run-harness.md`, `delegation-proof-protocol.md` — synthetic dry-run harness and founder-independence proof protocol. SPEC; states it is not proof by itself.

### offers/
- `cash-entry-service-ladder.md` — tiers A1-A6, B1-B3, C1-C4; declares Class III Transition Map Pilot the only default DO NOW. SPEC; no prices.
- `class-iii-transition-map.md` — offer spec, "internal offer specification / validation stage". SPEC.
- `gumroad-funnel-plan.md` — draft Gumroad copy, all prices `[price — user to set]`, CTA "Request a Transition Intelligence Assessment". DRAFT.

### 04_GROWTH/
- `ASSET_VALIDATION_LEDGER_2026-09-16.md` — Change Surface Mapper and Evidence Change Control Pack gate statuses; mostly UNKNOWN/PENDING. Honest ledger.
- `DISCOVERABILITY_COMMERCIAL_EVIDENCE_FLEETS_2026-09-19.md` — DISCOVERY-8 / COMMERCIAL-8 mission definitions, E-ladder caps, P0 LinkedIn/entity defect, baseline tasks (P0-A/B/C not shown as completed). PLAN.
- `CLIENT_ACQUISITION_ENGINE.md` (607 B) — pre-narrowing funnel to "Transition Intelligence Scan / Portfolio Intelligence Review / Monitoring". Stale stub.
- `EXPANSION_FLEET_EXECUTION`, `CLINICOPS_EXPANSION_ARCHITECTURE`, `ACTIVE_PORTFOLIO_OS`, `VISIBILITY_EXPANSION_SPRINT`, `PRODUCT_EXTRACTION_DOCTRINE`, `expansion_lanes.json`, `CONTENT_ENGINE`, `AUTOMATED_PUBLISHING_PIPELINE` — multi-lane expansion planning, largely superseded by the 2026-09-18 positioning. PLAN/history.

### 05_CLIENT_DELIVERY/
- `CLIENT_DELIVERY_ENGINE.md` (688 B) — one-page workflow and quality-gate list; names "Transition Intelligence Scan" and "Monitoring Service". Stub, not linked to the preflight/review/verify chain.

### 00_STATE/
- `BUSINESS_THESIS.md` — flagship = Regulatory Change Integrity Review; EXP-001 threshold; E0-E9 ladder; standard paid-pilot CLI chain. Policy.
- `ACTIVE_FLEETS.md` — mission fleets, EXP-001 threshold, E-ladder, AI-COMPANY-001, paid-pilot path. Policy.
- `GOVERNANCE_BOUNDARIES.md` — the only place private-state facts leak in (448-row private master, delivery failure, partner-meeting hold, HubSpot unused, DNC list). Mixed: policy plus unverifiable REAL claims.
- `CHANGELOG_AND_NEXT.md`, `PRODUCTION_SURFACE.md`, `AGENT_TAXONOMY.md` — status and next steps.
- All carry the banner "shard proposal (draft, not yet reconciled against live main)".

### Governance files
- `CLAIM_RULES.md` (8 claim rules), `AGENTS.md` (specialization gate, non-negotiables), `VALIDATION_AND_SCALABILITY_GATES.md` (7 dimensions, lifecycle PROTOTYPE to SCALABLE, "commercial validation needs E4+"). Policy.
- `03_OPERATIONS/CUSTOMER_DISCOVERY_LEDGER.md` — blank conversation-record template (not in `revenue/`). TEMPLATE, zero entries.

### Public surfaces
- `docs/services.html` — one flagship: Regulatory Change Integrity Review; entry via portfolio-scoped scan; monitoring only after demonstrated recurrence; no price, no timeline, no named proof of delivery. Consistent with claim discipline.
- `docs/assessment-intake.html` — browser-local scope brief; explicit next-step question ("discovery only / fixed-scope quote / bounded review / procurement or budget owner can be involved") that separates research from buying intent; output goes only via `mailto:info@clinicops.dk`. No endpoint, no analytics. Good for privacy; means no measurable funnel.

## 3. Contradictions and inconsistencies

1. **Flagship offer identity is not single.** `docs/services.html` and `BUSINESS_THESIS.md` say the flagship is the Regulatory Change Integrity Review. `offers/cash-entry-service-ladder.md`, `sales/first-pilot-scope-template.md`, `sales/standard-pilot-preflight.md`, the buyer playbook and the activation envelope all make the **Class III Transition Map Pilot** the sole default DO NOW and the only thing the delegation envelope covers. `sales/integrity-gate-pilot.md` defines a third (Integrity Gate, its own envelope), `05_CLIENT_DELIVERY` and `04_GROWTH/CLIENT_ACQUISITION_ENGINE.md` a fourth ("Transition Intelligence Scan"), Gumroad copy a fifth ("Transition Intelligence Assessment"). The positioning file is stated to win, but the sales/delivery machinery was not re-based to it.
2. **E4 is implied but not evidenced.** `CHANGELOG_AND_NEXT.md` says to "move E4 -> E6+", implying E4 exists; EXP-001 result is "pending"; growth docs say public state is E1. Do not treat the changelog phrase as an E4 record.
3. **Activation gate cannot pass today.** The envelope requires "approved standard commercial terms", a "pre-approved standard", and a named qualified reviewer before kickoff. No price, terms document, or reviewer roster exists in the repo. Preflight would return NON-STANDARD - NOT ACTIVATED for any real buyer.
4. **Danish route vs demand claims.** `BUSINESS_THESIS.md` keeps Danish PV and Danish linguistic validation as "demand-evidenced" secondary entries, and the founder is Denmark-based, yet Danish-domiciled organisations are barred from cold outreach ("public posting only"). The repo defines no compliant channel to reach them (inbound, warm intro, events); `global-sales-swarm.json` S24 hedges with "non-Danish cold-email or partner intro".
5. **Volume plan vs ceiling and doctrine.** The swarm targets 99 net-new opportunities across 33 cells; the 15/day ceiling and "3-5 high-information conversations over 100 low-context messages" (`revenue/CLAUDE_HANDOFF.md`) point the other way. It is not a breach (99 fits within ~7 send-days) but the plan measures leads, not conversations, and predates the E-ladder emphasis.
6. **Stale entry points vs narrowing.** `assessment-intake.html` still offers TrialOps, QMS, Clinical AI, Lab, Clinic Operations workstreams that `BUSINESS_THESIS.md` says are archived from public architecture. Presets keep the broad lanes live on an intake page.
7. **State-of-record ambiguity.** `AGENTS.md` and `revenue/CLAUDE_HANDOFF.md` tell agents to read `AGENT_STATE.md` first; that file is now a "DRAFT PROPOSAL - not applied to live main" index and every `00_STATE/` shard is labelled unreconciled. The actual current state cannot be confirmed from this checkout.
8. **Founder-personal vs AI-run.** Intake page promises briefs "answered personally" by the founder; AI-COMPANY-001 and the delegation envelope aim at founder-independent execution. Both cannot be the response model; today only the founder-personal one is real, and founder-independence is explicitly unproven.
9. **Two discovery ledgers, both empty.** `03_OPERATIONS/CUSTOMER_DISCOVERY_LEDGER.md` (blank template) and EXP-001 in `experiments/` both say results pending, while `revenue/CLAUDE_HANDOFF.md` asks for outcomes to be logged in the experiment ledger. No sanitized aggregate learning has been committed for sends already made.
10. **Private state leaking upward as unverifiable claims.** The 448-row master, 12 Sept sends, partner-meeting hold and empty HubSpot appear only as prose in a public-repo governance file. Useful, but no sanitized count (sent, bounced, replied, meetings) exists to support any E-level.

## 4. Gaps blocking customer discovery

1. **No recorded buyer-interaction evidence.** Zero logged E4/E5 events (no private evidence refs, no sanitized aggregates: sent / delivered / bounced / human-replied / meetings held). Without this the E-level cannot move and EXP-001 cannot be evaluated.
2. **No single named offer / ICP for discovery.** One flagship wording plus one target buyer segment (manufacturer vs AR vs consultancy) must be chosen and applied across intake, playbook, scope template and outreach. Currently five names and three buyer types in parallel.
3. **Private account working set not evidenced.** Revenue OS has never been run on real data per the repo; the 448-row master is not reconciled to the Revenue OS schema (segment, trigger, source_url, evidence_note, scores). No prioritised 3-5 conversation queue exists.
4. **No compliant route to Danish-domiciled prospects and no warm-intro/partner pipeline.** Public posting and inbound are the only permitted routes; there is no plan or metric for them (LinkedIn identity itself flagged as a P0 duplicate/stale defect, baseline P0-A/B/C unrecorded).
5. **No instrumented inbound path.** Scanner and intake are browser-local with no telemetry and mailto-only submission. Privacy-correct, but there is no approved way to know whether anyone used the scanner or started a brief; HubSpot is "essentially unused".
6. **Discovery ledger template unused and split.** Needs one private ledger with the captured fields (trigger, workaround, frequency, consequence, owner, objection, budget path) and a sanitized aggregate feed into the experiment ledger.

## 5. Gaps blocking a first paid delivery

1. **No price, no commercial terms, no scope-to-cash package.** Gumroad and offer docs have no prices; the activation gate requires "pre-approved standard terms". Decision needed (Ali, policy-level): first-scope price range, payment condition (upfront vs deposit vs PO), invoice/tax handling for a Denmark-based seller, liability wording.
2. **No named qualified human reviewer.** The review gate and preflight require a named, qualified reviewer assigned before kickoff; none is recorded, and no reviewer capacity/economics (hours, cost) are measured.
3. **Delivery chain built for the wrong flagship.** The preflight -> bundle -> review -> verify chain is tied to the Class III Transition Map; the flagship (Regulatory Change Integrity Review) has a separate Integrity Gate CLI and change-control packet with a different envelope. It is unclear which path a first paying buyer would go through and whether the same gates apply.
4. **Delivery-side data-handling not operational.** Real portfolio material must stay in "approved private storage"; the repo does not identify the store, access controls or NDA/DPA template. Delivery engine doc (`05_CLIENT_DELIVERY`) is a stub with no run-book.
5. **No design-partner policy in force.** The activation gate treats no/low-fee design-partner work as an exception needing a separate approved policy that does not exist. That removes the most likely early path (discounted first pilot) from the delegated workflow, so first-delivery scoping falls back on Ali personally.
6. **No repeatability/validation evidence.** Assets are PUBLIC-candidate or "available for bounded scoping"; none has an independent external user or completed case. Delivery effort is unmeasured, so pricing cannot be evidence-based.

## 6. Smallest honest next steps (recommendations only)

1. Decide and record one flagship name + one first ICP; align intake, playbook, scope template and delivery chain to it.
2. Reconcile the private master to Revenue OS schema privately; select 3-5 accounts; log every real conversation (or lack of response) with a private evidence ref; commit only sanitized aggregate counts to EXP-001.
3. Ali policy decision on price band, payment condition and a named qualified reviewer, so preflight can legitimately return ACTIVATED.
4. Define the compliant Danish route (inbound, events, LinkedIn public posting) with a metric.
5. Add a minimal consented, non-tracking way to count intake briefs received (mailbox tally is enough; no tracking deployment without Ali approval).
6. Do not raise any public wording above "pilot-stage / available for bounded review" until E4+ evidence and a completed external case exist.
