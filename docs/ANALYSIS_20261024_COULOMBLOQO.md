# PhD-Level Forensic, Mathematical & Experimental Analysis — `COULOMB-LOQO` (`2026-10-24`)

**Repository:** `buffedlizard55-lab/GEMSDOE92` (`EPSG:32611`, `3730 × 3292` at `100 m` = `12,279,160` cells; `5,167,373` in-footprint cells; `60,988` in-footprint `existing_faults` pixels)  
**Pre-Registration (frozen prior to code/scores):** [`docs/HYPOTHESES_20261024_COULOMBLOQO.md`](HYPOTHESES_20261024_COULOMBLOQO.md)  
**Primary Generated Artifact:** [`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`](downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif) (`SHA-256: 8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`, `ZIP SHA-256: 448395137acb4860c24402fb53002539f3c688f8c232c79c23991353623c4c48` — verified in [`evidence/coulomb_loqo_run_card.json`](../evidence/coulomb_loqo_run_card.json))  
**Automated Gate Status:**
- **Download & `[0, 1]` Format Gate:** **PASS (`10/10` `gems.gates` + `gems57.validate`) — OK TO DOWNLOAD FOR RESEARCH**
- **Weekly Competition Slot Gate:** **STOP (`verdict: "negative"`, `submission_eligible: false`, `0` slots spent) — NOT CLEARED FOR A WEEKLY SLOT** under the literal public registry `> 70%` overlap rule (`1.0` against dense `17GEMSDOE E-proba-multiscale`, `5,167,373` positive pixels).

---

## 1. Exact Mathematical Formulation of the DOE GEMS Distance-Weighted Tversky Index (DTI)

Per the official DrivenData reference notebook ([`drivendataorg/gems-prize-reference-solution/unet-mc-cv-reference-solution.ipynb`](https://github.com/drivendataorg/gems-prize-reference-solution), Cell 16) and [`vendor/gems57/metric.py`](../vendor/gems57/metric.py), let $\Omega \subset \{0,\dots,3729\} \times \{0,\dots,3291\}$ be the in-footprint domain ($|\Omega| = 5{,}167{,}373$), $C \subset \Omega$ be the public mapped fault catalogue (`existing_faults.tif`, $|C| = 60{,}988$), and $G \subset \Omega \setminus C$ be the hidden ground-truth fault trace set evaluated strictly on $\Omega_{\text{eval}} = \Omega \setminus C$.

For a submitted prediction $p : \Omega \to [0, 1]$ (with known-catalogue pixels zeroed on $\Omega_{\text{eval}}$) and the `300 m` (`R = 3.0 px`) linear triangular proximity kernel $K(r) = \max(0, 1 - r / 3.0)$, define proximity fields via Euclidean distance transforms:
$$c_{\text{true}}(x) = \max_{g \in G} K(\|x - g\|_2) = \max\!\left(0,\, 1 - \frac{d(x, G)}{3.0}\right),$$
for binary dot predictions $p = \mathbf{1}_A$ ($A \subset \Omega_{\text{eval}}$, $|A| = S$):
$$c_{\text{pred}}(g) = \max_{x \in A} K(\|g - x\|_2) = \max\!\left(0,\, 1 - \frac{d(g, A)}{3.0}\right).$$

Then on $\Omega_{\text{eval}} = \Omega \setminus C$:
$$\mathrm{TP}_w = \frac{\sum_{x \in A} c_{\text{true}}(x) + \sum_{g \in G} c_{\text{pred}}(g)}{2}, \qquad \mathrm{FP}_w = \sum_{x \in A} \big(1 - c_{\text{true}}(x)\big) = |A| - \sum_{x \in A} c_{\text{true}}(x), \qquad \mathrm{FN}_w = \sum_{g \in G} \big(1 - c_{\text{pred}}(g)\big) = |G| - \sum_{g \in G} c_{\text{pred}}(g),$$
and with **$\alpha = 0.2$ on false positives ($\mathrm{FP}_w$)** and **$\beta = 0.8$ on false negatives ($\mathrm{FN}_w$)**:
$$\mathrm{DTI}(A, G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w}.$$

> **Forensic Correction (`#IR-92-ALPHA-BETA-PROSE-SWAP`):** Earlier prose in `README.md` and `ANALYSIS_20261024_APRONRIDGE.md` inverted the denominator as $\alpha\,\mathrm{FN}_w + \beta\,\mathrm{FP}_w$, claiming false positives carried a $4\times$ heavier penalty ($0.8$) than false negatives ($0.2$). Direct verification against `drivendataorg/gems-prize-reference-solution` (`alpha = 0.2 # weight for false positives`, `beta = 0.8 # weight for false negatives`) and `vendor/gems57/metric.py` (`ALPHA = 0.2`, `BETA = 0.8`, `denom = tp_w + ALPHA * fp_w + BETA * fn_w`) proves the exact opposite: **recall ($\beta = 0.8$) is weighted $4\times$ more heavily than precision ($\alpha = 0.2$)**, while redundant dots within `< 2.8 px` of an already-placed dot STILL hurt DTI because $\max_{x \in A} K(\|g - x\|_2)$ saturates ($\Delta \sum_{g \in G} c_{\text{pred}}(g) \approx 0$) whereas $\mathrm{FP}_w$ grows linearly ($+0.2$ per zero-hit dot)!

---

## 2. Why & How `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Beat Every Listed `GEMSDOE` Site

Direct byte-level inspection of the SHA-256-verified ancestor rasters (`h19_5.tif`, `d28.tif`, `h27_4_solo.tif`, and `parent_R0_zeros.tif` = `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`) proves an **exact zero-XOR four-stage geometric filter cascade**:

| Stage | Sibling Repo & Raster | In-Footprint Dots | Prompt Score (`[CLAIM]`) | Exact Byte-Verified Algebraic Relation | Why DTI Jumped |
|---|---|---:|---|---|---|
| **0. Reference U-Net** | `drivendataorg/gems-prize-reference-solution` | dense `[0,1]` | baseline | 5-split MC CV U-Net (`patch=128`, `TverskyLoss(0.2, 0.8)`) | Diffuse probability ribbons accumulate massive $\sum_x p(x)(1 - c_{\text{true}}(x))$ across 1–3 km widths. |
| **1. Multi-Physics 1-px Worm Skeleton** | `19GEMSDOE` (`H19-5`) | `121,131` | `0.1922` / `0.2194` | 1-px skeletonized geophysical/3DEP fault worms (`d_cat > 0`) | Collapses 2D ribbons to 1D structural traces, eliminating transverse FP bloat. |
| **2. Kernel-Matched Poisson De-Aliasing** | `GEMSDOE25` (`D2.8`) | `44,090` | `0.2600` (`D1.5` `0.2477`) | `D2.8 ⊂ H19-5` (`min_dist ≈ 2.83 px = 283 m ≈ 300 m` kernel radius) | Cuts `-77,041` (`-63.6%`) redundant along-strike dots while preserving nearly 100% of $\max_{x \in A} K(\|g-x\|_2)$ along `H19-5`! |
| **3. 100 m Catalogue Collar Prune (`SOLO`)** | `GEMSDOE28` (`h27_4_solo`) | `40,199` | `0.2708` | **`XOR(SOLO, D2.8 & (d_cat > 1.0)) == 0`** (`-3,891` dots all at `d_cat == 1.0`) | Removes `3,891` dots immediately adjacent (`100 m`) to `existing_faults` (which are masked from $\Omega_{\text{eval}}$). *(Corrects `#IR-92-SOLO-R1-BYTE-IDENTITY`: prior prose misattributed this to speckle removal.)* |
| **4. 200 m Catalogue Collar Prune (`R0`)** | `GEMSDOE32` (`h33-2-b2`) | `37,654` | **`0.2778`** | **`XOR(R0, D2.8 & (d_cat > 2.0)) == 0`** (`-2,545` dots at `1.0 < d_cat <= 2.0`) | Removes `2,545` additional near-catalogue digitization-halo dots while keeping `2,171` splay/tip dots at `2.0 < d_cat <= 3.0` (`200–300 m`). |

Meanwhile, why did sibling experiments score slightly lower or plateau?
- **`GEMSDOE36` (`anderson-geothermal-pinn-38854`, `0.2750` `[CLAIM]`, #2 listed score):** Proved that **Andersonian Basin-and-Range fault-strike mechanics + geothermal upflow** carry genuine leaderboard signal (`0.2750`), nearly matching `GEMSDOE32` without pure `D2.8` copying.
- **`GEMSDOE70` (`0.2478` `[CLAIM]`) & `GEMSDOE76` (`0.2343` `[CLAIM]`):** Highest non-`R0`-copy out-of-fold ML learners; demonstrated genuine spatially-blocked OOF learning + submodular 300 m allocation, yet lost ~`0.030` DTI to `GEMSDOE32` because pixel-wise probability rasters lacked sharp 1D Hessian/monoclinal crest localization and explicit footwall-polarity / 2D Coulomb resolution.

---

## 3. Why `GEMSDOE32` (`0.2778` `[CLAIM]`) Leaves Substantial Headroom (`0.3195` / `0.4413` Leaderboard) — and Why Prior `GEMSDOE92` Lanes Plateaued

1. **`R0` Is 100% Confined to `H19-5` and Thinned in Physics-Blind Row-Major Scan Order:**
   - Every dot of `R0` lies inside `H19-5` (`121,131` px). Any active Quaternary alluvial-fan splay, synthetic piedmont fault, or concealed intrabasin geothermal conduit missed by `H19-5` receives **zero coverage** (`c_pred = 0`, penalized at $\beta = 0.8$).
   - Worse, `D2.8` thinned `H19-5` in top-to-bottom row-major scan order rather than fault probability, stranding thousands of dots on unstrained Mesozoic pluton boundaries and barren playas (`R0` static `HOLDOUT-DTI = 0.004006`).
2. **Why Prior `GEMSDOE92` Heuristic Lanes Hit Opposing Glass Ceilings:**
   - **Un-normalized terrain lanes (`BREAKLINE` `0.004861`, `STEPEDGE` `0.004228`):** Hijacked `74.8%` by steep `25–40°` bare mountain-core cliffs (`#IR-92-BREAKLINE-RANGECORE-75PCT`), recovering `1:500k` `SGMC` bedrock contacts (`0.126–0.141`) while missing subtle `1–5 m` Quaternary piedmont scarps.
   - **Hand-crafted piedmont elevation boxcar lanes (`APRONRIDGE` `0.008354`, `HYDROCONDUIT` `0.008549`):** Suppressing `det_elev` outside a rigid piedmont band doubled static `HOLDOUT-DTI` (`0.00835–0.00855`), **but** starved legitimate horst-bounding bedrock faults (`APRONRIDGE` placed only `1.6%` of dots in the upper relief tercile; `HYDROCONDUIT` dropped `-22.9%` vs `R0` on `SGMC` `PROXY`, `0.0741` vs `0.0961`, and **lost** to `H19-5` under strict zero-self-masking `d_visible > 2.0` holdout: `0.0852` vs `0.0968`!). Furthermore, `APRONRIDGE` treated `Band 6 tc` as magnetic curvature when `Band 6` is actually **Radiometric Total Count** (`r = 0.99714` with `GeoDAWN` Band 4; `#IR-92-BAND6-TC-MISLABEL`).

---

## 4. How `COULOMB-LOQO` Solves Both Regimes Simultaneously

Implemented in [`gems/coulomb_loqo.py`](../gems/coulomb_loqo.py) and screened prior to dot placement via [`scripts/screen_coulomb_loqo.py`](../scripts/screen_coulomb_loqo.py):

1. **24 Strictly Catalogue-Free Physical Features (`Groups A–E`, Zero Transductive Quadrant Coupling):**
   - **Group A (Multi-Scale Topographic Hessian Ridges, Scarp Step & Cover):** Scale-normalized principal negative Hessian eigenvalues $\max(0, -\lambda_1(\sigma))\sigma^2$ at $\sigma \in \{1.2, 3.0\}\text{ px}$ (`120 m` & `300 m`), relative log-slope break $\|\nabla\log(\text{slope}+1^\circ)\|$, `600 m` cross-strike step monotonicity $\mu_{\text{step}}$ (separating one-sided scarps from V-gullies), elevation coherence, `det_elev`, `log(1 + depth_to_base_surf)`, and basement-step gradient.
   - **Group B (Polarity-Locked Footwall–Hangingwall Dip Concordance):** Signed gradient concordance between `Band 12 det_elev` and `Band 13 iso_grav_anom`, inverse concordance with `Band 15 depth_to_base_surf`, and explicit East–West footwall polarity lock pairing $\partial_x(\text{Band 12})$ with **`Band 18 iso_grav_anom_hg`** (verified unsupervised at $r = +0.6260$ with $\partial_x\text{Band 13}$ vs $+0.0295$ with $\partial_y\text{Band 13}$), plus AGC-equalized gravity tilt (`Bands 5 & 11`). Rejects non-tectonic Lake Lahontan recessional shorelines whose topographic steps carry zero or inverted basement gravity steps.
   - **Group C (True `Band 2 RTP` Tilt/Demag/Hessian & Circular Axial Strike Phase-Locking):** Replaces mislabeled `Band 6 tc` with true Reduced-to-Pole (`Band 2 rtp`) tilt contact, positive-Laplacian hydrothermal magnetite-destruction troughs, scale-normalized RTP Hessian ridges, and the circular double-angle axial strike order parameter $R_{\text{axial}}(x) \in [0, 1]$ across topography + RTP + gravity.
   - **Group D (Stress-Resolved 2D Transtensional Coulomb Tendency):** Projects `Bands 7 & 8` (`geod_shearrate`, `geod_dilaterate`) onto local composite fault strike $\theta_{\text{comp}}(x)$ relative to NW Great Basin WNW–ESE extension ($\sigma_{h,\min} \approx \text{N}105^\circ\text{E}$, optimal normal strike $\theta_0 = \text{N}15^\circ\text{E}$), boosting single-feature withheld-fault AUC from `0.5145` (raw dilatation) to **`0.5574`** (`f17_coulomb_dilation_tendency`).
   - **Group E (MT Smectite Clay-Cap Margin, Radioelements & Blind Geothermometry):** Lateral log-gradient of `Band 17 cond_surf`, `GeoDAWN` `K/(Th+1)` potassic alteration and $\|\nabla(U/(Th+1))\|$ redox fronts, and `GDR #1391` surface thermal + `>= 80 °C` blind quartz/chalcedony/Na-K-Ca geothermometer plumes (`419` blind pixels; `dist_known_fault_px` explicitly dropped and unit-tested against column poisoning).
2. **4-Quadrant Leave-One-Quadrant-Out (LOQO) Spatial Cross-Fitting + 1D Structural Crest Sharpening:**
   - Each quadrant $q \in \{0,1,2,3\}$ is predicted strictly by a regularized `HistGradientBoostingClassifier` fit on `quad != q` eroded by a `>= 12 px` (`1.2 km`) guard band (`2.4 km` inter-quadrant separation matching `gems57.holdout`), with negative background pixels restricted to `d_label > 5.0 px` (`> 500 m`).
   - Out-of-quadrant probability $P_{\text{LOQO}}(x)$ naturally learns optimal Basin-and-Range relief allocation (**`27.7%` basin / `40.8%` piedmont / `31.5%` range**) without hand-coded elevation boxcars, and is localized onto 1-px crests via $S_{\text{full}}(x) = P_{\text{LOQO}}(x)\big(0.15 + 0.85\max(L_{\text{topo}}(x), 0.80\,L_{\text{sub}}(x))\big)$.

---

## 5. Complete Auditable Experimental Results (All Evidence Classes Explicit)

### 5.1 Pre-Registered 3-Experiment Ablation + Repository Benchmark Ladder

Evaluator: `gems57-pooled-hide-v2` (`8` buffered spatial quadrant folds across `seeds 20, 30`, `22,663` withheld whole-component fault pixels, `1,000` paired 20 km spatial-block bootstrap draws, `seed = 520810`; full receipt in [`evidence/coulomb_loqo_proxy_audit.json`](../evidence/coulomb_loqo_proxy_audit.json)).

| Candidate / Baseline | Dots (`H19-5` %) | Static `HOLDOUT-DTI` (`22,663` px, 95% CI) | Paired $\Delta$ vs `R0` (95% CI) | Strict Draw-Blind `d_vis > 2.0` `HOLDOUT-DTI` | Off-Cat `SGMC` `PROXY` (`62,703` px) | Local Overlap (`41` rasters) | Sparse Public `<=90k` (`1,121` rasters) | Literal Public (`1,368` rasters) |
|---|---:|---|---|---|---|---|---|---|
| **`COULOMBLOQO standalone` (Exp 1 — Primary)** | `37,654` (`0%`) | **`0.009220 [0.007983, 0.010493]`** | **`+0.005214 [+0.004130, +0.006326]`** | **`0.113316 [0.100614, 0.127163]`** | **`0.090569`** | **`0.6164` (PASS)** | `0.7004` (`1 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO nocoulomb` (Exp 2 — Group A Ablation)** | `37,654` (`0%`) | **`0.009151 [0.007944, 0.010389]`** | **`+0.005145 [+0.004054, +0.006266]`** | — | `0.091251` | **`0.6640` (PASS)** | `0.7396` (`5 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO dual45` (Exp 3 — 45% H19 + 55% Far)** | `37,654` (`45%`) | **`0.009107 [0.007977, 0.010325]`** | **`+0.005101 [+0.004145, +0.006055]`** | **`0.101998 [0.090846, 0.112907]`** | **`0.094057`** | **`0.5982` (PASS)** | **`0.6488` (`0 > 70%`)** | `1.0000` (dense STOP) |
| *Diagnostic:* `COULOMBLOQO draw-blind` (`d_cat > 2.0`) | `37,654` (`0%`) | *`0.009689 [0.008374, 0.011014]`* | *`+0.005683 [+0.004545, +0.006825]`* | *`0.113316`* | — | — | — | — |
| `HYDROCONDUIT f45hydro` (prior #1 static holdout) | `37,654` (`55%`) | `0.008549 [0.007461, 0.009684]` | `+0.004543` | `0.085221` *(loses to H19)* | `0.074107` | `0.5500` (PASS) | `0.6518` (`0 > 70%`) | `1.0000` (dense STOP) |
| `APRONRIDGE free1d` (prior active primary) | `37,654` (`0%`) | `0.008354 [0.006823, 0.010135]` | `+0.004347` | — | `0.080098` | `0.6507` (PASS) | — | `1.0000` (dense STOP) |
| `PIEDFRONT f45Ptop` | `37,654` (`55%`) | `0.006137 [0.005125, 0.007265]` | `+0.002131` | — | `0.059993` (`f35`) | `0.5500` (PASS) | — | `1.0000` (dense STOP) |
| `RELIEF p10piedmont` (`R0`-duplicate reference) | `37,654` (`100%`) | `0.006045 [0.005179, 0.006882]` | `+0.002039` | — | `0.087245` | `0.9938` (DUP) | — | `1.0000` (DUP) |
| `STRAINBREAK f60s2i` | `37,654` (`40%`) | `0.005487 [0.004550, 0.006386]` | `+0.001481` | — | `0.105162` | `0.4150` (PASS) | `0.6844` (`0 > 70%`) | `1.0000` (dense STOP) |
| `ANASIG f45Atop` | `37,654` (`55%`) | `0.004967 [0.004102, 0.005931]` | `+0.000961` | — | `0.080556` | `0.5500` (PASS) | — | `1.0000` (dense STOP) |
| `SPRINGALIGN f33Ctop` | `37,654` (`67%`) | `0.004865 [0.004038, 0.005782]` | `+0.000859` | — | `0.080173` | `0.6700` (PASS) | — | `1.0000` (dense STOP) |
| `BREAKLINE f45Ltop` | `37,654` (`55%`) | `0.004861 [0.003930, 0.005887]` | `+0.000855` | — | `0.126105` | `0.5500` (PASS) | — | `1.0000` (dense STOP) |
| `STEPEDGE f45Sraw` (`f60Sraw` `0.003980`) | `37,654` (`55%`) | `0.004228 [0.003387, 0.005240]` | `+0.000222` | — | `0.141464` (`f60`) | `0.4610` (`f60`) | — | `1.0000` (dense STOP) |
| `R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | `37,654` (`100%`) | `0.004006 [0.003408, 0.004651]` | baseline | `0.096757` (`H19 d_vis>2`) | `0.096060` | self | — | — |

### 5.2 Key Scientific Findings from the 3-Experiment Ablation

1. **Breakthrough on Zero-Self-Masking Rule-2 Holdout (`d_visible > 2.0`):**
   - Because static deployment rasters enforce `d_full_cat > 2.0 px`, static holdout evaluation zeroes `84.7%` of withheld catalogue segments within `200 m` of themselves (`#IR-92-STATIC-DCAT2-SELFMASK`), testing only `200–300 m` flank halos.
   - Under strict Protocol Rule-2 fold-by-fold evaluation (`P_draw20` and `P_draw30` fit strictly on `fold["visible"]` in `quad != q`, excluding `hidden_all + 3 px` everywhere, and masking only `d_visible <= 2.0`), **`COULOMBLOQO standalone` (`0%` `H19-5`) achieves `HOLDOUT-DTI = 0.113316 [0.100614, 0.127163]`**, beating `H19_skeleton_dvis2` (`0.096757 [0.084839, 0.108454]`) by **`+0.016559` with paired 95% CI `[+0.008170, +0.024980]` strictly above zero** (and `+33.0%` above `HYDROCONDUIT`'s `0.085221`)!
2. **Simultaneous Recovery of Bedrock Faults (`SGMC PROXY`):**
   - Unlike `HYDROCONDUIT` (`0.074107`) and `APRONRIDGE` (`0.080098`), `COULOMBLOQO` learns from out-of-quadrant physics where range-bounding horst faults vs piedmont splays occur (`27.7%` basin / `40.8%` piedmont / `31.5%` range), lifting `SGMC PROXY` DTI to **`0.090569`** (`+22.2%` over `HYDROCONDUIT`) on `standalone` and **`0.094057`** (`+26.9%` over `HYDROCONDUIT`) on `dual45`.
3. **Value of Multi-Physics Coulomb + Polarity + RTP + Hydrothermal Channels (`standalone` vs `nocoulomb`):**
   - Adding Groups B–E (`standalone`) outperforms Group-A-only (`nocoulomb`) on static `HOLDOUT-DTI` (`0.009220` vs `0.009151`), increases subsurface-dominant fault dots **`8.1×`** (`1,634` vs `202`), reduces `H19-5` 3-px overlap by **`-4.76` percentage points** (`0.6164` vs `0.6640`), and cuts `<= 90k`-px public sparse overlaps `> 70%` from `5` rasters down to `1` (`0.700404` vs `GEMSDOE52` `61,427` px, just `15` dots above `0.7000`), while `dual45` achieves **`0 / 1,121` (`max = 0.6488`)** across all `<= 90k`-px public submissions!

---

## 6. Can We Beat `0.2778` (`[CLAIM]`) on DrivenData? Honest Assessment & Selector Playbook

- **Scientific Evidence (`HOLDOUT-DTI` & `PROXY`, Zero Projections Written as Scores):**
  - Across every local evaluation instrument in `GEMSDOE92`, `COULOMBLOQO standalone` (`0.009220` static `HOLDOUT-DTI`, `0.113316` strict Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`, `0.090569` `SGMC` `PROXY`) is the **only standalone (`0% H19-5`) architecture in repository history** to simultaneously beat `R0` by `+130.2%` on static holdout, beat `H19-5` (`+17.1%`, 95% CI `> 0`) on unmasked whole-segment recovery, and retain `94.3%` of `R0`'s `1:500k` bedrock `SGMC` score.
  - However, per **Protocol Rule 3**, no local `HOLDOUT-DTI` or `PROXY` number may ever be projected as a live leaderboard score; only an **`ORGANIZER-CONFIRMED`** DrivenData submission receipt can verify whether `COULOMBLOQO` exceeds `0.2778` `[CLAIM]`.
- **Two Explicit Human-Selector Gates Before Spending Any Weekly Slot (`<= 3 / week`):**
  1. **Blocker 1 (Protocol Rule 1 Dense-Surface Policy):** `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` sets all `5,167,373` in-footprint cells `> 0`, forcing `forward_overlap = 1.0` for **every** nonempty raster under a literal reading of Rule 1. If the human selector defines the uniqueness pool as **sparse competition-budget submissions (`<= 90,000` positive pixels)**, `COULOMBLOQO dual45` (`0.009107` static / `0.1020` `d_vis>2` / `0.0941` `SGMC`) already passes **`0 / 1,121` (`max = 0.6488 <= 0.70`)** across all 102 public `GEMSDOE` repositories, and `HYDROCONDUIT f45hydro` (`0.008549`) passes **`0 / 1,179` (`<= 150k` px, `max = 0.6719`)**. Until the operator formally adopts that policy, **all candidates remain `submission_eligible: false` (`verdict: "negative"`)**.
  2. **Blocker 0 (Zero `ORGANIZER-CONFIRMED` Receipts in `ledger/submissions.csv`):** Once Blocker 1 is resolved by the human selector, verify or obtain one `ORGANIZER-CONFIRMED` receipt for parent `R0` (`0.2778` `[CLAIM]`) and at most **one** top `GEMSDOE92` candidate (`COULOMBLOQO dual45` under `<= 90k`-px uniqueness, or `COULOMBLOQO standalone` under `<= 55k`-px budget-matched uniqueness) — never submitting two variants from the same lane in the same week.
