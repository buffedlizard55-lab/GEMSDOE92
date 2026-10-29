# Pre-Registered Untried Geological Hypotheses — 2026-10-29 (`MARUSSI-TRISHEAR` & `WALKER-LANE-VORTICITY`)

- **Pre-registered UTC:** `2026-10-29T15:10:00Z` (**strictly BEFORE** implementing `gems/marussi_trishear.py` or running any holdout/placement experiment)
- **Branch:** `arena/67c0d7b6-gemsdoe92`
- **Novelty verification:** Audited all `60` prior `docs/HYPOTHESES*.md` memos and all `59` `gems/*.py` modules (`0` prior matches for `Marussi`, `Bevis`, `Pedersen-Rasmussen`, `trishear`, `Allmendinger`, `fault-propagation monocline`, `Cooper terracing`, `Niblett-Bostick`, `MT skin depth`, `Caldwell phase tensor`, `Helmholtz-Hodge kinematic vorticity`, and `0` code implementations of `Gallardo-Meju cross-gradient`).
- **Pre-implementation data-hygiene gates enforced across all hypotheses:**
  1. **Finite float32 sentinel masking:** Every band of `training_features.tif` (`3,730 × 3,292`, `EPSG:32611`) carries `3,061–3,073` finite `-3.4028235e+38` sentinel pixels inside the valid footprint (`5,167,373` px). Every raw band is masked on `(~np.isfinite(x)) | (np.abs(x) > 1e20)` and nearest-neighbor EDT-continued **before** any FFT, Hilbert/Riesz, or spatial-derivative operator so edge bells never ring across footprint collars.
  2. **Band 6 (`tc`) identity lock:** `Band 6` of `training_features.tif` (`min = -10.89`, `max = 186.10`, `p99 = 35.42`, metadata description `"tc - Tilt angle or total curvature"`) is empirically **airborne gamma-ray Radiometric Total Count / unnormalized values**, **not** bounded $[-\pi/2, \pi/2]$ Miller-Singh magnetic tilt (`IR-1028B-3`). True Miller-Singh magnetic tilt $\theta_{\text{mag}} = \arctan(\partial_z M_{\text{RTP}} / [\|\nabla_h M_{\text{RTP}}\| + \varepsilon])$ is computed strictly from `Band 02` (`rtp`, Reduced-to-Pole magnetic anomaly) and cross-checked against `Band 09` (`tmi_vg`) / `Band 03` (`tmi_hg`).
  3. **Leakage-canary lock (`AUC <= 0.90`):** `dist_known_fault_px` and `thermalclass` in `gdr_wellspring_in_footprint.csv` are stripped by name (`LEAKY_COLUMNS`) and never loaded. Every engineered feature is tested solo on `gems57-pooled-hide-v2` (`22,663` withheld positives across `8` spatial fold-draws); any feature with symmetric solo `AUC > 0.90` fails closed before model training.
  4. **Zero `cons_2d` holdout contamination:** Unlike `rieszlbm2` (`HOLDOUT-DTI = 0.03799`), holdout scoring uses **strictly** zero-catalogue geophysical operators plus self-excluded `fold["visible"]` structural geometry (`gems/faultnet.py` / `gems/tipcomp.py`), never a static fleet consensus raster that masks the full `existing_faults.tif`.

---

## Hypothesis 1 (`H-92M1`, Rank #1 — SELECTED PRIMARY): **3D Laplace-Consistent Marussi Gravity Tensor 2D-Dimensionality + Allmendinger Trishear Blind-Tip Monocline + Gallardo-Meju Cross-Gradient (`MARUSSI-TRISHEAR`)**

### 1. Specific layers involved (all SHA-256-pinned in `.cache/gems_inputs/`, exact `(3730, 3292)` `EPSG:32611` grid)
- **Gravity field triad (`training_features.tif`):** `Band 13` (`iso_grav_anom`, Isostatic Gravity Anomaly $g_z$), `Band 11` (`iso_grav_anom_vg`, measured $T_{zz}$), `Band 18` (`iso_grav_anom_hg`, measured $\|(T_{xz}, T_{yz})\|$).
- **Aeromagnetic field (`training_features.tif` + `geodawn_extensions_u8.tif`):** `Band 02` (`rtp`, Reduced-to-Pole magnetic anomaly), `Band 03` (`tmi_hg`), `Band 09` (`tmi_vg`), `geodawn Band 04` (`TMI_up150`).
- **Subsurface electrical conductivity (`training_features.tif`):** `Band 17` (`cond_surf`, subsurface electrical conductivity $\sigma$), transformed to **Niblett-Bostick electromagnetic skin-depth contrast** $\delta_{\text{MT}} \propto 1/\sqrt{\sigma + \varepsilon}$ and horizontal log-admittance gradient $\|\nabla_h \ln(\sigma + \varepsilon)\|$.
- **Basin cover & 10 m surface curvature (`training_features.tif` + `topo_10m_derived_100m_u8.tif`):** `Band 15` (`depth_to_base_surf`, sedimentary cover thickness $h_{\text{sed}}$), `Band 12` (`det_elev`), `Band 19` (`det_elev_slope`), `topo10 Band 02` (`slope_max`), `topo10 Band 06` (`curv_prof_absmax`), `topo10 Band 07` (`aspect_coherence`), `topo10 Band 09` (`dem_mean`).
- **Radiometric potassium/thorium alteration (`training_features.tif` + `geodawn_extensions_u8.tif`):** `Band 06` (`tc`), `geodawn Band 01` (`ThK`), `geodawn Band 02` (`UK`), `geodawn Band 03` (`UTh`).

### 2. Physical signature & mathematical transform
1. **Full 3D Laplace-consistent Marussi potential-field tensor (`Pedersen & Rasmussen 1990`, *Geophysics* 55:1558; `Bevis & Pedersen 2014`, *J. Geodesy*):**
   Outside density sources, the gravitational disturbance potential $U$ satisfies $\nabla^2 U = 0$, so in 2D wavenumber space $\mathbf{k} = (k_x, k_y)$ with $k = \|\mathbf{k}\|$:
   $$\widehat{T}_{xx} = -\frac{k_x^2}{k}\widehat{g}_z, \quad \widehat{T}_{yy} = -\frac{k_y^2}{k}\widehat{g}_z, \quad \widehat{T}_{xy} = -\frac{k_x k_y}{k}\widehat{g}_z, \quad \widehat{T}_{xz} = i k_x \widehat{g}_z, \quad \widehat{T}_{yz} = i k_y \widehat{g}_z, \quad \widehat{T}_{zz} = k \widehat{g}_z$$
   (band-limited with radial cosine taper $\lambda \in [600\text{ m}, 25\text{ km}]$ so 100 m gridding noise is suppressed while basement steps at $0.3\text{–}4\text{ km}$ depth are preserved). From the symmetric $3\times 3$ Marussi tensor $\mathbf{T}(\mathbf{x})$ with trace $T_{xx}+T_{yy}+T_{zz}=0$, we compute the rotational invariants:
   $$I_1 = T_{xx}T_{yy} + T_{yy}T_{zz} + T_{zz}T_{xx} - T_{xy}^2 - T_{xz}^2 - T_{yz}^2 \le 0, \qquad I_2 = \det(\mathbf{T})$$
   and the **Pedersen-Rasmussen dimensionality index**:
   $$D_{2\text{D}}(\mathbf{x}) = 1 - \frac{|I_2(\mathbf{x})|}{2\left(-I_1(\mathbf{x})/3 + \varepsilon\right)^{3/2}} \in [0, 1].$$
   - Over an **elongate planar fault step / intrabasin horst boundary** ($\partial_s \to 0$ along strike), $\mathbf{T}$ has one zero eigenvalue ($\det \mathbf{T} = 0$), so **$D_{2\text{D}} \to 1$**!
   - Over a **3D equant pluton, caldera plug, or circular alluvial sub-basin**, $|I_2|$ attains its maximum $2(-I_1/3)^{3/2}$, so **$D_{2\text{D}} \to 0$**!
2. **Allmendinger (1998, *Tectonics* 17:640) Trishear Blind-Fault-Propagation Monocline Operator:**
   A blind normal or transtensional fault whose upper tip arrests at depth $z_{\text{tip}}$ beneath unconsolidated Plio-Quaternary valley fill ($h_{\text{sed}} > 120\text{ m}$, `Band 15`) does **not** break the surface as a sharp rupture scarp; instead it deforms the overlying wedge into an **asymmetric broad monocline** ($\lambda \approx 0.6\text{–}2.4\text{ km}$, subtle slope inflection $\nabla^2 h_{\text{DEM}}$) directly updip (toward the footwall at $55^\circ\text{–}65^\circ$ dip, horizontal offset $z_{\text{tip}}/\tan 60^\circ \approx 200\text{–}900\text{ m}$) of a sharp **Marussi basement step** ($D_{2\text{D}} \cdot \|(T_{xz}, T_{yz})\|$) and **Cooper & Cowan (2006) potential-field terracing inflection**. Coupling the deep 2D Marussi step with the updip long-wavelength monocline inflection over thick cover ($h_{\text{sed}} > 120\text{ m}$) isolates active blind growth faults!
3. **Gallardo & Meju (2003, *GRL* 30:1658) Joint Gravity–Magnetic Cross-Gradient + Demagnetized Alteration Trough:**
   $$\boldsymbol{\tau}_{gm}(\mathbf{x}) = \nabla_h g_{\text{CBA}} \times \nabla_h M_{\text{RTP}}, \qquad C_{\parallel}(\mathbf{x}) = \frac{|\nabla_h g_{\text{CBA}} \cdot \nabla_h M_{\text{RTP}}|}{\|\nabla_h g_{\text{CBA}}\|\,\|\nabla_h M_{\text{RTP}}\| + \varepsilon}$$
   Normal lithological/fault contacts juxtapose both density and magnetization along the same strike ($\boldsymbol{\tau}_{gm} \to 0, C_{\parallel} \to 1$), **except** where upwelling $150\text{–}250^\circ\text{C}$ geothermal fluids alter titanomagnetite to pyrite/hematite/illite along the fault damage zone — producing a **high-2D-gravity Marussi step ($D_{2\text{D}} \to 1$) coincident with a local RTP magnetic susceptibility trough and Niblett-Bostick MT skin-depth gradient**!
4. **True Salem et al. (2008, *Leading Edge* 27:96) Suspended Tilt-Depth Estimate (`B02` RTP, fixing `IR-1028B-3`):**
   Using true magnetic tilt $\theta_{\text{mag}}$ computed from `B02` RTP (not `B06` radiometric `tc`), contact depth $z_c \approx 1 / \|\nabla_h \theta_{\text{mag}}\|_{|\theta_{\text{mag}}| < \pi/6}$ separates shallow volcanic flow edges ($z_c < 150\text{ m}$) from basement-rooted geothermal conduits ($250\text{ m} \le z_c \le 2500\text{ m}$).

### 3. Why `H-92M1` catches faults missing from USGS QFF / INGENIOUS
USGS Quaternary Fault and Fold mapping relies on subaerial LiDAR/airphoto scarps and trenching; across Humboldt/Churchill/Pershing/Lander valleys (Dixie Valley, Carson Sink, Buena Vista, Grass Valley, Granite Springs, Gabbs), Lake Lahontan shoreline reworking (`< 15.5 ka`) and rapid playa aggradation erase subaerial scarps while blind tips propagate as **trishear monoclines** above buried basement steps (`Faulds & Hinz 2015`, World Geothermal Congress — **~39–45% of Great Basin geothermal systems are blind**, having neither hot springs nor mapped surface Quaternary scarps!).

### 4. Named non-fault mimic process & anti-mimic gate
- **Primary non-fault mimics:** (a) **Subaerial canyon/escarpment rims and basalt mesa edges** (`slope > 8^\circ`, shallow Salem depth $z_c < 150\text{ m}$, thin sediment cover $h_{\text{sed}} < 30\text{ m}$), and (b) **3D circular plutons / caldera ring plugs** (high $\|\nabla g\|$ yet equant 3D geometry $D_{2\text{D}} \to 0$).
- **Anti-mimic suppressors:** Multiply by $D_{2\text{D}}$ (kills 3D plutons/plugs) and penalize steep subaerial bedrock scarps (`slope` $\times$ low `depth_to_basement`).

### 5. Differentiation from existing repo work
- `gems/riesz_locked.py` used 2D image-space Riesz monogenic phase congruency on `B02`/`B13` **and** accidentally treated `Band 6 tc` as magnetic tilt (`IR-1028B-3`), without Laplace vertical components ($T_{xz}, T_{yz}, T_{zz}$), without 3D invariant $D_{2\text{D}} = 1 - |I_2|/[2(-I_1/3)^{3/2}]$, without trishear monocline dip-offset coupling, and without Gallardo-Meju cross-gradient.
- `gems/tipcomp.py`, `gems/listric.py`, and `gems/faultnet.py` extrapolate known `existing_faults.tif` tips; `H-92M1` extracts **zero-catalogue 3D potential-field + trishear structural crests** across blind basins first, then fuses with self-excluded fold-visible fault geometry in `E2`.

---

## Hypothesis 2 (`H-92M2`, Rank #2 — CO-TESTED IN `E2`): **Helmholtz-Hodge Geodetic Velocity Decomposition & Walker Lane Kinematic Vorticity Strike-Partitioning (`WALKER-LANE-VORTICITY`)**

### 1. Specific layers involved
- **Geodetic strain & shear (`training_features.tif`):** `Band 07` (`geodetic_strain_rate`, principal/dilatational extension rate $\dot{\varepsilon}$), `Band 08` (`geodetic_shear_rate`, engineering shear rate $\dot{\gamma}$).
- **Structural orientation fields:** Marussi principal horizontal strike $\psi_T(\mathbf{x}) = \frac{1}{2}\arctan2(2 T_{xy}, T_{xx}-T_{yy}) + \frac{\pi}{2}$ (zero-catalogue strike!) and self-excluded fold-visible fault tangent $\psi_{\text{vis}}(\mathbf{x})$ (`gems/faultnet.py`).

### 2. Physical signature & mathematical transform
In the western-to-central Great Basin (exactly our EPSG:32611 footprint spanning the **Walker Lane–Central Nevada Seismic Belt transition** into the central Basin and Range; `Hammond, Blewitt & Kreemer 2011`, *JGR* 116:B04402; `Faulds et al. 2006`, *GSA Special Paper* 400):
- Pure Basin-and-Range dip-slip extension ($\dot{\varepsilon}$ high, $\dot{\gamma}$ low) reactivates **N015°E–N035°E** range-front normal faults.
- Transtensional Walker Lane / accommodation-zone shear ($\dot{\gamma}$ high relative to $\dot{\varepsilon}$) partitions slip onto **N315°W dextral strike-slip faults** and **N055°E–N075°E sinistral/normal step-over pull-aparts** (e.g., Carson Sink, Humboldt structural zone, Dixie-Fairview accommodation belt)!
We compute the **Truesdell dimensionless kinematic vorticity proxy**:
$$W_k(\mathbf{x}) = \frac{|\dot{\gamma}(\mathbf{x})|}{\sqrt{\dot{\gamma}(\mathbf{x})^2 + \dot{\varepsilon}(\mathbf{x})^2 + \varepsilon^2}} \in [0, 1]$$
and weight candidate Marussi-Trishear fault crests by **regime-compatible strike alignment**:
$$S_{\text{vort}}(\psi, W_k) = (1 - W_k)\cos^2(\psi - 22^\circ) + W_k \max\bigl(\cos^2(\psi - 62^\circ),\; \cos^2(\psi - 142^\circ)\bigr)$$
together with spatial **shear-strain gradient** $\|\nabla_h \dot{\gamma}\|$ at block boundaries.

### 3. Why `H-92M2` catches faults missing from USGS QFF / INGENIOUS
Oblique ENE accommodation faults and short pull-apart transfer relays inside transtensional step-overs (`W_k > 0.65`) accommodate small vertical throw per earthquake (hence no prominent range-front scarp in USGS QFF!), yet maintain **critically stressed tensile fracture permeability** hosting major Great Basin geothermal fields (Bradys, Desert Peak, Salt Wells, Soda Lake, Humboldt House; `Faulds & Hinz 2015`).

### 4. Named non-fault mimic process
- **Mimic:** Long-wavelength GPS station interpolation lobes ($\sim 15\text{–}30\text{ km}$) bleeding smoothly across unfaulted granitic range cores (`Band 15 depth_to_basement ~ 0`).
- **Suppressor:** Gate $S_{\text{vort}}$ strictly by high-wavenumber localized Marussi 2D structural steps ($D_{2\text{D}}$) so smooth GPS lobes cannot create false positives without a sharp subsurface discontinuity.

### 5. Differentiation from existing repo work
- Prior modules (`gems/slip_tendency.py`, `gems/coulomb.py`, `gems/strain_part.py`) assumed a **uniform** regional Basin-and-Range $\sigma_{\text{Hmax}}$ azimuth (`N015°E–N025°E`) or raw strain magnitude; none computed kinematic vorticity $W_k$ to **rotate** the favored structural strike from NNE dip-slip to ENE/NW Walker Lane pull-aparts.

---

## Hypothesis 3 (`H-92M3`, Rank #3 — EXTERNAL OFFICIAL DATA DESIGN, DOCUMENTED FOR UNRESTRICTED RUNNERS): **3D Magnetotelluric Phase-Tensor Skew $\beta_{\text{PT}}$ & Vertical Crustal Fluid-Conduit Plumes (`CALDWELL-MT-PHASE-TENSOR`)**

- **Specific layers & official free source:** USGS ScienceBase **USArray / Great Basin 3D Magnetotelluric Impedance & Resistivity Models** (`Bedrosian et al. / Peacock et al., USGS Data Releases on https://www.sciencebase.gov/catalog/`, public domain CC0 EDI/NetCDF impedance tensors $\mathbf{Z}(\omega)$ at $0.01\text{–}1000\text{ s}$), fused with in-repo `Band 17` (`mt_resistivity_2km`).
- **Physical transform (`Caldwell, Bibby & Brown 2004`, *Geophys. J. Int.* 158:457):** Galvanic distortion-free MT phase tensor $\boldsymbol{\Phi} = \mathbf{X}^{-1}\mathbf{Y}$ ($\mathbf{Z} = \mathbf{X} + i\mathbf{Y}$) yields coordinate-invariant 3D skew angle $\beta_{\text{PT}} = \frac{1}{2}\arctan\bigl((\Phi_{xy}-\Phi_{yx})/(\Phi_{xx}+\Phi_{yy})\bigr)$. Subvertical hydrothermal upflow zones along blind fault intersections produce $|\beta_{\text{PT}}| > 5^\circ$ beneath electrically conductive smectite clay caps (`1–5 km` skin depth) even where `mt_resistivity_2km` alone sees only a broad conductive playa.
- **Why missing from USGS QFF & non-fault mimic:** Conductive saline Lahontan playa clays (`Carson Sink / Humboldt Sink`) mimic geothermal clay caps in scalar 2 km resistivity (`Band 17`), whereas flat-lying 1D/2D playa brines have $|\beta_{\text{PT}}| \approx 0^\circ$!
- **Obtainability verification:** Public free USGS federal dataset (`sciencebase.gov`), **not reachable inside this sandbox's strict 6-host allowlist** (`github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`). Therefore we approximate the zero-distortion lateral admittance step via Niblett-Bostick skin-depth log-gradient minus playa topographic flatness (`tpi_2km`, `slope`) inside `H-92M1`, and preserve full 3D EDI phase-tensor ingestion for unrestricted hosts.

---

## Hypothesis 4 (`H-92M4`, Rank #4 — EXTERNAL OFFICIAL DATA DESIGN, DOCUMENTED FOR UNRESTRICTED RUNNERS): **OPERA/ARIA Sentinel-1 InSAR Seasonal Poroelastic Cross-Fault Phase-Gradient Step (`ARIA-INSAR-POROELASTIC-BARRIER`)**

- **Specific layers & official free source:** NASA/JPL OPERA Surface Displacement from Sentinel-1 (`OPERA_L3_DISP-S1_V1`, 30 m posting, 2016–2026 ascending + descending LOS time series, freely distributed by NASA Alaska Satellite Facility DAAC `https://asf.alaska.edu/datasets/daac/opera/` & Earthdata).
- **Physical transform (`Chaussard et al. 2014`, *RSE*; `Reinisch et al. 2020`, geothermal InSAR):** Unmapped blind Quaternary faults cemented by hydrothermal silica/calcite act as **impermeable cross-fault hydraulic baffles** inside alluvial aquifers. Decomposing seasonal (`1 yr` sinusoid) vertical poroelastic breathing amplitude $A_{\text{yr}}(\mathbf{x})$ and taking its directional horizontal gradient $\|\nabla_h A_{\text{yr}}\|$ isolates sharp `100 m`-wide hydraulic head steps across blind intrabasin faults where topography is dead flat (`slope < 0.3^\circ`).
- **Why missing from USGS QFF & non-fault mimic:** Zero topographic scarp across active agricultural/playa basins (`Fallon/Carson Sink`, `Lovelock`, `Dixie Valley`); mimic = agricultural well-field boundary or lithologic paleo-channel edge, suppressed by requiring linear strike persistence (`> 2.5 km`) and coincidence with Marussi $D_{2\text{D}}$ basement step.
- **Obtainability verification:** Official free US government product (`asf.alaska.edu`), blocked by sandbox egress allowlist (`6` hosts only) and NASA Earthdata bearer token policy; documented as Priority #1 external layer for unrestricted offline runners.

---

## Ranking & Pre-Registered Experimental Plan (`<= 3` Experiments, `<= 2` Hours)

| Rank | ID | Hypothesis | Expected `HOLDOUT-DTI` Gain | Compute / Impl Cost | In-Sandbox Obtainable? | Action in This Session |
|---:|:---|:---|:---|:---|:---|:---|
| **1** | **`H-92M1`** | **3D Laplace Marussi Tensor $D_{2\text{D}}$ + Allmendinger Trishear Blind Monocline + Gallardo-Meju Cross-Gradient + True `B02` Tilt-Depth** | **`+0.008` to `+0.020`** over pure-physics baselines; strong complementarity to `faultnet` | Low (~80s feature compute on `3991×2469` grid via vectorized numpy FFT) | **YES (100% SHA-256 verified `.cache/gems_inputs/`)** | **Execute (`E1`, `E2`, `E3`)** |
| **2** | **`H-92M2`** | **Walker Lane Geodetic Kinematic Vorticity $W_k$ Strike-Partitioning (`B07`, `B08`)** | **`+0.003` to `+0.008`** synergistic lift on ENE/NW step-over corridors | Very Low (~8s vectorized orientation coupling) | **YES (100% SHA-256 verified `.cache/gems_inputs/`)** | **Co-execute in `E1`/`E2`/`E3` (with ablation check)** |
| **3** | `H-92M3` | Caldwell 3D MT Phase-Tensor Skew $\beta_{\text{PT}}$ (`USGS ScienceBase`) | `+0.006` to `+0.015` in saline playa basins | Medium (~2 GB EDI/NetCDF ingest) | Blocked by 6-host sandbox allowlist (scalar Niblett-Bostick proxy included in `H-92M1`) | Documented + scalar skin-depth proxy tested |
| **4** | `H-92M4` | OPERA/ARIA Sentinel-1 Poroelastic Aquifer-Baffle Step (`NASA ASF`) | `+0.010` to `+0.025` inside flat Lahontan basins | High (~15 GB multi-frame NetCDF) | Blocked by 6-host sandbox allowlist | Documented for unrestricted runners |

### Pre-registered 3-Experiment Budget (`<= 3` runs total)
1. **Experiment `E1` (`MARUSSI-TRISHEAR-PURE-PHYS`):** Zero-catalogue 14-feature `H-92M1 + H-92M2` stack (`marussi_trishear.py`), solo-feature leakage canary check (`symmetric AUC <= 0.90` on every feature across all `22,663` withheld positives of `gems57-pooled-hide-v2`), 4-quadrant spatially-blocked LOQO logistic/ridge prospectivity + 1D directional non-maximum structural crest placement. Tests pure blind geophysical fault recovery with **zero** fault-catalogue geometry.
2. **Experiment `E2` (`MARUSSI-TRISHEAR-STRUCTURAL-FUSION`):** Spatially-blocked 4-fold LOQO fusion combining self-excluded `fold["visible"]` structural continuation (`gems/faultnet.py`, recomputed strictly per fold with zero withheld-fault leakage and zero `cons_2d` contamination) with `H-92M1 + H-92M2` Marussi-Trishear + Walker-Lane Vorticity features, tested head-to-head on `gems57-pooled-hide-v2` against **both** `parent_R0` (`0.097750`) **and** the matched `faultnet`-only ablation control (paired block/segment bootstrap 95% CI).
3. **Experiment `E3` (`MARUSSI-TRISHEAR-UNIQUE-PLACEMENT`):** Full-footprint deployment (`gemsdoe92-marussitrishear-...-zeros.tif`) using `vendor/gems57/submission_writer.py`, combining the `E2` physical-structural surface with non-circular `LBM-v3` (`lam=5e-3`, validated on `131` claims / `lbmc1` `0.2784` OOT) expected-300 m-kernel DTI submodular placement + explicit offender-column uniqueness caps (`<= 0.665 <= 0.70` across **all `2,262` registry SHA-256 rasters** on **BOTH** `surface_top_n` via 1D structural crest surface `[0.50, 1.00]` over continuous `[0.00, 0.49]` susceptibility **AND** `final_dots`, with `|Spearman rho| <= 0.90`), while recording the fail-closed literal dense-witness check (`1.000` vs `17GEMSDOE`).
