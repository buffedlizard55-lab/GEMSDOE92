# Submission selector — evidence, not a slot recommendation

**Current decision:** no weekly slot is recommended. The local evidence has no candidate that both clears the literal registry-overlap rule and is positive on the available holdout. This plan is an audit summary only; selecting a slot is a separate human decision. No slot was used by the agent.

## Current downloadable candidate

- **File:** `docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.tif`
- **Format:** **OK TO DOWNLOAD**; all 10 local gates pass on the served bytes. One float32 band, EPSG:32611, 3730 × 3292, matching sample-submission transform, all values finite and in [0,1], zero outside the footprint, zero mass on the mapped catalogue.
- **Uniqueness:** saved scan passes against 14 locally accessible registry rasters (surface max Spearman 0.0277; final-dot max Spearman 0.0082; maximum 3-px dot overlap 0.2534). This is not global registry coverage.
- **HOLDOUT-DTI:** evaluator `gems57-pooled-hide-v2`, 11,321 withheld positives, 95% CI `[0.0000, 0.0000]`: candidate 0.0000. R0 proxy baseline 0.0037 `[0.0031, 0.0044]`. Verdict **negative**; not recommended for a slot.
- **Name:** `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f`
- **Note (116 characters):** `h33-h33-2-b2; STEPOVER step-over dots 3-10px off catalogue at visible trace tips; HOLDOUT-DTI 0.0000 [0.0000,0.0000]`
- **Audit:** [`docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-audit.json`](docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-audit.json)

The holdout is catalogue-derived, so its structural zero does **not** establish zero performance on genuinely unmapped faults. It also cannot be used to rescue a candidate as a contest winner. The positive holdout results below fail uniqueness.

## Why the historical `0.2778` cannot be explained as a verified win

`h33-h33-2-b2` is recorded as a **CLAIM 0.2778** from the supplied GEMSDOE32 listing; this repository has no organizer receipt for it. A plausible mechanistic explanation is that a fixed prediction budget, spatial thinning, reduced redundant mass, and placement near structures can benefit a distance-tolerant asymmetric DTI. The available evidence does not prove this caused the reported value. The official public leaderboard page was checked on 2026-10-24 and displayed 0.4413 at #1 (public leaderboard snapshot, not a receipt for this project). The prompt's 0.3195 is an older conflicting snapshot. A higher live score is possible in principle, but no local result forecasts or confirms one.

## Existing arms and disposition

All values in this table are from the recorded local holdout instruments; they are **not** leaderboard scores.

| Candidate | HOLDOUT-DTI evidence | Registry result | Disposition |
|---|---|---|---|
| RELIEF p10 | `gems57-pooled-hide-v2`, 22,663 withheld positives; 0.006045 `[0.005187, 0.006927]`; Δ vs R0 +0.002039 `[0.001483, 0.002504]` | 99.38% of dots within 3 px of R0 | Duplicate under literal rule; no slot |
| DILATATION p10/p12/p15 | `gems57-pooled-hide-v2`, 22,663 withheld positives; p12 0.005779 `[0.004863, 0.006851]`; Δ +0.00177 `[0.00111, 0.00246]` | 99.37–99.40% of dots within 3 px of R0 | Duplicate under literal rule; no slot |
| TIPGAP FAR | `gems57-pooled-hide-v2`, 22,663 withheld positives; 0.002723 `[0.002324, 0.003131]`; Δ vs R0 −0.001283 | 67.00% within 3 px of R0 | Clears local overlap threshold but negative; no slot |
| STEPOVER | `gems57-pooled-hide-v2`, 11,321 withheld positives; 0.0000 `[0.0000, 0.0000]` | Unique within 14-raster local scan | Downloadable negative result; no slot |

The RELIEF/DILATATION results above are not comparable to STEPOVER/TIPGAP across holdout versions and withheld-positive counts. Their internal comparisons use the evaluator versions stated in their run cards. The literal uniqueness rule governs; arrival-set interpretation does not override it.

## Next work and stop conditions

1. Do not run another experiment until the shared experiment budget is explicitly reset and the authorized full feature stack is staged. `.cache/gems_inputs/training_features.tif` is absent in this checkout.
2. Use the 3–5 untried mechanism hypotheses and source-availability notes in [`docs/hypotheses_20261024.md`](docs/hypotheses_20261024.md). The top candidate cannot presently be validated because the competition data download is login-gated here.
3. After data access, test each feature alone as a leakage canary; derive catalogue features from visible segments only; withhold whole segments with a buffer; mask visible faults pixel-exactly; use pooled DTI α=0.2, β=0.8, 300 m triangular kernel, and report withheld count + 95% CI.
4. Check surface correlation before placement and final-dot overlap/correlation after placement against the registry. Stop and log duplicate if a threshold is crossed. Run format validation on the actual site-served bytes and match its SHA to the audit receipt.
5. Only then can the separate human selector consider spending a weekly slot. Copy a live score only from the organizer submission-page receipt into `ledger/submissions.csv`.

## Sources

- [DrivenData competition problem, provided features, and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official competition rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [Faulds et al. structural investigations of Great Basin geothermal fields](https://www.osti.gov/servlets/purl/1110517)
