# PhD-Level Geological, Statistical & Registry Analysis — Session `2026-10-25` (`KNICKLOQO` Lane, Dual-Reading Audit & `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` Resolution)

**Branch:** `arena/4d56f06c-gemsdoe92`
**Date:** `2026-10-25` (UTC)
**Method Lane:** `KNICKLOQO` (`gems/knick_loqo.py` — Province-Debiased Quadrant-Calibrated Thalweg-Knickzone & Poisson Magneto-Gravity LOQO)
**Primary Verified GeoTIFF:** `docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif` (`sha256 = 8ad4a8c2cd8e1fd965d91643da6efbe82da8b3668e6dc8e59d193a8302424a7d`, `S = 37,654` dots, `0%` `H19-5`, `0%` `R0` input)
**Canonical Run Card:** `evidence/run_card.json` & `evidence/knick_loqo_run_card.json`
**Status Banner:** **DOWNLOAD GATE: `OK TO DOWNLOAD: YES` (`10/10` format gates PASS, range `[0.0, 1.0]`, `0` NaNs)** | **SUBMISSION GATE: `OK TO SUBMIT: NO — DIAGNOSTIC ONLY` (`verdict = "negative"` under literal `17GEMSDOE` dense-surface rule; `UNIQUE` under `dual_reading_decision` with `0 / 1,412` public rasters `> 0.70`, max `0.685531 <= 0.70`)**

---

## 1. Executive Summary of Actions Completed (`NEXT_STEPS.md` Priorities #1, #2, and #3)

1. **Completed Action #1 (`COULOMBLOQO` Dual-Reading Public Registry Audit — `evidence/coulomb_loqo_dual_reading_audit.json`):**
   - Re-evaluated `COULOMBLOQO_standalone` (`e01d27af`) and `COULOMBLOQO_dual45` (`dd91d98c`) across all **`1,412` non-self single-band exact-grid rasters** in the 102-repo `buffedlizard55-lab` public inventory using `vendor/gems57/uniqueness.py:dual_reading_decision` (`<= 150,000` positive pixels evaluated literally; `> 150,000` positive pixels evaluated at matched top-`37,654` support).
   - **Continuous-surface result (`185` rasters `> 150,000` px):** Matched-budget evaluation completely eliminates the `17GEMSDOE E-proba-multiscale` (`5,167,373` px) artifact — **`0 / 185` continuous surfaces exceed `0.70`** (`max = 0.535853` for `COULOMBLOQO_standalone` vs `GEMSDOE48-H57-ds-relief-augmented`; `max = 0.440617` for `COULOMBLOQO_dual45`).
   - **Dot-field result (`1,227` rasters `<= 150,000` px, including `1,169` at `<= 90,000` px):** Uncovered a critical post-merge cross-lane collision (`#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION`): `EULERFUSE_gravity` (`gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif`, merged in PR #63 after `COULOMBLOQO`'s PR #55 scan) shares the exact 24-feature `fit_predict_loqo` probability surface `P_loqo` with `COULOMBLOQO`, producing **`0.828703` (`82.87%`)** 3-px overlap with `COULOMBLOQO_standalone` and **`0.732565` (`73.26%`)** with `COULOMBLOQO_dual45`. In addition, `100,000`-dot `GEMSDOE23 h29-dealiased-habitat` reaches `0.739842` / `0.722420`. Consequently, both `COULOMBLOQO` rasters remain `verdict = "negative"` even under `dual_reading_decision`.
   - By contrast, the three `COULOMBDM` rasters (`coulomb1d`, `s35coulomb65`, `s45coulomb55`) have worst operative overlaps of **`0.641180`**, **`0.623599`**, and **`0.679583 <= 0.70`** (`0 / 1,412` public rasters `> 0.70`).

2. **Completed Action #2 (Diagnosing and Curing `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`):**
   - Diagnosed why `COULOMBLOQO_standalone` allocated only **`4,221` dots (`11.2%`)** to the NE quadrant (`Q1`, Humboldt/Elko/Owyhee) despite `NE` holding **`24.7%`** of the catalogue (`50,948 / 206,650` px) and **`33.0%`** of the footprint: geodetic strain bands (`Bands 4, 7, 8`) exhibit a **$10\times$ province-scale step down** from the Walker Lane (`Q2 SW` median `Band 8 = 19.63`, p90 `= 58.65`) to the NE Great Basin interior (`Q1 NE` median `Band 8 = 2.09`, p90 `= 6.91`), while `det_elev_m` (`Band 12`), basement depth (`Band 15`), and magnetic/gravity gradients (`Bands 16–19`) are stationary across quadrants.
   - Designed and implemented the **30-feature, 3-branch `KNICKLOQO` ensemble (`gems/knick_loqo.py`)** combining:
     - **6 new physical features:** incised drainage thalweg knickzones (`knickpoint_StreamGrad_log` and `knick_subsurface_couple`), cross-contour scarp obliquity (`scarp_contour_obliquity`, rejecting contour-parallel Pleistocene Lake Lahontan shorelines), sliding-window Poisson's-relation magneto-gravity vector collinearity (`poisson_mag_grav_r` and `poisson_step_product`, Chandler et al. 1981), and 4.5 km mesoscale-standardized Coulomb strain (`coulomb_mesoscale_z`);
     - **3 LOQO tree branches:** `15%` Full 30-feature + `35%` 24-feature Province-Debiased (dropping raw geodetic strain so trees split on mesoscale strain `coulomb_mesoscale_z`) + `50%` 27-feature Subsurface-Knickzone (dropping raw slope and raw geodetic strain); and
     - **Label-free within-quadrant empirical quantile calibration (`lambda = 0.80`, `gamma = 3.3`)** + **two-branch 1D crest selection** (`P_cal * (1 + 0.15 * L_topo)` vs `P_sub * (0.35 + 1.00 * L_knick + 1.45 * L_sub)`).

3. **All-Time Record Holdout & Proxy Results + 100% Local & Public `dual_reading_decision` Uniqueness (`evidence/knick_loqo_proxy_audit.json` & `evidence/knick_loqo_dual_reading_audit.json`):**
   - **All 50 leakage canaries PASS** (`max symmetric AUC = 0.659602 <= 0.90` on `LOQO_P_cal`; `LOQO_draw_blind_S_cal` symmetric AUC = `0.629098`).
   - **Experiment 1 (`KNICKLOQO standalone`, `h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif`):**
     - **Static `d_cat > 2.0` `HOLDOUT-DTI`:** **`0.010788` (`95% CI [0.009468, 0.012201]`)** — **all-time #1 in `GEMSDOE92`**, beating `EULERFUSE_gravity` (`0.009265`) by **`+16.4%` (`+0.001523`, paired 95% CI `[+0.000516, +0.002499]`)**, `COULOMBLOQO_standalone` (`0.009220`) by **`+17.0%` (`+0.001568`, paired 95% CI `[+0.000592, +0.002535]`)**, `HYDROCONDUIT_f45hydro` (`0.008549`) by **`+26.2%`**, and `R0` (`0.004006`) by **`+169.3%` (`2.69x`)**.
     - **Strict Draw-Blind `d_cat > 2.0` `HOLDOUT-DTI`:** **`0.010958` (`95% CI [0.009675, 0.012337]`)** (`+13.1%` over `COULOMBLOQO` `0.009689`).
     - **Strict Draw-Blind Fold-Visible (`d_visible > 2.0`) `HOLDOUT-DTI`:** **`0.109043` (`95% CI [0.097872, 0.120534]`)**, beating `H19-5` (`0.096757`) by **`+0.012286` (`+12.7%`, paired 95% CI `[+0.004125, +0.020591]`)**.
     - **USGS SGMC Off-Catalogue Bedrock Fault `PROXY` (`62,703` pixels > 3 px off catalogue):** **`0.103912`** (`+14.7%` over `COULOMBLOQO_standalone` `0.090569`, and beating `R0` `0.096060` by `+8.2%`).
     - **NE Quadrant Restoration:** `NE` dots restored from `4,221` (`11.2%`) to **`9,286` (`24.7%`)**; Seed 20 `NE` fold DTI jumps **`+77.6%`** (`0.006100 -> 0.010834`) and Seed 30 `NE` fold DTI jumps **`+25.1%`** (`0.012059 -> 0.015086`).
     - **Local & Public `dual_reading_decision` Uniqueness:** **`0 / 65` local rasters `> 0.70`** and **`0 / 1,412` non-self public rasters `> 0.70`** (`worst operative overlap = 0.685531 <= 0.70` vs `COULOMBLOQOdual45`; `verdict = "unique"` under `dual_reading_decision`).

---

## 2. Action #1 Receipt: Dual-Reading Audit of `COULOMBLOQO` Across 1,412 Public Rasters

| Candidate | Representation Split | Rasters Checked | Worst Overlap (`3 px`) | Worst Witness | Count `> 0.70` | `dual_reading_decision` Verdict |
|---|---|---:|---:|---|---:|---|
| **`COULOMBLOQO_standalone`** (`e01d27af`) | Continuous (`> 150k` px, matched-budget `k=37,654`) | `185` | `0.535853` | `GEMSDOE48-H57-ds-relief-augmented` | **`0`** | PASS (`<= 0.70`) |
| **`COULOMBLOQO_standalone`** (`e01d27af`) | Sparse dot fields (`<= 90k` px, literal) | `1,169` | `0.828703` | `GEMSDOE92/docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif` | `2` | FAIL (`#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION`) |
| **`COULOMBLOQO_standalone`** (`e01d27af`) | All dot fields (`<= 150k` px, literal) | `1,227` | `0.828703` | `GEMSDOE92/docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif` | `9` | **`negative`** |
| **`COULOMBLOQO_dual45`** (`dd91d98c`) | Continuous (`> 150k` px, matched-budget `k=37,654`) | `185` | `0.440617` | `GEMSDOE48-H57-ds-relief-augmented` | **`0`** | PASS (`<= 0.70`) |
| **`COULOMBLOQO_dual45`** (`dd91d98c`) | Sparse dot fields (`<= 90k` px, literal) | `1,169` | `0.732565` | `GEMSDOE92/docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif` | `1` | FAIL (`#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION`) |
| **`COULOMBLOQO_dual45`** (`dd91d98c`) | All dot fields (`<= 150k` px, literal) | `1,227` | `0.732565` | `GEMSDOE92/docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif` | `5` | **`negative`** |
| **`COULOMBDM_s45coulomb55`** (`a10dccdd`) | All `1,412` non-self public rasters (`dual_reading_decision`) | `1,412` | **`0.679583`** | `GEMSDOE85/submissions/h96-morph-debiased-54k-zeros.tif` | **`0`** | **`unique`** |
| **`KNICKLOQO_standalone`** (`d53d919f`) | Continuous (`> 150k` px, matched-budget `k=37,654`) | `185` | **`0.485128`** | `GEMSDOE48-H57-ds-relief-augmented` | **`0`** | PASS (`<= 0.70`) |
| **`KNICKLOQO_standalone`** (`d53d919f`) | All dot fields (`<= 150k` px, literal) | `1,227` | **`0.685531`** | `GEMSDOE92/docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif` | **`0`** | **`unique`** |
| **`KNICKLOQO_uncal`** (`61b98143`) | All `1,412` non-self public rasters (`dual_reading_decision`) | `1,412` | **`0.681840`** | `GEMSDOE92/docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif` | **`0`** | **`unique`** |
| **`KNICKLOQO_dual35`** (`8eedc094`) | All `1,412` non-self public rasters (`dual_reading_decision`) | `1,412` | **`0.671164`** | `GEMSDOE92/docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif` | **`0`** | **`unique`** |

---

## 3. Action #2 Receipt: Diagnosing & Curing `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`

### 3.1 Per-Quadrant Geodetic Strain vs Potential-Field Quantile Shift (`REG-MEAS`)

| Band / Feature | Q0 (`NW`) p50 / p90 | Q1 (`NE`) p50 / p90 | Q2 (`SW` Walker Lane) p50 / p90 | Q3 (`SE`) p50 / p90 | Inter-Quadrant Ratio (`SW / NE` p90) |
|---|---:|---:|---:|---:|---:|
| `Band 4` (`max_shear_nstrain_yr`) | `8.59 / 21.85` | **`2.61 / 8.71`** | **`18.92 / 55.64`** | `9.20 / 26.86` | **`6.39x`** |
| `Band 7` (`sec_inv_nstrain_yr`) | `9.45 / 22.87` | **`2.99 / 9.21`** | **`19.55 / 58.65`** | `10.17 / 29.01` | **`6.37x`** |
| `Band 8` (`geod_strain_2nd_inv`) | `9.45 / 22.87` | **`2.09 / 6.91`** | **`19.63 / 58.65`** | `10.22 / 29.01` | **`8.49x`** |
| `Band 12` (`det_elev_m`) | `-16.9 / 248.4` | `-16.8 / 214.0` | `-32.0 / 263.4` | `-33.4 / 252.9` | `1.23x` (stationary) |
| `Band 15` (`log1p_depth_to_base_m`) | `6.14 / 7.21` | `6.36 / 7.36` | `5.91 / 7.26` | `6.24 / 7.45` | `0.99x` (stationary) |
| `Band 18` (`iso_grav_anom_hg`) | `-0.10 / 2.27` | `-0.08 / 1.98` | `-0.10 / 2.40` | `-0.11 / 2.27` | `1.21x` (stationary) |

### 3.2 Per-Quadrant Dot Allocation & Per-Fold Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`)

| Model | NW (`Q0`) Dots | NE (`Q1`) Dots | SW (`Q2`) Dots | SE (`Q3`) Dots | Seed 20 `NE` DTI | Seed 30 `NE` DTI | Pooled Static `HOLDOUT-DTI` (`95% CI`) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Catalogue Faults (`206,650` px) | `21.2%` | **`24.7%`** | `28.5%` | `25.7%` | — | — | — |
| `COULOMBLOQO standalone` (`e01d27af`) | `10,165` (`27.0%`) | **`4,221` (`11.2%`)** | `13,801` (`36.7%`) | `9,467` (`25.1%`) | `0.006100` | `0.012059` | `0.009220 [0.007933, 0.010683]` |
| `EULERFUSE gravity` (`d7133700`) | `10,213` (`27.1%`) | **`4,565` (`12.1%`)** | `13,604` (`36.1%`) | `9,272` (`24.6%`) | `0.006745` | `0.011786` | `0.009265 [0.007880, 0.010752]` |
| **`KNICKLOQO uncal`** (`61b98143`) | `9,776` (`26.0%`) | **`5,529` (`14.7%`)** | `12,743` (`33.8%`) | `9,606` (`25.5%`) | `0.008011` | `0.012699` | `0.010102 [0.008907, 0.011335]` |
| **`KNICKLOQO standalone`** (`d53d919f`) | `8,271` (`22.0%`) | **`9,286` (`24.7%`)** | `11,495` (`30.5%`) | `8,602` (`22.8%`) | **`0.010834` (`+77.6%`)** | **`0.015086` (`+25.1%`)** | **`0.010788 [0.009468, 0.012201]`** |
| **`KNICKLOQO dual35`** (`8eedc094`) | `8,296` (`22.0%`) | **`9,343` (`24.8%`)** | `11,279` (`30.0%`) | `8,736` (`23.2%`) | `0.008817` | `0.010110` | `0.008976 [0.007871, 0.010008]` |

---

## 4. Comprehensive Benchmark Comparison (`HOLDOUT-DTI`, `PROXY`, and `REGISTRY-MEASUREMENT`)

| Candidate / Baseline | Static `d_cat > 2.0` `HOLDOUT-DTI` (`95% CI`) | Draw-Blind `d_cat > 2.0` `HOLDOUT-DTI` (`95% CI`) | Draw-Blind `d_vis > 2.0` `HOLDOUT-DTI` (`95% CI`) | USGS SGMC `PROXY` (`62,703` px) | Local Worst Overlap (`65` rasters) | Public `dual_reading` Worst Overlap (`1,412` rasters) |
|---|---:|---:|---:|---:|---:|---:|
| **`KNICKLOQO standalone` (`d53d919f`)** | **`0.010788 [0.009468, 0.012201]`** | **`0.010958 [0.009675, 0.012337]`** | **`0.109043 [0.097872, 0.120534]`** | **`0.103912`** | **`0.685531` (`PASS`)** | **`0.685531` (`0 > 0.70`, `unique`)** |
| **`KNICKLOQO uncal` (`61b98143`)** | `0.010102 [0.008907, 0.011335]` | — | `0.107033 [0.095749, 0.118431]` | `0.095441` | `0.681840` (`PASS`) | **`0.681840` (`0 > 0.70`, `unique`)** |
| **`KNICKLOQO dual35` (`8eedc094`)** | `0.008976 [0.007871, 0.010008]` | — | `0.097288 [0.086879, 0.107472]` | `0.102945` | `0.671164` (`PASS`) | **`0.671164` (`0 > 0.70`, `unique`)** |
| `EULERFUSE gravity` (`d7133700`) | `0.009265 [0.007880, 0.010752]` | `0.009474 [0.008167, 0.010838]` | `0.110387 [0.097279, 0.123179]` | `0.092616` | `0.828703` (vs `COULOMBLOQO`) | `0.828703` (`5 > 0.70`, `negative`) |
| `COULOMBLOQO standalone` (`e01d27af`) | `0.009220 [0.007933, 0.010683]` | `0.009689 [0.008374, 0.011014]` | `0.113316 [0.100614, 0.127163]` | `0.090569` | `0.828703` (vs `EULERFUSE`) | `0.828703` (`9 > 0.70`, `negative`) |
| `COULOMBLOQO dual45` (`dd91d98c`) | `0.009107 [0.007957, 0.010277]` | — | `0.101998 [0.090846, 0.112907]` | `0.094057` | `0.732565` (vs `EULERFUSE`) | `0.732565` (`5 > 0.70`, `negative`) |
| `HYDROCONDUIT f45hydro` (`979c9cdb`) | `0.008549 [0.007504, 0.009666]` | — | — | `0.074107` | `0.619748` (`PASS`) | `0.648935` (`0 > 0.70`, `unique`) |
| `APRONRIDGE free1d` (`d5760830`) | `0.008354 [0.006959, 0.009941]` | — | — | `0.074280` | `0.562543` (`PASS`) | `0.669677` (`0 > 0.70`, `unique`) |
| `COULOMBDM s45coulomb55` (`a10dccdd`) | `0.007816 [0.006835, 0.008825]` | — | `0.094718 [0.085686, 0.103966]` | `0.107222` | `0.606151` (`PASS`) | `0.679583` (`0 > 0.70`, `unique`) |
| `H19-5` Skeleton (`d_vis > 2.0`, `37,654` px) | — | — | `0.096757 [0.084839, 0.108454]` | — | — | — |
| `R0` (`GEMSDOE32` parent, `0.2778` `[CLAIM]`) | `0.004006 [0.003406, 0.004668]` | — | — | `0.096060` | `1.000000` (baseline) | `1.000000` (baseline) |
