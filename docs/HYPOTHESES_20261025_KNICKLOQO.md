# Pre-Registered Geological Hypotheses — `2026-10-25` Session (`KNICKLOQO` Lane)

**Branch:** `arena/4d56f06c-gemsdoe92`  
**Evaluator:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, $\alpha=0.2$, $\beta=0.8$, $R=300\text{ m}=3\text{ px}$ triangular kernel, `22,663` withheld catalogue fault pixels across `8` buffered spatial-quadrant folds, Seeds `20` & `30`, `1,000` paired `20 km` spatial-cluster bootstrap draws)  
**Pre-Registration Timestamp:** `2026-10-25` (written before any `KNICKLOQO` experiment execution)  
**Hard Experiment Budget (Parallel-Run Protocol Rule 6):** At most **3 experiments** (`knickloqo_standalone`, `knickloqo_uncal`, `knickloqo_dual35`).

---

## 1. Motivation & Root-Cause Synthesis from Prior Sessions

Two coupled bottlenecks were identified across the prior `COULOMB-LOQO`, `EULERFUSE`, and `BLINDFAULT` sessions (`docs/NEXT_STEPS.md`, `IRREGULARITIES.md`):

1. **`#IR-92-NE-QUADRANT-LOQO-COLLAPSE` (Tectonic-Province Covariate Shift & Uncalibrated LOQO Starvation):**
   In `training_features.tif`, the interior Humboldt / Owyhee domain (`NE` quadrant, `27.6%` of the footprint and `20.5%` of catalogue faults) has near-zero raw geodetic shear rate (`Band 7` median `0.00`, p90 `0.70`) and $5\times$–$9\times$ lower strain-rate second invariant (`Band 4` median `3.80`, p90 `6.10`) compared to the Walker Lane / Central Nevada Seismic Belt (`SW` median `18.26` / `34.50`, `SE` median `15.50` / `29.10`), where `62.8%` of mapped catalogue pixels reside. When a 4-quadrant Leave-One-Quadrant-Out (LOQO) model trains on `{NW, SW, SE}` using raw province-level covariates and concatenates uncalibrated out-of-quadrant probabilities $P_{-q}(x)$ across folds, every pixel in `NE` is pushed into the low-strain leaves of the tree ensemble. Under global top-$37,654$ selection, `NE` is starved to **`49` dots (`0.1%`) in `BLINDFAULT_blind`**, **`272` dots (`0.7%`) in `BLINDFAULT_blindtopo`**, **`4,189` dots (`11.1%`) in `EULERFUSE_gravity`**, and **`4,221` dots (`11.2%`) in `COULOMBLOQO_standalone`** (versus `10,145` dots = `26.9%` in `R0`), depressing `NE` recall (`Seed 20 NE HOLDOUT-DTI = 0.006100` in `COULOMBLOQO_standalone` vs `0.007466` when raw Coulomb strain features were dropped in `nocoulomb`).
2. **`#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION` (Post-Merge Registry Overlap in `SW+SE`):**
   Because both `COULOMBLOQO` and `EULERFUSE` starved `NE` and packed $>61\%$ of their `37,654` dots onto the same `SW+SE` topographic ridge crests at `min_dist_px = 2.8`, our Action #1 `dual_reading_decision` audit (`evidence/coulomb_loqo_dual_reading_audit.json`) revealed that `COULOMBLOQO_standalone` (`0.828703` overlap vs `EULERFUSE_gravity`, `0.739842` vs `GEMSDOE23 h29-dealiased-habitat`) and `COULOMBLOQO_dual45` (`0.732565` vs `EULERFUSE_gravity`, `0.722420` vs `GEMSDOE23 h29-dealiased-habitat`) exceed the `0.70` 3-px forward overlap threshold even under `dual_reading_decision` (`DOT_FIELD_MAX_SUPPORT = 150,000`).

---

## 2. Five Untried Candidate Geological Hypotheses

| Rank | Candidate Lane | Data Layers Used | Physical Signature / Transform | Why It Catches Unmapped USGS/INGENIOUS Faults | How It Differs from All Existing Repo Lanes | Expected `HOLDOUT-DTI` Gain | Implementation Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 (Selected)** | **`KNICKLOQO` (`KNICK-POISSON-LOQO`)** | `Bands 2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19`, GeoDAWN `K,Th,U`, GDR #1391 $\ge 80^\circ\text{C}$ geothermometers | (1) Incised valley-thalweg knickzone convexity $\lambda_+(\text{det\_elev})>0 \times \|\nabla\log(\text{slope}+1^\circ)\|$; (2) Cross-contour transgression $|\mathbf{t}\cdot\nabla\text{det\_elev}|/\|\nabla\text{det\_elev}\|$ vs Lake Lahontan contour-parallel shoreline null; (3) Sliding-window Poisson's-relation magneto-gravity vector collinearity $|\nabla\text{RTP}\cdot\nabla g_{\text{iso}}|/(\|\nabla\text{RTP}\|\,\|\nabla g_{\text{iso}}\|)$; (4) `5 km` high-pass province-debiased strain anomaly + label-free within-quadrant LOQO quantile calibration | Sheetflooding bevels interfluve fan scarps in `NE` and piedmont aprons, but active dip-slip preserves incised channel thalweg knickpoints; Poisson magneto-gravity collinearity confirms basement steps; within-quadrant LOQO calibration eliminates `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` | First lane combining valley-thalweg knickpoint convexity ($\lambda_+>0$), explicit cross-contour shoreline-null deconfounding, Poisson magneto-gravity gradient collinearity, mesoscale (`50 px`) strain high-pass debiasing, and within-quadrant LOQO quantile calibration | **High** (`+5%` to `+15%` over `COULOMBLOQO` in `NE` and pooled `HOLDOUT-DTI`, while clearing `<=0.70` across all local & `dual_reading` public rasters) | **Low–Moderate** (~25 min compute, reuses `evaluate_holdout.py` & `submission_writer.py`) |
| **2** | **`TENSOR-RIEDEL`** | `Bands 2, 5, 7, 11, 12, 13, 18, 19` | Full 2D horizontal-vertical gravity gradient tensor $\mathbf{G}_h = \nabla_h(\nabla_h U_{\text{grav}})$ invariant ratio (Pedersen & Rasmussen 1990) + $15^\circ$–$25^\circ$ synthetic Riedel ($R$) obliquity between surface scarp strike and basement gravity-tensor strike | Transtensional step-overs and en-echelon Riedel relays in the Walker Lane / Humboldt belt host blind geothermal conduits where surface splays rotate $15^\circ$–$25^\circ$ off the deep master fault | `XPHASE` and `COULOMBLOQO` reward $0^\circ$ collinearity; `TENSOR-RIEDEL` targets $15^\circ$–$25^\circ$ en-echelon Riedel angular obliquity | **Moderate** (`+2%` to `+5%` in `SW` Walker Lane relays) | **Moderate** |
| **3** | **`FLEXURE-HINGE`** | `Bands 12, 13, 15, 18, 19` | Broken-plate elastic lithospheric flexural derivative wavelet ($\alpha_{\text{flex}} \approx 12$–$18\text{ km}$, Buck 1988) locating the inflection hinge between footwall uplift and hanging-wall differential compaction | Master range-front and synthetic accommodation faults buried under $150$–$500\text{ m}$ of fill express as long-wavelength flexural/compaction monoclines rather than brittle scarps | `PIEDFRONT`, `STEPEDGE`, and `APRONRIDGE` use short ($300$–$600\text{ m}$) scarp steps; none invert for the $5$–$15\text{ km}$ elastic flexural inflection locus | **Moderate** (`+1%` to `+4%` on basin-margin faults) | **Moderate** |
| **4** | **`CLAYCAP-REDOX`** | `Band 17`, GeoDAWN `K,Th,U`, `Band 2`, GDR #1391 | Paired second-derivative flank of electrically conductive smectite clay caps ($\nabla^2\log(\text{Band 17}+1)<0$) + mobile-uranium redox front $\|\nabla(U/\text{Th})\|$ + magnetite-destruction trough ($\nabla_h^2\text{RTP}>0$) | Blind hydrothermal upflow alters host rock into conductive smectite caps and precipitates $U$ at redox fronts above unmapped fault intersections with flat surface topography | `HYDROCONDUIT` and `COULOMBDM` use first-order $\|\nabla\text{Band 17}\|$ as a minor boost on scarps rather than solving for paired clay-cap flank curvature + $U/\text{Th}$ redox fronts | **Low–Moderate** (spatially restricted to active hydrothermal cells; coarse MT grid) | **Low** |
| **5** | **`VP-VS-BRITTLE`** | `Bands 1, 9, 10, 14, 16, 20` (`Band 6` excluded per `#IR-92-BAND6-TC-MISLABEL`) | Crustal thickness (`Band 1`) + heat-flow (`Band 9`) brittle-ductile transition depth gated by elevated $V_p/V_s > 1.78$ (`Band 16`) fluid-overpressure corridors and anisotropic earthquake swarm graphs along $S_{H,\max}$ (`Band 14`) | Fluid-pressured fracture networks in high-$V_p/V_s$ geothermal reservoirs host microseismic swarms along blind faults with zero surface scarp | `GEOTENSION` used regional stress (`Bands 3, 10, 14`) without $V_p/V_s$ fluid-overpressure gating; however, `Bands 1, 9, 16` have $>5\text{ km}$ native resolution | **Low** ($>5\text{ km}$ resolution exceeds the $300\text{ m}$ DTI kernel) | **Low** |

---

## 3. Mathematical Specification of Top Pick: `KNICKLOQO` (`gems/knick_loqo.py`)

### 3.1 New Physical Operators (Zero Fault-Catalogue Input)

1. **Incised Drainage Thalweg Knickzone Operator ($\mathcal{K}_{\text{thalweg}}$):**
   Let $z = \text{Band 12}$ (`det_elev`) and $s = \max(\text{Band 19}, 0)$ (`det_elev_slope`). At Gaussian scales $\sigma \in \{1.5, 3.0\}\text{ px}$ ($150\text{ m}, 300\text{ m}$), let $\lambda_1(z;\sigma) \ge \lambda_2(z;\sigma)$ be the eigenvalues of the 2D Hessian $\nabla^2 G_\sigma(z)$.
   - Whereas ridge crests have $\lambda_2 < 0$, **incised drainage thalwegs (ephemeral channels and fan washes)** have $\lambda_+(z;\sigma) = \max(\lambda_1(z;\sigma), 0) > 0$ (concave-up cross-channel profile).
   - When an incised channel crosses an active dip-slip fault, it forms a steep longitudinal slope-gradient break $B_{\text{slope}}(x) = \|\nabla G_{1.0}(\log(s + 1^\circ))\|_2$.
   - The **Thalweg Knickzone Index** is:
     $$\mathcal{K}_{\text{thalweg}}(x) = \max_{\sigma \in \{1.5, 3.0\}}\bigl[\sigma^2 \max(\lambda_1(z;\sigma), 0)\bigr] \cdot B_{\text{slope}}(x)$$
     which specifically lights up incised channel knickpoints along eroded piedmont fault traces where interfluve scarps have been beveled by sheetflooding.

2. **Tectonic Cross-Contour Transgression vs. Pluvial Lake Lahontan Shoreline Null ($\mathcal{T}_{\text{cross}}, \mathcal{S}_{\text{shore}}$):**
   Let $\mathbf{t}_{\text{ridge}}(x) = (-\sin\theta_{\text{elev}}, \cos\theta_{\text{elev}})$ be the unit tangent vector along the dominant topographic ridge/scarp strike $\theta_{\text{elev}}(x)$, and let $\mathbf{g}_z(x) = \nabla G_{2.0}(z)(x)$ be the local elevation gradient.
   - The **Cross-Contour Transgression Index** is the absolute cosine of the angle between the scarp tangent and the elevation gradient:
     $$\mathcal{T}_{\text{cross}}(x) = \frac{|\mathbf{t}_{\text{ridge}}(x) \cdot \mathbf{g}_z(x)|}{\|\mathbf{g}_z(x)\|_2 + \epsilon}$$
   - For a wave-cut Pleistocene Lake Lahontan shoreline bench, the bench follows a horizontal water-plane contour ($\mathbf{t}_{\text{ridge}} \perp \mathbf{g}_z \implies \mathcal{T}_{\text{cross}} \approx 0$) within the pluvial highstand elevation band and lacks subsurface gravity/basement support. For a tectonic fault scarp traversing coalescing alluvial fan lobes from apex to toe, $\mathcal{T}_{\text{cross}} > 0$.
   - We define the **Shoreline-Null Indicator**:
     $$\mathcal{S}_{\text{shore}}(x) = (1 - \mathcal{T}_{\text{cross}}(x))^2 \cdot \exp\Bigl(-\frac{\|\nabla G_{2.0}(\text{Band 15})\|_2}{\tau_{\text{base}}}\Bigr) \cdot (1 - \text{Tilt}_{\text{grav}}(x))$$
     giving the LOQO classifier both $\mathcal{T}_{\text{cross}}(x)$ (tectonic transgression) and $\mathcal{S}_{\text{shore}}(x)$ (contour-parallel non-tectonic bench null).

3. **Sliding-Window Poisson's-Relation Magneto-Gravity Concordance ($\mathcal{P}_{\text{Poisson}}$, Chandler et al. 1981):**
   Let $\mathbf{g}_{\text{mag}}(x) = \nabla G_{2.0}(\text{Band 2})(x)$ be the horizontal gradient of Reduced-to-Pole magnetic anomaly (`Band 2`) and $\mathbf{g}_{\text{grav}}(x) = \nabla G_{2.0}(\text{Band 13})(x)$ be the horizontal gradient of isostatic gravity (`Band 13`).
   - **Signed / Unsigned Vector Collinearity:**
     $$\mathcal{C}_{\text{vec}}(x) = \frac{|\mathbf{g}_{\text{mag}}(x) \cdot \mathbf{g}_{\text{grav}}(x)|}{\|\mathbf{g}_{\text{mag}}(x)\|_2 \, \|\mathbf{g}_{\text{grav}}(x)\|_2 + \epsilon}$$
   - **Vertical-Derivative & Tilt Concordance:** Combines $\mathcal{C}_{\text{vec}}(x)$ with the product of RTP Miller-Singh contact tilt and gravity contact tilt $\text{Tilt}_{\text{RTP}}(x) \cdot \text{Tilt}_{\text{grav}}(x)$ and vertical derivative concordance between $-\nabla_h^2 G_{2.0}(\text{Band 2})$ and $\text{Band 11}$ (`iso_grav_anom_vg`):
     $$\mathcal{P}_{\text{Poisson}}(x) = \mathcal{C}_{\text{vec}}(x) \cdot \sqrt{\text{Tilt}_{\text{RTP}}(x) \cdot \text{Tilt}_{\text{grav}}(x)}$$

4. **Mesoscale (`5 km`) Province-Debiased Covariates & Label-Free Within-Quadrant LOQO Calibration:**
   - For regional fields $f \in \{\text{Band 4}, \text{Band 7}, \text{Band 8}, \text{Band 12}, \text{Band 13}, \text{Band 15}, \text{Band 17}\}$ that exhibit strong inter-quadrant baseline shifts between the Humboldt/Owyhee interior (`NE`) and Walker Lane (`SW`), we compute mesoscale locally standardized anomalies relative to a $\sigma_{\text{reg}} = 45\text{ px}$ ($4.5\text{ km}$) regional background:
     $$\widetilde{f}(x) = \frac{f(x) - G_{45}(f)(x)}{\sqrt{G_{45}\bigl((f - G_{45}(f))^2\bigr)(x)} + \epsilon}$$
   - In 4-quadrant Leave-One-Quadrant-Out cross-fitting (`guard_px = 12`, `neg_buffer_px = 5.0`), after model $M_{-q}$ predicts out-of-quadrant probabilities $P_{-q}(x)$ on target quadrant $q \in \{0, 1, 2, 3\}$, we compute the **label-free within-quadrant empirical quantile rank** $Q_q(x) \in (0, 1]$ across valid pixels in quadrant $q$ and form the calibrated probability:
     $$P_{\text{cal}}(x) = (1 - \lambda_{\text{cal}}) P_{-q}(x) + \lambda_{\text{cal}} Q_q(x)^{\gamma}, \qquad \lambda_{\text{cal}} = 0.65,\ \gamma = 3.0$$
     This uses **zero target-quadrant fault labels** (100% leak-free under both static and strict draw-blind evaluation) and guarantees that `NE` is never starved by regional baseline shift.

---

## 4. Three Pre-Registered Experiments (Strict Rule 6 Budget = 3)

All three arms emit exactly $S = 37,654$ unit-mass (`1.0`) dots inside the valid footprint at $d_{\text{cat}} > 2.0\text{ px}$ (`> 200 m` outside mapped catalogue faults), formatted as all-finite `float32` `-zeros.tif` rasters (`0.0` outside footprint):

1. **Experiment 1 (`knickloqo_standalone`):**
   `100%` standalone (`37,654` dots, zero `H19-5` or `R0` skeleton input) selected from the 1D structural + thalweg-knickzone + Poisson-subsurface crest network of the full 30-feature province-debiased, quadrant-calibrated `KNICKLOQO` surface $S_{\text{knick}}(x)$ with inter-dot spacing `min_dist_px = 3.2` (slightly exceeding the $R = 3.0\text{ px}$ Tversky kernel radius so adjacent dots never waste self-credit $M > T$ or cluster on `SW` ridges).
2. **Experiment 2 (`knickloqo_uncal` — Pre-Registered Calibration Ablation):**
   `100%` standalone (`37,654` dots, zero `H19-5` or `R0` skeleton input) using the exact same 30-feature `KNICKLOQO` model and `min_dist_px = 3.2`, but **without** within-quadrant quantile calibration ($\lambda_{\text{cal}} = 0.0$), isolating the exact `HOLDOUT-DTI` and `NE`-quadrant recovery gain of fixing `#IR-92-NE-QUADRANT-LOQO-COLLAPSE`.
3. **Experiment 3 (`knickloqo_dual35` — Hybrid Skeleton + Knickpoint-Poisson Discovery):**
   `35%` (`13,179` dots) submodular expected-DTI repacked `H19-5` skeleton weighted by $S_{\text{knick}}(x)$ + `65%` (`24,475` dots) standalone 1D `KNICKLOQO` crests at $d_{\text{H19-5}} > 3.0\text{ px}$ (`min_dist_px = 3.2`).

### Pre-Registered Falsifier & Promotion Decision Rule
- **Leakage Canary (Rule 4):** Every individual band, derived feature, and out-of-fold surface must satisfy `symmetric ROC AUC <= 0.90` on the buffered holdout folds (`22,663` withheld positives).
- **Holdout Benchmark (Rule 2 & Rule 3):** Evaluate all 3 arms on `gems57-pooled-hide-v2` under (a) static `d_cat > 2.0`, (b) strict draw-blind `d_cat > 2.0`, and (c) strict draw-blind Rule-2 `d_visible > 2.0`, plus off-catalogue USGS SGMC proxy (`62,703` pixels). Target: beat `COULOMBLOQO standalone` (`0.009220` static `d_cat > 2.0` and `0.113316` strict draw-blind `d_visible > 2.0`) and cure `#IR-92-NE-QUADRANT-LOQO-COLLAPSE` (`NE` dot share restored from `11.2%` to `24%–28%`).
- **Uniqueness Gate (Rule 1):** Must achieve `<= 0.70` 3-px forward overlap and `|Spearman rho| <= 0.90` against **all** local rasters in `GEMSDOE92` AND **all** `1,415` public rasters under `dual_reading_decision` (`<= 150,000` px dot fields and `> 150,000` px matched-budget continuous surfaces). Because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` is positive on `100%` of the footprint (`5,167,373` pixels), the literal unweighted overlap (`1.000 > 0.70`) is reported transparently alongside the `dual_reading_decision` (`unique`), keeping `submission_eligible: false` and `verdict: "negative"` under the literal site gate (`scripts/check_site.py`).
