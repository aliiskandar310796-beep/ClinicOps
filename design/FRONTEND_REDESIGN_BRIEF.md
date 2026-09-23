# ClinicOps frontend redesign brief ("ledger")

Status: ACTIVE for the 2026-09 redesign. Tokens remain canonical in `DESIGN_TOKENS.md`; this file names the composition rules.

## Design read

Redesign, visual overhaul with information architecture, URLs and copy preserved. Audience: RA/QA leads and regulatory operations at EU medical-device manufacturers and authorised representatives. Trust-first, technical, Nordic. Dials: DESIGN_VARIANCE 4, MOTION_INTENSITY 3, VISUAL_DENSITY 5.

## Language

- Structure from hairlines, type and space. Not boxes, shadows or gradients. Cards are open (a top rule), not bordered boxes.
- One accent (teal `--accent`), one neutral family (green-tinted grey), one radius scale (`--r` 6px, `--r-sm` 4px). No pills (999px). No glow, no decorative gradients.
- Geist (sans) and Geist Mono, self-hosted in `docs/assets/fonts/`. Mono is for identifiers, labels, status words, numbers. Never link Google Fonts or any third-party origin (privacy-first audience, "nothing leaves the page").
- Status is always colour plus word: use `.st .st-ok|.st-hold|.st-warn|.st-na` (aligned, mismatch signal / conflicting, missing evidence / requires qualified review, not applicable). Tabular numerals for data.
- Real product screenshots only (`docs/assets/scanner-exception-queue.png`). No div-built fake dashboards. Diagrams as inline SVG using tokens.
- Motion: only the hero settle-in, hover/active feedback, nav underline, and cross-page view transition. All gated by `prefers-reduced-motion`.
- Light and dark from tokens (`prefers-color-scheme`). Never hard-code hex values in page CSS: use `var(--...)`.

## Composition vocabulary (already in `docs/site.css`)

`.wrap`, `.hero` + `.hero-grid`, `.eyebrow` / `.kicker` (mono label, use sparingly: at most one per three sections), `.lede`, `.cta-row` with `.cta.primary` / `.cta.ghost` (one primary per view), `.cta-links` (quiet text links for secondary intents), `.grid` (`.two` `.three` `.four` `.asym`), `.card` (+ `.link-card`, `.feature`), `.ledger` (rows: title left, body right), `.flow` (5-step rule row), `.model` (numbered hairline list), `.tags` (chips for enumerations), `.callout` (+ `.boundary`), `.split`, `.source-list`, `.steps`, `figure` / `figcaption`, `.diagram`, `table`, `.field`, `.btn`, `.st-*`, `.closing` (closing CTA block).

Rules of thumb: vary layout families down a page (do not stack three identical card grids); enumerations of more than five items get `.tags` or a grouped layout, not a bullet list; hero headline at most three lines; nav stays one line.

## Non-negotiables (this is a regulated-domain repo)

1. Do not change visible copy, headings, link targets, anchor ids, form field names/ids, JS behaviour or data attributes. Markup and class changes are fine. If a copy defect is spotted, list it in the report instead of fixing it.
2. Do not edit `docs/site.css`. Page-specific rules go in that page's own `<style>` block using tokens. If a rule is needed on 3+ pages, report the CSS snippet to the lead.
3. Do not edit the generated header/nav (`scripts/harmonize_public_shell.py` owns it).
4. Keep `<title>`, meta, canonical, JSON-LD, and `<!-- claim-* -->` comments byte-identical.
5. After edits run: `python3 scripts/validate_internal_links.py`, `python3 scripts/validate_site_metadata.py`, `python3 scripts/validate_content_claims.py`, and `python3 -m pytest tests -q -k "site or copy or website or public"`.
6. Verify visually with Playwright at 1440x900 and 390x844, light and dark (`page.emulateMedia({colorScheme:'dark'})`), no horizontal scroll, no console errors. Serve `docs/` with `python3 -m http.server`.
