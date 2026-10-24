# GEMSDOE92 — DOE GEMS Prize #306 Auditable Submission Workbench (`HYDROCONDUIT` Session)

> ### ✅ DOWNLOAD STATUS: **FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH**
> ### ⛔ SUBMISSION / WEEKLY SLOT STATUS: **DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`, `submission_eligible: false`; DUPLICATE UNDER THE LITERAL REGISTRY RULE)**
>
> - **Current Primary GeoTIFF (zeros outside, `nodata=None`):** [`docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`](docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif) · [One-TIFF ZIP](docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.zip)
> - **SHA-256 (`-zeros.tif`):** `c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd` (`37,654` unit-mass dots, `0.0` outside footprint, `0` catalogue mass)
> - **Suggested Submission Name (for ledger / human selector record only):** `GEMSDOE92-HYDROCONDUIT-f45hydro-20261024`
> - **Suggested Form Note (106 / 140 chars):** `h33-h33-2-b2; HYDROCONDUIT f45hydro: 20710 piedmont H19-5 + 16944 off-skel scarp/RTP/GDR dots (>3px H19-5)`
> - **Automated Gate Receipts:** [Format & Public-Registry Audit JSON](docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-audit.json) (`10/10` `gems.gates` + `13/13` `gems57.validate` PASS — prevents DrivenData error `"Predicted values must be in range [0, 1]"`) · [Protocol Run Card JSON](docs/downloads/hydroconduit_run_card.json)
> - **Site Pages:** [Main Workbench (`docs/index.html`)](docs/index.html) · [Executive Summary & Submission Form Guide (`docs/executive-summary.html`)](docs/executive-summary.html) · [Detailed Submission Procedure (`docs/SUBMIT.html`)](docs/SUBMIT.html) · [Candidate Geological Hypotheses (`docs/HYPOTHESES.html`)](docs/HYPOTHESES.html)

---

## Why Is `HYDROCONDUIT f45hydro` OK to Download Yet Blocked From Submission?

1. **Why It Is a Genuine Scientific & Holdout Breakthrough (`OK TO DOWNLOAD`):**
   - **First candidate in `GEMSDOE92` to beat BOTH `R0` and prior holdout-best `RELIEF p10`:** On the shared `gems57-pooled-hide-v2` buffered spatial holdout (`22,663` withheld catalogue fault pixels, `1,000` paired cluster-bootstrap draws), `HYDROCONDUIT f45hydro` achieves **`HOLDOUT-DTI = 0.008549 [0.007626, 0.009487]`** — **`+113.4%` over `R0` (`0.004006`)** (`Δ = +0.004543 [+0.003770, +0.005315]`) and **`+41.4%` over `RELIEF p10` (`0.006045`)** (`Δ = +0.002504 [+0.001795, +0.003222]`).
   - **Passes all 24 single-feature leakage canaries:** max symmetric ROC AUC = **`0.65012 <= 0.90`** (`evidence/hydroconduit_preplacement_screen.json`).
   - **Unique against ALL local rasters AND ALL 1,147 sparse dot-like rasters across 102 public `GEMSDOE` repositories:** Local worst 3-px forward overlap = **`0.5500 <= 0.70`** (`|rho| = 0.2982 <= 0.90`; pre-placement surface `0.1892 <= 0.70`, `|rho| = 0.1098`). Live 102-repo GitHub API scan (`1,332` compatible rasters) shows **`0 / 1,147` sparse rasters (`<= 150,000` positive px) exceed `70%`** (`max = 0.6719 <= 0.70`; `|rho| <= 0.4396`).
2. **Why `verdict` Remains `"negative"` (`DO NOT SUBMIT` Without Human Policy Override):**
   - **Literal Public Dense-Witness Rule:** Under the literal Rule-1 definition (`support = (theirs > 0) & footprint`, no representation exemption), `118` dense public surfaces (`> 150,000` positive pixels, led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` which is positive on **`5,167,373 / 5,167,373 = 100%` of footprint cells**) yield `1.000 > 0.70` forward overlap for **any** nonempty in-footprint prediction. Only a human operator can exempt dense continuous probability surfaces (`> 150k` px).
   - **Multi-Instrument Disclosure:** True Rule-2 fold-by-fold `d_visible > 2.0` holdout (`0.0852` vs `0.0968` `H19-5` skeleton-only) and off-catalogue `USGS SGMC` bedrock fault proxy (`0.0741` vs `0.0961` `R0`) show that static-holdout gains partly reflect piedmont `H19-5` collar repacking while forcing `45%` of mass `> 300 m` off `H19-5` trades `H19-5` spine density and exposed mountain-core bedrock faults (`SGMC`).

---

## PhD Analysis: Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Led the Listed Sites & How to Beat It

Full forensic derivation: [`docs/ANALYSIS_20261024_HYDROCONDUIT.md`](docs/ANALYSIS_20261024_HYDROCONDUIT.md).

1. **Why `h33-h33-2-b2` (`0.2778` `[CLAIM]`, no organizer receipt in `ledger/`) Beat Other Listed Sites (`0.2512–0.2750` `[CLAIM]`):**
   - **Asymmetric Distance-Weighted Tversky Geometry ($\alpha=0.2, \beta=0.8$, 300 m triangular kernel):** Coverage of a target pixel uses the **maximum** kernel weight $\max_{x \in A} (1 - d(g,x)/300\,\mathrm{m})$, while every redundant dot adds full unit mass to the false-positive penalty $0.2\,\mathrm{FP}_w$.
   - `GEMSDOE32` combined four orthogonal structural operations: **(i)** 1-px geophysical/DEM worm crest extraction (`H19-5`, `121,131` px, `0.2194` `[CLAIM]`), **(ii)** geodesic Poisson-disk de-aliasing at `2.828 px` = `283 m` matching the `300 m` kernel radius (`D2.8`, `46,612` px, `0.2649` `[CLAIM]`), **(iii)** isolated 1–2-dot speckle pruning (`SOLO`, `40,199` px, `0.2708` `[CLAIM]`), and **(iv)** `<= 200 m` (`d_cat <= 2.0 px`) known-catalogue exclusion (`37,654` px, `0.2778` `[CLAIM]`), removing dead mass on masked catalogue traces while retaining `2,171` splay dots at `200–300 m`.
2. **Why `R0` Has Headroom Above `0.2778` `[CLAIM]` (Prompt-Reported LB Top `0.3195` / `0.4413` `[CLAIM]`):**
   - `R0` thinned `H19-5` in **physics-blind row-major scan order**, stranding thousands of dots on bare mountain-core contacts and flat playas, and is **100% blind** to subtle Quaternary piedmont alluvial-fan scarps and hydrothermally altered conduits lacking multi-line potential-field worms.
   - Prior `GEMSDOE92` off-skeleton lanes (`BREAKLINE`) used un-normalized $\|\nabla \text{slope}\|$, which was hijacked **`74.8%` by bare mountain range-core cliffs (`det_elev >= +38.8 m`)** and `28.9%` by E–W incised canyons, and missed `Band 2 RTP` magnetic tilt/demagnetization because `Band 6 tc` in `training_features.tif` is actually **Radiometric Total Count (`r = 0.99714` with `GeoDAWN TC`)** (`#IR-92-BAND6-TC-MISLABEL`).
   - `HYDROCONDUIT` fixes all three defects (`83.4%` piedmont / `6.2%` range core, true `Band 2 RTP` tilt/demag + `GeoDAWN K/Th` + `Band 17` MT + `GDR #1391` surface & `>= 80 °C` blind silica/cation geothermometry), more than doubling `R0` on the shared static holdout (`0.004006 -> 0.008549`, `+113.4%`) — though only an `ORGANIZER-CONFIRMED` submission receipt can prove live leaderboard superiority over `0.2778` `[CLAIM]`.

---

## Summary Benchmark Table (Evidence Labels Explicit)

| Artifact / Baseline | Dots | Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` pos, 95% CI) | Paired $\Delta$ vs `RELIEF p10` | `SGMC` `PROXY` DTI (`62,703` px) | Local Overlap (`<=0.70`) | Sparse Public `<=150k` (`1,147` rasters) | Literal Public (`1,332` rasters) |
|---|---:|---|---|---|---|---|---|
| `R0` (`h33-h33-2-b2`, `0.2778` `CLAIM`) | 37,654 | `0.004006 [0.003424, 0.004690]` | `-0.002039` | `0.096060` | self | — | — |
| `RELIEF p10` (prior holdout best) | 37,654 | `0.006045 [0.005187, 0.006927]` | baseline | `0.087245` | `0.9938` (DUP) | — | `1.0000` (DUP) |
| `BREAKLINE f45Ltop` | 37,654 | `0.004861 [0.004032, 0.005822]` | `-0.001185` | `0.126105` | `0.5500` | — | `1.0000` (DUP) |
| `SPRINGALIGN f33Ctop` | 37,654 | `0.004865 [0.004025, 0.005785]` | `-0.001180` | `0.080173` | `0.6700` | — | `1.0000` (DUP) |
| `ANASIG f45Atop` | 37,654 | `0.004967 [0.004098, 0.005940]` | `-0.001078` | `0.080556` | `0.5500` | — | `1.0000` (DUP) |
| `STRAINBREAK f60s2i` | 37,654 | `0.005487 [0.004522, 0.006430]` | `-0.000558` | `0.105162` | `0.4150` | `0.7105` (`3 > 70%`) | `1.0000` (DUP) |
| **`HYDROCONDUIT f45pied` (Exp 1)** | 37,654 | **`0.008524 [0.007621, 0.009459]`** | **`+0.002479`** | `0.073312` | **`0.5500` (PASS)** | — | `1.0000` (dense DUP) |
| **`HYDROCONDUIT f45hydro` (Exp 2 — Primary)** | 37,654 | **`0.008549 [0.007626, 0.009487]`** | **`+0.002504`** | `0.074107` | **`0.5500` (PASS)** | **`0.6719` (`0 > 70%`, PASS)** | `1.0000` (dense DUP) |
| **`HYDROCONDUIT f50hydro` (Exp 3)** | 37,654 | **`0.008457 [0.007532, 0.009430]`** | **`+0.002412`** | `0.072799` | **`0.5143` (PASS)** | **`0.6578` (`0 > 70%`, PASS)** | `1.0000` (dense DUP) |

---

## Arena Core Values

- **Maximize P(Win):** Every experiment is pre-registered from physical Basin-and-Range fault/geothermal mechanisms (`docs/HYPOTHESES_20261024_HYDROCONDUIT.md`), screened with single-feature leakage canaries, evaluated with spatial whole-component holdouts (`gems57-pooled-hide-v2`), and audited against 1,332 public rasters so scarce weekly competition slots are never wasted on duplicates or noise.
- **Own the Outcome:** Format validation (`[0, 1]` finite range, zero NaNs, `EPSG:32611` `3730 × 3292` grid, zero catalogue mass), irregularity discovery (`IRREGULARITIES.md`), and multi-instrument trade-off reporting (`d_visible > 2.0` vs static `d_cat > 2.0` vs `SGMC`) run end-to-end inside the project without waiting for manual inspection.

---

## Reproducible Validation & Verification Pipeline

```bash
# 1. Restore SHA-256-pinned stack & external inputs into .cache/gems_inputs/
python3 scripts/restore_inputs.py && python3 scripts/verify_manifest.py

# 2. Run automated unit & site-contract test suite
.venv/bin/python -m pytest -q

# 3. Reproduce pre-placement leakage canaries & surface uniqueness screen
.venv/bin/python scripts/screen_hydroconduit_surface.py

# 4. Build & gate-check the 3 pre-registered HYDROCONDUIT experiments
.venv/bin/python scripts/build_hydroconduit_variants.py
.venv/bin/python scripts/report_hydroconduit_proxies.py

# 5. Validate all served downloads & site banners automatically (zero human inspector required)
.venv/bin/python scripts/validate_submission.py
.venv/bin/python scripts/check_site.py
```

---

## Trusted Official Sources

- [DrivenData Competition #306 Problem & Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [About](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) · [Data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Competition Rules PDF (NREL/TP-5700-96647)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData Reference Solution Repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN Airborne Magnetic & Radiometric Surveys](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [Data Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository (GDR) INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program) · [USGS SGMC](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d)
- [EPSG:32611 WGS 84 / UTM Zone 11N](https://epsg.io/32611) · [Tversky Index (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index)

---

## Stored Session Prompt

<details>
<summary>Click to expand full stored session prompt</summary>

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
