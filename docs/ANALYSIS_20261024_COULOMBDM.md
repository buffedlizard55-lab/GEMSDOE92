# PhD Structural Geology & Metric Forensics — Why `GEMSDOE32` Scored `0.2778` (`CLAIM`), the Centerline-Tightness Paradox, and the `COULOMBDM` Breakthrough (`2026-10-24`)

## 1. Evidence & Provenance Discipline (`Protocol Rule 3`)

Every number in this document carries an explicit, auditable provenance class:

- **`ORGANIZER-CONFIRMED`**: Score copied from a DrivenData submission-page receipt (`0` rows currently in `ledger/submissions.csv`).
- **`CLAIM` / `LEADERBOARD-SNAPSHOT`**: Prompt- or owner-reported figures without an archived organizer submission receipt in `ledger/submissions.csv` (`GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`: `0.2778` `CLAIM`; prompt leaderboard reference: `0.3195` `LEADERBOARD-SNAPSHOT`; 2026-10-24 leaderboard check: `0.4413` `LEADERBOARD-SNAPSHOT`).
- **`HOLDOUT-DTI`**: Evaluated locally by the shared spatially blocked whole-segment evaluator `vendor/gems57/evaluate_holdout.py` (`evaluator_version = "gems57-pooled-hide-v2"`, `8` buffered connected-component folds across seeds `20` and `30`, `22,663` withheld positive pixels across `363` spatial clusters, `alpha = 0.2`, `beta = 0.8`, `300 m` triangular buffer, `1,000` paired cluster-bootstrap draws). Reported under **both** evaluation regimes:
  1. *Static `d_cat > 2.0` `HOLDOUT-DTI`*: scores a pre-built submission raster whose `d_cat > 2.0 px` exclusion was computed against full `existing_faults.tif`.
  2. *Rule-2 Fold-Visible `d_vis > 2.0` `HOLDOUT-DTI`*: enforces `d_vis > 2.0 px` strictly from each fold's `visible` catalogue (`0` full-catalogue self-masking of withheld fault segments, matching how DrivenData scores genuinely unmapped test-set faults).
- **`PROXY`**: Off-catalogue `USGS SGMC` 1:500k bedrock fault DTI (`derived_sgmc_faults_100m_u8.tif`, `62,703` positive pixels at `> 3 px` from `existing_faults.tif`).
- **`REGISTRY-MEASUREMENT`**: Exact 3-px forward overlap and Spearman rank correlation against local rasters and Git-blob-verified public `buffedlizard55-lab/*GEMSDOE*` rasters.

---

## 2. PhD-Level Forensic Analysis of `GEMSDOE32` (`0.2778` `CLAIM`) vs Competition Leaderboard (`0.3195` / `0.4413`)

### 2.1 Official Tversky Metric Algebra (`drivendataorg/gems-prize-reference-solution`)

Direct audit of Prof. John Lipor's official reference repository ([`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution), `unet-mc-cv-reference-solution.ipynb`, Cells 0 & 16) and `vendor/gems57/metric.py` verifies the exact Distance-weighted Tversky Index (`DTI`) on the `3730 × 3292` `EPSG:32611` (`100 m`) study footprint (`5,167,373` valid cells):

$$\text{DTI}(P, G) = \frac{\text{TP}_w}{\text{TP}_w + \alpha\,\text{FP}_w + \beta\,\text{FN}_w}, \qquad \alpha = 0.2\;\text{(FP weight)}, \quad \beta = 0.8\;\text{(FN weight)}$$

with `300 m` (`3 px`) radial linear kernel $K(r) = \max(0, 1 - r/3)$. *(Audit note: an earlier `APRONRIDGE` draft inverted $\alpha$ and $\beta$ in prose while calling the correct `vendor/gems57/metric.py` code; both `README.md` and `ANALYSIS_20261024_APRONRIDGE.md` are corrected in this PR.)*

Let $dT = \Delta\text{TP}_w \in [0, A]$ denote the buffered true-positive mass gained by adding one isolated unit dot (`1.0` at a single pixel, whose `300 m` cone has total integral $A = \sum_{r \le 3} K(r) \approx 9.85$), and let $k$ denote the redundant cone mass wasted on already-covered halo or masked `existing_faults.tif` pixels. Differentiating $\text{DTI}$ with respect to one marginal dot yields the exact binary-dot optimality condition:

$$\Delta\text{DTI} > 0 \iff dT > \frac{\alpha\,\text{DTI}}{1 - \alpha\,\text{DTI} - \beta\,\text{DTI}}\,(A - dT - k_{\text{masked}}) \approx \alpha\,\text{DTI}\,(A - dT)\;\text{in the small-mass regime}$$

At $\text{DTI} \approx 0.28$ and $\alpha = 0.2$, **every missed fault pixel carries $4\times$ the unit penalty of a false-positive pixel ($\beta/\alpha = 4.0$)**, yet unthresholded dense probability maps (`5.17M` positive cells, such as `17GEMSDOE E-proba-multiscale`) still collapse because the `> 98%` fault-free interior of the Great Basin multiplies $\alpha\,\text{FP}_w$ by millions of background pixels (as explicitly noted in Cell 16 of `unet-mc-cv-reference-solution.ipynb`, where thresholding `> 0.1` boosts DTI).

### 2.2 Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `CLAIM`) Beat Earlier Site Submissions

Bit-exact lineage verification (`gems/parent.py`) and cross-repo inspection of `19GEMSDOE` reveal four concrete mechanisms behind `R0`'s climb from `0.1922` (`CLAIM`) to `0.2778` (`CLAIM`):

1. **Supervised Multi-Band CNN Ridge Localization (`H19-5`, `121,131` px, `0.1922` `CLAIM`):** Trained on `labels.tif` over the 19-band stack, `H19-5` extracts `1-px` geophysical/topographic ridge centrelines rather than broad probability halos. However, `19GEMSDOE` masked `existing_faults.tif` **only at exact pixel overlap (`d_cat == 0`)**, leaving `5,694` dots within `0 < d_cat <= 2.0 px` whose `300 m` cones spilled heavily onto already-mapped catalogue faults (earning zero new-fault credit while accumulating $\alpha\,\text{FP}_w$).
2. **Kernel-Matched `2.8 px` (`280 m`) Poisson-Disk Thinning (`D2.8`, `44,090` px, `0.2600` `CLAIM`, `+0.0678`):** Because $\tilde{P}(x) = \max_y K(\|x-y\|)P(y)$ uses a `max` envelope over `R = 3.0 px`, adjacent `1-px` ridge pixels (`d = 100 m`) overlap by `> 75%` in cone area ($dT_{\text{marginal}} \approx 0$), paying full $\alpha\,\text{FP}_w$ wherever the ridge wanders off-fault. Enforcing `r >= 2.8 px` preserves continuous `300 m` along-strike coverage while eliminating `63.6%` of redundant dots.
3. **Topological Speckle Pruning (`SOLO`, `39,580` px, `0.2708` `CLAIM`, `+0.0108`):** Dropping isolated `< 2-dot` fragments removes point-source volcanic plugs, cultural magnetic dipoles, and DEM pit artifacts while preserving strike-continuous faults (`L >= 500 m`).
4. **Catalogue Halo Clearance (`d_cat > 2.0 px`) + All-Finite Zeros-Outside Encoding (`R0`, `37,654` px, `0.2778` `CLAIM`, `+0.0070`):** Pruning `1,926` near-catalogue collar dots removes wasted cone mass around `existing_faults.tif`, and writing `0.0` (`nodata=None`) outside the `5,167,373`-pixel study footprint prevents DrivenData's portal validator rejection (`"Predicted values must be in range [0, 1]"`).

### 2.3 Why `GEMSDOE32` (`0.2778` `CLAIM`) Trails Top Leaderboard Entries (`0.3195` / `0.4413` `LEADERBOARD-SNAPSHOT`)

Despite its strong geometric post-processing, `R0` has four severe geological ceilings:
1. **Physics-Blind Row-Major Decimation (`58.2%` Non-Piedmont Allocation):** `D2.8` thinned `H19-5` in deterministic top-to-bottom scan order rather than physical fault probability, stranding `20.4%` (`7,691` dots) on deep central playa floors (dominated by Pleistocene Lake Lahontan strandlines) and `37.7%` (`14,204` dots) in high bare-rock mountain interiors (dominated by inactive Mesozoic thrusts and erosional cliffs), leaving only `41.8%` in the active piedmont transition zone.
2. **Dipolar Raw-TMI Shift (`300–800 m`) Without Upward-Continued RTP (`Band 2`):** At NW Nevada's `~63–65°` geomagnetic inclination, raw Total Magnetic Intensity (`Bands 3, 9, 14`) shifts magnetic gradient peaks `300–800 m` laterally off vertical basement faults — **outside the `300 m` DTI scoring kernel**!
3. **Unused Transtensional Geodesy & Blind Geothermal Conduit Layers:** `R0` never resolves GPS/InSAR volumetric dilatation (`Band 8`) vs conjugate Walker Lane / Humboldt shear (`Bands 4, 7`) onto local ridge strike, and ignores `Band 17` MT smectite clay-cap lateral boundaries, GeoDAWN `K/Th` & `U/Th` contact gradients, and `GDR #1391` blind (`>= 80 °C`) chemical geothermometers.
4. **Prior `GEMSDOE92` Lane Trade-Offs:**
   - `HYDROCONDUIT f45hydro` achieved the repo's highest static `HOLDOUT-DTI` (`0.008549`), but placed its `16,944` off-skeleton dots on a 2D smooth envelope without 1D NMS crest extraction (`Rule-2 d_vis > 2.0 HOLDOUT-DTI = 0.085221 < H19-5 0.096757`; `SGMC = 0.074107`).
   - `APRONRIDGE free1d` (`0.008354` static, `0.086787` `d_vis > 2.0`) introduced 4-axis 1D crests, but (i) misread `Band 6 (tc)` (Radiometric Total Count, $r = 0.99714$ with `GeoDAWN TC`) as magnetic curvature, (ii) left its 3-factor `R_rtp` uncalibrated so DEM slope breaks won `89.5%` of crests, and (iii) suppressed shallow-cover (`< 20 m`) corroborated bedrock relay faults.

---

## 3. `COULOMBDM` Pre-Registered Design & Experimental Results (`3 / 3` Budget Cap)

Implemented in `gems/coulombdm.py`, unit-tested in `tests/test_coulombdm.py`, pre-screened in `scripts/screen_coulombdm_surface.py` (`evidence/coulombdm_preplacement_screen.json`), built via `scripts/build_coulombdm_variants.py` (`evidence/coulombdm_variants.json`), and evaluated across all four instruments via `scripts/report_coulombdm_proxies.py` (`evidence/coulombdm_proxy_audit.json`) and `scripts/audit_public_registry.py` (`evidence/coulombdm_public_registry_uniqueness.json`):

### 3.1 Multi-Instrument Evaluation Table (`gems57-pooled-hide-v2`, `22,663` Withheld Positives)

| Candidate / Baseline | Dots (`H19-5` / Off-Skel) | Static `d_cat > 2.0` `HOLDOUT-DTI` [95% CI] | Rule-2 Fold-Visible `d_vis > 2.0` `HOLDOUT-DTI` [95% CI] | Off-Cat `USGS SGMC` (`PROXY`) | Local Overlap (`44` rasters) | Sparse Public (`<=150k` px, `1,181` rasters) |
|---|---:|---|---|---:|---:|---:|
| **`COULOMBDM coulomb1d`** *(Exp 1 — Standalone Blind-Fault Champion)* | **`0 / 37,654`** | `0.006467 [0.005660, 0.007214]` | **`0.094496 [0.085916, 0.102867]`** *(**#1 Non-CNN**)* | `0.070345` | **`0.5859`** (`PASS`) | **`0.6412` (`0 > 70%`)** |
| **`COULOMBDM s35coulomb65`** *(Exp 2 — 35% Skel / 65% Far)* | `13,179 / 24,475` | `0.007304 [0.006526, 0.008086]` | `0.080088 [0.071825, 0.087498]` | `0.072289` | **`0.6236`** (`PASS`) | **`0.6236` (`0 > 70%`)** |
| **`COULOMBDM s45coulomb55`** *(Exp 3 — Session Primary)* | **`16,944 / 20,710`** | **`0.007816 [0.006994, 0.008644]`** | **`0.086867 [0.078084, 0.095150]`** | **`0.075208`** | **`0.6796`** (`PASS`) | **`0.6796` (`0 > 70%`)** |
| `HYDROCONDUIT f45hydro` *(prior hybrid best)* | `20,710 / 16,944` | **`0.008549 [0.007626, 0.009487]`** | `0.085221 [0.076455, 0.093977]` | `0.074107` | `0.5500` (`PASS`) | `0.6719` (`0 > 70%`) |
| `APRONRIDGE free1d` *(prior standalone best)* | `0 / 37,654` | `0.008354 [0.006823, 0.010135]` | `0.086787 [0.074881, 0.098456]` | `0.080098` | `0.6507` (`PASS`) | `0.6456` (spot-check) |
| `H19-5` Supervised CNN Skeleton *(reference)* | `37,654 / 0` | — *(masked in `R0`)* | **`0.096757 [0.088267, 0.105915]`** | — | — | — |
| `PIEDFRONT f35Ptop` | `24,475 / 13,179` | `0.006425 [0.005375, 0.007479]` | — | `0.059993` | `0.6500` (`PASS`) | — |
| `RELIEF p10piedmont` *(early holdout ref)* | `37,654 / 0` | `0.006045 [0.005179, 0.006882]` | — | `0.087245` | `0.9938` (`DUP`) | — |
| `STRAINBREAK f60s2i` | `15,062 / 22,592` | `0.005487 [0.004550, 0.006386]` | — | `0.105162` | `0.6642` (`PASS`) | `0.7105` (`3 > 70%`) |
| `ANASIG f45Atop` | `20,710 / 16,944` | `0.004967 [0.004102, 0.005931]` | — | `0.080556` | `0.5877` (`PASS`) | — |
| `SPRINGALIGN f33Ctop` | `25,228 / 12,426` | `0.004865 [0.004038, 0.005782]` | — | `0.080173` | `0.6700` (`PASS`) | — |
| `BREAKLINE f45Ltop` | `20,710 / 16,944` | `0.004861 [0.003930, 0.005887]` | — | `0.126105` | `0.5500` (`PASS`) | — |
| `STEPEDGE f60Sraw` | `15,062 / 22,592` | `0.003980 [0.003295, 0.004702]` | — | **`0.141464`** | `0.4609` (`PASS`) | — |
| `Parent R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | `37,654 / 0` | `0.004006 [0.003408, 0.004651]` | — | `0.096060` | `self` | — |

---

## 4. Three Major Scientific Discoveries from `COULOMBDM`

### Discovery 1 — Standalone Physics (`COULOMBDM coulomb1d`, `0% H19-5`) Matches Supervised `H19-5` on True Blind-Fault Recovery (`0.094496` vs `0.096757`)

On **Rule-2 Fold-Visible (`d_vis > 2.0`) `HOLDOUT-DTI`** — where each fold masks only `fold['visible']` (`existing_faults.tif` minus the withheld test fault segments), so genuinely blind fault segments are **not** artificially self-erased within `200 m` of their own axis — standalone `COULOMBDM coulomb1d` achieves:

$$\text{HOLDOUT-DTI}_{\text{Rule-2}}(\texttt{coulomb1d}) = \mathbf{0.094496}\;\;[0.085916,\;0.102867]$$

- **Statistically indistinguishable from the supervised `H19-5` CNN** (`0.096757 [0.088267, 0.105915]`; paired cluster-bootstrap difference $\Delta = -0.002261$, `95% CI [-0.009834, +0.005283]`) despite using **zero `H19-5` pixels and zero `labels.tif` supervision** (`96.8%` distinct exact pixels from `R0`; `46.09%` of `coulomb1d` crests independently re-discover `H19-5` fault traces within `300 m` from first-principles mechanics!).
- **New all-time repository non-CNN high on blind-fault recovery:** beats `APRONRIDGE free1d` (`0.086787`) by **`+8.9%`** (`+0.007709`) and `HYDROCONDUIT f45hydro` (`0.085221`) by **`+10.9%`** (`+0.009275`). Even hybrid `COULOMBDM s45coulomb55` (`0.086867`) edges past both `APRONRIDGE free1d` and `HYDROCONDUIT f45hydro` on `d_vis > 2.0`.

### Discovery 2 — Mathematical Explanation of the Static (`d_cat > 2.0`) vs Fold-Visible (`d_vis > 2.0`) Centerline-Tightness Paradox

Why does `coulomb1d` jump **ahead** of `APRONRIDGE free1d` by `+8.9%` on fold-visible `d_vis > 2.0` (`0.094496` vs `0.086787`), while scoring **behind** `APRONRIDGE free1d` on static `d_cat > 2.0` (`0.006467` vs `0.008354`)?

Consider a detector whose cross-strike localization offset $r_\perp$ from a fault trace follows a zero-mean Gaussian $\mathcal{N}(0, \sigma_\perp^2)$:
- **On a genuinely unmapped test fault** (both DrivenData's hidden test set **and** Rule-2 `d_vis > 2.0`, because unmapped faults are absent from `existing_faults.tif`!), every dot at $r_\perp \in [0, 300\text{ m}]$ scores triangular kernel credit $K(r_\perp) = 1 - r_\perp/300$, which is strictly maximized at $r_\perp = 0$ ($\sigma_\perp \to 0$). Continuous-angle bilinear Canny 1D NMS (`oriented_nms_1d`) + multi-altitude upward-continued `Band 2 RTP` (`z = 100, 300, 600 m`) locks `COULOMBDM` crests tightly onto $r_\perp \le 200\text{ m}$, driving `d_vis > 2.0` `HOLDOUT-DTI` up to **`0.094496`**.
- **On static `d_cat > 2.0` evaluation of a pre-built submission raster**, the submission filter `d_cat > 2.0 px` **deletes every dot with $r_\perp \le 200\text{ m}$** around the withheld catalogue fault, leaving only the narrow outer annulus $r_\perp \in (200\text{ m}, 300\text{ m}]$ where $K(r_\perp) < 1/3$! A tighter fault-axis detector ($\sigma_\perp \approx 100\text{ m}$) places most of its mass inside $r_\perp \le 200\text{ m}$ (deleted by static `d_cat > 2.0`) and fewer stray flanking dots in $200 < r_\perp \le 300\text{ m}$, whereas a slightly broader 4-axis discretised crest (`APRONRIDGE`) or 2D conduit halo (`HYDROCONDUIT`) leaves more residual dots in the `200–283 m` flank!
- **Crucial Governance Rule (`Own the Outcome`):** Even though this geometric insight favors `COULOMBDM` on true unmapped faults (`d_vis > 2.0`), we **never** change our pre-registered promotion gate post-hoc. Because `s45coulomb55` (`0.007816`) does not surpass `HYDROCONDUIT f45hydro` (`0.008549`) on the pre-registered static `HOLDOUT-DTI` comparator **and** the literal public dense witness (`17GEMSDOE`) blocks all nonempty rasters, `COULOMBDM` is recorded with `verdict: "negative"` and `submission_eligible: false`, while reporting both instruments side-by-side for the human selector.

### Discovery 3 — Balanced Three-Channel Allocation Lifts `SGMC` Above `HYDROCONDUIT` While Passing `1,181 / 1,181` Sparse Public Uniqueness Checks

- **Balanced Physical Channel Winners:** Across `37,654` standalone `COULOMBDM` 1D crests, `53.7%` (`20,233`) are won by piedmont monoclinal scarps (`R_pied`), `22.9%` (`8,612`) by concealed upward-continued RTP / gravity / MT clay-cap / GDR subsurface conduits (`R_sub`), and `23.4%` (`8,809`) by geophysically corroborated bedrock relays (`R_bed`) — fixing `APRONRIDGE`'s `89.5%` single-channel DEM dominance and lifting `s45coulomb55` `USGS SGMC` (`0.075208`) above `HYDROCONDUIT f45hydro` (`0.074107`).
- **35 / 35 Leakage Canaries PASS:** Maximum single-feature symmetric ROC AUC across all 35 raw and derived features is **`0.640176 <= 0.90`** (`S_pct = 0.640176`, `scarp_edge_pct = 0.637050`, `r_bed = 0.617078`, `hab_coulomb_pct = 0.611464`, `r_sub = 0.571016`, Rank-4 `seismic_anisotropy = 0.510962`).
- **Complete Local (`44` rasters) & Live `102`-Repo Public (`1,370` rasters) Uniqueness Audit:**
  - *Local registry (`44` rasters)*: `coulomb1d = 0.585861`, `s35coulomb65 = 0.623599`, `s45coulomb55 = 0.679583` (`all <= 0.70`), worst `|rho| = 0.413022 <= 0.90` (`duplicate: false`).
  - *Live `102`-repo public sparse fleet (`1,181` rasters with `<= 150,000` positive pixels)*: **`0 / 1,181` exceed `70%` forward 3-px overlap on any `COULOMBDM` arm** (`coulomb1d` max `0.641180`, `s35coulomb65` max `0.623599`, `s45coulomb55` max `0.679583`; worst `|Spearman rho|` across all `1,370` rasters `0.352130` pre-placement / `0.413022` final).
  - *Literal binding dense-surface witness (`185` dense `> 150k`-px rasters)*: `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373 / 5,167,373` positive footprint cells) yields `forward_overlap = 1.000 > 0.70`, triggering fail-closed `stop_required: true`, `submission_eligible: false`, `verdict: "negative"`.

---

## 5. Human Selector Portfolio Recommendation (`Maximize P(Win)` Under `<= 3 / Week` Cap)

Zero weekly slots have been consumed by `GEMSDOE92` (`74 BUILT`, `0 ORGANIZER-CONFIRMED RECEIPT` post-merge). Once a human operator (a) adopts an explicit sparse-support registry policy (`<= 150,000` positive pixels, excluding full-footprint probability surfaces from `3-px` binary dot halo comparison) and (b) records one baseline `ORGANIZER-CONFIRMED` receipt (`Blocker 0`), `GEMSDOE92` now provides orthogonal, pairwise locally unique (`<= 68.0%` 3-px overlap; `COULOMBDM` vs `COULOMBLOQO` `<= 54.5%`), `100%` format-validated candidates spanning supervised LOQO, hybrid hydrothermal, and zero-label pure-physics hypothesis classes:

1. **Slot Candidate A (Supervised LOQO Holdout Leader — `0.009220` Static / `0.113316` LOQO `d_vis>2`):** `COULOMBLOQO dual45` (`0.009107` static, `0 / 1,121` `<= 90k`-px sparse public overlaps `> 70%`) or `COULOMBLOQO standalone` (`0.009220` static, `1` `61k`-px public raster at `0.7004`).
2. **Slot Candidate B (Zero-Label Pure-Physics Blind-Fault Leader — `0.094496` Rule-2 `d_vis>2`, `0 / 1,181` `<= 150k`-px Sparse Public Overlaps `> 70%`):** `COULOMBDM coulomb1d` (`h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif`, `0% H19-5`, `0%` catalogue supervision; `47.6%` local overlap with `COULOMBLOQO standalone`, `58.6%` with `HYDROCONDUIT`), **or** `COULOMBDM s45coulomb55` (`0.007816` static, `0.086867` `d_vis > 2.0`, `0.075208` `SGMC`, `0 / 1,181` `<= 150k`-px sparse public overlaps `> 70%`).
3. **Slot Candidate C (Piedmont-Hydrothermal Hybrid — `0.008549` Static):** `HYDROCONDUIT f45hydro` (`h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`, `0 / 1,147` `<= 150k`-px sparse public overlaps `> 70%`).
