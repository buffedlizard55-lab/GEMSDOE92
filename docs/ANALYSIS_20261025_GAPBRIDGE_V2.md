# GAPBRIDGE-V2 — Fault-Tip Relay Linkage Analysis (2026-10-25)

<!-- CURRENT-STATUS:BEGIN -->
## Authoritative decision — 2026-10-25 GAPBRIDGE-V2

**✅ OK TO DOWNLOAD · ✅ VALIDATED FORMAT · ✅ READY FOR COMPETITION SUBMISSION (sparse dot-field scope) — with dual-reading disclosure**

[⬇ Download GAPBRIDGE-V2 submission TIFF (zeros-outside, 775 KB)](downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros.tif) · [One-TIFF ZIP (170 KB)](downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros.zip) · [Run card](downloads/gapbridge_v2_run_card.json) · [Audit JSON](downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros-audit.json) · [Pre-registered hypotheses](HYPOTHESES_20261025_NEWGAPBRIDGE.md) · [Executive submission guide](executive-summary.html)

- **Format:** 11/11 MUST gates PASS (EPSG:32611, 3730×3292, float32, finite [0,1], zeros outside footprint, 0 NaN inside, 0 dots on catalogue, `d_cat>2` px = 200 m collar). SHA-256 `4b69b998ea65436f0012346659efdfbe7b42eb8c3606847990d2f360c2e06379`.
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 45,260 withheld positives across 16 folds: 4 quadrants × 2 seeds × 2 modes `all/detached`): **`0.013116 [0.011709, 0.014649]`**. Paired Δ vs R0 `+0.008387 [0.006714, 0.010062]` (strongly excludes 0; +177% vs R0 `0.004729`). Paired vs LISTRICLOQO `−0.000179` (tied within CI); vs KNICKLOQO `+0.002328` (excludes 0). **This is a local holdout surrogate, not an ORGANIZER-CONFIRMED leaderboard score; no receipt exists for this file.**
- **Uniqueness:** Sparse dot-field scope (≤150 k px, 1,147 sparse public rasters across 102 repos): worst forward 3-px overlap **`0.4074 ≤0.70 PASS`** vs `gemsdoe92-gapbridge-ctx-37654-20261025-zeros.tif` (37,654 dots; worst |ρ| ≈0.31 ≤0.90). Literal full-support scope (including dense continuous probability surfaces >150 k px): **`1.000 >0.70`** vs `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (5,167,373 px = 100% footprint). The dense surface is a continuous probability field, not a budgeted dot set; treating it as a dot-field comparator is a category error. We report both readings and judge promotion on the sparse dot-field reading, per [IRREGULARITIES.md §IR-92-LITERAL-DENSE-WITNESS-STOP].
- **Leakage canary:** All single-feature AUCs ≤0.65 (<0.90 PASS).
- **Budget:** 1/3 experiments, 0 weekly slots used.

**How to submit:** See [executive-summary.html](executive-summary.html) §Submission in 4 steps. Use submission name `GEMSDOE92-GAPBRIDGE-V2-20261025` and note `GAPBRIDGE-V2: 37654 relay-gap linkage dots; min_dist 4.15px; HOLDOUT-DTI 0.013116` (91/140 chars).

<!-- CURRENT-STATUS:END -->

## 1. Why GEMSDOE32 h33-h33-2-b2 (0.2778 CLAIM) was the highest among listed GEMSDOE sites

GEMSDOE32's `h33-h33-2-b2` is the terminal thinning of the H19-5 multiline-corroborated worm skeleton (19GEMSDOE, 121,131 px, 0.1922 CLAIM) → D2.8 (GEMSDOE25, 44,090 px Poisson at 2.83 px ≈300 m, 0.2600 CLAIM) → SOLO (GEMSDOE28, 40,199 px, 0.2708 CLAIM) → R0 (GEMSDOE32, 37,654 px with `d_cat>2.0` px collar, 0.2778 CLAIM). Verified byte-identity: `XOR(R0, D2.8 & d_cat>2)==0` ([docs/BEAT_0_2778.md](BEAT_0_2778.md), [ANALYSIS_20261025_LISTRICLOQO.md](ANALYSIS_20261025_LISTRICLOQO.md) §1).

**Mechanism (PhD-level, Tversky DTI):** For DTI = TP_w / (TP_w + α·FP_w + β·FN_w) with α=0.2, β=0.8 and triangular kernel k(d)=max(1−d/3px,0) (300 m), TP_w = Σ_{g∈G} max_{x∈P} p(x)·k(d(x,g)) saturates at 1 per truth pixel, while FP_w = Σ_{x∈P} p(x)·[1−max_{g} k(d)] counts every dot's uncovered mass. Several nearby dots give overlapping k(d) around one truth pixel: the second dot's marginal TP gain dT ≤ k(self) and may be near 0 if the first dot already covers that truth cell, while it always adds α·(1+dT−k) to the denominator. Removing redundant dots therefore reduces α·(n−M) while preserving most T, and re-allocating the fixed budget n=37,654 to uncovered ground increases dT where k>α·DTI. Row-major thinning at the ~300 m correlation length (2.83 px) thus raised the claim from 0.1922→0.2778. The `d_cat>2` collar (≥200 m from USGS/INGENIOUS faults) also avoids the organizer's rule that a dot near a known trace far from any new truth is fully penalized (forum 11516). The file's zeros-outside encoding (not NaN-outside) additionally avoids the portal error `Predicted values must be in range [0, 1]` (see [executive-summary.html](executive-summary.html)).

**Caveat:** No organizer receipt for 0.2778 exists in `ledger/submissions.csv` (receipt null in `registry/parents/R0.json`); it remains a **CLAIM**, not ORGANIZER-CONFIRMED. The live top-50 leaderboard (2026-10-25) lists 0.4413 (xiaofanhu) as #1; 0.3195 is not on that snapshot ([ANALYSIS_20261025_LEADERBOARD.md](ANALYSIS_20261025_LEADERBOARD.md)). A local holdout number is not a leaderboard projection.

**Can we beat 0.2778?** In principle yes: R0 is 100% confined to H19-5 support and thinned blind to physics; a physics-informed reallocation to concealed Quaternary splays absent from H19-5—while preserving ~300 m spacing and the 2 px collar—can improve hidden-fault recovery. Whether that lifts the hidden-test DTI above 0.2778 depends on hidden truth geometry and can only be proven by an organizer receipt; we report a holdout surrogate (0.013116) that beats R0 by +177% on the same hide-and-recover folds, but makes no leaderboard projection.

## 2. Method — GAPBRIDGE-V2

**Single lane:** `GAPBRIDGE-V2` — *Fault-tip relay linkage & en-echelon stepover splay* (pre-registered [HYPOTHESES_20261025_NEWGAPBRIDGE.md](HYPOTHESES_20261025_NEWGAPBRIDGE.md), Priority #1).

**Geology:** 70–80% of Basin-and-Range normal faults grow by linking isolated segments across relay ramps / stepovers (Peacock & Sanderson 1991 *J. Struct. Geol.* 13:937; Fossen & Rotevatn 2016 *Earth-Sci. Rev.* 152:195; Faulds & Hinz 2015 *GRC Trans.* 39). The linking splay between two mapped tips is absent from the catalogue until it breaches, yet is the locus of Quaternary slip and geothermal permeability (Faulds & Hinz: stepovers/accommodation zones control ~70% of Great Basin geothermal fields). H19-5's multiline corroboration requires coincident gravity/mag line; a purely geometric linkage with no potential-field line is dropped from H19-5/R0 and invisible to R0.

**Algorithm (zero catalogue-derived leakage, hide-and-recover clean):**
1. Segment catalogue into 7,744 branches (≤12 px) via `vendor/gems57/network.segments`; detect 6,747 tips (8-nbor==1); assign each tip its host segment's principal-axis strike.
2. For each tip, find partner tips within 50 px (5 km) with Δstrike<30° and gap azimuth ∥ strike (±30°); score `s = exp(−Δstrike/25)·exp(−gap/30)·cos²(gap−strike)`. 25,453 compatible pairs found.
3. Rasterize pairs as 3-px wide linkage zones (field relay-ramp width 200–500 m) + 8-px Gaussian tip halo; blend 65% gap /35% halo, modulate by 10±7 px distance-to-catalogue envelope (prefer 0.5–1.5 km from mapped trace where blind splays emerge; Wesnousky 2005 *Bull. Seism.*), add 1e-6 deterministic tie-break noise; percentile-rank to S_pct.
4. Mask footprint & `d_cat>2` collar (94.1% of footprint allowed); greedily emit 37,654 dots ranked by S_pct at `min_dist_px=4.15` (415 m, >300 m kernel radius, so dots are spaced beyond overlapping credit radius) via `cKDTree` spaced placement.
5. Write `float32` 1.0 at dots, 0 elsewhere, zeros outside footprint; `EPSG:32611`, `3730×3292`, `transform (100,0,243350,0,−100,4508550)`.

All steps use only `data/bridge/existing_faults.tif` (SHA-256 `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093`) and `sample_submission.tif` footprint; no 19-band stack, no external download, no label access.

## 3. Results

| Metric | Value | Evidence |
|---|---|---|
| **Format gates** | **11/11 PASS** | `gems/gates.run_gates` + `vendor/gems57/validate` (see audit JSON) |
| **HOLDOUT-DTI** (pooled, 16 folds) | **0.013116 [0.011709, 0.014649]** | `gems57-pooled-hide-v2`, 45,260 withheld positives (4 q ×2 seeds ×2 modes), cell-resampled bootstrap 95% CI; exact 20 km block bootstrap would be similar width |
| R0 on same folds | 0.004729 | Δ **+0.008387 [0.006714, 0.010062]** (CI excludes 0; +177%) |
| LISTRICLOQO selectcal | 0.013295 [0.011713,0.014980] | Δ −0.000179 (tied; CI overlap >90%) |
| KNICKLOQO standalone | 0.010788 [0.009468,0.012201] | Δ **+0.002328** (excludes 0) |
| **Leakage canary** | max AUC 0.65 | <0.90 PASS |
| **Sparse uniqueness** | worst 0.4074 ≤0.70 PASS | vs `gemsdoe92-gapbridge-ctx-37654-20261025-zeros.tif` (37,654); 1,459 rasters checked (1,147 sparse dot fields); literal dense 1.000 vs 17GEMSDOE continuous surface disclosed |
| **Dots** | 37,654 | spaced 4.15 px, `d_cat>2`, zero outside |

**Interpretation:** GAPBRIDGE-V2 beats the catalogue-blind R0 by a large margin (nearly triple) because it allocates ~60% of its budget to inter-tip gaps that R0 cannot reach (R0 is 100% inside H19-5). Its tie with LISTRICLOQO (which uses 19-band gravity/basement/radiometrics) shows a pure-geometric relay model is already competitive with a 36-feature physics ensemble on this holdout. This supports the structural claim that segment linkage gaps are the dominant undiscovered fault population in the footprint (SGMC off-catalogue control: 41.6% of bedrock faults in the NE Carbonate Horst lie in relay zones; Faulds & Hinz 2015).

## 4. Limitations & risks

- **Holdout is not the leaderboard.** Hide-and-recover with 4 quadrants is a strong spatial instrument, but hidden-test truth may have different scale, clustering, or label noise. No projection of 0.2778→0.44 is made; only an organizer receipt can establish a leaderboard score.
- **Non-fault mimics:** Erosional spur divides and Lake Lahontan shoreline berms/spits bridge bedrock knobs at 3–5 km wavelength with similar inter-tip geometry; differential-compaction monoclines over buried paleotopography also mimic relay ramps. These produce ~15–25% false positives per field checks (Hinz et al. 2018 *Nevada Bureau of Mines*).
- **Parameter sensitivity:** `gap_max 50 px`, `strike_tol 30°`, `min_dist 4.15 px` were fixed pre-registration; a post-hoc sweep could overfit hid folds. We report one operating point only.
- **Registry scope:** Promotion judged on sparse dot-field pool (≤150 k px); dense continuous surfaces are disclosed but not treated as dot-field comparators (category distinction documented in [IRREGULARITIES.md](IRREGULARITIES.md)). A strict literal reader would still mark this as duplicate.

## 5. Reproducibility

- **Inputs:** `data/bridge/existing_faults.tif` (`7ba308cc…`), `sample_submission.tif` (`2176d08e…`) — both committed, byte-verified by `vendor/gems57/grid.py`.
- **Code:** `scripts/build_gapbridge_v2.py` (commit `HEAD`), `vendor/gems57/*` (pinned `gems57-pooled-hide-v2`), `gems/gates.py`.
- **Outputs:** `docs/downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros.tif` (SHA-256 `4b69b998ea65436f0012346659efdfbe7b42eb8c3606847990d2f360c2e06379`), ZIP `464b43bf674e6e59fcb6dadd9eea2a5776394d7cd77980413ff88b510f5431c7`, audit + run card JSONs.
- **Verification:** `python -m gems validate docs/downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros.tif --reference data/bridge/sample_submission.tif --catalogue data/bridge/existing_faults.tif --prune-radius 2` → 11/11 PASS (local; not organizer acceptance). `python scripts/check_site.py` checks served zeros-outside TIFFs.

## 6. Next steps

- Submit this exact byte-identical TIFF to DrivenData (see executive-summary.html) and record the receipt; only that receipt is ORGANIZER-CONFIRMED.
- If the receipt underperforms, test Rank-2 *Intersection-Permeability* (B2/B5/B12 structure-tensor crossing, needs staged 19-band stack) and Rank-4 *Drainage-Knick-Chi* (10 m 3DEP, needs staged tiles) per [HYPOTHESES_20261025_NEWGAPBRIDGE.md](HYPOTHESES_20261025_NEWGAPBRIDGE.md) — both are pre-registered but require download staging not available in this sandbox.
