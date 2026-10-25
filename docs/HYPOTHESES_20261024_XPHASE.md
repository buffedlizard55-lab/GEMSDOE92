# Pre-Registered Candidate Geological Hypotheses — `XPHASE` Session (2026-10-24 UTC)

**Frozen before any surface construction, holdout evaluation, or GeoTIFF emission.**

- **Lane (Protocol Rule 1):** single named method **`XPHASE`** — Magnetotelluric–Gravity Transverse-Phase Concordance (`gems/xphase.py`).
- **Reuse (Protocol Rule 2):** SHA-256-verified 19-band stack via `scripts/restore_inputs.py`; `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel); `vendor/gems57/submission_writer.py`; `gems/breakline.py` primitives (`percentile_rank`, `structure_tensor_coherence`, `spaced_top_mask`). No private metric fork.
- **Labels (Protocol Rule 3):** every number is `HOLDOUT-DTI`, `PROXY`, `REGISTRY-MEASUREMENT`, `CLAIM`, or `LEADERBOARD-SNAPSHOT`. Zero `ORGANIZER-CONFIRMED` receipts exist.
- **Canaries (Protocol Rule 4):** every raw band and every derived `XPHASE` channel is tested alone on buffered holdout folds; symmetric ROC AUC > 0.90 = leakage, stop.
- **Budget (Protocol Rule 6):** three pre-registered experiments (`standalone`, `nophase`, `dual40`).

## Why GEMSDOE32 (`h33-h33-2-b2`, `0.2778` `[CLAIM]`) Led Listed Sites

Byte-verified cascade, not a projection: `H19-5` (121,131 px, `0.1922` `[CLAIM]`) → Poisson-thinned `D2.8` (44,090 px, `0.2600` `[CLAIM]`) → `SOLO` = `D2.8 & d_cat > 1.0` (40,199 px, `0.2708` `[CLAIM]`) → `R0` = `D2.8 & d_cat > 2.0` (37,654 px, `0.2778` `[CLAIM]`). Official DTI (`drivendataorg/gems-prize-reference-solution` Cell 16; `vendor/gems57/metric.py`) is

$$\mathrm{DTI}=\frac{\mathrm{TP}_w}{\mathrm{TP}_w+0.2\,\mathrm{FP}_w+0.8\,\mathrm{FN}_w},\qquad K(r)=\max(0,1-r/300\,\mathrm{m}).$$

Spacing at ~2.8 px saturates the pointwise kernel maximum; extra dots inside 280 m add FP weight with ~0 TP gain. Leaderboard snapshot `0.4413` (2026-10-24, not a receipt) shows headroom on *unmapped* faults. `R0` is 100% confined to the `H19-5` worm and cannot discover concealed basin feeders.

## Ranked Untried Hypotheses (this session)

| Rank | ID | Layers | Physical signature | Why it can catch catalogue-missing faults | Difference from this repo | Expected DTI / cost / viability |
|---:|---|---|---|---|---|---|
| **1 (built)** | **`XPHASE`** | Band 17 `cond_surf`; Band 13 `iso_grav_anom`; Band 15 `depth_to_base_surf`; Band 19 `det_elev_slope`; Band 5 `iso_grav_anom_slope` | Strike-parallel MT log-conductivity gradient × isostatic-gravity gradient with a 1–3 px *transverse phase lag* (offset peaks along the joint normal), intermediate-cover gate, high-slope suppression | Blind Great Basin feeders juxtapose dense basement against basin fill (gravity contact) *and* bound a smectite clay cap / upflow (MT lateral margin) with **no Quaternary scarp**. Catalogue mapping stops at the range front. | `HYDROCONDUIT` used raw `cond_surf` *level*; `APRONRIDGE` used gravity-*slope habitat* on DEM ridges; `COULOMB-LOQO` folded `\|\nabla\log B17\|` into a 24-feature HGB without testing **orientation agreement or across-strike lag** vs gravity. No lane emits on MT–gravity *phase*. | Rank 1 — highest expected discovery of concealed conduits / low–medium CPU / **100% viable now** (in-stack) |
| 2 | `EULER-N0` | Bands 2, 11, 13, 18, 15 | Reid et al. (1990) N=0 contact Euler / tilt-depth subcrop clusters depth-consistent with Band 15 | Buried horst edges under 100–600 m fill | Untried as a standalone emission; `ANASIG` is TMI *amplitude*, not 3-D contact solutions | Moderate / medium-high CPU / viable; deferred (budget) |
| 3 | `RADIO-CONTACT` | `geodawn_rad_u8.tif` K, Th, U + Band 12 | Opposing K-depletion / U-enrichment polarity across a strike | Hydrothermal alteration of a young splay under thin regolith | Repo radiometric uses are intensity ranks, not paired opposing-element polarity | Uncertain / medium / viable (pinned GeoDAWN cache) |
| 4 | `DRAINAGE-KNICK` | Bands 12, 19 | Collinear thalweg knickpoints across parallel washes | Sheetflood-degraded Holocene bajada faults | **Not fully viable here:** Band 12 is *detrended* elevation; D8 routing on a residual DEM is physically invalid without AMSL 3DEP | Held until orthometric DEM |
| 5 | `INSAR-3DEP1M` | USGS 3DEP 1 m + OPERA DISP-S1 | LiDAR scarplets + pumping-deconfounded creep steps | Decimetre Holocene scarps below 100 m posting | Sandbox cannot reach `apps.nationalmap.gov` / Earthdata | **Not viable in this sandbox** |

## Named non-fault process that could mimic `XPHASE`

Saline playa clay rings sitting on a non-tectonic basin-fill density contact; irrigation/agriculture conductivity fronts along canal alignments; Tertiary tuff / basalt pinchouts that are both dense and (weakly) conductive.

## Three pre-registered experiments

All emit 37,654 unit-mass dots, zeros outside the footprint, `d_cat > 2.0` px, `min_dist_px = 2.8`:

1. **`standalone`** — 100% 1-D crests of `S_xphase` (0% H19-5 / R0).
2. **`nophase`** — ablation: same emission on `S` *without* the transverse-lag term (tests whether offset peaks, not mere co-aligned gradients, carry the signal).
3. **`dual40`** — 15,062 (40%) H19-5 pixels ranked by `S_xphase` + 22,592 (60%) far (`d_H19 > 3`) 1-D crests.

## Official sources (manual review)

- [DrivenData #306 problem & metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official U-Net reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NREL/TP-5700-96647 rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [DOI 10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)
- [DOE GDR #1391 INGENIOUS](https://gdr.openei.org/submissions/1391) · [GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [USGS SGMC](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d)
- [EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
- Wannamaker et al. on Great Basin MT clay caps; Faulds & Hinz (2015) on structural settings of Great Basin geothermal systems.
