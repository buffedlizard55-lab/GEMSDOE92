# Session prompt — GEMSDOE92

Read this at the start of every session, together with `README.md`.

## Mission

Produce a **unique** GeoTIFF for DrivenData competition 306 (DOE GEMS Prize: hidden geothermal-related faults, NW Great Basin, EPSG:32611 100 m). The file must be obviously downloadable from the GitHub Pages site. Inspection and validation run in the project, without a human inspector in the loop. A human still performs the DrivenData upload (3/week cap).

Parent studied: GEMSDOE32 `h33-h33-2-b2` CLAIM 0.2778 (zeros). That score is **not** ORGANIZER-CONFIRMED in this ledger. Prompt-cited public tops (0.3195 / 0.4413) are likewise not receipts here.

## Parallel-run protocol

1. **Lane.** One method. If Spearman vs any registry raster > 0.90, or >70% of dots fall within 3 px of one registry raster, log duplicate and stop.
2. **Reuse.** Cached feature stack, `vendor/gems57/evaluate_holdout.py`, `vendor/gems57/submission_writer.py`. Holdout = hide-and-recover: withhold whole fault segments with a buffer; catalogue-based features only from visible faults; mask visible faults pixel-exactly; pooled DTI α=0.2 β=0.8, 300 m triangular kernel.
3. **Label every number** HOLDOUT-DTI (evaluator version, n withheld positives, 95% CI) or ORGANIZER-CONFIRMED. A projection is never a score.
4. **Leakage canary.** Test each feature alone on the holdout. AUC > 0.90 means leakage until proven otherwise.
5. **Run card JSON:** hypothesis; mechanism; named non-fault process that could mimic it; holdout DTI+CI; correlation/overlap vs registry; raster sha256; validator (no NaN inside footprint, values in [0,1], CRS/shape/transform match); submission name + note ≤140 chars; verdict promote/negative. Negative results are deliverables.
6. **Budget.** Stop after 3 experiments or 2 hours. Do not pick submissions; promotion is a separate selector step.

## Site / download rules

- Zeros-outside encoding is the only download offered (portal error: `Predicted values must be in range [0, 1]`).
- Banner must say whether the file is OK to download **and** whether it is recommended for a weekly slot.
- Executive summary subpage explains the DrivenData form (name + note).
- No manual inspection required for format validation (`scripts/check_site.py`, `gems.gates`, `gems57.validate`).

## Official sources

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://docs.nlr.gov/docs/fy26osti/96647.pdf
- https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- https://gdr.openei.org/submissions/1391
- https://epsg.io/32611
- https://en.wikipedia.org/wiki/Tversky_index
- https://gbcge.org/current-projects/ingenious/

## Core values

Maximize P(Win). Own the outcome end to end. Do not copy a previous submission except to learn.

## Current repository status (as checked 2026-10-24)

The prior DILATATION experiment budget is exhausted (p10, p12, p15). Their holdout results are positive relative to R0, but each is over the literal 70%/3-pixel registry duplicate threshold; record them as duplicates and do not recommend a weekly slot. TIPGAP FAR clears the overlap threshold (67.00%) but its HOLDOUT-DTI is below R0, so it is a negative deliverable. A format-valid TIFF may be downloaded for review, but no current artifact is cleared to submit. Do not begin another arm without a fresh task/session budget; the next scientifically useful action is resolve the uniqueness-versus-credit gap, then validate with the shared holdout before slot selection.
