# GEMSDOE92 — GEMS Prize evidence and research workspace

**Current disposition (2026-10-24): no GeoTIFF is cleared for submission under the literal registry-uniqueness rule.** A hash-verified public same-grid raster is positive at every legal output cell, so every nonempty candidate has forward dot overlap `1.0`, exceeding the `0.70` stop limit. This run selected a future depth-stratified USGS MT lane and stopped before feature construction or placement. No slot was used and no DrivenData upload occurred.

## Existing parallel-run artifacts — inspection only

These files were added to `main` by a separate parallel session; they are not outputs of the selected MT assessment and are not globally cleared by the current all-raster uniqueness rule.

- **TIPGAP FAR**: [`docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif`](docs/downloads/h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a-zeros.tif), SHA-256 `0ca8248acace558f5cf86b153134b8fd5cc2b7d5b343d0a36f000f9fbfe4758f`. Its local format preflight passed, and local comparisons reported parent overlap `0.6700` and Spearman `0.6690`; its run card says the accessible registry scan was incomplete. **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives) is `0.002723`, 95% CI `[0.002324, 0.003131]`, versus R0 `0.004006`, 95% CI `[0.003408, 0.004651]`: negative. The local result is not global uniqueness clearance; do not submit.
- **RELIEF p10**: an inspection artifact in `docs/downloads/`, separately marked negative. Its stored comparison has 99.3812% of candidate dots within 3 px of parent R0, above the 70% limit. Its historical `HOLDOUT-DTI` is `0.006045` (same evaluator, 22,663 withheld positives, 95% CI `[0.005187, 0.006927]`); this does not override its duplicate stop or constitute an organizer score.

The website labels the TIPGAP file as **inspection-only / DO NOT SUBMIT**. Format validity, a local parent comparison, and a public download do not establish global uniqueness, scientific benefit, or organizer acceptance. Do not copy either artifact into a new submission.

## Start every future session here

Read this `README.md` and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) first; then review [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), `IRREGULARITIES.md`, [`docs/review_passes_20261024.md`](docs/review_passes_20261024.md), [`docs/research_assessment_20261024.md`](docs/research_assessment_20261024.md), `SLOT_PLAN.md`, and `docs/SUBMIT.md`. Check current Git state, input provenance, registry scope, official sources, and all relevant run cards before changing files. Reconcile prior artifacts rather than treating a repository summary as current truth.

## Project brief

The GEMS Prize asks for a single-band 100 m GeoTIFF prediction of fault locations across the GeoDAWN study area. The local grid is 3,730 × 3,292, EPSG:32611, transform `(100, 0, 243350, 0, -100, 4508550)`. The official distance-weighted Tversky metric uses `alpha=0.2`, `beta=0.8`, and a 300 m triangular distance kernel. Public fault labels are incomplete; the scientific goal is credible detection of unmapped faults, not merely reproducing the known catalogue.

The pinned 19-band stack and other large inputs were restored into ignored `.cache/gems_inputs/` from hash-checked GitHub mirrors. Those mirrors are integrity-pinned but not organizer-authenticated. Per the project constraint, do not contact DrivenData or Dropbox to restore assets; GitHub-hosted mirrors are permitted. Do not add restored competition inputs to Git.

## Operating rules

- **One method lane per run.** Rank 3–5 untried geological hypotheses and document named layers, signatures, off-catalogue rationale, novelty limits, qualitative expected holdout benefit, costs, and non-fault mimics. Select one lane; do not silently switch or copy a prior raster.
- **Hard budget:** stop after three experiments or two hours, whichever comes first. Never spend a weekly slot in local development. Promotion is a separate selector decision.
- **Uniqueness before placement and again on final dots.** Use shared `vendor/gems57/uniqueness.py` and an auditable public-raster inventory. Compare surface rank correlation and forward dot overlap. Under the current literal rule, `Spearman |rho| > 0.90` or forward overlap `>0.70` against any registry raster blocks. Do not exempt dense/continuous rasters or change this scope silently. An incomplete inventory is not clearance.
- **Holdout protocol.** Reuse the shared cache, `vendor/gems57/holdout.py`, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`; hold out whole buffered fault segments, derive catalogue features only from visible faults, mask visible faults pixel-exactly, and evaluate pooled DTI with `alpha=0.2`, `beta=0.8`, and the 300 m triangular kernel. Include evaluator version, withheld-positive count, and paired spatial-cluster 95% CI. Test each feature alone as a leakage canary; AUC above 0.90 is leakage until explained.
- **Score labels:** every local evaluation is `HOLDOUT-DTI` with evaluator/version, withheld-positive count, and 95% CI. Use `ORGANIZER-CONFIRMED` only for a value copied from an actual submission receipt. Label leaderboard values as display observations and model outputs as projections, never scores.
- **Artifact contract:** only if all scientific, uniqueness, and format gates pass, create one easy-to-download single-band float32 GeoTIFF with finite `[0,1]` values and exact CRS/shape/transform. Reopen and validate it, record SHA-256, and use a short unique name plus a note no longer than 140 characters. **Do not upload it.** If the gate is universally blocked, do not create a zero-valued decoy or call an uncleared file unique.
- **Three reviews and provenance:** review evidence/claims, geology/holdout design, and registry/grid/package safety in three passes. Record irregularities and link verified official sources for manual review.
- **Final response:** include one JSON run card with the hypothesis/mechanism, named mimic, holdout result or explicit `NOT_RUN`, registry correlation/overlap, raster SHA-256, validator, submission name/note, and promote/negative verdict.

## Current evidence and stop condition

- Parent `h33-h33-2-b2`: 37,654 dots. Its reported `0.2778` is an owner **CLAIM**, not `ORGANIZER-CONFIRMED`; the local ledger contains no receipt. GEMSDOE32 labels its H33-2-B2 artifact **UNSCORED**. The official public leaderboard page observed on 2026-10-24 displayed `0.4413`, `0.3916`, and `0.3904` at ranks 1–3; those are display observations, not account receipts, and conflict with the supplied `0.3195` snapshot.
- The witness is `buffedlizard55-lab/17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`, SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`. It is positive on all 5,167,373 footprint cells. The legal domain after exact catalogue exclusion has 5,106,385 cells; uncovered count is zero. Thus every nonempty legal prediction has forward overlap `1.0` under the shared literal support rule. The proof is method-independent; candidate-specific Spearman was not run.
- The selected future lane is depth-stratified USGS MT conductance breaks. No candidate surface/dots were built for this lane; holdout DTI/CI, candidate SHA, validator, and submission name/note are `NOT_RUN`/null. See [`evidence/run_card_mt_registry_stop_20261024.json`](evidence/run_card_mt_registry_stop_20261024.json). The witness is cached only under ignored `.cache/public_gems_tifs/`.
- [`registry/public_gems_tif_inventory.json`](registry/public_gems_tif_inventory.json) is a metadata-only scan of 101 public owner repositories matching the documented GEMSDOE pattern. The complete 06:33:50 UTC snapshot plus one locally fetched current-main TIFF metadata supplement gives 2,509 TIFF paths, 1,999 candidate-like paths, and 1,306 unique candidate-like blobs. A full refresh at 06:44:48 UTC failed on GitHub API rate limiting; only this repository's new main-tree TIFF was supplemented, so other repositories may have changed. The inventory is not a decoded, byte-level comparison and cannot overturn the universal witness proof.
- Post-integration local tests: **83 passed**, with 12 Rasterio `PendingDeprecationWarning`s. `scripts/check_site.py` also passes 10 local format gates for the existing TIPGAP inspection file; that is not global uniqueness clearance, a fresh candidate validation, a holdout result, or organizer acceptance.

## Key files

- `docs/research_assessment_20261024.md` — score audit, ranked hypotheses, selected future lane, source links.
- `docs/review_passes_20261024.md` — three-pass review, current stop decision, reproduction commands.
- `evidence/run_card_mt_registry_stop_20261024.json` — this run's blocked H1 card; no candidate was produced.
- `evidence/registry_saturation_blocker.json` — hash/grid-verified universal-overlap certificate.
- `registry/public_gems_tif_inventory.json` — metadata-only public GitHub TIFF inventory.
- `scripts/scan_public_gems_tif_registry.py` — regenerate the inventory with authenticated `gh`.
- `scripts/check_registry_saturation.py` — fetches only the GitHub witness and reproduces the shared blocker certificate.
- `docs/index.html`, `docs/submit.html` — existing parallel artifact shown as inspection-only, not submission approval.
- `vendor/gems57/` — shared grid, holdout, uniqueness, writer, and validation logic; do not fork privately.
- `IRREGULARITIES.md` — decision-changing caveats and parallel-run reconciliations.

If a future user explicitly changes how full-support rasters participate in the dot-overlap gate, record that authorization first and rerun the complete inventory/correlation comparison before considering any lane. Until then, no nonempty download-ready candidate can honestly be called unique under the active protocol.
