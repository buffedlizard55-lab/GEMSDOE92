# Follow-up repository review — 2026-10-28

## Decision

**No current TIFF is cleared for competition upload.** The TIPCOMP TIFF is available for research download only. Its file format is locally valid, but its promotion run card is negative: the pre-registered model lower-bound gate failed, fold-proper holdout did not beat its R0-recipe control, and the full-registry/dense-witness interpretation is not resolved. Do not use a weekly submission slot.

This review is documentation/guardrail work only. No geological experiment, holdout, new candidate raster, or slot selection was performed. The TIPCOMP experiment record already uses its 3/3 experiment budget; the current full feature cache is absent; and the referenced single-method lane paragraph is missing from the supplied prompt. The generated TIFF is retained as a negative/research result, not promoted.

## Why the GEMSDOE32 0.2778 entry is plausible (bounded conclusion)

The supplied focus-9 inventory lists GEMSDOE32's `h33-h33-2-b2` result as 0.2778. The repository classifies that value as an owner/user `CLAIM`, not an `ORGANIZER-CONFIRMED` receipt. A plausible metric-aligned explanation in the stored audits is that a sparse trace candidate was pruned away from mapped-fault neighborhoods and allocated to locations where it could receive distance-tolerant credit, avoiding some redundant false-positive mass. This remains a hypothesis about the mechanism, not a causal finding: the hidden labels and organizer receipt are unavailable in this checkout.

The observed 0.2778 `CLAIM` cannot be used as a certified ground truth or as an expected result. The current TIPCOMP values `0.3485` and `0.3109` are `MODEL` estimates, not scores. The candidate's fold-proper result is a tie with the R0-recipe control, so these projections do not prove that it beats GEMSDOE32 on the public leaderboard.

## Executive comparison — nine requested sites

The current landing page and [`nine-sites.html`](nine-sites.html) link to the pinned historical source files and list each site's highest entry. These are the highest supplied `CLAIM`s in the repository's 2026-10-28 inventory, not live verified leaderboard results. All peaks are marked study-only; the recorded historical registry scan found clones or excessive overlap. No prior peak should be uploaded again as a “unique” submission.

| Site | Highest supplied file | Supplied value | Status |
|---|---|---:|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 `CLAIM` | Reported identical dot support to GEMSDOE25; research only |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778 `CLAIM`** | Highest supplied value of these nine; reported clones; research only |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 `CLAIM` | Historical registry duplication reported; research only |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 `CLAIM` | Historical registry duplication reported; research only |

Score-estimator columns in the site's nine-site comparison are `MODEL` projections and must not be substituted for organizer results. The source links there are commit-pinned GitHub file links for manual review; they are not evidence that this session freshly re-downloaded every source or confirmed each claim with DrivenData.

## TIPCOMP artifact: status and audit facts

- Research-only TIFF: [`gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif`](downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif).
- Byte-bound run card: [`JSON`](downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json), SHA-256 `8f27b9d6478526d72a055f0a56c7c8f6db1d63f2f5c66233b7eedbf9937579cf`.
- The archived card labels the fold-proper value as `HOLDOUT-DTI`, evaluator `gems57-pooled-hide-v2`, 22,663 withheld positive pixels: 0.09617 [0.08521, 0.10665]. The same-card R0-recipe control is 0.09775 [0.08590, 0.11077]; paired difference is −0.00158 [−0.01787, +0.01469]. Because the paired CI includes zero, this is not a holdout win. These are prior recorded values, not independently re-run in this follow-up.
- The card's `MODEL` estimates are 0.3485 (published-128 model) and 0.3109 (26-claim refit). Its refit bootstrap q05 is 0.2688, below the pre-registered 0.2778 bound, and the experiment verdict is `negative` / `submission_eligible: false` (IR-1028B-4).
- The archived PI-1 inventory measurement reports 0.68485 worst 3-px dot overlap and 0.18171 maximum sampled absolute rank correlation across 165 local registry rasters. This scoped measurement is not a complete external registry scan and does not resolve the project's conservative dense-witness/continuous-surface interpretation. It is therefore not a global uniqueness certification.
- Local format gates are separate from science and registry gates. A format pass only confirms the raster's grid/range encoding against the local template; it does not confer upload eligibility.

The repository landing page now makes the TIPCOMP download available only under an explicit **DO NOT SUBMIT** warning. Historical name/note metadata remain for audit and are not instructions for portal entry.

## Three review passes

### Pass 1 — inspect and validate

1. Read the README, persistent session prompt, charter, current reviews, run card, readiness records, renderer, validator, site checker, and nine-site inventory.
2. Created an ignored local virtual environment from `requirements.txt` after initial test commands showed `pytest`/`numpy` were missing. No environment artifacts are tracked.
3. Ran the TIPCOMP format CLI; its actual TIF was format-valid (11/11 gates) but output correctly retained a non-submission warning. Ran the generated-site checker over 127 served rasters.
4. Ran the full tests: **791 passed, 19 skipped** before adding the new review regression test (see Pass 2).

### Pass 2 — consistency and safety corrections

1. Found a visible status contradiction: README described TIPCOMP as needing a selector decision even though its machine run card was `negative` and `submission_eligible: false`; the TIPCOMP subpage similarly suggested a selector might override a failed mandatory threshold.
2. Replaced the README lead with one unambiguous state: **research download only; do not submit**, preserving the run card's failing gate and model-vs-score distinction.
3. Updated the TIPCOMP executive summary to label its TIFF as research-only, state the negative verdict at the top, and distinguish a future generic submission guide from eligibility for this candidate.
4. Updated `scripts/render_safe_review.py`, the shared renderer for the active landing page, to show the TIPCOMP artifact and its byte-bound disposition without implying promotion. The renderer checks the artifact's SHA-256 and refuses a non-negative/non-ineligible TIPCOMP card.
5. Corrected `validate_submission.py` to look for an artifact-adjacent run card first rather than describing every newer file using the unrelated legacy VARIO card. It remains fail-closed and never authorizes a slot. Legacy fallback behavior is retained for compatibility.
6. Added a regression test asserting the landing page and TIPCOMP summary show the matching-hash artifact as **DO NOT SUBMIT**, and asserting the recorded lower-bound/paired-CI failure conditions.

### Pass 3 — final verification and boundaries

Completed after the changes:

- `PYTHONPATH=vendor .venv/bin/python scripts/render_site_v3.py` regenerated the evidence-bound landing pages and status feeds.
- `.venv/bin/python -m pytest tests -q` → **792 passed, 19 skipped**, 171 warnings (Rasterio deprecation/georeferencing warnings; no test failures).
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` → **SITE CHECK PASS (127 served raster(s) gated)**; the primary remains negative.
- `.venv/bin/python validate_submission.py docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif` → all **11 format gates PASS** and exact SHA-256 match, followed by `DO NOT SUBMIT: byte-bound run card ... verdict=negative; ... submission_eligible=false`. Exit code 1 is intentional for a non-eligible candidate, not a format failure.
- `git diff --check` and README/run-card SHA/status assertions pass after cleanup. The candidate TIFF bytes were not edited.

## Protocol scope and blockers

No new 3–5-hypothesis ranking or experiment was started. The supplied protocol constrains the work to a single method paragraph that is absent, and the prior TIPCOMP session's three-experiment budget is already exhausted. The 19-band cached feature stack is not in this checkout. Starting a new experiment without the missing lane and required shared data would violate the requested protocol. The current repository includes historical hypothesis documents; they are not new proposals or fresh validation.

The project also has a policy ambiguity: whether a dense continuous registry surface is counted as a dot set for the stated 70%/3-px uniqueness stop. The code must continue to disclose literal and matched-budget interpretations; do not select the interpretation that produces the preferred result. The current TIPCOMP measurement cannot be called globally unique until a complete registry and governing representation rule are available.

The failed-in-this-sandbox initial commands (`python3 -m pytest`, `scripts/check_site.py`) lacked installed Python packages. Installing pinned project dependencies in ignored `.venv/` made local test execution possible. Outbound access available to this agent did not permit fresh access to DrivenData, USGS, DOE GDR, Dropbox, or the public leaderboard. No live values, data availability, licensing, submission cap, or organizer acceptance are asserted here.

## Official/manual-review links

These are the project's official-source references for manual checking. They were not live fetched in this follow-up; links alone are not represented as source verification.

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem statement and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data page (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official GEMS Prize reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE/NLR competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS GDR submission #1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

## Next-session order

1. Read `README.md`, `SESSION_PROMPT.md`, `docs/PROJECT_CHARTER.md`, this review, and `docs/NEXT_STEPS.md`.
2. Obtain and provenance/license-check the shared competition cache and complete registry snapshot via an authorized source; do not substitute the catalogue copy in `data/bridge/labels.tif` as independent truth.
3. Resolve the missing method-lane paragraph and dense-witness overlap representation rule before any further experiment.
4. Only with a new authorized experiment budget, preregister genuinely untried candidate hypotheses, run each feature-alone leakage canary, and run the shared fold-visible buffered holdout before placement.
5. Keep the download label and upload eligibility separate; do not consume a portal slot unless mandatory evidence passes. Record any actual organizer score only from a submission-page receipt.
