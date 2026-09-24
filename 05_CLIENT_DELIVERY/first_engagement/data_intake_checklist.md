# Data Intake Checklist — TEMPLATE

Use before any client material is opened. Tick per engagement: `[ ]`. Nothing here refers to a real client.

## A. Gate before receiving anything
- [ ] SOW signed and activation condition met (upfront payment, deposit/first milestone, or accepted PO/signed commitment).
- [ ] Buyer confirms in writing authority to share the material.
- [ ] Buyer confirms: no patient-identifiable data, no credentials, no third-party confidential data they cannot share.
- [ ] Private storage location created and approved (not the public repo, GitHub Pages or public CI). Location: `[ ]`
- [ ] Named human reviewer assigned and qualified (ClinicOps side): `[ ]`  Client regulatory owner: `[ ]`
- [ ] Transfer channel agreed (encrypted/access-controlled): `[ ]`

## B. Type A — Change Integrity Review inputs
- [ ] Approved/authoritative source (what it is, version, date, owner) — becomes `controlled_sources`.
- [ ] The change: field, old value, new value, approving source — becomes `changes`.
- [ ] List of downstream surfaces expected to reflect it (EUDAMED, UDI data, certificates, SS(C)P, declarations, labels, IFUs, controlled documents, language versions), each with an evidence reference — becomes `surfaces`.
- [ ] Which fields must match authority / be present on which surface — becomes `rules`.
- [ ] Evidence window as-of date; export dates for each surface.
- [ ] Identifier conventions (Basic UDI-DI, UDI-DI, certificate numbers, revision vs issue-date semantics).
- [ ] Sizes within limits: <=50 sources, <=100 surfaces, <=250 rules, <=250 changes, text fields <=10,000 chars, file <=5 MB.
- [ ] `data_governance` flags can truthfully be set: `contains_patient_identifiable_data: false`, `processing_authorized: true`, `source_population_approved: true`.

## C. Type B — Portfolio inputs (`examples/portfolio_intake_template.csv`)
Columns: company, device, actor_role (MF/AR/PR), registration_type (legacy/MDR), basic_udi_di, certificate_expiry, danish_market, linked_sscp, source_url, notes.
- [ ] Unknown values entered as `unknown` or blank, never guessed.
- [ ] Actor role recorded per row; PR (procedure pack) rows kept separate.
- [ ] Evidence URL and evidence date per row where known.
- [ ] Extra client columns are tolerated but not relied on.

## D. Quality checks on receipt
- [ ] File opens; encoding and date formats consistent; duplicates identified.
- [ ] SHA-256 of each received file recorded in the closure record.
- [ ] Spot-check: three records traced back to their source.
- [ ] Questions to client logged; unanswered items stay "unresolved" rather than assumed.
- [ ] Anything unexpected (personal data, credentials, out-of-scope confidential files): stop, notify client, quarantine, delete per SOW section 8.

## E. Exclusions confirmed with client
- [ ] No regulatory determination requested. [ ] No document-body comparison unless files supplied. [ ] Public-register screening is not a full audit.
