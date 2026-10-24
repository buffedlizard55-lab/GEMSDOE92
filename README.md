# GEMSDOE92 — DOE GEMS Prize (#306): Automated Fault Discovery & Validation Workbench

**Live GitHub Pages Workbench:** <https://buffedlizard55-lab.github.io/GEMSDOE92/>  
**Executive Summary Subpage:** [`docs/executive-summary.html`](docs/executive-summary.html) · **Submission Guide:** [`docs/SUBMIT.html`](docs/SUBMIT.html) · **5 Ranked Untried Hypotheses:** [`docs/HYPOTHESES_20261024_COULOMBLOQO.md`](docs/HYPOTHESES_20261024_COULOMBLOQO.md) · **Full PhD Analysis:** [`docs/ANALYSIS_20261024_COULOMBLOQO.md`](docs/ANALYSIS_20261024_COULOMBLOQO.md)

---

## Immediate Two-Question Status (Automated Project Validation — Zero Human Inspector Required)

| Question | Automated Verdict | Exact Evidence & Reason |
|---|---|---|
| **1. Is the primary `.tif` OK TO DOWNLOAD?** | **✅ YES — OK TO DOWNLOAD FOR RESEARCH** | [`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`](docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif) (`SHA-256: 8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`) passes **10/10** `gems.gates` + `gems57.validate` + `scripts/check_site.py` checks (`EPSG:32611`, `3730 × 3292`, `float32`, finite `[0.0, 1.0]` everywhere, `0.0` outside footprint, `0` NaN anywhere — preventing DrivenData's `"Predicted values must be in range [0, 1]"` error — `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`). |
| **2. Is it CLEARED TO SUBMIT to a live weekly DrivenData slot?** | **⛔ NO — DO NOT SUBMIT (`submission_eligible: false`, `verdict: "negative"`)** | Locally unique across **all 41 cross-lane `GEMSDOE92` rasters** (`worst 3-px overlap = 0.6164 <= 0.70`, `|phi| = 0.0493 <= 0.90`), and sibling `dual45` achieves **`0 / 1,121` (`max = 0.6488 <= 0.70`)** across all `<= 90k`-px sparse public submissions, **but** under the literal Rule-1 public scan (`1,368` template rasters across 102 public `GEMSDOE` repos), dense full-footprint probability surfaces led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373 / 5,167,373` positive footprint cells) force `forward_overlap = 1.000 > 0.70` ([`evidence/coulomb_loqo_public_registry_uniqueness.json`](evidence/coulomb_loqo_public_registry_uniqueness.json)). `0` weekly slots spent. |

### Primary Artifact Card (`COULOMBLOQO standalone`)

| Field | Value |
|---|---|
| **Download (zeros-outside `.tif`)** | [`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`](docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif) · [`.zip`](docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.zip) |
| **Unique Submission Name (local ledger)** | `GEMSDOE92-COULOMBLOQO-standalone-20261024` |
| **Submission Note (`89 / 140` chars)** | `h33-h33-2-b2; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)` |
| **SHA-256 (`-zeros.tif` / `.zip`)** | `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e` / `448395137acb4860c24402fb53002539f3c688f8c232c79c23991353623c4c48` |
| **Audit & Protocol Rule 5 Run Card** | [`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-audit.json`](docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-audit.json) · [`evidence/coulomb_loqo_run_card.json`](evidence/coulomb_loqo_run_card.json) |
| **Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` px)** | **`0.009220 [0.007983, 0.010493]`** (**#1 all-time `GEMSDOE92` high**; `+130.2%` vs `R0` `0.004006`; `+52.5%` vs `RELIEF p10` `0.006045`; beats `HYDROCONDUIT` `0.008549` & `APRONRIDGE` `0.008354`; strict draw-blind `d_cat > 2.0` = **`0.009689`**) |
| **Strict Draw-Blind Rule-2 `d_visible > 2.0` `HOLDOUT-DTI`** | **`0.113316 [0.100614, 0.127163]`** vs `H19-5` `0.096757` (paired $\Delta = +0.016559$, 95% CI `[+0.008170, +0.024980]` — **first `0% H19-5` standalone model in repo history to beat `H19-5`**) |
| **Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px)** | **`0.090569`** (`+22.2%` over `HYDROCONDUIT` `0.074107`; sibling `dual45` = **`0.094057`** vs `R0` `0.096060`) |
| **Leakage Canaries (43 raw/derived/LOQO features)** | **PASS** — `max symmetric AUC = 0.672638 <= 0.90` ([`evidence/coulomb_loqo_screen.json`](evidence/coulomb_loqo_screen.json)) |

---

## PhD Answer: Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Beat Every Listed `GEMSDOE` Site & How to Beat It

Full mathematical derivation: [`docs/ANALYSIS_20261024_COULOMBLOQO.md`](docs/ANALYSIS_20261024_COULOMBLOQO.md).

1. **Exact DTI Metric Geometry (`#IR-92-ALPHA-BETA-PROSE-SWAP` Corrected):**
   - Verified directly against [`drivendataorg/gems-prize-reference-solution/unet-mc-cv-reference-solution.ipynb`](https://github.com/drivendataorg/gems-prize-reference-solution) (Cell 16) and [`vendor/gems57/metric.py`](vendor/gems57/metric.py):
     $$\mathrm{DTI}(A, G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w}, \qquad K(r) = \max\!\left(0,\, 1 - \frac{r}{300\,\mathrm{m}}\right), \qquad \Omega_{\text{eval}} = \Omega \setminus C.$$
   - Contrary to inverted prose in earlier session docs, **false negatives carry $4\times$ the denominator weight of false positives ($\beta = 0.8$ vs $\alpha = 0.2$)**. Nevertheless, placing two dots closer than `2.8 px` (`280 m`) still degrades DTI because $c_{\text{pred}}(g) = \max_{x \in A} K(\|g - x\|_2)$ takes a **pointwise maximum** rather than a sum — redundant dots add $\approx 0$ to $\mathrm{TP}_w$ while adding full $+0.2$ per-dot penalty to $0.2\,\mathrm{FP}_w$.
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
| `APRONRIDGE free1d` | `37,654` (`0%`) | `0.008354 [0.006823, 0.010135]` | — | `0.080098` | `0.6507` (PASS) | — | `1.0000` (dense STOP) |
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
