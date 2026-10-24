# Submission guide — current status and future-only procedure

## Current decision: do not submit any current download

**No candidate is cleared for a weekly competition slot.** Every TIFF currently served from this repository is a research-only historical artifact with a negative/blocked verdict. The latest prior research artifact came from the SPRINGALIGN lane; it was not generated in this review. No new candidate or weekly slot was generated/used in this review.

A hash-verified public registry raster is positive on all **5,167,373 / 5,167,373 footprint cells**. This is a **REGISTRY-MEASUREMENT**, not a competition score. Under the literal >70% within-3-pixel rule, every nonempty in-footprint candidate overlaps this witness by 100% and must stop. The single witness is decisive for rejection, but is not an exhaustive public-registry scan. Do not exempt a dense raster, change the threshold silently, or create an empty/cosmetic TIFF to evade it.

For current receipts and caveats see:

- [`downloads/current_status.json`](downloads/current_status.json)
- [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json)
- [Three-pass repository review](REPO_REVIEW_20261024.md)
- [Homepage / research downloads](index.html)

## Latest prior research file — SPRINGALIGN (not for submission)

**OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT.** The saved exact-byte audit passes local format gates, but the saved scientific result is negative and the public witness blocks it under the literal rule. The filename uses the future date stamp `20261025`; the saved run card does not contain a generation timestamp, so that date is not independently authenticated.

- File: [`downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif`](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif)
- SHA-256: `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1`
- Project/run-card ID: `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025` (repository identifier; a separate portal Name field was not verified)
- Optional form note (94 characters): `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5`
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives: 0.0048650690, 95% CI [0.0040254482, 0.0057850159]. Paired difference vs saved RELIEF p10 holdout best: −0.0011800634, 95% CI [−0.0020652571, −0.0003371520]. Not a competition score.
- **REGISTRY-MEASUREMENT:** local 28-raster final-dot maximum forward overlap 0.670 vs R0; a single full-footprint-positive public witness gives 1.0 overlap for every nonempty in-footprint candidate under the literal rule.
- Evidence: [exact-byte format audit](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-audit.json) · [experiment run card](downloads/springalign_run_card.json) · [source card](../evidence/springalign_run_card.json) · [analysis](ANALYSIS_20261025_SPRINGALIGN.md).

## Earlier ANASIG research archive

**OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT.** Its zeros-outside GeoTIFF has a saved local format audit, but its verdict is negative and its measured forward overlap against the same full-footprint witness is 1.0.

- File: [`downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif`](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif)
- SHA-256: `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`
- Archive-only name: `GEMSDOE92-ANASIG-f45Atop-20261024`
- Archive-only note (84 characters): `h33-h33-2-b2; ANASIG f45Atop 16944 far dots on analytic-signal ridges >3px off H19-5`

Do not paste historical names/notes into a competition form.

## Future submission procedure — conditional, not for current files

Only follow these steps if a future exact-byte candidate audit says `submission_eligible: true`, the experiment card says `verdict: promote`, all required holdout/leakage/pre-placement/final-dot/format gates pass, and a separate human selector authorizes a slot within the then-current quota.

1. Open the candidate’s exact-byte audit and confirm its filename and SHA-256. A format-only pass does not establish eligibility.
2. Download that audit’s `-zeros.tif` unchanged; do not re-encode it. If using a ZIP, it must contain exactly one TIFF.
3. Sign in to the registered competitor account and open the [official DrivenData GEMS submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/). This project does not store credentials or upload for you.
4. Select the audited `.tif` or a ZIP containing one TIFF.
5. If the form presents its optional note field, copy the unique candidate note (≤140 characters) from that exact run card. The descriptive filename and run-card ID identify the artifact within this repository; do not assume the portal has a separate Name field unless it is displayed.
6. Submit only after the human selector authorizes the exact candidate and checks the weekly quota. Record the actual organizer receipt in `ledger/submissions.csv`; never record HOLDOUT-DTI, MODEL, or PROXY as a competition score.

## Prevent the range error

The portal error previously reported was `Predicted values must be in range [0, 1]`. The automated local checker rereads each served zeros-outside raster and validates one float32 band, template CRS/shape/transform, finite in-footprint values in [0,1], no NaNs inside the footprint, and the configured outside-footprint convention. Use the audited zeros-outside TIF unchanged. These checks address format/range only; they do not promise a score, uniqueness, organizer eligibility, or acceptance.

Run:

```bash
.venv/bin/python scripts/check_site.py
```

## Cautious score context

The prompt and repository associate GEMSDOE32 `h33-h33-2-b2` with **CLAIM 0.2778**. There is no organizer receipt for it in this checkout. The prompt’s leaderboard snapshots `0.3195` and `0.4413` conflict; neither was freshly verified in this review. Any mechanism involving fixed-budget allocation, spatial thinning, or known-fault exclusion is a hypothesis, not causal evidence. The saved local holdout best is **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives), 0.0060451324, 95% CI [0.0051870225, 0.0069268388]; it was not rerun here and is not a competition score.

**Evidence labels:** HOLDOUT-DTI = local spatial holdout; REGISTRY-MEASUREMENT = comparison to a registry raster; CLAIM = reported without receipt; ORGANIZER-CONFIRMED = copied from an actual submission receipt. Never equate them.
