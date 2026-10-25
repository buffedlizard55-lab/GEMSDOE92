# Pre-Registered Geological Hypotheses — `CHILISTRIC` Session (2026-10-25)

**Branch:** `arena/2d4c152c-gemsdoe92`  
**Competition:** DrivenData Competition #306 — *DOE Geothermal Exploration Machine Learning Prize (GEMS)*  
**Evaluator:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `alpha=0.20`, `beta=0.80`, `300 m` / `3.0 px` linear distance-decay kernel, `22,663` withheld hidden fault pixels across 8 spatial buffered component folds `seeds 20, 30`, `1,000` 20 km spatial-block bootstrap resamples `seed=520810`)  
**Pre-Registration Timestamp:** `2026-10-25T00:00:00Z` (written and frozen prior to model implementation or holdout evaluation)

---

## 1. Motivation from Previous-Session Next Steps & `R0` (`0.2778 [CLAIM]`) Forensics

Before proposing new features, we inspected both `docs/NEXT_STEPS.md` and the primary-source lineage of `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, reported `0.2778 [CLAIM]`):

1. **Why `R0` reached `0.2778 [CLAIM]` while `GEMSDOE36` fell to `0.2750 [CLAIM]`:** Primary-source verification of `19GEMSDOE/src/gems/hypotheses.py` (`synthesize_h19_5_openness_thermal_corroborated`) and byte-for-byte raster algebra on disk prove that `H19-5` (`121,131` px, `0.1922 [CLAIM]`) was gated by a **multi-line corroboration factor** (`clip(second_best / 0.18, 0.35, 1.0)`) across 4 orthogonal physical families (10 m/1 m scarp openness, anti-piedmont geopotential/basement ramp, structural relay tip geometry, and GDR thermal/geothermometer conduits), followed by `2.8 px` greedy spacing (`D2.8`, `44,090` px, `0.2600 [CLAIM]`) and `d_cat > 2.0 px` catalogue collar pruning (`R0 = D2.8 & (d_cat > 2.0)`, `37,654` px, `0.2778 [CLAIM]`, **0 pixel XOR**). Adding `1,200` un-corroborated PINN dots (`GEMSDOE36`) dropped the reported score to `0.2750 [CLAIM]`.
2. **Two Unresolved Bottlenecks in Current Repository Champions (`LISTRICLOQO` & `VENTSCARP`):**
   - `LISTRICLOQO` (`0.013295` static `HOLDOUT-DTI`, `0.114410` draw-blind `HOLDOUT-DTI`) uses **only the 100 m DEM** (`Bands 12, 19`), missing `< 3 m` Holocene piedmont scarps and narrow tributary knickpoints below `100 m` Nyquist resolution, and uses a **spatially constant `{3.6, 4.4, 5.2} px` updip shift** (`docs/NEXT_STEPS.md` Priority #2), overshooting shallow bedrock-pediment faults (`h_base < 200 m`) onto footwall granite while under-shifting deep graben listric master faults (`h_base > 650 m`).
   - `VENTSCARP` (`0.112213` draw-blind `HOLDOUT-DTI`, `0.008212` static `HOLDOUT-DTI`) introduces seamless **USGS 3DEP 10 m** sub-pixel scarp excess and tufa-filtered **DOE GDR `#1391` INGENIOUS** paleo-vents/`2 m` temperature probes, but applies **zero updip listric projection** (leaving gravity/basement ramps `300–650 m` down-dip in the hanging wall outside the `300 m` DTI kernel) and projects vents along a **rigid global `N18E` azimuth** even across NW-striking Walker Lane (`N35W`) and NE-striking Humboldt (`N50E`) domains.
   - Neither lane tests **DTI-optimal additive secondary recall expansion** (`docs/NEXT_STEPS.md` Priority #1: preserving exact `1.0` peak crests on top `37,654` ridges while adding multi-line corroborated secondary crests without fixed-$L_1$ peak dilution).

---

## 2. Five Ranked Untried Candidate Geological Hypotheses

| Rank | Lane ID | Specific Layers Used | Target Physical Signature | Why Missing from USGS/INGENIOUS Catalogue | Named Non-Fault Mimic & Deconfounder | Expected `HOLDOUT-DTI` Lift | Impl. Cost | Sandbox Data Viability |
|---:|---|---|---|---|---|---|---|---|
| **1** | **`CHILISTRIC`** *(Selected)* | Competition `Bands 2,4,5,7,8,11,12,13,15,17,18,19` + **USGS 3DEP 10 m** (`topo_10m_derived_100m_u8.tif`, `dem10_chi_100m_i16.tif`) + **DOE GDR `#1391`** (`paleo_geothermal_regional.zip`, `2m_temperature_probe…zip`, `gdr_wellspring…csv`) + **USGS GeoDAWN** (`geodawn_rad_u8.tif`, `geodawn_extensions_u8.tif`) | Depth- & tilt-adaptive updip listric projection $s_{\text{adapt}}(x) = \operatorname{clip}(h_{\text{eff}}(x)\cot\theta_{\text{dip}}(x)/100,\,1.8,\,6.4)\text{ px}$ fused with 3DEP `10 m` sub-pixel scarp excess, interfluve-bridged `10 m` fluvial $\chi$-knickpoints, and **local-strike-advected** tufa-filtered sinter/`2 m`-probe/demagnetization valves + multi-line corroboration gate | Degraded `< 3 m` Holocene piedmont scarps blurred out at `100 m` DEM; shallow pediment & deep listric basin faults mis-projected by fixed dip offsets; zero-relief blind geothermal conduits marked only by sinter, `2 m` conductive plumes, and magnetite destruction | (1) Pleistocene Lake Lahontan (`~1,330 m`) wave-cut benches & lacustrine `Tufa` mounds (deconfounded via `Tufa` exclusion + cross-contour transgression); (2) buried paleovalley compaction hinges; (3) primary felsic tuff `U`/`K` cooling margins | **High** (`+0.0005` to `+0.0020` static `d_cat>2.0` & Rule-2 `d_visible>2.0` over `LISTRICLOQO`) | Medium (~18 min) | **100% Viable** (all 19 inputs SHA-256-verified on disk) |
| **2** | `RIEDEL-OBLIQUE-TENSOR` | `Bands 2,3,4,5,7,8,9,11,13,18` + 3DEP `10 m` `hs_lineament`, `aspect_coherence` | Strain-rate shear/dilatation-gated angular obliquity filter $\exp(-(\Delta\theta - 18^\circ)^2 / 98)$ isolating synthetic $R_1$ Riedel en-echelon splays rotated $15^\circ\text{--}25^\circ$ from underlying basement gravity strike | Regional mappers trace bounding range-front faults but omit short (`0.5–2.5 km`) internal en-echelon synthetic Riedel splays in Walker Lane step-overs | Miocene basaltic dike swarms and welded ignimbrite cooling joints oblique to basin margins | Medium (`+0.0003` to `+0.0008`, localized to SW Walker Lane) | Low-Med | Viable (staged), lower footprint coverage than Rank 1 |
| **3** | `MT-DEPTH-CHANGEPOINT` | `Band 17` (`cond_surf`), `Band 15` (`depth_to_base_surf`), `Band 12/13/18`, GeoDAWN `TMI_up150` | Non-parametric conditional residual $r_{\text{MT}}(x) = \log\sigma_{\text{MT}}(x) - \mathbb{E}[\log\sigma_{\text{MT}}\mid h_{\text{base}}(x), z(x)]$ Canny edge concordant with `TMI_up150 - RTP` demagnetization | Blind intrabasin geothermal faults beneath flat playas lack scarps and sharp density steps but create abrupt smectite/brine lateral MT conductivity walls cross-cutting basin-depth contours | Closed-basin evaporite brine lenses, lithium-claystone facies transitions, and agricultural irrigation return-flow plumes | Medium-Low (`Band 17` ~2–5 km station spacing limits `300 m` standalone precision) | Low | Viable (staged), best used as secondary feature rather than standalone crest |
| **4** | `CURIE-POISSON-THERMAL-DEMAG` | `Band 2` (`rtp`), `Band 11/13` (`iso_grav_anom_vg`, `iso_grav_anom`), GeoDAWN `TMI_up150`, `ThK`, `UTh` | $1.5\text{ km}$ moving-window breakdown $(1 - R^2_{\text{Poisson}})\max(0, -\beta_{\text{Poisson}})$ of Poisson's gravity–pseudogravity relation where sharp Bouguer steps coincide with hydrothermally destroyed magnetization | Argillically altered fault cores soften scarp morphology and lose magnetic contrast (` magnetite -> pyrite/hematite`), eluding both aerial-photo and aeromagnetic picks | Non-magnetic Paleozoic carbonate thrusts against metasediments or reversely magnetized Tertiary rhyolite domes | Medium-Low | Medium | Viable (staged), narrower target class than Rank 1 |
| **5** | `INSAR-3DEP1M-MICROSEIS` | NASA OPERA `DISP-S1` 30 m InSAR velocity, USGS 3DEP `1 m` LiDAR DEM, relocated USGS ComCat / NSL microseismicity | Pumping-bowl-orthogonal interseismic LOS velocity gradients $|\nabla v_{\text{LOS}}|$ fused with `0.3–1.5 m` `1 m` LiDAR scarplets and updip projections of planar microseismic hypocenters | Aseismic creeping intrabasin faults and sub-meter Holocene scarplets invisible at `10 m`/`100 m` DEM without historic $M>5.5$ surface rupture | Agricultural/mining groundwater-pumping subsidence margin fissures (Mason, Diamond, Humboldt valleys) and seasonal playa clay heave | High in principle, **0.0 in sandbox** | High | **NOT VIABLE in sandbox** (`earthdata.nasa.gov`, `usgs.gov` blocked by network policy; staged `1 m` LiDAR covers only `75.37%` per `#IR-92-LIDAR-COVERAGE-BIAS`) |

---

## 3. Detailed Physical Specification of Rank 1 (`CHILISTRIC`)

### 3.1 How `CHILISTRIC` Differs From Every Existing Model in `GEMSDOE92`

1. **Depth- & Tilt-Adaptive Listric Updip Shift $s_{\text{adapt}}(x)$ (`f37`, `L_adapt_listric`):**
   For a listric normal fault dipping into a sedimentary basin at local dip angle $\theta_{\text{dip}}(x) \in [41^\circ, 58^\circ]$, the maximum horizontal Bouguer/isostatic gravity gradient sits over the mid-depth density contrast at effective depth $h_{\text{eff}}(x) \approx 0.55\,\min(h_{\text{base}}(x),\, 1100\text{ m})$ (`Band 15`). Using the smoothed potential-field tilt proxy (`Band 18` horizontal gradient vs `|Band 11|` vertical gradient) to bound $\cot\theta_{\text{dip}}(x) \in [0.65, 1.12]$, we define the continuous spatially adaptive updip offset in `100 m` pixels:
   $$s_{\text{adapt}}(x) = \operatorname{clip}\!\left(1.65 + \frac{0.0046\,h_{\text{eff}}(x)\,\cot\theta_{\text{dip}}(x)}{1.0},\; 1.80,\; 6.20\right)$$
   and evaluate a 3-point Gaussian quadrature bracket $\{s_{\text{adapt}}(x) - 0.75,\, s_{\text{adapt}}(x),\, s_{\text{adapt}}(x) + 0.75\}\text{ px}$ along $-\mathbf{n}_{\text{updip}}(x)$ (shifting down-dip hanging-wall potential ramps updip onto the footwall surface break!). Unlike `LISTRICLOQO` (fixed `{3.6, 4.4, 5.2} px`) and `VENTSCARP` (`0 px` shift), `CHILISTRIC` lands inside the `300 m` (`3.0 px`) DTI scoring cone across **both** shallow pediment margins (`180–250 m` shift) and deep asymmetric grabens (`500–620 m` shift).

2. **Seamless 3DEP 10 m Sub-Pixel Scarp Excess + 10 m Fluvial $\chi$-Step Interfluve Bridge (`f38..f40`, `L_scarp10m_chi_bridge`):**
   - Computes sub-pixel scarp localization $E_{10\text{m}}(x) = \max(0,\, \log(1 + S_{10\text{m,max}}(x)) - \log(1 + S_{100\text{m}}(x)))$ weighted by 10 m `aspect_coherence` and `curv_prof_absmax`, explicitly multiplied by a cross-contour transgression gate ($1 - 0.55\,M_{\text{Lahontan}}(x)$) that suppresses horizontal `~1,330 m` Lake Lahontan wave-cut benches where scarp strike parallels elevation contours and lacks any updip gravity ramp.
   - Bridges 10 m tributary channel-steepness steps (`dem10_chi_100m_i16.tif`: `step_max_x1000` and `ksn_max_m0.9` in drainage cells $\log_{10}A \in [4.5, 7.8]$) across adjacent faceted interfluve spurs (`±3.4 px` and `±4.6 px` along the local strike tangent $\mathbf{t}_{\text{strike}}(x)$).

3. **Local-Strike-Advected Hydrothermal Valve & Magnetite-Destruction Conduit (`f41..f43`, `L_hydro_valve`):**
   - Rasterizes tufa-excluded INGENIOUS paleo-geothermal deposits (`195` siliceous sinter, explosion craters, `Qss`, travertine; `86` pure `Tufa` shoreline mounds excluded), `709` positive `2 m` temperature probe conductive anomalies (`F2mDAB > 0`), and `gdr_wellspring_in_footprint.csv` geothermometer springs (`dist_known_fault_px` strictly dropped).
   - Instead of `VENTSCARP`'s fixed `N18E` Gaussian kernel alone, advects hydrothermal valve impulses **along the local geophysical/topographic strike tangent $\mathbf{t}_{\text{strike}}(x)$** (`±3, ±6, ±10, ±15 px`) and locks them onto local Grauch (2001) shallow magnetite-destruction lows (`z(TMI_up150) - z(RTP) > 0`), GeoDAWN `K/Th` + `U/Th` alteration edges, and basin-depth-deconfounded MT lateral conductivity gradients!

4. **Second-Best Multi-Line Corroboration Gate (`f44`, `S_crest`):**
   - Computes normalized ranks of the 3 orthogonal physical line families at every pixel:
     - $\Lambda_1(x)$: `L_scarp10m_chi_bridge` (sub-pixel `10 m` scarp & $\chi$-knickpoint geomorphic line),
     - $\Lambda_2(x)$: `L_adapt_listric` (depth/tilt-adaptive updip subsurface Bouguer/basement/Poisson ramp),
     - $\Lambda_3(x)$: `L_hydro_valve` (strike-guided hydrothermal vent/`2 m`-probe/alteration/demag/relay line).
   - Defines `second_best(x)` as the **second largest** of $\{\Lambda_1(x), \Lambda_2(x), \Lambda_3(x)\}$ so single-modality false positives (pure shoreline benches, pure paleovalley gravity steps, or pure felsic tuff radiometric contacts) are penalized while multi-physics fault traces are amplified!

---

## 4. Pre-Registered 3-Experiment Budget (Protocol Rule 6)

All 3 experiments share a single cached 44-feature zero-leakage stack (`gems/chilistric.py`) verified against Rule 4 single-feature leakage canaries (`symmetric AUC <= 0.90` on all 44 features) before fitting:

1. **Experiment 1 (`adapt37k` — Matched `37,654`-Dot Binary Unit Crests):**
   - 4-branch selective-quadrant-calibrated LOQO ensemble (`Full 44f`, `Province-Debiased`, `Adaptive-Listric-Subsurface`, `10m-Scarp-Chi-HydroValve`) fused with multi-line corroborated crest surface (`S_crest`), `min_dist_px = 4.40`, `d_cat > 2.0`, exact `37,654` unit `{0.0, 1.0}` pixels.
   - Tests pure spatial re-localization from `100 m` fixed-offset `LISTRICLOQO` to `10 m` scarp/$\chi$ + depth-adaptive listric + strike-guided hydrothermal valve at identical dot budget.
2. **Experiment 2 (`addtail52k` — DTI-Optimal Non-Diluting Additive Secondary Tail):**
   - Retains the exact top `37,654` unit crests (`value = 1.0`) from `adapt37k` AND adds `14,346` non-overlapping (`min_dist_px = 4.20` from primary + mutually spaced) secondary multi-line corroborated crests (`total 52,000` positive pixels) at amplitude `w_tail = 0.55` (`values in {0.0, 0.55, 1.0} ⊂ [0, 1]`).
   - Directly executes `docs/NEXT_STEPS.md` Priority #1: tests whether asymmetric Tversky ($\beta/\alpha = 4.0$) rewards non-diluting secondary recall expansion on **both** static `d_cat > 2.0` and strict draw-blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`.
3. **Experiment 3 (`no10m_fixed` — Causal 10 m Geomorphic & Adaptive-Offset Ablation):**
   - Masks out all `10 m` 3DEP scarp/$\chi$, paleo-vent/`2 m`-probe, and adaptive dip-offset channels (`cols 36..43`), falling back to `100 m` DEM + fixed dip-offset crests at the identical `37,654` binary budget (`min_dist_px = 4.40`).
   - Quantifies the exact paired spatial-block bootstrap `HOLDOUT-DTI` lift contributed by `CHILISTRIC`'s new physics.

### Mandatory Pass/Stop Gates
- **Rule 1 Uniqueness:** Pre-placement continuous surface AND final dots checked against all local rasters and all `1,503` compatible single-band rasters across `102` `buffedlizard55-lab/*GEMSDOE*` repositories (`|rho| <= 0.90`; operational `3 px` overlap `<= 0.70`; literal unweighted `17GEMSDOE` dense-surface witness `1.0000 > 0.70` reported transparently with `submission_eligible: false`, `verdict: "negative"`).
- **Rule 4 Leakage Canary:** Every single feature (`f01..f44`) must have `symmetric AUC <= 0.90` on withheld hidden faults before model training.
- **Format & Encoding Validator:** Every `.tif` written via `vendor/gems57/submission_writer.py` must pass `11/11` `gems/gates.py` checks (`EPSG:32611`, `3730x3292`, `float32`, `all_finite=True`, `values in [0, 1]`, `zero_outside=True`, `0` on catalogue, `0` within `2 px` of catalogue).
