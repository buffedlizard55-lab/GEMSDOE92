# Historical GEMSDOE92 project charter — superseded as session prompt

> **Do not use this file as the current operating prompt.** Start each session with the repository-root [`README.md`](https://github.com/buffedlizard55-lab/GEMSDOE92/blob/main/README.md), the complete current contract, and consult [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) for the evidence status. This preserved charter includes an older environment snapshot and candidate criteria that may conflict with the current no-submit decision.

## Mission and operating rules

Build an auditable, reproducible system for identifying geothermal/Quaternary-fault prospects and producing a valid single-band GeoTIFF for DrivenData GEMS Prize #306. The operational goal is a strong competition result, but no projected value is a score and no unverified result is presented as fact. Optimize for evidence, not leaderboard speculation; own failures and record limitations.

The original charter instructed readers to consult this file, `README.md`, `SLOT_PLAN.md`, `IRREGULARITIES.md`, and the applicable mechanism/evidence files. That workflow has been superseded: use the current root `README.md` as the only session-start prompt and treat `SLOT_PLAN.md` as a historical archive. Use one declared experiment lane at a time; do not copy a previous raster as a new candidate. Reuse the common feature stack, whole-fault-segment buffered hide-and-recover evaluator, and shared submission writer. Derive catalogue features only from visible traces, mask visible traces pixel-exactly, and evaluate pooled DTI with alpha 0.2, beta 0.8, and a 300 m triangular kernel. A feature-only holdout AUC above 0.90 is a leakage alarm and must be investigated before use. No experiment may exceed the current budget (three experiments or two hours), and a candidate is not promoted or submitted without passing the agreed holdout decision rule. Do not consume a competition slot as part of local development.

Every reported numeric result must be explicitly labeled either:

- **HOLDOUT-DTI** — evaluator/version, withheld-positive count, and 95% CI; or
- **ORGANIZER-CONFIRMED** — copied from an actual submission-page receipt.

A model projection, proxy, claimed score, or leaderboard observation is not an organizer-confirmed score. Record failed and negative experiments as deliverables. Do not silently treat proxies as DTI, or treat a format pass as scientific validation.

## Submission acceptance

A downloadable candidate must be clearly identified as a candidate and have a unique descriptive name plus a form note of at most 140 characters. Before release, verify by reopening the exact file from disk: single-band float32 GeoTIFF, competition CRS, shape, transform, no NaN within footprint, every in-footprint value in [0,1], and the required outside-footprint convention. Record the SHA-256 and validator output. A green format validator alone does not establish expected score, originality against every external repository, or organizer acceptance. Keep competition data and candidate rasters out of public Git unless redistribution rights are verified.

## Historical evidence boundary (superseded checkout snapshot)

The repository identifies `h33-h33-2-b2` as the parent, but its `0.2778` is recorded as a **CLAIM**, not a receipt. The cited public leaderboard value `0.4413` and prompt's later `0.3195` are conflicting owner-provided snapshots and have not been retrieved or verified here. No score improvement over either value can be asserted. `ledger/submissions.csv` reports built experiments, not organizer-confirmed scores. Current review and score provenance are in the root README and `REVIEW_CURRENT.md`.

At the time this charter snapshot was written, the checkout had some small bridge rasters, parent rasters, and prior release TIFFs but no usable `.cache/gems_inputs` full 19-band feature stack, and its runtime lacked numpy, scipy, rasterio, scikit-learn, and pytest. This is historical availability information, not the current runtime state. The present README records that the feature stack remains absent, dependencies are installed in the ignored `.venv`, and the local checks have been run. The availability of files in Git is not proof of organizer provenance or redistribution permission. Do not substitute the project's known-fault proxy for the required whole-segment buffered holdout.

## Reproducibility / run card required for each experiment

At experiment completion, record one machine-readable JSON card containing: hypothesis; mechanism; named non-fault mimic; HOLDOUT-DTI with evaluator version, withheld-positive count and 95% CI (or explicit `NOT_RUN` and reason); correlation/overlap versus registry raster(s) (or `NOT_RUN` and reason); candidate raster SHA-256 (or `NOT_GENERATED`); validator output for NaN/range/CRS/shape/transform (or `NOT_RUN`); unique submission name and <=140-character note (or `NOT_GENERATED`); and verdict `promote` or `negative` (use `blocked` if required evidence could not be obtained). No blanks should masquerade as results.

## Source links for manual audit

- Competition overview/rules: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem description and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition data tab (login may be required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- About page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- DOE/NLR competition document: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN data record: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- INGENIOUS GDR submission: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611

Links identify sources to check; they do not mean this session independently verified every linked page or each claim in the historical ledger.
