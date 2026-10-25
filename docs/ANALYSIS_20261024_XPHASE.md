# Analysis — `XPHASE` (MT–Gravity Transverse-Phase Concordance), 2026-10-24

## PhD answer: why GEMSDOE32 scored `0.2778` `[CLAIM]` and whether we can beat it

GEMSDOE32 `h33-h33-2-b2` (`R0`, 37,654 dots) is not a new-fault detector. It is a spacing-and-clearance filter of a fixed worm skeleton:

`H19-5` (121,131 px, `0.1922` `[CLAIM]`) → `D2.8` Poisson thinning at 2.83 px (44,090 px, `0.2600` `[CLAIM]`) → `SOLO` = `D2.8 & d_cat > 1.0` (40,199 px, `0.2708` `[CLAIM]`) → `R0` = `D2.8 & d_cat > 2.0` (37,654 px, `0.2778` `[CLAIM]`).

Official DTI (DrivenData reference Cell 16; `vendor/gems57/metric.py`) weights false negatives 4× false positives (β=0.8, α=0.2) with a 300 m triangular kernel that takes a **pointwise maximum**. Dots closer than ~2.8 px add FP weight with ~0 TP gain. That geometry, plus staying just off the catalogue (`d_cat > 2`), explains the listed-site high among GEMSDOE clones. It does **not** explain the live leaderboard snapshot `0.4413` (2026-10-24, not a receipt): that gap is unmapped faults.

`XPHASE` tests one untried discovery mechanism for those unmapped faults: strike-parallel MT log-conductivity and isostatic-gravity gradients with a 200 m transverse lag under intermediate cover. Local **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives) for the best arm `dual40` is **`0.004653 [0.003955, 0.005390]`**, above `R0` `0.004006` by `+0.000647` whose paired 95% CI **includes 0** (`[-0.000109, +0.001375]`). It is below repository holdout-best `COULOMB-LOQO standalone` `0.009220`. Ablating the lag (`nophase` `0.003487`) matches standalone (`0.003492`): the lag term is not load-bearing on this catalogue hide-and-recover instrument. **Negative result. Do not submit.**

## Experiments (budget = 3)

| Arm | Dots | HOLDOUT-DTI (22,663 pos) | SGMC PROXY | Local 3-px overlap | Verdict |
|---|---:|---|---:|---:|---|
| `dual40` (primary) | 37,654 (40% H19) | **0.004653 [0.003955, 0.005390]** | 0.047166 | 0.4000 (H19-5) | negative |
| `standalone` | 37,654 (0% H19) | 0.003492 [0.002741, 0.004240] | 0.027957 | 0.2528 | negative |
| `nophase` | 37,654 (0% H19) | 0.003487 [0.002781, 0.004186] | 0.027573 | 0.2514 | negative |
| `R0` control | 37,654 | 0.004006 [0.003406, 0.004668] | 0.096060 | self | CLAIM 0.2778 |
| `COULOMB-LOQO standalone` | 37,654 | 0.009220 [0.007933, 0.010683] | 0.090569 | 0.6164 | negative / holdout-best |

Leakage canaries: max symmetric AUC **0.553140 ≤ 0.90** (Band 19 slope). Local uniqueness PASS (74 rasters). Literal public witness `17GEMSDOE E-proba-multiscale` (5,167,373 / 5,167,373 footprint positive, git blob `374c88b1…`) → forward overlap **1.000** → `submission_eligible: false`.

## Interpretation

Static hide-and-recover of mapped catalogue segments rewards remaining on the `H19-5` spine (`dual40` beats standalone). `XPHASE` far dots sit on MT/gravity phase crests that are only weakly aligned with withheld Quaternary traces (canaries ~0.51). Named mimic (playa clay on a basin density contact) is consistent with the low SGMC recovery. The lane is a **valid negative**: unique locally, format-valid, scientifically distinct, not a weekly-slot candidate.

Primary bytes: `docs/downloads/h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif` SHA-256 `080018382de33758c78e1b11f80098a1f736ac7de5f4c55641bd84b52b0f7200`.
