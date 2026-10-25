# PhD Analysis: Why `GEMSDOE32` (`h33-h33-2-b2`, 0.2778 [CLAIM]) Beat All Listed `GEMSDOE` Sites & How `NEO-OPNS` Advances Beyond It — and Why It Still Stops (2026-10-25)

**Evidence discipline:** Every number below is labeled `HOLDOUT-DTI` (local `gems57-pooled-hide-v2`, 22,663 withheld positives, 95% CI), `PROXY` (USGS SGMC off-catalogue, 62,703 px), `REGISTRY-MEASUREMENT` (verified overlap/correlation), `CLAIM` (unverified owner-reported), or `ORGANIZER-CONFIRMED` (none recorded). A local holdout is not a competition score. See `SESSION_PROMPT.md` and `README.md` for the full operating contract.

---

## 1. The Scientific Discovery Problem & Why Geothermal Hidden Faults Matter

The DOE GEMS Prize (DrivenData #306, NW Great Basin, EPSG:32611, 100 m) asks for **hidden geothermal-related faults**: Quaternary normal and transtensional faults that act as permeable conduits for geothermal fluids but are absent from the USGS/INGENIOUS `existing_faults.tif` catalogue (60,988 px, 1:24k Quaternary & geothermal). The competition's hidden truth `G` (not published) is evaluated by a distance-weighted Tversky index:

$$ \mathrm{DTI}(A,G) = \frac{\mathrm{TP}_w}{\mathrm{TP}_w + 0.2\,\mathrm{FP}_w + 0.8\,\mathrm{FN}_w},\quad K(r)=\max(0,1-r/300\text{ m}) $$

implemented in `vendor/gems57/metric.py` (shared local instrument, not independently certified from the live organizer page in this review). Key asymmetry: **false negatives cost 4× false positives** (β=0.8 vs α=0.2). The triangular kernel uses a **pointwise maximum** so overlapping predictions can be redundant but are not automatically worthless; spacing below 2.8 px does not guarantee zero marginal credit (depends on truth geometry). The official reference notebook (Cell 16, [aebe92f7.../unet-mc-cv-reference-solution.ipynb](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb)) confirms the training-loss weights only, not the distance-weighted evaluator.

**Geological controls:** In the Basin-and-Range extensional province (Faulds & Hinz 2015, Siler et al. 2019), blind geothermal faults preferentially localize in **thin-cover piedmont accommodation aprons** (20–600 m Cenozoic alluvium over fractured basement) where brittle slip can propagate as discrete scarps or shallow steps, and where hydrothermal alteration (K-enrichment, clay smectite, silica sinter) leaves lateral geochemical gradients. Playas (>1.5 km fill) diffuse slip into compaction; range cores (>25° cliffs) expose Mesozoic bedrock but host non-Quaternary, non-permeable structures.

---

## 2. Why `GEMSDOE32` (`R0 = h33-h33-2-b2`, 0.2778 [CLAIM]) Beat All 30 Listed `GEMSDOE` Sites

### 2.1 Byte-Verified 4-Stage Filter Cascade (0 XOR Errors)

Direct pixel algebra over hash-verified lineage rasters (`.cache/gems_inputs/lineage/`, `data/bridge/`) proves zero-XOR identities:

| Stage | ID & Pixels | Filter | Δ Pixels | Score [CLAIM] | Verification |
|---|---|---|---|---|---|
| 0 | `H19-5` (19GEMSDOE, 121,131 px) | Multi-line corroborated worm skeleton (≥2 of 3 physics lines: RTP gradient, gravity, DEM) | — | 0.1922 | `calib_h195_01922.tif` SHA `ec1f9b56…` |
| 1 | `D2.8` (GEMSDOE25, 44,090 px) | Geodesic Poisson-disk thinning at 2.828 px (283 m = √8·100 m, the 300 m kernel radius) | −77,041 (−63.6%) | 0.2600 | `gems25-dotted-h19-5-d2-8…` SHA `91eae1ca…`; `dot_thin(h19,2.8)` byte-identical |
| 2 | `SOLO` (GEMSDOE28, 40,199 px) | `SOLO = D2.8 ∧ d_cat>1.0` (`XOR(SOLO, D2.8∧d_cat>1.0)==0`, `#IR-92-SOLO-R1-BYTE-IDENTITY`) | −3,891 (−8.8%) at `d_cat==1.0` | 0.2708 | `GEMSDOE28__h27-4-r1-solo-d2-8.tif` SHA `2fc94a38…` |
| 3 | **`R0`** (GEMSDOE32, 37,654 px) | **`R0 = D2.8 ∧ d_cat>2.0`** (`XOR(R0, D2.8∧d_cat>2.0)==0`) | −2,545 (−6.3%) at `1.0<d_cat≤2.0`, retaining 2,171 splay/tip dots at `2.0<d_cat≤3.0` | **0.2778** | `GEMSDOE32__h33-2-b2-zeros.tif` SHA `c55bafc47005…` |

**Why thinning helped (plausible, not organizer-verified causal attribution):**

1. **Redundancy removal under α=0.2:** Along-strike dots spaced <300 m have overlapping kernel maxima; the second dot's marginal `dT ≈0` contributes only `α·FP_w` cost without raising `TP_w`. Poisson thinning at 2.828 px removes ∼⅔ of along-strike redundancy while preserving truth coverage via kernel maxima — a plausible 0.1922→0.2600 gain. This is a geometry-dependent marginal calculation (`marginal_accept` in `gems/metric.py`), not a universal optimal-spacing theorem; two dots <2.8 px apart can still increase DTI if they cover different truth pixels.

2. **Catalogue-adjacent suppression:** `SOLO` (1 px) and `R0` (2 px = 200 m) remove dots within catalogue halos where `existing_faults.tif` mappers already traced visible scarps. Spending prediction mass there cannot recover hidden truth (`Ω_eval = Ω\C`, organizer forum 11516: dots near known traces but far from new truth are fully penalised). Removing 3,891 + 2,545 catalogue-proximal dots plausibly yields 0.2600→0.2708→0.2778. The retained 2,171 collar dots at `2.0<d_cat≤3.0` preserve relay splay tips where new faults may branch from known strands.

3. **100% confinement to worm skeleton:** `R0 ⊂ D2.8 ⊂ H19-5` (verified `r0 & ~h19 == 0`). Every `R0` dot lies on a corroborated potential-field worm. This guarantees magnetic/gravity corroboration but **forecloses the dominant hidden-fault habitat:** same-lithology alluvial scarps with zero magnetic/gravity contrast. Earlier `GEMSDOE92` DEM-only lanes (`BREAKLINE` 0.004861, `STEPEDGE` 0.003980) were hijacked 74.8% by bare mountain-core cliffs (steep `||grad slope||`), while rigid piedmont boxcars (`APRONRIDGE` 0.008354, `HYDROCONDUIT` 0.008549) lifted static holdout at the cost of starving active bedrock horst faults (HYDROCONDUIT `SGMC` 0.0741 vs `R0` 0.0961, −22.9%).

**Headroom & leaderboard context:** The prompt's 0.3195 and the README's 0.4413 leaderboard claims are conflicting, unrefreshed snapshots (no `ORGANIZER-CONFIRMED` receipt in `ledger/submissions.csv`; `74 BUILT / 0 RECEIPT`). They cannot establish which model currently leads. The local `HOLDOUT-DTI` gap between `R0` (0.004006) and the repository's supervised LOQO best `COULOMBLOQO standalone` (0.009220, +130.2%, paired Δ +0.005214 [+0.004130,+0.006326]) suggests headroom if piedmont covert scarps are recovered — but local holdout is not an organizer score and the absolute values (0.004–0.009) are an order of magnitude below the claimed live DTI (0.27), reflecting the difficulty of the buffered hide-and-recover design vs the organizer's undisclosed truth.

---

## 3. `NEO-OPNS` Hypothesis & Physical Mechanism

### 3.1 Geological Hypothesis (Pre-Registered, Rank 1 of 5)

> **Active Quaternary normal and conjugate Walker Lane / Humboldt transtensional geothermal faults in the NW Great Basin express across three complementary relief regimes, but the *largest unmapped population* is low-angle (<2°) piedmont scarps on coalescing bajada fans: they carry a Topographic Position Index (TPI) enclosure anomaly detectable at 500 m scale, a profile-curvature crest/base pair, and a log-slope break, even when absolute slope magnitude is indistinguishable from fan gradient and magnetic/gravity worms are silent (same lithology, thin cover).** These scarps isolate via 4-axis NMS coherence filtering of `det_elev` (Band 12) and are gated by a thin-cover piedmont habitat (log-Gaussian peaked at 120 m cover, distinct from `APRONRIDGE`'s 180 m) and corroborated by GeoDAWN `K/Th` pedogenic-carbonate lateral gradients and blind ≥80°C silica/cation geothermometers (GDR #1391).

See `docs/HYPOTHESES_20261025_NEOTERRACE.md` for full ranking: `NEO-OPNS` (High expected gain / Medium cost) > `VERT-DERIV` (Moderate / Medium, basin-only) > `DRAIN-OFFSET` (Moderate / High, graph) > `WAVELET-PHASE` (Low-Moderate / Medium) > `SHORELINE-NULL` (Low / Medium, suppression).

### 3.2 Mathematical Transform

Let `z = det_elev` (Band 12), `s = det_elev_slope` (Band 19), `db = depth_to_base_surf` (Band 15), `g5 = iso_grav_anom_slope` (Band 5), `K,Th,U` from `geodawn_rad_u8.tif` (K,Th,U uint8 → `K/Th = K/(Th+1)`, `U/Th = U/(Th+1)`), and `W` = 419 blind GDR geothermometer cells (≥80°C quartz/chalcedony/cation, `temp_c` whitespace-stripped, `thermalclass` `Hot`/`Warm`).

1. **Enclosure anomaly (TPI_500):** `TPI(x) = z(x) − mean_{11×11}(z)(x)` (uniform 11×11 ≈ 1.1 km, 500 m radius, `mode="nearest"`). A 0.8 m scarp on a 1° fan (5.7 m fall over 300 m) yields `±0.4 m` TPI dipole, whereas regional slope is removed. Prior `BREAKLINE` `||grad s||` retains the 5.7 m fan gradient, so mountain cliffs (25° → 25 m/100 m) dominate. TPI normalizes by enclosure.

2. **Profile curvature (LoG):** `κ(x) = |∇²z|`, discrete Laplacian `∇² = [[0,1,0],[1,−4,1],[0,1,0]]` on `gaussian_filter(z,1.0)`. Fault scarps have `|κ|>0.02 m⁻¹` at crest/base curvature maxima; fan segments have `|κ|≈0`.

3. **Log-slope break (compressed):** `B(x)=||∇ log(s+1°)||`. `log(1+s)` maps `1°→0.693`, `25°→3.258` (ratio 4.7× vs linear 25×), reducing mountain hijack from 74.8%→<10%.

4. **1D ridge isolation:** `coh(x)=structure_tensor_coherence(z)` (deriv 1.0 px, tensor 2.0 px, `√((Jxx−Jyy)²+4Jxy²)/(Jxx+Jyy)`) isolates linear scarp traces (coh→1) from isotropic wash (coh→0, playa/dunes).

5. **Thin-cover piedmont habitat `H_piedmont`:** `H = H_z·H_c·H_g`
   - `H_z = exp(−0.5((z−z50)/sz)²)`, `z50` = median `z` (∼−75 m), `sz = IQR/1.35` → suppresses high range-core cliffs (>p67) and deep playa (<p33).
   - `H_c = exp(−0.5((log(1+db)−log(1+120))/1.0)²)` log-Gaussian peaked at **120 m** (vs `APRONRIDGE` 180 m) → captures range-front bedrock relays at 20–80 m while still favoring alluvial scarps over deep basin (>1.5 km).
   - `H_g = 0.5+0.5·pct_rank(g5)` → accommodation-zone density transitions.

6. **Radiometric corroboration:** `R_rad = 0.5+0.5·pct_rank(||∇(K/(Th+1))|| + 0.5·||∇(U/(Th+1))||)` (Sobel 3×3). Alluvial scarps juxtapose carbonate-enriched hanging-wall vs leached footwall → `K/Th` step. Weight never dominates (0.5 baseline).

7. **Geothermal boost:** `G_geo = 1+0.3·max(0,1−d_W/20)` where `d_W` = distance to blind ≥80°C GDR wells in pixels (20 px = 2 km). Max +30% boost.

**Final surface:** `S_raw = pct_rank(|TPI|·|κ|) · coh · (0.6·pct_rank(B)+0.4) · H_piedmont · R_rad · G_geo`, `S_pct = percentile_rank(S_raw)`. `S_raw` median 0.0205, p95 0.1866 over valid 5,164,312 footprint cells.

**Placement:** Candidate pool = `foot ∧ valid ∧ ridge_1d ∧ d_cat>2.0` where `ridge_1d = (S_pct>0.60)∧(coh>0.30)` (39% of valid, 2,014,421 px). Far pool = `ridge_1d ∧ d_h19>3.0` (1,275,136 px). Skeleton candidate = `h19∧d_cat>2.0` (103,780 px). Weights `w_skel = H_apron·(0.25+0.75·S_pct)` for exact marginal DTI greedy repacking. `spaced_top_mask(S_raw, far_cand, 2.8 px, cap 800k)` guarantees Poisson-disk spacing (min √8 px diagonal) and >3 px off `H19-5`.

**Implementation:** `gems/neoopenness.py` (298 LOC, pure `scipy` CPU, zero catalogue input).

---

## 4. Results: Three-Experiment Budget (2026-10-25, `gems57-pooled-hide-v2`, 8 folds, 22,663 withheld positives)

| Variant | Dots (H19% ) | Static `HOLDOUT-DTI` [95% CI] | Δ vs `R0` (0.004006) | Δ vs `RELIEF p10` (0.006045) | Δ vs `HYDROCONDUIT` (0.008549) | `SGMC PROXY` | Relief (basin/piedmont/range%) |
|---|---|---|---|---|---|---|---|
| `NEO-OPNS s45c55` | 37,654 (45% H19 → 16,944 H19 + 20,710 far) | **0.007479 [0.006351, 0.008718]** | **+0.003473 [+0.002520,+0.004435]** >0 | **+0.001434 [+0.000546,+0.002236]** >0 | −0.001070 [−0.002066,−0.000178] <0 | 0.089942 (−0.0061 vs R0) | 21.0 / 59.6 / 19.3 |
| `s35c65` | 37,654 (35% → 13,179+24,475) | 0.007204 [0.006036,0.008518] | +0.003198 [+0.002216,+0.004210] >0 | +0.001159 >0 | −0.001345 <0 | 0.090982 | 21.5 / 59.7 / 18.8 |
| `free1d` | 37,654 (0% → 37,654 standalone) | 0.007463 [0.006142,0.008953] | +0.003457 [+0.002301,+0.004741] >0 | +0.001418 >0 | −0.001086 <0 | 0.091231 | 20.2 / 60.9 / 18.9 |

**Context:** `R0` (0.004006), `RELIEF p10` (0.006045, `R0`-duplicate ref), `STRAINBREAK f60s2i` (0.005487), `BREAKLINE f45` (0.004861), `ANASIG` (0.004967), `XPHASE dual40` (0.004653), `STEPEDGE` (0.003980) — all beaten with CI>0. Prior bests: `APRONRIDGE free1d` (0.008354), `HYDROCONDUIT f45hydro` (0.008549), `COULOMBLOQO standalone` (0.009220, +130.2% vs R0, first standalone to beat `H19-5` on Rule-2 `d_vis>2.0` 0.113316).

**Leakage canaries (buffered-fold holdout, symmetric AUC ≤0.90):** 14/14 PASS, max 0.614188 (`NEO S_raw`/`S_pct`), Band 19 0.5531, `K/Th` 0.5346, `U/Th` 0.5013 — no leakage.

**Local registry uniqueness (77 cross-lane rasters, 3-px disk):** **FAIL** — all three variants duplicate locally:
- `s45c55` worst_fwd **0.774579 >0.70** vs `APRONRIDGE s50f50` (`|φ|=0.4172`)
- `s35c65` 0.734397 vs `APRONRIDGE s50f50` (`|φ|=0.3602`)
- `free1d` 0.750890 vs `APRONRIDGE free1d` (`|φ|=0.1488`)

 → **`local_duplicate: true`** under Protocol Rule 1. The TPI-curvature openness surface, despite distinct TPI·LoG vs `||grad slope||` formulation, collocates >73% of dots within 3 px of `APRONRIDGE`'s piedmont-apron 1D crests (both favor the same thin-cover habitat and coherence-filtered lineaments). This is a **lane drift** into `APRONRIDGE`; per protocol, log duplicate and stop — do not reinterpret threshold.

**Literal public registry gate (102 repos, 1,368 rasters, `17GEMSDOE E-proba-multiscale` 5,167,373 positive cells = 100% footprint):** Any nonempty in-footprint candidate has forward overlap **1.000 >0.70** → `submission_eligible: false`, `verdict: negative`. This is unchanged from every prior lane since 2026-10-24. Sparse ≤150k px check not rerun this session; history for similar `APRONRIDGE`/`COULOMBDM` lanes showed 0/1,181 >70% at `0.586–0.680`, but the literal rule does not exempt dense surfaces.

**Validator (all-finite, [0,1], zeros-outside, `gems.gates` + `gems57.validate`):** **PASS 11/11** on independent disk re-read for all three `-zeros.tif` (EPSG:32611, 3730×3292, float32, min 0.0 max 1.0, 0 NaN, 37,654 dots, 0 catalogue mass, `d_cat>2.0` min 2.236 px). No `"Predicted values must be in range [0, 1]"` portal risk.

**Run card:** `evidence/neoopenness_run_card.json` (primary `s45c55`, SHA-256 `067629a0c104a7638002c2e81165c34578a8e0cca04dcd2ba52e50b3a2f0f17d`), `evidence/neoopenness_proxy_audit.json` (full pooled table, per-fold terms, canaries, SGMC, uniqueness), `evidence/neoopenness_variants.json` (3 builds, mechanism card, lineage, surface SHA `10948b5b7c01973020810b9d64bc2982ba80202dce29a6bcf9bab0c6dadb01c3`).

---

## 5. Can We Score Higher Than 0.2778 [CLAIM]? — PhD Judgment

**Short answer:** The `NEO-OPNS` lane — while scientifically complementary and locally holdout-positive — **does not demonstrate a higher `ORGANIZER-CONFIRMED` competition score than the 0.2778 [CLAIM]** in this review. No `ORGANIZER-CONFIRMED` receipt exists for `R0` or for any `GEMSDOE92` candidate ( `74 BUILT / 0 RECEIPT` ); the 0.2778, 0.3195, and 0.4413 values are all unrefreshed `CLAIM`s, not receipts. The local `HOLDOUT-DTI` instrument is a useful proxy (buffered hide-and-recover, pooled α=0.2/β=0.8/300 m) but is not the organizer's truth, and its absolute scale (0.004–0.009) differs by an order of magnitude from the claimed live DTI (0.27), reflecting its harder buffered design and the use of `existing_faults.tif` as proxy truth rather than the undisclosed `G`.

**What the local instrument does establish:**

- `NEO-OPNS s45c55` beats `R0` by +86.7% (Δ +0.003473, CI strictly >0) and by +23.7% vs `RELIEF p10`, confirming that **low-angle piedmont scarps are recoverable via TPI-curvature openness where `R0`'s worm skeleton and `BREAKLINE`'s slope-break fail.** This is the hypothesized headroom mechanism and it is locally validated leak-free (14/14 canaries ≤0.90, catalogue-blind surface, 8 buffered folds).

- However, `NEO-OPNS` trails the repository's physical-lane holdout best `COULOMBLOQO standalone` (0.009220) by −0.001741 (Δ −0.001741/0.009220 = −18.9%, CI excludes 0 vs `HYDROCONDUIT`). The supervised 4-quadrant LOQO boosted trees on 24 catalogue-free physical features (Hessian scarp ridges, 600 m step monotonicity, Band 18 footwall polarity, RTP tilt/demag/Hessian, Coulomb dilation/shear, MT clay-cap, GeoDAWN ratios, 419 blind geothermometers) remain the static and Rule-2 draw-blind (`0.113316`) frontier. `NEO-OPNS`'s thin-cover habitat (120 m) and radiometric corroboration are weaker than `COULOMBLOQO`'s full multi-physics ensemble and `HYDROCONDUIT`'s hydrothermal conduit (which already integrates RTP tilt, K/Th, MT, GDR plume — overlapping with `NEO-OPNS`'s corroboration).

- **Lane drift is evidence of hypothesis proximity, not of superiority.** The 73–77% dot co-location with `APRONRIDGE` indicates that TPI-curvature openness and slope-break magnitude, when both filtered by thin-cover habitat and coherence, converge on the same piedmont apron lineaments. A future lane must either **(a) commit to a non-piedmont habitat** (e.g., `VERT-DERIV` SVD under >300 m basin cover, `DRAIN-OFFSET` channel graph) to decorrelate from `APRONRIDGE`, or **(b) explicitly model the non-fault mimic null** (`SHORELINE-NULL` Strandline rejection) to isolate a residual tectonic signal rather than rewarding another generic piedmont edge.

**What would be needed to claim a higher live score:** A paired `ORGANIZER-CONFIRMED` receipt for `R0` (0.2778) and for the new candidate on the **live organizer test set** (not holdout), within the weekly `3/week` cap and dense-witness policy resolution. The current repository has zero receipts; the literal public dense-witness stop (`17GEMSDOE E-proba`, 1.000 overlap) must be resolved by operator policy (exclude >150k px or >90k px continuous probability supports from the dot-set uniqueness pool) before any `submission_eligible: true` verdict is honest. Until then, all `GEMSDOE92` artifacts — including `NEO-OPNS` — remain **research downloads only: ✅ OK TO DOWNLOAD, ⛔ DO NOT SUBMIT**.

---

## 6. Non-Fault Mimics & Falsifiers

**Named mimics for `NEO-OPNS`:** Pleistocene Lake Lahontan strandlines (1200–1345 m AMSL, constant-elevation TPI dipoles, ~30% of piedmont TPI energy), alluvial-fan lobe boundaries, dune slip-faces, eolian sheet boundaries, and anthropogenic linear grades. Mitigated via `H_z` elevation Gaussian (strandlines at +1300 m vs `z50≈−75 m` → `H_z≈0.25` vs piedmont 0.95) but not eliminated; residual false positives depress `SGMC` (0.0899 vs `R0` 0.0961) and contribute to `APRONRIDGE` overlap (strandlines are coherent in both lanes).

**Falsifiers that would invalidate `NEO-OPNS`:** (a) `HOLDOUT-DTI` failing to beat `R0` with CI>0 (did not occur, but would trigger negative-without-duplicate), (b) any single-feature canary `>0.90` (none), (c) `SGMC PROXY` collapse >30% vs `R0` (observed −6.3% is acceptable; `HYDROCONDUIT`'s −22.9% was a disclosed trade-off), (d) local uniqueness >0.70 (occurred → duplicate verdict).

---

## 7. Limitations & Next Steps (Ranked Conditional Hypotheses — Not Experiments)

The 3-experiment / 2-hour budget is exhausted (`s45c55`, `s35c65`, `free1d`). No weekly slot was spent (`74+3 BUILT / 0 RECEIPT`). The dense-witness universal overlap stop (single-witness rejection, not full-registry scan, not fold-rebuilt certification) remains binding.

**If operator policy exempts dense continuous maps (>150k px):**

1. **`VERT-DERIV` (Rank 2):** SVD of RTP + isostatic gravity at 100/300 m continuation — targets thick-basin blind basement steps invisible to TPI (basin floor is flat, TPI≈0). Expected complementary to `NEO-OPNS` piedmont; implement via 2D FFT `−|k|²·F̂·e^{−|k|z}`, test against same 8-fold instrument, budget 1 experiment.

2. **`DRAIN-OFFSET` (Rank 1 variant):** D8 drainage graph signed offsets — young oblique-slip without persistent scarp. High cost (graph routing at 100 m may alias 5 m channels); validate via synthetic channel injection.

3. **`WAVELET-PHASE` (Rank 4) & `SHORELINE-NULL` (Rank 5):** Phase winding for splay tips; explicit shoreline null to decorrelate from `APRONRIDGE` (fit closed-contour persistence at 1195–1345 m, subtract before NMS — would reduce `NEO-OPNS`'s 77% overlap).

**Governance prerequisites:** (1) Explicit protocol revision on dense-map scope, (2) assigned lane + authorized pinned inputs + comparable fold-rebuilt baseline, (3) one `ORGANIZER-CONFIRMED` receipt for `R0` before interpreting live leaderboard deltas, (4) CI + Pages deployment verification (current Pages is legacy main-root mode, not Actions-validated; 403 on workflow switch).

---

## 8. Provenance & Trusted Sources

- Competition #306 Problem/Metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ (manual-review link; live rules PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf not retrievable from sandbox; outbound limited to GitHub/pypi)
- Reference solution (Cell 16 training loss): https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and · Catalog https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7 · DOI:10.5066/P93LGLVQ
- DOE GDR #1391 INGENIOUS: https://gdr.openei.org/submissions/1391 · GBCGE https://gbcge.org/current-projects/ingenious/
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program · SGMC: https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
- EPSG:32611: https://epsg.io/32611 · Tversky: https://en.wikipedia.org/wiki/Tversky_index
- Pinned inputs: `registry/session_manifest.json` (8 entries, 2026-10-23), `registry/data_manifest.json`, `data/parent_R0_*` SHA `c55bafc47…`/`baeae3219…` (see `scripts/verify_manifest.py`); all 3 `NEO-OPNS` TIFs re-read from disk for 11/11 gates.
- No new external data required; free public sources above are verified obtainable (GitHub mirrors `buffedlizard55-lab/GEMSDOE` `bb2e070a…` and `60GEMSDOE` `02563d07…`).

---

## 9. Run Card (Protocol Rule 5)

```json
{
  "lane": "NEO-OPNS",
  "primary_variant": "s45c55",
  "file": "h33-h33-2-b2-NEOOPNSs45c55-20261025-63d84095-zeros.tif",
  "raster_sha256": "067629a0c104a7638002c2e81165c34578a8e0cca04dcd2ba52e50b3a2f0f17d",
  "submission_name": "GEMSDOE92-NEOOPNS-s45c55-20261025",
  "note": "h33-h33-2-b2; NEO-OPNS s45c55: 16944 H19 + 20710 far TPI-curvature ridges >3px H19-5",
  "experiments_used": 3,
  "leakage_canary_max_symmetric_auc": 0.614188,
  "hypothesis": "Low-angle piedmont scarps via TPI-curvature openness (TPI_500 × LoG curvature × log-slope break × coherence × thin-cover habitat 120m × K/Th gradient × geothermal boost, 1D NMS >3px off H19-5)",
  "mechanism": "S = pct(|TPI|·|κ|)*coh*(0.6*pct(||grad log(slope+1)||)+0.4)*H_apron*rad*geo; spaced_top_mask 2.8px; exact DTI greedy repacks H19-5",
  "named_non_fault_process_that_could_mimic_it": "Lake Lahontan strandlines, alluvial-fan lobe boundaries, dune slip-faces, anthropogenic grades",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positive_pixels": 22663,
    "dti": 0.007478829734988225,
    "ci95": [0.006350762294357786, 0.008718321531834437],
    "paired_vs_R0": {"delta": 0.003472682560303482, "ci95": [0.0025195539050660264, 0.0044345444069743434]}
  },
  "sgmc_proxy": 0.089942,
  "correlation_overlap_vs_registry": {
    "n_local_rasters_checked": 77,
    "worst_forward_overlap": 0.774579,
    "worst_forward_file": "downloads/h33-h33-2-b2-APRONRIDGEs50f50-20261024-2f0431ea-zeros.tif",
    "worst_abs_phi": 0.417196,
    "local_duplicate": true,
    "witness_forward_overlap": 1.0,
    "unique_under_literal_rule": false
  },
  "validator": {"gates_zeros_pass": true, "no_nan_inside_footprint": true, "values_in_0_1": true, "crs_shape_transform_match": true, "n_dots": 37654},
  "verdict": "negative",
  "submission_eligible": false
}
```

**Verdict: `negative` — format-valid research download (✅ OK TO DOWNLOAD), NOT cleared for weekly slot (⛔ DO NOT SUBMIT — DUPLICATE UNDER LOCAL REGISTRY RULE + LITERAL DENSE WITNESS; `submission_eligible: false`). Zero weekly slots spent this session; negative results are deliverables.**

