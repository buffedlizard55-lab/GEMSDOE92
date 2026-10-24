# Session prompt — GEMSDOE92

Read this file and `README.md` at the start of every session. This is the standing operator contract for the repository.

## Mission

Produce a unique, scientifically defensible GeoTIFF for DrivenData competition 306 (DOE GEMS Prize: hidden geothermal-related faults, NW Great Basin, EPSG:32611 at 100 m). The public Pages site must make the download obvious and state distinctly whether the file is format-valid to download and whether it is recommended for a weekly competition slot. Format inspection/validation must run in the project without a human inspector. A human competitor still authenticates, selects a slot, and uploads.

The GEMSDOE32 `h33-h33-2-b2` value 0.2778 remains an owner-reported CLAIM without a submission-page receipt in this repository. The official public leaderboard was checked on 2026-10-24 and displayed 0.4413 at #1; this is an official leaderboard snapshot, not a receipt for GEMSDOE32 or GEMSDOE92. The prompt's 0.3195 is an older conflicting snapshot. Never elevate a CLAIM or leaderboard observation into an organizer receipt for this project's submission.

## Parallel-run protocol

1. **One method lane.** Before placement and on final dots, compare against registry rasters. If Spearman rank correlation > 0.90 or >70% of dots are within 3 px of one registry raster, log duplicate and stop. State registry-scan coverage; a local index is not global proof.
2. **Reuse shared tools.** Use the authorized cached feature stack, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`. Hide whole fault segments with a buffer; derive catalogue features only from visible faults; mask visible faults pixel-exactly; evaluate pooled DTI α=0.2, β=0.8, 300 m triangular kernel. Fix shared tools in the template rather than making a private fork.
3. **Label every performance value.** `HOLDOUT-DTI` must include evaluator version, withheld-positive count, and 95% CI. `ORGANIZER-CONFIRMED` must be copied from a submission-page receipt. A projection is never a score.
4. **Leakage canary.** Test each feature alone on holdout; AUC >0.90 is leakage until proven otherwise.
5. **Run card.** Record hypothesis, mechanism, named non-fault mimic, holdout DTI + CI, correlation/overlap vs registry, raster SHA-256, validator result (no NaN inside footprint, values [0,1], CRS/shape/transform match), submission name and note ≤140 characters, and verdict `promote` or `negative`.
6. **Budget/selector.** Stop after 3 experiments or 2 hours. Do not pick competition submissions: weekly-slot promotion is a separate selector step. Negative results are deliverables.

## Current verified project state (reviewed 2026-10-24)

- The site download is `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.tif` (zeros outside). Local format/range/grid validation passes; full receipt is `docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros-audit.json`.
- The candidate is **OK TO DOWNLOAD, NOT RECOMMENDED FOR A SLOT**. Its saved run card reports HOLDOUT-DTI 0.0000 [0.0000, 0.0000], evaluator `gems57-pooled-hide-v2`, 11,321 withheld positives. It is unique only against the documented 14 locally accessible registry rasters.
- The previous RELIEF/DILATATION positive holdout arms fail the literal >70% within-3-px overlap rule against R0; record them as duplicates, not promoted candidates.
- No new experiment was performed in the latest review. The three-experiment budget was already consumed; the full `training_features.tif` stack is absent from the current cache.

## Site and submission rules

- Zeros-outside encoding is the offered download because it is all finite and avoids the reported portal range error.
- Executive summary: `docs/SUBMIT.html`; lowercase duplicate and `executive-summary.html` point to that canonical page.
- `scripts/check_site.py`, `gems.gates`, and `gems57.validate` perform local format preflight. Local PASS is not organizer acceptance or performance evidence.
- Never claim a holdout score predicts organizer score. Do not submit or spend a weekly slot from this agent session.

## Official sources

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://docs.nlr.gov/docs/fy26osti/96647.pdf
- https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- https://gdr.openei.org/submissions/1391
- https://epsg.io/32611
- https://www.osti.gov/servlets/purl/1110517

## Core values

Maximize P(Win): weigh evidence, upside, and risk rather than optimizing for a flattering narrative. Own the outcome end to end: record negative results, blockers, and validation limits honestly.
