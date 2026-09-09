# Claude continuation handoff — ClinicOps Revenue OS

Use this after completing the previously assigned browser/account work for clinicops.dk, LinkedIn, and Gumroad.

## Coordination floor

Before doing anything:
1. fetch latest `main`;
2. read `AGENT_STATE.md`, `AGENTS.md`, `CLAIM_RULES.md`, `revenue/README.md`, and `experiments/EXPERIMENT_LEDGER.md`;
3. treat GitHub `main` as canonical;
4. preserve concurrent ChatGPT/Copilot work; on conflicts, fetch and merge rather than overwrite;
5. run relevant tests/CI before declaring repository work complete.

## Revenue OS now implemented

The repo contains:
- `src/clinicops_os/revenue.py` — coverage-aware account intelligence and prioritisation;
- `examples/revenue_accounts.csv` — sanitized fixture only;
- `tests/test_revenue.py` — scoring/boundary tests;
- `clinicops-revenue-rank` — CLI that emits schema-versioned JSON;
- `revenue/README.md` — operating contract and privacy/regulatory boundaries.

The commercial score is **not** regulatory/compliance/legal/enforcement risk.

Unknown values must remain unknown. Do not fill blank budget, access, urgency, or other fields with guesses just to obtain a score.

## Your next job

Operationalise Revenue OS against real market evidence without putting private commercial data in this public repository.

### Step 1 — Verify previous browser work

Report what actually changed on:
- clinicops.dk / GoDaddy;
- Ali Iskandar LinkedIn profile;
- ClinicOps LinkedIn company page;
- Gumroad.

For each: give before/after, exact live URL, expected impact, rollback option, and any unresolved blocker.

Do not claim a change is live until you verify it live.

### Step 2 — Build a private account working set

Use browser/web research and existing legitimate business context to identify a small set of potential buyers or partners. Keep the real working set private; do not commit named prospect rows to the public repo.

For each account capture only evidence-backed values for:
- company;
- segment (`manufacturer`, `authorised_representative`, `consultancy`, `distributor`, `other`);
- geography;
- trigger;
- source URL;
- evidence note;
- experiment ID;
- urgency 0–5;
- offer fit 0–5;
- evidence strength 0–5;
- partner leverage 0–5;
- access strength 0–5;
- budget signal 0–5;
- reuse potential 0–5.

If a scored field is unknown, leave it blank.

### Step 3 — Rank and select experiments

Run:

```bash
clinicops-revenue-rank <private-accounts.csv>
```

Use the output as an operating queue, not as truth.

Interpret next-experiment labels narrowly:
- `RESEARCH` — gather better evidence before contact assumptions;
- `DISCOVERY` — test pain/current workaround;
- `WARM INTRO / DISCOVERY` — access is weak/unknown;
- `PARTNER CONVERSATION` — test AR/consultancy workflow integration or white-label fit;
- `PILOT` — test a tightly scoped paid or sponsored engagement.

Do not mass-message accounts. Prefer 3–5 high-information conversations over 100 low-context messages.

### Step 4 — Feed learning back safely

For each material test:
- link it to `experiments/EXPERIMENT_LEDGER.md`;
- capture hypothesis, smallest test, metric, kill condition, result, and learning;
- commit only sanitized/aggregated learning to the public repo;
- keep private names/contact details/private findings out of public GitHub.

### Step 5 — Improve the system only when evidence justifies it

Good reasons to modify Revenue OS:
- a repeated real-world data shape is missing;
- a score produces obviously bad prioritisation across several cases;
- a repeated manual reconciliation step can be removed;
- a machine handoff needs a stable additional field.

Bad reasons:
- adding dashboards before use;
- adding more agents because it feels productive;
- scraping broad prospect lists without a test;
- turning missing regulatory metadata into sales allegations;
- increasing score complexity without buyer-learning evidence.

## Output back to ChatGPT / Ali

Return a compact operator report:
1. external changes verified live;
2. number of accounts researched privately;
3. Revenue OS band distribution and score coverage distribution (aggregated, no private details unless Ali explicitly asks and the surface is private);
4. top 3 experiments and why;
5. what evidence is still missing;
6. what you changed in GitHub, with commit SHAs;
7. CI status;
8. one recommended next move with the highest expected learning/revenue leverage.

## Objective

ClinicOps should compound toward:

`regulatory signal → defensible evidence → commercial trigger → ranked experiment → buyer learning → reusable asset → paid work → stronger intelligence`

Optimize for learning velocity and revenue evidence, not activity volume.
