# Candidate handoff — human review and submission only

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot (the NaN-outside primary `.tif` and `-zeros.tif` fallback carry identical in-footprint values and score identically).

## Session candidates (`AXIS = SNAP`, 2026-10-23)

All three candidates preserve exact R0 dot count (`37,654` binary unit-mass dots), R0 catalogue exclusions (zero catalogue mass, `d_cat > 2.0 px`), and R0 `D2.8` Poisson-disk inter-dot spacing (`min_nn = 2.8284 px`), changing **only** the `<=2 px` edge/scarp snap operator. Form notes are `<=140` characters.

| Order | Primary file (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Form note (`<=140` chars) | Mean / max disp | Primary SHA-256 (`-zeros` SHA-256) | Format receipt |
|---:|---|---|---|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24.tif` | `releases/h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24-zeros.tif` | `h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24` | `h33-h33-2-b2; SNAP <=2.0px edge+scarp+break (nn>=2.8); mean disp 1.23px; pred MODEL:+0.012` (90 chars) | `1.234 px` / `2.000 px` (82.05% px changed) | `2a65fe24766375d5d2330daa9547f33a0cd16838d20675b1a03d531b0e33601d` (`96c8598a20114682579078044f03149c15d42f79cc8143d9f7300bd1881d2d1e`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`; `min_nn = 2.828 px`. |
| 2 | `releases/h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc.tif` | `releases/h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc-zeros.tif` | `h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc` | `h33-h33-2-b2; SNAP <=1.41px 8-nbr edge+scarp+break (nn>=2.8); mean disp 0.95px; pred MODEL:+0.008` (97 chars) | `0.954 px` / `1.414 px` (78.00% px changed) | `01fb4acccb35abbc96078b2ec80e48e455979dc470d72756763cc2bbeefc6915` (`d00f1fe26dc3a755ec4f181806cb73ad172ddaecfaacc9e2914bbc7c4bf472f1`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`; `min_nn = 2.828 px`. |
| 3 (conditional control) | `releases/h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c.tif` | `releases/h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c-zeros.tif` | `h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c` | `h33-h33-2-b2; SNAP <=2.0px TMI+grav horiz grad only (nn>=2.8); mean disp 1.37px; pred MODEL:-0.002` (98 chars) | `1.366 px` / `2.000 px` (79.07% px changed) | `41697f8c25a7e3989b512a9cfb5993fcc52b07693e2ef97f061606b6a36b6ea2` (`f1c72a877b47f1f121caa2cf24412aa2ff1d415d3be9c41b13d28ddeda5f9271`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`; `min_nn = 2.828 px`. |

*(Slot 3 note per `SLOT_PLAN.md`: if Slot 1 `SNAPscarp2p0px` improves or is neutral, allocate Slot 3 to orthogonal `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` recorded in `evidence/prune_rungs.json`; submit `SNAPpot2p0px` only if Slot 1 drops by `>= 0.01` to test concealed-basin potential-field dominance.)*

## Report-only diagnostics (`PROXY`, never gates or scores)

- **Catalogue hide-and-recover `PROXY`** (`n = 22,663` withheld catalogue positives, paired 20 km spatial-block bootstrap 95% CI, `evidence/snap_proxy_audit.json`):
  - `R0`: `0.004006 [0.003408, 0.004651]`
  - `SNAPscarp2p0px`: `0.004804 [0.004033, 0.005685]` (`+0.000798` vs R0)
  - `SNAPscarp1p4px`: `0.004556 [0.003803, 0.005445]` (`+0.000550` vs R0)
  - `SNAPpot2p0px`: `0.004575 [0.003902, 0.005273]` (`+0.000569` vs R0)
- **Single-feature leakage canaries** (symmetric AUC on hidden catalogue folds): `Band 3 tmi_hg = 0.5012`, `Band 5 iso_grav_anom_slope = 0.5511`, `Band 19 det_elev_slope = 0.5531`, `||grad Band 19|| = 0.5685` — max `0.5685 << 0.90` (`REPORT_ONLY_PASS`).
- **USGS SGMC off-catalogue bedrock control `PROXY`** (`n = 62,703` pixels `>3 px` from catalogue): `R0 = 0.096060`; `SNAPscarp2p0px = 0.098727` (`+0.002667`); `SNAPscarp1p4px = 0.097540` (`+0.001480`); `SNAPpot2p0px = 0.092757` (`-0.003303`).

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12 manifest pins into gitignored `.cache/gems_inputs/`).
3. `python scripts/build_snap_variants.py` (rebuilds R0 byte-for-byte, generates all 6 GeoTIFFs in `releases/`, re-reads from disk, runs format gates, and writes `evidence/snap_variants.json`).
4. `python scripts/report_snap_proxies.py` (computes report-only diagnostics in `evidence/snap_proxy_audit.json`).
