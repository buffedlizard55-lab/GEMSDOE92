# 2026-10-30 Three-Pass Repository & Focus-9 Review

**Decision: `OK TO DOWNLOAD FOR RESEARCH ONLY` · `DO NOT SUBMIT`.** No new TIFF, geological experiment, or holdout was produced in this review; no competition slot was used. This is an evidence and publication review, not a competition-score verification or organizer decision.

## Executive summary

- The **current site download anchor** is the existing `LIDAR-SINTERVALVE` research raster, SHA-256 `0db6046848adf1ac78d71baa34a49ae54c75018542ca50c3d2fb3e479505780e`. The TIFF is available for research only; it is not cleared for portal upload.
- Its local GeoTIFF format audit passes **11/11** gates: one-band `float32`, `EPSG:32611`, shape `3730 × 3292`, sample transform, all finite values in `[0,1]`, no NaN/Inf, and exact zero outside the valid footprint. This is a local format result, not organizer acceptance.
- A fresh 2026-10-30 **final-dot PI-1** registry audit passes at worst 3-pixel overlap `0.690949` and worst `|ρ|=0.058252`. It compares 2,345 SHA-256 values from an eight-owner public GitHub mirror snapshot. It does **not** re-audit the missing pre-placement surface. The prior run card recorded pre-placement top-N overlap `1.000` and `|ρ|=0.803516`; the literal full-support witness remains `1.000 > 0.70`. The final-dot pass does not waive either stop.
- Stored `HOLDOUT-DTI` (not rerun here) is `0.178619` `[0.163071, 0.193316]`; versus `control_netexpand_far = 0.177976`, paired Δ is `+0.000643` with 95% CI `[-0.002525, +0.004321]`. The interval includes zero, so an improvement over that prior best is not established. Do not use a weekly slot.
- **All nine Focus-9 pinned files** (`GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, `36`) match their exact registry paths, byte sizes, and SHA-256 values; all nine have exact-byte copies in another repository. This is an exact-hash check, not a new spatial-overlap/rank-correlation audit, a freshness guarantee beyond the dated snapshot, or organizer verification.
- The exact method paragraph referenced by the standing prompt was not present. No lane was selected by inference. The four hypotheses below remain backlog items—unimplemented/unrun in the inspected project code, but previously documented, not novel.
- The visible site and machine-readable current/readiness feeds now point to the existing LIDAR research raster. `docs/index.html` has one explicit `data-primary="true"` TIFF anchor; `docs/nine-sites.html` is a review page and has no primary-download designation. Focus-9 receipts, input-restoration receipt, format audit, final-dot receipt, and status feeds are linked or downloadable.

## Pass 1 — Evidence, identity, and provenance

### Restored inputs

All **22/22** pinned inputs from `registry/session_manifest.json`, `registry/ventscarp_external_manifest.json`, and `registry/lidar1m_external_manifest.json` were hash- and size-verified. The core raster audit is **12/12**, including the `EPSG:32611`, `3730 × 3292`, 100 m, 19-band training stack. Persistent receipt: [`evidence/input_restore_20261030.json`](../evidence/input_restore_20261030.json) and downloadable copy [`docs/downloads/input_restore_20261030.json`](downloads/input_restore_20261030.json).

**Provenance caveat:** these checks bind bytes to pinned public GitHub owner-maintained mirrors. Direct official organizer/source-host access and redistribution rights were not independently verified. This is not proof of official origin, permission, or competition eligibility.

### Fresh registry snapshot and LIDAR artifact

Snapshot identity recorded in both the Focus-9 and LIDAR receipts:

- Built `2026-10-30T23:22:46Z`; 8 owners, 108 repositories, 3,522 grid-compatible raster records, 2,346 unique SHA-256 values, 0 errors.
- Inventory SHA-256: `55f2f0b7c1cf439c435e393df0dad84c44e750b68eab727bcb8375b533e46ed6`.
- Snapshot method: current default-branch GitHub owner-mirror tarballs; it is not a single commit-pinned, organizer-authenticated fleet snapshot.

The LIDAR receipt at [`evidence/lidarsintervalve_registry_20261030.json`](../evidence/lidarsintervalve_registry_20261030.json) excludes the candidate's own SHA from comparisons (2,345 comparison hashes), audits 37,654 final dots, and reports PI-1 pass. Worst overlap `0.690949` is against `buffedlizard55-lab/13GEMSDOE`; worst `|ρ|=0.058252`. The candidate's stored run card separately records the failed/missing pre-placement evidence and literal witness. Full receipt: [`docs/downloads/lidarsintervalve_registry_20261030.json`](downloads/lidarsintervalve_registry_20261030.json).

### Focus-9 byte audit

The reproducible audit is `scripts/audit_focus9_registry_v3.py`; its persistent receipt is [`evidence/focus9_registry_20261030.json`](../evidence/focus9_registry_20261030.json). It reports 9/9 exact path/hash/size matches and 9/9 with exact copies in another repository. Counts of distinct other repositories with same-SHA copies are below; the download page gives representative repositories and pinned links.

| Site | Owner-reported `CLAIM` | Exact same-byte copies in other repositories |
|---|---:|---:|
| GEMSDOE24 | 0.2477 | 8 |
| GEMSDOE25 | 0.2600 | 12 |
| GEMSDOE27 | 0.2449 | 7 |
| GEMSDOE28 | 0.2710 | 5 |
| GEMSDOE30 | 0.2600 | 10 |
| GEMSDOE31 | 0.2708 | 3 |
| GEMSDOE32 | 0.2778 | 18 |
| GEMSDOE33 | 0.2632 | 14 |
| GEMSDOE36 | 0.2750 | 13 |

The separately stored LBM-v3 LOGO values are diagnostics from `evidence/lbm_v3_model_20261029.json`, **not scores**: 24 `0.252894`; 25 `0.258007`; 27 `0.250741`; 28 `0.260576`; 30 `0.258007`; 31 `0.262884`; 32 `0.263968`; 33 `0.261018`; 36 `0.262040`. Model-wide LOGO RMSE is `0.028028`, Spearman `0.920708`. This is a claim-trained repository diagnostic; it cannot validate an organizer score or infer a new submission result.

## Pass 2 — Scientific claims, comparison, and protocol gates

### GEMSDOE32 `0.2778` versus `0.3195` and `0.4413`

- The pinned `GEMSDOE32 h33-h33-2-b2` file is tied to an owner-maintained `0.2778` **CLAIM**. This repository has no organizer submission receipt binding that raster to a score. The exact file is a 37,654-dot binary TIFF with SHA-256 `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`.
- A cautious mechanism-level possibility is that a sparse dot budget and spatial thinning can trade redundant detections against local recovery under a tolerance-based score. The artifact lineage does not identify which design choice caused the reported value, does not reveal hidden labels, and cannot establish a causal explanation. The LBM-v3 LOGO value `0.263968` is a separate model diagnostic, not a reproduction or score estimate.
- Historical repository records are not consistent enough to treat the other values as current verified benchmarks. `docs/ANALYSIS_20261025_LEADERBOARD.md` records a 2026-10-25 top-50 snapshot with `0.4413` for `xiaofanhu`, not a GEMSDOE entry, and says `0.3195` did not appear in that top-50 (the adjacent reported values were `0.3217` and `0.3169`). `evidence/focus9_executive_audit_20261026.json` describes a sibling cache recording `xiaofanhu = 0.4437` on 2026-10-26, `0.4413` on 2026-10-25, and `0.3195` as an earlier historical figure. This review did not fetch the live leaderboard or independently reconstruct the archived pages.
- Therefore `0.2778`, `0.3195`, and `0.4413` are not interchangeable observations. The larger numbers are historical leaderboard references in repository/prompt material, not organizer receipts for GEMSDOE32 or GEMSDOE92; none is claimed as the current live leader. Local `HOLDOUT-DTI` is a spatially blocked visible-catalogue recovery measure and is not numerically comparable to a leaderboard score.

### Ranked unimplemented research hypotheses (not selected or tested)

The four ideas below are in the prior backlog (`docs/HYPOTHESES_20261028_9649DFC1.md`). No corresponding integrated loader/feature/experiment implementation was found in the inspected `gems/` code. They are **untried in this checkout's integrated experimental pipeline**, but not new ideas and not evidence of expected gain. Ranking is qualitative—mechanistic directness, expected data burden, and confounder risk—not measured DTI or numerical `P(Win)`.

1. **NWIS groundwater-head and seasonal phase-lag barrier.** Test whether pumping/screen-depth-controlled response across nearby wells shows a persistent cross-strike head or seasonal-lag discontinuity. Control for pumping, irrigation, aquifer boundaries, and well density. Official starting point for later manual review: [USGS Water Services groundwater-level API](https://waterservices.usgs.gov/rest/gwlevels-service/). *Ranked first for a direct structural test if site coverage is adequate; coverage/metadata burden is high and unverified.*
2. **ASTER TIR + Landsat SWIR alteration seam.** Test whether co-registered silica/clay alteration boundaries align with structural corridors after lithology and land-cover controls. Main mimics are lithologic contacts, playa/dune surfaces, mine waste, and registration error. Official starting points: [NASA LP DAAC ASTER GED v3](https://lpdaac.usgs.gov/products/ag100v003/) and [USGS Landsat Collection 2 Level-2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products). *Ranked second for geothermal relevance; direct fault specificity and coverage remain uncertain.*
3. **ComCat focal-mechanism consensus × geodetic strain.** Propagate nodal-plane uncertainty and event quality; test whether independent events' plane orientations agree with local strain and independent lineaments, while separating induced sequences/aftershocks. Main risks: sparse mechanisms, nodal-plane ambiguity, induced seismicity, and sampling bias. Official starting points: [USGS FDSN event service](https://earthquake.usgs.gov/fdsnws/event/1/) and [ComCat documentation](https://earthquake.usgs.gov/data/comcat/). *Ranked third: structurally specific but likely sparse and costly to control.*
4. **Repeat-pass thermal persistence.** Test multi-date, seasonally normalized land-surface-temperature lineaments after elevation, aspect, land-cover, irrigation, cloud, and emissivity controls. Main mimics include soil moisture, vegetation, transient surface flux, and revisit gaps. Official starting point: [USGS Landsat Collection 2 Level-2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products). *Ranked fourth: potentially useful context but least specific to fault geometry and highly confounded.*

The exact assigned method paragraph is absent, so none of these is selected as the current lane. Official links are for later manual review only; they were **not live-fetched or availability/rights-checked** in this review. No experiment or holdout was authorized or run.

### Protocol decision

The current artifact remains negative under the standing contract:

1. The LIDAR pre-placement surface is missing for the fresh 2026-10-30 inventory; the older run-card value `1.000` exceeds the `0.70` overlap threshold.
2. The literal full-support witness reports `1.000`, so a sparse final-dot PI-1 pass cannot be interpreted as a waiver.
3. The stored paired `HOLDOUT-DTI` result versus the prior best includes zero; the no-slot decision rule is not met.
4. Official organizer provenance and redistribution rights are unverified.
5. No current method paragraph exists. Do not infer a lane, run another experiment, produce a candidate TIFF, or describe an existing raster as cleared.

No new candidate, holdout, weekly-slot decision, or portal upload was made. A future authorized experiment must reuse cached features, shared evaluator and writer; use whole buffered fault-segment holdout, visible-only catalogue features, exact visible-fault masking, pooled DTI `α=0.2, β=0.8`, 300 m triangular kernel; run feature-alone leakage canaries (AUC `>0.90` is a stop); audit uniqueness both before placement and on final dots (rank correlation `≤0.90`, no more than 70% within 3 px of any registry raster); and emit a JSON run card. The maximum is three experiments or two hours. A weekly slot remains separate and requires the paired holdout decision rule and all gates.

## Pass 3 — Site wiring, validation, and delivery

- Updated the renderer so the **existing LIDAR-SINTERVALVE TIFF** is the current research-download anchor, while the old RIESZ entry remains historical context. The current/readiness JSON feeds bind to the same run card, exact TIFF hash, 11-gate format audit, current registry receipt, and negative status.
- Added a Focus-9 page with all nine commit-pinned file identities, owner-reported `CLAIM` values, explicitly non-score `MODEL` diagnostics, exact-byte clone results, current download status, benchmark caveats, the ranked backlog, and official URLs marked not live-verified.
- Made the input, Focus-9, and fresh LIDAR registry receipts downloadable; retained the separate `OK TO DOWNLOAD FOR RESEARCH ONLY` versus `DO NOT SUBMIT` distinction. No new TIFF was generated.
- Extended `scripts/check_site.py` to accept the historical LIDAR run-card uniqueness schema (`correlation_overlap_vs_registry`) without relaxing promotion checks.
- Final checks completed after wiring: the full test suite passes (859 passed, 19 skipped, 171 warnings); `scripts/check_site.py` passes for 132 served rasters; the standalone validator reports 11/11 local format gates PASS and then returns the expected rejection-only `DO NOT SUBMIT` decision (exit 1); `compileall` and `git diff --check` pass. Exact commands are listed in [Final verification](#final-verification).

## Review artifacts and links

- [Executive summary / current status](index.html)
- [Nine-site review](nine-sites.html)
- [Focus-9 review page](focus9-review-20261030.html)
- [Submission instructions](how-to-submit.html)
- [Current status feed](downloads/current_submission.json) · [readiness feed](downloads/readiness.json)
- [LIDAR format audit](downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros-audit.json) · [run card](downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e_run_card.json) · [fresh final-dot audit](downloads/lidarsintervalve_registry_20261030.json)
- [Focus-9 exact-hash receipt](downloads/focus9_registry_20261030.json) · [input restore receipt](downloads/input_restore_20261030.json)

## External links — official references supplied for later review; not live-verified here

- [DrivenData competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) · [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [reference solution repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [USGS GeoDAWN DOI](https://doi.org/10.5066/P93LGLVQ) · [DOE GDR / INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [USGS NWIS groundwater levels](https://waterservices.usgs.gov/rest/gwlevels-service/) · [NASA LP DAAC ASTER GED v3](https://lpdaac.usgs.gov/products/ag100v003/) · [USGS Landsat Collection 2 Level-2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products) · [USGS FDSN event service](https://earthquake.usgs.gov/fdsnws/event/1/) · [ComCat documentation](https://earthquake.usgs.gov/data/comcat/)

These are reference URLs only. This review did not fetch the official pages or verify current contest rules, live leaderboard values, data availability, or redistribution terms.

## Final verification

Executed after the last renderer/checker/test-source edit:

```text
PYTHONPATH=vendor .venv/bin/python scripts/render_site_v3.py                 PASS (generated pages and status outputs refreshed)
.venv/bin/python -m pytest tests -q                                         859 passed, 19 skipped, 171 warnings
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py                    PASS (132 served rasters gated)
PYTHONPATH=vendor .venv/bin/python validate_submission.py docs/downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif  11/11 format gates PASS; then DO NOT SUBMIT, exit 1 as designed
.venv/bin/python -m compileall -q scripts tests                             PASS
git diff --check                                                            PASS
```

The validator's nonzero exit is intentional: it verifies format but is rejection-only and refuses to authorize a weekly slot. The `171` warnings are existing Rasterio pending-deprecation warnings plus a test-only georeference warning; no test failed.
