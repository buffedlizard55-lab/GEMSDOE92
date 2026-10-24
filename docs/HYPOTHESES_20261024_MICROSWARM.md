# Pre-registered geological hypotheses — GEMSDOE92 `MICROSWARM` lane (2026-10-24)

**Protocol:** ranked before building; only the top candidate is validated on the spatially blocked
holdout (`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel) within the 3-experiment /
2-hour budget. Lower-ranked hypotheses remain documented, not built, unless a later session opens a
new budget. Every candidate must pass: single-feature leakage canaries (symmetric AUC ≤ 0.90),
forward 3-px overlap ≤ 0.70 and |Spearman ρ| ≤ 0.90 vs every accessible registry raster, all 10
format gates (finite [0,1], zeros outside footprint, EPSG:32611, 3730×3292, template transform),
and zero catalogue mass.

## Context: what this repo has already tried (do not re-litigate)

| Lane | What it targeted | Status |
|---|---|---|
| R0 / H19-5 → D1.5 → D2.8 → SOLO → B2 | 1-px geophysical+DEM worm skeleton, 2.828 px Poisson spacing, d_cat ≤ 2 px prune | Parent; CLAIM 0.2778 (unverified) |
| RELIEF p10piedmont | 10% mass shift from basin/range to piedmont H19-5 | Holdout best 0.006045; local duplicate of R0 (>0.90 overlap) |
| BREAKLINE f33/f38/f45 | DEM scarp-break coherence Bands 12/19 | 0.004861; duplicate vs public dense witness |
| SCARPPOL f33/f38/f45 | Fall-line signed 2nd derivative Bands 12/19 | 0.005315; 0.900–0.913 overlap with BREAKLINE → duplicate |
| ANASIG f45 | Analytic signal Bands 3/9/14 | 0.004967; below holdout best; witness blocked |
| STRAINBREAK f45/f60/f75 | \|∇strain\| × scarp break Bands 4/19 | 0.005487 best; below RELIEF p10; witness blocked |
| STEPEDGE f33/f45/f60 | Aperture-persistent DEM steps Band 12 | 0.003980; SGMC-best 0.1415 but below holdout bars |
| PIEDFRONT f35/f40/f45 | Piedmont scarp-break × envelope, exact-DTI hole refill | 0.006425 best non-collar; CI vs RELIEF p10 includes 0 |
| APRONRIDGE free1d/s60f40/s50f50 | Piedmont apron (Bands 12/15/5) × RTP curvature crests (Bands 2/6) | 0.008354 #1 standalone; witness blocked |
| HYDROCONDUIT f45pied/f45hydro/f50hydro | R0 + RTP/K-Th/MT/GDR conduit hybrid | 0.008549 #1 hybrid; witness blocked |
| visible-collar / DILATATION / TIPGAP / STEPOVER | Catalogue collar, dilatation, tip-gap, stepover dots | Negative / duplicates |

## Ranked candidate hypotheses (new, not yet built)

### Rank 1 — MICROSWARM: short off-catalogue fault-segment rescue (TOP candidate — build this session)

- **Specific layers:** `data/bridge/h19_5.tif` (candidate fault skeleton), `data/bridge/existing_faults.tif` (USGS/INGENIOUS mapped catalogue), `data/bridge/sample_submission.tif` (grid/footprint). Local data only — no external download required.
- **Physical signature:** connected components of the h19_5 skeleton that are **short** (5–60 px ≈ 0.5–6 km) AND lie **>3 px off the mapped catalogue**, emitted as unit-mass dots on a ≥2.8 px Poisson-disk (kernel-radius-matched) grid. Target: dense swarms of short Quaternary normal faults, relay ramps and stepover fractures that host Great Basin geothermal upflow (Dixie Valley / Salt Wells style) but are under-mapped by the catalogue, which favors long through-going traces.
- **Why it catches faults missing from USGS/INGENIOUS:** R0/D2.8/SOLO prune exactly these pixels as "isolated speckle"; MICROSWARM inverts that logic and makes short segments the primary emission. No lane in this repo uses a short-segment-dominated emission; all existing off-skeleton lanes (BREAKLINE, SCARPPOL, STEPEDGE, STRAINBREAK) place dots on continuous ridge/step surfaces, and collar lanes sit directly beside mapped traces.
- **Named non-fault mimic:** Playa shoreline fragments, wash/drainage segments, and alluvial-fan terrace risers can look like short lineaments. Mitigation: h19_5 is already a worm-filtered geophysical/DEM lineament catalogue (not raw topography), plus Euclidean clearance ≥3 px from mapped faults keeps dots off trace-parallel erosional mimics.
- **Difference from this repo:** First lane whose primary emission is pruned-by-predecessors short segments; zero reuse of R0 dots; no Band stack required (works with local data only).
- **Implementation cost:** LOW (one script, local data, <30 min).
- **Expected DTI:** discovery-oriented; dots off catalogue earn little catalogue holdout credit (holdout truth = withheld catalogue segments), so holdout DTI may trail RELIEF p10 (0.006045). SGMC off-catalogue proxy is the natural read, but the pinned SGMC input is absent from this checkout (network-restricted) — report holdout honestly and mark proxy unavailable.

### Rank 2 — HOLE-RESCUE (full network): refill R0's spacing-legal H19-5 holes

- **Layers:** h19_5 skeleton, existing_faults catalogue, parent R0 dots.
- **Signature:** h19_5 pixels >2.8 px from any R0 dot and >2 px off catalogue, refilled to 37,654 dots by exact marginal expected-DTI greedy (`select_exact_marginal_dti_add`).
- **Why missing faults:** R0's D2.8 BFS thinning stranded spacing-legal holes along real strands; PIEDFRONT refilled only 4,000 piedmont holes — full-network hole rescue is untried.
- **Mimic:** bajada aprons and shoreline fragments (same as PIEDFRONT).
- **Difference:** full-network (not piedmont-only) hole refill on skeleton pixels R0 discarded.
- **Cost:** LOW. Near-duplicate risk vs PIEDFRONT's refill stage — check final-dot overlap <0.70 before any build.

### Rank 3 — ORIENTED STEPOVER/RELAY dilation zones (revised geometry)

- **Layers:** h19_5 skeleton, existing_faults catalogue; optionally USGS Quaternary fault trace orientations.
- **Signature:** 3–8 px dilation of skeleton segment endpoints/gaps oriented along Walker Lane NNE–SSW trends — releasing stepover/pull-apart dilation zones where blind geothermal upflow localizes.
- **Why missing faults:** stepover centres are commonly unmapped as discrete faults.
- **Mimic:** incised drainages at jog intersections.
- **Difference:** STEPOVER tip10px N5000 was already built (negative); this hypothesis needs revised geometry (dilation-zone masks, orientation filter) before retry — may need 1 m DEM (USGS 3DEP link, login-gated).
- **Cost:** MEDIUM; external 1 m DEM not verifiable from sandbox.

### Rank 4 — D2.8-minus-SOLO isolated-dot rescue

- **Layers:** d28.tif (44,090 dotted H19-5), h27_4_solo.tif (40,199 SOLO-pruned dots), existing_faults catalogue.
- **Signature:** d28 dots removed by SOLO pruning ("isolated point dipoles"), re-emitted ≥2.8 px apart and >3 px off catalogue.
- **Why missing faults:** SOLO treats isolation as noise; isolated short faults may be real micro-faults.
- **Mimic:** same as MICROSWARM (shoreline/drainage fragments).
- **Difference:** rescues SOLO-removed dots rather than short components; strongly overlapping MICROSWARM's target set — merge into MICROSWARM analysis rather than a separate build.
- **Cost:** LOW (variant of Rank 1).

### Rank 5 — Catalogue annulus band 2.8–5 px (near-trace splays)

- **Layers:** existing_faults catalogue only.
- **Signature:** pixels at Euclidean distance 2.8–5 px from the visible catalogue, off skeleton, spaced ≥2.8 px.
- **Why missing faults:** off-trace splays running parallel to mapped faults within one kernel radius.
- **Mimic:** colluvial wedges and terrace risers hugging mapped scarps.
- **Difference:** close to the already-tested visible-collar lane (negative, catalogue-collar artifact, public duplicate) — lowest priority; build only if a later session revisits collar geometry with non-catalogue truth.
- **Cost:** LOW.

## Decision rule for this session

Build **Rank 1 MICROSWARM** only. Evaluate pooled HOLDOUT-DTI vs R0 and vs holdout-best RELIEF p10 (0.006045), run leakage canaries, measure local registry uniqueness, write the zeros-outside GeoTIFF, run all format gates, and emit the run card (promote / negative). No weekly slot is spent; promotion is a separate human selector step.
