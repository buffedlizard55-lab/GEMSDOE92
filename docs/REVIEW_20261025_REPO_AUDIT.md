# GEMSDOE92 repository review — 2026-10-25

## Scope and decision

This is a repository/code-and-evidence audit, not a new geological experiment. The active DRAINAGE-KNICK run card records experiment `1/3`; the parallel-run instruction limits work to a single method lane and sets a maximum of three experiments. No new experiment, submission slot, or organizer submission was used in this review.

**Current artifact:** `docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif` is **OK TO DOWNLOAD FOR RESEARCH** after local automated validation, but **DO NOT SUBMIT** (`verdict: negative`, `submission_eligible: false`). This is not organizer acceptance. SHA-256: `ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910`.

## Repository verification (this run)

- `python -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pytest tests -q`: **367 passed**, 126 Rasterio/Affine pending-deprecation warnings. `.venv` is ignored and is not a deliverable.
- `.venv/bin/python scripts/check_site.py`: **PASS**, 63 served rasters passed the site's format gates. The checker reported its explicit HTML `data-primary` as `h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif`.
- `.venv/bin/python -m gems validate docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif --reference data/bridge/sample_submission.tif`: **9 gates PASS**. Re-read checksum matched the run card; single-band float32, EPSG:32611, 3730×3292, transform matches reference, values in `[0,1]`, no NaN in footprint, zeros outside.
- Git working tree was clean before this report. Tests and the site checker verify software/format invariants; they do not establish leaderboard performance or organizer eligibility.

## Scientific result and interpretation

The run card reports **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, strict fold-visible `d_visible > 2 px`, 8 folds, 1,000 spatial-block bootstrap draws): **0.061728 [0.047046, 0.075316]**. This is below the recorded within-repository Rule-2 holdout best `0.113316`; do not compare these values to an organizer leaderboard score as if they were the same instrument.

The supplied GEMSDOE32 result `0.2778` and prompt's `0.3195` / `0.4413` leaderboard figures are not backed by a current DrivenData receipt in this checkout. The repository's analysis appropriately calls 0.2778 a **CLAIM**: thinning/spacing the positive predictions can plausibly reduce false-positive mass under a distance-tolerant metric, but available evidence cannot establish why it scored that way or predict a higher organizer score. The current HOLDOUT-DTI does not support a claim of beating 0.2778.

DRAINAGE-KNICK targets persistent terrain knickzones × basement-depth edge × shear. The run card's single-feature leakage canary maximum is 0.597114 (<0.90). Local-registry max correlation/overlap are 0.063413 / 0.477320. Public comparison is explicitly incomplete: 747 rasters read, 705 download failures, so the scan is not exhaustive; moreover literal overlap reaches 1.0 against a dense full-footprint registry surface. Under the supplied literal rule, this is a duplicate stop regardless of byte uniqueness or low correlation. The byte hash only establishes distinct file bytes, not a distinct scientific surface or permission to submit.

## Irregularities requiring attention

1. **The site has multiple competing “current” declarations.** The first banner in `docs/index.html` says the newest lane is KNICKLOQO, while the automated site check's explicitly tagged primary is the older COULOMBDM TIFF. README's opening artifact names DRAINAGE-KNICK; elsewhere it summarizes still other lanes. These are separate archived results, not interchangeable primary status. Before a site release, reconcile the top-level designation and label every historical lane explicitly.
2. **The download artifact is not submit-cleared.** Its range/CRS/shape/transform are valid, but holdout is below the repository best and the public-registry overlap rule fails. Do not present its download button as permission to upload to DrivenData.
3. **Evidence provenance is bounded.** The run card reports a partial public GitHub raster scan with 705 failed downloads; the documented data bridge is owner-mirror sourced and not organizer-authenticated. No competition-page receipt was available to verify the cited score claims.
4. **No live official-source revalidation is asserted here.** This audit uses repository files and local computation. It does not claim current leaderboard, policy, or source-page contents were independently refreshed.

## Recommended next steps (no slot spent)

- Fix the website's single source of truth for the latest artifact: derive the prominent banner, README summary, and `data-primary` from one run-card-backed record; ensure the visible status says both “OK TO DOWNLOAD FOR RESEARCH” and “DO NOT SUBMIT” where applicable.
- Keep the negative result as a deliverable. Do not promote DRAINAGE-KNICK or use a weekly slot. The mandatory literal duplicate rule is currently independently disqualifying.
- For any future candidate, start with the shared cached feature stack and fold-rebuilt evaluator, run each feature's leakage canary, test the proposed surface against the registry before placement and the final dots after placement, and stop at three experiments. Do not use static full-catalogue masking as a substitute for fold-visible withholding.
- Refresh public-registry evidence with transparent coverage and failures; never describe an incomplete scan as exhaustive. Verify any leaderboard number from a dated organizer receipt before presenting it as confirmed.

## Run card (review artifact)

```json
{
  "hypothesis": "Repository review only; no new geological hypothesis or raster was tested.",
  "mechanism": "Three-pass source/evidence/code inspection plus pytest, site gates, and independent artifact-format validation.",
  "named_non_fault_process": "Not applicable to this review; the audited DRAINAGE-KNICK run card names shorelines, stratigraphic contacts, fan toes, and DEM seams.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positives": 22663,
    "value": 0.061728,
    "ci95": [0.047046, 0.075316]
  },
  "correlation_overlap_vs_registry": {
    "evidence_class": "REGISTRY-MEASUREMENT",
    "local_worst_abs_spearman": 0.063413,
    "local_worst_overlap": 0.477320,
    "public_literal_overlap": 1.0,
    "public_scan_complete": false,
    "public_rasters_read": 747,
    "public_download_failures": 705
  },
  "raster_sha256": "ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910",
  "validator_output": {
    "no_nan_inside_footprint": true,
    "values_in_0_1": true,
    "crs_shape_transform_match": true,
    "site_rasters_gated": 63,
    "tests": "367 passed"
  },
  "submission_name": "GEMSDOE92-DRAINAGE_KNICK-20261025",
  "note": "terrain knick + basement edge + shear; research only; negative holdout/registry gate",
  "verdict": "negative"
}
```
