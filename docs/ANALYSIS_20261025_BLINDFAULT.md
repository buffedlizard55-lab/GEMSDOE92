# ANALYSIS — `BLINDFAULT` session (2026-10-25): covariate-shift-corrected, subsurface-only LOQO

**Verdict: `negative`. ✅ OK TO DOWNLOAD (format-valid, unique). ⛔ DO NOT SUBMIT (fails the pre-registered promotion gate).**
Pre-registration: [`HYPOTHESES_20261025_BLINDFAULT.md`](HYPOTHESES_20261025_BLINDFAULT.md) · machine evidence: [`../evidence/blindfault_holdout.json`](../evidence/blindfault_holdout.json), [`../evidence/blindfault_uniqueness.json`](../evidence/blindfault_uniqueness.json), [run card](downloads/blindfault_run_card.json).

## 1. Question answered first: why `GEMSDOE32` scored `0.2778` `[CLAIM]`, and can it be beaten?

(Receipts `0.1922 → 0.2600 → 0.2708 → 0.2778` are owner-supplied claims; the byte-exact lineage `H19-5 → D2.8 → SOLO → R0` is verified locally — `evidence/r0_forensics_20261024.json`.)

1. **It is an emission optimum, not a detection optimum.** Every step after `H19-5` edits *which* of the same ridge pixels are emitted: Poisson thinning to ≥ 2.83 px (the 300 m kernel makes closer dots redundant in `TP_w` but each still costs `α = 0.2` in `FP_w`), then removing dots within 1 px and 2 px of the catalogue (near-catalogue dots are penalised as "known", organiser forum thread 11516).
2. **Solving the three receipts for the hidden truth size.** With `D = α(T + n − M) + βK` and `T ≈ M` for a spaced dot field, the `SOLO → R0` pair (`−2,545` dots, `+0.0070`) and `D2.8 → SOLO` pair (`−3,891` dots, `+0.0108`) are only consistent if the removed dots carried ≈ 0 credit, which gives `K ≈ 1.3 × 10⁴` hidden truth cells and `T ≈ 5.1 × 10³` credit — i.e. **≈ 13 % of `R0`'s 37,654 dots are productive**. The marginal-dot acceptance bar is `k > α · DTI ≈ 0.056`.
3. **Consequence.** `R0` sits close to the point where further thinning stops paying (`0.2708 → 0.2778` was a 2.6 % relative gain for a 6.3 % cut). Beating it requires raising the *hit rate* of the dot population, i.e. finding the ≈ 87 % of truth `R0` misses. Because the catalogue is a Quaternary *scarp* catalogue, that missing population is biased toward topographically subtle faults. **That is the only head-room argument consistent with the receipts, and it is what this lane tested.**
4. **Can it be beaten?** Yes in principle (leaderboard `0.3195`/`0.4413` `[CLAIM]` prove the metric allows it), but **not by this lane**: see §3.

## 2. What was built (one lane, three pre-registered arms, nothing else)

`gems/blindfault.py` + `scripts/run_blindfault.py` + `scripts/finalize_blindfault.py`. 12 catalogue-free subsurface features (RTP and isostatic-gravity horizontal-gradient magnitudes, TMI tilt angle, gravity VG and signed E–W HG, depth-to-basement gradient and level, MT conductivity gradient and level, geodetic dilatation and shear, 1 km low-pass detrended elevation as context). `HistGradientBoostingClassifier`, 4-quadrant leave-one-quadrant-out, 1.2 km guard, 500 m negative buffer, `neg:pos = 3`. Positives weighted `w = 1/(0.1 + c)` with `c` the rank-normalised 5 × 5 max of log-slope (`blind`), unweighted (`blindflat`), or weighted with log-slope also exposed as a feature (`blindtopo`). Emission: top-37,654 spaced ≥ 2.83 px on `foot ∧ valid ∧ d_cat > 2.0` (zero catalogue mass).

Leakage canaries (each feature alone vs. 22,663 withheld positives / 200k far negatives): **max symmetric AUC `0.5728`** (`f11_geod_shear`); all 13 features and the weight field pass `≤ 0.90`.

## 3. Results — every number is `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, buffered whole-component draws seeds 20 + 30, 8 folds, **22,663 withheld positives**, 1,000-draw 20 km-block bootstrap)

### 3.1 Primary promotion instrument: strict draw-blind LOQO, fold-visible `d_visible > 2.0`

| Arm | DTI | 95 % CI | Paired Δ vs `blind` |
|---|---:|---|---|
| `H19-5` (supervised reference, same emission rule) | **0.096757** | [0.084640, 0.108096] | +0.058915 [+0.043969, +0.072467] |
| `blindtopo` | 0.047896 | [0.038079, 0.057970] | +0.010053 [+0.003230, +0.015890] |
| `blindflat` | 0.047475 | [0.035767, 0.059748] | +0.009633 [−0.001105, +0.019150] |
| **`blind` (hypothesis)** | 0.037842 | [0.029376, 0.047036] | — |
| Repository holdout-best (`COULOMBLOQO standalone`, stored, same evaluator/seeds) | 0.113316 | [0.100614, 0.127163] | not re-run |

**Gate: FAIL.** Best arm `blindtopo 0.047896` < holdout-best `0.113316` and < `H19-5 0.096757`. The hypothesis arm is the *worst* of the three.

### 3.2 Mechanism instrument: same folds restricted to withheld components in the lowest conspicuity tercile (6,065 withheld positives; tercile cut `c ≤ 0.448 / 0.441`)

| Arm | DTI | 95 % CI |
|---|---:|---|
| `blindtopo` | 0.014386 | [0.008371, 0.020784] |
| `blind` | 0.011041 | [0.004739, 0.018804] |
| `blindflat` | 0.010713 | [0.004647, 0.017001] |
| `H19-5` | 0.007166 | [0.004529, 0.010079] |

Directionally as predicted — all three subsurface LOQO arms beat `H19-5` on subtle faults — but `blind − H19-5 = +0.003876 [−0.002360, +0.012181]` does **not** exclude 0, and `blind − blindflat = +0.000328 [−0.007947, +0.009929]` shows the **importance reweighting itself is not load-bearing**. The feature family, not the covariate-shift correction, carries the (small) subtle-fault gain.

### 3.3 Static reading of the deployment rasters (`d_cat > 2.0`, comparable to the repository static table)

`blindflat 0.005595 [0.004385, 0.006729]` > `blindtopo 0.004585` > `blind 0.004070 [0.002992, 0.005139]` ≈ `R0 0.004006 [0.003406, 0.004668]`. All below the static holdout-best `0.009220`.

### 3.4 Falsification summary (PhD reading)

- **Covariate-shift reweighting toward low-conspicuity positives is falsified as a mechanism** at this resolution: it moved 42.6 % of dots into the low-conspicuity tercile (vs 22.0 % unweighted) without improving recovery of low-conspicuity faults. The potential-field/MT/geodetic bands at 100 m simply do not localise individual subtle faults to 300 m; their canary AUCs (`0.50–0.57`) are barely above chance pixel-wise, and the learner's quadrant extrapolation collapses entirely in NE (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE`, per-fold DTI `0.000–0.005`).
- **Topography remains indispensable** (`blindtopo > blind`, CI excludes 0). This is consistent with every previous session: the only lane that ever beat `H19-5` on the primary instrument (`COULOMBLOQO`, `0.113316`) used multi-scale topographic Hessian ridges as its backbone.
- Named mimic check: not reached — the lane fails before mimic discrimination matters.

## 4. Uniqueness (`REGISTRY-MEASUREMENT`) and the dense-witness policy resolution

Policy fixed once in the shared template (`vendor/gems57/uniqueness.py`: `matched_budget_support`, `dual_overlap`, `dual_reading_decision`; `IRREGULARITIES.md` `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`). Both readings are reported; the operative lane-duplication test uses the matched-budget reading for continuous surfaces (> 150,000 positive px) and the literal reading for dot fields. Numbers for all three arms, the complete local registry (91 rasters) and the complete cached public registry (1,396 Git-blob-verified blobs from 102 owner repos) are in [`../evidence/blindfault_uniqueness.json`](../evidence/blindfault_uniqueness.json) and summarised in the run card and README.

## 5. Deliverables

| Arm | File (`docs/downloads/`) | SHA-256 | Status |
|---|---|---|---|
| `blindtopo` (best arm; ZIP served) | `gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif` | see run card | ✅ download · ⛔ do not submit |
| `blindflat` | `gemsdoe92-blindfault-blindflat-37654-20261025-1e27ea5c-zeros.tif` | see run card | ✅ download · ⛔ do not submit |
| `blind` | `gemsdoe92-blindfault-blind-37654-20261025-d4f09813-zeros.tif` | see run card | ✅ download · ⛔ do not submit |

All three: `float32`, `EPSG:32611`, `3730 × 3292`, finite in `[0, 1]`, `0.0` outside the footprint, 37,654 unit dots, 0 catalogue mass — written and re-read through `gems57.submission_writer` / `gems57.validate` (no human inspection). Weekly slots used: **0**. Experiments used: **3 / 3**.

## 6. What this changes for the next session

1. **Do not retry subsurface-only learners** at 100 m for 300 m localisation; three sessions (`EULERFUSE`, `COULOMBDM coulomb1d`, `BLINDFAULT`) now agree.
2. The dense-witness blocker is resolved in the template; the stored `COULOMBLOQO standalone` / `dual45` artifacts (the only ones that beat `H19-5` on the primary instrument) should be re-read under `dual_reading_decision` against the cached public registry **as the first action next session** — that is the highest-P(Win) step available, and it is a selector step, not an experiment.
3. The low-conspicuity instrument is now implemented (`scripts/run_blindfault.py::low_conspicuity_fold`) and should be reported for every future lane.
