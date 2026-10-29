# Pre-Registered Untried Geological & Geothermal-Vent Hypotheses (`2026-10-29` — `LIDAR-SINTERVALVE` Lane)

**Pre-registration timestamp:** `2026-10-29` (authored **strictly prior** to writing or executing any experiment code for this session).  
**Authorized lane:** Single-method structural/geothermal lane (`H-92G1: LIDAR1M-ANTISLOPE-SINTERVALVE`), tested within the strict **3-experiment / 2-hour budget** (`E1` single-feature leakage canaries & pre-placement surface registry audit; `E2` fold-proper spatially-blocked `gems57-pooled-hide-v2` hide-and-recover holdout vs `R0_recipe` and all-time repo holdout record `netexpand_far = 0.177976`; `E3` registry-capped full-footprint GeoTIFF + shrinkage-debiased `LBM-v3` audit across all `2,263` unique SHA-256 rasters in 8 GitHub owners).

---

## Codebase Audit Prior to Pre-Registration (`60` Existing Modules in `gems/`)

Before formulating new hypotheses, every module in `gems/` (`knick_loqo.py`, `listric.py`, `chilistric.py`, `faultnet.py`, `netexpand.py`, `coulomb_loqo.py`, `thermotilt.py`, `ventscarp.py`, `riedelvent.py`, `salem_seismo.py`, `riesz_locked.py`, `tipcomp.py`, `vario.py`, etc.) and all prior hypothesis backlogs (`docs/HYPOTHESES_20261028_STANDING.md`, `docs/HYPOTHESES_20261028_9649DFC1.md`, `docs/HYPOTHESES_UNTRYED.md`) were audited:

1. **Zero ingestion of USGS 3DEP 1-meter bare-earth LiDAR in `gems/`:** `grep -rn "lidar_scarp" gems/` returns **0 matches**. Every prior topographic module in `GEMSDOE92` stopped at 100 m (`det_elev`, `det_elev_slope`) or 10 m (`topo_10m_derived_100m_u8.tif`, `dem10_chi_100m_i16.tif`), which smooths out decimeter-to-meter (`0.2–1.5 m`) piedmont fault scarplets, antithetic uphill-facing graben scarplets, and silica-cemented hydrothermal fissure ridges.
2. **Untapped Band-6 Radiometric Total Count (`tc`) + Grauch Magnetite-Destruction Concordance:** `docs/downloads/input_cache_d30d387c.json` proved `training_features.tif` Band 6 (`tc`) is USGS GeoDAWN Radiometric Total Count (`r = 0.99714`), previously misread as magnetic tilt in `salem_seismo.py`.
3. **Untapped Differential Swarm Clustering (`ieq` vs `deq`):** No module in `gems/` exploits the log-excess of full instrumental swarm seismicity (`B16 ieq_n100a15`) over declustered background seismicity (`B10 deq_n100a15`) gated by geodetic dilational strain (`B08 geod_dilaterate`).

---

## Ranked Hypotheses (Ranked by Expected DTI Gain / Implementation Cost & Sandbox Data Availability)

| Rank | ID & Name | Specific Layers Used | Expected DTI Gain | Impl. Cost | Official Free Data & Sandbox Obtainability | Action This Session |
|---:|---|---|---|---|---|---|
| **#1** | **`H-92G1`** `LIDAR1M-ANTISLOPE-SINTERVALVE` | USGS 3DEP 1 m LiDAR (`lidar_scarp_features_u8.tif`, 12 bands, 75.34% footprint) quantile-bridged with 3DEP 10 m (`topo_10m_derived_100m_u8.tif`, 100%), DOE GDR #1391 tufa-filtered paleo-geothermal sinter/Qss/explosion vents + 2 m temperature probes + Fournier enthalpy disequilibrium (`gdr_wellspring_in_footprint.csv`) + volcanic vents (`gdr_volcanic_vents_in_footprint.csv`), `training_features.tif` subsurface Riesz/basement/MT (`B02, B12, B13, B15, B17`), and fold-visible fault network continuation (`d_vis > 4.0 px`) | **High** (`+0.005` to `+0.020` `HOLDOUT-DTI` over `R0_recipe` `0.09775`, challenging all-time repo record `netexpand_far` `0.17798`) | **Medium** (`~350` LOC + 8-fold LOQO) | **YES — Verified & SHA-256 Restored:** USGS 3DEP 1 m DEM (US Public Domain, `17 U.S.C. § 105`, `https://www.usgs.gov/3d-elevation-program`, `sha256=d580bb8bdcdb…`, `36,943,606` B) + DOE GDR #1391 (`CC-BY-4.0`, `https://gdr.openei.org/submissions/1391`) | **IMPLEMENT & VALIDATE (Top Ranked)** |
| **#2** | **`H-92G2`** `TC-RADON-MAGDESTRUCT-SEAM` | `training_features.tif` Band 6 (`tc` GeoDAWN Total Count), `geodawn_extensions_u8.tif` (`U/Th`, `U/K`, `Th/K`, `TMI_up150`), `B02` (`rtp`), `B17` (`cond_surf`) | **Low–Moderate** (`+0.002` to `+0.006` `HOLDOUT-DTI` in volcanic/alluvial cover) | **Low** | **YES — Verified & SHA-256 Restored:** USGS GeoDAWN (`https://doi.org/10.5066/P93LGLVQ`, US Public Domain) | **Defer standalone lane** (keep single-lane discipline) |
| **#3** | **`H-92G3`** `SIBSON-SWARM-DILATATION-MESH` | `training_features.tif` Band 16 (`ieq_n100a15`), Band 10 (`deq_n100a15`), Band 8 (`geod_dilaterate`), Band 7 (`geod_shearrate`), Band 15 (`depth_to_base_surf`) | **Low–Moderate** (`+0.001` to `+0.005` `HOLDOUT-DTI`; 100 m smoothing of catalog epicenters limits 300 m precision) | **Low** | **YES — In Competition Stack:** INGENIOUS/USGS seismicity & GPS strain (`https://gdr.openei.org/submissions/1391`) | **Defer standalone lane** (keep single-lane discipline) |
| **#4** | **`H-92G4`** `NWIS-HYDRAULIC-HEAD-BAFFLE` | USGS NWIS groundwater static water-level table (`waterservices.usgs.gov`) + `B12 det_elev` + `B15 depth_to_base_surf` | **Moderate** on concealed clay-gouge basin faults | **Medium** | **NO (Blocked by Sandbox Allowlist):** Free US Public Domain (`https://waterservices.usgs.gov/rest/gwlevels-service/`), unreachable from sandbox (`github.com`/`pypi.org`/`npmjs.org` only) | **Documented for open-internet staging** |
| **#5** | **`H-92G5`** `ASTER-TIR-SILICA-SWIR-HALO` | NASA LP DAAC ASTER GED v3 Bands 10–14 (`ag100v003`) quartz/opaline reststrahlen index + USGS Landsat C2L2 SWIR `2.20 µm` Al-OH clay halo | **Moderate** on fossil hydrothermal outflow seams | **High** (multi-GB tile mosaic) | **NO (Blocked by Sandbox Allowlist):** Free NASA/USGS Public Domain (`https://lpdaac.usgs.gov/products/ag100v003/`), unreachable from sandbox | **Documented for open-internet staging** |

---

## Detailed Specification of All 5 Hypotheses

### Rank #1 (Selected Single-Method Lane): `H-92G1` — `LIDAR1M-ANTISLOPE-SINTERVALVE`
*(Seamless 1m→10m Quantile-Bridged Wallace Crest–Toe Curvature Dipole, Uphill-Facing Antislope Graben Scarp & Channel-Bank Veto Coupled to Tufa-Filtered Sinter/2m-Probe Hydrothermal Valves)*

- **(a) Specific layers used:**
  1. `lidar_scarp_features_u8.tif` (`3730×3292`, `EPSG:32611`, derived from 706/716 USGS 3DEP 1 m bare-earth LiDAR DEM tiles at 2 m work resolution, `3,892,984` valid cells = `75.34%` of footprint, zero fault-catalogue inputs):
     - `B01 ex_max` (max 2 m slope minus 30 m regional slope), `B03 step_max` (max 10 m minus 50 m slope),
     - `B04 lapneg_max` (`-LoG(6 m)` convex scarp crest curvature), `B05 lappos_max` (`+LoG(6 m)` concave colluvial-wedge toe curvature),
     - `B06 downface_max` (band-passed step gradient **along** 100 m regional upslope — synthetic piedmont normal scarp),
     - `B07 upface_max` (band-passed step gradient **against** 100 m regional slope — **antithetic uphill-facing graben / fissure-ridge scarplet**),
     - `B08 cross_max` (band-passed gradient **across** regional slope — incised channel-bank / fan-gully detector),
     - `B09 relief` (sub-100m elevation range), `B10 coh100` (2 m structure-tensor orientation coherence), `B11 strike` (2 m strike azimuth `0–180°`), `B12 valid` (`1` = full LiDAR coverage, `0` = non-LiDAR cell).
  2. `topo_10m_derived_100m_u8.tif` (100% footprint coverage USGS 3DEP 10 m sub-pixel `slope_p90`, `steep_frac`, `curv_prof_absmax`, `aspect_coherence`, `hs_lineament`, `relief_local`, `dem_mean`) — used strictly to quantile-bridge the `24.66%` non-LiDAR gap so zero tile-boundary seam exists.
  3. DOE GDR #1391 INGENIOUS hydrothermal & volcanic conduit layers (`paleo_geothermal_regional.zip` keeping `Sinter`, `Silica-cemented sand`, `Explosion craters`, `Sulfate crust` while rejecting shoreline `Tufa`; `2m_temperature_probe_INGENIOUS_regional_data.zip` shallow conductive `T_2m` residual; `gdr_wellspring_in_footprint.csv` Fournier quartz/chalcedony enthalpy disequilibrium `ΔT = max(T_quartz, T_chalc) - T_meas`; `gdr_volcanic_vents_in_footprint.csv` Quaternary dike/vent alignments).
  4. Subsurface potential-field & structural continuation context (`training_features.tif` `B02 rtp`, `B12 det_elev`, `B13 iso_grav_anom`, `B15 depth_to_base_surf`, `B17 cond_surf`, plus fold-visible `gems/faultnet.py` + `gems/netexpand.py` visible-fault continuation features computed strictly from `fold["visible"]` during `E2` holdout).

- **(b) Physical signature & mathematical transform:**
  1. **De-quantization & Survey-Seam-Free Quantile Bridge:** Invert the documented `lidar_scarp_features.json` encoding $x = x_{\max}\cdot t^{-1}((q - 1)/254)$ on `valid >= 0.5`. Map each physical index inside `valid >= 0.5` to empirical rank-percentiles $u \in (0, 1)$, and fit an out-of-fold ridge map $\hat{u}_{10\text{m}}(x)$ from the 9-band 10 m DEM stack on `valid >= 0.5` to seamlessly impute the `24.66%` `valid < 0.5` cells (matched mean and variance, verified by testing `valid` alone as a leakage/seam canary).
  2. **Wallace (1977) Paired Crest–Toe Curvature Dipole with Fluvial Channel-Bank Veto (`W_scarp`):**
     $$W_{\text{dipole}} = \sqrt{\kappa_{-}^{\text{6m}} \cdot \kappa_{+}^{\text{6m}}} \cdot C_{100}, \qquad V_{\text{bank}} = \frac{\max(g_{\text{down}},\, g_{\text{up}}) - g_{\text{cross}}}{\max(g_{\text{down}},\, g_{\text{up}}) + g_{\text{cross}} + \varepsilon}$$
     $$W_{\text{scarp}} = \frac{W_{\text{dipole}} \cdot \max(0,\, V_{\text{bank}})}{\sqrt{R_{100} + 5\,\text{m}}}$$
     A Quaternary fault scarp produces a **collocated convex crest and concave colluvial-wedge toe** oriented **parallel** to topographic contours ($g_{\text{down}}$ or $g_{\text{up}} \gg g_{\text{cross}}$) on low-relief piedmont fans ($R_{100}$ small), whereas incised ephemeral stream banks strike **downslope** ($g_{\text{cross}} \gg \max(g_{\text{down}}, g_{\text{up}}) \implies V_{\text{bank}} \le 0$).
  3. **Antithetic Uphill-Facing Graben & Fissure-Ridge Asymmetry (`A_graben`) with Lahontan Shoreline Suppression:**
     $$A_{\text{graben}} = \frac{g_{\text{up}} \cdot C_{100} \cdot (1 - S_{\text{Lahontan}})}{\sqrt{R_{100} + 5\,\text{m}}}, \qquad S_{\text{Lahontan}} = \exp\!\left(-\frac{(z - 1330\,\text{m})^2}{2\,(45\,\text{m})^2}\right) \cdot \mathbb{I}[\text{low subsurface }\nabla g]$$
     Fluvial erosion cannot carve an uphill-facing contour-parallel step on an alluvial fan, and wave-cut Pleistocene Lake Lahontan highstand benches (`~1,330 m` elevation in western/central Nevada) face exclusively *downslope* toward the playa ($g_{\text{down}} \gg g_{\text{up}}$) and lack subsurface gravity/magnetic roots.
  4. **Cross-Scale Strike-Locked Sinter / 2m-Probe Hydrothermal Conduit (`H_valve`):**
     Compute 2D Riesz monogenic subsurface strike $\theta_{\text{sub}}$ from `B13 iso_grav_anom` + `B15 depth_to_base_surf`, enforce axial alignment $|\cos(\theta_{1\text{m}} - \theta_{\text{sub}})|$ with 1 m LiDAR tensor strike `B11`, and gate with a multi-scale hydrothermal kernel combining tufa-filtered sinter/explosion-crater/Qss deposits, shallow 2 m conductive temperature probe anomalies (`ΔT_2m` detrended for elevation), Fournier silica geothermometer disequilibrium (`ΔT_chem > 25°C`), and Quaternary volcanic vent alignments.

- **(c) Why it catches faults missing from the USGS / INGENIOUS compilation:**
  1. Approximately 60–75% of commercially productive Great Basin geothermal systems (Brady's, Desert Peak, Salt Wells, San Emidio, McGinness Hills, Tungsten Mountain; Faulds et al., 2011, 2020) are structurally controlled by **intra-basin step-overs, synthetic–antithetic piedmont grabens, and blind accommodation zones** whose surface expression consists of degraded `0.2–1.2 m` alluvial scarplets or silica-cemented fissure ridges invisible on 1:24k aerial photos and completely smoothed away in 10 m / 30 m DEMs.
  2. Unlike range-bounding master faults (already densely mapped in `existing_faults.tif`), off-catalogue step-over strands frequently lie `400 m – 3 km` basinward of mapped range fronts (`d_vis > 4 px`), directly in the high-leverage zone of the competition's 300 m triangular DTI kernel.

- **(d) Named non-fault geological/anthropogenic mimics & explicit deconfounders:**
  1. **Incised alluvial-fan channel banks & arroyos:** Vetoed directly by `V_bank` (`cross_max` suppression).
  2. **Pleistocene Lake Lahontan (`~1,330 m`) & Lake Dixie wave-cut beach ridges and shorezone tufa mounds:** Vetoed by `upface_max` antithetic pairing, `S_Lahontan` highstand contour damping where subsurface basement gradient is flat, and explicit removal of `Tufa` rows from `Paleo_geothermal_final.csv`.
  3. **Interstate I-80 / US-50 / railroad embankment cuts across playas:** Suppressed by requiring multi-cell tectonic corridor continuity + subsurface potential-field/basement support (`B13/B15/B17`).

- **(e) How it differs from existing repository work:**
  - First module in `GEMSDOE92` (`gems/lidar_sintervalve.py`) to ingest the 12-band USGS 3DEP 1 m LiDAR tensor/LoG dataset (`lidar_scarp_features_u8.tif`) and `gdr_volcanic_vents_in_footprint.csv`.
  - First explicit Wallace paired 6 m LoG crest–toe dipole (`sqrt(lapneg * lappos)`), first uphill-facing antislope graben detector (`upface_max`), first sub-100m cross-slope channel-bank veto (`cross_max`), and first seamless 1m→10m quantile-imputation bridge fused with fold-proper far-corridor (`d_vis > 4.0`) LOQO training.

---

### Rank #2: `H-92G2` — `TC-RADON-MAGDESTRUCT-SEAM`
- **(a) Specific layers:** `training_features.tif` Band 6 (`tc`, verified GeoDAWN Radiometric Total Count), `geodawn_extensions_u8.tif` (`U/Th`, `U/K`, `Th/K`, `TMI_up150`), `B02` (`rtp`), `B17` (`cond_surf`).
- **(b) Physical signature / transform:** High-pass lithology-normalized radiometric eU/eTh and Total-Count linear ridge $Z_{\text{Rn}} = \text{LoG}_{\sigma}(\text{TC}) + \text{zscore}(U/Th)$ collocated with Grauch (2002) short-wavelength magnetite-destruction troughs $D_{\text{mag}} = \max(0, \text{TMI}_{\text{up150}} - \text{RTP})$ and shallow smectite MT conductivity (`B17`).
- **(c) Why off-catalogue:** Permeable blind fault damage zones advect $^{222}\text{Rn}$ gas (`t_{1/2}=3.8 d`, detected via $^{214}\text{Bi}$ gamma emission in `TC` and `U`) and leach primary titanomagnetite in volcanic/alluvial cover even where zero topographic scarp survives.
- **(d) Named non-fault mimic:** Unfaulted high-silica rhyolite domes and uraniferous playa evaporite pans.
- **(e) Repo distinction:** `salem_seismo.py` misread Band 6 `tc` as magnetic tilt; `radiocontact` looked at K/Th lithologic boundaries rather than collinear eU/TC + magnetite-destruction fault seams.

### Rank #3: `H-92G3` — `SIBSON-SWARM-DILATATION-MESH`
- **(a) Specific layers:** `B16` (`ieq_n100a15` full instrumental seismicity), `B10` (`deq_n100a15` declustered seismicity), `B08` (`geod_dilaterate`), `B07` (`geod_shearrate`), `B15` (`depth_to_base_surf`).
- **(b) Physical signature / transform:** Sibson (1996) fluid-driven mesh-swarm index $M_{\text{swarm}} = [\log(1 + \text{ieq}) - \log(1 + \text{deq})] \cdot \sigma(\dot{\varepsilon}_{\text{dil}} / (|\dot{\varepsilon}_{\text{shear}}| + \varepsilon))$ along intermediate basement-depth flanks (`400–2,000 m`).
- **(c) Why off-catalogue:** Pressurized geothermal fluids trigger non-Omori micro-earthquake swarms (`ieq >> deq`) on blind dilatant fracture meshes at `3–7 km` depth with no mapped Quaternary surface rupture.
- **(d) Named non-fault mimic:** Open-pit mine blasting clusters and geothermal plant reinjection seismicity.
- **(e) Repo distinction:** Prior modules used either `deq` alone (`salem_seismo.py`) or seismic *deficit* (`riesz_locked.py`); none computed the `ieq/deq` swarm-clustering excess gated by GPS dilatation.

### Rank #4: `H-92G4` — `NWIS-HYDRAULIC-HEAD-BAFFLE` *(External — Blocked in Sandbox)*
- **(a) Specific layers:** USGS NWIS Groundwater Levels (`https://waterservices.usgs.gov/rest/gwlevels-service/`) + `B12 det_elev` + `B15 depth_to_base_surf`.
- **(b) Physical signature / transform:** Anisotropic cross-strike hydraulic-head step $|\nabla h_{\text{wt}}|$ exceeding topographically driven Darcy flow across low-permeability clay-smear fault cores (Bense et al., 2013).
- **(c) Why off-catalogue:** Concealed intra-basin normal faults act as 10–50 m groundwater baffles beneath flat agricultural/playa floors.
- **(d) Named non-fault mimic:** Irrigation pumping cones of depression.
- **(e) Availability:** Official free US Public Domain (`waterservices.usgs.gov`), blocked by sandbox outbound host allowlist.

### Rank #5: `H-92G5` — `ASTER-TIR-SILICA-SWIR-HALO` *(External — Blocked in Sandbox)*
- **(a) Specific layers:** NASA LP DAAC ASTER GED v3 (`ag100v003`, Bands 10–14 TIR emissivity) + USGS Landsat C2L2 SWIR (`2.20 µm`).
- **(b) Physical signature / transform:** Quartz/chalcedony `8.6–9.1 µm` reststrahlen emissivity minimum flanked by `2.20 µm` illite/kaolinite clay alteration halo.
- **(c) Why off-catalogue:** Fossil self-sealed silica ledges mark blind geothermal upflow faults across desert basins where hot springs are now extinct.
- **(d) Named non-fault mimic:** Eolian quartz dune sheets (`Sand Mountain`) and mine waste dumps.
- **(e) Availability:** Official free NASA/USGS Public Domain (`lpdaac.usgs.gov`), blocked by sandbox outbound host allowlist.

---

## Pre-Registered 3-Experiment Protocol & Falsification Criteria

1. **`E1` — Single-Feature Leakage Canaries & Pre-Placement Surface Uniqueness Gate:**
   - Evaluate every individual `H-92G1` feature (plus `lidar_valid` tile-coverage indicator) alone on `gems57-pooled-hide-v2` (`seeds=(20, 30)`, `22,663` withheld positive pixels). **Hard gate:** symmetric `AUC <= 0.90` on every feature (`Rule 4`), and `lidar_valid` symmetric `AUC < 0.60` confirming survey coverage does not leak fault labels.
   - Check pre-placement continuous surface rank correlation (`|Spearman ρ| <= 0.90`) and top-`N` / literal overlap against all `2,263` unique SHA-256 rasters in `.cache/registry_v3`.
2. **`E2` — Spatially-Blocked Fold-Proper `HOLDOUT-DTI` vs `R0_recipe` and All-Time Record `netexpand_far`:**
   - Train 8-fold Leave-One-Spatial-Block-Out HistGradientBoosting (`LIDAR-SINTERVALVE`) using **zero-catalogue `H-92G1` features + strictly `fold["visible"]` network continuation features (`gems/faultnet.py`)**, masking `fold["visible"]` pixel-exactly and emitting sparse `37,654`-dot crests (`d_vis > 4.0 px` far-corridor and `d_vis > 2.0 px` standard corridor).
   - Score via `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `alpha=0.2`, `beta=0.8`, `300 m` triangular kernel, `1,000` paired 20 km block bootstrap draws) against:
     - `R0_recipe` (`0.09775`),
     - `NETEXPAND` (`0.14680` at `d_vis > 2.0`), and
     - **`netexpand_far` (`0.177976` `[0.163109, 0.193227]` at `d_vis > 4.0` — the all-time repository `HOLDOUT-DTI` record)**.
3. **`E3` — Full-Data Registry-Unique GeoTIFF Build (`<= 0.65` PI-1 Overlap Across All `2,263` Rasters) & Dual Gate Audit:**
   - Emit deterministic single-band `float32` GeoTIFF (`docs/downloads/gemsdoe92-lidarsintervalve-...-20261029-...-zeros.tif` + `.zip`) via shared `submission_writer.py` / `gems/gates.py` (`[0, 1]`, `0` NaN, `0.0` outside footprint, `d_cat > 2.0 px`).
   - Enforce PI-1 3-px overlap `<= 0.65` (`< 0.70`) and `|ρ| <= 0.90` across all `2,263` unique SHA-256 rasters in 8 GitHub owners (including `lbmc1`, `rieszlbm2`, `tipcomp`, `blindcorridor`, and all Focus-9 peaks), while recording the binding literal `17GEMSDOE` / `13GEMSDOE` dense-witness stop (`1.000 > 0.70`) and keeping `verdict = "negative"`, `submission_eligible = false` fail-closed if ANY binding gate (including literal overlap) blocks promotion.
