# ClinicOps Regulatory Knowledge Graph Specification

## Purpose

Define the minimum structured intelligence model that lets ClinicOps connect portfolio evidence, regulatory events, commercial opportunities and client learning without turning the public repository into a client-data store.

This is a data-contract specification, not a claim that ClinicOps currently has complete population coverage.

## Core entities

### Organisation

Fields:
- organisation_id
- display_name
- organisation_type: manufacturer / authorised_representative / consultancy / distributor / other
- geography
- public_source_refs
- private_record_ref (optional pointer only; never raw private data in the public repo)

### Device

Fields:
- device_id
- organisation_id
- device_name
- actor_role
- registration_type
- basic_udi_di
- public_identifier
- class_or_risk_context
- source_refs

### Certificate

Fields:
- certificate_id
- device_id
- expiry_date
- certificate_type
- evidence_source
- evidence_confidence

### SSCP evidence record

Fields:
- sscp_record_id
- device_id
- linked_public_metadata: true / false / unknown
- revision_or_date_when_known
- source_refs
- evidence_note

A missing public link must remain an evidence state, not a non-compliance conclusion.

### Market-language operation

Fields:
- market_record_id
- device_id
- target_market
- language
- document_type
- evidence_state
- source_ref

Do not infer language obligations from geography alone without evidence.

### Regulatory event

Fields:
- event_id
- scope
- event_type
- effective_or_observed_date
- claim_ids
- primary_source_refs
- limitations

Events must preserve the difference between primary rule, guidance, observed system behaviour and ClinicOps derivation.

### Commercial opportunity

Fields:
- opportunity_id
- organisation_id
- buyer_segment
- pain_hypothesis
- evidence_refs
- commercial_priority_score
- experiment_id
- status

Commercial scores are never regulatory/compliance risk scores.

### Experiment

Use the contract implemented in `src/clinicops_os/experiments.py`.

### Client action

Fields:
- action_id
- engagement_id
- device_id (optional)
- action_text
- evidence_refs
- owner
- target_date
- status
- human_reviewed

Client actions are work-plan outputs, not legal conclusions.

## Relationships

Organisation
-> has Device
-> may have Certificate
-> may have SSCP evidence record
-> may have Market-language operation
-> is affected by Regulatory event
-> may create Commercial opportunity
-> is tested through Experiment
-> may result in Client action

## Provenance requirements

Every material evidence-bearing node should retain:
- source reference or private evidence pointer;
- observation / source date when available;
- evidence class;
- limitations;
- human-review state where relevant.

## Storage strategy

### Public GitHub

Allowed:
- schemas
- code
- sanitized examples
- public primary-source references
- anonymised research outputs

Not allowed by default:
- client portfolios
- prospect lists
- mailbox content
- credentials
- private named-device findings
- confidential documents

### Private engagement storage

Use a client-specific controlled workspace outside the public repository. Store only stable references/hashes in generated deliverables where useful for reproducibility.

## Implementation sequence

1. Keep the existing portfolio JSON contract as the first device/portfolio projection.
2. Keep Revenue OS account records as the first commercial projection.
3. Keep the experiment registry as the learning projection.
4. Add identifiers between these projections only when real client workflows need the joins.
5. Move to a relational database only after repeated client usage proves the need.

The graph is a conceptual and contract layer first. Do not introduce graph-database infrastructure merely because the model is called a knowledge graph.
