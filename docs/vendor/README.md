# Vendored third-party assets

Vendored (not hot-linked) so the site stays self-hosted, pinned and reviewable. Loaded lazily only by the pages that need them.

| File | Package | Version | License | Source | Purpose |
|---|---|---|---|---|---|
| tabulator-6.5.3.min.js / .css | tabulator-tables (npm) | 6.5.3 | MIT | https://tabulator.info / npm registry tarball | Exception-workbench data grid in the Regulatory Integrity Scanner |
| pdfjs/pdf.min.mjs | pdfjs-dist (npm) | 6.3.289 | Apache-2.0 | https://mozilla.github.io/pdf.js / npm registry tarball | Client-side PDF text-layer extraction (upload-and-confirm auto-fill), Technical File Consistency Check |
| pdfjs/pdf.worker.min.mjs | pdfjs-dist (npm) | 6.3.289 | Apache-2.0 | https://mozilla.github.io/pdf.js / npm registry tarball | Background worker pdf.js requires to parse a PDF off the main thread |

Update strategy: bump deliberately, re-pin, re-hash, re-run E2E. Removal strategy: the Scanner falls back to its plain findings table if the grid asset fails to load — no evidence record depends on the grid; the consistency check falls back to manual paste/type entry if the pdf.js asset fails to load or a given PDF fails to parse — no finding depends on the upload path, only on the grid values, exactly as before it existed.

No CDN is used for any vendored file above — everything here is served from this origin, which is what lets every tool's "nothing you enter or import leaves this browser" claim hold without exception. pdf.js's optional CMap/standard-fonts asset packs (needed mainly for non-Latin-script embedded fonts) are deliberately not vendored, to keep the footprint to the two files above (~1.7 MB combined) rather than a much larger asset set; a PDF that needs them surfaces as a caught extraction error in `assets/pdf-extract.js` ("could not read this file locally — enter values manually"), never a silent wrong answer. Danish- and English-language regulatory PDFs (IFUs, DoCs, certificates, SS(C)Ps) are Latin-script and unaffected. Revisit if a real document ever needs it.

sha256 (js):
- tabulator-6.5.3.min.js: see repo history / verify with `sha256sum`.
- pdfjs/pdf.min.mjs: `f80490490320511e5df18c580b9edd6b5db8058dceebaf6f161992e0a964b9e2`
- pdfjs/pdf.worker.min.mjs: `8ab0e5e30031b4a06ecfddd5ae9562f0227f830ee7ec9ed1a968b134243d2386`
