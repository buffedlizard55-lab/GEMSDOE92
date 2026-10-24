# Submission status — no artifact cleared

> **DO NOT SUBMIT any TIFF or ZIP in this repository.** The current ANASIG zeros-outside file is valid for research download only. It fails the literal public-registry overlap gate against one fresh, hash-verified witness. No submission slot was used, and this page does not authorize an upload or choose a slot.

## Current research artifact

- [Research download — ANASIG GeoTIFF — DO NOT SUBMIT](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif)
- [Research ZIP — DO NOT SUBMIT](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.zip)
- SHA-256: `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`
- Status receipts: [10-gate format audit](downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json) · [fresh single-witness measurement](downloads/public_witness_anasig.json) · [current run card](downloads/current_registry_stop_run_card_20261024.json)

## Why submission is blocked

**REGISTRY-MEASUREMENT:** The exact public 17GEMSDOE E-proba witness has positive support on every competition-footprint cell. The existing ANASIG output has 100% forward 3-pixel overlap with it; the literal stop limit is greater than 70%. Its 3-pixel halo covers every allowed cell, so any nonempty in-footprint raster fails. This is a single-witness rejection, not a full registry scan. The candidate's pre-placement surface was not checked against this witness.

The older 1,279-raster / 11GEMSDOE scan belongs to the visible-collar candidate; do not attribute it to ANASIG. The fresh ANASIG check is the single-witness 17GEMSDOE measurement linked above.

The file passes local format gates (one-band float32, EPSG:32611, 3730×3292, matching transform, finite [0,1], no NaN inside, zeros outside, zero catalogue mass). **Format validity is not submission eligibility.**

## Scores and limitations

Prior ANASIG **HOLDOUT-DTI**: evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives, 95% CI: `0.004967 [0.004098, 0.005940]`. Paired HOLDOUT-DTI difference vs the prior holdout-best RELIEF p10: `−0.001078 [−0.002034, −0.000112]`. These local estimates are not organizer scores and were not rerun in this review.

GEMSDOE32 `0.2778` is a **CLAIM** without a verified receipt. The conflicting `0.3195` and `0.4413` values are **LEADERBOARD-SNAPSHOT** records, not independently refreshed this review. See [`ledger/score_claims.csv`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/ledger/score_claims.csv) and [`executive-summary.html`](executive-summary.html).

## Current action

No form instructions, active name/note, or upload recommendation are given because no artifact is eligible. Any future selector action must be separate, use a new exact artifact whose machine-readable receipt marks it eligible, and respect the weekly cap. This agent does not log in, upload, or spend a slot.
