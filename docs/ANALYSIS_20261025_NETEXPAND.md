# NETEXPAND analysis — why R0 "0.2778" tops the owner ladder, and what we built (2026-10-25)

Branch `arena/a7cdad14-gemsdoe92`. Pre-registration: [HYPOTHESES_20261025_NETEXPAND.md](HYPOTHESES_20261025_NETEXPAND.md).
Run card: [netexpand_run_card.json](downloads/netexpand_run_card.json). All scores below are
**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, strict draw-blind fold-visible)
unless labelled **CLAIM**. There is **no ORGANIZER-CONFIRMED score** for any file in this repo.

## Executive summary — download / submit status (read this first)

**✅ OK TO DOWNLOAD (format-valid, portal-safe encoding) · ⛔ DO NOT SUBMIT / DO NOT SPEND A WEEKLY SLOT**
(`verdict: negative` under the parallel-run protocol — reason §4.3).

| Arm | HOLDOUT-DTI [95% CI] | Download (one click) | SHA-256 |
|---|---|---|---|
| `netexpand_far` (primary) | **0.177976 [0.163109, 0.193227]** | [TIF](downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.tif) · [ZIP](downloads/gemsdoe92-netexpand-netexpandfar-37654-20261025-47bacc15-zeros.zip) | `a1bc94252d17f7a2…` |
| `netexpand` (conservative, d>2) | 0.146798 [0.134181, 0.159612] | [TIF](downloads/gemsdoe92-netexpand-netexpand-37654-20261025-f705be3a-zeros.tif) · [ZIP](downloads/gemsdoe92-netexpand-netexpand-37654-20261025-f705be3a-zeros.zip) | `48efe78365aff4a6…` |
| `nocontext` (ablation) | 0.115566 [0.102084, 0.129132] | [TIF](downloads/gemsdoe92-netexpand-nocontext-37654-20261025-d0b7d6e4-zeros.tif) | `5e3a8e7c21da8d75…` |

Submission name (primary): `gemsdoe92-netexpand-netexpand_far-20261025-47bacc15` ·
Note (≤140): `NETEXPAND far: same LOQO pure-crest surface, dots >4px off catalogue; 37654 dots 2.8px`.
How a future cleared file is submitted: [executive summary](executive-summary.html) / [SUBMIT guide](SUBMIT.html).
Validate any file yourself, no human inspector needed:
`python3 validate_submission.py docs/downloads/<file>-zeros.tif` → must print `FORMAT PASS` (11/11 gates);
it always also prints the registry stop — format pass ≠ slot clearance.

## 1. Why/how did GEMSDOE32 `h33-h33-2-b2` get "0.2778"? (verified line-by-line)

**It is not an organizer score.** Fetched live this session, the GEMSDOE32 page
(https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) labels the file
**UNSCORED**, states *"NO ORGANISER SCORE EXISTS for this or any artifact in this repository"*,
and quotes a **projected** 0.2747 (MODEL). `registry/parents/R0.json`: `receipt: null`.
The prompt's 0.2778, 0.3195 and 0.4413 are therefore **CLAIMs** (⚠️ IRREGULARITY F1 below).

What *is* verified (re-measured this session from SHA-256-pinned rasters): R0 is the end of a
strictly nested emission-editing chain on one detector — H19-5 121,131 px ⊃ D1.5 60,069 ⊃
D2.8 44,090 ⊃ SOLO 40,199 ⊃ R0 37,654 (every descendant ⊂ H19-5; SOLO→R0 deletes exactly
2,545 dots ≤2 px from the catalogue; NN spacing ≥2.828 px). Under the official metric
(distance-weighted Tversky, α=0.2 FP, β=0.8 FN, 300 m triangular kernel — DrivenData
problem page https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/;
reference solution https://github.com/drivendataorg/gems-prize-reference-solution), truth
credit saturates per truth pixel while each dot pays α·FP. Thinning to kernel spacing +
pruning the masked catalogue halo removes zero-yield mass; the marginal bar is
`k > α·DTI ≈ 0.056` at DTI 0.2778. **Conclusion (PhD-level, mechanistic): R0 is an
emission optimum on a fixed ranking. Surpassing the CLAIM requires a better detector
ranking at identical emission rules — which is what NETEXPAND tests. Whether any file
beats 0.2778 on the organizer's hidden labels can only be proven by an organizer receipt.**

Owner-site score pattern (prompt inventory, all CLAIMs): dotted/thinned H19-5 descendants
0.24–0.28 ≫ continuous surfaces and far-from-catalogue novelty lanes 0.00–0.16. This is
consistent with hidden faults being concentrated near mapped systems (splays/extensions)
and with the metric's redundancy penalty — the two effects NETEXPAND exploits directly.

## 2. What NETEXPAND did

45-feature 3-branch quadrant-LOQO HGB: KNICKLOQO 30 + LISTRIC 4 + FAULTNET self-excluded
visible-catalogue network context 5 + NEW 6 (gravity ASA & coherence B11/B13/B18;
standardized magnetic ASA & coherence B9/B14; RTP variance suppression B2; MT change-point
B17×B15), pure ASA/coherence/listric 1-D crest, 37,654 dots ≥2.8 px, zeros-outside float32
(shared `submission_writer`; all-finite, `nodata=None` — the fix for the portal
*"Predicted values must be in range [0, 1]"* error, whose verified causes are float32
sentinel −3.4e38 leaks / NaN nodata handling). Inputs restored autonomously via
`scripts/restore_inputs.py` and SHA-256-verified (`training_features.tif 4371c82e…`);
no DrivenData/Dropbox contact, no manual step. Named non-fault mimics: range-front
lithologic contacts, equant plutons, thick non-magnetic Lahontan sediments, playa salinity fronts.

## 3. Holdout results (strict hide-and-recover; context & models refit on visible only)

| Arm / control | HOLDOUT-DTI [95% CI] | Paired Δ vs arm (primary) |
|---|---|---|
| **netexpand_far** | **0.177976 [0.163109, 0.193227]** | — |
| netexpand | 0.146798 [0.134181, 0.159612] | far − netexpand **+0.031177 [+0.026004, +0.036243]** |
| nocontext | 0.115566 [0.102084, 0.129132] | context effect **+0.031232 [+0.020624, +0.042818]** |
| control_knick_far (emission-matched) | 0.111601 [0.098294, 0.125051] | far − ctrl_far **+0.066375 [+0.053280, +0.079413]** |
| control_knick | 0.109069 [0.096130, 0.122483] | new-features effect (nocontext−knick) **+0.006497 [+0.000528, +0.011908]** |
| control_H19_5 / control_R0 | 0.096757 / 0.004006 | far − H19-5 +0.081219 [+0.069063, +0.094129] |

Leakage canaries (Rule 4, both draws): max symmetric AUC **0.7775** (`cx_logtip`) ≤ 0.90 — PASS,
all 45 features. Format gates: **11/11 PASS** on independent disk re-read (EPSG:32611,
3730×3292, float32, min 0.0 max 1.0, 0 NaN, 0 on-catalogue).
Ablations attribute the gain cleanly: network context ≈ +0.031 (dominant), new ASA/coherence/
curie/MT features ≈ +0.006 (small, real), far emission ≈ +0.031 on this model but only +0.0025
on the control — i.e. the context model wastes collar mass that far emission reclaims.

**Instrument caveats (must not be elided):** (i) by construction of the buffered draw every
withheld truth pixel lies >3 px from visible catalogue (measured min 3.16 px), so the holdout
cannot reward 2–3 px collar dots that may score on organizer truth — `netexpand` (d>2) is the
conservative organizer-facing sibling; never submit both. (ii) `netexpand_far` nominally exceeds
the recorded FAULTNET `netfar` 0.175147 by +0.0028 — **within overlapping CIs and not paired**
(same folds/evaluator, different run): consistent with parity, **not** proven superiority.

## 4. Uniqueness — the binding failure

### 4.1 vs parent lineage (organizer-facing novelty): PASS
Forward 3-px overlap vs R0 0.278–0.347, H19-5 0.386–0.399, D2.8 0.347–0.358; surface |ρ| ≤ 0.19.
Byte-, pixel- and support-distinct from every GEMSDOE32-lineage file. **Not a copy.**

### 4.2 vs complete local registry (123 byte-unique rasters): FAIL (lane drift)
`netexpand` 0.7615 vs FAULTNET `netctx`; `netexpand_far` 0.7844 vs FAULTNET `netfar`;
`nocontext` 0.8145 vs KNICKLOQO standalone — all > 0.70 (dot-field literal reading).
Sharing FAULTNET's context fields + KNICKLOQO base makes any top-N emission land on the
same catalogue-adjacent ground; the pure crest did not differentiate enough because the
probability ranking dominates. Per Protocol Rule 1 this is a **duplicate lane: logged, stopped.**
3/3 experiment budget consumed; no 4th rescue experiment was run.

### 4.3 Verdict
`negative` for all arms; **0 weekly slots used**. This is a deliverable negative result with a
positive scientific core: the detector ranking is the best yet measured in-repo on the strict
instrument, but it is not a *new lane*. Selector guidance (human step, Rule 6): if one slot is
ever spent on this mechanism family, prefer `netexpand` (d>2, conservative) or `netexpand_far`
(holdout-max) over the older FAULTNET files they dominate on identical folds — after resolving
the lane/operator policy (§5 F2) and recording the receipt in `ledger/submissions.csv`.

## 5. Irregularities flagged for review (no hallucinations)

- **F1 — "0.2778 / 0.4413 / 0.3195" are CLAIMs.** GEMSDOE32's own page says UNSCORED / no
  organiser score exists; no receipt in `ledger/`. Leaderboard values were not independently
  verified (login wall). Never compare HOLDOUT-DTI to these numbers as like-for-like.
- **F2 — Literal registry rule is unsatisfiable as written.** Pinned dense witnesses
  (e.g. 17GEMSDOE E-proba, 5,167,373/5,167,373 positive footprint px in prior audits) force
  literal overlap 1.0 for *any* non-empty raster. This session reports the operative
  dot-field/matched-budget reading **and** literal counts; uniquely, NETEXPAND fails even the
  operative reading locally, so F2 does not decide this verdict. Operator must still resolve F2
  before any future lane can be "promoted" under a literal reading.
- **F3 — No lane paragraph was supplied** in the prompt ("single method paragraph below" is absent);
  NETEXPAND was self-assigned as Rank-1 of the pre-registered set and stayed inside it.
- **F4 — Public fleet not re-scanned** this session (local failure already decisive, fail-closed);
  `registry_rasters_checked=123` local only. Prior public scans (1,368–1,451 rasters) remain in `evidence/`.
- **F5 — Data provenance:** competition rasters come from owner GitHub mirrors, SHA-256-pinned,
  not organizer-authenticated downloads (sandbox allow-list); redistribution terms unchecked
  (pre-existing flag in `registry/session_manifest.json`). Official sources for manual review:
  DrivenData #306 pages/data tab, NLR rules PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf,
  USGS GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and,
  GDR #1391 https://gdr.openei.org/submissions/1391, INGENIOUS https://gbcge.org/current-projects/ingenious/,
  EPSG:32611 https://epsg.io/32611, Tversky index https://en.wikipedia.org/wiki/Tversky_index.

## 6. Next lane (documented, not run — budget exhausted)

**NETEXPAND-R (repelled emission):** same probabilities, but ≥35% of dots constrained
>3 px from the union of FAULTNET+KNICKLOQO supports (dual-pool greedy as in LISTRIC `dual35`),
re-scored on the identical holdout to price the novelty constraint; or drop distance/tip context
fields (highest canaries, most FAULTNET-identifying) keeping density/strike only. Expected:
uniqueness ≤0.65 at a holdout cost to be measured — promote only if it still beats `control_knick`
paired. Then GDR-GEOTHERMOMETER-FIELD (Rank 2, `HYPOTHESES_20261025_NETEXPAND.md`).

## 7. Limitations & what I need

No DrivenData auth/receipts, no GPU (HGB CPU only, 3 GB RAM), no non-GitHub network
(USGS/GDR/Earthdata unreachable from sandbox), no live leaderboard/weekly-cap verification.
Needed from operator: (1) F2 dense-witness policy decision; (2) one organizer receipt for any
submitted file to calibrate holdout→live mapping; (3) weekly-cap confirmation at selector time.
Nothing else blocks the pipeline: restore → stack → holdout → deploy → finalize is fully autonomous.
