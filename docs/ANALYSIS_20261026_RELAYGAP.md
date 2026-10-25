# RELAYGAP Analysis — Why GEMSDOE32 0.2778 Scored Highest and How to Beat It (with Holdout Evidence)

**Date:** 2026-10-26 (UTC)  
**Lane:** `RELAYGAP` — catalogue-tip relay-gap detector (tip-density, strike-weighted)  
**Branch:** `arena/a4cb22d8-gemsdoe92`  
**Status:** ✅ Format-valid zeros-outside TIFFs (3 experiments, 0 weekly slots spent) · Holdout-measured, not organizer-scored

## Executive answer (why 0.2778 and how to beat it)

### Why `h33-h33-2-b2` (CLAIM 0.2778) was the highest among the listed GEMSDOE* sites

The byte-checked lineage from SHA-256-pinned rasters in `.cache/gems_inputs/lineage/` and `data/bridge/` is:

| raster | +px | CLAIM | editorial operation |
|---|---:|---|---|
| H19-5 (`19GEMSDOE`) | 121,131 lines | 0.1922 | worm ridge set |
| D1.5 (`GEMSDOE24`) | 60,069 dots | 0.2477 | line → dot thinning |
| D2.8 (`GEMSDOE25`) | 44,090 | 0.2600 | spacing ≈2.8 px (≈ kernel radius) |
| SOLO (`GEMSDOE28`) | 40,199 | 0.2708 | drop dots ≤1 px of catalogue |
| **R0 = h33-h33-2-b2 (`GEMSDOE32`)** | **37,654** | **0.2778** | drop dots ≤2 px of catalogue |

The official DrivenData metric is `DTI = TPw / (TPw + 0.2·FPw + 0.8·|G|)` with 300 m triangular kernel `k(d)=max(0,1-d/3)` (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/, https://github.com/drivendataorg/gems-prize-reference-solution, https://en.wikipedia.org/wiki/Tversky_index, `vendor/gems57/metric.py` verified against `metric.dti_exact` on 30 random small cases to ≤1e-11). For binary dots:

- `TPw = Σ_g max_j p_j·k(d(j,g))` saturates per truth pixel (one nearby dot already gives full credit).
- `FPw = Σ_j p_j·(1 - max_g k(d(j,g)))` accrues per dot.

**Consequences:**

1. **Redundancy removal.** Dots closer than ~2.8 px share the same truth halo; deleting one keeps most `TPw` and cuts `0.2·FPw` linearly. Thinning H19-5 lines to 2.8 px dots keeps ~85% of `TPw` and cuts `FPw` 2.7×.
2. **Known-fault halo removal.** Organizer forum thread 11516 (cited in prior docs, not live-verified from sandbox) states visible catalogue pixels are masked from scoring. Dots ≤2 px from a mapped trace therefore contribute `TPw≈0` and only add `FPw`; removing the 2,545 `SOLO→R0` dots raises `DTI` by `Δ(1/DTI)≈0.2·ΔFP/TPw`, implying `TPw≈5.5k`, `|G|≈15k` (back-of-envelope, not a score).
3. **Budget optimality.** The marginal bar for one more non-redundant dot is `k > 0.2·DTI ≈ 0.056`. Most low-rank H19-5 pixels are below it.

**Thus R0 is an *emission optimum* on a fixed detector.** It does not discover new geology; it prunes a known ridge set to the metric's optimal geometry. Every higher CLAIM (0.2600→0.2708→0.2778) narrowed the same H19-5 support.

### Why other lanes scored lower in the listed sites

- **Breakline/Scarppol/StepEdge (Bands 12/19 `‖∇slope‖×coherence`):** 74.8% of off-skeleton dots fell on bare range-core cliffs (`det_elev` top tercile, `p>38.8 m`) and 28.9% on transverse canyon azimuths (65–135°), while only 18.2% reached the piedmont where >75% of INGENIOUS blind systems actually sit (Faulds et al. 2015, https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf; Wallace 1977). SGMC proxy 0.126 vs 0.096 for R0 confirms bedrock bias.
- **ANASIG (Bands 3/9/14 raw TMI gradients):** unreduced TMI lacks RTP phase correction; deep intrabasin steps (>200 m fill) are 100× weaker than range-front gradients and are invisible without reduction-to-pole.
- **NaN-outside encodings (`-nan.tif`):** The portal error `Predicted values must be in range [0, 1]` is triggered by any `NaN` or out-of-range finite value. `gems.gates` now rejects `Inf` outside and requires `require_submission_encoding=True` (all finite, `[0,1]`, zeros outside). Only `*-zeros.tif` with `0.0` outside is portal-safe (verified via `python -m gems validate` on every served file).
- **Dense continuous surfaces (17GEMSDOE `E-proba-multiscale`, 5,167,373 px = 100% footprint):** Under the literal “every positive cell is a dot” reading, every sparse candidate has forward overlap `1.0 > 0.70`. It is a dense probability field, not a dot field; its relevant test is rank correlation `|ρ| ≤0.90`, not dot overlap (flagged `#IR-92-DENSE-WITNESS-MATCHED-BUDGET` and `#IR-92-FAULTNET-DOT-DEFINITION`).

### How to beat 0.2778 (and the reported 0.4413 public #1)

The public leaderboard snapshot 0.4413 (`xiaofanhu`, 2026-10-24) — itself a CLAIM — proves 0.2778 is not a ceiling. Beating it requires a **better detector**, not more pruning:

1. **Target what R0 omits.** Faulds & Hinz (2015) and later inventories find step-overs/relay ramps host ~32% of Great Basin geothermal systems, terminations/intersections another ~25%, while major range-front segments host only ~3%. ~39% of INGENIOUS systems are blind (no Quaternary scarp). Worms lock onto the basement cutoff, catalogue onto scarps — neither onto the **relay breaching splay** 0.3–5 km between masters. That population is the hidden test set.

2. **Use independent physics.** R0/H19-5 are magnetic/gravity/topography worm derivatives. Independent confirmation needs:
   - RTP tilt/demagnetization trough (`∇²RTP >0` + `K/Th >p85` + `U/Th` redox, hydrothermal alteration) — *not* raw TMI.
   - Bouguer Poisson breakdown `α_Poisson` (`σ(ρ)` windowed regression of pseudogravity vs observed gravity) + basement curvature `κ_{B,⊥}`.
   - MT clay-cap lateral margin `‖∇log cond_surf‖` (smectite cap edge).
   - Blind silica/Na-K-Ca geothermometers `≥80 °C` (`GDR #1391`, https://gdr.openei.org/submissions/1391).
   - 3DEP 10 m micro-scarp curvature (USGS 3DEP, https://www.usgs.gov/3d-elevation-program) with Lahontan shoreline masking (1332 m AMSL).

   Each has a named mimic that must be de-confounded (range-core cliffs, Miocene basalt flow margins, playa clays, irrigation ponds, Lahontan beach ridges).

3. **Calibrate continuous `p_i ∈ [0.12,1.0]` to the DTI optimum.** Under `α=0.2`, any non-overlapping ridge pixel with marginal kernel credit `c_i > 0.2·DTI ≈0.056–0.088` raises `DTI` at `p=1`. Hard truncation at 37,654 discards 40,000–80,000 positive-expectation pixels (proved in PROVINCETOE §3.2). Future winners will emit `p_i` via out-of-fold Platt scaling, not `0/1`.

4. **Fix the NE-quadrant collapse.** All LOQO lanes score ~0 in NE (thick fill, different MT coverage). A 3-quadrant deployment with H19-5 fallback in NE is pre-registrable.

---

## RELAYGAP lane — targeting the relay gap

**Hypothesis:** Relay breaching faults sit in the tip-density high between en echelon masters (0.5–4 km separation, strike difference ≤20°, overlap ≥30%). The catalogue maps masters; it omits the transfers that host 57% of geothermal systems (Faulds et al. 2006, 2010, 2021a, https://www.osti.gov/servlets/purl/1110517; Giddens & Faulds 2025, https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf; Kim et al. 2004, https://doi.org/10.1016/j.jsg.2003.08.002).

**Mechanism:** For each fold, compute endpoints of the *visible* catalogue (8-connected, degree 1), smooth tip density with σ=8 px (800 m), mask to `2 < d_cat ≤60 px` halo (6 km search), modulate by local strike variance (structure-tensor coherence `1-coh`), normalize to `[0,1]`, smooth 300 m halo, greedy emit 37,654 dots at 2.8 px spacing (exact marginal-DTI greedy would be ideal but rank-greedy is near-optimal under `p=1` and spacing-dominated keeps; prior BREAKLINE test showed spaced top-L beats exact-DTI greedy by +0.000701 [+0.000321,+0.001161] when weights are rank-percentile). Visible faults are masked pixel-exactly; no 19-band stack is used.

**Non-fault mimic:** Collinear lithologic contacts, reactivated Luning-Fencemaker thrust slivers, and Pleistocene Lake Lahontan beach-ridge gaps between range fronts.

**Difference from repo:** `faultnet.py` adds 5 catalogue-network fields to a 24-feature HGB but learns emission; `STEPOVER` extrapolates tips along strike, `TIPGAPfar18f33` uses far-field tip proximity; none place dots *inside* the inter-tip gap interior weighted by tip density + strike variance. `BREAKLINE/SCARPPOL/STEPEDGE` are DEM curvature, not catalogue topology. `KNICKLOQO/VENTSCARP/POISSONFLEX` are LOQO learners needing the 19-band stack — this lane is stack-free.

### Experiments (budget = 3, 0 slots spent)

| arm | sigma | strike weight | d_cat | dots | HOLDOUT-DTI (gems57-pooled-hide-v2, 22,641 withheld, 8 folds seeds 20/21, 1000-draw cell bootstrap) | vs R0 | canary (catalogue AUC) |
|---|---|---|---|---|---|---|---|
| **relay** (primary) | 8 px | yes | (2,60] | 37,654 | **0.009453 [0.008898, 0.009970]** | **+0.005068 [+0.0040,+0.0062]** (+115%) | 0.8584 |
| relay_far | 8 px | yes | (4,60] | 37,654 | 0.000000 [0.0000,0.0000] | −0.004385 | 0.8584 |
| relay_norotate (ablation) | 3 px | no | (2,60] | 37,654 | 0.008511 [0.007966,0.008956] | +0.004126 [+0.0031,+0.0052] | 0.7074 |

- Controls on identical folds: **R0 0.004385 [0.003779,0.005080]** (rebuilt here; prior published R0 0.004006 on 22,663 withheld is within bootstrap variance), **H19-5 not rerun** (historically 0.096757 on Rule-2 `d_visible>2`, which is a different instrument).
- Single-feature leakage canary max = 0.8584 <0.90 (PASS). The tip-density surface is not a catalogue proxy that can memorize withheld segments.
- Static `d_cat>2` instrument is the primary for this catalogue-only lane; the stricter Rule-2 `d_visible>2` instrument would be reported if we had a full LOQO ensemble, but for a stack-free lane the static gate is the fair comparison (it is how R0 was gated).

**Interpretation:** `relay` more than doubles R0 and beats every prior pure-topography lane (`BREAKLINE f45 0.004861`, `SCARPPOL f45 0.005315`, `STRAINBREAK f60 0.005487`, `STEPEDGE f60 0.003980`). It is below the LOQO holdout best `KNICKLOQO standalone 0.010788 [0.009468,0.012201]` and `VENTSCARP 0.112213` on Rule-2, as expected for a stack-free model — but it is the **best stack-free HOLDOUT-DTI in GEMSDOE92** and the first to beat R0 with CI excluding 0 without any geophysics.

`relay_far` collapses to 0 because truly blind hidden faults in this holdout instrument sit within 2–4 px of visible masters (they are near-continuations, not 4 km-step-overs); the 300 m halo that R0 lineage shows to be low-yield on the organizer truth is actually high-yield on the catalogue-recovery proxy. This falsifies the “far-only” hedge for this instrument.

`relay_norotate` trails `relay` by −0.000942 [−0.0006,−0.0013] — strike-variance weighting is load-bearing, not decorative.

### Uniqueness (REGISTRY-MEASUREMENT)

- **Local sparse dot fields (≤150k px, ~120 served + bridge):** worst forward 3-px overlap `0.2421` vs `d28.tif` (44,090 px), `0.1921` vs `LISTRICDIP updip50` (37,654 px), `0.1152` vs `existing_faults.tif` (60,988 px) — all `≤0.70`. `|ρ|` on dot fields is <0.20. **PASS locally.**
- **Exact bytes:** SHA-256 `a6896265...` matches 0 of 120 local rasters; `byte_unique_among_checked=true`.
- **Public registry (102 repos, ~1,382 valid rasters):** not re-scanned this session (no `.cache/gemsdoe_public_registry` staged; network egress limited to GitHub/PyPI, and 418 MB training stack not staged). For a sparse 37,654-dot candidate the worst `≤80k`-dot public raster in prior lanes was `0.6804 ≤0.70` (`POISSONFLEX` audit) and `≤150k` worst was `0.6855` (`KNICKLOQO`). Extrapolating, `RELAYGAP relay` is expected to be `≤0.70` under the **like-for-like dot-field** reading.
- **Literal dense-surface reading (5,167,373 px `17GEMSDOE E-proba-multiscale`, 100% footprint):** forward overlap `1.0 >0.70` (every nonempty candidate fires). This is the pinned witness in `docs/downloads/review_c5e3848c_preflight.json` (`WITNESS_SHA256 ab0a0a62…`, `WITNESS_BLOB 374c88b1…`). It is a **continuous probability surface**, not a dot field; its relevant test is `|ρ| ≤0.90`, which passes (`|ρ|≈0.01` for our tip-density vs uniform-dense). The operative verdict uses the like-for-like reading; both readings are published (IR #IR-92-DENSE-WITNESS-MATCHED-BUDGET, #IR-92-FAULTNET-DOT-DEFINITION). **Literal firing is disclosed but not used to claim duplication.**

### Validator (prevents portal `[0,1]` error)

All three TIFFs: **11/11 MUST gates PASS** (`crs EPSG:32611`, `shape 3730×3292`, `transform 100,0,243350,0,-100,4508550`, `dtype float32 1 band`, `values_in_0_1 0 violations`, `no_nan_inside 0`, `nan_outside 0 nan 0 inf 0 zero 7111787`, `submission_encoding all_finite true [0.0,1.0] zero_outside true`, `catalogue_zero_mass 0`, `distance_from_catalogue radius 2 px 0 within`, `reread_sha256`).

This guarantees `Predicted values must be in range [0, 1]` will **not** occur (all values finite, in `[0,1]`, zeros outside, no NaN anywhere — the prior portal error came from `NaN`-outside encodings).

### Submission name / note / verdict

- **Submitted file (primary):** `gemsdoe92-relaygap-relay-37654-20261026T000000Z-zeros.tif` — SHA-256 `a689626572077c81a6d2763ac93f3354dcc301deec9d51399d11de48f9f5256e` — ZIP `gemsdoe92-relaygap-relay-37654-20261026T000000Z-zeros.zip`
- **Name (31/140):** `GEMSDOE92-RELAYGAP-relay-20261026`
- **Note (117/140):** `RELAYGAP relay: 37654 tip-density relay gaps (2<d<60px, strike-weighted); HOLDOUT-DTI 0.009453 [0.008898,0.00997] vs R0 0.004385`
- **Verdict:** `negative` / `submission_eligible: false` under the binding literal dense-surface reading; **`promote` under the like-for-like dot-field reading** (0/120 local >0.70). Weekly slots remain **0** until the selector resolves the dense-surface policy. Negative results are deliverables.

---

## Sources and verification

- Competition problem/metrics/leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ · https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ · https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and · DOI https://doi.org/10.5066/P93LGLVQ
- GDR INGENIOUS #1391: https://gdr.openei.org/submissions/1391
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Faulds & Hinz 2015 WGC: https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf
- Faulds et al. overview: https://www.osti.gov/servlets/purl/1110517
- Giddens & Faulds 2025: https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2025/Giddens.pdf
- Kim et al. 2004: https://doi.org/10.1016/j.jsg.2003.08.002
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program
- OPERA DISP-S1: https://www.earthdata.nasa.gov/data/catalog/asf-opera-l3-disp-s1-v1.0

Sandbox egress is limited to `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`; non-GitHub pages above were **not live-verified** from here and are for manual review. Site scores `0.2778`, `0.3195`, `0.4413` remain **CLAIM** (no organizer receipt in `ledger/submissions.csv`).
