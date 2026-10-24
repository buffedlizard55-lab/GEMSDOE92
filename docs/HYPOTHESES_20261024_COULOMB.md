# Candidate Geological Hypotheses — 2026-10-24 `COULOMB` Session (Pre-Registered Before Any Screening or Building)

**Protocol compliance (Rules 1–6, recorded BEFORE any experiment, screen value, or holdout evaluation):**

- **Lane discipline (Rule 1):** One method lane is built this session (Rank 1 `COULOMB-OPEN` unless its
  pre-placement surface fails the screen gate, in which case the next ranked lane is screened in order).
  Rank-correlation (`|ρ| ≤ 0.90`) and 3-px dot overlap (`≤ 0.70`) are checked on the pre-placement surface
  **before** placement **and** on the final dots against all locally accessible registry rasters. A surface
  failing either check is logged as a duplicate and never built.
- **Reuse, don't rebuild (Rule 2):** Uses `.cache/gems_inputs/training_features.tif` (SHA-256 `4371c82e…`,
  restored + verified this session), `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, α=0.2,
  β=0.8, 300 m triangular kernel), `vendor/gems57/submission_writer.py`, `scripts/exact_dti_refill.py`,
  and `gems.breakline / gems.hydroconduit / gems.apronridge` components (imported, never forked).
- **Evidence labels (Rule 3):** Every metric is labeled `HOLDOUT-DTI` (evaluator version +
  withheld-positive count + 95% CI), `PROXY` (off-catalogue USGS SGMC control), `REGISTRY-MEASUREMENT`,
  or `CLAIM`. A projection is never written as a score.
- **Leakage canary (Rule 4):** Every constituent band and derived surface is tested alone on the buffered
  holdout before trusting any result (`symmetric AUC > 0.90` = stop and investigate).
- **Budget (Rule 6):** Maximum **3 built experiments** within the 2-hour budget. Promotion to a weekly
  submission slot is a separate human selector step; no slot is spent here regardless of outcome.

**Band semantics below were read this session from the pinned `training_features.tif` itself**
(GDAL descriptions, `EPSG:32611`, `3730×3292`): Band 2 `rtp`, 4 `geod_2ndinv`
(strain-rate tensor magnitude), 5 `iso_grav_anom_slope`, 6 `tc` (**mislabeled**: measured in-repo as
radiometric Total Count, `r = 0.99714` with GeoDAWN TC — see `#IR-92-BAND6-TC-MISLABEL`; never used as a
magnetic tilt here), 7 `geod_shearrate` (angular deformation rate, GPS/InSAR), 8 `geod_dilaterate`
(volumetric strain rate, expansion/contraction), 10 `deq_n100a15` (distance to earthquake, n=100 km),
12 `det_elev`, 15 `depth_to_base_surf` (sedimentary cover thickness), 16 `ieq_n100a15` (earthquake
intensity/density, n=100 km), 17 `cond_surf` (subsurface electrical conductivity), 19 `det_elev_slope`.
No new external data is required for Ranks 1–4 (all in-stack + already-pinned GDR/GeoDAWN/SGMC files).

**Why a new lane can still help after `HYDROCONDUIT f45hydro` (`HOLDOUT-DTI = 0.008549`) and
`APRONRIDGE free1d` (`0.008354`):** every built lane weights lineaments by **scalar** strain magnitude
(`STRAINBREAK`: `L × pct(Band 4)`; `HYDROCONDUIT`: `0.5·pct(Band 4)+0.5·pct(Band 8)` averaged, then
multiplied by a static strike prior). No lane **resolves the strain state onto the per-pixel fault
orientation** (opening across the lineament vs shear along it), no lane uses the **shear-rate band**
(Band 7) or the **instrumental-seismicity bands** (Bands 10/16) in any built emission, and no lane
computes an **amplitude-normalized magnetic tilt ratio**. Those four gaps are Ranks 1–4. Rank 5 names
the blocked external-data lane with its exact free official source.

---

## Rank 1 (screen first; build only on screen pass): `COULOMB-OPEN` — Orientation-Resolved Transtensional Opening Tendency on Sharp Lineaments

- **Specific layer(s):** In-stack Bands `2` (`rtp`), `12` (`det_elev`), `19` (`det_elev_slope`),
  `7` (`geod_shearrate`), `8` (`geod_dilaterate`), `4` (`geod_2ndinv`), `15` (`depth_to_base_surf`),
  `5` (`iso_grav_anom_slope`).
- **Physical signature (transform):** `S = max(R_rtp_tilt, R_scarp_rel) × O_coulomb × H_apron`, where:
  - `R_rtp_tilt` = true Miller–Singh / Verduzco phase-normalized RTP tilt-contact edge + positive-Laplacian
    magnetite-destruction trough computed from Band 2 via Laplace's equation (reused
    `gems.hydroconduit.rtp_tilt_and_demag`, not forked);
  - `R_scarp_rel` = background-normalized relative log-slope break `‖∇log(max(slope,0)+1°)‖` ×
    structure-tensor coherence × 600 m cross-strike monotonicity (reused `gems.hydroconduit`
    construction, not forked);
  - `O_coulomb` = **orientation-resolved opening tendency**: local extensional strain
    `E_local = max(standardized Band 8, 0)` projected across the per-pixel lineament normal,
    `E_local × cos²(θ_strike + 90° − α_ext)`, with regional max-extension azimuth pre-registered as the
    design constant `α_ext = 100°` (WNW–ESE Basin-and-Range GPS extension; Hammond & Thatcher 2004;
    Kreemer et al. 2012 — **assumed, never fitted on the holdout**), plus a Walker Lane dextral-shear
    concordance term `pct(Band 7)` concentrated on the NW-striking set (120°–160°) that accommodates
    dextral transtension (Faulds, Henry & Hinz);
  - `H_apron` = thin-cover piedmont accommodation envelope (reused `gems.apronridge.apron_habitat`).
  Emission is **standalone** (0 `H19-5` / `R0` input) on 4-axis 1D crests with 2.8 px spacing, repelling
  all prior far sets `> 3 px`.
- **Why it catches a catalogue-missing fault:** Slip/dilation-tendency theory (Morris, Ferrill &
  Henderson 1996) predicts critically stressed fractures — optimally oriented for simultaneous shear
  slip and normal opening under the present stress field — maintain breccia permeability and rupture
  first, whereas misoriented pre-Quaternary bedrock contacts stay locked and impermeable. The
  `existing_faults.tif` catalogue maps scarps regardless of present-day activity; a young,
  still-propagating blind strand in an opening relay can be geomorphically subtle (missed by
  photo-era mapping and multi-line worms) while sitting in crust that is measurably extending across
  its strike today (cf. the 2020 M6.5 Monte Cristo Range rupture of largely unmapped strands).
  Resolving strain **onto orientation** separates opening normal faults from high-strain-rate but
  shear-parallel locked strands that scalar-strain lanes (`STRAINBREAK`, `DILATATION`) cannot tell apart.
- **How it differs from everything already implemented:** `STRAINBREAK` multiplies isotropic `BREAKLINE L`
  by scalar `pct(Band 4)`; `DILATATION` re-ranks **on**-skeleton dots by scalar Band 8 (99.4% `R0`
  overlap, literal duplicate); `HYDROCONDUIT` averages scalar `0.5·pct(Band 4)+0.5·pct(Band 8)` and
  multiplies by a **static** strike prior `0.35+0.65·cos²(az−15°)` that scores a strike identically in
  extending and locked crust. `COULOMB-OPEN` is the first lane to **multiplicatively couple signed local
  dilatation/shear with per-pixel strike misfit** (the same strike scores differently in extending vs
  contracting crust), the first to use **Band 7 (`geod_shearrate`)** in any built emission, and a
  standalone (0-skeleton) emission like `APRONRIDGE free1d` but on a Coulomb-reweighted surface with
  explicit prior-far repulsion. Pre-placement surface uniqueness vs `HYDROCONDUIT`/`APRONRIDGE` is
  **measured, not assumed** (screen gate below).
- **Named non-fault mimic:** Distributed alluvial compaction / groundwater-withdrawal subsidence bowls
  (e.g., Clayton Valley brine withdrawal, agricultural pumping) produce apparent dilatation without
  tectonic faulting; Walker Lane elastic strain shadows show high shear rate parallel to locked
  strike-slip segments with no open normal fault; and incised piedmont wash walls can align near-NNE
  by chance inside extending crust.
- **Expected DTI improvement / cost:** **Highest expected `HOLDOUT-DTI` of the screenable set**
  (standalone-Coulomb point estimate in the `0.006–0.009` band spanned by `PIEDFRONT`–`HYDROCONDUIT`;
  beating the repo best `0.008549` is NOT assumed — it is the promotion bar). Directly implements
  `docs/NEXT_STEPS.md` Priority 2 item 4 (queued `COULOMB-SLIP-TENDENCY`, never built). Cost **LOW–MEDIUM**
  (in-stack bands + reused components; one strain-projection pass). Data **viable now** (all SHA-pinned).
- **Falsifier:** Screen canary `> 0.90`, surface top-37,654 overlap `> 0.70` or `|ρ| > 0.90` vs any
  pre-session raster (duplicate → do not build), or built `HOLDOUT-DTI` at/below `R0` with paired CI
  excluding a gain.

## Rank 2 (screen if Rank 1 fails its screen gate): `SEISMO-SWARM` — Instrumental-Seismicity Proximity × Coherent Lineament

- **Specific layer(s):** In-stack Bands `10` (`deq_n100a15`), `16` (`ieq_n100a15`), `4` (`geod_2ndinv`)
  for the swarm prior; Bands `12`/`19` (relative-scarp coherence) or Band 2 (RTP-tilt edge) for 100 m
  localization.
- **Physical signature:** `prox = pct_rank(−deq) × pct_rank(ieq) × pct_rank(2ndinv) × L_coh`, where `L_coh`
  is a sharp coherent-lineament field (relative log-slope break × coherence, reused construction).
  Pixels simultaneously close to many earthquakes, inside dense swarms, and under high strain — pinned
  to the nearest sharp lineament — are emitted standalone on 1D crests.
- **Why it catches a catalogue-missing fault:** The catalogue integrates Quaternary geologic time;
  `deq`/`ieq` integrate instrumental decades. Swarms and mainshock–aftershock sequences light up blind
  faults with no prior Quaternary scarp (2020 Monte Cristo M6.5; 2008 Wells M6.0). A swarm-centered
  lineament with no catalogue trace is exactly the competition's "new fault" target class
  ([problem p.967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).
- **How it differs:** Bands `10`/`16` have **never been used in any built lane** (proposed only as
  Rank 3 in the DILATATION hypotheses doc; never screened or built). Near-guaranteed surface
  uniqueness by band disjointness.
- **Named non-fault mimic:** Anthropogenic seismicity (Dixie Valley geothermal production, mining
  blasts) clusters without new tectonic faults; deep (>15 km) swarm lineations need not project to a
  mappable surface trace.
- **Expected / cost:** **Low–moderate** expected gain — `deq`/`ieq` kernels use `n = 100 km` radius
  (per GDAL descriptions), far smoother than the 300 m DTI kernel, so all localization rides on `L_coh`.
  Cost **LOW**. Viable now (in-stack).

## Rank 3 (screen only unless Ranks 1–2 both fail): `MAGTILT-CONTACT` — Amplitude-Normalized TMI Tilt-Derivative Zero-Crossing Ridge

- **Specific layer(s):** In-stack Bands `3` (`tmi_hg`), `9` (`tmi_vg`, signed), `2` (`rtp`, coherence gate).
- **Physical signature:** Magnetic tilt angle `θ_m = atan2(Band 9, Band 3 + ε)` (Salem et al. 2007);
  zero-crossing ridge `exp(−|θ_m|/0.25) × pct(‖∇θ_m‖) × coh(Band 2)`.
- **Why it catches a catalogue-missing fault:** The ratio `atan2(VG, HG)` is amplitude-normalized:
  it equalizes weak, deep buried basement fault contacts against shallow Neogene basalt clutter,
  whereas `ANASIG`'s `sqrt(Band 3² + Band 9²)` amplitude decays as `1/z²` and is dominated by shallow
  noise. Concealed intrabasin faults with zero scarp and deep magnetic steps are the target.
- **How it differs:** Proposed as Rank 4 in the PIEDFRONT hypotheses doc but **never built**; no lane
  has computed the signed ratio `Band 9 / Band 3`, its gradient, or an RTP-coherence-gated tilt ridge
  (`ANASIG` used unnormalized amplitude; `HYDROCONDUIT`/`APRONRIDGE` used Band-2-derived edges, never
  the TMI VG/HG ratio).
- **Named non-fault mimic:** Remanently magnetized lava-flow margins, dike swarms, and cultural metallic
  infrastructure produce identical tilt zero-crossings.
- **Expected / cost:** **Low–moderate** (magnetic-only lacks 100 m scarp localization per the `ANASIG`
  lesson: `0.004967`). Cost **LOW**. Viable now (in-stack).

## Rank 4 (screen only unless Ranks 1–3 all fail): `MTEDGE-DILAT` — Standalone MT Conductivity Lateral-Edge × Dilatation

- **Specific layer(s):** In-stack Bands `17` (`cond_surf`), `8` (`geod_dilaterate`).
- **Physical signature:** `pct(‖∇Band 17‖) × pct(max(Band 8, 0)) × coh(Band 17)` — the lateral edge of
  conductive smectite clay caps / brine plumes in positively dilating crust.
- **Why it catches a catalogue-missing fault:** Upflow faults sit at the resistive-to-conductive lateral
  margin of clay caps fed by deep brines (Faulds step-over model); dilating relays keep the margin
  permeable. No scarp required.
- **How it differs:** `HYDROCONDUIT` used Band 17 **level** as 20% of `G_hydro`; `MTSHEAR-CONDUIT` screened
  `‖∇B17‖ × pct(B7)` but was never built standalone and never with signed-dilatation gating. A
  standalone **gradient** (not level) × opening lane is unbuilt.
- **Named non-fault mimic:** Playa lake clays (Lahontan), lithium-brine clays, and conductive
  lacustrine flats without faulting.
- **Expected / cost:** **Low** (MT grid smooth at 100 m; screened components weak at `0.5191` canary /
  `0.0245` far-SGMC). Cost **LOW**. Viable now (in-stack).

## Rank 5 (HELD — not viable in this sandbox; named with exact source): `LIDAR1M-LAHONTAN` — 1 m 3DEP Micro-Scarp Curvature Minus Lahontan Stillstands

- **Specific layer(s):** External USGS 3DEP 1 m bare-earth LiDAR DEM tiles + published Lake Lahontan
  Sehoo highstand (~1330–1338 m AMSL) and recessional stillstand contours.
- **Physical signature:** Sub-meter scarp-crest/base curvature doublets on 1 m LiDAR, resampled to the
  100 m competition grid, explicitly zeroing contour-parallel beach ridges within ±4 m of stillstands.
- **Why it would catch catalogue-missing faults:** Decimeter-scale Holocene scarps are smoothed out of
  100 m `det_elev`; the competition's new-fault labels were expert-mapped on high-resolution DEMs
  ([problem p.967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)), so the
  label-generation instrument itself is the highest-signal channel (likely how the `0.4413` `[CLAIM]`
  leader differs).
- **How it differs:** No lane in `GEMSDOE92` ingests 1 m tiles or true orthometric AMSL shoreline masks
  (`Band 12 det_elev` has regional elevation removed, so absolute 1335 m AMSL contours cannot be
  reconstructed from it).
- **Named non-fault mimic:** (explicitly masked by design) Lahontan beach ridges; residual mimics are
  fluvial terrace risers and fault-line scarps on inactive contacts.
- **Obtainability check (per protocol — FAILS here, so HELD):** Requires (a) `1m_DEM_links.csv` from the
  competition [data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
  (**requires DrivenData login**; sandbox has no credentials and must not request them), and
  (b) USGS 3DEP tiles via `apps.nationalmap.gov` / TNM Access API (**outside the sandbox's allowed
  outbound hosts**: `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`,
  `pypi.org`, `files.pythonhosted.org`). Free official sources exist
  ([USGS 3DEP](https://www.usgs.gov/3d-elevation-program),
  [GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)),
  but they are **not obtainable from this execution environment** → Rank 5 is recorded as HELD and is
  **not proposed as viable this session**.

---

## Pre-registered screen → build rule (identical instruments to prior sessions)

Screen script `scripts/screen_coulomb_surfaces.py` (preserved in-repo, same harness as
`scripts/screen_stepedge_surfaces.py`, gate-zero reproducing the `BREAKLINE-L` baseline) scores each
candidate surface on:

1. **(a) Leakage canary:** single-feature symmetric AUC vs withheld catalogue positives
   (buffered-component folds, seeds 20/30, rng 520810). **Stop that surface if `> 0.90`.**
2. **(b) Discovery diagnostics:** a 16,944-dot spaced top-set (2.8 px floor, `> 3 px` off `H19-5`,
   `d_cat > 2 px`) scored alone as `PROXY` on off-catalogue USGS SGMC bedrock faults
   ([SGMC](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d), 62,703 px) and on the
   fixed-catalogue diagnostic (labeled diagnostic, never a holdout).
3. **(c) Lane-disjointness:** far-set forward overlap vs prior lanes' far dots **and** full-surface
   top-37,654 spaced-set overlap + sampled Spearman vs `HYDROCONDUIT S_hydro`, `APRONRIDGE S_raw`,
   `PIEDFRONT`, `BREAKLINE f45`, `R0`/`H19-5`. **A surface with overlap `> 0.70` or `|ρ| > 0.90` vs any
   pre-session raster is logged as a duplicate and never built.**

**Build rule:** screen Rank 1 (`COULOMB-free`) first. If it passes (a)+(c), build the 3 pre-registered
`COULOMB` experiments below and stop screening. If it fails, screen Rank 2 (`SEISMO-SWARM`) under the
same gate (build up to 3 seismo-parameterized standalone doses on pass), then Rank 3, then Rank 4.
Rank 5 is never built here.

## Pre-registered 3-experiment design (`COULOMB` family; all standalone, 0 `H19-5`/`R0` input)

All three hold the exact unit-mass budget `N = 37,654` dots, `d_cat > 2.0 px`, zero catalogue mass,
2.8 px spacing floor on 4-axis 1D crests, repelling **all** prior off-skeleton far sets `> 3 px`
(Tier-1: off-`H19-5` portions of all prior hybrid far sets + whole `APRONRIDGE free1d`).

*Pre-results construction amendment (same session, before any screen value exists):* 1D-crest pixels are
sparse, so Tier-1 repulsion may exhaust the crest pool below placeable capacity. If the Tier-1 crest
pool holds fewer than 120,000 pixels, the builder falls back to Tier-2 repulsion (the 5 highest-risk
sets only: `APRONRIDGE free1d`, `HYDROCONDUIT f45hydro` far, `PIEDFRONT f35` far, `BREAKLINE f45` far,
`STEPEDGE f60` far) and records the tier used per experiment in `evidence/coulomb_variants.json`. The
binding check remains the post-build whole-file `≤ 0.70 / ≤ 0.90` measurement vs every pre-session
local raster; repulsion is a construction aid, never a substitute for measurement.

1. **Experiment 1 (`COULOMB-free`):** `S = max(R_rtp_tilt, R_scarp_rel) × O_coulomb × H_apron` —
   full-physics standalone; the head-to-head vs `APRONRIDGE free1d` at fixed emission geometry.
2. **Experiment 2 (`COULOMB-open`):** `S = max(R_rtp_tilt, R_scarp_rel) × O_coulomb` (**no** apron gate) —
   ablation testing whether the piedmont envelope helps (expect: more range-core mass, lower
   `HOLDOUT-DTI`, higher `SGMC PROXY`; informative either way).
3. **Experiment 3 (`COULOMB-seismo`):** `S = Exp-1 S × (0.50 + 0.50 × seismo_prior)` with
   `seismo_prior = pct(−deq) × pct(ieq) × pct(2ndinv)` — Rank-1 × Rank-2 fusion test.

### Promotion gate (fail-closed; checked per experiment, not per family)

An experiment may receive `verdict: "promote"` **only if ALL hold simultaneously**:

1. **Holdout-best gate:** pooled `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives,
   8 buffered folds) strictly exceeds the current repo best among locally-unique artifacts
   (`HYDROCONDUIT f45hydro = 0.008549`), with paired 95% spatial-cluster bootstrap CI excluding `0` vs `R0`.
2. **Leakage gate:** every input band and composite surface symmetric AUC `≤ 0.90`.
3. **Literal uniqueness gate (both phases):** forward 3-px overlap `≤ 0.70` and `|Spearman ρ| ≤ 0.90` on
   **both** the pre-placement surface and the final dots vs **every** local registry raster. (Note: the
   binding dense public witness `17GEMSDOE E-proba-multiscale`, positive on 100% of the footprint, is
   expected to keep `submission_eligible: false` under the literal public rule; it is reported, never
   waived. A sparse-public (`≤150k` px) diagnostic is attempted; a rate-limited/partial scan is recorded
   as NOT clearance.)
4. **Automated format gate:** 10/10 MUST gates pass on independent disk re-read (`EPSG:32611`,
   `3730 × 3292`, template geotransform, `float32`, single band, `nodata=None`, all cells finite in
   `[0, 1]`, zeros outside footprint, zero catalogue mass).

Otherwise `verdict: "negative"` — format-valid, **OK TO DOWNLOAD for research**, **NOT CLEARED for a
weekly slot** — published as a negative deliverable with run card, per protocol.
