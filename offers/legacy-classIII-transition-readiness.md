# Legacy Class III Transition Readiness Scan

Status: internal offer specification — not a legal assurance or published price sheet.

## Buyer
- EU authorised representatives with multi-manufacturer portfolios.
- Regulatory consultancies managing transition work across multiple manufacturers.
- Class III / implantable-device manufacturers with legacy registrations and EU market-language obligations.

## Customer question
Which devices should enter the transition work queue first, what evidence supports that prioritisation, and what must still be verified before action?

## Inputs
### Public-source baseline
- EUDAMED public registration metadata available through demonstrably reachable interfaces.
- Actor role and identifier structure.
- Public certificate / manufacturer / SS(C)P metadata when available.

### Client-supplied enrichment, when available
- Certificate expiry / transition dates and certificate identifiers.
- Market-country list.
- Current Basic UDI-DI / UDI-DI mapping.
- SS(C)P master and translation inventory.
- Notified-body and internal document-control status.

## Outputs
1. **Portfolio status map** — separates legacy-style registrations, MDR MF-role registrations, and PR-role system/procedure-pack records.
2. **Transition queue** — prioritised list based on certificate timing, regulatory context, evidence completeness, and market relevance.
3. **Evidence ledger** — source, date checked, observation, limitation, and unresolved question for every material finding.
4. **SS(C)P readiness view** — identifies where an SS(C)P workstream is relevant without treating missing public metadata as a compliance allegation.
5. **Market-language matrix** — when client market data is supplied, maps document-language work without assuming language versions share a revision scale.
6. **Human-reviewed action list** — separates machine-detectable signals from regulatory judgement requiring accountable review.

## Standard exclusions
- No claim of complete public-register coverage.
- No legal opinion on MDR transition eligibility.
- No allegation of manufacturer or notified-body non-compliance based solely on public metadata.
- No assumption that a B-prefixed identifier alone establishes every downstream SS(C)P consequence.
- No certificate-expiry inference when the certificate evidence has not been supplied or independently verified.

## Evidence standard
Every externally reusable statement should reference a ClinicOps claim-registry ID or a client-specific evidence record. Derived and observed claims must carry their limitations. Time-sensitive claims must be re-verified after their review date.

## Delivery shape
### Phase 1 — screening
Machine-assisted portfolio normalisation and signal extraction. Fast, reproducible, low-cost.

### Phase 2 — judgement
Human review of priority rows, source reconciliation, regulatory context, and unresolved questions. This is the defensible paid layer.

### Phase 3 — work plan
Optional implementation queue for SS(C)P, UDI, language/document-control, certificate, or registration workstreams.

## Pilot success criteria
A pilot is successful if the buyer can answer, with evidence:
- how many portfolio rows require transition investigation;
- which five to ten rows should be reviewed first and why;
- what evidence is missing before a regulatory conclusion can be made;
- what work can be automated safely and what requires professional judgement.

## Product principle
Sell the scan as the front door. Sell the accountable judgement and work plan.
