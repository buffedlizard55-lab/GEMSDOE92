# GEMSDOE92 — auditable GEMS Prize research and GeoTIFF preflight

> **Start every session here, then read [`SESSION_PROMPT.md`](SESSION_PROMPT.md).** Stay on the session branch and respect the one-method lane, three-experiment/two-hour budget, evidence labels, and the separate human slot selector.

## Executive status

**A unique-within-local-registry, format-valid GeoTIFF is available to download. It is a negative research result and is NOT recommended for a competition slot.** Format validity, lane uniqueness, scientific evidence, and organizer acceptance are different gates.

- **Download:** [`docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.tif`](docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.tif) · [ZIP containing one TIFF](docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-zeros.zip)
- **Public site:** https://buffedlizard55-lab.github.io/GEMSDOE92/
- **Submission instructions:** [`docs/SUBMIT.html`](docs/SUBMIT.html) · [`docs/hypotheses_20261024.md`](docs/hypotheses_20261024.md)
- **Format status:** **OK TO DOWNLOAD.** Ten local MUST gates pass on an independent re-read; one float32 band, EPSG:32611, 3730 × 3292, sample-grid transform, finite values in [0,1], no NaN in the footprint, zeros outside, and no positive mass on the known-fault catalogue.
- **Slot status:** **NOT RECOMMENDED.** This candidate's HOLDOUT-DTI is 0.0000 [0.0000, 0.0000], below its R0 proxy baseline. The score is local only, not an organizer result. No slot was used.
- **Uniqueness:** passes the saved scan against 14 locally accessible registry rasters. This is not proof of global uniqueness; incomplete external/private registries remain a limitation.
- **Audit and run card:** [`docs/downloads/*-audit.json`](docs/downloads/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f-audit.json) · [`evidence/run_card.json`](evidence/run_card.json) · [`evidence/stepover_evidence.json`](evidence/stepover_evidence.json).

## Operator prompt / standing requirements

The purpose of this repository is to make auditable scientific progress toward discovering previously unmapped geothermal-related faults in the DOE GEMS Prize region and to produce a compliant submission GeoTIFF where evidence supports it. A download must be obvious from the start of the site and must state separately whether the file is format-valid to download and whether it is recommended for a weekly submission slot. Local inspection and format validation are automated; DrivenData upload and slot selection remain human actions.

For every session:

1. **One method lane.** Do not copy a sibling site's submission. Compare pre-placement feature surfaces and final dots against the registry. If Spearman rank correlation exceeds 0.90 or more than 70% of dots are within 3 px of a registry raster, log a duplicate and stop.
2. **Reuse the shared stack and tools.** Use the cached feature stack, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`. Hold out whole fault segments with a buffer; derive catalogue features from visible faults only; mask visible faults pixel-exactly; evaluate pooled DTI with α=0.2, β=0.8, and a 300 m triangular kernel. Fix shared-tool defects in the shared tool, never a private fork.
3. **Label every result.** A local metric is **HOLDOUT-DTI** and must include evaluator version, withheld-positive count, and 95% CI. A competition value is **ORGANIZER-CONFIRMED** only when copied from a submission-page receipt. A projection is never a score.
4. **Leakage canary.** Test each feature alone on holdout truth. AUC above 0.90 is leakage until proven otherwise.
5. **Run card.** Record hypothesis; mechanism; a named non-fault mimic; HOLDOUT-DTI and CI; correlation/overlap vs registry; raster SHA-256; validator results (no NaN inside footprint, values [0,1], CRS/shape/transform match); submission name and ≤140-character note; verdict `promote` or `negative`.
6. **Budget and selector.** Stop after 3 experiments or 2 hours. Do not select a competition submission slot; promotion is a separate step subject to the weekly cap. A negative result is a deliverable.
7. **No hallucinated standings.** The GEMSDOE32 0.2778 remains an owner-reported CLAIM with no receipt here. The official public leaderboard was checked on 2026-10-24 and displays 0.4413 at #1; this is an official leaderboard snapshot, not a submission-page receipt for GEMSDOE32 or GEMSDOE92. The prompt's 0.3195 is an older conflicting snapshot.
8. **Core values.** Maximize P(Win): weigh evidence, upside, and risk rather than optimizing for a flattering narrative. Own the outcome end to end: report failures and blockers instead of disguising them.

## What the existing evidence says

- `h33-h33-2-b2` is associated with an owner-reported **CLAIM 0.2778**, but no organizer receipt is present in this repository. Its documented lineage—fixed-size spatially thinned ridge dots, reduced redundancy, and avoidance of known traces—is compatible with the distance-tolerant asymmetric DTI, but this is a mechanistic explanation, not proof of causality.
- **HOLDOUT-DTI** for STEPOVER (`gems57-pooled-hide-v2`, 11,321 withheld positives, 95% CI `[0.0000, 0.0000]`) is negative versus R0 proxy baseline `0.0037 [0.0031, 0.0044]`. It does not show that a genuinely unmapped fault would score zero; this holdout is catalogue-derived and has a structural limitation.
- RELIEF/DILATATION run cards report positive catalogue-holdout deltas but fail the literal whole-file overlap rule against registered parent R0. They are not cleared for a slot. The unique STEPOVER artifact is negative. At present, no candidate in the repository is both expected to improve under the recorded holdout and clear under the literal uniqueness rule.
- The three-to-five next hypotheses, mechanisms, mimics, differences from implemented approaches, relative priority, cost, source availability, and stopping condition are in [`docs/hypotheses_20261024.md`](docs/hypotheses_20261024.md). No new experiment was run in this review because the budget was already consumed and the feature stack is missing locally.

## Answer to “why 0.2778, and can we beat it?”

The observed 0.2778 cannot be causally explained from the supplied public score listing alone: the source artifact's organizer receipt and private test truth are absent. A plausible reason for a high DTI is a fixed dot budget concentrated on spatially distinct ridge candidates that fall within the competition's distance kernel of hidden truth; redundant dots are costly under the asymmetric false-positive term. This is a hypothesis consistent with the known lineage, not a demonstrated explanation. Generating a higher score is possible in principle, but no local HOLDOUT-DTI or model projection establishes that it will happen. Only an organizer-confirmed submission receipt can answer that question for a live submission.

## Run and verify locally

Python dependencies are pinned in `requirements.txt`.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests -q
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
.venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data
.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data
```

Do not rebuild variants as part of a review unless the active lane and remaining budget explicitly allow another experiment. The active source stack `training_features.tif` is not in the current checkout cache; no new feature experiment can be reproduced until the authorized input is staged and pinned.

## Limitations and outstanding work

- **No DrivenData authentication in this session.** The agent cannot fetch login-gated competition inputs, upload, select a slot, or retrieve a private leaderboard receipt.
- **Missing cached stack.** `.cache/gems_inputs/training_features.tif` is absent. The official data page is <https://www.drivendata.org/competitions/306/competition-doe-gems/data/> and requires competitor access. Do not replace it with a public mirror whose redistribution terms are unchecked.
- **Holdout mismatch.** The shared holdout hides known catalogue segments, whereas the competition tests faults missing from the public catalogue. A positive holdout preference may not generalize to new-fault scoring.
- **Registry scope.** “Unique” means only that the candidate cleared the recorded scan of 14 locally accessible rasters, not every GEMSDOE page or private registry.
- **Redistribution terms.** Competition input rasters in this public repo and mirrors need terms review. See [`registry/session_manifest.json`](registry/session_manifest.json) and [`IRREGULARITIES.md`](IRREGULARITIES.md).
- **Leaderboard evidence class.** The public leaderboard was read on 2026-10-24 and displayed 0.4413 at #1 (official leaderboard snapshot, not a submission-page receipt for this candidate). The prompt's 0.3195 is an older conflicting snapshot. The GEMSDOE32 0.2778 remains a CLAIM without a receipt here.

## Verified official sources for manual review

- [Competition overview, problem, data and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (observed 2026-10-24; snapshot, not this project's receipt)
- [Competition data page (login-gated)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository / INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [Faulds et al. Great Basin structural-geothermal context](https://www.osti.gov/servlets/purl/1110517)
- [GEMSDOE32 H33-2-B2 historical project page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) (owner analysis; not a DrivenData receipt)

See [`docs/ANALYSIS.md`](docs/ANALYSIS.md), [`docs/REVIEW_AND_NEXT_STEPS.md`](docs/REVIEW_AND_NEXT_STEPS.md), [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md), and [`IRREGULARITIES.md`](IRREGULARITIES.md) for details and historical findings.
