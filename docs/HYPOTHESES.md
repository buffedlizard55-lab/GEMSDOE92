# Ranked geological hypothesis backlog — 2026-10-24

> **Status: unvalidated backlog only; no active lane; no candidate is currently viable to test or submit.** These are ranked by qualitative expected scientific information per implementation cost *if* the policy and data-access blockers are resolved. They are not score forecasts. Machine-readable record: [`hypothesis_queue_20261024.json`](hypothesis_queue_20261024.json).

A fresh `REGISTRY-MEASUREMENT` found one hash-verified public raster positive on every allowed footprint cell. Under the literal `>70%` overlap stop, every nonempty candidate in the footprint fails before placement. No experiment or TIFF was generated for this queue. Do not try to evade the stop by moving dots outside the footprint, choosing an empty raster, or excluding the witness.

The list was checked against tracked builders, run cards, and prior hypothesis notes. “Unvalidated” means the exact formulation below has no tracked build/holdout result; it does **not** claim global novelty. Several related concepts were previously screened and are called out explicitly. No external source is called verified or viable in this review; the official sites were not reachable from the permitted network hosts, and the large feature stack is absent from `.cache/gems_inputs/`.

## Rank 1 — DRAINAGE-RELAY: multi-catchment deflection / knickpoint coherence

- **Layers:** competition DEM Band 12 `det_elev`, Band 19 `det_elev_slope`, and a hydrologically conditioned drainage graph with derived channel profiles.
- **Physical signature:** a collinear, repeated same-sense lateral deflection or knickpoint across several neighboring channels/catchments, with a consistent cross-channel step. Test the network-level motif, not an isolated high-gradient pixel.
- **Why it could find a catalogue-missing fault:** a young, low-throw blind fault may deform several channels before a clear surface scarp is mapped; repetition across catchments can persist where any one local break is weak.
- **Difference from repo methods:** BREAKLINE and SCARPPOL rank local slope-break or fall-line-curvature pixels. This would use drainage-graph topology and cross-catchment displacement; no such builder/result was found in the reviewed tracked evidence.
- **Named non-fault mimics:** lithologic/cementation boundaries, alluvial-fan avulsion or drainage capture, Pleistocene shorelines, roads/canals/dams.
- **Expected value / cost:** medium potential information value; moderate-to-high implementation and validation cost. A 100 m DEM may be too coarse for small offsets. No numeric HOLDOUT-DTI expectation is assigned.
- **Data requirement / source:** exact hash-verified competition DEM stack or an independently authorized, grid-matched DEM. Official starting point: [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/). Availability and terms were not verified; the stack is absent from the current cache. **Not viable now.**

## Rank 2 — SPRING-PAIR-STRIKE: geothermal discharge pair alignment

- **Layers:** DOE GDR INGENIOUS spring/well coordinates, temperature and chemistry with source-quality flags; optional DEM-derived catchment/valley orientation only as a mimic control.
- **Physical signature:** determine whether independent hot-spring or geothermometry-confirmed well pairs form fault-compatible, strike-coherent corridors using pairwise axial orientations and spatially blocked controls—not point density.
- **Why it could find a catalogue-missing fault:** blind permeable strands may connect separated surface discharge points while lacking a mapped Quaternary scarp.
- **Difference from repo methods:** a prior spring-density/elongation screen was not promising. The explicit spring-pair alignment construction was left unbuilt; it is not a claim that spring density worked.
- **Named non-fault mimics:** regional aquifer or lithologic-contact discharge; outlets following a river/playa margin; anthropogenic production wells; multiple outlets connected by an aquifer rather than a fault.
- **Expected value / cost:** medium-high geological specificity but uncertain power; moderate-high cost for point provenance, duplicate removal, cluster dependence, and leakage-safe spatial validation. No numeric HOLDOUT-DTI expectation is assigned.
- **Data requirement / source:** official GDR submission 1391 with source terms, coordinates, temperature, and provenance checked. [GDR / INGENIOUS #1391](https://gdr.openei.org/submissions/1391). The project manifest records a CC BY 4.0 classification for a pinned mirror, but this review did not verify the live official source or current terms. **Not viable now.**

## Rank 3 — HOST-NORMALIZED-RADIOMETRIC-RESIDUAL

- **Layers:** USGS GeoDAWN K, eTh, eU and total-count channels; competition Band 15 `depth_to_base_surf` and Band 17 `cond_surf` as candidate host/cover covariates; survey-quality masks.
- **Physical signature:** estimate local, host-conditioned multi-channel radiometric residuals, then test coherent linear K/eTh/eU alteration edges. Do not rank an unconditioned total-count gradient or ratio as if it were a fault.
- **Why it could find a catalogue-missing fault:** fluid-rock alteration may mark a concealed permeable fault or splay with little relief and weak regional magnetic/gravity contrast.
- **Difference from repo methods:** a related total-count-gradient screen exists. The proposed host-normalized multichannel residual is a different, unvalidated formulation; do not describe radiometric work generally as untouched.
- **Named non-fault mimics:** primary felsic/mafic lithology, soil moisture/weathering/transported cover, playa salts or clay, survey striping/altitude/shielding.
- **Expected value / cost:** low-to-medium potential until host normalization and survey QA are demonstrated; high cost for co-registration, flight-line QC, compositional effects, and independent validation. No numeric HOLDOUT-DTI expectation is assigned.
- **Data requirement / source:** official GeoDAWN channels and coverage/quality metadata. [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [DOI 10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ). The manifest records a public-domain classification for a pinned mirror; live source, coverage, terms, and availability were not checked this review. **Not viable now.**

## Rank 4 — MULTISEASON-THERMAL-CORRIDOR

- **Layers:** multi-date Landsat Collection 2 surface-temperature scenes; DEM slope/aspect, land-cover and acquisition-quality controls; optional independently sourced spring locations for interpretation, not target labels.
- **Physical signature:** persistent, seasonally matched thermal residuals arranged along a narrow corridor after controlling for slope/aspect, land cover, acquisition time and emissivity. Require repeated observations, not one warm pixel.
- **Why it could find a catalogue-missing fault:** shallow geothermal upflow may express persistent surface heat above a blind permeable structure that is not mapped from scarps or potential-field lineaments.
- **Difference from repo methods:** no Landsat thermal time-series lane was found in the reviewed tracked evidence; this differs from static geophysics and DEM priors, though its relationship to fault labels is indirect.
- **Named non-fault mimics:** sun-facing slopes, irrigation/urban/industrial heat, wildfire scars, exposed rock/emissivity errors, seasonal moisture and atmospheric artifacts.
- **Expected value / cost:** low-to-medium potential because thermal anomalies are indirect; high cost for scene selection, cloud/season controls and reproducible processing. No numeric HOLDOUT-DTI expectation is assigned.
- **Data requirement / source:** official multi-date Landsat Collection 2 surface-temperature data and processing metadata. [USGS Landsat Collection 2 Surface Temperature](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature). Availability, coverage and terms were not verified. **Not viable now.**

## Gate before any future implementation

1. Resolve the binding public-registry policy explicitly. Until then, do not build or place candidate dots.
2. Verify authorized source bytes, terms and hashes; restore only to the ignored cache. A matching owner-mirror hash is not organizer authentication.
3. Select one method lane in a later authorized session. Before placement compare the **actual lane surface** to the accessible registry; after placement compare final dots. Stop on `|Spearman| >0.90` or `>70%` forward 3-pixel overlap with any one raster.
4. Reuse `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. Hold out whole fault components with a buffer; use visible-fault-only catalogue features and pixel-exact masking; pooled DTI `α=0.2`, `β=0.8`, `300 m` triangular kernel.
5. Run feature-alone symmetric-AUC leakage canaries (`AUC >0.90` is leakage until investigated), automated format gates, and a complete run card. Stop after three experiments or two hours. Slot selection remains separate.
