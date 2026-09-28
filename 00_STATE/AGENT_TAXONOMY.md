# Agent Taxonomy

> Migrated verbatim from the pre-2026-09-23 `AGENT_STATE.md` monolith as part of the connectome-lens shard proposal (draft, not yet reconciled against live `main`). Content below this line is unedited from the original section.

## Agent taxonomy (canonical, 2026-09-17)

Three layers, not three competing fleets:

1. **Core accountable business agents (6, canonical)** — the named agents in `06_AGENTS`/department mapping (Regulatory Evidence Steward, Opportunity Architect, Customer Discovery Agent, Visibility Architect, Portfolio Operator, Release Sentinel). Accountability and department ownership live here.
2. **Specialist profiles (`.github/agents/*.agent.md`, currently 8)** — sentinels/builders operating *under* the core agents (the 6 above plus specialist additions such as validation-scalability-sentinel and asset-fleet-builder). They add capability, not accountability.
3. **Operational loops (`agents/fleet.json`, currently 22)** — bounded recurring tasks/automation roles (radars, canaries, miners, triage). These are legacy-named automation loops, **not** accountable agents; they run under a core agent's remit and their sends/posts always route through the top-level session per E-007. Since 2026-09-25 ten of them are implemented by the Tier-0 jobs in `autonomy/jobs/` (claude.ai scheduled tasks; see `autonomy/README.md`): `regulatory-radar`, `resilience-engineer`, `content-synthesizer`, `inbox-signal-triage`, `tier0-verification`, `termbase-builder`, `fleet-watchdog`, `pipeline-hygiene`, `invoice-prep`, `eudamed-private-research`. Those loops draft, report and open pull requests; they never send, never publish and never push to `main`.

`competitor-radar` is renamed **`peer-market-radar`** (2026-09-17): ClinicOps treats Visiana/BoneXpert, consultancies, CROs and QA/RA teams as peers, benchmarks, partners and possible buyers — never adversaries. It observes public hiring, buying patterns, operational pain and tooling adoption to find white space; it never uses non-public information, and hiring demand counts as E1 market evidence only, never buyer validation.

