# ClinicOps shared agent state — INDEX (draft shard, 2026-09-23)

**DRAFT PROPOSAL — not applied to live `main`.** This is a connectome-lens architecture
draft: splitting the single monolithic `AGENT_STATE.md` into topic-sharded registers under
`00_STATE/`, each independently updatable by its owning agent, to reduce the write-collision
risk the original file already documented (see `00_STATE/GOVERNANCE_BOUNDARIES.md` ->
"Write-discipline incidents — 2026-09-13"). Before this becomes a real PR: re-fetch current
`main` (this draft was built from a clone that may already be stale — the original file's own
first rule is "always fetch live state again before acting") and re-apply/rebase this split
against whatever has landed since, since `00_STATE/ACTIVE_FLEETS.md` and
`00_STATE/CHANGELOG_AND_NEXT.md` are the highest-churn sections and most likely to have moved.

Every session must still read this index first, then open only the shard(s) relevant to the
task at hand -- reading all six shards together reconstructs the original file exactly (verified
by an automated reconstruction diff at split time -- zero content was dropped or reworded).

## Shards

| Shard | Covers | Typical churn |
|---|---|---|
| `00_STATE/BUSINESS_THESIS.md` | Canonical-truth rule, current business thesis/positioning, growth/AI-gateway doctrine, budget doctrine | Low |
| `00_STATE/ACTIVE_FLEETS.md` | Active outcome fleets, EXP-001 threshold, AI Company OS / evidence ladder, paid-pilot operating path, founder-independence proof | **High** |
| `00_STATE/AGENT_TAXONOMY.md` | Canonical agent taxonomy (core agents / specialist profiles / operational loops) | Low |
| `00_STATE/PRODUCTION_SURFACE.md` | Public production surface, search/indexing, EUDAMED Watch, privacy/claim governance | Medium |
| `00_STATE/GOVERNANCE_BOUNDARIES.md` | CI/resilience gates, private commercial/CRM state rules, external-action boundaries, repo governance/security | Low (high-stakes when it does change) |
| `00_STATE/CHANGELOG_AND_NEXT.md` | Recent merged operating changes, coordination protocol, highest-leverage next work | **High** |

## Last reconciled

Draft cut from a snapshot last reconciled 2026-09-17 (per original file) + connectome-lens
review 2026-09-23. **Not a fresh reconciliation** — the next real edit must fetch live `main`
first.
