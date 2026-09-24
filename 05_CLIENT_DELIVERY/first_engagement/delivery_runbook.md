# Delivery Runbook — first paid engagement (TEMPLATE)

Every command below exists in `pyproject.toml` `[project.scripts]` and was checked against `src/clinicops_os/*cli.py`. Run all client work outside the repo checkout (private folder `$ENG`, for example `~/private/engagements/<ref>/`), never inside a git-tracked directory. Install once with `pip install -e .` in a virtualenv.

Two tracks share the same stages:
- **Track A, Change Integrity Review** (flagship in `docs/services.html`): case JSON -> `clinicops-integrity-*`.
- **Track B, Class III Transition Map Pilot** (default `DO NOW` entry in `offers/cash-entry-service-ladder.md`): portfolio CSV -> `clinicops-pilot-*`.

Known gap: no tool converts client exports into a Track A `case.json`; this is manual/analyst work (model on `examples/integrity_gate_case.example.json`). Budget time for it.

## Day 0 — Signed SOW
1. Countersigned SOW filed in `$ENG/00_contract/`. Payment activation condition met (`invoice_and_terms_checklist.md`).
2. Create `$ENG/{01_received,02_work,03_bundle,04_review,05_delivered}`; restrict permissions (`chmod -R go-rwx $ENG`).
3. Send `data_intake_checklist.md` to client. Track B only: complete an activation record from `examples/standard_pilot_preflight.example.json` (fill honestly; the gate refuses false values) and run
   `clinicops-pilot-preflight $ENG/00_contract/activation.json` (exit 2 = not activated; do not proceed).

## Day 1–2 — Intake
4. Receive files into `01_received`; record `sha256sum` of each. Apply checklist section D.
5. Track B: `clinicops-portfolio-validate $ENG/01_received/portfolio.csv`. Exit 2 = blocking errors; return to client. Warnings stay visible in the report.
6. Track A: build `02_work/case.json`; check `clinicops-integrity-gate` will accept it (its safety preflight rejects missing `data_governance`, over-limit sizes, non-finite numbers).
7. Intake accepted as complete -> confirm in writing; the delivery clock starts.

## Day 3–4 — Generate
8. Track B: `clinicops-pilot-bundle $ENG/01_received/portfolio.csv $ENG/03_bundle YYYY-MM-DD` -> `client_report.html`, `portfolio_report.md`, `portfolio_report.json`, `intake_diagnostics.md`, `manifest.json`.
   Optional: `clinicops-portfolio-report <csv> YYYY-MM-DD` / `clinicops-portfolio-json <csv> YYYY-MM-DD` for stdout views.
9. Track A: `clinicops-integrity-gate $ENG/02_work/case.json $ENG/03_bundle` -> `integrity_report.{json,md,html}` and `manifest.json`.
10. Dry run first if the flow is unfamiliar: `clinicops-pilot-dry-run <preflight.json> <review.json> <portfolio.csv> <outdir>` using the synthetic examples in `examples/` (never real data).

## Day 5–6 — QC and human review
11. Automated QC:
    - Track B: `clinicops-pilot-verify $ENG/03_bundle $ENG/01_received/portfolio.csv`
    - Track A: `clinicops-integrity-verify $ENG/03_bundle $ENG/02_work/case.json`
12. Manual QC (reviewer): every finding has source link, expected, observed, status from the bounded vocabulary, owner, next action; no wording implies compliance/non-compliance or manufacturer fault; "match" language limited to metadata; sample design, retrieval limits, unresolved cases stated; anonymisation status stated (CLAIM_RULES 1–8); no internal notes left; spot-check five findings against source files.
13. Reviewer attestations:
    - Track B: `clinicops-pilot-review-prepare activation.json $ENG/03_bundle > $ENG/04_review/review_record.json`; the reviewer sets each attestation true only after doing the step and fills `review_completed_on`; then `clinicops-pilot-review-gate activation.json $ENG/04_review/review_record.json $ENG/03_bundle`.
    - Track A: `clinicops-integrity-review-prepare $ENG/03_bundle > $ENG/04_review/review_record.json`; reviewer fills reviewer, role, date, `review_minutes`, decision, every `finding_dispositions` value, and attestations; then `clinicops-integrity-review-gate $ENG/04_review/review_record.json $ENG/03_bundle`.
    - Then re-run Track A verify with `--require-review` for release status. Any edit after review requires regenerating and re-reviewing (hashes bind the record to the manifest).
    `review_minutes` also feeds the pilot success metrics (`pilot_offer.md`). Gate exit 2 = do not release.

## Day 7 — Private render and delivery
14. `client_report.html` / `integrity_report.html` are self-contained (no network resources), so the private render is simply the file: open it locally from `03_bundle`, review in a browser with network off if wished.
    Note: `render_public_demo.py`, `render_examples.py` and the `docs/` site are public paths; never point them at client data.
15. Copy final files to `05_delivered/`; send by the approved access-controlled channel (not public hosting, not public CI). Record recipient, time, file hashes.
16. Review call: what is strong enough to act on, what needs verification, owners, exclusions.

## Day 8–10 — Corrections and closure
17. Client corrections logged as new evidence; if outputs change, re-run steps 8–13 (new bundle, new review).
18. Acceptance per SOW section 9. Complete `closure_record_template.md`. Send invoice/final milestone.
19. Purge (below) on the retention date in the SOW; record in the closure record.

## Purging client data
There is no purge script in the repo. Manual procedure:
1. Confirm retention date reached or client requested erasure, and no legal hold.
2. List everything: `$ENG` tree, email attachments, downloads, editor/temp files, shell history lines with client paths, backups, cloud-sync copies.
3. Delete `01_received`, `02_work`, `03_bundle`, `04_review`, and `05_delivered` per SOW (keep only what the SOW says, e.g. manifest hashes and the closure record with no client content). `rm -rf` is not secure erase on SSD/cloud; use full-disk encryption on the working device so deletion plus key protection suffices, and delete provider-side copies and trash.
4. Verify: search the machine and mailbox for client name, file names and hashes.
5. Confirm deletion to the client in writing; date and method into the closure record.
6. Confirm nothing entered the repo: `git status` and search for the client name in the repository.

## Do not
Invent commands; run client data through CI or public Pages; skip the review gate; promise savings not measured in the engagement.
