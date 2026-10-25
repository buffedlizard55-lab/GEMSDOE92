# Pre-Registered Hypotheses — `BLINDFAULT` session (2026-10-25, written BEFORE any screen/build)

Sandbox budget this session: 2 CPUs, 3 GB RAM, ≤ 3 experiments, ≤ 2 h. Lane name: **`BLINDFAULT`**.

## Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) led, restated in one paragraph

The byte-verified cascade is `H19-5` (121,131 px, `0.1922`) → Poisson thin at 2.83 px (`D2.8`, 44,090 px, `0.2600`) → drop `d_cat ≤ 1` (`SOLO`, 40,199 px, `0.2708`) → drop `d_cat ≤ 2` (`R0`, 37,654 px, `0.2778`). Every step after `H19-5` is an **emission** edit, not a detection edit. Under the DTI identity `D = α(T + n − M) + βK` with `α = 0.2`, `β = 0.8`, the two near-catalogue prunes removed 6,436 dots while the score rose, which is only possible if those dots carried ≈0 truth credit: solving the three receipts under `T ≈ M` gives `K ≈ 1.3 × 10⁴` truth cells and `T ≈ 5.1 × 10³` credit, i.e. ≈13 % of `R0` dots are productive. The marginal-dot bar is `k > α·DTI ≈ 0.056`, so **any dot family with ≥ ~6 % hit probability per dot improves the score, and any family below it hurts**. The missing fault population (INGENIOUS additions absent from the USGS Quaternary catalogue) is, by construction of the catalogue, biased toward **topographically subtle** structures; `H19-5`'s topographic ridges catch the conspicuous tail only. The head-room to `0.3195`/`0.4413` `[CLAIM]` is therefore in the *subtle* tail, not in further thinning.

## Distribution-shift statement (the central claim of this session)

The local hide-and-recover holdout withholds **catalogue** segments. Catalogue faults are, on average, more conspicuous (steeper `Band 19` slope, sharper `Band 12` steps) than the competition's held-out *new* faults. A learner optimised for the catalogue holdout is rewarded for conspicuity. This is classic covariate shift between training labels and the deployment target (Shimodaira 2000, *J. Stat. Plan. Inference* 90:227; Sugiyama et al. 2007, *JMLR* 8:985). The standard fix is importance weighting of the training positives by a density ratio that favours the target regime. Here the target regime is operationalised as **low topographic conspicuity**.

## Ranked untried hypotheses (none of these is in `evidence/lane_registry_index.json`, `docs/HYPOTHESES_*.md`, or `gems/*.py`)

| Rank | Lane | Layers | Physical signature / transform | Why it catches a fault *missing* from the catalogue | Mimic (named non-fault process) | Expected gain | Cost |
|---|---|---|---|---|---|---|---|
| **1 (BUILD)** | **`BLINDFAULT`** — conspicuity-reweighted, subsurface-only LOQO | Bands 2 (RTP), 11 (grav VG), 13 (grav anomaly), 15 (depth-to-basement), 17 (MT conductivity), 18 (E–W grav HG), 7/8 (geodetic shear/dilatation); Band 19 slope used **only** to build importance weights, never as a feature; Band 12 low-pass as basin/range context | Gaussian-derivative horizontal-gradient magnitudes (σ = 1.5 px) of RTP, gravity, basement depth and conductivity; local-amplitude-normalised RTP tilt; 4-quadrant LOQO `HistGradientBoostingClassifier` trained with positive sample weight `w = 1/(ε + c)` where `c` is the catalogue pixel's 5 × 5 max of normalised log-slope | The catalogue is a Quaternary *scarp* catalogue; faults without a preserved scarp were systematically under-mapped. Training positives are reweighted toward the catalogue's own low-scarp members so the model learns the subsurface fingerprint of faults that do **not** show in the DEM, then applied everywhere | Buried lithologic contacts and dykes in basin fill (potential-field edge without displacement); clay-rich lacustrine facies boundaries (MT edge) | Highest: directly targets the population that scores | Low — 9 rasters, one HGB fit per quadrant, fits in 3 GB |
| 2 | `POISSONCORR` — Poisson's-relation local correlation break | Bands 2 (RTP) and 11 (grav VG) | Sliding-window (21 px) Pearson correlation between RTP and gravity vertical gradient (pseudo-gravity relation, Chandler et al. 1981 *Geophysics* 46:30); faults = linear zeros/sign reversals of the correlation map | Basement steps offset both density and magnetisation contrasts coherently; intrusions offset only one. Catches concealed basement faults under alluvium | Compositional changes in a single pluton; remanent magnetisation | Medium–low (km-scale localisation vs 300 m kernel) | Medium |
| 3 | `KNICKLINE` — flow-routing knickpoint alignment | Band 12 (detrended elevation) | D8 flow accumulation on detrended DEM, longitudinal-profile convexity (χ-space) per channel, Radon alignment of knickpoints across adjacent canyons | Range-front faults with diffused scarps still leave aligned knickpoints upstream | Lithologic contacts between resistant/soft units; base-level falls of Lake Lahontan | Medium | High (flow routing on a *detrended* DEM is only valid inside ranges); official 10 m 3DEP tiles not reachable from this sandbox |
| 4 | `STRIKEDEVIATION` — local strike departure from N15°E optimal | Band 12 + Band 8 | Structure-tensor strike of relief vs. Coulomb-optimal strike under the local dilatation tensor; penalise relief lineaments far from optimal | Optimally-oriented but subtle lineaments are more likely active faults than well-expressed but misoriented ones (e.g. shorelines are strike-random) | Glacial/fluvial terraces aligned with range fronts | Low–medium | Low |
| 5 | `INSAR-CREEP` (held) | External Sentinel-1 InSAR LOS velocity (ASF/ARIA OPERA DISP-S1, free, official) | Phase-gradient step across a line | Aseismic creep on unmapped faults | Groundwater pumping subsidence bowls | Unknown | Blocked: sandbox egress restricted to GitHub/PyPI |

## Pre-registered experiment arms (frozen before the first fit; exactly 3)

Common: 4-quadrant LOQO (`guard_px = 12`, `neg_buffer_px = 5`, `neg:pos = 4`), 37,654 unit-mass dots, spacing ≥ 2.83 px, emission domain `foot ∧ valid ∧ d_cat > 2.0` (the `R0`-proven emission rule, zero catalogue mass).

1. `blind` — subsurface-only features, conspicuity-reweighted positives (the hypothesis).
2. `blindflat` — identical features, **unweighted** positives (ablation: isolates the reweighting mechanism).
3. `blindtopo` — reweighted positives but Band 19 log-slope added as a feature (ablation: tests whether the shift correction survives when the model is allowed to see conspicuity).

## Instruments and decision rule (frozen)

- **Primary promotion instrument:** `HOLDOUT-DTI`, `gems57-pooled-hide-v2`, buffered whole-component draws seeds 20 + 30 (8 folds, 22,663 withheld positives), strict draw-blind LOQO (hidden components + 3 px collar excluded from training), emission under fold-visible `d_visible > 2.0`. Repository holdout-best on this instrument: `COULOMBLOQO standalone 0.113316 [0.100614, 0.127163]`; supervised reference `H19-5 0.096757`.
- **Mechanism instrument (reported, not a promotion gate):** the same folds restricted to withheld components in the **lowest conspicuity tercile** — the regime the hypothesis claims to win.
- **Leakage canary:** every feature alone, symmetric AUC ≤ 0.90 on the withheld positives vs. far negatives.
- **Uniqueness:** pre-placement surface Spearman |ρ| ≤ 0.90 vs. every local registry raster; final dots forward 3 px overlap ≤ 0.70 vs. every dot-field raster; dense rasters compared on a matched-budget top-K support (policy resolution documented in `IRREGULARITIES.md` this session). Both literal and matched-budget readings are printed.
- **Verdict rule:** `promote` only if the best arm's primary `HOLDOUT-DTI` point estimate exceeds `0.113316` **and** the paired 95 % CI vs. the `blindflat` ablation excludes 0 **and** all uniqueness gates pass; otherwise `negative`. Negative results are deliverables.

## Official sources (line-by-line, for manual review)

- Competition problem/metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Rules (NREL/TP-5700-96647): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS GDR #1391: https://gdr.openei.org/submissions/1391
- Covariate shift / importance weighting: Shimodaira (2000) https://doi.org/10.1016/S0378-3758(00)00115-4 ; Sugiyama, Krauledat & Müller (2007) https://jmlr.org/papers/v8/sugiyama07a.html
- Poisson's relation: Chandler, Koski, Hinze & Braile (1981) https://doi.org/10.1190/1.1441136
- ASF OPERA DISP-S1 (for Rank 5, not reachable here): https://www.jpl.nasa.gov/go/opera/products/disp-product-suite/
