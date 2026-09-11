# EUDAMED Public API reuse review

Review date: 2026-09-12

Status: **reviewed for the current monthly read-only monitor**. This is an operational due-diligence note, not legal advice and not a statement that API use is unlimited or can never be restricted later.

## Conclusion

The current ClinicOps monthly EUDAMED watch is consistent with the official public-interface materials reviewed on 2026-09-12:

- the current Commission EUDAMED Public API user guide says the Public API is public and not restricted to particular users, that any individual or organisation may download public EUDAMED data through it, and that the data may be integrated directly into third-party software;
- the guide exposes GET-only access and paginated JSON output, and the reviewed guide contains no stated request-rate, quota, throttling or separate EUDAMED-specific reuse condition;
- Commission Decision 2011/833/EU establishes a general principle that Commission documents are available for commercial or non-commercial reuse, normally without charge and without individual application, subject to applicable conditions;
- the Commission legal notice states that EU-owned website content is generally reusable under CC BY 4.0 unless otherwise indicated, with attribution and change-indication requirements and with third-party/rightsholder exceptions.

On that evidence, a monthly bounded GET-only monitor using a fixed identifying User-Agent, one-second spacing, a finite page cap and no authentication is a conservative implementation of the intended public API use. No official source reviewed requires disabling the existing monthly schedule.

## Important boundaries

This review does **not** mean:

- the API has a guaranteed service level or unlimited request allowance;
- future Commission terms, technical controls or API documentation can be ignored;
- third-party intellectual-property rights in submitted data, names, marks or documents are licensed by this review;
- raw named EUDAMED records should be republished publicly without a separate rights/privacy assessment;
- a 403/429 or explicit operator instruction may be bypassed or worked around.

ClinicOps' existing design is intentionally more conservative than the minimum evidence reviewed here: the scheduled workflow publishes aggregate-only output and pseudonymous HMAC keys, while fully named reports remain private/local.

## Operational rule

Keep the monthly schedule only while all of the following remain true:

1. calls are GET-only against the documented public API;
2. the monitor remains bounded and rate-limited (currently `--sleep 1.0`, finite `--max-pages`);
3. the User-Agent identifies ClinicOps;
4. no authentication/access-control circumvention is introduced;
5. public repository output remains anonymised under the existing leak contract;
6. repeated HTTP 429/403 responses, a new published API term, robots/policy notice, or an explicit Commission instruction triggers a stop-and-review before continued automated polling.

Do not respond to a new limit by increasing concurrency, rotating identities, proxying around controls, or otherwise attempting to evade the operator's restriction.

## Sources reviewed

Authoritative sources reviewed directly on 2026-09-12:

1. European Commission, **EUDAMED user guide — Public API** (2026), especially the Introduction / “Who can use the Public API” and pagination sections:  
   https://webgate.ec.europa.eu/eudamed-play-help/en/files/Public%20API%20-%20user%20guide.pdf
2. Commission Decision **2011/833/EU of 12 December 2011 on the reuse of Commission documents**, Articles 4, 6, 9 and 10:  
   https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32011D0833
3. European Commission **Legal notice**, copyright/reuse section:  
   https://commission.europa.eu/legal-notice_en

## Re-review trigger

Re-run this review before relying on the schedule if any of the following happens:

- the EUDAMED Public API guide or endpoint family changes materially;
- the API starts returning rate-limit/access-denial responses under the current bounded pattern;
- the Commission publishes EUDAMED-specific API terms, a developer agreement, quota policy or automated-access notice;
- ClinicOps changes from aggregate/pseudonymous public output to publication of raw named records;
- request volume or cadence increases materially beyond the current monthly watch.

Absent one of those triggers, this note closes the prior D-17 due-diligence gap for the current implementation.
