# Hypotheses ranked BEFORE the build — session 2026-10-24 (branch `arena/949d4182-gemsdoe92`)

Evidence classes used everywhere: **CLAIM** (operator-reported leaderboard score, no organizer
receipt in this repo) · **MODEL** (algebraic inversion / projection, never a score) ·
**REGISTRY-MEASUREMENT** (measured on cached public GEMSDOE rasters) · **HOLDOUT-DTI** (shared
hide-and-recover evaluator) · **OFFICIAL** (DrivenData / DOE text, link given).

## 0. What the live record already tells us (inputs to the ranking)

| rung (nested rasters, measured subset relations) | dots removed | claimed score | step |
|---|---:|---:|---:|
| H19-5 skeleton (binary) | — | 0.1922 | |
| → D1.5 thinning | 61,062 | 0.2477 | +0.0555 |
| → D2.8 thinning | 15,979 | 0.2600 | +0.0123 |
| → SOLO: drop the 3,891 dots at exactly 1.0 px from the catalogue | 3,891 | 0.2708 | +0.0108 |
| → R0: drop the 2,545 dots at 1.41–2.0 px | 2,545 | 0.2778 | +0.0070 |

* Per-dot gain of both catalogue-flank rungs is 2.78e-6 and 2.75e-6; the zero-credit ceiling at
  these operating points is 2.9e-6 (MODEL). Both groups carried ≤ ~7 units of true-positive
  credit out of ~5,070 — they were essentially pure false positives. The scorer masks the mapped
  catalogue (OFFICIAL: DrivenData forum thread 11516, staff reply 2026-09-16) and "new fault" means
  *any fault pixel not already captured by USGS/INGENIOUS* (thread 11536).
* Added groups behave the other way: **R0 + 1,200 "geothermal PINN" dots = 0.2750** (CLAIM;
  measured set relation: R0 ⊂ that raster) implies ~0.008 credit per added dot, below the random-
  placement level (0.023) and an order of magnitude below R0's own 0.134.
* Break-even: a dot must earn ≥ ~0.056 credit to raise DTI at this operating point (MODEL).

## 1. Ranked hypotheses (all untried in this repository)

Ranking key = expected DTI gain × P(valid) ÷ cost, with eligibility under the 70 % / 0.90 lane rule.

| # | hypothesis | layers | physical signature & mimic | why it can catch catalogue-missing faults | how it differs from the repo | expected DTI gain (MODEL / prior) | cost |
|---|---|---|---|---|---|---|---|
| **1** | **LCS — LB-calibrated lane consensus.** Select dots where several *independent* registry lanes agree, with per-lane vote weight = its leaderboard-implied credit per dot; ≥ 33 % of dots forced outside every single registry raster's 3 px halo; vote excess measured *inside* distance-to-catalogue strata | registry lane rasters (10 voters) + d_cat; H19-5 only for the halo-survival profile | multi-modality agreement (potential-field edges ∧ slope breaks ∧ radon ∧ strain …). Mimic it does **not** remove: range-front lithologic contacts / escarpments shared by all potential-field lanes; mimic it **does** address: geophysical re-detection of mapped faults (halo-survival factor + stratified excess) | far dots sit only where ≥ 2 lanes with *different* physics fire, instead of at a single uncalibrated surface (BREAKLINE-style) whose far dots measured ~random credit | first lane that uses the registry as an ensemble with CLAIM-calibrated weights and a leave-one-lane-out credit model; selection under a per-raster overlap cap over all 924 distinct registry rasters | −0.02 … +0.03 around R0; central ≈ 0 to +0.01 (see §3) | low: registry already cached |
| 2 | Catalogue-trained U-Net (organizers' own reference approach) with DTI-optimal thresholding, catalogue masking and spatially blocked CV | 19 bands | fault-like potential-field/topographic signatures learned from 60,988 mapped px; mimic: whatever the catalogue labels also carry (range fronts) | learns signatures, not positions; new faults share signatures with mapped ones | the repo's supervised lanes were pixel GBDTs (live 0.03–0.04); no CNN, no masked-halo-aware loss | unknown; leaderboard cluster ≈ 0.33 suggests ceiling ≫ R0, but not attributable to this | high: CPU-only sandbox, hours of training; organizers' notebook is GPU-oriented |
| 3 | Skeleton-continuity prune: drop dots on isolated 1-px / very short skeleton components | band-derived H19-5 geometry | faults are continuous; mimic: threshold noise and survey-line artefacts. The D2.8 autopsy reports 10,099 of 44,090 dots (22.9 %) on isolated 1-px components (CLAIM of an earlier session; recompute before use) | removes false positives only; adds nothing | R0-subset ⇒ lane-duplicate by the literal rule, so it can only serve as an *inner-core rule* | +0.003 … +0.010 if those dots sit below break-even | low |
| 4 | Calibrated halo-rung extension (B3/B4/B5) | d_cat | re-detection halo of mapped faults | removal only | already built as PRUNE rungs, never scored; halo-survival model puts d ∈ (2,3] at ~0.05 credit, i.e. ≈ break-even | −0.001 … +0.003 | trivial; lane-duplicate |
| 5 | Survey-artefact (flight/tie-line, block-seam) filter | 19 bands + GeoDAWN line metadata | axis-aligned, perfectly straight skeleton runs; mimic: levelling artefacts | removes false positives only | `gems73` seam-free magnetics touched this but did not filter the parent | +0.002 … +0.005 | **blocked**: needs GeoDAWN survey line/tie-line metadata (USGS release doi 10.5066/P93LGLVQ named in the official rules) — obtainability from this sandbox **not** verified |

**Choice.** H1 is the only one that (a) is eligible under the lane-uniqueness rule, (b) rests on a
label-informed validation that exists today, and (c) is cheap enough for the budget. H2 has the
highest *upside* and is the recommended next-session investment if GPU time exists; it is **not**
claimed here.

## 2. Pre-build screens (run before this document was finalised — stated for honesty)

* **S1 — leaderboard concordance** (`scripts/lb_concordance.py`, `evidence/lb_concordance_*.json`):
  over 11 independent lanes, agreement with the *other* lanes vs. the lane's own implied credit per
  dot: Spearman **+0.75** (permutation p = 0.0046); without the two SGMC lanes (n = 9) **+0.60**
  (p = 0.088). n is small, scores are CLAIMs, and 8 of 11 file matches are name-based: this is
  *suggestive*, not conclusive.
* **S2 — leave-one-lane-out credit model (first prototype, pool d_cat > 2 px):** predicting each held-out lane's credit per dot from the
  other lanes' votes, with halo-survival: MAE **0.021** at γ = 0.30 vs **0.049** for the
  distance-only null (γ = 0); Spearman +0.80. γ = 0.30 was the grid minimiser over
  {0, .15, .3, .5, .75, 1} and was fixed before the candidate was built. *(On the final pool, d_cat > 3 px: Spearman +0.83 / MAE 0.034 at 0.30; the MAE minimiser moved to 0.75 —
  see §4.)*

## 3. Pre-registered kill criteria (a negative result is a deliverable)

1. **Model:** MODEL-projected DTI of the *uniqueness-capped* selection must not fall below R0's
   projection by more than the LOO error band, else the verdict is *negative*.
2. **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, seeds 20 & 30, paired 20 km spatial-block bootstrap):
   candidate − R0 reported with 95 % CI. Caveat stated up front: the voter lanes were built from
   the full catalogue, so this instrument is **not fold-pure** for them; it is a diagnostic, not a
   promotion proof.
3. **Leakage canary:** the consensus score alone, hidden catalogue segments vs. same-fold
   background; symmetric AUC > 0.90 ⇒ stop and investigate.
4. **Uniqueness, both phases (pre-placement surface and final dots):** |Spearman| ≤ 0.90 and ≤ 70 %
   of dots within 3 px of any registry raster, over the full 924-raster distinct inventory. The one
   structural exception — rasters that are positive on > 20 % of the footprint — is reported
   side-by-side, never silently dropped (see `docs/UNIQUENESS_POLICY_20261024.md`).
5. **Format gates:** single band, float32, EPSG:32611, 3730 × 3292, template transform, all finite,
   values in [0, 1], zero outside footprint, zero dots on the catalogue, name & note ≤ 140 chars.

A projection is never written as a score. No slot is spent, approved or implied by this repository.

## 4. Outcome (appended after the build — the ranking above is unchanged)

* **H1 was built** as `GEMSDOE92-lcs-consensus-37654-20261024-58fd2c77-zeros.tif`; results in `docs/ANALYSIS_20261024_LCS.md`.
* **Kill criteria, as applied:** (1) MODEL projection 0.263–0.321 vs R0 0.2778, band ± 0.066 (one typical LOO error at γ = 0.30, MAE 0.034): not triggered, and not
  distinguishable from R0; (2) HOLDOUT-DTI = 0.000000 **by construction** (every dot > 3 px from every mapped fault; the random control also 0) — the instrument is
  degenerate for any file honouring the 3-px rule, so the paired CI against the holdout best is entirely below 0 and the slot verdict is **negative**, with ≈ no evidential weight;
  (3) canary AUC 0.519: pass; (4) Tier S pass both phases, Tier L pass on final dots / fail on the surface, Tier T fail (as for a random file); (5) all 10 MUST gates pass at the strict 3-px radius.
* **Deviations (also in `IRREGULARITIES.md`):** γ kept at 0.30 although the MAE minimiser moved to 0.75 on the final pool (Spearman still peaks at 0.30); pool tightened to d_cat > 3 px after
  reading the gate code (brief constraint 4); Tier-L class defined by halo coverage rather than support after the vendor gate caught a 0.7254 violation in v2.
* **Ranking after the fact:** H1 stays first for *eligibility and cost*; H3 (fragment prune, **8,719 of R0's dots on isolated 1-px skeleton components, untested live**) is the best *probe*;
  H2 (CNN/U-Net) remains the highest-upside, highest-cost item and is the recommended next investment if GPU time or lidar access exists.
* **H5 data source verified; the artefact test is negative.** The GeoDAWN release is public (USGS ScienceBase item 657e1d85d34e23d3533209f7, doi 10.5066/P93LGLVQ): E–W flight lines at 200/400 m, N–S tie lines at 2/4 km,
  four acquisition blocks, tie-line and micro-levelling, flight-path shapefiles and flight-line CSVs included (read as page text; binaries are not reachable from this sandbox's shell). `scripts/orientation_check.py`
  (`evidence/orientation_check_20261024.json`): elongated dot strings within ±10° of E–W (flight direction) are **6.0 %** of R0's and **4.0 %** of LCS's (uniform 11.1 %, mapped faults 3.0 %); N–S shares (21.0 % / 22.5 %) track the catalogue's 19.1 %.
  No flight-line striping signature; an N–S tie-line test needs the flight-path shapefiles. H5's expected gain stays at the low end (+0.002…+0.005) and it is no longer "blocked" on obtainability, only on shell access.
