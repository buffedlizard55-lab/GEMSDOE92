# GEMSDOE92 repository review — 2026-10-30

## Executive decision

**DO NOT SUBMIT any file in this checkout.** The review produced no new candidate TIFF, no holdout run, and no selection of a competition slot. The requested *single method paragraph* is not present as an unambiguous lane assignment, the previous lane records say the three-experiment budget was exhausted, and the binding literal registry-overlap rule still rejects every nonempty in-footprint prediction because the pinned witness is positive throughout the footprint. The repository's shared readiness feed likewise says `submission_eligible=false`.

The nine-site summary is available at [Executive summary: focus sites](executive-summary-nine-sites-20261030.html). It identifies each highest supplied owner claim, the historical research TIFF, estimated leaderboard score availability, and the uniqueness outcome. The only defensible answer for an exact-file leaderboard **estimate** is “not available”: historical owner claims are not organizer receipts, and HOLDOUT-DTI on catalogue faults is not a calibrated forecast of hidden geothermal faults.

## Three-pass review

### Pass 1 — inventory and reproduce

- Read `README.md`, `SESSION_PROMPT.md`, `docs/PROJECT_CHARTER.md`, `docs/NEXT_STEPS.md`, the upstream same-day `docs/REVIEW_20261030_SESSION.md`, the standing protocol/review documents, current readiness JSON, and the focus-nine evidence bundle.
- Inspected `gems/`, `scripts/`, `vendor/gems57/`, `tests/`, `data/`, `registry/`, `docs/downloads/`, and the site-generation/checking path.
- Installed the pinned `requirements.txt` into ignored `.venv/`; no dependency or application code was changed.
- `.venv/bin/python -m pytest tests -q`: **842 passed, 19 skipped**.
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`: **PASS**, 132 served raster files format-gated.
- `.venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data`: **RESULT OK** for the checked-in pinned bridge files.
- `.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data`: **PARENT VERIFIED**, `h33-h33-2-b2`, SHA-256 `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`.

The automated checks establish repository regression, served-file formatting, and the local parent recipe only. They do not establish data rights, hidden-label performance, full registry uniqueness, organizer acceptance, or that the live site/leaderboard is current.

### Pass 2 — challenge assumptions and identify blockers

1. **No TIFF was generated.** The full feature stack (`.cache/gems_inputs/training_features.tif`) and full current registry snapshot are absent from this checkout. `data/bridge/` contains a limited example/parent set, not the full feature stack required by the prescribed holdout and candidate writer. The older audit records explicitly mark redistribution provenance for mirrored competition rasters as unchecked.
2. **No new experiment was authorized or run.** The message refers to a single method paragraph but does not identify a single standalone method lane. Existing dated records also state that the prior lane consumed its three-experiment budget. Neither requirement permits choosing a fresh lane by inference.
3. **Uniqueness STOP remains binding.** The repository's documented literal reading of the 70% 3-pixel condition encounters a full-footprint probability witness. A matched-budget or sparse-only view is not a waiver. This review did not download or rescan the external registry, so it does not claim the archived inventory is current.
4. **No exact leaderboard estimate is supportable.** The nine supplied values are owner `CLAIM`s. The repository has stored `HOLDOUT-DTI` diagnostics, but those measure recovery of withheld known-catalogue segments under the local evaluator; they are not estimates of an organizer's hidden-label score. `0.2778`, `0.3195`, `0.4413`, and the separate `0.2784` value are not organizer-confirmed in this checkout.
5. **Status/website freshness is not implied by tests.** The project has pinned snapshots and a static GitHub Pages site, not a verified live DrivenData feed. The host allowlist permits GitHub and package registries, not DrivenData, USGS, NASA/LP DAAC, DOE GDR, or the rules-PDF host; their current page contents and access were not live-checked in this review.
6. **Submission-format ambiguity:** local validation enforces one-band float32, grid/CRS/transform, finite in-footprint values in `[0,1]`, and the project's zero-outside convention. That local PASS is useful protection against the reported range error but does not prove the organizer portal's exact current nodata interpretation.
7. **Primary-pointer mismatch (flagged):** the evidence-bound Pages renderer and status JSON still point to RIESZ-LBM2 while the README and `SUBMISSION_READY.md` foreground other later research candidates. The upstream same-day review documents this discrepancy. This report adds an up-to-date focus-nine link but does not silently select or promote a candidate; the current-primary mismatch remains unresolved.

### Pass 3 — verify report against original request and scope

- The linked nine-site table contains the requested `GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, and `36` rows; each file is labeled **research reference only / do not submit**.
- Per-site scores are clearly labeled **CLAIM**, historical HOLDOUT-DTI values are separately labeled with evaluator/version, withheld-positive count, and CI, and no estimate is misrepresented as a score.
- Every selected historical peak has a failure against the archived nine-site pairwise/registry checks; it is not eligible as a *unique new submission*. A fresh comprehensive registry scan was not claimed.
- The review preserves the one-card JSON at the end, labels the current holdout as `NOT_RUN`, records no new raster hash, and records the validator/regression outcomes.
- No experiment exceeded the session budget; zero competition slots were used.

## Focus-site findings

The highest supplied claim among the nine is GEMSDOE32's `h33-h33-2-b2` at `0.2778` (owner claim, no receipt in this checkout). The report gives a plausible mechanism—sparse, spatially separated dots reduce redundant predicted mass under a distance-buffered metric—without claiming that this caused the claimed leaderboard value. GEMSDOE36's supplied `anderson-geothermal-pinn` result is a strict support superset of GEMSDOE32's dots in the archived audit, with extra dots and a lower owner-claimed score; this is suggestive, not a controlled causal experiment.

The original repo evidence reports exact clones and/or severe 3-pixel overlap among the nine peaks. For example, the archived D28 predictions at GEMSDOE25 and GEMSDOE30 are identical; GEMSDOE27's top-gap raster is duplicated in other repositories; GEMSDOE32's parent has exact clones; and GEMSDOE36 contains the GEMSDOE32 support. Therefore **none of these files is a unique new TIFF**. Their download links are shown only to support forensic review, not to invite re-submission.

`HOLDOUT-DTI` historical diagnostic values are included as a warning, not a forecast. In particular, a low static-catalogue HOLDOUT-DTI alongside a high owner CLAIM is evidence that this local proxy is not a dependable exact-file leaderboard estimator for these artifacts. Do not fit or extrapolate a leaderboard score from these nine rows.

## Conditional future hypothesis shortlist (not authorized experiments)

The request asks for fresh hypotheses before implementation. The following are research leads, not selected methods or validated predictions. A code scan found no exact implementation of these specific operators in `gems/`; adjacent ideas have appeared in historical backlog documents, so “unimplemented” here does not mean “never previously discussed.” Every lead is blocked pending an assigned method paragraph, a refreshed source/rights audit, a restored feature cache/registry, and a new explicitly authorized budget.

| Rank (qualitative) | Hypothesis | Specific layers / physical signature | Why it may find uncatalogued faults; distinction from existing code | Non-fault mimic | Relative expected DTI improvement | Data availability and implementation cost |
|---|---|---|---|---|---|
| 1 | **Dextral channel-offset persistence** | Native USGS 3DEP DEM and NHD flowlines; measure multi-channel lateral displacement, same-sense offset coherence and along-strike persistence, rather than vertical knickpoint or scarp strength. | Secondary strike-slip strands may be submerged in alluvial fans and omitted from regional fault maps; the specific observable is planform channel offset, unlike existing vertical knick/knickzone features. | Lithologic contacts, irrigation canals, road culverts, and inherited drainage capture. | **Potentially moderate; confidence low and unquantified.** Directly targets a distinct fault motion mode, but only where preserved channels cross candidate strands. | Official sources: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [USGS National Hydrography Dataset](https://www.usgs.gov/national-hydrography/national-hydrography-dataset). **Not staged here; official hosts are not reachable under this sandbox policy.** Cost medium/high (DEM/flowline extraction + segment-level uncertainty). |
| 2 | **ASTER hydrothermal-mineral assemblage anomaly** | NASA ASTER SWIR/TIR reflectance products; robustly compare silica/clay/carbonate alteration indicators to local lithologic background and separate coherent alteration corridors from single-pixel spectral outliers. | Fossil or active hydrothermal alteration may mark fluid pathways whose short splays and discharge-zone structures are not mapped as faults; spectral assemblage differs from the repo's potential-field, topographic, and radiometric operators. | Unaltered volcanic lithology, desert varnish, grain-size/illumination effects, and vegetation/moisture. | **Potentially moderate-to-high, but very low confidence without coverage tests.** Geothermal alteration is direct but can be dominated by bedrock lithology and scene effects. | Official source: [NASA LP DAAC ASTER products](https://lpdaac.usgs.gov/products/). **No imagery or coverage cache is present; official endpoint is outside the allowed hosts.** Cost high (scene selection, atmospheric/terrain correction, mosaicking, coverage bias). |
| 3 | **Pre-development groundwater-head barrier** | USGS NWIS groundwater levels, well construction/time metadata, screened intervals, DEM and basin-depth context; infer persistent cross-strike hydraulic-head steps with pumping-season and aquifer-unit controls. | Sealed or clay-smeared concealed faults can compartmentalize aquifers under flat basin fill without an exposed scarp; this tests measured hydraulic head rather than thermal plume proxies. | Pumping cones, perched aquifers, stratigraphic facies changes, and inconsistent well datums. | **Potentially moderate, low confidence.** Geologic mechanism is plausible but sparse wells and aquifer heterogeneity may prevent detection. | Official source: [USGS Water Data / NWIS](https://waterdata.usgs.gov/nwis). **Not staged; current access/coverage not verified from this network-restricted run.** Cost medium/high; well density and metadata may make the hypothesis non-identifiable. |
| 4 | **Seasonal InSAR deformation-phase discontinuity** | NASA/JPL OPERA Sentinel-1 displacement time series; across-strike change in annual amplitude/phase plus secular velocity, tested only where track geometry/coherence support comparison. | Aseismic fault-core permeability contrasts may create narrow deformation/hydraulic boundaries without mapped surface rupture; temporal phase is distinct from the repo's static geodetic strain grids. | Groundwater pumping, subsidence, decorrelation, vegetation, and orbit/processing seams. | **Potentially moderate, low confidence.** Temporal observability could be valuable where coherent multi-season coverage exists; broad coverage/processing noise may overwhelm it. | Official source: [NASA/JPL OPERA products](https://www.jpl.nasa.gov/go/opera/products/disp-product-suite/). **Not staged and not obtainable from the sandbox allowlist.** Cost high (time-series, track harmonization, pumping controls). |

No numerical expected score is attached to these leads. Their relative ranking is a qualitative combination of potential signal specificity and cost, not a `MODEL` or leaderboard projection. The first actual experiment must be pre-registered in the assigned lane and run through the shared, fold-rebuilt, segment-buffered hide-and-recover evaluator with feature-alone canaries. If source inputs cannot be obtained from an official free endpoint, do not label that hypothesis viable.

## Official review links

- [DrivenData problem statement](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — manual review link; not live-verified here.
- [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — login may be required; not accessed here.
- [DrivenData official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — link recorded; not live-verified here.
- [DrivenData reference solution on GitHub](https://github.com/drivendataorg/gems-prize-reference-solution) — source repository; this review used the local pinned shared evaluator/writer code.
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391) — source links for the existing workflow; not live-verified here.

## Remaining work, in decision order

1. Obtain the exact, permitted official competition data and document data-use/redistribution rights; restore and hash-check the complete feature stack and current registry.
2. Resolve the missing single-lane paragraph and the literal full-footprint-witness interpretation without silently changing thresholds or semantics.
3. Reconcile the three-experiment budget with the session owner before any experiment; no weekly submission slot is involved in local work.
4. Only then pre-register the lane hypothesis, use the shared evaluator and writer, test each feature alone, compare paired HOLDOUT-DTI against the same-evaluator best control, and check uniqueness both before placement and on final dots.
5. Validate the exact final bytes against the portal's current official template/rules. Keep any selector decision separate, use the weekly cap shown on the submission page, and record an actual organizer receipt if one is ever obtained.

## Final run card

```json
{
  "hypothesis": "No new geological hypothesis was selected for an experiment because the prompt does not identify its required single method paragraph; four conditional research leads are documented above.",
  "mechanism": "Repository and evidence review plus regression/format checks only; no candidate raster was generated and no holdout was run.",
  "named_non_fault_process_that_could_mimic_it": "Potential future geomorphic signals can be mimicked by lithologic contacts, canals, pumping, perched aquifers, facies changes, vegetation, and processing seams; no new raster was tested.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "NOT_RUN in this review; shared evaluator is vendor/gems57/evaluate_holdout.py (gems57-pooled-hide-v2)",
    "withheld_positive_pixels": null,
    "ci95": null,
    "note": "No new score or projection. Archived historic values are not freshly reproduced in this review."
  },
  "correlation_overlap_vs_registry": {
    "measurement": "NOT_RUN in this review",
    "pre_placement_surface": null,
    "final_dots": null,
    "archived_protocol_status": "Literal full-footprint witness remains a STOP for nonempty candidates; archived focus-site artifacts also fail pairwise/full-registry checks.",
    "verdict": "negative"
  },
  "raster_sha256": null,
  "validator_output": {
    "new_candidate": "NOT_GENERATED",
    "no_nan_inside_footprint": "NOT_RUN for a new candidate",
    "values_in_0_1": "NOT_RUN for a new candidate",
    "crs_shape_transform_match": "NOT_RUN for a new candidate",
    "served_raster_gate": "PASS; 132 served rasters checked by scripts/check_site.py",
    "manifest": "PASS for checked-in pinned bridge files",
    "parent": "PASS; h33-h33-2-b2 sha256 c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "test_suite": "842 passed, 19 skipped"
  },
  "submission_name": null,
  "submission_note": "No new TIFF generated; no existing research TIFF is cleared to submit.",
  "experiments_run": 0,
  "weekly_slots_used": 0,
  "verdict": "negative"
}
```
