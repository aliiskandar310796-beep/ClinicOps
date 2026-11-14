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

## 9. Viability and validation record (added 2026-11-14, stage 4 assurance)

PRINCE2 tests a business case as desirable, viable and achievable. Each is rated below with what supports it. Nothing here is rated higher than the evidence allows.

### 9.1 Options appraised

| Option | Verdict |
|---|---|
| A. Leave the MedTech-only front door | Rejected by the owner's 2026-11-14 feedback; eCOA stayed hidden. |
| B. Restyle only | Does not fix structure or the missing eCOA path. |
| C. Three-lane front door, tools as proof, plain copy (built) | Chosen. |
| D. Large-firm style (service menu, scale and "track record" claims) | Rejected. A one-person practice cannot evidence scale, and the claim gates ban those words. |

### 9.2 Benchmark of comparable practices (2026-11-14)

Sources read: Signant Health eCOA science consulting pages and brochure, ICON eCOA and outcome-measures pages, ProPharma eCOA services, Clario eCOA science overview, Oxford University Innovation COA services, Pure Global, Johner Institut, Freyr and Fang Consulting device-regulatory pages, eCOA project-manager job postings (IQVIA, Clario, Syneos, Alimentiv, Medable), Everest Group (2024) and IDC MarketScape abstracts on life-science buyer selection, and agency articles on B2B homepages.

What the evidence supports, and how the build uses it:

- Large eCOA firms win on scale (Signant cites 50+ in-house scientists). A one-person practice should not copy that; it should be specific and checkable. Used: problem-first headline, three named lanes, free tools placed before the engagement process.
- Job postings show the buyer's day-to-day words: licensing, translation vendors, migration, user acceptance testing, timelines, risk. Used in the eCOA lane, limited to what the workbench actually covers (no UAT or vendor-selection claim, because it has neither).
- Everest's abstract says pharma buyers weight domain expertise and MedTech buyers lean to strategic partners; IDC stresses vetting references and project-management skill. Only abstracts were available. Used as direction, not as proof.
- Agency pages cite conversion and trust statistics. Their sources are weak and mostly vendor marketing, so none is relied on or quoted on the site.
- Practices lead with outcomes and named clients. ClinicOps cannot name clients. Substitute: inspectable tools, a named person with approved wording, stated limits, and a free first step.

### 9.3 Cold-read test

Three independent reader agents each read only the homepage text as a different buyer: an eCOA lead at a sponsor, a device regulatory manager, and a Danish pharma safety lead. These are simulated readers, not real buyers, and cannot replace interviews.

| Reader | Clarity | Credibility | Relevance | Would email |
|---|---|---|---|---|
| eCOA lead | 7 | 4 | 6 | Maybe |
| Device RA manager | 6 | 4 | 6 | Maybe |
| Danish safety lead | 7 | 5 | 6 | Maybe |

Fixed after the test: filler lines ("go wrong quietly", generic stage names), an unsupported Swedish and Norwegian review claim (now "review the Danish myself"), three repeats of "from Denmark", no explanation for the breadth of lanes (added the shared habit), no answer to the one-person risk (added), literature monitoring and DHPC tools not linked from the Danish lane, no Danish text on a page that sells Danish review, no LinkedIn link.

Not fixable by copy, raised by all three readers: no evidence of experience. Missing items, each needing the owner's approval before use: years of experience, eCOA platforms worked with, anonymised outcomes, current availability, indicative rate, confidentiality and insurance statements, a photo. Until some of these are approved, credibility stays the weak point.

### 9.4 Quality criteria and evidence

| Criterion | Test | Result |
|---|---|---|
| Visitor can state what is offered in one sentence | Cold read, 3 readers | All three stated it correctly |
| eCOA reachable in one click from home | Nav, hero button, lane, tool list | Pass |
| No claim outside approved wording | `validate_professional_claims.py`, claim gate | Pass |
| No data leaves the browser | Playwright network audits on the tools | Pass |
| Accessibility | axe serious/critical gate, all key pages | Pass |
| Mobile layout | 320, 390, 1024 and 1440 px checks | Pass |
| Contract tests pin the new identity | `test_strategic_invariants.py`, positioning contract | Pass |

### 9.5 Rating

- Achievable: validated. Built, tested and reviewable.
- Desirable: partly supported. Buyer vocabulary and role demand exist; no real buyer has been interviewed.
- Viable: not validated. Commercial return is an assumption until the benefits review below.

### 9.6 Benefits review (proposed, owner to confirm)

The site sets no analytics, by policy, so measures use what is already visible:

- Enquiries by email and scope form that arrive after merge, and which lane each names.
- GitHub repository traffic (page views, referrers) for the 14-day window, read by the owner.
- A repeat of the cold-read test, plus two or three real buyers asked to read the page for five minutes.

Review date: 2027-02-14, about 13 weeks after release. Suggested tolerance: if no qualified enquiry names any of the three lanes by then, treat the broader front door as unproven and revisit D1. The numbers are the owner's to set.
