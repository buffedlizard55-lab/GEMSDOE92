# Fresh repository audit — 2026-10-25

## Decision

**Existing research TIFF: OK to download for research. DO NOT SUBMIT.** The request for a new, unique, submission-cleared TIFF remains unfulfilled. This audit did not generate a raster, run a geological experiment, select a slot, or obtain an organizer score.

The binding pre-placement stop from [review 797e](REVIEW_797E507A.md) remains decisive: its pinned witness covers every footprint pixel, so every non-empty in-footprint prediction set violates the literal forward-overlap threshold. This is a **REGISTRY-MEASUREMENT** from one pinned witness and a rejection-only result, not proof of a complete registry inventory. Reinterpreting it as matched-budget clearance would break the active protocol.

- **Research file:** [existing LISTRICDIP TIFF](downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif)
- **SHA-256:** `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e` (checked against the stored receipt)
- **Download decision:** yes, for research only; no, not for competition submission.
- **HOLDOUT-DTI:** not rerun or recertified in this audit. No score is inferred from the prior artifact or from the leaderboard.
- **ORGANIZER-CONFIRMED:** none; the local submission ledger reports no receipt.

## Three-pass review

### Pass 1 — read the operating brief and inspect the project

Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_797E507A.md`, and `docs/HYPOTHESES_797E507A.md` before acting. The project has shared raster gates, writer/evaluator code, a registry preflight, a submission guide, a first-in-body public status panel, a pinned data manifest, and an organizer-receipt ledger. No private evaluator or writer was created.

The raw training feature cache is not staged in this checkout. The actual restoration entry point is `scripts/restore_inputs.py`; the prompt-mentioned `scripts/download_competition_data.sh` and `scripts/prepare_data.py` are absent. Competition data remain login-gated at the official data page, and owner-mirror hashes do not verify organizer origin or redistribution permission. The current audit does not claim those inputs were restored.

**Documentation defect found and fixed:** the first screen of `README.md` still promoted a later LISTRIC experimental lane and its numerical result, while the generated public status and pinned review said that no new unique submission was cleared. The README now states the rejection-only decision first, links the actual existing research TIFF, and distinguishes research download from submission eligibility. The older c5e renderer included README in its managed-page list and would overwrite this newer first-screen summary; `scripts/render_current_status.py` now manages only its own compatibility pages, while dedicated tests protect README's authoritative summary. Historical results below are explicitly secondary.

### Pass 2 — validate behavior, format, provenance, and edge cases

The local Python environment initially had no NumPy or pytest; project dependencies were installed in ignored `.venv/` from `requirements.txt`. This changes no tracked project inputs.

Fresh checks on this checkout:

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest tests -q` | **493 passed**, 140 Rasterio `PendingDeprecationWarning`s; no test failures |
| `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` | **PASS**, all **82 served raster files** reopened and gated |
| `.venv/bin/python scripts/render_public_status.py --check` | **PASS**, primary hash and first-in-body panel agree on all configured public entry pages |
| `make verify manifest ledger PYTHON=.venv/bin/python` | **PASS**: pinned R0 parent, data manifest, and receipt ledger (111 rows; no best receipt) |
| `git diff --check` | **PASS** on the final tracked/untracked review changes |

The existing primary's stored receipt records single band `float32`, `EPSG:32611`, shape `3730 × 3292`, matching 100 m transform, finite values in `[0,1]`, zero outside the footprint, and a reread SHA-256 match. This is format validation only. The authoritative site status panel prevents those checks from being mistaken for uniqueness clearance or organizer acceptance.

The `pytest` suite currently emits Rasterio's pending affine-multiplication deprecation warning. It is non-fatal, but should be resolved in shared code and pinned dependencies rather than suppressed. The current Pages API/deployment limitation described in `REVIEW_797E507A.md` also remains: local checks do not prove that GitHub Pages has deployed these bytes.

### Pass 3 — compare against the complete request and preserve next steps

Three ranked conditional methods already exist in [the hypothesis register](HYPOTHESES_797E507A.md). They are proposals only, not experiments or established discoveries:

1. **Directional magnetic semivariogram change point** — cached B2 RTP magnetic field; contrast lag-dependent, detrended along-strike covariance on opposite sides of trial lines. A blind basement domain boundary might change magnetic texture without a surface scarp. **Mimic:** basalt-flow or intrusive-rock contacts and survey noise. Medium cost; expected incremental value is uncertain and qualitatively highest of the three.
2. **Magnetic–gravity cross-bispectral phase coupling** — cached B2 RTP magnetic and B13 isostatic gravity; seek a cross-strike discontinuity in amplitude-normalized nonlinear phase coupling across scales. A boundary between source-depth regimes could perturb coupling missed by single-field derivatives. **Mimic:** volcanic compositional boundaries and gridding artifacts. High cost; low-to-medium, uncertain value.
3. **Relief-matched increment-distribution transport** — cached B12 elevation and B19 slope; compare cross-front elevation-increment distributions after conditioning on relief, aspect, and elevation. Distributed deformation could leave a subtle geomorphic signature after sharp scarps degrade. **Mimic:** lithologic erodibility differences, alluvial-fan age, and Lake Lahontan shoreline terraces. High cost; low, uncertain value.

The register documents why these transforms differ from the local implemented operators, and provides falsification suggestions. Their claimed novelty is limited to searches of the local repository and prior registers, not all public competitor projects. The cache is absent and the binding stop disallows the requested top-candidate evaluation now. Therefore **none is called viable or validated**; no feature-alone AUC, HOLDOUT-DTI, confidence interval, or candidate surface was computed. Continuing would contradict the active stop. The prior work also has repeated tuning against one holdout, so any future authorized experiment needs an untouched outer spatial test.

## GEMSDOE32 and score claims

The saved source-verification receipt says the GitHub-pinned GEMSDOE32 page describes the `h33-h33-2-b2` generation as pruning dots near its dotted base and labels itself `UNSCORED` / `NO ORGANISER SCORE EXISTS`. Therefore the prompt's `0.2778` remains **USER-REPORTED / UNVERIFIED**, not ORGANIZER-CONFIRMED. The repository does not establish causally why it got that external score. The plausible local metric mechanism (less redundant mass near known catalogue faults, more opportunity to cover other positives) remains a hypothesis, not proof.

The prompt's `0.3195` and `0.4413` leaderboard figures are conflicting snapshots and were not freshly retrievable in this environment. No claim here says a holdout value beats a live leaderboard score. See `docs/REVIEW_797E507A.md` for the source-pinned explanation and boundary.

## Trusted source links and access limits

- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR / INGENIOUS](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611](https://epsg.io/32611)

The sandbox's outbound allowlist permits GitHub, npm, and PyPI only. Competition forms, live leaderboard, rules PDF, USGS and GDR pages could not be fetched in this audit. Links are official starting points, not claims of fresh verification. The public reference solution repository and source receipts pinned in the previous review are separately hash-verified, but do not establish organizer scores or access to hidden labels.

## Ordered next steps

1. Keep all current TIFF links clearly marked **research-only / DO NOT SUBMIT** while the literal uniqueness stop remains binding.
2. Do not run the ranked top hypothesis or generate a new surface until the active protocol supplies an allowed lane and resolves the universal witness conflict without a private reinterpretation. Then pre-register only the selected method, verify feature-band identities and lawful input provenance, run individual leakage canaries, use the shared visible-only buffered holdout/evaluator/writer, compare to a freshly rerun same-instrument control, and test a locked outer split.
3. Fix the Rasterio affine deprecation in the shared implementation and keep CI dependencies pinned.
4. Obtain documented competition-data use/redistribution terms and an authenticated organizer score receipt through permitted access. Never equate a local holdout with a leaderboard score.
5. Verify an actual GitHub Pages deployment after merge; local static checks are not live deployment proof.
6. Only a separate selector, after every required gate passes and within the current weekly cap, can recommend a real submission slot.

## Run card

```json
{
  "hypothesis": "Conditional review only; top proposal is a magnetic directional-semivariogram change point on cached B2 RTP.",
  "mechanism": "Contrast detrended, lag-dependent magnetic covariance across trial boundaries to detect concealed basement-domain changes.",
  "named_non_fault_mimic": "Basalt-flow or intrusive-rock contacts; survey noise.",
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
    "evidence_source": "review797e_primary_witness.json; existing raster only",
    "no_nan_inside_footprint": true,
    "values_in_0_1": true,
    "crs_matches": true,
    "shape_matches": true,
    "transform_matches": true,
    "submission_format_valid": true,
    "uniqueness_clearance": false
  },
  "submission_name": "GEMSDOE92-LISTRICDIP-updip50-20261025 (existing; not a new submission)",
  "note": "Existing LISTRICDIP research raster; format-valid but fails literal overlap stop; do not submit.",
  "verdict": "negative"
}
```
