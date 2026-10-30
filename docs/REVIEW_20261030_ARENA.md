# Repository review — 2026-10-30

## Executive decision

**No new GeoTIFF was generated. Do not submit any download currently served by this repository.** This is an evidence-based negative result, not a failed attempt to satisfy the format validator: the active fail-closed status is `docs/downloads/readiness.json` (`verdict: negative`, `submission_eligible: false`). Existing rasters remain available for research only.

The requested combination—generate a genuinely unique TIFF, test it under the supplied registry thresholds, and stop if it breaches either threshold—cannot be met with the evidence and policy currently present. The repository's pinned dense-support witness was freshly fetched through the permitted GitHub API during this review and passed the existing byte/hash-bound preflight: all `5,167,373` finite template-footprint cells are positive. Under the literal candidate-directed 3-pixel overlap rule, any nonempty in-footprint candidate therefore has overlap `1.0`, above the `0.70` stop. This is a conservative registry-policy result, **not proof that the candidate would be geologically identical**. A second pinned binary-lattice witness is also recorded as a universal stop at the required dot budget. Do not reinterpret or waive either witness silently.

There is no standalone, named method paragraph in the current user prompt to designate as the sole experiment lane. The repo also has a large set of historical experiments and no current evidence package that authorizes another lane. Accordingly, this review did not create a surface, place dots, run feature canaries, run a holdout, or spend a competition slot. It also did not claim a score estimate where none can be calibrated defensibly.

## Focus-9 executive summary

This table is a **historical snapshot**, not a current organizer leaderboard audit. Values supplied for these sites are owner/user-reported **CLAIM**s, not ORGANIZER-CONFIRMED receipts. The per-file model score estimate is **not supportable**: the archived focus-site audit has no calibrated exact-file estimate and no organizer receipt binding each reported score to that TIFF. “Unique” means passing the prompt's pairwise screen against the other eight focus-site rasters; all nine fail at least one criterion. These are references for analysis, not files cleared to submit.

| Site | Best named submission in the supplied focus-site set | Reported result | Estimated score | Unique vs. other eight? | Decision |
|---|---|---:|---|---|---|
| GEMSDOE24 | [`h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan`](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/9da8a18381e179530c3b878d073314feaa26a20c/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif?raw=1) | **CLAIM 0.2477** | Not supportable | **No** — 1.0000 directed 3-px overlap with GEMSDOE27; `|rho|=0.9896` | Research reference only |
| GEMSDOE25 | [`dotted-h19-5-d2-8-20261002-e56ea318af89-nan`](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/cafbfe509670f4c0ba2a8475e288620a0aab0559/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif?raw=1) | **CLAIM 0.2600** | Not supportable | **No** — exact in-footprint prediction match with GEMSDOE30 | Research reference only |
| GEMSDOE27 | [`topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan`](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/cf8b4c201f2cc2ef649b6ca7cd32f235c2f6743a/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif?raw=1) | **CLAIM 0.2449** | Not supportable | **No** — 0.9798 directed 3-px overlap with GEMSDOE24; `|rho|=0.9896` | Research reference only |
| GEMSDOE28 | [`h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan`](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/12ec4fea4c97a7887a7ca8a06f9bd94c7609ea07/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif?raw=1) | **CLAIM 0.2710** | Not supportable | **No** — 0.8278 directed 3-px overlap with GEMSDOE25 | Research reference only |
| GEMSDOE30 | [`d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca`](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/35ce8911e2c3287eed973eacd12c252e8cb3f34c/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif?raw=1) | **CLAIM 0.2600** | Not supportable | **No** — exact in-footprint prediction match with GEMSDOE25 | Research reference only |
| GEMSDOE31 | [`h27-4-solo-d28-20261004-8acb75e1`](https://github.com/buffedlizard55-lab/GEMSDOE31/blob/8e91d82ae236c92b917302122237e45fc20ec337/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif?raw=1) | **CLAIM 0.2708** | Not supportable | **No** — 1.0000 directed 3-px overlap with GEMSDOE25; `|rho|=0.9545` | Research reference only |
| GEMSDOE32 | [`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/8b00ee91b9d6d7ef0e3762eb7bc0c92bee0928d1/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif?raw=1) | **CLAIM 0.2778** — highest supplied focus-site claim | Not supportable | **No** — 1.0000 directed 3-px overlap with GEMSDOE36; `|rho|=0.9843` | Research reference only; do not re-submit |
| GEMSDOE33 | [`h33d-analog-tip-stepover-r30-20261004-cb490425926e`](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/be96d94c8d829dbe4a5ae50330ae36130e10b807/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif?raw=1) | **CLAIM 0.2632** | Not supportable | **No** — 0.9028 directed 3-px overlap with GEMSDOE25 | Research reference only |
| GEMSDOE36 | [`anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros`](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/2c78770e0544259082b0b6b73ce8e4d0749c175d/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif?raw=1) | **CLAIM 0.2750** | Not supportable | **No** — 0.9717 directed 3-px overlap with GEMSDOE25; `|rho|=0.9090` | Research reference only |

**Source/evidence scope:** the snapshot and raster-by-raster pairwise audit are recorded in [`focus_sites_release_review_20261026.json`](downloads/focus_sites_release_review_20261026.json), [`focus9_pairwise_recheck_14f85876.json`](downloads/focus9_pairwise_recheck_14f85876.json), and the existing [nine-site audit page](nine-sites.html). The refs were pinned in the 2026-10-26 source inventory. They were not refreshed against today's GitHub main refs in this review. The table must not be treated as a live score feed.

### Why the reported GEMSDOE32 value was high (and what is not known)

The recorded lineage says `h33-h33-2-b2` is a R0-style thinning of an earlier dotted H19-5/D2.8 candidate: retain the D2.8-like spatial pattern while removing predictions within roughly two pixels of the known-catalogue mask. A plausible metric mechanism is that reducing redundant positive mass can lower false-positive cost (the cited competition metric weights false positives less than false negatives) while a tolerance kernel still rewards predictions near withheld traces. This is a **mechanistic hypothesis**, not causal attribution: the target labels are hidden, the `0.2778` is an owner/user **CLAIM**, and no organizer receipt is available to bind it to the exact raster. It is not evidence that a copy, clone, or small perturbation will score well. The same footprint is represented by a tracked parent raster in this repository, so reusing it would violate the user's uniqueness requirement.

The user-provided `0.3195` and `0.4413` leaderboard snapshots conflict with one another and have not been verified from the live organizer page in this sandbox. Neither is a valid comparison target until a dated organizer page/receipt is captured. A new score cannot be predicted from these numbers alone.

## Pre-implementation research ideas (not authorized experiments)

The items below are a screening shortlist only. They are not assigned to an experiment lane, not implemented, not tested, and not predictions of score improvement. Repository searches found no obvious matching module name for these exact transforms, but keyword absence is not proof of novelty. No numeric DTI gains are forecast.

| Rank | Hypothesis and layers | Signature and off-catalogue rationale | Named mimic / confound | Expected DTI potential (qualitative only) | Difference from current modules; cost and data status |
|---|---|---|---|---|---|
| 1 | **LiDAR channel-network deflection and catchment asymmetry** — USGS 3DEP bare-earth DEM (1 m-derived products) with existing GeoDAWN gravity/magnetic and MT/basement grids for structural corroboration. | Extract channel centerlines and compare upstream/downstream azimuth, local drainage-area imbalance, and cross-valley profile curvature. A persistent, cross-catchment deflection co-located with a subsurface structural axis may indicate a blind fault even without a preserved scarp. | Lithologic boundary, fan-lobe avulsion, road/ditch diversion, or differential erosion. | **Highest relative potential of this shortlist; unmeasured.** | Distinct from the current LiDAR antislope/channel-bank veto and drainage-knickpoint features: targets network planform/area deflection, not a local scarp or knickpoint. **Medium-high cost.** Source: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program); its complete cached stack is not present here. Restore and verify exact tiles/coverage before viability. |
| 2 | **Landsat seasonal thermal persistence across blind structures** — USGS Landsat Collection 2 Level-2 surface temperature time series plus existing magnetic/MT structure. | Multi-season robust thermal residual and cross-structure gradient persistence; a persistent linear anomaly may reflect deep fluid circulation rather than a one-date surface-temperature contrast. | Elevation/aspect, albedo, irrigated agriculture, land-cover change, wildfire scars, and emissivity errors. | **Moderate potential; unmeasured and highly confounded.** | The present catalog uses regional potential fields and geothermal proxies, not a multi-year Landsat thermal time-series transform. **High cost** (acquisition, QA, cloud/seasonal normalization, alignment); source: [USGS Landsat Collection 2](https://www.usgs.gov/landsat-missions/landsat-collection-2). No collection was fetched or verified in this restricted session; **blocked pending acquisition and coverage audit**. |
| 3 | **Focal-mechanism stress-consistency corridors** — USGS ComCat focal mechanisms / moment tensors, where available, with existing geodetic strain and subsurface structure. | Compare nodal-plane uncertainty and inferred slip orientation with local stress/strain and lineament strike; coherent structures may reveal blind active fault systems absent from surface-fault maps. | Sparse event coverage, aftershock sequences, anthropogenic/extraction seismicity, and mechanism ambiguity. | **Low-to-moderate potential; unmeasured; likely limited by coverage.** | Existing seismic modules use event density/declustering; this candidate targets mechanism orientation and uncertainty rather than counts. **High cost** because catalog density and depth may be inadequate at the 100 m grid scale. Source: [USGS ComCat](https://earthquake.usgs.gov/data/comcat/). Official API reachability and mechanism coverage could not be checked here; therefore **not viable until checked**. |
| 4 | **Fault-controlled hydrograph transfer function** — USGS NWIS daily streamflow and groundwater levels, paired with elevation, basin boundaries, and existing basement/MT structure. | Test for persistent cross-structure lags, attenuation, and baseflow discontinuities across inferred barriers/conduits; a hydraulic contrast could flag buried fault zones that have little surface expression. | Pumping, irrigation returns, dams, channel regulation, seasonal snowmelt, and aquifer/lithology boundaries. | **Low-to-moderate potential; unmeasured.** | Differs from existing static spring/temperature and the already-proposed static groundwater-head-step idea (H-92G4) by using temporal response/covariance; repo-wide novelty is therefore **not established**. **High data-engineering cost.** Source: [USGS NWIS](https://waterdata.usgs.gov/nwis); access/coverage not checked, so blocked and not viable yet. |

No one item is promoted as the next lane: the user-supplied single-lane paragraph is missing, the pre-placement witness rejects nonempty candidates under the literal rule, and no full data/registry cache was independently restored in this checkout. The explicit stop takes precedence over the request to produce a TIFF. These ideas must not be treated as justification for a weekly slot.

## Three-pass repository review

### Pass 1 — inspect and verify

- Read the current status, charter, standing prompt, session prompt, previous review, site summaries, and submission records.
- Installed the pinned `requirements.txt` dependencies in ignored `.venv/`.
- **PASS:** `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` validated **132** served rasters.
- **PASS:** `.venv/bin/python -m pytest tests -q` → **839 passed, 19 skipped** after integrating the concurrent main-branch audit additions (171 warnings; 85.70 seconds).
- **PASS:** `gems manifest` and `gems parent` confirmed the tracked inputs and R0 parent (`h33-h33-2-b2`, 37,654 dots); those checks do not rerun model training or the holdout.
- **PASS:** `.venv/bin/python scripts/review_project.py --fetch-witness --output .cache/review_20261030.json` fetched and hash-validated the pinned GitHub witness; preflight found `5,167,373 / 5,167,373` footprint cells positive and confirmed the literal stop. Its complete receipt is in ignored `.cache/` and is not a tracked deliverable.

### Pass 2 — challenge assumptions and look for stale/broken artifacts

- **Finding / site check inconsistency:** `scripts/render_focus9_page.py --check` exits 2 with `current research status disagrees with the review`: the focus-nine page generator compares the active RIESZ readiness record against an October 26 historical audit of the VARIO artifact. The mismatch is real and fail-closed; I did not overwrite historical evidence or regenerate the page from stale inputs.
- **Finding / banner check stale:** `scripts/render_review_banner.py --check` exits 2 with `missing or duplicate authoritative status marker`. This is a stale generated-page contract. The standard `check_site.py` and all tests still pass, so they do not cover these direct renderer checks.
- **Freshness limitation:** the focus-site inventory is pinned to October 26 commits and does not represent a verified current feed as of this review. The competition leaderboard, submission page, weekly quota, and current site files were not authenticated here; this environment permits outbound access to GitHub but not the DrivenData, DOE/NLR, USGS, or GDR hosts.
- **Score estimate limitation:** the exact focus-site predictions have no reliable calibrated prospective score estimate. The owner-reported figures remain `CLAIM`; do not relabel the historical leaderboard model's `MODEL` output as a score.
- **Competition input limitation:** only the bridge/example rasters and parent rasters are tracked in `data/`; the full feature stack is not in this checkout. The shared evaluator and writer exist, but a fresh full-stack holdout cannot be independently reproduced here.

### Pass 3 — reconcile against the request and define the next safe steps

- The table includes every requested focus site, a pinned research-file link, the best score claim from the supplied site list, a non-estimate where evidence is inadequate, and an explicit uniqueness/submit decision.
- Added a prominent link to this review at the landing page's current-status banner through the active safe renderer; regenerated the pages and verified both `docs/index.html` and the root landing page point to this review.
- The `0.2778` analysis distinguishes plausible metric behavior from causal proof and from an organizer receipt.
- No candidate TIFF was created; this is required by the literal duplicate stop and does **not** satisfy the user's desire for a new unique download. There is no valid way to label a newly created TIFF “OK TO SUBMIT” under the current gate.
- No experiment slot or competition slot was used. The analysis shortlist is not an experiment authorization.
- The older root/home pages still contain historical “OK TO DOWNLOAD” references; those are for research and are not clearance. Prefer the active [`readiness.json`](downloads/readiness.json) and [`SUBMISSION_READY.md`](../SUBMISSION_READY.md).

## Ordered next steps

1. Resolve the universal dense/binary witness interpretation **as a policy rule**, rather than bypassing it with a narrower uniqueness metric. Update the shared gate once, with tests and a documented rule change; until then keep the stop.
2. Supply an explicit single geological method paragraph/lane and reset/authorize an experiment budget only through the project's selector process. The next lane should have three preregistered experiments maximum and no slot spent before a holdout win.
3. Restore full, provenance-pinned competition features and the complete public registry; record hashes, CRS, transform, nodata/sentinel behavior, coverage, licensing, and source timestamps.
4. Only after the uniqueness stop is resolved: run feature-alone leakage canaries, then shared fold-visible whole-segment buffered hide-and-recover via `vendor/gems57/evaluate_holdout.py`/the shared wrapper. Compare the paired 95% CI to the current same-evaluator best before any candidate TIFF is written.
5. Repair the stale focus-nine renderer and status/banner contract from a single active source of truth; re-run its direct `--check`, `check_site.py`, all tests, and full `review_project.py` before publication.
6. Fetch the current organizer rules/leaderboard/weekly cap through an authorized path and record source URL, timestamp, response hash, and a genuine receipt. Until then, no live status or organizer score is claimed.

## Run card — this review

See [`evidence/review_20261030_run_card.json`](../evidence/review_20261030_run_card.json) for the machine-readable record. Summary: hypothesis not experimentally tested; no raster SHA-256; no candidate validator output; no organizer-confirmed score; verdict `negative`.

## Official/manual-review sources

These canonical sources are stored in the project charter and focus-site audit. They were **not all live-verified in this session**. The GitHub-hosted pinned TIFF references above were derived from the local inventory; official competition and data-site access remains a blocker.

- [DrivenData competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData data tab (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [DOE GDR INGENIOUS submission](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
