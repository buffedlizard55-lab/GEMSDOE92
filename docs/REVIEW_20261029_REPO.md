# Repository review — 2026-10-29

## Executive decision

**No GeoTIFF is cleared for competition submission. Do not submit the current candidate or spend a weekly slot.** This review made no candidate raster, did not run a geological experiment, and did not promote/select a submission. This is consistent with the repo's recorded three-experiment cap and negative promotion decision. The user prompt gives no standalone method paragraph for the required single lane; inventing one would violate its own protocol.

The current, machine-readable status is `docs/downloads/current_submission.json` and `docs/downloads/readiness.json`: the RIESZ-LBM2 raster is downloadable for research, but `ok_to_submit=false`, `submission_eligible=false`, `verdict=negative`. It fails the registry uniqueness stop and did not beat the recorded R0 recipe holdout control. Its `0.321602` value is labeled a `MODEL` projection, not a competition score. The `0.2778`, `0.3195`, and `0.4413` values in the prompt are not backed by an organizer receipt in this checkout and must not be presented as organizer-confirmed.

## What was inspected

- Current status/readiness JSON and `SUBMISSION_READY.md`.
- Repository instructions and pipelines, including `scripts/ali_*`, the shared `vendor/gems57` evaluation/writer code, uniqueness and site-check scripts.
- Focus-site reporting and audit material, including the nine-site review for GEMSDOE24/25/27/28/30/31/32/33/36.
- The existing review and prompt documentation. The README already points to a stored standing prompt; its own documentation notes that prompt is a reconstruction, not the verbatim original.
- Current working tree and branch state; it was clean before this review.

## Verification run in this checkout

Installed the pinned project requirements into the ignored `.venv` (no tracked dependency changes).

- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` — **PASS**, 128 served raster files gated.
- `.venv/bin/python -m pytest tests -q` — **804 passed, 19 skipped, 171 warnings** (76.30 seconds).
- A plain system-Python invocation initially could not run these checks because the environment lacked NumPy/pytest; the isolated project environment resolved that without altering tracked files.

These are repository-level format, status-consistency, and regression checks. They are not a fresh reproduction of historical holdout measurements, not a full rerun of the training pipeline, and not organizer acceptance.

## Findings and risks

1. **Submission status is properly fail-closed in the current records.** The download remains labeled research-only. Keep that distinction obvious; local format validity does not imply eligibility or likely leaderboard performance.
2. **No new candidate is justified from the available evidence.** The previous holdout is recorded as historical evidence and was not independently rerun here. The full feature cache is absent from the checked-in data; `data/bridge` contains only the smaller bridge/example raster set. Do not report an estimated score as a measured score.
3. **Registry uniqueness is an operational blocker.** The latest review reports a literal full-support registry witness triggering the prescribed overlap stop. A sparse-only overlap view does not waive that stop. The public registry cache is ignored/not present in this checkout, so a new full-registry audit was not independently repeated.
4. **Focus-site leaderboard numbers are claims, not receipts.** The site summaries are useful forensic history, but source freshness and organizer confirmations are not re-established by running the local test suite. GEMSDOE32's `0.2778` is the highest supplied claim among the nine named sites; the repo's historical explanation is a plausible mechanism, not proof of causality.
5. **The requested autonomous feed is not equivalent to a local static Pages site.** Current status artifacts have pinned/historical provenance. Any claim of being up-to-date requires a successful scheduled fetch, timestamp/commit evidence, and freshness monitoring; none was established in this review.
6. **External source checks were not live-verified.** This sandbox's outbound host restriction prevents checking DrivenData, DOE GDR, USGS, and other official sources. Existing URLs remain useful review links, but availability, current rules, leaderboard, and source coverage must be checked in a suitable connected environment.
7. **Current prompt ambiguity:** it asks for 3–5 candidates and for one single method lane at once, but supplies no unique lane paragraph; it also directs stopping after a three-experiment budget, while repository records say the prior lane exhausted that budget. Therefore this review deliberately does not suggest or run another experimental candidate.
8. **Requested PR/merge:** this review is documentation-only and has no candidate submission or code change requiring integration; no PR was opened and no merge was attempted. Merging a review into `main` is not part of the scientific submission gate and this session is constrained to its active branch.

## Next steps, ordered by gating value

1. Restore the complete, provenance-checked feature stack and a complete registry snapshot; verify hashes, CRS, transform, footprint, nodata conventions, and source/licensing records.
2. Resolve the missing lane paragraph and registry-witness interpretation in the protocol before authorizing a further experiment. Follow the stated experiment cap unless a new protocol is explicitly approved.
3. If authorized, run the shared fold-rebuilt hide-and-recover evaluator, pixel-exact visible-fault masking, and feature-alone leakage canaries. Require paired holdout improvement over the current best before considering any slot.
4. Run pre-placement and final-dot uniqueness checks against the full registry; retain a byte-bound run card and independent validator receipt.
5. Check current official rules, leaderboard, portal submission format and weekly quota live. Keep the selection/slot step separate from modeling and never label `MODEL` or owner-site `CLAIM` as `ORGANIZER-CONFIRMED`.
6. Build feed freshness observability (last successful fetch, source URL, retrieved timestamp, hash, and a stale-feed warning) only when a permitted reliable source endpoint is available.

## Final run card (this review)

```json
{
  "hypothesis": "No new geological hypothesis was tested; the prior authorized experiment budget is recorded as exhausted.",
  "mechanism": "Repository audit and automated regression/served-TIFF validation only; no raster generation or holdout scoring occurred.",
  "named_non_fault_process_that_could_mimic_it": "No new raster was generated; the repository's prior review identifies canyon rims, fan-head incision, paleoshorelines, and lithologic contacts as possible edge mimics.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "not run in this review",
    "withheld_positive_pixels": null,
    "ci95": null,
    "note": "Historical archived values are not freshly reproduced; no projection is reported as a score."
  },
  "correlation_overlap_vs_registry": {
    "measurement": "not rerun in this review",
    "prior_status": "current archived candidate fails conservative registry uniqueness gate",
    "verdict": "negative"
  },
  "raster_sha256": null,
  "validator_output": {
    "no_nan_inside_footprint": "historical current candidate gate only; no new raster produced",
    "values_in_0_1": "historical current candidate gate only; no new raster produced",
    "crs_shape_transform_match": "historical current candidate gate only; no new raster produced",
    "site_check": "PASS, 128 served rasters gated",
    "test_suite": "804 passed, 19 skipped"
  },
  "submission_name": null,
  "submission_note": "No submission generated; current candidate remains DO NOT SUBMIT.",
  "verdict": "negative"
}
```
