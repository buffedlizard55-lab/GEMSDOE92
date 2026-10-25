# GEMSDOE92 — DOE GEMS Prize #306 Auditable Submission Workbench

**Read first:** the block immediately below is the newest session's automated decision (rendered from its run card). Older banners further down are historical lane closeouts kept for audit. Two questions are answered for every served file, by the project, with no human inspector: **(1) OK to download?** (format gates) **(2) OK to submit?** (pre-registered holdout gate + dual-reading uniqueness).

<!-- BLINDFAULT:BEGIN (rendered by scripts/render_blindfault_site.py from evidence/blindfault_run_card.json) -->
> ### Session 2026-10-25 — lane `BLINDFAULT` (new unique TIFF generated; verdict **`negative`**)
> **✅ OK TO DOWNLOAD** (format-valid, unique) · **⛔ DO NOT SUBMIT — verdict `negative` (automated gate: primary HOLDOUT-DTI 0.047896 < holdout-best 0.113316)** · weekly slots used: **0** · experiments: **3/3**
>
> - **Download:** [`gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif`](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.zip) · [audit JSON](docs/downloads/gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-audit.json) · [run card](docs/downloads/blindfault_run_card.json) · [analysis](docs/ANALYSIS_20261025_BLINDFAULT.md) · [pre-registered hypotheses](docs/HYPOTHESES_20261025_BLINDFAULT.md)
> - **SHA-256:** `c91170e5d4ffc67a18378aa9f479b8786ff6e92970e12e6646de14dbc6c5cf3d` · ZIP `5a01bcb7d7066982349d9f9357a4e7172c20e588364ac82b306aac4258a32181`
> - **Validator (automated, no human step):** single band `float32`, `EPSG:32611`, `3730 × 3292`, finite values in `[0, 1]`, `0.0` outside footprint, 37,654 unit dots, 0 catalogue mass — written and re-read through `gems57.submission_writer` / `gems57.validate`.
> - **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, strict draw-blind LOQO, `d_visible > 2.0`): `blindtopo` **0.047896 [0.038079, 0.057970]**; `blind` (hypothesis arm) 0.037842 [0.029376, 0.047036]; `blindflat` 0.047475 [0.035767, 0.059748]; `H19-5` reference 0.096757 [0.084640, 0.108096]; repository holdout-best `COULOMBLOQO standalone` 0.113316. Low-conspicuity tercile (mechanism instrument, 6,065 positives): `blind` 0.011041 [0.004739, 0.018804] vs `H19-5` 0.007166 [0.004529, 0.010079].
> - **Leakage canaries:** max symmetric AUC 0.5728 (all ≤ 0.90).
> - **Uniqueness (REGISTRY-MEASUREMENT, dual reading — `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`):** local registry (91 rasters): matched-budget worst overlap 0.4014 (`local:docs/downloads/h33-h33-2-b2-COULOMBLOQOdual45-20261024-dd91d98c-zeros.tif`), literal worst 0.4014, worst |ρ| 0.0923; public registry (1386 Git-blob-verified rasters, 102 repos, complete=True): matched-budget worst overlap 0.5219 (`12GEMSDOE/docs/downloads/12GEMSDOE_r6-nms3-h28-texture_8721329b55c7.tif`), literal worst 1.0000, worst |ρ| 0.3402. Overlap with parent `R0`: 0.2613. Specificity proof: the organizer-scored parent `R0` itself has literal overlap 1.000 / matched-budget 0.037 against the dense witness.
> - **Submission name:** `GEMSDOE92-BLINDFAULT-blindtopo-20261025` · **Note (86/140):** `BLINDFAULT blindtopo: 37654 LOQO dots, slope-blind cov-shift wts; HOLDOUT-DTI 0.047896`
> - Sibling arms (also format-valid, research only): `gemsdoe92-blindfault-blind-37654-20261025-d4f09813-zeros.tif` (`b2cd485934adfa9a…`), `gemsdoe92-blindfault-blindflat-37654-20261025-1e27ea5c-zeros.tif` (`3ccf1d798a7a3e18…`).
<!-- BLINDFAULT:END -->

**Latest session review:** [Three-pass findings and ranked conditional hypotheses](docs/REVIEW_918B947A.md) · [fresh run card](docs/downloads/review_918b947a_run_card.json). Subsequent `COULOMBDM` (and parallel `XPHASE`) work generated unique research TIFFs that are **OK TO DOWNLOAD** and **DO NOT SUBMIT**. The literal overlap rule remains unsatisfiable for weekly-slot clearance because a pinned registry raster covers the entire footprint. The operational user brief is retained below and in `SESSION_PROMPT.md`; read both at session start. Maximize P(Win) and Own the Outcome mean preserving negative evidence, not fabricating submission clearance.

> ### Parallel lane closeout — `EULERFUSE gravity`: ✅ OK TO DOWNLOAD FOR RESEARCH; ⛔ DO NOT SUBMIT
> [Exact GeoTIFF](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif) · [one-TIFF ZIP](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.zip) · [audit](docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros-audit.json) · [run card](docs/downloads/eulerfuse_run_card.json) · [public scan](docs/downloads/eulerfuse_public_registry.json) · [analysis](docs/ANALYSIS_20261024_EULERFUSE.md). Exact TIF SHA-256: `5820e882512843a334f4497ed7f294af937339f729e4eeeecdc33d9cdafeeab9`; no exact SHA match in the pre-publication scan of `1,378` exact-grid rasters; `11/11` format gates PASS with all values finite in `[0,1]`. Strict draw-blind **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, `22,663` withheld positives) is `0.110387 [0.097279, 0.123179]`, below fresh control `0.113316 [0.101071, 0.126266]`; paired delta `-0.002929 [-0.006700, 0.000763]`. Literal public overlap is `1.000 > 0.70`. Name: `GEMSDOE92-EULERFUSE-gravity-20261024`; 80/140-character record-only note: `EULERFUSE gravity: 37654 LOQO Euler-contact dots; HOLDOUT-DTI 0.110387; negative`. Verdict `negative`; `submission_eligible: false`; 3/3 experiments and 0 weekly slots.

> ### ✅ DOWNLOAD STATUS: **FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH**
> ### ⛔ SUBMISSION / WEEKLY SLOT STATUS: **DO NOT SUBMIT — NOT CLEARED (`verdict: "negative"`, `submission_eligible: false`; literal public dense-witness stop)**
>
> Read this README, [`SESSION_PROMPT.md`](SESSION_PROMPT.md), and [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md) at every session start.
>
> - **Current research download:** [`docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif`](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif) · [One-TIFF ZIP](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.zip) · [Audit JSON](docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-audit.json) (`11 / 11` format MUST gates PASS; `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0.0` outside footprint, `0` NaNs anywhere, `37,654` unit-mass dots, `0` catalogue mass).
> - **SHA-256 (`-zeros.tif`):** `44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12` (ZIP: `2d1c23a2ce4b2396c30eebdea86981785b3a24356a77dcd0195ebae0b5a8e754`)
> - **Suggested Submission Name (research record only — DO NOT UPLOAD YET):** `GEMSDOE92-COULOMBDM-s45coulomb55-20261024`
> - **Suggested Submission Note (`112 / 140` chars):** `h33-h33-2-b2; COULOMBDM s45coulomb55: 16944 Coulomb-H19 + 20710 off-skel 1D Coulomb/RTP/clay ridges (>3px H19-5)`
> - **Measured `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** Static `d_cat > 2.0` **`0.007816 [0.006994, 0.008644]`** (`+95.1%` vs `R0` `0.004006`; `+29.3%` vs `RELIEF p10` `0.006045`); zero-label standalone sibling [`coulomb1d`](docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif) (`0% H19-5`, `0%` catalogue supervision) achieves Rule-2 fold-visible `d_vis > 2.0` **`0.094496 [0.085916, 0.102867]`** (matching supervised `H19-5` `0.096757` within 95% CI). Static holdout is below supervised LOQO repository holdout-best `COULOMB-LOQO standalone` `0.009220`. Local `HOLDOUT-DTI` is **not** an `ORGANIZER-CONFIRMED` competition score.
> - **Uniqueness & Stop Gate:** Locally unique against all 58 repository rasters (`worst 3-px overlap = 0.679583 <= 0.70`, `|ρ| = 0.4130 <= 0.90`; vs `COULOMBLOQO` `<= 0.5448`, vs `XPHASE` `<= 0.2979`) and **`0 / 1,181` sparse (`<= 150k` px) public rasters exceed `70%`** across 102 `GEMSDOE` repos ([102-repo scan](docs/downloads/coulombdm_public_registry_uniqueness.json)). Blocked by the literal public dense witness `17GEMSDOE E-proba-multiscale` (`5,167,373` positive footprint cells → `1.000` forward overlap; [witness](docs/downloads/public_witness_s45coulomb55.json) · [Run Card](docs/downloads/coulombdm_run_card.json)). **0 weekly slots spent (`74 BUILT / 0 RECEIPT`).**
> - **Lane:** `COULOMBDM` = zero-label 2D Mohr–Coulomb dilatant shear (`Bands 4, 7, 8`) × 2D FFT upward-continued `Band 2 RTP` (`100/300/600 m`) + `Band 17` MT clay-cap edges + lateral `GeoDAWN K/Th, U/Th` contact gradients + `>= 80 °C` blind `GDR #1391` geothermometers along Canny cross-strike 1D NMS centrelines. Siblings: [coulomb1d](docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif) (`0.094496` Rule-2 / `0.006467` static), [s35coulomb65](docs/downloads/h33-h33-2-b2-COULOMBDMs35coulomb65-20261024-1091c5a7-zeros.tif) (`0.007304` static).
> - **Workbench & Analysis:** [Main Workbench](docs/index.html) · [Executive Summary](docs/executive-summary.html) · [Submission Guide](docs/SUBMIT.html) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261024_COULOMBDM.md) · [PhD Analysis](docs/ANALYSIS_20261024_COULOMBDM.md)
> - **Parallel three-pass repository review (2026-10-24):** [Findings, ranked future hypotheses, verified checks and limitations](docs/REVIEW_20261024_ARENA.md) · [JSON run card](evidence/arena_review_run_card_20261024.json). The literal public-registry duplicate stop remains binding for weekly slots.

## Prior/parallel candidate summary & full technical reference

Among earlier historical baselines, repository holdout-best remains `COULOMBLOQO standalone` (`h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`, `0.009220 [0.007983, 0.010493]`). `APRONRIDGE free1d` (`h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`) recorded `0.008354 [0.006823, 0.010135]` while the higher documented HYDROCONDUIT hybrid is `HYDROCONDUIT f45hydro` (`h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`) at `0.008549 [0.007626, 0.009487]`; merged parallel lanes recorded `COULOMBDM s45coulomb55` (`0.007816 [0.006994, 0.008644]` static; zero-label `coulomb1d` `0.094496` Rule-2 `d_vis > 2.0`), `GEOTENSION free1d` (`0.007615 [0.005832, 0.009386]`), `PIEDFRONT f35Ptop` (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`, `0.006425`), `COULOMB seismo` (`0.005808 [0.004846, 0.006809]`), `XPHASE dual40` (`h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif`, `0.004653 [0.003955, 0.005390]`), `EULERFUSE gravity` (strict draw-blind `0.110387 [0.097279, 0.123179]`, below its fresh `0.113316` control), `BASEMENTEDGE step3` (`0.000000`), and `MICROSWARM short` (`0.000000`) — all `verdict: "negative"`, `submission_eligible: false`.

---

## PhD Answer: Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Beat Every Listed `GEMSDOE` Site & How to Beat It

Full mathematical derivation: [`docs/ANALYSIS_20261024_COULOMBLOQO.md`](docs/ANALYSIS_20261024_COULOMBLOQO.md).

1. **Exact DTI Metric Geometry (`#IR-92-ALPHA-BETA-PROSE-SWAP` Corrected):**
   - The [official reference notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) (Cell 16) confirms the **training-loss** weights only. It does not implement distance-weighted evaluation. The following DTI equation is implemented by the shared local [`vendor/gems57/metric.py`](vendor/gems57/metric.py), not independently certified from the live organizer problem page in this review:
     $$\mathrm{DTI}(A, G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w}, \qquad K(r) = \max\!\left(0,\, 1 - \frac{r}{300\,\mathrm{m}}\right), \qquad \Omega_{\text{eval}} = \Omega \setminus C.$$
   - Contrary to inverted prose in earlier session docs, **false negatives carry $4\times$ the denominator weight of false positives ($\beta = 0.8$ vs $\alpha = 0.2$)**. The triangular-kernel coverage uses a **pointwise maximum**, so overlapping predictions can be redundant. However, separation below `2.8 px` does **not** imply zero marginal truth credit or a full per-dot false-positive penalty; each depends on the actual truth geometry. Thinning is a plausible mechanism for the reported improvement, not a universally optimal spacing theorem.
2. **Exact Zero-XOR Byte-Verified Ancestor Cascade of `GEMSDOE32` (`R0`):**
   - `H19-5` (`19GEMSDOE`, `121,131` px, `0.1922` `[CLAIM]`) $\to$ `D2.8` (`GEMSDOE25`, `44,090` px Poisson-thinned at `2.83 px ≈ 300 m`, `0.2600` `[CLAIM]`) $\to$ `SOLO` (`GEMSDOE28`, `40,199` px with **`XOR(SOLO, D2.8 & d_cat > 1.0) == 0`**, `-3,891` px at `d_cat == 1.0`, `0.2708` `[CLAIM]`; `#IR-92-SOLO-R1-BYTE-IDENTITY`) $\to$ **`R0` / `GEMSDOE32 h33-2-b2`** (`37,654` px with **`XOR(R0, D2.8 & d_cat > 2.0) == 0`**, `-2,545` px at `1.0 < d_cat <= 2.0`, retaining `2,171` splay/tip dots at `2.0 < d_cat <= 3.0`, `0.2778` `[CLAIM]`).
3. **Why `R0` Has Headroom (`0.3195` / `0.4413` Leaderboard `[CLAIM]`) & How `COULOMB-LOQO` Breaks Through:**
   - `R0` is 100% confined to `H19-5` and thinned in physics-blind row-major scan order (`0.004006` static `HOLDOUT-DTI`). Earlier `GEMSDOE92` un-normalized terrain lanes (`BREAKLINE` `0.004861`, `STEPEDGE` `0.003980`) were hijacked `74.8%` by bare mountain-core cliffs, while rigid piedmont elevation boxcars (`APRONRIDGE` `0.008354`, `HYDROCONDUIT` `0.008549`) starved active bedrock horst faults (causing `HYDROCONDUIT` to lose to `H19-5` on unmasked `d_visible > 2.0` holdout, `0.0852` vs `0.0968`, and lose `22.9%` on `SGMC`).
   - **`COULOMB-LOQO`** trains regularized 4-quadrant Leave-One-Quadrant-Out (`>= 1.2 km` guard band, `> 500 m` negative buffer) boosted trees on **24 strictly catalogue-free physical features** (`gems/coulomb_loqo.py`): multi-scale Hessian scarp ridges, 600 m step monotonicity, signed `Band 18` E–W gravity-gradient footwall polarity concordance ($r = +0.6260$ with $\partial_x\text{Band 13}$), true `Band 2 RTP` tilt/demag/Hessian (replacing mislabeled `Band 6 tc` = Radiometric Total Count), circular cross-physics axial strike phase-locking, N15°E/conjugate 2D Coulomb dilation & slip tendency, MT clay-cap margins, `GeoDAWN K/Th, U/Th`, and `419` blind `>= 80 °C` silica/cation geothermometer cells (`dist_known_fault_px` explicitly dropped).

---

## Multi-Instrument Benchmark Table (All Evidence Labels Explicit; Zero Projections as Scores)

| Candidate / Baseline | Dots (`H19` %) | Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` pos, 95% CI) | Rule-2 `d_vis > 2.0` `HOLDOUT-DTI` | `SGMC` `PROXY` (`62,703` px) | Local Overlap (`<=0.70`) | Sparse Public `<=90k` (`1,121` rasters) | Literal Public (`1,368` rasters) |
|---|---:|---|---|---|---|---|---|
| **`COULOMBLOQO standalone` (Exp 1 — Primary)** | `37,654` (`0%`) | **`0.009220 [0.007983, 0.010493]`** | **`0.113316 [0.100614, 0.127163]`** | **`0.090569`** | **`0.6164` (PASS)** | `0.7004` (`1 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO nocoulomb` (Exp 2 — Ablation)** | `37,654` (`0%`) | **`0.009151 [0.007944, 0.010389]`** | — | `0.091251` | **`0.6640` (PASS)** | `0.7396` (`5 > 70%`) | `1.0000` (dense STOP) |
| **`COULOMBLOQO dual45` (Exp 3 — Hybrid)** | `37,654` (`45%`) | **`0.009107 [0.007977, 0.010325]`** | **`0.101998 [0.090846, 0.112907]`** | **`0.094057`** | **`0.5982` (PASS)** | **`0.6488` (`0 > 70%`)** | `1.0000` (dense STOP) |
| `HYDROCONDUIT f45hydro` | `37,654` (`55%`) | `0.008549 [0.007461, 0.009684]` | `0.085221` | `0.074107` | `0.5500` (PASS) | `0.6518` (`0 > 70%`) | `1.0000` (dense STOP) |
| `APRONRIDGE free1d` | `37,654` (`0%`) | `0.008354 [0.006823, 0.010135]` | `0.086787` | `0.080098` | `0.6507` (PASS) | — | `1.0000` (dense STOP) |
| **`COULOMBDM s45coulomb55` (Current Research Download)** | `37,654` (`45%`) | **`0.007816 [0.006994, 0.008644]`** | **`0.086867`** | **`0.075208`** | **`0.6796` (PASS)** | **`0.6796` (`0 / 1,181 <=150k > 70%`)** | `1.0000` (dense STOP) |
| **`COULOMBDM coulomb1d` (Zero-Label Blind-Fault)** | `37,654` (`0%`) | `0.006467 [0.005660, 0.007214]` | **`0.094496 [0.085916, 0.102867]`** | `0.070345` | **`0.5859` (PASS)** | **`0.5859` (`0 / 1,181 <=150k > 70%`)** | `1.0000` (dense STOP) |
| `GEMSDOE92-PIEDFRONT-f35Ptop-20261024` (`h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`) | `37,654` (`65%`) | `0.006425 [0.005375, 0.007479]` | — | `0.059993` | `0.6500` (PASS) | — | `1.0000` (dense STOP) |
| `RELIEF p10piedmont` (`R0`-duplicate ref) | `37,654` (`100%`) | `0.006045 [0.005179, 0.006882]` | — | `0.087245` | `0.9938` (DUP) | — | `1.0000` (DUP) |
| `STRAINBREAK f60s2i` | `37,654` (`40%`) | `0.005487 [0.004550, 0.006386]` | — | `0.105162` | `0.4150` (PASS) | `0.6844` (`0 > 70%`) | `1.0000` (dense STOP) |
| `ANASIG f45Atop` / `SPRINGALIGN f33Ctop` / `BREAKLINE f45Ltop` | `37,654` | `0.004967` / `0.004865` / `0.004861` | — | `0.0806` / `0.0802` / `0.1261` | `0.55–0.67` | — | `1.0000` (dense STOP) |
| `STEPEDGE f60Sraw` | `37,654` (`40%`) | `0.003980 [0.003295, 0.004702]` | — | `0.141464` | `0.4610` (PASS) | — | `1.0000` (dense STOP) |
| `R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | `37,654` (`100%`) | `0.004006 [0.003408, 0.004651]` | `0.096757` (`H19`) | `0.096060` | self | — | — |

---

## Audited 19-Band `training_features.tif` Stack (`EPSG:32611`, `3730 × 3292`, `5,167,373` Footprint Cells, `60,988` `existing_faults` Pixels)

| Band | GDAL Description & Verified Physical Identity | Sign | Valid Footprint Px | `q05` | Median (`q50`) | `q95` | Role in `COULOMB-LOQO` |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `mag_anom` — Magnetic anomaly | Signed | `5,164,312` | `-204.37` | `-57.69` | `162.74` | Superseded by inclination-corrected Band 2 `rtp` |
| **2** | **`rtp` — Reduced-to-Pole magnetic anomaly** | **Signed** | `5,164,312` | `-332.48` | `-137.22` | `153.75` | **Group C: RTP tilt edge, positive-Laplacian demag trough, Hessian ridge, axial strike** |
| 3 | `tmi_hg` — TMI horizontal gradient | Non-neg | `5,164,312` | `1.64` | `13.16` | `93.85` | Archived in `ANASIG` |
| **4** | **`geod_2ndinv` — Geodetic strain-rate 2nd invariant** | **Non-neg** | `5,164,312` | `2.50` | `19.91` | `46.20` | **Group D: Strain magnitude (`f19`)** |
| **5** | **`iso_grav_anom_slope` — Isostatic gravity slope** | **Non-neg** | `5,164,312` | `0.029` | `0.102` | `0.270` | **Group B: AGC-equalized gravity tilt (`f12`)** |
| 6 | `tc` — **Verified Radiometric Total Count** (`r = 0.99714` w/ `GeoDAWN` Band 4; mislabeled as magnetic tilt in header, `#IR-92-BAND6-TC-MISLABEL`) | Non-neg | `5,164,300` | `11.81` | `18.48` | `25.58` | Replaced by clean `GeoDAWN` `K, Th, U` ratios (`f22, f23`) |
| **7** | **`geod_shearrate` — Geodetic shear strain rate** | **Non-neg** | `5,164,312` | `0.00` | `9.70` | `29.14` | **Group D: 2D Coulomb slip tendency (`f18`)** |
| **8** | **`geod_dilaterate` — Geodetic volumetric dilatation rate** | **Signed** | `5,164,312` | `-2.85` | `5.50` | `19.20` | **Group D: N15°E Coulomb dilation tendency (`f17`, AUC `0.5574`)** |
| 9 | `tmi_vg` — TMI vertical gradient | Signed | `5,164,312` | `-0.285` | `-0.009` | `0.319` | Archived in `ANASIG` |
| 10 | `deq_n100a15` — Distance to earthquake | Non-neg | `5,164,312` | `180.80` | `622.80` | `8631.38` | Screened negative (`100 km` smoothing) |
| **11** | **`iso_grav_anom_vg` — Isostatic gravity vertical gradient** | **Signed** | `5,164,312` | `-2.70` | `-0.072` | `2.61` | **Group B: Gravity tilt denominator (`f12`)** |
| **12** | **`det_elev` — Detrended elevation (`3DEP`)** | **Signed** | `5,164,312` | `-330.67` | `-75.58` | `450.24` | **Groups A–C: Step monotonicity, coherence, footwall polarity** |
| **13** | **`iso_grav_anom` — Isostatic gravity anomaly** | **Signed** | `5,164,312` | `-26.09` | `-7.26` | `7.74` | **Groups B–C: Footwall dip concordance (`f09`) & axial strike** |
| 14 | `tmi` — Total magnetic intensity | Signed | `5,164,312` | `-298.64` | `-124.82` | `140.08` | Superseded by Band 2 `rtp` |
| **15** | **`depth_to_base_surf` — Depth to basement / cover thickness (m)** | **Signed** | `5,164,312` | `6.21` | `316.37` | `1881.26` | **Groups A–B: Cover thickness, basement gradient & concordance** |
| 16 | `ieq_n100a15` — Earthquake intensity/density | Non-neg | `5,164,312` | `312.50` | `755.70` | `2723.60` | Screened negative (`100 km` smoothing) |
| **17** | **`cond_surf` — Subsurface MT electrical conductivity** | **Non-neg** | `5,164,312` | `1.84` | `2.89` | `3.91` | **Group E: Smectite clay-cap margin gradient (`f20`) & level (`f21`)** |
| **18** | **`iso_grav_anom_hg` — Signed E–W horizontal gravity derivative** ($r = +0.6260$ w/ $\partial_x\text{B13}$) | **Signed** | `5,164,312` | `-3.40` | `0.038` | `3.30` | **Group B: E–W normal-fault footwall polarity lock (`f11`, AUC `0.5596`)** |
| **19** | **`det_elev_slope` — Detrended elevation slope (`3DEP`)** | **Non-neg** | `5,164,312` | `0.168` | `3.749` | `25.337` | **Group A: Relative log-slope break (`f01`, AUC `0.6039`) & Hessian ridges** |

---

## Reproducible Pipeline (Zero Manual Steps)

`BLINDFAULT` (2026-10-25; 2 CPUs / 3 GB is enough):

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy rasterio pandas pytest "scikit-learn>=1.5,<2.0"
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py   # SHA-256-pinned inputs → .cache/gems_inputs/
PYTHONPATH=vendor .venv/bin/python scripts/run_blindfault.py        # features, canaries, 3 LOQO arms, HOLDOUT-DTI, dots → evidence/blindfault_holdout.json
PYTHONPATH=vendor .venv/bin/python scripts/finalize_blindfault.py   # submission_writer TIFFs, local + cached public dual-reading uniqueness, run card
.venv/bin/python scripts/render_blindfault_site.py                  # README/site status blocks rendered from the run card
PYTHON=.venv/bin/python make test && PYTHON=.venv/bin/python make site && PYTHON=.venv/bin/python make verify && PYTHON=.venv/bin/python make ledger
```


`EULERFUSE` closeout (use a clean/scratch checkout because the builder refuses to overwrite pinned bytes):

```bash
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py
PYTHONPATH=vendor .venv/bin/python scripts/screen_eulerfuse.py
PYTHONPATH=vendor .venv/bin/python scripts/evaluate_eulerfuse.py
PYTHONPATH=vendor .venv/bin/python scripts/build_eulerfuse_submission.py
PYTHONPATH=vendor .venv/bin/python scripts/audit_public_registry.py \
  --candidate docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif \
  --surface .cache/eulerfuse_surfaces/EULERFUSE-gravity-surface-20261024.tif \
  --output evidence/eulerfuse_public_registry.json
PYTHONPATH=vendor .venv/bin/python scripts/finalize_eulerfuse.py
```

The finalizer validates source-receipt agreement and writes the negative run card without human input. The stored registry scan predates publication of these bytes; a later self-match must not be misrepresented as evidence that the file copied a prior submission.

Current/prior holdout-best pipeline:

```bash
# 1. Restore & SHA-256-verify all 12 competition/external inputs into gitignored .cache/gems_inputs/
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py

# 2. Screen all 43 single-feature/LOQO leakage canaries (<=0.90) & pre-placement local uniqueness
.venv/bin/python scripts/screen_coulomb_loqo.py

# 3. Build & 10/10 gate-check the 3 pre-registered COULOMB-LOQO variants via submission_writer.py
.venv/bin/python scripts/build_coulomb_loqo_variants.py

# 4. Run multi-instrument HOLDOUT-DTI (static + strict Rule-2 d_vis>2.0), SGMC PROXY, & local registry audit
.venv/bin/python scripts/report_coulomb_loqo_proxies.py

# 5. Run live 102-repo Git-blob-verified public registry scan & assemble Protocol Rule 5 Run Card
.venv/bin/python scripts/audit_public_registry.py \
  --candidate docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif \
  --surface .cache/gems_inputs/coulomb_loqo_S_full_surface.tif \
  --out-name coulomb_loqo_public_registry_uniqueness
.venv/bin/python scripts/finalize_coulomb_loqo_run_card.py

# 6. Run full automated unit tests, submission validator, site contract, manifest & ledger gates
PYTHON=.venv/bin/python make test && PYTHON=.venv/bin/python make site && PYTHON=.venv/bin/python make verify && PYTHON=.venv/bin/python make ledger
```

---

## Arena Core Values

- **Maximize P(Win):** Every hypothesis is pre-registered from Basin-and-Range structural & geothermal physics (`docs/HYPOTHESES_20261024_COULOMBLOQO.md`), tested against single-feature leakage canaries (`<= 0.90`), validated on whole-segment spatial holdouts (`gems57-pooled-hide-v2` static AND strict draw-blind `d_visible > 2.0`) plus independent `USGS SGMC` bedrock controls, and scanned across 1,368 public rasters so scarce weekly competition slots (`<= 3 / week`) are never wasted on duplicates or unvalidated heuristics.
- **Own the Outcome:** We own verification end to end — catching and fixing inverted $\alpha/\beta$ Tversky formulas (`#IR-92-ALPHA-BETA-PROSE-SWAP`), `SOLO` byte-identity errors (`#IR-92-SOLO-R1-BYTE-IDENTITY`), spatial-block bootstrap `extend` bugs (`#IR-92-HYDROCONDUIT-EXTEND-TERMS`), `Band 6 tc` header mislabeling (`#IR-92-BAND6-TC-MISLABEL`), and HTML merge seams (`#IR-92-PR49-MERGE-SEAMS`), while validating every served `[0, 1]` GeoTIFF automatically without human inspection.

---

## Trusted Official Sources

- [DrivenData Competition #306 Problem & Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [About](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) · [Data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official Competition Rules PDF (NREL/TP-5700-96647)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData Official Reference Solution (`drivendataorg/gems-prize-reference-solution`)](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN Airborne Magnetic & Radiometric Surveys](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [USGS Data Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository (GDR) INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program) · [USGS State Geologic Map Compilation (SGMC)](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d)
- [EPSG:32611 WGS 84 / UTM Zone 11N](https://epsg.io/32611) · [Tversky Index (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index)

---

## Persistent Session Prompt Reference

Full durable operating contract also stored in [`SESSION_PROMPT.md`](SESSION_PROMPT.md).

<details>
<summary>Click to expand persistent session prompt</summary>

```markdown
Review the repo. Work on the previous sessions' next steps first.

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Stay inside one method lane. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.
4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.
5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

Study GEMSDOE32 (h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778): why and how did this get the highest score among the listed GEMSDOE sites, and are we able to generate a submission that scores higher than 0.2778? Before implementing anything, generate and rank 3-5 candidate geological hypotheses yet to be tried, verify data availability, validate format in [0, 1] without human inspection, provide unique submission name and note + executive summary subpage, store prompt in README.md, uphold Arena Core Values (Maximize P(Win), Own the Outcome), run 3 passes, and create and merge PR into main.
```

</details>
