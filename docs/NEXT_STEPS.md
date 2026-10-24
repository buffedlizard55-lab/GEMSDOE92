# Next Steps — `GEMSDOE92` (Updated 2026-10-24)

## Prior-Session Queued Action Items — Completed in This Session

1. **Completed 1,300-raster public-registry audit on `BREAKLINE f45Ltop` (`evidence/breakline_public_registry_uniqueness.json`):**
   - Verified across all `102` public `buffedlizard55-lab` GEMSDOE repositories (`1,294` non-BREAKLINE rasters): `122` rasters exceed `70%` forward 3-px overlap (`68` space-filling `>=70%`-halo surfaces + `54` `<70%`-halo rasters up to `0.9130` vs `GEMSDOE3/coverage-v3-wide`), `verdict: negative`.
2. **Completed off-catalogue `USGS SGMC` bedrock-fault evaluation on `visible-collar-r0-excluded` (`evidence/scarpdipole_proxy_audit.json`):**
   - `visible-collar` collapses **`-77.94%`** vs `R0` (`0.021192` vs `0.096060` across `n = 62,703` off-catalogue `SGMC` fault pixels), and its prior `11.7×` holdout headline was proved to be a fold-fair (`0.046866`) vs pre-punched static `R0` (`0.004006`) masking confound (`1.61×` vs fold-fair `parent_B2_visible = 0.029074`).
3. **Repaired malformed JSON trailing comma & parallelized `scripts/audit_public_registry.py`:**
   - Repaired `evidence/public_registry_uniqueness.json` + `docs/downloads/public_registry_uniqueness.json`; certified universal all-positive blocker `17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373 / 5,167,373` positive footprint pixels).
4. **Screened 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_SCARPDIPOLE.md`) and implemented `SCARPDIPOLE` (`gems/scarpdipole.py`):**
   - Built `f42dipole` (primary), `f45dipole`, and `f50dipole` via shared `submission_writer.py`.
   - `SCARPDIPOLE f42dipole` ranks **#1 on fold-fair `HOLDOUT-DTI`** (`0.098565 [0.087985, 0.108974]`, `3.39×` `parent_B2_visible` and `2.10×` `visible_collar`), **#1 on static `HOLDOUT-DTI`** (`0.006812 [0.005770, 0.008034]`), **`+12.26%` above `R0` on off-catalogue `USGS SGMC`** (`0.107841`), **`10/10` format-valid**, and **`0 / 1,004` overlaps `> 70%` across all sparse dotted public submissions (`<= 60,000` dots)** (`max = 0.6877`), while faithfully recording binding `verdict: negative` under the un-waived literal all-rasters rule due to `17GEMSDOE`.

---

## Immediate Recommended Next Steps for Future Sessions

1. **Human Selector Policy Decision on `17GEMSDOE` Saturation (`SLOT_PLAN.md`):**
   - Because `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` has positive support on `100.0%` of the `5,167,373` footprint cells, **no nonempty submission can ever pass** the literal un-scoped `>70%` positive-support rule (`finite > 0`).
   - Decide explicitly whether the 3-px dot-overlap gate applies to sparse dot-field submissions (`<= 60,000` positive pixels, where `SCARPDIPOLE f42dipole` has `0 / 1,004` overlaps `> 70%`) while full-footprint Spearman rank correlation (`|ρ| <= 0.90`, where `SCARPDIPOLE f42dipole` has `max |ρ| = 0.3152`) governs continuous surfaces.
   - If the human selector adopts that rule, **`h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif` is immediately ready for one live weekly DrivenData slot** (and if submitted, record the exact `ORGANIZER-CONFIRMED` score and UTC timestamp in `ledger/submissions.csv`).

2. **How to Close the Gap Toward Leaderboard `#1` (`0.4413` `LEADERBOARD-SNAPSHOT` vs `0.2778` Sparse Dot-Skeleton Ceiling):**
   - As proved in `README.md` §3, binary unit-mass dot skeletons (`p ∈ {0, 1}` at `>= 2.8 px` spacing) pay a fixed `α = 0.2` FP tax on every isolated dot in a negative cell and leave small uncovered gaps between `2.8 px` dots along continuous fault strands.
   - Closing the gap from `~0.28` toward `0.32–0.44+` requires **calibrated continuous-probability `[0, 1]` multi-scale neural/boosted segmentation** (building on Prof. John Lipor's official `drivendataorg/gems-prize-reference-solution` Monte-Carlo CV U-Net) trained strictly on buffered whole-segment spatial folds with **DTI-surrogate cover loss** (`fault_cover_map` max-pooling with `α = 0.2, β = 0.8`) and multi-channel raw inputs (`det_elev` scarp-dipole tensor + raw `rtp` + raw `iso_grav_anom` + `depth_to_base_surf` + geodetic strain invariants), run on a GPU environment (`>= 16 GB` VRAM).

3. **Additional Official Public Data Layers Worth Staging in `registry/session_manifest.json` (in an Unrestricted Network Environment):**
   - **USGS Quaternary Fault and Fold Database (QFFD):** Verify attribute-level slip-rate / recency classes against `existing_faults` to understand which low-slip Class B/C Quaternary structures are systematically omitted from the competition compilation.
   - **Nevada Bureau of Mines and Geology (NBMG) 1:24,000–1:100,000 Quadrangle Fault Compilations & InSAR Deformation Velocity Maps (UNR / ARIA Sentinel-1):** Direct physical observables of blind sub-alluvial creep/subsidence boundaries across Basin-and-Range geothermal play fairways without relying on coarse 2 km gravity gridding.
   - **Live Public Registry Refresh:** In a network-unthrottled session, run `python scripts/audit_public_registry.py --candidate docs/downloads/h33-h33-2-b2-SCARPDIPOLEf42dipole-20261024-5bc7d987-zeros.tif --surface .cache/diag/scarpdipole_S_pct.npy` without `--cache-only` to capture any newly pushed public repositories since `2026-10-24`.
