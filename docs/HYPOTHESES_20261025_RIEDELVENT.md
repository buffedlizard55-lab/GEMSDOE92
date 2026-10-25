# Pre-Registered Geological Hypotheses — `2026-10-25` Session (`RIEDELVENT` Lane)

**Branch:** `arena/bbfe2d11-gemsdoe92`
**Pre-Registration Timestamp:** Locked prior to any `RIEDELVENT` feature evaluation, holdout scoring, or GeoTIFF emission.
**Shared Evaluator (Protocol Rule 2 — zero private forks):** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, $\alpha = 0.2$, $\beta = 0.8$, $R = 300\text{ m} = 3.0\text{ px}$ triangular $\max$-kernel, `22,663` withheld catalogue fault pixels across `8` buffered whole-segment folds, `seeds 20, 30`, `1,000`-draw paired `20 km` spatial-cluster bootstrap).
**Shared Packaging & Validation (Protocol Rule 2):** `vendor/gems57/submission_writer.py`, `vendor/gems57/validate.py`, `gems/gates.py`, `vendor/gems57/uniqueness.py`.
**Experiment Budget (Protocol Rule 6):** Strictly `3` experiments (`riedelvent_bin37k`, `collinear_novent_bin37k`, `riedelvent_tail85k`); **`0` live weekly DrivenData submission slots spent**.
**Stored Repository Holdout Bests to Beat:**
- **Strict Draw-Blind Rule-2 (`d_visible > 2.0`, public-unique zero-catalogue LOQO):** `VENTSCARP ventscarp` **`0.112213 [0.096670, 0.127254]`** (`evidence/ventscarp_run_card.json`), `LISTRIC standalone` `0.110593 [0.097436, 0.123346]` (public-duplicate `0.7107 > 0.70`), `KNICKLOQO standalone` `0.109043 [0.097872, 0.120534]`.
- **Static Deployment Raster (`d_cat > 2.0`):** `LISTRIC standalone` **`0.010909 [0.009543, 0.012278]`** (public-duplicate `0.7107 > 0.70`), `KNICKLOQO standalone` **`0.010788 [0.009468, 0.012201]`** (#1 public-unique under `dual_reading_decision`).
- **Off-Catalogue Bedrock Structure (`USGS SGMC PROXY`):** `POISSONFLEX opt` (`45k` dots) `0.120957`, `KNICKLOQO standalone` (`37,654` dots) `0.103912` (`d_cat > 3 px`) / `0.095878` (`d_cat > 5 px`).

---

## 1. Execution of Prior-Session Next Steps (`docs/NEXT_STEPS.md`)

Per `SESSION_PROMPT.md` ("Work on the next steps from the previous sessions first"), we audited the top carried-over technical items in `docs/NEXT_STEPS.md`:
1. **`LISTRIC` (`2026-10-26`) Untried Queue #1 — `TENSOR-RIEDEL` ($15^\circ\text{–}25^\circ$ En-Échelon Riedel Obliquity + Gravity Gradient Tensor Dimensionality):** Ranked #2 across five prior pre-registrations (`KNICKLOQO`, `LISTRICDIP`, `RADIODECOUPLE`, `CURIEDEMAG`, `LISTRIC`) and moved to **#1 untried in-cache hypothesis** after `LISTRIC` was executed in PR #100.
2. **`VENTSCARP` (`2026-10-25`) Next Step #1 + `LISTRICLAG` (`2026-10-25`) Next Step #1 — Slope-Regime Multi-Resolution Fusion + Additive Non-Diluted Secondary Tail (`37,654 @ 1.0 + tail`):**
   - `VENTSCARP` E3 proved that *fixed-L1 peak dilution* (`47,000` peaks summing to `37,654`, scaling top peaks `< 1.0`) significantly hurts DTI (`-0.005193`).
   - `LISTRICLAG` E3 proved that *keeping top `37,654` peaks at full `1.0`* while adding a secondary spaced tail (`@ 0.30`) lifts `HOLDOUT-DTI` by `+13.4%` paired — a direct consequence of the Möbius linearity of `vendor/gems57/metric.py::dti_exact` in $p(x) \in [0, 1]$.
3. **Line-by-Line Band Verification Discovery (`#IR-92-VENTSCARP-BAND-INDEX-MISATTRIBUTION`):** Direct GDAL metadata inspection of `.cache/gems_inputs/training_features.tif` (`19` bands) revealed that `gems/ventscarp.py` read `Band 3` (`tmi_hg`) under variable `b3_hf`, differentiated `Band 18` (`iso_grav_anom_hg`) as if it were scalar gravity `Band 13` (`iso_grav_anom`), and swapped variable names between `Band 4` (`geod_2ndinv`) and `Band 8` (`geod_dilaterate`). `RIEDELVENT` asserts exact GDAL `band_name` tags on file open and uses verified `Band 13` (`iso_grav_anom`), `Band 11` (`iso_grav_anom_vg`), `Band 18` (`iso_grav_anom_hg`), `Band 7` (`geod_shearrate`), `Band 8` (`geod_dilaterate`), and `Band 4` (`geod_2ndinv`).

---

## 2. Five Untried Candidate Geological Hypotheses (Ranked by Expected DTI Gain / Cost)

| Rank | Hypothesis ID | Specific Layer(s) Involved (Verified GDAL Tags) | Physical Signature Targeted | Why It Catches Catalogue-Missing Faults Rather Than Mapped Ones | Named Non-Fault Mimic(s) & Deconfounder | How It Differs From All Implemented Repo Lanes | Expected DTI Gain / Cost / Sandbox Viability |
|---:|---|---|---|---|---|---|---|
| **1 (Selected)** | **`RIEDELVENT`** (*Transtensional Riedel $R/R'$ Obliquity & 3D Gravity-Tensor Step-Over Valve + 3DEP-10m Scarp + INGENIOUS Hydrothermal Vents + Möbius Additive Tail*) | `training_features.tif` Bands `2` (`rtp`), `3` (`tmi_hg`), `4` (`geod_2ndinv`), `5` (`iso_grav_anom_slope`), `7` (`geod_shearrate`), `8` (`geod_dilaterate`), `11` (`iso_grav_anom_vg`), `12` (`det_elev`), `13` (`iso_grav_anom`), `15` (`depth_to_base_surf`), `17` (`cond_surf`), `18` (`iso_grav_anom_hg`), `19` (`det_elev_slope`); USGS 3DEP `10 m` `topo_10m_derived_100m_u8.tif` + `dem10_chi_100m_i16.tif`; GeoDAWN `geodawn_rad_u8.tif` + `geodawn_extensions_u8.tif`; DOE GDR `#1391` Tufa-filtered `Paleo_geothermal_final.csv`, `2m_temperature_probe`, `gdr_wellspring` | (1) 2D horizontal gravity gradient tensor $\mathbf{G}_h = \nabla_h \nabla_h g_{\text{iso}}$ 3D step-over invariant $I_{\text{3D}} = \frac{4|\lambda_1\lambda_2|}{\lambda_1^2+\lambda_2^2+\varepsilon} R(\|\mathbf{G}_{\text{AS}}\|)$ (Pedersen & Rasmussen, 1990); (2) synthetic Riedel $R$-shear ($15^\circ\text{–}25^\circ$, $\mu_R=20^\circ$) & antithetic $R'$-shear ($65^\circ\text{–}80^\circ$, $\mu_{R'}=72^\circ$) strike obliquity between `3DEP 10 m` scarp strike and basement gravity/RTP strike (Tchalenko, 1970), gated by geodetic shear $\times$ dilatation (`B7, B8`); (3) `10 m` sub-pixel piedmont scarp + fluvial $\chi$/thalweg knickzones + Tufa-filtered hydrothermal sinter/probe fault-valves; (4) Möbius-DTI additive secondary tail (`37,654 @ 1.0 + 47,346 @ [0.30, 0.60]`) | USGS/NBMG airphoto/LiDAR compilations map `~97%` of continuous $0^\circ$-collinear range fronts, whereas `~76%` of blind Great Basin geothermal systems sit in **en-échelon Riedel step-overs, horse-tail terminations, and conjugate relay breaches** (Faulds & Hinz, 2015) where short cover splays rotate $15^\circ\text{–}25^\circ$ or $72^\circ$ off the buried basement step and express only as `15–35 m` degraded fan scarps (`10 m` DEM) and localized silica/thermal anomalies | (a) Longitudinal/barchanoid eolian sand dunes oblique to basin margins (suppressed via `10 m` fluvial $\chi$/$k_{sn}$ incision & elevation-step monotonicity); (b) Pleistocene Lake Lahontan shoreline bars (`1,330 m` AMSL) & lacustrine tufa mounds (`86` Tufa sites excluded + contour-parallel null); (c) tilted volcanic cuesta hogbacks | Every prior multi-physics lane (`XPHASE`, `COULOMBLOQO`, `KNICKLOQO`, `POISSONKNICK`, `EULERFUSE`, `PROVINCETOE`, `LISTRIC`) rewarded $0^\circ$ collinearity ($\cos 2\Delta\theta$) on `100 m` grids only; `VENTSCARP` lacked Riedel obliquity, gravity-tensor 3D invariants, true `B13`/`B11`/`B7` coupling, `100 m` thalweg concavity, and non-diluted additive tail | **Highest expected gain** (targets both `>0.0109` static & `>0.1122` Rule-2 + clears `62GEMSDOE` `<= 0.70`) / Moderate cost (~18 min CPU) / **100% Viable** (all inputs SHA-256-verified on disk) |
| **2** | **`ELASTIC-FLEXURE-WAVELENGTH`** (*Broken-Plate Lithospheric Flexural Admittance Residual, Buck 1988*) | `training_features.tif` Bands `12` (`det_elev`), `13` (`iso_grav_anom`), `15` (`depth_to_base_surf`), `18` (`iso_grav_anom_hg`) | 2D radial FFT flexural transfer admittance residual $\Delta g_{\text{flex}}(k) = \hat{g}_{\text{iso}}(k) - Z_{\text{plate}}(k; T_e)\hat{h}(k)$ for effective elastic thickness $T_e \in [2, 5]\text{ km}$ ($\alpha_{\text{flex}} \in [6, 14]\text{ km}$) isolating broken-plate footwall rebound / hanging-wall rollover hinges | Master detachments buried under `300–1,200 m` of Plio-Quaternary valley fill lack sharp `100 m` scarps and express regionally as `8–15 km` flexural monoclines | Caldera resurgence domes, differential compaction sags over unfaulted paleo-channels | `POISSONFLEX` and `flexure_knick_province.py` used local `100–600 m` Gaussian Laplacians, never `6–14 km` wavenumber flexural admittance | **Moderate** (`6–14 km` hinges require sub-pixel scarp coupling to localize within `300 m` DTI cone) / Low–Moderate cost / **100% Viable** (in-cache) |
| **3** | **`GAMMA-ALTERATION-REDOX-HALO`** (*Concentric Adularia-`K/Th` Core vs Oxidized `U/Th` Flank Across MT Clay-Cap Perimeters*) | `geodawn_rad_u8.tif` (`K, Th, U`), `geodawn_extensions_u8.tif` (`ThK, UK, UTh, TMI_up150`), `training_features.tif` Bands `2` (`rtp`), `17` (`cond_surf`) | Signed annular radial difference `[K/Th(r < 300 m) - K/Th(300–900 m)] x [U/Th(300–900 m) - U/Th(r < 300 m)]` straddling steep `Band 17` MT smectite clay-cap flanks and RTP demagnetization troughs (Hedenquist et al., 2000) | Boiling hydrothermal upflow argillicizes and bleaches fault rock, destroying mechanical scarp relief so airphoto mappers miss altered fault traces | High-silica peralkaline rhyolite ash-flow tuffs with primary magmatic K/U enrichment; closed-basin playa uranyl evaporite sinks | `RADIOCONTACT` (`0.005066`) and `RADIODECOUPLE` (`0.053167`) used co-located first-order gradients, never concentric core-to-flank chemical redox zoning | **Low–Moderate** (gamma-ray depth `~30–50 cm` is masked by thick Holocene eolian/playa cover) / Low cost / **100% Viable** (in-cache) |
| **4** | **`SENTINEL1-INSAR-CREEP-DECONFOUND`** (*Pumping-Deconfounded Interseismic InSAR Velocity Gradient + Dense MIDAS GPS Strain*) | External NASA ASF DAAC / JPL ARIA Sentinel-1 GUNW LOS velocity frames (`~90 m`) + UNR NGL MIDAS GPS station velocities + NDWR pumping well logs | `90 m` spatial phase-gradient shear steps across interseismic creeping faults after subtracting circular poroelastic groundwater-pumping subsidence bowls | Actively creeping blind transtensional strands in Walker Lane / CNSB accumulate strain across unmapped basin floors without Holocene surface rupture | Agricultural groundwater pumping subsidence cones (Mason, Smith, Diamond Valleys); playa evaporite seasonal heave | `Bands 4, 7, 8` interpolate sparse GPS at `>20 km` smoothing and cannot resolve individual `100 m` fault traces; no repo lane uses InSAR | **High potential if staged**, High cost / **NOT VIABLE IN SANDBOX** (`asf.alaska.edu`, `aria-share.jpl.nasa.gov`, `geodesy.unr.edu` blocked by GitHub/PyPI-only egress policy) |
| **5** | **`NSL-RELOCATED-HYPOCENTER-UPDIP`** (*3D Double-Difference Microseismic Fault-Plane RANSAC Up-Dip Projection*) | External USGS ANSS ComCat (`earthquake.usgs.gov`) + UNR Nevada Seismological Laboratory waveform-relocated hypocenter catalog $(x, y, z, M)$ | 3D planar cluster RANSAC fit at `3–12 km` depth projected up-dip $(x_0 + z_0 \cot\delta \cos\psi, y_0 + z_0 \cot\delta \sin\psi)$ to `EPSG:32611` surface trace | Blind seismogenic faults accommodate `M 0.5–3.5` fracture swarms at depth without breaking Quaternary alluvium (`39%` blind Great Basin systems) | Magmatic dike swarms, geothermal injection-induced cloud seismicity (Dixie Valley / Brady's wellfields) | `Band 10` (`deq`) / `Band 16` (`ieq`) / `MICROSWARM` (`0.000000`) had scalar epicentral density with zero hypocentral depth $z_0$ or dip projection | **Moderate–High potential if staged** / **NOT VIABLE IN SANDBOX** (`earthquake.usgs.gov` unreachable under sandbox network allowlist) |

---

## 3. Exact Mathematical Specification of Rank-1 `RIEDELVENT` (Locked Pre-Execution)

### 3.1 Gravity Gradient Tensor & Riedel Obliquity Equations (`gems/riedelvent.py`)

1. **Horizontal Gravity Gradient Tensor & 3D Step-Over Singularity (`Band 13` `iso_grav_anom`, `Band 11` `iso_grav_anom_vg`):**
   Smooth `Band 13` ($g$) at $\sigma_g = 2.2\text{ px}$ ($220\text{ m}$) inside `valid` and form the symmetric 2D Hessian / horizontal gravity gradient tensor:
   $$\mathbf{G}_h(x) = \begin{pmatrix} g_{xx} & g_{xy} \\ g_{xy} & g_{yy} \end{pmatrix}, \qquad \lambda_{1,2} = \frac{g_{xx} + g_{yy}}{2} \pm \sqrt{\left(\frac{g_{xx} - g_{yy}}{2}\right)^2 + g_{xy}^2}.$$
   Let $\|\mathbf{G}_{\text{AS}}\| = \sqrt{g_{xx}^2 + 2g_{xy}^2 + g_{yy}^2 + g_{zz}^2}$ using `Band 11` ($g_{zz}$). Following Pedersen & Rasmussen (1990), define the scale-free **3D Step-Over / Accommodation Tensor Invariant**:
   $$I_{\text{3D}}(x) = \frac{4\,|\lambda_1(x)\,\lambda_2(x)|}{\lambda_1(x)^2 + \lambda_2(x)^2 + \varepsilon} \cdot R_{\Omega}\!\left(\|\mathbf{G}_{\text{AS}}(x)\|\right) \in [0, 1],$$
   which vanishes ($I_{\text{3D}} \to 0$) on infinite 2D planar range-front steps ($\lambda_2 \to 0$) and peaks ($I_{\text{3D}} \to 1$) at 3D relay-ramp breaches, fault terminations, and intersections.

2. **En-Échelon Riedel $R$ ($20^\circ$) & Conjugate $R'$ ($72^\circ$) Surface-to-Basement Strike Obliquity:**
   Let $\mathbf{g}_{\text{surf}} = \nabla_{\sigma=1.2}\bigl(0.65\,S_{10\text{m},p90} + 0.35\,\log(1 + S_{100\text{m}})\bigr)$ define local near-surface scarp normal azimuth $\psi_{\text{surf}}$ (strike $\theta_{\text{surf}} = \psi_{\text{surf}} + 90^\circ$), and let $\mathbf{g}_{\text{base}}$ from smoothed `Band 13` gravity + `Band 2` RTP define basement step normal azimuth $\psi_{\text{base}}$ (strike $\theta_{\text{base}} = \psi_{\text{base}} + 90^\circ$). The acute axial strike difference is:
   $$\Delta\theta(x) = \arccos\!\Bigl(\mathrm{clip}\bigl(|\cos(\theta_{\text{surf}}(x) - \theta_{\text{base}}(x))|,\, 0,\, 1\bigr)\Bigr) \in [0^\circ, 90^\circ].$$
   With edge-strength product $M_{\text{sb}}(x) = \sqrt{R_{\Omega}(\|\mathbf{g}_{\text{surf}}\|)\, R_{\Omega}(\|\mathbf{g}_{\text{base}}\|)}$:
   - **Synthetic Riedel $R$/$P$ Splay Coupling ($\mu_R = 20^\circ, \sigma_R = 8.5^\circ$):**
     $$\mathcal{R}_{\text{syn}}(x) = \exp\!\left(-\frac{(\Delta\theta(x) - 20^\circ)^2}{2 \cdot 8.5^2}\right) M_{\text{sb}}(x).$$
   - **Antithetic Conjugate $R'$ Cross-Relay Coupling ($\mu_{R'} = 72^\circ, \sigma_{R'} = 9.5^\circ$):**
     $$\mathcal{R}_{\text{conj}}(x) = \exp\!\left(-\frac{(\Delta\theta(x) - 72^\circ)^2}{2 \cdot 9.5^2}\right) M_{\text{sb}}(x).$$
   - **Pure Oblique Splay Excess over $0^\circ$ Range-Front Collinearity:**
     $$\mathcal{R}_{\text{excess}}(x) = \max\!\left(0,\, \max(\mathcal{R}_{\text{syn}}, \mathcal{R}_{\text{conj}}) - \exp\!\left(-\frac{\Delta\theta(x)^2}{2 \cdot 8.5^2}\right) M_{\text{sb}}(x)\right).$$
   - **Geodetic Transtensional Fault-Valve Pump (`Band 7` `geod_shearrate`, `Band 8` `geod_dilaterate`):**
     $$\mathcal{P}_{\text{trans}}(x) = \bigl(0.55\,\mathcal{R}_{\text{syn}}(x) + 0.25\,\mathcal{R}_{\text{conj}}(x) + 0.20\,I_{\text{3D}}(x)\bigr) \cdot \sigma_+\!\bigl(z_{45}(\text{Band 7})\bigr) \cdot \bigl(0.5 + 0.5\,\sigma_+\!(z_{45}(\text{Band 8}))\bigr).$$

### 3.2 Möbius-Linear DTI Additive Tail Theorem (Motivation for Pre-Registered Arm 3)

In `vendor/gems57/metric.py::dti_exact` ($\alpha = 0.2, \beta = 0.8$, $1 - \beta = 0.2 = \alpha$), for any candidate prediction $p \in [0, 1]^\Omega$:
$$\mathrm{DTI}(p, G) = \frac{T(p)}{T(p) + 0.2\,F(p) + 0.8(|G| - T(p))} = \frac{T(p)}{0.2\,T(p) + 0.2\,F(p) + 0.8\,|G|}.$$
Adding a single spaced (`>= 3.0 px`) crest pixel $x$ with weight $w \in (0, 1]$ yields $\Delta T = w\,c_T(x)$ and $\Delta F = w(1 - q(x))$, giving the Möbius function:
$$f(w) = \frac{T_0 + w\,c_T(x)}{D_0 + 0.2\,w\bigl(c_T(x) + 1 - q(x)\bigr)}, \qquad f'(w) = \frac{c_T(x)\,D_0 - 0.2\bigl(c_T(x) + 1 - q(x)\bigr)T_0}{\bigl[D_0 + 0.2\,w(c_T(x) + 1 - q(x))\bigr]^2}.$$
Because the numerator of $f'(w)$ is independent of $w$, **$f(w)$ is strictly monotone increasing on $[0, 1]$ whenever $E[c_T(x)] > \frac{0.2\,\mathrm{DTI}}{1 - 0.2\,\mathrm{DTI}}(1 - E[q(x)])$**. Thus:
1. Primary crests (`1..37,654`) must remain at **$w = 1.0$** (never diluted as in `VENTSCARP` E3).
2. Secondary spaced crests (`37,655..85,000`) with moderate posterior confidence should be **added** with monotone confidence weights $w_k \in [0.30, 0.60]$ rather than truncated to `0.0`!

---

## 4. Three Pre-Registered Experimental Arms (Hard Cap = 3)

All three arms use zero fault-catalogue features, `4`-quadrant Leave-One-Quadrant-Out (`LOQO`, `>= 1.2 km` guard band, `> 500 m` negative buffer) `HistGradientBoostingClassifier` ensembles with label-free within-quadrant quantile calibration (`calib_weight = 0.80`, `power_gamma = 3.2`), strict `d_cat > 2.0 px` exclusion (`d_visible > 2.0 px` on draw-blind holdout), `float32` in `[0.0, 1.0]`, and `0.0` outside the footprint:

1. **Arm 1 — `riedelvent_bin37k` (Primary Binary `37,654`-Dot Benchmark):**
   - Full `32`-feature `RIEDELVENT` 4-branch LOQO ensemble (`20%` Full + `30%` Province-Debiased + `30%` Riedel-Subsurface-Knick + `20%` Hydrothermal-10mScarp) sharpened onto 1D Riedel + `10 m` piedmont scarp + fluvial $\chi$/thalweg-knick + subsurface crests (`min_dist = 3.2 px`, `37,654` binary unit dots).
2. **Arm 2 — `collinear_novent_bin37k` (Causal Mechanism Ablation, `37,654` Binary Dots):**
   - Drops all `6` Group-B `TENSOR-RIEDEL` features AND all `8` Group-C INGENIOUS hydrothermal vent / alteration features (leaving `18` collinear `10 m` + `100 m` topographic/geophysical/knickzone features) and replaces the Riedel + hydrothermal crest channels with $0^\circ$-collinear scarp + gravity crests at identical `37,654` binary unit-dot budget (`min_dist = 3.2 px`). Directly isolates the causal gain of Riedel transtensional obliquity + hydrothermal fault-valve vents.
3. **Arm 3 — `riedelvent_tail85k` (Möbius-DTI Additive Tail, `85,000` Spaced Crests):**
   - Uses the identical `RIEDELVENT` continuous crest surface from Arm 1 (`min_dist = 3.0 px`, `85,000` spaced 1D crests): ranks `1..37,654` emitted at exact `1.000`, and secondary ranks `37,655..85,000` (`47,346` crests) emitted with a deterministic linear confidence ramp from `0.60` down to `0.30` (`L1` total mass `= 37,654 + 47,346 * 0.45 = 58,959.7`).

---

## 5. Falsifiers & Fail-Closed Governance Rules

1. **Leakage Canary Gate (Rule 4):** Every raw band and every one of the `32` `RIEDELVENT` features must satisfy symmetric holdout ROC AUC $\max(\mathrm{AUC}, 1 - \mathrm{AUC}) \le 0.90$ before trusting any model output.
2. **Pre-Placement & Post-Placement Uniqueness Gate (Rule 1):** Both continuous pre-placement surfaces and final emitted rasters must satisfy $|\rho_{\text{Spearman}}| \le 0.90$ and `3 px` forward overlap $\le 0.70$ across all local `GEMSDOE92` rasters AND across all `102` public `GEMSDOE*` repositories under `dual_reading_decision` (`<= 150,000`-px dot fields literally, `> 150,000`-px continuous surfaces on matched-budget top-`k`).
3. **Literal Dense-Witness Fail-Closed Rule:** Because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` sets all `5,167,373` footprint pixels `> 0`, literal unweighted forward overlap is `1.000 > 0.70` for every non-empty raster. All outputs will therefore carry `submission_eligible: false` and `verdict: "negative"` (**OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT WITHOUT HUMAN SELECTOR POLICY DECISION**), spending **`0` weekly DrivenData slots**.

## 6. Official Verified Sources for Manual Review

- DrivenData Competition #306 Problem Description & DTI Metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- DrivenData Competition #306 Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official Prize Rules PDF (NREL/DOE): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Official Reference U-Net Solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN Airborne Magnetic & Radiometric Survey: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and · https://doi.org/10.5066/P93LGLVQ
- USGS 3D Elevation Program (`1/3`-arc-second `~10 m` DEM): https://www.usgs.gov/3d-elevation-program
- DOE Geothermal Data Repository `#1391` (GBCGE/UNR INGENIOUS Regional Dataset, CC BY 4.0): https://gdr.openei.org/submissions/1391
- Great Basin Center for Geothermal Energy INGENIOUS Project: https://gbcge.org/current-projects/ingenious/
- EPSG:32611 (`WGS 84 / UTM zone 11N`): https://epsg.io/32611
- Tversky Index: https://en.wikipedia.org/wiki/Tversky_index
- Tchalenko, J. S. (1970), *Similarities between shear zones of different magnitudes*, GSA Bulletin 81(6), 1625–1640.
- Pedersen, L. B., & Rasmussen, T. M. (1990), *The gradient tensor of potential field anomalies*, Geophysics 55(12), 1558–1566.
- Faulds, J. E., & Hinz, N. H. (2015), *Favorable tectonic and structural settings of geothermal systems in the Great Basin region, western USA*, Proc. World Geothermal Congress: https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
