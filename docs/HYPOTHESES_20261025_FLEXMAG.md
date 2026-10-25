# Pre-registered hypotheses — FLEXMAG session (2026-10-25)

Written **before** any FLEXMAG surface was computed, any dot was placed, or any
holdout in this session was run. Session budget: ≤3 experiments, ≤2 hours,
0 weekly slots. Protocol: shared evaluator `vendor/gems57/evaluate_holdout.py`
(`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel), shared writer
`vendor/gems57/submission_writer.py`, leakage canary ≤0.90 symmetric AUC per
feature, uniqueness ≤0.70 forward 3-px dot overlap and |ρ|≤0.90 vs registry
(checked on the surface before placement and on final dots).

All band identities below were read from the restored pinned stack itself
(`.cache/gems_inputs/training_features.tif`, SHA-256 `4371c82e…`, GDAL band
descriptions, this session) — no new external data is required for ranks 1–4.

## Ranked candidates (expected HOLDOUT-DTI gain × cost × lane-drift risk)

| # | Hypothesis | Layers (verified band IDs) | Physical signature / transform | Why it catches a fault missing from USGS/INGENIOUS | Difference from everything in this repo | Named non-fault mimic | Expected gain / cost |
|---|---|---|---|---|---|---|---|
| **1** | **FLEXMAG** — a blind (non-breaching) normal fault expresses at the surface as a *forced fold / monocline hinge* in cover and basement at mesoscale wavelength, co-located with a strike-blind magnetic edge from the damage zone / juxtaposed magnetic basement | B15 `depth_to_base_surf`, B12 `det_elev`, B3 `tmi_hg`, B9 `tmi_vg` | Difference-of-Gaussians band-pass (σ 6 px − 30 px ≈ 0.6–3 km smoothing scales) of B15/B12 → \|∇band-pass\| hinge crest × mesoscale structure-tensor coherence × magnetic analytic-signal amplitude √(B3²+B9²) concordance gate | Scarp-based mapping (photo/lidar, the catalogue's basis) cannot see a fault whose tip has not breached the surface; the fold hinge and the subsurface magnetic contrast are its only expressions | No lane isolates a 5–15 km-wavelength flexure hinge; prior scales are ≤600 m steps or 4.5 km strain z-scores. LISTRIC* lanes use ≤8 px surface↔subsurface offsets, not band-pass flexure. ANASIG used magnetic ASA alone at native scale without any flexure concordance | Sedimentary onlap / paleo-valley margins and regional basin-edge flexure (hinge without a fault); dike margins (magnetic edge without flexure) — the concordance product is designed to require both | **Medium / low** (4 bands, closed-form, no training) |
| 2 | **FLEXURE-HINGE alone** (FLEXMAG without the magnetic gate) | B15, B12 | Same DoG hinge × coherence | Same blind-fault rationale | Ablation of rank 1; listed in `docs/NEXT_STEPS.md` untried queue as FLEXURE-HINGE | Basin-margin onlap (unfiltered) | Medium-low / very low |
| 3 | **MAG-QUAD** (magnetic analogue of GRAV-QUAD) | B1 `mag_anom`, B2 `rtp`, B3, B9, B14 `tmi` | Magnetic ASA × native-scale structure-tensor coherence (reuse `gems/gravquad.py:structure_tensor_coherence`) | Hydrothermal magnetite destruction / susceptibility juxtaposition along buried strands invisible in topography | Named untried in `docs/HYPOTHESES_20261025_NEXT.md` rank 5; GRAV-QUAD is gravity-only | Equant intrusions, cultural magnetic noise | Low-medium / very low (GRAV-QUAD standalone plateaued low) |
| 4 | **MT-CHANGEPOINT** | B17 `cond_surf`, B15 | Conductivity discontinuity conditioned on locally constant cover thickness | A fluid-filled fracture conduit changes conductivity without changing cover thickness or topography | Prior MT use gated on conductivity *level*/clay-cap edges, never a change-point conditioned on a third stabilising variable | Playa salinity / irrigation return flow | Low-medium / low |
| 5 | **LOQO-FEATURE-EXPAND** (add ASA/coherence/flexure columns to the KNICKLOQO 30-feature LOQO ensemble) | B2,4,5,7,8,11,12,13,15,17,18,19 + GeoDAWN rad + GDR #1391 | Supervised HGB LOQO retrain | Same as KNICKLOQO | Highest expected raw HOLDOUT-DTI (supervised lanes hold the records) **but** LISTRIC v1 precedent: feature-appended LOQO hit 0.763212 dot overlap vs KNICKLOQO → protocol rule-1 duplicate/STOP. Ranked last on lane-drift risk, not on DTI | K-rich ash beds, equant plutons | High / high (+ duplicate risk) |

## Selected lane (rank 1) — single method paragraph

**FLEXMAG.** Surface (catalogue-free; the catalogue is used only for placement
clearance and holdout masks, never inside a feature):
`hinge = geomean(pct|∇DoG(B15)|, pct|∇DoG(B12)|)`,
`coh = mesoscale structure-tensor coherence of DoG(B15)`,
`mag = pct(√(B3²+B9²) smoothed σ=2px)`,
`S_flexmag = pct( hinge × coh × (0.30 + 0.70·mag) )`.
Emission is the lineage-proven rule, unchanged so the surface is the only
variable: 37,654 binary dots, greedy descending-surface order, ≥2.8 px spacing
(`gems.breakline.spaced_top_mask`, candidate cap 900,000), clearance
`d_catalogue > 2 px`, zeros-outside float32 in [0,1] via the shared writer.

### Experiments (exactly 3, pre-registered)
1. **flexmag** — rank-1 surface above (the candidate).
2. **flex** — ablation: `pct(hinge × coh)` (no magnetic gate).
3. **mag** — ablation: `pct(mag_ASA × native coherence of RTP)` (no flexure).

Control on identical folds/budgets: **GRAVQUAD surface** (`gems.gravquad.lane_surface`,
existing lane, re-placed per draw — a control, not a 4th experiment) and the
final-dot **R0** raster on the static instrument only.

### Holdout (primary instrument, protocol rule 2)
`holdout.buffered_component_draw` seeds 20+30 (whole 8-connected components,
20% hide, 3-px feature buffer, 12-px boundary erosion; 8 quadrant folds,
22,663 withheld positives expected — verify at runtime). Because the surface
is catalogue-free it is computed once; **placement is re-done per draw** with
clearance from that draw's scoring-visible catalogue (`masked_known`), so dots
*can* land on withheld components. Pooled DTI + 1,000-draw paired 20-km
spatial-block bootstrap (`evaluate_holdout.pooled_summary`, seed 520810).
The static final-dot instrument (full-catalogue clearance) is reported only as
a labelled, biased-down diagnostic for table comparability.

### Promotion bar (fixed before results)
`verdict: promote` requires **all** of: (i) primary HOLDOUT-DTI of experiment 1
> 0.113316 (COULOMB-LOQO draw-blind record encoded in prior builders;
KNICKLOQO 0.109043; FAULTNET's higher 0.175147 uses catalogue-network features,
a different feature class — recorded, not recomputed here); (ii) paired 95% CI
vs the GRAVQUAD control excludes 0 from above; (iii) every leakage canary
≤0.90; (iv) local-registry forward overlap ≤0.70 and |ρ|≤0.90 on surface and
final dots; (v) all format gates pass on a disk re-read. Even then,
`submission_eligible` stays **false** in this session: promotion to a weekly
slot is the separate selector step (protocol rule 6), and the literal-reading
registry stop plus a fresh 102-repo public scan must be resolved there.
Anything else → `verdict: negative` (a deliverable), **DO NOT SUBMIT**.

### Data availability check
No new external data needed. Free official sources for manual review:
USGS GeoDAWN <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> ·
DOE GDR #1391 <https://gdr.openei.org/submissions/1391> ·
INGENIOUS <https://gbcge.org/current-projects/ingenious/> ·
competition <https://www.drivendata.org/competitions/306/competition-doe-gems/> ·
reference solution <https://github.com/drivendataorg/gems-prize-reference-solution> ·
EPSG:32611 <https://epsg.io/32611>.
Non-GitHub hosts are unreachable from this sandbox; availability of the
in-stack bands was instead verified byte-for-byte via the pinned
`registry/session_manifest.json` SHA-256 restore (this session, 12/12 files).
