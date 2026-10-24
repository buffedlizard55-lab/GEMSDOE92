# NEXT_STEPS — after the 2026-10-24 registry stop

## Current status

One new method was evaluated: a 200–300 m collar around visible mapped faults, excluding the parent R0 dots' 300 m halo. It passes file-format gates and improves the local catalogue hide-and-recover measure, but the expanded public registry scan triggers the protocol's literal duplicate stop. **The result is negative. Do not use a weekly submission slot.** The TIF remains available as a negative deliverable, with the homepage clearly saying format-valid/downloadable but not cleared for submission.

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`; buffered whole-component hide/recover; 8 spatial folds, seeds 20 and 30; 22,663 withheld positives; 1,000 paired 20 km block bootstrap draws): candidate 0.046866 [0.040216, 0.053315]; R0 0.004006 [0.003424, 0.004690]; paired Δ +0.042860 [+0.036122, +0.049357]. This is not a DrivenData score.

## Critical uniqueness finding

The initial in-repository 14-raster audit was too narrow and produced an incorrect selector-positive result. It is superseded. A broader scan of current default branches in 102 public `buffedlizard55-lab` repositories found 1,629 relevant TIFF paths / 1,285 unique Git blobs; 1,279 single-band rasters matched the target grid and were compared. The candidate's pre-placement surface and final dots both have **1.000000** forward 3-px overlap with accessible registry rasters; **131/1,279** exceed the 70% threshold. Worst absolute Spearman is below the 0.90 threshold (0.421367 on the surface; 0.492957 on the final dots), but overlap alone triggers the stop rule.

A concrete witness is [11GEMSDOE `gems-structural-area06-v1.tif`](https://github.com/buffedlizard55-lab/11GEMSDOE/blob/main/docs/downloads/gems-structural-area06-v1.tif), for which all candidate dots are within 3 px of positive support. Another witness is 17GEMSDOE's full-footprint `E-proba-multiscale` surface. Under the user's literal instruction, these are binding; this project does not waive the test because a raster has dense support. Full measurements/scope are `evidence/public_registry_uniqueness.json`.

The scan is broad, not exhaustive: historical branches, private repositories, other owners, unlinked GitHub Pages files, zip-only assets, and assets outside the searched directories may be missing. This caveat does not undo a duplicate already found.

## Highest-value work, in order

1. **Do not submit this candidate.** Keep it as a negative deliverable; preserve the cross-site audit and the corrected negative verdict. The build script must fail closed if the matching global audit is missing or says duplicate.
2. **Keep the registry scan repeatable/current.** `scripts/audit_public_registry.py` queries current public default-branch trees, downloads submission TIFF blobs to ignored `.cache/`, verifies Git blob SHA and size, and records failures. Run it periodically; never claim it covers deleted/history/site-hosted files.
3. **Resolve the literal overlap gate with the operator/policy owner outside this agent.** Until then, any candidate with >70% forward 3-px overlap against any registry raster is a duplicate and must stop. Do not silently substitute arrival-only overlap or exempt dense rasters.
4. **Calibrate with an organizer receipt.** The local evaluator recovers mapped catalogue segments; live target is private/new faults. A human may choose a different candidate only through the separate selector after reviewing policy and weekly quota. Upload/receipt entry are human-only.
5. **Build an off-catalogue validation instrument** before further candidate experiments. Score it separately from HOLDOUT-DTI and label it PROXY, never private test performance.
6. **Obtain the missing GeoDAWN stack through the official competition data tab** if authorized, hash/size/grid verify it, and check license/data terms. The feature stack is absent from this checkout's cache; band-specific hypotheses remain untested.
7. **Resolve redistribution terms** for tracked `data/` and releases; see `IRREGULARITIES.md`.
8. Keep both submission guides, homepage, run card, validator tests and status strings synchronized. A format pass means downloadable, not selected/submittable.

## Candidate queue and experiment budget

The five-hypothesis list is `docs/hypotheses_visible_collar_20261024.md`. Candidate 1 was tested and stopped by the duplicate gate. The lane protocol says stop when a duplicate is found; do not continue by testing more placement variations under this lane. Any future lane requires a fresh session, distinct hypothesis, pre-placement surface registry test, and the stated 3-experiment/2-hour budget.

## Data and evidence boundary

The bridged sample submission, catalogue, and parent are hash-verified against owner mirrors. That proves the local bytes match those pins; it does not authenticate them with DrivenData or establish redistribution permission. Official competition data and upload can require login. No credentials are stored or requested. A HOLDOUT-DTI value is never an organizer score.

## Parallel-session update — BREAKLINE (2026-10-24)

The band-based queue was in fact tested by a parallel session with a restored stack (`scripts/restore_inputs.py`): BREAKLINE f33/f38/f45 (`docs/ANALYSIS_20261024.md`). Consequences for the queue above: (1) **first action next session:** run `scripts/audit_public_registry.py` against `BREAKLINEf45Ltop` — it is unique on the 18-raster local registry (worst 55.0% vs R0) but un-scanned publicly, and the collar precedent shows dense public rasters can stop any candidate under the literal forward-overlap rule; record the result either way. (2) The off-catalogue instrument requested in item 4 partially exists: the USGS SGMC bedrock-fault control (62,703 px) is implemented in `scripts/report_breakline_proxies.py` (BREAKLINE +31% vs R0; collar candidate not yet scored on it — cheap, do it). (3) Blocker 0 unchanged: 36 BUILT / 0 RECEIPT in `ledger/`; one organizer receipt still outranks every local instrument disagreement (collar's catalogue-proximity holdout 0.0469 vs BREAKLINE's discovery-oriented SGMC gain price different things). (4) Do not build a fourth BREAKLINE dose or re-litigate screened-out lanes (BASEMENT-STEP/Band 15 SGMC AUC 0.378; pure seismicity too smooth; radiometrics AUC≈0.50).

## Latest review: decisive BREAKLINE public witness

See [current review](REVIEW_CURRENT.md). The queued public check now rejects BREAKLINE: 100% forward overlap with the hash-verified 17GEMSDOE full-halo raster. Every nonempty in-footprint candidate fails the current literal gate against this witness. This supersedes the pending-public-scan status above; the full registry was not rescanned. Zero new experiments or submission slots; resolve the policy before more placements.

## Follow-up registry stop (2026-10-24)

**2026-10-24 follow-up — BREAKLINE is now a confirmed duplicate under the literal registry rule.** A live, Git-blob-verified witness check compared one raster from 11GEMSDOE and five from 17GEMSDOE. BREAKLINE final dots have **100% forward 3-px overlap** with the dense 17GEMSDOE E-proba raster. This is REGISTRY-MEASUREMENT, not a competition score. The actual BREAKLINE pre-placement surface was not supplied and was **not checked**; no collar surface was substituted. A final-dot failure alone requires stop. No new experiment or TIFF was generated; no slot used. See [follow-up review](REVIEW_REGISTRY_STOP_20261024.md) and [run card](evidence/breakline_registry_stop_run_card.json). **Download for research only; do not submit.**
