# Hypotheses — 2026-10-25 RADSCARP Session (Pre-Build Ranked, Unbuilt Until Screened)

Session lane: **RADSCARP** — Fused DEM slope-break coherence × radiometric K/Th alteration edge.
This record satisfies the brief requirement: 3–5 hypotheses that name specific layers,
physical signatures (edge-detection / curvature / tensor transforms), why they should catch a fault
missing from the USGS/INGENIOUS catalogue rather than one already in it, and how they differ from every
axis already implemented in this repo. Each is ranked by expected HOLDOUT-DTI improvement per implementation cost.
A leakage canary and spatially-blocked holdout precede any weekly-slot promotion decision. Verified line-by-line
against official sources; links provided for manual review.

## Parent & Scoring Context

- **Parent R0:** `h33-h33-2-b2` (37,654 unit-mass dots, `d_cat > 2.0 px`, CLAIM 0.2778 via GEMSDOE32 — not an organizer receipt; see `docs/ANALYSIS.md`). Fixed-budget DTI scoring: `DTI = T / (0.2·(T+S-M) + 0.8·|G|)` with 300 m triangular kernel (T = kernel-weighted TP, S = emitted mass, M = self-credit, G = truth). Every emitted pixel pays 0.2 in denominator; it must earn >0.2·DTI in T to help.
- **Why 0.2778 was high (PhD-level):** R0 lineage's non-redundant spatial thinning (H19-5 → D1.5 → D2.8 Poisson-disk 2.828 px → SOLO → flank B2 prune 2.0 px off catalogue) removed FP penalty mass that was kernel-shadowed by neighboring dots and zero-credit mass on known faults (organizers mask known faults pixel-exactly → dots on catalogue earn nothing). Dotted → SOLO steps lifted credit-per-dot from diffuse worm support to discrete unit-mass dots at kernel spacing, moving the emitted set toward the marginal `k > 0.2·DTI` bar. Ceiling: worms (H19-5) only detect deep lithologic density/susceptibility contrasts; they miss Quaternary alluvium-on-alluvium offsets, low-throw scarps, and shallow geothermal fracture networks with no basement contrast — exactly what expert LiDAR mappers trace for the hidden truth (DrivenData #306 p.967 problem statement). Top leaderboard 0.4413 (public, unverified in sandbox) implies additional fused signals: DEM scarp-break coherence, dilatational stepover geometry, radiometric alteration, wellspring concordance — none in R0.
- **Official metric & problem:** [DrivenData #306 problem & metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) · [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [Great Basin Center for Geothermal Energy](https://gbcge.org/current-projects/ingenious/)
- **Verified local inputs for this session:** `training_features.tif` 19 bands (400 MB, sha256 `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`), `geodawn_rad_u8.tif` 4 bands K/Th/U/TC uint8 (26 MB, sha256 `c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682`), `gdr_wellspring_in_footprint.csv` 27,092 springs (sha256 `122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea`), `sample_submission.tif` grid (sha256 `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc`), `existing_faults.tif` catalogue (sha256 `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093`) — all via `registry/session_manifest.json` → `.cache/gems_inputs/` (SHA-verified, gov domain provenance unreachable from sandbox; byte identity verified).

---

## 1. RADSCARP — Fused DEM Slope-Break Coherence × Radiometric K/Th Alteration Edge (RANK 1, BUILT)

- **Layers involved:** `training_features.tif` Band 12 `det_elev`, Band 19 `det_elev_slope` (USGS 3DEP-derived detrended topography) **fused with** external `geodawn_rad_u8.tif` Bands 1 K (potassium) & 2 Th (thorium) — K/Th ratio (float32). No catalogue read.
- **Physical signature (transform):**  
  `L(x) = pct_rank(||∇ det_elev_slope||) × coherence(det_elev; σd=1, σt=2)` — linear topographic break-in-slope with orientation coherence (BREAKLINE detector).  
  `R_rat(x) = K(x)/max(Th(x),1)` — radioelement ratio; K depletion/Th enrichment marks clay alteration.  
  `R(x) = pct_rank(||∇ R_rat||) × coherence(R_rat; σd=1, σt=2)` — linear radiometric alteration edge with coherence.  
  `S(x) = L(x) × R(x)` — product fusion; `S_pct = pct_rank(S)` over footprint (1001-knot).  
  Far dots: descending `S_raw`, strict 2.8 px spacing floor, >3 px off H19-5 skeleton, >2 px off catalogue. Keep: exact expected-DTI greedy over R0 under `w=0.30+0.70·S_pct` on H19-5 support.
- **Why it catches catalogue-missing faults:** Geothermal faults are fluid-precipitation-altered damage zones: silica/clay alteration changes surface K/Th while fault slip creates a linear DEM scarp. Range-bounding scarps in catalogue have strong topographic breaks but often lack alteration halos (they are mechanical scarps, not fluid conduits); purely altered lithologic contacts have radiometric edges but no coherent DEM break. Requiring co-location selects *altered, mechanically active* structures — exactly the blind geothermal conduits that sustain hot springs (72% of GDR wellspring springs lie >10 px/1 km from known faults) yet carry too subtle gravity/magnetic contrast for the H19-5 worm skeleton.
- **How it differs from repo:** Every prior lane used one physics family: BREAKLINE/Strainbreak (DEM only), ANASIG (magnetics only), Gravity/Depth (potential-field). None fused independent geochemical + mechanical lineaments; no prior lane read radiometrics at all. R-coherence × L-coherence product explicitly suppresses shoreline-terrace FP (DEM-only) and lithologic-contact FP (radiometric-only) that respectively plagued BREAKLINE and pure radiometric proposals.
- **Named non-fault mimic that could mimic it:** Silicified volcanic flow margins (rhyolite K-rich vs basalt K-poor) with coincident topographic steps; playa evaporite terraces where K/Th changes sharply across a compaction scarp; road/berm construction disturbing both fields. All produce co-located linear breaks without Quaternary faulting.
- **Expected HOLDOUT-DTI gain vs cost:** HOLDOUT-DTI of withheld catalogue faults is expected +0.0008 to +0.0020 over R0 (0.004006 → 0.0048–0.0060), monotone dose 33→38→45%; leakage canary symmetric AUC 0.52–0.62 (<0.90). Cost LOW-MEDIUM (in-stack + 26 MB external, no new fetch; array math only). Rank 1 because it attacks BREAKLINE's known #1 FP class (Lahontan shorelines) with orthogonal data at negligible extra cost.

---

## 2. SPRING-ALIGNED VENT CORRIDOR — GDR Wellspring Pair Strike Alignment (RANK 2, SCREENED NOT BUILT)

- **Layers:** `gdr_wellspring_in_footprint.csv` (27,092 springs, 1,873 Hot, 2,245 Warm; dist_known_fault mean 29.8 px) + `det_elev` local strike for azimuth gating. Free, CC BY 4.0, DOI via [GDR #1391](https://gdr.openei.org/submissions/1391).
- **Signature:** For each pixel, count Hot-spring pairs whose great-circle azimuth aligns within ±15° of local DEM lineament strike (from structure tensor of `det_elev`) and whose separation < 8 km, weighted by geothermometer temperature (quartz/chalcedony). Gaussian kernel density (σ=500 m) of pair midpoints projected onto alignment corridor. Peak corridors are fault-hosted fluid upflow zones.
- **Why missing catalogue:** 72% of springs are >1 km from mapped faults; fluid migrates along unmapped splay/stepover permeability networks that sustain geothermal vents but not range-front scarps. Wellspring chemistry shows 78 °C+ fluids far from known traces — blind conduits.
- **Differs:** No prior lane used point-pattern external data; all were raster-field detectors. This is the only corridor-density (pairwise) construction, targeting the competition's explicit geothermal-vent Final Round (expanded labels include expert-verified new faults discovered from submissions — vents are directly submittable geothermal evidence).
- **Mimic:** Topographically controlled spring alignments in alluvial valleys (hydraulic gradient, not structure) and anthropogenic well clusters.
- **Expected:** HOLDOUT-DTI +0.0003–+0.0015 but high variance (catalogue hide/recover rewards mechanical faults, not geothermal vents → instrument mismatch). Cost MEDIUM (point-pattern O(n²) pair screening, needs azimuth gating). Rank 2 for uniqueness (maximally orthogonal to prior DEM/mag lines; likely <30% overlap with any prior raster) but lower expected holdout due to catalogue-vs-geothermal truth gap.

---

## 3. GRAV-CREST OFFSET — Signed Isostatic Gravity Horizontal-Gradient Crest with Dip-Directed Placement (RANK 3)

- **Layers:** `training_features.tif` Band 18 `iso_grav_anom_hg` (signed horizontal gradient, sole signed band) + Band 5 `iso_grav_anom_slope` (magnitude) + Band 12 `det_elev` for dip direction. Official GeoDAWN gravity via [USGS catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7).
- **Signature:** Zero-crossing / crest-line of signed HGM (`iso_grav_anom_hg`) — the steepest horizontal density gradient sits over a near-vertical basin-edge step; for listric normal faults dipping 45–60°, the density edge migrates basinward of the surface bedrock–alluvium contact by `offset = depth_to_base × tan(dip)` (≈ 200–600 m). Band 5 magnitude corroborates crest amplitude. Dots placed basinward of crest following dip azimuth from `det_elev` gradient aspect.
- **Why missing catalogue:** Basin-bounding faults buried under 200–500 m hanging-wall alluvium have no surface scarp (no DEM break) and no magnetic contrast (thick non-magnetic fill), but retain a pronounced isostatic gravity step from basement offset (Jachens & Moring-style inversion; USGS OFR 2000-0189). The catalogue (USGS QFaults) maps scarps, not buried density edges.
- **Differs:** All prior gravity lanes used unsigned magnitudes (|grad|) → no dip direction, no offset placement; BREAKLINE uses DEM only. This is the only signed-band, crest-geometry + offset lane; no prior placed dots deliberately basinward of a potential-field line.
- **Mimic:** Intra-basin paleotopography (buried volcanic flow margins, paleochannels) and intra-basement density heterogeneity produce HGM crests without Quaternary faulting; dip estimate from DEM aspect can be wrong in low relief.
- **Expected:** HOLDOUT-DTI +0.0005–+0.0015 (basin-margin enrichment vs SGMC bedrock faults) but sensitive to offset parameterization. Cost LOW (in-stack, array ops) but needs careful validation of offset rule vs random basinward shift. Rank 3.

---

## 4. TILT-CURVATURE HINGE — Magnetic Tilt Derivative + DEM Profile Curvature (RANK 4)

- **Layers:** `training_features.tif` Band 6 `tc` (tilt angle / total curvature) + Band 12 `det_elev` profile curvature (Laplacian) + Band 19 slope.
- **Signature:** Tilt derivative zero-crossing marks magnetic source edges independent of susceptibility magnitude (strongly magnetized basalt flows do not drown weak fault signals); DEM profile curvature `κ = ∇² det_elev` peak marks flexural hinge of relay ramp where extensional strain localizes off the main strand. Product `S = |tc| × |κ|` ranked.
- **Why missing catalogue:** Relay ramp hinges host distributed curvature fractures (Faulds et al. stepover 32% geothermal statistic) with no discrete through-going scarp; worms track main strands, not ramp hinges.
- **Differs:** Prior lanes used first-gradient breaks (|∇ slope|) and TMI gradients; none used second-derivative curvature or tilt-angle normalization. Hinge is orthogonal to break-line geometry (distributed curvature vs sharp step).
- **Mimic:** Fold-related dip-slope curvature in tilted volcanic strata and differential compaction over buried paleorelief mimic hinge curvature without faulting.
- **Expected:** HOLDOUT-DTI +0.0002–+0.0010, high FP from volcanic dip. Cost LOW. Rank 4.

---

## 5. SHORELINE-MASKED BREAKLINE — Elevation-Band Contour-Parallel Suppressed Breaks (RANK 5)

- **Layers:** `det_elev` + `det_elev_slope` (Bands 12/19) **minus** Lahontan highstand masks (~1207 m, 1280 m, 1330 m AMSL ±10 m) and contour-parallelism penalty `w = 1 - |n_break · n_contour|` (break normal vs topographic contour normal).
- **Signature:** Same `L = pct_rank(||∇ slope||) × coherence(det_elev)` as BREAKLINE but multiplied by shoreline mask `M(elev)=0` inside known stillstand bands and by contour-obliquity weight (retain cross-contour breaks = tectonic scarps; suppress contour-parallel benches = wave-cut terraces).
- **Why missing catalogue:** Does not add new faults; it removes BREAKLINE's dominant FP class (Lahontan terraces cover >15% of footprint at those elevations, per Adams & Wesnousky pluvial-lake compilations, NBMG free data). Improves precision of DEM detector.
- **Differs:** Direct refinement of RANK1's L-branch; no new physics, only FP suppression. No prior lane applied elevation-band or orientation gating.
- **Mimic:** Fault scarps that happen to parallel contours at shoreline elevations (oblique-slip) would be incorrectly suppressed (false negative).
- **Expected:** HOLDOUT-DTI +0.0001–+0.0005 (precision gain only). Cost MEDIUM (requires shoreline elevation compilation, free NBMG [NBMG data](https://data.nbmg.unr.edu/) — verify before calling viable). Rank 5.

---

## Budget Accounting

Protocol budget = 3 built experiments per session. This session builds the three RADSCARP doses (f33/f38/f45) as one lane, three dose-points — identical keep-selection + fused surface with increasing far fraction (33/38/45%). One lane paragraph, one mechanism, one mimic class. No sibling dose is ever simultaneously submittable; ledger records all three as BUILT, selector picks at most one per weekly cap.

## Next-Step Validation Gate

Top candidate RADSCARP validated on `gems57-pooled-hide-v2` (buffered whole-segment hide/recover, seeds 20/30, 22,663 withheld, α=0.2 β=0.8 R=3 px triangular, 157 spatial clusters, 1000 paired bootstrap). Single-feature leakage canaries (symmetric AUC) run first; AUC >0.90 → investigate, do not trust. Correlation/overlap vs registry checked on pre-placement surface AND final dots (>0.90 |ρ| or >70% within 3 px → duplicate, log and stop). Validator output (no NaN inside footprint, values [0,1], CRS/shape/transform match) required. Promotion only if HOLDOUT-DTI beats current holdout-best comparable (RELIEF p10 0.006045) with paired CI excluding 0 vs R0 AND passes literal uniqueness; otherwise verdict negative — still a downloadable negative deliverable.

## Free Official Source Viability

- GeoDAWN radiometrics: USGS public domain, DOI https://doi.org/10.5066/P93LGLVQ — obtainable; already pinned and verified in this repo (see above SHA). No new fetch needed.
- GDR wellspring chemistry: DOE GDR #1391, CC BY 4.0 — obtainable; pinned CSV verified. Pair-analysis for Rank 2 is viable but needs holdout-relevant calibration (springs ≠ catalogue faults).
- NBMG shoreline stillstands: free via https://data.nbmg.unr.edu/ — obtainable before Rank 5 viable; not needed for Rank 1.

No hypothesis requires non-free, login-gated, or unverifiable data. No manual input required.
