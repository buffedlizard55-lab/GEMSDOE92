# Next Steps — `GEMSDOE92` (Updated 2026-10-24)

## Prior-Session Queued Action Items — Completed Across Merged 2026-10-24 Sessions

1. **Completed 1,300-raster public-registry audit on `BREAKLINE f45Ltop` (`evidence/breakline_public_registry_uniqueness.json`) & public witness verification (`docs/REVIEW_CURRENT.md`):**
   - Verified across all `102` public `buffedlizard55-lab` GEMSDOE repositories (`1,294` non-BREAKLINE rasters, both pre-placement surface and final dots): `122` rasters exceed `70%` forward 3-px overlap (`68` space-filling `>=70%`-halo surfaces + `54` `<70%`-halo rasters up to `0.9130` vs `GEMSDOE3/coverage-v3-wide`), `verdict: negative`.
2. **Completed off-catalogue `USGS SGMC` bedrock-fault evaluation on `visible-collar-r0-excluded` (`evidence/scarpdipole_proxy_audit.json`):**
   - `visible-collar` collapses **`-77.94%`** vs `R0` (`0.021192` vs `0.096060` across `n = 62,703` off-catalogue `SGMC` fault pixels), and its prior `11.7×` holdout headline was proved to be a fold-fair (`0.046866`) vs pre-punched static `R0` (`0.004006`) masking confound (`1.61×` vs fold-fair `parent_B2_visible = 0.029074`).
3. **Repaired JSON syntax & generalized fail-closed `scripts/audit_public_registry.py`:**
   - Repaired `evidence/public_registry_uniqueness.json` + `docs/downloads/public_registry_uniqueness.json`; certified universal all-positive blocker `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373 / 5,167,373` positive footprint pixels).
4. **Evaluated concurrent sibling lanes (`SCARPPOL`, `ANASIG`, `STRAINBREAK`, `GRAVCrest`) & implemented `SCARPDIPOLE` (`gems/scarpdipole.py`):**
   - `SCARPPOL` hit duplicate stop (`0.900–0.913` vs `BREAKLINE` due to coverage-dominated R0 keep-greedy); `GRAVCrest` was falsified in screen; `ANASIG f45Atop` (`0.004967`) and `STRAINBREAK f60s2i` (`0.005487`) beat `R0` (`0.004006`) on static holdout but fell short of `RELIEF p10` (`0.006045`).
   - **`SCARPDIPOLE` (`f42dipole` primary, `f45dipole`, `f50dipole`)** differentiated BOTH the `H19-5` keep stage (piedmont scarp-dipole reranking) and the `>3 px` off-skeleton emission (`docs/HYPOTHESES_20261024_SCARPDIPOLE.md`), ranking **#1 on fold-fair `HOLDOUT-DTI`** (`0.098565 [0.087985, 0.108974]`, `3.39×` `parent_B2_visible` and `2.10×` `visible_collar`), **#1 on static `HOLDOUT-DTI`** (`0.006812 [0.005770, 0.008034]`, beating `RELIEF p10`, `STRAINBREAK`, `ANASIG`, `BREAKLINE`, and `R0`), **`+12.26%` above `R0` on off-catalogue `USGS SGMC`** (`0.107841`), **`10/10` format-valid**, `0 / 27` local overlaps `> 70%` (`max = 0.6605`), and **`0 / 1,004` overlaps `> 70%` across all sparse dotted public submissions (`<= 60,000` dots)** (`max = 0.6877`), while faithfully recording binding `verdict: negative` under the un-waived literal all-rasters rule due to `17GEMSDOE`.

---

## Immediate Recommended Next Steps for Future Sessions

1. **Human Selector Policy Decision on `17GEMSDOE` Saturation (`SLOT_PLAN.md`):**
   - Because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` has positive support on `100.0%` of the `5,167,373` footprint cells, **no nonempty submission can ever pass** the literal un-scoped `>70%` positive-support rule (`finite > 0`).
   - Decide explicitly whether the 3-px dot-overlap gate applies to sparse dot-field submissions (`<= 60,000` positive pixels, where `SCARPDIPOLE f42dipole` has `0 / 1,004` overlaps `> 70%`) while full-footprint Spearman rank correlation (`|ρ| <= 0.90`, where `SCARPDIPOLE f42dipole` has `max |ρ| = 0.3152`) governs continuous surfaces.
   - If the human selector adopts that rule, **`h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif` is immediately ready for one live weekly DrivenData slot** (`46 BUILT / 0 RECEIPT` in `ledger/submissions.csv` — one `ORGANIZER-CONFIRMED` receipt outranks further uncalibrated local variants).

2. **How to Close the Gap Toward Leaderboard `#1` (`0.4413` `LEADERBOARD-SNAPSHOT` vs `0.2778` Sparse Dot-Skeleton Ceiling):**
   - Binary unit-mass dot skeletons (`p ∈ {0, 1}` at `>= 2.8 px` spacing) pay a fixed `α = 0.2` FP tax on every isolated dot in a negative cell and leave small uncovered gaps between `2.8 px` dots along continuous fault strands.
   - Closing the gap from `~0.28` toward `0.32–0.44+` requires **calibrated continuous-probability `[0, 1]` multi-scale neural/boosted segmentation** (building on Prof. John Lipor's official `drivendataorg/gems-prize-reference-solution` Monte-Carlo CV U-Net) trained strictly on buffered whole-segment spatial folds with **DTI-surrogate cover loss** (`fault_cover_map` max-pooling with `α = 0.2, β = 0.8`) and multi-channel raw inputs (`det_elev` scarp-dipole tensor + raw `rtp` + raw `iso_grav_anom` + `depth_to_base_surf` + geodetic strain invariants), run on a GPU environment (`>= 16 GB` VRAM).

3. **Additional Official Public Data Layers & Guards:**
   - **USGS Quaternary Fault and Fold Database (QFFD) & NBMG / ARIA Sentinel-1 InSAR Velocity Maps:** Stage under `registry/session_manifest.json` in an unrestricted network environment after verifying official redistribution/use terms.
   - **Do Not Re-Litigate Exhausted Single-Band Lanes:** Do not rebuild pure R0-keep-greedy DEM ridges (`SCARPPOL` / `BREAKLINE`), `BASEMENT-STEP` (`Band 15`), `GRAVCrest`, or fourth `STRAINBREAK` doses.
   - **Live Public Registry Refresh:** In a network-unthrottled session, run `python scripts/audit_public_registry.py --candidate docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif --surface .cache/diag/scarpdipole_S_pct.npy --out evidence/scarpdipole_public_registry_uniqueness.json` without `--cache-only` to capture any newly pushed public repositories.
