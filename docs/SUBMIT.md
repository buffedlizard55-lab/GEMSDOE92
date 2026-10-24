# Submission guide — current status and future-only procedure

## Current decision: do not submit any current download

**No candidate is cleared for a weekly competition slot.** Every TIFF currently served from this repository is a historical research artifact with a negative/blocked verdict. No new candidate was generated and no slot was used in the current review.

A hash-verified public registry raster is positive on all **5,167,373 / 5,167,373 footprint cells**. This is a **REGISTRY-MEASUREMENT**, not a competition score. Under the literal >70% within-3-pixel rule, every nonempty in-footprint candidate overlaps this witness by 100% and must stop. The single witness is decisive for rejection, but is not an exhaustive public-registry scan. Do not exempt a dense raster, change the threshold silently, or create an empty/cosmetic TIF to evade it.

For current receipts and caveats see:

- [`downloads/current_status.json`](downloads/current_status.json)
- [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json)
- [Three-pass repository review](REPO_REVIEW_20261024.md)
- [Homepage / research downloads](index.html)

## Research-only ANASIG file

**OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT.** The historical ANASIG zeros-outside GeoTIFF has a saved local format audit, but its verdict is negative and its measured forward overlap with the full-footprint witness is 1.0.

- File: [`downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif`](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif)
- SHA-256: `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`
- Archive-only name: `GEMSDOE92-ANASIG-f45Atop-20261024`
- Archive-only note (84 characters): `h33-h33-2-b2; ANASIG f45Atop 16944 far dots on analytic-signal ridges >3px off H19-5`

The name/note above are for historical traceability; do not paste them into a competition submission form.

## Future submission procedure — conditional, not for current files

Only follow these steps if a future exact-byte candidate audit says `submission_eligible: true`, the experiment card says `verdict: promote`, all required holdout/leakage/pre-placement/final-dot/format gates pass, and a separate human selector authorizes a slot within the then-current quota.

1. Open the candidate’s exact-byte audit and confirm its filename and SHA-256. A format-only pass does not establish eligibility.
2. Download that audit’s `-zeros.tif` unchanged; do not re-encode it. If using a ZIP, it must contain exactly one TIFF.
3. Sign in to the registered competitor account and open the [official DrivenData GEMS submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/). This project does not store credentials or upload for you.
4. Select the audited `.tif` or one-TIFF ZIP.
5. Copy the unique submission name and note (≤140 characters) from that same candidate’s audit. Never use the archive-only fields above.
6. Submit only after the human selector authorizes the exact candidate and confirms the weekly quota. Record the actual organizer receipt in `ledger/submissions.csv`; do not record HOLDOUT-DTI, MODEL, or PROXY as a competition score.

## Prevent the range error

The portal error previously reported was `Predicted values must be in range [0, 1]`. The automated local checker rereads each served zeros-outside raster and validates one float32 band, template CRS/shape/transform, finite in-footprint values in [0,1], no NaNs inside the footprint, and the configured outside-footprint convention. Use the audited zeros-outside TIF unchanged. These checks address format/range only; they do not promise a score, uniqueness, organizer eligibility, or acceptance.

Run:

```bash
.venv/bin/python scripts/check_site.py
```

## Cautious score context

The prompt and repository associate GEMSDOE32 `h33-h33-2-b2` with **CLAIM 0.2778**. There is no organizer receipt for it in this checkout. The prompt’s leaderboard snapshots `0.3195` and `0.4413` conflict; neither was freshly verified in this review. A possible mechanism involving fixed-budget allocation, spatial thinning, or known-fault exclusion is only a hypothesis, not causal evidence. The best saved local result is **HOLDOUT-DTI** (evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives), 0.006045, 95% CI [0.005187, 0.006927]; it was not rerun here and is not a competition score.

**Evidence labels:** HOLDOUT-DTI = local spatial holdout; REGISTRY-MEASUREMENT = comparison to a registry raster; CLAIM = reported without receipt; ORGANIZER-CONFIRMED = copied from an actual submission receipt. Never equate them.
