# Session review — 2026-10-28 (branch `arena/e57e6a90-gemsdoe92`)

## Executive summary

**DO NOT SUBMIT. No file is cleared for upload.** This session generated **no new TIFF**, ran **no holdout experiment** and used **no weekly slot**. The reasons are measured below, not asserted.

| Question | Answer | Evidence |
|---|---|---|
| Which file should I download and submit? | **None.** No file is cleared. | Every candidate fails at least one gate (table below). |
| Is any GEMSDOE site's file unique? | **No.** All 36 pairs among the nine focus sites exceed the 70% overlap limit in at least one direction. | [pairwise receipt](downloads/focus9_pairwise_recheck_14f85876.json) |
| Highest owner-reported score | GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` = **0.2778** (CLAIM, no organizer receipt) | [GEMSDOE32 site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) |
| Can a unique file be made that beats 0.2778? | **Not demonstrated, and not testable here.** Two blockers: the holdout needs the 19-band training-feature cache (absent), and the duplicate rule's representation question is unresolved (below). | §3, §5 |
| Is the "single method paragraph" the prompt refers to present? | **No.** It is referenced ("the single method paragraph below") but not supplied. Without it no experiment lane is assigned. | prompt text |

### Why the literal rule blocks everything — and what the official reference actually submits

The [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) (default branch, commit `aebe92f7c8a990f0e3443451b7a825d9afd6336b`, cloned this session) writes a **continuous float map** of predicted probabilities. Its notebook says *"it may be advantageous to threshold this map for better scoring"* and visualises `y_final > 0.1`. The reference solution's own output is therefore a probability surface, not a binary dot set. (The official `example_submission.tif` was not fetched; it is not on the sandbox allowlist.)

The pinned witness [`17GEMSDOE_E-proba-multiscale`](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/6fc71d19d49dca4960d5434bd81b6dd06fcc030a/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) is exactly this kind of surface. Re-verified this session:

* codeload tarball, file SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be` (matches the pin).
* float32, 3292×3730, EPSG:32611, finite on 5,167,373 cells; **every finite cell is positive** (min 0.00046, max 0.984, median 0.219).
* top-37,654 cutoff = 0.8438.

Under the **literal** reading (“every positive witness cell is a dot”), any nonempty in-footprint candidate has overlap 1.0 > 0.70. That is the existing stop, and it reproduces.

Under a **top-K** reading (the witness's dots are its top-K cells, K = candidate dot count), overlap is small:

| Candidate (REGISTRY-MEASUREMENT, 3-px Euclidean disk) | Dots | Literal overlap | Top-K overlap | Limit |
|---|---|---|---|---|
| Riesz primary `gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif` | 50,000 | 1.000 | **0.0070** | 0.70 |
| GEMSDOE32 `0.2778` file (`data/parent_R0_zeros.tif`) | 37,654 | 1.000 | 0.0366 | 0.70 |

Source: [`downloads/review_20261028_overlap.json`](downloads/review_20261028_overlap.json), produced by `scripts/measure_registry_overlap.py`.

**This is a policy question, not a finding of compliance.** The protocol forbids silently choosing a reading. The top-K reading is one witness only, so it does not establish uniqueness against the other registry rasters. It is listed as a decision for the policy owner (§5).

### Per-site table (owner-reported CLAIMs; nothing here is an organizer score)

Estimate column: no validated estimator exists in this checkout (see §4). A number in that column would be a projection, and the protocol forbids writing projections as scores.

| Site | Highest owner-reported file (submission name) | CLAIM | Estimate | Unique vs other 8 focus sites? | Cleared to submit? |
|---|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | not estimable | **No** | **No** |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | not estimable | **No** | **No** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | not estimable | **No** | **No** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | not estimable | **No** | **No** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | not estimable | **No** | **No** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | not estimable | **No** | **No** |
| **GEMSDOE32** | **`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`** | **0.2778** | not estimable | **No** | **No** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | not estimable | **No** | **No** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | not estimable | **No** | **No** |

Scores are transcribed from the prompt. The GEMSDOE27 entry uses the highest of its three listed files (0.2449 over 0.2250 and 0.2190). Owner pages and the scores themselves were not re-fetched this session.

## Three review passes

* **Pass 1 (build and verify):** wrote the overlap tool and receipt, ran the Riesz validator and the full test suite (780 passed, 19 skipped before; 787 passed after).
* **Pass 2 (bugs and assumptions):** the top-K routine padded binary witnesses with zero background (a spurious 1.0 for the 0.2778 file), fixed and covered by a regression test. Also corrected: an overstated "bimodal" claim, speculation about mimics, a validator output taken from the wrong script (the decision gate is the root `validate_submission.py`), a non-existent file link, a session-time figure that was never logged, and an "official example" claim the reference notebook does not support.
* **Pass 3 (against the request):** re-ran the hashes and the full suite, and checked every number in the executive summary against a receipt (`review_20261028_overlap.json`, the run card, or the pairwise receipt). Items still open are listed in §6 and §8.

## 1. Verification log (every fact, its source, and whether it was re-checked here)

| # | Fact | Source | Checked this session |
|---|---|---|---|
| V1 | Reference solution outputs a continuous float map and suggests thresholding | [README](https://github.com/drivendataorg/gems-prize-reference-solution), [notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb) | Yes (cloned, read) |
| V2 | Witness file SHA-256 `ab0a0a62…` and grid | [pinned witness](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/6fc71d19d49dca4960d5434bd81b6dd06fcc030a/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) (codeload) | Yes (hash matched) |
| V3 | Witness: all 5,167,373 finite cells positive; top-37,654 cutoff 0.8438 | computed from V2 | Yes |
| V4 | Riesz primary SHA-256 `d168c7d2…`; validator 11/11 gates | `docs/downloads/gemsdoe92-rieszlbm2-…-zeros.tif` | Yes (`validate_submission.py` run) |
| V5 | Riesz holdout 0.0380 [0.0310, 0.0447] vs R0 recipe 0.0978 [0.0859, 0.1108], 22,663 withheld | [run card](downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json) | Read (not re-run) |
| V6 | Holdout vs leaderboard CLAIMs: Spearman 0.131 (n = 128) | same run card, `instrument_validity` | Read (not re-run) |
| V7 | GEMSDOE32 file: 37,654 binary dots (`1.0`), 0 on catalogue, 0 within 2 px of catalogue, 2,171 at 2–3 px, 35,483 > 3 px | `data/parent_R0_zeros.tif` (SHA-256 `c55bafc4…`, matches [`registry/data_manifest.json`](../registry/data_manifest.json)) | Yes (computed) |
| V8 | Pruning the 2,171 band dots would give a file that is 100% within 3 px of GEMSDOE32's own dots | derived from V7 | Yes (arithmetic: every remaining dot is an original GEMSDOE32 dot) |
| V9 | Riesz dots within 3 px of GEMSDOE32 dots: 55.4% (< 0.70) | computed | Yes |
| V10 | All 36 focus-site pairs duplicate in at least one direction | [pairwise receipt](downloads/focus9_pairwise_recheck_14f85876.json), `holdout_run: false` | Read (not re-run) |
| V11 | Test baseline: 780 passed, 19 skipped (pre-change) | `pytest tests` | Yes |
| V12 | Training-feature cache (19 bands) is not in the checkout | file search of `/` | Yes (absent) |
| V13 | `data/bridge/labels.tif` is byte-identical to `existing_faults.tif` (both SHA-256 `7ba308cc…`) | sha256sum | Yes |

Not verified, and not claimed: the leaderboard values (0.4413 and 0.3195 conflict in the prompt; the public leaderboard is not monitored, per [DrivenData terms](https://www.drivendata.org/termsofuse/), which the repo already records); the official metric and rules PDF (`docs.nlr.gov` and DrivenData are outside this sandbox's network allowlist); GEMSDOE32's claimed lineage (d2.8 → h27-4 → h33-2-b2) and its 0.2778 score. The lineage and score are owner-reported.

## 2. Why 0.2778 is the highest owner-reported score (PhD-level, bounded by V7)

Measured: the GEMSDOE32 file is a **binary** 37,654-dot set (exactly the budget) with **no dot on the catalogue** and **no dot within 2 px** of it. Counted by distance to the catalogue: 0 dots within 2 px, 2,171 in the 2–3 px band, and 35,483 more than 3 px away. (Counts only; no distribution shape was tested.)

The mechanism that the evidence supports:

* The competition's evaluator excludes known USGS/INGENIOUS fault pixels (a DrivenData community reply, as recorded in the repo's earlier review [SITE_REVIEW_20261026](SITE_REVIEW_20261026.md) and linked [here](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2); not re-fetched this session). Dots on the catalogue earn nothing, so removing them from the budget is free.
* The absence of dots within 2 px is consistent with a 2-px exclusion collar, and the 2–3 px band is left intact. Whether those 2,171 dots are a weakness is an **untested hypothesis**: the holdout that could test it cannot be run here (V12).

The effect of the other owner-reported steps (kernel-aware dotting, a supervised skeleton) cannot be verified from this checkout.

**The uniqueness rule makes the obvious improvement illegal.** Pruning the 2,171 band dots (V8) produces a file that is a 100% duplicate of GEMSDOE32. Incremental edits of the best file cannot be submitted under the literal 70% rule. A genuinely different lane is required.

## 3. Can we beat 0.2778? — what was tested and what was not

* Tested: the Riesz candidate (the repo's latest unique file). It passes the top-K and pairwise uniqueness checks. Its own holdout (0.0380) is far below R0 (0.0978), and the protocol says not to spend a slot without beating the holdout best. **Rejected.**
* Not testable: any new candidate. Validation requires the shared 19-band feature stack, which is not in this checkout (V12). Without it no holdout, canary or leakage test can run, so no candidate can meet the protocol.
* Not tested here: the leaderboard instrument itself. The holdout's Spearman with CLAIMs is 0.13 (V6), so even a holdout win is weak evidence for a leaderboard win.

## 4. Score-estimate policy

The only numeric estimate for the best candidate in the repo is a MODEL value of **0.3216** for the Riesz file. That model is calibrated to owner CLAIMs, its R0 counterfactual is 0.2728 under the same model, and it has not been validated against an organizer receipt. It is recorded only as a MODEL estimate and is **not** a score. No per-site estimate is given, because no validated estimator exists.

## 5. Decisions required from the policy owner (not resolved by this session)

1. **Representation:** does "dots" mean every positive cell of a probability surface (literal, universal stop) or a top-K/thresholded dot set (top-K reading, Riesz 0.0070 vs the 0.70 limit)? The official reference's continuous output supports the need to decide explicitly.
2. **Method lane:** supply the single method paragraph the prompt refers to. Without it, no experiment lane can be assigned.
3. **Data access:** the 19-band training-feature cache and a complete registry snapshot are needed for any holdout. DrivenData data requires login (the [data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)). Those files are not in this sandbox and cannot be downloaded from it.
4. **Weekly slot:** the cap is 3 per week per the [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), which is not reachable from this sandbox. Confirm it on the submission page before any selection.

## 6. Irregularities flagged for review

* **I1 — Conflicting leaderboard numbers:** the prompt gives the GEMSDOE leaderboard high as both 0.4413 and 0.3195. Neither was verified here.
* **I2 — Missing method paragraph:** referenced twice, never supplied.
* **I3 — Validator binds to a stale card:** `validate_submission.py` reads `evidence/vario_run_card.json` (an archived lane). For any other file it prints "not the byte-bound run-card primary," so its message is misleading even though its exit status (1, DO NOT SUBMIT) is correct. Existing tests depend on this path, so it is flagged rather than rewired here.
* **I4 — `labels.tif` is a copy of the catalogue:** `data/bridge/labels.tif` is byte-identical to `existing_faults.tif` (V13). It is not an independent truth label set. Any "holdout" built on it would test against the catalogue, not hidden truth.
* **I5 — Stop reading is an interpretation:** the universal stop follows from treating a continuous surface as dots (see the executive summary). A stop that can't be overturned by any candidate is not a measurement of duplication; it is a consequence of the chosen reading.
* **I6 — Holdout–leaderboard weak alignment:** Spearman 0.131 (V6).
* **I7 — Riesz card reports a MODEL 0.3216** alongside a holdout below R0. The MODEL figure must not be cited as a score.
* **I8 — Pairwise receipt is a stored record:** `focus9_pairwise_recheck_14f85876.json` was not re-run in this session.

## 7. What changed in this session

* `scripts/measure_registry_overlap.py` — the two-reading overlap measurement (Euclidean 3-px disk; top-K ranks only positive cells). The first draft let zero-valued background fill top-K for binary witnesses; it was caught by a check on `data/parent_R0_zeros.tif`, fixed, and covered by `tests/test_registry_overlap_20261028.py` (7 tests).
* `docs/downloads/review_20261028_overlap.json` — the receipt for the Riesz file against the witness.
* `docs/downloads/review_20261028_arena_e57e6a90_run_card.json` — the run card.
* This document, and a pointer in the [README](../README.md) status box.

No new TIFF, holdout run, leakage canary, experiment or weekly slot. Experiments used: 0 of 3. Session time was not logged; no experiment was started, so the budget was not approached.

## 8. Next steps (owner-ordered; each blocked on §5)

1. Resolve §5.1 and §5.2 in writing. Until then, record every file as research-only.
2. Restore the shared feature cache and verify its provenance and license against the DrivenData terms.
3. Only then, pre-register 3–5 untried hypotheses (candidate: a 3-px catalogue collar on a *different* base lane, which avoids the R0 duplicate problem; V8 shows a same-base variant cannot pass).
4. Run the feature-alone canaries and the buffered holdout before any placement.
5. Use a separate selector for any slot.

Official sources for manual review: [competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/), [problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR #1391 (INGENIOUS)](https://gdr.openei.org/submissions/1391), [EPSG:32611](https://epsg.io/32611).
