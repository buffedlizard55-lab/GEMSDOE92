# Forensic Review, `GEMSDOE32` Analysis & `HYDROCONDUIT` Session Report (2026-10-24)

## 1. Executive Verdict (Read First)

- **Primary Artifact Generated:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd` (`37,654` unit-mass dots, `0.0` outside footprint, `nodata=None`)
  - **ZIP Bundle:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.zip`
  - **Suggested Submission Name:** `GEMSDOE92-HYDROCONDUIT-f45hydro-20261024`
  - **Suggested Form Note (106 / 140 chars):** `h33-h33-2-b2; HYDROCONDUIT f45hydro: 20710 piedmont H19-5 + 16944 off-skel scarp/RTP/GDR dots (>3px H19-5)`
- **Download Status:** **✅ FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH** (`10 / 10` `gems.gates` MUST checks + `13 / 13` `gems57.validate` checks pass on independent disk reread; zero NaNs anywhere, finite values in `[0, 1]`, zero catalogue mass, exact `EPSG:32611` `3730 × 3292` grid).
- **Weekly Slot / Submission Status:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`, `submission_eligible: false`).**
  1. **Positive Breakthroughs Achieved:** `HYDROCONDUIT f45hydro` is the **first candidate in `GEMSDOE92` history** to beat **both** `R0` (`0.004006 -> 0.008549`, **`+113.4%`**, paired 95% CI `[+0.003770, +0.005315]`) **and** the repository's prior holdout best `RELIEF p10` (`0.006045 -> 0.008549`, **`+41.4%`**, paired 95% CI `[+0.001795, +0.003222]`) on the shared `gems57-pooled-hide-v2` static-raster holdout while passing **every** single-feature leakage canary (`max symmetric AUC = 0.6501 <= 0.90`), **every** local registry uniqueness check (`worst 3-px overlap = 0.5500 <= 0.70`, `|rho| = 0.2982 <= 0.90`), and **every one of the 1,147 sparse dot-like rasters (`<= 150,000` positive px) across all 102 public `buffedlizard55-lab/*GEMSDOE*` repositories** (`0` sparse rasters over `70%`, max `0.6719 <= 0.70`, `|rho| <= 0.4396 <= 0.90`).
  2. **Why `verdict` Remains `"negative"` (`DO NOT SUBMIT`):**
     - **Binding Literal Public Dense-Witness Rule:** Across all `1,332` compatible single-band rasters in the live 102-repo GitHub API scan (`evidence/hydroconduit_public_registry_uniqueness.json`), `118` dense continuous/semi-dense surfaces (`> 150,000` positive pixels, led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` with `5,167,373 / 5,167,373 = 100%` positive footprint pixels) yield `100% > 70%` forward 3-px overlap under the literal Rule-1 wording ("no representation exemption"). Per repository contract, an agent session never waives this rule unilaterally.
     - **Multi-Instrument Disclosure (`Own the Outcome`):** Our newly added Rule-2 fold-by-fold `d_visible > 2.0` holdout (`0.0852` vs `0.0968` `H19-5` skeleton-only) and off-catalogue `USGS SGMC` proxy (`0.0741` vs `0.0961` `R0`) demonstrate that static-holdout gains partly reflect repacking `H19-5` piedmont strands across `R0`'s `d_full_cat > 2.0` exclusion gaps (`3,642` vs `2,171` collar dots at `2 < d_cat <= 3` px), whereas moving `45%` of dots `>3 px` off `H19-5` trades `H19-5` spine density and exposed mountain-core `SGMC` bedrock faults (`SGMC` range-core faults dropped from `74.8%` in `BREAKLINE` to `6.2%` in `HYDROCONDUIT`).

---

## 2. Why Did `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`) Score Highest Among Listed GEMSDOE Sites — And Can We Beat It?

### 2.1 Exact Byte-Verified Anatomy of `GEMSDOE32` (`R0`)
Direct inspection of `buffedlizard55-lab/GEMSDOE32/README.md` (via GitHub API) and byte-exact reproduction in `data/parent_R0_zeros.tif` (`sha256 c55bafc470054e82…`, `37,654` dots) establishes **four exact reasons** why `h33-h33-2-b2` (`0.2778` `[CLAIM]`, no organizer submission-page receipt in `ledger/`) outperformed the other prompt-listed `GEMSDOE` sites (`0.2512`–`0.2750` `[CLAIM]`):

1. **Multi-Scale Potential-Field + DEM Worm Skeleton (`H19-5`, `121,131` px, `0.2194` `[CLAIM]`):** Rather than raw per-pixel thresholding or wide probability clouds (which explode the false-positive term $\alpha\,\mathrm{FP}_w$ in the asymmetric Distance-Weighted Tversky denominator $\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w$), `H19-5` traces 1-px ridge crests of geophysical/topographic gradients across the NW Great Basin.
2. **Poisson-Disk Geodesic De-Aliasing (`D1.5 -> D2.8`, `44,090` px [disk-verified 2026-10-24; was `46,612`], `0.2649` `[CLAIM]`):** Adjacent 100 m pixels along a ridge share >85% of their `300 m` (`3 px`) triangular kernel $k(d)=\max(0, 1 - d/300\,\mathrm{m})$. Thinning to minimum Euclidean spacing `2.828 px` (`283 m`, matching the `300 m` kernel radius) eliminated ~61% of redundant FP mass while preserving nearly 100% of ridge max-coverage $T(A)=\sum_{g} \max_{x\in A} k(\|g-x\|)$ (`+0.0455` `[CLAIM]`).
3. **Component Micro-Fragment Pruning (`SOLO`, `40,199` px, `0.2708` `[CLAIM]`):** Dropping short isolated `1–2`-dot worm speckles (`6,413` px) removed uncorrelated noise speckles (`+0.0059` `[CLAIM]`).
4. **Known-Catalogue `200 m` (`<= 2 px`) Exclusion (`H33-2-B2`, `37,654` px, `0.2778` `[CLAIM]`):** Competition scoring masks mapped `existing_faults.tif` (`60,988` px), and ground-truth blind/unmapped target faults rarely duplicate a mapped trace within `<= 200 m` while still branching as splays/relay tips at `200–300 m` (`2 < d_cat <= 3` px, where `R0` keeps `2,171` dots). Removing `2,545` dots at `d_cat <= 2 px` saved dead denominator weight without losing off-catalogue splay reach (`+0.0070` `[CLAIM]`).
5. **Why Other Listed Sites Scored Lower (`0.2512–0.2750` `[CLAIM]`):** Sibling runs that emitted continuous/un-thinned probability bands, over-pruned `d_cat <= 4–5 px`, re-differentiated already-noisy derivative bands (`GEMSDOE32` showed spatial derivatives help raw potential/surface bands like `det_elev` `+10.1%` and `depth_to_base_surf` `+3.5%`, whereas re-differentiating `tc`/`geod_*` degrades signal), or moved >50% of mass onto unscreened bare-rock cliffs lost coverage on buried range-front faults.

### 2.2 Can `0.2778` `[CLAIM]` Be Beaten — And How?
- **Historical Context (`CLAIM`):** Prompt-quoted public leaderboard figures (`0.3195` `[CLAIM]` and later `0.4413` `[CLAIM / LEADERBOARD-SNAPSHOT]`) indicate substantial headroom above `0.2778` `[CLAIM]`, though neither has a verified receipt in this checkout and **local `HOLDOUT-DTI` can never be compared numerically to a live leaderboard score**.
- **Structural Ceiling of `R0` Diagnosed Locally:**
  1. `R0`'s `37,654` dots were thinned from `H19-5` in **row-major scan order without any physical habitat weighting**, stranding thousands of dots on bare pre-Quaternary mountain-core bedrock contacts and flat playa interiors while leaving gaps along piedmont range-front hinges.
  2. `R0` is **100% confined to `H19-5`**, so it has **zero** reach on subtle Quaternary alluvial-fan scarps or hydrothermally demagnetized conduits (`>300 m` from a potential-field worm).
- **What Beats `R0` Locally (Without Overclaiming Live Leaderboard Gain):**
  - On the repository's shared `gems57-pooled-hide-v2` static holdout, `HYDROCONDUIT f45hydro` more than doubles `R0` (`0.004006 -> 0.008549`, **`+113.4%`**) and beats prior holdout-best `RELIEF p10` (`0.006045 -> 0.008549`, **`+41.4%`**) while remaining locally and sparse-publicly unique (`0.5500` local, `0.6719` sparse-public `<= 150k` px).
  - Whether that translates to beating `0.2778` on DrivenData's hidden test set can **only** be established by an `ORGANIZER-CONFIRMED` submission receipt after a human selector resolves the dense-witness policy question and weighs the `d_visible > 2.0` (`0.0852` vs `0.0968`) and `SGMC` (`0.0741` vs `0.0961`) trade-offs.

---

## 3. Newly Discovered Data & Evaluation Irregularities (Logged in `IRREGULARITIES.md`)

1. **`Band 6 (tc)` Metadata Mislabelling (`#IR-92-BAND6-TC-MISLABEL`):** `training_features.tif` Band 6 is tagged `"tc - Tilt angle or total curvature - magnetic field derivative"`, yet across all `5,164,300` valid footprint pixels its values are strictly positive (`p05=11.82`, `p50=18.51`, `p95=25.63`) and correlate at **`r = 0.99714`** with USGS GeoDAWN Radiometric Total Count (`geodawn_rad_u8.tif` Band 4 `TC`). It is **airborne gamma-ray Total Count**, not magnetic tilt angle. `HYDROCONDUIT` computes the true Reduced-to-Pole (`Band 2 rtp`) Laplace tilt-contact and magnetite-destruction trough directly from `Band 2`.
2. **`GDR #1391` Trailing-Space `'Hot '` Category & Overlooked Blind Geothermometers (`#IR-92-GDR-HOT-WHITESPACE`):** In `gdr_wellspring_in_footprint.csv` (`27,092` rows), `121` rows carry `thermalclass == 'Hot '` (with a trailing space), and **`419` unique footprint pixels (`732` rows)** have cold/unmeasured surface `temp_c < 40 °C` while quartz, chalcedony, or Na-K-Ca chemical geothermometers record **`>= 80 °C`** deep reservoir temperatures. `gems/hydroconduit.py` strips whitespace and incorporates all `2,312` thermal + blind-geothermometer pixels.
3. **Static `d_full_cat > 2.0` Self-Masking on Hide-and-Recover Holdout (`#IR-92-STATIC-DCAT2-SELFMASK`):** Static deployment rasters built with `d_cat > 2.0` against the *full* `existing_faults.tif` automatically zero out predictions within `<= 200 m` of withheld `fold["truth"]` segments, depressing static `HOLDOUT-DTI` by ~10×–20× (`0.0040–0.0085`) relative to true Rule-2 fold-by-fold `d_visible > 2.0` (`0.0852–0.0968`). We report **both** readouts side by side.
4. **Unsupervised Diagnosis of `BREAKLINE` Range-Core Hijack (`#IR-92-BREAKLINE-RANGECORE-75PCT`):** `74.75%` of `BREAKLINE f45`'s `16,944` off-skeleton dots landed in the top `det_elev` tercile (`>= +38.75 m`, bare mountain range cores) and `28.9%` struck E–W/WNW (`65°–135°`) along incised erosional canyons, leaving only `18.15%` in the piedmont. `HYDROCONDUIT` inverted that ratio to **`83.45%` piedmont / `6.22%` range core**.

---

## 4. Pre-Placement Canaries & Uniqueness + 3-Experiment Results

### 4.1 Single-Feature Leakage Canaries (Protocol Rule 4 — All 24 Features PASS `<= 0.90`)
Full table in `evidence/hydroconduit_preplacement_screen.json`. Key single-feature ROC AUCs on buffered withheld fault folds (`seeds 20 + 30`, `22,663` positives):
- Raw bands: `Band 2 rtp` `0.5135`, `Band 4 geod_2ndinv` `0.5102`, `Band 8 geod_dilaterate` `0.5145`, `Band 12 det_elev` `0.5024` (sym), `Band 15 depth_to_base` `0.5149`, `Band 17 cond_surf` `0.5060`, `Band 19 det_elev_slope` `0.5531`.
- Derived physical transforms: `rel_break_pct` `0.5779`, `mu_step` (600 m step monotonicity) `0.5820`, `coh_elev` `0.5521`, **`t_scarp` `0.6230`**, `p_elev` (piedmont hinge) `0.5756`, `p_cover` `0.5429`, `kappa_strike` (Andersonian N15°E) `0.5800`, **`S_pied_pct` `0.6501`**, **`S_hydro_pct` `0.6479`**.
- **Max symmetric AUC across all 24 features: `0.65012 <= 0.90` (`PASS`).**

### 4.2 Benchmark Table Across All 3 Pre-Registered `HYDROCONDUIT` Arms & Prior Baselines

| Candidate / Baseline | Dots | Far (`>3 px` H19-5) | Far Piedmont % | Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 95% CI) | Paired $\Delta$ vs `R0` (95% CI) | Paired $\Delta$ vs `RELIEF p10` (95% CI) | `SGMC` `PROXY` DTI (`62,703` px) | Local Worst 3-px Overlap | Sparse Public (`<=150k` px, `1,147` rasters) Worst Overlap | Literal Public (`1,332` rasters incl. dense) |
|---|---:|---:|---:|---|---|---|---|---|---|---|
| `R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | 37,654 | 0% | — | `0.004006 [0.003424, 0.004690]` | baseline | `-0.002039` | `0.096060` | `1.0000` (self) | — | — |
| `RELIEF p10` (prior holdout best) | 37,654 | 0% | — | `0.006045 [0.005187, 0.006927]` | `+0.002039` | baseline | `0.087245` | **`0.9938` (DUP)** | — | `1.0000` (DUP) |
| `BREAKLINE f45Ltop` | 37,654 | 45% | 18.2% | `0.004861 [0.004032, 0.005822]` | `+0.000854` | `-0.001185` | **`0.126105`** | `0.5500` | — | `1.0000` (DUP) |
| `SPRINGALIGN f33Ctop` | 37,654 | 33% | — | `0.004865 [0.004025, 0.005785]` | `+0.000859` | `-0.001180` | `0.080173` | `0.6700` | — | `1.0000` (DUP) |
| `ANASIG f45Atop` | 37,654 | 45% | — | `0.004967 [0.004098, 0.005940]` | `+0.000961` | `-0.001078` | `0.080556` | `0.5500` | — | `1.0000` (DUP) |
| `STRAINBREAK f60s2i` | 37,654 | 60% | — | `0.005487 [0.004522, 0.006430]` | `+0.001481` | `-0.000558` | `0.105162` | `0.4150` | `0.7105` (`3 > 70%`) | `1.0000` (DUP) |
| **`HYDROCONDUIT f45pied` (Exp 1)** | 37,654 | 45% | **85.8%** | **`0.008524 [0.007621, 0.009459]`** | **`+0.004518 [+0.003770, +0.005265]`** | **`+0.002479 [+0.001792, +0.003191]`** | `0.073312` | **`0.5500` (PASS)** | — | `1.0000` (dense DUP) |
| **`HYDROCONDUIT f45hydro` (Exp 2 — Primary)** | 37,654 | 45% | **83.4%** | **`0.008549 [0.007626, 0.009487]`** | **`+0.004543 [+0.003770, +0.005315]`** | **`+0.002504 [+0.001795, +0.003222]`** | `0.074107` | **`0.5500` (PASS)** | **`0.6719` (`0 > 70%`, PASS)** | `1.0000` (`118` dense `>150k` px; **STOP**) |
| **`HYDROCONDUIT f50hydro` (Exp 3)** | 37,654 | 50% | **82.8%** | **`0.008457 [0.007532, 0.009430]`** | **`+0.004451 [+0.003687, +0.005235]`** | **`+0.002412 [+0.001722, +0.003154]`** | `0.072799` | **`0.5143` (PASS)** | **`0.6578` (`0 > 70%`, PASS)** | `1.0000` (`118` dense `>150k` px; **STOP**) |

- **Rule-2 Fold-by-Fold `d_visible > 2.0` Diagnostic (`evidence/hydroconduit_proxy_audit.json`):** `H19_skeleton_dvis2 = 0.096757 [0.087402, 0.106214]` vs `HYDROCONDUIT_f45hydro_dvis2 = 0.085221 [0.075098, 0.094963]` ($\Delta = -0.011536 [-0.020635, -0.002477]$).

---

## 5. Reproducibility Commands

```bash
python3 scripts/restore_inputs.py
python3 scripts/verify_manifest.py
python3 -m pytest -q
python3 scripts/screen_hydroconduit_surface.py
python3 scripts/build_hydroconduit_variants.py
python3 scripts/report_hydroconduit_proxies.py
python3 scripts/audit_public_registry.py \
  --candidate docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif \
  --surface .cache/gems_inputs/hydroconduit_S_hydro_surface.tif \
  --out-name hydroconduit_public_registry_uniqueness
python3 scripts/make_hydroconduit_run_card.py
python3 scripts/validate_submission.py
python3 scripts/check_site.py
```
