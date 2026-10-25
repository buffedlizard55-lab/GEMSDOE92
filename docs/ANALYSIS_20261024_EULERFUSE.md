# EULERFUSE closeout and PhD-level answer (2026-10-24 UTC)

## Executive decision

A genuinely new GeoTIFF was generated from a new physical method, not copied from an earlier submission:

- **File:** `docs/downloads/gemsdoe92-eulerfuse-gravity-37654-20261024-d7133700-zeros.tif`
- **SHA-256:** `5820e882512843a334f4497ed7f294af937339f729e4eeeecdc33d9cdafeeab9`
- **Local format verdict:** **PASS** (`11/11` gates; single band, float32, EPSG:32611, 3730 × 3292, exact reference transform, all finite, range `[0,1]`, zero outside footprint, zero catalogue mass)
- **Competition-slot verdict:** **NEGATIVE — DO NOT SUBMIT.** It did not beat the current comparable holdout control and it triggers the prompt's literal public-registry overlap stop. No weekly slot was used.

The artifact is safe to download for research and structurally acceptable to the local format validator. “Format-valid” is not organizer acceptance and is not permission to upload it.

## Why the `GEMSDOE32` dotted file plausibly reached the owner-reported `0.2778`

`0.2778` is an owner-provided **CLAIM**, not an `ORGANIZER-CONFIRMED` receipt in this repository. The exact raster lineage, however, is byte-verifiable:

1. `H19-5` has `121,131` positive pixels.
2. `D2.8` reduces that support to `44,090` pixels with a spacing rule near the 300 m credit-kernel scale.
3. `SOLO` is exactly `D2.8 & (distance_to_catalogue > 1 pixel)`, with `40,199` pixels.
4. `R0` / `h33-h33-2-b2` is exactly `D2.8 & (distance_to_catalogue > 2 pixels)`, with `37,654` pixels.

That cascade matches the official metric's geometry. The official reference implementation uses

`DTI = TPw / (TPw + 0.2 FPw + 0.8 FNw)`

with a 300 m triangular distance kernel. Dense neighboring predictions compete for the same maximum truth-pixel credit, so removing redundant mass near already-covered locations reduces weighted false-positive cost without proportionally reducing true-positive credit. The final 2-pixel catalogue collar also removes pixels that cannot represent a catalogue-missing target. This is a metric-aware sparsification explanation, not proof of the unarchived score claim.

The checked `GEMSDOE32` source page at GitHub commit `098f3af9508a135277ef4d1bf2266e2e448be814` explicitly said that no organizer score existed in that repository. Therefore this project does not promote its projections or owner claims to receipts.

## Can a new method score above `0.2778`?

**Scientifically possible; not demonstrated here.** The leaderboard values in the owner prompt (`0.3195` and `0.4413`) conflict in time and were not retrievable from the login-restricted competition host in this sandbox. They remain prompt-provided snapshots, not verified receipts. The existence of higher owner-provided leaderboard values indicates that `0.2778` is not a mathematical ceiling, but no local holdout value can be converted into a live score.

The most defensible route is to increase independent recovery of covered, catalogue-missing structures while preserving approximately kernel-scale emission spacing. Merely re-thinning the H19-5 lineage is unlikely to bridge the gap. A new physical detector must add true fault credit rather than mass. That is why this session tested inferred potential-field source locations rather than another catalogue-collar or dot-budget tweak.

## What EULERFUSE tested

The new method solved the moving-window structural-index `N=0` Euler equation

`(x − x0) Fx + (y − y0) Fy + (z − z0) Fz = 0`

independently on reduced-to-pole magnetic anomaly (Band 2) and isostatic gravity anomaly (Band 13). It retained stable shallow solutions, rasterized inferred source subcrops, computed cross-physics colocation and depth agreement, and compared inferred source depth with Band 15 depth to basement. These catalogue-free features were added to the existing physical feature stack and fitted with four-quadrant leave-one-quadrant-out models.

Three arms were frozen before evaluation:

| Arm | Definition | Primary HOLDOUT-DTI (`gems57-pooled-hide-v2`, 22,663 withheld positives, 95% CI) | Static deployment-mask HOLDOUT-DTI (same evaluator/count, 95% CI) | SGMC PROXY DTI |
|---|---|---:|---:|---:|
| `joint` | RTP + gravity Euler features | `0.109410 [0.096290, 0.122634]` | `0.009655 [0.008334, 0.011186]` | `0.086393` |
| **`gravity`** | gravity Euler ablation; best primary arm | **`0.110387 [0.097279, 0.123179]`** | `0.009265 [0.007974, 0.010740]` | `0.084539` |
| `joint45` | 45% H19-5 control + 55% joint-Euler crests | `0.097180 [0.086444, 0.107964]` | `0.006495 [0.005669, 0.007361]` | `0.090528` |
| fresh base control | reproduced COULOMB-LOQO surface without Euler features | `0.113316 [0.101071, 0.126266]` | `0.009220 [0.008012, 0.010607]` | `0.090569` |

The gravity arm's paired **HOLDOUT-DTI** delta from the fresh base control is `−0.002929`, 95% CI `[−0.006700, +0.000763]`. It neither beats the control by point estimate nor excludes zero in the favorable direction. The promotion gate therefore fails.

## Interpretation of the negative result

The geological mechanism is plausible, but this implementation's Euler solutions are too sparse and weakly discriminative at the 100 m competition grid:

- magnetic centers tested: `13,037`; accepted rasterized source cells: `7,374`;
- gravity centers tested: `6,789`; accepted rasterized source cells: `582`;
- each raw Euler feature's symmetric single-feature holdout AUC is approximately `0.500–0.501`, while the fresh base model's draw-blind surface reaches `0.662808`;
- adding weak Euler channels slightly reduced the primary draw-blind holdout result.

This is consistent with coarse/smoothed regional potential fields localizing lithologic contacts and buried source edges, but not uniquely identifying recently active, permeable Quaternary faults. Volcanic contacts and pluton margins are the named non-fault mimic. The result falsifies this exact 100 m, 9×9-window implementation as an improvement; it does not falsify Euler interpretation at airborne line-level resolution.

## Leakage, uniqueness, and validation

- **Leakage canary:** 36 tested base/new/composite features; maximum symmetric AUC `0.662808 <= 0.90` — PASS.
- **Local pre-placement registry:** 49 rasters; worst surface `|rho| = 0.158150`; worst preview 3-pixel overlap `0.620492 <= 0.70` — PASS.
- **Local final registry:** worst `|phi| = 0.057603`; worst overlap `0.620492 <= 0.70` — PASS.
- **Public registry:** 102 current public owner repositories, 1,378 one-band exact-grid rasters compared; exact file-hash matches `0`; worst surface `|rho| = 0.451197`, worst final `|rho| = 0.289024`, both below `0.90`. Under the requested literal support rule, however, pre-placement and final overlap each equal `1.000` against `17GEMSDOE E-proba-multiscale`, which is positive on all `5,167,373` footprint cells. This is a binding duplicate stop even though it is a dense continuous field.
- **Format:** exact-file automated receipt records all values in `[0,1]`, no NaN or infinity anywhere, matching CRS/shape/transform, and `0.0` outside the footprint.

## Sources for manual review and verification status

1. Official reference solution: https://github.com/drivendataorg/gems-prize-reference-solution — retrieved at commit `aebe92f7c8a990f0e3443451b7a825d9afd6336b`; metric arithmetic verified from code/notebook.
2. GeoDAWN official record: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 and https://doi.org/10.5066/P93LGLVQ — official links recorded; these hosts were blocked here. The restored stack matched its pinned owner-mirror SHA-256; upstream redistribution identity remains flagged, not silently certified.
3. DOE GDR INGENIOUS: https://gdr.openei.org/submissions/1391 — official link recorded; host blocked here; pinned local CSV hash verified.
4. GEMSDOE32 source: https://github.com/buffedlizard55-lab/GEMSDOE32 — source page and artifact lineage checked through GitHub.
5. Competition problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ — link supplied for manual review; login/network restrictions prevented a fresh official-page receipt in this session.

## Final scientific verdict

**Negative.** EULERFUSE is a real, distinct, reproducible experiment and yields a byte-unique, format-valid TIF, but it should not consume a competition slot. The strongest next research direction is not another Euler parameter sweep—the three-experiment budget is exhausted—but a new preregistered lane using cross-catchment drainage knickpoint alignment or higher-resolution official 1 m 3DEP data when legally and technically obtainable.
