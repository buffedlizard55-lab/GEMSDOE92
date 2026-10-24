# GEMSDOE92 repository re-audit — 2026-10-24

## Decision

**Research download: OK. Competition submission: NOT CLEARED; do not submit.** This review generated no GeoTIFF, ran no geological experiment, and used no submission slot. The request for a fresh unique TIFF is not fulfilled in this pass: the active literal registry rule forces a duplicate stop for every nonempty prediction on the valid footprint. Reusing or renaming an old TIFF, or emitting a zero/no-signal raster to dodge the check, would not satisfy the scientific objective.

The current download remains [`APRONRIDGE free1d`](downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif) (SHA-256 `1a29a5d81e8561954f04a563b4975cb84d00898b8d7634700a9d409a10e06cbc`). It is format-valid for research, but its final dots have `REGISTRY-MEASUREMENT` forward 3-pixel overlap `1.000` with the verified `17GEMSDOE E-proba-multiscale` witness, whose positive support covers all `5,167,373` footprint cells. See [exact-file witness receipt](downloads/public_witness_apronridge.json). That witness is a continuous dense probability surface; the literal overlap rule makes this an operational duplicate, **not** a claim that the geological hypotheses or rasters are equivalent.

## What the supplied `0.2778` can and cannot tell us

The GEMSDOE32 value `0.2778` remains a prompt-supplied **CLAIM**, not an `ORGANIZER-CONFIRMED` receipt in this checkout. The plausible mechanism documented in [`ANALYSIS_20261024_STEPEDGE.md`](ANALYSIS_20261024_STEPEDGE.md) is that thinning, pruning and clearance from already mapped faults reduced redundant/off-target prediction mass while retaining useful distance-weighted coverage. This is mechanistic interpretation, not causal proof: score alone does not identify the model or its effects, and the private test labels and a submission-page receipt are not available here. The conflicting `0.3195` and `0.4413` values are not refreshed in this review. No local `HOLDOUT-DTI` result can establish an improvement over a competition leaderboard score.

For traceability, the parent-file lineage and local evaluator behavior are documented in `registry/parents/R0.json`, `gems/parent.py`, and the linked analysis. The only defensible interpretation is that the owner-reported artifact is consistent with a spaced/pruned catalogue-derived candidate and achieved the claimed reported score; no stronger causal or leaderboard claim follows without organizer evidence.

## Hypothesis planning and stop boundary

The four conditional research ideas and their layers, mechanisms, non-fault mimics, differences from existing modules, and qualitative cost/value ranks are already recorded in [`REVIEW_AUTOMATED_20261024.md`](REVIEW_AUTOMATED_20261024.md) and [`docs/HYPOTHESES_20261024_APRONRIDGE.md`](HYPOTHESES_20261024_APRONRIDGE.md). They remain a **future, unvalidated queue**, not new ideas tested in this pass. The feature stack `training_features.tif` is absent from the staged `data/` directory; no new external source was fetched or verified here. Therefore no candidate was pre-screened or tested, and no expected score or holdout improvement is projected.

The next scientific work is conditional: after an authorized resolution of how dense continuous registry rasters are treated, restore inputs from the permitted official source, select one method lane, compare its real surface before placement, run each feature's leakage canary, and evaluate whole-segment buffered hide-and-recover using the shared `vendor/gems57/evaluate_holdout.py`. Reuse the shared `vendor/gems57/submission_writer.py`; do not fork the evaluator. Stay within the three-experiment / two-hour budget. Only a candidate that beats the registered holdout-best and clears both pre-placement and final-dot registry checks can reach a separate selector decision.

## Three review passes

1. **Pass 1 — repository and previous-session review:** Read `README.md`, `SESSION_PROMPT.md`, `docs/NEXT_STEPS.md`, current site pages, existing run cards, registry witness receipts and the shared validation/evaluator entry points. Identified stale current-state text: README's primary download pointed at HYDROCONDUIT while the site and APRONRIDGE section identify APRONRIDGE; the current next-step list advised an upload despite the binding witness stop; and the ledger row count had advanced. Corrected the current README pointer and replaced the top of `docs/NEXT_STEPS.md` with a fail-closed current status and action order.
2. **Pass 2 — defects and edge cases:** Installed the pinned `requirements.txt` into ignored `.venv` because system Python had no NumPy/pytest. Confirmed the current surface checker fails closed on served rasters and no new candidate is needed or permitted to demonstrate that gate. Rechecked cached inputs and confirmed the feature stack is not staged. Did not treat the dense witness as geological equivalence, a leaderboard score, or a full fresh registry scan.
3. **Pass 3 — original requirements and evidence:** Re-ran tests, site checks, manifest verification, parent verification, ledger inspection, compilation and whitespace checks. The download is clearly labeled research-only; executive and submission guides identify the upload process while explicitly blocking this current artifact. No slot or organizer receipt was claimed. The requested fresh unique TIFF remains explicitly unmet rather than misrepresented.

## Verification record

Machine-readable card: [downloaded JSON](downloads/review_20261024_reaudit_run_card.json) (canonical copy: [`evidence/review_20261024_reaudit_run_card.json`](../evidence/review_20261024_reaudit_run_card.json)).

- `python -m pytest tests -q` under `.venv`: **199 passed**, with 103 non-fatal Rasterio/Affine pending-deprecation warnings.
- `PYTHONPATH=vendor python scripts/check_site.py`: **PASS**, all 25 served zeros-outside TIFFs gated.
- `PYTHONPATH=vendor python -m gems manifest --manifest registry/data_manifest.json --data-root data`: all 8 manifest inputs verified.
- `PYTHONPATH=vendor python -m gems parent --recipe registry/parents/R0.json --data-root data`: pinned R0 verified; 37,654 dots, total mass 37,654, target footprint 5,167,373 cells.
- `PYTHONPATH=vendor python -m gems ledger`: 57 rows, all `BUILT`; **0 `ORGANIZER-CONFIRMED` receipts**.
- `python -m compileall -q gems scripts tests vendor/gems57` and `git diff --check`: PASS.

All verification above establishes local software/data integrity only. It does not establish portal acceptance, fresh official-source retrieval, global registry completeness, organizer confirmation, a live leaderboard score, or that APRONRIDGE beats the competition's private test score.

## Official and source review boundary

The official manual-review links remain in [`SESSION_PROMPT.md`](../SESSION_PROMPT.md). No non-GitHub official source (DrivenData, USGS, GDR, NLR) or live leaderboard was fetched in this review. The hash-verified witness is an owner-repository file, not an official competition receipt. Previously recorded credentials/data-access limitations remain: the DrivenData data tab requires authenticated access per prior repository evidence, and competition source/license terms must be checked before reuse or redistribution.

## Limitations / irregularities

- **Binding policy trap:** one registry raster has positive support on every footprint cell, so the literal final-dot overlap test necessarily rejects any nonempty in-footprint candidate. Do not alter the threshold or silently exempt dense rasters. This is the principal blocker to promotion.
- **Score provenance:** `0.2778`, `0.3195`, and `0.4413` are not organizer receipts in this checkout; the latter two are also conflicting supplied snapshots.
- **Missing source inputs:** the full feature stack is not staged; no full model-training or new holdout experiment was run.
- **No new submission:** the existing downloadable TIF is prior research output, not newly generated in this session; there is no new unique TIF to submit and no slot should be used.
- **Automation boundary:** local file/format checks are automated. An authorized DrivenData account, upload, slot selection, and organizer receipt remain external to this local repository workflow.
