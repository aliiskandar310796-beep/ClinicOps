# ClinicOps operating changelog

## 2026-11-14
- Added the eCOA Delivery Workbench (`docs/ecoa-delivery-workbench`) as an adjacent, browser-local sanitized prototype: instrument-language plan, protocol-vs-specification schedule comparison, testing skeleton, risk and issue registers, change-surface mapping, tolerances, highlight report; PRINCE2-structured; 18 sources verified against origin on 2026-11-14.
- Added Node rule tests (30), a pytest contract test (9), and a Playwright journey (111 checks) to CI.
- Fixed during testing: calendar-impossible dates (for example 30 February) were accepted by `isoDate`.

## 2026-09-09
- Initialized public GitHub operating repository.
- Encoded 8 Sep headline reversal into standing claim rules and claim guard.
- Added a versioned claim registry with evidence class, allowed use, limitations, review dates and supersession state.
- Added publication-pack generation so approved claims carry their limitations and source ledger into downstream work.
- Added opportunity scoring that rewards evidence, leverage, defensibility and reuse while penalizing risk and maintenance burden.
- Added portfolio transition report generator for AR/manufacturer work-plan screening.
- Added a deterministic sanitized portfolio report fixture and CI drift check.
- Refactored the EUDAMED API canary into a testable module; ordinary CI uses no live EUDAMED network calls.
- Added multi-agent collaboration contract so ChatGPT/Claude/other assistants can coordinate through durable shared state.
- Added the internal Class III Transition Map offer specification and buyer-validation criteria.
- Raised the verified CI baseline to 30 passing tests plus Ruff, claim-registry audit, report-fixture check and public-copy claim gate.
- Isolated GitHub Pages enablement as the single tracked manual deployment dependency in issue #1.

## 2026-09-08
- Corrected initial SS(C)P-linking hypothesis after systematic class III census.
- Reframed commercial thesis from manufacturer diligence gap to legacy-to-MDR transition gap.
- Added API reachability and page-size limitations to publication constraints.
