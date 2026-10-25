# PhD Structural-Geophysical Analysis: `GEMSDOE32` (`0.2778` `[CLAIM]`), the Leaderboard Gap (`0.3195` / `0.4413` `[LEADERBOARD-SNAPSHOT]`), and the `POISSONFLEX` Lane (`2026-10-25`)

> **Governance & Evidence Discipline (Parallel-Run Protocol Rule 3):**
> - Every local evaluation figure is labeled **`HOLDOUT-DTI`** (`gems57-pooled-hide-v2`, `22,663` withheld positives across `8` spatially buffered quadrant folds, seeds `20 + 30`, `1,000` paired `20 km` block-bootstrap draws), **`PROXY`** (`62,122` off-catalogue USGS SGMC bedrock fault pixels `> 3 px` from `existing_faults`), or **`REGISTRY-MEASUREMENT`**.
> - `0.2778` (`GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`) is an owner-supplied **`[CLAIM]`** (`0` `ORGANIZER-CONFIRMED` submission receipts exist in `ledger/submissions.csv`). `0.4413` (recorded `2026-10-24`) and `0.3195` (older prompt snapshot) are **`[LEADERBOARD-SNAPSHOT]`** reference points from [DrivenData DOE GEMS Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). Never equate or project a local holdout number onto a live leaderboard score.
> - **Session Deliverable & Verdict (`evidence/poissonflex_run_card.json`):**
>   - **Research GeoTIFF (`✅ OK TO DOWNLOAD FOR RESEARCH — 10/10 + 13/13 automated format gates PASS`):** `docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif` (`SHA-256 = 37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b`, `45,000` unit dots, `float32`, `[0.0, 1.0]`, `0.0` outside footprint, `0` NaN, `EPSG:32611` `3730 × 3292`).
>   - **Slot Verdict (`⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT`):** `verdict = "negative"`, `submission_eligible = false`, `0` weekly slots spent (`3/3` experiment budget used).

---

## 1. Closure of Previous-Session Next Steps (`docs/NEXT_STEPS.md` Items #1 & #2)

Before designing or running any new model, we executed the two highest-priority open investigations queued by the preceding session (`docs/NEXT_STEPS.md`):

### 1.1 Complete `1,414`-Blob Dual-Reading Audit of `COULOMBLOQO` (`evidence/coulomb_loqo_dual_reading_selector.json`)

The prior session noted that `COULOMBLOQO standalone` (`0.113316` stored / `0.113890` paired `d_vis > 2.0` `HOLDOUT-DTI`, `0.009220` static `HOLDOUT-DTI`) had only been audited under the legacy literal dense-witness rule (`1.000` overlap against `17GEMSDOE E-proba-multiscale`, `5,094,398` positive pixels) and needed a complete evaluation under `vendor/gems57/uniqueness.py:dual_reading_decision` across the full `102`-repository public Git-blob inventory (`1,414` unique blobs, `missing_blobs == 0`).

Running that complete scan across all `1,321` non-self public rasters produced an unambiguous result:

| Candidate (`GEMSDOE92`) | Stored `d_vis > 2.0` `HOLDOUT-DTI` | Continuous Surface Worst Matched-Budget Overlap (`>150k` px) | Sparse Public Witnesses (`<=150k` px) `> 0.70` | Worst Operative Overlap (`dual_reading_decision`) | Verdict |
|---|---:|---:|---:|---:|---|
| `COULOMBLOQO standalone` (`37,654` px) | `0.113316` | `0.535853 <= 0.70` (`PASS`) | **`8` witnesses `> 0.70`** | **`0.739842 > 0.70`** (`GEMSDOE23 h29` `100,000` px) | **`negative` (STOP)** |
| `COULOMBLOQO dual45` (`37,654` px) | `0.101998` | `0.546954 <= 0.70` (`PASS`) | **`4` witnesses `> 0.70`** | **`0.722420 > 0.70`** (`62GEMSDOE ventcons` `125,890` px) | **`negative` (STOP)** |

**Takeaway:** Switching from the degenerate literal dense-witness rule (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`) to `dual_reading_decision` eliminates the `17GEMSDOE` `1.000` false positive (`0.5359` matched-budget), **but `COULOMBLOQO` still fails closed** against `100,000–125,890`-pixel intermediate-support rasters (`GEMSDOE23 h29/h24` and `62GEMSDOE ventcons`) that sit just below `DOT_FIELD_MAX_SUPPORT = 150,000`. Neither `COULOMBLOQO` arm can be promoted without changing the protocol threshold.

### 1.2 Exact Root Cause of `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` (`evidence/ne_quadrant_loqo_collapse_diagnostic.json`)

In the `BLINDFAULT` session, leave-one-quadrant-out (LOQO) models collapsed to `DTI = 0.000–0.005` on the `NE` fold (`0.1%–0.7%` of deployment dots placed in `NE`), and even `COULOMBLOQO standalone` allocated only `11.2%` (`4,221` dots) to `NE` vs `39.8%` (`14,983` dots) to `SW`. Stratifying all 19 geophysical bands and `existing_faults` across the four spatial quadrants (`NW`, `NE`, `SW`, `SE`) isolated three compounding causes:

| Diagnostic Quantity | `NW` | `NE` | `SW` | `SE` | Physical Interpretation |
|---|---:|---:|---:|---:|---|
| Valid footprint share (`5,167,373` px) | `22.3%` | **`27.6%`** | `27.6%` | `22.4%` | `NE` and `SW` are tied as the largest footprint quadrants |
| Mapped `existing_faults` share (`60,988` px) | `16.7%` | **`20.5%`** | **`33.7%`** | **`29.1%`** | **`SW + SE` hold `62.8%`** of mapped catalogue scarps (`8.76` vs `14.37–15.38` per `1,000` px) |
| `B07 geod_shearrate` median (`p90`) | `6.30` (`13.90`) | **`0.00` (`0.70`)** | `18.26` (`27.99`) | `15.50` (`30.41`) | Geodetic GPS strain-rate grid drops to zero across `>50%` of `NE` (outside Walker Lane / CNSB GPS station density) |
| `B04 geod_2ndinv` median (`p90`) | `15.60` (`28.09`) | **`3.80` (`6.10`)** | `34.50` (`46.40`) | `29.10` (`45.69`) | `NE` 2nd-invariant strain is **`9.1x` lower** than `SW`, so raw strain thresholds learned on `NW+SW+SE` starve `NE` |
| `B15 depth_to_base_surf` median (`p90`, m) | `253.5` (`1112.3`) | **`204.9` (`1395.3`)** | `454.9` (`1194.2`) | `320.2` (`1457.5`) | Bifurcated volcanic-plateau (`205 m` median) + deep graben (`1,395 m` `p90`) basement geometry in `NE` |
| `B13 iso_grav_anom` median (`p90`, mGal) | `-4.62` (`+5.76`) | **`-3.32` (`+8.64`)** | `-9.03` (`-0.41`) | `-12.27` (`-1.02`) | `+5.7` to `+9.0 mGal` regional crustal Bouguer/isostatic baseline shift across `NE` vs `SW/SE` |

Because `HistGradientBoostingClassifier` splits on raw feature levels (`geod_shearrate > 12`, `geod_2ndinv > 20`, `iso_grav_anom < -5`), a fold model trained on `NW + SW + SE` outputs systematically depressed raw probabilities across `NE`.

---

## 2. PhD-Level Analysis: Why `GEMSDOE32` (`0.2778` `[CLAIM]`) Led the ~90-Repo GEMSDOE Fleet, and How to Reach `0.3195`–`0.4413`

### 2.1 Exact Mathematical Anatomy of the Competition Metric (`DTI`)

Per the [DOE GEMS Competition Problem Description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), the [Official Rules PDF (`96647.pdf`)](https://docs.nlr.gov/docs/fy26osti/96647.pdf), the [DrivenData Reference Solution](https://github.com/drivendataorg/gems-prize-reference-solution), and the [Tversky Index formulation](https://en.wikipedia.org/wiki/Tversky_index), predictions $P \in [0, 1]^{3730 \times 3292}$ on the `100 m` [EPSG:32611](https://epsg.io/32611) grid are evaluated strictly on unmapped valid cells $\Omega' = \text{footprint} \setminus \text{existing\_faults}$ (`5,106,385` pixels) via maximum-convolution with a `300 m` (`3`-pixel) radial linear tent kernel $K(\Delta r) = \max(0, 1 - \|\Delta r\|_2 / 3)$:

$$M(A)_i = \max_{j:\,\|i - j\|_2 \le 3} A_j \cdot \left(1 - \frac{\|i - j\|_2}{3}\right), \qquad \text{DTI}(P, T) = \frac{\text{TP}_w}{\text{TP}_w + 0.2\,\text{FP}_w + 0.8\,\text{FN}_w}$$

where $\text{TP}_w = \sum_{i \in \Omega'} \min(M(P)_i, M(T)_i)$, $\text{FP}_w = \sum_{i \in \Omega'} \max(M(P)_i - M(T)_i, 0)$, and $\text{FN}_w = \sum_{i \in \Omega'} \max(M(T)_i - M(P)_i, 0)$.

Three exact consequences govern every winning submission in this competition:

1. **Continuous Probability Mass Dilution vs Binary Unit Support:** Any diffuse probability sheet $P_i \in (0.05, 0.40)$ spanning millions of basin pixels inflates $0.2\,\text{FP}_w$ across `~5.1M` background cells (`FP_w ~ 500,000+`), crushing $\text{DTI} < 0.06$ even when recall is high. Conversely, discrete unit impulses $P_i \in \{0, 1\}$ concentrate maximum `300 m` tent height (`1.0` at center, `0.667` at `100 m`, `0.333` at `200 m`) solely on high-odds structural crests.
2. **Why `GEMSDOE32`'s `D2.8` Blue-Noise Decimation Generated `79.2%` of Its Gain (`0.1922 -> 0.2600` `[CLAIM]`):**
   Byte-exact reconstruction of `parent_R0_zeros.tif` (`registry/parents/R0.json`) proves zero-pixel-XOR identity across four deterministic stages:
   - **`H19-5` Connected Ridge Skeleton (`121,131` px $\to$ `0.1922` `[CLAIM]`):** A continuous `1`-px fault trace places `3` adjacent unit pixels per `300 m` of strike. Because $M(P)$ uses a **$\max$** operator (not a sum!), three adjacent pixels along strike cover almost the exact same `300 m` tent envelope as a single pixel, wasting `~64%` of pixel mass on redundant halo overlap where any off-fault excursion pays full `0.2 FP_w` penalty without adding `TP_w`.
   - **`D2.8` Poisson-Disk Decimation (`121,131 -> 44,090` px at $d_{\min} = \sqrt{8} \approx 2.828\text{ px}$ $\to$ `0.2600` `[CLAIM]`, `+0.0678`):** Spacing unit dots by `283 m` along a 1D fault trace keeps $M(P)$ between `0.529` (midpoint at `141 m`) and `1.000` (dot center) everywhere along the fault (`>82%` of full continuous-line `TP_w` credit!) while slashing total `FP_w` volume by **`63.6%`**.
   - **`H27-4-SOLO` Non-Fault Landform Veto (`44,090 -> 40,199` px $\to$ `0.2708` `[CLAIM]`, `+0.0108`):** Prunes short isolated alluvial-fan wash walls and drainage divides lacking along-strike structural continuity.
   - **`B2` Catalogue Dead-Zone Collar Prune (`40,199 -> 37,654` px = `D2.8 & (d_cat > 2.0)` $\to$ `0.2778` `[CLAIM]`, `+0.0070`):** Because `existing_faults` pixels are excluded from $\Omega'$, a dot placed at $d_{\text{cat}} \le 2.0\text{ px}$ loses up to half its `300 m` tent kernel onto un-scored catalogue cells while paying `0.2 FP_w` on adjacent unmapped cells.
3. **Marginal Value Theorem Under $\beta / \alpha = 4$:** Adding one spaced unit dot of halo integral $h = \sum_{\|r\|<3}(1 - \|r\|/3) \approx 9.65$ mass-pixels with expected truth overlap fraction $\bar{c} = \Delta\text{TP}_w / h$ strictly increases $\text{DTI}$ iff:
   $$\frac{\partial \text{DTI}}{\partial N} > 0 \iff \bar{c} > \frac{\alpha\,\text{DTI}}{1 + (\beta - \alpha)\,\text{DTI}} = \frac{0.2\,\text{DTI}}{1 + 0.6\,\text{DTI}}$$
   At $\text{DTI} = 0.11$, a dot needs only **$\bar{c} > 2.07\%$** expected overlap to improve DTI; even at $\text{DTI} = 0.4413$, any dot with **$\bar{c} > 6.98\%$** improves the score! `GEMSDOE32`'s hard-coded `37,654` support arose as an uncalibrated byproduct of `D2.8` on `H19-5`, leaving recall on the table whenever multi-physics features identify additional high-probability structures.

### 2.2 Why `GEMSDOE32` Plateaus at `0.2778` `[CLAIM]` and What Separates `0.2778` from `0.3195` / `0.4413` (`[LEADERBOARD-SNAPSHOT]`)

Our empirical holdout Ladder across `30` implemented lanes in `GEMSDOE92` (`0.004006` static `HOLDOUT-DTI` for `R0` $\to$ `0.008824` for `POISSONFLEX` / `0.009220` for `COULOMBLOQO`, a **`2.2x–2.3x` static holdout gain over `R0`**; and `0.095386` $\to$ **`0.120957`** on `62,122` off-catalogue USGS SGMC bedrock faults) exposes the exact ceiling of `GEMSDOE32` and how top `0.35–0.44` leaderboard entries surpass it:

1. **`GEMSDOE32` Is Nearly Purely Topographic (`B19 det_elev_slope` Bias):** `H19-5` extracts range-front topographic breaks of slope. Yet in the [GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/) / [OpenEI GDR #1391](https://gdr.openei.org/submissions/1391) hidden-geothermal setting (e.g., McGinness Hills, Tungsten Mountain, Bradys, Desert Peak, Dixie Valley piedmont step-overs), the highest-value **unmapped** faults are either (a) **low-relief Holocene piedmont scarps (`1–4 m` vertical offset)** smeared below the Nyquist limit of the `100 m` competition DEM, or (b) **intrabasin concealed accommodation zones and relay ramps** expressed in [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) airborne magnetics/radiometrics, isostatic gravity, basement depth, and MT conductivity.
2. **Non-Fault Topographic Mimics in 100 m DEMs:** Without subsurface polarity/Poisson discrimination, 100 m break-of-slope detectors place thousands of false-positive dots on **Pleistocene Lake Lahontan highstand wave-cut shorelines (`~1,330 m` contour)**, incised alluvial-fan wash walls, and flat-lying Tertiary basalt mesa rims.
3. **Pixelwise Tabular GBDT vs End-to-End 2D Convolutional / Soft-DTI Lineament Architecture:** Every model in `GEMSDOE92` (`COULOMBLOQO`, `EULERFUSE`, `POISSONFLEX`) uses pixelwise `HistGradientBoostingClassifier` on handcrafted multi-scale filters (`100 m`–`1.2 km`) followed by heuristic 1D ridge thinning. Pixelwise trees cannot see `5–25 km` **en-echelon fault-tip relay geometry**, step-over linkage across alluvial fans, or curvilinear range-front continuity, nor do they optimize the `300 m`-halo Tversky objective directly.
4. **External `1 m`–`10 m` Official USGS 3DEP Elevation & Quaternary Fault-Trace Context (Permitted Public Data Outside Sandbox):** Under [Official Rules (`96647.pdf`)](https://docs.nlr.gov/docs/fy26osti/96647.pdf), public government datasets available free of charge prior to the competition deadline — specifically [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) `1 m` LiDAR / `1/3 arc-second (~10 m)` seamless DEMs — resolve `0.5–2 m` Holocene fault scarps across Basin-and-Range alluvial fans (`100x` finer spatial resolution than `B12/B19`) while immediately separating `0.0%`-grade horizontal Lake Lahontan wave-cut benches from dipping fault scarps! (In this sandbox, outbound internet is restricted to GitHub/PyPI/npm, so USGS `tnmaccess` / `planetarycomputer` S3 buckets cannot be queried directly.)

**Actionable Engineering Path to `0.3195`–`0.4413` (Outside Network-Restricted Sandbox):**
1. **Multi-Scale 2D U-Net / ConvNeXt-Small Trained Directly on Differentiable Soft-DTI Loss** ($\mathcal{L}_{\text{Soft-DTI}} = 1 - \frac{\langle \tilde{M}_\tau(P), M(T)\rangle}{\langle \tilde{M}_\tau(P), M(T)\rangle + 0.2\,\text{FP}_\tau + 0.8\,\text{FN}_\tau}$ using smooth max-pooling $\tilde{M}_\tau$ over the exact `300 m` tent kernel) with `8`-fold buffered LOQO cross-fitting on all 19 bands + `POISSONFLEX` physical operators (`f01`–`f30`).
2. **Ingest Official `1/3 arc-sec (10 m)` & `1 m` LiDAR USGS 3DEP Tiles** ([USGS 3DEP](https://www.usgs.gov/3d-elevation-program)), downsampling `10 m` directional scarp curvature, Lahontan shoreline contour flatness, and across-fan profile offsets onto the `100 m` `EPSG:32611` grid (verified against single-feature `<= 0.90` leakage canaries).
3. **Calibrated Hybrid Allocation (`45,000–58,000` Blue-Noise Dots at $d_{\min} \in [2.6, 2.8]\text{ px}$)** preserving catalogue-density regional priors where surface scarps dominate while injecting high-precision `POISSONFLEX` Poisson-demagnetization + basement-rollover conduits in sediment-covered basins.

---

## 3. Pre-Registered Hypothesis & Physical Design of `POISSONFLEX`

Pre-registered in [`docs/HYPOTHESES_20261025_POISSONFLEX.md`](HYPOTHESES_20261025_POISSONFLEX.md) before writing model code, **`POISSONFLEX`** tests four genuinely untried structural-geophysical operators on the `100 m` grid (`gems/poissonflex.py`, verified by `7/7` unit tests in `tests/test_poissonflex.py`):

1. **Poisson Gravity–Magnetic Relation Breakdown (`f01`–`f04`, `moving_window_poisson`):** Under Poisson's (1826) potential-field theorem, a homogeneous lithologic body or unaltered pluton/ash-flow contact obeys $\nabla g_{\text{iso}} \propto (\Delta\rho / \Delta J)\,\nabla g_{\text{pseudo}}$, where $g_{\text{pseudo}} = \mathcal{F}^{-1}\{\widehat{\text{RTP}}(\mathbf{k}) / |\mathbf{k}|\}$ is Baranov's (1957) wavenumber pseudogravity transform of `Band 2` (`rtp`). In a hydrothermally active Basin-and-Range fault zone, rising $120\text{–}250\,^\circ\text{C}$ fluids **destroy magnetite to pyrite/hematite/illite** (`RTP` trough / decorrelation) while **precipitating dense quartz/calcite fault-core cement** (`iso_grav_anom` gradient ridge). Over `9 × 9` (`900 m`) moving windows, `f03_poisson_demag_conduit` isolates high gravity-gradient fault conduits with collapsed local $|r(g_{\text{iso}}, g_{\text{pseudo}})|$ and negative $\nabla^2\text{RTP}$ troughs — rejecting unaltered volcanic/pluton contacts where $g_{\text{iso}}$ and $g_{\text{pseudo}}$ co-vary linearly.
2. **Listric Hanging-Wall Rollover & Differential Compaction Flexure (`f05`–`f08`, `basement_rollover_flexure`):** Computes maximum positive (`footwall shoulder`) and negative (`hanging-wall rollover`) Hessian principal curvatures of `Band 15` (`depth_to_base_surf`) at $\sigma \in \{300, 700\}\text{ m}$ plus differential-compaction lock where subtle surface topographic curvature aligns with buried basement-step orientation.
3. **Drainage Knickpoint Saddle & Along-Strike Line-Integral Accumulation (`f09`–`f11`, `knickpoint_saddle_and_integral`):** Detects saddle-shaped (`\lambda_1 \lambda_2 < 0`) range-front canyon thalweg convexities and integrates them along `8` candidate fault-strike azimuths (`1.5 km` Gaussian line kernel), capturing aligned knickpoints across parallel canyons even where interfluve scarps are eroded.
4. **Quadrant-Deconfounded Covariate Rank Alignment & Nested Visible-Only OOF Support Selection (`within_quadrant_rank`, `bolstad_equalize_quadrants`, `select_nested_oof_budget`):** Aligns raw regional-drift covariates (`geod_shearrate`, `geod_2ndinv`, `iso_grav_anom`, `depth_to_base_surf`) via unlabeled within-quadrant percentile ranks (`0` labels used) and selects optimal blue-noise support $S_{\text{opt}} \in \{26\text{k}, 30\text{k}, 34\text{k}, 37,654, 41.5\text{k}, 45\text{k}\}$ strictly on nested `3`-fold visible-catalogue OOF (`d_inner_vis > 2.0`, outer hidden fold never read).

---

## 4. Auditable Experimental Results (`3/3` Pre-Registered Arms)

### 4.1 Stage 2 — Single-Feature Leakage Canary Audit (`.cache/poissonflex/canaries.json`)

Every one of the `30` features (`f01`–`f30`) plus both `1D` crest scaffolds (`L_scarp_knick`, `L_poisson_flex`) passed the Protocol Rule 4 single-feature holdout AUC gate (`<= 0.90`) across all `22,663` withheld positives (`32 / 32 PASS`, **`max_symmetric_auc = 0.616108`**):

| Feature / Scaffold | Raw Holdout AUC | Symmetric Holdout AUC | Status (`<= 0.90`) | Physical Verification Note |
|---|---:|---:|---|---|
| `f12_rel_log_slope_break` | `0.616108` | **`0.616108`** | **PASS** | Strongest single local topographic scarp indicator |
| `L_scarp_knick` (scaffold) | `0.603321` | `0.603321` | **PASS** | Break-of-slope + knickpoint 1D crest scaffold |
| `f23_coulomb_ext_aligned` | `0.566654` | **`0.566654`** | **PASS** | `+0.0092` AUC over unaligned `f24` (`0.557429`) from quadrant alignment |
| `f11_valley_pinch_break` | `0.554517` | **`0.554517`** | **PASS** | New canyon-pinch geomorphic fault-crossing signal |
| `f22_cross_physics_axial_lock` | `0.548810` | **`0.548810`** | **PASS** | Circular axial strike lock across topo, gravity, basement, RTP & knickpoint |
| `f03_poisson_demag_conduit` | `0.548458` | **`0.548458`** | **PASS** | **`3.66x` excess AUC** (`+0.0485` vs `+0.0133`) over raw `f20_rtp_tilt_edge` (`0.513278`) |
| `f10_knick_strike_integral` | `0.541065` | **`0.541065`** | **PASS** | Along-strike multi-canyon knickpoint alignment |
| `f05_base_shoulder_curv` | `0.466343` | **`0.533657`** | **PASS** | Buried basement rollover/shoulder Hessian curvature |
| `f25_strain_2ndinv_qrank` | `0.526468` | **`0.526468`** | **PASS** | **`2.60x` excess AUC** over raw `f26_strain_2ndinv_raw` (`0.510186`) |
| `f07_compaction_flex_lock` | `0.524771` | **`0.524771`** | **PASS** | Surface-to-basement differential compaction lock |

### 4.2 Stage 3 & Stage 4 — Primary Draw-Blind `HOLDOUT-DTI`, Static `HOLDOUT-DTI`, and Off-Catalogue `USGS SGMC` `PROXY` (`evidence/poissonflex_holdout.json`)

Nested visible-only OOF calibration selected `$S_{\text{opt}} = 41,500$` on `seed=20` (visible OOF DTI `0.098089` vs `0.097165` at `37,654`) and `$S_{\text{opt}} = 45,000$` on `seed=30` (`0.113578` vs `0.113229`) and full deployment (`0.104300` vs `0.100383` at `37,654`):

| Candidate / Control | Dots | Primary Strict Draw-Blind `HOLDOUT-DTI` (`d_vis > 2.0`, `22,663` px) | Paired $\Delta$ vs `poissonflex_opt` (`95% CI`) | Low-Conspicuity `HOLDOUT-DTI` (`6,065` px) | Static Deployment `HOLDOUT-DTI` (`d_cat > 2.0`) | Off-Catalogue `USGS SGMC` `PROXY` (`62,122` px) |
|---|---:|---:|---:|---:|---:|---:|
| **`POISSONFLEX poissonflex_opt` (Best Arm)** | **`45,000`** | **`0.107466 [0.094158, 0.120431]`** | — | `0.006341 [0.003294, 0.009611]` | **`0.008824 [0.007601, 0.010081]`** | **`0.120957` (`#1` among top LOQO lanes)** |
| `POISSONFLEX poissonflex_eq` (Arm 1) | `37,654` | `0.103768 [0.090267, 0.117066]` | `+0.003698 [+0.001774, +0.005673]` | `0.005665 [0.002915, 0.008680]` | `0.008176 [0.006938, 0.009399]` | `0.105407` |
| `POISSONFLEX poissonflex_raw` (Arm 2) | `37,654` | `0.102861 [0.089368, 0.116130]` | `+0.004605 [+0.002709, +0.006717]` | `0.005323 [0.002649, 0.008368]` | `0.008180 [0.006894, 0.009460]` | `0.107319` |
| `COULOMBLOQO standalone` (Repo Holdout-Best) | `37,654` | **`0.113890 [0.100124, 0.127440]`** | **`-0.006424 [-0.013250, +0.000170]`** | `0.008205 [0.004352, 0.012814]` | **`0.009220 [0.007983, 0.010493]`** | `0.089332` |
| `H19-5` Skeleton (`GEMSDOE32` Ancestor) | `~116k` | `0.096757 [0.084298, 0.108421]` | **`+0.010709 [+0.002297, +0.018444]`** | `0.007166 [0.004586, 0.010133]` | — | — |
| `R0` (`GEMSDOE32` `0.2778` `[CLAIM]` Parent) | `37,654` | — | — | — | `0.004006 [0.003408, 0.004651]` | `0.095386` |
| `BLINDFAULT blindtopo` (Prior Session) | `37,654` | `0.047896 [0.038079, 0.057970]` | (`+0.059570` gain) | `0.006118 [0.003706, 0.008819]` | `0.005526 [0.004610, 0.006469]` | — |
| `COULOMBDM coulomb1d` / `s45` (Zero-Label) | `37,654` | `0.094496 [0.085916, 0.102867]` | (`+0.012970` gain) | — | `0.007816 [0.006994, 0.008644]` | `0.075208` |

### 4.3 Mechanistic Discovery: The Double-Edged Quadrant Calibration Paradox (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`)

Stratifying deployment dot shares and holdout DTI by quadrant (`NW`, `NE`, `SW`, `SE`) reveals a deep geophysical-statistical trade-off that explains **every single number** in Table 4.2:

| Model | Deployment Dot Shares (`NW / NE / SW / SE`) | Primary `d_vis > 2.0` Mean DTI (`NW / NE / SW / SE`) | Static `d_cat > 2.0` Mean DTI (`NW / NE / SW / SE`) | Off-Catalogue `SGMC PROXY` |
|---|---|---|---|---:|
| **`POISSONFLEX poissonflex_opt`** (`45,000` dots) | **`21.9% / 22.7% / 33.8% / 21.6%`** | **`0.1176` (`#1`)** / `0.1216` / `0.0960` / `0.1021` | **`0.0121` (`#1`)** / `0.0086` / `0.0086` / `0.0067` | **`0.120957` (`+35.4%`)** |
| `POISSONFLEX poissonflex_eq` (`37,654` dots) | `22.1% / 22.1% / 34.3% / 21.4%` | `0.1175` / `0.1203` / `0.0898` / `0.0975` | `0.0119` / `0.0075` / `0.0079` / `0.0062` | `0.105407` (`+18.0%`) |
| `COULOMBLOQO standalone` (`37,654` dots) | `24.3% /` **`11.2%`** `/ 39.8% / 24.7%` | `0.1119` / **`0.1366`** / `0.1022` / `0.1171` | `0.0116` / `0.0088` / `0.0097` / `0.0069` | `0.089332` |
| `H19-5` (`GEMSDOE32` Skeleton) | — | `0.0940 / 0.1155 / 0.0844 / 0.0965` | — | — |
| `R0` (`GEMSDOE32` Parent) | `19.6% / 23.1% / 33.8% / 23.5%` | — | `0.0041 / 0.0047 / 0.0037 / 0.0036` | `0.095386` |

1. **Complete Cure of `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`:** Within-quadrant unlabeled covariate rank alignment (`within_quadrant_rank`) completely eliminated `NE` starvation, lifting `NE` dot allocation from `0.1%` (`BLINDFAULT`) and `11.2%` (`COULOMBLOQO`) to **`22.7%` (`10,215` dots)** — closely matching `R0`'s `23.1%`!
2. **`POISSONFLEX` Beats `H19-5` & `R0` in All 4 Quadrants, and Beats `COULOMBLOQO` in `NW` (`0.117551` vs `0.111948` Primary; `0.012115` vs `0.011625` Static):** Where mapped fault density matches footprint area (`NW`), adding Poisson demagnetization, basement rollover, and canyon knickpoints improves holdout recovery over `COULOMBLOQO`.
3. **Why `COULOMBLOQO` Scored `0.1366` in `NE` With Only `4,221` (`11.2%`) Dots While `POISSONFLEX` Jumped `+35.4%` on Off-Catalogue Bedrock Faults:**
   - In `COULOMBLOQO`, the accidental near-zero geodetic strain in `NE` acted as an **implicit precision filter** on the hide-and-recover `existing_faults` catalogue: placing only `4,221` ultra-high-slope dots in `NE` captured the few sharpest mapped `NE` range fronts while cutting `0.2 FP_w` in `NE` by `58%`!
   - When `POISSONFLEX` restored `NE` to `10,215` dots (`22.7%`) and activated the `L_poisson_flex` subsurface scaffold (`18.1%` of dots on low-conspicuity `<= 0.44` terrain), those `+6,000` concealed/bedrock `NE` and `NW` dots **boosted off-catalogue `USGS SGMC` fault recovery by `+35.4%` (`0.089332 -> 0.120957`, beating `R0` `0.095386` by `+26.8%`!)**, while on the surface-scarp-biased `existing_faults` hide-and-recover test those unmapped bedrock/intrabasin structures were counted as false positives (`-0.006424` overall paired delta vs `COULOMBLOQO`).

### 4.4 Stage 5 — Complete Local (`97` Rasters) & Public (`1,414` Blobs / `102` Repos) Uniqueness Audit (`evidence/poissonflex_uniqueness.json`)

| Scope | Rasters Compared | `poissonflex_opt` Continuous Surface Max `\|\rho\|` (`<= 0.90`) | `poissonflex_opt` Worst Overlap | Gate Status & Witness |
|---|---:|---:|---:|---|
| **Local `GEMSDOE92` Registry** | `97` | **`0.1674 <= 0.90` (`PASS`)** | **`0.6488 <= 0.70` (`PASS`)** | **UNIQUE LOCALLY** (vs `R0`: `0.5031`; vs `COULOMBLOQO standalone`: `0.5997`; worst local: `COULOMBLOQOnocoulomb` `0.6488`) |
| **Public Comparable-Budget (`<= 80,000` dots, `102` repos)** | `1,158` | **`0.1311 <= 0.90` (`PASS`)** | **`0.6804 <= 0.70` (`PASS`)** | **UNIQUE AT COMPARABLE BUDGET** (worst: `GEMSDOE52 h87` `61,427` px at `0.6804`; `GEMSDOE63` `54,864` px at `0.6699`) |
| **Public Continuous Surfaces (`> 150,000` px, matched-budget)** | `185` | **`0.4668 <= 0.90` (`PASS`)** | **`0.5471 <= 0.70` (`PASS`)** | `17GEMSDOE E-proba-multiscale` literal `1.0000` $\to$ matched-budget `0.3652 <= 0.70` (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`) |
| **Public Intermediate-Support (`100k–126k` px under `150k` cap)** | `61` | `0.1311 <= 0.90` (`PASS`) | **`0.7541 > 0.70` (`STOP`)** | `62GEMSDOE ventcons` (`125,890` px = `2.80x` our support, `0.7541`) & `GEMSDOE23 h29` (`100,000` px, `0.7506`) — flagged as `#IR-92-INTERMEDIATE-SUPPORT-ASYMMETRIC-OVERLAP` |

Because `poissonflex_opt` (`0.107466`) both trails repository holdout-best `COULOMBLOQO standalone` (`0.113890`) under Protocol Rule 6 **and** trips the strict `150,000`-pixel dot-field overlap ceiling on `100k–126k`-pixel rasters (`0.7541 > 0.70`) under Protocol Rule 1, we fail closed: **`verdict = "negative"`**, **`submission_eligible = false`**, **`0` weekly submission slots spent**.

---

## 5. Limitations & Concrete Next Steps for the Next Session

1. **Asymmetric Overlap Bias on `100k–150k`-Dot Public Rasters (`#IR-92-INTERMEDIATE-SUPPORT-ASYMMETRIC-OVERLAP`):** Both `COULOMBLOQO standalone` (`0.7398`) and `POISSONFLEX` (`0.7541`) are unique against **every** comparable-budget (`<= 80,000`-dot) submission across all `102` repositories, yet fail `_near(M)[T].mean() <= 0.70` against `100,000–125,890`-pixel rasters whose `3`-pixel halos blanket `~31%` of all range-front scarps in the Great Basin. Any future candidate targeting `verdict: "promote"` under the unaltered `DOT_FIELD_MAX_SUPPORT = 150,000` rule must either (a) shift `>35%` of its support onto genuine intrabasin/piedmont structures (`>3 px` from `H19-5`) while maintaining `HOLDOUT-DTI > 0.113890`, or (b) apply symmetric/matched-K overlap whenever `their_dots > 1.5 * my_dots` if authorized by operator governance.
2. **Next Untried Hypothesis (`THERMAL-UPFLOW-PECLET`, Rank #2 in `docs/HYPOTHESES_20261025_POISSONFLEX.md`):** Combine `POISSONFLEX`'s high-SGMC-recall Poisson/flexure operators with advective groundwater Péclet thermal plumes (`OpenEI GDR #1391`) and **selective quadrant calibration** (applying within-quadrant rank alignment to subsurface channels while retaining catalogue-density prior scaling on surface-scarp channels so `NE` is neither starved as in `BLINDFAULT` nor over-allocated relative to `existing_faults` density).
3. **End-to-End 2D Convolutional Soft-DTI Lineament Learner (CPU-Feasible Patch ConvNet):** Replace pixelwise `HistGradientBoostingClassifier` with a lightweight `64 × 64`-patch 2D dilated ConvNet (`~80k` parameters, `< 15 min` CPU training across 8 LOQO folds) trained directly on the differentiable `300 m`-tent Soft-DTI loss so `5–15 km` along-strike structural continuity and step-over relay geometry are learned directly rather than approximated by Gaussian filters.
