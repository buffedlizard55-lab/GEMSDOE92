# RADSCARP 2026-10-25 — Fused Scarp + Radiometric Alteration Lane: Design, Instruments, and Verdict

## Question: Why did h33-h33-2-b2 obtain CLAIM 0.2778, and can a new candidate exceed it?

### Evidence class for the 0.2778 number

The association `h33-h33-2-b2 → 0.2778` is listed on [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) as **CLAIM 0.2778** (no organizer receipt in `ledger/submissions.csv`; `registry/parents/R0.json` has `receipt: null`). The prompt cites conflicting snapshots 0.3195 and 0.4413 for the overall GEMSDOE leaderboard high; a public read of the [official DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) on 2026-10-24 showed 0.4413 at #1 (**LEADERBOARD-SNAPSHOT**, not a receipt for GEMSDOE32 or GEMSDOE92). All three numbers are owner-reported or public-snapshot claims, never written here as ORGANIZER-CONFIRMED scores.

That distinction matters: only a submission-page receipt (file SHA, score, date copied from the portal) is an organizer-confirmed score. Holdout instruments, projections, and model Monte Carlos are not scores.

### Mechanistic explanation for 0.2778 (PhD-level, plausible not causal proof)

**Competition truth:** The private test set is expert-mapped new faults in the GeoDAWN region (NW NV) that are *not* in the public USGS/INGENIOUS catalogue (60,988 px at 100 m). Experts label on high-resolution topography (1 m LiDAR / 10 m DEM) — primarily subtle Quaternary normal-fault scarps, dilatational stepovers, and geothermal-conduit permeability zones ([problem description p.967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)). The public catalogue is Quaternary faults from aerial-photo mapping of range-bounding scarps on older imagery — incomplete and potentially inaccurate.

**Metric:** Distance-weighted Tversky index with triangular 300 m kernel:
`DTI = T / (0.2·(T+S-M) + 0.8·|G|)` ([metric definition](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric), [Tversky index](https://en.wikipedia.org/wiki/Tversky_index), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)).
`T` = kernel-weighted true positives (coverage of truth by prediction mass), `S` = emitted mass Σ p, `M` = self-credit Σ max_g k(g,p), `|G|` = truth size, α=0.2 FP weight, β=0.8 FN weight. Every unit of prediction pays 0.2 in denominator; it must earn >0.2·DTI in `T` to raise the score. Spacing within the 3 px kernel trades off: nearby pixels share `T` coverage but each pays full `S`.

**Why dotted → SOLO → R0/B2 steps helped:**

1. **D1.5 → D2.8 Poisson thinning (1.5 → 2.8 px nearest-neighbor floor):** The H19-5 worm support is a thick, multi-pixel-wide ridge from potential-field lineaments (magnetic/gravity worms detect deep lithologic density/susceptibility steps). Two adjacent ridge pixels cover the same truth pixel under the 300 m kernel (max-pooled `T`), but both contribute to `S` and `FP_w`. Thinning at 2.8 px (the R0 lineage's `sqrt(8)` diagonal floor) eliminated kernel-shadowed redundancy, raising credit-per-dot from ~0.04 to ~0.06 and lifting DTI from 0.1922 (power-law budget) to 0.2600 (dotted-D2.8, 44k → 40k dots) on the group's live receipt.

2. **SOLO (0.2708):** Removed isolated low-gain dots (sub-buffer) and dots within 1 px of mapped faults. Because organizers mask known faults pixel-exactly (forum 11516: known-fault predictions earn zero `T` but pay full `S`/`FP_w`), pruning near-catalogue mass directly cut `FP_w`.

3. **B2 / R0 flank prune 2.0 px (0.2778):** Enforced strict `d_cat > 2.0 px` (200 m) clearance from the USGS/INGENIOUS catalogue, deleting 2,171 parent dots within 2 px of known faults. Any prediction on or adjacent to a mapped fault is guaranteed `FP_w` under the pixel-exact mask; removing those 5.8% of dots moved the file toward the marginal `k > 0.2·DTI ≈ 0.055` break-even bar. Fixed budget at 37,654 dots.

**Why 0.2778 is an asymptotic ceiling vs 0.4413:**

- **Target ground truth:** Expert-mapped new faults are *missing* from the catalogue because they lack deep basement contrast: Quaternary alluvium-on-alluvium offsets, <20 m throw scarps in basin fill, and shallow geothermal fracture networks. Potential-field worms (H19-5) only detect lithologic-scale density/magnetic steps; they systematically miss exactly those faults. No amount of thinning a worm skeleton can place dots where the skeleton has no support — it only optimizes precision within the skeleton's coverage.

- **How top public boards reach 0.44:** Inferred fusion (from leaderboard method notes and GBCGE INGENIOUS disclosures):
  1. High-confidence skeleton core (~20k dots) for basement-offset range-front faults.
  2. High-res DEM scarp-break detector (structure-tensor coherence × slope-gradient, as in BREAKLINE) for alluvium scarps.
  3. Dilatational stepover / pull-apart geometry (geodetic dilatation × relay-bend detectors) for geothermal vent clusters.
  4. Radiometric alteration halos (K/Th from GeoDAWN gamma survey, DOI [P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)) for hydrothermal fluid conduits.
  5. Poisson-disk spacing discipline across all components.

R0/B2 executed only (1) with perfect spacing and catalogue clearance — the first-order gain. The remaining 0.16 gap to 0.44 is recall on faults with no worm support, requiring independent DEM/radiometric/structural detectors.

---

## 2. RADSCARP Lane Built This Session

**Lane paragraph (protocol rule 1):** Fuse a linear DEM slope-break detector with a linear radiometric alteration edge detector as `S = L × R`, where `L = pct_rank(||∇ det_elev_slope||) × coherence(det_elev)` and `R = pct_rank(||∇(K/Th)||) × coherence(K/Th)` (K/Th ratio from GeoDAWN airborne gamma, Bands 1–2 uint8). Place 33–45% of the fixed 37,654-dot budget on the strongest fused `S` ridges >3 px off the entire H19-5 skeleton and >2 px off the catalogue, under 2.8 px spacing; keep the remaining skeleton dots via exact expected-DTI greedy under `w = 0.30 + 0.70·S_pct` on H19-5 support. Named non-fault mimics: silicified volcanic flow margins, playa evaporite terraces, and road/berm corridors that produce co-located breaks without Quaternary faulting.

**Design, screen and ranking:** `docs/HYPOTHESES_20261025_RADSCARP.md` — five lanes ranked pre-build; RADSCARP Rank 1 (expected HOLDOUT-DTI +0.0008 to +0.0020, cost LOW-MEDIUM, free official data: [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)).

Surface (`gems/radscarp.py`, Bands 12/19 + K/Th ratio):
```
R_rat = K / max(Th,1)   (uint8 → float32, 0.5–99.5% clipped)
L_raw = pct_rank(||grad Band19||) × coherence(Band12; σd=1, σt=2)
R_raw = pct_rank(||grad R_rat||) × coherence(R_rat; σd=1, σt=2)
S_raw = L_raw × R_raw
S_pct = pct_rank(S_raw)
```
All ranks over valid footprint (1001-knot). No catalogue read.

**KEEP:** exact marginal expected-DTI greedy over R0 only, `w = 0.30 + 0.70·S_pct` on H19-5 support.
**FAR:** `spaced_top_mask` descending `S_raw`, strict <2.8 px floor, over `footprint & valid topo & d_cat>2 & d_H19>3 & ~R0` (pool 3,974,627 px; scan cap top-400k by `S_raw`). Doses f33/f38/f45 = 12,426 / 14,309 / 16,944 far dots; each file exactly 37,654 unit dots; builders re-gate every file (count, `d_cat>2`, zero catalogue mass, `d_H19>3`, reopened hashes). By construction whole-file forward overlap vs R0 equals kept fraction (67.0/62.0/55.0%).

### Candidate geological hypotheses (ranked, pre-build)

| Rank | Hypothesis | Target Signature | Layer(s) | Missing-Fault Rationale | Expected DTI Gain / Cost | Distinct vs Prior | Free Source |
|------|------------|----------------|----------|------------------------|--------------------------|-------------------|-------------|
| **1** | **RADSCARP (BUILT)** | Co-located DEM break × K/Th alteration edge | 12/19 + K/Th | Geothermal conduits are both mechanically scarred and geochemically altered; requires both → suppresses shoreline (DEM-only) and lithologic (rad-only) FP | +0.0008–0.0020 / LOW-MED | First radiometric fusion; no prior read K/Th | [GeoDAWN P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) |
| 2 | SPRING-ALIGNED VENT | Spring-pair strike-aligned corridor density | GDR wellspring + det_elev strike | 72% springs >1 km from known faults → blind geothermal fault-hosted vents | +0.0003–0.0015 / MED | Only pairwise point-pattern lane | [GDR #1391](https://gdr.openei.org/submissions/1391) |
| 3 | GRAV-CREST OFFSET | Signed HGM crest + dip-directed basinward offset | 18 HGM signed + 5 slope + 12 aspect | Buried basin-bounding faults under alluvium: density edge basinward of surface trace | +0.0005–0.0015 / LOW | Only signed-band crest geometry | [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) |
| 4 | TILT-CURVATURE HINGE | Magnetic tilt × DEM profile curvature | 6 tilt + 12 curvature | Relay-ramp flexural hinges: distributed curvature, no discrete scarp | +0.0002–0.0010 / LOW | Only hinge (2nd derivative) lane | In-stack |
| 5 | SHORELINE-MASKED BREAKLINE | Elevation-band + contour-parallel suppressed `L` | 12/19 + Lahontan masks | Removes Lahontan terrace FP (dominant Great Basin mimic) | +0.0001–0.0005 / MED | Only FP-suppressed `L` | [NBMG](https://data.nbmg.unr.edu/) |

Full ranking with mimics, screens, costs: `docs/HYPOTHESES_20261025_RADSCARP.md`.

---

## 3. Instrument Results (all labels machine-checked in evidence)

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`: buffered whole-component hide/recover, seeds 20/30, 4 quadrants, 8 spatial folds, 22,663 withheld catalogue px, 158 clusters, 1,000 paired bootstrap draws, α=0.2 β=0.8 R=3 px):

| Arm | HOLDOUT-DTI | Δ vs R0 (paired 95% CI) | Δ vs RELIEF p10 | Δ vs BREAKLINE f45 |
|-----|-------------|------------------------|-----------------|-------------------|
| R0 | 0.004006 [0.003408, 0.004651] | — | — | — |
| RELIEF p10 (holdout-best) | 0.006045 [0.005179, 0.006882] | — | — | — |
| BREAKLINE f45 (prior lane) | 0.004861 [0.003930, 0.005887] | +0.000854 [+0.000300,+0.001423] | −0.001185 | — |
| **RADSCARP f33** | **0.004453 [0.003754, 0.005253]** | **+0.000447 [−0.000054,+0.000961]** | −0.001592 | −0.000408 |
| **RADSCARP f38** | **0.004413 [0.003687, 0.005252]** | **+0.000407 [−0.000037,+0.000895]** | −0.001632 | −0.000448 |
| **RADSCARP f45 (primary)** | **0.004324 [0.003606, 0.005083]** | **+0.000318 [−0.000176,+0.000823]** | **−0.001721 [−0.002418,−0.001002]** | **−0.000536 [−0.001089,−0.000071]** |

- **No dose beats R0 significantly** (f45 CI includes 0). Ranked f33 > f38 > f45 — monotone decline vs BREAKLINE f45, indicating the fused product does not concentrate per-pixel fault probability as strongly as the DEM-only detector on withheld catalogue truth (predominantly mechanical scarps, not alteration-controlled).
- **Leakage canary** (symmetric AUC vs 1-px-dilated withheld truth): max = Breakline `L_pct` 0.6216; Radscarp `S_pct` 0.5646 → REPORT_ONLY_PASS; none near 0.90 stop.
- **SGMC off-catalogue control** (USGS SGMC bedrock faults, 62,703 truth px, `d_cat>3`): R0 0.09606 → BREAKLINE f45 0.12611 (+31.3%) vs RADSCARP f45 0.11575 (+20.5%) vs f33 0.11158. All doses above R0, but RADSCARP below BREAKLINE — some off-catalogue signal but insufficient to offset catalogue loss.
- **Fixed-catalogue diagnostic** (full known, `known=None`): R0 0.006709 → BREAKLINE 0.007746 → RADSCARP f45 0.007039 (tracks holdout ratios for BREAKLINE but not for RADSCARP's fused product).

**Literal uniqueness vs local registry (51 rasters: releases + docs/downloads + lineage, deduped, single-band exact grid):**

| Arm | Worst forward overlap (>0.70 → duplicate) | Worst |ρ| | Duplicate |
|-----|-------------------------------------------|---------|-----------|
| RADSCARP f33 | 0.751 vs BREAKLINE f45 | 0.668 vs R0 | **true** |
| RADSCARP f38 | 0.734 vs BREAKLINE f45 | 0.617 vs R0 | **true** |
| RADSCARP f45 | **0.710 vs BREAKLINE f45** | 0.547 vs R0 | **true** |

All three doses share the DEM `L` component strongly enough that far dots remain within 3 px of prior BREAKLINE far dots; even f45 (most unique) exceeds 70%. A pure radiometric or spring-corridor lane without the DEM component would be needed for <0.70.

**Public-registry binding witness (dense full-footprint raster):** The prior session's hash-verified `17GEMSDOE_E-proba-multiscale` (SHA-256 `ab0a0a62…`, 5,167,373 positives = 100% of footprint; halo coverage 1.0) gives **forward overlap 1.0** for every nonempty in-footprint candidate, including RADSCARP f45 (`evidence/breakline_public_witness.json` reused). Under the brief's literal rule (`>70% within 3 px of any registry raster → duplicate, log and stop, no dense-raster exemption`), **no nonempty submission can pass** while that raster is in scope. This is a REGISTRY-MEASUREMENT stop, not a score. Dense-only diagnostics (even vs ≤150k sparse-dot rasters, 1,125 checked) still show 0.71 worst vs BREAKLINE f45 — not solely a dense-surface artifact.

## 4. Verdict

Pre-registered promotion rule: promote only if HOLDOUT-DTI beats holdout-best (RELIEF p10 0.006045) **and** passes literal uniqueness **and** format gates. RADSCARP f45 passes gates (10/10) and is format-valid for download, but:

- HOLDOUT-DTI 0.004324 does **not** beat R0 significantly (CI includes 0), is significantly **below** BREAKLINE f45 (−0.000536 [−0.001089,−0.000071]) and **below** holdout-best RELIEF p10 (−0.001721 [−0.002418,−0.001002]).
- SGMC off-catalogue control prefers strain-blind BREAKLINE.
- Local literal uniqueness fails (0.710 >0.70 vs BREAKLINE f45) and public literal gate fails (1.0 vs dense full-footprint witness).

**Verdict: negative — NOT_CLEARED for a weekly slot.** File remains format-valid, locally gated, and downloadable as a negative deliverable with full evidence.

## 5. What would change the picture

1. **Any ORGANIZER-CONFIRMED receipt** recalibrates: R0-claim fraction, keep-vs-far balance, whether holdout gains transfer to live truth. No lane in this repo has a receipt; without one, dose escalation beyond 45% is guesswork.
2. **Lane design:** Remove the shared DEM component for uniqueness — test pure `R = K/Th coherence × grad` or spring-corridor density (Rank 2) as a second lane, screening in-memory before building.
3. **Registry policy:** Operator decision on literal rule vs dense full-footprint rasters (currently every nonempty file fails). Until resolved, no candidate can be both honest and “promote” under that literal rule — do not silently reinterpret it.

## 6. Reproducibility & Verification

```bash
python scripts/restore_inputs.py          # SHA-verified 400 MB training_features + 26 MB radiometrics
pytest -v                                 # 123+ tests (gates, breakline, radscarp, parent lineage)
python scripts/build_radscarp_variants.py # builds f33/f38/f45, ledger + evidence
python scripts/report_radscarp_proxies.py # pooled HOLDOUT-DTI + canaries + SGMC + uniqueness
python scripts/validate_submission.py --candidate releases/h33-h33-2-b2-RADSCARPf45-20261025-d56ae6fc-zeros.tif
PYTHONPATH=vendor python scripts/check_site.py
```

All pins verified: `registry/session_manifest.json` (training_features sha256 `4371c82e…`, geodawn_rad_u8 `c22420f7…`, wellspring `122718e6…`). Grid: EPSG:32611, 3730×3292 @100 m, float32, [0,1], zeros outside.

## 7. Irregularities flagged

- Dense full-footprint `17GEMSDOE_E-proba` (100% footprint positive) makes literal `>70%` gate unsatisfiable for any nonempty in-footprint prediction — flagged in `IRREGULARITIES.md` and `docs/REVIEW_CURRENT.md`; requires operator policy decision.
- RADSCARP fusion assumed co-location of scarp + alteration would superset either detector; holdout shows the fused rank dilutes the DEM-only concentration that drives catalogue recovery. Do not retry fusion without screening pure `R` first.
- `data/` and `releases/*.tif` are tracked in this repo by convention but flagged as public-repo competition-raster exposure (`IRREGULARITIES.md` 2026-10-23).
