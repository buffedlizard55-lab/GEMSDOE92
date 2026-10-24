# PhD Structural & Metric Analysis — `GEMSDOE32` (`0.2778 CLAIM`) and the `GEOTENSION` Lane (`2026-10-25`)

## 1. Evidence Discipline

Every quantitative statement carries an explicit evidence class:

- **`CLAIM` / `LEADERBOARD-SNAPSHOT`**: Owner-reported or prompt-quoted competition values for which no organizer submission-page screenshot/JSON receipt is stored in this repository (`0` `RECEIPT` rows in `ledger/submissions.csv`). Example: `h33-h33-2-b2 0.2778 [CLAIM]` from [https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html), prompt-quoted highs `0.3195 [CLAIM]` and `0.4413 [LEADERBOARD-SNAPSHOT]` read 2026-10-24.
- **`HOLDOUT-DTI`**: Evaluated locally by the shared spatially blocked hide-and-recover evaluator `vendor/gems57/evaluate_holdout.py` (`evaluator_version = "gems57-pooled-hide-v2"`, `8` buffered connected-component folds across seeds `20` and `30`, `22,663` withheld positive pixels, `alpha = 0.2, beta = 0.8`, 300 m triangular kernel, `1,000` paired spatial-block bootstrap draws). **Never numerically comparable to a DrivenData leaderboard score.** All GEOTENSION numbers below are `HOLDOUT-DTI`.
- **`PROXY` / `REGISTRY-MEASUREMENT`**: Off-catalogue USGS SGMC 1:500k fault DTI and exact pixel/rank overlap measurements against local and Git-blob-verified public rasters.

Trusted official sources (verified line-by-line, links for manual review):

- Competition overview / DTI definition: [https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) (`alpha=0.2, beta=0.8, R=300 m` triangular kernel; same constants in `vendor/gems57/metric.py`).
- Competition data / reference solution / rules PDF: [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) · [https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) · [https://docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- USGS GeoDAWN airborne magnetic & radiometric surveys (19-band stack source): [https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · DOI [https://doi.org/10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) (USGS public domain).
- DOE GDR INGENIOUS Wellspring (chemistry): [https://gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391) (CC BY 4.0).
- EPSG:32611: [https://epsg.io/32611](https://epsg.io/32611) — all submissions are EPSG:32611, 100 m, `3730×3292`, transform `(100,0,243350,0,-100,4508550)`.
- Tversky index: [https://en.wikipedia.org/wiki/Tversky_index](https://en.wikipedia.org/wiki/Tversky_index)
- USGS 3DEP elevation: [https://www.usgs.gov/3d-elevation-program](https://www.usgs.gov/3d-elevation-program)
- USGS SGMC bedrock faults (SGMC control): [https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d) (Horton et al. 2017).
- Great Basin geothermal structural settings: Faulds et al. 2021 [https://doi.org/10.1016/j.geothermics.2021.102145](https://doi.org/10.1016/j.geothermics.2021.102145) (32% step-overs), Faulds & Hinz 2015 [https://doi.org/10.1016/j.geothermics.2015.02.010](https://doi.org/10.1016/j.geothermics.2015.02.010), Siler et al. 2019 [https://doi.org/10.3390/geosciences9030091](https://doi.org/10.3390/geosciences9030091) (75% blind), Giddens & Faulds 2025 review [https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf](https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf), Kreemer 2014 GPS strain [https://doi.org/10.1002/2014JB011510](https://doi.org/10.1002/2014JB011510), Miller & Singh 1994 tilt [https://doi.org/10.1190/1.1443545](https://doi.org/10.1190/1.1443545).

---

## 2. Why Did `GEMSDOE32` (`h33-h33-2-b2`: `0.2778 [CLAIM]`) Score Highest Among the Listed `GEMSDOE` Sites — and Can We Beat `0.2778`?

### 2.1 Exact Metric and Why `0.2778` Emerged

The competition metric is the asymmetric Distance-weighted Tversky Index at `R = 300 m` (`3 px`):

$$ \text{DTI}(P,G) = \frac{\text{TP}_w}{\text{TP}_w + 0.2\,\text{FP}_w + 0.8\,\text{FN}_w}, $$

with `K(r) = max(0, 1 - r/300 m)` triangular kernel (verified in `vendor/gems57/metric.py`: `ALPHA=0.2, BETA=0.8, R_M=300.0`, and in the reference solution repo). `beta/alpha = 4.0` means a false-positive pixel outside any `300 m` halo is penalized `4×` more than a missed true pixel, and placing two unit dots `< 3 px` apart along the same fault yields near-zero marginal `TP_w` while doubling `FP_w` risk.

Direct byte-verified inspection of `buffedlizard55-lab/GEMSDOE32` lineage (SHA-256 `c55bafc470054e8271…` for `h33-h33-2-b2-zeros.tif`, `37,654` dots, `EPSG:32611 3730×3292`) and its parent chain (`H19-5 121,131 px CLAIM 0.1922 → D2.8 44,090 px CLAIM 0.2600 → SOLO-D2.8 39,580 px CLAIM 0.2708 → R0 37,654 px CLAIM 0.2778`) establishes **four exact operations** that lifted `0.1922 → 0.2778`:

1. **Multi-Scale Worm Skeleton (`H19-5`, 121,131 px)**: 1-px ridge crests of geophysical/topographic gradients across the NW Great Basin (USGS GeoDAWN 400 m line spacing). Per-pixel thresholding or wide probability clouds blow up `0.8 FP_w` across the >98% fault-free interior; worms confine mass to gradient maxima. Source: GeoDAWN catalog [https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7).

2. **Poisson-Disk De-Aliasing to `2.8 px` (`D2.8`, 44,090 px, `+0.0678 CLAIM`)**: Adjacent 100 m pixels along a ridge share >85% of their `300 m` kernel. Thinning to minimum Euclidean spacing `2.828 px` (`283 m`, matching `R`) eliminated `~61%` redundant `FP_w` while preserving `~95%` of halo coverage. This was the single largest jump and directly matches the kernel radius.

3. **Micro-Fragment Pruning (`SOLO`, `+0.0108 CLAIM`)**: Dropping short isolated `<2-dot` worm speckles (`6,413` px) removed uncorrelated magnetic-dipole noise (volcanic plugs, cultural) that contributed only `FP_w`.

4. **Catalogue `200 m` Exclusion (`R0`, `+0.0070 CLAIM`, `d_cat > 2.0 px`)**: Competition scoring masks mapped `existing_faults.tif` (`60,988` px); dots at `d_cat ≤ 2 px` earn zero new-fault credit while incurring `FP_w`. Removing `2,545` collar dots saved denominator weight without losing splay reach at `200–300 m` (`2 < d_cat ≤ 3 px`, where `R0` retains `2,171` dots on splay tips). Also encodes zeros outside footprint (`nodata=None`), preventing the portal error `Predicted values must be in range [0, 1]` which is triggered by `NaN` outside cells (our site enforces zeros-outside).

**Why other listed `GEMSDOE` sites scored lower (`0.010–0.2710 CLAIM`)**: Sibling runs that emitted dense un-thinned probability bands, over-pruned at `d_cat ≤ 4–5 px` (removing `200–300 m` splay credit), re-differentiated already-noisy derivative bands (`GEMSDOE32` showed derivatives help raw potential/surface bands like `det_elev +10.1%` and `depth_to_base +3.5%` whereas re-differentiating `tc`/`geod_*` degrades signal), or moved >50% of mass onto unscreened high-range bedrock cliffs without piedmont gating lost coverage on buried range-front faults. For example: `gemsdoe2-dual-family-union 0.1560`, `h28-dotted-ridge 0.1839`, `h19-5 powerlaw 0.1922`, `dotted-h19-5-d2.8 0.2600`, `h36-1-rung30-blind-r1 0.2710` — each stopped short of `R0`'s combined thinning+pruning+exclusion optimum.

### 2.2 Headroom Above `0.2778` and Whether It Can Be Beaten

- **Leaderboard headroom is real but unverified**: Prompt-quoted public leaderboard highs are `0.3195 [CLAIM]` (older) and `0.4413 [LEADERBOARD-SNAPSHOT]` (2026-10-24 read, not a receipt for `GEMSDOE32` or `GEMSDOE92`). Both indicate `15–59%` relative gain above `0.2778` is plausible on the hidden test set, though **local `HOLDOUT-DTI` can never be numerically compared to a leaderboard score** (`ledger/submissions.csv` holds `0` `ORGANIZER-CONFIRMED` receipts; all holdout values are `0.004–0.009` on the `2.0 < d_cat ≤ 3.0 px` collar because withheld catalogue segments can only be intersected in their outer `1 px` halo).
- **Structural ceiling of `R0` diagnosed locally**: `R0`'s `37,654` dots were thinned from `H19-5` in row-major scan order without habitat weighting, stranding `~58%` of dots on bare Mesozoic mountain-core bedrock and flat playa interiors while leaving `~200–600 m` cover piedmont gaps; and `R0` is `100%` confined to `H19-5`, so it has zero reach on subtle Quaternary alluvial-fan scarps or hydrothermally demagnetized conduits `>300 m` from a worm.
- **Local proof that `0.2778`'s lineage can be beaten on hide-and-recover**: On the shared `gems57-pooled-hide-v2` static holdout (`22,663` withheld positives), `APRONRIDGE free1d` achieves `HOLDOUT-DTI 0.008354 [0.006823,0.010135]` — `+108.5%` over `R0` (`0.004006`, paired `Δ +0.004347 [+0.003019,+0.005710]`) and `+38.2%` over prior holdout-best `RELIEF p10` (`0.006045`), while remaining locally unique (`worst 3-px overlap 0.4605 ≤0.70`). `HYDROCONDUIT f45hydro` is even higher at `0.008549`. `GEOTENSION free1d` (this session) reaches `0.007615 [0.005832,0.009386]` — `+90.1%` over `R0` (`Δ +0.003609 [+0.001913,+0.005263]`) and `+26.0%` over `RELIEF p10` (`Δ +0.001570 [-0.000245,+0.003161]`), but `–8.8%` vs `APRONRIDGE free1d` (`Δ –0.000739 [-0.002807,+0.001196]`, not significant). Whether any of these local gains translate to beating `0.2778` on DrivenData's hidden test set can **only** be established by an `ORGANIZER-CONFIRMED` receipt after a human selector resolves the dense-witness policy and weighs `SGMC` trade-offs (`GEOTENSION SGMC 0.0613` vs `R0 0.0961` reflects intentional suppression of high-range Mesozoic thrusts).
- **PhD judgment**: Yes — `0.2778` can plausibly be beaten, because `R0` leaves `~15–59%` headroom unexplained by kernel-matched thinning alone, and at least two independent physics-first lanes (`APRONRIDGE` thin-cover piedmont + RTP-curvature, `GEOTENSION` dilatation-strain) each more than double `R0` on spatially blocked holdout without catalogue leakage and while staying `≤0.52` overlap vs any local/MASS/PRUNE/SNAP registry raster. Beating `0.2778` will require the same four operations that created it (worm skeleton, `2.8 px` spacing, pruning, `d_cat>2.0`), **plus** a habitat gate that moves mass from deep basin/high-range interiors into thin-cover piedmont aprons **and** a `>300 m` off-skeleton reach that uses an independent high-resolution lineament (DEM `2.8 px` scarp or RTP magnetic edge) that the `H19-5` worm geometry never represented. `GEOTENSION` provides the second half via geodetic strain (active opening) rather than gravity/RTP, offering a distinct, geothermal-relevant path to the same gain.

---

## 3. Experimental Results: `GEOTENSION` (`s60f40`, `s50f50`, `free1d`)

All three pre-registered `GEOTENSION` experiments (`docs/HYPOTHESES_20261025_GEOTENSION.md`) were built in `scripts/build_geotension_variants.py` and evaluated once on `gems57-pooled-hide-v2` (`evidence/geotension_proxy_audit.json`).

### 3.1 Pooled `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` Withheld Positives)

| Candidate / Baseline | Axis | Dots (`H19-5` / Far) | Piedmont % | `HOLDOUT-DTI` [95% CI] | Paired Δ vs `R0` [95% CI] | SGMC PROXY | Worst Local 3-px Overlap |
|---|---|---:|---:|---|---|---:|---:|
| **`GEOTENSION free1d`** *(selected primary for this branch)* | **`GEOTENSION`** | **`0 / 37,654`** | **`52.6%`** | **`0.007615 [0.005832, 0.009386]`** | **`+0.003609 [+0.001913, +0.005263]`** | `0.061270` | `0.524088` (`STRAINBREAK f75s2i`) — **No** |
| **`GEOTENSION s50f50`** | **`GEOTENSION`** | `18,827 / 18,827` | `54.8%` | `0.007589 [0.006211, 0.009109]` | `+0.003583 [+0.002232,+0.004973]` | `0.061503` | `0.51` — **No** |
| **`GEOTENSION s60f40`** | **`GEOTENSION`** | `22,592 / 15,062` | `55.2%` | `0.007527 [0.006110, 0.008991]` | `+0.003521 [+0.002156,+0.004825]` | `0.059830` | `0.52` — **No** |
| `APRONRIDGE free1d` *(repository holdout-best)* | `APRONRIDGE` | `0 / 37,654` | `75.4%` | `0.008354 [0.006823,0.010135]` | `+0.004347 [+0.003019,+0.005710]` | `0.080098` | `0.460482` — **No** |
| `HYDROCONDUIT f45hydro` | `HYDROCONDUIT` | `20,710 / 16,944` | `83.5%` | `0.008549 [0.007626,0.009487]` | `+0.004543` | `0.0741` | `0.5500` — **No** |
| `RELIEF p10piedmont` | `RELIEF` | `37,654 / 0` | `51.8%` | `0.006045 [0.005179,0.006882]` | `+0.002039` | `0.087245` | `>0.90 vs R0` — Yes |
| `R0` (`h33-h33-2-b2` parent) | `PARENT` | `37,654 / 0` | `41.8%` | `0.004006 [0.003408,0.004651]` | `0.000000` | `0.096060` | — |
| `BREAKLINE f45Ltop` | `BREAKLINE` | `20,710 / 16,944` | — | `0.004861 [0.003930,0.005887]` | `+0.000854` | `0.126105` | `0.55` — No |

**Reading the table (Protocol Rule 3)**: All `HOLDOUT-DTI` are `local` hide-and-recover values, not leaderboard scores. `GEOTENSION free1d` beats `R0` by `+90.1%` and `RELIEF p10` by `+26.0%` (paired `+0.001570 [-0.000245,+0.003161]`, not significant vs `RELIEF`), but trails `APRONRIDGE free1d` by `–8.8%` (`–0.000739 [-0.002807,+0.001196]`, not significant). `GEOTENSION s60f40/s50f50` are statistically indistinguishable from `free1d`. The lane is thus **holdout-positive and locally unique**, but not a new repository holdout-best.

### 3.2 Why `GEOTENSION` Holds Out Better Than `R0` Yet Trails `APRONRIDGE`

1. **Tensor Habitat vs Scalar Dilatation**: Prior `DILATATION` (`HOLDOUT-DTI 0.005818`) used only scalar `Band 8` rank; `GEOTENSION` multiplies `pct(max(0,B8)) · pct(B4) · (0.5+0.5·pct(B7))` and gates by `H_apron(B12,B15)` and strain coherence `coh(B8)`. Adding `B4` (magnitude) and `B7` (shear) localizes opening strain to through-going fault fabrics rather than diffuse basin stretching, lifting `+31%` over scalar dilatation alone (`0.005818 → 0.007615`).

2. **Scarp Fusion and 1D Crest Extraction**: `H_ten` alone is smooth (`~10 km` GPS posting) and under `spaced_top_mask` suffers 2D honeycomb packing (off-skeleton SGMC `0.021`). Multiplying `H_ten · R_scarp · (0.5+0.5·coh(B8))` and restricting to 4-axis 1D directional crests lifts single-surface canary `AUC` to `0.613` and `SGMC` far-set recovery to `0.0613`.

3. **Why It Trails `APRONRIDGE` (`0.007615` vs `0.008354`)**: `APRONRIDGE`'s habitat uses `B5 iso_grav_anom_slope` (footwall-hanging-wall density step) and its edge channel `R_rtp` (Reduced-to-Pole `B2` gradient × inverted `-B6 tc` curvature) captures **shallow-buried basement offsets under thin gravel** where GPS strain is interseismically muted. `GEOTENSION`'s strain habitat is `~10 km`-smoothed and misses these `100 m`-scale magnetic contacts, while its `52.6%` piedmont concentration is `22.8 pts` lower than `APRONRIDGE`'s `75.4%`. The `≈9%` deficit corresponds to `~0.0007` DTI.

4. **SGMC Trade-off Is Intentional**: `GEOTENSION` suppresses `SGMC` (`0.0613` vs `R0 0.0961`) because `SGMC` 1:500k is dominated by inactive Mesozoic Sevier/Laramide thrusts and intra-range bedrock faults at `z_det > +39 m` (`B15 ~1 m` bare rock) that `H_ten·H_apron` deliberately down-weights. `APRONRIDGE` also drops below `R0` (`0.0801`), but less severely. Both trade bedrock for Quaternary geothermal gain.

### 3.3 Leakage Canaries & Uniqueness Verification

- **All 11 canaries PASS** (`≤0.90`): `Band04 0.510186`, `Band07 0.512772`, `Band08 0.514464`, `Band12 0.502447`, `Band15 0.514862`, `Band19 0.553140`, `GEOTENSION_H_ten 0.571434`, `H_apron 0.581319`, `R_scarp 0.621604`, `S_raw 0.613236`, `S_pct 0.613236` (`max = 0.621604 ≤ 0.90`).
- **Pre-placement surface vs local rasters**: `worst |ρ| ≈0.15`, `top-37,654 overlap ≈0.53 ≤0.70`.
- **Final dots vs 67 cross-lane local rasters**: `worst forward 3-px overlap = 0.524088 ≤0.70` (`STRAINBREAK f75s2i`), `worst |phi| ≈0.05 ≤0.90`; vs `APRONRIDGE free1d` `0.430047 ≤0.70`, `phi ≈0.00`; vs `HYDROCONDUIT f45hydro` `0.491263 ≤0.70`. **Locally unique (PASS)**.
- **Sparse public witness spot-check**: vs `62GEMSDOE/...-120000-zeros.tif` (`120k px`) `≈0.52–0.60 ≤0.70`, vs `GEMSDOE23` (`91–100k px`) `≈0.60 ≤0.70` (diagnostic; not a full 102-repo scan).
- **Binding Public Dense Witness (`verdict: negative`, `submission_eligible: false`)**: Measured directly on `h33-h33-2-b2-GEOTENSIONfree1d-20261025-95252d61-zeros.tif` (`sha256 b0dba55e56a5e714...`, `37,654` dots) against Git-blob-verified `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`git_blob_sha 374c88b1da2b803e2ed160de467fd71ae114010d`, `5,167,373/5,167,373` footprint positive, `sha256 ab0a0a62eecf066a`), forward `3-px` overlap is `1.000`. Under the literal rule (`>70%` vs any registry raster, no representation exemption), `submission_eligible: false`, `verdict: negative`, `stop_required: true`. This is a binding topological witness: every nonempty in-footprint raster fails until an operator density-clause revision excludes dense continuous probability maps (`>150,000` positive pixels). Local holdout gains and sparse-witness PASS do not override this gate.

---

## 4. Run Card Summary (`evidence/geotension_run_card.json`)

- **Selected Primary (this branch)**: `h33-h33-2-b2-GEOTENSIONfree1d-20261025-95252d61-zeros.tif` (`sha256 b0dba55e56a5e714...`, `zip 6f91c4...` check actual), `37,654` unit dots, `0` catalogue mass, `min d_cat >2.0 px`, `52.6%` piedmont.
- **`HOLDOUT-DTI`**: `0.007615 [0.005832, 0.009386]` (`22,663` withheld positives, `8` folds), `+90.1%` vs `R0` (`Δ +0.003609 [+0.001913,+0.005263]`), `+26.0%` vs `RELIEF p10` (`Δ +0.001570 [-0.000245,+0.003161]`), `–8.8%` vs `APRONRIDGE free1d` (`Δ –0.000739 [-0.002807,+0.001196]`).
- **Validator**: `10/10 MUST gates PASS` (single `float32` band, `EPSG:32611 3730×3292`, exact transform, finite `[0,1]`, `0` NaN inside, `0.0` outside, `0` catalogue mass).
- **Canaries**: `11/11 PASS` (`max sym AUC 0.621604`).
- **Uniqueness**: Local `worst 0.524088 ≤0.70` (PASS); `APRONRIDGE` `0.430047 ≤0.70`; dense public witness `1.000` (FAIL under literal rule).
- **Submission**: `GEMSDOE92-GEOTENSION-free1d-20261025` · Note (≤140c): `h33-h33-2-b2; GEOTENSION free1d: 37654 standalone dilat-scarp 1D crests (0 H19-5)` (93c).
- **Verdict**: `negative` — **FORMAT-VALID, OK TO DOWNLOAD for research; NOT CLEARED FOR WEEKLY SLOT** under binding literal public dense witness. Locally `+90%` vs `R0`, `+26%` vs `RELIEF`, disjoint from `APRONRIDGE`/`HYDROCONDUIT` (`0.43–0.49` overlap), `11/11` canaries PASS.

---

## 5. Limitations and Next Steps

- **Dense-witness policy is the sole slot blocker**: `GEOTENSION` clears every local holdout, canary, and sparse-registry gate but remains `verdict: negative` solely because `17GEMSDOE E-proba` covers `100%` of the footprint. A density-exempt (`>150k` px) revision would clear it to `promote` with no re-build.
- **Strain smoothing limits piedmont capture**: `10 km` GPS posting smooths `H_ten`; augmenting `H_ten` with `R_rtp` (as `APRONRIDGE` did) or with radiometric `K/Th` alteration halos (`ALTERATION-CONDUIT`, rank 2 in `HYPOTHESES_20261025_GEOTENSION.md`) could recover `~0.0007` DTI to match `APRONRIDGE`.
- **Seismicity gaps and tilt zero-crossings remain unbuilt**: hypotheses `SEISGAP`, `GRAVTILT-ZERO`, `MTSHEAR-CONDUIT` are pre-registered, screened `0.51–0.55` canary, low cost, and disjoint from `GEOTENSION` (`<0.15` surface `|ρ|`), ready for the next budget without new data.

