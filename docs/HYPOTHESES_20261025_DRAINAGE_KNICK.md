# Pre-run decision — DRAINAGE-KNICK (2026-10-25)

This file was written before executing this lane. The five-candidate preregistration is preserved at [`HYPOTHESES_20261026_RADIOCONTACT.md`](HYPOTHESES_20261026_RADIOCONTACT.md). Its rank-1 RADIOCONTACT experiment was negative, so this run advances the already specified rank-2 candidate without changing its mechanism after seeing results.

## Ranked candidates (no numeric score projections)

| Rank | Layers | Target signature | Why potentially absent from catalogue | Difference from existing work | Mimic | Cost |
|---:|---|---|---|---|---|---|
| 1 | B12 detrended elevation, B19 slope, B15 basement depth, B7 shear | Persistent multi-scale terrain curvature/slope break coincident with basement-depth edge and shear | A buried or degraded fault can deflect/steepen drainage and offset basement without a preserved mapped scarp | First label-free joint knickzone–basement-edge lane; POISSONFLEX used a learned multi-feature knick integral, not this standalone conjunction | Resistant beds, Lake Lahontan shorelines, fan toes, DEM seams | Medium |
| 2 | B17 conductivity, B15 basement depth | Conductivity change-point after conditioning on cover thickness | Fluid-bearing blind strands can remain electrically visible beneath uniform cover | Prior MT lanes used level/edge but not cover-stabilized change points | Salinity/facies boundaries | Low |
| 3 | B11/B18 gravity derivatives | Gravity derivative quadrature | Buried density-offset structures need not have magnetic or surface expression | Standalone gravity quadrature rather than classifier input | Lithologic density contact | Low |
| 4 | B10/B16 seismic summaries, B13 gravity | Along-strike seismic/gravity lateral lag | Seismicity can follow a blind permeable strand | Tests offset, not earthquake intensity alone | Magmatic/induced swarm | Low |
| 5 | Official USGS 3DEP 1 m DEM tiles | Channel-profile knickpoints and drainage deflection | High-resolution drainage offsets can outlive subtle scarps | True flow-network method, unlike raster curvature | Lithologic knickpoints, roads | High; data not staged, so not viable in this run |

No new external data are needed for ranks 1–4; they use the SHA-256-pinned competition stack. Rank 5 specifically requires free official USGS 3DEP products (`https://www.usgs.gov/3d-elevation-program`), but availability of every competition-footprint tile was not verified in this restricted sandbox, so it is not called viable here.

## Registered test

The lane surface is the geometric mean of (a) scale-persistent absolute DEM Laplacian and local log-slope departure, (b) Gaussian depth-to-basement gradient, and (c) shear-rate percentile. Each feature receives an independent leakage canary. Holdout placement is rebuilt per fold from only visible faults, with >2 px visible-fault clearance. Evaluation is pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel), `gems57-pooled-hide-v2`, eight buffered folds, 22,663 withheld positives, with a 1,000-draw spatial-block bootstrap CI.

Promotion requires beating the repository strict holdout best (`0.113316`, labeled HOLDOUT-DTI in its source run card), all canaries ≤0.90, all automated raster gates, and registry thresholds |rho|≤0.90 and 3-px overlap≤0.70. Otherwise the unique format-valid TIFF remains a negative research deliverable and must not consume a weekly slot.
