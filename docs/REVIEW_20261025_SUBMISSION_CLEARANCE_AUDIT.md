# Post-merge submission-clearance audit — 2026-10-25

## Decision

**No current TIFF is cleared for a weekly slot. Do not submit KNICKLOQO or LISTRICDIP.** The homepage's latest research download remains LISTRICDIP updip50 (SHA-256 `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`). KNICKLOQO remains a separate local HOLDOUT-DTI best (SHA-256 `8ad4a8c2cd8e1fd989b63c752d5e9efc4ba87a2f608ccd551e8787648920d347`). Both are format-valid research artifacts; neither is slot-cleared under the unchanged literal registry rule.

This review was extended after main merged PR #89, titled “SUBMISSION READY: KNICKLOQO standalone cleared for submission.” That PR's status conflicts with the standing task's binding uniqueness rule. This report records and corrects that conflict; it does not alter historical raster bytes or claim an organizer decision.

## Concrete policy/evidence conflict

`docs/downloads/knickloqo_submission_run_card.json` records the literal `17GEMSDOE E-proba-multiscale` witness as covering all `5,167,373` footprint pixels and the candidate's literal forward overlap as `1.0` (original run card fields `uniqueness.literal_witness`, lines 177–182). The user-specified rule says `>70% within 3 px` is duplicate/stop; therefore `1.000 > 0.70` is a stop. The PR then declared the witness “NOT BINDING,” used `dual_reading_decision` matched-budget comparisons, and set `submission_eligible: true` (original fields lines 156–200). That is a policy substitution, not a new measurement, and violates the standing instruction not to redefine the threshold. The corrected run card preserves matched-budget results as diagnostics, records the literal duplicate stop as operative, and sets `verdict: negative`, `submission_eligible: false`.

The old run card's values remain historical measurements; the corrected eligibility field is the policy decision applied by this review. No full registry scan was rerun here. In particular, the old matched-budget `0/1,412` outcome is not represented as current literal-rule clearance.

## Unsupported score language withdrawn

`SUBMISSION_READY.md`, `docs/SUBMIT_NOW.html`, `docs/BEAT_0_2778.md`, `docs/index_new.html`, and root `validate_submission.py` made “cleared/submit now” or live-score projection claims. They have been corrected because:

- KNICKLOQO `0.010788 [0.009468, 0.012201]` and LISTRICDIP `0.005420 [0.004294, 0.006551]` are internal **HOLDOUT-DTI** outputs (`gems57-pooled-hide-v2`, 22,663 withheld positives), not organizer scores.
- The `0.2778` GEMSDOE32 figure is an unverified **CLAIM** in this checkout; the ledger has no organizer-confirmed receipt. A local holdout value cannot be translated into `0.28–0.32` or `0.35–0.40` organizer points without calibration evidence.
- GeoTIFF format validation establishes encoding/range compatibility only. It does not establish registry uniqueness, hidden-label performance, or competition acceptance.
- `validate_submission.py` previously printed “FILE IS READY FOR SUBMISSION” and a score estimate even when the uniqueness gate was not evaluated; its successful output now explicitly says format checks are not submission clearance.

No organizer receipt was found or created in this review. No upload or weekly slot was used.

## Unvalidated FKP code prototype from PR #89

`gems/flexure_knick_province.py` was added with an unsupported “expected improvement” claim but no accompanying holdout receipt or candidate raster. That projection has been replaced with “unknown,” and `fit_fkp_loqo` now fails closed with `NotImplementedError` until the implementation is corrected. Do not treat it as an implemented/validated winning lane. Source inspection identifies blockers before it can be run or promoted:

1. **Shape inconsistency:** `compute_province_aware_features` standardizes `dem_band[mask]` etc. into flattened per-quadrant vectors of different lengths, then calls `np.stack`; this cannot produce a uniform `(features, rows, cols)` stack for unequal quadrant areas. The masked full-grid arrays created just above are not used.
2. **Distance-transform/label semantics:** `fit_fkp_loqo` applies `distance_transform_edt(existing_faults > 0)`. With a binary fault mask, the transform measures distances inside the positive mask to background zeros; outside it is zero. The later `(weights > 5)` labels therefore do not implement “far from known faults is positive” as the comments claim and may be single-class.
3. **LOQO prediction leakage:** its fold loop fits a model on three quadrants, then predicts over *all* pixels for every fold and averages all four predictions. A pixel's own quadrant is included in three models; this is not a held-out-quadrant prediction. No spatial-buffer enforcement is visible in that function.
4. **Mask/writer contract:** the final writer uses `sample > 0` for the footprint and sets `nodata=0.0`; those assumptions need verification against the shared sample-mask and submission-writer contract before any output can be considered.
5. **No experimental evidence:** the declared expected improvement is unsupported; no model was run, no canaries or blocked holdout are reported for FKP, and no surface/final-dot uniqueness check exists for an FKP candidate.

The pinned full feature stack is absent from the cache, and the code has no tests in the merged change. Do not run it or promote it until the shape, label, fold-isolation, masking/writer, preregistration, and required uniqueness issues are corrected and tested. This is a source review, not a claim that the prototype generated a TIFF.

## Three-pass and project-state implications

- **Pass 1 — evidence:** compared the new merged run card, static submission pages, validator script, FKP source and existing audits. Verified both TIFF hashes against local bytes earlier in the review. No portal/leaderboard access or organizer receipt was available.
- **Pass 2 — correction:** reverted the false submission-ready language, removed unsupported live-score estimates, updated the new run-card eligibility decision to the unchanged literal threshold, and made the format validator format-only.
- **Pass 3 — recheck:** added automated assertions for the negative eligibility state, page-level wording, and quarantined FKP prototype. Final checks: 376 pytest tests passed (126 nonfatal Rasterio/Affine warnings); site checker passed all 66 served TIFFs; `validate_submission.py` passed format gates and explicitly stated that this is not submission clearance; manifest, parent, and ledger checks passed (97 rows, no best receipt); staged and unstaged `git diff --check` passed.

For current-primary status, ranked conditional hypotheses, and documented source availability caveats, see [`REVIEW_REPOSITORY_20261025.md`](REVIEW_REPOSITORY_20261025.md). The linked official products were not queried for exact AOI coverage in this runtime; do not treat them as downloaded or spatially validated.

**Maximize P(Win):** preserve the slot and do not turn local metrics into a score forecast. **Own the Outcome:** correct the public guidance, preserve the contradictory upstream claim as documented history, and report the prototype blockers before any candidate is promoted.
