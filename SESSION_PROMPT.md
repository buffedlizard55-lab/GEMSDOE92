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

- A zeros-outside encoding is currently offered for **review only** because the reported portal error was `Predicted values must be in range [0, 1]`; it is not confirmed submission-compliant. The official problem page says data outside the submission bounds should be null/NaN, so do not submit a zero-filled outside mask without organizer confirmation.
- Banner must say whether the file is OK to download for review **and** whether it is recommended for a weekly slot; local range validation is not official acceptance.
- Executive summary subpage explains the DrivenData form (name + note) and clearly says when not to upload.
- Project format/uniqueness checks run without manual pixel inspection (`scripts/check_site.py`, `gems.gates`, `gems57.validate`); slot selection and organizer validation remain external.

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

## Session history and current review state

- The previously executed TIPGAP FAR (`far18f33`) lane passes local range/geometry preflight and was below the R0 holdout baseline; its verdict is **negative**. Its zero-filled outside mask also lacks confirmed acceptance against the official null/NaN outside-bounds statement. It remains a documented negative diagnostic artifact.
- This checkout also contains DILATATION p10/p12/p15 artifacts whose filenames/evidence carry the date `2026-10-25`, later than the present review date (`2026-10-24` UTC). Treat that as a provenance irregularity, not a date to silently normalize.
- Current research review follows the repository README's DILATATION scope, but does **not** launch a new experiment: the official 19-band training feature stack is absent from `data/` and `.cache/`. DILATATION p12 passes local range/geometry gates, but its zero-filled outside mask differs from the official null/NaN statement, and its 99.37% overlap within 3 px of registered parent R0 breaches the 70% uniqueness stop. It is **not cleared / not recommended for submission**.
- The official training-data page is https://www.drivendata.org/competitions/306/competition-doe-gems/data/ (login may be required). Do not use a public owner mirror as an official substitute when redistribution terms are unchecked. No weekly slot is selected or spent.
