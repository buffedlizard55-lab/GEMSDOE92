# GEMSDOE92 — GEMS Prize research workspace

**State as of 2026-10-24:** candidate generation is stopped by the literal public-raster uniqueness gate. No new candidate GeoTIFF was built, no weekly slot was used, and nothing was uploaded. Read the stop finding before proposing any submission.

## Start every future session here

Before running code or changing a file, read this `README.md` first, then review:

1. `IRREGULARITIES.md` — decision-changing data, score, and method caveats.
2. `docs/review_passes_20261024.md` — latest three-pass review and stop decision.
3. `docs/research_assessment_20261024.md` — ranked hypotheses and selected lane.
4. `SLOT_PLAN.md` and `docs/SUBMIT.md` — historical candidate slate, not authorization to submit.
5. `registry/session_manifest.json`, `registry/public_gems_tif_inventory.json`, and `evidence/run_card_20261024.json` — inputs, registry scope, and latest run status.
6. `ledger/submissions.csv`, `docs/mechanism_cards.md`, and the relevant evidence JSON before relying on any earlier build or score.

Re-check current public sources and Git state when a new session starts. Do not treat a prior session summary, a leaderboard display, a model projection, or a repository artifact as a submission receipt.

## Project brief

The GEMS Prize asks for a single-band, 100 m GeoTIFF prediction of fault locations across the GeoDAWN study area. The local grid contract is 3,730 × 3,292, EPSG:32611, transform `(100, 0, 243350, 0, -100, 4508550)`. The official distance-weighted Tversky metric uses `alpha=0.2`, `beta=0.8`, and a 300 m triangular distance kernel. Public fault labels are incomplete; the scientific goal is credible detection of unmapped faults, not merely reproducing the known catalogue.

The pinned 19-band stack and other large inputs are restored into ignored `.cache/gems_inputs/` from hash-checked GitHub mirrors. These mirrors are integrity-pinned but are not organizer-authenticated. Do not contact DrivenData or Dropbox to restore assets; GitHub-hosted mirrors are permitted. Do not add restored competition inputs to Git.

## Operating rules

- **One method lane per session.** Before implementation, rank 3–5 untried geological hypotheses and document named layers, target signatures, rationale for off-catalogue faults, differences from existing work, expected holdout benefit, costs, and named non-fault mimics. Select one lane; do not silently switch.
- **Hard budget:** stop after three experiments or two hours, whichever comes first. A weekly submission slot is never spent by the agent. Promotion is a separate selector decision.
- **Uniqueness before placement and again on final dots.** Use the shared `vendor/gems57/uniqueness.py` implementation and an auditable public-raster inventory. Compare surface rank correlation and forward dot overlap. Under the current literal rule, `Spearman |rho| > 0.90` or forward overlap `>0.70` blocks; log the collision and stop. Do not exempt dense/continuous rasters or change this scope silently. An incomplete inventory is not clearance.
- **Blocked holdout protocol.** Reuse the shared `vendor/gems57/holdout.py` and `vendor/gems57/evaluate_holdout.py`; hold out whole buffered fault components/segments, derive any catalogue-based features only from fold-visible faults, mask visible faults pixel-exactly, and use pooled DTI with `alpha=0.2`, `beta=0.8`, and the 300 m triangular kernel. Use the evaluator's paired spatial-cluster 95% CI. Test every feature alone as a leakage canary; AUC above 0.90 is leakage until explained.
- **Never overstate scores.** Label every local evaluation `HOLDOUT-DTI` and include evaluator version, withheld-positive count, and 95% CI. Use `ORGANIZER-CONFIRMED` only for a value copied from a submission receipt. Label public leaderboard values as display observations and model outputs as projections, never scores.
- **Submission artifact contract.** If and only if the gates pass, use `vendor/gems57/submission_writer.py` to create one easy-to-download single-band float32 GeoTIFF, finite values in `[0,1]`, exact grid/CRS/transform, with a short unique name and a note of at most 140 characters. Run local validation and record its SHA-256. Label download/submission status clearly. **Do not upload it.** No artifact is created just to satisfy a filename requirement if uniqueness is blocked.
- **Three reviews and provenance.** Review evidence/claims, geology and holdout design, and registry/package safety in three separate passes. Record irregularities in `IRREGULARITIES.md`. Use official verified sources for factual claims and give the user links for manual review.
- **Final response.** End with exactly one JSON run card containing hypothesis/mechanism, named non-fault mimic, holdout DTI and CI (or explicit `NOT_RUN` nulls), evaluator/count, registry correlation/overlap, raster SHA-256, validator result, submission name/note, and promote/negative verdict.

## Current evidence and stop condition

- Parent `h33-h33-2-b2`: 37,654 dots; exact lineage hashes are recorded in `registry/parents/R0.json`. Its `0.2778` score is an owner-reported **CLAIM**. The local ledger has 21 `BUILT` rows and zero `RECEIPT` rows. The public GEMSDOE32 page labels its artifact **UNSCORED**.
- Official public leaderboard observation on 2026-10-24: displayed top values `0.4413`, `0.3916`, `0.3904`. These are leaderboard display values, not an account receipt; the supplied `0.3195` value conflicts with that observation.
- Existing, historical catalogue-proxy evidence: `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives) for `RELIEFp10piedmont` is `0.006045` with 95% CI `[0.005187, 0.006927]`, versus R0 `0.004006` `[0.003424, 0.004690]`. This is a prior local proxy result, not a fresh run, private/public leaderboard score, or evidence that a better organizer prediction is supportable.
- A reproducible saturation check found the public `17GEMSDOE` raster `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`) positive on every one of the 5,167,373 footprint cells. All 5,106,385 legal cells after exact catalogue exclusion are covered; uncovered count is zero. Under the shared literal overlap rule, every nonempty legal prediction has forward overlap `1.0`, exceeding the `0.70` limit. This is a method-independent stop, not a claim that a candidate-specific Spearman comparison was run.
- No candidate surface or final dots were built for the selected depth-stratified MT lane. The lane has no holdout DTI/CI, candidate SHA, format-validator result, submission name, or slot decision. The TIF writer was not called. The single witness bytes live only under ignored `.cache/public_gems_tifs/`.
- Local tests after the documentation/audit changes: **75 passed**, 12 Rasterio `PendingDeprecationWarning`s. This is not a holdout or submission-format receipt.
- `registry/public_gems_tif_inventory.json` is a metadata-only scan of 101 public owner repositories: 2,508 TIFF paths counted, 1,998 candidate-like paths under a documented heuristic, 1,305 unique candidate-like Git blobs (1,046,507,603 bytes by GitHub metadata). It is not a decoded, full content-level comparison; see its scope limitations and `evidence/registry_saturation_blocker.json`.

## Key files

- `docs/research_assessment_20261024.md` — evidence review, ranked hypotheses, and selected future lane.
- `docs/review_passes_20261024.md` — three-pass review, source links, and reproduction commands.
- `evidence/run_card_20261024.json` — latest run card; no candidate was produced.
- `evidence/registry_saturation_blocker.json` — hash/grid-verified universal-overlap certificate.
- `scripts/scan_public_gems_tif_registry.py` — reproducible metadata-only public GitHub path scan.
- `scripts/check_registry_saturation.py` — downloads only the GitHub witness and reproduces the shared blocker certificate.
- `vendor/gems57/` — shared grid, holdout evaluator, writer, validator, and uniqueness logic; do not fork privately.
- `IRREGULARITIES.md` — append decision-changing findings.

If a future user explicitly changes how continuous full-support surfaces participate in the dot-overlap gate, document that rule change first, rerun the complete registry comparison, and only then consider the selected lane. Until then, no nonempty download-ready candidate can honestly be called unique under the active protocol.
