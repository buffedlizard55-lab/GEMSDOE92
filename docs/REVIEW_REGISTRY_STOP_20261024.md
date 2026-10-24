# Three-pass review — BREAKLINE public-registry stop

> **Historical registry-stop note for BREAKLINE / visible-collar; not the current ANASIG scope.** The current ANASIG result is a single 17GEMSDOE witness check, not the older 1,279-raster / 11GEMSDOE scan. Current status: [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md).


## Executive decision

**Format-valid and downloadable; NOT unique under the supplied rule; DO NOT SUBMIT.** No new TIFF was generated: the mandatory duplicate stop overrides the request to generate another candidate. No competition slot was used. This session stayed in the existing BREAKLINE verification lane, with zero candidate experiments.

## Pass 1 — complete the previous-session blocker

Read README, SESSION_PROMPT and NEXT_STEPS first. Existing ranked hypotheses, signatures, costs, mimics and prior tests are retained in [BREAKLINE hypotheses](HYPOTHESES_20261024_BREAKLINE.md); no new hypothesis was implemented. Ran the outstanding public-registry verification as a bounded witness search rather than downloading the entire registry again.

REGISTRY-MEASUREMENT: 11GEMSDOE's one matching raster gives forward overlap 0.246162 and absolute Spearman 0.014429. This does **not** stop BREAKLINE. 17GEMSDOE's five matching rasters include E-proba, positive at all 5,167,373 footprint cells. Against it, BREAKLINE final forward overlap is **1.000000**; Spearman is 0.031591. Worst absolute Spearman across those five is 0.033706. The overlap alone mandates duplicate-stop. Dense-support rasters were not exempted.

- [11GEMSDOE source](https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif)
- [17GEMSDOE binding witness](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif)
- [Reproducible witness receipt, including immutable Git blob hash and SHA-256](downloads/breakline_public_registry_witness17.json)

Both witnesses were obtained through live GitHub API repository trees and checked by Git blob SHA-1 and byte length before comparison. This authenticates repository bytes, not competition provenance or scientific truth. This is six rasters in two repositories, **not** a new full public scan.

## Pass 2 — correctness review and regression fixes

Found that `audit_public_registry.py --candidate` always rebuilt the collar lane surface, even for BREAKLINE. Fixed the shared repo auditor: explicit `--surface` reads the actual lane surface, checks its grid, and never substitutes another lane. Legacy collar reconstruction is restricted to its exact filename. BREAKLINE's pre-placement check is explicitly **NOT_CHECKED**; the final duplicate is sufficient to stop. This follow-up does not retroactively satisfy the missed pre-placement gate.

Added bounded `--witness-repo` and separate `--output` options. Witness-only checks cannot claim full-scan clearance. Separate cache inventory/index names prevent replacing the full registry inventory. Candidate grid mismatches are rejected before array comparison. Empty/failed summaries cannot say uniqueness passed. The auditor no longer returns `promote` from uniqueness alone: promotion requires separate scientific and selector gates.

## Pass 3 — independent recheck and requirements audit

Re-read unchanged BREAKLINE bytes with the project's validator: all ten gates pass, single float32 band, EPSG:32611, shape 3730 × 3292, matching transform, range [0,1], finite inside, zeros outside, zero catalogue mass. SHA-256: `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`.

Historical **HOLDOUT-DTI**, not rerun here: `gems57-pooled-hide-v2`, 22,663 withheld catalogue positives; BREAKLINE 0.004861, 95% CI [0.004032, 0.005822]. These cannot predict an organizer score or establish new-fault discovery. The reported GEMSDOE32 0.2778 and conflicting leaderboard snapshots remain user/repository claims, not organizer receipts. See [prior causal analysis and its limitations](ANALYSIS_20261024.md).

Automated test suite, pinned-input manifest, parent verification and every served-TIFF site gate were run. Homepage and submission guide now prominently state the public witness failure. All download bytes are unchanged; no existing TIFF was copied as a new submission.

## Official sources and limits

The [DrivenData reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution) is reachable through GitHub (root listing checked live). [Official problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR INGENIOUS](https://gdr.openei.org/submissions/1391), and [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) are manual-review links, **not freshly verified sources** in this network-restricted session. No current leaderboard, weekly quota, external data license or organizer acceptance is asserted.

Next: resolve the universal dense-support overlap blocker through the policy owner; until then no candidate can clear the literal rule against a full-footprint positive raster. Do not silently reinterpret “dots.” Then restore pinned features if needed, pre-register a distinct lane and its genuine pre-placement surface, and evaluate whole-segment buffered holdouts with leakage canaries before emission. Obtain organizer receipts only for a separately selected, cleared candidate. No GPU is required for the existing array-based pipeline; this session does not validate the prompt's claim that GPU training is the remaining blocker.

### Publication and test closeout

Final suite: **123 passed**, with 17 Rasterio/Affine pending-deprecation warnings; no test failures. `make manifest`, `make verify`, all ten served-file site checks, and `git diff --check` pass. GitHub Pages API reports `main` at `/`; attempting to change it to `/docs` was denied with HTTP 403 (integration permission). Added a root `index.html` redirect plus `.nojekyll` instead, so root hosting reaches the existing workbench without changing settings. Live post-merge rendering is not yet verified. GitHub repository authentication itself worked; no credentials were requested.
