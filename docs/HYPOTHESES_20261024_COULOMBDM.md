# Pre-Registered Geological Hypotheses — `COULOMBDM` Session (`2026-10-24`)

> **Protocol Compliance (Rules 1–6):** Written and locked **before** building or scoring any candidate GeoTIFF in this session. Names 5 untried geological hypotheses in `GEMSDOE92`, specifying for each: (1) exact input layer(s), (2) physical signature and mathematical transform, (3) why it catches faults **missing** from the USGS/INGENIOUS `existing_faults.tif` catalogue rather than faults already in it, (4) named non-fault geological mimics, (5) how it differs from all 9 prior `gems/*.py` modules in `GEMSDOE92`, and (6) external data obtainability verification from official free public sources. Ranked by expected `DTI` improvement and implementation cost.

---

## Forensic Diagnosis Preceding Hypothesis Design

Line-by-line review of the repository at commit `c16e8b7` (post-`APRONRIDGE` PR #49 and post-`HYDROCONDUIT` PR #51) identified four concrete scientific and algebraic gaps explaining why every prior lane sacrificed at least one local validation instrument (`Static HOLDOUT-DTI` vs `Rule-2 Fold-Visible d_visible > 2.0 HOLDOUT-DTI` vs `Off-Catalogue USGS SGMC Bedrock PROXY`):

1. **Official Metric Sign Clarification (`drivendataorg/gems-prize-reference-solution`):** Direct inspection of Prof. John Lipor's official reference notebook (`unet-mc-cv-reference-solution.ipynb`, Cells 0 & 16) and `vendor/gems57/metric.py` confirms **`alpha = 0.2` weights false positives (`0.2 * FP_w`) and `beta = 0.8` weights false negatives (`0.8 * FN_w`)** — a 4:1 recall-favoring asymmetry (fixing an inverted prose description in `APRONRIDGE`'s writeup). Under the exact binary-dot marginal optimality condition $dT > \alpha \cdot \text{DTI} \cdot (dT + 1 - k)$, `2.8 px` (`280 m`) spacing removes redundant along-strike overlap (`dT ≈ 0`), while discovering unmapped fault families that `H19-5` missed simultaneously raises numerator `TP_w` and cuts the `4×`-weighted `0.8 * FN_w` denominator.
2. **Uniaxial Azimuth Bias vs Full 2D Mohr–Coulomb Transtensional Mechanics:** `HYDROCONDUIT` used a single uniaxial $\cos^2(\theta - 15^\circ)$ strike weight that penalized legitimate $\text{N}35^\circ\text{W}$ (`145°`) Walker Lane dextral-normal faults (`cos^2(130°) = 0.41`) and $\text{N}55^\circ\text{E}$ (`55°`) Humboldt Structural Zone sinistral-normal faults (`cos^2(40°) = 0.59`), and never coupled ridge orientation $\theta(x)$ to whether the local GPS/InSAR strain field (`Bands 4, 7, 8`) is undergoing volumetric dilation (`Band 8 > 0`) vs conjugate shear (`Band 7`).
3. **2D Blob Packing in `HYDROCONDUIT` vs Mislabelled `Band 6 tc` & Scale Suppression in `APRONRIDGE`:**
   - `HYDROCONDUIT` (`0.008549` static `HOLDOUT-DTI`) emitted its 16,944 off-skeleton dots directly on a smooth 2D continuous surface without 1D crest extraction, creating 2D hexagonal clusters that depressed `Rule-2 fold-visible d_visible > 2.0 HOLDOUT-DTI` (`0.0852` vs `0.0968` `H19-5`) and crushed `SGMC` bedrock fault recovery (`0.0741` vs `0.0961` `R0`).
   - `APRONRIDGE` (`0.008354` static, `0.0868` `d_vis > 2.0`, `0.0801` `SGMC`) extracted 4-axis 1D crests, but (i) treated `Band 6 tc` as magnetic curvature when `Band 6` is actually **airborne gamma-ray Radiometric Total Count** (`r = 0.99714` with `GeoDAWN TC`, `#IR-92-BAND6-TC-MISLABEL`), (ii) multiplied three `[0,1]` factors in `R_rtp` against two in `R_scarp` so un-normalized `BREAKLINE` won `89.5%` of crests, and (iii) multiplied every pixel by a single piedmont cover Gaussian (`cover_center = 180 m`) that suppressed exposed range-front/relay bedrock faults (`depth_to_base < 20 m`).

---

## Ranked Candidate Geological Hypotheses (5 Untried Concepts)

| Rank | ID | Layers Used | Core Physical Transform | Expected DTI Gain | Impl. Cost | Sandbox Viable? |
|---:|---|---|---|---|---|---|
| **1** | **`COULOMBDM`** *(Selected Lane)* | `Bands 2, 4, 5, 7, 8, 11, 12, 15, 17, 19` + `GeoDAWN K,Th,U` + `GDR #1391` | Two-regime oriented 2D Mohr–Coulomb dilation/shear criticality + multi-altitude FFT upward-continued RTP tilt/demag + gravity tilt + MT clay-cap lateral edge along Canny-style cross-strike 1D NMS crests | **High** (lifts piedmont, concealed basin, AND corroborated bedrock faults simultaneously) | Medium (~250 LOC CPU) | **Yes** (`12/12` SHA-256 inputs verified) |
| **2** | **`MTCLAY-CAPEDGE`** | `Band 17`, `GeoDAWN K,Th,U`, `Band 2`, `GDR #1391` | Lateral gradient $\|\nabla\text{cond\_surf}\|$ of smectite clay-cap margins $\times$ `U/(Th+1)` redox roll-front $\times$ blind geothermometer halo | Moderate-High (folded into `COULOMBDM` hydrothermal conduit term; standalone MT grid too coarse alone) | Low | **Yes** (folded into Rank 1 subsurface channel) |
| **3** | **`UPCONT-EULER`** | `Bands 2, 11, 13, 15, 18` | 2D Fourier upward-continued RTP (`100/300/600 m`) + structural-index depth ratio matched to `Band 15` basement interface | Moderate-High (upward-continued RTP tilt persistence folded into `COULOMBDM` Channel 2; standalone misses zero-susceptibility alluvial scarps) | Medium | **Yes** (upward continuation folded into Rank 1) |
| **4** | **`SEISMIC-ANISOTROPY`** | `Bands 10, 16, 4, 7, 19` | $-\nabla^2 \log(\text{deq\_n100a15}+50) \times \text{pct}(\text{ieq\_n100a15}) \times \text{pct}(\text{geod\_shearrate})$ on 1D scarps | Low-Moderate (`n=100 km` seismicity smoothing radius is ~300× wider than `300 m` DTI kernel) | Low | **Yes** (screened in `screen_coulombdm_surface.py`) |
| **5** | **`LIDAR-1M-LAHONTAN`** | External USGS 3DEP 1 m LiDAR DEMs (`1m_DEM_links.csv`) + NAVD88 AMSL elevation + `Bands 12, 19` | Sub-meter `5–25 m` openness scarp doublet + orthometric `1195–1345 m` AMSL contour-parallel Lake Lahontan shoreline rejection | Very High (sub-pixel Holocene scarps + exact shoreline rejection) | High (multi-GB tile streaming) | **No — Blocked by sandbox network allowlist** (deferred; official source documented below) |

---

### Detailed Specification of All 5 Hypotheses

#### 1. `COULOMBDM` — Two-Regime Oriented 2D Mohr–Coulomb Slip-Dilation & Multi-Altitude Upward-Continued RTP/Clay-Cap 1D Ridge Synthesis *(Rank 1 — Implemented)*

- **Specific Layers Involved:**
  - `training_features.tif`: Band 2 (`rtp`), Band 4 (`geod_2ndinv`), Band 5 (`iso_grav_anom_slope`), Band 7 (`geod_shearrate`), Band 8 (`geod_dilaterate`), Band 11 (`iso_grav_anom_vg`), Band 12 (`det_elev`), Band 15 (`depth_to_base_surf`), Band 17 (`cond_surf`), Band 19 (`det_elev_slope`).
  - `external/geodawn_rad_u8.tif`: Band 1 (`K`), Band 2 (`Th`), Band 3 (`U`) ([USGS GeoDAWN DOI:10.5066/P93LGLVQ](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)).
  - `external/gdr_wellspring_in_footprint.csv`: `temp_c`, `thermalclass` (whitespace-stripped), `geothermquartz_c`, `geothermchalc_c`, `geothermcat_c` ([DOE GDR #1391 INGENIOUS](https://gdr.openei.org/submissions/1391)).
- **Physical Signature & Mathematical Transform:**
  1. **Oriented 2D Mohr–Coulomb Transtensional Criticality ($C_{\text{coulomb}}(x, \theta)$) (Morris, Ferrill & Henderson, 1996; Faulds & Hinz, 2015):**
     Under NW Great Basin regional extension ($\sigma_{H,\max} \approx \text{N}15^\circ\text{E}$, $\sigma_{h,\min} \approx \text{N}105^\circ\text{E}$), a ridge element with local compass strike $\theta(x) \in [0^\circ, 180^\circ)$ experiences:
     - *Tensile / Dip-Slip Normal Opening* proportional to positive volumetric crustal dilatation (`max(Band 8, 0)`): $D_{\text{open}}(x,\theta) = \text{pct}(\max(B_8, 0)) \cdot \cos^2(\theta - 18^\circ)$.
     - *Conjugate Walker Lane ($\text{N}30^\circ\text{W} = 150^\circ$) & Humboldt ($\text{N}60^\circ\text{E} = 60^\circ$) Transtensional Shear* at $\pm 45^\circ$ to $\sigma_{H,\max}$ proportional to GPS/InSAR shear strain rate: $D_{\text{shear}}(x,\theta) = \text{pct}(\sqrt{\max(B_7,0)\cdot\max(B_4,0)}) \cdot \sin^2(2(\theta - 15^\circ))$.
     - Crucially, **both** $\cos^2(\theta - 18^\circ)$ and $\sin^2(2(\theta - 15^\circ))$ vanish near $\theta \approx 105^\circ$ ($\text{WNW–ESE}$), simultaneously suppressing compressional fault clamping and range-perpendicular erosional canyons / alluvial-fan washes while preserving all three productive geothermal fault orientations (NNE Basin-and-Range normal, NNW Walker Lane dextral-normal, and ENE Humboldt sinistral-normal).
  2. **Multi-Altitude FFT Upward-Continued RTP Tilt-Contact & Demagnetization + Gravity Tilt + MT Clay-Cap Lateral Edge ($R_{\text{sub}}$):**
     - Symmetric-padded 2D Fourier upward continuation $\hat{U}(k; z) = \hat{U}(k; 0)\,e^{-|k|z}$ of `Band 2 (rtp)` across $z \in \{100, 300, 600\text{ m}\}$ yields depth-persistent Miller–Singh tilt-contact crests $\left(\prod_{z} \cos\text{Tilt}_{\text{RTP}}(z)\right)^{1/3} \cdot \text{coh}(\text{RTP}_{300\text{ m}})$, rejecting surficial volcanic float while centering directly over buried vertical contacts without raw-TMI dipolar inclination shift.
     - Fused with positive-Laplacian RTP magnetite-destruction troughs ($\nabla_{\text{H}}^2 \text{RTP}_{100\text{ m}} > 0$), Miller–Singh isostatic gravity contact tilt $B_5 / \sqrt{B_5^2 + (0.04\,B_{11})^2 + \epsilon}$, smectite clay-cap lateral boundary gradient $\|\nabla B_{17}\|$, lateral GeoDAWN radiometric contact gradients $\|\nabla(\text{K}/(\text{Th}+1))\| + \|\nabla(\text{U}/(\text{Th}+1))\|$ (pre-build screen refinement: raw `K/Th` and `U/Th` levels anti-correlate slightly with holdout faults at `AUC = 0.44–0.47` because bare Tertiary felsic mountain cores carry high K and U, whereas hydrothermal/juxtaposition fault contacts express as steep lateral radiometric gradients), and `GDR #1391` blind (`>= 80 °C`) geothermometer plumes.
  3. **Two-Regime Matched-Scale Union + Continuous-Angle Canny Cross-Strike 1D NMS (`oriented_nms_1d`):**
     - *Regime 1 (Piedmont Hinge Monoclinal Scarp, $R_{\text{pied}}$):* Matched-scale relative log-slope break $\|\nabla\log(\max(B_{19},0)+1^\circ)\| \cdot \mu_{\text{step}}(B_{12}) \cdot \text{coh}(B_{12})$ gated by thin-to-intermediate piedmont accommodation envelope and $C_{\text{coulomb}}(x, \theta_{\text{elev}})$.
     - *Regime 2 (Concealed Basin/Piedmont Subsurface Conduit, $R_{\text{sub}}$):* Scale-calibrated (`0.72 * sub_raw`) multi-altitude RTP + gravity tilt + MT clay-cap gradient + radiometric contact gradient + GDR conduit gated by sedimentary cover (`15–1,200 m`) and $C_{\text{coulomb}}(x, \theta_{\text{rtp}})$.
     - *Regime 3 (Geophysically Corroborated Bedrock Relay/Horst, $R_{\text{bed}}$):* Scale-calibrated (`0.64 * scarp_raw * range_gate`) monotonic topographic steps above `p33` elevation **strictly multiplied by** subsurface RTP/gravity contact + $C_{\text{coulomb}}$ criticality (finalized in `scripts/screen_coulombdm_surface.py` before `0 / 3` experiment builds ran, balancing `37,654` 1D crests at `53.7%` piedmont / `22.9%` subsurface / `23.4%` bedrock), recovering unmapped range-block/relay faults (`SGMC`) while rejecting passive erosional cliffs.
     - Extracted along strict bilinear cross-strike Canny 1D NMS centrelines $S(x) \ge S(x \pm \mathbf{n}(\theta^*(x)))$ (`1-px` ridges, eliminating 2D blob clustering).
- **Why Missing from USGS/INGENIOUS Catalogue:** Catches (a) degraded `1–5 m` piedmont alluvial scarps lacking potential-field worms, (b) concealed intrabasin/piedmont faults beneath `50–800 m` of fan wash where surface scarps were erased and raw TMI was laterally shifted `300–800 m` off-fault by geomagnetic inclination, (c) conjugate NW Walker Lane & ENE Humboldt shear stepovers previously suppressed by uniaxial N15°E filters, and (d) clay-capped blind geothermal conduits (`>= 80 °C` chemical geothermometers, cold surface waters).
- **Named Non-Fault Mimics:** Pluvial Lake Lahontan recessional strandlines parallel to NNE basin margins, buried Miocene basaltic dike margins / paleochannels with magnetic detritus, saline playa-margin MT conductivity gradients, and linear lithologic contacts in range fronts.
- **How It Differs from All Prior Repo Lanes:** First lane in `GEMSDOE92` to implement (i) true 2D Mohr–Coulomb dilation+conjugate-shear orientation projection (`Bands 4, 7, 8`), (ii) multi-altitude FFT upward continuation of `Band 2 RTP`, (iii) Miller–Singh gravity tilt from `Bands 5 & 11`, (iv) lateral MT clay-cap gradient $\|\nabla\text{Band 17}\|$ + `U/(Th+1)` redox alteration, (v) corroborated bedrock-vs-cover two-regime synthesis, and (vi) continuous-angle bilinear Canny cross-strike 1D NMS.

#### 2. `MTCLAY-CAPEDGE` — Magnetotelluric Smectite Clay-Cap Lateral Edge & `U/Th` Redox Conduit *(Rank 2)*
- **Layers:** `Band 17 (cond_surf)`, `GeoDAWN Bands 1–3 (K, Th, U)`, `Band 2 (rtp)`, `GDR #1391`.
- **Signature:** Steep lateral electrical conductivity gradient $\|\nabla B_{17}\|$ at resistive-footwall / conductive-smectite-cap contacts multiplied by mobile-uranium roll-front enrichment `U/(Th+1)` and blind `>= 80 °C` geothermometry.
- **Why Missing:** Blind clay-capped geothermal upflow zones (~75% of Great Basin resources) lack surface scarps and hot springs.
- **Difference:** Prior `HYDROCONDUIT` used raw `Band 17` amplitude rather than clay-cap boundary gradient $\|\nabla B_{17}\|$ and ignored `Band 3 (U)`. Incorporated into `COULOMBDM` subsurface conduit rather than emitted standalone because MT grid spacing (`>1 km`) is coarser than the `300 m` DTI kernel.

#### 3. `UPCONT-EULER` — Multi-Altitude FFT Potential-Field Upward Continuation & Basement-Interface Depth Bridge *(Rank 3)*
- **Layers:** `Bands 2 (rtp), 11, 13, 15, 18`.
- **Signature:** Fourier upward continuation $e^{-|k|z}$ ($z = 100, 300, 600\text{ m}$) + local potential-field homogeneity depth ratio matched against `Band 15 depth_to_base_surf`.
- **Why Missing:** Buried intrabasin horsts have zero `Band 19` surface slope expression and dipolar inclination shift in raw `TMI`.
- **Difference:** `ANASIG` used raw TMI (`Bands 3, 9`) without RTP or upward continuation; `APRONRIDGE` misread `Band 6 tc` (Radiometric Total Count) as magnetic tilt. Multi-altitude RTP upward continuation is folded into `COULOMBDM` Channel 2.

#### 4. `SEISMIC-ANISOTROPY` — Azimuthal Microseismicity Corridor × Geodetic Shear Localization *(Rank 4)*
- **Layers:** `Band 10 (deq_n100a15)`, `Band 16 (ieq_n100a15)`, `Band 4`, `Band 7`, `Band 19`.
- **Signature:** $-\nabla^2\log(B_{10}+50) \cdot \text{pct}(B_{16}) \cdot \text{pct}(B_7)$ gated on 1D scarps.
- **Why Missing:** Nascent Walker Lane microseismic relay zones slip before accumulating tall Quaternary scarps.
- **Difference:** First test of `Bands 10 & 16` in `GEMSDOE92`; ranked #4 (screen-only) because `n=100 km` earthquake kernel smoothing cannot localize faults to `300 m` on its own.

#### 5. `LIDAR-1M-LAHONTAN` — 1 m USGS 3DEP Sub-Meter Scarp Doublet + Orthometric Lake Lahontan Shoreline Rejection *(Rank 5 — External Data Blocked in Sandbox)*
- **Layers & Official Free Public Sources:** USGS 3D Elevation Program (3DEP) 1 m LiDAR DEMs ([https://www.usgs.gov/3d-elevation-program](https://www.usgs.gov/3d-elevation-program), [USGS 3DEP S3 StagedProducts](https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/1m/)) + DrivenData `1m_DEM_links.csv` ([https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)).
- **Obtainability Verification:** **NOT OBTAINABLE in this sandbox** (outbound network policy allows only `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`; orthometric AMSL elevation is absent from pinned `.cache/gems_inputs/`). Flagged non-viable in-sandbox per prompt rule and documented for unrestricted execution.

---

## Pre-Registered 3-Experiment Budget & Promotion Gate (`Protocol Rules 1–6`)

Hard session cap: **3 experiments** (`S = 37,654` unit-mass dots, `0.0` outside footprint, `nodata=None`, `d_cat > 2.0 px`, `0` catalogue mass):

1. **`coulomb1d` (Experiment 1 — Pure Standalone Physics 1D NMS Crests, `0% H19-5`):**
   `37,654` unit dots spaced at `min_dist_px = 2.8` strictly along `oriented_nms_1d` crests of `COULOMBDM` (`0` `H19-5` or `R0` pixels). Tests pure multi-physics + 2D Mohr–Coulomb + Canny 1D NMS against `APRONRIDGE free1d` (`0.008354` static, `0.086787` `d_vis > 2.0`, `0.080098` `SGMC`).
2. **`s35coulomb65` (Experiment 2 — `35%` Submodular Coulomb `H19-5` + `65%` Off-Skeleton 1D `COULOMBDM` Crests):**
   `13,179` (`35%`) `H19-5` dots selected via exact marginal expected-DTI greedy (`select_exact_marginal_dti_add`) weighted by `COULOMBDM` habitat + `24,475` (`65%`) spaced `2.8 px` dots strictly `> 3.0 px` off `H19-5` along `oriented_nms_1d` `COULOMBDM` crests (mathematically bounding 3-px forward overlap against `H19-5` and `R0` to `<= 35.0% << 70%`).
3. **`s45coulomb55` (Experiment 3 — `45%` Submodular Coulomb `H19-5` + `55%` Off-Skeleton 1D `COULOMBDM` Crests):**
   `16,944` (`45%`) `H19-5` dots via exact marginal expected-DTI greedy + `20,710` (`55%`) spaced `2.8 px` dots strictly `> 3.0 px` off `H19-5` along `oriented_nms_1d` `COULOMBDM` crests (mathematically bounding 3-px overlap against `H19-5` and `R0` to `<= 45.0% << 70%`).

**Strict Pre-Registered Gates:**
- **Leakage Canary (Rule 4):** Every raw and derived feature must satisfy symmetric ROC `AUC <= 0.90` on buffered holdout folds before any result is trusted.
- **Uniqueness (Rule 1):** Pre-placement surface AND final dots must satisfy `|Spearman rho| <= 0.90` and `<= 70%` 3-px forward overlap against all local registry rasters; live/cached 102-repo public registry scan must verify `0` sparse (`<= 150,000` positive px) duplicates (`<= 0.70`) AND record the binding literal dense-surface status (`17GEMSDOE E-proba-multiscale`, `100%` footprint positive) without silent waiver (`verdict: "negative"`, `submission_eligible: false` until human operator policy override).
