# Vendored third-party assets

Vendored (not hot-linked) so the site stays self-hosted, pinned and reviewable. Loaded lazily only by the pages that need them.

| File | Package | Version | License | Source | Purpose |
|---|---|---|---|---|---|
| tabulator-6.5.3.min.js / .css | tabulator-tables (npm) | 6.5.3 | MIT | https://tabulator.info / npm registry tarball | Exception-workbench data grid in the Regulatory Integrity Scanner |

Update strategy: bump deliberately, re-pin, re-hash, re-run E2E. Removal strategy: the Scanner falls back to its plain findings table if the grid asset fails to load — no evidence record depends on the grid.
sha256 (js): see repo history / verify with `sha256sum`.
