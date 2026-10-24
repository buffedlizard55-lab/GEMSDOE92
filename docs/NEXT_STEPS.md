# Next Steps — `GEMSDOE92` (Updated `2026-10-24`, Post-`COULOMB-LOQO` Session)

## 1. Completed in the `COULOMB-LOQO` Session

1. **Unified PR #49 Merge State & Corrected 5 Newly Verified Irregularities (`IRREGULARITIES.md`):**
   - `#IR-92-ALPHA-BETA-PROSE-SWAP`: Corrected inverted Tversky denominator prose (`0.2 * FP_w + 0.8 * FN_w`, verified in `drivendataorg/gems-prize-reference-solution` Cell 16 and `vendor/gems57/metric.py`).
   - `#IR-92-SOLO-R1-BYTE-IDENTITY` & `#IR-92-CAT-COUNT-PROSE`: Proved exact zero-XOR ancestor cascade `H19-5 (121,131) -> D2.8 (44,090) -> SOLO (40,199 = D2.8 & d_cat > 1.0) -> R0 (37,654 = D2.8 & d_cat > 2.0)` across `60,988` `existing_faults` pixels.
   - `#IR-92-HYDROCONDUIT-EXTEND-TERMS`: Fixed `scripts/report_hydroconduit_proxies.py` to sum `all_terms + terms` per physical 20 km spatial block instead of concatenating `8 * n_blocks` rows.
   - `#IR-92-PR49-MERGE-SEAMS`: Eliminated duplicate `id="download-springalign"` in `docs/index.html`, repaired invalid `</main><footer>...</footer></section><section>` markup in `docs/HYPOTHESES.html`, and unified all pages around a single active primary.
2. **Pre-Registered 5 Untried Geological Hypotheses (`docs/HYPOTHESES_20261024_COULOMBLOQO.md`) & Implemented #1 `COULOMB-LOQO` (`gems/coulomb_loqo.py`):**
   - 24 strictly catalogue-free physical features (`dist_known_fault_px` explicitly dropped; zero cross-quadrant quantile coupling), 4-quadrant Leave-One-Quadrant-Out (`>= 1.2 km` guard band, `> 500 m` negative buffer) `HistGradientBoostingClassifier`, and 1D multi-physics crest localization.
   - Set **new all-time `GEMSDOE92` #1 records on BOTH holdout instruments**:
     - Static `gems57-pooled-hide-v2` `HOLDOUT-DTI`: **`0.009220 [0.007983, 0.010493]`** (`+130.2%` vs `R0` `0.004006`; strict draw-blind `d_cat > 2.0` = `0.009689`).
     - Strict Rule-2 unmasked `d_visible > 2.0` `HOLDOUT-DTI`: **`0.113316 [0.100614, 0.127163]`**, beating `H19-5` (`0.096757`) by `+0.016559` (`95% CI [+0.008170, +0.024980]`) — **first standalone (`0% H19-5`) model in repo history to beat `H19-5`**!
     - Recovered `USGS SGMC` `PROXY` DTI to **`0.090569`** (`standalone`, `+22.2%` over `HYDROCONDUIT`) and **`0.094057`** (`dual45`, `+26.9%` over `HYDROCONDUIT`).

---

## 2. Prioritized Next Steps for Future Sessions / Human Selector

1. **Human Selector Action — Resolve `Blocker 1` (Dense Public Probability Surface Uniqueness Scope) & `Blocker 0` (Organizer Calibration Receipt):**
   - Formalize whether dense continuous/habitat rasters (`> 90,000` positive pixels, such as `17GEMSDOE E-proba-multiscale` at `5,167,373` pixels) are excluded from the sparse competition-budget uniqueness pool.
   - Under a `<= 90,000`-px sparse uniqueness pool, `COULOMBLOQO dual45` (`0.009107` static / `0.1020` `d_vis>2` / `0.0941` `SGMC`, `0 / 1,121` `> 70%`) is ready for human selector evaluation alongside one `ORGANIZER-CONFIRMED` calibration receipt on `R0`.
2. **Next Untried Physics Lanes (Pre-Registered Queue in `docs/HYPOTHESES_20261024_COULOMBLOQO.md`):**
   - **Hypothesis 3 (`EULER-RTP-GRAV-N0`):** Moving-window 3D contact Euler deconvolution ($N = 0$, Reid et al., 1990) jointly over `Bands 2, 9, 14` (RTP/TMI) and `Bands 5, 11, 13, 18` (isostatic gravity & E–W horizontal gradient) to estimate exact subcrop $(x_0, y_0, z_0)$ coordinates of concealed faults beneath `50–1,200 m` of basin fill without relying on surface DEM slope.
   - **Hypothesis 4 (`DRAINAGE-KNICK-RADON`):** Cross-canyon thalweg longitudinal convexity & deflected-drainage Radon line-integral alignment across parallel range-front canyons (`Bands 12, 19, 15, 7`) to detect degraded Pleistocene range-front faults where interfluve scarps have diffused away.
   - **Hypothesis 5 (`INSAR-3DEP1M-DECONFOUNDED`, Contingent on External Tile Staging):** If an operator with unrestricted outbound network access stages ASF ARIA/OPERA Sentinel-1 InSAR velocity tiles and USGS 3DEP 1 m LiDAR tiles into `.cache/gems_inputs/external/`, test pumping-deconfounded creep/subsidence phase-gradient steps (`> 2 km` from `GDR #1391` production wells).
3. **Do Not Repeat Closed / Falsified Lanes:**
   - Do not revisit raw-thresholded `GRAVCrest`, standalone `BASEMENT-STEP`, pure seismicity (`Bands 10, 16`), un-normalized slope breaks (`BREAKLINE`, `STEPEDGE`, `SCARPPOL`), `> 70%` kept-`R0` edits (`RELIEF`, `DILATATION`), or misuse `Band 6 tc` as magnetic tilt (`#IR-92-BAND6-TC-MISLABEL`).
