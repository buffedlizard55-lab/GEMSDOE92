# Repository review — 2026-10-30 UTC

## Executive decision

**No TIFF is cleared to submit. Do not spend a competition slot.** This review created no raster, ran no geological experiment, and did not select or promote a submission. It deliberately stops before experiment design because the supplied parallel-run protocol says to stay in “the single method paragraph below,” but the request contains no uniquely assigned method paragraph, and the repository records the previous three-experiment allowance as exhausted. Inventing a lane or silently resetting that budget would violate the stated protocol. This is a negative result, not a claim that a higher leaderboard score is impossible.

The repository does contain a unique research TIFF, [DEXP-Kostrov E3](downloads/gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17-zeros.tif), but it is **DO NOT SUBMIT**. Its recorded holdout and format checks do not override its recorded literal registry duplicate stop, uncertainty over official input redistribution provenance, or separate-selector requirement. The file is already in the repository; it was not generated in this review.

## Evidence and current artifacts

| Item | Evidence / finding | Interpretation |
|---|---|---|
| Highest supplied score among the nine focus sites | GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`: `0.2778` **CLAIM** | Highest owner-reported value among the nine in the supplied inventory. No organizer receipt tying this score to the exact file was found in the checked-in evidence. |
| Best later GEMSDOE92 owner report | `lbmc1`: `0.2784` **CLAIM** | Newer than the focus-nine `0.2778` report, but still not an organizer-confirmed receipt. It should not be conflated with the requested nine-site winner. |
| Current site-generation source | `scripts/render_site_v3.py` fixes the published primary to the 2026-10-28 RIESZ-LBM2 card; `docs/downloads/current_submission.json` and `readiness.json` also point to RIESZ-LBM2 | These are internally consistent with the generated site but older than several 2026-10-29 artifacts. |
| Newer research files surfaced by `scripts/check_site.py` | DEXP-Kostrov, MARUSSI-TRISHEAR, ADMITRELAY, and LIDAR-SINTERVALVE are all reported as negative / DO NOT SUBMIT; the checker calls LIDAR-SINTERVALVE `CURRENT-20261029` | The top-level README emphasizes DEXP, while `SUBMISSION_READY.md` emphasizes MARUSSI. This is a material editorial/currentness mismatch; there is no single unambiguous newest-candidate pointer across all entry points. |
| DEXP-Kostrov E3 | **HOLDOUT-DTI** `0.117438 [0.104226, 0.130267]`, `gems57-pooled-hide-v2`, `22,663` withheld positives; paired vs R0 recipe `+0.019688 [0.008586, 0.031664]` | A local hide-and-recover metric, not a leaderboard prediction or organizer score. |
| LIDAR-SINTERVALVE far arm | **HOLDOUT-DTI** `0.178619 [0.163071, 0.193316]`, same evaluator and withheld-positive count | Higher than the DEXP holdout, but paired improvement over the prior `control_netexpand_far` is only `+0.000643 [-0.002525, +0.004321]`; the interval includes zero. It is below the documented repo holdout best (`relay_conduit`, `0.184485`, same evaluator family). These values do not estimate its competition leaderboard score. |
| DEXP uniqueness | The archived 8-owner/2,262-raster audit records operational PI-1 pre-placement overlap `0.65405`, final-dot overlap `0.63890`, and respective maximum absolute correlations `0.409836` and `0.043992`; the same card records literal overlap `1.000` against a dense witness | PI-1 passes the numeric thresholds, but the protocol's literal positive-pixel reading fails. No alternate interpretation is treated as a waiver. These are archived registry measurements, not a fresh registry rescan in this review. |
| TIFF format | DEXP bytes hash to `80d66b0590b26ddc9ac56af3964289f63f9c07c80931e3e69a7089dbabbc6faf`; local inspection reports one-band `float32`, EPSG:32611, shape `3730×3292`, finite values in `[0,1]`, and two unique values. `scripts/check_site.py` reports `SITE CHECK PASS (132 served raster(s) gated)` | This addresses the prior out-of-range error for local format checks only; it does not establish organizer acceptance or submission eligibility. |
| Tests | `.venv/bin/python -m pytest tests -q`: `834 passed, 19 skipped`, `171` warnings | Regression coverage passed. Warnings are recorded, not suppressed. This does not reproduce historical experiments. |
| Official online status | Not checked live from this environment | The outbound network allowlist does not include DrivenData, USGS, DOE GDR, or the listed GitHub Pages domains. Thus leaderboard values `0.3195` / `0.4413`, portal rules, source availability, and publication freshness remain unverified here. |

## Why GEMSDOE32 may have reached 0.2778 — and what can be said safely

The repository's forensic notes characterize the referenced raster as a 37,654-dot, spatially thinned H19-5-derived prediction and describe its allocation between proximal off-catalogue corridors and more distal blind structures. That is a plausible mechanism for a strong score under a distance-buffered fault metric: detections near a withheld mapped fault can earn partial credit through the 300 m kernel, while excessive predictions away from faults incur a false-positive cost; thinning can reduce redundant nearby mass. The Tversky asymmetry (`alpha=0.2`, `beta=0.8`) makes missed positives more costly than false-positive mass under the documented convention, so a broad-but-controlled corridor prediction can outperform a sparse local-only map.

Those are explanations consistent with the archived raster and metric, **not demonstrated causes of the reported 0.2778**. The site score is only a **CLAIM** absent an organizer receipt, and the private competition labels are unavailable for an exact score decomposition. The `0.3195` and `0.4413` values in the prompt likewise were not independently verified here. No defensible score projection can be derived from these inputs alone. Holdout DTI is useful for relative research selection, but should not be relabeled as an estimated leaderboard score.

## Focus-nine executive table

The site inventory and archived focus-nine audit identify GEMSDOE32 as the highest supplied claim among the requested nine. The row-safe recheck [`focus9_pairwise_recheck_14f85876.json`](downloads/focus9_pairwise_recheck_14f85876.json) reports that **all 36 pairs** trigger the pairwise duplicate criterion in at least one direction or via correlation; prior numeric metrics changed for 35 pairs, so use this corrected recheck rather than earlier pairwise values. None of the nine is distinct from all other eight under the stated pairwise gate. The historical TIFFs are not cleared to re-submit. Exact file links and additional fields are maintained in [`docs/nine-sites.html`](nine-sites.html). The score values below are **CLAIMs**, not organizer receipts.

| Site | Best supplied submission / reported score | Estimate for a new submission | Distinct from all other nine? | Download / submit guidance |
|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5…` — `0.2477 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE25 | `dotted-h19-5-d2-8…` — `0.2600 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE27 | `topo-gap-closure-t-v2…` — `0.2449 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE28 | `h36-1-rung30-blind-r1…` — `0.2710 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE30 | `d28-poisson300m-offcat…` — `0.2600 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE31 | `h27-4-solo-d28…` — `0.2708 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE32 | `h33-h33-2-b2…` — `0.2778 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Highest supplied nine-site claim; historic file not cleared to submit |
| GEMSDOE33 | `h33d-analog-tip-stepover…` — `0.2632 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |
| GEMSDOE36 | `anderson-geothermal-pinn…` — `0.2750 CLAIM` | Not established | **No** — fails at least one directional-overlap/correlation comparison | Research comparison only; do not submit historic file |

This table intentionally does not fabricate numeric leaderboard estimates. The existing site's `MODEL` diagnostics are model outputs, not organizer scores; they need a fresh independent calibration audit before being presented as useful individual score estimates.

## Passes performed

### Pass 1 — Implement/reproduce and verify

No method implementation was permitted by the incomplete lane assignment and exhausted recorded experiment budget. Installed the pinned `requirements.txt` dependencies into ignored `.venv`, ran `scripts/check_site.py`, tested the two relevant GeoTIFF byte hashes and grid metadata, and ran the full automated test suite. All checks completed as reported above.

### Pass 2 — Review assumptions and omissions

Found a real status-currentness issue: top README, `SUBMISSION_READY.md`, generated `docs/index.html`, and the current status JSON do not identify the same primary candidate. The site generator and its tests intentionally bind the current primary to RIESZ-LBM2, while the site checker lists newer research artifacts. This review documents the mismatch rather than silently editing a generated page without updating its evidence-bound renderer and tests. Also found that model/score wording is liable to confuse `MODEL`, owner `CLAIM`, `HOLDOUT-DTI`, and `ORGANIZER-CONFIRMED`; this report labels them separately.

### Pass 3 — Recheck against the request

The nine-site table and download guidance are present; the top supplied claim is identified without calling it verified. No new, unique TIF is advertised as submission-ready, because the protocol does not authorize a new lane and existing recorded candidates fail at least one mandatory gate. No slot was spent. A literal registration stop is preserved. No official live-source claims were added.

## Official sources for manual review

The following are the official/reference URLs supplied in the project request. They were **not live-fetched in this review** because these hosts are outside the configured outbound allowlist; current availability and content are therefore not asserted here.

- [DrivenData competition overview and problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- [DOE/NLR submission rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and [DrivenData terms of use](https://www.drivendata.org/termsofuse/).
- [Official DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).
- [USGS GeoDAWN airborne magnetic and radiometric survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391), and [EPSG:32611 definition](https://epsg.io/32611).

## Required next work / limitations

1. Resolve the top-level candidate/status-source mismatch by making one evidence-bound primary artifact the same across `scripts/render_site_v3.py`, `docs/index.html`, `docs/downloads/current_submission.json`, `docs/downloads/readiness.json`, `README.md`, and `SUBMISSION_READY.md`; regenerate with the shared renderer and retain tests. Continue to mark it research-only unless every promotion gate passes.
2. A future research run needs a uniquely assigned method paragraph and a valid experiment budget. Do not infer a method lane from a list of prior concepts, privately fork the shared evaluator/writer, or exceed the stated cap.
3. The complete cached feature stack is absent from this checkout; `data/` contains bridge/demo files and two parent rasters rather than the full training feature stack. No full independent rerun of historical DTI results was possible in this review.
4. Complete a fresh pre-placement and final-dot registry scan against the actual current registry if and when a new authorized candidate is built. Keep both literal and operational overlap readings visible until the rule is settled; the literal witness currently blocks all nonempty rasters.
5. Obtain and pin official input provenance and redistribution rights. The presence of mirrors/artifacts in Git does not prove licensing or organizer provenance.
6. Validate any score-estimator by prospective, lineage-isolated data and mark it `MODEL`; never display it as a submission score. Do not poll/scrape the leaderboard contrary to its stated terms.
7. The requested “no human input” conflicts with the protocol's separate human selector decision for weekly slot use. The safe automated project boundary is to validate and clearly report readiness, never to spend a portal slot without the required selector.

## Review run card

See [`evidence/review_20261030_run_card.json`](../evidence/review_20261030_run_card.json). It records no experiment or new TIFF, the reviewed DEXP raster hash, existing holdout/registry evidence labels, local validator outcome, and `verdict: negative`.
