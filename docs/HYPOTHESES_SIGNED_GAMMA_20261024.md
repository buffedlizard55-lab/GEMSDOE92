# Hypotheses — 2026-10-24 SIGNED-GAMMA Session (ranked before building)

Protocol: generate 3–5 geologically distinct, previously untried hypotheses, rank by expected HOLDOUT-DTI gain per build cost, validate top one on spatially-blocked hide-and-recover before any weekly-slot consideration. All expected gains are MODEL projections, not organizer scores. Leakage canary threshold symmetric AUC 0.90. Budget: 3 experiments / 2 h. Stay in one lane; literal uniqueness vs registry is hard stop (ρ>0.90 or >70% dots within 3 px).

Design constraint (verified): R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 exactly (pixelwise, session 2026-10-24). Any file whose dots stay on the H19-5 worm skeleton shares ≤70% within 3 px of R0 only by emitting skeleton pixels R0 dropped—behavioural near-duplicate. True lane separation requires material fraction >3 px off whole skeleton and pays for displaced parent mass.

Training stack is now present (`.cache/gems_inputs/training_features.tif` 418,912,844 B, sha256 `4371c82e…`, 19 bands, EPSG:32611 100 m) via `scripts/restore_inputs.py` (pinned `registry/session_manifest.json`). Band semantics verified this session (see `evidence/breakline_proxy_audit.json` band list): Band 5 `iso_grav_anom_slope` unsigned HGM, Band 18 `iso_grav_anom_hg` signed E-W `dg/dx` (sole signed band), Band 12 `det_elev`, Band 19 `det_elev_slope`, Band 6 `tilt_angle`, Band 15 `depth_to_base_surf`, Band 17 `cond_surf`, Band 8 `geod_dilaterate`, etc.

---

## 1. SIGNED-GAMMA OFFSET — Basinward gravity-edge displacement (BUILD THIS SESSION) ★

- **Layers:** `training_features.tif` Band 18 `iso_grav_anom_hg` (signed E-W `dg/dx`, range [-15.44,+12.86], the sole signed field) + Band 5 `iso_grav_anom_slope` (unsigned HGM magnitude, corr=0.962 with ||grad g||) + Band 12/19 as valid-topography mask only. No catalogue geometry.
- **Physical signature:** `HGM ridge = pct_rank(Band 5) >0.85` (strong gravity gradient edge). `L = pct_rank(Band 5) × pct_rank(|Band 18|)` (edges that are strong both as magnitude and as E-W directional step). Candidate **not on the ridge** but **3–5 px basinward**: offset vector `+dx` (east) where `Band 18 <0` (gravity dropping eastward → basin east of fault, W-dipping footwall high west) and `-dx` (west) where `Band 18 >0`. Dipping/listric normal-fault model (USGS Jachens & Moring isostatic inversion literature: OFR 2000-0189, 2005-1339; Geosphere 2017) predicts HGM peak sits basinward of surface scarp by `depth × cot(dip)` (100–500 m at 1–3 km depth, 45–60° dip). Catalogue mapped scarps (Qfaults from older aerial imagery) and worm skeleton trace the HGM crest; expert DEM mapping (competition labels, DrivenData #306 p.967) traces the surface scarp—offset reveals blind under-cover segment.
- **Why it finds catalogue-missing faults:** Concealed intrabasin/range-front faults under Quaternary basin fill (e.g., Dixie Valley, Edwards Creek, Fallon basin) have a clear isostatic gravity step (basement offset) but no scarp on older low-res imagery and no magnetic contrast (same alluvium both sides) → absent from Qfaults and from H19-5 worms (which required magnetic+gravity concordance). They are precisely the "new fault" that includes newly mapped geometry of an existing system—tip extensions and parallel strands under cover (forum guidance thread 11516). A dot on the HGM crest earns credit only if truth aligns with the density edge; a dot basinward of it earns credit where the new-fault surface trace is offset from the edge—exactly the hidden portion.
- **Difference from repo:** No prior lane used signed Band 18 at all. SNAP used Band 5 magnitude only, BREAKLINE used DEM only, RELIEF/DILATATION used tercile re-ranking on skeleton, CONCENTRATION used block density. No lane ever placed dots deliberately offset from a geophysical edge following a dip-direction rule. The far pool is >3 px off every H19-5 pixel by construction, so ~55% vs R0 forward overlap (unique vs worm family) if we keep 55% parent.
- **Named mimic (falsifier):** Lateral density gradients from facies changes within basin fill (e.g., coarse fan wedge vs lacustrine clay), paleoshoreline beach ridges with density contrast, and salt/ash layers—all produce gravity edges with no brittle fault. Dots concentrated on a fan-margin step would be pure FP.
- **Expected DTI & cost:** MODEL HOLDOUT-DTI +0.001 to +0.004 vs R0 (0.004006) on `gems57-pooled-hide-v2` (8 buffered folds, 22,663 withheld), SGMC bedrock-fault control predicted flat-to-up (SGMC faults are basement offsets, should enrich). Leakage canary: Band 5 AUC 0.5149, Band 18 |AUC| ~0.54 (both <<0.90 from prior screens). Implementation cost **LOW** (two band reads, two percentile ranks, ridge roll offsets, one spaced_top_mask). **Rank 1/5** — cheapest direct test of a textbook gravity-edge offset that no prior lane exercised.

Free, official data source: none needed beyond pinned stack (USGS GeoDAWN via `registry/session_manifest.json`). Upstream USGS GeoDAWN catalog for manual review: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 (17 U.S.C. §105 public domain). Competition page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ (metric: DTI α0.2 β0.8 R=300 m).

---

## 2. STRAIN-SHARPENED BREAKLINE — Active dilatation × coherent scarp-break (rank 2)

- **Layers:** Band 12/19 BREAKLINE `L = pct_rank(||grad Band19||) × coherence(Band12)` multiplied by normalized Band 8 `geod_dilaterate` (nstrain/yr, p33=3.80 p67=7.24, mean 6.36) and optionally Band 4 `geod_2ndinv`. `L_strain = L × (0.5+0.5×pct_rank(Band 8))`. No catalogue geometry.
- **Signature:** Linear, coherent DEM break-in-slope that is currently dilating—an extensional fault presently loading. The 2020 M6.5 Monte Cristo Range earthquake ruptured largely unmapped Candelaria fault segments (USGS pub 70217872; Koehler et al. 2021 SRL) showing seismogenic, absent-from-catalogue structures are active.
- **Why catalogue-missing:** Catalogue is static compilation of Quaternary scarps on pre-2020 imagery; active distributed strain highlights blind structures accommodating contemporary Basin-and-Range extension (Walker Lane shear + Central Nevada Seismic Belt) beneath cover, invisible to scarp-only mapping.
- **Difference:** DILATATION lane (Band 8 tercile, 0.007 DTI MODEL, duplicate of R0 at 99.4%) re-ranked dots *on* the skeleton; BREAKLINE placed DEM breaks off skeleton. No lane ever used strain as a *multiplier on an independent far lineament*—pure strain or seismicity alone screened too smooth to place dots (BREAKLINE doc §4, rank 3). This is multiplicative sharpening, not re-ranking skeleton.
- **Mimic:** Subsidence bowls from Clayton Valley lithium-brine pumping, agricultural withdrawal (e.g., Fallon basin), and elastic strain shadows around locked Walker Lane strike-slip segments—high dilatation without brittle surface fault.
- **Expected:** HOLDOUT +0.0005 to +0.002 vs R0 if active signal helps; SGMC neutral. Leakage canary Band 8 AUC 0.5149. Cost LOW-MEDIUM (one additional rank). Rank 2—plausible but needs receipt to know if far dose direction is correct first.

Official source: already pinned (Band 8). USGS strain: https://www.usgs.gov/programs/earthquake-hazards/science/science-topics/geodesy (public domain).

---

## 3. CONDUCTIVITY-ALTERATION EDGE — Clay/alteration along permeable fault (rank 3)

- **Layers:** Band 17 `cond_surf` (surface conductivity, S/m, proxy for clay-alteration / fluid-path conductivity) + Band 15 `depth_to_base_surf` (m, sediment thickness) as cover filter. External check: `geodawn_rad_u8.tif` 26 MB (K/Th/U radiometrics, sha256 `c22420f7…`) for corroboration but not used for placement.
- **Signature:** `pct_rank(|∇cond_surf|)` or Laplacian ridges aligned with linear conductivity highs, conditioned on shallow-moderate cover (200–800 m) where alteration is not swamped by thick conductive lacustrine fill. Fault permeability → geothermal fluid circulation → clay/zeolite alteration → elevated conductivity along strike.
- **Why catalogue-missing:** Catalogue faults mapped via scarp/magnetic; geothermal-related hidden faults often lack scarp (blinded by young alluvium) and lack magnetic contrast (juxtaposed identical tuffs) but have alteration halo detectable only by EM/conductivity. Dixie Valley geothermal field's concealed fault is classic.
- **Difference:** No lane used Band 17 at all. BASEMENT-STEP (Band 15) screened out (SGMC AUC 0.378 << chance); radiometric K/Th gradients screened out per SESSION_PROMPT addendum. Conductivity as alteration proxy is orthogonal.
- **Mimic:** Playa clay pans, phreatic evaporite crusts, and thick smectite-rich lacustrine sediments (e.g., Carson Sink) produce high-conductivity lineaments with no faulting.
- **Expected:** Small HOLDOUT gain (+0.0003 to +0.0015); SGMC + maybe if basement faults have alteration, but playa mimic risk high. Leakage canary Band 17 AUC 0.5059 <<0.90. Cost LOW. Rank 3—most geothermal-specific but highest FP risk.

Official sources: pinned Band 17; GDR INGENIOUS conductivity/alteration via https://gdr.openei.org/submissions/1391 (CC BY 4.0); USGS Geochemistry: https://www.usgs.gov/centers/gemsc (public).

---

## 4. TILT-ANGLE MAGNETIC BASEMENT EDGE — Tilt-zero worm persistence (rank 4)

- **Layers:** Band 6 `tilt_angle` (magnetic tilt derivative, range ~[-π/2,+π/2], zero over magnetic contact) + Band 14 `tmi` + Band 3 `tmi_hg`. Signature: tilt zero-contour persistence across vertical-derivative scales (analytic-signal analogue without amplitude bias). `T = pct_rank(|tilt|) _inverted` near zero? Actually place on `|tilt| < ~5°` contours where horizontal extent >1 km and corroborated by `|TMI_hg|>p75`.
- **Why catalogue-missing:** Magnetic basement offset under >500 m basin fill has no surface scarp and weak H19-5 worm expression (H19-5 required multi-field ridge concordance; single-field tilt edge may have been dropped as sub-bar during H19-5 pruning). Expert magnetics mapping traces such edges; catalogue from aerial photos missed them.
- **Difference:** H19-5 worms used analytic-signal / HGM ridges; tilt-zero is amplitude-normalized (Miller & Singh 1994) and detects deeper, weaker contacts that fail amplitude threshold—different detection physics despite same magnetic source field. No prior lane implemented tilt-zero persistence (cvarlw-thin and xscale-worm-persistence attempted scale persistence on other fields, both 0.23/0.058 live but not tilt).
- **Mimic:** Intrabasement lithologic contacts (e.g., granite vs gabbro sill), Curie-isotherm topography, and cultural noise (powerlines) produce tilt zeros with no Quaternary fault.
- **Expected:** MODEST (+0.0005 to +0.002) if deeper basement faults exist unmapped; leakage low (Band 6 AUC 0.51). Cost LOW. Rank 4—geologically sound but overlaps with H19-5 family more than H1/H2.

Official: pinned Band 6; USGS magnetic processing: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and (public domain).

---

## 5. SHORELINE-MASKED BREAKLINE — Lake Lahontan stillstand suppression (rank 5)

- **Layers:** BREAKLINE `L_pct` (Band 12/19) minus Lahontan shoreline elevation penalty + contour-parallel penalty. Shoreline stillstand elevations 1330 m, 1360 m, 1380 m (USGS/NBMG free compilations: Adams et al. 2008 GSA Special Paper; Reheis 1999 NBMG Map; USGS OFR 2011-1232) + 30 m DEM from USGS 3DEP (https://www.usgs.gov/3d-elevation-program, 1 m links shipped as `1m_DEM_links.csv`).
- **Signature:** `L_masked = L_pct × (1 - shoreline_proximity(elev)) × (1 - contour_parallelism)` where `shoreline_proximity = exp(-(elev - H_shore)² / 2σ²)` σ~10 m and `contour_parallelism = |cos(θ_L - θ_contour)|` averaged over 3 px window (>0.85 = bench).
- **Why catalogue-missing:** BREAKLINE's dominant FP is Lahontan shorelines/terraces (named mimic). Removing shoreline-parallel breaks raises precision (α=0.2 denominator) without sacrificing recall of cross-slope fault scarps.
- **Difference:** Directly attacks BREAKLINE's known mimic class; no prior lane masked by external paleoshoreline elevations. Prior RELIEF/DILATATION removed low-prior dots globally, not by geomorphic process filter.
- **Mimic of the correction:** Fault scarps that happen to parallel contours at shoreline elevation (e.g., range-front fault bench coincidences) would be incorrectly down-weighted.
- **Expected:** If BREAKLINE far mass is shoreline-contaminated, HOLDOUT may be flat (catalogue hide-and-recover not shoreline-sensitive) but LIVE DTI could improve precision; HOLDOUT delta +0 to +0.0005 vs BREAKLINE alone. Cost MEDIUM-HIGH (external shoreline catalog, DEM contour analysis, manual elevation datum alignment to EPSG:32611). Rank 5—only measurable if BREAKLINE live receipt shows far dose earning; not first to test.

Official sources: Adams et al. shoreline elevations via https://pubs.usgs.gov/of/2011/1232/ (public domain); 3DEP DEM https://apps.nationalmap.gov/downloader/ (public); NBMG maps https://www.nbmg.unr.edu/ (state public).

---

## Budget & validation promise

One lane = SIGNED-GAMMA OFFSET (#1). Before any weekly-slot spend, validate on spatially-blocked holdout (`hide whole fault segments with 12-px eroded-quadrant buffer, derive every catalogue-based feature only from visible faults, mask visible faults pixel-exactly, pooled DTI α0.2 β0.8 300 m triangular kernel` via `vendor/gems57/evaluate_holdout.py` + `holdout.buffered_component_draw` 8 folds seeds 20 & 30 → 22,663 withheld positives) and leakage canary (single-band AUC must be <0.90). Also report SGMC off-catalogue USGS bedrock-fault control (62,703 px, `derived_sgmc_faults_100m_u8.tif`). Literal uniqueness checked both vs 14-raster local index and, via `scripts/audit_public_registry.py`, vs 1,279 public default-branch rasters (dense-surface universal-blocker caveat disclosed). Run card JSON with HOLDOUT-DTI + CI, overlap/ρ vs registry, raster sha256, validator output, submission name/note ≤140 chars, verdict promote/negative. Negative results are deliverables.

External data used this session is strictly from pinned `.cache/gems_inputs/` (sha256-verified, no DrivenData login, no dropbox). No new download without free-official-source viability check.
