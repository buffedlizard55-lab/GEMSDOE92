# Repository review — 2026-10-25

## Decision

**Research download only. DO NOT SUBMIT; do not spend a weekly slot.** This review did not generate, rename, copy, or select a TIFF. The requested new unique submission remains unmet. The binding pre-placement gate rejected further placement; proceeding would contradict the stated parallel-run protocol.

## Scope and reproduction

The checkout has the template rasters in `data/bridge/`, shared package code under `gems/`, experiment scripts under `scripts/`, a registry/ledger, a static Pages site under `docs/`, and numerous historic candidate rasters. The repository README and `SESSION_PROMPT.md` already contain the persistent operating brief, evidence labeling rules, submission guide, and explicit uniqueness stop.

Fresh automated command:

```bash
.venv/bin/python scripts/audit_readiness.py --fetch-witness --output .cache/session_20261025_review.json
```

Exit code **1** is the command's documented confirmed-STOP outcome, not an execution failure. The immutable JSON receipt is [`evidence/review_20261025_readiness.json`](../evidence/review_20261025_readiness.json). It downloads a pinned public GitHub raster, checks its SHA-256 and alignment, and confirms positive values in all `5,167,373` template footprint cells. Thus every nonempty in-footprint candidate would have forward overlap `1.0`, above the user-specified `0.70` threshold. This is a one-witness rejection proof, not a full registry uniqueness scan. No candidate surface or dots were created, so surface rank correlation and final-dot checks were correctly not run.

The existing primary research TIFF was independently revalidated by the audit: SHA-256 `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`; one `float32` band, `EPSG:32611`, shape `3730 × 3292`, matching transform, all values finite and in `[0,1]`, no NaN in the footprint, and zeros outside. **This is not a new submission and is not cleared to submit.**

## Three passes

1. **Implement/verify:** No model or raster implementation was appropriate after the binding stop. Installed the repository's pinned dependencies into ignored `.venv/`, fetched and rechecked the witness through the shared readiness script, and saved a machine-readable receipt.
2. **Review for bugs/assumptions:** Confirmed `audit_readiness.py` documents exit `1` as confirmed stop and `2` as inconclusive; the actual receipt verifies the exact pinned witness, full footprint support, and existing file checks. Avoided treating the receipt's existing TIFF-format PASS as uniqueness clearance. Noted that supplied score snapshots conflict (`0.3195` and `0.4413`), and neither is independently authenticated in this review.
3. **Recheck against the brief:** Ran all tests, the site checks, ledger, manifest, and parent verification. Exact outputs are below. No holdout, leakage canaries, geological experiment, weekly submission, or organizer score was claimed.

## Validation results

- `pytest tests -q`: **525 passed**, 140 upstream Rasterio pending-deprecation warnings.
- `PYTHONPATH=vendor python scripts/check_site.py`: **PASS**, 82 served rasters gated.
- `python -m gems ledger`: **111 rows**, all shown `UNSCORED`, best receipt `none`.
- `python -m gems manifest --manifest registry/data_manifest.json --data-root data`: **PASS**.
- `python -m gems parent --recipe registry/parents/R0.json --data-root data`: **PARENT VERIFIED (pinned artefact)**; this validates the pinned artifact, not a reconstruction of its training recipe.
- Witness audit: confirmed STOP; exit `1` by design.

Commands used the repository's `.venv` because the base interpreter had no NumPy/pytest and rejected system-wide pip writes under PEP 668. The virtual environment is ignored and not a deliverable.

## Hypothesis planning / constraint

The prompt's required “single method paragraph” is not present in the message. Repository history includes already tested lanes such as listric, scarp, gravity, drainage, radiometric, flexural, and stress variants; rebranding one as novel would be misleading. Existing conditional untried concepts include `TENSOR-RIEDEL` and `FLEXURE-HINGE` in the historical LISTRIC hypothesis queue and the shortlist in [`docs/HYPOTHESES_20261025_REVIEW.md`](HYPOTHESES_20261025_REVIEW.md). They are **not authorized or validated candidates for this run**: the universal literal overlap stop occurs before placement and no method lane was assigned. Further, an unavailable official external layer cannot be described as obtainable from the current sandbox merely because a public source URL exists.

The requested 3–5 hypothesis ranking and top-candidate holdout test are therefore deferred, not fabricated. The correct next step is resolution of the duplicate-policy contradiction and explicit assignment of the intended method paragraph; then freeze a comparable holdout control, validate the candidate before a slot, and run canaries/uniqueness screens per the README contract.

## Important evidence limits / irregularities

- The prompt's GEMSDOE32 `0.2778`, leaderboard `0.3195`, and `0.4413` are not proven by an organizer submission receipt in this checkout. The ledger reports no receipt. The GEMSDOE32 page and prior local analysis treat `0.2778` as an owner-reported claim, not organizer-confirmed score.
- The registry witness is a public project artifact, not organizer authentication or evidence about geological mechanism. Its full-support footprint makes the literal >70% overlap test degenerate for any nonempty output. We did **not** silently substitute a matched-budget comparison: that would violate the user-stated literal stop rule. Resolving that policy conflict is necessary before a new unique candidate can be emitted.
- No HOLDOUT-DTI was run in this review. The evaluator version, withheld-positive count, and 95% CI are consequently **not applicable / null**, rather than zero or a projected score.
- No live DrivenData page, current cap, current leaderboard, login-gated data, or submission receipt was checked in this run. Do not infer permission, current score, or slot availability.
- The repo includes artifacts dated 2026-10-26 although the session date is 2026-10-25. These future-dated records were not treated as evidence of chronology or independently rerun in this review.
- Site workflow-mode publishing limitations recorded by prior repo reviews remain outside the checks performed here; local site checks do not prove GitHub Pages production deployment is gated by CI.

## Machine-readable run card

```json
{
  "hypothesis": "The pinned registry positive support covers the full footprint, so any nonempty in-footprint output violates the literal overlap gate.",
  "mechanism": "Every candidate positive lies on positive witness support, yielding forward 3-pixel overlap 1.0.",
  "named_non_fault_process_that_could_mimic_it": "A space-filling continuous prediction background; this overlap is not evidence of shared geological mechanisms.",
  "holdout_dti": null,
  "holdout_label": "Not run: stopped before placement; no evaluator/version, withheld positives, or CI.",
  "correlation_overlap_vs_registry": {
    "evidence_class": "REGISTRY-MEASUREMENT",
    "scope": "one hash-pinned witness; rejection only",
    "rank_correlation": null,
    "forward_overlap_for_any_nonempty_in_footprint_candidate": 1.0,
    "threshold": 0.70
  },
  "raster_sha256": "91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e",
  "validator_output": {
    "existing_research_artifact_only": true,
    "no_nan_inside_footprint": true,
    "all_finite": true,
    "values_in_0_1": true,
    "crs_shape_transform_match": true,
    "crs": "EPSG:32611",
    "shape": [3730, 3292],
    "footprint_pixels": 5167373
  },
  "submission_name": null,
  "note": "Review only; no candidate generated; DO NOT SUBMIT.",
  "verdict": "negative"
}
```
