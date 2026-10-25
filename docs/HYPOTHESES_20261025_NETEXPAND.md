# Pre-registered hypotheses — GEMSDOE92 NETEXPAND session (2026-10-25)

**Branch:** `arena/a7cdad14-gemsdoe92` · **Budget:** max 3 experiments, 0 weekly slots spent by this repo
(selector step is separate). **Evaluator:** `vendor/gems57/evaluate_holdout.py`
(`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel, seeds 20+30 buffered
whole-component quadrant draw, 22,663 withheld positives, pooled DTI + 1,000-draw paired
20 km spatial-block bootstrap). Written **before** any NETEXPAND experiment was run.

## 0. Verified facts this ranking rests on (line-by-line, this session)

1. **The "0.2778" for GEMSDOE32 `h33-h33-2-b2…-zeros` is a CLAIM, not an organizer score.**
   The live GEMSDOE32 page itself labels that file **UNSCORED**, states *"NO ORGANISER SCORE
   EXISTS for this or any artifact in this repository"*, and gives a **projected** 0.2747
   (MODEL, not a score): https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
   (fetched this session). `registry/parents/R0.json` records `receipt: null`;
   `ledger/submissions.csv` holds no organizer receipt. The user's 0.4413 / 0.3195 leaderboard
   figures are likewise **unverified in this checkout** (no receipt; DrivenData requires login).
2. **R0 lineage is nested emission editing of one detector (measured this session from
   SHA-256-pinned rasters):** H19-5 121,131 px (CLAIM 0.1922) ⊃ D1.5 60,069 (0.2477) ⊃
   D2.8 44,090 (0.2600) ⊃ SOLO 40,199 (0.2708, drops dots ≤1 px from catalogue) ⊃
   R0 37,654 (drops the remaining **2,545** dots ≤2 px; min catalogue distance 2.236 px;
   NN spacing ≥2.828 px). Every descendant is a strict pixel-subset of H19-5.
3. **Why it (plausibly) tops the owner's CLAIM ladder — metric mechanics, not geology magic:**
   under DTI (`vendor/gems57/metric.py`), truth credit saturates at 1 per truth pixel while
   every dot pays α=0.2 FP weight. Thinning to ≈kernel-diameter spacing and pruning the
   ≤2 px catalogue halo (catalogue pixels are masked from organizer scoring) removes
   near-zero-yield mass. Marginal bar for one more non-redundant dot: `k > α·DTI ≈ 0.056`
   at DTI 0.2778. **Beating it therefore requires a better detector ranking at the same
   emission rules** (≈37,654 dots, ≥2.8 px spacing, `d_cat>2`), not another thinning trick.
4. **Strongest validated detector uplift in this repo is catalogue-network context:**
   FAULTNET `netfar` HOLDOUT-DTI **0.175147 [0.159756, 0.189860]** vs rebuilt COULOMBLOQO
   control 0.113890 (paired Δ +0.061, CI excludes 0; `evidence/faultnet_holdout.json`),
   but FAULTNET **failed uniqueness** (final-dot overlap 0.759 vs a public 80k dotted raster).
   Best static-instrument detector is LISTRIC/KNICKLOQO ≈0.0109/0.0108. Standalone
   zero-label physics lanes plateau far lower (RADIOCONTACT 0.005066, GRAV-QUAD 0.005092,
   CURIE-DEMAG Rule-2 0.0508). Lesson: supervised LOQO + orthogonal physics ≫ any single transform.

## 1. Five candidate hypotheses not yet tried (ranked by expected HOLDOUT-DTI gain ÷ cost)

| Rank | Lane / layers | Physical signature (transform) | Why it catches a catalogue-missing fault | Difference from everything implemented here | Named non-fault mimic | Gain / cost / viability |
|---|---|---|---|---|---|---|
| **1 (SELECTED)** | **NETEXPAND** — KNICKLOQO 30 features (B2,4,5,7,8,11,12,13,15,17,18,19 + GeoDAWN K/Th/U + GDR #1391 blind plume) **+ LISTRIC 4 + FAULTNET network-context 5 (from visible catalogue only) + 6 new**: gravity analytic-signal amplitude & structure-tensor coherence (B11,B13,B18), standardized magnetic ASA & coherence (B9,B14 gradients), RTP multi-scale variance suppression (B2, 3 vs 15 px), MT change-point at constant cover (B17×B15) | 3-branch quadrant-LOQO HGB learns **interactions**: subordinate splay near a mapped master (context density/tip/strike) × sharp strike-blind basement/magnetic edge (ASA×coherence) × demagnetized/MT-bounded alteration (suppression×change-point); emitted **only on 1-D crests of the new ASA/coherence/listric channels** (pure crest) | Geothermal upflow localizes on splays, relays and step-overs 0.3–5 km from mapped masters (Faulds & Hinz 2015) whose scarps are diffused/buried — invisible to scarp cataloguing — but whose density/susceptibility edge and clay-cap/alteration halo persist in GeoDAWN potential fields + MT | FAULTNET had context but **no** ASA/coherence/curie features and crested on old channels (→ duplicate); KNICKLOQO/LISTRIC had **no network context at all**; GRAV-QUAD/CURIE-DEMAG tested ASA/suppression **standalone, never as LOQO inputs**; magnetic ASA and MT change-point have never been computed in this repo in any form | Range-front lithologic contacts parallel to mapped faults; equant plutons (killed by coherence); thick non-magnetic Lahontan sediments (fake suppression); playa salinity fronts (fake MT change-point) | **Highest**: builds on the only two validated uplifts (context +0.06 Rule-2; LOQO ≈2× standalone). Cost **medium** (reuses `knick_loqo`, `listric`, `faultnet`, `gravquad`, `curie_demag` functions; ~45-col LOQO). **Viable now**: all inputs SHA-256-pinned and restored this session (`training_features.tif 4371c82e…`) |
| 2 | **GDR-GEOTHERMOMETER-FIELD** — standalone IDW/kriged quartz/chalcedony/cation temperature field from pinned GDR #1391 table (27,092 rows), `dist_known_fault_px` dropped, `thermalclass` whitespace defect fixed | Interpolated reservoir-temperature surface × B15 thin-cover gate | Directly targets **hot, fluid-conducting** blind feeders with zero topographic/potential-field expression — the literal "geothermal vent" signal | GDR data has only ever been 1-of-30 classifier features (`gdr_blind_geotherm_plume`); never a standalone geostatistical field with variogram audit | Irrigation-return / high-TDS shallow groundwater; playa evaporative concentration | Medium gain (field-scale recall, poor 100 m trace precision) / low cost / viable now (pinned CSV `122718e…`; source https://gdr.openei.org/submissions/1391) |
| 3 | **TENSOR-RIEDEL** — B11,B13,B18 gravity gradient tensor + B7,B8 geodetic shear azimuth + B12 strike | 15–25° (R) / ~75° (R′) obliquity filter bank between surface strike and basement-tensor strike, oriented by GPS shear | En-échelon Riedel relays above blind Walker Lane masters host upflow **at the relay**, offset from the single mapped scarp | All prior angular terms reward 0° collinearity (XPHASE, Poisson); none scores *diagnostic obliquity* | Volcanic flow fabric; fault-parallel dikes | Medium / medium / viable now (stack only) |
| 4 | **FLEXURE-HINGE** — B12,B13,B15,B19 | 5–15 km biharmonic `∇⁴z` + paired footwall/hanging-wall curvature-dipole hinge (Buck 1988 elastic flexure) | Buried range-fronts under 150–500 m fill warp cover into monoclines without surface rupture | Prior curvature work is 300–600 m 2nd-derivative only; no 4th-order paired-dipole hinge | Differential compaction over paleo-channels; caldera ring faults | Medium-low / medium (4th derivatives amplify DEM noise) / viable now |
| 5 | **INSAR-CREEP / 3DEP-1M** — Sentinel-1 LOS velocity steps (NASA OPERA DISP-S1) + USGS 3DEP 1 m lidar micro-scarp curvature | mm/yr LOS discontinuity + sub-100 m scarp curvature | Actively creeping / interseismically straining blind faults; scarps below 100 m grid detection | No lane ingests InSAR or 1 m DEM | Groundwater subsidence bowls; Lahontan shorelines | Potentially high / **NOT VIABLE in this sandbox**: free official sources exist — OPERA DISP-S1 https://www.earthdata.nasa.gov/ (ASF DAAC) and USGS 3DEP https://www.usgs.gov/3d-elevation-program — but neither host is on the sandbox allow-list (github/pypi only) and tiles are not staged. Declared non-viable here; do not propose as this session's lane |

## 2. Frozen NETEXPAND specification (single lane; 3 experiments max)

- **Features (45):** KNICK 30 (`gems/knick_loqo.py:FEATURE_NAMES`, catalogue-free) + LISTRIC 4
  (`gems/listric.py`) + CONTEXT 5 (`gems/faultnet.py:context_fields`, self-excluded, rebuilt
  from the **visible** catalogue in every holdout draw; full catalogue only for deploy) +
  NEW 6 (`gems/netexpand.py`, catalogue-free): `grav_asa, grav_coh, mag_asa, mag_coh,
  curie_suppression, mt_changepoint` (IQR-standardized 3-component ASA where band units differ;
  reuses `gravquad.analytic_signal_amplitude/structure_tensor_coherence` and
  `curie_demag.local_variance` — no duplicated math).
- **Model:** 3-branch LOQO exactly as LISTRIC (15% full-45 / 35% province-debiased+new+context /
  50% subsurface-knick+new+context), guard 12 px, negatives >5 px from labels, 4:1,
  `max_iter=185`, within-quadrant quantile calibration (λ=0.80, γ=3.3).
- **Crest (pure):** `L_new = max(√(rank(gravASA)·rank(gravCoh)), √(rank(magASA)·rank(magCoh)),
  rank(curie_suppression·mt_changepoint), L_listric³)`; topo/knick crest channels zeroed
  (the LISTRIC amendment that cured the 0.763 duplicate of KNICKLOQO).
- **Emission:** 37,654 unit dots, spacing ≥2.8 px, `d>2 px` from (visible) catalogue, zeros-outside
  float32 via shared `submission_writer` (fix for portal *"[0,1]"* rejection: all-finite, `nodata=None`).
- **Arms:** (1) `netexpand` d>2 · (2) `netexpand_far` same probabilities, d>4 (FAULTNET's best
  emission) · (3) `nocontext` ablation (identical minus 5 context cols) — attributes the context gain.
- **Holdout (primary, protocol Rule 2):** strict draw-blind fold-visible rebuild per seed
  (context + LOQO refit on visible only, hidden+3 px excluded from training, visible masked
  pixel-exactly). Controls on identical folds: KNICK30 3-branch (original crest), R0 dots,
  H19-5 spaced skeleton. **Promotion bar:** beat **both** the in-run KNICK control **and** the
  recorded FAULTNET `netfar` 0.175147 level with paired 95% CI where computable; any canary
  symmetric AUC >0.90 ⇒ leakage stop (Rule 4).
- **Uniqueness (Rule 1):** surface (pre-placement, top-N) **and** final dots vs the complete
  local registry: fail/stop if |Spearman ρ|>0.90 or >70% dots within 3 px of any one raster.
  Dense continuous public surfaces are reported under **both** readings (literal positive-support
  and FAULTNET's operative matched-budget/dot-field reading, flagged `#IR-92-FAULTNET-DOT-DEFINITION`);
  the literal reading is never hidden.
- **Falsifier:** pooled HOLDOUT-DTI ≤ KNICK control, or canary >0.90, or operative overlap >0.70
  ⇒ verdict `negative` (research download only). Negative results are deliverables.
