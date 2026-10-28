# Repository review and decision — 2026-10-28

## Executive decision

**DO NOT SUBMIT the current RIESZ-LOCKED GeoTIFF.** It is available as a **format-validated research download only**. No new TIFF was generated, no additional experiment was run, and no weekly submission slot was selected in this review.

The prior generated homepage called the file “OK TO SUBMIT” even though its own evidence recorded `catalogue_holdout_beats_r0_recipe: false`, pre-placement surface overlap `1.0`, and a literal full-support registry duplicate. That is a material status contradiction. We corrected the card verdict, audit receipt, current status feeds, site generator, rendered GitHub Pages pages, README current section, and session-start note. The underlying TIFF bytes and its measured values were not altered.

**Download status:** OK TO DOWNLOAD FOR RESEARCH.
**Submission status:** **⛔ DO NOT SUBMIT.**
**Artifact:** [`gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif`](downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif)
**SHA-256:** `d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a`
**Submission selector:** none; this is not a real-slot recommendation.

## Decision gates and evidence class

| Protocol condition | Recorded result | Decision |
|---|---|---|
| Rule 1, pre-placement surface: stop if overlap >70% or `|rho| >0.90` | Stored run-card uniqueness record has pre-placement surface overlap `1.000` against the dense/full-support witness; surface `|rho| = 0.550328`. | **FAIL — stop before placement.** The archived experiment continued to placement, which was inconsistent with the stated protocol. |
| Rule 1, final dots: same overlap/correlation rule | Literal full-support witness overlap is `1.000`; narrower sparse-dot PI-1 inventory maximum is `0.6556` across 2,162 indexed raster hashes and final max `|rho| = 0.144898`. | **FAIL under the specified conservative literal stop.** The sparse-only interpretation is disclosed, not used to waive the stop. The question of whether a continuous full-support raster is a “dot raster” remains a policy ambiguity. |
| Rule 2, shared spatial holdout vs control | Archived `HOLDOUT-DTI`, `gems57-pooled-hide-v2`, 22,663 withheld positive pixels: E3 `0.037987 [0.031011, 0.044656]`; R0 recipe `0.097750 [0.085900, 0.110766]`; paired difference `-0.059763 [-0.072005, -0.046653]`. | **FAIL — candidate is significantly below R0 in the recorded paired interval.** |
| Rule 3, score labels | `0.321602` is a fitted `MODEL` projection; `0.2778` and the prompt's `0.3195` / `0.4413` are `CLAIM` / user-provided values in the supplied materials. No organizer receipt is in this repository. | No projection is described as a score. |
| Rule 4, feature-alone canaries | Archived record reports RIESZ-LOCKED max symmetric AUC `0.65694` over 16 features and overall maximum `0.75320`, under `0.90`. | Recorded PASS, not a substitute for Rule 1 or Rule 2. |
| Rule 6, budget | Historical RIESZ-LOCKED work used E1–E3, i.e. 3/3 experiments. | **Budget exhausted.** No experiment was run here. |
| Local format | `scripts/check_site.py` re-read 126 served TIFFs and passed the shared format/range gates (2026-10-28). Current file: one-band float32, EPSG:32611, 3292×3730, exact sample transform, values in `[0,1]`, no NaN/Inf, zeros outside footprint. | Format-valid research file only; local validation is not organizer acceptance. |

The archived holdout was **not independently reproduced in this review**. The full cached feature stack named in the holdout evidence is absent from this checkout (`data/bridge` contains sample/catalogue rasters and historical examples, not the full model feature cache). The sandbox's allowed outbound hosts do not include DrivenData, Dropbox, USGS, DOE GDR, or the other official data hosts referenced here. Thus external source availability, current leaderboard values, provenance of owner mirrors, and the organizer receipt status were not live-verified. The session prompt is explicit that the current public status page is not a live score feed.

## Focus-site executive comparison

Inventory source: `evidence/focus9_sources_20261028.json`, `evidence/focus9_uniqueness_20261028.json`, `evidence/lbm_v1_model.json`. Scores remain owner-reported `CLAIM`s; `MODEL (LOGO)` is a regression projection and not a leaderboard score. The `unique` test is against the pinned public 8-owner raster inventory as recorded by the prior run. The best files listed below are research references, **not eligible submissions**.

| Site | Highest listed submission file (commit-pinned source/download in [site table](nine-sites.html)) | `CLAIM` | `MODEL (LOGO)` | Registry / duplication finding | Recommendation |
|---|---|---:|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | 0.25769 | `unique_pi1=false`; recorded 1.000 worst overlap; byte copies in GEMSDOE mirrors | Study only; do not re-upload |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | 0.26702 | `unique_pi1=false`; 1.000 worst overlap; exact byte copies include GEMSDOE24/30/32 mirrors | Study only; do not re-upload |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | 0.25520 | `unique_pi1=false`; exact copies include GEMSDOE28/63/67 | Study only; do not re-upload |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | 0.27247 | `unique_pi1=false`; exact copies include GEMSDOE48/86 and KANLERGEMSDOE2 | Study only; do not re-upload |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | 0.26702 | `unique_pi1=false`; exact copies are listed in fleet inventory | Study only; do not re-upload |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | 0.27403 | `unique_pi1=false`; exact copy in KANLERGEMSDOE2 | Study only; do not re-upload |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778** | 0.27728 | `unique_pi1=false`; byte-identical copies in multiple repositories; the site inventory records 1.000 worst overlap | Highest `CLAIM` of these nine; study only |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | 0.27103 | `unique_pi1=false`; exact copies include GEMSDOE48-family mirrors | Study only; do not re-upload |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | 0.27471 | `unique_pi1=false`; exact copies include GEMSDOE63/67 and other mirrors | Study only; do not re-upload |

The generated [nine-site page](nine-sites.html) includes the commit-pinned download links, score claims, fitted model estimates, per-site submission inventory (including the supplied latest lower-scoring entries), and clone references. The pin is a historical snapshot, not a live freshness check. A current leaderboard value cannot be estimated from this table with organizer certainty.

## Why the GEMSDOE32 entry may have scored 0.2778

The repository's historical lineage analysis attributes the high entry to a sparse, H19-5-derived trace pattern with distance-based pruning from mapped faults. Such pruning is plausible under a distance-tolerant metric: mapped traces are masked/unrewarded, while predictions away from them can retain useful support and unnecessary false-positive weight is reduced. The shared metric is asymmetric and spatially tolerant, so reducing redundant/background predictions can improve a score without discovering new geology. This is a mechanistic hypothesis supported by the stored byte/lineage audit, **not a causal demonstration**: hidden positive labels and an organizer score receipt are unavailable locally. The user-supplied `0.2778`, `0.3195`, and `0.4413` values are not independently confirmed in this review.

The tested RIESZ-LOCKED E3 hybrid does **not** establish a route to beating the `0.2778` `CLAIM`: its `HOLDOUT-DTI` is `0.037987`, and that metric measures hide-and-recover performance on known catalogue faults, not leaderboard discovery of missing faults. Its `0.321602 MODEL` projection is not a substitute or a prediction certified by an organizer.

## Hypothesis/lane request and data-access decision

The previous session pre-registered H-92A through H-92E. H-92A–D (Riesz/monogenic steps and piedmont scarps; Wijns/biharmonic basement contacts; locked strain deficit with fluvial knickzones; geothermal enthalpy-disequilibrium/Péclet outflow) were included in the prior three-experiment sequence. The previous H-92E proposal involved Curie spectral depth / future LiDAR, but the repository already has Curie-related code, so it cannot be presented as a novel untried repo method without a fresh audit. Those are **historical candidates**, not a new hypothesis shortlist.

The present prompt says “your lane is the single method paragraph below” but does not provide a distinct method paragraph. Picking 3–5 new hypotheses anyway would violate the single-lane restriction. The three-experiment cap is also already used. Accordingly, no new hypotheses are ranked as viable, no external-data-dependent idea is claimed obtainable, and nothing is implemented. USGS 3DEP LiDAR is an official catalog reference ([USGS 3DEP catalog](https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e)); it was **not obtained or live checked for coverage/access** in this sandbox, so it is only a future data-access lead, not a validated candidate.

## Three-pass review

### Pass 1 — implementation and first verification
- Read the active review, run card, holdout JSON, TIFF, current status feeds, page renderer, tests, and repository state.
- Found a status safety defect: the page promoted a candidate despite a false required R0 holdout gate and a literal pre-placement overlap stop.
- Corrected the authoritative run-card verdict/eligibility and per-file audit decision without changing raster bytes. Added a machine-readable `promotion_review` trace.
- Updated `scripts/render_site_v3.py` so a promotion attempt fails closed when literal registry or holdout gates fail; regenerated `docs/index.html`, `docs/how-to-submit.html`, `docs/nine-sites.html`, root redirect, and status feeds. Changed portal instructions to state that the current file must not be uploaded.
- Updated the README and session prompt to place the corrected decision first; marked the prior “submit lbmc1” next steps as historical/superseded.

### Pass 2 — bug, assumption, and edge-case review
- Kept the narrower sparse overlap numbers visible but prevented them from overriding the required literal overlap gate.
- Re-labelled `0.3216` as `MODEL projection`; reported the holdout/control and paired interval side-by-side; explicitly disclosed no organizer receipt and no independent holdout rerun.
- Removed the overclaim that a locally valid TIFF “cannot trigger” portal rejection; local format validation is not organizer acceptance.
- Replaced stale “OK TO SUBMIT” labels with unmistakable **DO NOT SUBMIT** in the current page and machine-readable status feeds.
- Disclosed that historical site inventory and owner-reported values are pinned/stale rather than a live feed. External official links are provided for review, but not described as freshly verified.

### Pass 3 — full request cross-check and validation
- Confirmed all nine focus sites are represented with a named highest submission, `CLAIM`, `MODEL (LOGO)`, and uniqueness/clone finding in the generated page; all nine focus-site records have `unique_pi1=false` and a recorded 1.000 worst overlap in the pinned inventory.
- Confirmed the candidate has `verdict=negative`, `submission_eligible=false`, `ok_to_download=true`, and the current page is generated from the same corrected JSON evidence.
- Re-ran `scripts/check_site.py`: **PASS (126 served raster(s) gated)**; it checked the sample grid, served TIFFs, hashes, local format constraints, and renderer/status consistency. Installed dependencies remain in ignored `.venv`; no dependency files changed.
- After this branch's first review, `main` advanced with independent audits. Integration retains its pinned full-support witness receipt (`evidence/audit_b6aa_20261028.json`) and separate Riesz final-dot check (`evidence/review_47314b7f_overlap.json`): the witness is positive on every template-footprint pixel and final-dot overlap is 1.000, respectively. These are rejection-only, single-witness findings—not proof of complete registry coverage, geological identity, or a fresh pre-placement Riesz calculation. The independent review reports final-footprint rank correlation 0.013638. A subsequent measurement (`docs/downloads/review_20261028_overlap.json`) reports literal overlap 1.000 but top-K overlap 0.00698 against that witness. This demonstrates that representation choice matters; top-K is not policy authorization or full-registry uniqueness. Later, merged PR #166 added a separate 30,000-dot `damagezone-close-dots` TIFF (`07d5f5d5…d3bbc`). This review does not adopt it: the repository says full-registry uniqueness is pending, its local surrogate `0.05164` is compared to the R0 raster `0.00473` rather than clearing the recorded R0 recipe `0.09775`, and the independent review documents that `labels.tif` is byte-identical to `existing_faults.tif`. It is therefore not evidence of hidden-fault generalization or submission eligibility. The current site discloses the file as an unselected research artifact only. See `docs/REVIEW_20261028_B6AA.md`, `docs/review-47314b7f.html`, `docs/REVIEW_20261028_SESSION.md`, and `docs/HYPOTHESES_UNTRYED.md`.
- Full test suite before integration: **775 passed, 19 skipped, 167 warnings**. After integrating `main`, a test initially failed because the generated guide/root page omitted the candidate identity; the fail-closed renderer now includes the exact research-only filename and SHA-256 on both. After merging the independent overlap receipt and its regression tests, final integrated suite: **787 passed, 19 skipped, 171 warnings**. `scripts/check_site.py`: **PASS (126 served rasters gated)**. The historical holdout remains unreproduced: the full feature cache is absent and the experiment budget is exhausted. Do not describe its stored values as freshly reproduced.

## Remaining limitations / next-session gates

1. Supply/assign the missing method-lane paragraph and explicitly resolve the full-support registry-witness interpretation; until then the conservative overlap stop applies.
2. Restore the complete feature stack and validate source provenance, hashes, nodata sentinels, reference grid, and complete registry inventory.
3. For any future authorized experiment, use the shared feature stack, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`; derive all catalogue features only from visible faults per fold, mask visible faults pixel-exactly, run every feature-alone canary, and check registry rank correlation/overlap on the surface before placement and on the final dots.
4. Require a candidate to beat the same-evaluator holdout best with a positive paired 95% CI before a separate human/selector slot step. A MODEL or owner-site CLAIM is not a result receipt.
5. Check official competition rules, weekly quota, and submission-page requirements live before any later upload. No current artifact qualifies.

## Official references for review

These links are the repository's official-domain references; due the sandbox host allowlist, they were **not fetched live in this review**:

- [DrivenData problem description and file format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DOE/NREL official competition rules (PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN magnetic/radiometric dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP data catalog](https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e)

## Final JSON run card

```json
{
  "hypothesis": "The archived RIESZ-LOCKED/LBM-v2 hybrid targets unmapped Basin-and-Range faults using Riesz phase steps, piedmont scarps, structural contacts, and geothermal outflow signals; this review does not assign a new method lane.",
  "mechanism": "Recorded E3 combines OOF geophysical prospectivity with a fitted LBM-v2 density model and 300 m DTI-oriented point placement. Its observed holdout failed the required R0 comparison, and the recorded pre-placement/final registry overlap triggers the conservative stop.",
  "named_non_fault_process_that_could_mimic_it": "Incised volcanic canyon or mesa rims and fan-head dissection gullies can produce sharp topographic edges; the archive also names paleoshorelines, lithologic knickpoints, plutonic contacts, and playa brines as mimics.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positive_pixels": 22663,
    "alpha": 0.2,
    "beta": 0.8,
    "triangular_kernel_radius_m": 300,
    "candidate_e3": 0.0379871472,
    "candidate_ci95": [0.0310108549, 0.0446562538],
    "r0_recipe_control": 0.0977501041,
    "r0_ci95": [0.0859004763, 0.1107664991],
    "paired_delta_candidate_minus_r0": -0.0597629569,
    "paired_delta_ci95": [-0.0720045951, -0.0466533871],
    "reproduction_status": "Historical recorded receipt; not independently rerun in this review because full feature cache is absent."
  },
  "registry_correlation_overlap": {
    "registry_snapshot": "2,162 unique raster hashes across 8 GitHub owners, pinned 2026-10-28",
    "preplacement_surface_overlap": 1.0,
    "preplacement_surface_abs_rank_correlation": 0.550328,
    "final_literal_full_support_overlap": 1.0,
    "final_sparse_dot_field_worst_overlap": 0.6556,
    "final_abs_rank_correlation": 0.144898,
    "threshold_overlap": 0.70,
    "threshold_abs_rank_correlation": 0.90,
    "verdict": "negative; conservative literal registry stop fails"
  },
  "raster_sha256": "d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a",
  "validator_output": {
    "local_site_check": "PASS (126 served rasters gated; 2026-10-28)",
    "no_nan_inside_footprint": true,
    "no_nan_anywhere": true,
    "values_in_0_1": true,
    "crs": "EPSG:32611 (matches sample grid)",
    "shape": [3292, 3730],
    "transform_matches_sample": true,
    "single_band_float32": true,
    "zeros_outside_footprint": true,
    "organizer_acceptance": "not verified"
  },
  "submission_name": "gemsdoe92-rieszlbm2-50000d-79041788",
  "submission_note": "Riesz-Locked LBM-v2: 50000 binary dots; 128-claim density + q85 mimic filter + OOF Riesz/piedmont/Peclet; <=65.6% 8-owner fleet cap.",
  "submission_note_characters": 132,
  "verdict": "negative"
}
```
