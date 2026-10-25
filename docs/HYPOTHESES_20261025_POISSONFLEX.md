# Pre-Registered Geological Hypotheses — `POISSONFLEX` Session (2026-10-25)

**Repository:** `buffedlizard55-lab/GEMSDOE92` · **Branch:** `arena/50fdd1bf-gemsdoe92`  
**Pre-registration timestamp:** `2026-10-25` (**committed prior to any `gems/poissonflex.py` implementation, feature screen, or holdout evaluation**)  
**Protocol governance:** Parallel-Run Protocol Rules 1–6 (`<= 3` experiment cap; leakage canary symmetric `AUC <= 0.90` on every feature; pre-placement surface & final-dot uniqueness `|rho| <= 0.90` and 3-px forward overlap `<= 0.70` under `gems57.uniqueness.dual_reading_decision` across all local + 102-repo public rasters; every score labeled `HOLDOUT-DTI` or `ORGANIZER-CONFIRMED`, never a projection).

---

## 0. Prerequisite Findings from Previous-Session Next Steps (`docs/NEXT_STEPS.md` #1 & #2)

Before designing new hypotheses, we executed both priority items queued in `docs/NEXT_STEPS.md`:

1. **Selector Re-Audit of Stored `COULOMBLOQO` Rasters Under `dual_reading_decision` (`evidence/coulomb_loqo_dual_reading_selector.json`):**
   Across the complete SHA-1-verified 102-repo public inventory (`1,414` unique blobs, `0` missing blobs; `1,321` non-empty non-self competition-grid rasters = `1,136` dot fields `<= 150,000` px + `185` continuous surfaces `> 150,000` px):
   - Every dense surface (`> 150,000` px, including `17GEMSDOE E-proba-multiscale` at `5,167,373` px) drops below `0.54` under matched-budget top-`37,654` support (`0.535853` for `standalone`, `0.440617` for `dual45`).
   - **However, BOTH `COULOMBLOQO standalone` (`0.739842` across 8 sparse dot-field witnesses in `GEMSDOE23`, `62GEMSDOE`, `12GEMSDOE`, `GEMSDOE52`) and `COULOMBLOQO dual45` (`0.722420` across 4 sparse witnesses in `GEMSDOE23` at `100,000 <= 150,000` px) still fail `dual_reading_decision` (`duplicate: true, verdict: "negative"`).**
   - Consequently, **no existing artifact in `GEMSDOE92` is eligible for a weekly submission slot**; a genuinely distinct, higher-`HOLDOUT-DTI` physical model is required.

2. **Root-Cause Resolution of `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` (`evidence/ne_quadrant_loqo_collapse_diagnostic.json`):**
   Stratifying all 19 input bands and all stored LOQO rasters across the 4 spatial quadrants (`NW 22.3%`, `NE 27.6%`, `SW 27.6%`, `SE 22.4%` of footprint) revealed a severe, previously unquantified **tectonic-province covariate shift**:
   - In **`NE`** (Northern Great Basin / Owyhee Volcanic Plateau / Humboldt River interior), GPS `Band 7 geod_shearrate` has `median = 0.0, p90 = 0.70` and `Band 4 geod_2ndinv` has `median = 3.8, p90 = 6.10`, whereas in `{NW, SW, SE}` (Walker Lane & Central Nevada Seismic Belt — the exact 3 training quadrants of `clf_NE`!), `geod_shearrate` medians are `6.3, 18.26, 15.5` (`p90 = 13.90–30.41`) and `geod_2ndinv` medians are `15.6, 34.5, 29.1` (`p90 = 28.09–46.40`).
   - Passing unstandardized regional covariates and concatenating uncalibrated out-of-quadrant `predict_proba` maps caused global top-`K` selection to **starve `NE`** (`0.1%–0.7%` of dots in `BLINDFAULT`, `mean_static_DTI = 0.000000–0.000163`; only `11.1%–11.2%` of dots in `EULERFUSE` and `COULOMBLOQO` across `27.6%` of the footprint!) while **over-packing `SW` scarps (`38.5%–52.6%`)** — the exact mechanism that drove `COULOMBLOQO`'s `0.7398` sparse overlap against SW-heavy `GEMSDOE23` / `GEMSDOE52` habitats!
   - By contrast, balanced-footprint references (`H19-5` `NE = 27.7%`, `R0` `NE = 26.9%`) achieve their **highest** per-quadrant holdout DTI in `NE` (`0.072524` and `0.004711`).

---

## 1. Ranked Untried Geological Hypotheses (4 Candidates, Ranked 1 → 4)

### Rank 1 (Selected for Implementation): `POISSONFLEX` — Province-Calibrated Moving-Window Poisson Gravity–Magnetic Demagnetization, Buried Basement 2nd-Order Rollover Flexure & Wineglass-Knickpoint LOQO Ridge Model

- **Specific Geophysical & Geomorphic Layers:**
  - `training_features.tif` (`EPSG:32611`, `3730 × 3292` at 100 m):
    - **Band 2 (`rtp`)**: Reduced-to-pole magnetic anomaly $M(\mathbf{x})$ (true magnetic channel; **Band 6 `tc` is excluded** per `#IR-92-BAND6-TC-MISLABEL` because it is Radiometric Total Count at $r = 0.99714$ with `geodawn_rad_u8.tif` Band 4);
    - **Band 11 (`iso_grav_anom_vg`)**, **Band 13 (`iso_grav_anom`)**, **Band 5 (`iso_grav_anom_slope`)**, **Band 18 (`iso_grav_anom_hg`)**: Isostatic gravity anomaly $g(\mathbf{x})$, vertical derivative $\partial_z g(\mathbf{x})$, horizontal gradient magnitude $\|\nabla_h g\|$, and signed E–W horizontal gradient $\partial_x g$;
    - **Band 15 (`depth_to_base_surf`)**: Gravity/drillhole-constrained Cenozoic sedimentary cover thickness $B(\mathbf{x}) \ge 0$;
    - **Band 12 (`det_elev`)** & **Band 19 (`det_elev_slope`)**: Detrended elevation $z(\mathbf{x})$ and slope;
    - **Band 4 (`geod_2ndinv`)**, **Band 7 (`geod_shearrate`)**, **Band 8 (`geod_dilaterate`)**: GPS/InSAR strain-rate invariants;
    - **Band 17 (`cond_surf`)**: Magnetotelluric subsurface electrical conductivity;
  - `external/geodawn_rad_u8.tif`: **Bands 1–3 (`K, Th, U`)** lateral contact gradients (`\|\nabla(K/(Th+1))\|`, `\|\nabla(U/(Th+1))\|`; raw K/U levels avoided as standalone polarity per `#IR-92-GEODAWN-RAW-LEVEL-INVERSION`);
  - `external/gdr_wellspring_in_footprint.csv` (DOE GDR #1391 / GBCGE INGENIOUS): surface thermal springs (`Hot` stripped per `#IR-92-GDR-HOT-WHITESPACE`) and `>= 80 °C` blind quartz/chalcedony/Na-K-Ca geothermometer wells (**`dist_known_fault_px` dropped immediately on load** per `#IR-92-GDR-CSV-FAULT-LEAKAGE-COL`).

- **Physical Signature & Mathematical Transforms (Three Untried Geophysical Operators + Unsupervised Province Calibration):**
  1. **Moving-Window Poisson Gravity–Magnetic Coupling & Hydrothermal Magnetite-Destruction Residual (Garland 1951; Cordell & Taylor 1971; Chandler et al. 1981; Blakely 1995 §5.5):**
     By Poisson's theorem, a basement block with uniform magnetization contrast $\Delta J$ and density contrast $\Delta\rho$ satisfies $M(\mathbf{x}) = A(\mathbf{x}) + \alpha_{\text{Poisson}}\,\partial_z g(\mathbf{x})$, where $\alpha_{\text{Poisson}} \propto \Delta J / \Delta\rho$. Over Gaussian moving window $W_\sigma$ ($\sigma = 4.0\text{ px} = 400\text{ m}$), let $\mu_M = G_\sigma * M$, $\mu_{gz} = G_\sigma * (\partial_z g)$, $\mathrm{Cov}_\sigma(M, \partial_z g) = G_\sigma * (M\,\partial_z g) - \mu_M \mu_{gz}$:
     - *Local Poisson Correlation:* $r_{\text{PG}}(\mathbf{x}) = \mathrm{Cov}_\sigma(M, \partial_z g) / (\sqrt{\mathrm{Var}_\sigma(M)\,\mathrm{Var}_\sigma(\partial_z g)} + \varepsilon) \in [-1, 1]$;
     - *Lateral Magnetization-to-Density Contact Jump:* $\|\nabla_h \operatorname{arsinh}(\alpha_{\text{Poisson}}(\mathbf{x}))\|$, where $\alpha_{\text{Poisson}} = \mathrm{Cov}_\sigma(M, \partial_z g)/(\mathrm{Var}_\sigma(\partial_z g) + \varepsilon_g)$, localizing steep juxtapositions of distinct crystalline/volcanic terranes across concealed basement faults;
     - *Hydrothermal Magnetite-Destruction Conduit Residual:* Along active geothermal upflow zones (`>80–220 °C`), hydrothermal alteration leaches ferrimagnetic titanomagnetite into non-magnetic pyrite/hematite/leucoxene ($\Delta J \to 0$) while silica/carbonate sealing preserves density contrast ($\|\nabla_h g\|$ high), producing a decoupled trough:
       $$D_{\text{Poisson}}(\mathbf{x}) = \widetilde{\|\nabla_h g\|}(\mathbf{x}) \cdot \bigl(1 - |r_{\text{PG}}(\mathbf{x})|\bigr) \cdot \operatorname{sat}\!\bigl(\max(0, \nabla_h^2 M(\mathbf{x}))\bigr).$$
  2. **Buried Basement 2nd-Order Listric Rollover Flexure & Differential-Compaction Hinge (Jachens & Holzer 1982; Gibbs 1984; Jachens & Moring 1990):**
     Let $L_B(\mathbf{x}) = \log(B(\mathbf{x}) + 20\text{ m})$ and $\mathbf{n}_B = \nabla G_3(L_B) / (\|\nabla G_3(L_B)\| + \varepsilon)$ be the basinward dip normal of the buried basement ramp:
     - *Cross-Strike Buried Footwall Shoulder Curvature:* $\kappa_{B,\perp}(\mathbf{x}) = \mathbf{n}_B^\top \mathbf{H}_\sigma(L_B)\,\mathbf{n}_B$ ($\sigma = 2.5\text{ px}$). Whereas $\|\nabla L_B\|$ peaks at the broad mid-ramp inflection `0.5–1.5 km` basinward of the fault subcrop, $\max(0, \kappa_{B,\perp})$ peaks directly over the **convex-upward buried footwall breakaway / synthetic normal-fault projection**;
     - *Differential-Compaction Monocline Concordance:* $C_{\text{compact}}(\mathbf{x}) = \tanh(-\kappa_{z,\perp}/c_z)\cdot\tanh(\kappa_{B,\perp}/c_B)$, detecting subtle 0.5–2 m surface compaction monoclines locked in normal curvature above buried bedrock steps.
  3. **Wineglass-Canyon Saddle Knickpoint & Tectonic-Strike Line Integral (Bull 2007; Kirby & Whipple 2012):**
     Compute the eigenvalues $\lambda_1 \ge \lambda_2$ of the smoothed elevation Hessian $\mathbf{H}_{\sigma=1.5}(z)$. At a fault-crossed range-front canyon mouth ("wineglass valley" / fan-head trench), topography is simultaneously **concave across the thalweg** ($\lambda_1 > 0$) and **convex down the longitudinal stream profile** ($\lambda_2 < 0$):
     $$K_{\text{knick}}(\mathbf{x}) = \sqrt{\max(0, \lambda_1(\mathbf{x})) \cdot \max(0, -\lambda_2(\mathbf{x}))}.$$
     Integrating $K_{\text{knick}}$ with an oriented anisotropic line kernel ($\sigma_\parallel = 6.0\text{ px}, \sigma_\perp = 1.0\text{ px}$) steered along regional gravity/basement strike bridges stream-dissected interfluve gaps where standard elevation coherence fails.
  4. **Unsupervised Within-Quadrant Covariate Alignment + Footprint-Proportional LOQO Tail Equalization:**
     Regional-baseline-shifted covariates (`geod_2ndinv`, `geod_shearrate`, `geod_dilaterate`, `iso_grav_anom`, `cond_surf`, `det_elev`) are mapped to **unlabeled within-quadrant empirical quantiles** $U_q(f(\mathbf{x})) \in [0, 1]$ (using zero fault labels and zero cross-quadrant data), and out-of-quadrant LOQO crest scores are calibrated across quadrants via **unlabeled within-quadrant survival-rank equalization** weighted by valid quadrant footprint share, eliminating `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`.

- **Why Catalogue-Missing Faults Are Detected:**
  1. Blind intrabasin geothermal feeders (e.g., Dixie Valley, Carson Sink, Humboldt House, McGinness Hills plays) have zero surface scarp and destroyed magnetite, defeating both DEM-scarp mappers and conventional magnetic-gradient worms, yet exhibit strong $D_{\text{Poisson}}$ gravity-retained / RTP-demagnetized troughs and $\kappa_{B,\perp} > 0$ basement rollover shoulders.
  2. Concealed basin-margin synthetic splays deform late Holocene alluvium only via differential compaction ($C_{\text{compact}} > 0$) updip of the gravity mid-ramp.
  3. Dissected Miocene volcanic-plateau faults across NE Nevada (Owyhee, Independence, Jarbidge, Santa Rosa ranges) preserve collinear canyon-mouth knickpoints ($K_{\text{knick}}$) despite low GPS strain baseline and eroded interfluve scarps.

- **Named Non-Fault Mimics & How `POISSONFLEX` Rejects Them:**
  1. *Flat-lying remanently magnetized Miocene flood-basalt flow margins (Owyhee / northern Nevada):* strong magnetic edges with near-zero Band 11 vertical-gravity step and negative/random $r_{\text{PG}}$, lacking $\kappa_{B,\perp} > 0$ basement footwall flexure.
  2. *Horizontal resistant welded-tuff ledges wrapping around range spurs:* local profile convexity follows contour curvature around spurs rather than maintaining straight cross-canyon alignment parallel to basement/gravity strike.
  3. *Pleistocene Lake Lahontan wave-cut strandlines:* contour-parallel benches with reversed or zero basement/gravity polarity concordance and zero Poisson basement step.
  4. *Closed-basin evaporite playa margins:* flat concentric conductivity rings with zero basement shoulder curvature and zero Coulomb-compatible tectonic strike.

- **Exact Difference from ALL 17 Existing `gems/*.py` Modules in `GEMSDOE92`:**
  - `eulerfuse.py` solved independent $N=0$ Euler source coordinates on RTP and gravity; `xphase.py` measured 200 m MT–gravity gradient lag; `coulomb_loqo.py` and `coulombdm.py` used separate RTP tilt/Hessian and gravity tilt/polarity. **None computed moving-window Poisson $(M, \partial_z g)$ regression, $\|\nabla_h \alpha_{\text{Poisson}}\|$, or the Poisson gravity-predicted magnetite-destruction residual $D_{\text{Poisson}}$.**
  - `apronridge.py`, `geotension.py`, `hydroconduit.py`, `neoopenness.py`, `xphase.py`, `coulomb_loqo.py`, and `blindfault.py` used only 0th-order cover gates or 1st-order $\|\nabla \log B\|$. **None computed the 2nd-order basement Hessian rollover shoulder $\kappa_{B,\perp} = \mathbf{n}_B^\top \mathbf{H}(\log B)\,\mathbf{n}_B$ or compaction flexure concordance.**
  - `breakline.py`, `scarppol.py`, `stepedge.py`, `piedfront.py`, `strainbreak.py`, and `coulomb_loqo.py` penalized low elevation coherence across canyon mouths. **None computed opposite-sign Hessian saddle knickpoints $K_{\text{knick}}$ or strike-steered cross-canyon knickpoint integrals.**
  - `coulomb_loqo.py`, `eulerfuse.py`, and `blindfault.py` concatenated uncalibrated out-of-quadrant LOQO predictions on unaligned regional covariates (`NE = 0.1%–11.2%` dots). **`POISSONFLEX` introduces strictly label-free within-quadrant covariate rank alignment + footprint-proportional tail equalization.**

- **Pre-Registered 3-Experiment Budget (`<= 3` arms total, Protocol Rule 6):**
  1. **`poissonflex_eq` (Primary Rank-1 Candidate, `S = 37,654`):** Full `POISSONFLEX` feature stack + 1D Poisson/flexure/knickpoint/scarp crest localizer + unsupervised within-quadrant covariate alignment + footprint-proportional quadrant tail equalization at exact parent budget `S = 37,654` (`min_dist = 2.8 px`).
  2. **`poissonflex_raw` (Domain-Calibration Ablation, `S = 37,654`):** Identical `POISSONFLEX` feature stack and crest localizer **without** quadrant tail equalization — isolating the causal holdout-DTI and sparse-uniqueness impact of resolving `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`.
  3. **`poissonflex_opt` (Nested Training-Fold Marginal-DTI Budget Calibration, `S = S_oof`):** Identical `poissonflex_eq` equalized surface emitted at support size $S_{\text{oof}}$ selected strictly by out-of-fold validation across the training quadrants only (zero access to held-out fold truth), testing whether `R0`'s historical `37,654` constant over- or under-emits under $\mathrm{DTI}_{0.2, 0.8}$.

- **Expected `HOLDOUT-DTI` Improvement & Implementation Cost (Pre-Experiment Expectation, NOT a Score):**
  Expected `+0.004` to `+0.015` improvement on strict draw-blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI` above `COULOMBLOQO standalone` (`0.113316`), positive gain on static `d_cat > 2.0` `HOLDOUT-DTI` (`> 0.009220`), AND expected drop of public `<= 150k`-px sparse 3-px forward overlap from `0.7398` to `< 0.68` by eliminating SW scarp over-concentration; ~25 minutes CPU on 2 cores within `3.8 GiB` RAM.

---

### Rank 2 (Queued Reserve): `THERMAL-UPFLOW-PECLET` — Updip Fault-Plane Deconvolution of Skewed Advection–Diffusion Geothermal Plumes

- **Specific Layers:** `external/gdr_wellspring_in_footprint.csv` (`temp_c`, quartz/chalcedony/Na-K-Ca geothermometers, depth; `dist_known_fault_px` dropped), Band 17 (`cond_surf`), Band 15 (`depth_to_base_surf`), Band 13 (`iso_grav_anom`), Band 18 (`iso_grav_anom_hg`), Band 12 (`det_elev`), `external/geodawn_rad_u8.tif` (`K, Th, U`).
- **Physical Signature & Transform:** Prior lanes (`springalign.py`, `hydroconduit.py`, `coulomb_loqo.py`) rasterized wells/springs as isotropic Gaussian kernels or spring-pair chords centered on surface outflow. In dipping Basin-and-Range aquifers, buoyant upflow ascends a $55^\circ\text{--}65^\circ$ normal fault and advects laterally down the shallow water-table gradient ($-\nabla G_{10}(z)$) into the hangingwall (`Péclet > 1`), displacing hot springs and shallow thermal wells `300–1,500 m` basinward of the rooted brittle fault subcrop. Solving an asymmetric upwind Advection–Diffusion kernel shifts plume likelihood updip along $-\nabla B(\mathbf{x})$ onto the nearest resistive-footwall / conductive-clay-cap boundary ($\|\nabla \log \text{Band 17}\|$).
- **Why Missing from Catalogue:** Outflow springs emerge inside flat hangingwall playas/marshes hundreds of meters from the concealed feeder fault, leaving zero surface scarp at either the spring or the updip subcrop.
- **Named Non-Fault Mimics:** Stratabound artesian carbonate warm springs, agricultural irrigation tailwater ponds, and closed-playa evaporite Na-K-Ca brine artifacts.
- **Difference from Existing Modules:** Replaces symmetric point/chord spring kernels (`springalign.py`, `hydroconduit.py`) with directional hydraulic-gradient + basement-updip Péclet deconvolution.
- **Expected `HOLDOUT-DTI` Improvement & Cost:** `+0.001` to `+0.004` localized around the 419 thermal/blind-geothermometer records (limited global recall across amagmatic/athermal fault segments); ~15 min CPU.

---

### Rank 3 (Queued Reserve): `SPECTRAL-DEPTH-DECAY` — Local Multi-Band Wavenumber Log-Power Slope Discontinuity (`Spector-Grant` Magnetic Source-Top Offset vs Gravity Basement Depth)

- **Specific Layers:** Band 2 (`rtp`), Band 14 (`tmi`), Band 13 (`iso_grav_anom`), Band 15 (`depth_to_base_surf`).
- **Physical Signature & Transform:** Under Spector & Grant (1970), radial ensemble log-power of RTP magnetics decays with wavenumber $k$ as $-2 z_{\text{mag}}$. Estimating local magnetic source-top depth $z_{\text{mag}}(\mathbf{x}) = \frac{1}{2(k_2 - k_1)}\log\frac{E(k_1,\mathbf{x})}{E(k_2,\mathbf{x})}$ from quadrature filter banks at wavelengths $\lambda \in \{300, 600, 1200, 2400\text{ m}\}$ yields two untried observables: (i) lateral magnetic-basement throw $\|\nabla_h z_{\text{mag}}(\mathbf{x})\|$ across concealed faults where susceptibility contrast is weak, and (ii) **intrabasin volcanic-horst discrepancy** $B(\mathbf{x}) - z_{\text{mag}}(\mathbf{x})$, isolating shallowly buried faulted Tertiary basalts sitting inside deep Cenozoic sedimentary basins ($z_{\text{mag}} \ll B$).
- **Why Missing from Catalogue:** Intrabasin buried basalt horsts (e.g., Carson Sink / Fallon / Desert Peak blind reservoirs) lie beneath flat Holocene lacustrine clays with zero scarp and weak surface gravity slope, yet exhibit sharp steps in $z_{\text{mag}}$ above deep gravity basement $B$.
- **Named Non-Fault Mimics:** Unfaulted erosional paleochannels filled with ponded basalt flows and gradational pluton aureoles.
- **Difference from Existing Modules:** `coulombdm.py` used multi-altitude upward-continued tilt persistence; `eulerfuse.py` solved $N=0$ contact Euler points; neither estimated continuous Spector–Grant spectral ensemble depth $z_{\text{mag}}(\mathbf{x})$ or the $(B - z_{\text{mag}})$ volcanic-in-basin discrepancy.
- **Expected `HOLDOUT-DTI` Improvement & Cost:** `+0.002` to `+0.006` in volcanic-floored basins; ~20 min CPU.

---

### Rank 4 (External Data Expansion — Verified Official Sources, Network-Blocked in Sandbox): `DECONFOUNDED-INSAR-3DEP-1M` — Pumping-Deconfounded OPERA Sentinel-1 Surface Displacement Gradient × USGS 3DEP 1 m LiDAR Micro-Scarps

- **Specific Official External Datasets (Verified Public Government Archives):**
  1. **NASA JPL / ASF DAAC OPERA Surface Displacement (`OPERA_L3_DISP-S1_V1`, 30 m posting, CC0):** `https://asf.alaska.edu/datasets/daac/opera/` (ascending + descending Sentinel-1 C-band InSAR line-of-sight velocity time series across Nevada/Oregon/California);
  2. **USGS 3DEP 1 m LiDAR Digital Elevation Models (Public Domain):** `https://www.usgs.gov/3d-elevation-program` (tile URLs enumerated in the competition's `Digital-elevation-model-links-JSON.pdf` / `1m_DEM_links.csv` handout on `https://www.drivendata.org/competitions/306/competition-doe-gems/data/`);
  3. **UNR Nevada Geodetic Laboratory MIDAS Dense GPS Velocities:** `http://geodesy.unr.edu/velocities/midas.IGS14.txt` (Blewitt et al. 2016) + **USGS NWIS Groundwater Sites:** `https://waterdata.usgs.gov/nwis`.
- **Physical Signature & Transform:** Invert ascending + descending Sentinel-1 LOS velocities for quasi-vertical $v_U$ and quasi-east $v_E$ at 100 m posting, subtract radially symmetric Mogi/poroelastic compaction bowls centered on agricultural/mining pumping wells, and intersect short-wavelength horizontal strain localization $\|\nabla_h v_E\|$ (`100–500 m` aperture vs 10–25 km GPS smoothing in Bands 4/7/8) with sub-meter (`0.3–1.5 m`) 3DEP 1 m LiDAR alluvial-fan micro-scarps aggregated onto the 100 m `EPSG:32611` grid.
- **Why Missing from Catalogue & Why It Bridges Toward `0.35–0.44`:** Legacy 1:24,000–1:250,000 aerial-photo fault maps missed `<1.5 m` Holocene piedmont scarps and aseismic creeping accommodation zones that 100 m DEM (`Bands 12, 19`) smooths below Nyquist; 1 m LiDAR + 30 m OPERA InSAR directly observe those missing Quaternary strands.
- **Named Non-Fault Mimics:** Agricultural pivot groundwater-subsidence rings, open-pit mine dewatering cones, highway embankments, and Pleistocene Lake Lahontan beach berms.
- **Sandbox Availability Verification:** Outbound network access in this execution environment is restricted strictly to `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, and `files.pythonhosted.org`; neither `1m_DEM_links.csv` nor OPERA/3DEP tiles are staged in `buffedlizard55-lab/*`. Accordingly, Rank 4 cannot be fetched inside this sandbox without violating zero-manual-input constraints and is documented with verified official URLs for an unrestricted runner, while Rank 1 (`POISSONFLEX`) is implemented and validated end-to-end below.
