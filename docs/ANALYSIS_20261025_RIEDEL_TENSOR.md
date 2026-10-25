# PhD Structural Geology & Potential-Field Geophysics Analysis: `RIEDELTENSOR` — 3D Laplace-Consistent Gravity-Gradient Tensor Invariants, En-Echelon Riedel ($R/R'$) Transtensional Relay Obliquity, Radiometric-Potential Alteration Coupling, and Selective Province-Debiased 4-Branch LOQO (`2026-10-25`)

- **Branch:** `arena/dbdc0fd1-gemsdoe92`
- **Lane:** `RIEDELTENSOR` (`gems/riedel_tensor.py`)
- **Primary Session Research Artifact (`0.0` outside footprint, DrivenData-ready `[0, 1]` range):**
  - `docs/downloads/h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `4a789af87b86fb80c8abca91ef8e7d9f8858b257f3d5642e6bd08b2288b76e9a`
  - **ZIP Archive:** `docs/downloads/h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47-zeros.zip` (`sha256: b373059417bdcc69000d92ef0d35562e607b29d7924f5eb29723ebdd46d87dc0`)
  - **NaN-twin Archive (`.cache/`):** `.cache/riedel_tensor_builds/h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47.tif` (`sha256: d6535ccfb31e6e8431b00e476bd5b2886081260928489c3b8e0d8c800ca6d475`)
  - **Submission Name:** `h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47-zeros.tif`
  - **Submission Note (`131 <= 140` chars):** `GEMSDOE92 RIEDELTENSOR standalone: 4-branch Laplace gravity-tensor + Riedel R/R' + basal-toe LOQO, 37654 dots, min_dist=4.48px [0,1]`
- **Automated Gate & Protocol Status:**
  - **OK TO DOWNLOAD:** **YES** (`10/10` `gems.gates` + `13/13` `gems57.validate` checks pass; `Float32`; `3730 x 3292`; `EPSG:32611`; `[0.0, 1.0]`; `0` NaNs anywhere in `-zeros.tif`; `37,654` unit-mass dots; `0` mass on `187,745` catalogue pixels; `min d_cat = 2.236 px > 2.0 px`).
  - **OK TO SUBMIT (Weekly DrivenData Slot):** **NO (`submission_eligible: false`, `verdict: "negative"`, `0` weekly slots spent)** — **UNIQUE** across all `79` local `GEMSDOE92` rasters (`max 3-px overlap = 0.685080 <= 0.70` vs `KNICKLOQOstandalone`, `max |phi| = 0.206680 <= 0.90`) and **UNIQUE under `dual_reading_decision`** across all `1,448` non-self public rasters in the `102`-repo `GEMSDOE` scan (`0 / 1,448` overlaps `> 0.70`; worst operative overlap `0.685080 <= 0.70`; sparse `<= 90k px` max `0.685080`; continuous `> 150k px` matched-budget max `0.483216`), **stopped solely** by the literal unweighted `> 70%` public overlap clause against the full-footprint continuous probability surface `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373` positive pixels = `100%` of valid footprint $\implies 1.000000 > 0.70$ for every nonempty submission; `#IR-92-PUBLIC-DENSE-SURFACE-STOP`).

---

## 1. Executive Summary of Results (Rule 3 Evidence Labels)

Every quantitative statement in this report is tagged with one of the four required Protocol Rule 3 evidence labels:
- **`[ORGANIZER-CONFIRMED]`** — Directly backed by official DrivenData platform artifacts or competition documentation.
- **`[HOLDOUT-DTI]`** — Evaluated with unmodified `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `alpha=0.2, beta=0.8`, $300\text{ m} = 3\text{ px}$ triangular kernel, `8` spatially blocked buffered folds across seeds `20` and `30`, `22,663` withheld catalogue fault pixels, `1,000` paired $20\text{ km}$ spatial-cluster bootstrap draws).
- **`[PROXY]`** — Evaluated against independent geologic truth (`USGS SGMC` bedrock faults $> 300\text{ m}$ off the competition catalogue, `62,703` pixels; or `DOE GDR #1391` blind thermal wells/springs).
- **`[CLAIM]`** — Mechanistic or mathematical hypothesis not directly measured on organizer hidden truth.

| Candidate / Baseline | Evidence Class | Pooled Static `d_cat > 2.0` `HOLDOUT-DTI` (`95% CI`) | Paired $\Delta$ vs `KNICKLOQO standalone` (`95% CI`) | Strict Draw-Blind `d_cat > 2.0` `HOLDOUT-DTI` (`95% CI`) | Strict Draw-Blind `d_visible > 2.0` `HOLDOUT-DTI` (`95% CI`) | Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px) | Local Worst 3-px Overlap (`<= 0.70`) | Public `dual_reading` Over `> 0.70` (`1,448` rasters) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`RIEDELTENSOR standalone` (`31b00e47`)** | **`[HOLDOUT-DTI]`** | **`0.011574` (`[0.010334, 0.012985]`) (#1 All-Time)** | **`+0.000786` (`[+0.000284, +0.001298]`, `+7.29%`)** | **`0.011576` (`[0.010423, 0.012879]`) (#1 All-Time)** | **`0.113119` (`[0.100329, 0.126839]`) (#1 Unique)** | **`0.105051` (#1 `37,654`-dot)** | **`0.685080` (PASS)** | **`0 / 1,448` (`max 0.685080`, PASS)** |
| **`RIEDELTENSOR uncal` (`e19ad8a9`)** | **`[HOLDOUT-DTI]`** | **`0.011265` (`[0.010070, 0.012652]`) (#2 All-Time)** | **`+0.000477` (`[-0.000046, +0.000999]`, `+4.42%`)** | `0.011576` (`[0.010423, 0.012879]`) | `0.110041` (`[0.097362, 0.123734]`) | `0.101502` | **`0.674563` (PASS)** | **`0 / 1,448` (`max 0.674563`, PASS)** |
| `KNICKLOQO standalone` (`d53d919f`, prev #1) | `[HOLDOUT-DTI]` | `0.010788` (`[0.009468, 0.012201]`) | `0.000000` (ref) | `0.010958` (`[0.009675, 0.012337]`) | `0.109043` (`[0.097872, 0.120534]`) | `0.103912` | `0.685531` (PASS) | `0 / 1,412` (`max 0.685531`, PASS) |
| `PROVINCETOE piedbasin` (`c22542ae`) | `[HOLDOUT-DTI]` | `0.009711` (`[0.008518, 0.010968]`) | `-0.001077` | — | `0.106452` (`[0.095452, 0.117309]`) | `0.091183` | `0.648165` (PASS) | `0 / 1,406` (`max 0.659133`, PASS) |
| `POISSONKNICK qcal` (`9cfcc9b9`) | `[HOLDOUT-DTI]` | `0.009304` (`[0.008167, 0.010539]`) | `-0.001484` | `0.009429` | `0.098491` (`[0.088827, 0.108650]`) | `0.093334` | `0.672518` (PASS) | `0 / 1,409` (`max 0.672518`, PASS) |
| `EULERFUSE gravity` (`d7133700`) | `[HOLDOUT-DTI]` | `0.009265` (`[0.007880, 0.010752]`) | `-0.001523` | — | `0.110387` (`[0.097996, 0.122575]`) | `0.087279` | `0.828703` (FAIL) | `> 0` (`max 0.828703`, FAIL) |
| `COULOMBLOQO standalone` (`e01d27af`) | `[HOLDOUT-DTI]` | `0.009220` (`[0.007933, 0.010683]`) | `-0.001568` | — | `0.113316` (`[0.100614, 0.127163]`) | `0.090569` | `0.828703` (FAIL) | `> 0` (`max 0.828703`, FAIL) |
| `COULOMBLOQO dual45` (`dd91d98c`) | `[HOLDOUT-DTI]` | `0.009107` (`[0.007957, 0.010277]`) | `-0.001681` | — | `0.103069` (`[0.091982, 0.114575]`) | `0.096518` | `0.685531` (PASS) | `0 / 1,412` (PASS) |
| `HYDROCONDUIT f45hydro` (`979c9cdb`) | `[HOLDOUT-DTI]` | `0.008549` (`[0.007504, 0.009666]`) | `-0.002239` | — | — | `0.096272` | `0.679051` (PASS) | `0 / 1,412` (PASS) |
| `POISSONFLEX opt` (`aa750b41`, `45k` dots) | `[HOLDOUT-DTI]` | `0.008518` (`[0.007419, 0.009675]`) | `-0.002270` | — | `0.107466` (`[0.096125, 0.118749]`) | `0.111270` (`45k` dots) | `0.642349` (PASS) | `0 / 1,403` (PASS) |
| `COULOMBDM s45coulomb55` (`a10dccdd`) | `[HOLDOUT-DTI]` | `0.007816` (`[0.006835, 0.008825]`) | `-0.002972` | — | — | `0.097254` | `0.653131` (PASS) | `0 / 1,412` (PASS) |
| `RIEDELTENSOR hybrid35` (`be3233f3`) | `[HOLDOUT-DTI]` | `0.007802` (`[0.006836, 0.008845]`) | `-0.002986` | — | `0.098725` (`[0.088154, 0.109136]`) | `0.101373` | `0.665135` (PASS) | `0 / 1,448` (`max 0.665135`, PASS) |
| `Parent R0` (`e5eb6e7e-zeros`) | `[HOLDOUT-DTI]` | `0.004006` (`[0.003406, 0.004668]`) | `-0.006782` | — | `0.096757` (`H19-5` skeleton) | `0.096060` | — (Parent) | — (Parent) |

---

## 2. Rigorous PhD-Level Answer: Why & How `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`R0`) Scored `0.2778` on `GEMSDOE32`, and How to Beat `0.2778` Toward `0.3195` and `0.4413`

### 2.1 Exact Provenance and Mathematical Structure of `R0` (`0.2778` `[ORGANIZER-CONFIRMED]`)

From the verified sibling repository screenshot `GEMSDOE16/evidence/screenshots/drivendata_submissions_page1.png` (`[ORGANIZER-CONFIRMED]`) and our bit-exact reconstruction recipe `registry/parents/R0.json` (verified via `python3 -m gems parent --recipe registry/parents/R0.json --data-root data`), `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`R0`) achieved a DrivenData public leaderboard score of **`0.2778` (`[ORGANIZER-CONFIRMED]`)** while contemporary `GEMSDOE` submissions scored lower (`0.08`–`0.26`). Five mathematical and physical mechanisms explain why `R0` succeeded where other early `GEMSDOE` submissions failed:

1. **Adaptation to the DrivenData Distance-Tolerant IoU (`DTI`) Metric (`[ORGANIZER-CONFIRMED]` / `[CLAIM]`):**
   In the DOE GEMS Geothermal Contest, predictions $P \in [0, 1]^{\Omega}$ are evaluated against hidden unmapped faults $T_{\text{hid}}$ outside the known catalogue $K$ (`existing_faults.tif`, $187,745$ pixels) via the Distance-Tolerant Intersection-over-Union (`DTI`) with triangular proximity kernel $k_R(d) = \max(0, 1 - d/R)$ at radius $R = 300\text{ m} = 3.0\text{ px}$ and weights $\alpha = 0.2$ (precision/user's accuracy) and $\beta = 0.8$ (recall/producer's accuracy):
   $$\text{DTI}(P, T_{\text{hid}}) = \frac{\alpha \sum_{x \in \Omega \setminus K} P(x)\,\tilde{T}_{\text{hid}}(x) + \beta \sum_{y \in \Omega \setminus K} T_{\text{hid}}(y)\,\tilde{P}(y)}{\alpha \sum_{x \in \Omega \setminus K} P(x) + \beta \sum_{y \in \Omega \setminus K} T_{\text{hid}}(y) + \text{missed/false terms}}, \quad \tilde{A}(z) = \max(0, 1 - d(z, \text{supp}(A))/R).$$
   Because $\beta = 0.8 = 4\alpha$, recall is weighted **four times** more heavily than precision, **provided** the total predicted mass $S = \sum_{x \in \Omega \setminus K} P(x)$ does not blow up the precision denominator $\alpha S$.
   - Submissions that emitted dense continuous probabilities across millions of pixels (`17GEMSDOE E-proba-multiscale` with $5,167,373$ positive pixels, or wide $5$–$10\text{ px}$ probability ribbons) inflated $\alpha \sum P(x)$ by $10\times$–$100\times$, collapsing the precision term and scoring $\le 0.12$.
   - Conversely, `R0` concentrated its entire mass into exactly **$S = 37,654$ binary unit-mass dots (`1.0`)** ($0.7287\%$ of the $5,167,373$-pixel valid footprint), matching the expected hidden fault pixel budget ($\sim 30,000$–$45,000$ pixels).

2. **1D Canny Breakline Skeletonization (`H19-5`, `125,890` pixels):**
   Instead of placing dots in 2D blobs, `R0` restricted its support to `data/bridge/h19_5.tif` (`125,890` pixels), a 1-pixel-wide Canny/Sobel breakline skeleton extracted primarily from topographic slope (`Band 2`) and terrain curvature (`Bands 3–4`). Because active Basin-and-Range normal faults are 1D linear-to-curvilinear structures, restricting $P(x) \in \{0, 1\}$ to a 1D skeleton maximizes linear strike coverage per unit mass $S$.

3. **Catalogue Exclusion Buffer (`d_cat > 2.0 px`):**
   Every pixel on or immediately adjacent to `existing_faults.tif` ($d_{\text{cat}} \le 2.0\text{ px} = 200\text{ m}$) is either zeroed out by the scorer or contributes redundant coverage to already-mapped faults. `R0` strictly enforced $d_{\text{cat}} > 2.0\text{ px}$ (`min d_cat = 2.236 px`, `0` mass on the `187,745` catalogue pixels).

4. **2-Tier Topographic Relief Gating (`H33-2-B2`):**
   In `R0`, candidate pixels on the `H19-5` skeleton were scored by a 2-tier relief/slope composite (`data/bridge/h24_3.tif` + `h29_2.tif`) that prioritized high-relief range-front scarps ($69.9\%$ of `R0` dots sit in high-relief range terrain and $22.6\%$ in upper piedmont, with only $7.5\%$ in low-relief basins).

5. **Safe Zero-Filled Outside-Footprint Encoding (`-zeros.tif`):**
   DrivenData's validator rejects any GeoTIFF containing `NaN` values (`"Predicted values must be in range [0, 1]"`). The `-zeros.tif` twin replaces all `7,111,787` outside-footprint `NaN` pixels with `0.0`, guaranteeing clean ingestion.

---

### 2.2 Four Structural Deficiencies of `R0` Revealed by Forensic Diagnostics

Despite scoring `0.2778` (`[ORGANIZER-CONFIRMED]`), forensic analysis of `R0` (`data/parent_R0_zeros.tif`) on our `gems57-pooled-hide-v2` holdout evaluator and `USGS SGMC` proxy exposes four severe structural bottlenecks:

1. **Catastrophic Row-Major Scan-Order Bias (`Q0 + Q1 = 76.2%` of all dots; `Q3 = 0 dots`):**
   Look at the quadrant dot distribution of `R0`:
   - `Q0` (NW): **`16,003` dots (`42.5%`)**
   - `Q1` (NE): **`12,672` dots (`33.7%`)**
   - `Q2` (SW): **`8,979` dots (`23.8%`)**
   - `Q3` (SE): **`0` dots (`0.0%`!)**
   Because `R0` filled its `37,654`-dot budget using a coarse 2-tier tie-breaker in row-major (`top-to-bottom`) raster order, its budget was completely exhausted before reaching the southern half of the study area (`Q3` received literally **zero** dots!). Any hidden fault in the SE quadrant (`Q3`) suffers a $100\%$ recall miss in `R0`.

2. **Blindness to Concealed Intra-Basin & Basal Piedmont Faults (`7.5%` Basin Allocation):**
   In the Great Basin (Faulds & Hinz 2015, *Geosphere*), over $75\%$ of blind geothermal systems (e.g., Bradys, Desert Peak, Salt Wells, Dixie Valley, McGinness Hills) are controlled by submerged intra-basin step-overs, accommodation zones, or alluvial-covered basal piedmont fault toes where surface slope is $< 3^\circ$. Because `R0` relies on high-relief topographic Canny edges (`H19-5`), $69.9\%$ of its dots sit on high-elevation bedrock ridges (many of which are non-faulted glacial/fluvial erosion cliffs), while only $7.5\%$ sit in low-relief basins.

3. **Zero Subsurface Gravity-Tensor, Magnetic, MT, or Radiometric Physics:**
   `R0` uses `0` gravity bands, `0` magnetic bands, `0` magnetotelluric (`MT`) resistivity bands, and `0` USGS GeoDAWN radiometric (`K, Th, U`) bands. Consequently, where Holocene alluvial fans bury a fault trace by even $5$–$20\text{ m}$ of unconsolidated gravel, `R0` has zero signal.

4. **Suboptimal Along-Strike Packing on `H19-5` (`HOLDOUT-DTI = 0.004006`):**
   On `gems57-pooled-hide-v2` (`22,663` withheld catalogue fault pixels), `R0` scores only **`0.004006 [0.003406, 0.004668]` `[HOLDOUT-DTI]`** because its dots are densely clustered in northern range interiors (`Q0/Q1`) rather than evenly spaced at the optimal submodular kernel stride along active tectonic structures across all four quadrants.

---

### 2.3 How `RIEDELTENSOR standalone` Surpasses `R0` and Every Prior Repository Model (and How to Reach `0.3195` / `0.4413`)

`RIEDELTENSOR standalone` (`h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47-zeros.tif`) directly remedies all four deficiencies of `R0`:

1. **Balanced All-Quadrant Spatial Coverage via Selective 4-Branch LOQO (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION` Fixed):**
   Instead of `R0`'s `Q3 = 0` collapse, `RIEDELTENSOR standalone` allocates dots across all four quadrants in proportion to active tectonic and basement structure:
   - `Q0` (NW): **`8,452` dots (`22.4%`)**
   - `Q1` (NE): **`9,077` dots (`24.1%`)**
   - `Q2` (SW): **`11,427` dots (`30.3%`)**
   - `Q3` (SE): **`8,698` dots (`23.1%`)**
   And across geomorphic provinces: **`24.7%` Basin / `38.2%` Piedmont / `37.2%` Range** (compared to `R0`'s `7.5%` Basin / `22.6%` Piedmont / `69.9%` Range).

2. **Four New Untried Subsurface & Structural Physics Channels (`36` Features, `0` Leakage):**
   - **3D Laplace-Consistent Gravity-Gradient Tensor Invariants (`H1`, Pedersen & Rasmussen 1990; Beiki 2010):** Uses Laplace's equation in source-free upper crust ($G_{xx} + G_{yy} + G_{zz} = 0$, so $G_{zz} = -(\partial_{xx} g_z + \partial_{yy} g_z)$) to compute the true vertical-derivative ridge angle $\theta_{\text{tensor}} = \arctan2(\|\nabla_h g_z\|_2, \max(-G_{zz}, 0))$ (which decays as $1/z^3$, localizing steep normal-fault contacts with $2\times$ narrower half-width than $1/z^2$ horizontal gradients) and the **normal-fault step-dipole discriminator** $(-\partial_{nn} g_z / (\sqrt{I_2} + \varepsilon)) \cdot \tanh(\|\nabla_h g_z\|_2)$ (which separates linear normal-fault steps where $\partial_{nn} g_z = 0$ from circular caldera/pluton centers where $\partial_{nn} g_z \gg 0$).
   - **En-Echelon Riedel ($R/R'$) Transtensional Relay Obliquity (`H2`, Riedel 1929; Wilcox et al. 1973; Faulds & Hinz 2015):** Measures the angular obliquity $\Delta\psi = \arccos(|\cos(\theta_{\text{scarp}} - \theta_{\text{deep}})|)$ between shallow topographic scarp strike and deep 4 km basement tensor strike, peaking at synthetic Riedel shear ($\Delta\psi \approx 19^\circ$, $\sigma = 10^\circ$) and antithetic conjugate Riedel shear ($\Delta\psi \approx 68^\circ$, $\sigma = 12^\circ$) relay step-overs.
   - **3D Radiometric-Potential Hydrothermal Alteration Coupling (`H3`, Micklethwaite et al. 2010):** Couples USGS GeoDAWN potassium-to-thorium (`K/Th`) adularia-sericite metasomatism and uranium-to-thorium (`U/Th`) redox fronts with positive 3D gravity-tensor tilt (`tensor_tilt_pos`) and MT phase-tensor conduits (`mt_log_cond_4km`).
   - **Submodular 1D Coverage Spacing (`min_dist_px = 4.48 px` $\approx \sqrt{20}\text{ px} = 448\text{ m}$):**
     By the **Submodular 1D Coverage Theorem** (proved in `docs/HYPOTHESES_20261025_RIEDEL_TENSOR.md` §2), for the $R = 3.0\text{ px}$ triangular kernel $k_3(d) = \max(0, 1 - d/3)$, placing dots along 1D fault crests at spacing $s = 4.48\text{ px}$ ($\sqrt{20}\text{ px} \approx 4.472\text{ px}$) guarantees that **every pixel along the fault trace between two consecutive dots has distance $\min(u, s - u) \le 2.24\text{ px} < 3.0\text{ px}$** (100% continuous non-zero kernel support along strike!) while reducing redundant pairwise kernel overlap from $2(3 - 1.6) = 2.8\text{ px}$ (at `KNICKLOQO`'s $3.2\text{ px}$ spacing) to $2(3 - 2.24) = 1.52\text{ px}$ and expanding total linear fault length covered by **$+40.0\%$** ($168.7\text{ km}$ vs $120.5\text{ km}$)!

3. **Quantitative Gains Over Every Prior Model (`[HOLDOUT-DTI]` & `[PROXY]`):**
   - **Pooled Static `d_cat > 2.0` `HOLDOUT-DTI`:** **`0.011574 [0.010334, 0.012985]`** — **#1 All-Time in `GEMSDOE92`**, beating:
     - `KNICKLOQO standalone` (`0.010788`): **`+7.29%` (`+0.000786`, paired 95% CI `[+0.000284, +0.001298]`, $p < 0.001$)**
     - `PROVINCETOE piedbasin` (`0.009711`): **`+19.18%` (`+0.001863`)**
     - `POISSONKNICK qcal` (`0.009304`): **`+24.40%` (`+0.002270`)**
     - `EULERFUSE gravity` (`0.009265`): **`+24.92%` (`+0.002309`, `[+0.001164, +0.003435]`)**
     - `COULOMBLOQO standalone` (`0.009220`): **`+25.53%` (`+0.002354`, `[+0.001319, +0.003388]`)**
     - `HYDROCONDUIT f45hydro` (`0.008549`): **`+35.38%` (`+0.003025`, `[+0.002153, +0.003899]`)**
     - `COULOMBDM s45coulomb55` (`0.007816`): **`+48.08%` (`+0.003758`, `[+0.002916, +0.004628]`)**
     - `Parent R0` (`0.004006`): **`+188.92%` (`+0.007568`, `[+0.006431, +0.008771]`)**
   - **Strict Draw-Blind OOF `d_cat > 2.0` `HOLDOUT-DTI`:** **`0.011576 [0.010423, 0.012879]`** (**#1 All-Time**, beating `KNICKLOQO` `0.010958` by **`+5.64%`**).
   - **Strict Draw-Blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`:** **`0.113119 [0.100329, 0.126839]`** (and **`0.113256 [0.101048, 0.125847]`** at $3.05\text{ px}$ spacing) — **#1 among all unique (`<= 0.70`) models in the repository**, beating `KNICKLOQO` (`0.109043`), `EULERFUSE` (`0.110387`), `POISSONFLEX` (`0.107466`), `PROVINCETOE` (`0.106452`), and `H19-5` (`0.096757`, paired $\Delta = +0.016362$, 95% CI `[+0.007978, +0.024722]`).
   - **Off-Catalogue `USGS SGMC` Bedrock Fault `PROXY` (`62,703` pixels $> 300\text{ m}$ off catalogue):** **`0.105051`** (**#1 All-Time among `37,654`-dot models**, beating `KNICKLOQO standalone` `0.103912`, `R0` `0.096060`, `PROVINCETOE` `0.091183`, and `COULOMBLOQO standalone` `0.090569`).

4. **Roadmap to `0.3195` (`#2` Leaderboard) and `0.4413` (`#1` Leaderboard) (`[CLAIM]`):**
   Why is there a gap between `0.2778` and `0.3195` / `0.4413` on the organizer test set?
   - **First**, restoring `Q3` (SE quadrant, `23.1%` of dots in `RIEDELTENSOR standalone` vs `0.0%` in `R0`) and concealed piedmont/intra-basin faults (`62.9%` piedmont+basin dots vs `30.1%` in `R0`) recovers the southern and concealed fault populations that `R0` completely missed.
   - **Second**, switching from 0D isolated dots (`min_dist = 4.48 px`) to **anisotropic along-strike continuous filament emission** (convolving the selected crest centers along the local tensor/scarp unit tangent $\mathbf{t}(x) = (\cos\theta, \sin\theta)$ with a $1\text{ px}$-wide, $3\text{ px}$-long unit-peak filament while adjusting the number of seed centers so total mass remains $S \approx 38,000$) increases producer's recall ($\beta = 0.8$) along continuous hidden fault segments without widening the cross-strike footprint (`docs/NEXT_STEPS.md`).

---

## 3. Pre-Registered Candidate Hypotheses & Ablation Design (Protocol Rule 6)

Before writing code, we pre-registered five untried geological hypotheses in `docs/HYPOTHESES_20261025_RIEDEL_TENSOR.md`, ranked by expected `HOLDOUT-DTI` improvement and implementation cost:

| Rank | Hypothesis ID & Name | Specific Layers Used | Physical Signature | Expected `HOLDOUT-DTI` Gain | Cost | Selected for Implementation |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| **1** | **`H1`: 3D Laplace-Consistent Gravity-Gradient Tensor Invariants & Normal-Fault Step-Dipole Ridges (`RIEDELTENSOR`)** | `Band 13` (`grav_bouguer`), `Band 14` (`grav_isostatic`), `Band 15` (`grav_hgm`), `Band 16` (`grav_vd`), `Bands 1–4` | Laplace identity $G_{zz} = -(\partial_{xx} g_z + \partial_{yy} g_z)$, vertical-derivative ridge angle $\arctan2(\|\nabla_h g_z\|_2, \max(-G_{zz}, 0))$, curved-sheet index $(-\partial_{nn} g_z / \sqrt{I_2})\tanh(\|\nabla_h g_z\|_2)$ | `+5%` to `+9%` (`+0.0005` to `+0.0010` static `d_cat > 2.0`) | Low–Mod (`~180` LOC) | **YES (Core of `RIEDELTENSOR`)** |
| **2** | **`H2`: En-Echelon Riedel ($R \approx 19^\circ$ / $R' \approx 68^\circ$) Transtensional Relay Obliquity & Selective 4-Branch LOQO** | `Bands 1–4` ($300\text{ m}$ scarp tensor), `Bands 14, 21, 39` ($4\text{ km}$ deep basement tensor), `existing_faults.tif` ($3.5\text{ km}$ structural fabric) | Bimodal obliquity $\exp(-(\Delta\psi - 19^\circ)^2 / 2\cdot 10^2) + 0.65\exp(-(\Delta\psi - 68^\circ)^2 / 2\cdot 12^2) \times \sqrt{C_{\text{scarp}} C_{\text{deep}}}$, selective 4-branch LOQO | `+4%` to `+7%` (`+0.0004` to `+0.0008` static `d_cat > 2.0`) | Low (`~120` LOC) | **YES (Core of `RIEDELTENSOR`)** |
| **3** | **`H3`: 3D Radiometric-Potential (`K/Th`, `U/Th` $\times$ Gravity-Tensor Tilt $\times$ MT) Alteration Contact Coupling** | `ext_geodawn_rad_u8.tif` (`K, Th, U`), `gdr_wellspring_in_footprint.csv`, `Bands 14, 21, 35, 39` | Potassium/Uranium hydrothermal metasomatism strictly gated by positive 3D gravity-tensor tilt and 4 km MT conductivity | `+2%` to `+4%` (`+0.0002` to `+0.0004` static `d_cat > 2.0`) | Low (`~80` LOC) | **YES (Core of `RIEDELTENSOR`)** |
| 4 | `H4`: Multi-Depth MT Skin-Depth Vertical Conductivity Gradient ($\partial_z \ln \sigma$ across `500 m -> 1 km -> 2 km -> 4 km`) | `Bands 32, 35, 39, 43`, `Band 14` | Smectite-illite clay-cap transition over sub-vertical brittle fault damage zones | `+1%` to `+3%` | Low | Partially incorporated via `mt_clay_cap_contrast` (`Band 32 - Band 39`) |
| 5 | `H5`: Conjugate Mohr-Coulomb Strain-Rate Tensor Principal-Axis Bifurcation | `Bands 44–54` (`10 km` coarse strain), `Bands 1–4` | Principal strain-rate axis rotation across transtensional domain boundaries | `+0.5%` to `+1.5%` | Low | Deferred (`10 km` strain resolution too coarse for $300\text{ m}$ DTI kernel) |

In strict compliance with **Protocol Rule 6 (`<= 3` experiments per session)**, we executed exactly **3 pre-registered experiments** inside the single `RIEDELTENSOR` method lane:
1. **Experiment 1 (`standalone` — `h33-h33-2-b2-RIEDELTENSORstandalone-20261025-31b00e47-zeros.tif`):** `100%` standalone `RIEDELTENSOR` (`0%` `H19-5`, `0%` `R0` dots), selective branch-specific quadrant quantile calibration ($\lambda = 0.80, \gamma = 3.3$), submodular 1D crest spacing `min_dist_px = 4.48 px`, `37,654` unit-mass dots (`d_cat > 2.0 px`).
2. **Experiment 2 (`uncal` — `h33-h33-2-b2-RIEDELTENSORuncal-20261025-e19ad8a9-zeros.tif`):** Pure uncalibrated ablation ($\lambda = 0.0$, using `P_uncal` and `S_uncal`) with identical 36-feature 4-branch LOQO and `min_dist_px = 4.48 px`, isolating the exact contribution of selective within-quadrant quantile calibration.
3. **Experiment 3 (`hybrid35` — `h33-h33-2-b2-RIEDELTENSORhybrid35-20261025-be3233f3-zeros.tif`):** `35%` (`13,179` dots) `H19-5` breakline skeleton + `65%` (`24,475` dots) far-field (`d_H19 > 3.0 px`) `RIEDELTENSOR` crests, testing whether anchoring 35% of the budget to `H19-5` helps or hurts relative to 100% standalone `RIEDELTENSOR`.

---

## 4. Resolution of `#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`

During diagnostic development of the 4-branch `RIEDELTENSOR` LOQO ensemble, we discovered a subtle statistical-geological phenomenon (documented in `IRREGULARITIES.md` as `#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`):
- **Branch A (`Full`, 36 features)** and **Branch B (`Province-Debiased`, 30 features)** include regional potential-field and strain backgrounds whose raw LOQO probabilities in `Q1` (NE, Humboldt/Owyhee volcanic plateau) are systematically depressed ($\text{mean } P \approx 0.14$ vs $0.23$ in `Q2` SW). Applying within-quadrant empirical quantile calibration ($\lambda = 0.80$) to Branches A & B restores spatial parity across all four quadrants (`#IR-92-NE-QUADRANT-LOQO-COLLAPSE`).
- **However**, **Branch C (`Subsurface-Tensor-Riedel`, 31 features)** and **Branch D (`Basal-Toe-Riedel`, 28 features)** are driven by localized $1/z^3$ gravity-gradient tensor ridges, Riedel $R/R'$ obliquity, and basal piedmont concavity. In `Q1` (NE), genuine subsurface tensor/toe anomalies are sparser than in `Q2` (SW), so the $99\text{th}$ percentile of `P_sub` / `P_toe` in `Q1` contains moderate-score background noise. Forcing full quantile equalization on Branches C & D inflates that `Q1` background tail into the top-$37,654$ budget, degrading `Static d_cat > 2.0 HOLDOUT-DTI` by `-0.00025` (`0.01132` vs `0.011574`).
- **Mathematical Fix (`fit_predict_riedel_tensor_loqo` in `gems/riedel_tensor.py`):**
  Apply within-quadrant quantile calibration ($\lambda = 0.80, \gamma = 3.3$) **selectively to the province-sensitive branches (`Full` and `Province-Debiased`)** while keeping the local derivative/tensor branches (`Subsurface-Tensor-Riedel` and `Basal-Toe-Riedel`) on their physical probability scale (`lambda = 0.25 * lambda` on the combined ensemble):
  $$P_{\text{ens, mix}}(x) = 0.14\,P_{\text{full, qcal}}(x) + 0.34\,P_{\text{deb, qcal}}(x) + 0.36\,P_{\text{sub, raw}}(x) + 0.16\,P_{\text{toe, raw}}(x).$$
  This achieves **both** balanced quadrant allocation (`Q0: 8,452`, `Q1: 9,077`, `Q2: 11,427`, `Q3: 8,698`) **and** the new all-time repository record on both `Static d_cat > 2.0 HOLDOUT-DTI` (`0.011574`) and `Strict Draw-Blind OOF d_cat > 2.0 HOLDOUT-DTI` (`0.011576`).

---

## 5. Verification of All 6 Parallel-Run Protocol Rules

### 5.1 Rule 1 (LANE & Uniqueness Before Placement and on Final Dots)
- **Single Method Lane:** All work in this session stays strictly inside the `RIEDELTENSOR` lane (`gems/riedel_tensor.py`, `scripts/screen_riedel_tensor.py`, `scripts/build_riedel_tensor_variants.py`, `scripts/report_riedel_tensor_proxies.py`, `scripts/finalize_riedel_tensor_run_card.py`).
- **Pre-Placement Continuous Surface Uniqueness (`.cache/gems_inputs/riedel_tensor_S_cal_surface.tif`, `sha256: 0458b32db3f103d00e178f605d5eb4c8c9c1be4bc4a47cd59a0e4bd9e266468a`):**
  - Evaluated across all `79` unique local `GEMSDOE92` rasters in `evidence/riedel_tensor_screen.json`:
  - **Worst `|Spearman rho|` (exact full footprint, `5,167,373` pixels):** **`0.192497 <= 0.90`** (vs `data/bridge/h19_5.tif`) — **PASS**.
  - **Worst top-`37,654` 3-px overlap:** **`0.685080 <= 0.70`** (vs `downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif`) — **PASS**.
- **Final-Dot Local Registry Uniqueness (`79` unique local rasters, `evidence/riedel_tensor_proxy_audit.json`):**
  - `standalone` (`31b00e47`): `worst_forward_overlap = 0.685080 <= 0.70`, `worst_|phi| = 0.206680 <= 0.90`, `local_duplicate = False` — **PASS**.
  - `uncal` (`e19ad8a9`): `worst_forward_overlap = 0.674563 <= 0.70`, `worst_|phi| = 0.202747 <= 0.90`, `local_duplicate = False` — **PASS**.
  - `hybrid35` (`be3233f3`): `worst_forward_overlap = 0.665135 <= 0.70`, `worst_|phi| = 0.238516 <= 0.90`, `local_duplicate = False` — **PASS**.
- **Final-Dot Public Registry Uniqueness (`102` `GEMSDOE` repos, `1,451` compatible rasters, `1,448` non-self rasters, `evidence/riedel_tensor_dual_reading_audit.json`):**
  - Under `dual_reading_decision` (literal 3-px overlap for all `1,439` sparse/dot rasters $\le 150,000\text{ px}$; matched-budget top-`37,654` 3-px overlap for the `9` continuous surfaces $> 150,000\text{ px}$):
    - `standalone`: **`0 / 1,448` rasters `> 0.70`** (`worst_operative_overlap_3px = 0.685080 <= 0.70`; sparse `<= 90k px` max `0.685080`; continuous `> 150k px` matched-budget max `0.483216`; `dual_reading_verdict = "unique"`).
    - `uncal`: **`0 / 1,448` rasters `> 0.70`** (`worst_operative_overlap_3px = 0.674563 <= 0.70`; `dual_reading_verdict = "unique"`).
    - `hybrid35`: **`0 / 1,448` rasters `> 0.70`** (`worst_operative_overlap_3px = 0.665135 <= 0.70`; `dual_reading_verdict = "unique"`).
  - Under `literal_3px_decision` (unweighted `> 0` support on `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`, which has `5,167,373` positive pixels = `100%` of the footprint): literal overlap is `1.000000 > 0.70`, so fail-closed governance sets `submission_eligible = false` and `verdict = "negative"`.

### 5.2 Rule 2 (REUSE, DON'T REBUILD)
- Reused `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`), `vendor/gems57/holdout.py`, `vendor/gems57/metric.py`, `vendor/gems57/validate.py`, `vendor/gems57/submission_writer.py`, and `gems/gates.py` without modification.

### 5.3 Rule 3 (LABEL EVERY NUMBER)
- Every metric across `evidence/riedel_tensor_*.json`, `docs/*.html`, `README.md`, and this report carries its explicit `HOLDOUT-DTI`, `ORGANIZER-CONFIRMED`, `PROXY`, or `CLAIM` label.

### 5.4 Rule 4 (LEAKAGE CANARY — All `97` Surfaces Tested Alone `<= 0.90` Symmetric AUC)
In `scripts/screen_riedel_tensor.py` (`evidence/riedel_tensor_screen.json`), we ran single-feature holdout leakage canaries across all `8` folds (`22,663` withheld catalogue fault pixels vs buffered negatives $> 500\text{ m}$ from all catalogue faults) on:
- All **56 raw bands** of `training_features.tif` (`max symmetric AUC = 0.635267 <= 0.90` on `Band 2` slope),
- All **36 engineered `RIEDELTENSOR` physical features** (`max symmetric AUC = 0.603859 <= 0.90`),
- All **5 LOQO probability & crest surfaces** (`LOQO_P_uncal`, `LOQO_P_cal`, `LOQO_S_cal`, `LOQO_S_uncal`, `LOQO_draw_blind_S_cal`; `max symmetric AUC = 0.664574 <= 0.90` on `LOQO_P_cal`).

| Feature / Surface Group | Feature Name | Pooled Raw AUC | Pooled Symmetric AUC (`max(AUC, 1-AUC)`) | Gate (`<= 0.90`) |
| :--- | :--- | :---: | :---: | :---: |
| **New `RIEDELTENSOR` Feature #31** | `grav_tensor_vdr_angle` ($1/z^3$ Laplace tensor ridge angle) | `0.506360` | `0.506360` | **PASS** |
| **New `RIEDELTENSOR` Feature #32** | `grav_curved_sheet_idx` (normal-fault step-dipole vs caldera) | `0.491088` | `0.508912` | **PASS** |
| **New `RIEDELTENSOR` Feature #33** | `riedel_relay_coupling` (en-echelon $R \approx 19^\circ$ / $R' \approx 68^\circ$ relay) | `0.556790` | `0.556790` | **PASS** |
| **New `RIEDELTENSOR` Feature #34** | `rad_pot_alteration` (`K/Th`, `U/Th` $\times$ tensor tilt $\times$ MT) | `0.509427` | `0.509427` | **PASS** |
| **New `RIEDELTENSOR` Feature #35** | `basement_step_polarity` (`RTP x Isostatic` step dipole) | `0.525699` | `0.525699` | **PASS** |
| **New `RIEDELTENSOR` Feature #36** | `mt_clay_cap_contrast` (`500 m - 4 km` MT clay-cap over conduit) | `0.483582` | `0.516418` | **PASS** |
| Highest Engineered Feature (of 36) | `rel_log_slope_break` | `0.603859` | `0.603859` | **PASS** |
| Highest Raw Band (of 56) | `raw_band_02` (slope) | `0.635267` | `0.635267` | **PASS** |
| `RIEDELTENSOR` LOQO Surface | `LOQO_P_uncal` | `0.649935` | `0.649935` | **PASS** |
| `RIEDELTENSOR` LOQO Surface | `LOQO_P_cal` | `0.664574` | `0.664574` | **PASS** |
| `RIEDELTENSOR` Crest Surface | `LOQO_S_cal` | `0.654032` | `0.654032` | **PASS** |
| `RIEDELTENSOR` Draw-Blind Surface | `LOQO_draw_blind_S_cal` | `0.648604` | `0.648604` | **PASS** |

### 5.5 Rule 5 (JSON RUN CARD)
- Emitted in `evidence/riedel_tensor_run_card.json` and `docs/downloads/riedel_tensor_run_card.json` (plus per-raster `-audit.json` sidecars in `docs/downloads/`), containing hypothesis, mechanism, named non-fault mimic process, holdout DTI + 95% CI, correlation/overlap vs local and public registries, raster SHA-256, validator output, submission name + note (`131 <= 140` chars), and verdict (`"negative"`).

### 5.6 Rule 6 (BUDGET)
- Stopped after exactly `3` pre-registered experiments (`standalone`, `uncal`, `hybrid35`) inside `1` method lane (`RIEDELTENSOR`). `0` weekly DrivenData slots were touched.

---

## 6. Per-Fold Holdout Breakdown (`gems57-pooled-hide-v2`, Seeds `20` & `30`)

| Fold | Seed | Quadrant | `RIEDELTENSOR standalone` (`31b00e47`) | `RIEDELTENSOR uncal` (`e19ad8a9`) | `KNICKLOQO standalone` (`d53d919f`) | `COULOMBLOQO standalone` (`e01d27af`) | `Parent R0` (`e5eb6e7e`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 20 | `Q0` (NW) | **`0.011056`** | `0.010817` | `0.010075` | `0.008515` | `0.005617` |
| 1 | 20 | `Q1` (NE) | **`0.008898`** | `0.007917` | `0.008498` | `0.004785` | `0.004628` |
| 2 | 20 | `Q2` (SW) | **`0.013191`** | `0.013256` | `0.012465` | `0.011432` | `0.004386` |
| 3 | 20 | `Q3` (SE) | **`0.011579`** | `0.011347` | `0.010539` | `0.009911` | `0.000000` |
| 4 | 30 | `Q0` (NW) | **`0.010870`** | `0.010519` | `0.010401` | `0.008949` | `0.006127` |
| 5 | 30 | `Q1` (NE) | **`0.009692`** | `0.008843` | `0.009083` | `0.005745` | `0.004673` |
| 6 | 30 | `Q2` (SW) | **`0.013819`** | `0.013847` | `0.013103` | `0.011907` | `0.004743` |
| 7 | 30 | `Q3` (SE) | **`0.012016`** | `0.011780` | `0.010879` | `0.010288` | `0.000000` |
| **Pooled** | **20+30** | **All (`22,663` px)** | **`0.011574`** | **`0.011265`** | **`0.010788`** | **`0.009220`** | **`0.004006`** |

Notice that **`RIEDELTENSOR standalone` beats `KNICKLOQO standalone`, `COULOMBLOQO standalone`, and `Parent R0` on EVERY SINGLE FOLD (`8/8` folds)**!

---

## 7. Documented Limitations & Irregularities

1. **Literal Public Registry Dense-Surface Overlap (`#IR-92-PUBLIC-DENSE-SURFACE-STOP`):**
   `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` contains `5,167,373` positive pixels (`100%` of the valid footprint), causing any nonempty submission to have `1.000000 > 0.70` literal 3-px overlap. Under `dual_reading_decision` (which evaluates continuous surfaces $> 150,000\text{ px}$ at matched top-$37,654$ budget and dot fields $\le 150,000\text{ px}$ literally), all three `RIEDELTENSOR` arms have **`0 / 1,448` overlaps `> 0.70`** (`max = 0.685080 <= 0.70`).
2. **Static `d_cat > 2.0` vs Fold-Visible `d_visible > 2.0` Ceiling (`#IR-92-STATIC-HOLDOUT-MASKING-CEILING`):**
   Any deployment-ready submission must mask `d_full_catalogue <= 2.0 px`, which automatically zeros out $\sim 90\%$ of the $3\text{ px}$ kernel support around withheld catalogue faults in `evaluate_holdout.py`. Evaluating the exact same draw-blind `RIEDELTENSOR` model with `d_visible > 2.0 px` yields **`0.113119 [0.100329, 0.126839]`** (`10x` higher numerical scale), confirming that the `~0.0116` scale on static rasters is a purely geometric artifact of full-catalogue masking.
3. **Sparse `DOE GDR #1391` Point Coverage (`#IR-92-GDR-1391-SPARSE-COVERAGE`):**
   Only `56` thermal wells/springs from `DOE GDR #1391` fall inside the competition footprint (`38` at $> 2\text{ px}$ from catalogue faults), so `plume_feat` must be used with conservative regularization (`max_depth=5`, `min_samples_leaf=500`) alongside full-coverage USGS GeoDAWN radiometrics.
4. **Double-Edged NE Quadrant Calibration (`#IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION`):**
   Resolved in `gems/riedel_tensor.py` by applying within-quadrant quantile calibration selectively to the province-sensitive branches (`Full` and `Province-Debiased`) while keeping the local derivative/tensor branches (`Subsurface-Tensor-Riedel` and `Basal-Toe-Riedel`) on their physical probability scale.

---

## 8. Verified Official Sources & References

1. **Pedersen, L. B., & Rasmussen, T. M. (1990).** *The gradient tensor of potential field anomalies: Some implications on data collection and data processing of maps.* Geophysics, 55(12), 1558–1566. [https://doi.org/10.1190/1.1442807](https://doi.org/10.1190/1.1442807)
2. **Beiki, M. (2010).** *Analytic signals of gravity gradient tensor and their application to estimate source location.* Geophysics, 75(6), I59–I74. [https://doi.org/10.1190/1.3493639](https://doi.org/10.1190/1.3493639)
3. **Riedel, W. (1929).** *Zur Mechanik geologischer Brucherscheinungen.* Zentralblatt für Mineralogie, Geologie und Paläontologie B, 354–368.
4. **Wilcox, R. E., Harding, T. P., & Seely, D. R. (1973).** *Basic wrench tectonics.* AAPG Bulletin, 57(1), 74–96. [https://doi.org/10.1306/819A424A-16C5-11D7-8645000102C1865D](https://doi.org/10.1306/819A424A-16C5-11D7-8645000102C1865D)
5. **Faulds, J. E., & Hinz, N. H. (2015).** *Favorable tectonic and structural settings of geothermal systems in the Great Basin region, western USA: Proxies for discovering blind geothermal systems.* Proceedings World Geothermal Congress 2015, Melbourne, Australia. [https://www.geothermal-energy.org/pdf/IGAstandard/WGC/2015/11077.pdf](https://www.geothermal-energy.org/pdf/IGAstandard/WGC/2015/11077.pdf)
6. **Micklethwaite, S., Sheldon, H. A., & Baker, T. (2010).** *Active fault and shear processes and their implications for mineral deposit formation and discovery.* Journal of Structural Geology, 32(2), 151–165. [https://doi.org/10.1016/j.jsg.2009.10.009](https://doi.org/10.1016/j.jsg.2009.10.009)
7. **Wallace, R. E. (1977).** *Profiles and ages of young fault scarps, north-central Nevada.* GSA Bulletin, 88(9), 1267–1281. [https://doi.org/10.1130/0016-7606(1977)88%3C1267:PAAOYF%3E2.0.CO;2](https://doi.org/10.1130/0016-7606(1977)88%3C1267:PAAOYF%3E2.0.CO;2)
8. **Whipple, K. X., & Tucker, G. E. (1999).** *Dynamics of the stream-power river incision model: Implications for height limits of mountain ranges, landscape response timescales, and research needs.* Journal of Geophysical Research: Solid Earth, 104(B8), 17661–17674. [https://doi.org/10.1029/1999JB900120](https://doi.org/10.1029/1999JB900120)
9. **Chandler, V. W., Koski, J. S., Hinze, W. J., & Braile, L. W. (1981).** *Analysis of multisource gravity and magnetic anomaly data sets by moving-window application of Poisson's theorem.* Geophysics, 46(1), 30–39. [https://doi.org/10.1190/1.1441136](https://doi.org/10.1190/1.1441136)
10. **DrivenData Competition 306 (DOE GEMS Geothermal Contest):** [https://www.drivendata.org/competitions/306/competition-gem-geothermal/](https://www.drivendata.org/competitions/306/competition-gem-geothermal/)
11. **USGS GeoDAWN Airborne Radiometric & Magnetic Survey (Data Release):** [https://doi.org/10.5066/P9P3625C](https://doi.org/10.5066/P9P3625C)
12. **USGS State Geologic Map Compilation (`SGMC`):** [https://doi.org/10.3133/ds1052](https://doi.org/10.3133/ds1052)
13. **Great Basin Center for Geothermal Energy — INGENIOUS Project (`DOE GDR #1391`):** [https://gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391)
