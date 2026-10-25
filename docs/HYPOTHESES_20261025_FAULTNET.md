# Pre-registration — lane `FAULTNET` (2026-10-25)

Written **before** any FAULTNET holdout number was computed. The only
measurement taken before this file was the single-feature leakage canary
screen required by protocol rule 4 (numbers below, reproduced in the run card).

## Why the parent (`h33-h33-2-b2`, USER-REPORTED 0.2778) scored highest

The lineage of USER-REPORTED (not ORGANIZER-CONFIRMED) scores on the owner's sites is
monotone and nested — every step edits *which pixels of the same H19-5 ridge set*
are emitted:

| raster | positive px | USER-REPORTED score | step |
|---|---:|---:|---|
| H19-5 (19GEMSDOE) | 121,131 (solid lines) | 0.1922 | ridge set |
| D1.5 (GEMSDOE24) | 60,069 (dots) | 0.2477 | thin lines to dots |
| D2.8 (GEMSDOE25) | 44,090 | 0.2600 | spacing 2.8 px |
| SOLO (GEMSDOE28) | 40,199 | 0.2708 | drop dots ≤ 1 px from catalogue |
| **R0 = h33-2-b2 (GEMSDOE32)** | **37,654** | **0.2778** | drop dots ≤ 2 px from catalogue |

Pixel counts were measured in this session from the SHA-256-pinned rasters
(`.cache/gems_inputs/lineage/`). Mechanism under the metric in
`vendor/gems57/metric.py` (`DTI = T / (0.2·T + 0.2·FP + 0.8·|G|)` for binary dots):

1. **Redundancy removal.** With a 300 m (3 px) triangular kernel, dots closer than
   about 2.8 px share truth credit (`T` saturates per truth pixel) but each one still
   costs `α = 0.2` in `FP`. Thinning lines to 2.8 px dots keeps most of `T` and cuts `FP` by about 2.7×.
2. **Known-fault halo removal.** Catalogue pixels are masked from scoring (organiser
   forum thread 11516). Dots ≤ 2 px from a mapped trace therefore score close to zero `T`.
   If the 2,545 dots removed by SOLO→R0 had zero yield, the finite difference
   `Δ(1/DTI) = 0.2·ΔFP / T` gives an implied truth credit `T ≈ 5.5k` and
   `|G| ≈ 15k` pixels. This is a back-of-envelope **projection**, not a score.
3. **Implication.** The parent is an *emission* optimum on a fixed detector. Beating it
   needs a better **detector ranking** at the same emission rules, because the
   marginal bar for one more non-redundant dot is only `k > α·DTI ≈ 0.056`.

## Candidate hypotheses (ranked by expected improvement ÷ cost)

| # | Name | Layers / signature | Why a *catalogue-missing* fault | Difference from repo | Mimic | Cost |
|---|---|---|---|---|---|---|
| **1** | **FAULTNET** (catalogue-network context) | Visible catalogue → self-excluded distance-to-other-fault, 1 km and 4 km fault density, distance to other faults' tips, and a regional-strike × topographic-edge alignment (Band 12 tensor). Added to the 24-feature COULOMBLOQO stack (Bands 2,4,5,7,8,11,12,13,15,17,18,19 + GeoDAWN K/Th/U + GDR #1391) | Fault populations cluster. Splays, antithetic faults, step-over and relay faults sit 0.3–5 km from mapped masters and share their strike (Kim et al. 2004, https://doi.org/10.1016/j.jsg.2003.08.002; Faulds & Hinz 2015, https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11017.pdf). Quaternary-fault compilations map only scarp-forming masters, which leaves these subordinate faults out of the catalogue | **No** LOQO lane in this repo uses the catalogue's own spatial arrangement as a feature (checked: `FEATURE_NAMES` in `coulomb_loqo.py`, `knick_loqo.py`, `poissonflex.py`, `provincetoe.py`) | Lithological contacts and range-front geomorphology parallel to mapped faults | Low |
| 2 | STRIKE-STEER emission | Anisotropic dot spacing along the local structure-tensor strike | Same detector, so better `T` per dot on curved traces | Emission-only, so registry overlap risk is high | Drainage lineaments | Low |
| 3 | MAG-TEXTURE OFFSET | Band 2 RTP windowed registration across trial lines | Buried strike-slip offsets of older fabric | Kinematic, not amplitude | Intrusive contacts | High |
| 4 | InSAR velocity step | Sentinel-1 LOS velocity discontinuities (OPERA DISP-S1, https://www.earthdata.nasa.gov/data/catalog/asf-opera-l3-disp-s1-v1.0) | Creeping or interseismic strain on unmapped faults | New data | Groundwater subsidence | **Blocked**: ASF/Earthdata is not on the sandbox allow-list |
| 5 | 3DEP 1 m scarp curvature | USGS 3DEP lidar (https://www.usgs.gov/3d-elevation-program) | Sub-100 m scarps | New data | Shorelines | **Blocked**: USGS is not on the allow-list |

## Frozen arms (budget = 3 experiments)

All arms share these settings: 37,654 dots, 2.8 px spacing floor, `directional_ridge_1d` crest gate,
COULOMBLOQO HistGradientBoosting LOQO (guard 12 px, negatives > 5 px, 4:1), and `sub_weight = 0.80`.

1. `netctx` — 24 physical + all 5 context fields; emission `d > 2 px` from the (visible) catalogue.
2. `netdens` — 24 physical + `cx_dens10, cx_dens40, cx_strike` only (no point-distance fields), `d > 2 px`.
3. `netfar` — `netctx` surface, emission restricted to `d > 4 px` (hedge: drops the 300 m halo
   that the R0 lineage shows to be low-yield on the organiser truth).

## Instrument and gates (unchanged shared tools)

- Primary instrument: **strict draw-blind fold-visible** `gems57-pooled-hide-v2`.
  It uses `buffered_component_draw` seeds 20 and 30 and refits every model from the visible catalogue only,
  excluding hidden components plus a 3 px collar. Context fields are rebuilt from the visible catalogue,
  and visible faults are masked pixel-exactly. The CI is a 1,000-draw paired 20 km cluster bootstrap.
- Comparable controls on identical folds: `COULOMBLOQO standalone` (the current holdout best, 0.113316 / 0.113890
  in earlier runs, rebuilt here) and `H19-5`.
- **Promotion rule:** best arm DTI > rebuilt COULOMBLOQO control **and** paired 95% CI of the difference > 0,
  canaries ≤ 0.90, format gates pass, registry rank-ρ ≤ 0.90 and dot overlap ≤ 0.70 (see the uniqueness
  reading below).
- Leakage canary screen (seeds 20/30, symmetric AUC, measured before this file): `cx_logdist` 0.751 / 0.742,
  `cx_dens10` 0.739 / 0.728, `cx_dens40` 0.697 / 0.698, `cx_strike` 0.508 / 0.512, `cx_logtip` 0.779 / 0.774.
  All are ≤ 0.90.

## Uniqueness reading (owner decision, flagged `#IR-92-FAULTNET-DOT-DEFINITION`)

The rule reads "more than 70% of your dots fall within 3 px of one registry raster's dots". A
registry raster whose positive support covers the footprint (for example 17GEMSDOE `E-proba-multiscale`, 5,167,373 px)
has no "dots". Read literally, it rejects **every** possible non-empty raster, including
a random one, so it cannot detect lane drift. FAULTNET therefore reads it as follows:

- **dot rasters** (positive support ≤ 150,000 px): literal positive support;
- **continuous surfaces** (> 150,000 px): their top-`n` pixels at our dot budget (matched budget),
  **plus** the rank-correlation clause (ρ ≤ 0.90), which is the clause written for surfaces.

The literal reading is still computed and published next to it. This is an interpretation, and it is flagged for human review.

## Link-verification status

The sandbox can reach only GitHub and PyPI. The following links were **not live-verified** from here and need a manual check: the Kim et al. 2004 DOI, the Faulds & Hinz 2015 WGC paper URL (the paper number is from memory), the OPERA DISP-S1 catalogue URL, the USGS 3DEP page, and organiser forum thread 11516 (quoted in earlier repository documents).

## Post-holdout addendum (written after results; does not alter the pre-registered rule)

- An emission-matched control (`control_COULOMBLOQO_far`, d > 4) was added after the first read-out. It made netfar's promotion
  stricter (it must beat both controls) and changed no other arm. See `#IR-92-FAULTNET-POSTHOC-CONTROL`.
- Outcome: all three arms beat the control on the holdout, but all three fail rule 1 on final dots. Verdict `negative` for
  every arm, and 0 weekly slots used. Full analysis: [ANALYSIS_20261025_FAULTNET.md](ANALYSIS_20261025_FAULTNET.md).
