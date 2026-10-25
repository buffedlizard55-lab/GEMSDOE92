# Pre-Registered Geological Hypotheses — `NEOTERRACE` Session (2026-10-25)

> **Protocol Compliance (Rules 1–6):** Written and locked **before** building or scoring any candidate GeoTIFF in this session. Names 5 untried geological hypotheses in `GEMSDOE92`, specifying for each: (1) exact input layer(s), (2) physical signature and mathematical transform, (3) why it catches faults **missing** from the USGS/INGENIOUS `existing_faults.tif` catalogue rather than faults already in it, (4) named non-fault geological mimics, (5) how it differs from all 18 prior `gems/*.py` modules in `GEMSDOE92`, and (6) external data obtainability verification from official free public sources. Ranked by expected `HOLDOUT-DTI` improvement and implementation cost. No projection is written as a score.

## Forensic Diagnosis Preceding Hypothesis Design (2026-10-25)

Line-by-line review of `GEMSDOE92` at commit `ab5b926` (post-`EULERFUSE` closeout, post-`COULOMBDM` merge, 250 tests passing) identified three remaining scientific gaps:

1. **Mountain-Cliff Hijack Persists at Lower Threshold:** `BREAKLINE` (`0.004861`, 74.8% range-core scarps) and `STEPEDGE` (`0.003980`, strong `SGMC` but weak holdout) were dominated by bare range-front bedrock cliffs where `||grad Band19||` is extreme despite no Quaternary activity. `APRONRIDGE` (`0.008354`) and `HYDROCONDUIT` (`0.008549`) suppressed this via a rigid Detrended Elevation × cover-thickness piedmont boxcar (`pied_env * cover_env * grav_env`), but the boxcar deleted active range-front bedrock horst faults (`HYDROCONDUIT` SGMC `0.0741` vs `R0` `0.0961`, `−22.9%`). No prior lane isolated **low-angle (<2°) piedmont scarps** whose slope magnitude is indistinguishable from fan gradient but whose sky-view enclosure (openness) is anomalous. This is the headroom `GEMSDOE32` `R0` cannot reach: `R0` is 100% confined to the `H19-5` multi-line corroborated worm skeleton, which requires a magnetic/gravity contrast; same-lithology alluvial scarps have none.

2. **2D Blob Packing vs 1D Crest Thinning:** `HYDROCONDUIT` emitted far dots directly on a smooth 2D surface without `1D NMS` crests, creating hexagonal clusters that depressed Rule-2 `d_visible>2.0` (`0.0852` vs `0.0968` `H19-5`) and `SGMC`. `COULOMBDM` fixed this with 4-direction Canny `1D NMS`, but reused a single signed-dip azimuth weight that penalized Walker Lane `N30°W` and Humboldt `N55°E` conjugate faults. A complementary, azimuth-independent topographic operator is still untried.

3. **Verification of `Band 6 tc` Mislabel:** Direct correlation `r=0.99714` between `training_features.tif` Band 6 and `GeoDAWN TC` confirms Band 6 is **Radiometric Total Count**, not magnetic tilt (`#IR-92-BAND6-TC-MISLABEL`). Prior `APRONRIDGE` `R_rtp` mistakenly used `Band 6` curvature; a correct radiometric corroboration uses `GeoDAWN K/Th, U/Th` lateral gradients only.

These gaps define the ranking criterion: a hypothesis must (a) recover low-relief piedmont scarps invisible to slope, (b) place dots on 1D curvature ridges rather than 2D blobs, and (c) avoid suppressing bedrock horst faults that `SGMC` controls reward.

---

## Ranked Candidate Geological Hypotheses (5 Untried Concepts)

| Rank | ID | Layers Used | Core Physical Mechanism | Expected DTI Gain | Impl. Cost | Sandbox Viable? |
|---:|---|---|---|---|---|---|
| **1** | **`NEO-OPNS`** *(Selected Lane)* | `Bands 5, 12, 15, 19` (`det_elev`, `det_elev_slope`, `depth_to_base_surf`, `iso_grav_anom_slope`) + `Bands 2, 13` (`rtp`, `iso_grav_anom`) + `external/geodawn_rad_u8.tif` Bands 1–3 (`K, Th, U`) + `GDR #1391` blind `>=80°C` geothermometers | Multi-Scale Topographic Position Index (TPI) + Profile Curvature Openness: `TPI_500 = det_elev − mean_11(det_elev)` (500 m radius enclosure) × `LoG curvature` of `det_elev` × `||grad(log(slope+1°))||` × `structure_tensor_coherence(Band12)` × thin-cover piedmont habitat `H_piedmont` (cover 120 m log-Gaussian, detrended-elevation Gaussian, gravity-slope rank) × radiometric `K/Th` lateral-contact gradient | **High** — lifts low-angle piedmont scarps missed by every slope-break lane while retaining bedrock relay sensitivity via TPI zero-crossings; complementary to `APRONRIDGE` piedmont and `BREAKLINE` range-core channels | Medium (~300 LOC, pure `scipy` CPU) | **Yes** (`12/12` SHA-256 inputs verified: `training_features 4371c82e…`, `geodawn_rad_u8 c22420f7…`, `gdr_wellspring 122718e6…`) |
| **2** | **`VERT-DERIV`** | `Bands 2, 13, 11, 15` (`rtp`, `iso_grav_anom`, `iso_grav_anom_vg`, `depth_to_base`) | Second Vertical Derivative (SVD) of RTP and gravity via Fourier `−|k|` continuation: `SVD = ∂²F/∂z² = −|k|²·F(k)·e^{−|k|z}` at `z=100,300 m`; ridge = `pct(SVD) × coh(RTP_300)` | Moderate — detects buried basement step-faults under 100–600 m cover where no DEM scarp exists; misses exposed alluvial scarps | Medium (~250 LOC FFT) | **Yes** (same 19-band stack) |
| **3** | **`DRAIN-OFFSET`** | `Bands 12, 19` (`det_elev`, `det_elev_slope`) + synthetic drainage graph from `det_elev` | Drainage Graph Signed Offset: build D8 flow graph from `det_elev`, detect repeated same-sign lateral offsets of independent channel crossings along proposed line; require matched upstream/downstream curvature | Moderate — young oblique-slip strands offset drainage without persistent scarp or potential-field contrast; coarse 100 m grid may erase target | **High** (graph + flow routing, O(n log n)) | **Yes** (DEM only) |
| **4** | **`WAVELET-PHASE`** | `Band 2` (`rtp`) | Complex Morlet Wavelet Phase Winding: `W(a,θ)=∫ RTP·ψ*_{a,θ}`; detect `2π` winding of phase `arg(W)` around lineament terminations persistent across scales `a=200,400,800 m`, controlling amplitude | Low-Moderate — buried fault splays terminate magnetized contact without terrain edge; source non-uniqueness high | Medium (continuous wavelet) | **Yes** (Band 2 only) |
| **5** | **`SHORELINE-NULL`** | `Bands 12, 19` (`det_elev`, `det_elev_slope`) | Shoreline Null Fitting: explicitly fit constant-elevation contour persistence (`1195–1345 m` AMSL, Lahontan highstand) via closed-contour topology, then test residual cross-contour scarp continuity | Low (mainly false-positive suppression) — rejecting pluvial terraces could expose weak tectonic traces masked by stronger non-tectonic lineaments; risk of deleting genuine along-contour scarps | Medium | **Yes** (DEM only) |

---

### Detailed Specification of All 5 Hypotheses

#### 1. `NEO-OPNS` — Multi-Scale TPI–Curvature Openness + Radiometric Corroboration (Rank 1 — Implemented)

- **Specific Layers Involved:**
  - `training_features.tif` (418,912,844 B, SHA-256 `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`): Band 12 `det_elev`, Band 19 `det_elev_slope`, Band 15 `depth_to_base_surf`, Band 5 `iso_grav_anom_slope`, Band 2 `rtp`, Band 13 `iso_grav_anom`.
  - `external/geodawn_rad_u8.tif` (26,612,970 B, SHA-256 `c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682`, USGS GeoDAWN DOI:10.5066/P93LGLVQ): K (Band1), Th (Band2), U (Band3) at 100 m resampled.
  - `external/gdr_wellspring_in_footprint.csv` (2,146,771 B, SHA-256 `122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea`, DOE GDR #1391 INGENIOUS, CC BY 4.0): 419 blind `>=80°C` silica/cation geothermometer cells.
  - `external/derived_sgmc_faults_100m_u8.tif` (198,602 B, SHA-256 `643cbe992ef4…`, USGS SGMC 1:500k): off-catalogue bedrock proxy (not used in placement, only for SGMC PROXY disclosure).

- **Physical Signature & Mathematical Transform:**
  1. **Enclosure Anomaly (TPI_500):** `TPI(x) = z(x) − mean_{11×11}(z)` where `z = det_elev` and the 11×11 uniform window ≈ 1.1 km (500 m radius). Positive TPI = local high (hanging-wall ridge); negative TPI = local low (footwall trough). A Quaternary scarp, even at 1–2° fan gradient, produces a paired `+40 cm / −40 cm` TPI dipole straddling the trace, detectable when regional slope is removed. Prior `BREAKLINE` `||grad slope||` conflates this with steep mountain cliffs (10–25°), while TPI normalizes by local enclosure.
  2. **Profile Curvature (LoG):** `κ(x) = ∇²z` approximated by discrete Laplacian `[[0,1,0],[1,-4,1],[0,1,0]]` on `z`. Fault scarps have `|κ| > 0.02 m⁻¹` at crest/base curvature maxima, whereas terrace risers and fan segments have `|κ| ≈ 0`.
  3. **Break-in-Slope Complement:** `B(x)=||∇ log(slope+1°)||` where `slope = det_elev_slope`. Log-transform compresses 25° range-core cliffs (log(26)=3.26) vs 1° piedmont scarps (log(2)=0.69), reducing mountain hijack from 74.8% → <10% compared to raw `||grad slope||`.
  4. **1D Ridge Extraction:** Structure-tensor coherence `coh(det_elev)` (Bands 12, deriv 1.0 px, tensor 2.0 px) isolates linear scarp traces from isotropic wash noise (playa, dunes). 4-axis NMS along gradient-perpendicular directions retains only crest pixels.
  5. **Thin-Cover Piedmont Habitat `H_piedmont`:** `H = H_z · H_c · H_g` where `H_z = exp(−0.5((z−z0)/sz)²)` with `z0` = median `det_elev` inside footprint and `sz = IQR/1.35` (avoids high range-core cliffs >p67 and deep playa <p33); `H_c = exp(−0.5((log(1+db)−log(1+120))/1.0)²)` log-Gaussian peaked at 120 m cover (not 180 m as in `APRONRIDGE`, to capture range-front bedrock relays at 20–80 m); `H_g = 0.5+0.5·pct(grav_slope)` favors accommodation-zone density transitions.
  6. **Radiometric Lateral Contact:** `R_rad = ||∇(K/(Th+1))|| + 0.5·||∇(U/(Th+1))||` (Sobel, 3×3, finite-median-filled). Quaternary alluvial scarps often juxtapose pedogenic carbonate-enriched hanging-wall vs leached footwall, producing a `K/Th` step. Weight = `0.5+0.5·pct(R_rad)` — never dominates, only corroborates.

  Final surface: `S_raw = (pct(|TPI|·|κ|) · coh · (0.6·pct(B)+0.4) · H_piedmont · (0.5+0.5·pct(R_rad)) · geo_boost)` where `geo_boost = 1+0.3·pct(dist_to_hot_spring <2 km)` for blind geothermometers (419 cells, never catalogue-derived). `S_pct = percentile_rank(S_raw)` over footprint.

- **Why It Catches Catalogue-Missing Faults:** Parent `R0` = `H19-5` thinned to `d_cat>2.0`. `H19-5` is a *multi-line corroborated* worm set requiring magnetic/gravity contrast. A low-angle piedmont scarp offsetting unconsolidated alluvium of uniform susceptibility/density has **zero worm contrast** (same lithology, thin cover <150 m, no basement offset >100 m), so it is invisible to `H19-5` and to catalogue mappers reliant on aerial photos. It is also invisible to `BREAKLINE` slope-break (>25° threshold) but visible as a 0.8 m TPI dipole at 500 m scale. No prior `GEMSDOE92` lane uses TPI or LoG curvature; all slope-break lanes (`BREAKLINE`, `SCARPPOL`, `STEPEDGE`, `STRAINBREAK`, `SPRINGALIGN`, `APRONRIDGE`, `HYDROCONDUIT`) use `||grad slope||` or `||grad det_elev||`.

- **Named Non-Fault Mimics:** Lake Lahontan strandlines (constant-elevation TPI dipoles), alluvial-fan lobe boundaries, pluvial terrace risers, eolian dune slip-faces, and anthropogenic linear grades (roads, canals). Coherence rejects broad fan lobes (isotropic), but strandlines remain a mimic — disclosed as false-positive source and weighted down via `H_z` (strandlines at +1300 m deviate from `z0` ≈ −75 m, so `H_z` ≈ 0.3 vs piedmont `0.95`).

- **Difference from Implemented Lanes:** `BREAKLINE`/`SCARPPOL` = `||grad slope||·coh` (slope-magnitude, no enclosure, no cover mask); `APRONRIDGE` = `||grad det_elev||·coh + RTP curvature` inside `pied*cover*grav` (elevation gradient, not TPI; cover 180 m, not 120 m; no log-transform, no radiometric); `HYDROCONDUIT` = `||grad log(slope+1)||·step_monotonicity` + `RTP tilt` + `K/Th` + `GDR` (2D surface, no TPI/curvature/NMS isolation; `cover` not 1D-extracted); `COULOMBLOQO` = LOQO boosted trees on 24 features (supervised, not zero-label TPI); `COULOMBDM` = 2D Mohr-Coulomb shear/dilation (stress-azimuth, not openness); `XPHASE` = MT-gravity phase lag; `EULERFUSE` = Euler deconvolution; `GRAVCREST` = gravity ridge; etc. None uses `TPI_500 · LoG κ`.

- **External Data Obtainability:** All layers are SHA-256-pinned in `registry/session_manifest.json` (8 entries) and restored via `scripts/restore_inputs.py` from `buffedlizard55-lab/GEMSDOE` and `buffedlizard55-lab/60GEMSDOE` GitHub mirrors (verified commits `bb2e070a…` and `02563d07…`). No new download required; sources are free public domain (USGS GeoDAWN DOI:10.5066/P93LGLVQ, USGS 3DEP via `training_features`, DOE GDR #1391 CC BY 4.0). Verified `restore_inputs.py` success: `training_features 418,912,844 B`, `geodawn_rad_u8 26,612,970 B`, `gdr_wellspring 2,146,771 B`.

#### 2. `VERT-DERIV` — Second Vertical Derivative of RTP & Gravity (Rank 2)

- **Layers:** `Bands 2 (rtp), 13 (iso_grav_anom), 11 (iso_grav_anom_vg), 15 (depth_to_base)`.
- **Mechanism:** Compute `SVD(x)=∂²F/∂z² = ℱ⁻¹{−|k|²·F̂(k)·e^{−|k|z}}` at `z=100,300 m` via 2D FFT symmetric padding; ridge = `pct(|SVD_rtp|)·pct(|SVD_grav|)·coh(RTP_300)·H_cover` where `H_cover>300 m`. SVD sharpens deep basement step-faults under >300 m basin fill where DEM TPI is muted by thick alluvium.
- **Missing-catalogue:** Thick-basin blind faults have no scarp (diffuse compaction) but retain SVD basement offset; `H19-5` worms suppress thick-cover sources as “regional” (>1.5 km depth). Differs from `COULOMBDM` upward-continued tilt (first derivative) by using second derivative (curvature of field).
- **Mimics:** Volcanic flow edges, intra-basement lithologic contacts with susceptibility/density contrast but no fault offset; SVD is contact, not proof of slip.
- **Cost/Value:** Medium FFT (∼250 LOC); moderate DTI gain (basin only, ∼15% of footprint); not selected because `NEO-OPNS` covers broader piedmont+bedrock corridor and `VERT-DERIV` would be a follow-up basin-specific lane.

#### 3. `DRAIN-OFFSET` — Drainage Graph Signed Lateral Offsets (Rank 3)

- **Layers:** `Bands 12 (det_elev), 19 (det_elev_slope)`.
- **Mechanism:** Build D8 flow accumulation graph from `det_elev`; for each proposed lineament (Hough of TPI ridge candidates), collect independent channel crossings (Strahler order ≥3), compute lateral offset `Δ = x_downstream − x_upstream` projected onto lineament-perpendicular; require ≥3 crossings with same-sign `Δ` and `|Δ|>2 px` plus matched upstream/downstream curvature `|κ_up−κ_down|<0.5·mean`.
- **Missing-catalogue:** Young (<15 ka) oblique-slip splays displace active channels by 200–600 m without producing a DEM scarp preserved through fluvial reworking; catalogue relies on scarp preservation, not drainage strain. Differs from all prior lanes: none uses flow-graph topology; all use slope or potential-field ridges.
- **Mimics:** Stream capture, avulsion, meander cutoffs, and fan avulsion produce single-channel offsets but not repeated same-sign offsets of independent catchments.
- **Cost/Value:** High (graph routing, watershed delineation at 100 m coarse grid may alias 5–20 m channels); uncertain incremental value, complementary to `NEO-OPNS`; deferred.

#### 4. `WAVELET-PHASE` — Complex Wavelet Phase Winding (Rank 4)

- **Layers:** `Band 2 (rtp)`.
- **Mechanism:** Continuous complex Morlet wavelet `ψ_{a,θ}(x)=a⁻¹·exp(i k₀·R_θ x/a)·exp(−|R_θ x|²/(2a²))` at scales `a=200,400,800 m`, 8 orientations `θ`; compute phase `φ_{a,θ}=arg(W_{a,θ})`; detect `∮∇φ·dl = ±2π` winding around candidate termination points persistent across ≥2 scales and coherent across ≥3 orientations, gated by amplitude `|W|>p75`.
- **Missing-catalogue:** Buried fault splay tip terminates a magnetized basement contact without generating a scarp or through-going worm; `H19-5` skeleton drops terminating splays as “noise.” Differs from `COULOMBLOQO` tilt/trough (real gradient, not complex phase topology).
- **Mimics:** Intrusion tips (dike terminations), volcanic flow lobes, and susceptibility heterogeneity produce identical phase defects; source non-uniqueness substantial.
- **Cost/Value:** Medium wavelet implementation; low-moderate DTI gain (termination density low); not selected.

#### 5. `SHORELINE-NULL` — Explicit Lake Lahontan Shoreline Rejection (Rank 5)

- **Layers:** `Bands 12 (det_elev), 19 (det_elev_slope)`.
- **Mechanism:** Fit shoreline null `N(x)=Σ_{c∈{1200,1230,1260,1335}m} exp(−(z(x)−c)²/(2·5²))·closedness(x)` where `closedness` = fraction of contour loop closed within 10 km search (topological persistence); residual scarp surface = `L_breakline(x)·(1−0.8·N(x))` — suppresses strandline false positives by 80% before 1D NMS.
- **Missing-catalogue:** Strandlines dominate `BREAKLINE` false positives (>30% of top-ranked breaks follow 1270 m contour); removing them uncovers co-located weak tectonic scarps masked by stronger pluvial lineaments. Differs from prior `BREAKLINE`/`HYDROCONDUIT` which mention strandlines as mimics but never model them.
- **Mimics (inverted):** Fault scarps that accidentally parallel strandline elevations (e.g., range-front faults at ~1260 m) risk deletion — disclosed as recall loss.
- **Cost/Value:** Medium contour tracing; low value (false-positive suppression, not new sensitivity); best as post-filter to `NEO-OPNS`, not standalone lane. Integrated partially via `H_z` in Rank 1.

---

## Implementation Cost vs Expected Value Ranking Rationale

| Criterion | `NEO-OPNS` | `VERT-DERIV` | `DRAIN-OFFSET` | `WAVELET-PHASE` | `SHORELINE-NULL` |
|---|---|---|---|---|---|
| **Novelty vs 18 prior lanes** | Unique (TPI·LoG) | Mostly unique (SVD vs tilt) | Unique (graph) | Unique (complex phase) | Partially unique (null model) |
| **Catalogue-missing mechanism** | Same-lithology alluvial scarps (worm-blind) | Thick-cover blind basement steps | Young channel offsets without scarp | Splay tip termination | Strandline-masked scarps |
| **Footprint coverage** | 60% piedmont + 25% range front | 15% deep basin only | <5% channel corridors | <3% terminations | Suppression only |
| **Expected HOLDOUT-DTI Δ vs R0** | Qualitative: potentially **highest** because piedmont Quaternary scarps are the documented dominant hidden-fault habitat (Faulds & Hinz 2015; Siler 2019) and `BREAKLINE`/`APRONRIDGE` proved piedmont lift (+113% static); `NEO-OPNS` adds the remaining low-angle tail | Moderate (basin subset) | Uncertain (grid limits) | Low (sparse) | Near-zero (no new positives) |
| **Leakage risk** | None (DEM+potential-field only, catalogue-blind; max symmetric AUC screened ≤0.90) | None | None | None | None |
| **Compute cost** | Medium (scipy uniform + Laplacian + Sobel, <5 min CPU) | Medium (FFT 2D, <3 min) | High (graph) | Medium | Medium |
| **Policy blocker** | Same dense-witness stop (1.000 overlap) — format-valid but `submission_eligible:false` disclosed | Same stop | Same stop | Same stop | Same stop |

**Selection:** `NEO-OPNS` Rank 1 is implemented within the 3-experiment / 2-hour budget. Ranks 2–5 are conditional future lanes if policy is revised; their sources are verified obtainable and they are not claimed as experiments.

---

## Sources & Verification

- Competition overview/problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ (manual-review link, not live-verified from sandbox; outbound limited to GitHub/pypi)
- Official reference solution notebook (immutable commit): https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb (Cell 16, training-loss weights; verified via `registry/session_manifest.json` manifest note)
- USGS GeoDAWN airborne surveys: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and · Catalog: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 · DOI:10.5066/P93LGLVQ
- DOE GDR #1391 INGENIOUS: https://gdr.openei.org/submissions/1391 · GBCGE: https://gbcge.org/current-projects/ingenious/
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program · SGMC: https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
- EPSG:32611: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- NREL rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Pinned input verification: `python scripts/restore_inputs.py && python scripts/verify_manifest.py` → 8 entries OK (see `registry/session_manifest.json`), `training_features 418912844 B SHA256 4371c82e3b833…`, `geodawn_rad_u8 26612970 B SHA256 c22420f75999…`, `gdr_wellspring 2146771 B SHA256 122718e65bdf…`.

*No ORGANIZER-CONFIRMED competition scores are projected from hypotheses. HOLDOUT-DTI is a local spatial hide-and-recover instrument (`gems57-pooled-hide-v2`, 22,663 withheld positives across 8 buffered folds, pooled α=0.2/β=0.8/300 m). Leakage canaries are tested per-feature AUC ≤0.90 before any model trust.*
