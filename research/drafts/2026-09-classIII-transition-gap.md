# Draft research note — the class III transition gap hiding in public EUDAMED data

**Status:** internal draft; not published. Evidence date: 9 September 2026.

## Headline finding

In a ClinicOps systematic sample drawn from the demonstrably reachable portion of the public EUDAMED device API on 8 September 2026, 98 distinct class III records were identified after deduplication. Of those sampled records:

- 70 were legacy registrations;
- 11 were PR-role system/procedure-pack records;
- 17 were MF-role MDR manufacturer registrations.

All 17 sampled MF-role MDR manufacturer registrations had linked SS(C)P metadata and were marked validated in the sampled public data.

**This is not a population rate and not a full-register audit.** It is a systematic sample inside the API frame ClinicOps could demonstrate was reachable on the observation date. [CO-CLM-0002]

## Why this matters

The first interpretation of the research was wrong. A convenience scan had mixed together class IIa/IIb devices, legacy registrations, and system/procedure-pack records. That made the public record look like a broad SS(C)P-linking diligence problem.

The class- and actor-role-aware census did not support that framing. The discarded claim — that manufacturers are broadly failing to link SS(C)Ps for MDR class III devices — remains explicitly rejected in the ClinicOps claim registry. [CO-CLM-0003]

The more useful question is therefore not:

> Which manufacturers failed to link an SS(C)P?

It is:

> Which portfolio items are still represented through a legacy registration path, and what evidence and timing determine the work required when they move into the MDR operating model?

That turns a public-data anomaly hunt into a transition work-plan problem.

## Regulatory and operational context

Under MDR Article 32(1), the manufacturer draws up an SSCP for implantable and class III devices, subject to the Article 32 exclusions. [CO-CLM-0001]

For legacy-device identification in EUDAMED, a B-prefixed EUDAMED DI is part of the legacy registration model and stands in place of the MDR Basic UDI-DI identifier concept for that legacy registration. [CO-CLM-0004]

ClinicOps uses that B-prefix as a **screening signal**, not as a standalone legal conclusion about every downstream SS(C)P consequence. The operational consequence is treated as a derivation from identifier structure, Article 32 and the EUDAMED SS(C)P operating model, not as a directly quoted Commission rule. [CO-CLM-0005]

The European Commission states that the Actor, UDI/Device, Notified Bodies & Certificates and Market Surveillance modules have been mandatory since 28 May 2026.

MDCG 2026-4 describes an evolving SS(C)P operating model in which manufacturers are expected to manage master versions and translations in EUDAMED, with notified bodies indicating validated SS(C)P(s) against relevant Basic UDI-DI(s). It described Production deployment of the revised functionality as planned for October 2026. [CO-CLM-0008; CO-CLM-0009]

For devices placed on the market before mandatory use of the UDI/Device module, MDCG 2026-4 recommends manufacturers upload SS(C)Ps as soon as possible and no later than 27 February 2027, while aligning timelines with notified bodies. This is MDCG guidance and must not be presented as a statutory Article 32 deadline. [CO-CLM-0010]

## Method

Eight read-only research agents were used to draw a systematic sample from the public EUDAMED UDI/device dataset.

- Pages read: 95
- UDI-DI records examined: 4,750
- Class III rows observed before deduplication: 213
- Distinct class III records after deduplication: 98

Records were separated by registration path / actor role before interpreting SS(C)P fields:

1. legacy registration path;
2. MF-role MDR manufacturer registration;
3. PR-role system/procedure-pack registration.

That separation is essential because a class III value on a system/procedure-pack record can reflect the highest-risk constituent and should not automatically be interpreted as an ordinary manufacturer-device classification.

## Measured API limits

ClinicOps' 8 September operational probes found a deep-offset reachability wall on the public `udiDiData` route: page 30,000 was repeatedly served while page 32,000 repeatedly failed during the observation window. [CO-CLM-0006]

ClinicOps also observed the route returning at most 50 records per page even when larger values were requested. [CO-CLM-0007]

These are point-in-time operational observations, not guaranteed API contracts. They are enough, however, to prohibit describing the method as an end-to-end audit of the public register.

## What the sample does and does not establish

### It supports

- a material transition-workload signal inside the sampled reachable frame;
- the need to separate legacy, MF and PR records before drawing SS(C)P conclusions;
- using public data to construct a portfolio work queue rather than a compliance allegation;
- a repeatable monthly time series if the same method and reachability frame remain comparable.

### It does not support

- saying that roughly 71% of all EU class III devices are legacy;
- saying that every legacy registration will follow the same transition timing;
- inferring certificate expiry from the public device record when certificate evidence has not been verified;
- alleging manufacturer or notified-body non-compliance from a missing public SS(C)P link;
- claiming that the public EUDAMED API provides complete register coverage.

## Commercial implication for ClinicOps

The machine-readable part of this work is becoming cheap. The defensible layer is not the scan itself; it is the accountable work of resolving certificate timing, identifier joins, SS(C)P status, market-language requirements, evidence gaps and ownership into a prioritised transition plan.

That is the design of the ClinicOps **Class III Transition Map**:

**free / low-cost screening → evidence-backed portfolio map → human-reviewed regulatory work plan**

For an authorised representative or regulatory consultancy managing many manufacturers, the useful portfolio question becomes:

> Which class III / implantable items are still on a legacy path, what are the verified transition triggers, and what needs to be ready for each one?

## Primary sources for the regulatory context

- Regulation (EU) 2017/745, Article 32: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745
- European Commission EUDAMED overview: https://health.ec.europa.eu/medical-devices-eudamed/overview_en
- European Commission UDI/Device registration: https://health.ec.europa.eu/medical-devices-eudamed/udidevice-registration_en
- MDCG 2026-4: https://health.ec.europa.eu/document/download/a80332cf-e9f0-4d45-8863-3d96e8c2a675_en?filename=mdcg_2026-4_en.pdf

## Pre-publication gate

Before publishing any derivative of this note:

1. Re-run the public API canary and record whether the reachability frame changed.
2. Re-run `clinicops-claims` and confirm every cited claim is still allowed for `research-note` use.
3. Generate an evidence pack with `clinicops-publication-pack`.
4. Run the claim guard on the final copy.
5. Adversarially review every sentence around any correction, not only the corrected phrase.
6. Keep the sample denominator and the no-full-register-audit limitation adjacent to any numerical headline.
