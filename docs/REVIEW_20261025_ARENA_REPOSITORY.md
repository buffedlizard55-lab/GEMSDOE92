# Three-pass repository review — 2026-10-25 UTC

## Decision summary

**Existing TIFFs are downloadable for research. DO NOT SUBMIT or spend a weekly slot. No TIFF or experiment was generated in this review.** The prompt's protocol does not assign this session a single method lane, and a pinned public raster that is positive throughout the study footprint forces literal forward dot overlap to `1.0`, exceeding the specified `0.70` stop threshold for every nonempty candidate. The stop applies before generating a new surface or placing dots. This report does not reinterpret that rule as a matched-budget exception.

The repository already contains the prior LISTRIC research TIFF, which passes the local GeoTIFF format/range validator, but its own run card records public overlap `0.710735 > 0.70` and literal dense-witness overlap `1.0`; it is not submission-cleared. It is byte-distinct from scanned rasters in the recorded scan, but byte uniqueness is not spatial uniqueness. Its filename/run-card date is `2026-10-26`, which is in the future relative to this review's date (`2026-10-25 UTC`); therefore this review does not assert that it is the chronologically latest artifact.

**Existing research artifact:** [`LISTRIC standalone zeros TIFF`](downloads/h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif) · [run card](../evidence/listric_run_card.json) · [analysis](ANALYSIS_20261026_LISTRIC.md). SHA-256: `7e4b46368b2a5949bcf626bfaa4457ed15a89dde38d412a1d07469411a31e2ab`.

## Pass 1 — inspect, validate, and establish what is known

### Repository and test status

- Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_CURRENT.md`, `docs/NEXT_STEPS.md`, the LISTRIC run card and the duplicate-stop receipts. The operating prompt is already retained in `README.md` and `SESSION_PROMPT.md`.
- Branch: `arena/eaf7abf4-gemsdoe92`; repository was clean before this review.
- Installed the pinned Python requirements in a local ignored `.venv` because the base interpreter lacked NumPy/Rasterio. No tracked dependency file was changed.
- `PYTHONPATH=vendor .venv/bin/python -m pytest tests -q`: **491 passed**; 140 upstream `PendingDeprecationWarning`s from Rasterio/Affine.
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`: **82 served rasters passed** the site-format gates.
- `gems parent`: pinned R0 parent verified; **37,654** dots and SHA prefix `c55bafc47005…` (parent evidence; not a score).
- `gems manifest`: all 8 staged manifest entries passed. `gems ledger`: **111 entries; best ORGANIZER-CONFIRMED receipt: none**.
- `gems validate` on the linked LISTRIC TIFF: PASS (9 gates): single-band `float32`; CRS `EPSG:32611`; shape `3730×3292`; geotransform equals sample; all values finite and within `[0,1]`; no NaNs inside or outside footprint; zeros outside footprint. This is a local format preflight, **not** organizer acceptance and **not** submission eligibility.

### What the `0.2778` figure supports

The prompt-reported GEMSDOE32 `0.2778` remains a **CLAIM**, not an **ORGANIZER-CONFIRMED** receipt: the local ledger has no receipt for that artifact. Local byte-level parent lineage analysis supports that R0 is a fixed-budget, spatially thinned descendant of the prior H19-5/Poisson-spaced skeleton, with an additional catalogue-clearance filter. Those design choices are *plausible* reasons it might be efficient under a distance-tolerant asymmetric Tversky score: thinning can reduce redundant nearby prediction mass, while the catalogue collar removes predictions near known traces and retains some predictions in the scoring kernel's outer vicinity. This is a mechanism-level explanation, not causal proof of the reported score.

A causally defensible explanation requires an organizer receipt tying the exact TIFF bytes to the score, plus controlled paired ablations on the organizer's test labels or a faithful public proxy. The repository contains no such receipt. The reported lineage does not prove hidden-fault discovery, nor can a local holdout number be compared numerically to the claimed competition score. Therefore **whether a new candidate can beat `0.2778` on the competition is unknown**; the reported score cannot be authenticated here.

### Existing LISTRIC measurements (clearly separated evidence classes)

- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, static `d_cat > 2 px`, 22,663 withheld positives; CI as recorded): `0.010909 [0.009543, 0.012278]`. This is local hide-and-recover evidence, not a competition score.
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, strict fold-visible `d_visible > 2 px`, 22,663 withheld positives; CI as recorded): `0.110593 [0.097436, 0.123346]`. This is a separate instrument and is not interchangeable with the static-mask result.
- Against the stored KNICKLOQO standalone static control, the paired **HOLDOUT-DTI** delta is `+0.000121 [-0.001167, +0.001262]` (22,663 withheld positives, same evaluator), with the interval including zero. The run card calls this nominal ordering, not a demonstrated improvement.
- **REGISTRY-MEASUREMENT:** pre-placement surface maximum absolute Spearman in its recorded public scan: `0.481384` (below `0.90`); final-dots maximum absolute Spearman: `0.146888` (below `0.90`). Public final-dot overlap reaches `0.710735` (above `0.70`); the pinned full-footprint raster yields literal overlap `1.0`. The LISTRIC run card verdict is negative. The broader witness preflight independently records that any nonempty in-footprint candidate has overlap `1.0` against the all-positive witness.
- **ORGANIZER-CONFIRMED:** no receipt for LISTRIC or GEMSDOE32 was present in the ledger.

### Ranked candidate hypotheses — proposals only, not experiments

Ranking is qualitative and reflects scientific distinctness, feasibility and cost. **Expected DTI improvement is unknown for every candidate; there are no score projections.** These hypotheses appear in the repository's untried queue and have no matching implementation found in `gems/`. They are not authorized for execution while the binding pre-placement stop and lane-assignment gap remain.

| Rank | Hypothesis; layers | Physical signature | Why it might detect a fault missing from the catalogue | Difference from implemented families | Expected improvement / implementation cost / data status | Named non-fault mimic |
|---|---|---|---|---|---|---|
| 1 | **TENSOR-RIEDEL**; cached competition bands B2, B5, B7, B11, B12, B13, B18, B19 | Gravity-gradient tensor invariant plus a `15–25°` Riedel-style obliquity filter between surface lineament and basement tensor orientation, conditioned on regional strain direction | Short transfer splays in transtensional relays may be omitted when a catalogue traces only the through-going structure | Existing XPHASE/COULOMB methods emphasize collinearity or fixed-angle stress tendencies; this tests the angularly offset en-echelon relay geometry | Qualitative potential: medium, uncertain. Cost: medium (tensor derivatives/eigenvectors and orientation controls). Competition stack bands are named, but **the feature cache is absent from this checkout**; restore only from the authorized, hash-pinned source and verify use rights before a run. | Volcanic flow fabric, basalt dikes, or gravity-source boundaries without fault displacement |
| 2 | **FLEXURE-HINGE**; cached B12 elevation, B13 gravity, B15 basement depth, B18 gravity gradient, B19 slope | Long-wavelength curvature/flexural inflection and paired footwall-uplift/hanging-wall-rollover signature at kilometre scale | Buried basin-margin faults can deform cover as a broad monocline without preserving a sharp scarp | Existing terrain lanes target short-wavelength scarps and steps; this tests a long-wavelength hinge conditioned by basement geometry | Qualitative potential: medium, uncertain. Cost: medium; high-order derivatives are noise-sensitive. Same absent competition-stack constraint as above. | Differential compaction over paleochannels, lacustrine loading, or caldera-related deformation |
| 3 | **MTCHANGE**; B17 conductivity surface with B15 basement depth | Conductivity change-point remaining after conditioning on cover/basement depth | A conductive lineament unexplained by basin-fill thickness could mark a fluid pathway missed by surface-fault mapping | Prior MT lanes use conductivity level or clay-cap edges, not a depth-conditioned residual change-point | Qualitative potential: low-to-medium, uncertain. Cost: low-to-medium. Needs the absent, authorized feature stack; otherwise no new external data identified. | Playa/irrigation salinity or lateral clay-facies change |
| 4 | **SEISGRAVLAG**; B10/B16 seismic-event density/energy and B13 gravity anomaly | Signed lateral offset between a seismicity-density flank and gravity edge | A swarm aligned along a blind structure may occur beside, rather than directly atop, the basement step | Prior seismicity tests use intensity/distance levels; this is a cross-layer offset geometry | Qualitative potential: low-to-medium, uncertain. Cost: low. Requires stack availability and a pre-registered offset/control design. | Magmatic or induced seismicity near a lithologic boundary |
| 5 | **INSAR-3DEP1M-CREEP**; Sentinel-1 InSAR deformation and USGS 3DEP 1 m DEM tiles | Persistent LOS-velocity gradient paired with sub-pixel bare-earth scarp/curvature | Active creeping faults and micro-scarps may be absent from the 100 m training stack and mapped-fault catalogue | No repo module ingests this external high-resolution InSAR + LiDAR combination | Potential is unknown; cost high and **not viable from this sandbox**: neither data source is staged and external hosts are outside the declared network allowlist. Free official source references: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) and [NASA OPERA DISP-S1](https://www.earthdata.nasa.gov/data/projects/opera). No claim that either dataset was downloaded or checked for a particular tile. | Groundwater pumping/subsidence, seasonal decorrelation, or anthropogenic fill movement |

### Why no candidate was tested

1. The user-provided parallel-run protocol requires a named method lane; this message supplies no single lane paragraph. `SESSION_PROMPT.md` also records that no lane paragraph was assigned.
2. The literal uniqueness stop occurs before surface generation: the pinned public witness has positive support at every footprint cell, so any nonempty prediction set has overlap `1.0 > 0.70`. This is independently documented in `evidence/review_f23_preflight.json` and `evidence/review376a_preflight.json`.
3. The cached 19-band feature stack is not present under `.cache/gems_inputs/`; only small bridge/parent rasters are staged. The shared evaluator and writer are in `vendor/gems57`, but their existence does not supply missing features or resolve the stop.
4. No weekly slot was used. A held-out result cannot be represented as a competition score; promotion remains a separate selector decision.

## Pass 2 — defects, contradictions and edge cases

- **Blocking protocol ambiguity:** “generate a unique TIFF” conflicts with the literal registry stop. Do not waive the `0.70` threshold or recast it as matched-budget-only without an explicit policy change.
- **Lane ambiguity:** no method paragraph names this session's single lane. The hypothesis list above is therefore a review deliverable, not permission to execute one.
- **Date irregularity:** the LISTRIC run card and artifact are dated `2026-10-26`, future-dated relative to this review on `2026-10-25 UTC`. Historical repository records may be preserved, but don't call it newly generated in this session or chronologically “latest” without resolving the date discrepancy.
- **Status-feed mismatch:** README’s prominent artifact banner points to LISTRIC, while `docs/downloads/current_submission.json` still points at FAULTNET and the served homepage’s current banner renders FAULTNET. Both say research/download only and do-not-submit; nevertheless the filename/holdout/source fields differ. Do not treat these independent files as a single synchronized current feed.
- **Historical overclaim risk:** some historical pages describe candidates as “unique” under a matched-budget diagnostic even though the unchanged literal rule fails. The operative status must remain negative; old receipts should be labeled historical rather than rewritten.
- **Score provenance:** `ledger` has 111 rows and no best receipt. GEMSDOE32 `0.2778`, prompt leaderboard figures and other project-site scores are not organizer receipts in this checkout. The official authenticated DrivenData pages and current weekly cap were not reachable through the declared allowlist in this review.
- **Source provenance:** official reference links are listed for manual review below, but external official pages were not live-fetched. A hash-pinned owner mirror proves byte identity to the mirror only, not source authenticity, redistribution permissions or allowed competition use.
- **Potential metric interpretation hazard:** the two recorded LISTRIC holdout instruments produce numerically different values because the masks/visible-fault derivation differ; neither can be silently substituted for the other or compared with an organizer score.

## Pass 3 — final checklist and ordered next work

- [x] Read the persistent prompt and repo operating rules.
- [x] Ran all automated Python tests: 491 passed; warnings preserved.
- [x] Ran site gates: 82 served rasters passed.
- [x] Verified pinned parent and eight-entry data manifest.
- [x] Validated existing LISTRIC zeros TIFF: 9/9 format gates pass; no NaNs; values in range; CRS/shape/transform match.
- [x] Read LISTRIC run card and public-registry measurements; no attempt to reinterpret its negative verdict.
- [x] Ranked five untried candidates, named layers/signatures/mimics, differentiated method families, and identified data/cost constraints.
- [x] No model experiment, candidate surface, placement, new TIFF, or weekly slot was created.
- [x] After merging the advanced `main` into this session branch to resolve the PR conflict, reran the complete suite: **525 passed, 140 upstream warnings**; site gates passed for **82** served rasters. Earlier runs were 491 tests and 498 tests as successive main updates were merged; 525 is the final post-merge result for this branch.

Next actions, in order of decision value:

1. Resolve the literal-overlap policy conflict and assign one named lane, without retroactively clearing existing submissions.
2. Reconcile the README, current-submission JSON, and rendered homepage feed from one byte-bound source; include explicit research-download versus submit status.
3. Obtain and provenance-check the authorized feature stack and rights; the current cache is absent.
4. If explicitly permitted, pre-register TENSOR-RIEDEL as the leading in-stack hypothesis, freeze the control and spatial outer test, run each constituent feature's leakage canary, then use the shared buffered hide/recover evaluator and writer. Stop on any leakage/uniqueness violation; the three-experiment/two-hour budget applies.
5. For INSAR/LiDAR, stage specific free official tiles only on a machine/network that can access the named official services and confirm usage terms before proposing a viable test.
6. Verify an actual DrivenData score receipt and weekly cap before any human selector spends a slot. No automation should upload or select a slot.

Trusted source pointers (not live-verified here): [DrivenData problem statement](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [NASA OPERA](https://www.earthdata.nasa.gov/data/projects/opera), [EPSG:32611](https://epsg.io/32611).

**Arena values applied:** Maximize P(Win) means do not spend a weekly entry on an unvalidated candidate or claim a score without a receipt. Own the Outcome means preserving negative evidence, running project automation, and fixing the evidence/status gaps rather than hiding them.

## Run card

The machine-readable card is [`../evidence/review_20261025_arena_run_card.json`](../evidence/review_20261025_arena_run_card.json). It describes the existing artifact reviewed, not a new submission generated in this review.
