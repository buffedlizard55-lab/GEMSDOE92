# Pre-Registered Geological Hypotheses — Session `2026-10-25` (Lane: `PROVINCETOE`)

**Status:** Frozen *prior* to fitting any model or generating any candidate raster in this session (`Protocol Rules 1–6`).  
**Method lane (single lane for this session):** `PROVINCETOE` — *Tectonic-Province Strain-Invariant Wallace Basal Toe-Concavity & Carbonate-Horst Isostatic Flexure LOQO*.  
**Experiment budget cap:** `3` pre-registered arms (`provincetoe`, `globalraw`, `piedbasin`), `<= 2` hours wall-clock, `0` live DrivenData weekly submission slots spent (`promotion` is an external human selector step).

---

## 1. Forensic Motivation: Resolving Prior `docs/NEXT_STEPS.md` Items #1 & #2 Before Designing New Physics

Before formulating new hypotheses, we executed items #1 and #2 of `docs/NEXT_STEPS.md` against the SHA-256-verified competition stack (`.cache/gems_inputs/`) and a freshly Git-SHA1-verified public registry scan across all `102` `buffedlizard55-lab` `*GEMSDOE*` repositories (`1,774` `.tif` paths $\to$ `1,413` unique Git blobs $\to$ `1,403` valid template-grid rasters, of which `1,354` belong to the `101` external repositories outside `GEMSDOE92`).

### 1.1 Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Led Listed Sites — and Why Re-Pruning It Cannot Reach `0.3195` / `0.4413` `[LEADERBOARD-SNAPSHOT]`
In the shared evaluator (`vendor/gems57/metric.py`), the Distance-Weighted Tversky Index (DTI) weights false positives by $\alpha = 0.2$ and false negatives by $\beta = 0.8$ (noting `#IR-92-ALPHA-BETA-PROSE-SWAP`: prose in older docs inverted $\alpha/\beta$, whereas code and the [official reference solution notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) confirm `0.2` FP / `0.8` FN loss weights; the notebook itself does not implement the organizer's distance-weighted scorer) with a $300\text{ m}$ (`3 px`) linear triangular proximity kernel and pixel-exact masking of known `existing_faults.tif` (`cat`). Local pixel forensics establish an exact zero-XOR cascade:
1. `H19-5` (`19GEMSDOE`, `121,131` px, `0.1922` `[CLAIM]`): 1-px skeleton of a multi-physics fault detector.
2. `D2.8` (`GEMSDOE25`, `44,090` px, `0.2600` `[CLAIM]`): Poisson-disk de-aliasing at $\approx 2.83\text{ px}$ (`-63.6%` redundant within-kernel mass).
3. `SOLO` (`GEMSDOE28`, `40,199` px, `0.2708` `[CLAIM]`): exact identity $\text{XOR}(\text{SOLO}, D_{2.8} \land d_{\text{cat}} > 1.0) = 0$.
4. `R0` / `GEMSDOE32` (`h33-h33-2-b2-zeros`, `37,654` px, `0.2778` `[CLAIM]`): exact identity $\text{XOR}(R_0, D_{2.8} \land d_{\text{cat}} > 2.0) = 0$.

Every stage from `H19-5` to `R0` strictly deleted zero-gain FP mass inside `H19-5`'s support without discovering a single new fault segment (`TP_w` flat/non-increasing). Surpassing `0.2778` `[CLAIM]` requires genuine **true-positive fault discovery** at $d_{\text{cat}} > 2.0\text{ px}$ across geological provinces where `H19-5` and existing `GEMSDOE*` lanes are blind.

### 1.2 Resolution of `docs/NEXT_STEPS.md` Item #1: Both `COULOMBLOQO` Arms Still Trip `> 0.70` Under `dual_reading_decision` — and Why
Evaluating `COULOMBLOQO standalone` (`HOLDOUT-DTI` `0.113316` Rule-2 `d_visible > 2.0`, `0.009220` static `d_cat > 2.0`) and `COULOMBLOQO dual45` (`0.101998` Rule-2, `0.009107` static) across all `1,354` external public rasters using `vendor/gems57/uniqueness.dual_reading_decision` (`DOT_FIELD_MAX_SUPPORT = 150_000`) proves:
- Every dense continuous surface (`> 150,000` positive pixels, including `17GEMSDOE E-proba-multiscale` with `5,167,373` positive footprint pixels) drops strictly `<= 0.70` under `matched_budget_support`.
- **However**, because rasters with `<= 150,000` positive pixels retain literal 3-px dot overlap:
  - `COULOMBLOQO standalone` collides `> 0.70` with **`8` external `dot_field` rasters**, led by `GEMSDOE23/docs/downloads/gemsdoe23-h29-dealiased-habitat-20261002-7bf9fac6-allfinite.tif` (`100,000` px, **`0.739842`**), `62GEMSDOE` (`125,890` px, `0.725129`), `12GEMSDOE` (`103,347` px, `0.704812`), and `GEMSDOE52` (`61,427` px, **`0.700404`**) $\to$ **`matched_budget_duplicate = True`**.
  - `COULOMBLOQO dual45` collides `> 0.70` with **`4` external `dot_field` rasters** (`GEMSDOE23` `h29-dealiased-habitat` **`0.722420`** and `h24-dispersed-habitat` `0.718649`) $\to$ **`matched_budget_duplicate = True`**.
- **Root-cause slope stratification (`REGISTRY-MEASUREMENT`):** Stratifying `COULOMBLOQO standalone` by Band 19 `det_elev_slope` reveals a severe alpine-cliff localization bias caused by `hessian_ridge_strength(log_slope)` (`max(0, -\lambda_{\min})`):

| Slope stratum (`Band 19 det_elev_slope`) | Footprint share | True `existing_faults` share | `COULOMBLOQO standalone` dot share | `COULOMBLOQO` 3-px overlap vs `GEMSDOE23` (`100k` px) |
|---|---:|---:|---:|---:|
| `[0.0°, 2.5°)` (basin floor / blind / playa margin) | `40.4%` | **`25.7%`** | **`4.2%`** (`6.1x` under-allocated) | `0.6317` |
| `[2.5°, 6.0°)` (piedmont toe / fan apron scarp) | `19.8%` | **`26.9%`** | `18.4%` | `0.6180` |
| `[6.0°, 12.0°)` (lower range-front facet) | `15.6%` | `24.4%` | `32.2%` | `0.7364` |
| `[12.0°, 90.0°)` (steep alpine cliffs / canyon walls) | `24.1%` | **`22.8%`** (`0.95x` lift) | **`45.2%`** (`17,021` dots!) | **`0.8020`** |

**`52.6%` of all true USGS/INGENIOUS Quaternary faults lie at `det_elev_slope < 6.0°`**, whereas `slope >= 12.0°` has **slight negative fault enrichment (`22.8% / 24.1% = 0.95x`)** because alpine spur crests and V-canyons dominate steep interiors. Yet `hessian_ridge_strength(log_slope)` peaks mid-cliff on `>= 12°` walls, dumping `45.2%` of `COULOMBLOQO`'s budget into steep range interiors where `GEMSDOE23` (`80.20%`) and `62GEMSDOE` (`83.62%` in `6°–12°`) also concentrate.

### 1.3 Resolution of `docs/NEXT_STEPS.md` Item #2: Quantitative Mechanism of `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`
Computing physical covariate distributions across the four label-blind `gems57` quadrants (`NW`, `NE`, `SW`, `SE`) resolves why both `COULOMBLOQO` and `BLINDFAULT` collapsed in `NE`:

| Quadrant | Footprint share | Catalogue fault density | Off-catalogue `SGMC` bedrock fault share | Median `Band 7 geod_shearrate` | Median fault `Band 3 tmi_hg` | Median fault `Band 5 grav_slope` | `H19-5` dot share | `COULOMBLOQO` dot share | `BLINDFAULT` dot share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `NW` | `22.3%` | `8.80‰` (`16.7%`) | `14.6%` (`8,270` px) | `6.3` | `15.8` | `0.119` | `22.5%` | `25.3%` | `35.4%` |
| **`NE`** | **`27.6%`** | **`8.76‰` (`20.5%`)** | **`41.6%` (`23,652` px!)** | **`0.0`** | **`6.4`** | **`0.129`** | **`27.7%`** | **`11.2%`** | **`0.7%` (`272` px!)** |
| `SW` | `27.6%` | `14.37‰` (`33.7%`) | `16.9%` (`9,578` px) | **`18.3`** | **`28.7`** | `0.088` | `27.9%` | **`39.8%`** | **`41.4%`** |
| `SE` | `22.4%` | `15.38‰` (`29.1%`) | `27.0%` (`15,322` px) | **`15.5`** | `12.2` | **`0.129`** | `21.9%` | `23.7%` | `22.6%` |

**Diagnosis:** `NE` (Northeastern Great Basin — Ruby Mountains, Independence Mountains, Jarbidge, Eastern Nevada Paleozoic Carbonate Province) has **the exact same catalogue fault density as `NW` (`8.76‰` vs `8.80‰`)** and **`41.6%` of all unmapped USGS SGMC bedrock faults** — more than any other quadrant! Furthermore, when `H19-5` allocates a footprint-proportional `27.7%` budget to `NE`, its `NE` quadrant-internal `HOLDOUT-DTI` (`0.0770–0.0824`) is **higher** than `NW` (`0.0603–0.0695`) and `SW` (`0.0624–0.0644`). Global LOQO models collapsed in `NE` solely because `NE` sits outside the high-strain Walker Lane (`geod_shearrate` median `0.0` vs `18.3` in `SW`) and consists of weakly magnetic Paleozoic carbonate horsts (`tmi_hg = 6.4` vs `28.7` in volcanic `SW`) with **strong density-contrast gravity gradients (`grav_slope = 0.129` vs `0.088` in `SW`)**. Feeding raw Walker Lane strain/magnetic magnitudes into a global classifier and applying a single uncalibrated global `37,654`-dot threshold starved `NE` to `11.2%` (`COULOMBLOQO`) and `0.7%` (`BLINDFAULT`).

---

## 2. Five Ranked Untried Geological Hypotheses

None of the five hypotheses below appears in `gems/*.py`, `evidence/lane_registry_index.json`, or any prior `docs/HYPOTHESES_*.md`.

| Rank | Code | Geological Hypothesis | Primary Layers | Expected `HOLDOUT-DTI` Gain | Build Cost | Status This Session |
|---:|---|---|---|---|---|---|
| **1** | **`PROVINCETOE`** | **Tectonic-Province Strain-Invariant Wallace Scarp-Diffusion Basal Toe-Concavity & Carbonate-Horst Isostatic Flexure LOQO** | `Bands 2, 3, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19` + `geodawn_rad_u8.tif` + `gdr_wellspring_in_footprint.csv` | **High (`+0.004` to `+0.020` on `d_vis > 2.0`; lifts `NE` & `<6°` piedmont/basin recovery while cutting `GEMSDOE23` overlap `< 0.70`)** | Low–Med (`~45 min`, 3 frozen arms) | **BUILD & TEST (Rank 1)** |
| 2 | `FLEXISOSTASY` | Broken-Elastic-Plate Flexural Footwall Uplift / Hangingwall Basin Wavelength Deconvolution ($\lambda_f \approx 8\text{–}15\text{ km}$) | `Bands 12, 13, 15` (`det_elev`, `iso_grav_anom`, `depth_to_base_surf`) | Moderate (`+0.002` to `+0.008` on deeply embayed pediment fronts) | Med (`~75 min`, multi-azimuth 2D broken-plate kernels) | Unbuilt backup |
| 3 | `HYDRO-SILICA-CAP` | Epithermal Potassic/Silica Upflow Core (`K/Th`) vs Flank Smectite Clay-Cap (`cond_surf`) Cross-Strike Dipole (`2–4 km` lateral zoning) | `geodawn_rad_u8.tif` (`K, Th`), `Band 17` (`cond_surf`), `gdr_wellspring_in_footprint.csv` | Low–Moderate (high precision on active amagmatic systems, covers `~15%` of total fault length) | Med (`~60 min`) | Unbuilt backup |
| 4 | `CURV-RELAY-RAMP` | En-Echelon Normal-Fault Relay-Ramp Hyperbolic Twist Saddle ($K = \lambda_1\lambda_2 < 0$) & Oblique Gravity Transfer Detector | `Bands 12, 19, 13, 2` | Low–Moderate (targets unmapped breaching faults in overlap zones; narrow spatial support) | Low–Med (`~45 min`) | Unbuilt backup |
| 5 | `EARTH-MRI-AEM-3DEP` | USGS Earth MRI Airborne EM Resistivity Curtain + 3DEP `1 m` LiDAR Micro-Scarp Integration | External USGS Earth MRI AEM + USGS 3DEP `1 m` DEM | Potentially High (`> +0.03` on Holocene micro-scarps), but unreachable inside restricted sandbox egress | Blocked by sandbox egress | Held (external) |

---

## 3. Detailed Specification of All 5 Hypotheses

### Rank 1 (Selected): `PROVINCETOE` — Tectonic-Province Strain-Invariant Wallace Basal Toe-Concavity & Carbonate-Horst Isostatic Flexure LOQO
- **Exact Layers & Verified Official Free Sources:**
  1. `training_features.tif` (DrivenData Competition #306 / USGS INGENIOUS compilation; SHA-256 `a2f431886dde...`): Band 2 (`rtp` — verified true magnetic RTP; Band 6 `tc` is excluded due to `#IR-92-BAND6-TC-MISLABEL` radiometric Total Count mislabeling), Band 3 (`tmi_hg`), Band 5 (`iso_grav_anom_slope`), Band 7 (`geod_shearrate`), Band 8 (`geod_dilaterate`), Band 11 (`iso_grav_anom_vg`), Band 12 (`det_elev`), Band 13 (`iso_grav_anom`), Band 15 (`depth_to_base_surf`), Band 17 (`cond_surf`), Band 18 (`iso_grav_anom_hg`), Band 19 (`det_elev_slope`).
  2. `geodawn_rad_u8.tif` ([USGS Data Release `10.5066/P9X84255` — GeoDAWN Radiometrics](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7); SHA-256 `4ce92c541f49...`): airborne gamma-ray `K`, `Th`, `U`.
  3. `gdr_wellspring_in_footprint.csv` ([DOE Geothermal Data Repository Submission #1391 — INGENIOUS Great Basin Geothermometry](https://gdr.openei.org/submissions/1391); SHA-256 `d5b5b9704fb3...`, with `dist_known_fault_px` dropped immediately on read).
- **Physical Signature & Mathematical Transform (3 Orthogonal Innovations Over `COULOMBLOQO`, `APRONRIDGE`, and `BLINDFAULT`):**
  1. **Wallace Scarp-Diffusion Basal Toe-Concavity & One-Sided Footwall-Apron Asymmetry** (Wallace, 1977 *GSA Bull.*; Hanks et al., 1984 *JGR*; Bull, 2007):
     - A normal fault separates an uplifted footwall block from a subsiding hangingwall alluvial fan/basin. Under diffusive scarp degradation $\partial z / \partial t = \kappa \nabla^2 z$, the fault trace lies at the **basal piedmont toe-concavity** (`1.5°–9°`) and across degraded intrabasin scarps (`0.5°–5°`), *not* mid-way up `>= 12°` alpine cliff faces where `hessian_ridge_strength(log_slope)` peaks.
     - Let $\lambda_{\max}(\nabla^2 G_\sigma * z_{\text{det}})$ be the **most positive** principal eigenvalue of the smoothed elevation Hessian ($\sigma \in \{1.5, 3.5\}\text{ px}$), capturing upward-concave basal breaklines:
       $$\kappa_{\text{toe}}(\sigma) = \max\bigl(0,\; +\lambda_{\max}(\nabla^2 G_\sigma * z_{\text{det}})\bigr)\,\sigma^2.$$
     - Along the unit upslope normal $\hat{n} = \nabla G_3(z_{\text{det}}) / (\|\nabla G_3(z_{\text{det}})\| + \varepsilon)$, sample the mean slope $4\text{ px}$ (`400 m`) upslope ($s_{+4}$) vs $4\text{ px}$ downslope ($s_{-4}$) and define **one-sided basal apron asymmetry**:
       $$A_{\text{toe}} = \frac{\max(0,\; s_{+4} - s_{-4})}{s_{+4} + s_{-4} + 1.0^\circ} \in [0, 1), \qquad B_{\text{wallace}} = \kappa_{\text{toe}}(1.5)\,(0.25 + 0.75\,A_{\text{toe}}).$$
     - Across gentle intrabasin scarps, also compute the **Wallace diffusion dipole** $D_{\text{wallace}} = \max(0, -\Delta_{\sigma=2} z_{+3\hat{n}}) \cdot \max(0, +\Delta_{\sigma=2} z_{-3\hat{n}})^{1/2}$, detecting paired footwall-crest convexity ($+300\text{ m}$ upslope) and hangingwall-toe concavity ($-300\text{ m}$ downslope) along the exact scarp inflection line.
  2. **Within-Quadrant Local Lithologic Contrast & Carbonate-Horst Isostatic Flexure (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE` Solution):**
     - Strictly inside each `valid & (quad == q)` domain (zero cross-quadrant kernel bleed; $\sigma_{\text{loc}} = 4.0\text{ px} = 400\text{ m}$ so $3\sigma_{\text{loc}} = 12\text{ px} = \text{guard\_px}$), normalize magnetic RTP gradient, isostatic gravity slope, basement-depth gradient, and MT conductivity gradient against their local lithologic background:
       $$\widetilde{G}_{\phi}(x) = \frac{|\nabla \phi(x)|}{G_{\sigma_{\text{loc}}}(|\nabla \phi|)(x) + c_\phi}.$$
     - In non-magnetic Paleozoic carbonate terrain (`NE`), where dense dolomite/limestone horsts ($\rho \approx 2.75\text{ g/cm}^3$) fault against low-density Cenozoic basin fill ($\rho \approx 2.15\text{ g/cm}^3$), carbonate-horst bounding faults exhibit sharp $\widetilde{G}_{\text{grav}}$ and $\widetilde{G}_{\text{base}}$ crests without requiring volcanic magnetic susceptibility!
  3. **Dimensionless Strain-Style Partitioning + Label-Blind Quadrant Quantile Calibration:**
     - Replace raw Walker Lane GPS strain magnitudes (`geod_shearrate`, `geod_2ndinv`) with dimensionless kinematic partitioning:
       $$\chi_{\text{dil}} = \frac{\dot{\epsilon}_{\text{dil}}}{|\dot{\epsilon}_{\text{dil}}| + \dot{\gamma}_{\text{shear}} + 1.0}, \qquad \Omega_{\text{norm}} = \cos^2(\theta - 15^\circ), \qquad \Omega_{\text{trans}} = \sin^2\bigl(2(\theta - 15^\circ)\bigr).$$
     - Calibrate each LOQO model's out-of-fold probability $p_q(x)$ on target quadrant $q$ via its **strictly label-blind unlabeled-footprint empirical rank** $u_q(x) \in (0, 1]$ across `valid & (quad == q)`, mapped through a monotone power transform $u_q(x)^\gamma$, guaranteeing footprint-proportional provincial dot allocation without ever touching a single test-quadrant label.
- **Why Missing From USGS/INGENIOUS Catalogue:** Long-recurrence ($10^4\text{–}10^5\text{ yr}$) normal faults in the low-GPS-strain Eastern/Northeastern Nevada Carbonate Province (`NE`, containing `41.6%` of off-catalogue SGMC bedrock faults) and degraded Late Pleistocene piedmont-toe / intrabasin scarps (`slope < 6°`, `52.6%` of true faults) lack crisp Holocene free-faces and instrumental seismicity swarms, causing systematic photogeologic omission.
- **Named Non-Fault Mimic & Engineered Suppression:** **Non-tectonic coalescing alluvial-fan bajada slope-apron breaks, V-shaped incised stream thalwegs, and Pluvial Lake Lahontan (`~1,330 m`) / Bonneville (`~1,580 m`) wave-cut shoreline nickpoints.**
  - *Suppression:* (i) Incised V-canyons have large $\kappa_{\text{toe}}$ but symmetric valley walls ($s_{+4} \approx s_{-4} \implies A_{\text{toe}} \approx 0$), suppressing thalwegs directly in $B_{\text{wallace}}$; (ii) Pluvial shorelines and passive bajada contours are strictly isohypsic ($\text{Var}_{\text{along-strike}}(z) \approx 0$) and lack basement/gravity step concordance, so we include **along-strike elevation progression** $|\hat{t} \cdot \nabla G_3(z)|$ and **signed footwall gravity/basement concordance** (`dip_grav`, `dip_base`) so the LOQO booster rejects surficial shoreline/bajada mimics; (iii) A gentle alpine-cliff taper $W_{\text{cliff}}(s) = 1 / (1 + (s / s_0)^2)$ prevents steep `>= 12°` erosional spur cliffs from hijacking 1D NMS placement.
- **Differentiation From Existing Repo Lanes & External Sparse Rasters:**
  - Unlike `COULOMBLOQO` (`hess_s12(log_slope)` convex cliff ridges + raw regional GPS shear $\to$ `45.2%` dots at `>= 12°`, `11.2%` in `NE`, `0.7398` collision vs `GEMSDOE23`), `PROVINCETOE` localizes on **concave** basal toes ($\lambda_{\max}(\nabla^2 z) > 0 \times A_{\text{toe}}$) + carbonate-horst gravity/basement flexure with strain-invariant provincial calibration.
  - Unlike `APRONRIDGE` and `NEO-OPNS` (unsupervised thin-cover `exp(-D_base/250m)` filters blended 45–60% with `R0`), `PROVINCETOE` copies **0% of `R0`/`H19-5`**, does not penalize deep basins (`D_base > 250 m`), and cross-fits 24 physical channels via 4-fold LOQO.
  - Unlike `BLINDFAULT` (slope-blind 100 m subsurface probability without topographic scarp localization $\to$ `0.0378` DTI, `0.7%` in `NE`), `PROVINCETOE` retains sharp 100 m basal-toe + subsurface 1D ridge localization across all four quadrants.

### Rank 2 (Unbuilt Backup): `FLEXISOSTASY` — Broken-Elastic-Plate Flexural Footwall Uplift / Hangingwall Subsidence Wavelength Deconvolution
- **Layers & Source:** `training_features.tif` Bands 12 (`det_elev`), 13 (`iso_grav_anom`), 15 (`depth_to_base_surf`).
- **Signature:** Convolves elevation and gravity with matched antisymmetric 1D broken-elastic-plate deflection profiles $w(n) = w_0 e^{-|n|/\alpha}\cos(|n|/\alpha)$ ($\alpha \in \{25, 50\}\text{ px} = 2.5\text{–}5\text{ km}$, Buck 1988 *JGR*) to infer the buried master normal-fault trace down-dip of eroded pediment embayments.
- **Why Missing:** Pedimentation in mature ranges (e.g., Granite Springs / Humboldt ranges) retreats the topographic mountain front $1\text{–}3\text{ km}$ into the footwall, leaving the master fault concealed under thin sheetwash alluvium.
- **Named Mimic & Suppression:** Tilted dip-slope cuesta of a Cenozoic ignimbrite mesa; suppressed by hangingwall `depth_to_base_surf` basin thickening.

### Rank 3 (Unbuilt Backup): `HYDRO-SILICA-CAP` — Epithermal Potassic/Silica Core (`K/Th`) vs Flank Smectite Clay-Cap (`cond_surf`) Cross-Strike Dipole
- **Layers & Source:** USGS GeoDAWN `geodawn_rad_u8.tif` (`K, Th`), `Band 17` (`cond_surf`), DOE GDR #1391 `gdr_wellspring_in_footprint.csv`.
- **Signature:** Cross-strike lateral offset (`15–35 px`) between potassic/silicified upflow fracture zones (`high K/Th`, low `cond_surf`) and adjacent conductive smectite alteration caps (`high cond_surf`, Cumming 2009).
- **Why Missing:** Blind hydrothermal upflow zones in basin-margin step-overs often cement Quaternary alluvium (silica sinter/travertine), muting young fault-scarp relief.
- **Named Mimic & Suppression:** Rhyolitic ash-flow tuff outcrop adjacent to a conductive saline playa pan; suppressed by requiring non-zero `iso_grav_anom_slope` across the contact.

### Rank 4 (Unbuilt Backup): `CURV-RELAY-RAMP` — En-Echelon Normal-Fault Relay-Ramp Hyperbolic Twist Saddle ($K = \lambda_1\lambda_2 < 0$)
- **Layers & Source:** `training_features.tif` Bands 12, 19, 13, 2.
- **Signature:** Negative Gaussian curvature saddles ($K = \det(\nabla^2 G_\sigma * z) < 0$, $\sigma = 4\text{ px}$) aligned with oblique gravity/RTP transfer gradients between overlapping normal-fault tips (Peacock & Sanderson, 1991; Faulds & Hinz, 2015).
- **Why Missing:** Small-displacement breaching faults across tilted relay ramps lack continuous range-front scarps yet host the highest structural permeability in Great Basin geothermal fields.
- **Named Mimic & Suppression:** Erosional drainage wind-gaps / mountain saddles; suppressed by requiring cross-saddle Bouguer/isostatic gravity relief.

### Rank 5 (Held — External Data Unreachable Under Sandbox Egress): `EARTH-MRI-AEM-3DEP`
- **Layers & Official Free Sources:** USGS Earth MRI airborne electromagnetic resistivity inversions ([`https://www.usgs.gov/special-topics/earth-mri`](https://www.usgs.gov/special-topics/earth-mri)) and USGS 3DEP `1 m` LiDAR DEMs ([`https://apps.nationalmap.gov/downloader/`](https://apps.nationalmap.gov/downloader/)).
- **Status:** Held because outbound sandbox network access is restricted to `github.com` / `pypi.org` (`registry/session_manifest.json`).

---

## 4. Pre-Registered 3-Experiment Protocol & Fail-Closed Promotion Gate (`Rank 1: PROVINCETOE`)

### 4.1 Frozen Experiment Arms (`Budget = 3`)
1. **Arm 1 (`provincetoe` — Primary Hypothesis Arm):** Full 24-channel `PROVINCETOE` stack (Wallace basal toe-concavity $\kappa_{\text{toe}}$, one-sided apron asymmetry $A_{\text{toe}}$, Wallace scarp-diffusion dipole $D_{\text{wallace}}$, within-quadrant locally normalized RTP/gravity/basement/MT gradients, signed footwall gravity/basement concordance, dimensionless kinematic partitioning $\chi_{\text{dil}}, \Omega_{\text{norm}}, \Omega_{\text{trans}}$, GeoDAWN `K/Th` & `U/Th` gradients, catalogue-blind GDR thermal plume) cross-fitted via 4-quadrant LOQO (`guard_px = 12`, `neg_buffer_px = 5`), calibrated per quadrant via **strictly label-blind footprint empirical rank** ($u_q^{2.0}$), and localized on 1D NMS crests of $S_{\text{toe}}$ with moderate alpine-cliff attenuation ($s_0 = 15^\circ$, `sub_weight = 0.85`), emitting `37,654` unit-mass dots at $d_{\text{cat}} > 2.0\text{ px}$ (`d_visible > 2.0\text{ px}$ in strict draw-blind holdout).
2. **Arm 2 (`globalraw` — Single-Axis Province-Shift Ablation):** Identical Wallace basal toe-concavity and geophysical features, **except** replacing dimensionless strain-style partitioning with raw regional `geod_shearrate` and `geod_2ndinv` magnitudes and omitting per-quadrant label-blind footprint calibration (global uncalibrated threshold). Directly measures the causal `HOLDOUT-DTI` impact of resolving `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`.
3. **Arm 3 (`piedbasin` — Stronger Alpine-Cliff Suppression & Equal Subsurface Flexure Arm):** Uses the `provincetoe` LOQO probability surface with stronger alpine-cliff suppression ($s_0 = 10.5^\circ$) and equal subsurface gravity/basement/RTP flexure localization (`sub_weight = 1.00`), testing whether shifting an even larger fraction of the `37,654`-dot budget onto `< 10°` piedmont toes and intrabasin gravity/basement steps improves precision and further lowers external sparse-registry overlap.

### 4.2 Mandatory Fail-Closed Gates (`Protocol Rules 1–6`)
1. **Leakage Canary Gate (Rule 4):** Every single feature in `PROVINCETOE` is tested solo against withheld fault pixels on `gems57-pooled-hide-v2` before evaluating composite surfaces. Any single feature with symmetric AUC `> 0.90` halts the run as leakage.
2. **Dual-Instrument `HOLDOUT-DTI` Gate (Rules 2–3):** Evaluate all three arms via `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `22,663` withheld positive pixels across seeds `20` & `30`, 158 physical `20 km` bootstrap clusters, `1,000` draws, seed `520810`) on:
   - **Primary strict draw-blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`** (LOQO refit separately for each draw using only `visible = cat & ~collar_3px`, never touching `hidden_all`), compared head-to-head against `H19-5` (`0.096757`) and repository holdout-best `COULOMBLOQO standalone` (`0.113316`), plus per-quadrant breakdown (`NW`, `NE`, `SW`, `SE`).
   - **Static deployment `d_cat > 2.0` `HOLDOUT-DTI`** (`R0` `0.004006`, `COULOMBDM` `0.007816`, `HYDROCONDUIT` `0.008549`, `COULOMBLOQO standalone` `0.009220`) and off-catalogue `USGS SGMC` (`d_cat > 5.0`) `PROXY` DTI.
3. **Local & 102-Repo Public Registry Uniqueness Gate (Rule 1):**
   - Check pre-placement continuous surface AND final `37,654`-dot rasters against all local cross-lane `GEMSDOE92` rasters and all `1,354` external valid public rasters across `101` external `buffedlizard55-lab` `*GEMSDOE*` repos.
   - Report **both** `vendor/gems57/uniqueness.dual_reading_decision` (operative matched-budget / sparse-witness rule: must satisfy `worst_matched_budget_forward_overlap <= 0.70` and `|Spearman rho| <= 0.90` — which `COULOMBLOQO` failed at `0.7398`) **and** the literal positive-support reading (`17GEMSDOE E-proba-multiscale`, `5,167,373` positive footprint cells $\to$ `1.000`). Under the repository's fail-closed site contract (`scripts/check_site.py`), any raster where `unique_under_literal_rule == False` remains `submission_eligible: false` (`⛔ DO NOT SUBMIT` to DrivenData portal until human selector resolution).
4. **Automated Format Gate (`submission_writer.py` + `gems/gates.py` + `gems57.validate`):** Emit `*-zeros.tif` strictly via `vendor/gems57/submission_writer.py` (`EPSG:32611`, `3730 x 3292`, single-band `float32`, finite `[0.0, 1.0]`, zero NaN anywhere, `0.0` outside footprint, `0` catalogue mass, `d_cat > 2.0 px`).
