# GEMSDOE92 — Auditable GEMS Prize Submission Workbench

> **Operating Contract:** Read this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every session. Every experiment adheres to parallel-run protocol rules (lane discipline, holdout evaluation, leakage canary, registry uniqueness, and machine-readable run cards). Core Values: **Maximize P(Win)** and **Own the Outcome**.

---

## Current Primary (2026-10-24, `APRONRIDGE free1d`): #1 All-Time Holdout-DTI & Standalone Physics GeoTIFF

**✅ FORMAT-VALID (10/10 automated gates PASS) — OK TO DOWNLOAD FOR RESEARCH.**  
**⛔ NOT CLEARED FOR A WEEKLY SLOT — DO NOT SUBMIT (`verdict: negative`, `submission_eligible: false` solely under the binding `17GEMSDOE` full-footprint dense public witness).**

| Field | Audited Value / Link |
|---|---|
| **Primary GeoTIFF (zeros-outside)** | [`docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`](docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif) |
| **Single-TIFF ZIP Archive** | [`docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.zip`](docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.zip) |
| **Submission Name** | `GEMSDOE92-APRONRIDGE-free1d-20261024` |
| **Submission Note (`92` chars `<= 140`)** | `h33-h33-2-b2; APRONRIDGE free1d: 37654 standalone 1D piedmont-apron + RTP ridges (0 H19-5)` |
| **SHA-256 (`-zeros.tif`)** | `1a29a5d81e8561954f04a563b4975cb84d00898b8d7634700a9d409a10e06cbc` |
| **SHA-256 (`.zip` / NaN-cache)** | `6f91c4a3b42083e5d30aaf071dbdc2a0dc0ae68363f8822afc701247be53871a` / `d5760830106d338184569e18ccbc05f7ee6d21b6067c32989e83440d4847a3f3` |
| **Grid & Automated Validation** | `EPSG:32611` · `3730 × 3292` @ `100 m` · single-band `float32` · `nodata=None` · finite `[0, 1]` (`0` NaNs in footprint, `0.0` outside) · `37,654` unit dots · `0` catalogue mass · `min d_cat > 2.0 px` (`10/10` gates PASS) |
| **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`)** | **`0.008354 [0.006823, 0.010135]`** (`22,663` withheld positives, `8` folds) — **#1 all-time in repo**: `+108.5%` vs `R0` (`0.004006`, paired Δ `+0.004347 [+0.003019, +0.005710]`), `+52.2%` vs `STRAINBREAK f60s2i` (`0.005487`), `+38.2%` vs `RELIEF p10` (`0.006045`) |
| **Leakage Canaries & `SGMC PROXY`** | `11/11 PASS` (`max symmetric AUC = 0.636490 <= 0.90`); USGS SGMC 1:500k off-catalogue `PROXY = 0.080098` (vs `R0` `0.096060`) |
| **Uniqueness (`REGISTRY-MEASUREMENT`)** | Surface vs `29` local rasters: `\|ρ\| <= 0.1222`, top-37k overlap `0.5527 <= 0.70`; final dots vs `43` cross-lane local rasters: **`worst_forward_overlap = 0.4605 <= 0.70`**, `\|φ\| <= 0.0561`; top public sparse witnesses (`62GEMSDOE`/`GEMSDOE23`): `0.6028–0.6456 <= 0.70`; **binding dense public witness `17GEMSDOE E-proba-multiscale` (`100%` footprint positive): `1.000` (`stop_required: true`)** |
| **Audit, Analysis & Site Guides** | [Format Audit JSON](docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-audit.json) · [Run Card JSON](evidence/apronridge_run_card.json) · [Witness Check JSON](evidence/public_witness_apronridge.json) · [PhD Analysis](docs/ANALYSIS_20261024_APRONRIDGE.md) · [Pre-Registered Hypotheses](docs/HYPOTHESES_20261024_APRONRIDGE.md) · [Executive Summary](docs/executive-summary.html) · [Submission Guide](docs/SUBMIT.html) |

Pre-registered hybrid ablation siblings built in the same 3-experiment budget (research-only; never submit multiple siblings): [`APRONRIDGE s60f40`](docs/downloads/h33-h33-2-b2-APRONRIDGEs60f40-20261024-6e7e0174-zeros.tif) (`HOLDOUT-DTI = 0.008291 [0.007073, 0.009643]`, worst local overlap `0.5916`) and [`APRONRIDGE s50f50`](docs/downloads/h33-h33-2-b2-APRONRIDGEs50f50-20261024-2f0431ea-zeros.tif) (`HOLDOUT-DTI = 0.008097 [0.006851, 0.009478]`, worst local overlap `0.5188`).

---

## Audited Cross-Lane Benchmark Table (`gems57-pooled-hide-v2`, `22,663` Withheld Positives)

> **Evidence Rule:** Local `HOLDOUT-DTI` and `SGMC PROXY` values rank methods on withheld catalogue segments and 1:500k bedrock faults; they are **never** numerically comparable to DrivenData leaderboard scores (`CLAIM 0.2778`, `LEADERBOARD-SNAPSHOT 0.3195 / 0.4413`). `ledger/submissions.csv` currently holds `48 BUILT / 0 RECEIPT` rows.

| Lane / Variant | Dots (`H19-5` / Off-Skel) | `HOLDOUT-DTI` [95% CI] | Paired Δ vs `R0` | `SGMC PROXY` | Canary Max AUC | Worst Local 3-px Overlap | Local Unique? | Slot Status |
|---|---:|---|---:|---:|---:|---:|---|---|
| **`APRONRIDGE free1d`** *(primary)* | `0 / 37,654` | **`0.008354 [0.006823, 0.010135]`** | **`+0.004347`** | `0.08010` | `0.6365` | **`0.4605`** | **Yes** | Blocked by `17GEMSDOE` dense witness |
| **`APRONRIDGE s60f40`** | `22,592 / 15,062` | **`0.008291 [0.007073, 0.009643]`** | **`+0.004285`** | `0.08135` | `0.6365` | `0.5916` | **Yes** | Sibling dose (research-only) |
| **`APRONRIDGE s50f50`** | `18,827 / 18,827` | **`0.008097 [0.006851, 0.009478]`** | **`+0.004091`** | `0.08149` | `0.6365` | `0.5188` | **Yes** | Sibling dose (research-only) |
| `RELIEF p10piedmont` | `37,654 / 0` | `0.006045 [0.005179, 0.006882]` | `+0.002039` | `0.08725` | `0.5531` | `> 0.90` (`R0`) | No (`R0` dup) | Stopped (local duplicate) |
| `STRAINBREAK f60s2i` | `15,062 / 22,592` | `0.005487 [0.004550, 0.006386]` | `+0.001481` | `0.10516` | `0.6216` | `0.6642` | Yes | Below `APRONRIDGE`; witness stop |
| `SCARPPOL f45Stop` | `20,710 / 16,944` | `0.005315 [0.004387, 0.006418]` | `+0.001309` | `0.12358` | `0.5945` | `0.9130` (`BL`) | No (`BL` dup) | Stopped (local duplicate) |
| `ANASIG f45Atop` | `20,710 / 16,944` | `0.004967 [0.004102, 0.005931]` | `+0.000961` | `0.08056` | `0.5511` | `0.5877` | Yes | Below `APRONRIDGE`; witness stop |
| `SPRINGALIGN f33Ctop` | `25,228 / 12,426` | `0.004865 [0.004038, 0.005782]` | `+0.000859` | `0.08017` | `0.5531` | `0.6700` | Yes | Below `APRONRIDGE`; witness stop |
| `BREAKLINE f45Ltop` | `20,710 / 16,944` | `0.004861 [0.003930, 0.005887]` | `+0.000854` | `0.12611` | `0.6216` | `0.5500` | Yes | Below `APRONRIDGE`; witness stop |
| `visible-collar` *(diagnostic)* | `0 / 37,654` | `0.046866` *(catalogue-collar artifact)* | `+0.042860` | `0.02119` | `0.7456` | `1.0000` (public) | Yes (local) | Stopped (catalogue-collar + public dup) |
| `R0` (`h33-h33-2-b2` parent) | `37,654 / 0` | `0.004006 [0.003408, 0.004651]` | `0.000000` | `0.09606` | — | — | Reference | `CLAIM 0.2778` baseline |

---

## PhD Analysis: Why `GEMSDOE32` Scored `0.2778` (`CLAIM`) & How `APRONRIDGE` Advances Discovery

Full mathematical & structural derivation: [`docs/ANALYSIS_20261024_APRONRIDGE.md`](docs/ANALYSIS_20261024_APRONRIDGE.md).

1. **Why `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`R0`) Reached `0.2778` (`CLAIM`)**:
   - Under the competition's asymmetric Distance-weighted Tversky Index ($\alpha = 0.2, \beta = 0.8$, `300 m` / `3 px` linear kernel, verified in [`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution)), false positives carry **4× the denominator penalty** of false negatives (`0.8` vs `0.2`), and overlapping dots closer than `2.8 px` saturate $\max_y K(\|x-y\|) P(y)$ without adding true-positive credit.
   - SHA-verified parent lineage (`gems/parent.py`): `H19-5` (`121,131` worm-skeleton px, `CLAIM 0.1922`) $\to$ `D1.5` (`86,625` px) $\to$ **`D2.8`** (`44,090` px at `280 m` kernel-matched spacing, `CLAIM 0.2600`, `+0.0678`) $\to$ **`SOLO`** (`39,580` px removing isolated point dipoles, `CLAIM 0.2708`, `+0.0108`) $\to$ **`R0/B2`** (`37,654` px pruning `1,926` dots within `d_cat <= 2.0 px` of mapped `existing_faults.tif` and encoding `0.0` outside footprint to avoid DrivenData's `NaN` range error, `CLAIM 0.2778`, `+0.0070`).
2. **Why `R0` Plateaued — and What `APRONRIDGE` Fixes**:
   - `R0` allocates `58.2%` of its dots to deep central playas (`20.4%`, where `> 1 km` basin fill masks basement faults and hosts Lake Lahontan shoreline mimics) or high eroded mountain cores (`37.7%`, dominated by inactive Mesozoic thrusts), leaving only `41.8%` in the piedmont transition; and its magnetic worms derive from raw `TMI` (`Bands 3/9/14`), whose gradients are laterally shifted `300–800 m` off steep faults by `~65°` geomagnetic inclination — exceeding the `300 m` DTI scoring cone.
   - **`APRONRIDGE`** confines habitat to the **thin-cover piedmont accommodation apron** (`Band 12 det_elev` transition $\times$ `Band 15 depth_to_base_surf` log-normal `~20–600 m` $\times$ `Band 5 iso_grav_anom_slope`, concentrating `75.4%` of `free1d` dots in the piedmont) and fuses coherent DEM slope-breaks (`Bands 19/12`) with inclination-corrected **Reduced-to-Pole magnetic gradient $\times$ inverted `tc` edge curvature** (`Bands 2/6`) along 4-axis 1D crests — more than doubling `R0` on `HOLDOUT-DTI` (`0.008354` vs `0.004006`) without using a single `H19-5` or `R0` pixel. Only a future `ORGANIZER-CONFIRMED` submission receipt can test whether this local holdout gain translates to the live leaderboard (`0.3195` / `0.4413` remain unverified `LEADERBOARD-SNAPSHOT` claims).

---

## Audited 19-Band `training_features.tif` Stack (`EPSG:32611`, `3730 × 3292`, `5,167,373` Footprint Cells)

Verified directly from GDAL band headers and footprint pixel distributions (`registry/session_manifest.json` SHA-256 `62b30541...`):

| Band | Official GDAL Description | Sign | Valid Footprint Px | `q05` | Median (`q50`) | `q95` | Used in `APRONRIDGE`? |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `mag_anom` — Magnetic anomaly | Signed | `5,164,312` | `-204.37` | `-57.69` | `162.74` | — |
| **2** | **`rtp` — Reduced to pole magnetic data (latitude/inclination-corrected)** | **Signed** | `5,164,312` | `-332.48` | `-137.22` | `153.75` | **Yes (`R_rtp` gradient & coherence)** |
| 3 | `tmi_hg` — Total magnetic intensity horizontal gradient | Non-neg | `5,164,312` | `1.64` | `13.16` | `93.85` | — |
| 4 | `geod_2ndinv` — Geodetic strain-rate second invariant | Non-neg | `5,164,312` | `2.50` | `19.91` | `46.20` | — |
| **5** | **`iso_grav_anom_slope` — Isostatic gravity anomaly slope** | **Non-neg** | `5,164,312` | `0.029` | `0.102` | `0.270` | **Yes (`H_apron` density-step prior)** |
| **6** | **`tc` — Magnetic tilt angle / total curvature edge derivative** | **Non-neg** | `5,164,300` | `11.81` | `18.48` | `25.58` | **Yes (`-tc` in `R_rtp`)** |
| 7 | `geod_shearrate` — Geodetic GPS/InSAR shear rate | Non-neg | `5,164,312` | `0.00` | `9.70` | `29.14` | Screened (`MTSHEAR-CONDUIT`) |
| 8 | `geod_dilaterate` — Geodetic volumetric dilatation rate | Signed | `5,164,312` | `-2.85` | `5.50` | `19.20` | — |
| 9 | `tmi_vg` — Total magnetic intensity vertical gradient | Signed | `5,164,312` | `-0.285` | `-0.009` | `0.319` | — |
| 10 | `deq_n100a15` — Distance to earthquake (`n=100 km, a=15°`) | Non-neg | `5,164,312` | `180.80` | `622.80` | `8631.38` | — |
| 11 | `iso_grav_anom_vg` — Isostatic gravity vertical gradient | Signed | `5,164,312` | `-2.70` | `-0.072` | `2.61` | Screened (`GRAVTILT-ZERO`) |
| **12** | **`det_elev` — Detrended elevation (`3DEP`)** | **Signed** | `5,164,312` | `-330.67` | `-75.58` | `450.24` | **Yes (`H_apron` + `R_scarp` coherence)** |
| 13 | `iso_grav_anom` — Isostatic gravity anomaly | Signed | `5,164,312` | `-26.09` | `-7.26` | `7.74` | Screened (`GRAVTILT-ZERO`) |
| 14 | `tmi` — Total magnetic intensity | Signed | `5,164,312` | `-298.64` | `-124.82` | `140.08` | — |
| **15** | **`depth_to_base_surf` — Depth to basement / sediment thickness (m)** | **Signed** | `5,164,312` | `6.21` | `316.37` | `1881.26` | **Yes (`H_apron` thin-cover gate)** |
| 16 | `ieq_n100a15` — Earthquake intensity/density (`n=100 km, a=15°`) | Non-neg | `5,164,312` | `312.50` | `755.70` | `2723.60` | — |
| 17 | `cond_surf` — Subsurface magnetotelluric electrical conductivity | Non-neg | `5,164,312` | `1.84` | `2.89` | `3.91` | Screened (`MTSHEAR-CONDUIT`) |
| 18 | `iso_grav_anom_hg` — Isostatic gravity horizontal gradient | Signed | `5,164,312` | `-3.40` | `0.038` | `3.30` | — |
| **19** | **`det_elev_slope` — Detrended elevation slope (`3DEP`)** | **Non-neg** | `5,164,312` | `0.168` | `3.749` | `25.337` | **Yes (`R_scarp` break-in-slope)** |

---

## Prior Session Candidate — `SPRINGALIGN f33Ctop` (2026-10-25, Superseded as Primary by `APRONRIDGE free1d`)

**✅ OK TO DOWNLOAD for research — ⛔ NOT CLEARED FOR A WEEKLY SLOT (verdict negative).**

| Deliverable | Link |
|---|---|
| **GeoTIFF (primary, zeros-outside)** | [docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif) |
| ZIP (one TIFF) | [docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip](docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.zip) |
| Submission name | `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025` |
| Note (≤140) | `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5` |
| SHA-256 (zeros) | `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1` |

SPRINGALIGN: hot-spring pair strike alignments (GDR INGENIOUS, pinned).
HOLDOUT-DTI `gems57-pooled-hide-v2` (22,663 withheld) **0.004865
[0.004025, 0.005785]** — beats R0, below holdout best RELIEF p10, so
**negative**: downloadable, not slot-cleared. Locally unique (surface
|ρ|≤0.009; final forward ≤0.670). Dense public witness policy unresolved.
Full record: [analysis](docs/ANALYSIS_20261025_SPRINGALIGN.md) ·
[run card](evidence/springalign_run_card.json). The 0.2778 GEMSDOE32
value remains a CLAIM (no receipt); no local score beats it by assertion.

**Historical closeout (superseded by SPRINGALIGN above for downloads): OK TO DOWNLOAD for research; NOT OK TO SUBMIT.** BREAKLINE witness: REGISTRY-MEASUREMENT 100% forward overlap with 17GEMSDOE dense raster. [Review](docs/REVIEW_CURRENT.md) · [closeout](docs/REVIEW_CLOSEOUT_20261024.md)

---
## New primary (ANASIG session, 2026-10-24): locally unique, still not cleared

**✅ FORMAT-VALID — OK TO DOWNLOAD for research. ⛔ DO NOT SUBMIT / NOT CLEARED FOR A WEEKLY SLOT.**

| Deliverable | Link |
|---|---|
| **GeoTIFF (primary)** | [Download ANASIG zeros-outside GeoTIFF](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif) |
| ZIP (one TIFF) | [Download ZIP](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.zip) |
| Submission name | `GEMSDOE92-ANASIG-f45Atop-20261024` |
| Note (84 chars) | `h33-h33-2-b2; ANASIG f45Atop 16944 far dots on analytic-signal ridges >3px off H19-5` |
| SHA-256 | `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5` |
| Audit | [Gate receipt](docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json) · [run card](evidence/anasig_run_card.json) · [analysis](docs/ANALYSIS_20261024_ANASIG.md) |

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld): ANASIG **0.004967 [0.004098, 0.005940]**, Δ vs R0 +0.000961 [+0.000168, +0.001814], vs holdout-best RELIEF p10 (0.006045) −0.001078 [−0.002034, −0.000112]; canary max 0.551113; SGMC PROXY 0.080556 vs R0 0.096060. Local uniqueness passes (24 rasters: worst forward 0.550, |ρ| 0.547; surface |ρ| 0.024). Slot blockers: holdout-best bar + the footprint-positive public witness below (forward overlap 1.000 for these bytes, `evidence/public_witness_anasig.json`). This session's rank-1 SCARPPOL lane beat BREAKLINE on holdout (0.005315) but overlaps it 0.900–0.913 → duplicate-stopped (`evidence/scarppol_run_card.json`). No slot used. Ranked hypotheses/screens: `docs/HYPOTHESES_20261024_SCARPPOL.md`.

---

## Parallel candidate — STRAINBREAK f60s2i (2026-10-24 late session, also negative)

**✅ FORMAT-VALID — OK TO DOWNLOAD. ⛔ NOT CLEARED FOR A WEEKLY SLOT (verdict negative).** Unique new TIF: 22,592 dots (60%) on strained coherent DEM scarp-breaks (`S = BREAKLINE L × pct_rank(Band 4 geod_2ndinv)`), >3 px off the whole H19-5 skeleton **and** >3 px off BREAKLINE f45's far dots; 15,062 coverage-greedy R0 dots kept; 37,654 total. Hypothesis: scarps on currently-loading structures (young step-over strands) are missed by both catalogue and worms. Mimic: Walker Lane strain shadows, subsidence, Lahontan shorelines in strained crust. This session's rank-1 GRAVCrest (signed Band-18 gravity crest) was **falsified by the pre-build SGMC screen and never built** (far-only SGMC 0.005–0.016 vs 0.072).

| Deliverable | Link |
|---|---|
| **GeoTIFF (zeros-outside)** | [Download](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif) · [ZIP](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2.zip) |
| Submission name | `GEMSDOE92-STRAINBREAK-f60s2i-20261024` |
| Note (87 chars) | `h33-h33-2-b2; STRAINBREAK f60s2i 22592 far dots on strained scarp-breaks >3px off H19-5` |
| SHA-256 (zeros) | `000d0bd7e0a549c2d38ca52a5df5b249763a7be998ad2ccfa30cc45136c05c1f` |
| Audit / run card | [audit](docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-audit.json) · [run card](evidence/strainbreak_run_card.json) · [analysis](docs/ANALYSIS_20261024_STRAINBREAK.md) · [hypotheses](docs/HYPOTHESES_20261024_GRAVCrest.md) |

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld px): f60s2i **0.005487 [0.004522, 0.006430]** — the best locally-unique holdout in this repo (R0 0.004006, BREAKLINE f45 0.004861), Δ vs R0 +0.001481 [+0.000582, +0.002296]; dose plateau f45 0.005022 → f60 → f75 0.005486. But it does **not** beat the holdout best (RELIEF p10 0.006045, paired Δ CI includes 0) and SGMC prefers BREAKLINE (0.12611 vs 0.10516) → promotion rule fails, verdict **negative**. Local uniqueness: worst forward overlap 40.0% / |ρ| 0.401 (21 rasters; surface worst 10.0% / sampled ρ 0.103). Expanded public-registry scan (1,309 rasters, complete for declared scope; `evidence/strainbreak_public_registry_uniqueness.json`): **literal duplicate stop triggered** — worst forward overlap 1.0 (17GEMSDOE full-footprint E-proba), 89 rasters >70%, worst |ρ| 0.417; even vs sparse dot-like rasters only (≤150k positives, 1,125 checked; diagnostic, not a gate) worst is 0.7105 with 3 over 70%. The queued BREAKLINE public scan was also run this session: likewise duplicate (134 >70%; `evidence/breakline_public_registry_uniqueness.json`). Leakage canary max 0.6216. Queued item closed: visible-collar SGMC = 0.021192 vs R0 0.09606 (its holdout gain does not transfer off-catalogue).

## Executive Summary — Format-Validated Candidate, One-Click Download

**✅ FORMAT-VALID — OK TO DOWNLOAD.** The generated submission raster is an all-finite, single-band float32 GeoTIFF, EPSG:32611, shape 3730 × 3292, matching the competition template geotransform. It contains zero NaNs inside the footprint, zeros outside, values strictly in `[0, 1]`, and passes all 10 local MUST gates on independent re-read from disk. This completely prevents the DrivenData portal error: `Predicted values must be in range [0, 1]`.

**⛔ NOT CLEARED FOR A WEEKLY SLOT — DUPLICATE UNDER THE LITERAL REGISTRY RULE.** An expanded scan found 100% 3-px forward overlap with public registry rasters (131 of 1,279 exceed 70%). Stop; do not submit. This file remains downloadable as a negative research deliverable. The scan covers current default branches in 102 public owner repositories, not every historic/site-hosted file.

| Deliverable | Link / Metadata |
|---|---|
| **GeoTIFF (.tif)** | [Download zeros-outside submission GeoTIFF](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif) |
| **ZIP (one TIFF)** | [Download ZIP (contains single TIFF)](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.zip) |
| **Submission Name** | `GEMSDOE92-visible-collar-r0-excluded-20261024` |
| **Note (62 chars)** | `Visible-fault collar 2-3 px; R0 3px halo excluded; 37,654 dots` |
| **SHA-256 Digest** | `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7` |
| **Grid / Dimensions** | EPSG:32611 · 3730 × 3292 @ 100 m resolution · float32 · 37,654 unit-mass dots |
| **Submission Guide** | [Executive Summary Subpage](docs/executive-summary.html) · [Submission Steps (SUBMIT.html)](docs/SUBMIT.html) · [Live Project Site](https://buffedlizard55-lab.github.io/GEMSDOE92/) |
| **Audit Receipt** | [Format Audit Receipt (JSON)](docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-audit.json) · [Full Run Card (JSON)](evidence/visible_collar_run_card.json) |

**Verdict: Negative (Duplicate).** Local format validity is 100% confirmed, but no competition slot was spent due to literal registry overlap.

---

## Parallel Candidate — BREAKLINE f45Ltop (DEM Scarp-Break Coherence)

A second session built **BREAKLINE f45Ltop**: keeping 20,710 parent R0 dots via exact expected-DTI greedy under an orientation-coherent slope-break field $L = \text{pct\_rank}(\|\nabla \text{det\_elev\_slope}\|) \times \text{coherence}(\text{det\_elev})$ (Bands 19/12), and allocating 16,944 far dots (45%) to the strongest coherent breaks located **>3 px off the entire H19-5 skeleton**.

- **Download:** [`docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif`](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif) · [ZIP](docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0.zip)
- **Submission Name:** `GEMSDOE92-BREAKLINE-f45Ltop-20261024`
- **Submission Note (90 chars):** `h33-h33-2-b2; BREAKLINE f45Ltop 16944 far dots on linear scarp-break ridges >3px off H19-5`
- **SHA-256 Digest:** `cd9c8a564588e6542b379cd36cbe05fc6da3be07b8edbc542bf737336907810e`
- **Validation:** 10/10 local MUST gates pass on independent re-read.
- **HOLDOUT-DTI:** **0.004861 [0.004032, 0.005822]**, paired delta vs R0 **+0.000854 [+0.000300, +0.001423]**; dose-monotone f33 &rarr; f38 &rarr; f45; USGS SGMC off-catalogue control **+31% vs R0** (0.12611 vs 0.09606); leakage canary max **0.6216** (<0.90 threshold).
- **Local Uniqueness:** Worst forward overlap **55.0%** (vs parent R0), worst $|\rho| = 0.547$; vs visible collar candidate only **3.5%** forward overlap (&phi; &asymp; 0.001, disjoint lanes).
- **Public Registry Audit:** A live public witness check confirmed 100% forward overlap with GEMSDOE17 E-proba. Duplicate; stop. See `evidence/breakline_public_registry_witness17.json`.
- **Verdict:** Negative / NOT CLEARED for slot (below holdout-best arms; stopped by registry overlap). Full analysis: [`docs/ANALYSIS_20261024.md`](docs/ANALYSIS_20261024.md); run card: [`evidence/breakline_run_card.json`](evidence/breakline_run_card.json).

---

## What the reported GEMSDOE32 value can support

The reported value **0.2778 is a CLAIM** copied from the supplied GEMSDOE32 site history; this checkout has no submission-page receipt for that artifact. The reported lineage H19-5 → D2.8 → SOLO → B2/R0 is consistent with changes to candidate geometry, thinning, pruning, and known-catalogue clearance. The prompt-reported intermediate values 0.1922, 0.2600, and 0.2708 are also CLAIMs, not organizer-confirmed receipts here.

A plausible mechanism is that thinning spatially redundant predictions reduces false-positive cost while maintaining coverage, and avoiding mapped catalogue pixels avoids predictions that may be masked. This is **mechanistic inference**, not causal proof: attributing score changes requires exact artifacts, identical scoring conditions, controlled ablations, and organizer receipts. Nearby predictions can have overlapping kernel support while each emitted prediction contributes to total prediction mass; that makes redundancy a sensible experiment, not proof that a specific thinning step caused the claimed increase. Local HOLDOUT-DTI is not comparable to private leaderboard scores.

The prompt's **0.3195 and 0.4413 are conflicting leaderboard snapshots/claims**; neither was refreshed in this session. We have no authenticated winning raster or method receipt, so cannot state that the highest-scoring submission fused a skeleton, DEM scarps, stepovers, radiometrics, or vent proximity. A score alone does not reveal its feature set. The project has not established that a candidate beats the 0.2778 CLAIM.

The concepts and previous screens are catalogued in [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html), [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md), and [`docs/REVIEW_CURRENT.md`](docs/REVIEW_CURRENT.md). Their rankings are research priorities, not score forecasts. BREAKLINE, SCARPPOL, ANASIG, and STRAINBREAK are already tested—not new hypotheses. The current full-footprint public-registry witness blocks all nonempty in-footprint predictions under the literal overlap rule; do not emit another submission artifact unless that policy blocker is explicitly resolved.

## Pre-Registered Geological Hypotheses (2026-10-24 `APRONRIDGE` Session, Ranked Before Building)

Full equations, mimics, and screen receipts: [`docs/HYPOTHESES_20261024_APRONRIDGE.md`](docs/HYPOTHESES_20261024_APRONRIDGE.md) · [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) · [`evidence/apron_prebuild_screen.json`](evidence/apron_prebuild_screen.json).

| Rank | Hypothesis | Specific Layers | Physical Signature & Transform | Why Missing from USGS / INGENIOUS Catalogue | Outcome (`SCREEN-AUC` / `HOLDOUT-DTI`) & Official Source |
|---:|---|---|---|---|---|
| **1** | **`APRONRIDGE` (Implemented)** | Bands `15`, `12`, `5`, `19`, `2`, `6` | Thin-cover piedmont apron $H_{\text{apron}}(B_{12}, B_{15}, B_5)$ gating $\max(R_{\text{scarp}}[B_{19},B_{12}],\,0.85\,R_{\text{rtp}}[B_2,B_6])$ on 4-axis 1D crests | Catches alluvial piedmont step-faults lacking gravity worms and shallow-buried basement steps whose raw-TMI signal was shifted `300–800 m` off-fault by geomagnetic inclination | Canary **`0.6365`**; **`free1d` `HOLDOUT-DTI = 0.008354`** (**#1 in repo**) · [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [DOE GDR #1391](https://gdr.openei.org/submissions/1391) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) |
| **2** | **`RTPTILT-CURV`** | Bands `2` (`rtp`) & `6` (`tc`) | $\|\nabla\text{rtp}\| \times (-\text{tc}) \times \text{coh}(\text{rtp})$ | Removes dipolar inclination skew over buried volcanic/basement contacts | Canary `0.5413`, far `SGMC = 0.0350` (folded into `APRONRIDGE` Channel 2, winning `10.5%` of far crests) · [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) |
| **3** | **`BLIND-GEOTHERM`** | GDR #1391 silica/cation geothermometers (`>=90°C`) + Bands `15`, `5` | Upflow halo ($\sigma=18\text{ px}$) around `477` deep-equilibrated chemical geothermometer anomalies gating thin-cover basement ramps | ~75% of Great Basin hydrothermal systems are blind (cool outflow waters retaining `>90°C` chemical equilibration above unmapped faults) | Canary `0.5519`, far `SGMC = 0.0190` (reserve hydrothermal gate) · [DOE GDR #1391](https://gdr.openei.org/submissions/1391) |
| **4** | **`MTSHEAR-CONDUIT`** | Bands `17` (`cond_surf`) & `7` (`geod_shearrate`) | Magnetotelluric conductance gradient $\times$ dextral-normal GPS/InSAR shear rate | Targets clay-altered / brine-filled transtensional Walker Lane conduits lacking scarps | Canary `0.5191`, far `SGMC = 0.0245` (not built: MT/GPS grid too smooth at `100 m`) · [INGENIOUS](https://gbcge.org/current-projects/ingenious/) |
| **5** | **`GRAVTILT-ZERO`** | Bands `11` (`iso_grav_anom_vg`), `5`, `13` | MAD-standardized gravity tilt zero-contour ridge | AGC-normalizes subtle intrabasin basement steps against large range-front pluton edges | Canary `0.5107`, far `SGMC = 0.0280` (not built: terrestrial gravity spacing `~2–5 km` exceeds `300 m` kernel) · [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |

---

## Core Values & Decision Framework

### Maximize P(Win)
&ldquo;Maximize the Probability of Winning&rdquo;: our decision-making framework. In every decision, we weigh trade-offs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside emotions and make tough decisions in order to maximize P(Win). &ldquo;Maximize P(Win)&rdquo; frees us from constraints and clarifies that we must put Arena first.

### Own the Outcome
We own results end to end &mdash; not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

---

## Reproducible Validation & Verification Pipeline

```bash
# 1. Restore all 12 SHA-256 pinned inputs into .cache/gems_inputs/
python3 scripts/restore_inputs.py

# 2. Rebuild & validate the 3 pre-registered APRONRIDGE experiments + holdout/uniqueness audit
.venv/bin/python scripts/build_apronridge_variants.py
.venv/bin/python scripts/report_apronridge_proxies.py

# 3. Run the automated test suite in the pinned environment
.venv/bin/python -m pytest -q

# 4. Verify pinned data manifests and hashes
.venv/bin/python scripts/verify_manifest.py

# 5. Run automated gate & site contract inspection on all served downloads
.venv/bin/python scripts/check_site.py

# 6. Format validation on the current primary GeoTIFF (format pass != slot clearance)
.venv/bin/python scripts/validate_submission.py --candidate docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif
```

---

## Trusted Sources & Manual Review Links

- [DrivenData Competition #306 Problem & Metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData DOE GEMS About Page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData Competition Rules (PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData Reference Solution Repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN Airborne Surveys Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE Geothermal Data Repository (GDR) INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [Great Basin Center for Geothermal Energy (INGENIOUS Project)](https://gbcge.org/current-projects/ingenious/)
- [USGS 3D Elevation Program (3DEP)](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611 WGS 84 / UTM Zone 11N Coordinate Reference System](https://epsg.io/32611)
- [Tversky Index Formulation (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index)

---

## Original Session Prompt

```markdown
Review the repo. 

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION.  DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION.  BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.  IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.  A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.

5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The following sites should serve as a starting point for understanding how to generate TIF submissions...
WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition.  Must be unique submission unlike any within the GEMSDOE sites above.  Verify working line by line no hallucinations.
Current competition leaderboard GEMSDOE high score: 0.4413
```
