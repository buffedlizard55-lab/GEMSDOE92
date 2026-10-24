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

## This session’s result (2026-10-24)

TIPGAP FAR (`far18f33`) is unique vs the local registry and format-valid. HOLDOUT-DTI did not beat R0. Verdict **negative**. File still published for download with that banner.

## Addendum 2026-10-24 (BREAKLINE session) — read after the protocol

- State: primary = `h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif`
  (sha256 `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`).
  Verdict **negative / NOT_CLEARED — NOT RECOMMENDED for a weekly slot** (HOLDOUT-DTI 0.004861 < holdout best RELIEF p10
  0.006045), but the first literal-unique (55.0 % ≤ 3 px vs R0, worst of 17 registry
  rasters) + parent-dominating (+0.000854 [+0.000300, +0.001423]) file in this repo;
  SGMC control +31 % vs R0. Do not relabel it "promote" without a receipt.
- One BREAKLINE dose total may ever be submitted (siblings share keep sets;
  0.82–0.86 mutual overlap, plus 3 SUPERSEDED exact-greedy siblings in `ledger/`).
- Emission rule matters more than the field: spaced top-L beat the exact expected-DTI
  greedy by +0.000701 [+0.000321, +0.001161] on the holdout with identical keeps.
  Re-validate the keep-stage greedy before reusing it; never deviate at build time
  from the selector the screen exercised.
- Do not retry: BASEMENT-STEP from Band 15 (screened out, SGMC AUC 0.378), pure
  seismicity placement (too smooth; multiplier only), radiometric K/Th gradients
  (AUC≈0.50), TIPGAP-far, STEPOVER, MASS ranking, CONCENTRATION bookkeeping.
- Facts to respect: R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 exactly; bridge `sample_submission.tif`
  *is* the catalogue (60,988 px) — geometry only; Band 18 is the only signed band;
  collar count 2,171 (float64 EDT); data path is `scripts/restore_inputs.py`
  (the brief's `download_competition_data.sh` / `prepare_data.py` do not exist).
- If a receipt now exists, recalibrate from it before building anything; `ledger/`
  had 36 BUILT / 0 RECEIPT at the end of this session. Ranked next lanes:
  `docs/HYPOTHESES_20261024_BREAKLINE.md`; full session analysis:
  `docs/ANALYSIS_20261024.md`; run card: `evidence/breakline_run_card.json`.
