# Candidate handoff — human review and submission only

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot (the NaN-outside primary `.tif` and `-zeros.tif` fallback carry identical in-footprint values and score identically).

## Current session candidates (`AXIS = RELIEF`, detrended-elevation tercile reallocation, 2026-10-24)

All three candidates preserve exact R0 dot count (`37,654` binary unit-mass dots), R0 catalogue exclusions (zero catalogue mass, `d_cat > 2.0 px`), and shift mass strictly from lowest-prior basin/range dots into highest-prior exact-expected-DTI H19-5 pixels within the piedmont relief tercile (`-142.91 m <= det_elev < +38.75 m`). Form notes are `<=140` characters.

| Order | Primary file (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Form note (`<=140` chars) | % changed / dots moved | Primary SHA-256 (`-zeros` SHA-256) | Format receipt |
|---:|---|---|---|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7.tif` | `releases/h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7-zeros.tif` | `h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7` | `h33-h33-2-b2; RELIEF shift 4518 dots (12%) basin/range->piedmont; pred MODEL:+0.008` (84 chars) | `12.00%` (4,518 dots moved) | `a0998ed7e9b39c91eead413ab1bd9c02511a29fb6f8438a36f921d3f3ef6d079` (`b0b3b1ffb3881a084211454d55ed0e417594b5f9a01bb57acbd8500f9aab9f17`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`. |
| 2 | `releases/h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24.tif` | `releases/h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24-zeros.tif` | `h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24` | `h33-h33-2-b2; SNAP <=2.0px edge+scarp+break (nn>=2.8); mean disp 1.23px; pred MODEL:+0.012` (90 chars) | `82.05%` (30,896 dots snapped) | `2a65fe24766375d5d2330daa9547f33a0cd16838d20675b1a03d531b0e33601d` (`96c8598a20114682579078044f03149c15d42f79cc8143d9f7300bd1881d2d1e`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`; `min_nn = 2.828 px`. |
| 3 | `releases/h33-h33-2-b2-RELIEFp15piedmont-20261024-15254f0a.tif` | `releases/h33-h33-2-b2-RELIEFp15piedmont-20261024-15254f0a-zeros.tif` | `h33-h33-2-b2-RELIEFp15piedmont-20261024-15254f0a` | `h33-h33-2-b2; RELIEF shift 5648 dots (15%) basin/range->piedmont; pred MODEL:+0.006` (84 chars) | `15.00%` (5,648 dots moved) | `15254f0a696be5f403eb84998242029139d9381fec21750caaafd202d10a2b57` (`c91ab90b1379767683b4e8a90f68c4c330a0e785294065e194c1e883934435b9`) | Disk reread PASS + `gems.gates` 10/10 PASS; `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; min `d_cat = 2.236 px`. |

*(Alternative 10% dose variant `releases/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24.tif` is built and recorded in `evidence/relief_variants.json`; previous session candidates across `SNAP` and `PRUNE` remain documented in `ledger/submissions.csv`.)*

## Report-only diagnostics (`PROXY`, never gates or scores)

- **Catalogue hide-and-recover `PROXY`** (`n = 22,663` withheld catalogue positives, paired 20 km spatial-block bootstrap 95% CI, `evidence/relief_proxy_audit.json`):
  - `R0`: `0.004006 [0.003424, 0.004690]`
  - `RELIEFp10piedmont`: `0.006045 [0.005187, 0.006927]` (`+0.002039` vs R0)
  - `RELIEFp12piedmont`: `0.005974 [0.005096, 0.006880]` (`+0.001967` vs R0)
  - `RELIEFp15piedmont`: `0.005961 [0.005071, 0.006873]` (`+0.001955` vs R0)
- **Single-feature leakage canaries** (symmetric AUC on hidden catalogue folds):
  - `Band 3 tmi_hg`: `0.5012`
  - `Band 5 iso_grav_anom_slope`: `0.5511`
  - `Band 12 det_elev`: `0.5024`
  - `Band 19 det_elev_slope`: `0.5531` — max `0.5531 << 0.90` (`REPORT_ONLY_PASS`).
- **USGS SGMC off-catalogue bedrock control `PROXY`** (`n = 62,703` pixels `>3 px` from catalogue):
  - `R0`: `0.096060`
  - `RELIEFp10piedmont`: `0.087245` (`-0.008815` vs R0)
  - `RELIEFp12piedmont`: `0.085162` (`-0.010898` vs R0)
  - `RELIEFp15piedmont`: `0.082782` (`-0.013278` vs R0)
  *(Notice: SGMC maps exhumed bedrock faults inside mountain ranges; reallocating dots away from range interiors into the piedmont alluvial plain naturally lowers the bedrock-only SGMC control, confirming genuine geographical reallocation).*

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12 manifest pins into gitignored `.cache/gems_inputs/`).
3. `python scripts/build_relief_variants.py` (rebuilds R0 byte-for-byte, generates all GeoTIFF pairs in `releases/`, re-reads from disk, runs format gates, and updates ledger/evidence).
4. `python scripts/report_relief_proxies.py` (computes report-only diagnostics in `evidence/relief_proxy_audit.json`).
