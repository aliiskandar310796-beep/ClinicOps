# ClinicOps capability registry

Status: ACTIVE CONTROL (created 2026-09-18 per the Master Execution Directive §70). Tracks major operational/technical capabilities so infrastructure never sprawls invisibly. States: PROPOSED · PILOT · ACTIVE · DEGRADED · DISABLED · RETIRED. Review cadence: touch a row whenever its capability materially changes; full pass at least monthly.

| Capability | State | Value | Dependency | Data exposure | Metric | Failure mode | Fallback | Last review |
|---|---|---|---|---|---|---|---|---|
| GitHub repo + CI + exact-SHA gated Pages deploy | ACTIVE | Source of truth, safe releases | GitHub Actions | Public repo only | CI green rate; blocked-red-deploy count (2 caught to date) | Actions outage | Manual dispatch guard allows rollback to any CI-green SHA | 2026-09-18 |
| Live-site smoke (check_live_site, 37 targets) | ACTIVE | Production truth per deploy + weekly ops-watch | requests | Public pages only | failures=0 | CDN staleness false alarms | Re-run after cache window | 2026-09-18 |
| Playwright browser verification (container) | ACTIVE | Real-browser QA of site + Scanner | /opt/pw-browsers chromium, proxy | Public site + local fixtures | problems=0 per sweep | Proxy egress changes | Local file:// QA | 2026-09-18 |
| Playwright E2E workflow in repo (e2e/) | PILOT | Reproducible operator-journey test vs production | GitHub Actions + playwright install | Public site + fictional fixture | journey pass; time-to-queue | CI minutes cost; flake | Manual dispatch only; non-gating | 2026-09-18 |
| Regulatory Integrity Scanner (browser-local) | ACTIVE | Free on-ramp to flagship | none (vanilla JS) | None — nothing leaves browser | time-to-first-useful-queue; external users (currently 0) | UX creates more work than spreadsheet (top risk) | Single-change mode; manual review | 2026-09-18 |
| Claim governance (registry + audits + CI checks) | ACTIVE | Claims discipline | scripts/validators | Public copy | violations found per audit | Stale registry | Manual audit (SITE_CLAIMS_AUDIT) | 2026-09-18 |
| Design tokens (design/DESIGN_TOKENS.md ↔ site.css) | ACTIVE | Visual consistency across site/SVG/reports | none | None | drift instances | Fork between surfaces | Tokens file is canonical | 2026-09-18 |
| Figma design library | PROPOSED | Editable visual hub | Figma account/MCP (not connected in current sessions) | Design assets only | — | Values forked from tokens file | DESIGN_TOKENS.md remains canonical | 2026-09-18 |
| EUDAMED public-API research tooling | ACTIVE | Evidence for research/registry work | Public EUDAMED API | Public data only | reproducible outputs | API/schema changes (scenario §46) | Cached evidence + dated limitations | 2026-09-18 |
| Adaptive memory (repo-canonical) | ACTIVE | Institutional memory | repo docs + business project | Internal | corrections preserved | Doc sprawl | Dated addenda discipline | 2026-09-18 |
| External semantic memory (vector) | PROPOSED | Retrieval assistance only — never company truth | one system max | TBD — classification required | recall precision vs repo grep | Competing memories / hallucinated recall | Repo remains canonical | 2026-09-18 |
| Headroom (context compression) | PROPOSED | Long-session efficiency | vendor | Conversation content | correctness after compression | Compressing away regulatory nuance/corrections | Do not adopt without measured correctness | 2026-09-18 |
| OmniRoute / model routing | PROPOSED | Provider resilience/cost | vendor | Prompt content — allowlist required | availability; per-task quality | Cheap-model downgrade on high-stakes interpretation | Single-provider default | 2026-09-18 |
| MapLibre/GeoJSON mapping | PROPOSED | Geography where it changes decisions | maplibre | Public data | decision value per map | Decorative maps | Tables | 2026-09-18 |
| Storybook / visual regression at component level | PROPOSED | Component QA at scale | node toolchain | None | — | Ceremony without components | Bounded Playwright screenshots | 2026-09-18 |
| Backend / database / multi-user | PROPOSED | Only if browser-local stops sufficing | hosting | CLIENT DATA — full threat model required first | — | Premature enterprise infrastructure | Browser-local + private delivery | 2026-09-18 |
| XLSX import in Scanner Mode B | PROPOSED | Fewer conversion steps for RA users | a vetted parser lib (size/security) | Browser-local file | usage evidence | Heavy JS; parser CVEs | CSV/JSON path + in-tool guidance | 2026-09-18 |

Rules: pilot ONE memory system at a time; never activate competing memories (MemPalace/Headroom/OmniRoute memory simultaneously); experimental rows never gate P0/P1 work; a row that stops earning its cost is RETIRED, not left ambient.
