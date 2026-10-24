# Hypotheses — 2026-10-24 (SCARPPOL session, ranked before building)

> **Historical SCARPPOL-session record.** Values, data-cache statements, and source checks below describe that earlier session and have not been revalidated in the current review. No lane is currently viable or authorized; see [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) and the current [`HYPOTHESES.md`](HYPOTHESES.md).

Protocol step: generate 3–5 previously untried geological hypotheses, rank by
expected HOLDOUT-DTI gain per build cost, validate the top one on the spatially
blocked holdout, stay inside one lane. Evidence labels are strict:
**HOLDOUT-DTI** = `gems57-pooled-hide-v2` pooled hide-and-recover;
**SCREEN-AUC** = single-feature symmetric AUC against the same withheld
catalogue positives (leakage canary instrument, not a DTI score);
**PROXY** = DTI of a spaced top-16,944 far set (>3 px off H19-5, >2 px off
catalogue) against USGS SGMC bedrock faults >3 px from the catalogue
(62,703 truth px). No number below is an organizer score or a projection of one.

Pre-build screens (this session, code in `.cache/diag/screen_*.py`, logs beside
them; surfaces are catalogue-independent, so the canary is a true single-feature
test). Controls on the same instruments: BREAKLINE L — SCREEN-AUC 0.621604,
far-PROXY 0.072325; parent R0 (full 37,654) — PROXY 0.096060.

| Rank | Hypothesis / layers | Physical signature | Why it could find a catalogue-missing fault | Difference from this repo | Screen (SCREEN-AUC / far-PROXY) | Cost / data |
|---:|---|---|---|---|---|---|
| **1 (build)** | **SCARPPOL** — Band 12 `det_elev`, Band 19 `det_elev_slope` | Directional second derivative of slope **along the fall line** (`dir2 = ∇slope · ĝrad_elev`), rank × structure-tensor coherence of `det_elev`. A fault scarp is a *signed* step: slope grows downhill across the crest, falls across the base. `\|dir2\|` fires on that crest/base pair; isotropic `‖∇slope‖` (BREAKLINE) fires on any roughness with the same magnitude. | Same-lithology / alluvium-offset faults with a scarp but no potential-field contrast are missed by the H19-5 worm skeleton; expert DEM mapping (the live label source) traces scarp polarity, not just break magnitude. | BREAKLINE used the *isotropic* magnitude `‖∇Band19‖`; the fall-line-projected, signed second derivative and its crest/base polarity have never been used in this repo. | 0.628012 / 0.067670 (pos-polarity-only variant: 0.622370 / 0.064466) | Low. In-stack bands, SHA-pinned (see below). |
| 2 | **GRAVCREST** — Band 18 `iso_grav_anom_hg` (signed; verified this session: corr 0.78 with ∂x of Band 13, corr 0.49 for \|Band18\| vs ‖∇Band13‖), Band 13, Band 5 | \|Band18\| rank × coherence(Band13): crest of the signed horizontal gravity gradient over a near-vertical density edge, potentially offset basinward of a dipping range-front fault (USGS maxspot literature). | Buried basin-bounding faults under cover with no scarp and no magnetic worm. | Prior lanes used unsigned gradient magnitudes on-skeleton; the signed band's crest geometry and deliberate off-skeleton placement are untried. | 0.533910 / 0.005259 (Band5 variant 0.549720 / 0.005477) — weak on both instruments; not built. | Low, in-stack. |
| 3 | **ANASIG** — Bands 3 `tmi_hg`, 9 `tmi_vg`, 14 `tmi` | Analytic-signal magnitude `sqrt(B3²+B9²)` rank × coherence(Band14): an orientation-invariant magnetic source-edge ridge. | Magnetic basement offsets beneath non-magnetic cover, invisible to gravity worms and DEM. | Repo worms (H19-5 lineage) are corroborated multi-line skeletons; a standalone analytic-signal ridge field placed >3 px off that skeleton is untried. | 0.503999 / 0.028167; ana×BREAKLINE concordance 0.573522 / 0.051244 (still below BREAKLINE alone) — not built. | Low, in-stack. |
| 4 | **HINGE** — Band 13 `iso_grav_anom` (+ Band 5) | \|Laplacian of smoothed Band13\| rank: curvature extrema of the isostatic gravity field = basin-fill hinge / basement-depth step under low relief. | Concealed intrabasin faults with a density step but weak first-gradient and no surface relief. | Prior relief/potential lanes used first-gradient ranks; signed second-derivative hinge lines conditioned on cover are untried. | 0.516863 / 0.025041 — not built. | Low, in-stack. |
| 5 | **SPRINGLINE** — GDR well/spring points (pinned `.cache/gems_inputs/external/gdr_wellspring_in_footprint.csv`, 12,570 unique cells; 928 Hot or ≥50 °C) + GeoDAWN radiometrics K/Th/U/TC (pinned `geodawn_rad_u8.tif`) | Anisotropic (N–S elongated) density of Hot springs/wells; K/Th and radiometric-gradient boundaries as alteration corroboration. Springs discharge where a permeable fault intersects topography — the geothermal-vent expression of a blind fault. | A blind permeable structure may have springs and alteration but no scarp, worm, or gravity crest. | Repo has never placed dots from point hydrothermal data or radiometric ratios. | Spring density/elongation SCREEN-AUC ≈ 0.500–0.517, far-PROXY 0.015–0.018; radiometric gradients far-PROXY 0.062–0.067 but SCREEN-AUC ≈ 0.50. Spring×BREAKLINE ≈ BREAKLINE alone. **Not built**: the point signal carries no measurable catalogue or SGMC enrichment at 100 m in this screen. | Medium. Sources are free/official (GDR <https://gdr.openei.org/submissions/1391>; USGS GeoDAWN <https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7>) and the exact files are already SHA-pinned in `registry/session_manifest.json` — availability verified this session by `scripts/restore_inputs.py` (all 12 pins OK). Revisit only with a line-alignment (spring-pair) construction, not density. |

Strain surfaces were also screened and rejected before ranking:
STRAINCREST (‖∇Band8‖ × coherence) 0.508436 / 0.022668; positive-dilatation
rank 0.512915 / 0.004850. DEM controls: step-gradient σ1/σ2 0.615620–0.617390 /
0.063327–0.065019; multi-scale persistence 0.595158 / 0.067184; elevation
Laplacian 0.590228 / 0.062550 — none clears BREAKLINE, so none is a new lane.

## Decision rule (set before building)

Build SCARPPOL doses f33/f38/f45 exactly as the BREAKLINE template built its
doses (exact-DTI-greedy keep under the lane weight; spaced top-surface far
dots >3 px off H19-5, >2 px off catalogue; 37,654 unit dots). Promote only if
**all** hold: (a) pooled HOLDOUT-DTI beats the current holdout best
(RELIEF p10, 0.006045) **and** paired Δ vs R0 excludes 0; (b) leakage canary
max symmetric AUC ≤ 0.90; (c) literal local-registry uniqueness (forward
3-px overlap ≤ 0.70 and |ρ| ≤ 0.90 vs every local dot raster) on surface
support and final dots; (d) 10/10 format gates. Otherwise verdict **negative**:
format-valid, downloadable, **not cleared for a weekly slot**. The known
full-footprint public witness (17GEMSDOE E-proba, positive on 100% of the
footprint — re-verified this session from its Git blob) is recorded separately
and never waived silently; see the run card.

Named non-fault mimic for SCARPPOL: Lahontan shoreline benches and fan-toe
breaks also produce a signed crest/base slope pair along the fall line, as do
incised channel banks and bedding-plane breaks on dipping strata.
