# Fresh repository audit — 2026-10-25

## Decision

**Existing research TIFF: OK to download for research. DO NOT SUBMIT.** The request for a new, unique, submission-cleared TIFF remains unfulfilled. This audit produced no raster, geological experiment, new holdout result, organizer receipt, or weekly-slot selection.

The latest merged protocol review is [7059163e](REVIEW_7059163E.md). Its pinned witness is positive throughout the competition footprint, so any nonempty in-footprint candidate necessarily violates the unchanged literal overlap threshold. This is a **REGISTRY-MEASUREMENT** rejection proof against one pinned witness, not a claim that the entire public registry has been inventoried or that the candidate is physically similar to every competitor submission. Do not reinterpret the threshold as matched-budget overlap.

- **Research file:** [existing LISTRICDIP TIFF](downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif)
- **SHA-256:** `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e` (**REGISTRY-MEASUREMENT** receipt rechecked against file bytes)
- **Download decision:** yes, for research only; no, not for competition submission.
- **HOLDOUT-DTI:** not run in the latest protocol review or in this audit; no fresh score/CI/count is available.
- **ORGANIZER-CONFIRMED:** none; the local submission ledger has no receipt.

## Three-pass review

### Pass 1 — read the operating brief and inspect the project

Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_7059163E.md`, and its evidence/run card before acting. The repository has shared raster gates, holdout evaluator and submission writer, registry preflight, executive submission guide, byte-bound page status, pinned data manifest, and organizer-receipt ledger. No private evaluator or writer was created.

The raw training feature cache is absent in this checkout. The actual restoration entry point is `scripts/restore_inputs.py`; the prompt-mentioned `scripts/download_competition_data.sh` and `scripts/prepare_data.py` do not exist here. The official DrivenData data page is login-gated from this environment. Owner-mirror hash verification does not establish organizer provenance or redistribution permission; no cache restoration is claimed.

**Documentation defect found and fixed:** README's opening section promoted a later historical LISTRIC lane and a numerical result, while the current protocol review requires a rejection-only decision. README now places the current research-only / DO NOT SUBMIT status first, links the existing primary and latest review, and separates this from the historical archive. The older c5e renderer previously managed README and could overwrite its current first screen; it now manages only its own compatibility pages. Regression tests protect the independent README summary and session-start pointer.

### Pass 2 — validate behavior, format, provenance, and edge cases

The initial environment lacked NumPy and pytest. Project dependencies were installed from `requirements.txt` in ignored `.venv/`; no tracked competition input or model was changed.

Final checks on the merged working tree:

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest tests -q` | **499 passed**, 140 non-fatal Rasterio `PendingDeprecationWarning`s |
| `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` | **PASS**, all **82 served raster files** reopened and gated |
| `.venv/bin/python scripts/render_public_status.py --check` | **PASS**, primary hash and first-in-body status agree on configured public entry pages |
| `.venv/bin/python scripts/render_current_status.py --check` | **PASS**, compatibility panels are current |
| `make verify manifest ledger PYTHON=.venv/bin/python` | **PASS**: pinned R0 parent, data manifest, and 111-row ledger; no best receipt |
| `git diff --check` | **PASS** on reviewed changes |

The existing primary's stored automated validator receipt records one-band `float32`, `EPSG:32611`, shape `3730 × 3292`, matching 100 m transform, finite values in `[0,1]`, no NaN inside the footprint, zero outside, and reread SHA-256 match. Those are **AUTOMATED-FORMAT-CHECK** facts only; they do not clear uniqueness, establish model skill, or guarantee DrivenData accepts an upload.

The test run emits Rasterio's pending affine-multiplication deprecation warning. It is non-fatal but should be corrected in shared code and pinned dependencies, not silenced. Local checks do not prove a live GitHub Pages deployment; the prior review records a Pages build-mode/API permission limitation.

### Pass 3 — complete-request check and ranked hypotheses

The latest review's four-item hypothesis register is reproduced below to make the decision visible. Ranking is qualitative expected **incremental HOLDOUT-DTI utility**, discounted for ambiguity and cost; improvement is unknown and is not a projected score. The named transforms were searched against the local code/register only, not every competitor or the scientific literature. All are unimplemented, unvalidated, and blocked from execution by the required stop and absent numerical cache.

| Rank / cost | Layers and targeted signature | Why it could find a catalogue-missing fault | Difference from local methods | Named non-fault mimic |
|---|---|---|---|---|
| 1 / medium-high | Cached B2 RTP magnetic texture: bidirectional, multiscale texture-restoration registration across trial traces, seeking coherent signed along-trace displacement. | A buried/degraded splay might offset magnetic fabric without a clear topographic scarp. | Existing Euler/source localization, analytic-signal and listric crest methods do not explicitly restore and reciprocally match magnetic texture across a trace. | Separate lava flows or intrusive contacts; require reciprocal matches, held-out windows, scale stability, lithologic-contact nulls, and reject survey seams. |
| 2 / medium | B2 RTP two-sided, detrended directional semivariogram change point, with B13 gravity only as an independent ablation. | A buried basement-domain boundary could change fabric covariance despite weak amplitude contrast. | Local field consistency and tilt/curvature methods are not multi-lag covariance-domain tests. | Basalt-domain boundaries and survey artifacts; demand directional/lag stability and covariance-matched nulls. |
| 3 / high | B2 RTP complex-wavelet phase-dislocation pairs stable across wavelengths and not dependent on amplitude gradients. | A subtle basement-fabric offset could create a phase slip without a strong edge or surface scarp. | Existing XPHASE compares fields; this would test within-field fabric slips and translation consistency. | Remanent-magnetization change, interfering sources, gridding seams, or phase singularities; use amplitude screening and phase-randomized surrogates. |
| 4 / high | B12 elevation and B19 slope; relief/aspect-conditioned optimal-transport distance between elevation-increment distributions across a front. | Distributed deformation may affect geomorphic distribution tails after sharp scarps degrade. | Existing drainage-convergence/curvature and relief gates do not compare matched increment distributions. | Lake Lahontan shoreline terraces, fan age, and erodibility; use elevation/relief-matched nulls and reject contour-following anomalies. |

No candidate was tested on the holdout, no feature-alone AUC was computed, and no TIFF was placed. The top option cannot be called viable: the protocol requires stopping before any candidate generation, band identities are not reverified from an available cache, and lawful input provenance remains unresolved. New official data are not needed for the four stated proposals, which depend on the missing template stack; the official [USGS GeoDAWN catalog](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) is the source pointer, not a source freshly retrieved here. A future authorized run must use shared visible-only buffered folds, pixel-exact masks, feature-alone leakage canaries, same-instrument controls, and an untouched outer split.

## GEMSDOE32 and leaderboard claims

At the pinned owner-page commit, GEMSDOE32 reports the `h33-h33-2-b2` process as B=2 catalogue-flank pruning of a dotted base, labels its estimate a **MODEL, not a score**, and says **UNSCORED / NO ORGANISER SCORE EXISTS** for artifacts represented on that page. This does not prove that the user never submitted later. The user's `0.2778` is therefore **CLAIM / USER-REPORTED / UNVERIFIED** absent a submission-page receipt. The likely mechanism—removing redundant predictions near mapped faults can reduce false-positive mass while retaining distance-tolerant coverage—is a hypothesis, not a causal explanation of an unverified organizer score.

The prompt's `0.3195` and `0.4413` are conflicting leaderboard snapshots and were not freshly retrievable. No local HOLDOUT-DTI here is represented as a live competition score or evidence of exceeding `0.2778`.

## Official source pointers and access boundary

- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611](https://epsg.io/32611)

Outbound retrieval here is limited to GitHub, npm, and PyPI; DrivenData forms/data, current leaderboard, NLR PDF, USGS, and GDR pages were not fetched during this audit. The official pointers are for manual review, not claims of fresh verification. The pinned GitHub receipts in [review 7059163e](REVIEW_7059163E.md) document which GitHub objects were retrieved and hash-checked.

## Ordered next steps

1. Keep every current TIFF link clearly marked **research-only / DO NOT SUBMIT** while the literal stop binds.
2. Do not run the top-ranked method or make a new surface until the active protocol explicitly resolves the universal witness conflict and supplies a lane. Do not privately reinterpret the rule.
3. After authorization, verify restored band identities/provenance and licenses; pre-register one method; run leakage canaries; use shared visible-only buffered holdouts/evaluator/writer; compare against a freshly rerun same-mask control; then test a locked outer split.
4. Fix the Rasterio affine deprecation in shared code and keep CI dependencies pinned.
5. Verify an actual Pages deployment, obtain current competition access/rules and authenticated organizer receipts, and then let a separate selector assess a slot under the actual cap.

## Run card

```json
{
  "hypothesis": "Conditional review only; top proposal is bidirectional multiscale magnetic-texture registration across trial traces.",
  "mechanism": "Reciprocally match B2 RTP texture across a trace and require coherent signed displacement across windows and scales.",
  "named_non_fault_mimic": "Separate lava flows, intrusive contacts, or survey seams.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "dti": null,
    "ci95": null,
    "withheld_positives": null,
    "status": "not run; protocol stop before any experiment"
  },
  "correlation_overlap_vs_registry": {
    "evidence_class": "REGISTRY-MEASUREMENT",
    "scope": "one pinned full-footprint witness; rejection only",
    "absolute_spearman": 0.010352227787484035,
    "forward_overlap": 1.0,
    "thresholds": {"absolute_spearman": 0.90, "forward_overlap": 0.70},
    "candidate_surface_generated": false
  },
  "raster_sha256": "91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e (existing research raster)",
  "validator_output": {
    "evidence_source": "review705_existing_primary_witness.json; existing raster only",
    "no_nan_inside_footprint": true,
    "values_in_0_1": true,
    "crs_matches": true,
    "shape_matches": true,
    "transform_matches": true,
    "submission_format_valid": true,
    "uniqueness_clearance": false
  },
  "submission_name": "GEMSDOE92-LISTRICDIP-updip50-20261025 (existing; not new)",
  "note": "Existing LISTRICDIP research raster; format-valid but fails literal overlap stop; do not submit.",
  "verdict": "negative"
}
```
