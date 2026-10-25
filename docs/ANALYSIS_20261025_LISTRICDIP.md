# LISTRICDIP — why the offset hypothesis lost, and what that says about 0.2778

Evidence class labels used below are not interchangeable. `HOLDOUT-DTI` is `gems57-pooled-hide-v2` on seeds 20 and 30 (22,663 withheld positive pixels, 1,000 paired draws, seed 520810). `CLAIM` is a number copied from a sibling site, not a receipt. `LEADERBOARD-SNAPSHOT` is a public page read, not a score for any file here. `PROXY` is an off-catalogue SGMC overlap, not the competition metric. `REGISTRY-MEASUREMENT` is a local or pinned-witness comparison. No projection is written as a score.

## What was tested

Pre-registration: `docs/HYPOTHESES_20261025_LISTRICDIP.md`. Operator: `gems/listricdip.py`. Runner: `scripts/run_listricdip.py`. Run card: `evidence/listricdip_run_card.json`.

The hypothesis was that a concealed 45–60° normal strand sits hundreds of metres up-dip of the basement-cutoff crest, and that a reversed-polarity antithetic sits 2.2–3.5 km down-dip. Catalogue worms and slope-break lanes lock onto the cutoff the USGS/INGENIOUS map already has. This lane does not. It is catalogue-free. Deployment zeros the catalogue at `d_cat > 2` px and spaces dots at 3.2 px so the 300 m DTI kernel does not count the same fault twice.

Three arms, the session budget:

| Arm | Dots emitted | Static `HOLDOUT-DTI` | Re-placed `d_visible > 2` `HOLDOUT-DTI` | SGMC `PROXY` |
|---|---:|---|---|---:|
| `updip50` | 37,654 (budget filled) | **0.005420 [0.004294, 0.006551]** | **0.048225 [0.039232, 0.056882]** | 0.040820 |
| `anti22` | 9,571 (budget not filled) | 0.001291 [0.000598, 0.002173] | 0.009696 [0.004249, 0.016321] | 0.034348 |
| `anti35` | 9,555 (budget not filled) | 0.001224 [0.000597, 0.002007] | 0.010025 [0.004411, 0.017090] | 0.034473 |

Paired static differences for `updip50`, same folds, 95% CI:

- versus parent `R0` 0.004006: **+0.001413 [+0.000062, +0.002699]** (CI excludes 0)
- versus `COULOMBLOQO` standalone 0.009220: **−0.003801 [−0.005358, −0.002278]**
- versus `KNICKLOQO` standalone 0.010788: **−0.005368 [−0.007248, −0.003621]**

It beats the thinned parent and loses to the repository holdout best. That is a negative result. It is not a slot recommendation.

## Why 0.2778 is not a target this file can claim

`GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` is reported on sibling sites as **CLAIM 0.2778**. That filename and that number were not on the public leaderboard page fetched 2026-10-25. The live public board that day showed #1 `xiaofanhu` **0.4413**, then 0.3916, 0.3904, 0.3724, 0.3539 ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)). Those figures are a snapshot. They are not receipts for this repository, and they are not a projection of what `updip50` would score if uploaded.

The byte-checked local cascade for the claimed file is emission geometry, not a new geological model: `H19-5` (121,131) → `D2.8` (44,090) → `SOLO` (40,199) → `R0` (37,654, `d_cat > 2`). Thinning dots inside the 300 m kernel and dropping pixels that sit on the mapped catalogue is what the sibling sites credit for the rise from a lower claim to 0.2778. Copying that raster is forbidden, and it is already in the registry.

A higher organizer score than 0.2778 is possible in principle: the public board is already above it. This session did not produce a file that beats the local holdout best, so it did not produce a file that should be spent to test that possibility. Local `HOLDOUT-DTI` 0.005420 is not 0.2778, is not 0.3195, and is not 0.4413.

## Why the mechanism failed

Two measurements, neither of which is a score, explain the loss.

1. **The up-dip shift is inside the kernel of the cutoff.** On the real stack the habitat (cover 400–1,100 m, off catalogue) is 1,599,385 pixels. The geometric shift has median 5.31 px (p10 3.71, p90 8.01), about 530 m. The competition kernel dies at 3 px (300 m). A large share of `updip50` dots therefore sit just outside, or on the shoulder of, a fault that coincides with the basement cutoff. Withheld catalogue segments are exactly that kind of fault. Shifting off them spends false-positive budget (α = 0.2) without buying the false negatives the hypothesis hoped to catch (β = 0.8). The paired gain over `R0` is real and small. The loss to knickzone and Coulomb lanes, which stay near the scarp the labels actually occupy, is larger and the CI excludes 0.

2. **Reversed polarity is rare, so the antithetic arms could not be the pre-registered experiment.** A 2–8 km regional basement gradient is opposed at `oppose > 0.5` by only a minority of high-gradient pixels (about 0.6% at 2 km, 3% at 4 km, 11% at 8 km; median oppose is 0). The pre-registered `oppose > 0.3` support is 221,759 pixels, but 3.2 px spacing on that support, after `d_cat > 2`, emits 9,571 and 9,555 dots, not 37,654. Padding with non-oppose pixels would have left the mechanism. Dropping spacing below 3.2 px would have stacked redundant false positives inside the DTI kernel. Both were refused. `anti22` and `anti35` then tied (0.001291 vs 0.001224). Distance is not load-bearing. The antithetic hypothesis, as specified, does not recover withheld segments.

The same-fold evaluation of the unthinned `H19-5` mask is 0.066289. That is not the previously published thinned Rule-2 figure 0.096757, and it is not budget-matched to 37,654 dots. `updip50`'s re-placed score 0.048225 loses to that unthinned mask (paired −0.018064 [−0.029586, −0.007215]). It was not compared, in this run, against a freshly re-thinned `H19-5`. The published Rule-2 leader in this repository remains `COULOMBLOQO` at about 0.1133–0.1139, from earlier run cards, not re-measured here.

SGMC off-catalogue `PROXY` for `updip50` is 0.040820 on 62,122 pixels more than 3 px from the competition catalogue. That is below the parent `R0` proxy near 0.096 recorded in earlier cards. The offset dots are not landing on the independent bedrock-fault traces either.

Leakage canaries: max symmetric AUC 0.5316, all ≤ 0.90. The low score is not a leaked label.

## Uniqueness

Local registry, 110 rasters under `docs/downloads`, `releases`, and `data` at scoring time: worst 3 px forward overlap **0.1968**, worst absolute Spearman **0.053**. Not a local duplicate. Final dots match the pre-placement screen, so the surface and the emission tell the same story.

After that screen, `main` gained `DRAINAGE-KNICK` (`ef6c27e3…`, 37,654 dots). A post-merge check of the written dots against that file is overlap **0.1892** (`updip50`), **0.0287** (`anti22`), **0.0286** (`anti35`). Stride-8 Spearman versus `updip50` is 0.025. Not a duplicate of that later raster. The 0.1968 figure is the scoring-time worst, not a claim that every future raster was scanned.

Pinned public witness `buffedlizard55-lab/17GEMSDOE` blob `374c88b1da2b803e2ed160de467fd71ae114010d` is positive on every footprint cell (5,167,373 / 5,167,373). Forward overlap is **1.0**. `stop_required: true`. `unique_under_literal_rule: false`. That witness rejects every nonempty in-footprint raster, including the parent. It is recorded. It is not hidden. This session did not scan 102 repositories; the witness is a rejection, not a clearance.

## Decision

`verdict: negative`. `submission_eligible: false`. Weekly slots used: 0. Experiments: 3 / 3.

`updip50` is **OK to download for research** (format gates pass, values in [0, 1], 0 NaN, 0 catalogue mass). It is **not OK to submit**. The antithetic siblings are the same decision, with the additional fact that they could not fill the pre-registered budget without abandoning the mechanism.

## What not to retry

- Do not copy `R0` or `h33-h33-2-b2`.
- Do not pad antithetic dots from `oppose ≤ 0.3`.
- Do not drop spacing below 3.2 px to force 37,654 dots.
- Do not multiply Band 18 by the depth gradient in float32 (overflow). The shipped operator uses float64 polarity and a rank product.
- Do not look up the antithetic direction along the local gradient. On a symmetric basin that lookup never opposes. The regional frame is required, and on this stack it still rarely opposes.
- Do not treat 0.005420, 0.2778, 0.3195, or 0.4413 as the same kind of number.
