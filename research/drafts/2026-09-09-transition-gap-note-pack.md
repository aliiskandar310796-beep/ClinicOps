# Publication pack — EUDAMED class III transition gap

Status: **internal draft pack; not published**  
Evidence date: **9 September 2026**  
Intended use: **research-note**

## Purpose

Turn the corrected 8 September class III census into ClinicOps' first research-led public note without reviving the rejected manufacturer-diligence narrative.

The commercial frame is a **transition work-plan problem**: identify which portfolio records are still in a legacy registration path, distinguish them from MDR manufacturer registrations and PR-role system/procedure-pack records, then connect the transition to certificate timing, Basic UDI-DI creation, SS(C)P operations and market-language document control.

## Safe headline candidates

1. **We sampled class III records in EUDAMED. The result changed our hypothesis.**
2. **The EUDAMED class III transition gap: what a 98-record sample actually showed**
3. **Legacy-to-MDR is the SS(C)P work-plan question hiding in public EUDAMED data**

Avoid percentage headlines that look like population estimates.

## Core evidence sequence

### 1. Start with the correction, not the original hypothesis
**CO-CLM-0002** — In the ClinicOps 8 September 2026 reachable-frame class III sample, 70 distinct records were legacy registrations, 11 were PR-role system/procedure-pack records, and 17 were MF-role MDR manufacturer registrations; all 17 sampled MF-role MDR registrations had linked SS(C)P metadata and were marked validated.

Required framing: this was a systematic sample within the demonstrably reachable public-API frame, not a population rate or full-register audit. The result directly rejects the earlier diligence-failure story.

### 2. Ground the duty-holder correctly
**CO-CLM-0001** — Under MDR Article 32(1), the manufacturer draws up an SSCP for implantable devices and class III devices, subject to the Article 32 exclusions.

Do not replace the duty-holder with passive wording when the point is who owns the work.

### 3. Explain why legacy identifiers matter without turning reasoning into law
**CO-CLM-0004** — EUDAMED legacy-device identification uses a B-prefixed EUDAMED DI in place of a Basic UDI-DI in the legacy registration model.

**CO-CLM-0005** — ClinicOps uses the B-prefix as a screening signal for the legacy registration path when reasoning about the MDR Basic UDI-DI/SS(C)P linkage model. State explicitly that the downstream linkage consequence is a ClinicOps derivation, not a directly quoted Commission rule.

### 4. Connect the finding to the new operating model
**CO-CLM-0009** — MDCG 2026-4 describes a revised model in which the manufacturer uploads the SS(C)P master version and translations, while the notified body indicates the validated SS(C)P against the relevant Basic UDI-DI(s).

Qualification: MDCG 2026-4 is non-binding and implementation is tied to the new EUDAMED functionality.

### 5. Make the near-term transition window concrete
**CO-CLM-0008** — MDCG 2026-4 planned Playground deployment in July 2026 and Production deployment in October 2026 for the revised functionality.

**CO-CLM-0010** — For devices placed on the market before mandatory use of the UDI/Devices module, MDCG 2026-4 recommends upload as soon as possible and no later than 27 February 2027, with manufacturers and notified bodies aligning timelines.

Never call 27 February 2027 a standalone statutory deadline. It is a recommendation in the non-binding MDCG position paper.

## Method box

Suggested compact method disclosure:

> ClinicOps sampled the public EUDAMED UDI/device dataset on 8 September 2026 using a systematic reachable-frame design. We examined 95 pages / 4,750 UDI-DI rows, isolated 213 class III rows and deduplicated them to 98 distinct records. We separated legacy-style registrations, MF-role manufacturer registrations and PR-role system/procedure-pack records before interpreting SS(C)P metadata. Deep-offset API failures prevented full-register coverage, so these results describe the sample, not the population.

## API limitation box

**CO-CLM-0006** — On 8 September, the public `udiDiData` route served probes around page 30,000 while probes around page 32,000 consistently failed. Treat this as a dated operational observation, not an endpoint contract.

**CO-CLM-0007** — ClinicOps observed a practical return cap of 50 records per page. Re-test before relying on it operationally.

Do not translate either observation into a claim that a fixed percentage of the register is permanently inaccessible.

## Commercial bridge

The research note should end with a work-plan question, not an accusation:

**For an AR or manufacturer portfolio: which class III devices are still represented through a legacy registration path, what is the certificate/transition timing for each, and what SS(C)P + language-control work becomes due as each portfolio item moves into the MDR operating model?**

That is the paid judgement layer. Public-data screening is the low-cost front door.

## Forbidden angles

- Manufacturers are broadly failing to link SS(C)Ps for MDR class III devices. **Rejected: CO-CLM-0003.**
- The sample proves a population-wide legacy percentage.
- ClinicOps audited the whole public EUDAMED register.
- Every B-prefixed record is legally incapable of carrying an SS(C)P link as an explicit Commission rule.
- 27 February 2027 is a statutory deadline created by Article 32.
- PR-role class III rows should be interpreted as ordinary manufacturer class III device registrations.

## Pre-publication checklist

1. Re-run `clinicops-claims` and confirm every cited claim is still in-date for `research-note` use.
2. Re-test the API behavior if the method box mentions reachability or page-size observations.
3. Verify the current status of the October 2026 Production deployment before publication if the note is published after implementation changes.
4. Run the full copy through `clinicops-claim-check` / `scripts/claim_gate.py`.
5. Do one adversarial regulatory read of the entire note after the last correction, not just the changed sentence.
6. Keep named manufacturer/device examples out of the first public note unless separately source-verified and deliberately approved.
