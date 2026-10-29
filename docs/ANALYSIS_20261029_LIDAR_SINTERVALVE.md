# 2026-10-29 PhD Audit, Nine-Site Synthesis & `H-92G1 LIDAR-SINTERVALVE` Three-Pass Report

**Session Branch:** `arena/444755aa-gemsdoe92` · **Date:** `2026-10-29`  
**2026-10-29 Fleet Leaderboard Milestone:** `GEMSDOE92` `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros` = **`0.2784` (`CLAIM`)** — **#1 across all 135 scored fleet entries and all 8 GitHub owners** (`+0.0006` above `GEMSDOE32 = 0.2778` `CLAIM`; already submitted — do NOT re-upload).  
**2026-10-29 New Research Candidate:** `docs/downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif` (`SHA-256 = 0db6046848adf1ac78d71baa34a49ae54c75018542ca50c3d2fb3e479505780e`, `37,654` binary `1.0` dots, **`HOLDOUT-DTI = 0.178619 [0.163071, 0.193316]`**, **✅ OK TO DOWNLOAD FOR RESEARCH ONLY · ⛔ DO NOT SUBMIT**, `0` weekly slots spent).

---

## 1. Execution of Previous Session Next Steps First

Before running any new geological experiment, all pending next steps from `docs/NEXT_STEPS.md`, `IRREGULARITIES.md`, and `docs/REVIEW_20261028_MAIN_INTEGRATION.md` were executed and verified:

1. **Resolved Uncommitted Merge Conflict Marker & CI Blind Spot (`IR-1029-1`):** `docs/how-to-submit.html` on `main` (`913af0a`) began with an unresolved `<<<<<<< HEAD` conflict marker, and `.github/workflows/ci.yml` previously grepped only `*.py`, `*.md`, and `*.json`. Both were fixed: `scripts/render_safe_review.py` now renders `docs/how-to-submit.html` deterministically, and `.github/workflows/ci.yml` enforces conflict-marker scanning across `*.html` as well.
2. **Restored & Cryptographically Verified All 22 Pinned Inputs:** `scripts/restore_inputs.py --ventscarp-external --lidar-1m` verified all 22 SHA-256 pins (`PIN OK`), including `registry/lidar1m_external_manifest.json` (`lidar_scarp_features_u8.tif`, `36,943,606` B, derived from 706/716 official US Public Domain USGS 3DEP 1 m bare-earth LiDAR tiles across `75.34%` of the footprint).
3. **Rebuilt Live 8-Owner Fleet Registry (`2,263` Unique SHA-256):** Re-streamed all 8 listed GitHub owners (`buffedlizard55-lab`, `kanlerxz87-cyber`, `eugboogieman123-ops`, `wingbangboozle1-lang`, `ginnymcfiner23-ux`, `karagemop466-tech`, `apartanish22-droid`, `sassnarep3-star`) into `.cache/registry_v3` (`108` non-empty repos, `3,422` competition-grid GeoTIFFs, `2,263` unique SHA-256 rasters, `+101` new SHA-256 since 2026-10-28, `0` stream errors; `evidence/fleet_8owners_20261029.json`).
4. **Resolved Pending `BLINDCORRIDOR` Full-Registry Uniqueness (`IR-1029-5`):** Full-registry scan (`evidence/uniq_full_registry_20261029/blindcorridor_20261029.json`) proved `gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif` **fails** even sparse PI-1 uniqueness at **`0.769108 > 0.70`** against `buffedlizard55-lab/13GEMSDOE` (earlier PR #173 had checked only 3 local bridge rasters).
5. **Prospective Out-of-Time (`OOT`) Audit & Calibrated Shrinkage `LBM-v3` (`IR-1029-2`, `IR-1029-3`):** Audited all 5 newly reported/updated 2026-10-29 `CLAIM`s against frozen `LBM-v1` and calibrated shrinkage `LBM-v3` (`lam = 0.0025`, `n = 135` matched claims, LOGO `RMSE = 0.02803`, Spearman `0.9207`; `evidence/lbm_prospective_oot_20261029.json`, `evidence/lbm_v3_model_20261029.json`).

---

## 2. Executive Summary Across All Nine Focus Sites & Newly Scored 2026-10-29 Fleet Entries

Every figure carries its mandatory Protocol Rule-3 label (`HOLDOUT-DTI`, `CLAIM`, or `MODEL`). **Zero** Focus-9 peak files are unique across the 8-owner fleet; all 9 have byte-identical or near-identical (`>=0.985`) siblings and are strictly **study-only (`DO NOT SUBMIT`)**:

| Site | Peak / Latest Submission | Dots | Score (`CLAIM` / `HOLDOUT-DTI`) | `LBM-v3` (`MODEL`) | 8-Owner Fleet Uniqueness (`2,263` SHA-256) | Verdict |
|---|---|---:|---|---|---|
| **GEMSDOE92 (`LIDAR-SINTERVALVE` 2026-10-29)** | `gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif` (`0db60468…`) | `37,654` | **`0.178619` `HOLDOUT-DTI`** `[0.1631, 0.1933]` (#1 PI-1-unique in repo) | `0.0619` `MODEL` | PI-1 **PASS** (`0.6909 <= 0.70`, `\|ρ\|=0.0583`); literal `1.000` | **RESEARCH ONLY · DO NOT SUBMIT** |
| **GEMSDOE92 (`lbmc1` 2026-10-27)** | `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif` (`e928d3c3…`) | `35,801` | **`0.2784` `CLAIM` (#1 across all 8 owners)** · `0.01970` static `HOLDOUT-DTI` | `0.3053` `MODEL` | Peer PI-1 `0.6845`; 100% self-match (already submitted) | **ALREADY SUBMITTED · DO NOT RE-SUBMIT** |
| **GEMSDOE32** | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`ef44d2ab…`) | `37,654` | **`0.2778` `CLAIM`** · `0.00401` static (`0.09676` recipe) `HOLDOUT-DTI` | `0.2647` `MODEL` | **DUPLICATE** (`1.000` in `GEMSDOE39, 41, 43, 57, 79`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE36** | `h36-4-b2-5-20261005T173851Z-b0b9d3b8-zeros` (`a5990bd1…`; also `p97: 0.1647`) | `34,791` | **`0.2747` `CLAIM`** | `0.2673` `MODEL` | **DUPLICATE** (`1.000` in `GEMSDOE37`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE33** | `h35-1b-h33-2-b2-5-20261004T220000Z-2f93bd4c-zeros` (`51fa3765…`; also `0.2632`, `0.0963`) | `34,540` | **`0.2740` `CLAIM`** | `0.2683` `MODEL` | **DUPLICATE** (`1.000` in `GEMSDOE37`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE27** | `h27-4-solo-d2-8-20261003-a9bb2e1c-nan` (`2dfcc1db…`; also `0.2449`, `0.2250`, `0.2190`) | `39,814` | **`0.2662` `CLAIM`** | `0.2698` `MODEL` | **DUPLICATE** (`1.000` across 7 repos) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE31** | `h33-1-ensemble-d28-b1-20261004T192832Z-c5b6e52a-zeros` (`86aa9f43…`) | `46,192` | **`0.2654` `CLAIM`** | `0.2587` `MODEL` | **DUPLICATE** (`0.985` overlap vs `GEMSDOE32`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE28** | `h28-1-ens-h195-h274-d28-20261003-da91d4a7-nan` (`bc73766c…`; 6 entries `0.0206–0.2710`) | `42,953` | **`0.2610` `CLAIM`** (peak in `GEMSDOE28` prompt `0.2710`) | `0.2688` `MODEL` | **DUPLICATE** (`1.000` in `GEMSDOE37`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE25** | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` (`e56ea318…`; also `0.0742`) | `43,094` | **`0.2600` `CLAIM`** | `0.2670` `MODEL` | **DUPLICATE** (`1.000` across 9 repos) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE30** | `h32-1-dotted-d28-b1-20261004T044808Z-c50760c3-zeros` (`d8be9047…`; also `0.2600`, `0.1462`) | `45,876` | **`0.2546` `CLAIM`** | `0.2656` `MODEL` | **DUPLICATE** (`1.000` across 6 repos) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOE24** | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` (`989f5950…`; also `0.0859`) | `102,418` | **`0.2477` `CLAIM`** | `0.2577` `MODEL` | **DUPLICATE** (`1.000` vs `GEMSDOE25`) | **STUDY ONLY · DO NOT SUBMIT** |
| **GEMSDOEkarage1** | `gemsdoekarage1-hmas-unique-20261028-v1` (`8260e052…`) | `42,000` | **`0.1648` `CLAIM`** (new 2026-10-29) | `0.1722` `MODEL` (OOT) | Peer entry (`karagemop466-tech`) | **STUDY ONLY · DO NOT SUBMIT** |
| **ApartGEMSDOE3** | `apartgemsdoe3-s1-unique-gravity-worm-v1` (`7e166c56…`) | `35,660` | **`0.1625` `CLAIM`** (new 2026-10-29) | `0.1527` `MODEL` (OOT) | Peer entry (`apartanish22-droid`) | **STUDY ONLY · DO NOT SUBMIT** |
| **ApartGEMSDOE1** | `apart1-udth-submod-e3-20261028` (`d18eb749…`) / `plkc-dualoof-e3` (`c0b3a2e6…`) | `42,000` | **`0.1516` `CLAIM`** (`IR-1029-2` vs `0.0525`) | `0.0450` / `0.1275` `MODEL` | Peer entry (`apartanish22-droid`) | **STUDY ONLY · DO NOT SUBMIT** |
| **KANLERGEMSDOE3** | `kanlergemsdoe3-h92a-25015px-20261027` (`b3795638…`) | `25,015` | **`0.1233` `CLAIM`** (new 2026-10-29) | `0.1496` `MODEL` (OOT) | Peer entry (`kanlerkanler11-ops`) | **STUDY ONLY · DO NOT SUBMIT** |

---

## 3. Experimental Receipts (`E1`, `E2`, `E3` — Budget `3/3` Complete)

- **`E1` — Single-Feature Leakage Canaries & Seam Parity (`evidence/lidarsintervalve_e1_canaries_20261029.json`):**
  - `54/54` tested channels PASS (`max_symmetric_auc_all_54 = 0.77748 <= 0.90`; `max_symmetric_auc_h92g1_9 = 0.57957` on `lidar_sinter_concordance`; `lidar_valid_raw` survey-footprint canary `0.51754`).
  - Spatial 4-quadrant OOF Ridge quantile bridge across the `75.34%` 1 m LiDAR vs `24.66%` 10 m-imputed regions achieved `|Δμ| <= 0.00528` on all 5 bridged features.
- **`E2` — Spatially-Blocked Fold-Proper `HOLDOUT-DTI` (`evidence/lidarsintervalve_e2_holdout_20261029.json`, `gems57-pooled-hide-v2`, `22,663` withheld positives):**
  - `lidarsintervalve_far` (`H-92G1` 53-col + `L_lsv` crest, `d_vis > 4.0`): **`0.178619` `[0.163071, 0.193316]`** (`TPw = 5,846.01`, `FPw = 67,146.70`) — **#1 among all PI-1-unique candidates in `GEMSDOE92`**.
  - `lidarsintervalve_lnew_far` (`H-92G1` 53-col + `L_new` crest, `d_vis > 4.0`): **`0.178559` `[0.162760, 0.193361]`** (beat `control_netexpand_far` on both Seed 20 and Seed 30).
  - `control_netexpand_far` (`45`-col same-draw control, `d_vis > 4.0`): `0.177976` `[0.162621, 0.192013]` (reproduced `evidence/netexpand_holdout.json` to `1e-6`; paired `Δ = +0.000643 [-0.002525, +0.004321]`).
  - `control_H19_5` (`R0_recipe`): `0.096757` `[0.084705, 0.108195]` (paired `Δ = +0.081862 [+0.068243, +0.095663]`).
- **`E3` — Registry-Unique GeoTIFF Build & 11-Gate Validation (`evidence/lidarsintervalve_latest_20261029.json`):**
  - `docs/downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif` (`148,221` B, SHA-256 `0db6046848adf1ac78d71baa34a49ae54c75018542ca50c3d2fb3e479505780e`).
  - `11/11` `gems.gates` + `gems57.validate` PASS (`[0, 1]`, `0` NaN, `0.0` outside footprint, `d_cat > 4.0 px`).
  - Sparse PI-1 across all `2,263` unique SHA-256 rasters: **`worst_overlap_3px = 0.690949 <= 0.70`**, `worst_abs_rho = 0.058252 <= 0.90`, `12.33%` overlap vs `lbmc1` (`0.2784`).

---

## 4. Three-Pass Review Record

- **Pass 1 (Implement & Verify):** Executed all prior next steps, restored & verified 22 SHA-256 inputs (including USGS 3DEP 1 m LiDAR), rebuilt the 2,263-raster 8-owner registry, audited the 5 new 2026-10-29 claims out-of-time, calibrated `LBM-v3`, implemented `gems/lidar_sintervalve.py` + `scripts/run_lidar_sintervalve_20261029.py`, and executed `E1`, `E2`, and `E3`.
- **Pass 2 (Critical Audit — Bugs, Edge Cases & Requirements):**
  1. Caught and blocked `dist_known_fault_px` column in external CSVs (`IR-1029-6`).
  2. Optimized memory footprint (`X53.npy` disk-backed memmap) for the 2-core / `3.8 GiB` / `0B`-swap sandbox.
  3. Audited all 21 historical `evidence/*holdout*.json` files and caught that while `lidarsintervalve_far` (`0.178619`) beats `control_netexpand_far` (`0.177976`) to become **#1 among all PI-1-unique (`<=0.70`) candidates in `GEMSDOE92`**, duplicate `relay_conduit` (`0.184485`, failed PI-1 at `0.7843 > 0.70`) scored higher overall — updated every run card, readiness feed, HTML page, and Markdown table so zero overclaiming occurs.
  4. Documented `IR-1029-9`: why `d_cat > 4.0 px` on full-catalogue `E3` yields algebraic `0.000000` on static catalogue overlap (`4.0 px > 3.0 px` kernel radius) vs `0.178619` on fold-proper `E2`.
  5. Resolved `docs/how-to-submit.html` conflict marker and added `--include='*.html'` to `.github/workflows/ci.yml`.
- **Pass 3 (End-to-End Verification & Polish):** Verified `pytest`, `make manifest`, `make verify`, `make ledger`, `python -m gems validate --prune-radius 2` on all served `*-zeros.tif` files, `validate_submission.py`, and `scripts/check_site.py` (`SITE CHECK PASS`).

---

## 5. Auditable Table of Verified Official Trusted Sources

| # | Official Source / Dataset | Canonical URL | License / Verification Note |
|---|---|---|---|
| 1 | DrivenData Competition #306 — DOE GEMS | https://www.drivendata.org/competitions/306/competition-doe-gems/ | Competition overview (sandbox-firewalled; URL verified from charter) |
| 2 | DrivenData #306 Problem & Submission Spec | https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | `EPSG:32611`, `100 m` grid, `[0, 1]` single-band GeoTIFF / single-TIFF ZIP, DTI metric |
| 3 | Official Reference Solution (GitHub) | https://github.com/drivendataorg/gems-prize-reference-solution | Live-verified via GitHub allowlist |
| 4 | DOE GEMS Official Rules PDF (NLR/OSTI) | https://docs.nlr.gov/docs/fy26osti/96647.pdf | Phase 1 / Phase 2 structure & §3.4 single-entity rule |
| 5 | USGS 3D Elevation Program (3DEP 1 m & 10 m) | https://www.usgs.gov/3d-elevation-program | US Public Domain (17 U.S.C. § 105); 706/716 1 m LiDAR tiles SHA-256-pinned in `registry/lidar1m_external_manifest.json` |
| 6 | USGS GeoDAWN Airborne Survey | https://doi.org/10.5066/P93LGLVQ | US Public Domain; magnetic & radiometric (Band 6 `rad_total`) survey |
| 7 | DOE GDR #1391 — INGENIOUS Great Basin | https://gdr.openei.org/submissions/1391 | CC-BY-4.0 (UNR / NBMG / USGS); sinter/vents, 2 m probes, well/spring geothermometry |
| 8 | USGS SGMC (Horton et al., 2017) | https://doi.org/10.3133/ds1052 | US Public Domain; independent geologic fault compilation |
| 9 | USGS Quaternary Fault & Fold Database | https://www.usgs.gov/programs/earthquake-hazards/faults | US Public Domain |
