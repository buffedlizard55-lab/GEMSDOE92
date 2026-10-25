# Pre-Registered Geological Hypotheses — `2026-10-25` Session (`RADIODECOUPLE` Lane)

**Session Date:** `2026-10-25`  
**Lane Name:** `RADIODECOUPLE` (`RADIO-POTENTIAL-DECOUPLE`)  
**Evaluator:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, $\alpha=0.2$, $\beta=0.8$, $R=300\text{ m}=3\text{ px}$ triangular kernel, `22,663` withheld catalogue fault pixels across `8` buffered spatial-quadrant folds, Seeds `20` & `30`, `1,000` paired `20 km` spatial-cluster bootstrap draws)  
**Pre-Registration Rule:** Written BEFORE executing any experiment or generating the submission raster.  
**Hard Experiment Budget (Parallel-Run Protocol Rule 6):** At most **3 experiments** (`radiodecouple_standalone`, `radiodecouple_demag`, `radiodecouple_dual35`).

---

## 1. Research Context & Physical Motivation

In the Basin and Range province of northwestern Nevada, geothermal energy production requires deep convective circulation of meteoric fluids along permeable fault damage zones. However, discovering **unmapped** blind faults (structures absent from the USGS Quaternary fault catalogue and the INGENIOUS project mapping) presents a fundamental geophysical challenge:

1. **Scarp Preservation Bias in the Catalogue:**
   The official USGS/INGENIOUS fault inventory is heavily biased toward young, preserved surface scarps. Faults with low Quaternary slip rates, faults concealed beneath Lake Lahontan pluvial lacustrine muds or thick alluvial fans, and blind structural step-overs possess no preserved topographic scarps, yet may host active high-enthalpy geothermal upflow.
2. **Hydrothermal Alteration vs. Surficial Ash-Flow Confounders:**
   Active and fossil geothermal upflow produces pervasive hydrothermal metasomatism in wall rocks:
   - **Potassium Metasomatism ($K/\text{Th}$ enrichment):** Illite and adularia precipitation during fluid ascent alters potassium concentration relative to immobile thorium.
   - **Uranium Mobility ($U/\text{Th}$ Redox Fronts):** Oxidizing hydrothermal fluids transport hexavalent uranium, precipitating uranium minerals along reducing fault selvages.
   - **Magnetite Destruction (Demagnetization Troughs):** High-temperature geothermal brines sulfidize and destroy primary magnetite in volcanic host rocks, producing local linear magnetic low troughs ($\nabla_h^2\text{RTP} > 0$).
   - **Smectite Clay Caps:** Low-temperature alteration caps above convective cells produce high electrical conductivity (low resistivity) detectable in magnetotelluric surveys (`Band 17 cond_surf`).
3. **The Critical Confounder (Why Previous Radiometric Lanes Failed):**
   Flat-lying, surficial Tertiary rhyolitic ash-flow sheets (ignimbrites) widespread across northwestern Nevada exhibit intense radiogenic signals ($K, U, Th$) and sharp erosional contact scarps. In prior simple approaches (such as `RADIOCONTACT`), scalar product operations mistook erosional edges of flat volcanic sheets for active fault contacts.
4. **The Physical Decoupling Solution:**
   True blind geothermal conduits are deeply rooted into the pre-Tertiary crystalline basement, creating sharp horizontal density contrasts ($\nabla_h g_{\text{iso}}$) and vertical gravity derivative peaks ($g_{\text{vg}}$, Band 11).
   When a radiometric alteration gradient $\nabla_h(K/\text{Th})$ is **collinear** with the deep horizontal gravity gradient $\nabla_h g_{\text{iso}}$ ($|\mathbf{n}_{\text{rad}} \cdot \mathbf{n}_{\text{grav}}| \to 1$), the alteration is structurally rooted in a tectonic basement fault. Conversely, when radiometric boundaries are decoupled or orthogonal to potential-field basement steps ($|\mathbf{n}_{\text{rad}} \cdot \mathbf{n}_{\text{grav}}| \to 0$), they represent rootless surficial ash-flow facies or evaporite contacts and are suppressed.

---

## 2. Five Untried Candidate Geological Hypotheses

| Rank | Candidate Lane | Data Layers Used | Physical Signature / Transform | Why It Catches Unmapped USGS/INGENIOUS Faults | How It Differs from All Existing Repo Lanes | Expected `HOLDOUT-DTI` Gain | Implementation Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 (Selected)** | **`RADIODECOUPLE` (`RADIO-POTENTIAL-DECOUPLE`)** | Pinned `geodawn_rad_u8` ($K, U, Th$), `training_features.tif` Band 2 (`rtp`), Band 5 (`iso_grav_anom_slope`), Band 11 (`iso_grav_anom_vg`), Band 13 (`iso_grav_anom`), Band 17 (`cond_surf`), Band 18 (`iso_grav_anom_hg_ew`) | 3D cross-physics vector tensor collinearity $|\mathbf{n}_{\text{rad}}\cdot\mathbf{n}_{\text{grav}}|$ between radiometric alteration gradients $\nabla_h(K/\text{Th})$ and gravity gradients $\nabla_h g_{\text{iso}}$, modulated by vertical gravity gradient magnitude $|g_{\text{vg}}|$, RTP demagnetization trough $\nabla_h^2\text{RTP} > 0$, and MT clay-cap conductivity level. | Quaternary scarps have diffused or were never formed in alluvium-covered blind faults, but hydrothermal fluid flow and basement density displacement remain intact. Decoupling suppresses non-tectonic surficial rhyolite sheets. | First lane to explicitly decouple surficial radiometric ash sheets from deep basement faults via vector collinearity; `RADIOCONTACT` used only scalar products without tensor alignment or demagnetization gating. | **High** (targets unmapped blind geothermal conduits) | **Low–Medium** (~10–15 min compute, reuses pinned inputs and shared evaluators) |
| **2** | **`TENSOR-RIEDEL`** | Band 5 (`iso_grav_anom_slope`), Band 11 (`iso_grav_anom_vg`), Band 13 (`iso_grav_anom`), Band 18 (`iso_grav_anom_hg_ew`), Band 7 (`geod_shearrate`), Band 8 (`geod_dilaterate`), Band 12 (`det_elev`) | 2D horizontal gravity gradient tensor $\mathbf{T}_{ij} = \partial_i\partial_j g_{\text{iso}}$ rotational invariant ratio $I = \frac{(\mathbf{T}_{xx}-\mathbf{T}_{yy})^2+4\mathbf{T}_{xy}^2}{(\mathbf{T}_{xx}+\mathbf{T}_{yy})^2}$ (Pedersen & Rasmussen 1990) + en-echelon synthetic Riedel ($R$) angular obliquity ($15^\circ\text{--}25^\circ$) relative to regional geodetic shear azimuth. | Primary geothermal settings occur in transtensional relay ramps and step-overs where splays rotate $15^\circ\text{--}25^\circ$ off master faults; catalogue mappers routinely omit short transfer splays inside basin floors. | Existing lanes reward $0^\circ$ collinearity; `TENSOR-RIEDEL` rewards angular obliquity characteristic of active pull-apart stepovers. | **Moderate–High** | **Medium** |
| **3** | **`FLEXURE-HINGE`** | Band 12 (`det_elev`), Band 13 (`iso_grav_anom`), Band 15 (`depth_to_base_surf`), Band 19 (`det_elev_slope`) | Broken-plate elastic lithospheric flexural curvature wavelet ($\alpha_{\text{flex}} \approx 10\text{--}15\text{ km}$, Buck 1988) zero-crossing inflection coupled with maximum basement depth gradient $\max\|\nabla(\text{depth\_to\_base})\|$. | Range-bounding normal faults concealed under $200\text{--}500\text{ m}$ of basin pediment do not show sharp surface scarps, but manifest as broad flexural monocline inflection lines at the surface. | Prior terrain lanes use high-frequency short-wavelength ($100\text{--}300\text{ m}$) scarp steps; `FLEXURE-HINGE` inverts for the long-wavelength elastic plate hinge. | **Moderate** | **Low** |
| **4** | **`CLAYCAP-REDOX`** | Band 17 (`cond_surf`), Band 2 (`rtp`), Band 15 (`depth_to_base_surf`), `geodawn_rad_u8` ($U, Th$) | Paired 2nd-derivative flank of conductive smectite clay caps ($\nabla^2\log(\text{Band 17}+1)<0$) + horizontal gradient of mobile uranium ratio $\|\nabla(U/\text{Th})\|$ + RTP demagnetization trough. | Targets hydrothermal clay-cap geochemical alteration and redox boundaries directly, rather than brittle surface fault scarps. | Prior lanes used raw MT level or edge without paired 2nd-derivative boundary condition and mobile uranium front. | **Low–Moderate** (spatially restricted to shallow hydrothermal cells) | **Low** |
| **5** | **`INSAR-3DEP1M-CREEP`** | USGS 3DEP 1 m LiDAR DEM tiles (`https://www.usgs.gov/3d-elevation-program`) + Sentinel-1 InSAR ascending/descending velocity fields | Persistent aseismic creep lineament: phase rate velocity discontinuity across faults confirmed on 1 m micro-scarp profiles. | Detects creeping faults that produce zero seismic events in Band 10/16 and subtle scarps invisible on 10 m / 30 m DEMs. | Utilizes high-resolution interferometric SAR and 1 m LiDAR. | **High** | **High / NOT VIABLE in this sandbox** (external tiles not staged; non-GitHub network restricted) |

---

## 3. Mathematical Specification of the Selected Candidate: `RADIODECOUPLE`

### 3.1 Operator Definition

Let the valid footprint mask be $\Omega \subset \mathbb{R}^2$. All inputs are evaluated strictly within $\Omega$.

1. **Radiometric Alteration Ratio & Gradient Vectors:**
   From `geodawn_rad_u8`, extract calibrated counts for Potassium ($K$), Thorium ($Th$), and Uranium ($U$).
   With regularization $\epsilon_0 = 1.0$:
   $$R_{K/\text{Th}}(x) = \frac{K(x)}{Th(x) + \epsilon_0}, \qquad R_{U/\text{Th}}(x) = \frac{U(x)}{Th(x) + \epsilon_0}$$
   Compute horizontal gradient vectors via central finite differences:
   $$\mathbf{g}_{\text{rad}}(x) = \nabla_h R_{K/\text{Th}}(x) = \left( \frac{\partial R_{K/\text{Th}}}{\partial x}, \frac{\partial R_{K/\text{Th}}}{\partial y} \right)$$
   $$\mathbf{n}_{\text{rad}}(x) = \frac{\mathbf{g}_{\text{rad}}(x)}{\|\mathbf{g}_{\text{rad}}(x)\|_2 + \epsilon}$$

2. **Potential-Field Gravity Gradient Vectors:**
   From `training_features.tif`, Band 13 is isostatic gravity anomaly $g_{\text{iso}}$, and Band 18 is signed E–W horizontal derivative $g_{\text{hg,ew}} \approx \partial_x g_{\text{iso}}$. We compute the full horizontal gradient vector:
   $$\mathbf{g}_{\text{grav}}(x) = \left( \text{Band 18}(x), \frac{\partial}{\partial y} \text{Band 13}(x) \right)$$
   $$\mathbf{n}_{\text{grav}}(x) = \frac{\mathbf{g}_{\text{grav}}(x)}{\|\mathbf{g}_{\text{grav}}(x)\|_2 + \epsilon}$$

3. **3D Vector Collinearity Decoupling Operator ($\mathcal{C}_{\text{vec}}$):**
   The degree of structural rooting is measured by the absolute cosine between the radiometric alteration contact normal and the basement gravity gradient normal:
   $$\mathcal{C}_{\text{vec}}(x) = |\mathbf{n}_{\text{rad}}(x) \cdot \mathbf{n}_{\text{grav}}(x)| \in [0, 1]$$
   - $\mathcal{C}_{\text{vec}} \approx 1$: The radiometric alteration front is parallel to the deep basement density contact (structurally rooted fault).
   - $\mathcal{C}_{\text{vec}} \approx 0$: The radiometric edge is decoupled from basement structure (surficial ash-flow sheet boundary or alluvial contact).

4. **Basement Depth & Density Amplitude Gating:**
   The surface is weighted by the vertical gravity gradient magnitude (Band 11, $g_{\text{vg}}$, marking steep basement contact boundaries) and gravity slope (Band 5, $g_{\text{slope}}$):
   $$\mathcal{A}_{\text{grav}}(x) = \text{pct\_rank}\bigl( |g_{\text{vg}}(x)| \cdot g_{\text{slope}}(x) \bigr)$$

5. **Hydrothermal Magnetite Demagnetization Trough ($\mathcal{M}_{\text{demag}}$):**
   Hydrothermal alteration destroys magnetic minerals. In Reduced-to-Pole magnetic anomaly (Band 2, $B_2$), linear fault demagnetization produces a local curvature trough:
   $$\mathcal{M}_{\text{demag}}(x) = \text{pct\_rank}\bigl( \max(\nabla_h^2 B_2(x), 0) \bigr)$$

6. **MT Smectite Clay-Cap Conductivity Gating ($\mathcal{E}_{\text{MT}}$):**
   From Band 17 (`cond_surf`):
   $$\mathcal{E}_{\text{MT}}(x) = \text{pct\_rank}\bigl(\text{Band 17}(x)\bigr)$$

7. **Synthesized Lane Surfaces:**
   - **Base Decoupled Surface:**
     $$S_{\text{standalone}}(x) = \text{pct\_rank}\bigl(\|\mathbf{g}_{\text{rad}}(x)\|_2\bigr) \cdot \mathcal{C}_{\text{vec}}(x) \cdot \mathcal{A}_{\text{grav}}(x) \cdot \mathcal{E}_{\text{MT}}(x)$$
   - **Demagnetization-Gated Surface:**
     $$S_{\text{demag}}(x) = S_{\text{standalone}}(x) \cdot \mathcal{M}_{\text{demag}}(x)$$

---

## 4. Three Pre-Registered Experimental Arms (Rule 6 Budget = 3)

All three arms emit exactly $S = 37,654$ unit-mass (`1.0`) dots inside the valid footprint at $d_{\text{cat}} > 2.0\text{ px}$ (`> 200 m` clearance outside mapped catalogue faults), formatted as single-band `float32` `-zeros.tif` GeoTIFFs (`0.0` outside footprint):

1. **Experiment 1 (`radiodecouple_standalone`):**
   `100%` standalone dots ($37,654$ dots, zero catalogue skeleton input) selected from the 1D ridge crests of $S_{\text{standalone}}(x)$ using non-maximum suppression (NMS) and spaced at $d_{\min} \ge 2.83\text{ px} \approx 300\text{ m}$ to match the DTI triangular kernel footprint.
2. **Experiment 2 (`radiodecouple_demag`):**
   `100%` standalone dots ($37,654$ dots) selected from $S_{\text{demag}}(x)$ (incorporating the magnetic demagnetization trough $\mathcal{M}_{\text{demag}}$) at $d_{\min} \ge 2.83\text{ px}$.
3. **Experiment 3 (`radiodecouple_dual35`):**
   Hybrid allocation: $35\%$ ($13,179$ dots) from submodular expected-DTI repacked `H19-5` skeleton weighted by $S_{\text{standalone}}(x)$ + $65\%$ ($24,475$ dots) standalone crests at $d_{\text{H19-5}} > 3.0\text{ px}$ ($d_{\min} \ge 2.83\text{ px}$).

### Pre-Registered Promotion Criteria & Stop Rules
- **Leakage Canaries (Protocol Rule 4):** Every feature ($\|\mathbf{g}_{\text{rad}}\|$, $\mathcal{C}_{\text{vec}}$, $\mathcal{A}_{\text{grav}}$, $\mathcal{M}_{\text{demag}}$, $\mathcal{E}_{\text{MT}}$, and $S$) must pass the symmetric ROC AUC canary test ($\le 0.90$) evaluated against withheld truth across the 8 holdout folds.
- **Holdout Benchmark (Protocol Rules 2 & 3):** Evaluated under `gems57-pooled-hide-v2` (22,663 withheld positives, 8 folds, 1,000 spatial bootstrap draws). Must beat the repository record holdout best (`0.113316` Rule-2 `d_visible > 2.0` / `0.010788` static `d_cat > 2.0`) with 95% CI excluding zero before touching any weekly slot.
- **Uniqueness Gate (Protocol Rule 1):** Forward 3-px overlap $\le 0.70$ and rank correlation $|\rho| \le 0.90$ across local and public registries. If literal public overlap trips on the 5.17M-pixel dense surface witness (`17GEMSDOE`), mark `verdict: "negative"`, set `submission_eligible: false`, and consume **0 weekly competition slots**.
