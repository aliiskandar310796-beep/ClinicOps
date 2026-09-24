# Statement of Work — TEMPLATE

Status: **template. Not a legal document until reviewed by a lawyer.** Fields in `[BRACKETS]` are filled per engagement. Fields marked `TO BE SET BY FOUNDER` are decisions, not defaults. No client named in this file is real.

Basis in repo: `docs/services.html` (Regulatory Change Integrity Review), `offers/class-iii-transition-map.md` (Transition Map Pilot), `CLAIM_RULES.md`, `docs/privacy-notice/index.html`.

## 1. Parties and reference
- Client: `[LEGAL ENTITY, ADDRESS, VAT ID]`   Client business owner: `[NAME, ROLE]`   Client qualified reviewer: `[NAME, ROLE]`
- Supplier: `[FOUNDER LEGAL NAME / TRADING NAME, CVR or NIF, ADDRESS, VAT ID]`
- SOW reference: `[ID]`   Date: `[YYYY-MM-DD]`   Engagement type (choose one): **A. Regulatory Change Integrity Review** (one change) / **B. Portfolio-scoped review** (portfolio export; Class III Transition Map Pilot format)

## 2. Purpose, in plain language
ClinicOps compares information you supply, and public registry information where reachable, against an approved source you name. It returns a list of places where records agree, disagree, or lack evidence, each linked to its source and given an owner. Your qualified people interpret the list and decide what to do.

## 3. What the client supplies (inputs)
See `data_intake_checklist.md`. In summary:
1. One approved/authoritative change or reference record (Type A) or a portfolio export (Type B).
2. A bounded list of downstream records/registers/documents ("surfaces") expected to reflect it, exported as CSV/XLSX/JSON or as file extracts.
3. A fixed evidence window: as-of date `[YYYY-MM-DD]`.
4. A named client regulatory owner able to answer source-authority questions within `[N]` working days.
5. Written confirmation that the client may share the material, and that it contains **no patient-identifiable data** and no credentials.

Bounds for this SOW: up to `[N]` sources, `[N]` surfaces, `[N]` rules, `[N]` records. (Engine limits for Type A cases are 50 sources, 100 surfaces, 250 rules, 250 changes; state tighter limits if wished.)

## 4. What is compared
- Type A: the approved value(s) of each declared field against the value observed on each declared surface, using the rules listed in Annex 1 (match to authority, required presence). Comparison is deterministic (same input, same output).
- Type B: portfolio rows segmented by actor role and registration path, with certificate timing, market/language and SS(C)P metadata, producing a triage work plan.
- Where document bodies are not supplied, comparison covers **metadata identifiers and dates only**. "Match" means those identifiers/dates align; it does not mean document contents were compared (CLAIM_RULES 7). Currency is compared on issue dates unless revision-number equivalence is shown (CLAIM_RULES 6).
- Public EUDAMED evidence is used only where reachable and is not a complete register audit (CLAIM_RULES 5).

## 5. Deliverable
A reviewer-approved bundle delivered through the agreed private channel:
- **Source-linked exception queue** with schema Source · Expected · Observed · Status · Evidence · Owner · Next Action · Closure. Status vocabulary: aligned · mismatch signal · missing evidence · conflicting evidence · unresolved · not applicable · requires qualified review.
- Human-readable report (HTML, Markdown), machine-readable JSON, and a manifest with SHA-256 hashes of input and outputs.
- Statement of sample design, retrieval limits, unresolved cases (CLAIM_RULES 8).
- One review call of up to `[N]` minutes, and a closure record (`closure_record_template.md`).

Delivery target: `[N]` working days after the client's intake is accepted as complete. One round of factual corrections is included; corrections are treated as new evidence, not silent overwrites.

## 6. Out of scope
- Any regulatory, legal, clinical, safety or compliance determination, including whether a device, certificate, SS(C)P or transition is compliant.
- Replacing the client's RA/QA staff, or a RIM/QMS/PLM/ERP system; entering or editing data in client systems.
- Complete public-register audit; retrieval of documents not supplied; translation; clinical or specialist review (available only as a separately scoped, independent introduction).
- Ongoing monitoring (separate agreement, only if a completed review shows recurrence).
- Any statement about manufacturer negligence. Findings describe record/document-operation state, not fault.

## 7. No regulatory determinations
Outputs are structured review work. Priority scores, if present, are operator triage only and are not a risk, compliance or legal score. The client's qualified team owns every interpretation and decision. Outputs must not be relied on externally (e.g. in submissions or to a notified body) before the client's own qualified review.

## 8. Data handling
- Client material is processed only for this SOW, in access-controlled private storage; never placed in the public repository, public GitHub Pages or public CI.
- The public site tools run in the browser and send nothing; this engagement is different: files the client sends by `[approved channel]` are processed by Supplier on `[Supplier device/storage — to be named]`.
- Retention: source files and working copies deleted `[N days — TO BE SET BY FOUNDER]` after closure or on written request, whichever is earlier. Delivered bundle and manifest kept `[N] — TO BE SET BY FOUNDER; suggest matching the invoice/bookkeeping retention need only for the invoice, not for client data]`. Deletion confirmed in writing (closure record).
- Sub-processors: `[none / list]`. AI-assisted tooling: `[state whether any client content is sent to a third-party AI service; default: none]`.
- GDPR: processing of client contact details and business material as described in the privacy notice. No special-category data is requested. If the client sends personal data by mistake, Supplier stops, tells the client and deletes it. `[Data-processing terms/DPA — LAWYER REVIEW: needed or not]`

## 9. Acceptance
Delivery is accepted when (a) the client confirms receipt of the reviewed bundle, and (b) the criteria in Annex 2 are met. If the client raises no written objection within `[N]` working days of delivery, it is deemed accepted. A valid objection identifies a deliverable that departs from this SOW; disagreement with a finding's interpretation is not a defect, since interpretation is the client's.

## 10. Fees and payment
- Fee: `[TO BE SET BY FOUNDER]`. The repo states no price. Suggested structure: fixed fee for the stated bounds; optional fixed add-on per extra `[N]` surfaces; a deposit or milestone payable before work starts (the pilot gate requires an upfront payment, a deposit/first milestone, or an accepted PO/signed commitment before activation); balance on delivery. Rationale: a fixed price makes the scope the client's decision and the pilot measurable.
- Currency `[EUR/DKK]`, VAT treatment and payment terms: see `invoice_and_terms_checklist.md`. Payment `[N]` days from invoice.

## 11. Liability, IP, confidentiality, law — LAWYER REVIEW REQUIRED
Placeholders only. Do not sign with these unreviewed.
- Limitation of liability: `[CAP — TO BE SET; e.g. tied to fees paid; LAWYER]`. Sole-trader unlimited personal liability and professional-indemnity insurance: `[LAWYER/INSURER]`.
- Exclusion of consequential loss and reliance on outputs: `[LAWYER]`.
- Confidentiality/NDA: `[mutual NDA reference or clause — LAWYER]`.
- IP: Supplier keeps tools/methods; client keeps its data and the delivered bundle for internal use `[LAWYER]`.
- Governing law and venue: `[TO BE SET — LAWYER]`. Term/termination `[LAWYER]`.
- Case-study/testimonial: none unless the opt-in clause in `pilot_offer.md` is separately signed.

## 12. Signatures
Client `[NAME / DATE]`   Supplier `[NAME / DATE]`

**Annex 1** Change/portfolio in scope, sources, surfaces, rules `[FILL]`.
**Annex 2** Acceptance criteria `[FILL: e.g. all declared surfaces processed or listed as unresolved; every finding has status, evidence link, owner; reviewer attestations complete; hashes verify]`.
