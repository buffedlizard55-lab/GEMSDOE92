# Pre-Registered Geological Hypotheses — `LISTRICDIP` (2026-10-25)

Written and locked **before** any `LISTRICDIP` experiment was scored. Branch `arena/5162a107-gemsdoe92`. Evaluator to be used, not forked: `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel). Writer to be used, not forked: `vendor/gems57/submission_writer.py`. Experiment budget: **3**. Weekly slots: **0** (promotion is a separate selector step).

No number below is a score. Prior `HOLDOUT-DTI` figures are cited from this repository's run cards. `0.2778` remains a sibling-site **CLAIM**. `0.4413` is a **LEADERBOARD-SNAPSHOT** read from the public DrivenData page on 2026-10-25, not an organizer receipt for any file in this repository.

## Why this lane, and why not a copy of `h33-h33-2-b2`

The listed GEMSDOE-site high of **CLAIM 0.2778** (`GEMSDOE32` `h33-h33-2-b2`) is an emission-geometry descendant of `H19-5`, not a new geological model. The byte-checked cascade in this repo is `H19-5` → Poisson-thinned `D2.8` → `SOLO` (`d_cat > 1`) → `R0` (`d_cat > 2`, 37,654 dots). Thinning redundant dots inside the 300 m kernel and dropping pixels that sit on the mapped catalogue raised the **claimed** organizer score from 0.1922 to 0.2778. That file is already in the registry. Copying it is forbidden.

The public leaderboard snapshot on 2026-10-25 shows **0.4413** (participant `xiaofanhu`), then 0.3916 and 0.3904 ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)). Those are not receipts for this repository. Beating 0.2778 on the organizer metric is possible in principle — the public board is already above it — but a local holdout number is not that score and will not be written as one.

Faulds & Hinz (2015) and the later Great Basin inventories find that **step-overs / relay ramps** host about 32% of known systems (about 40% of favorable structural settings in the INGENIOUS study area), fault intersections and terminations most of the rest, and **major range-front fault segments only about 3%**. About 39% of known systems are blind. Worm skeletons and slope-break lanes lock onto the range-front contact the catalogue already maps. The untried target is the **lateral offset between that deep contact and the near-surface strand**, plus the **reversed-polarity antithetic** one relay-width down-dip.

## Five untried candidates

| Rank | ID | Layers | Physical signature | Why it can hit a fault absent from USGS/INGENIOUS | Difference from this repo | Expected value | Cost | Viable here? |
|---|---|---|---|---|---|---|---|---|
| **1** | **`LISTRICDIP`** | Bands 12, 13, 15, 18, 19 (`det_elev`, `iso_grav_anom`, `depth_to_base_surf`, `iso_grav_anom_hg`, `det_elev_slope`) | Horizontal offset \(\Delta = C \cot\delta\) between the basement-cutoff crest and the up-dip surface trace; antithetic crest 2.2 km and 3.5 km down-dip where the depth gradient reverses | Catalogue and airphoto mapping lock onto exposed scarps. Worms lock onto the basement cutoff. A 45–60° strand under 400–1,100 m of fill is separated from that cutoff by several pixels; the connecting relay breach is what regional catalogues omit | No module shifts emission by \(C\cot\delta\). `XPHASE` uses a fixed 2 px MT lag. `STEPOVER` uses visible catalogue tracts. `COULOMBLOQO` polarity is co-located | High if withheld strands are offset from the basement cutoff; low if they sit on it | Low–moderate (catalogue-free, no new download) | **Yes** — bands are in the SHA-256-pinned `training_features.tif` |
| 2 | `TENSOR-RIEDEL` | Bands 2, 13, 18, 19 | 15–25° obliquity between surface-scarp strike and the gravity-gradient strike (Riedel R) | En-echelon relays rotate off the master fault; collinear worm/phase lanes reward 0° lock | `XPHASE` and `COULOMBLOQO` reward collinearity, not 15–25° | Moderate, Walker Lane only | Moderate | Yes, same stack. Not this session |
| 3 | `FLEXURE-HINGE` | Bands 12, 13, 15, 18 | Broken-plate flexural inflection at 12–18 km (Buck 1988 wavelength) | Buried master faults under thick fill express as long-wavelength monoclines, not 300–600 m scarps | `PIEDFRONT` / `APRONRIDGE` use short scarp steps | Moderate, basin margins | Moderate | Yes, same stack. Not this session |
| 4 | `CLAYCAP-REDOX` | Band 17, GeoDAWN K/Th and U/Th, Band 2 | Smectite-cap curvature \(\nabla^2 \log(\mathrm{cond}) < 0\) plus a U/Th redox front and an RTP demagnetization trough | Blind upflow alters rock above an unmapped intersection with no scarp | `HYDROCONDUIT` uses first-order conductivity gradient, not paired cap curvature and U/Th | Low–moderate; MT grid is coarse. `RADIOCONTACT` already failed a radiometric-contact cousin | Low | GeoDAWN is pinned from the owner mirror of USGS DOI [10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ). Not selected: prior radiometric-contact lane was negative |
| 5 | `INSAR-3DEP1M` | Sentinel-1 LOS gradient, 3DEP 1 m | Pumping-deconfounded creep step and lidar micro-scarp | Historic creep and sub-pixel scarps are absent from both the 100 m stack and the catalogue | No lane has InSAR or 1 m lidar | Unknown until tiles exist | High | **Not viable in this sandbox.** Official free sources: USGS 3DEP ([3dep.usgs.gov](https://www.usgs.gov/3d-elevation-program)) and NASA ASF/OPERA Sentinel-1. Neither host is reachable from this sandbox (GitHub/PyPI only). Not proposed as a runnable experiment |

Named non-fault mimic for Rank 1: a compaction monocline or alluvial fan trench over an unfaulted density step, and a contour-parallel pluvial bench. Absolute Lake Lahontan shoreline elevations (about 1332 m AMSL) are **not** applied: Band 12 is detrended elevation, not orthometric height. The bench null is cross-contour geometry only.

## Three experiments (budget = 3)

All catalogue-free. Deployment dots, where emitted, satisfy `d_cat > 2` px, unit mass, spacing 3.2 px, zeros outside the footprint, values in [0, 1].

1. **`updip50`** — surface trace up-dip of the basement-cutoff crest by \(\Delta = C \cot 50^\circ\), only where smoothed cover is 400–1,100 m (concealed strand). 37,654 hard dots.
2. **`anti22`** — reversed-polarity basement-gradient crest 22 px (2.2 km) down-dip of the master cutoff, inside the published relay-width range (Giddens & Faulds report a mean near 2.5–2.8 km). 37,654 hard dots. Direction/distance ablation.
3. **`anti35`** — same operator at 35 px (3.5 km). If `anti22` and `anti35` tie, distance is not load-bearing.

Falsifier: a single-feature symmetric AUC above 0.90 is leakage until proven otherwise. An arm whose pre-placement top-37,654 support or final dots exceed 0.70 forward 3 px overlap or 0.90 absolute rank correlation against any local registry raster is a duplicate; that arm stops. Beating the stored repository holdout best is required before any weekly-slot recommendation. This session will not recommend a slot.

## Post-score addendum (2026-10-25, after the three arms)

The locked budgets above were not silently rewritten. The run could not fill them.

- `updip50` emitted the locked 37,654 dots.
- `anti22` emitted 9,571 and `anti35` emitted 9,555. The reversed-polarity support (`oppose > 0.3`) cannot hold 37,654 dots at 3.2 px spacing after `d_cat > 2`. Padding from `oppose ≤ 0.3`, or spacing below 3.2 px, was refused. Those arms are a documented deviation, not the pre-registered emission.
- Static HOLDOUT-DTI: `updip50` 0.005420 [0.004294, 0.006551]; `anti22` 0.001291; `anti35` 0.001224. `updip50` beats `R0` and loses to `KNICKLOQO` 0.010788 and `COULOMBLOQO` 0.009220. Verdict `negative`. No weekly slot.
- `anti22` and `anti35` tied. Distance is not load-bearing, which is the ablation the pre-registration asked for.

## Sources (manual review)

- Competition problem and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Public leaderboard (snapshot, not a receipt): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution (training-loss weights, not the distance-weighted evaluator): https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and and https://doi.org/10.5066/P93LGLVQ
- DOE GDR #1391: https://gdr.openei.org/submissions/1391
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Faulds & Hinz structural settings: https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
- Faulds favorable settings (2026 workshop paper): https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2026/Faulds.pdf
- Giddens & Faulds step-over widths: https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf
