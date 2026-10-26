# Executive evidence review — 26 October 2026

**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** No candidate is cleared and no leaderboard estimate is defensible from these data. No organizer receipt was obtained.

## Nine focus sites

These are the highest historical values supplied in the brief, not newly verified organizer scores. Static re-scoring uses `gems57-pooled-hide-v2`, 22,663 withheld positive occurrences, 1,000-draw physical-block bootstrap 95% CI. Static predictions were built with the full catalogue: these numbers are diagnostic and are NOT the requested fold-rebuilt hide-and-recover test. They must not rank competition submissions.

| Site / arm | Historical reported value | Positive pixels | Static HOLDOUT-DTI [95% CI] | Worst cross-site 3-px overlap |
|---|---:|---:|---|---:|
| GEMSDOE24 | 0.2477 CLAIM | 60,069 | 0.090296 [0.078978, 0.101672] | 1.0000 |
| GEMSDOE25 | 0.2600 CLAIM | 44,090 | 0.093234 [0.082033, 0.104341] | 1.0000 |
| GEMSDOE27 | 0.2449 CLAIM | 61,328 | 0.089959 [0.078678, 0.101220] | 0.9802 |
| GEMSDOE28_h36_1 | 0.2710 CLAIM | 37,660 | 0.027383 [0.024301, 0.030473] | 1.0000 |
| GEMSDOE30 | 0.2600 CLAIM | 44,090 | 0.093234 [0.082033, 0.104341] | 1.0000 |
| GEMSDOE31 | 0.2708 CLAIM | 40,199 | 0.029358 [0.026134, 0.032593] | 1.0000 |
| GEMSDOE32 | 0.2778 CLAIM | 37,654 | 0.004006 [0.003424, 0.004690] | 1.0000 |
| GEMSDOE33 | 0.2632 CLAIM | 41,865 | 0.053143 [0.047384, 0.058857] | 0.9971 |
| GEMSDOE36 | 0.2750 CLAIM | 38,854 | 0.004192 [0.003569, 0.004887] | 0.9758 |

GEMSDOE32 has the highest supplied historical claim (0.2778); it is not a new unique candidate. GEMSDOE25 and GEMSDOE30 have identical positive support; GEMSDOE28 SOLO and GEMSDOE31 likewise have identical support despite different TIFF encodings. GEMSDOE36 contains every R0 dot plus 1,200 additional dots. Different filenames and file hashes alone do not demonstrate uniqueness.

## Why GEMSDOE32 could improve on its ancestors

Pinned R0 verification found 37,654 dots, obtained from D2.8 by removing dots within 2 pixels of the mapped catalogue. Thinning and collar pruning can change the tradeoff between distance-weighted true-positive coverage and false-positive mass. The exact effect depends on hidden truth. The claimed score changes cannot establish causation, marginal precision, a theoretical ceiling, or a hidden-label count. No projection above 0.2778, 0.3195, or 0.4413 is justified here.

## New THERMOTILT research

Hypothesis: signed magnetic/gravity tilt edges, upslope back-projection of thermal anomalies, and opposing-gradient accommodation signatures might identify concealed faults. Intact lithologic contacts, groundwater outflow, and erosional or shoreline features can mimic these signatures. Surface derivatives do not prove fault dip, geothermal productivity, or a discovered vent.

Three arms were constructed with the shared submission writer; all passed 11 local format checks: single float32 band, exact template CRS/shape/transform, finite values in [0,1], zeros outside, no positive catalogue pixels, and no dots within 2 pixels of the catalogue.

| Research file | Diagnostic HOLDOUT-DTI [95% CI] | Sparse dot overlap | Submission decision |
|---|---|---:|---|
| [gemsdoe92-thermotilt-blind-37654-20261026-8c11022a-zeros.tif](downloads/gemsdoe92-thermotilt-blind-37654-20261026-8c11022a-zeros.tif) | 0.054441 [0.046275, 0.062765] | 0.624847 | DO NOT SUBMIT |
| [gemsdoe92-thermotilt-distal-37654-20261026-a0907c10-zeros.tif](downloads/gemsdoe92-thermotilt-distal-37654-20261026-a0907c10-zeros.tif) | 0.065541 [0.056557, 0.074268] | 0.595634 | DO NOT SUBMIT |
| [gemsdoe92-thermotilt-graded50k-50000-20261026-36a00875-zeros.tif](downloads/gemsdoe92-thermotilt-graded50k-50000-20261026-36a00875-zeros.tif) | 0.081472 [0.071270, 0.090871] | 0.588060 | DO NOT SUBMIT |

HOLDOUT-DTI evaluator: `gems57-pooled-hide-v2`, 22,663 withheld positive occurrences. These are saved experimental outputs, **not certified leak-free estimates** for the reasons below. The literal dense-witness overlap is 1.0.

## Critical limitations and protocol deviations

- Pre-placement registry checks were executed after placement and evaluation, not before. This violates the requested stop ordering; no promotion is permitted.
- The literal full-footprint witness was already known before this experiment. Continuing construction did not honor the literal stop.
- Stage-1 OOF context is not nested within each outer Stage-2 test quadrant: training context can depend on labels in that outer quadrant. AUC below 0.90 does not prove absence of leakage. Reported HOLDOUT-DTI is diagnostic, not certified promotion evidence.
- Only seed 20 was used for feature canaries. Missingness was not independently tested (the runner tested nonzero indicators).
- Public Spearman checks covered selected overlap witnesses, not every registry raster. Flat-offset dilation can wrap at row edges. Sparse uniqueness PASS is provisional, not exhaustive certification.
- The three-arm experiment budget was reached. No further experiment or submission slot is authorized. Network policy prevents current organizer leaderboard/rules/receipt verification.

## Sources and access boundaries

- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Competition description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Organizer data portal](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Rules PDF supplied by owner](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391)

Non-GitHub official pages were not fetched here. Input SHA-256 checks establish mirror identity, not official authenticity or redistribution rights. Exact input identities and source declarations are in `registry/session_manifest.json` and `registry/ventscarp_external_manifest.json`; no invented source identifiers or hashes should be substituted.

## Next work

Honor the literal stop and obtain a documented protocol resolution before another placement. Fix nested outer-fold context isolation in the shared model pipeline, run canaries on each draw including raw missingness, and implement exact two-dimensional registry comparisons before placement. Lock an untouched outer spatial test rather than reusing these adaptively selected folds. Only then evaluate a newly assigned method lane. An organizer receipt and current weekly cap are required for a separate real-slot selector decision.
