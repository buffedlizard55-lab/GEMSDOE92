# ALI lane — aggregate-label inversion + physics-only placement (GEMSDOE92, 2026-10-25)

## Decision (read this first)

| Question | Answer |
|---|---|
| New file generated? | **Yes.** [`gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif`](downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif) (136,103 B, SHA-256 `25398a5dee456a5fa491cb2b6b4dbd967f60b2e4239e62ac6871297c39ec7b37`) · [one-TIFF ZIP](downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.zip) · [run card](downloads/ali_run_card.json) |
| OK to download? | **YES — research only.** All automated format checks pass: one float32 band, EPSG:32611, 3730×3292, matching transform, finite values in {0, 1}, no NaN anywhere, zeros outside the footprint, 0 dots on catalogued faults. So it cannot cause the portal error "Predicted values must be in range [0, 1]". |
| OK to submit? | **NO — NOT CLEARED FOR A WEEKLY SLOT.** Two independent reasons. (1) **Duplicate under the registry rule.** The final dots exceed the 0.70 forward-overlap limit against real dot fields, not only against dense surfaces. Example: 80.6% of the dots are within 3 px of 12GEMSDOE `r7-nms3-dem10-scarp`, whose 3-px halo covers only 31.7% of the domain. In total, 30 such dot fields exceed 0.70. (2) **Does not beat the current holdout best.** It ties the R0-recipe control. |
| Name / note (if a human selector ever overrides) | `gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros` · `GEMSDOE92 ALI: OOF physics fault-appearance model, NMS 250 m, 37654 dots >300 m off-catalogue; holdout ties R0 recipe` (117 characters) |
| Organizer score | None. No receipt exists. Every leaderboard number below is an owner-reported **CLAIM**. |
| Budget | 3 experiments, 0 weekly slots. Stopped per protocol: duplicate and budget exhausted. |

## 1. Why `h33-h33-2-b2` scored 0.2778 — verified from the raster bytes

The following set identities were computed this session from the SHA-pinned rasters:

* `dotted-h19-5-d2-8` (44,090 px) ⊂ `H19-5` (121,131 px). The same holds for `d1-5` (60,069 px).
* `h27-4-solo` (40,199 px) = d2.8 minus every dot ≤ 1 px from a catalogued fault.
* **`h33-h33-2-b2` (37,654 px) = d2.8 minus every dot ≤ 2 px from a catalogued fault.**
* The 35,483 dots more than 3 px from the catalogue are **identical** in d2.8, h27-4 and h33-2-b2.

Owner-reported scores along this lineage (CLAIMs): H19-5 0.1922 → d1.5 0.2477 → d2.8 0.2600 → h27-4 0.2708 → h33-2-b2 0.2778.

**Mechanism.** Three effects stack:

1. **The skeleton.** H19-5 is the ridge set of a supervised, multi-line-corroborated fault-likelihood surface at a 2.45% budget. Its inputs are 1 m/10 m openness and local-relief scarps, anti-piedmont scarps, geopotential worms and a small thermal term ([19GEMSDOE `hypotheses.py`](https://github.com/buffedlizard55-lab/19GEMSDOE/blob/a3aca62fdb2be428f4245e22570cbc54082b2c15/src/gems/hypotheses.py)).
2. **Dotting.** With the official 300 m triangular kernel, one dot on a truth line earns up to 1 + 2·(2/3) + 2·(1/3) = 3 px of TP credit, but pays only α = 0.2 per unit of false-positive mass. Thinning the 1-px skeleton to 2.8 px spacing keeps ≈ 78% of line credit at ≈ 36% of the FP mass. This took the score from 0.19 to 0.26.
3. **The catalogue buffer.** Catalogued pixels are excluded from scoring (DrivenData staff, [forum 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)). A "new fault" is any fault pixel not already captured ([forum 11536](https://community.drivendata.org/t/where-do-you-draw-the-line/11536)). Dots within 200 m of a catalogued trace still pay FP but earn almost no TP. Removing 3,891 dots (≤ 1 px) and then 2,545 more (1–2 px) each raised the score.
   * Solving the DTI algebra with zero-yield removed dots gives implied TP mass of ≈ 5,074·φ (first step) and ≈ 5,470·φ (second step). φ is the unknown public-chunk fraction. The two estimates agree within 8% (MODEL).

**Independent confirmation from 105 scored registry rasters** (exact registry matches of the owner-reported names): rasters concentrated within about 2–3 px of the catalogue score near zero.

| Raster | Score (CLAIM) |
|---|---|
| `gems79-tilt-ring` | 0.0005 |
| `gems81-cont-poisson-buf2` | 0.0041 |
| `repo-c0-habitat` | 0.0041 |
| `17GEMSDOE_F-ensemble` | 0.0187 |

**Can a unique file beat it?** Uniqueness caps reuse of the H19-5 skeleton at 70% of dots. Six registry submissions met that cap, and all six scored below 0.2778 (0/6):

| Submission | Score (CLAIM) |
|---|---|
| gems70-p5 | 0.2478 |
| gate_ortho | 0.2376 |
| gems76-ptcf | 0.2343 |
| gems73 | 0.1917 |
| gems82 | 0.1886 |
| gems91-lftg | 0.1823 |

Beating 0.2778 with a unique file needs ≥ 30% of the dots in new places that are about as productive as H19-5's best dots. This session shows that physics-driven placements now land on pixels already claimed by earlier dot fields, which makes that very hard.

## 2. What the 105 scored rasters say (aggregate-label inversion, MODEL)

The expected TP of submission s is E[TP_s] = Σ_g λ(g)·C_s(g), where C_s is the exact kernel coverage. This is exact in expectation for **any** truth process with pixel inclusion probability λ, because expectation is linear.

λ is log-linear over three strata:

* **D:** catalogue distance.
* **F:** quantile of our own out-of-fold Fault-Appearance Model (FAM).
* **H:** proximity to the H19-5 skeleton.

The model was fitted to 99 distinct owner-reported scores ([`scripts/ali_fit.py`](../scripts/ali_fit.py)):

| Model | Parameters | LOO-RMSE | LOO Spearman |
|---|---|---|---|
| D only | 4 | 0.0929 | 0.189 |
| D + H (H19-5 proximity) | 5 | 0.0340 | 0.913 |
| **D + F (physics only; no prior submission used)** | 9 | 0.0440 | **0.906** |
| D + F + H | 10 | 0.0251 | 0.952 |

**Findings.**

* (a) Fault appearance in the physical layers alone ranks the leaderboard almost as well as the H19-5 skeleton.
* (b) The D + H model under-predicts the off-skeleton physics lanes by 0.07–0.13: gems70-p5, gate_ortho, gems76-ptcf, gems73, gems82, gems91-lftg. So productive territory exists off the skeleton.
* (c) **Extrapolation warning.** The FAM placement puts 9% of its dots in the top-0.5% FAM stratum and 68% in the top 4%. No scored raster exceeded 8.2% or 21.7% respectively.
  * The D + F + H projection (candidate 0.344 vs R0 0.282, jackknife SE of Δ = 0.044) is therefore **not reliable**.
  * The conservative D + H projection gives 0.107.
  * Model-free warning: the raster with the most top-FAM far dots, `17GEMSDOE_F-ensemble`, scored 0.0187.

## 3. Ranked untried hypotheses

Expected gains are unknown until tested. The ranking weighs the chance of landing on *new* pixels against cost.

| Rank | Hypothesis | Layers | Physical signature / operator | Why it catches faults missing from USGS/INGENIOUS | How it differs from the repo | Non-fault mimic | Cost |
|---|---|---|---|---|---|---|---|
| 1 | **Dextral drainage-deflection coherence (Walker Lane)** | `dem10_chi` (log-area, steps), 10 m aspect coherence, det_elev, geodetic shear (bands 4, 7) | Along-strike runs of channels deflected right-laterally by a consistent amount (shutter ridges, offset channels); Hough coherence at strain-compatible NW strikes | Strike-slip strands with little vertical relief make weak scarps. The Qfault DB records Quaternary sources of M>6 earthquakes ([USGS](https://www.usgs.gov/programs/earthquake-hazards/faults)), so short secondary strands are under-represented | KNICKLOQO used vertical knickpoints; no lane measured *lateral* deflection coherence. It targets a different signature, so it is the most likely to land on unclaimed pixels | Joint- or contact-controlled drainage; canals | Medium (may need the native 10 m DEM; official USGS 3DEP access not verified this session) |
| 2 | **Strain-compatible orientation gate on FAM ridges** | FAM ridges + structure-tensor strike; geod_2ndinv / shear / dilatation (bands 4, 7, 8) | Keep ridge segments whose strike lies within ±20° of the locally optimal normal-fault strike (⊥ extension) or the dextral plane | Real active faults are kinematically compatible; shorelines and terraces follow contours instead | COULOMB lanes modelled stress from visible faults; none gated lineament *orientation* by geodetic strain style | Bedding or foliation aligned with tectonic grain | Low |
| 3 | **Pleistocene-shoreline veto** | 10 m DEM mean, det_elev, profile curvature, aspect coherence | Detect contour-parallel benches that recur at common elevations and veto ridges running along them | Removes the most common linear slope-break false positive in western Nevada basins; this matters because α = 0.2 FP mass dominates the denominator | `datum-lahontan` (62GEMSDOE, 0.0000) used the datum as *signal*; here it is a *veto* | Fault scarps that coincide with a shoreline | Low–medium |
| 4 | **Relay / termination splay allocation** ([Faulds & Hinz 2015](https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf): step-overs ~32%, terminations ~25%, intersections ~22% of Great Basin systems) | Catalogue tips/overlaps (visible only), FAM | Allocate dots to FAM ridges inside overlap zones between catalogued tips | Experts map connecting splays inside relay ramps, and these are geothermally favourable | Partially tried: `h33d-analog-tip-stepover` scored 0.2632 and `h69 relay` 0.0053, so lower rank | Landslide headscarps at range fronts | Low |

**Tested this session (rank 0): ALI-FAM placement → negative** (duplicate; holdout tie). See §4–5.

## 4. Experiments (HOLDOUT-DTI, evaluator `gems57-pooled-hide-v2`, seeds 20/30, 8 LOQO folds, 22,663 withheld positives, 95% paired spatial-block bootstrap)

For each seed, the FAM was retrained on that draw's **visible** catalogue only, quadrant out-of-fold. Dots were re-placed against the visible catalogue.

| Arm | HOLDOUT-DTI | 95% CI |
|---|---|---|
| **E1 ALI FAM-NMS, 2.5 px, 37,654 dots** | **0.097216** | [0.079836, 0.117747] |
| E2 ALI FAM-NMS, 2.5 px, 26,000 dots | 0.083680 | [0.066581, 0.102822] |
| Control: R0 recipe (d2.8 minus d_visible ≤ 2) | 0.097493 | [0.085480, 0.111055] |
| Control: H19-5 skeleton | 0.066289 | [0.057687, 0.076151] |
| Control: single-layer det_elev_slope NMS (matched) | 0.030010 | [0.023106, 0.037804] |
| Control: matched random dots | 0.041924 | [0.037701, 0.045892] |

Paired differences for E1:

| E1 minus | Δ | 95% CI | Reading |
|---|---|---|---|
| R0 recipe | −0.000278 | [−0.015980, +0.015900] | **tie** |
| H19-5 skeleton | +0.030926 | [+0.017163, +0.047419] | E1 better |
| Random dots | +0.055291 | [+0.039297, +0.074113] | E1 better |
| E2 | +0.013535 | [+0.008919, +0.017710] | E1 better |

Current holdout best in the repo: FAULTNET netfar 0.175147. VENTSCARP rule-2 scored 0.112213. **E1 does not beat it.**

E3 was the leaderboard-calibrated projection sweep (MODEL only; §2). It makes no holdout claim.

**Leakage canaries:** 52 single features, maximum symmetric AUC 0.586 (`ctx_gradmag_detelev_s3`). The seed FAM alone reached 0.659. All are below the 0.90 leakage limit.

## 5. Uniqueness (REGISTRY-MEASUREMENT, full scan)

The scan covered 1,591 blobs: every synced `buffedlizard55-lab/*GEMSDOE*` TIFF plus local downloads. 1,583 were compared, excluding the candidate itself; 2 were unreadable or on another grid, and 5 were empty.

* **Literal reading:** worst forward overlap 1.0, from surfaces that are positive at every footprint cell. 99 rasters exceed 0.70.
* **Discriminating dot fields only** (rasters whose 3-px halo covers < 70% of the domain, so a random candidate would not fire): the candidate **still fires**:

30 discriminating dot fields fire. Selected rows:

| Registry raster | Dots | Halo coverage | Candidate forward overlap |
|---|---|---|---|
| GEMSDOE3 `coverage-v3-wide` (worst overall) | 624,025 | 0.610 | 0.907 |
| 12GEMSDOE `r7-nms3-dem10-scarp` (tightest) | 103,347 | 0.317 | **0.806** |
| GEMSDOE67 `ovtr-ml-cover` | 167,597 | 0.544 | 0.876 |
| GEMSDOE22 `h23-a` | 335,879 | 0.409 | 0.793 |
| GEMSDOE70 `p5-submodular-54000` | 54,000 | 0.232 | 0.729 |
| GEMSDOE45 `phase-parity` | 82,678 | 0.230 | 0.708 |

* **Rank correlation:** worst |ρ| = 0.078 on the final dots. On the pre-placement FAM surface, worst |ρ| = 0.401. No raster exceeds 0.90.
* **Verdict: duplicate → stop.** The dense-surface policy question does not change this outcome, because real dot fields fire too.

## 6. Sources verified this session

| Source | Link | Used for |
|---|---|---|
| DrivenData problem description | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | metric (α = 0.2, β = 0.8, 300 m triangular kernel), labels, rounds, format |
| GEMS Prize Official Rules (NLR, Sept 2026) | https://docs.nlr.gov/docs/fy26osti/96647.pdf | 3 submissions/week, one final selection, public/private split, AI disclosure, finalist code |
| Staff ruling: known faults masked (both rounds) | https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516 | catalogue buffer logic |
| Staff ruling: "new fault" definition | https://community.drivendata.org/t/where-do-you-draw-the-line/11536 | newly mapped geometry of an existing system counts |
| GeoDAWN (cited by the rules) | https://doi.org/10.5066/P93LGLVQ | feature provenance |
| INGENIOUS compilation (cited by the rules) | https://doi.org/10.15121/1881483 | label provenance |
| USGS Quaternary Fault and Fold Database | https://www.usgs.gov/programs/earthquake-hazards/faults | M>6, ≤1.6 Ma scope explains why catalogue faults are missing |
| Machette et al. 2003, OFR 03-417 | https://doi.org/10.3133/ofr03417 | database design |
| Faulds & Hinz 2015 (WGC) | https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf | favourable structural settings |
| DrivenData reference solution | https://github.com/drivendataorg/gems-prize-reference-solution (commit `aebe92f7`) | baseline context |
| H19-5 recipe | https://github.com/buffedlizard55-lab/19GEMSDOE/blob/a3aca62fdb2be428f4245e22570cbc54082b2c15/src/gems/hypotheses.py | §1 mechanism |
| gate_ortho / gems70 descriptions | [GEMSDOE49 README](https://github.com/buffedlizard55-lab/GEMSDOE49/blob/8ab48f22d02d8be3b8e01d843ed7dc7967b87c44/README.md) · [GEMSDOE70 README](https://github.com/buffedlizard55-lab/GEMSDOE70/blob/158aec19800d4c7b8ca9fb94b06567e2b7d61e8d/README.md) | §1 analogs |

DrivenData's Terms of Use restrict robots. Pages were opened individually to verify facts. No leaderboard or forum crawling was done, and the live leaderboard was **not** fetched. The two leaderboard values in the brief (0.4413 and 0.3195) conflict and remain owner-reported.

## 7. Limitations and irregularities

* All scores are CLAIMs. The repo holds no organizer receipt.
* The public leaderboard covers only the public chunks.
* The hide-and-recover instrument measures recovery of *catalogue* faults, not new faults. R0's static holdout value is the worst in the repo, yet R0 has the best claimed score.
* The leaderboard inversion has weakly identified catalogue-distance coefficients, and its FAM projection extrapolates (§2c).
* Sandbox storage incident: several large `.npy` caches came back with their first 4 KB data page zeroed. The ALI scripts now SHA-256 every saved array on read-back; see IRREGULARITIES.md `IR-92-NPY-PAGE-ZERO`.
* The pre-placement surface check ran after placement in this session, an ordering deviation. The final-dot check is decisive.

## 8. Reproduce

```bash
.venv/bin/python scripts/restore_inputs.py --ventscarp-external
.venv/bin/python scripts/sync_public_registry_git.py
.venv/bin/python scripts/ali_features.py
for L in full seed20 seed30; do .venv/bin/python scripts/ali_fam_oof.py --labelset $L; done
.venv/bin/python scripts/ali_scored_table.py      # owner-reported CLAIMs -> exact registry blobs
.venv/bin/python scripts/ali_design.py && .venv/bin/python scripts/ali_fit.py
.venv/bin/python scripts/ali_fam_evidence.py && .venv/bin/python scripts/ali_holdout.py
.venv/bin/python scripts/ali_build_submission.py
.venv/bin/python scripts/ali_uniqueness.py ALI=docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif
.venv/bin/python scripts/ali_project.py docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif
.venv/bin/python scripts/ali_run_card.py
```

## 9. Three-pass record

1. **Implement and verify.** Scripts ran end to end on SHA-pinned inputs. Every large cache is hash-verified on read-back. The shared writer and validator pass, the site check passes (83 served rasters gated, including this file) and the test suite passes (`tests/test_ali_lane.py` adds kernel, coverage, NMS and storage-integrity tests).
2. **Review for bugs and edge cases.** This pass caught four problems:
   * the zeroed-page corruption (fixed, IR-92-NPY-PAGE-ZERO);
   * a NaN-unsafe read-back comparison (fixed);
   * a duplicated gate row in the audit (fixed);
   * a mislabelled canary (0.659 is the seed FAM model, not a single feature; fixed).
   The FAM projection was also recognised as extrapolation and downgraded to MODEL.
3. **Recheck against the request.**
   * New TIFF: done.
   * Obvious download/submit verdict: done (first panel on every page).
   * Name and note ≤ 140 characters: done.
   * PhD-level 0.2778 answer: done (§1).
   * 3–5 hypotheses: done (§3).
   * Holdout with labelled numbers and CI: done (§4).
   * Leakage canaries: done.
   * Registry uniqueness on surface and dots: done (§5).
   * Run card: done.
   * Official links: done (§6).
   * Irregularities: done.
   * **Unmet:** a *unique* submittable file. The new raster is a registry duplicate and only ties the comparable control, so it is not cleared.
