# Submission executive summary

## Download status

**OK TO DOWNLOAD — format-valid.** The project landing page offers a zeros-outside, all-finite float32 GeoTIFF that matches the sample grid and passes all local MUST gates. The downloadable raster is unique within the recorded 14-raster local registry scan.

**NOT RECOMMENDED FOR A WEEKLY SUBMISSION SLOT.** The STEPOVER candidate is a negative result on the local holdout. Local validation and local uniqueness do not imply contest performance or organizer acceptance.

- [Download GeoTIFF](downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.tif)
- [Download ZIP containing one TIFF](downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.zip)
- [Machine audit receipt](downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-audit.json)

**Submission name:** `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f`

**Optional note (116/140 characters):** `h33-h33-2-b2; STEPOVER step-over dots 3-10px off catalogue at visible trace tips; HOLDOUT-DTI 0.0000 [0.0000,0.0000]`

## Evidence

- **HOLDOUT-DTI** — evaluator `gems57-pooled-hide-v2`; 11,321 withheld positives; pooled DTI α=0.2, β=0.8, 300 m triangular kernel; 95% CI: `0.0000 [0.0000, 0.0000]`. R0 proxy baseline: `0.0037 [0.0031, 0.0044]`. Verdict negative.
- **Local registry scan:** 14 locally accessible rasters; the saved card reports worst surface Spearman 0.0277, final-dot Spearman 0.0082, and maximum 3-px overlap 0.2534. This is not proof of global uniqueness.
- **Local format preflight:** single-band float32, EPSG:32611, shape 3730×3292, sample transform match, all values finite in [0,1], no NaN inside footprint, zeros outside, zero positive catalogue mass. Audit SHA-256 matches the served TIF.

## Competition form

The human competitor must sign in to the [DrivenData submissions page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/), select “New submission”, upload the `.tif` (or ZIP containing exactly one TIFF), and paste the name and optional note above. Do not submit this candidate unless a human explicitly chooses to override the negative recommendation. After upload, record the score/date from the submission-page receipt as **ORGANIZER-CONFIRMED**. The agent does not authenticate, upload, or spend a slot.

See the [public landing page](index.html), [ranked hypotheses and data access assessment](hypotheses_20261024.md), and [current slot plan](../SLOT_PLAN.md).
