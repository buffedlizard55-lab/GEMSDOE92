# Pre-Registered Geological & Geothermal-Vent Hypotheses — Session `2026-10-25` (`VENTSCARP` Lane)

**Pre-registered (UTC):** `2026-10-25` (frozen **prior to** accessing `labels.tif`, running single-feature leakage canaries, or executing any `evaluate_holdout.py` fold)  
**Repository / Branch:** `buffedlizard55-lab/GEMSDOE92` (`arena/effd5a31-gemsdoe92`)  
**Single Method Lane Selected (Parallel-Run Protocol Rule 1):** `VENTSCARP` — *USGS 3DEP 10 m Sub-Pixel Piedmont Scarp Curvature × Tufa-Filtered Paleo/Blind Hydrothermal Vent Valve Out-of-Quadrant (`LOQO`) Discovery*  
**Experiment Cap (Rule 6):** Strictly `<= 3` experiments (`Arm 1: ventscarp`, `Arm 2: scarp10m_novent`, `Arm 3: ventscarp_soft`) and `<= 2` hours (`0` live weekly DrivenData slots consumed).

---

## 1. Scientific Motivation & Previous-Session Next-Steps Synthesis

Forensic audit of `GEMSDOE92`'s 27 prior lanes (`docs/NEXT_STEPS.md`, `docs/ANALYSIS_20261025_PROVINCETOE.md`) established three physical bottlenecks limiting blind-fault discovery on the `5,167,373`-pixel GeoDAWN footprint (`EPSG:32611`, `100 m` grid):

1. **The `< 6°` Sub-Pixel Piedmont Scarp Blind Spot (`docs/NEXT_STEPS.md` Item #3):**  
   Across the competition footprint, **`52.6%` of mapped fault pixels sit on low slopes `< 6°` (`25.7%` in `[0°, 2.5°)` and `26.9%` in `[2.5°, 6°)`), whereas only `22.8%` sit on steep cliffs `>= 12°`**. On the competition's smoothed `100 m` DEM (`Bands 12/19`), a `1.5–3.5 m` Holocene piedmont or intrabasinal fault scarp (`10–25 m` wide at `10°–22°` true face angle) averages down to `< 1.5°` across a `100 m × 100 m` cell — indistinguishable from alluvial fan sheetwash noise. Consequently, `100 m`-only models (`COULOMBLOQO`, `EULERFUSE`, `GEMSDOE23`, `62GEMSDOE`) over-concentrated `35%–45%` of their dots onto bare `>= 12°` range-front cliffs, both forfeiting the `52.6%` low-relief fault population and colliding `> 0.70` with external over-budget cliff rasters (`GEMSDOE23` `100,000` dots; `62GEMSDOE` `125,890` dots).
2. **Untapped Blind & Paleo-Geothermal Vent Physics (Core Competition Domain):**  
   Over `75%` of Great Basin geothermal systems are *blind* (lacking boiling surface springs because modern water tables sit tens of meters beneath intermontane basin fill; Coolbaugh et al., 2006; Faulds & Hinz, 2015). However, these hidden hydrothermal upflow faults leave two diagnostic field signatures compiled by the DOE INGENIOUS project (`https://gdr.openei.org/submissions/1391`) that **no prior `GEMSDOE92` lane has ever used**:
   - **Relict Pleistocene/Holocene hydrothermal vent precipitates** (`Paleo_geothermal_final.csv`: siliceous opal-A/chalcedonic `Sinter`, `Silica-cemented sand` `Qss`, `Explosion craters`, `Silicified fault breccia`, `Sulfur`/`Alteration`, and non-lacustrine `Travertine`) deposited along dilatant step-overs and fault terminations during higher pluvial water tables; and
   - **Shallow 2-meter conductive temperature probe anomalies** (`2m_temperature_probe_INGENIOUS_regional_data.zip`: background-normalized `2mDAB` up to `+54.7°C` across `34` Great Basin prospect grids inside the footprint) measuring conductive heat leakage directly above blind upflow conduits.
3. **Province Covariate Shift (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE`, `docs/NEXT_STEPS.md` Item #2) & Soft-Value Tversky Allocation (`Item #4`):**  
   Eastern Nevada's `NE` Carbonate Horst-Graben Terrane hosts `41.6%` of off-catalogue `USGS SGMC` bedrock faults despite near-zero GPS shear strain (`Band 7 median = 0.00`) and weak carbonate magnetization (`|\nabla T| = 6.4`), requiring strictly masked within-quadrant standardization + label-blind quadrant rank calibration. Meanwhile, `docs/NEXT_STEPS.md` Item #4 calls for testing continuous `p_i in (0, 1]` Tversky confidence calibration on Poisson-spaced peaks against binary `{0, 1}` selection on an identical out-of-quadrant surface.

---

## 2. Pre-ImplementationObtainability & Zero-Leakage Provenance Verification

Before committing to any hypothesis, all five candidate external datasets were verified obtainable inside the GitHub-only sandbox from pinned commit `02563d07fb85d2f4d35887503d380d34d4017197` of `buffedlizard55-lab/60GEMSDOE` (same upstream provenance repository already referenced by `registry/session_manifest.json`), with official US government public-domain / CC-BY-4.0 licenses, SHA-256 checksums, footprint coverage measured using **only** `sample_submission.tif` (zero access to `labels.tif`), and confirmed zero fault-catalogue inputs:

| Dataset File | Official Upstream Source & License | Bytes | SHA-256 Digest | Footprint Coverage (`5,167,373` px) | Catalogue-Free Check |
|---|---|---:|---|---|---|
| `topo_10m_derived_100m_u8.tif` | [USGS 3DEP 1/3 arc-sec (~10 m) Seamless DEM](https://www.usgs.gov/3d-elevation-program) (`prd-tnm.s3.amazonaws.com/.../Elevation/13/TIFF/current/`, US Public Domain, 17 U.S.C. § 105) | `32,523,329` | `a6398d9950965dec6aae6ccecdaa6ced48645d133eab222cbdd11def9bdabfa4` | **`5,167,373 / 5,167,373` (`100.00%`)** across 9 sub-pixel `10 m` bands | PASS — pure 3DEP DEM aggregation |
| `dem10_chi_100m_i16.tif` | [USGS 3DEP 1/3 arc-sec (~10 m) Seamless DEM](https://www.usgs.gov/3d-elevation-program) (18 SHA-256-logged `USGS_13_n*w*` tiles, US Public Domain) | `12,777,098` | `8897ba9c30ef1cd7ad5f23c16c6dfd7bb070e7e757f36fd9486eb45edfd973a5` | `786,299 / 5,167,373` (`15.22%` fluvial channel network across 100% tile coverage) | PASS — pure D8 channel $\chi$/$k_{sn}$ |
| `paleo_geothermal_regional.zip` | [DOE GDR #1391 — Great Basin INGENIOUS Project](https://gdr.openei.org/submissions/1391) (`Paleo_geothermal_final.csv`, Faulds et al., UNR/GBCGE, CC BY 4.0) | `84,008` | `faffcf697f32dbbf6cbb317cd1effb3e305538ce38eb239d72d0c6fa071e91ca` | `281` sites in footprint (`195` hydrothermal vents + `86` `Tufa` mimics) | PASS — coordinates + lithologic deposit type only |
| `2m_temperature_probe_INGENIOUS_regional_data.zip` | [DOE GDR #1391 — Great Basin INGENIOUS Project](https://gdr.openei.org/submissions/1391) (`2m_temperature_probe_n83geo`, GPO / UNR GBCGE / NBMG, CC BY 4.0) | `1,080,530` | `1301f70d230058e616ea5d34d1c7a32fabf7d49198172f376c59c89bd652eca3` | `2,782` probe stations across `34` Great Basin survey areas (`2mDAB` up to `+54.7°C`) | PASS — shallow `2 m` temperatures only |
| `geodawn_extensions_u8.tif` | [USGS ScienceBase GeoDAWN Compilation](https://doi.org/10.5066/P9X6556H) (`doi:10.5066/P9X6556H`, US Public Domain) | `27,132,925` | `a35a9c6d2a14786f4dab85481ee59769213072f5dab5b2535ea82ae4d9bb7d9b` | **`5,166,085 / 5,167,373` (`99.98%`)** (`Th/K`, `U/K`, `U/Th`, `TMI_up150`) | PASS — airborne gamma-ray & aeromagnetics |

*(Governance exclusion: `gdr_volcanic_vents_in_footprint.csv` contains a pre-computed `dist_known_fault_px` column and is **strictly excluded** from all feature pipelines and logged in `IRREGULARITIES.md` as `#IR-92-VOLCANIC-CSV-DIST-KNOWN-FAULT`.)*

---

## 3. Four Untried Candidate Geological Hypotheses (Ranked by Expected DTI Gain & Cost)

### Hypothesis H1 (Rank #1 — SELECTED LANE: `VENTSCARP`)
**Seamless 10 m Sub-Pixel Piedmont Scarp Localization × Tufa-Filtered Paleo/Blind Hydrothermal Vent Valve (`VENTSCARP`)**

- **Input Layers Operated On:**
  1. `topo_10m_derived_100m_u8.tif` Bands 1–8 (`slope_p90`, `slope_max`, `steep_frac`, `slope_std`, `relief_local`, `curv_prof_absmax`, `aspect_coherence`, `hs_lineament`) + `dem10_chi_100m_i16.tif` Bands 1, 3 (`step_max_x1000`, `ksn_max_m0.9`);
  2. `Paleo_geothermal_final.csv` (`Deposit_type != 'Tufa'`), `2m_temperature_probe_n83geo` (`F2mDAB`), and `gdr_wellspring_in_footprint.csv` (`temp_c >= 30°C`);
  3. `geodawn_extensions_u8.tif` (`Th/K`, `U/Th`, `TMI_up150`) + `training_features.tif` (`Bands 2, 3, 4, 5, 7, 8, 12, 13, 15, 17, 18, 19`) + strictly fold-visible fault mask (`visible_faults` on holdout; `existing_faults.tif` at deployment).
- **Physical Signature & Mathematical Transform:**
  - *Sub-pixel scarp excess & break sharpness:* On a uniform `18°` mountain slope, `10 m` maximum slope $S_{\max,10\text{m}}$ and `100 m` slope $\theta_{100\text{m}} = \arctan(\text{Band 19})$ are nearly equal, whereas a discrete `10–25 m` Holocene piedmont/intrabasinal fault scarp cutting a `< 5°` alluvial fan produces a sharp positive **sub-pixel scarp localization ratio** $\Delta S_{10/100} = \log(1 + S_{\max,10\text{m}}) - \log(1 + \theta_{100\text{m}})$, elevated within-cell slope dispersion $S_{\text{std},10\text{m}}$, high `10 m` Wallace crest/toe profile curvature $\kappa_{\text{prof},10\text{m}}$ (`curv_prof_absmax`), and coherent linear strike $C_{\text{asp},10\text{m}} \cdot L_{\text{hs},10\text{m}}$.
  - *Tufa-filtered anisotropic hydrothermal fault-valve field:* Excludes all `86` Pleistocene pluvial Lake Lahontan shoreline `Tufa` mounds (`Deposit_type` containing `tufa` without `travertine`), retains the `195` true hydrothermal paleo-vents (`Silica-cemented sand` `Qss`, `Sinter` `Qssi` [$T_{\text{res}} \ge 175^\circ\text{C}$], `Explosion craters`, `Silicified fault breccia`, `Alteration`, `Sulfur`, `Travertine`), combines them with shallow blind thermal anomalies ($\text{2mDAB} \ge +1.5^\circ\text{C}$, log-weighted by excess temperature) and active thermal wells/springs ($T \ge 30^\circ\text{C}$), and projects them along an **anisotropic Great Basin normal-fault strike kernel** ($\theta_{\text{GB}} = \text{N}18^\circ\text{E}$, $\sigma_\parallel = 2.4\text{ km}$, $\sigma_\perp = 0.8\text{ km}$; Faulds & Hinz, 2015) plus a broad district upflow halo ($\sigma = 5.0\text{ km}$) interacted with sub-pixel scarp sharpness.
  - *Hydrothermal alteration & shallow demagnetization coupling:* Combines K-metasomatic potassium enrichment ($-\text{Th/K}$), redox-trapped uranium (`U/Th`), shallow hydrothermal magnetite-destruction vertical residual ($\text{RTP}_{\text{Band 2}} - \widehat{\text{TMI}}_{\text{up150}}$; Grauch, 2001), MT clay-cap lateral gradient $|\nabla \log \sigma_{\text{MT}}|$ (`Band 17`), and within-quadrant standardized carbonate/basement gravity step (`Bands 5, 13, 15, 18`).
- **Why It Catches Faults Missing from USGS/INGENIOUS Specifically:**
  USGS QFolds and INGENIOUS maps systematically capture tall `> 12°` bedrock range-front scarps visible on regional airphotos while missing **(i)** low-relief `1–3 m` synthetic/antithetic piedmont and intrabasinal scarps in `[0°, 6°)` unconsolidated basin fill (where `52.6%` of faults reside, previously erased by `100 m` DEM averaging), and **(ii)** **blind / fossil hydrothermal fault-valve conduits** where Pleistocene water-table drop shut off surface geysers, leaving only `Qss` silica-cemented sand, opal sinter aprons, or shallow `+2°C`–`+54°C` `2mDAB` conductive anomalies over unmapped buried step-overs.
- **Named Non-Fault Mimic Processes & Suppression:**
  1. *Pleistocene Lake Lahontan wave-cut shoreline berms (`~1,330 m` Sehoo highstand) & lacustrine tufa towers:* suppressed by (a) explicit removal of `Tufa` deposits from `Paleo_geothermal_final.csv`, and (b) requiring cross-contour strike / subsurface gravity-basement-magnetic support rather than contour-parallel zero-gravity beach berms.
  2. *Steep alpine talus chutes & incised fan-head arroyos:* suppressed by $\Delta S_{10/100}$ (which cancels uniform steep cliffs) and `aspect_coherence × hs_lineament` planar-scarp filtering.
- **How It Differs from All Prior Work in `GEMSDOE92` and `GEMSDOE*` Sites:**
  First lane in `GEMSDOE92` to integrate `topo_10m_derived_100m_u8.tif`, `Paleo_geothermal_final.csv` (with tufa mimic filtering), `2m_temperature_probe` `2mDAB`, and `geodawn_extensions_u8.tif`. Unlike `60GEMSDOE`'s channel-restricted `dem10` $\chi$ lanes (`15.2%` channel mask), `VENTSCARP` covers `100.00%` of the footprint and explicitly re-weights away from over-crowded `>= 12°` cliffs into `[0°, 8°)` piedmont/intrabasinal hydrothermal scarps.
- **Expected DTI Gain & Cost:** **Rank #1** — Highest expected `HOLDOUT-DTI` lift (`+8%` to `+25%` on static `d_cat > 2.0` over `KNICKLOQO`'s `0.010788`, while targeting `<= 0.70` external 102-repo sparse overlap); ~25 min compute, `< 1.5 GiB` peak RSS.

---

### Hypothesis H2 (Rank #2)
**Intrabasinal Hydrothermal Magnetite-Destruction Vertical Continuation Residual (`GRAUCHMAG`)**

- **Input Layers & Transform:** `training_features.tif` Band 2 (`rtp`), `geodawn_extensions_u8.tif` Band 4 (`TMI_up150`), and Band 15 (`basement_depth`). Computes standardized shallow vertical magnetic continuation residual $R_{\text{mag}} = z(\text{RTP}) - z(\text{TMI}_{\text{up150}})$ and 1D trough/step curvature inside sedimentary basins ($Z_{\text{base}} > 300\text{ m}$), isolating shallow (`< 300 m`) fault-controlled oxidation of detrital magnetite to hematite/pyrite by ascending hydrothermal fluids (Grauch, 2001, *Geophysics* 66(3), 766–780).
- **Why It Catches Missing Faults:** Intrabasinal faults cutting Plio-Quaternary alluvium lack bedrock escarpments entirely, yet create sharp `100–300 m` linear aeromagnetic lows/steps missed by gravity (`Band 18`) and `100 m` topography (`Band 12`).
- **Named Non-Fault Mimic:** *Magnetite-bearing basaltic paleochannels and Neogene dike swarms.*
- **Differentiation:** `XPHASE` and `EULERFUSE` used single-level FFT derivatives of Band 2 alone; neither used multi-altitude `TMI_up150` upward-continuation residuals or targeted hydrothermal demagnetization troughs.
- **Expected DTI Gain & Cost:** **Rank #2** — Strong in `NW`/`SW` volcanic-detritus basins, but weak standalone in `NE` Paleozoic carbonate basins (`41.6%` of off-catalogue SGMC faults) where host susceptibility is near zero. Included as a tested physical channel inside H1 (`Arm 1` vs `Arm 2`); standalone lane deferred.

---

### Hypothesis H3 (Rank #3)
**K-Metasomatic Adularia/Illite & Redox-Uranium Clay-Cap Perimeter Breach (`ALTERCAP`)**

- **Input Layers & Transform:** `geodawn_extensions_u8.tif` Bands 1–3 (`Th/K`, `U/K`, `U/Th`), `Band 6` (`tc`), `Band 17` (`mt_resistivity`), and `Band 3` (`heatflow`). Computes potassium-over-immobile-thorium enrichment ($-\log(\text{Th/K})$) $\times$ uranium-over-thorium enrichment (`U/Th`) gated by 3D MT conductive smectite clay-cap lateral boundaries ($|\nabla \log \sigma_{\text{MT}}|$).
- **Why It Catches Missing Faults:** Boiling alkali-chloride fluids precipitate adularia/illite (enriching K while Th stays immobile) and trap $\text{U}^{6+}\to\text{U}^{4+}$ along unmapped range-margin and relay-ramp feeder faults breaching the perimeter of conductive clay caps without requiring active hot-spring discharge.
- **Named Non-Fault Mimic:** *Unfaulted alkali rhyolite ash-flow tuffs and potassic playa mudflats* (`RADIOCONTACT` showed radiometric ratios without 10 m scarp localization yield `0.0449` Rule-2 DTI).
- **Differentiation:** `RADIOCONTACT` measured across-strike lithologic *gradients* $|\nabla(\text{K/Th})|$; `ALTERCAP` measures hydrothermal *enrichment maxima* coupled to MT clay-cap edges.
- **Expected DTI Gain & Cost:** **Rank #3** — Low standalone spatial precision (`~5 km` MT smoothness vs `300 m` DTI kernel), high value when gated by 10 m scarp localization in H1.

---

### Hypothesis H4 (Rank #4 — Deferred Due to Survey-Selection Confound)
**USGS 3DEP 1 m LiDAR Bare-Earth Crest-Convexity × Toe-Concavity Dipole (`LIDARSCARP`)**

- **Input Layers & Transform:** `lidar_scarp_features_u8.tif` (`lapneg_max`, `lappos_max`, `step_max`, `coh100`, `valid` across `1 m` 3DEP LiDAR projects). Extracts paired Wallace (1977) scarp-crest convexity and basal-toe concavity dipoles.
- **Why It Catches Missing Faults:** Bare-earth `1 m` LiDAR penetrates sagebrush canopy to resolve `< 1 m` Holocene scarps invisible on `10 m` and `100 m` DEMs.
- **Named Non-Fault Mimic & Confound (`#IR-92-LIDAR-COVERAGE-BIAS`):** *Highway embankments, railroad grades, mine benches*, plus **non-random `75.37%` acquisition coverage** (`24.63%` of footprint missing LiDAR, preferentially unflown in rural eastern basins while flown directly along known Dixie Valley / Walker Lane fault zones).
- **Expected DTI Gain & Cost:** **Rank #4 (Deferred)** — Seamless `10 m` 3DEP (`100.00%` footprint coverage) captures sub-pixel scarps without survey-boundary leakage or rural-basin starvation.

---

## 4. Pre-Registered 3-Experiment Design (`<= 3` Experiments Total)

All three arms use the exact shared template evaluator `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `22,663` withheld positives across 8 spatially buffered folds on `seeds 20, 30`, plus blocked 4-quadrant `LOQO` out-of-province inference so quadrant $q$ never sees labels from quadrant $q$):

1. **Experiment 1 (`ventscarp` — Full Pre-Registered Primary Candidate, Binary `{0.0, 1.0}`, `37,654` dots):**  
   Out-of-quadrant (`LOQO`) L2-regularized logistic model (`C = 0.25`) trained on 1D scarp/ridge candidate pixels (`d_visible > 2.0 px` on holdout; `d_cat > 2.0 px` at deployment) combining:
   - Seamless `10 m` 3DEP sub-pixel scarp excess $\Delta S_{10/100}$, `curv_prof_absmax`, `slope_std`, `steep_frac`, linear scarp coherence `aspect_coherence × hs_lineament`, and `10 m` channel $\Delta k_{sn}$ (`dem10_chi_100m_i16.tif`);
   - Tufa-filtered INGENIOUS paleo-geothermal vents (`195` hydrothermal sites) + INGENIOUS `2mDAB` shallow thermal anomalies + active thermal wells/springs ($T \ge 30^\circ\text{C}$) anisotropic N18°E strike-aligned fault-valve field + GeoDAWN hydrothermal `K/Th`, `U/Th`, shallow magnetite-destruction residual `z(RTP) - z(TMI_up150)`, `Heatflow`, and `MT` clay-cap gradient;
   - Within-quadrant standardized `100 m` gravity/basement/strain/topographic features + draw-blind visible-fault tip/step-over corridor indicators;
   - Label-blind quadrant rank calibration (`gamma = 1.5`) + Poisson-disk greedy spacing (`min_dist_px = 2.8`, `37,654` unit-mass dots).
2. **Experiment 2 (`scarp10m_novent` — Geothermal-Vent & Hydrothermal Ablation Control, Binary `{0.0, 1.0}`, `37,654` dots):**  
   Identical `LOQO` architecture, identical `10 m` 3DEP sub-pixel scarp + `100 m` gravity/basement/strain/visible-corridor features, **with all geothermal-vent, shallow temperature probe, thermal spring, radiometric alteration, upward-continued magnetic residual, heatflow, and MT features ablated (`0` hydrothermal channels)**. Isolates the exact out-of-quadrant blind-fault discovery lift of geothermal-vent physics.
3. **Experiment 3 (`ventscarp_soft` — Continuous `[0, 1]` Tversky Confidence Calibration Test, `docs/NEXT_STEPS.md` Item #4):**  
   Zero additional model training: takes the exact `Experiment 1` (`ventscarp`) out-of-quadrant continuous surface, selects `48,000` Poisson-spaced peaks (`min_dist_px = 2.8`), and assigns smooth calibrated confidence weights $p_i \in [0.30, 1.00]$ (`sum(p) ≈ 37,654`) monotone in out-of-quadrant posterior rank to test whether continuous Tversky allocation beats binary `{0, 1}` dot allocation under `vendor/gems57/metric.py::dti_exact`.

---

## 5. Pre-Registered Gates & Fail-Closed Promotion Criteria

1. **Single-Feature Holdout Leakage Canary (Rule 4):** Every feature tested alone on `gems57-pooled-hide-v2` (`22,663` withheld positives) **before** model evaluation; any feature with symmetric `AUC > 0.90` (`max(AUC, 1 - AUC) > 0.90`) halts the run as leakage until proven otherwise.
2. **Pre-Placement Surface & Final-Dot Uniqueness (Rule 1):** Checked against **both** all local `GEMSDOE92` rasters and all `102` public `GEMSDOE*` repositories (`|Spearman rho| <= 0.90` on pre-placement surface; `3-px forward overlap <= 0.70` on final dots). Under binding repository governance (`#IR-92-LITERAL-DENSE-WITNESS-STOP`), because dense continuous witness `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373` positive pixels) forces literal forward overlap `1.000 > 0.70`, `verdict` must remain `"negative"` (`submission_eligible: false`) for live weekly-slot spending even when `dual_reading_decision` (`DOT_FIELD_MAX_SUPPORT = 150,000`) passes `<= 0.70` across every sparse external dot field. Both literal (`1.000`) and matched-budget / `dual_reading_decision` sparse overlaps will be reported side-by-side.
3. **Automated Format Validation (`[0, 1]` Safety):** Written exclusively via `vendor/gems57/submission_writer.py` and verified by `gems/gates.py` (`11/11` MUST gates) and `vendor/gems57/validate.py` (`EPSG:32611`, `3730 × 3292`, `float32`, `0` NaN/Inf anywhere, finite values in `[0.0, 1.0]`, `0.0` outside footprint).
