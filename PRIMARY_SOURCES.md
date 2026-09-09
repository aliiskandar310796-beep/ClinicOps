# Primary-source registry

Checked 9 September 2026. This file records source roles, not legal advice.

## MDR Article 32 — SSCP duty holder and baseline upload model
Source: Regulation (EU) 2017/745, Article 32
https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0745

Use for:
- manufacturer duty to draw up an SSCP for implantable and class III devices, subject to the Article 32 exclusions;
- public availability via EUDAMED;
- notified-body validation and the regulation's baseline notified-body upload wording;
- inclusion of the Basic UDI-DI in the SSCP.

Do not use guidance to silently overwrite the regulation. When describing the 2026 operational transition, cite the MDCG position paper separately and distinguish it from binding law.

## MDCG 2026-4 — operational SS(C)P transition in EUDAMED
Source: MDCG Position Paper: Management of SS(C)P in EUDAMED after mandatory use, June 2026
https://health.ec.europa.eu/document/download/a80332cf-e9f0-4d45-8863-3d96e8c2a675_en?filename=mdcg_2026-4_en.pdf

Use for:
- planned reassignment of EUDAMED SS(C)P upload tasks to manufacturers;
- manufacturer upload of master version and translations under the revised operating model;
- notified-body indication of validated SS(C)P(s) against relevant Basic UDI-DI(s);
- planned Playground deployment in July 2026 and Production deployment in October 2026;
- the recommendation that manufacturers upload SS(C)Ps for devices placed on the market before mandatory use as soon as possible and no later than 27 February 2027.

Qualification: MDCG documents are not legally binding and MDCG 2026-4 says so explicitly.

## EUDAMED mandatory modules
Source: European Commission EUDAMED overview / mandatory-use announcement
https://health.ec.europa.eu/medical-devices-eudamed/overview_en

Use for: first four modules mandatory from 28 May 2026 — Actor registration, UDI/Device registration, Notified Bodies & Certificates, Market Surveillance.

## Legacy-device identifiers
Sources: European Commission EUDAMED Information Centre
https://webgate.ec.europa.eu/eudamed-help/en/search-by-module/devices/legacy-devices/basic-concepts/identification-details/generation-of-identification-details-for-a-legacy-device-when-a-udi-di-does-not-exist.html
https://webgate.ec.europa.eu/eudamed-play-help/en/search-by-module/devices/legacy-devices/basic-concepts/identification-details/generation-of-identification-details-for-a-legacy-device-when-a-udi-di-already-exists.html
https://webgate.ec.europa.eu/eudamed-help/en/search-by-module/devices/udi-devices/basic-concepts/categorisation-of-devices.html

Use for:
- legacy devices use an EUDAMED DI in place of a Basic UDI-DI;
- EUDAMED DI starts with `B-`;
- when a UDI-DI already exists, EUDAMED automatically generates the EUDAMED DI by adding the `B-` prefix;
- when no UDI-DI exists, a B-prefixed EUDAMED DI and D-prefixed EUDAMED ID are used.

Important: these sources support identifier structure. They do **not** by themselves state the full ClinicOps derived consequence about linked SS(C)P behavior. Keep that consequence labelled as derivation/observed system behavior.

## System/procedure pack risk class
Source: European Commission EUDAMED Information Centre
https://webgate.ec.europa.eu/eudamed-help/en/actor/topics-by-actor/system-procedure-pack-producer/register-basic-udi-di-together-with-a-udi-di-for-a-system-or-procedure-pack/basic-udi-di-information.html

Use for: the EUDAMED SPP registration field uses the **highest risk class of devices that are part of the system or procedure pack**. Do not interpret that field as if it were necessarily an ordinary classification of the pack itself.

## Actor roles
Source: European Commission actor registration / EUDAMED information
https://health.ec.europa.eu/medical-devices-eudamed/actor-registration-module_en

Use for: manufacturers, authorised representatives, system/procedure-pack producers and importers are distinct actor roles. Preserve role-aware analysis.

## MDCG 2019-9 Rev.1 — SSCP revision/translation management
Source: MDCG 2019-9 Rev.1, Summary of safety and clinical performance
https://health.ec.europa.eu/document/download/5f082b2f-8d51-495c-9ab9-985a9f39ece4_en?filename=md_mdcg_2019_9_sscp_en.pdf

Use for:
- SSCP revision histories should identify revision number/date/main changes and validation status/language;
- updated SSCPs can exist while validation timing is in process according to the described conformity-assessment route;
- translations are the manufacturer's responsibility under the guidance model, and the translated documents are not themselves validated by the notified body;
- revision history transparency is therefore part of the intended document control model.

Qualification: MDCG guidance is non-binding. Do not convert a document-vs-record difference into an irregularity without establishing the exact process state.
