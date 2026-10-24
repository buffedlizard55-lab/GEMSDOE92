# NEXT_STEPS — after the 2026-10-24 LCS session (supersedes everything below for action purposes)

## Decisions only the operator can make (in this order)
1. **Confirm the uniqueness policy** (`registry/uniqueness_policy.json`, decisive tier S). It is the one judgment call in this session: thresholds unchanged, nothing dropped silently, but the *set of rasters* the
   test applies to was tiered because the literal all-registry rule cannot be passed by any file (a random file fails it against 51 rasters). To change it: edit `decisive_tier`, run `make site`.
2. **Paste the verbatim prompt and score list** into `ledger/raw_paste.txt` and the README standing brief (the reconstructions are flagged IR-92-01).
3. **Confirm that reading public DrivenData pages with a fetch tool is acceptable** (IR-92-07); earlier sessions refrained citing the terms.

## The file and what to do with it
* `docs/downloads/GEMSDOE92-lcs-consensus-37654-20261024-58fd2c77-zeros.tif` is OK TO DOWNLOAD and OK TO SUBMIT (policy S); slot verdict **negative** under the pre-registered holdout rule, which is degenerate for this file (IR-92-06).
  It is an *exploration arm* at R0's exact budget: the live score difference to 0.2778 isolates the effect of lane consensus + uniqueness caps (same N, spacing and exclusion rule).
* **Before any upload re-run the registry scan** (`scripts/fetch_registry_cache.py` → `registry_digests.py` → `registry_gate.py`): sibling sessions may have added rasters.

## Highest-value experiments, in order (each is one weekly slot; the human selector decides — three per week)
1. **PROBE — R0 minus isolated skeleton fragments** (`python scripts/build_singleton_probe.py`; 28,935 dots). 8,719 of R0's dots (23.2 %) sit on isolated 1-px components of H19-5 (59.7 % on components ≤ 10 px) and no scored raster removes them.
   Score change ≈ (n/D)·(0.0556·(1−k̄) − 0.944·c): **+0.024 if those dots carry zero credit, 0 at c = 0.056, −0.036 at c = 0.134**. One receipt measures their credit directly. It is a lane duplicate (R0 subset): a *measurement*, not a lane candidate.
2. **LCS (this file)** — receipt vs 0.2778 at matched budget; then update the credit model with the result (the board is a 4-decimal group-testing instrument: ±1 % on a group's credit).
3. After receipts: if the probe shows fragment dots are worthless, **apply the fragment rule inside every future lane** (it is a 23 % false-positive reservoir); if LCS ≥ R0, raise the consensus weight and widen the voter set; if LCS < R0, the lane-concordance premise (ρ +0.60…+0.83) did not transfer to dot-level precision — record it as a negative.

## Research queue (ranked; none is claimed)
1. **Catalogue-trained U-Net with masked-halo-aware thresholding** (the organizers' own approach, `drivendataorg/gems-prize-reference-solution`). Highest upside, high cost: needs GPU hours; the sandbox is 2 CPUs / 3.9 GB. The leaderboard cluster at ≈ 0.33 is consistent with thresholded catalogue-trained models (inference, not evidence).
2. **Lidar-derivative scarp detectors validated on public expert picks** (the #5 team's stated approach, forum 11531): needs USGS 3DEP 1 m DEM access (`1m_DEM_links.csv`) — **not reachable from this sandbox's shell** (only github.com / PyPI / npm).
3. **Fold-pure holdout**: catalogue exclusion computed from visible faults only; requires per-fold lane rebuilds. Until then the repository has no instrument that can rank a file honouring the 3-px rule (IR-92-06).
4. GeoDAWN survey line / tie-line metadata (USGS release doi 10.5066/P93LGLVQ) for an artefact-mimic filter — obtainability from this sandbox not verified.

## Standing facts to reuse (all verified this session; see `docs/WHY_R0_0_2778.md`)
* Known faults are masked, "new fault" = any pixel not captured by USGS/INGENIOUS, pooled single Tversky, same metric in all rounds, truth sources undisclosed (forum 11516 / 11536 / 11550 / 11556 / 11527).
* Break-even credit ≈ 0.056 per dot; random placement ≈ 0.023; R0 ≈ 0.134; independent lanes 0.065–0.119 (MODEL on CLAIMs).
* Registry scope: 102 repos, 924 distinct rasters; blankets = 63.

---

# NEXT_STEPS — after the 2026-10-24 ANASIG session

## Current status (supersedes the collar section below for action purposes)

**ANASIG f45 is the primary download; verdict negative / NOT CLEARED.** Locally lane-unique (worst forward 0.550, |ρ| 0.547 over 24 local rasters; surface |ρ| 0.024), format-valid (10/10 gates), HOLDOUT-DTI 0.004967 [0.004098, 0.005940] (Δ vs R0 +0.000961 [+0.000168, +0.001814]) — but below the holdout best RELIEF p10 (paired Δ −0.001078 [−0.002034, −0.000112]), below R0 on the SGMC proxy (0.080556 vs 0.096060), and stopped by the binding public witness (17GEMSDOE E-proba, 100% footprint-positive; forward overlap 1.000 for these bytes, `evidence/public_witness_anasig.json`). **Do not spend a slot.** Full record: `docs/ANALYSIS_20261024_ANASIG.md`.

## Highest-value work, in order

1. **Operator decision on the literal public rule.** As written, a footprint-positive continuous raster makes every candidate a duplicate (proven, not hypothetical). Until resolved, no candidate in this repo can be both honest and "promote" under that rule — do not silently reinterpret it.
2. **Do not rebuild SCARPPOL or BREAKLINE doses.** Template keep-greedy is coverage-dominated (~90% shared keeps); any new DEM-ridge lane must change the keep stage too, or start from a non-R0 keep set, and must check final dots vs BREAKLINE/SCARPPOL *before* calling itself a new lane.
3. **Beat the holdout best honestly first.** Next lane must clear RELIEF p10 (0.006045) on `gems57-pooled-hide-v2` with paired CI excluding 0 vs R0 *and* stay <0.70 forward overlap vs BREAKLINE/SCARPPOL/R0 — ANASIG cleared uniqueness, not the holdout bar.
4. **Spring-pair alignment (not density)** is the one untested geothermal-vent construction left from this session's screens; it needs a strike-alignment screen before any build.
5. Keep `scripts/audit_public_registry.py` fail-closed: it now requires `--surface` for non-collar candidates (shared-tool fix this session).

---

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

## Late-session update — STRAINBREAK + GRAVCrest screen (2026-10-24)

Done this session: (1) fixed corrupt `public_registry_uniqueness.json` (missing comma, both copies); (2) closed the queued collar-on-SGMC item: **0.021192 vs R0 0.09606** — collar holdout gain does not transfer off-catalogue; (3) screened 7 surfaces under a pre-registered rule — GRAVCrest (rank 1) falsified, not built; (4) built STRAINBREAK f45/f60/f75 (3 experiments, budget exhausted): HOLDOUT-DTI up to **0.005487 (f60)**, dose plateau at f60=f75, SGMC 0.10516 < BREAKLINE 0.12611, locally unique (worst 40.0%); primary `h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif` (sha256 `000d0bd7…5c1f`), verdict **negative** (does not beat RELIEF p10 holdout best). Analysis: `docs/ANALYSIS_20261024_STRAINBREAK.md`; run card: `evidence/strainbreak_run_card.json`.

Next, in order: (1) **one organizer receipt** (human selector; BREAKLINE vs STRAINBREAK is now an explicit instruments-disagree choice — SGMC vs holdout — and cannot be resolved locally); (2) do not build a fourth STRAINBREAK dose (plateau measured) or retry GRAVCrest without a new gravity product; (3) shoreline-suppressed BREAKLINE only after a receipt prices far dots; (4) keep `scripts/check_site.py` + full pytest green whenever the served primary changes (primary is now `data-primary`-tagged; audits must carry `run_card` + `verdict`).
