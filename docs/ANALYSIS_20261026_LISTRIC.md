# PhD Analysis — 2026-10-26 `LISTRIC` Session

## 1. Why/how did GEMSDOE32 `h33-h33-2-b2` reach 0.2778 (CLAIM), highest among listed GEMSDOE sites?
Evidence classes: `0.2778` is an owner-reported **CLAIM** — `registry/parents/R0.json` has `receipt: null` and `ledger/submissions.csv` holds no ORGANIZER-CONFIRMED receipt for it (re-verified this session; `make verify` PASS, pin `c55bafc4…ab6fa9`). Line-by-line mechanism (full forensic in `docs/ANALYSIS_20261024_COULOMBLOQO.md` §2):
1. **H19-5 support (0.1922 CLAIM):** multiline-corroborated openness/thermal ridge skeleton concentrates mass on structurally corroborated lineaments rather than diffuse probability.
2. **D2.8 Poisson-spaced dots (0.2600→0.2708 CLAIM):** under distance-weighted Tversky (α=0.2, β=0.8, 300 m triangular kernel per official problem page), spaced unit dots avoid redundant overlapping cones; each dot buys independent 300 m coverage.
3. **`d_cat>2.0px` prune + 37,654 budget (0.2778 CLAIM):** removes 2,545 dots in the 100–200 m catalogue digitisation halo (wasted on already-known faults, which the hidden test excludes), keeping 2,171 dots in the 200–300 m splay collar.
4. **Zeros-outside encoding:** finite [0,1] everywhere avoids the portal `"Predicted values must be in range [0, 1]"` rejection that NaN-outside files risk.
Why it trails the leaderboard snapshots (0.3195/0.4413): its surface is a single-family ridge skeleton — no subsurface (gravity/magnetic/MT), stress, or province calibration — so blind/buried faults with weak topographic expression are systematically missed. Local HOLDOUT-DTI (0.004–0.011 scale) is a *relative ranking instrument only*: deployment candidates mask `d_cat≤2px`, so withheld faults are only scorable in their 200–300 m collar (kernel ≤1/3). **No local number can prove >0.2778 on DrivenData; only an ORGANIZER-CONFIRMED receipt can.**

## 2. This session: LISTRIC (NEXT_STEPS Rank 4, pre-registered `docs/HYPOTHESES_20261026_LISTRIC.md`)
Hypothesis: catalogue-missing listric normal faults show a 200–800 m offset between surface scarp (B12/B19) and subsurface gravity/basement inflection (B15/B18), dip concordance, and rollover curvature. Implemented as 4 catalogue-free features (`gems/listric.py`) on the KNICKLOQO LOQO stack; v1 merged crest was a Rule-1 duplicate of KNICKLOQO (0.763212>0.70, STOP, no TIF emitted) → amended pre-emission to LISTRIC-PURE crest (`L_listric³` only).

## 3. Measured results (all HOLDOUT-DTI, `gems57-pooled-hide-v2`, 22,663 withheld px; `evidence/listric_proxy_audit.json`)
| Arm | Static HOLDOUT-DTI | Draw-blind d_vis>2 | SGMC PROXY | Local worst | Public dual-reading (1,472 rasters) |
|---|---|---|---|---|---|
| **standalone** | **0.010909 [0.009543,0.012278]** | 0.110593 [0.097436,0.123346] | 0.097959 | 0.644872 | **0.710735 duplicate** (62GEMSDOE 125,890-dot) |
| uncal | 0.010385 [0.009080,0.011643] | 0.110501 | 0.096324 | 0.616004 | 0.702050 duplicate |
| dual35 | 0.009446 [0.008237,0.010705] | 0.098798 | 0.098840 | 0.653822 | 0.679104 unique |
| KNICKLOQO standalone (prior best) | 0.010788 [0.009468,0.012201] | 0.109043 | 0.103912 | — | unique (0.685531) |
| R0 (0.2778 CLAIM) | 0.004006 [0.003406,0.004668] | — | 0.096060 | — | — |

Paired Δ standalone vs KNICKLOQO = +0.000121 [-0.001167,+0.001262] (**includes 0 — not a proven improvement**); vs R0 = +0.006902 [+0.005729,+0.008081]. Canaries: all PASS, max symmetric AUC 0.667141 (listric features 0.526–0.622 ≤ 0.90).

## 4. Judgement
LISTRIC-PURE is a **negative deliverable**: its best arm nominally tops the static holdout but (a) is statistically indistinguishable from KNICKLOQO, (b) loses on the independent SGMC bedrock proxy, and (c) is a public-registry duplicate even under the dual reading (0.710735>0.70 vs an over-budget 125,890-dot 62GEMSDOE raster), plus literal 1.000 vs dense full-footprint surfaces. The dual35 arm is public-unique but below holdout best. **No LISTRIC TIF may be submitted; 0 slots spent.** Whether anything in this repo beats 0.2778 remains unknowable without a first ORGANIZER-CONFIRMED receipt — the single highest-P(Win) next action remains the human selector decision on KNICKLOQOstandalone (dual-reading-unique, prior #1) documented in `docs/NEXT_STEPS.md`.
