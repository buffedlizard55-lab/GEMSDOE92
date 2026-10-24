# GEMSDOE92 — Auditable GEMS Prize Submission Workbench

> **Operating Contract:** Read this README and [`SESSION_PROMPT.md`](SESSION_PROMPT.md) at the start of every session. Every experiment adheres to parallel-run protocol rules (lane discipline, holdout evaluation, leakage canary, registry uniqueness, and machine-readable run cards). Core Values: **Maximize P(Win)** and **Own the Outcome**.

---

## Latest (2026-10-24, PIEDFRONT f35Ptop): NEW UNIQUE TIF GENERATED — HIGHEST NON-COLLAR HOLDOUT-DTI (`0.006425`)

**✅ OK TO DOWNLOAD for research (10/10 format gates PASS on disk reread) — ⛔ NOT CLEARED FOR A WEEKLY SLOT (verdict `negative`).**

| Deliverable | Link |
|---|---|
| **GeoTIFF (primary, zeros-outside)** | [docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif](docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif) |
| ZIP (one TIFF) | [docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.zip](docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.zip) |
| Submission name | `GEMSDOE92-PIEDFRONT-f35Ptop-20261024` |
| Note (≤140 chars, 111 chars) | `h33-h33-2-b2; PIEDFRONT f35Ptop 13179 far piedmont scarp-gravity dots >3px off H19-5 + 4000 H19-5 hole refill` |
| SHA-256 (zeros) | `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8` |
| Audit / Run Card / Analysis | [gate audit receipt](docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-audit.json) · [run card](evidence/piedfront_run_card.json) · [analysis](docs/ANALYSIS_20261024_PIEDFRONT.md) · [hypotheses](docs/HYPOTHESES_20261024_PIEDFRONT.md) · [17GEMSDOE witness](evidence/piedfront_public_registry_witness17.json) |

**What `PIEDFRONT` is and why it broke the off-skeleton `HOLDOUT-DTI` ceiling:**
- Prior off-skeleton lanes (`BREAKLINE f45` `0.004861`, `SCARPPOL f45` `0.005315`, `STRAINBREAK f60` `0.005487`, `ANASIG f45` `0.004967`, `SPRINGALIGN f33` `0.004865`) trailed `RELIEF p10` (`0.006045`) because unnormalized DEM slope-break magnitude $\|\nabla\,\text{det\_elev\_slope}\|$ placed **74.8%** of far dots in steep mountain range interiors (`det_elev >= 38.76 m`), whereas active Basin-and-Range normal faults and blind geothermal step-overs sit at the piedmont range-front transition. Simultaneously, `R0` (`h33-h33-2-b2`) had **794 spacing-legal holes** on `H19-5` ($d_{\text{R0}} > 2.8\text{ px}, d_{\text{cat}} > 2.0\text{ px}$) left behind when `b2` pruned $d_{\text{cat}} \le 2\text{ px}$ dots without re-thinning.
- `PIEDFRONT` normalizes the DEM scarp-break by local background slope ($\|\nabla\,\text{det\_elev\_slope}\| / (\text{det\_elev\_slope} + 2^\circ)$, Band 19 × Band 12 coherence), gates by the piedmont elevation + basement-depth + isostatic-gravity-slope envelope $W_{\text{pied}}$ (Bands 12, 15, 5), refills **4,000 piedmont `H19-5` holes** via exact marginal expected-DTI greedy, and places **13,179 (35%) / 15,062 (40%) / 16,944 (45%) far dots** (`78.7%` in the piedmont) strictly $>3.0\text{ px}$ off `H19-5` and $>3.0\text{ px}$ off all 5 prior off-skeleton lanes' far sets.
- **Pooled `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives, 8 folds, 1,000 paired 20 km cluster draws):**
  - **`PIEDFRONT f35Ptop`: `0.006425 [0.005375, 0.007479]`** — **all-time highest non-collar `HOLDOUT-DTI` in the repository**, beating `R0` (`0.004006`) by **`+0.002418 [+0.001538, +0.003255]` (`+60.4%`)**, beating `BREAKLINE f45` (`0.004861`) by **`+0.001564 [+0.000471, +0.002607]` (`+32.2%`)**, beating `STRAINBREAK f60` (`0.005487`) by `+0.000938 [-0.000322, +0.002239]`, and exceeding `RELIEF p10` (`0.006045`) in point estimate across all three doses (`f35Ptop` `0.006425`, `f40Ptop` `0.006402`, `f45Ptop` `0.006137`).
  - **Leakage canaries:** max symmetric AUC = `0.639112` ($\le 0.90$ PASS).
  - **Local registry uniqueness (`REGISTRY-MEASUREMENT`, 29 local rasters):** pre-placement surface worst `|ρ| = 0.127084`, top-37,654 3-px overlap `0.434907`; final dots `f35Ptop` worst 3-px forward overlap **`0.649997` (`h19_5.tif`, $\le 0.70$ PASS)**, worst `|φ| = 0.585871` ($\le 0.90$ PASS).
  - **Why verdict is still `negative` (NOT CLEARED FOR A WEEKLY SLOT):** (1) Paired 95% CI against `RELIEF p10` (`[-0.000257, +0.001066]`) includes zero and off-catalogue `SGMC` bedrock fault proxy (`0.059993`) is below `R0` (`0.096060`), and (2) the dense public witness (`17GEMSDOE E-proba`, positive on 100% of the footprint) triggers the literal $>70\%$ forward-overlap rule (`evidence/piedfront_public_registry_witness17.json`).

---

## Prior (2026-10-25, SPRINGALIGN): UNIQUE TIF GENERATED

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

## Candidate Geological Hypotheses (Ranked — Session 2026-10-24 `PIEDFRONT` + Prior Inventory)

### Session 2026-10-24 Pre-Registered Untried Hypotheses ([`docs/HYPOTHESES_20261024_PIEDFRONT.md`](docs/HYPOTHESES_20261024_PIEDFRONT.md))

| Rank | Hypothesis | Target Signature | Layer(s) Involved | Missing Fault Rationale | Expected DTI Rank / Cost | Data Source & Official Link |
|---|---|---|---|---|---|---|
| **1** | **`PIEDFRONT` (Built — Holdout Best `0.006425`)** | Relative scarp-break $\|\nabla\,\text{det\_elev\_slope}\| / (\text{det\_elev\_slope}+2^\circ)$ × `coh(det_elev)` × piedmont/cover gravity-slope envelope $W_{\text{pied}}$, plus 4,000 piedmont `H19-5` hole refills | Band 12 (`det_elev`), Band 19 (`det_elev_slope`), Band 5 (`iso_grav_anom_slope`), Band 15 (`depth_to_base_surf`) | Unnormalized `BREAKLINE` placed 74.8% of far dots in steep mountain range interiors; relative break + piedmont gravity/cover gating concentrates 78.7% of far dots in the piedmont range-front transition where active Quaternary normal faults and blind geothermal step-overs sit. | **Rank 1 (Built: `0.006425`)** / Low (~35 lines in-stack) | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [GDR #1391](https://gdr.openei.org/submissions/1391) |
| **2** | **`GRAVTILT` (Untried)** | Isostatic gravity tilt-angle zero-crossing $\cos(\arctan(\text{Band 11}/\text{Band 5})) \times \text{pct\_rank}(\text{Band 5}) \times \text{coh}(\text{Band 13})$ | Band 11 (`iso_grav_anom`), Band 5 (`iso_grav_anom_slope`), Band 13 (`gravity`) | AGC-like ratio of residual gravity to horizontal gradient places $\theta_g = 0$ directly over buried basement fault steps at all depths, even where `GRAVCrest`'s raw horizontal-gradient inflection was washed out by regional basin gradients. | **Rank 2** / Low (~30 lines in-stack) | [USGS GeoDAWN Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [GDR #1391](https://gdr.openei.org/submissions/1391) |
| **3** | **`GEOTHERM-CHALC` (Untried)** | Chemical geothermometer disequilibrium $\Delta T = \max(T_{\text{quartz}}, T_{\text{chalc}}, T_{\text{cat}}) - T_{\text{surface}}$ coupled with `cond_surf` (Band 17) & `geod_dilaterate` (Band 8) | Pinned GDR `#1391` well/spring geochemistry (`na_ppm`, `k_ppm`, `ca_ppm`, `sio2_ppm`, `temp_c`) + Bands 17, 8 | Cold/warm mixed springs with high silica/Na-K-Ca geothermometer disequilibrium mark deep fault upflow conduits missed by `SPRINGALIGN`'s raw $T \ge 40^\circ\text{C}$ filter. | **Rank 3** / Medium (~65 lines, pinned CSV + stack) | [GDR / INGENIOUS #1391](https://gdr.openei.org/submissions/1391) |
| **4** | **`MAGTILT-CONTACT` (Untried)** | Magnetic tilt-derivative steep gradient $\|\nabla\arctan(\text{Band 9}/\text{Band 3})\|$ gated by `rtp` coherence (Band 2) and low `tc` (Band 6) | Band 2 (`rtp`), Band 3 (` mag_hgrad`), Band 6 (`tc`), Band 9 (`mag_1vd`) | Equalizes shallow volcanic and deep sub-alluvial intrabasinal horst/relay fault contacts where `ANASIG`'s unnormalized amplitude was dominated by shallow basaltic lavas. | **Rank 4** / Low–Medium (~45 lines in-stack) | [USGS GeoDAWN Aeromagnetics](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |

### Prior Hypothesis Inventory ([`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) · [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md))

| Rank | Hypothesis | Target Signature | Layer(s) Involved | Missing Fault Rationale | Expected DTI Rank / Cost | Data Source & Official Link |
|---|---|---|---|---|---|---|
| **1** | **BREAKLINE (Built)** | Structure-tensor coherence on detrended slope breaks | Band 19 (`det_elev_slope`) & Band 12 (`det_elev`) | Quaternary scarps in alluvium lack magnetic/gravity contrast but express as sharp linear breaks on DEMs. | **Top (Rank 1)** / Low (in-stack) | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) |
| **2** | **GAMMA-CREST** | Signed gravity horizontal gradient zero-crossing & asymmetric crest | Band 18 (`iso_grav_anom_hg`, signed) & Band 5 (`iso_grav_anom_slope`) | Basinward density edge of listric/dipping normal faults buried under thick hanging-wall alluvium. | **Rank 2** / Low (in-stack) | [USGS GeoDAWN Catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |
| **3** | **DILATATIONAL-STEPOVER** | Positive dilatational strain rate on structural relay bends | Bands 8, 7, 4 (geodetic strain) & Band 19 (DEM breaks) | Geothermal fluid permeability localizes in extensional stepovers and pull-apart jogs between overlapping fault strands. | **Rank 3** / Medium (in-stack) | [UNR Nevada Geodetic Lab](http://geodesy.unr.edu/) |
| **4** | **HYDROTHERMAL-ALTERATION** | K/Th radiometric ratio gradients & magnetic destruction | External GeoDAWN Radiometrics (`geodawn_rad_u8.tif`) & Band 14 (TMI) | Hydrothermal alteration halos trace active fluid-transmitting fault corridors lacking surface scarps. | **Rank 4** / Medium (pinned cache) | [USGS GeoDAWN Radiometrics](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) |
| **5** | **SHORELINE-FILTERED SCARP** | Elevation-band contour-parallel suppressed breaklines | Bands 19, 12 + Lake Lahontan highstand masks (~1330 m AMSL) | Removes wave-cut shoreline terraces (the dominant non-tectonic false-positive mimic in the Great Basin). | **Rank 5** / Medium (requires NBMG shoreline grid) | [Nevada Bureau of Mines & Geology](https://data.nbmg.unr.edu/) |


Detailed documentation: [`docs/HYPOTHESES.html`](docs/HYPOTHESES.html) · [`docs/HYPOTHESES.md`](docs/HYPOTHESES.md).

---

## Core Values & Decision Framework

### Maximize P(Win)
&ldquo;Maximize the Probability of Winning&rdquo;: our decision-making framework. In every decision, we weigh trade-offs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside emotions and make tough decisions in order to maximize P(Win). &ldquo;Maximize P(Win)&rdquo; frees us from constraints and clarifies that we must put Arena first.

### Own the Outcome
We own results end to end &mdash; not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

---

## Reproducible Validation & Verification Pipeline

```bash
# 1. Restore all SHA-256 pinned inputs into .cache/gems_inputs/
python3 scripts/restore_inputs.py

# 2. Run the automated test suite in the pinned environment
.venv/bin/python -m pytest -q

# 3. Verify pinned data manifests and hashes
.venv/bin/python scripts/verify_manifest.py

# 4. Run automated gate inspection on all served downloads
.venv/bin/python scripts/check_site.py

# 5. Format validation on a candidate (format pass is not submission clearance)
.venv/bin/python scripts/validate_submission.py --candidate docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif
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
