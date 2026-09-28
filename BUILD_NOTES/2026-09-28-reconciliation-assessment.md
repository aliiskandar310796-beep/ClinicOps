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
