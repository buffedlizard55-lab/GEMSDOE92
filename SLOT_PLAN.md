# SLOT_PLAN — MASS axis session 2026-10-23

Deadline: 2026-12-03 (confirm on competition page). One entity, 3 scored submissions per rolling week, one final file chosen blind.

## Parent
h33-h33-2-b2 (GEMSDOE32): 37,654 dots, none within 2px of catalogue, CLAIM 0.2778. sha256 c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9. Verified against mirror.

## This session — AXIS=MASS
We built 3 variants differing ONLY on mass, ranking from H19-5 continuous field (recorded recipe: H19-5 -> D2.8 (44,090) -> H27-4-SOLO (40,199) -> B2 prune (37,654)).

| slot | file | n_dots | % changed | predicted | mechanism |
|---|---|---|---|---|---|
| 1 (best bet) | h33-h33-2-b2-MASS_SWAP10-20261023-3e776063 | 37,654 | 10% | +0.001 to +0.006 MODEL | Keep budget, improve avg credit by swapping lowest 10% H19-5 with next 10% |
| 2 | h33-h33-2-b2-MASS_D10-20261023-e26a6cb8 | 33,889 | 10% | +0.002 to +0.008 MODEL | Drop low-ranked dots if marginal credit <0.2*DTI (~0.056) |
| 3 | h33-h33-2-b2-MASS_A10-20261023-e5613a00 | 41,419 | 10% | -0.001 to -0.005 MODEL | Test if budget saturated; if live > parent, optimum higher |

All files: float32 EPSG:32611 100m, same transform as sample_submission.tif, values in [0,1], NaN outside (primary) and zeros outside (fallback), zero catalogue mass, re-read after write.

## What each result would change
- If SWAP10 beats parent by >=0.01: confirms ranking carries signal beyond random, mass optimum at ~37k but quality can be improved at same budget. Next: combine with CONCENTRATION (move mass to high-prior km blocks) and SNAP (move <=2px to edge response).
- If D10 beats parent: mass optimum lower than 37k, marginal dots are noise. Next: test MASS_D20 (30k) and combine with PRUNE B3 (35,483) to see if further pruning helps.
- If A10 beats parent: mass optimum higher, budget not saturated, marginal credit > bar. Next: test MASS_A20 (45k) and CONCENTRATION to allocate added dots to high-prior blocks.
- If all three underperform by >0.01: mass at 37,654 is near optimum, ranking by H19-5 insufficient, need better ranking (e.g., multi-physics consensus or tip/step-over prior).

Treat live change <0.01 as no evidence (public chunks only, private may differ).

## Default plan to deadline (per brief)
- wk1-2: MASS, CONCENTRATION, SNAP, PRUNE, RELIEF (one axis per session, 3 variants each, 3 slots/week)
- wk3-4: combine two best axes (e.g., best MASS + best CONCENTRATION)
- wk5-6: confirm, choose final file and fallback, re-validate format of both

Weeks left: from 2026-10-23 to 2026-12-03 = ~6 weeks, ~18 slots max (3/week). We have used 0 slots this week, 3 built this session (BUILT, not yet submitted).

## Better axes proposals (mechanism, confounder, falsifier) — do not build this session
1. **CONCENTRATION with SGMC-calibrated prior**: Move 15% dots from lowest 1km-block density to highest. Mechanism: hidden faults cluster where SGMC faults cluster off-catalogue. Confounder: SGMC faults are mapped faults, may bias to exposed areas. Falsifier: if block-density CV of best files 0.51-0.59 not reproduced, or live drops.
2. **SNAP to LiDAR scarp + mag gradient**: Move each dot <=2px to strongest edge response in window (TMI gradient, lidar scarp). Mechanism: GeoDAWN 400m line spacing causes ~300m positional uncertainty, snapping corrects. Confounder: scarp product contains non-fault scarps (roads, terraces). Falsifier: mean displacement >1.5px with no live gain.
3. **RELIEF tercile shift**: Shift 10% mass from basin to range-front tercile (detrended elevation). Mechanism: range-front faults control geothermal systems (Faulds inventory). Confounder: basin faults are blind and more valuable for geothermal, but less expressed. Falsifier: if relief distribution of best files uniform, no gain.

## Gates
- MUST pass: format check, zero catalogue mass, sha256 not in ledger, parent-diff recorded, re-read after write — all PASS this session
- REPORT ONLY: catalogue hide-and-recover PROXY (not computed this session — need SGMC off-catalogue truth, but we have no leakage canary >0.90 AUC), leakage canary (not computed), SGMC control (not computed)

## Next human actions
- Fill TOP_PUBLIC from leaderboard with date
- Choose one of three MASS files for slot 1 (recommend SWAP10)
- Submit from own registered account (do not use dropbox.com, do not scrape leaderboard)
- Record receipt score in ledger/submissions.csv
