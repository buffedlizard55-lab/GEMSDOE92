# Pre-registered hypotheses — GEMSDOE92 VARIO session, 2026-10-25 (branch arena/d7ca8737-gemsdoe92)

Written **before** any VARIO experiment was run. Budget (parallel-run protocol
rule 6): at most 3 candidate experiments, at most 2 hours of experiment time,
0 weekly submission slots spent by this session. Every number produced later
must be labelled HOLDOUT-DTI (evaluator version, withheld positives, 95% CI),
PROXY, MODEL, CLAIM, or ORGANIZER-CONFIRMED. No projection is a score.

## Verified starting facts (re-measured this session, 2026-10-25)

All items below were re-read from bytes on disk or fetched today; nothing is
copied from a prior session's prose without re-checking.

1. **Grid/template.** `data/bridge/sample_submission.tif` SHA-256
   `2176d08e…35cbc` (matches `registry/data_manifest.json`): EPSG:32611,
   3730×3292, transform (100,0,243350,0,−100,4508550), float32, 1 band,
   nodata NaN, 5,167,373 finite (footprint) cells, 60,988 catalogue pixels in
   `labels.tif`/`existing_faults.tif` (identical SHA-256 `7ba308cc…4093`).
2. **19-band stack restored and hash-verified.** `scripts/restore_inputs.py`
   restored `.cache/gems_inputs/training_features.tif`
   (418,912,844 B, SHA-256 `4371c82e…3bc5`) plus the VENTSCARP external stack
   (`topo_10m_derived_100m_u8.tif` `a6398d99…bfa4`, 9 uint8 bands aggregated
   from the USGS 3DEP 1/3-arc-second DEM, band scales in its pinned manifest;
   `dem10_chi_100m_i16.tif` `8897ba9c…73a5`; `geodawn_rad_u8.tif`
   `c22420f7…a682`, bands K/Th/U/TC; `gdr_wellspring_in_footprint.csv`
   `122718e6…96ea`; USGS SGMC faults raster `643cbe99…2da0`, 83,593 positive
   pixels). Band identities were read from the training-features TIFF tags
   themselves (B2 rtp, B13 iso_grav_anom, B15 depth_to_base_surf,
   B17 cond_surf, B12 det_elev, B19 det_elev_slope, …). Provenance caveat:
   these are SHA-pinned owner mirrors on GitHub, not organizer-authenticated
   downloads (DrivenData is login-walled and unreachable from this sandbox;
   see `registry/session_manifest.json` public_mirror_flag).
3. **Official metric (fetched today).** DrivenData problem page
   https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
   defines DTI with α=0.2 (FP), β=0.8 (FN), triangular kernel R=300 m, worked
   example TPw=3.00, FPw=1.89, FNw=2.00 → 0.60. `vendor/gems57/metric.py`
   implements the same equations (verified against `dti_bruteforce` in
   `tests/test_metric.py`). The same page states the private/public test
   faults are **new faults manually identified by experts, not in the public
   USGS database** — i.e. the live truth is not a catalogue holdout.
4. **Live leaderboard (fetched today).**
   https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
   shows #1 = 0.4413 (xiaofanhu, 5 d ago), #2 = 0.3916. This verifies the
   brief's 0.4413 figure as of today; the brief's 0.3195 figure is stale.
5. **GEMSDOE32 / R0 lineage (byte-verified today).** With
   `d_cat` = EDT distance to the 60,988-pixel catalogue:
   `XOR(R0, D2.8 & d_cat>2) = 0` (37,654 px), `XOR(SOLO, D2.8 & d_cat>1) = 0`
   (40,199 px), D2.8 (44,090 px) ⊂ H19-5 (121,131 px), R0 ⊂ H19-5. The
   reported climb 0.1922 → 0.2600 → 0.2708 → 0.2778 is recorded in
   `ledger/historical_climb.csv` with evidence_label **CLAIM** and
   receipt = N. The GEMSDOE32 page fetched today
   (https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html, commit
   012e17b2) still calls h33-2-b2 **UNSCORED**, projects 0.2747 as "a MODEL,
   not a score", and states "NO ORGANISER SCORE EXISTS for this or any
   artifact in this repository". Therefore **0.2778 remains a CLAIM**
   (owner-reported in the session brief), not ORGANIZER-CONFIRMED.
   Mechanism (metric math, not causal proof of a private score): for a binary
   dot field, DTI = T/(0.2·(T+n−M)+0.8·|G|) with T = covered-truth credit,
   M = total dot self-credit (`vendor/gems57/metric.py`). A non-redundant dot
   raises DTI iff its kernel credit k > α·DTI ≈ 0.052–0.056 at DTI≈0.26–0.28.
   Neighbouring dots on the same 1-px strand share truth cells (T saturates
   per truth cell while n keeps costing 0.2·(1−k)), so thinning H19-5 at
   2.83 px and deleting dots that cannot recover off-catalogue truth
   (d_cat ≤ 2 px) raises mean credit per dot at fixed geometry. The same
   arithmetic predicts diminishing returns beyond B=2 (only 2,545 dots were
   removed between SOLO and R0 for a reported +0.0070), so further pruning of
   the same surface cannot plausibly close the ≈0.16 gap to 0.4413; that gap
   requires higher credit density, i.e. a better-ranked surface, which is what
   this session tests.

## Ranked candidate hypotheses (3–5 required by the brief)

| Rank | Lane / layers | Physical signature (transform) | Why it should catch a fault missing from USGS/INGENIOUS | How it differs from everything implemented in `gems/*.py` | Named non-fault mimic | Expected HOLDOUT-DTI gain / cost |
|---|---|---|---|---|---|---|
| 1 — **VARIO-SCARP-NET LOQO** (implemented this session) | B2 `rtp`; B17 `cond_surf` × B15 `depth_to_base_surf`; USGS 3DEP 10 m-derived `topo_10m` bands 1–8 + `dem10_chi` band 1; on top of the proven 24-feature COULOMBLOQO stack (`gems/coulomb_loqo.py`) and 5 self-excluded FAULTNET context fields (`gems/faultnet.py`) | (a) **Directional semivariogram anisotropy of RTP**: local γ(h,θ)=½·mean[(z(x)−z(x+hθ))²] (Gaussian-localised squared lagged differences) at lags 2 and 4 px, 4 azimuths; features = anisotropy (γmax−γmin)/(γmean+ε) at each lag and the lag-ratio γ4/γ2. A fault that offsets/rotates magnetic fabric, or a damage zone that destroys fabric continuity across strike, produces high across-strike γ with low along-strike γ even where the RTP amplitude step is weak. (b) **MT change-point at constant cover**: \|∇log σ\| (B17) discounted where \|∇log(depth+10)\| (B15) is large, so a conductivity break inside a block of near-constant cover thickness is scored, not a cover-thickness effect. (c) 10 m sub-pixel scarp statistics already aggregated to the 100 m grid (slope_p90/max/std, steep_frac, curv_prof_absmax, aspect coherence, hillshade lineament, relief) + 10 m χ step. | Expert-mapped hidden faults were identified largely from high-resolution topography and lineament interpretation; 1–3 m piedmont scarps are invisible in the 100 m `det_elev` bands but survive in 10 m within-cell slope/curvature dispersion. Buried splays with no preserved scarp can still rotate shallow magnetic fabric (covariance-domain signal) and channel fluids (MT break at constant cover). Catalogue faults are the ones already obvious in 100 m derivatives, so new information must come from sub-pixel topography and covariance/conductivity domains. | No existing module computes a multi-lag directional semivariogram (`anasig`/`eulerfuse`/`poissonflex` use pointwise derivatives/tilt/Euler sources; `xphase` compares phases of two fields). No module conditions an MT gradient on constant basement depth (`hydroconduit`/`coulombdm` use conductivity level or clay-cap edges). `ventscarp` uses the 10 m bands inside its own 26-feature ensemble but never as added columns to the COULOMBLOQO+FAULTNET stack, and never with (a)/(b). Emission arm E3 also tests the GEMSDOE32 live-scatter idea (crest surface blurred at σ=1.85 px before spaced emission) which no GEMSDOE92 lane has used. | Lava-flow/intrusive contacts and GeoDAWN flight-line seams (anisotropy without displacement); playa/aquifer salinity fronts and facies changes (MT break without a fault); Lake Lahontan shoreline berms and fan-age breaks (10 m scarp statistics). Falsification: single-feature leakage canaries, quadrant-blocked LOQO, and the requirement that the new columns improve paired holdout DTI vs a same-draw control refit. | **Highest expected gain.** The only two approaches that have beaten H19-5 on the strict draw-blind instrument in this repo are supervised LOQO ensembles and adding context columns to one (FAULTNET, HOLDOUT-DTI 0.175147, gems57-pooled-hide-v2, 22,663 withheld, evidence/faultnet_holdout.json). Adding three previously unused feature families to that architecture is the cheapest way to test for a further paired gain. Cost: medium (one new module `gems/vario.py`, one run script reusing shared stack/holdout/writer). |
| 2 — Magnetic texture-restoration registration | B2 `rtp` (optional B14 `tmi`) | For candidate traces, estimate the along-trace translation that best re-aligns magnetic texture patches on the two sides (normalised cross-correlation over multiple windows/scales); score = coherent signed offset. | An oblique splay can laterally offset older magnetic fabric while its own topographic trace is buried/degraded — a displacement measurement, not an edge. | No module attempts cross-fault texture matching/restoration; all magnetic lanes are derivative-, tilt- or source-based. | Separate lava flows or intrusive contacts mimicking offset; survey seams. Needs reciprocal-match and held-out-window nulls. | Medium-high potential, **high cost/risk** (trace proposal + registration search in 3 GB RAM); deferred this session. |
| 3 — GDR geothermometer thermal field | Pinned GDR #1391 table `.cache/gems_inputs/external/gdr_wellspring_in_footprint.csv` (SHA `122718e6…96ea`, restored today — obtainable, no new download) | IDW/kriging of quartz/chalcedony/cation geothermometer temperatures with the known `thermalclass` whitespace defect fixed (`'Hot '` vs `'Hot'`) and `dist_known_fault_px` dropped (label leak). | Targets actively conducting (hot) structures directly; a blind geothermal feeder can be invisible in topography/potential fields. This is the most literal "geothermal vent" signal. | Existing lanes use ≥80 °C cells only as one plume feature inside classifiers; none builds a standalone interpolated thermal field. | Irrigation-affected shallow groundwater and playa evaporative concentration mimicking warm cation geothermometers. Spatial precision at 100 m is questionable, so expected DTI gain is modest. | Medium, low cost. Ranked below VARIO because prior zero-label standalone fields in this repo plateau far below supervised LOQO on the holdout. |
| 4 — SEIS-GRAV-LAG | B10 `deq_n100a15`, B16 `ieq_n100a15` vs B13 `iso_grav_anom` | Signed lateral offset between a seismicity-density flank and the neighbouring gravity basement step (cross-strike lag at maximum correlation, 0.3–2 km). | A blind strike-permeable fault can host a seismic swarm alongside (not over) a buried basement step; distance-to-earthquake alone misses the offset geometry. | Prior seismic use is raw distance/intensity; no signed two-field lag exists. | Magmatic/induced swarms over purely lithologic density contrasts. The 100 km-smoothed seismic bands limit 100 m precision. | Low-medium, low cost. |
| 5 — Relief-increment distribution front (optimal transport) | B12 `det_elev`, B19 `det_elev_slope` | Wasserstein distance between elevation-increment distributions sampled on the two sides of a front, conditioned on relief/aspect. | Distributed deformation can change increment-distribution tails after a sharp scarp degrades. | `drainage_knick`/`provincetoe` use convergence/curvature/relief gating, not matched distribution distances. | Shoreline terraces, fan-age and erodibility contrasts; needs relief-matched nulls. | Low-medium, high cost. |

**External data viability.** Rank 1, 3, 4, 5 need only the pinned stacks
restored and hash-verified today (listed above). Rank 2 needs only B2.
The genuinely overlooked free official source is the competition's own
1 m DEM link table (USGS 3DEP, public domain) referenced on the problem
page; it is **not obtainable from this sandbox** (non-GitHub hosts are
blocked, and no sibling GitHub mirror in the manifest carries 1 m tiles),
so no 1 m-DEM hypothesis is claimed viable this session. The 10 m-derived
stack is the finest DEM derivative obtainable here.

## Frozen experiment plan (3 candidate experiments + 2 same-draw controls)

Shared tools only (protocol rule 2): `gems/coulomb_loqo.py` stack + LOQO fit,
`gems/faultnet.py` context fields, `vendor/gems57/holdout.py`
(`buffered_component_draw`, whole components, 3 px feature-context buffer,
12 px domain erosion), `vendor/gems57/evaluate_holdout.py` (pooled DTI,
α=0.2, β=0.8, 300 m triangular kernel, evaluator `gems57-pooled-hide-v2`),
`gems/breakline.spaced_top_mask` emission, `vendor/gems57/submission_writer.py`
packaging. No private fork of the metric, holdout or writer.

- **Primary instrument (pre-registered):** strict draw-blind buffered
  whole-component holdout, seeds (20, 30) — the exact FAULTNET instrument —
  with every catalogue-derived feature (context fields, LOQO labels, emission
  distance) computed from the **visible** catalogue of each draw, visible
  faults masked pixel-exactly in scoring, 37,654 dots per arm.
  HOLDOUT-DTI reported with evaluator version, withheld positives and paired
  spatial-cluster 95% CI against the same-draw controls.
- **E1 `vario_full`** — 24 phys + 9 new (3 semivariogram + 1 MT-changepoint +
  5 topo10/χ) + 5 context = 38 cols; crest surface; spaced emission,
  `d_visible > 2` (holdout) / `d_cat > 2` (deploy).
- **E2 `vario_nctx`** — 24 phys + 9 new, no context (isolates the new physics
  from catalogue-network context).
- **E3 `vario_smooth`** — E1 model (no refit), emission from the crest surface
  Gaussian-blurred at σ=1.85 px before spaced emission (tests the
  live-scatter emission hypothesis on the same instrument).
- **Controls:** `control_COULOMBLOQO` (24 phys, same seeds/draws/code path as
  FAULTNET's control) and `control_H19_5` (scan-order spaced H19-5 dots), plus
  the recorded FAULTNET `netfar` 0.175147 [0.159756, 0.189860] on this identical
  instrument as the historical holdout-best reference (non-paired).
- **Leakage canary (rule 4):** every column alone per seed; symmetric AUC
  > 0.90 ⇒ stop (leakage until proven otherwise).
- **Uniqueness (rule 1):** surface rank-correlation and final-dot
  within-3-px overlap vs the local registry actually present in this repo
  (`docs/downloads/*.tif` + pinned lineage), reported under **both** readings:
  literal positive-support (known to fail for every non-empty raster against
  pinned full-footprint dense surfaces — a specification defect documented in
  `docs/downloads/review_f23_preflight.json`) and the operative sparse
  dot-field reading (registry rasters with ≤150k positive pixels). Promotion
  uses the operative reading and must disclose the literal one; ρ limit 0.90,
  overlap limit 0.70.
- **Promotion rule:** verdict `promote` (to the separate selector step) only if
  (i) format gates pass, (ii) canaries pass, (iii) E1 beats the best same-draw
  control with a paired 95% CI excluding 0, and (iv) operative uniqueness
  passes. Otherwise verdict `negative`. Deployment file = E1 dots from the
  full-catalogue fit, regardless, so a real unique TIFF exists either way; the
  site banner is generated from the run card, not hand-written.
