# ClinicOps Class III Transition Map

Status: **internal offer specification / validation stage**

## Job to be done

Turn a class III / implantable portfolio into a defensible transition work plan by separating legacy registration paths, MDR manufacturer registrations and system/procedure-pack records, then connecting each item to certificate timing, Basic UDI-DI readiness, SS(C)P operations and market-language document control.

This is **not** positioned as a compliance audit of EUDAMED and it does not allege that manufacturers have failed to link documents.

## Best-fit buyers

- EU authorised representatives managing many manufacturer portfolios.
- Manufacturers with multiple class III / implantable devices transitioning from directive-era certificates.
- Regulatory consultancies that need a white-label evidence/work-plan layer.
- Portfolio owners entering Denmark or another market where language/document-control work must be scheduled.

## Trigger events

- Certificate transition / expiry planning.
- Portfolio migration from a legacy registration path into MDR registration.
- Basic UDI-DI creation or reconciliation.
- SS(C)P upload / validation / translation workflow change.
- Market-language readiness review.
- AR onboarding or portfolio transfer.

## Inputs

Minimum useful portfolio CSV:

- manufacturer / legal entity
- actor role where known (MF / AR / PR)
- device / family label
- Basic UDI-DI, UDI-DI or EUDAMED DI where available
- legislation / registration path signal
- risk class
- certificate identifier, regime and expiry / transition date where known
- target markets / languages
- linked SS(C)P metadata if observed
- public evidence URLs and evidence date

Do not require every field before starting. Missing join keys are themselves useful work-plan items when recorded as unknown rather than guessed.

## Engine

Use `clinicops-portfolio-report` for deterministic segmentation and report generation. Feed only evidence-supported fields into the engine.

Core categories:

1. **Legacy-path manufacturer record** — transition discovery queue.
2. **MDR MF-role registration** — verify current portfolio/document-operating state without presuming a defect.
3. **PR-role system/procedure-pack record** — keep separate from ordinary manufacturer-device interpretation.
4. **Unresolved** — evidence gap requiring targeted human review.

## Deliverables

### 1. Portfolio transition map
For every row: registration-path category, evidence status, certificate timing, market/language relevance and next evidence/action step.

### 2. Priority work queue
Rank items by:
- dated transition/certificate pressure;
- class III / implantable relevance;
- Danish or other market-language need;
- identifier/join-key completeness;
- evidence confidence;
- degree of human regulatory judgement needed.

### 3. Evidence appendix
For each material conclusion: source URL/file, capture date, evidence class and limitation.

### 4. Management summary
Answer portfolio questions such as:
- How many items are still represented through a legacy registration path in the supplied/reachable evidence set?
- Which items have the nearest transition/certificate dates?
- Which records need Basic UDI-DI / certificate / SS(C)P evidence reconciliation before a work plan can be finalised?
- Which market-language document sets need coordinated review?

Always describe the population as the supplied/reachable portfolio evidence, not the entire public register unless full coverage has actually been established by another method.

## Free front door

The **EUDAMED Identifier Check** is a screening tool, not the paid product. Use it to explain structural identifier signals and collect the minimum input needed for a transition conversation.

The free layer should create a question:

> What does this identifier/registration path imply for the portfolio work plan?

The paid layer answers that question with evidence, context and accountable human judgement.

## Evidence-backed commercial bridge

Current claim IDs to use in discovery / deliverables only where their gate allows the intended use:

- `CO-CLM-0001` — Article 32 manufacturer duty-holder context.
- `CO-CLM-0004` — B-prefixed EUDAMED DI identifier structure.
- `CO-CLM-0005` — ClinicOps B-prefix operational derivation, explicitly labelled as derivation.
- `CO-CLM-0009` — MDCG 2026-4 manufacturer-upload / notified-body indication operating model.
- `CO-CLM-0010` — MDCG recommendation for pre-mandatory-use SS(C)P uploads by 27 February 2027, explicitly non-binding.

`CO-CLM-0002` is useful aggregate research context but must never be presented as a population rate.

## Non-negotiable boundaries

- Do not sell “we found your non-compliance” from public metadata.
- Do not call a B-prefix consequence a directly stated Commission SS(C)P rule.
- Do not interpret PR-role rows as ordinary MF-role manufacturer registrations.
- Do not call the 27 February 2027 MDCG recommendation a statutory Article 32 deadline.
- Do not imply full-register API coverage.
- Do not infer certificate expiry, market placement or language obligation when the evidence does not support it.

## Validation experiment

Before building more product surface, validate the offer in three portfolio conversations.

Success signal: the buyer supplies or discusses a portfolio list and asks for a scoped transition work plan, not merely general regulatory advice.

Failure signal: conversations consistently remain at generic EUDAMED education and no buyer is willing to share a portfolio or pay for human-reviewed prioritisation.

Only after that signal should ClinicOps invest in richer dashboards, integrations or automated account ingestion.
