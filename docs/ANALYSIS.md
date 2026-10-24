# GEMSDOE92 — Hypothesis analysis and submission design (session 2026-10-24)

## The question: h33-h33-2-b2-zeros scored 0.2778 — why, and can we beat it?

### What 0.2778 actually is

`h33-h33-2-b2` (GEMSDOE32, 2026-10-04T22:00:00Z, uuid e5eb6e7e) is an **owner-reported CLAIM of 0.2778**. It is NOT an ORGANIZER-CONFIRMED receipt: `ledger/submissions.csv` has 23 BUILT rows and zero RECEIPT rows; no submission-page receipt date or score is recorded for it (see `registry/parents/R0.json`, `receipt: null`, IRREGULARITIES 2026-10-23 "No TOP_PUBLIC filled").

Mechanically, the file is plausible as a strong entry: 37,654 unit-mass dots on the H19-5 ridge skeleton, D2.8 Poisson-disk spacing (min nn 2.828 px), zero mass on the mapped catalogue (`d_cat` min 2.236 px, 0 dots ≤ 2 px), exact DTI kernel budget (triangular R=3 px/300 m, alpha 0.2, beta 0.8). Under the DTI algebra, a fixed dot budget spent on non-redundant dots that each reach withheld truth pixels within 3 px maximizes `TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w)`; R0's design (fixed count, spacing floor, off-catalogue placement) follows that algebra. That is *why* it plausibly ranked highest among the listed GEMSDOE site entries (next best listed: 0.2750, 0.2708, 0.2707, 0.2649, 0.2632, 0.2600…).

### Can we generate a submission scoring higher than 0.2778?

**Unknown until an ORGANIZER-CONFIRMED receipt exists.** No local proxy (holdout-DTI, SGMC control, leakage canary) is the organizer metric; the brief (parallel-run protocol rule 3) forbids writing a projection as a score. What we *can* do, within budget, is:

1. Generate a **unique** raster (not a copy of any GEMSDOE site file; lane-checked against locally accessible registry rasters).
2. Validate it locally without human intervention: format gates (CRS EPSG:32611, 3730x3292, geotransform of sample_submission.tif, float32, 1 band, values in [0,1], no NaN inside footprint, zero catalogue mass, dots > 3 px from catalogue).
3. Evaluate it on the spatially-blocked hide-and-recover holdout (pooled DTI + 95% CI) and beat the R0 holdout baseline before spending a submission slot.
4. Publish the TIF with an obvious download path and an executive summary stating exactly whether it is OK to download and submit (locally valid: YES; organizer acceptance/score: only after receipt).

The submission below is generated under that discipline. Its live score relative to 0.2778 (and to the current leaderboard high of 0.4413 / 0.3195 depending on snapshot) is ORGANIZER-CONFIRMED only after upload; the local readout is HOLDOUT-DTI only.

---

## Candidate hypotheses not yet tried in this repo

Tried axes (repo): MASS, PRUNE, SNAP, CONCENTRATION, RELIEF — all reallocate or reposition dots on/near H19-5 support, relief terciles, 1 km catalogue-prior blocks, or edge-response windows ≤ 2 px.

| Rank | Hypothesis | Layer(s) | Physical signature | Why it catches catalogue-missing faults | Difference from repo implementation | Est. DTI gain | Cost |
|---|---|---|---|---|---|---|---|
| 1 | **STEPOVER** (validated this session) | visible catalogue traces (existing_faults/labels) only | Step-over / relay-ramp geometry at trace tips: dots 3–10 px off mapped traces, in the strike-continuation direction of trace tips | Blind geothermal strands localize at 3-D step-overs and relay ramps between mapped traces; these junctions are under-mapped in USGS/INGENIOUS and held-out truth sits just beyond the visible buffer (nearest_visible_to_truth = 3.16 px) | Places NEW dots only off-catalogue (≥3 px) at tip step-overs; SNAP moves existing dots ≤2 px onto edges; PRUNE refills nearest legal pixels; CONCENTRATION uses 1 km block priors | Holdout decides (target: clear R0 0.00370 [0.00301,0.00432]) | Low — local data only |
| 2 | **MAG-EDGE ridges** | Band 3 TMI horiz grad, Band 13 unsigned gravity gradient (19-band stack) | `||∇TMI||` / gravity-gradient ridge crests (demagnetized hydrothermal fault zones) | Blind faults with geophysical expression but no surface trace; not captured by trace-proximity priors | Needs training_features.tif (419 MB owner mirror, gitignored restore); repo SNAP mixes bands and moves dots ≤2 px, never places off-catalogue dots by gradient ridge | Medium | Medium — 419 MB restore |
| 3 | **RAD-ANOMALY** | USGS GeoDAWN radiometrics (DOI 10.5066/P93LGLVQ, public domain; pinned ext_geodawn_rad_u8) | K/Th depletion or eU enrichment halos over hydrothermal alteration | Concealed faults marked by alteration, invisible to structural priors | Not used anywhere in repo; external restore needed (26 MB) | Medium | Medium — external data |
| 4 | **WELLSPRING proximity** | GDR #1391 CC BY 4.0 INGENIOUS geothermometry (pinned gdr_wellspring_in_footprint.csv) | Near-surface geothermal indicators / well geochemistry | Directly targets blind geothermal systems rather than structure | Only used report-only in repo (SGMC control) | Low-medium | Low — 2.1 MB pinned CSV |
| 5 | **TIP-DILATION** (fallback) | visible catalogue traces | Pure distance-to-tip field (no strike alignment) | Same step-over mechanism as #1, simpler | No strike information; lower expected gain than STEPOVER | Low | Low |

**Validated top candidate this session: STEPOVER** (Rank 1). Hypotheses 2–5 are documented for future sessions; 2–4 require external/restored data that must be obtained (pins exist in registry/session_manifest.json) before they are viable.

---

## Method of the validated submission (STEPOVER)

- Holdout: `gems57.buffered_component_draw` (label-blind quadrants, whole-component withholding, `hide_frac=0.20`, `buffer_px=3`, `boundary_px=12`, seed 20) → 11,321 withheld positives across 4 folds / 323 spatial blocks.
- Features derived ONLY from visible faults (`catalogue & ~hidden_all`); visible faults masked pixel-exactly from scoring (`known` mask).
- Candidate domain: footprint & `d_cat > 3 px` (zero catalogue mass; off mapped faults) & within 3–10 px of a visible trace tip (step-over/relay zone).
- Favourability `s(x) = cos²(relative angle between tip→pixel and tip strike) * exp(-(d_tip - 3)/3)` — visible geometry only.
- Dots placed greedily by descending `s`, 1 px minimum spacing, unit mass, count chosen by holdout-DTI sweep (5k/10k/15k).
- Score: pooled DTI, alpha 0.2, beta 0.8, triangular kernel R=300 m (3 px), evaluator `gems57-pooled-hide-v2` — reported as HOLDOUT-DTI with 95% CI and withheld-positive count.
- Leakage canary: single-feature AUC of `s` vs held truth must be < 0.90 (result below).
- Packaging: `gems57.submission_writer` fail-closed writer → all-finite GeoTIFF (zeros outside footprint) + ZIP + receipt JSON; then `gems.gates` MUST-pass format gates vs `sample_submission.tif`.
- Uniqueness (LANE): rank correlation ≤ 0.90 and ≤ 70% of dots within 3 px of every locally accessible registry raster (R0 + GEMSDOE92 releases) — checked on surface before placement and on final dots.

**Labels:** every number hereafter is HOLDOUT-DTI (evaluator version `gems57-pooled-hide-v2`, # withheld positives, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). No projection is written as a score. The organizer high score (0.4413 / 0.3195 depending on snapshot) and the GEMSDOE32 claim (0.2778) are CLAIMS/receipts from other sites, not results of this submission.
