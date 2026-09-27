# Vendored third-party assets

Vendored (not hot-linked) so the site stays self-hosted, pinned and reviewable. Loaded lazily only by the pages that need them.

| File | Package | Version | License | Source | Purpose |
|---|---|---|---|---|---|
| tabulator-6.5.3.min.js / .css | tabulator-tables (npm) | 6.5.3 | MIT | https://tabulator.info / npm registry tarball | Exception-workbench data grid in the Regulatory Integrity Scanner |
| pdfjs/pdf.min.mjs | pdfjs-dist (npm) | 6.3.289 | Apache-2.0 | https://mozilla.github.io/pdf.js / npm registry tarball | Client-side PDF text-layer extraction (upload-and-confirm auto-fill), Technical File Consistency Check |
| pdfjs/pdf.worker.min.mjs | pdfjs-dist (npm) | 6.3.289 | Apache-2.0 | https://mozilla.github.io/pdf.js / npm registry tarball | Background worker pdf.js requires to parse a PDF off the main thread |
| tesseract/tesseract.min.js | tesseract.js (npm) | 7.0.0 | Apache-2.0 | https://github.com/naptha/tesseract.js / npm registry tarball | Main OCR API (`window.Tesseract`), opt-in fallback for scanned/image PDFs with no text layer, Technical File Consistency Check |
| tesseract/worker.min.js | tesseract.js (npm) | 7.0.0 | Apache-2.0 | https://github.com/naptha/tesseract.js / npm registry tarball | Self-hostable worker script tesseract.js requires to run OCR off the main thread |
| tesseract/tesseract-core-lstm.js | tesseract.js-core (npm) | 6.1.2 (resolved by npm as tesseract.js 7.0.0's dependency at vendoring time) | Apache-2.0 | https://github.com/naptha/tesseract.js-core / npm registry tarball | WASM glue code for the LSTM-only, non-SIMD OCR engine build (the broadly-compatible variant; deliberately not the SIMD build, to keep one code path) |
| tesseract/tesseract-core-lstm.wasm | tesseract.js-core (npm) | 6.1.2 (see above) | Apache-2.0 | https://github.com/naptha/tesseract.js-core / npm registry tarball | The compiled Tesseract OCR engine binary itself |
| tesseract/eng.traineddata.gz | tesseract-ocr-eng (apt, `tessdata_fast`) | 1:4.1.0-2 (Debian package; upstream `tessdata_fast` from the `tesseract-ocr` GitHub org) | Apache-2.0 | `/usr/share/tesseract-ocr/5/tessdata/eng.traineddata` (Debian `tesseract-ocr-eng` package), gzipped locally for vendoring | English trained-data the OCR engine reads to recognize characters — not obtainable from either npm package, only via the `tesseract-ocr-eng` system package or tesseract.js's own (CDN-hosted, not vendored here) language-data host |

Update strategy: bump deliberately, re-pin, re-hash, re-run E2E. Removal strategy: the Scanner falls back to its plain findings table if the grid asset fails to load — no evidence record depends on the grid; the consistency check falls back to manual paste/type entry if the pdf.js asset fails to load or a given PDF fails to parse — no finding depends on the upload path, only on the grid values, exactly as before it existed; if any tesseract/* file fails to load, OCR reports a caught error ("could not run local OCR — enter this column's values manually") and the page is otherwise unaffected, since OCR is reached only by an explicit, opt-in button that appears solely for a scanned/image PDF with no text layer.

No CDN is used for any vendored file above — everything here is served from this origin, which is what lets every tool's "nothing you enter or import leaves this browser" claim hold without exception. pdf.js's optional CMap/standard-fonts asset packs (needed mainly for non-Latin-script embedded fonts) are deliberately not vendored, to keep the footprint to the two files above (~1.7 MB combined) rather than a much larger asset set; a PDF that needs them surfaces as a caught extraction error in `assets/pdf-extract.js` ("could not read this file locally — enter values manually"), never a silent wrong answer. Danish- and English-language regulatory PDFs (IFUs, DoCs, certificates, SS(C)Ps) are Latin-script and unaffected. Revisit if a real document ever needs it.

The `tesseract/` set (~4.9 MB combined) is loaded lazily and only once a person clicks "Try OCR on this file" for a specific scanned upload — it never loads on page visit, and never loads for a PDF that already has a usable text layer (that path uses only pdf.js, above). Only the English trained-data file is vendored, matching the site's English/Danish-label detector patterns and its Latin-script regulatory-document scope; other languages are out of scope, same boundary as the text-layer path. `tesseract-core-lstm.js`/`.wasm` is deliberately the LSTM-only, non-SIMD engine build rather than the faster SIMD variant tesseract.js can also serve, so `assets/ocr-extract.js` has exactly one engine file to load and hash rather than a runtime SIMD-support branch — the accuracy/speed difference is not meaningful at this tool's low, occasional OCR volume. Every OCR-derived auto-fill is marked with its own confidence tier (visually distinct from a text-layer "strong"/"weak" match) and must be reviewed against the source, per `docs/assets/ocr-extract.js`'s own header comment and the Technical File Consistency Check's "What PDF upload can and can't do" callout.

sha256 (js):
- tabulator-6.5.3.min.js: see repo history / verify with `sha256sum`.
- pdfjs/pdf.min.mjs: `f80490490320511e5df18c580b9edd6b5db8058dceebaf6f161992e0a964b9e2`
- pdfjs/pdf.worker.min.mjs: `8ab0e5e30031b4a06ecfddd5ae9562f0227f830ee7ec9ed1a968b134243d2386`
- tesseract/tesseract.min.js: `000c27d9cd0def655f77b36c72a389c0ab13793aa31cb4d7aab56d09c0afbc7e`
- tesseract/worker.min.js: `576b7df7e3393e137e51849357c9adb53fe7ac1bb69bfa06cf3d61520f182c6d`
- tesseract/tesseract-core-lstm.js: `6510efc4e8b45c5465df30679b9911ffe0071cd2ee982fa064e6f5136ef2de85`
- tesseract/tesseract-core-lstm.wasm: `66b17df6e20c5329a17ffa9c202a47eaa3e32500b253d4c7f38e7f2bc01457c3`
- tesseract/eng.traineddata.gz: `810abad94b8c2c3b6201acfe289dbf41781ff2e0ad4dd1c01a7fce05290dac49`
