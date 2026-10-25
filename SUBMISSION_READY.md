# Current submission-status override — research downloads only

**DO NOT SUBMIT any current TIFF or spend a weekly slot.** This file replaces the “CLEARED FOR SUBMISSION” instructions merged in PR #89. The literal registry gate is binding for this review: the pinned `17GEMSDOE` raster is positive at all `5,167,373` footprint cells, so every nonempty in-footprint prediction has 3-px forward overlap `1.000 > 0.70` and must stop before placement.

## Research artifact: KNICKLOQO standalone

- [Download TIFF for research only](docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif) · [one-TIFF ZIP for research only](docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.zip)
- TIFF SHA-256: `8ad4a8c2cd8e1fd989b63c752d5e9efc4ba87a2f608ccd551e8787648920d347`
- ZIP SHA-256: `4b31db8b8ba3e6abff9397d700a5814669d00c82f2bad44554c1577ee4dc1767`
- Directly measured TIFF metadata: 149,177 bytes; one-band `float32`; `EPSG:32611`; 3,730 rows × 3,292 columns; 100 m pixels; transform origin `(243350, 4508550)`; no nodata. The embedded ZIP TIFF hash matches the TIFF above.
- Format validity supports research download only. It does not establish uniqueness under the binding rule, holdout promotion, organizer acceptance, or permission to submit.

## Evidence and decision

The older KNICKLOQO static **HOLDOUT-DTI** is `0.010788 [0.009468, 0.012201]` (`gems57-pooled-hide-v2`, 22,663 withheld positives); it is a local evaluation, not a competition score. The public registry report records the literal duplicate result as `1.0`, `unique_under_literal_rule: false`, and `stop_required: true`. A separate merged run card called the raster eligible under `dual_reading_decision`; that alternate-policy claim does not satisfy the literal stop.

The previously published live-score projection of `0.28–0.32` (and optimistic `0.35–0.40`) is withdrawn: no organizer receipt or independent evidence supports it. The user-provided `GEMSDOE32` `0.2778` remains an unverified **CLAIM**, not a verified target score.

- [Three-pass repository audit and limitations](docs/REVIEW_20261025_REPO_AUDIT.md)
- [Binding literal-gate review](docs/REVIEW_376A8469.md)
- [Historical KNICKLOQO run card](docs/downloads/knickloqo_submission_run_card.json) — includes an explicit current-review override and preserves the original alternate-policy claim for audit.
- [Original KNICKLOQO analysis](docs/ANALYSIS_20261025_KNICKLOQO.md)

**No TIFF or experiment was generated for this review. No weekly slot was used. No organizer-confirmed score receipt is present.**
