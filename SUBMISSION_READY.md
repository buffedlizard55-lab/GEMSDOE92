# No submission-cleared TIFF — GEMSDOE92

**Current decision: DO NOT SUBMIT any TIFF in this repository or spend a weekly slot.**

The automated format gate can establish GeoTIFF compatibility, but that is not sufficient for submission eligibility. The binding literal registry protocol is stopped by a pinned public raster that is positive in all `5,167,373` footprint pixels. Therefore every nonempty in-footprint raster has 3-pixel forward overlap `1.0`, exceeding the `0.70` limit. Matched-budget comparisons are diagnostic only and do not override this stop.

## Available download (research only)

The current research artifact listed on the site is LISTRICDIP updip50:

- [GeoTIFF](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif) — **OK TO DOWNLOAD FOR RESEARCH; NOT CLEARED FOR SUBMISSION**
- [Run card](docs/downloads/listricdip_run_card.json) · [audit](docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-audit.json) · [automated submit-guide/status page](docs/listricdip.html)
- Exact SHA-256: `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`
- Record-only name: `GEMSDOE92-LISTRICDIP-updip50-20261025`
- Record-only note (77/140 chars): `LISTRICDIP updip50: 37654 listric-offset dots; HOLDOUT-DTI 0.005420; negative`

Its **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, static `d_cat > 2` instrument) is `0.005420 [0.004294, 0.006551]`. This is local validation, not an organizer score; the run card records a negative verdict and literal-overlap stop. No score for this artifact is implied by the name/note fields.

## Why the previous “submission ready” claim was withdrawn

A previous KNICKLOQO page interpreted `dual_reading_decision`'s matched-budget result as submission clearance while explicitly excluding the full-footprint witness. That conflicts with the binding project rule, which applies literal forward overlap to every registry raster. The old recommendation and score projection were unsupported and are superseded. The KNICKLOQO TIFF remains available only as a historical research artifact; its format validity does not make it eligible.

The user-reported GEMSDOE32 `0.2778` and leaderboard values `0.3195` / `0.4413` are not verified organizer receipts in the local ledger. There is no defensible live-score projection here. See [the careful assessment of the `0.2778` claim](docs/BEAT_0_2778.md) and the [current three-pass repository review](docs/REVIEW_20261025_REPOSITORY_REVIEW.md).

## If a future file is actually cleared

Only after the literal gate is resolved under an explicitly authorized rule, a candidate beats the locked holdout control, passes the single-feature leakage canaries and pre/post-placement uniqueness checks, and its exact bytes pass the automated CRS/shape/transform/range validator should the selector consider a weekly slot. The human account holder still uploads the TIFF and enters its name/note on DrivenData; the project does not claim to submit automatically.
