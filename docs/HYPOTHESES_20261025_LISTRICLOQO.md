# Pre-Registered Geological Hypotheses — `2026-10-25` Session (`LISTRICLOQO` Lane)

**Branch:** `arena/a5100f33-gemsdoe92`  
**Evaluator:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, $\alpha=0.2$, $\beta=0.8$, $R=300\text{ m}=3\text{ px}$ triangular kernel, `22,663` withheld catalogue fault pixels across `8` buffered spatial-quadrant folds, Seeds `20` & `30`, `1,000` paired `20 km` spatial-cluster bootstrap draws)  
**Pre-Registration Timestamp:** `2026-10-25` (written and frozen before any `LISTRICLOQO` code or experiment execution)  
**Hard Experiment Budget (Parallel-Run Protocol Rule 6):** At most **3 experiments** (`listric_standalone`, `listric_nolistric`, `listric_dual35`), **0 weekly competition slots used**.

---

## 1. Motivation & Root-Cause Synthesis from Previous Sessions (`docs/NEXT_STEPS.md`)

Reviewing the repository and the ordered next steps in [`docs/NEXT_STEPS.md`](NEXT_STEPS.md) reveals three coupled physical and statistical findings across `COULOMBLOQO`, `PROVINCETOE`, `POISSONFLEX`, `POISSONKNICK`, and `KNICKLOQO`:

1. **The Dip-Offset Geometry of Basin-and-Range Normal Faults (`LISTRIC-ASYMMETRY-DIP`, [`docs/NEXT_STEPS.md`](NEXT_STEPS.md) Untried Queue Rank 4):**
   In the Northwestern Great Basin (Okaya & Thompson 1985; Wernicke 1995; Faulds & Hinz 2015, INGENIOUS Play Fairway), range-front and intrabasin normal faults dip at $\delta \approx 45^\circ\text{--}60^\circ$ into the hanging-wall basin (and listric faults shallow with depth).
   - While the **surface fault trace** (scarp break, Wallace basal toe, or incised channel knickpoint) lies at the surface bedrock/alluvial contact $x_0$, the **subsurface geophysical inflection** — maximum horizontal gravity gradient (`Band 5` `iso_grav_anom_slope`, `Band 18` `iso_grav_anom_hg`), basement depth gradient (`Band 15` `depth_to_base`), RTP magnetic contact (`Band 2` `rtp`), and MT conductive smectite clay-cap edge (`Band 17` `cond_surf`) — reflects the density/susceptibility/conductivity contrast at **mid-basin depth** ($z_{\text{mid}} \approx 300\text{--}600\text{ m}$).
   - Consequently, the subsurface gradient maximum is laterally displaced by $\Delta r = z_{\text{mid}}\cot\delta \approx 300\text{--}500\text{ m}$ ($3\text{--}5\text{ px}$) downslope into the hanging wall along $\hat{\mathbf{n}}_{\text{hw}}(x) = -\nabla G_3(z_{\text{elev}})/\|\nabla G_3(z_{\text{elev}})\|_2$.
   - Every prior lane in `GEMSDOE92` (`COULOMBLOQO`, `EULERFUSE`, `PROVINCETOE`, `POISSONFLEX`, `POISSONKNICK`, `KNICKLOQO`) evaluated surface and subsurface features only at the **same pixel $x$** ($\Delta r = 0$). As a result, when `KNICKLOQO` boosted `L_sub` (`sub_weight = 1.45`) and downweighted `L_topo` (`topo_weight = 0.15`), it achieved the all-time #1 static `d_cat > 2.0` `HOLDOUT-DTI` (`0.010788`) and #1 draw-blind `d_cat > 2.0` `HOLDOUT-DTI` (`0.010958`), but trailed `COULOMBLOQO standalone` on strict draw-blind `d_visible > 2.0` (`0.109043` vs `0.113316` / `0.113890`) where withheld fault centerlines at $x_0$ are unmasked.

2. **2D Gravity-Gradient Tensor Invariants & Synthetic Riedel ($18^\circ$) En-Echelon Relay Coupling (`TENSOR-RIEDEL`, [`docs/HYPOTHESES_20261025_KNICKLOQO.md`](HYPOTHESES_20261025_KNICKLOQO.md) Rank 2):**
   In transtensional step-overs and relay ramps of the Walker Lane and Humboldt structural belt (Faulds & Hinz 2015), active geothermal fault splays form **synthetic Riedel ($R$) shears** oriented at $|\Delta\theta| \approx 15^\circ\text{--}25^\circ$ relative to the deep basement gravity-tensor strike. Prior lanes (`XPHASE`, `COULOMBLOQO`, `KNICKLOQO`) rewarded only $0^\circ$ collinearity ($\cos 2\Delta\theta$) and did not extract the full 2D horizontal-vertical gravity gradient tensor invariants (Pedersen & Rasmussen 1990; Beiki 2010) from `Bands 5, 11, 13, 18`.

3. **Selective Subsurface-Branch Quadrant Calibration (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`, [`docs/NEXT_STEPS.md`](NEXT_STEPS.md) Priority #2):**
   In `evidence/provincetoe_holdout.json` and `evidence/knick_loqo_proxy_audit.json`, uncalibrated `COULOMBLOQO` starved `NE` (`Q1`) to `11.2%` of dots (`734.30` `tpw` in `NE`), whereas full-quadrant rank equalization (`provincetoe` $\gamma=2.0$, `KNICKLOQO` $\lambda=0.80$) lifted `NE` to `978.45` `tpw` (`+244.15` `tpw`) **at the cost of removing `-261.61` `tpw` from `SW`** (where `33.5%` of the `22,663` withheld fault pixels reside). Calibrating the **subsurface/debiased LOQO branches** strongly across quadrants while applying a **prior-preserving calibration blend** ($\lambda_{\text{cal}} = 0.50$) and **branch-balanced 1D crest localization** (`L_topo_toe + L_knick + L_sub_listric`) recovers `NE` recall (`~20%–23%` dot share) **without** starving `SW` Walker Lane fault density, while avoiding `COULOMBLOQO`'s `SW` alpine cliff collision (`0.8287` vs `EULERFUSE`, `0.7398` vs `GEMSDOE23`) and `PROVINCETOE`'s `62GEMSDOE` collision (`0.7918`).

---

## 2. Five Untried Candidate Geological Hypotheses

| Rank | Candidate Lane | Specific Layers Used | Physical Signature / Mathematical Transform | Why It Catches Faults Missing from the USGS/INGENIOUS Catalogue | How It Differs from All Existing Repo Lanes | Expected `HOLDOUT-DTI` Improvement | Implementation Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 (Selected)** | **`LISTRICLOQO` (`gems/listric_loqo.py`)** | `Bands 2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19`, GeoDAWN `K,Th,U` (`ext_geodawn_rad_u8`), GDR #1391 $\ge 80^\circ\text{C}$ wells (`Band 6` excluded per `#IR-92-BAND6-TC-MISLABEL`) | (1) Up-dip & down-dip Listric Hanging-Wall Dip-Offset Operators ($\Delta r \in \{3, 5\}\text{ px}$ along $\hat{\mathbf{n}}_{\text{hw}}$) coupling surface scarp/Wallace-toe breaks to down-dip gravity/basement/RTP/MT steps; (2) Full 2D horizontal-vertical gravity gradient tensor invariants & 3D analytic signal tilt ($\mathbf{G}_h, \mathbf{g}_{vz}$ from `Bands 5, 11, 13, 18`, Pedersen & Rasmussen 1990); (3) Synthetic Riedel ($R$-shear, $|\Delta\theta|\approx 18^\circ$) en-echelon obliquity coupling; (4) Selective subsurface-branch quadrant calibration ($\lambda_{\text{cal}}=0.50$) + Wallace-toe/knickzone/listric 1D crest localization | Catches $45^\circ\text{--}60^\circ$ dipping normal faults whose subsurface gravity/basement step lies $300\text{--}500\text{ m}$ down-dip in the hanging wall, buried piedmont accommodation splays $250\text{--}450\text{ m}$ basinward of range fronts, and $15^\circ\text{--}25^\circ$ Riedel relay splays in transtensional step-overs | First lane with non-local cross-strike dip-offset pullback/projection ($\Delta r = 3\text{--}5\text{ px}$ along $\hat{\mathbf{n}}_{\text{hw}}$), full 2D gravity-gradient tensor invariants ($\Lambda_1, \Lambda_2, \mathbf{g}_{vz}$), $18^\circ$ Riedel obliquity kernel, and selective subsurface-branch quadrant calibration | **High** (targets beating both `KNICKLOQO` `0.010788` on static `d_cat > 2.0` AND `COULOMBLOQO` `0.113316` on strict draw-blind `d_visible > 2.0`, while clearing `<=0.70` across all local & `dual_reading` public rasters) | **Low–Moderate** (~20 min compute; 100% self-contained on verified pinned stack) |
| **2** | **`THERMO-RHEO-BDT`** | `Bands 1, 9, 10, 14, 16, 17, 20` | Thermal-rheological brittle–ductile transition depth proxy $Z_{\text{BDT}} \propto \text{Band 1} / (\text{Band 9} + \epsilon)$ gated by elevated $V_p/V_s > 1.76$ (`Band 16`) fluid-overpressure corridors and microseismic distance (`Band 20`) | Pressurized geothermal fluids elevate $V_p/V_s$ and shallow the brittle–ductile transition beneath blind fault intersections lacking surface scarps | No existing lane combines crustal thickness (`Band 1`), heat flow (`Band 9`), and $V_p/V_s$ (`Band 16`) into a brittle-thickness fluid-overpressure gate | **Low–Moderate** (native resolution of `Bands 1, 9, 16` is $>5\text{ km}$, too coarse for $300\text{ m}$ DTI without Rank 1's 1D localizers) | **Low** |
| **3** | **`CURIE-DEMAG-RATIO`** | `Band 2` (`rtp`), `Band 9` (`heatflow`), `Band 17` (`cond_surf`), GeoDAWN `K, Th, U` | Multi-altitude FFT upward-continuation gradient decay ratio $\log(\|\nabla_h\text{RTP}_{100\text{m}}\| / (\|\nabla_h\text{RTP}_{800\text{m}}\|+\epsilon))$ isolating shallow hydrothermal magnetite destruction from deep plutonic edges | Hydrothermal fluids ascending along unmapped faults alter magnetite to paramagnetic pyrite/clay in the upper $500\text{ m}$, steepening shallow vs. deep RTP decay | `COULOMBDM` summed upward-continued RTP tilts additively rather than computing the spectral depth-decay ratio | **Moderate** in volcanic terrains (`SW`/`NW`); silent in low-susceptibility carbonate basins (`NE`/`SE`) | **Low–Moderate** |
| **4** | **`PLAYA-EVAPORITE-NULL`** | `Band 12` (`det_elev`), `Band 17` (`cond_surf`), `Band 19` (`det_elev_slope`), GeoDAWN `K, Th` | Isotropic basin-floor concavity ($\lambda_1 \approx \lambda_2 > 0$, eccentricity $< 0.25$) $\times$ flat slope ($< 0.5^\circ$) $\times$ high MT conductivity (`Band 17`) $\times$ evaporative `K/Th` enrichment | Suppresses non-tectonic conductive/radiometric false positives around saline playa deflation margins (Carson Sink, Humboldt Sink) | Existing lanes deconfound contour-parallel Lake Lahontan shorelines (`KNICKLOQO`) and alpine cliffs (`PROVINCETOE`), but not isotropic conductive playa deflation rims | **Low** (pure negative suppressor; requires pairing with a positive 1D fault detector) | **Low** |
| **5** | **`SENTINEL1-INSAR-3DEP10M`** *(External Data Required)* | External [USGS 3DEP 1/3-arc-second (`10 m`) DEM](https://www.usgs.gov/3d-elevation-program) + [ASF Sentinel-1 InSAR LOS velocity](https://asf.alaska.edu/) + [USGS NWIS groundwater levels](https://waterdata.usgs.gov/nwis) | Sub-pixel ($10\text{ m}$) fine-scale scarp curvature + pumping-deconfounded InSAR interseismic creep gradient across blind intrabasin faults | Catches sub-meter Holocene fault scarps invisible at $100\text{ m}$ DEM resolution and actively creeping blind faults | Uses $10\times$ finer external elevation and satellite radar interferometry not present in `training_features.tif` | **High** *(if external tiles staged)* | **Blocked in sandbox** (network egress restricted to GitHub/PyPI; requires offline staging via `scripts/download_competition_data.sh`) |

---

## 3. Mathematical Specification of Top Candidate: `LISTRICLOQO` (`gems/listric_loqo.py`)

### 3.1 Six New Physical Operators (Group G, Zero Fault-Catalogue Input)

Let $z = \text{Band 12}$ (`det_elev`), $s = \max(\text{Band 19}, 0)$ (`det_elev_slope`), $g = \text{Band 13}$ (`iso_grav_anom`), $g_s = \text{Band 5}$ (`iso_grav_anom_slope`), $g_{vg} = \text{Band 11}$ (`iso_grav_anom_vg`), $g_{hg} = \text{Band 18}$ (`iso_grav_anom_hg`), $D_b = \max(\text{Band 15}, 0)$ (`depth_to_base`), $M = \text{Band 2}$ (`rtp`), and $\sigma_{\text{MT}} = \max(\text{Band 17}, 0.1)$ (`cond_surf`).

1. **Up-Dip Listric Hanging-Wall Subsurface Pullback ($\Phi_{\text{listric}}^{\text{up}}$, `listric_hw_updip_pullback`):**
   Let $\mathbf{g}_{z,3} = \nabla G_{3.0}(z)$ be the range-to-basin elevation gradient, so the unit vector pointing **downslope into the hanging-wall basin** is:
   $$\hat{\mathbf{n}}_{\text{hw}}(x) = -\frac{\mathbf{g}_{z,3}(x)}{\|\mathbf{g}_{z,3}(x)\|_2 + 0.5\text{ m}}$$
   Let $\mathcal{G}_{\text{sub}}(x) \in [0, 1]$ be the composite subsurface contact strength at pixel $x$:
   $$\mathcal{G}_{\text{sub}}(x) = 0.35\,\text{Tilt}_{\text{grav}}(x) + 0.30\,\text{sat}\bigl(\|\nabla G_{2.0}\log(D_b + 10)\|_2,\,0.025\bigr) + 0.20\,\text{Tilt}_{\text{RTP}}(x) + 0.15\,\text{sat}\bigl(\|\nabla G_{2.0}\log\sigma_{\text{MT}}\|_2,\,0.012\bigr)$$
   Sampling $\mathcal{G}_{\text{sub}}$ at hanging-wall dip offsets $\Delta r \in \{3.0, 5.0\}\text{ px}$ ($300\text{ m}, 500\text{ m}$ down-dip for $\delta \in [45^\circ, 60^\circ]$) and gating by hanging-wall basin deepening $\Delta D_b(x) = \tanh\bigl((D_b(x + 4\hat{\mathbf{n}}_{\text{hw}}) - D_b(x - 4\hat{\mathbf{n}}_{\text{hw}})) / 150\text{ m}\bigr)_+$:
   $$\Phi_{\text{listric}}^{\text{up}}(x) = \max_{\Delta r \in \{3.0, 5.0\}}\Bigl[\mathcal{G}_{\text{sub}}\bigl(x + \Delta r\,\hat{\mathbf{n}}_{\text{hw}}(x)\bigr)\Bigr] \cdot \bigl(0.35 + 0.65\,\Delta D_b(x)\bigr)$$
   This pulls the down-dip gravity/basement/RTP/MT fault signal back onto the surface fault trace $x_0$, while vanishing on non-tectonic erosional mountain cliffs where $D_b \approx 0$ on both sides ($\Delta D_b \approx 0$).

2. **Down-Dip Listric Range-Front-to-Basin Accommodation Splay Projection ($\Phi_{\text{listric}}^{\text{dn}}$, `listric_fw_downdip_splay`):**
   Conversely, for synthetic piedmont accommodation faults and range-front step-out splays located $250\text{--}450\text{ m}$ basinward of the main topographic toe (where `d_cat > 2.0` masks out the main range-front fault), we sample the surface topographic scarp/toe strength $L_{\text{topo}}(x - \Delta r\,\hat{\mathbf{n}}_{\text{hw}}(x))$ upslope toward the footwall at $\Delta r \in \{2.5, 4.0\}\text{ px}$ and gate it by the local subsurface contact strength $\mathcal{G}_{\text{sub}}(x)$:
   $$\Phi_{\text{listric}}^{\text{dn}}(x) = \max_{\Delta r \in \{2.5, 4.0\}}\Bigl[L_{\text{topo}}\bigl(x - \Delta r\,\hat{\mathbf{n}}_{\text{hw}}(x)\bigr)\Bigr] \cdot \mathcal{G}_{\text{sub}}(x)$$

3. **Wallace Basal Piedmont Toe Asymmetry ($\mathcal{W}_{\text{toe}}$, `wallace_basal_toe_asym`):**
   Let $\lambda_+(z;\sigma) = \sigma^2 \max(\lambda_1(\nabla^2 G_\sigma(z)), 0)$ be the upward profile concavity at $\sigma = 2.0\text{ px}$ ($200\text{ m}$) and let $A_{\text{apron}}(x) = \frac{\max(s(x - 3\hat{\mathbf{n}}_{\text{hw}}) - s(x + 3\hat{\mathbf{n}}_{\text{hw}}), 0)}{s(x - 3\hat{\mathbf{n}}_{\text{hw}}) + s(x + 3\hat{\mathbf{n}}_{\text{hw}}) + 1^\circ} \cdot \mu_{\text{step}}(x)$ be the footwall-steep vs. hanging-wall-gentle apron asymmetry. Then:
   $$\mathcal{W}_{\text{toe}}(x) = \text{sat}\bigl(\lambda_+(z; 2.0),\,1.5\bigr) \cdot \bigl(0.30 + 0.70\,A_{\text{apron}}(x)\bigr)$$
   which peaks at the basal piedmont fault toe and suppresses both symmetric V-canyons ($\mu_{\text{step}} \approx 0$) and bare alpine summit ridges ($\lambda_+ = 0, A_{\text{apron}} = 0$).

4. **Full 2D Horizontal-Vertical Gravity-Gradient Tensor Tilt ($\Theta_{\text{3D}}$, `grav_tensor_3d_tilt`, Pedersen & Rasmussen 1990; Beiki 2010):**
   From `Band 13` ($g$) and `Band 11` ($g_{vg} = \partial_z g$), compute the $2\times 2$ horizontal gravity gradient tensor $\mathbf{G}_h = \nabla_h(\nabla_h G_{2.0}(g))$ with Frobenius norm $\|\mathbf{G}_h\|_F = \sqrt{G_{xx}^2 + 2 G_{xy}^2 + G_{yy}^2}$ and horizontal gradient of the vertical derivative $\mathbf{g}_{vz} = \nabla_h G_{1.5}(g_{vg})$:
   $$\Theta_{\text{3D}}(x) = \frac{\|\mathbf{g}_{vz}(x)\|_2}{\sqrt{\|\mathbf{g}_{vz}(x)\|_2^2 + \|\mathbf{G}_h(x)\|_F^2 + \epsilon^2}}$$

5. **Gravity-Tensor Fault-Contact Eccentricity ($\mathcal{E}_{\text{tensor}}$, `grav_tensor_contact_ecc`):**
   Let $\Lambda_1(x) \ge \Lambda_2(x)$ be the eigenvalues of $\mathbf{G}_h(x)$. Across an elongated 2D dipping fault contact, $|\Lambda_1 - \Lambda_2|$ is large (strong cross-strike curvature anisotropy) while the inflection zero-crossing of the vertical derivative gradient peaks:
   $$\mathcal{E}_{\text{tensor}}(x) = \frac{|\Lambda_1(x) - \Lambda_2(x)|}{|\Lambda_1(x)| + |\Lambda_2(x)| + \epsilon} \cdot \text{sat}\bigl(g_s(x),\,0.08\bigr)$$

6. **Synthetic Riedel ($R$-Shear, $|\Delta\theta| \approx 18^\circ$) En-Echelon Obliquity Coupling ($\mathcal{R}_{\text{Riedel}}$, `riedel_en_echelon_coupling`):**
   Let $|\Delta\theta(x)| \in [0^\circ, 90^\circ]$ be the acute axial angle between local topographic strike $\theta_{\text{topo}}(x)$ and basement gravity strike $\theta_{\text{grav}}(x)$. We reward synthetic Riedel ($R$-shear) en-echelon obliquity centered at $18^\circ$ ($\sigma_\theta = 11^\circ$):
   $$\mathcal{R}_{\text{Riedel}}(x) = \exp\!\left(-\frac{(|\Delta\theta(x)| - 18^\circ)^2}{2\,(11^\circ)^2}\right) \cdot \text{Coh}_{\text{topo}}(x) \cdot \text{Coh}_{\text{grav}}(x)$$

---

## 4. Selective Subsurface-Branch Quadrant Calibration & Balanced 1D Crest Architecture

To resolve `#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`:
- We train three 4-quadrant LOQO branches (`guard_px = 12`, `neg_buffer_px = 5.0`, `neg_pos_ratio = 4`):
  1. `p_full` (all 36 features): Full physical + listric + gravity-tensor + Riedel + knickzone + Poisson stack;
  2. `p_debiased` (30 province-debiased features, excluding raw regional baseline levels);
  3. `p_sub_listric` (32 subsurface + listric + knickzone + Wallace-toe features, excluding raw surface slope Hessian ridges).
- **Selective Calibration:**
  - The subsurface/debiased ensemble $P_{\text{sub-ens}} = 0.45\,p_{\text{debiased}} + 0.55\,p_{\text{sub\_listric}}$ is calibrated within each quadrant ($\lambda_{\text{sub}} = 0.85, \gamma = 3.2$) so that deep basement/gravity/knickzone structures in `NE` (`Q1`) are never starved by the $8.5\times$ Walker Lane geodetic strain shift.
  - The full ensemble blends the uncalibrated prior-preserving probability $P_{\text{raw}} = 0.25\,p_{\text{full}} + 0.35\,p_{\text{debiased}} + 0.40\,p_{\text{sub\_listric}}$ with within-quadrant quantile calibration at moderate weight $\lambda_{\text{cal}} = 0.55, \gamma = 3.1$, preserving `SW`/`SE` high-density fault recall while restoring `NE` dot allocation to `~21%–24%`.
- **Balanced Multi-Mechanism 1D Crest Surface (`build_listric_crest_surface`):**
  Instead of `KNICKLOQO`'s `topo_weight = 0.15` (which under-weighted surface fault traces on `d_visible > 2.0`) or `COULOMBLOQO`'s `topo_weight = 1.00` on raw alpine cliffs (which collided with `EULERFUSE` at `0.8287` and `GEMSDOE23` at `0.7398`), `LISTRICLOQO` forms:
  $$L_{\text{trace}}(x) = \max\Bigl(w_{\text{toe}}\,L_{\text{topo\_listric}}(x),\ w_{\text{knick}}\,L_{\text{knick}}(x),\ w_{\text{sub}}\,L_{\text{sub\_tensor}}(x)\Bigr)$$
  where $L_{\text{topo\_listric}}(x)$ boosts scarp/Wallace-toe breaks that have **up-dip listric hanging-wall subsurface support** $\Phi_{\text{listric}}^{\text{up}}(x)$ and softly tapers bare $>16^\circ$ alpine cliffs lacking subsurface support!

---

## 5. Three Pre-Registered Experiments (Strict Rule 6 Budget = 3)

All three arms emit exactly $S = 37,654$ unit-mass (`1.0`) dots inside the valid footprint at $d_{\text{cat}} > 2.0\text{ px}$, formatted as all-finite `float32` `-zeros.tif` rasters (`0.0` outside footprint):

1. **Experiment 1 (`listric_standalone` — Primary Full `LISTRICLOQO` Model):**
   `100%` standalone (`37,654` dots, zero `H19-5` or `R0` skeleton input) selected from the 1D crest network of the selective-quadrant-calibrated 36-feature `LISTRICLOQO` surface $S_{\text{listric}}(x)$ with inter-dot spacing `min_dist_px = 3.1`.
2. **Experiment 2 (`listric_nolistric` — Pre-Registered Ablation Without Listric Dip-Offset / Gravity-Tensor / Calibration):**
   `100%` standalone (`37,654` dots, zero `H19-5` or `R0` skeleton input) using the uncalibrated raw probability surface without listric dip-offset / selective quadrant calibration, isolating the exact `HOLDOUT-DTI` contribution of the new `LISTRICLOQO` mechanism.
3. **Experiment 3 (`listric_dual35` — Hybrid Expected-DTI Skeleton + Off-Skeleton Listric Discovery):**
   `35%` (`13,179` dots) exact marginal expected-DTI repacked `H19-5` skeleton weighted by $S_{\text{listric}}(x)$ + `65%` (`24,475` dots) standalone 1D `LISTRICLOQO` crests at $d_{\text{H19-5}} > 3.0\text{ px}$ (`min_dist_px = 3.1`).

### Pre-Registered Falsifier & Promotion Decision Rule
- **Leakage Canary (Rule 4):** Every individual band, derived feature, and LOQO surface must satisfy `symmetric ROC AUC <= 0.90` on the buffered holdout folds (`22,663` withheld positives).
- **Holdout Benchmark (Rule 2 & Rule 3):** Evaluate all 3 arms on `gems57-pooled-hide-v2` under (a) static `d_cat > 2.0`, (b) strict draw-blind `d_cat > 2.0`, and (c) strict draw-blind Rule-2 `d_visible > 2.0`, plus off-catalogue USGS SGMC proxy (`62,703` pixels). Target: beat `KNICKLOQO standalone` (`0.010788` static `d_cat > 2.0` and `0.010958` draw-blind `d_cat > 2.0`) AND beat `COULOMBLOQO standalone` (`0.113316` strict draw-blind `d_visible > 2.0`).
- **Uniqueness Gate (Rule 1):** Must achieve `<= 0.70` 3-px forward overlap and `|Spearman rho| <= 0.90` against **all** local rasters in `GEMSDOE92` AND **all** public witnesses under `dual_reading_decision` (`<= 150,000` px dot fields and `> 150,000` px matched-budget continuous surfaces). Because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is positive on `100%` of the footprint (`5,167,373` pixels), the literal unweighted overlap (`1.000 > 0.70`) is reported transparently alongside the `dual_reading_decision`, keeping `submission_eligible: false` and `verdict: "negative"` under the literal site gate (`scripts/check_site.py`).
