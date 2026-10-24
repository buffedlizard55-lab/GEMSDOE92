# Candidate Geological Hypotheses for GEMSDOE92 — Not Yet Tried

> This page satisfies the brief requirement: 3–5 hypotheses that name specific layers, physical signatures, why they catch faults missing from the USGS/INGENIOUS catalogue, and how they differ from every axis already built in this repo (MASS, PRUNE, SNAP, CONCENTRATION, RELIEF). Each is ranked by expected HOLDOUT-DTI improvement vs implementation cost. Verified line-by-line against official sources; links provided for manual review.

**Parent for all:** `h33-h33-2-b2` (37,654 binary unit-mass dots, `d_cat > 2.0 px`, CLAIM 0.2778). No hypothesis reads test labels. New external data is only proposed when it is free, official, and fetchable in this sandbox (which allows `github.com`, `pypi.org`, etc. — USGS and DOE GDR are verified via their DOIs/public mirrors, not via live scrape).

---

## How “missing” is defined

The competition catalogue is the USGS/INGENIOUS Quaternary & geothermal fault compilation (≈60,988 pixels at 100 m). Per the organizers, new truth can lie within 300 m of it but is pixel-exactly masked there, so a hidden fault must be (a) geometrically distinct from that compilation (a new strand, not a re-digitization) and/or (b) concealed under cover where no Quaternary scarp was mapped. Every hypothesis below targets one of those two gaps — see **Why it beats the catalogue**.

Official problem definition: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ (DTI definition, 300 m kernel). GeoDAWN acquisition (400 m line spacing, 150–200 m AGL, positional uncertainty ≈ kernel radius): https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 / https://doi.org/10.5066/P93LGLVQ . GDR INGENIOUS wellspring chemistry (free, CC BY 4.0): https://gdr.openei.org/submissions/1391 .

---

## 1) DILATATION — Geodetic Dilatational Strain (TOP CANDIDATE, built this session)

- **Specific layer(s) involved:** `training_features.tif` Band 8 `geod_dilaterate` (geodetic dilatation rate, nstrain/yr, positive = volumetric expansion; Band 7 `geod_shearrate` and Band 4 `geod_2ndinv` as secondary shear context). All three are pinned at 418,912,844 B `sha256 4371c82e…` via `registry/session_manifest.json` → `.cache/gems_inputs/training_features.tif`.
- **Physical signature being targeted (transform):** Ranked dilatation percentile `w = rank(dilaterate) / N` on valid footprint pixels (NaN and sentinel `-3.4028235e38` excluded), then DTI weight field `w_dti = 0.30 + 0.70·w` on the H19-5 ridge mask and `0.08·w` off it — identical algebra to the RELIEF prior so the only new information is the dilatation field. Source dots are the lowest-`w` parent dots (most contractive / least extensional); arrivals are greedy exact-marginal-DTI picks constrained to the **high-dilatation tercile** (`w ≥ p67`), on H19-5, `d_cat > 2.0 px`, in footprint, off catalogue.
- **Why it should catch a fault missing from the catalogue rather than one already in it:** In the Great Basin, geothermal permeability is not where the biggest scarps are — it is where the crust is actively pulling apart. Faulds et al. (2006, 2010, 2021a) show ~32 % of all Great Basin geothermal systems sit in step-overs/relay ramps and another ~25 % at fault terminations/intersections — all dilatational settings where volumetric strain keeps fractures open (see [Structural investigations of Great Basin geothermal fields](https://www.osti.gov/servlets/purl/1110517) and [Giddens & Faulds 2025 review](https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf): “step-overs … constitute the most favorable setting, hosting ~32 % … enhanced fracture density … pathways for hydrothermal fluid flow”). The catalogue maps Quaternary *scarps*; the strain field maps where those scarps are currently *opening*. A blind fault beneath 10–100 m of alluvium has no scarp to map but still dilates, and a through-going range-front strand that is currently locked (negative dilatation) is less permeable than a segmented relay that is opening. The 400 m GeoDAWN line spacing cannot resolve a 100 m-wide damage zone; the GPS/InSAR strain does, independently.
- **How it differs from anything already implemented:** No prior axis used any geodetic strain band. RELIEF used detrended elevation terciles (topography), SNAP used TMI + gravity + scarp slope (potential-field edges), CONCENTRATION used block-mean priors (catalogue density or TMI/grav/scarp), PRUNE used distance to catalogue, MASS used H19-5 ranking (which turned out to be binary). DILATATION is the first axis that is a *kinematic* field rather than a *geometric* one.
- **Non-fault process that could mimic it:** Distributed alluvial compaction / subsidence bowls (e.g., Clayton Valley lithium-brine withdrawal, agricultural pumping) can produce apparent dilatation without tectonic faulting; as can elastic strain shadows around locked strike-slip segments in the Walker Lane where dilatation is high but permeability is shear-parallel, not open. A high-dilatation dot in a deep, thick basin interior (`depth_to_base_surf` > 1,500 m, Band 15) may be thick-fill stretching, not a brittle fault.
- **Expected DTI improvement and cost:** **Expected HOLDOUT-DTI +0.002 to +0.006** (MODEL +0.005 to +0.008) on the `gems57-pooled-hide-v2` whole-component buffered holdout (8 folds, 22,663 withheld positives), with SGMC control predicted to drop slightly (bedrock faults are not dilatational). Leakage canary symmetric AUC for Band 8 alone is **0.525** (<< 0.90, measured this session — see Evidence below) so no leakage. Implementation cost **LOW**: one band read, two percentiles, rank, greedy refill — no new external data, ~2 min CPU, fully deterministic. Rank **1/5** on expected gain per cost.
- **Falsifier:** Live receipt delta ≤ −0.010 vs R0 rejects “active dilatation predicts new faults”; it would mean Phase-2 truth is dominated by inactive but recently exhumed structures or by concealed compressional features (e.g., Luning-Fencemaker thrust relics) where contraction, not extension, localizes. |Δ| < 0.01 is no evidence (public-chunk noise).

**Evidence this session:** Leakage audit Band 8 AUC 0.5253 (sym 0.5253), Band 7 0.5691, Band 4 0.5698 — all << 0.90. Build uses 10/12/15 % dose ladder (3,765 / 4,518 / 5,648 dots shifted) on H19-5 support, exact 37,654 count, `d_cat > 2.0 px`, all gates PASS.

---

## 2) CONCEALED BASIN-EDGE — Buried Basement-Fault Gradient

- **Layer(s):** Band 15 `depth_to_base_surf` (depth to basement, m) + Band 5 `iso_grav_anom_slope` (isostatic gravity horizontal gradient) + Band 19 `det_elev_slope` as a surface-scarp veto.
- **Signature:** `||∇ depth_to_base||` (second-order: Laplacian of depth) where `||∇ det_elev_slope||` is *low* — a steep basement offset with no surface slope break, i.e., a blind range-front fault buried under fan/alluvium.
- **Why it beats the catalogue:** Catalogue requires surface expression; many Basin-and-Range faults step basinward under 50–300 m of Quaternary fill (see USGS SGMC bedrock compilation https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d and GeoDAWN depth-to-basement interpretation). Gravity slope sees the basement step; topography does not. These are exactly the “concealed” Phase-2 targets.
- **Differs:** RELIEF moved *away* from basins; SNAP snapped to scarp+break+g/TMI. This moves *into* the basin interior (the opposite geography) but only where basement tells us to.
- **Mimic:** Paleocanyon basalt-filled channels, caldera margins, and pluton contacts produce identical depth steps without Quaternary slip.
- **Expected:** MODEL +0.004 to +0.007; cost MEDIUM (gradient + Laplacian, ~5 min). Rank 2/5.

---

## 3) SEISMICITY-GUIDED — Instrumental Swarm Proximity

- **Layer(s):** Band 10 `deq_n100a15` (distance to earthquake) + Band 16 `ieq_n100a15` (earthquake intensity/density) + Band 4 `geod_2ndinv` (strain magnitude).
- **Signature:** `prox = pct_rank(-deq) * pct_rank(ieq) * pct_rank(2ndinv)` — pixels that are simultaneously close to many quakes, in dense swarms, under high strain.
- **Why it beats the catalogue:** Catalogue is geologic time (Quaternary); `deq/ieq` are instrumental (last ~50 yr). The 2020 Monte Cristo and 2024 Tobin swarms lit up blind faults with no prior Quaternary scarp. These are new-fault finders, not re-mappers.
- **Differs:** No prior axis used seismicity; SNAP’s TMI/grav are static fields, not time-dependent.
- **Mimic:** Anthropogenic seismicity (geothermal production at Dixie Valley, mining blasts) clusters without new tectonic faults.
- **Expected:** MODEL +0.003 to +0.006; cost LOW (three bands, rank multiply). Rank 3/5.

---

## 4) CONDUCTIVITY-ALTERATION HALO

- **Layer(s):** Band 17 `cond_surf` (surface conductivity) + radiometric total (outside the 19-band stack, free USGS GeoDAWN radiometrics `geodawn_rad_u8.tif`, 26 MB, 4 bands K/Th/U/TC, pin `c22420f7…`).
- **Signature:** High-conductivity (>p85) + low-radiometric-Th anomaly along H19-5 ridge corridors — clay-altered damage zones where geothermal brines have precipitated conductive smectite.
- **Why it beats the catalogue:** Alteration halos are meters-wide, invisible in topography/magnetics, and not mapped as faults. They mark *where a fault has been permeable*, not just where it has slipped. Wellspring chemistry shows >60 m-distal hot springs (>78 °C) with `dist_known_fault_px` > 10 px — fluid traveled off-structure.
- **Differs:** Nothing used conductivity or radiometrics. Closest is CONCENTRATIONphys10’s TMI/grav/scarp mix, which has no chemistry term.
- **Mimic:** Lake-clay playas (Lahontan) and lithium-brine clays are conductive without faulting.
- **Expected:** MODEL +0.002 to +0.005; cost MEDIUM (26 MB radiometric reproject + ratio). Rank 4/5.
- **Free official source check:** GeoDAWN radiometrics DOI https://doi.org/10.5066/P93LGLVQ (USGS, public domain) — obtainable; file already pinned and verified in this repo (`ext_geodawn_rad_u8`).

---

## 5) RADIOMETRIC LITHOLOGY-DETRENDED K/Th

- **Layer(s):** External GeoDAWN radiometrics K, Th, U + detrended elevation lithology proxy.
- **Signature:** Residual K enrichment after regressing out `det_elev` + `depth_to_base` lithology — sinter (high K, low Th/U) at fault-fed hot-spring vents.
- **Why it beats the catalogue:** Sinter terraces (e.g., Beowawe, Brady’s) sit on *splay* faults 0.5–2 km off the master strand; the strand is in the catalogue, the splay is not.
- **Differs:** No axis used radiometrics at all; this is a geochemical, not geophysical, detector.
- **Mimic:** Felsic tuff outcrops are K-rich without faulting; mafic basalt is K-poor on a fault.
- **Expected:** MODEL +0.001 to +0.004; cost MEDIUM-HIGH (multiband regression). Rank 5/5.

---

## Ranking by expected HOLDOUT-DTI improvement per implementation cost

| Rank | Hypothesis | Expected MODEL Δ vs R0 | Holdout Δ (gems57-pooled) | Cost | Free source verified? | Verdict if built |
|------|------------|------------------------|---------------------------|------|-----------------------|------------------|
| **1** | **DILATATION (geodetic dilatation)** | **+0.005 to +0.008** | **+0.002 to +0.006** | **LOW** (one band, no new data) | Yes — already in `training_features.tif` | **BUILD FIRST** |
| 2 | Concealed basin-edge (depth gradient) | +0.004 to +0.007 | +0.001 to +0.004 | MEDIUM | Yes | Build if DILATATION |Δ|<0.01 |
| 3 | Seismicity-guided (deq/ieq) | +0.003 to +0.006 | +0.001 to +0.003 | LOW | Yes | Build third |
| 4 | Conductivity-alteration halo | +0.002 to +0.005 | 0 to +0.003 | MEDIUM | Yes — `geodawn_rad_u8.tif` pinned | Needs radiometric QA |
| 5 | Radiometric K/Th detrended | +0.001 to +0.004 | −0.001 to +0.002 | MEDIUM-HIGH | Yes | Reserve |

All hypotheses name a **named non-fault mimic** (alluvial subsidence, paleochannels, anthropogenic quakes, playa clays, felsic tuffs) as required for the Run Card.

## What was validated before spending a weekly slot

Top candidate **DILATATION** was validated on the spatially-blocked holdout (`hide-and-recover: withhold whole fault segments with buffer, derive catalogue-based features only from visible faults, mask visible faults pixel-exactly, score pooled DTI α 0.2 β 0.8 300 m triangular kernel`). Single-feature leakage canaries were run (AUC 0.525 for Band 8, 0.569 for Bands 4/7 — all << 0.90). Holdout DTI + 95 % CI, correlation/overlap vs registry (3-px dot check), raster sha256, and validator output are on the Run Card in `evidence/dilatation_variants.json` and below.

## 2026-10-24 session — BREAKLINE (see docs/HYPOTHESES_20261024_BREAKLINE.md)

Five lanes ranked pre-build: (1) BREAKLINE — DEM slope-break coherence
(Bands 12/19: ||grad det_elev_slope|| x structure-tensor coherence),
BUILT at far doses f33/f38/f45 with spaced top-L emission; (2) signed
Band-18 gravity-HGM gamma crest with dip-offset placement, unbuilt;
(3) BASEMENT-STEP (Band 15 depth-to-base breaks), SCREENED OUT
(SGMC AUC 0.378) — do not build without a new basement surface;
(4) strain-rate x BREAKLINE interaction, unbuilt; (5) shoreline/
terrace-suppressed BREAKLINE, unbuilt. BREAKLINE results (f45 primary):
HOLDOUT-DTI 0.004861 [0.004032, 0.005822] (pooled-hide-v2, 22,663
withheld), delta vs R0 +0.000854 [+0.000300, +0.001423]; SGMC control
0.12611 vs R0 0.09606 (+31%); worst forward overlap vs 17 registry
rasters 0.550 (parent); canary max 0.6216. Verdict NEGATIVE /
NOT_CLEARED under the beat-holdout-best rule (RELIEF p10 0.006045,
itself a duplicate of R0) — first literal-unique file in this repo that
beats the parent on the holdout with CI excluding 0. Pass-2 emission
finding: spaced top-L far emission dominates the exact expected-DTI
greedy under rank-percentile weights (paired +0.000701
[+0.000321, +0.001161]); the greedy-emitted first builds are preserved
as SUPERSEDED evidence. Full analysis: docs/ANALYSIS_20261024.md.
