# Grok reconciliation proposal: assessment and implementation

Date: 2026-09-28. Engineering assessment, not a regulatory or commercial verdict.

| Dimension | Assessment |
| --- | --- |
| Strategic fit | 8/10: directly supports approved source → records → exceptions → review. |
| Supplied implementation readiness | 3/10: illustrative scaffold with unsafe rendering, unvalidated inputs, source authority bypass, false empty alignment, omitted checks and placeholder hashing. |
| Value of copying unchanged | 2/10: current scanner already implements most proposed browser/import/workbench features. |
| Technical feasibility | High for browser-local structured evidence reconciliation; no backend required. |
| Buyer value / repeatability / scalability | Unknown; deployment and internal tests are not external validation. |

## Decision and delivered scope

Extend the existing `docs/integrity-scanner.html` on its existing GitHub Pages deployment. No second site, hosting migration, account service or data upload pipeline.

- Add an evidence-matrix mode accepting the proposal's source/surfaces/observations shape.
- Optional explicit `scope` lists field/surface pairs; without scope every declared field is checked on every declared surface. Missing observations remain missing, never silently disappear.
- Approved source values govern comparison. A conflicting observation-level expected value is a conflict, not an override.
- Preserve all findings and all supplied observation evidence. N/A needs explicit scope exclusion and reason. Matching values without provenance need review.
- `exact` is the default; `trim`, `relaxed` and `qualified` are explicit per-field rules. Qualified mode does not infer translated or clinical equivalence.
- Shared dependency-free browser/Node rules module, version 1.0.0. Avoid independent Python/TypeScript copies with divergent behavior.
- JSON export preserves comparison input and rules; full SHA-256 input and packet fingerprints. Input object keys are sorted recursively, array order remains material, JSON is UTF-8. To verify, remove only `packet_sha256`, canonicalize and hash. This is this module's canonical format, not a claim of RFC 8785 interoperability.
- Human-readable HTML report; formula-safe CSV with closure fields appended after existing columns; raw JSON values remain unchanged.
- Closure requires an owner and evidence reference; original machine status is retained. Review fields are self-reported, local, and unauthenticated. They do not prove qualified review or constitute regulatory release authorization.
- Fix stale result export after input edits/failed runs and outer-space loss in exact single-change checks.

## Technical validation

Local: 268 Python tests pass; 14 new Node tests pass; Ruff, metadata, internal links, public shell and public-copy gates pass. Synthetic 1,000-observation test is below 2 seconds in this environment (not a browser performance guarantee).

CI additionally runs the existing scanner journey, full scanner journey, and the new matrix/closure/fingerprint journey against the checked-out source before production deployment. Exact release results are recorded by GitHub Actions and the pull request, not assumed here.

## Boundaries and backlog

The matrix compares entered structured values. It does not fetch EUDAMED, parse arbitrary regulatory document bodies, verify a cited file/hash, choose legal source authority, authenticate reviewers, or establish equivalence between translations. A hash is not a signature, identity check or proof that evidence is true. Current CSV/XLSX portfolio rules retain their existing grouping semantics; use explicit matrix scope where field applicability differs by record.

The optional multi-user backend and authenticated audit trail are deferred: they add privacy/security/operating cost without established demand. No automated regulatory conclusions or public enrichment were added. Specimens are fictional. The supplied proposal's Sprint 5 acceptance criteria were incomplete.

## Smallest external validation

Two independent intended RA/QA users should complete a bounded real change without developer rescue. Record preparation time, missing/mismatch agreement with their reference review, useful handoff, and willingness to pay. Keep case evidence private. The repository's scalability gate additionally requires three independent cases across two organisations/workflows and measured marginal effort. Until then, the status is technically tested for defined cases, pilot-stage commercially.

## Operations

Public code only; no client data. Source changes use a feature branch and PR; production deploy remains gated on the exact main SHA's CI. Rollback is a reviewed revert of this PR followed by the same gates. Release Sentinel owns technical handoff; the next buyer-value test belongs to Customer Discovery and the accountable qualified reviewer.

## CodeQL DOM-XSS alert on the workbook XML reader

CI's CodeQL scan flagged a DOM-based cross-site-scripting risk on the workbook XML reader (`parseXLSX`/`extract` in `docs/integrity-scanner.html`, the client-side `.xlsx` importer for the portfolio-scan pane). This is pre-existing code, not part of this branch's diff; the branch's own CI run surfaced it. This session could not open the alert itself (GitHub API access is not enabled for this session), so the investigation worked from the source instead of the alert record.

Every render path downstream of the workbook reader — the sheet picker, the column-mapping panel, the exception queue, the results table/grid, and the HTML export — passes workbook-derived text through the file's single hand-written `esc()` function before it reaches `innerHTML`, and `esc()` escapes all five HTML-significant characters (`& < > " '`). CodeQL's default DOM-XSS query recognizes a small fixed list of sanitizer calls (e.g. `DOMPurify.sanitize`); a hand-rolled escaper is a well-documented source of false positives for that query, since the tool sees a taint flow into `innerHTML` and has no model telling it the flow was neutralized in between.

To settle this with evidence rather than argument, this session added `e2e/xlsx_xss_journey.mjs` and a new fixture (`e2e/fixtures/xss-payload.xlsx`, generated by a one-off script, not committed as a generator since it is a single fixed fixture) carrying three independent HTML/script payloads — one each in the sheet name, the header row, and a cell value. The journey uploads it, runs a scan, and asserts: the workbook still parses (a payload is data, not a parse failure); each payload reaches the visible page and the HTML export only as escaped text; no `<img>` element is ever created from any of them; no dialog fires (i.e. no `onerror` handler ever executes); and there are no page errors. All 12 assertions pass locally against the current source. Existing suites were independently re-run in this session, not merely trusted from the prior narrative: 268 Python tests, 14 Node reconciliation tests, and all three prior E2E journeys (18 + 133 + the matrix/closure journey) pass unchanged.

Conclusion: on the evidence available in this session, the alert is very likely a false positive against `esc()`'s escaping, not an exploitable gap — but that conclusion should be confirmed by whoever can open the alert in GitHub's UI, since this session cannot read the CodeQL alert's exact rule ID or flagged line to dismiss it directly. If it is confirmed a false positive, dismiss it in GitHub's UI as "used in tests" is wrong; use "false positive" with a link to this note and the new journey. If the reviewer's read differs — for example if the real flagged sink is somewhere this session's read of the code missed — the new journey's fixture and structure should make it straightforward to extend with the specific case.
