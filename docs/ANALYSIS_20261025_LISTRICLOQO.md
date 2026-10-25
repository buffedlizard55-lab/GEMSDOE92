# PhD Technical Analysis — `GEMSDOE32` (`0.2778` `[CLAIM]`) Derivation, Path Beyond `0.3195` / `0.4413`, and `LISTRICLOQO` Holdout & Registry Audit (`2026-10-25`)

**Repository:** `buffedlizard55-lab/GEMSDOE92` | **Branch:** `arena/a5100f33-gemsdoe92`  
**Evaluator:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, $\alpha=0.2$, $\beta=0.8$, $R=300\text{ m}=3\text{ px}$ triangular kernel, `22,663` withheld catalogue fault pixels across `8` buffered spatial-quadrant folds, Seeds `20` & `30`, `1,000` paired `20 km` spatial-cluster bootstrap draws)  
**Pre-Registered Hypotheses:** [`docs/HYPOTHESES_20261025_LISTRICLOQO.md`](HYPOTHESES_20261025_LISTRICLOQO.md)  
**Run Card JSON:** [`evidence/listric_loqo_run_card.json`](../evidence/listric_loqo_run_card.json) | [`docs/downloads/listric_loqo_run_card.json`](downloads/listric_loqo_run_card.json)

---

## 1. PhD-Level Derivation: Why and How `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778` `[CLAIM]`) Achieved Its Score

> **Evidence Classification Notice (Protocol Rule 3):** Throughout this document, every number is explicitly labeled by its evidence class:
> - **`HOLDOUT-DTI`** (`gems57-pooled-hide-v2`, `22,663` withheld positives, 95% bootstrap CI);
> - **`PROXY`** (`62,703` off-catalogue USGS SGMC bedrock fault pixels at $>3\text{ px}$ from `existing_faults.tif`);
> - **`REGISTRY-MEASUREMENT`** (exact SHA-256 / Git-blob 3-px forward overlap and Spearman rank correlation);
> - **`CLAIM`** (unverified historical scores quoted in user prompts without an organizer submission-page receipt in `ledger/submissions.csv`, where `0` rows have `status == "RECEIPT"`);
> - **`LEADERBOARD-SNAPSHOT`** (`0.4413` public #1 recorded on `2026-10-24`; `0.3195` older prompt-quoted snapshot).

### 1.1 Exact Mathematical Structure of the Distance-Weighted Tversky Index ($\alpha = 0.2, \beta = 0.8$)

Per the [Official DOE GEMS Prize Rules (NREL/NLR PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf), the [Competition Problem Description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), and `vendor/gems57/metric.py`, submissions are evaluated on a $3730 \times 3292$ raster grid in `EPSG:32611` (NAD83 / UTM Zone 11N, $100\text{ m}$ pixel spacing, $5{,}167{,}373$ valid footprint pixels). Let $\Omega \subset \mathbb{Z}^2$ be the valid footprint, $G_{\text{vis}} \subset \Omega$ be the公开 mapped fault catalogue (`existing_faults.tif`, $|G_{\text{vis}}| = 60{,}988$ pixels), and $G_{\text{hid}} \subset \Omega \setminus G_{\text{vis}}$ be the withheld evaluation fault set.

For a predicted raster $\hat{y}: \Omega \to [0, 1]$ after masking visible catalogue pixels ($\hat{y}(x) \leftarrow 0$ on $G_{\text{vis}}$) and the $300\text{ m}$ ($R = 3\text{ px}$) radial linear-decay proximity kernel:
$$K(d) = \max\!\left(0,\; 1 - \frac{d}{R}\right), \qquad R = 3.0\text{ px}\ (300\text{ m}),$$
let $d_{\text{truth}}(x) = \min_{g \in G_{\text{hid}}} \|x - g\|_2$ and $d_{\text{pred}}(g) = \min_{x:\,\hat{y}(x)>0} \|g - x\|_2$. For a binary dot field $\hat{y}(x) \in \{0, 1\}$ with total emitted mass $S = \sum_{x \in \Omega \setminus G_{\text{vis}}} \hat{y}(x)$:
$$\text{TP}_w(\hat{y}) = \sum_{x \in \Omega \setminus G_{\text{vis}}} \hat{y}(x)\,K\bigl(d_{\text{truth}}(x)\bigr), \qquad \text{FP}_w(\hat{y}) = S - \text{TP}_w(\hat{y}),$$
$$\text{FN}_w(\hat{y}) = \sum_{g \in G_{\text{hid}}} \Bigl(1 - K\bigl(d_{\text{pred}}(g)\bigr)\Bigr).$$
The Distance-Weighted Tversky Index with false-positive weight $\alpha = 0.2$ and false-negative weight $\beta = 0.8$ ([Tversky 1977](https://en.wikipedia.org/wiki/Tversky_index)) is:
$$\text{DTI}_{0.2, 0.8}(\hat{y}, G_{\text{hid}}) = \frac{\text{TP}_w(\hat{y})}{\text{TP}_w(\hat{y}) + 0.2\,\text{FP}_w(\hat{y}) + 0.8\,\text{FN}_w(\hat{y})} = \frac{\text{TP}_w(\hat{y})}{0.8\,\text{TP}_w(\hat{y}) + 0.2\,S + 0.8\,\text{FN}_w(\hat{y})}.$$

Taking the first variation with respect to adding $\Delta S$ dots of marginal expected proximity overlap $\mu_{\text{add}} = \mathbb{E}[K(d_{\text{truth}}(x))]$ around an operating point $(S_0, \text{DTI}_0)$ yields the exact marginal break-even threshold:
$$\frac{\partial \text{DTI}}{\partial S}\bigg|_{S_0} > 0 \iff \mu_{\text{add}}(x) > \tau^*(\text{DTI}_0) = \frac{\alpha\,\text{DTI}_0}{1 - \beta\,\text{DTI}_0} = \frac{0.2\,\text{DTI}_0}{1 - 0.8\,\text{DTI}_0}.$$
- At $\text{DTI}_0 = 0.1922$ (`H19-5` `[CLAIM]`): $\tau^*(0.1922) = \frac{0.03844}{0.84624} = 0.04543$. Any pixel whose expected proximity credit is below $4.54\%$ (specifically, any pixel inside the $d_{\text{cat}} \le 2.8\text{ px}$ halo of an already-mapped fault where $G_{\text{hid}}$ is absent outside tip continuations) has $\mu_{\text{add}} \approx 0 < \tau^*$ and strictly degrades the denominator by $+0.2$ per pixel.
- At $\text{DTI}_0 = 0.2778$ (`R0` `[CLAIM]`): $\tau^*(0.2778) = \frac{0.05556}{0.77776} = 0.07144$.
- At $\text{DTI}_0 = 0.4413$ (`LEADERBOARD-SNAPSHOT`): $\tau^*(0.4413) = \frac{0.08826}{0.64696} = 0.13642$.

### 1.2 Pixel-Exact Constructive Lineage of `R0` (`h33-h33-2-b2`, Verified by `python3 -m gems parent`)

Rebuilding `R0` from the SHA-256-verified lineage rasters in `.cache/gems_inputs/lineage/` (`registry/parents/R0.json`, verified to `sha256 = c55bafc4f062...` on `-zeros.tif` and `337d3d9d9a45...` on `-nan.tif`) proves an **exact nested set inclusion**:
$$R_0\ (37{,}654\text{ px}) \;\subset\; \text{H27-4-SOLO}\ (40{,}199\text{ px}) \;\subset\; \text{D2.8}\ (44{,}090\text{ px}) \;\subset\; \text{H19-5}\ (121{,}131\text{ px}).$$

| Lineage Stage | Support $S$ (Dots) | Geometric / Physical Operation | Denominator Penalty $0.2\,S$ | Historical Score (`[CLAIM]`) | Mathematical Mechanism of Score Gain |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **`H19-5`** (`calib_h195_01922.tif`) | `121,131` | Binary $\{0, 1\}$ morphological skeleton of DEM break-of-slope (`Bands 12, 19`) + gravity/magnetic edges | `24,226.2` | `0.1922` `[CLAIM]` | High recall along surface scarps, but `77,041` dots ($63.6\%$) lie within $d_{\text{cat}} \le 2.8\text{ px}$ of known catalogue faults where $\mu_{\text{add}} \approx 0$, bloating $0.2\,\text{FP}_w$ by $+15{,}408.2$. |
| **`D2.8`** (`gems25-dotted-h19-5-d2-8`) | `44,090` | Hard Euclidean collar exclusion: retain only $x \in \text{H19-5}$ with $d_{\text{cat}}(x) > 2.8\text{ px}$ | `8,818.0` | `0.2647` `[CLAIM]` (`+0.0725`) | Eliminates `77,041` zero-credit collar false positives ($\Delta(0.2\,\text{FP}_w) = -15{,}408.2$, a $-63.6\%$ reduction in false-positive denominator drag) while losing almost zero $\text{TP}_w$ on unmapped faults. |
| **`H27-4-SOLO`** (`GEMSDOE28__h27-4-r1-solo-d2-8`) | `40,199` | Connected-component / isolated-speckle pruning inside `D2.8` | `8,039.8` | `0.2735` `[CLAIM]` (`+0.0088`) | Prunes `3,891` short, low-coherence erosional drainage speckles inside `D2.8` ($\Delta(0.2\,\text{FP}_w) = -778.2$). |
| **`R0` (`h33-h33-2-b2`)** (`parent_R0_zeros.tif`) | `37,654` | Relax collar from $d_{\text{cat}} > 2.8$ to $d_{\text{cat}} > 2.0\text{ px}$ (`+2,171` fault-tip/stepover collar pixels in $2.0 < d_{\text{cat}} \le 2.8$) + raster scan-order budget cap to `37,654` | `7,530.8` | `0.2778` `[CLAIM]` (`+0.0043`) | Recovers `2,171` high-credit along-strike fault-tip extensions and relay-ramp step-overs at $200\text{--}280\text{ m}$ from mapped fault tips while trimming `4,716` southern scan-order pixels. |

### 1.3 Why `R0` (`GEMSDOE32`) Plateaued and How to Surpass `0.2778` / `0.3195` / `0.4413`

Despite its surgical denominator pruning, `R0` has four fundamental physical ceilings verified by direct measurement in this repository:
1. **`H19-5` Is Strictly Binary (`{0.0, 1.0}`):** Every pixel in `data/bridge/h19_5.tif` has value $0.0$ or $1.0$. Consequently, `R0` has no continuous physical ranking and cannot distinguish a tectonic normal fault with a $500\text{ m}$ hanging-wall basin step from a non-faulted alpine cliff or Lake Lahontan shoreline.
2. **Zero Off-Skeleton Discovery ($R_0 \subset \text{H19-5}$):** `100%` of `R0`'s `37,654` dots lie on the `H19-5` topographic break-of-slope skeleton. On our spatially-blocked holdout (`gems57-pooled-hide-v2`, `22,663` withheld positives), `R0` scores only **`0.004006 [0.003408, 0.004651]` `HOLDOUT-DTI`** on static `d_cat > 2.0` (`H19-5` skeleton scores `0.096757` on `d_visible > 2.0`), because buried intrabasin faults, piedmont accommodation splays, and blind INGENIOUS geothermal conduits (`39%` of Great Basin geothermal systems; [Faulds & Hinz 2015](https://gbcge.org/current-projects/ingenious/)) lack a sharp surface break of slope at $x_0$.
3. **Zero Dip-Offset Correction for $45^\circ\text{--}60^\circ$ Normal Faults:** Range-front and intrabasin normal faults dip at $45^\circ\text{--}60^\circ$ into the hanging-wall basin (Okaya & Thompson 1985; Wernicke 1995). The subsurface gravity (`Bands 5, 11, 13, 18`), basement depth (`Band 15`), RTP magnetic (`Band 2`), and MT smectite clay-cap (`Band 17`) gradients peak $300\text{--}500\text{ m}$ ($3\text{--}5\text{ px}$) **downslope in the hanging wall** relative to the surface trace $x_0$. Evaluating surface and subsurface features only at $\Delta r = 0$ misses the physical coupling between the surface Wallace basal toe and its down-dip hanging-wall basin step.
4. **Regional Walker Lane vs. Interior Basin Covariate Shift (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`):** Geodetic strain rates (`Bands 4, 7, 8`) drop by $6.4\times\text{--}8.5\times$ from the `SW` Walker Lane to the `NE` Humboldt/Owyhee interior, starving uncalibrated models in `NE` (`11.2%` dots in `COULOMBLOQO`), whereas naive uniform 4-quadrant equalization over-penalizes `SW` fault density.

---

## 2. Empirical Validation of `LISTRICLOQO` (`gems/listric_loqo.py`)

### 2.1 Rule-4 Single-Feature Leakage Canary (`evidence/listric_loqo_screen.json`)

Every raw band, all `36` catalogue-free physical features (Groups A–G), and all `LOQO` probability/crest surfaces were tested individually on the `8` buffered holdout folds (`22,663` withheld positives, Seeds `20` & `30`) BEFORE building any candidate GeoTIFF:
- **Maximum symmetric ROC AUC across all 56 features & surfaces:** **`0.674631 <= 0.90`** (`LOQO_P_cal`) — **ALL PASS (`0` leaks)**.
- **New Group-G `LISTRICLOQO` Operators (Single-Feature Out-of-Fold Canary AUCs):**
  - `wallace_basal_toe_asym` ($\mathcal{W}_{\text{toe}}$): **`0.603377`**
  - `listric_fw_downdip_splay` ($\Phi_{\text{listric}}^{\text{dn}}$): **`0.582676`**
  - `listric_hw_updip_pullback` ($\Phi_{\text{listric}}^{\text{up}}$): **`0.571519`**
  - `grav_tensor_contact_ecc` ($\mathcal{E}_{\text{tensor}}$): **`0.550586`**
  - `riedel_en_echelon_coupling` ($\mathcal{R}_{\text{Riedel}}$): **`0.546813`**
  - `grav_tensor_3d_tilt` ($\Theta_{\text{3D}}$): **`0.526580`**
  - `LOQO_P_cal` (selective-calibrated 36-feature 3-branch LOQO): **`0.674631`** (up **`+0.015029`** over `KNICKLOQO`'s `0.659602`)
  - `LOQO_draw_blind_S_cal` (strict draw-blind OOF surface): **`0.669933`** (up **`+0.019953`** over `KNICKLOQO`'s `0.649980`)

### 2.2 Spatially-Blocked Holdout & Off-Catalogue SGMC Proxy Results (`evidence/listric_loqo_proxy_audit.json`)

| Candidate / Baseline | Static `d_cat > 2.0` `HOLDOUT-DTI` `[95% CI]` | Paired $\Delta$ vs `LISTRICLOQO standalone` `[95% CI]` | Strict Draw-Blind `d_cat > 2.0` `HOLDOUT-DTI` `[95% CI]` | Strict Draw-Blind `d_visible > 2.0` `HOLDOUT-DTI` `[95% CI]` | Off-Catalogue `USGS SGMC PROXY` (`62,703` px) | Worst Local Overlap (`79` rasters) | Public `dual_reading` Verdict (`<=0.70`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`LISTRICLOQO standalone` (`293bc624`) — NEW #1** | **`0.012034` `[0.010422, 0.013591]`** | — *(Reference)* | **`0.011440` `[0.009888, 0.012893]`** | **`0.111159` `[0.098186, 0.123409]`** | `0.093533` | **`0.693817 <= 0.70`** (`PASS`) | **`0.693817 <= 0.70`** (`unique`, `0` over `0.70`) |
| **`LISTRICLOQO nolistric` (`f0caed0e`) — #2** | **`0.011543` `[0.009986, 0.013053]`** | **`+0.000490` `[+0.000181, +0.000838]`** | — *(Ablation)* | `0.107412 [0.094441, 0.120305]` | `0.092089` | **`0.640968 <= 0.70`** (`PASS`) | **`0.648165 <= 0.70`** (`unique`, `0` over `0.70`) |
| **`KNICKLOQO standalone` (`d53d919f`) — Prev #1** | `0.010788 [0.009438, 0.012150]` | **`+0.001246` `[+0.000115, +0.002272]`** | `0.010958 [0.009675, 0.012337]` | `0.109043 [0.097872, 0.120534]` | `0.103912` | `0.685531 <= 0.70` | `0.685531 <= 0.70` (`unique`) |
| **`LISTRICLOQO dual35` (`c3c4bba3`)** | `0.009783 [0.008521, 0.011079]` | **`+0.002250` `[+0.001383, +0.003152]`** | — *(Hybrid)* | `0.101459 [0.090204, 0.112552]` | `0.095682` | **`0.694508 <= 0.70`** (`PASS`) | **`0.694508 <= 0.70`** (`unique`, `0` over `0.70`) |
| **`PROVINCETOE provincetoe` (`8b69d44e`)** | `0.009685 [0.008329, 0.011116]` | **`+0.002349` `[+0.001299, +0.003429]`** | `0.009711 [0.008385, 0.011168]` | `0.106452 [0.094462, 0.118749]` | `0.094095` | `0.674696 <= 0.70` | `0.791842 > 0.70` (`62GEMSDOE`) |
| **`POISSONKNICK qcal` (`9cfcc9b9`)** | `0.009304 [0.008005, 0.010704]` | **`+0.002729` `[+0.001356, +0.004060]`** | `0.009304 [0.007836, 0.010810]` | `0.098491 [0.086942, 0.110054]` | `0.081106` | `0.645668 <= 0.70` | `0.625432 <= 0.70` (`unique`) |
| **`EULERFUSE gravity` (`d7133700`)** | `0.009265 [0.007887, 0.010665]` | **`+0.002769` `[+0.001460, +0.004032]`** | — | `0.110387 [0.097754, 0.123996]` | `0.085383` | `0.828703 > 0.70` | `0.828703 > 0.70` (`COULOMBLOQO`) |
| **`COULOMBLOQO standalone` (`e01d27af`)** | `0.009220 [0.007983, 0.010493]` | **`+0.002814` `[+0.001552, +0.004050]`** | `0.009689 [0.008374, 0.011014]` | `0.113316 [0.100614, 0.127163]` | `0.090569` | `0.828703 > 0.70` | `0.828703 > 0.70` (`EULERFUSE` / `GEMSDOE23`) |
| **`R0` (`h33-h33-2-b2`, parent)** | `0.004006 [0.003408, 0.004651]` | **`+0.008028` `[+0.006640, +0.009424]`** | `0.004006 [0.003408, 0.004651]` | `0.096757 [0.084839, 0.108454]` *(H19-5)* | `0.096060` | — | `1.000` *(self in registry)* |

### 2.3 Key Scientific Takeaways from the 3 Pre-Registered Experiments

1. **New All-Time Repository Record on Static `d_cat > 2.0` (`0.012034`) and Strict Draw-Blind `d_cat > 2.0` (`0.011440`):**
   `LISTRICLOQO standalone` (`h33-h33-2-b2-LISTRICLOQOstandalone-20261025-293bc624-zeros.tif`, SHA-256 `f431957f5d63759c7f9de3f09e133323957b508855800ebb14d95ed766d87898`, ZIP SHA-256 `bc71ea63f72c7d02b9d1bc2c063ae0b5bfb8d41d2c0ae4ccf6f09850e58af116`) achieves **`0.012034 [0.010422, 0.013591]` `HOLDOUT-DTI`**, beating the previous repository #1 `KNICKLOQO standalone` (`0.010788`) by **`+11.55%`** (paired bootstrap $\Delta = +0.001246$, 95% CI `[+0.000115, +0.002272]`, strictly positive), beating `PROVINCETOE` (`0.009685`) by **`+24.25%`**, beating `COULOMBLOQO standalone` (`0.009220`) by **`+30.52%`**, and beating parent `R0` (`0.004006`) by **`+200.40%` (`3.00x`)**.
2. **Selective Subsurface-Branch Quadrant Calibration Beats Uncalibrated Ablation on Every Metric (`standalone` vs. `nolistric`):**
   Comparing Experiment 1 (`standalone`) against Experiment 2 (`nolistric` uncalibrated ablation) proves that selective subsurface-branch quadrant calibration lifts static `d_cat > 2.0` `HOLDOUT-DTI` from `0.011543` to `0.012034` (paired $\Delta = +0.000490$, 95% CI `[+0.000181, +0.000838]`) and lifts strict draw-blind `d_visible > 2.0` `HOLDOUT-DTI` from `0.107412` to **`0.111159`** (paired $\Delta = +0.003747$, 95% CI `[+0.001368, +0.006282]`), restoring `NE` (`Q1`) allocation from `4,904` dots (`13.0%` in `nolistric`) to `9,430` dots (`25.0%` in `standalone`) and lifting `Seed 20 NE` DTI by **`+66.0%`** (`0.008057 -> 0.013375`) and `Seed 30 NE` DTI by **`+35.1%`** (`0.012872 -> 0.017393`).
3. **100% Standalone `LISTRICLOQO` Beats the 35% `H19-5` Hybrid (`standalone` vs. `dual35`):**
   Anchoring `35%` (`13,179` dots) on the legacy `H19-5` skeleton (`dual35`) reduces static `d_cat > 2.0` `HOLDOUT-DTI` from `0.012034` to `0.009783` (`-0.002250`) and reduces strict draw-blind `d_visible > 2.0` from `0.111159` to `0.101459` (`-0.009700`), confirming that `100%` standalone 1D listric-scarp + down-dip splay + gravity-tensor/Riedel crests dominate `H19-5` skeleton hybrids.
4. **Uniqueness Across All 79 Local Rasters and All Public Dual-Reading Witnesses:**
   All three `LISTRICLOQO` arms pass `<= 0.70` 3-px forward overlap and `|Spearman| <= 0.90` against all `79` unique local rasters (`standalone` max `= 0.693817`, `nolistric` max `= 0.640968`, `dual35` max `= 0.694508`) and all Git-blob-verified public witnesses under `dual_reading_decision` (`standalone` max public dot-field overlap `= 0.671482 <= 0.70` vs `GEMSDOE52` `61,427` px; `62GEMSDOE` `120,000` px `= 0.630796 <= 0.70`; `GEMSDOE23 h29` `100,000` px `= 0.658974 <= 0.70`; `17GEMSDOE` `5,167,373` px matched-budget `= 0.057311 <= 0.70`). Under the literal unweighted `> 70%` public overlap clause (`SESSION_PROMPT.md`), `17GEMSDOE E-proba-multiscale` (`100%` footprint positive) yields literal overlap `1.000`, so `verdict = "negative"` and `submission_eligible = false` are preserved (`OK TO DOWNLOAD FOR RESEARCH — DO NOT SUBMIT TO A LIVE WEEKLY COMPETITION SLOT`).
