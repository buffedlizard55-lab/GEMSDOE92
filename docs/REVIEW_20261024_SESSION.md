# Repository review and tooling hardening — 2026-10-24 UTC

## Decision

**No new TIFF, geological experiment, or weekly submission slot was produced/used in this review.** Existing site downloads remain available for research only; none is cleared for contest submission. The user's request for a fresh unique candidate is explicitly **unfulfilled** because the current literal registry rule has a binding witness that blocks every nonempty in-footprint prediction. We do not bypass that stop or claim that an old TIFF is new.

The site-primary witness receipt reports a full-footprint positive raster: `5,167,373 / 5,167,373` competition-footprint cells positive. This is **REGISTRY-MEASUREMENT** ([witness receipt](downloads/review_20261024_springalign_witness_v2.json)), not a score. The exact existing SPRINGALIGN file has **REGISTRY-MEASUREMENT** forward overlap `1.0` and Spearman `0.0437294869`; the pre-placement surface was not checked in that retrospective rejection. A full scan was not repeated. The witness alone is sufficient under the literal >70% final-dot stop; this does not assert geological equivalence or global completeness.

## Scientific response and limits

The supplied GEMSDOE32 `h33-h33-2-b2` value **0.2778 is a CLAIM**, not an organizer receipt in this repository. Prior local forensics are documented in [`ANALYSIS_20261024_STEPEDGE.md`](ANALYSIS_20261024_STEPEDGE.md): the parent geometry is consistent with a fixed prediction budget, spatial thinning and pruning/known-fault clearance reducing redundant or masked predictions while retaining distance-weighted coverage. That is a plausible mechanism, not causal proof; the exact evaluated bytes and private target labels are not available. The user-supplied `0.3195` and `0.4413` leaderboard values conflict and were not refreshed in this review. No local HOLDOUT-DTI result can establish that a candidate beats any of those live-score claims.

The four conditional, ranked ideas already recorded in [`REVIEW_AUTOMATED_20261024.md`](REVIEW_AUTOMATED_20261024.md) remain a queue, not implemented work: (1) cross-profile DEM step-versus-channel likelihood (Bands 12/19); (2) offset correspondence between magnetic edges and DEM breaks (Bands 14/12/19); (3) terrain-conditioned gravity residual edges (Bands 13/12); (4) relief-matched null testing for spring-alignment votes (GDR INGENIOUS points plus Band 12). Each names non-fault mimics in the linked review. Expected gain is unmeasured; ranks are qualitative value/cost priorities, not numerical projections or claims of global novelty.

**No hypothesis was validated this session.** The cached `training_features.tif` is absent from this checkout (`data/` contains bridge/template and parent rasters only; no `.cache` inputs were staged). The official DrivenData competition data tab is the specified source for that stack, but the current runtime did not access it or authenticate. The prior review states the data endpoint is login-gated. The GDR and other non-GitHub sources were not accessed here. Pinned owner mirrors, if later restored, prove byte identity only—not official provenance, availability terms, or redistribution permission. A spatial holdout validation and a pre-placement comparison are both deferred until policy and input-data access are resolved. No submission slot was touched.

## Shared validation bug found and fixed

Before this change, `gems.gates._g_nan_outside()` treated every non-finite outside-footprint value as NaN. Therefore an infinity outside the footprint could be reported as an allowed NaN-outside encoding, even though the public CLI was used as a submission preflight. The separate `vendor/gems57.validate` writer path and current website check were stricter, but the shared CLI contract was inconsistent.

The shared fix is centralized in `gems/gates.py`; the documented `make validate FILE=...` target was also corrected to default to the committed sample grid instead of expanding an unset `REFERENCE` variable:

- Research/intermediate `run_gates()` retains the legacy NaN-outside option, but now rejects infinity or any other nonzero finite value outside the footprint.
- Its explicit `require_submission_encoding=True` mode requires every pixel finite, globally in `[0,1]`, and exactly zero outside the footprint; it also requires a nonempty footprint.
- `python -m gems validate` always uses strict submission encoding. There is no CLI override that could present a NaN-outside raster as upload-safe.
- `scripts/check_site.py` uses the same strict shared gate for every served zeros-outside TIFF.
- `scripts/audit_download.py` applies strict mode to the zeros-outside candidate; its historical NaN twin remains a research comparison only.
- Tests cover strict zeros/NaN behavior, CLI behavior, and infinity/out-of-range values outside the footprint.

No raster bytes, ledger entries, scores, model outputs, uniqueness thresholds, or historical receipts were changed.

## Three review passes

1. **Pass 1 — implementation:** reviewed the README/session contract, current status, site, submission guides, common validation code, public witness receipt, and test inventory. Added a strict shared upload-preflight mode and corrected the stale Markdown submission summary so it agrees with the Pages primary and its negative verdict.
2. **Pass 2 — bugs/edge cases:** found the infinity-as-NaN gate defect; added regression tests for `+Inf`, `-Inf`, and finite nonzero/out-of-range outside-footprint values. Kept the NaN-outside allowance only in the explicitly generic legacy/research API. The command-line submission preflight and site checker are strict.
3. **Pass 3 — original requirements:** rechecked the no-copy rule, lane stop, holdout/canary limits, run-card requirement, download-versus-submit status, executive guide, official source boundaries, experiment budget and selector separation. No new geological lane or slot was selected. The fresh unique TIFF requirement remains unmet because satisfying it while following the binding literal gate is impossible; no workaround is represented as success.

## Integration with the updated main branch

While PR #50 was open, `main` advanced through PR #48, which integrated the separate PIEDFRONT parallel session. This branch was synchronized with that updated `main` to make PR #50 mergeable. The PIEDFRONT artifacts were **not** generated or experimentally changed in this repository-review/tooling-hardening session; their existing run card remains negative because the dense public witness still triggers the literal duplicate stop. The integrated site now serves 19 zeros-outside TIFFs, all research-only. The PIEDFRONT HOLDOUT-DTI remains a local evaluator result, not an organizer score.

## Verification record

The initial system Python did not include NumPy or pytest. An ignored `.venv` was created from `requirements.txt` (no environment files tracked). Final integrated-branch verification: **186 tests passed** with **103 nonfatal Rasterio/Affine pending-deprecation warnings**; `scripts/check_site.py` passed on all **19 served zeros-outside TIFFs**; all **8 pinned input hashes** verified; the pinned R0 parent proof passed; the strict CLI reread the existing SPRINGALIGN primary and passed **9 format gates**; an internal-link audit of the four main HTML pages found **156 local links with 0 missing targets**; `compileall`, the `make validate` dry run, run-card mirror equality/JSON validation, and the PR-diff `git diff --check` passed. The CLI/site results are format checks only, not uniqueness clearance or competition results. The machine-readable session run card is available at [`downloads/repo_review_run_card_20261024.json`](downloads/repo_review_run_card_20261024.json) (the canonical working copy is `evidence/repo_review_run_card_20261024.json`). No leaderboard, submission portal, quota, organizer receipt, or non-GitHub official source was accessed. Rasterio/Affine warnings are nonfatal and unrelated to validation semantics.

## Official/manual-review references

- [DrivenData problem/metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — not fetched in this review.
- [DrivenData competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — not fetched in this review; official source required for the absent feature stack.
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — repository link; not newly fetched in this review.
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and [DOE GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391) — official source leads; availability, contents and license were not rechecked.
- [EPSG:32611](https://epsg.io/32611) — CRS reference link, not newly fetched.

Source links above are provided for manual review and are not represented as newly verified facts in this session. See [`IRREGULARITIES.md`](../IRREGULARITIES.md) and [`NEXT_STEPS.md`](NEXT_STEPS.md) for data-use, registry-policy, access and publication blockers.
