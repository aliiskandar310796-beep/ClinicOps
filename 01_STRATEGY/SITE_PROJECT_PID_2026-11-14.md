# ClinicOps website: project initiation document (2026-11-14)

Status: PROPOSED. Built on branch `feat/site-restructure-clinical-operations`. Not merged until the owner confirms Decision D1 below.

Method: PRINCE2 7 structure (business case, stages, tolerances, management by exception), with PMP vocabulary where it is clearer (scope baseline, risk register, lessons learned). PRINCE2® is a registered trademark of PeopleCert. No accreditation is claimed.

## 1. Why this project exists

Owner feedback, 2026-11-14: the site has no red thread, eCOA is hard to find, the front page does not read as "Danish clinical operations", the structure feels artificial, and the copy carries traces of machine writing.

Findings from the review that followed:

- The homepage described one lane (EU MedTech regulatory data integrity). eCOA, the newest and most substantial tool, was one entry in a long tool list.
- Navigation labels described internal products, not the visitor's problem.
- Copy repeated the same abstractions (deterministic, fail-closed, reconciliation, surfaces, reviewer-ready) and the same "not X but Y" sentence shape. Boundary and privacy lines were duplicated across pages. The voice switched between "ClinicOps" and "I".
- Some sentences made claims without a source ("seven systems", "no company does one often enough", "every PV team re-derives one").

## 2. Business case

One front door for a sole practitioner whose real work spans three areas. A visitor should know within one screen what is offered, which tool is free, and what to do next. Success is measured by the existing conversion-path contract and by qualitative review, not by traffic claims.

## 3. Scope baseline

In scope: homepage, primary navigation and footer, tools page, plain-language rewrites of the pages named in the copy audits, contract tests that pin the new identity.

Out of scope: new tools, new regulatory claims, outreach, LinkedIn changes, any change to the browser-local privacy model.

## 4. Decisions

| ID | Decision | Owner | Status |
|---|---|---|---|
| D1 | Reverse the 2026-09-18 positioning (MedTech data integrity as the only identity). The front door becomes clinical operations support from Denmark with three named lanes: eCOA, medical device records, Danish language and pharmacovigilance. Inner MedTech pages keep their wording. | Ali | Awaiting confirmation. Built on his 2026-11-14 instruction. The old document is kept and carries a dated addendum. |
| D2 | `alibaba/page-agent` is not shipped on the public site. It is an in-page agent that needs an external LLM endpoint. That would send page content off the browser, contradict the "nothing you type is uploaded" statement, and add an AI layer the owner wants removed. It could be used privately as a QA driver if an endpoint and key are supplied. | Ali | Decided here, open to override. |
| D3 | "Danish" is the front-door framing, in line with the owner's instruction. The standing operating rule warns against over-leaning on Danish. The compromise: Danish is in the headline and one lane, while the other two lanes are written for an international audience. | Ali | Flag for review. |
| D4 | Homepage speaks in first person ("I help"). The About page already does. | Ali | Flag for review. |

## 5. Stages and work packages

| Stage | Work package | Product | State |
|---|---|---|---|
| 1 Direction | Audit of structure and copy | Two audit reports | Done |
| 2 Structure | Homepage, navigation, tools page | New `docs/index.html`, nav, `docs/tools.html` | Done on branch |
| 3 Voice | Plain-language rewrites | 24 sentence-level replacements across 17 pages | Done on branch. Remaining pages listed in section 7 |
| 4 Assurance | Contract tests, validators, browser journeys | Test suite and CI | Gates listed in the PR |
| 5 Release | Owner review, merge, deploy | Merged PR, live check | Waits for D1 |

## 6. Tolerances and risks

Tolerances: no new claim without a registered source; no change to approved professional wordings; sitemap stays at or under 40 URLs; every gate in CI stays green.

| Risk | Likelihood | Effect | Response |
|---|---|---|---|
| Owner rejects the broader identity | Medium | Revert homepage and nav commits | Work is on a branch; the old document is preserved |
| Plain rewrite loses a precise regulatory meaning | Low | Misleading page | Each rewrite keeps the original object and verb; owner reviews the diff |
| Remaining pages still read as machine-written | High | Owner's complaint persists | Section 7 lists them; do them next |
| Visual judgement is mine alone | High | "Does not look artificial" is not proven | Owner review of screenshots before merge |

## 7. Open items

- Rewrite the remaining pages from the audit: tool pages beyond the sentences already changed, and the longer sections of about, services and denmark-market-access.
- Confirm the About-page claims (years of experience, degrees, named databases) match approved wording.
- Verify the quoted wording in claim CO-CLM-0012.
- Degree title: memory and the professional-claims gate differ. The gate wording is the one in use.
- The external EUDAMED canary check on PR #120 fails on a 429 from the source.

## 8. Lessons logged

- Contract tests that pin copy were the main cost of changing identity. Each pin now names the date and this document.
