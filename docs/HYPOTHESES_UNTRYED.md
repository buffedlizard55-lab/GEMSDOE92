# Untried geological/geothermal-vent hypotheses (pre-registered)

Ranked by expected DTI improvement and implementation cost. Per the Parallel-Run Protocol, validate the top candidate on the spatially-blocked holdout **before** touching a weekly submission slot; a slot is a separate selector decision. Every feature is tested alone first — single-feature AUC > 0.90 is a leakage alarm. External data must be free and official; the specific source is named for each idea that needs it.

None of these has been implemented or validated in this session. They are deliverables for a future session.

---

## H1 — Damage-zone proximal dots (this session's candidate; PARTIALLY VALIDATED)

- **Layers:** USGS/INGENIOUS Quaternary & geothermal fault catalogue (existing_faults), Euclidean distance transform.
- **Physical signature / transform:** dots in the immediate fault damage zone, strictly 2–3 px (200–300 m at 100 m grid) from mapped catalogue lines — on the catalogue for zero-mass gate compliance but within the 3 px triangular kernel of withheld truth pixels.
- **Why it catches faults missing from the catalogue:** withheld holdout segments are continuations of visible strands; dots in the damage zone sit within kernel range of them, whereas every focus-site high scorer scatters at 15–30 px.
- **How it differs from anything in the repo:** all existing lanes place dots 15–30 px from the catalogue (R0, d28, h19-5, h27-4-solo all 0% on catalogue, mean distance 25–29 px). No lane exploits the 2–3 px band.
- **Named non-fault mimic:** clustered lithologic/alteration lineaments and alluvial-fan edges that resemble damage-zone dots but are not Quaternary geothermal faults.
- **Expected DTI gain:** pooled HOLDOUT-DTI 0.05164 (this session's instrument) vs R0 raster 0.00473 — but vs the reported R0 recipe 0.09775 it is not demonstrated; leaderboard projection unknown.
- **Cost:** LOW — uses only data/bridge (catalogue + sample grid), already implemented.
- **Status:** generated `gemsdoe92-damagezone-close-dots-20261028-zeros.tif`; format gates 11/11 PASS; unique vs local focus TIFFs; holdout vs R0-raster better but vs reported R0 recipe unconfirmed → **not slot-cleared**.

---

## H2 — Radiometric-total-count (TC) decay away from mapped faults

- **Layers:** GeoDAWN airborne radiometric survey, Band 6 = Total Count (tc) — verified in-repo as `r = 0.997140` with tc, not magnetic tilt (`r = 0.012796`; see input-cache audit). USGS GeoDAWN (official, public).
- **Physical signature / transform:** exponential decay of radiometric total count with distance from a mapped fault trace (hydrothermal alteration halo / radon decay chain near permeable fault zones). Transform: distance-to-catalogue-weighted tc, i.e. tc(x) * exp(-d(x, catalogue) / L).
- **Why it catches faults missing from the catalogue:** geothermal upflow leaves radiometric/alteration signatures on faults too young or too small to be in the Quaternary catalogue; tc decay spots those without relying on mapped traces.
- **How it differs:** in-repo band 6 was previously mislabelled as magnetic tilt; this uses tc decay as the signature, a different physical channel.
- **Named non-fault mimic:** naturally high-K/thorium granitic terrain and alluvial fans with high radiometric count unrelated to faults.
- **Data source:** USGS GeoDAWN (gdr.openei.org/submissions/1391; USGS data page) — free, official. Obtainability: verify downloadable from USGS/GDR before proposing as viable.
- **Expected DTI gain:** MODERATE (unproven); **Cost:** MEDIUM (needs 19-band training features / GeoDAWN tc raster, login-walled in this sandbox).

---

## H3 — Curvature / second-derivative of DEM (scarp convexity) off-catalogue

- **Layers:** 1 m or 10 m DEM (1m_DEM_links.csv, official). Transform: profile+plan curvature or Laplacian of the DEM; select high-convexity (scarp crest) pixels off-catalogue.
- **Physical signature / transform:** fault scarps are convex-up breaks in slope; curvature highlights the scarp crest independent of catalogue mapping.
- **Why it catches faults missing from the catalogue:** scarps on young Quaternary faults that predate / were never mapped; curvature catches the geomorphic expression, not the map.
- **How it differs:** existing scarppol/lidarscarp lanes use raw DEM relief or scarp masks; this is a curvature second-derivative on off-catalogue pixels.
- **Named non-fault mimic:** glacial cirques, alluvial fan toes, and landslide scarps that mimic fault-scarp curvature.
- **Data source:** USGS 3DEP / 1 m DEM links (1m_DEM_links.csv) — free, official. Obtainability: verify CSV downloadable before proposing as viable.
- **Expected DTI gain:** MODERATE; **Cost:** MEDIUM (needs DEM download + processing).

---

## H4 — Thermal-infrared nighttime anomaly (vegetation / soil moisture proxy)

- **Layers:** Landsat 8/9 TIRS or ECOSTRESS nighttime land-surface temperature (USGS EarthExplorer / NASA LP DAAC — free, official).
- **Physical signature / transform:** geothermal faults warm the near-surface; nighttime thermal anomaly (LST above local background after elevation/season correction) off-catalogue.
- **Why it catches faults missing from the catalogue:** blind geothermal faults with surface thermal expression but no mapped Quaternary trace.
- **How it differs:** no in-repo lane uses thermal IR; all are magnetics/radiometrics/DEM/catalogue.
- **Named non-fault mimic:** urban heat islands, irrigated agriculture, water bodies.
- **Data source:** USGS EarthExplorer / NASA LP DAAC — free, official. Obtainability: verify before proposing as viable.
- **Expected DTI gain:** LOW–MODERATE (signal is weak and confounded); **Cost:** MEDIUM–HIGH (atmospheric correction, co-registration).

---

## H5 — Seismicity-rate / b-value anomaly (microseismicity on blind structures)

- **Layers:** USGS ANSS / ComCat earthquake catalog (free, official). Transform: seismicity rate and b-value in a sliding window; cluster of small events on a structure with no mapped fault.
- **Physical signature / transform:** blind geothermal faults host microseismicity; rate/b-value anomalies pin active structures absent from the Quaternary catalogue.
- **Why it catches faults missing from the catalogue:** directly targets *active* fluid-conducting structures, including ones never mapped.
- **How it differs:** no in-repo lane uses instrumental seismicity.
- **Named non-fault mimic:** aftershock clusters, mining blasts, reservoir-induced seismicity.
- **Data source:** USGS ComCat/ANSS — free, official. Obtainability: confirm API/bulk download before proposing as viable.
- **Expected DTI gain:** LOW–MODERATE; **Cost:** MEDIUM.

---

## Ranking (expected DTI gain vs cost)

| Rank | Hypothesis | Expected DTI gain | Cost | Data needed | Viability check |
|------|-----------|-------------------|------|-------------|-----------------|
| 1 | H1 damage-zone dots | demonstrated 0.05164 (instrument) vs R0-raster 0.00473 | LOW | none (data/bridge) | viable — generated |
| 2 | H2 radiometric TC decay | MODERATE | MEDIUM | GeoDAWN Band 6 tc | verify USGS/GDR download |
| 3 | H3 DEM curvature | MODERATE | MEDIUM | 1m DEM links CSV | verify download |
| 4 | H4 nighttime thermal IR | LOW–MODERATE | MEDIUM–HIGH | Landsat/ECOSTRESS LST | verify download |
| 5 | H5 seismicity b-value | LOW–MODERATE | MEDIUM | USGS ComCat | verify API |

**Next session:** run H1's leakage canary (single-feature AUC <= 0.90) on the full feature stack if obtainable; resolve the holdout-instrument discrepancy (this session's R0 = 0.0047 vs reported recipe 0.09775); then, only if H1 beats the R0 recipe on holdout AND passes full public-registry uniqueness, present it to the separate weekly-slot selector.
