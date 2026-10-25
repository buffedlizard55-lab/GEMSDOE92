# PhD Forensic Analysis, Leaderboard Deconstruction & `LISTRICLOQO` Audit Report (2026-10-25)

- **Session Date (UTC)**: `2026-10-25`
- **Active Lane**: `LISTRICLOQO` — Updip-Projected Listric Hanging-Wall Subsurface Ramps + Interfluve-Bridged Drainage Knickzones + Airborne `K/Th` & `U/Th` Redox-Contact Concordance + Selective-Branch Quadrant-Calibrated 3-Branch `LOQO` Ensemble
- **Pre-Registration Document**: [`docs/HYPOTHESES_20261025_LISTRICLOQO.md`](HYPOTHESES_20261025_LISTRICLOQO.md)
- **Primary Deliverable (`selectcal`)**: [`docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif`](downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif) (`SHA-256 = 58e5d780f3602e17adef92df9877f581c922e3621b0fc1b853e623e95c048b17`, `37,654` unit dots in `[0, 1]`, `11/11` format gates PASS)
- **Sibling Deliverables**:
  - `standalone`: [`docs/downloads/h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif`](downloads/h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif) (`SHA-256 = dc6d8f06053a48efdc07146535f4fc27b50643fc54fd7fc7a3fa243d119186cb`, `37,654` unit dots in `[0, 1]`, `11/11` format gates PASS)
  - `uncal`: [`docs/downloads/h33-h33-2-b2-LISTRICLOQOuncal-20261025-2962f45f-zeros.tif`](downloads/h33-h33-2-b2-LISTRICLOQOuncal-20261025-2962f45f-zeros.tif) (`SHA-256 = 304ffdc6ac5899da5947f0f19dfb33579adc6e112d8af3e7f97f770f0c55b0aa`, `37,654` unit dots in `[0, 1]`, `11/11` format gates PASS)
- **Rule 5 Run Card**: [`evidence/listric_loqo_run_card.json`](../evidence/listric_loqo_run_card.json) (mirror: [`docs/downloads/listric_loqo_run_card.json`](downloads/listric_loqo_run_card.json))

---

## 0. Executive Status Banner (Two-Part Operational Verdict)

| Question | Status | Concrete Evidence |
| :--- | :--- | :--- |
| **1. Is `h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif` (and siblings `standalone`, `uncal`) OK TO DOWNLOAD & FORMAT-VALID?** | **YES — `OK TO DOWNLOAD FOR RESEARCH / FORMAT-VALID (11/11 GATES PASS)`** | Re-opened from disk via `vendor/gems57/validate.py` and `gems/gates.py`: `3730 x 3292` `float32`, `EPSG:32611`, values strictly in **`{0.0, 1.0} ⊂ [0, 1]`** (resolves the organizer `"Predicted values must be in range [0, 1]"` error), `0` NaN/Inf anywhere on the `12,279,160`-pixel raster, `0` outside-footprint mass, `0` mapped-catalogue overlap (`min d_cat = 2.2361 px > 2.0 px`), and `37,654` unit dots. |
| **2. Did `LISTRICLOQO` beat every prior `HOLDOUT-DTI` benchmark in `GEMSDOE92` AND pass operational matched-budget uniqueness across all `1,459` public rasters in `102` repos?** | **YES — NEW ALL-TIME #1 ON BOTH STATIC `d_cat > 2.0` (`0.013295`) AND STRICT DRAW-BLIND `d_visible > 2.0` (`0.114410`), WITH `0 / 1,459` OPERATIONAL COLLISIONS (`<= 0.6903 <= 0.70`)** | On `gems57-pooled-hide-v2` (`22,663` withheld positive pixels across 8 spatial-block folds), `LISTRICLOQO selectcal` reaches static `d_cat > 2.0` **`HOLDOUT-DTI = 0.013295 [0.011713, 0.014980]`** (**`+23.2%`** over prior #1 `KNICKLOQO standalone = 0.010788`, paired $\Delta = +0.002508\,[+0.001477, +0.003463]$, $p < 10^{-4}$; **`+231.9%`** over parent `R0 = 0.004006`), while `LISTRICLOQO standalone` reaches strict draw-blind Rule-2 `d_visible > 2.0` **`HOLDOUT-DTI = 0.114410 [0.101808, 0.127706]`** (`selectcal = 0.113938`), beating prior #1 `COULOMBLOQO standalone = 0.113316` and `KNICKLOQO standalone = 0.109043`. Across all `1,459` non-self single-band exact-grid rasters in `102` public `GEMSDOE` repositories (`1,469` unique Git blobs, `0` download failures) and all `68` unique local `GEMSDOE92` rasters, `selectcal` achieves **`0 / 1,459` operational overlaps `> 0.70`** (max **`0.690259 <= 0.70`**, `|ρ| <= 0.4685 <= 0.90`). |
| **3. Is a weekly competition slot automatically spent (`submission_eligible`)?** | **NO — `DO NOT AUTO-SUBMIT (`verdict = "negative"`, `submission_eligible = false`, `0` weekly slots spent)`** | Under the repository's fail-closed literal unweighted public overlap check (`vendor/gems57/uniqueness.py:binding_duplicate_decision`), the everywhere-positive `5,167,373`-pixel continuous probability surface `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` triggers literal forward overlap `1.0000 > 0.70` against every non-empty raster on the competition grid (including `R0`). Per `#IR-92-DENSE-WITNESS-MATCHED-BUDGET` and `REVIEW376A`, both readings are reported side-by-side and `0` weekly slots are spent automatically. |

---

## 1. PhD-Level Forensic Deconstruction: Why `GEMSDOE32` Scored `0.2778 [CLAIM]`, and How to Beat `0.2778`, `0.3195`, and Leaderboard `0.4413`

### 1.1 Exact Mathematical Mechanics of the DrivenData Distance-Weighted Tversky Index (`DTI`)

Let $\Omega \subset \{0,\dots,3729\} \times \{0,\dots,3291\}$ denote the valid competition footprint ($|\Omega| = 5,167,373$ pixels at $100\text{ m}$ UTM Zone 11N resolution, $\text{EPSG:32611}$), let $C \subset \Omega$ denote the known USGS/INGENIOUS Quaternary fault catalogue (`existing_faults.tif`, $|C| = 60,988$ pixels $= 1.180\%$ of $\Omega$), and let $G \subset \Omega \setminus C$ denote the organizer's hidden withheld fault evaluation mask.

For a predicted raster $P : \Omega \to [0, 1]$ (with `0.0` on $\Omega^c \cup C$) and the $300\text{ m}$ ($r = 3.0\text{ px}$) linear-decay distance kernel
$$K(d) = \max\!\left(0,\; 1 - \frac{d}{r}\right), \qquad r = 3.0\text{ px},$$
define the distance-buffered truth field $T_K(x) = \max_{g \in G} K(\|x - g\|_2)$ and the distance-buffered prediction field $P_K(g) = \max_{x \in \operatorname{supp}(P)} P(x)\,K(\|g - x\|_2)$. Using the official DrivenData reference notebook coefficients (`drivendataorg/gems-prize-reference-solution/unet-mc-cv-reference-solution.ipynb`, Cell 16: $\alpha = 0.2$ on false positives, $\beta = 0.8$ on false negatives) implemented in `vendor/gems57/metric.py`:
$$\mathrm{TP}_w = \sum_{g \in G} P_K(g), \qquad \mathrm{FN}_w = \sum_{g \in G} \bigl(1 - P_K(g)\bigr) = |G| - \mathrm{TP}_w, \qquad \mathrm{FP}_w = \sum_{x \in (\Omega \setminus C) \setminus B_r(G)} P(x)\bigl(1 - T_K(x)\bigr),$$
$$\mathrm{DTI}(P, G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + \alpha\,\mathrm{FP}_w + \beta\,\mathrm{FN}_w} = \frac{\mathrm{TP}_w}{0.2\,\mathrm{TP}_w + 0.8\,|G| + 0.2\,\mathrm{FP}_w}.$$

Three structural properties of this functional govern every leaderboard transition from `0.1922` to `0.4413`:

1. **Asymmetric Recall Dominance ($\beta / \alpha = 4.0$):** Every unit of missed hidden fault pixel ($\mathrm{FN}_w$) penalizes the denominator **$4\times$ more heavily** than a unit of false-positive mass ($\mathrm{FP}_w$). When hidden fault size $|G|$ is on the order of $1.5\times 10^4\text{--}3.0\times 10^4$ pixels and a binary submission emits $S = |A| = 37,654$ unit dots ($P(x) \in \{0, 1\}$), the denominator is approximately $0.8\,|G| + 0.2\,S + 0.2\,\mathrm{TP}_w$.
2. **Envelope Saturation Under Sub-Kernel Clustering ($\|x_i - x_j\|_2 < 2.8\text{ px}$):** Because $\mathrm{TP}_w = \sum_{g \in G} \max_{x \in A} K(\|g - x\|_2)$ takes a **pointwise maximum** rather than a sum over $x \in A$, placing a second dot $x_j$ within $1\text{--}2\text{ px}$ of $x_i$ adds almost zero marginal truth coverage $\Delta \mathrm{TP}_w \approx 0$ while still adding $+0.2\,(1 - T_K(x_j))$ to $\alpha\,\mathrm{FP}_w$ whenever $x_j \notin B_r(G)$. Conversely, spacing dots at $\Delta s \approx 2.8\text{--}4.3\text{ px}$ along a 1D fault crest covers a continuous fault trace with $3\times\text{--}4\times$ fewer dots, freeing the remaining dot budget to cover additional unmapped faults.
3. **Zero-Credit Collar Around Mapped Catalogue Faults ($d_{\text{cat}} \le 2.0\text{ px}$):** Because the organizer's hidden truth $G$ consists of **unmapped** faults ($G \cap C = \varnothing$) and segments buffered away from mapped traces $C$, dots placed at $d_{\text{cat}}(x) = \min_{c \in C} \|x - c\|_2 \le 2.0\text{ px}$ incur pure $+0.2\,\mathrm{FP}_w$ penalty with near-zero hidden-fault $\mathrm{TP}_w$ credit.

---

### 1.2 Byte-Verified Ancestor Lineage of `GEMSDOE32` (`R0`: `0.2778 [CLAIM]`)

Direct pixel-algebraic audit of the SHA-256-verified bridge and lineage rasters in `data/bridge/` (`registry/data_manifest.json`) and `.cache/gems_inputs/lineage/` (`registry/session_manifest.json`) proves the exact four-stage construction of `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, `data/parent_R0_zeros.tif`):

| Stage | Artifact Path | SHA-256 Prefix | Positive Pixels ($S$) | Exact Byte / Set Algebra Identity | Reported Score (`[CLAIM]`) | Physical / Mathematical Operation |
| :--- | :--- | :--- | ---: | :--- | ---: | :--- |
| **Stage 1** | `data/bridge/h19_5.tif` | `ec1f9b56...` | `121,131` | Binary `{0, 1}` mask (`2.344%` of footprint) | `0.1922` / `0.2194` `[CLAIM]` | Multi-physics continuous probability thresholded into $3\text{--}5\text{ px}$ wide ribbons along range fronts. Over-packs dots inside the same $r = 3\text{ px}$ kernel ($\alpha\,\mathrm{FP}_w \approx 24,226$). |
| **Stage 2** | `data/bridge/d28.tif` | `91eae1ca...` | `44,090` | `D2.8 ⊂ H19-5` (`100.00%` inside `H19-5`, $\min_{i\neq j}\|x_i - x_j\|_2 \approx 2.8\text{ px}$) | `0.2600` / `0.2649` `[CLAIM]` | Poisson-disk $2.8\text{ px}$ decimation removes `77,041` redundant ribbon pixels (`-63.6%` $\mathrm{FP}_w$) while preserving almost $100\%$ of $\max_{x \in A} K(\|g - x\|_2)$ along `H19-5`. |
| **Stage 3** | `data/bridge/h27_4_solo.tif` | `ab023001...` (`zeros`) / `2fc94a38...` (`GEMSDOE28`) | `40,199` | **`XOR(SOLO, D2.8 & (d_cat > 1.0)) == 0`** (`-3,891` px at $d_{\text{cat}} \le 1.0\text{ px}$) | `0.2708` `[CLAIM]` | Exact 1-pixel catalogue collar prune around `existing_faults.tif` removes `3,891` zero-credit boundary dots. |
| **Stage 4 (`R0`)** | `data/parent_R0_zeros.tif` | `c55bafc4...` (`zeros`) / `baeae321...` (`nan`) | `37,654` | **`XOR(R0, D2.8 & (d_cat > 2.0)) == 0`** (`-2,545` px at $1.0 < d_{\text{cat}} \le 2.0\text{ px}$) | **`0.2778`** `[CLAIM]` | Exact 2-pixel Euclidean catalogue collar prune ($\min d_{\text{cat}} = \sqrt{5} \approx 2.2361\text{ px}$), eliminating `6,436` total near-catalogue false positives from `D2.8`. |

**Why `GEMSDOE32` (`R0`) beat all 13 other listed `GEMSDOE` sites in the user prompt:**
1. Every site that emitted **raw continuous probabilities** or **dense multi-pixel ribbons** (`> 100,000` positive pixels) inflated $\alpha\,\mathrm{FP}_w = 0.2 \sum P(x)(1 - T_K(x))$ across millions of background cells.
2. Every site that emitted **NaN outside the footprint without organizer zero-fill** or **out-of-range float values (`< 0` or `> 1`)** failed the competition parser (`"Predicted values must be in range [0, 1]"`).
3. `GEMSDOE32` (`R0`) combined **binary `{0, 1}` unit dots** + **$2.8\text{ px}$ kernel-matched spacing (`D2.8`)** + **exact $d_{\text{cat}} > 2.0\text{ px}$ catalogue collar pruning (`-6,436` px)** + **zeros-outside encoding**.

---

### 1.3 Why `GEMSDOE32` (`0.2778 [CLAIM]`) Plateaus, and How to Beat `0.2778`, `0.3195`, and `0.4413`

Despite its optimal geometric post-processing of `H19-5`, `R0` is **100.00% confined to `H19-5`** (`R0 ⊂ H19-5`). Our spatial-block holdout (`gems57-pooled-hide-v2`, `22,663` withheld positives) and off-catalogue `USGS SGMC` 1:500,000 bedrock fault audit (`62,122` off-catalogue fault pixels at $d_{\text{cat}} > 3\text{ px}$) expose three severe structural ceilings of `H19-5`:

1. **The Catalogue-Proximity & Range-Front Ceiling of `H19-5`:**
   - Although `H19-5` covers `53.5%` of mapped `existing_faults.tif` within $3.0\text{ px}$, `51.8%` of `R0`'s dots lie within $15\text{ px}$ ($1.5\text{ km}$) of existing mapped faults. When entire connected fault systems are withheld with a $30\text{ px}$ ($3\text{ km}$) exclusion collar (`gems57-pooled-hide-v2`), static `R0` collapses to **`HOLDOUT-DTI = 0.004006 [0.003406, 0.004668]`**.
   - Against off-catalogue `USGS SGMC` bedrock faults (`d_cat > 3\text{ px}`), `H19-5`'s entire `121,131`-pixel mask covers only **`37.8%`** within $3.0\text{ px}$, leaving **`62.2%`** of buried intrabasin, piedmont-toe, relay-ramp, and NE carbonate-horst faults completely unreachable by any subset or perturbation of `H19-5` (`MASS`, `PRUNE`, `SNAP`, `CONCENTRATION`).
2. **The In-Situ Subsurface Dip-Offset Bias (`300–550 m` Down-Dip of the Surface Scarp):**
   - Previous standalone LOQO lanes (`COULOMBLOQO`, `POISSONKNICK`, `KNICKLOQO`) added subsurface Bouguer gravity (`Bands 5, 11, 13, 18`), depth-to-basement (`Band 15`), and magnetic (`Bands 2, 3, 6, 10, 14`) ridges (`L_sub`) **in situ**.
   - However, Basin and Range range-bounding normal faults dip $45^\circ\text{--}60^\circ$ basinward (often listric at $1.0\text{--}2.5\text{ km}$ depth; Grauch & Cordell 1987; Okaya & Thompson 1985). Consequently, the maximum horizontal gradient of Bouguer gravity and basement depth lies **$360\text{--}520\text{ m}$ ($3.6\text{--}5.2\text{ px}$) basinward (down-dip)** of the surface fault trace!
   - Because the DrivenData DTI kernel radius is strictly $r = 300\text{ m}$ ($3.0\text{ px}$), dots placed directly on the in-situ subsurface gradient crest at $3.6\text{--}5.2\text{ px}$ down-dip receive **zero DTI truth credit ($K(d) = 0$ for $d \ge 3.0\text{ px}$)** against the surface/piedmont fault trace AND collide (`0.6855`) with prior in-situ subsurface lanes.
3. **The Drainage-Thalweg Sparsity Gap Across Faceted Interfluve Spurs:**
   - `KNICKLOQO`'s drainage knickpoint channel (`L_knick`) required local topographic concavity ($\nabla^2 z < 0$), which holds inside incised drainage canyons but vanishes (`L_knick = 0`) across convex triangular faceted interfluve spurs (`300–900 m` wide) between canyons (Wallace 1978), creating `4–9 px` gaps along continuous range-front fault traces.

| Score Tier | Benchmark / Candidate | Static `d_cat > 2.0` `HOLDOUT-DTI` (`gems57-pooled-hide-v2`) | Strict Draw-Blind `d_visible > 2.0` `HOLDOUT-DTI` | External `USGS SGMC` Bedrock `PROXY` DTI | What Separates This Tier Physically & Mathematically |
| :--- | :--- | ---: | ---: | ---: | :--- |
| **Tier 1 (`0.2778 [CLAIM]`)** | `GEMSDOE32` (`R0`, `h33-h33-2-b2`) | `0.004006 [0.003406, 0.004668]` | `0.096757 [0.084839, 0.108454]` (`H19_skeleton`) | `0.096060` | 100% inside `H19-5` (`2.8 px` spacing + $d_{\text{cat}} > 2.0\text{ px}$ collar). Zero off-skeleton fault recovery. |
| **Tier 2 (`0.3195 [CLAIM]`)** | First-generation standalone / hybrid 1D LOQO lanes (`COULOMBLOQO`, `POISSONKNICK`, `PROVINCETOE`, `KNICKLOQO`) | `0.009220` $\to$ `0.010788 [0.009468, 0.012201]` (`+130%` to `+169%` vs `R0`) | `0.098491` $\to$ `0.113316 [0.100614, 0.127163]` | `0.081106` $\to$ `0.103912` | Replaces `H19-5` with 1D Canny-NMS crests from out-of-quadrant (LOQO) tree ensembles + within-quadrant calibration (`NE` recovery), but places subsurface ridges **in situ** ($360\text{--}520\text{ m}$ down-dip) and leaves interfluve spurs unbridged. |
| **Tier 3 (`LISTRICLOQO`, This Session)** | **`LISTRICLOQO selectcal` & `standalone`** (`h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif`) | **`0.013295 [0.011713, 0.014980]`** (`selectcal`, **`+231.9%` vs `R0`**, **`+23.2%` vs `KNICKLOQO`**) / **`0.013250`** (`standalone`) | **`0.114410 [0.101808, 0.127706]`** (`standalone`, **#1 all-time**) / **`0.113938`** (`selectcal`, **#2 all-time**) | **`0.103442`** (`selectcal`) / **`0.103139`** (`standalone`) | **Projects subsurface gravity/basement/Poisson ramps updip by $3.6\text{--}5.2\text{ px}$ ($360\text{--}520\text{ m}$) onto the footwall scarp**, bridges canyon knickpoints across $\pm 3.8\text{--}4.8\text{ px}$ interfluve spurs, adds dual-ratio `K/Th` & `U/Th` redox-contact concordance + relay-ramp transfer, and applies selective branch quadrant calibration (`min_dist_px = 4.15–4.30`). |
| **Tier 4 (`0.4413 [CLAIM]` Leaderboard Ceiling)** | Theoretical / Full-Resolution Multi-Scale Boundary | Requires external high-res data beyond 100 m stack | — | — | Reaching `> 0.40` requires sub-100 m DEM scarp curvature (`USGS 3DEP 1/3 arc-second = 10 m`), InSAR phase-gradient lineaments (`ARIA/OPERA Sentinel-1`), and relocated microseismicity (`Waldhauser & Ellsworth 2000` double-difference catalogue) to resolve $10\text{--}30\text{ m}$ intrabasin Holocene scarps that are sub-pixel at $100\text{ m}$ resolution. |

---

## 2. Execution of Prior Session Next Steps (`docs/NEXT_STEPS.md`)

Before training or evaluating `LISTRICLOQO`, we executed the prioritized engineering and scientific follow-ups from `docs/NEXT_STEPS.md`:

1. **Resolved `#IR-92-PUBLIC-SCAN-RATELIMIT-705-FAILURES` in Shared Tooling (`scripts/audit_public_registry.py`):**
   - *Root Cause*: When scanning `1,469` unique Git blobs across `102` `buffedlizard55-lab/*GEMSDOE*` repositories, per-blob `gh api repos/.../git/blobs/<sha>` calls exhausted the 5,000/hr GitHub REST rate limit and raw `github.com/.../raw/...` connections failed with TLS EOF (`_ssl.c:992`).
   - *Shared-Tool Fix (Protocol Rule 2)*: Added `prefetch_via_local_and_codeload()` to `scripts/audit_public_registry.py`, which first seeds matching SHA-1 blobs from local disk (`docs/downloads/`, `releases/`, `data/`) and then streams repository tarballs (`https://codeload.github.com/buffedlizard55-lab/<repo>/tar.gz/<branch>`) in a single HTTP request per repository, verifying every extracted `.tif` against its exact Git blob SHA-1 (`blob <size>\0<bytes>`).
   - *Verification*: All **`1,469 / 1,469` unique `.tif` blobs across `102` repositories** were fetched and SHA-1-verified with **`0` download failures** (`1,459` compatible single-band exact-grid `3730 x 3292` rasters). All 10 unit/regression tests in `tests/test_public_audit.py` and `tests/test_public_registry_audit.py` pass (`10 passed`).
2. **Resolved the Subsurface Dip-Offset & Interfluve Gap Bottleneck (`#IR-92-LISTRIC-DIP-OFFSET-OVERLAP`):**
   - Implemented `bilinear_sample_2d` and updip listric projection along $\mathbf{n}_{\text{updip}}$ ($s \in \{3.6, 4.4, 5.2\}\text{ px}$) plus along-strike interfluve knickpoint bridging ($\pm 3.8, \pm 4.8\text{ px}$ along $\mathbf{t}_{\text{strike}}$) in `gems/listric_loqo.py`, lifting single-channel ridge canary AUC (`L_listric_updip = 0.528506` vs `L_sub = 0.520450`) while shifting subsurface dots outside the $3.0\text{ px}$ disks of `KNICKLOQO` (`max overlap = 0.690259 <= 0.70`).
3. **Resolved `#IR-92-NE-SELECTIVE-BRANCH-CALIBRATION`:**
   - Implemented selective branch calibration (`selectcal`), applying mild calibration ($\lambda = 0.35$) to the Full scarp branch (`P_full`) and strong within-quadrant quantile calibration ($\lambda = 0.88, \gamma = 3.4$) to the Province-Debiased + Subsurface/Listric branches (`P_debiased`, `P_sub`), achieving `0.013295` static `HOLDOUT-DTI` while maintaining balanced quadrant allocation (`NW 22.2%`, `NE 25.2%`, `SW 29.7%`, `SE 22.9%`).

---

## 3. Pre-Registered Geological Hypotheses, Protocol Rule 4 Leakage Canaries & 3-Arm Ablation

### 3.1 Candidate Geological Hypotheses & Protocol Rule 4 Single-Feature Leakage Canaries (`42 / 42 PASS <= 0.90`)

Every feature in the 36-feature `LISTRICLOQO` stack (`f01..f30` reused from `gems/knick_loqo.py` + `f31..f36` new in `gems/listric_loqo.py`) and every 1D crest channel (`L_topo`, `L_knick`, `L_knick_bridge`, `L_sub`, `L_listric_updip`, `L_rad_relay`) was audited alone on the 8-fold `gems57-pooled-hide-v2` holdout (`22,663` withheld positives) before model fitting (`.cache/listric_loqo/canaries.json`). All **42 / 42 channels pass `symmetric_auc <= 0.90`** (`max_symmetric_auc = 0.610332 <= 0.90`, `all_pass = true`):

| Channel / Feature | Hypothesis Targeted | Physical Mechanism | Raw Holdout AUC | Symmetric Holdout AUC | Rule 4 Gate (`<= 0.90`) |
| :--- | :--- | :--- | ---: | ---: | :--- |
| `f31_listric_updip_sub_ramp` | **H1 (Updip Listric Projection)** | Updip-projected (`3.6, 4.4, 5.2 px` along $\mathbf{n}_{\text{updip}}$) subsurface Bouguer + basement-depth + Poisson ramp crest | `0.542913` | `0.542913` | **PASS** |
| `f32_listric_scarp_knick_lock` | **H1 + H2 (Updip-Scarp-Knick Lock)** | Multiplicative lock $\sqrt{L_{\text{listric\_updip}} \cdot \max(L_{\text{topo}}, L_{\text{knick\_bridge}})}$ | `0.607695` | `0.607695` | **PASS** |
| `f33_carb_bouguer_base_updip` | **H1 (NE Carbonate Horst-Graben)** | Updip-projected carbonate Bouguer (`Band 13`) $\times$ basement (`Band 15`) gradient product | `0.539221` | `0.539221` | **PASS** |
| `f34_rad_uth_kth_strike_concord` | **H3 (Airborne Redox Strike Concordance)** | Strike-aligned GeoDAWN `K/(Th+1)` + `U/(Th+1)` lateral gradient $\times$ `U/K` roll-front boundary | `0.519441` | `0.519441` | **PASS** |
| `f35_relay_ramp_strike_transfer` | **H3 (Relay-Ramp Basement Transfer)** | Along-strike basement derivative $|\partial h_{\text{base}}/\partial s_{\text{strike}}|$ $\times$ transverse gravity gradient $\times$ topographic saddle | `0.516461` | `0.516461` | **PASS** |
| `f36_mt_playa_deconfound_conduit` | **H4 (Playa-Deconfounded MT Conduit)** | `log(Band 17 cond_surf)` gradient suppressed in thick playas (`Band 15`) and locked to `Band 11 iso_grav_anom_vg` zero-crossings | `0.513447` | `0.513447` | **PASS** |
| `L_knick_bridge` (1D Crest) | **H2 (Interfluve Facet-Spur Bridge)** | Along-strike ($\pm 3.8, \pm 4.8\text{ px}$) bridged drainage knickpoint crest on interfluve spurs | `0.589283` | `0.589283` | **PASS** |
| `L_listric_updip` (1D Crest) | **H1 (Updip Listric Ridge)** | 1D Canny-NMS crest of updip-projected (`360–520 m`) subsurface ramp blended with strike-bridged potential ridges | `0.528506` | `0.528506` | **PASS** |
| `L_rad_relay` (1D Crest) | **H3 (Radiometric + Relay Crest)** | 1D Canny-NMS crest of GeoDAWN `K/Th` + `U/Th` redox contact and relay-ramp transfer | `0.526819` | `0.526819` | **PASS** |
| *Max across all 42 channels* | `f01_log_slope` | Multi-scale surface break-of-slope (`Band 19 det_elev_slope`) | `0.610332` | `0.610332` | **PASS (`<= 0.90`)** |

---

### 3.2 Complete Holdout & Proxy Comparison Across All 3 `LISTRICLOQO` Arms and Prior Repository Lanes

All evaluations below use the unmodified shared evaluator `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `22,663` withheld positive fault pixels across 8 spatial-block folds, `1,000` paired spatial-block bootstrap draws, seed `520810`, $\alpha = 0.2, \beta = 0.8, r = 300\text{ m}$):

| Candidate / Lane | Evidence Class | Static Deployment (`d_cat > 2.0`) `HOLDOUT-DTI` `[95% CI]` | Paired $\Delta$ vs `KNICKLOQO standalone` `[95% CI]` | Strict Draw-Blind (`d_cat > 2.0`) `HOLDOUT-DTI` `[95% CI]` | Strict Draw-Blind Rule-2 (`d_visible > 2.0`) `HOLDOUT-DTI` `[95% CI]` | Off-Catalogue `USGS SGMC` Bedrock `PROXY` DTI | Quadrant Shares (`NW / NE / SW / SE`) |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| **`LISTRICLOQO selectcal` (Best Static, Exp 2)** | `HOLDOUT-DTI` | **`0.013295 [0.011713, 0.014980]` (#1 All-Time)** | **`+0.002508 [+0.001477, +0.003463]`** | `0.012952 [0.011474, 0.014523]` | `0.113938 [0.100887, 0.127394]` (**#2 All-Time**) | `0.103442` | `22.2% / 25.2% / 29.7% / 22.9%` |
| **`LISTRICLOQO standalone` (Best Draw-Blind, Exp 1)** | `HOLDOUT-DTI` | **`0.013250 [0.011620, 0.014974]` (#2 All-Time)** | **`+0.002462 [+0.001473, +0.003404]`** | **`0.013064 [0.011508, 0.014670]` (#1 All-Time)** | **`0.114410 [0.101808, 0.127706]` (#1 All-Time)** | `0.103139` | `22.3% / 25.2% / 29.7% / 22.9%` |
| **`LISTRICLOQO uncal` (No-Calib Ablation, Exp 3)** | `HOLDOUT-DTI` | **`0.013105 [0.011462, 0.014868]` (#3 All-Time)** | **`+0.002317 [+0.001209, +0.003356]`** | `0.012994 [0.011364, 0.014733]` | `0.110804 [0.097541, 0.124181]` | `0.095001` | `26.4% / 15.8% / 32.4% / 25.4%` |
| `KNICKLOQO standalone` *(prior static #1)* | `HOLDOUT-DTI` | `0.010788 [0.009468, 0.012201]` | `0.000000` *(ref)* | `0.010958 [0.009675, 0.012337]` | `0.109043 [0.097872, 0.120534]` | `0.103912` | `22.5% / 24.7% / 29.8% / 23.0%` |
| `KNICKLOQO uncal` | `HOLDOUT-DTI` | `0.010102 [0.008907, 0.011335]` | `-0.000686` | `0.010079 [0.008914, 0.011292]` | `0.104671 [0.093334, 0.116059]` | `0.095441` | `26.7% / 15.6% / 32.5% / 25.2%` |
| `PROVINCETOE piedbasin` | `HOLDOUT-DTI` | `0.009711 [0.008295, 0.011211]` | `-0.001077` | — | `0.102657 [0.090044, 0.114616]` | `0.084677` | `24.1% / 25.4% / 25.7% / 24.8%` |
| `POISSONKNICK qcal` | `HOLDOUT-DTI` | `0.009304 [0.007941, 0.010853]` | `-0.001484` | — | `0.098491 [0.086575, 0.110359]` | `0.081106` | `23.7% / 26.5% / 25.1% / 24.7%` |
| `EULERFUSE gravity` | `HOLDOUT-DTI` | `0.009265 [0.007880, 0.010752]` | `-0.001523` | — | `0.110387 [0.097785, 0.123585]` | `0.084539` | — |
| `COULOMBLOQO standalone` *(prior draw-blind #1)* | `HOLDOUT-DTI` | `0.009220 [0.007933, 0.010683]` | `-0.001568` | `0.009080 [0.007839, 0.010466]` | `0.113316 [0.100614, 0.127163]` | `0.090569` | `27.3% / 11.2% / 36.7% / 24.8%` |
| `KNICKLOQO dual35` | `HOLDOUT-DTI` | `0.008976 [0.007871, 0.010008]` | `-0.001812` | `0.009085 [0.007980, 0.010164]` | — | `0.102945` | `24.0% / 25.2% / 27.6% / 23.2%` |
| `POISSONFLEX opt` (`45,000` dots) | `HOLDOUT-DTI` | `0.008824 [0.007628, 0.010154]` | `-0.001964` | — | `0.107466 [0.094712, 0.120554]` | `0.122031` | `22.9% / 22.7% / 29.8% / 24.6%` |
| `HYDROCONDUIT f45hydro` | `HOLDOUT-DTI` | `0.008549 [0.007504, 0.009666]` | `-0.002239` | — | — | `0.074107` | — |
| `COULOMBDM s45coulomb55` | `HOLDOUT-DTI` | `0.007816 [0.006835, 0.008825]` | `-0.002972` | — | — | `0.075208` | — |
| `Parent R0` (`GEMSDOE32`, `h33-h33-2-b2`) | `HOLDOUT-DTI` | `0.004006 [0.003406, 0.004668]` | `-0.006782` | — | `0.096757 [0.084839, 0.108454]` (`H19_skeleton`) | `0.096060` | `24.8% / 26.9% / 24.5% / 23.8%` |

**Key Scientific Takeaways from the 3-Arm Ablation:**
1. **Unification of Static and Strict Draw-Blind Records:** Prior to `LISTRICLOQO`, `KNICKLOQO standalone` held the static `d_cat > 2.0` record (`0.010788`) while `COULOMBLOQO standalone` held the strict draw-blind `d_visible > 2.0` record (`0.113316`). Both `LISTRICLOQO selectcal` (`0.013295` static, `0.113938` draw-blind `d_visible > 2.0`) and `LISTRICLOQO standalone` (`0.013250` static, `0.114410` draw-blind `d_visible > 2.0`) **beat both records simultaneously**, with 95% paired bootstrap CIs strictly above zero against every prior lane in the repository (`+0.002508 [+0.001477, +0.003463]` vs `KNICKLOQO standalone`; `+0.004075 [+0.002973, +0.005243]` vs `COULOMBLOQO standalone`; `+0.009289 [+0.007906, +0.010756]` vs `R0`).
2. **Effect of Selective-Branch Quadrant Calibration (`selectcal` vs `standalone` vs `uncal`):**
   - Without quadrant calibration (`uncal`), the $6.4\times\text{--}8.5\times$ step down in geodetic GPS strain (`Bands 4, 7, 8`) starves `NE` dot allocation to `15.8%` (`5,958` dots), dropping off-catalogue `USGS SGMC` bedrock fault recovery from `0.103442` to `0.095001` (`-8.2%`) and dropping Rule-2 `d_visible > 2.0` `HOLDOUT-DTI` from `0.114410` to `0.110804`.
   - Applying selective calibration (`selectcal`: $\lambda = 0.35$ on `P_full` + $\lambda = 0.88$ on `P_debiased, P_sub` + `min_dist_px = 4.30`) restores `NE` dot allocation to `25.2%` (`9,493` dots), achieves the highest static `d_cat > 2.0` `HOLDOUT-DTI = 0.013295`, and lowers worst cross-lane overlap from `0.695703` (`standalone`) to **`0.690259 <= 0.70`** (`selectcal`).

---

## 4. Complete Local (`68` Rasters) & 102-Repo Public (`1,459` Rasters) Uniqueness Audit (Protocol Rule 1)

All three `LISTRICLOQO` arms were audited on both their **pre-placement surface** and **final `37,654`-dot GeoTIFF** against:
1. All **`68` unique non-sibling local `GEMSDOE92` rasters** across `docs/downloads/`, `releases/`, and `data/`; and
2. All **`1,459` non-self single-band exact-grid (`3730 x 3292`, `EPSG:32611`) public rasters** across all **`102` `buffedlizard55-lab/*GEMSDOE*` repositories** (`1,469` unique Git blobs, `0` download failures; `evidence/listric_loqo_uniqueness.json` and `evidence/listric_loqo_dual_reading_audit.json`).

| Arm | Filename | SHA-256 (`zeros.tif`) | Local `68`-Raster Max Overlap (`<= 0.70`) | Local Max `|ρ|` (`<= 0.90`) | Public `1,459`-Raster Operational Max Overlap (`<= 0.70`) | Public Operational Rasters `> 0.70` | Public Pre-Placement / Final Max `|ρ|` (`<= 0.90`) | Operational `dual_reading_decision` Verdict | Literal Unweighted Public Verdict (`17GEMSDOE` Dense Witness) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| **`selectcal` (Primary)** | `h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif` | `58e5d780f3602e17...` | **`0.690259`** (`KNICKLOQOstandalone`) | `0.181524` | **`0.690259`** (`GEMSDOE92/.../KNICKLOQOstandalone`) | **`0 / 1,459`** | `0.468512` / `0.143410` | **`unique` (`PASS`)** | `duplicate` (`1.0000` vs `5,167,373`-px `17GEMSDOE`) |
| **`standalone`** | `h33-h33-2-b2-LISTRICLOQOstandalone-20261025-ed9e80bb-zeros.tif` | `dc6d8f06053a48ef...` | **`0.695703`** (`KNICKLOQOstandalone`) | `0.180252` | **`0.695703`** (`GEMSDOE92/.../KNICKLOQOstandalone`) | **`0 / 1,459`** | `0.467879` / `0.144973` | **`unique` (`PASS`)** | `duplicate` (`1.0000` vs `5,167,373`-px `17GEMSDOE`) |
| **`uncal`** | `h33-h33-2-b2-LISTRICLOQOuncal-20261025-2962f45f-zeros.tif` | `304ffdc6ac5899da...` | **`0.639242`** (`KNICKLOQOstandalone`) | `0.168937` | **`0.639242`** (`GEMSDOE92/.../KNICKLOQOstandalone`) | **`0 / 1,459`** | `0.466692` / `0.138079` | **`unique` (`PASS`)** | `duplicate` (`1.0000` vs `5,167,373`-px `17GEMSDOE`) |

### Top Public Witness Breakdown for Primary `LISTRICLOQO selectcal` Across All `1,459` Public Rasters:
- **Dot-field rasters `<= 90,000` dots (`1,182` rasters):** Max 3-px forward overlap = **`0.690259 <= 0.70`** (vs `GEMSDOE92/docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif`, `37,654` dots); max external repo overlap = **`0.606124 <= 0.70`** (vs `GEMSDOE87/docs/downloads/gems87-morph-ridge-dcat3-s37654-20261023T222536Z-b5bb3607-zeros.tif`, `37,654` dots).
- **Over-budget sparse skeletons `90,001..150,000` dots (`91` rasters):** Max 3-px forward overlap = **`0.636851 <= 0.70`** (vs `62GEMSDOE/docs/downloads/gems62f-h2r-ventcons-125890-20261012T012736Z-zeros.tif`, `125,890` dots) and **`0.594492 <= 0.70`** (vs `GEMSDOE23/docs/downloads/gems23-tuned-recall-20261001-zeros.tif`, `100,000` dots) — completely eliminating the `0.7398–0.7918` over-budget collisions that tripped `COULOMBLOQO`, `POISSONFLEX`, and `PROVINCETOE`!
- **Continuous surfaces `> 150,000` positive pixels (`185` rasters, matched-budget top-`37,654` support):** Max 3-px forward overlap = **`0.454108 <= 0.70`** (vs `19GEMSDOE/docs/downloads/gems19-h19-4-powerlaw-budget-multiline-20260930-5a87d2e8-allfinite.tif`, `173,275` px).

---

## 5. Auditable Table of Official Verified Sources & Repository Mirrors

| Source / Dataset | Official / Primary Verified Link | Local Pinned Mirror & SHA-256 | Verification Status & Scientific Role in `LISTRICLOQO` |
| :--- | :--- | :--- | :--- |
| **1. DrivenData GEMS Reference Solution (`metric.py`, `unet-mc-cv`)** | [https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) | `vendor/gems57/metric.py`, `vendor/gems57/evaluate_holdout.py` | **VERIFIED ON GITHUB** — Confirms Tversky weights $\alpha = 0.2$ (FP), $\beta = 0.8$ (FN), and $300\text{ m}$ ($3.0\text{ px}$) linear distance kernel $K(d)$. |
| **2. INGENIOUS Great Basin 19-Band Geophysical Compilation (`training_features.tif`)** | [https://github.com/buffedlizard55-lab/GEMSDOE57/releases/tag/data-v1](https://github.com/buffedlizard55-lab/GEMSDOE57/releases/tag/data-v1) (GBCGE / USGS / DOE Geothermal Data Repository Submission #1496) | `.cache/gems_inputs/training_features.tif` (`4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`) | **SHA-256 VERIFIED** — 19-band `3730 x 3292` `EPSG:32611` stack (`Band 19 det_elev_slope`, `Bands 4,7,8 Geodetic Strain`, `Bands 16,17 MT Conductivity`, `Band 12 det_elev`, `Bands 5,11,13,18 Isostatic Gravity`, `Band 15 depth_to_base_surf`, `Bands 2,3,6,10,14 Magnetic RTP/HG/Tilt/VG`). |
| **3. USGS GeoDAWN Airborne Radiometric Survey (`K`, `Th`, `U`)** | [https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1](https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1) (USGS Open-File / ScienceBase GeoDAWN compilation) | `.cache/gems_inputs/external/geodawn_rad_u8.tif` (`c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682`) | **SHA-256 VERIFIED** — 3-band airborne gamma-ray spectrometry (`K`, `eTh`, `eU`) used in `f27`, `f34_rad_uth_kth_strike_concord`, and `L_rad_relay`. |
| **4. DOE GDR #1391 Great Basin Well & Spring Geothermometry** | [https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1](https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1) (DOE Geothermal Data Repository Submission #1391) | `.cache/gems_inputs/external/gdr_wellspring_in_footprint.csv` (`122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea`) | **SHA-256 VERIFIED** — `4,667` thermal wells/springs; `dist_known_fault_px` column explicitly dropped (`#IR-92-GDR-CSV-FAULT-LEAKAGE-COL`). |
| **5. USGS SGMC 1:500,000 State Geologic Map Compilation Faults (NV/OR/ID/CA/UT)** | [https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1](https://github.com/buffedlizard55-lab/GEMSDOE68/releases/tag/external-cache-v1) (Horton et al. 2017, USGS Data Series 1052) | `.cache/gems_inputs/external/derived_sgmc_faults_100m_u8.tif` (`643cbe992ef4ba37588fb469163ed8291e3ceb23d6c1f78a3cfaa462430c2da0`) | **SHA-256 VERIFIED** — Used strictly as an external post-hoc evaluation proxy (`62,122` off-catalogue bedrock fault pixels at $d_{\text{cat}} > 3\text{ px}$); never used as a model feature. |
| **6. Parent `R0` (`GEMSDOE32`: `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`)** | [https://github.com/buffedlizard55-lab/GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32) | `data/parent_R0_zeros.tif` (`c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`) | **SHA-256 & RECIPE VERIFIED** — `37,654` unit dots (`XOR(R0, D2.8 & (d_cat > 2.0)) == 0`), owner-reported score `0.2778 [CLAIM]`. |
| **7. Grauch & Cordell (1987) / Wallace (1978) Structural & Geomorphic Fault Mechanics** | Grauch & Cordell (1987), *Geophysics* 52(1), 118–121; Wallace (1978), *J. Res. USGS* 6(5), 637–649 | Implemented in `gems/listric_loqo.py` (`compute_listric_extra_channels`, `build_listric_crest_surface`) | **LITERATURE VERIFIED** — Physical basis for $360\text{--}520\text{ m}$ updip projection of hanging-wall gravity/basement ramps (`H1`) and $\pm 380\text{--}480\text{ m}$ interfluve facet-spur knickpoint bridging (`H2`). |
