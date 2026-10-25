# Pre-registered hypotheses — GEMSDOE92, session 2026-10-26 (RADIOCONTACT lane)

Written BEFORE any code/build for this lane, per Protocol Rule 7. These are
untried geological hypotheses; no numeric gain is projected. Band numbers are
1-based positions in the pinned 19-band GeoDAWN stack
(`training_features.tif`, GDAL-verified band audit in README.md). All
candidate surfaces are computed only from the pinned stack plus the
pinned public-domain GeoDAWN radiometrics layer
(`ext_geodawn_rad_u8`, SHA-256 `c22420f75999...`, restored 2026-10-26 per
`registry/session_manifest.json`). No competition labels are read.

Context from prior sessions (learning, not copying):
- Holdout-best instrument: strict Rule-2 `d_visible > 2.0` HOLDT-DTI
  `COULOMB-LOQO standalone` = `0.113316 [0.100614, 0.127163]` (22,663 withheld
  positives, `gems57-pooled-hide-v2`); static `d_cat > 2.0` best =
  `COULOMB-LOQO standalone` `0.009220 [0.007983, 0.010493]`. R0 static =
  `0.004006`.
- `GEMSDOE32 h33-h33-2-b2` (R0) CLAIM `0.2778` is an owner-reported CLAIM, not
  an organizer receipt; R0 is 100% confined to the H19-5 catalogue skeleton
  (XOR(R0, D2.8 & d_cat > 2.0) == 0) thinned to ~3 px spacing. Its organizer
  score plausibly comes from recovering mapped faults at kernel-optimal
  spacing, not from blind-fault discovery.
- Every nonempty in-footprint raster fails the LITERAL public rule vs the
  17GEMSDOE E-proba-multiscale witness (100% footprint-positive -> literal
  overlap 1.000). The matched-budget reading (#IR-92-DENSE-WITNESS-MATCHED-
  BUDGET, <= 0.70 for >150k-px surfaces) is the operative lane test; literal
  is always printed.
- No weekly slot may be spent until a lane beats holdout-best on the
  registered comparison AND clears the uniqueness gate.

| Rank | Named lane / layers | Physical signature (transform) | Why it catches faults missing from USGS/INGENIOUS | Difference from repo implementations | Named non-fault mimic | Expected gain / cost |
|---|---|---|---|---|---|---|
| 1 | **RADIOCONTACT**: GeoDAWN U/K & Th/K contact edges (`ext_geodawn_rad_u8`) x gravity-gradient concordance (B11 `iso_grav_anom_vg`, B18 `iso_grav_anom_hg_ew`, B5 `iso_grav_anom_slope`) + MT level B17 `cond_surf` | Hydrothermal alteration contact: opposing U/K vs Th/K polarity across a strike, coherent with buried density-contact gravity gradients and footwall polarity; MT-high fluid pathway. Blind faults under thin cover juxtapose altered vs unaltered rock with no preserved scarp. | USGS/INGENIOUS is a scarp catalogue: faults whose scarps have diffused (Quaternary, low slip) or are buried under playa/alluvium were never mapped. Radiometric alteration halos and gravity-gradient contacts are independent of scarp preservation and directly mark fluid-conducting basement structures. | No lane uses radiometric contact polarity or gravity-gradient quadrature. COULOMB-LOQO uses geodetic strain + RTP tilt + MT clay *edges*; EULERFUSE uses Euler depth solutions; HYDROCONDUIT/APRONRIDGE use topographic scarps. RADIOCONTACT is the first alteration-mineralogy lane and the first blind-cover lane driven by density contrast rather than topography. | Lithologic K-rich ash-fall beds, non-tectonic basin-fill contacts, playa salinity/evaporite conductivity (MT), irrigation salinity (cond_surf). | Expected: medium-high (first alteration lane; geothermal systems are alteration-controlled). Cost: low-medium (one external 26 MB layer restored + 4 stack bands; no flow routing). |
| 2 | **DRAINAGE-KNICK**: B12 `det_elev`, B19 `det_elev_slope`, B15 `depth_to_base_surf`, B7 `geod_shearrate` | Deflected drainage / knickpoint: cross-cutting stream deflection at a range front with a coincident basement-depth step and shear-rate anomaly; degraded Pleistocene range-front fault with diffused scarp. | Scarpless blind faults still deflect drainages and offset basement; the catalogue only mapped scarps, so a knickpoint catchment finds structures the worm skeleton (potential-field) and scarp lanes miss entirely. | No lane uses drainage geometry. All terrain lanes (BREAKLINE, SCARPPOL, STEPEDGE, STRAINBREAK, PIEDFRONT) use raw slope/scarp magnitude or coherence, not drainage deflection. | Lithologic knickpoints on resistant dikes/beds, alluvial-fan segment boundaries, pluvial-lake shoreline terraces (Lahontan). | Expected: high for catalogue-missing degraded faults. Cost: medium (flow routing/knickpoint extraction on 5.17M px; runtime/memory risk in 3 GB sandbox). |
| 3 | **GRAV-QUAD**: B11 `iso_grav_anom_vg` x B18 `iso_grav_anom_hg_ew` concordance | Vertical-gravity-gradient and E-W horizontal-derivative sign concordance across a strike: buried basement fault juxtaposing density contrasts with footwall up to the east (W-dipping normal faults, the Basin-and-Range dominant polarity). | Density-contrast faults with weak magnetic expression are invisible to RTP/tilt lanes; gravity-gradient sign-locking marks the fault plane itself rather than its edges. | COULOMB-LOQO uses B18 footwall polarity as one of 24 features inside a classifier; GRAV-QUAD is a standalone 2-D gradient-quadrature surface, never built as its own lane. | Lateral density changes from non-fault lithologic contacts (basement terrane boundaries), uncompensated topographic loads. | Expected: medium. Cost: low (two stack bands). |
| 4 | **SEIS-GRAV-LAG**: B10 `deq_n100a15`, B16 `ieq_n100a15` vs B13 `iso_grav_anom` | Spatially coherent seismic swarm flank running *alongside* (not over) a gravity-defined buried basement step: lateral offset between seismicity density and gravity anomaly marks a blind strike-permeable fault. | Swarms localize on permeable blind structures absent from the surface catalogue; distance-to-earthquake alone (screened negative, 100 km smoothing) misses the lateral offset signature. | Prior seismicity lanes used distance/intensity alone (screened negative). This tests signed cross-strike lateral separation between two continuous fields — untested. | Magmatic/induced seismicity near purely lithologic density contacts; aftershock alignments on mapped faults (excluded via d_cat mask). | Expected: medium-low (coarse 100 km smoothed seismicity). Cost: low. |
| 5 | **MT-CHANGEPOINT**: B17 `cond_surf` vs B15 `depth_to_base_surf` | Conductivity change-point at locally constant inferred cover depth: focused fracture-fluid conduit within a uniform cover-thickness block, i.e. a blind strand not explained by alluvium thickness alone. | Cover-thickness-controlled MT anomalies explain most conductivity variation; a change-point *within* constant cover requires a discrete fracture zone — a blind fault missing from the catalogue. | Earlier MT gating (HYDROCONDUIT/COULOMBDM) conditioned on conductivity level or clay-cap edges, not on cover-stabilized change-points. | Salinity changes within playa aquifers, irrigation, land-use effects; clay facies changes. | Expected: low-medium. Cost: low. |

Pre-registration rule: Rank 1 (RADIOCONTACT) is the top candidate for this session. If it fails the leakage canary (any feature symmetric AUC > 0.90) or the holdout bar (paired CI vs R0 excludes 0 and beats COULOMB-LOQO 0.113316 Rule-2 / 0.009220 static), no build proceeds and the session ends negative — Rank 2 (DRAINAGE-KNICK) becomes the documented fallback, not an auto-build.

Stop conditions (protocol): |rho| > 0.90 or >70% of dots within 3 px of one registry raster => duplicate, log and stop. Budget: 3 experiments / 2 hours this session.
