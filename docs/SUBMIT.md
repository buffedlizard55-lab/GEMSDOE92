# Candidate handoff — human review and submission only

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot (the NaN-outside primary `.tif` and `-zeros.tif` fallback carry identical in-footprint values and score identically).

## Current session candidates (`AXIS = RELIEF`, detrended-elevation terciles, 2026-10-24)

All three candidates preserve exact R0 dot count (`37,654` binary unit-mass dots), total mass (`37,654.0`), `H19-5` corridor support, zero catalogue mass, `d_cat > 3.0 px` on 100% of newly added dots (`d_cat > 2.0 px` on surviving inherited R0 dots), and `D1.5` non-cardinal inter-dot spacing (`min_nn = 1.4142 px`), shifting **exact `11.0002%` (`4,142` dots)** between equal-area `Band 12 (det_elev)` structural-relief terciles (`Basin <= -142.91 m`, `Piedmont (-142.91, +38.75] m`, `Range-front > +38.75 m`) via within-tercile `Band 19 (det_elev_slope)` + break-in-slope exact marginal DTI. Form notes are `<=140` characters.

| Order | Primary file (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Form note (`<=140` chars) | Changed (`%`) & tercile shift | Primary SHA-256 (`-zeros` SHA-256) | Format receipt |
|---:|---|---|---|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-RELIEFbasin11pct-20261024-2d06de50.tif` | `releases/h33-h33-2-b2-RELIEFbasin11pct-20261024-2d06de50-zeros.tif` | `h33-h33-2-b2-RELIEFbasin11pct-20261024-2d06de50` | `h33-h33-2-b2; RELIEF +11% mass to Basin (4142 dots, fixed 37654); pred MODEL:+0.008` (83 chars) | `4,142` (`11.0002%`); Basin `20.43% -> 31.43%` (`7,692 -> 11,834`) | `2d06de502fbe0a00f958b767fe35979505f2ba9718bc2fa8e2efd9e01b7a347c` (`0595c9ed6dd2e12264f7329106a5b821ff9591c5b0fcafeb64a4ad99518c1d5e`) | Disk reread PASS + `gems.gates` PASS (declared inherited R0 `2<d_cat<=3` collar `1,882 <= 2,171`; `0` added dots `<=3.0 px`); `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; `min_nn = 1.414 px`. |
| 2 | `releases/h33-h33-2-b2-RELIEFpiedmont11pct-20261024-455a16f0.tif` | `releases/h33-h33-2-b2-RELIEFpiedmont11pct-20261024-455a16f0-zeros.tif` | `h33-h33-2-b2-RELIEFpiedmont11pct-20261024-455a16f0` | `h33-h33-2-b2; RELIEF +11% mass to Piedmont (4142 dots, fixed 37654); pred MODEL:+0.005` (86 chars) | `4,142` (`11.0002%`); Piedmont `41.81% -> 52.81%` (`15,742 -> 19,884`) | `455a16f0663bd20e0745e6c54f59bff996fadc5198dad1292df3b05c26b18042` (`8ed1c29fe76a2b92f11226bae7fb81b9b23a465a2b2355a47924e39ec46a172f`) | Disk reread PASS + `gems.gates` PASS (declared inherited R0 `2<d_cat<=3` collar `1,880 <= 2,171`; `0` added dots `<=3.0 px`); `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; `min_nn = 1.414 px`. |
| 3 (bedrock control) | `releases/h33-h33-2-b2-RELIEFrangefront11pct-20261024-9909bb67.tif` | `releases/h33-h33-2-b2-RELIEFrangefront11pct-20261024-9909bb67-zeros.tif` | `h33-h33-2-b2-RELIEFrangefront11pct-20261024-9909bb67` | `h33-h33-2-b2; RELIEF +11% mass to Range-front (4142 dots, fixed 37654); pred MODEL:-0.005` (89 chars) | `4,142` (`11.0002%`); Range-front `37.72% -> 48.72%` (`14,204 -> 18,346`) | `9909bb675e23d59fbce0c084f33f8bf7a58be22bc8c82d5e606bc0f3a6b9586e` (`6d250a1a7e4dc39fe3550fffd0e48bada54b097c052fa1ec77637c77581e0696`) | Disk reread PASS + `gems.gates` PASS (declared inherited R0 `2<d_cat<=3` collar `1,874 <= 2,171`; `0` added dots `<=3.0 px`); `EPSG:32611`; `3730x3292`; exact `sample_submission.tif` transform; `float32`, 1 band; values in `[0,1]`; 0 NaN inside footprint; NaN outside; 37,654 unit-mass dots; 0 catalogue mass; `min_nn = 1.414 px`. |

*(Portfolio note per `SLOT_PLAN.md`: to test 3 orthogonal axes in one rolling week, pair `RELIEFbasin11pct` [Slot 2] with `h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24` [Slot 1, `evidence/snap_variants.json`] and `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` [Slot 3, `evidence/prune_rungs.json`]; hold `RELIEFpiedmont11pct` and `RELIEFrangefront11pct` for conditional Week-2 relief resolution.)*

## Report-only diagnostics (`PROXY`, never gates or scores)

- **Catalogue hide-and-recover `PROXY`** (`n = 22,663` withheld catalogue positives, paired 20 km spatial-block bootstrap 95% CI, `evidence/relief_proxy_audit.json`):
  - `R0`: `0.004006 [0.003415, 0.004664]`
  - `basin11pct`: `0.003192 [0.002637, 0.003817]` (`-0.000814` vs R0 — reflects ~13% fewer inherited `2.0<d_cat<=3.0` collar dots because all newly added dots strictly enforce `d_cat > 3.0 px`)
  - `piedmont11pct`: `0.003262 [0.002714, 0.003882]` (`-0.000744` vs R0)
  - `rangefront11pct`: `0.003257 [0.002747, 0.003794]` (`-0.000749` vs R0)
- **Single-feature leakage canaries** (symmetric AUC on hidden catalogue folds): `Band 12 det_elev = 0.5027`, `Band 19 det_elev_slope = 0.5526`, `||grad Band 19|| = 0.5676` — max `0.5676 << 0.90` (`REPORT_ONLY_PASS`).
- **USGS SGMC off-catalogue bedrock control `PROXY`** (`n = 62,703` pixels `>3 px` from catalogue, 63.6% situated in exposed `Range-front` bedrock): `R0 = 0.096060`; `basin11pct = 0.091736` (`-0.004324`); `piedmont11pct = 0.091842` (`-0.004218`); `rangefront11pct = 0.095652` (`-0.000408`).

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12 manifest pins into gitignored `.cache/gems_inputs/`).
3. `python scripts/build_relief_variants.py` (rebuilds R0 byte-for-byte, generates all 6 `RELIEF` GeoTIFFs in `releases/`, re-reads from disk, runs format gates, and writes `evidence/relief_variants.json`).
4. `python scripts/report_relief_proxies.py` (computes report-only diagnostics in `evidence/relief_proxy_audit.json`).
