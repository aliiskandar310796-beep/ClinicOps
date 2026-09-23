# Frontend QA (qa/)

Lean browser QA for the static site in `docs/`. Uses the global Playwright
(`export NODE_PATH=$(npm root -g)`; Chromium only by default). axe-core and
Lighthouse install locally into `qa/node_modules` (gitignored) on first run.

```
qa/run.sh fast   # CI: matrix @1440+390 light, axe @1440 light
qa/run.sh full   # matrix 5 widths x light/dark, axe 1440+390 x light/dark, Lighthouse
```
Exit codes: `0` pass, `1` findings, `2` infrastructure error (server/browser/install).
Outputs land in `qa/out/` (gitignored): `matrix.json`, `a11y.md/json`, `perf.md/json`,
`shots/` (full-page JPEGs), and a hand-written `REPORT.md`.

Scripts (run individually with `node qa/<name>.cjs`, server on :8102 or `QA_BASE_URL`):
- `matrix.cjs`: every `docs/sitemap.xml` URL + `/404.html`; overflow, console/request
  errors, nav clipping, images, skip link, focus indicators (first 15 stops),
  reduced motion, 24x24 targets (WCAG 2.2 SC 2.5.8, warning only).
  Env: `QA_WIDTHS`, `QA_SCHEMES`, `QA_ONLY=about,services`, `QA_BROWSER=firefox|webkit`, `QA_SHOTS=0`.
- `a11y.cjs`: axe-core, tags wcag2a/2aa/21aa/22aa.
- `perf.cjs`: Lighthouse mobile+desktop on 4 key pages; LCP <= 2.5s, CLS <= 0.1.

Limits: axe is automated and is NOT proof of WCAG conformance. Lighthouse is lab data,
not field data; TBT is only a proxy, INP is field-only and not measured. External
(third-party) request failures are warnings because CI sandboxes may block them.
Focus-indicator check tests computed outline/box-shadow, not contrast or visibility of the ring.
