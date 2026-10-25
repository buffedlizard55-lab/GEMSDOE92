# Pre-Registered Geological Hypotheses — `RELAYGAP` (2026-10-26)

Written and locked **before** any `RELAYGAP` experiment was scored. Branch `arena/a4cb22d8-gemsdoe92`. Evaluator to be used, not forked: `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel). Writer to be used, not forked: `vendor/gems57/submission_writer.py`. Experiment budget: **3**. Weekly slots: **0** until selector step.

No number below is a score. Prior `HOLDOUT-DTI` figures are cited from this repository's run cards. `0.2778` and `0.4413` remain **CLAIM**s (owner-reported, not ORGANIZER-CONFIRMED; see `ledger/site_scores_claimed_20261025.csv` and `docs/BEAT_0_2778.md`).

## Why GEMSDOE32 `h33-h33-2-b2` (CLAIM 0.2778) scored highest among the listed sites — and how to beat it

### The 0.2778 mechanism (verified from pinned rasters; not an organizer receipt)

The byte-checked lineage in `.cache/gems_inputs/lineage/` and `data/bridge/` is:

| raster | positive px | CLAIM score | editorial step |
|---|---|---:|---|
| H19-5 (`19GEMSDOE`) | 121,131 (continuous worm lines) | 0.1922 | ridge-set detector |
| D1.5 (`GEMSDOE24`) | 60,069 (dots) | 0.2477 | thin lines → dots |
| D2.8 (`GEMSDOE25`) | 44,090 | 0.2600 | enforce ~2.8 px spacing |
| SOLO (`GEMSDOE28`) | 40,199 | 0.2708 | drop dots ≤1 px from catalogue |
| **R0 = h33-h33-2-b2 (`GEMSDOE32`)** | **37,654** | **0.2778** | drop dots ≤2 px from catalogue |

Under the official metric `DTI = TPw / (TPw + 0.2·FPw + 0.8·|G|)` with 300 m (3 px) triangular kernel (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/, https://github.com/drivendataorg/gems-prize-reference-solution, https://en.wikipedia.org/wiki/Tversky_index, `vendor/gems57/metric.py`):

1. **Redundancy removal.** Dots closer than ~2.8 px share the same truth halo: `TPw` is a `max` per truth pixel (saturates), while `FPw = Σ p·(1-max k)` accrues per dot. Thinning cuts `FPw` ~2.7× while preserving most `TPw`.
2. **Known-fault halo removal.** Organizer forum (thread 11516, cited in prior docs) masks visible catalogue pixels from scoring; dots ≤2 px from a mapped trace contribute almost zero `TPw` and only add `FPw`. Removing them raises `DTI`.
3. **Budget optimality.** The marginal bar for one more non-redundant dot is `k > 0.2·DTI ≈ 0.056`; many low-rank H19-5 pixels are below it.

**Thus R0 is an *emission optimum* on a fixed detector (H19-5 worm ridges).** Its score comes from metric-aware pruning and spacing, not from discovering blind faults beyond H19-5. Copying it is forbidden and would be a registry duplicate (literal overlap 1.0 vs its registry copies).

### Why other listed sites scored lower

- **Breakline/Scarppol/StepEdge lanes** used un-normalized `||∇slope|| × coherence` on Bands 12/19: 74.8% of off-skeleton dots landed on bare range-core cliffs (`det_elev` top tercile) and 28.9% on transverse canyon orientations, missing the piedmont where >75% of INGENIOUS blind systems actually localize (Faulds et al. 2015, https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf; Wallace 1977). SGMC proxy 0.096 vs 0.126 for breakline confirms bedrock bias.
- **Pure magnetic lanes (`ANASIG`)** used unreduced TMI gradients (Bands 3/9/14) without RTP phase correction; deep intrabasin steps are 100× too weak to compete with range-front gradients.
- **NaN-outside encodings** (`-nan.tif` files) violate the current `gems.gates` strict mode and return the portal error `Predicted values must be in range [0, 1]` (the validator previously mis-classified infinities; fixed here). Zeros-outside is the only portal-safe encoding.
- **Dense continuous surfaces** (e.g., 17GEMSDOE `E-proba-multiscale`, 5,167,373 px) are valid rasters but under the literal “every positive cell is a dot” reading make every sparse candidate have forward overlap 1.0. They are **not** sparse dot fields; treating them literally is a representation mismatch flagged as `#IR-92-DENSE-WITNESS-MATCHED-BUDGET`.

### How to beat 0.2778 (PhD-level roadmap)

Beating R0 requires a **better detector**, not more pruning, at the same metric-aware emission:

1. **Target what R0 cannot see.** Great Basin geothermal systems are not on master range fronts (only ~3% of favorable settings, Faulds & Hinz 2015). ~32% sit in step-overs/relay ramps and ~25% at terminations/intersections — exactly the subordinate faults that a Quaternary scarp catalogue omits. ~39% of INGENIOUS systems are blind (no surface scarp). A detector that finds *relay gaps* and *antithetic splays* between mapped masters will recover withheld faults that R0 leaves as `FNw`.

2. **Use independent physics, not re-weighted topography.** R0 and H19-5 are topography/magnetic worm derivatives. Independent confirmation requires: (a) reduced-to-pole (RTP) magnetic tilt/demagnetization (hydrothermal magnetite destruction), (b) Bouguer gravity Poisson breakdown `σ(ρ)` and basement curvature, (c) MT clay-cap lateral margins, (d) blind silica/Na-K-Ca geothermometers, (e) 3DEP 10 m micro-scarp curvature (USGS 3DEP, https://www.usgs.gov/3d-elevation-program). Each has a distinct non-fault mimic (range-core cliffs, basalt contacts, playa clays, irrigation ponds, Lahontan shorelines) that must be explicitly de-confounded.

3. **Calibrate continuous probabilities, don’t hard-threshold at 37,654.** Under `α=0.2`, any non-overlapping ridge pixel with expected marginal kernel credit `c_i > 0.2·D ≈ 0.056–0.088` raises `DTI` if added at `p=1`. Hard binary truncation discards 40,000–80,000 positive-expectation pixels (proven in PROVINCETOE analysis). Future winners will emit `p_i ∈ [0.12, 1.0]` out to `c*(D)=0.2D` with multi-scale contextual continuity.

4. **Solve the NE-quadrant collapse.** All LOQO lanes score ~0 in NE; it has thick basin fill and different MT coverage. A 3-quadrant deployment with H19-5 fallback in NE is a legitimate, pre-registrable hybrid (next-steps queue).

The public leaderboard snapshot 0.4413 (2026-10-24, participant `xiaofanhu`) — itself a CLAIM — suggests this physics + calibration path is already being pursued elsewhere. Local holdout bests that point the same way are `VENTSCARP` (Rule-2 0.112213), `FAULTNET netfar` (Rule-2 0.175147 but 0.758 overlap vs 80k GEMSDOE37), `KNICKLOQO standalone` (static 0.010788, Rule-2 0.109043, `0/1412 >0.70` under dual reading), and `POISSONFLEX opt` (Rule-2 0.107466).

## Five untried candidates (ranked by expected HOLDOUT-DTI gain ÷ implementation cost)

| Rank | ID | Specific layer(s) | Physical signature (transform) | Why it catches a fault missing from USGS/INGENIOUS catalogue | Difference from every `gems/*.py` in this repo | Non-fault mimic | Expected gain / Cost / Viable? |
|---|---|---|---|---|---|---|---|
| **1 (BUILD)** | **`RELAYGAP`** | `existing_faults.tif` catalogue geometry alone (self-excluded tip-gap network; no 19-band stack) | Relay-gap centerlines between en echelon catalogue tips: for each tip pair with separation 0.5–4.0 km, strike difference ≤20°, overlap ≥30% of length, score `S = exp(-d/1.5km) · cos(Δstrike) · gap_width/4km` smoothed with 300 m kernel; self-excluded distance to nearest *other* tip (`cx_logtip`) and to gap interior | Catalogue maps through-going masters; it systematically omits the breaching splay, synthetic/antithetic relay faults, and step-over transfer faults that link them — and those host ~57% of geothermal systems (Faulds et al. 2006, 2010, 2021a, https://www.osti.gov/servlets/purl/1110517; Giddens & Faulds 2025, https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf). These faults sit 0.3–5 km from masters, share regional N–NNE strike, and have no Quaternary scarp until they breach — exactly the blind population in the hidden test set | `faultnet.py` adds 5 catalogue-context fields to a 24-feature LOQO but emits via learned HGB; `STEPOVER` extrapolates tips along strike (tip10px), `TIPGAPfar18f33` uses far-field tip proximity; none place dots *inside* the inter-tip gap interior weighted by overlap/width. `BREAKLINE/SCARPPOL/STEPEDGE` are DEM curvature, not catalogue topology. `KNICKLOQO/VENTSCARP/POISSONFLEX` are LOQO learners requiring the 19-band stack — this lane is catalogue-free and stack-free | Collinear lithologic contacts, Luning-Fencemaker thrust relics, and Lake Lahontan beach-ridge gaps that happen to align between range-front fault tips | **+0.004 to +0.010 static `HOLDOUT-DTI` over R0** / LOW cost (2 min CPU, 3 GB) / **Yes** — only `existing_faults.tif` + `sample_submission.tif` needed |
| 2 | `BASIN-HINGE` | Bands 12,13,15,18 (`det_elev`, `iso_grav_anom`, `depth_to_base_surf`, `iso_grav_anom_hg`) | 2nd-order basement rollover shoulder `κ_{B,⊥}=n_B^T H(log B) n_B` perpendicular to gravity gradient, with footwall gravity-pole concordance | Blind extensional faults under 0.4–1.2 km fill express as forced monoclines, not scarps; Worms lock onto the basement cutoff, catalogue onto scarps, neither onto the flexure hinge 300–800 m up-dip | `poissonflex.py` computes `κ_{B,⊥}` but fused with Poisson/MT/knickpoint/LOQO; `apronridge.py`/`piedfront.py` use 1st-order slope-break + cover gate only | Compaction drape monoclines over unfaulted density steps | +0.003 to +0.008 / Medium / Yes (stack) |
| 3 | `ALTERATION-TROUGH` | Bands 2,6,17 + `geodawn_rad_u8.tif` (K/Th/U) | RTP Laplacian demagnetization trough `(∇²_RTP >0)` ∧ `K/Th` potassic halo (p85) ∧ `U/Th` redox front, gated by MT conductive cap lateral gradient | Hydrothermally altered blind conduits destroy magnetite and precipitate adularia/illite with no topographic scarp; surface hot springs are quenched or absent (blind) | `hydroconduit.py` uses `||∇log cond||` + `K/(Th+1)` + RTP tilt-edge but not paired `∇²_RTP` trough + U/Th; `radiocontact.py`/`radiodecouple.py` are 1st-order K/Th levels | Felsic tuff/granite K anomalies and Miocene basalt demagnetized flow margins | +0.002 to +0.006 / Medium / Yes (pinned radiometrics) |
| 4 | `KNICK-COLLINEAR` | Bands 12,19 (`det_elev`, `det_elev_slope`) via D8 on AMSL-corrected DEM | D8 flow-accumulation thalweg knickpoints + χ-space convexity + Radon alignment across ≥3 adjacent catchments (strike-steered integral) | 0.5–2 m Holocene bajada scarps are erased in 100 m detrended DEM but survive as aligned knickpoints upstream of the buried fault | `drainage_knick.py` is a single-scale knickline, not multi-catchment Radon; `poissonknick.py` is Poisson-flexure context | Resistant/soft lithologic contacts and Lahontan stillstand benches | +0.002 to +0.005 / High (routing O(n log n)) / **No** — Band 12 is detrended, not AMSL; needs official 3DEP 10 m tile (USGS 3DEP, https://www.usgs.gov/3d-elevation-program, not fetchable in sandbox). Verify before claiming viable |
| 5 | `INSAR-CREEP` | Sentinel-1 LOS velocity (OPERA DISP-S1, https://www.earthdata.nasa.gov/data/catalog/asf-opera-l3-disp-s1-v1.0) + relocated microseismicity | LOS velocity step `Δv_LOS > 1 mm/yr` within 400 m of catalogue-parallel lineament + microseismic epicenter lineation (b-value <1.0) | Creeping blind faults accumulate interseismic slip with no geomorphic scarp; catalogue is Quaternary-geomorphic, not geodetic | No lane ingests InSAR or seismicity (`MICROSWARM` was screened out) | Poroelastic subsidence bowls (lithium brine pumping) and anthropogenic seismicity | Unknown / High / **No** — NASA ASF/OPERA and USGS ComCat are not on sandbox allow-list (github.com, pypi.org, registry.npmjs.org only). Name free official source first: OPERA DISP-S1 via Earthdata Login (https://urs.earthdata.nasa.gov/) and USGS Earthquake Catalog (https://earthquake.usgs.gov/earthquakes/search/). Both require network fetches unverifiable here; do not propose as viable without staging SHA-256-pinned mirror |

All hypotheses name a **named non-fault process** as required for the Run Card. Expected gains are **pre-experiment projections, never scores**.

## Three experiments (budget = 3)

All catalogue-derived fields are recomputed from **visible faults only** per hide-and-recover fold (parallel-run protocol rule 2). Deployment dots satisfy `d_cat > 2 px` (strict), unit mass `p=1`, spacing floor 2.8 px, `values ∈ [0,1]`, zeros outside footprint, `EPSG:32611 3730×3292`.

1. **`relay`** — Primary RELAYGAP surface: tip-gap score `S` smoothed with σ=1.5 px, masked to `d_cat ∈ (2, 60]` px halo (2 px exclusion + 60 px cap = 6 km search radius), emission of 37,654 dots via greedy exact-marginal-DTI (kernel 3 px) on the gap-smoothed surface. Spacing 2.8 px.
2. **`relay_far`** — Same surface, emission restricted to `d_cat > 4 px` (remove the 300 m halo that R0 lineage shows is low-yield; hedge for hidden truth that is truly blind rather than near-catalogue).
3. **`relay_norotate`** — Ablation: gap score without strike-alignment weight (`cos Δstrike` set to 1). Tests whether strike concordance is load-bearing vs distance alone.

Falsifier: single-feature symmetric AUC >0.90 ⇒ leakage until proven otherwise. An arm whose pre-placement top-37,654 support or final dots exceed 0.70 forward 3-px overlap or 0.90 |ρ| vs any local registry raster is a duplicate; that arm stops. Beating the stored holdout best (`KNICKLOQO standalone` static 0.010788, Rule-2 0.113316) is required before any selector recommendation. This session will not spend a weekly slot.

## Post-score addendum (filled after the three arms)

_During execution, record paired bootstrap CIs vs R0 / H19-5 / KNICKLOQO, leakage max, registry worst-case, and validator SHA. Do not overwrite this pre-registration._

## Sources (manual review)

- Competition problem/metrics: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition about/Great Basin: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ (snapshot, not receipt)
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and and DOI https://doi.org/10.5066/P93LGLVQ
- GDR INGENIOUS #1391: https://gdr.openei.org/submissions/1391
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Faulds & Hinz 2015 favorable settings: https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
- Faulds et al. structural settings overview: https://www.osti.gov/servlets/purl/1110517
- Giddens & Faulds 2025 step-over widths: https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf
- Kim, Peacock & Sanderson 2004 fault damage zones: https://doi.org/10.1016/j.jsg.2003.08.002
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program
- OPERA DISP-S1: https://www.earthdata.nasa.gov/data/catalog/asf-opera-l3-disp-s1-v1.0

The non-GitHub competition pages, GDR DOI, and leaderboard were **not live-verified** from this sandbox (egress limited to `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`); they are public official links for manual review.
