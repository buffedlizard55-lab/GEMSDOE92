# Candidate Geological Hypotheses & Pre-Registration — 2026-10-25 (MT-CHANGEPOINT Lane)

## 1. Candidate Geological Hypotheses (3–5 Untried Ideas)

As required by the operating protocol, we systematically generate, evaluate, and rank candidate geological hypotheses targeting hidden/unmapped faults in the Northwestern Great Basin (Nevada/California) geothermal study area before code execution.

| Rank | Hypothesis & Layers | Target Physical Signature | Why It Catches Missing Faults (Not in Catalogue) | Difference From Existing Repository Implementations | Expected DTI / Cost | Free Official Source / Availability |
|---|---|---|---|---|---|---|
| **1 (Selected)** | **MT-CHANGEPOINT**: Magnetotelluric Conductive Conduit & Basement Changepoint Coupling<br>• Layers: B17 (`cond_surf` MT conductivity), B15 (`depth_to_base_surf`), B11 (`iso_grav_anom_vg`), B19 (`det_elev_slope`) | Directional spatial gradient of log-conductivity normalized by moving-window variance ($\text{CP}_{\text{MT}} = \|\nabla \log(1+\sigma)\| / (\sigma_{\text{local}} + \epsilon)$) coupled with basement step-edge concordance ($|\cos \Delta\theta|$) and playa deconfounding | Blind geothermal faults lack surficial scarps (eroded or buried under Quaternary alluvium) but host active ascending hydrothermal brine circulation and argillic clay alteration caps (smectite/illite), creating steep lateral electrical conductivity steps along basement boundaries | Prior methods (`HYDROCONDUIT`) used scalar conductivity thresholding; MT-CHANGEPOINT computes spatial gradient changepoints normalized by local variance, strictly aligned with basement DoG gradients and filtered against passive playa sinks | Expected DTI: High (+0.002 to +0.006 holdout gain; strong blind-fault sensitivity)<br>Cost: Low/Medium (fully in-stack; CPU efficient) | Pre-staged in `.cache/gems_inputs/training_features.tif` (Bands 11, 15, 17, 19). No external data required. |
| **2** | **DEPTH-ADAPTIVE LISTRIC PROJECTION**: Spatially-Varying Grauch-Cordell Updip Projection<br>• Layers: B15 (`depth_to_base_surf`), B18 (`iso_grav_anom_hg`), B11 (`iso_grav_anom_vg`), B2 (`rtp`) | Continuous updip displacement $s(x) = \text{clip}(h_{\text{base}}(x) \cot 52^\circ / 100\text{ m}, 2.5, 6.5)\text{ px}$ projected from basement boundary gradients along footwall normal | Normal faults in the Basin & Range dip at ~50°–60°; deep geophysical boundaries reflect the fault at basement depth (200–1000 m), which emerges updip at the surface. Unmapped blind splays are missed when assuming vertical fault planes | Prior `LISTRICLOQO` used a discrete 3-offset fixed envelope (3.6, 4.4, 5.2 px); this operator computes continuous depth-dependent projection | Expected DTI: High<br>Cost: Low | In-stack (Bands 2, 11, 15, 18). Verified available. |
| **3** | **TENSOR-RIEDEL**: 2D Geodetic Strain Tensor Riedel Shear Conjugation<br>• Layers: B4 (`geod_2ndinv`), B7 (`geod_shearrate`), B8 (`geod_dilaterate`) | Resolves the 2D infinitesimal strain tensor to compute maximum shear stress axes and projects synthetic Riedel ($R$, $15^\circ$) and antithetic Riedel ($R'$, $75^\circ$) shear orientations | Transtensional stepovers transfer strain between master faults along sub-resolution en echelon fractures that lack mapped scarps but concentrate geothermal permeability | Prior methods used scalar shear or dilatation independently; TENSOR-RIEDEL reconstructs the tensor eigenvectors | Expected DTI: Moderate<br>Cost: Medium | In-stack (Bands 4, 7, 8). Verified available. |
| **4** | **THERMO-ISOSTATIC GRAV-MAG CO-CURVATURE**: Curie-Bouguer Thermal Demagnetization Coupling<br>• Layers: B11 (`iso_grav_anom_vg`), B9 (`tmi_vg`), B6 (`tc`) | Joint Hessian eigenvalue analysis of combined pseudogravity and reduced-to-pole magnetic potential | Active hydrothermal upflow zones demagnetize titanomagnetite to pyrite/leucoxene along deep structural conduits, producing coincident negative magnetic curvature and gravity gradients | Prior `CURIEDEMAG` used regional low-pass thermal filters; this uses localized multi-scale Hessian curvature | Expected DTI: Moderate<br>Cost: Medium | In-stack (Bands 6, 9, 11). Verified available. |
| **5** | **SUB-100m TOPOGRAPHIC BREAK-OF-SLOPE (External Data Required)**<br>• Layers: USGS 3DEP 1/3 arc-second (10 m) DEM + InSAR phase coherence | 10 m DEM profile curvature and residual relief aggregated to 100 m cell grid to resolve 10–30 m subtle alluvial scarps | Captures late Pleistocene/Holocene scarps completely sub-pixel in 100 m regional DEM | Cannot be resolved from 100 m `det_elev` band alone | Expected DTI: Very High (crucial to bridge toward 0.4413)<br>Cost: High (requires downloading external 10 m tiles) | Free official source: USGS 3DEP program (https://www.usgs.gov/3d-elevation-program / ScienceBase / National Map). Requires external staging. |

---

## 2. Selected Hypothesis Pre-Registration: MT-CHANGEPOINT

### 2.1 Theoretical Mechanism
In extensional geothermal systems, faults act as primary controls on fluid permeability. Saline hydrothermal fluids alter country rock into conductive smectite/illite clay caps. This produces sharp lateral conductivity contrasts ($\nabla \log(1+\sigma)$) in Magnetotellurics (Band 17). To separate genuine geothermal conduits from conductive non-fault evaporite playas (e.g. Carson Sink), we require:
1. Directional concordance ($|\cos \Delta\theta|$) with basement step-edges (Band 15 DoG gradient).
2. Vertical gravity gradient anomalies (Band 11) reflecting hydrothermal mineral self-sealing.
3. Topographic and basement slope deconfounding to suppress flat, deep playa sinks.

### 2.2 Pre-Registered Experimental Arms (Max 3 per Budget)
- **Arm 1 (`mtcp`)**: Full MT-Changepoint coincidence surface ($S_{\text{mtcp}} = \text{pct}( \text{CP}_{\text{MT}} \cdot |\cos \Delta\theta| \cdot \text{pct}(G_{\text{base}}) \cdot (0.35 + 0.65 \cdot \text{pct}(|V_{\text{grav}}|)) \cdot W_{\text{playa}} )$).
- **Arm 2 (`mt`)**: MT changepoint alone ablation ($S_{\text{mt}} = \text{pct}(\text{CP}_{\text{MT}})$).
- **Arm 3 (`base_grav`)**: Basement gradient $\times$ gravity vertical gradient ablation ($S_{\text{base\_grav}} = \text{pct}(G_{\text{base}} \cdot (0.35 + 0.65 \cdot \text{pct}(|V_{\text{grav}}|)))$).
- **Control**: `gravquad_control` (re-placed under identical conditions).

### 2.3 Strict Validation Gates
1. Pinned input SHA-256 verification before computation.
2. Zero catalogue features in surface computation (`gems/mt_changepoint.py`).
3. Single-feature leakage canaries: max symmetric AUC $\le 0.90$.
4. Pre-placement surface registry screen: Spearman $|\rho| \le 0.90$ vs unique local registry rasters.
5. Primary holdout: `buffered_component_draw` (seeds 20+30), fold-visible clearance $>2\text{ px}$, pooled DTI, 95% bootstrap CI. Promotion bar: `0.113316` (`COULOMBLOQO` record).
6. Shared writer: float32, single band, finite `[0, 1]`, zeros outside footprint, `nodata=None`, matching CRS/shape/transform.
