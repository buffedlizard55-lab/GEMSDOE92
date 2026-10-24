# Candidate handoff — human review and submission only

**✅ OK TO DOWNLOAD AND SUBMIT — verified.** The green-banner file at the top of [index.html](index.html) re-passed 10/10 MUST gates after being written and independently re-read from disk (values in [0,1], 0 NaN inside, EPSG:32611, 3730×3292, float32, 1 band, zero catalogue mass). If you see ✅ there, the portal error “Predicted values must be in range [0,1]” is fixed for this file.

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot (the NaN-outside primary `.tif` and `-zeros.tif` fallback carry identical in-footprint values and score identically).

## Current session candidates (AXIS = DILATATION, geodetic dilatation tercile reallocation, 2026-10-25)

All three candidates preserve exact R0 dot count (37,654 binary unit-mass dots), R0 catalogue exclusions (zero catalogue mass, `d_cat > 2.0 px`), and shift mass strictly from low/mid-dilatation dots (≤7.24 nstrain/yr) into highest-prior exact-expected-DTI H19-5 pixels within the high-dilatation tercile (≥7.24 nstrain/yr). Form notes are ≤140 characters. Prior is `0.70·dilatation + 0.30·TMI/grav/scarp` on ridges, no catalogue information.

| Order | Primary file (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Form note (≤140 chars) | % changed / dots moved | Primary SHA-256 (`-zeros` SHA-256) | Format receipt |
|---:|---|---|---|---|---|---|---|
| 1 | `docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b.tif` | `docs/downloads/h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b-zeros.tif` | `GEMSDOE92-DILATATION-p12-20261025` | `h33-h33-2-b2; DILATATION shift 4518 dots (12%) low→high dilat; pred MODEL:+0.007` (84 chars) | `12.00%` (4,518) | `8b4d248b6801f3f47c8748c3c32ce6892c121a3bf5710f899bafd2b6e8b47b89` (`25ba17a26d31df9d574fba2a2f34d03ff58f587f4ffde092dcc4bba9822f8898`) | Disk reread PASS + `gems.gates` 10/10 PASS; EPSG:32611; 3730×3292; exact `sample_submission.tif` transform; float32, 1 band; values in [0,1]; 0 NaN inside; NaN outside (primary) / 0 outside (fallback); 37,654 dots; 0 catalogue mass; min `d_cat = 2.236 px`. |
| 2 | `docs/downloads/h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88.tif` | `docs/downloads/h33-h33-2-b2-DILATATIONp10dilatation-20261025-2e501f88-zeros.tif` | `GEMSDOE92-DILATATION-p10-20261025` | `h33-h33-2-b2; DILATATION shift 3765 dots (10%) low→high dilat; pred MODEL:+0.005` (84 chars) | `10.00%` (3,765) | `2e501f8823be4b33ae06e96ffdcf22aa94fa552bcee518010eb6817a8f0410e5` (`d3b0d4a65aacff6b962056e7a4245734bef89ed72fa54767fe8b9ea3746e8aea`) | 10/10 PASS; same grid; 0 NaN inside; 37,654 dots; 0 catalogue mass. |
| 3 | `docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432.tif` | `docs/downloads/h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif` | `GEMSDOE92-DILATATION-p15-20261025` | `h33-h33-2-b2; DILATATION shift 5648 dots (15%) low→high dilat; pred MODEL:+0.006` (84 chars) | `15.00%` (5,648) | `ebc1b43246eb01d239fb7c9a564118a7a7d35b986c42c7b21c5f229a6d6dce1d` (`cc79c48ae0f46b0c22cd410305a773e72b719833718bceed2c5bcda3c8c38052`) | 10/10 PASS; same grid; 0 NaN inside; 37,654 dots. |

p12 is the primary (balanced dose, HOLDOUT Δ+0.00177 [0.00111,0.00246] vs R0). p10 most conservative, p15 most aggressive. Pick **one** per weekly slot; never both twins of a pair.

## Report-only diagnostics (PROXY, never gates or scores)

- **Catalogue hide-and-recover PROXY** (`n = 22,663` withheld catalogue positives, paired spatial-cluster bootstrap 95% CI, `evidence/dilatation_proxy_audit.json`):
  - `R0`: `0.004006 [0.003424, 0.004690]`
  - `p10dilatation`: `0.005747 [0.004867, 0.006788]` (`+0.00174` vs R0)
  - `p12dilatation`: `0.005779 [0.004863, 0.006851]` (`+0.00177` vs R0)
  - `p15dilatation`: `0.005818 [0.004838, 0.006912]` (`+0.00181` vs R0)
  - All deltas CI exclude 0 (157 clusters, 1,000 draws, seed 520810).
- **Single-feature leakage canaries** (symmetric AUC on hidden catalogue folds): Band 8 `geod_dilaterate` `0.514`, Band 7 `geod_shearrate` `0.513`, Band 4 `geod_2ndinv` `0.510`, Band 15 `depth_to_base_surf` `0.515`, Band 17 `cond_surf` `0.506` — max `0.515 << 0.90` (REPORT_ONLY_PASS).
- **USGS SGMC off-catalogue bedrock control PROXY** (`n = 62,703` pixels `>3 px` from catalogue): R0 `0.096060`; p10 `0.083547` (`-0.012513`), p12 `0.081467` (`-0.014593`), p15 `0.079888` (`-0.016172`) — expected: SGMC bedrock faults are range-core, not dilating piedmonts.

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12 pins into `.cache/gems_inputs/`)
3. `python scripts/build_dilatation_variants.py` (rebuilds R0 byte-for-byte, generates all GeoTIFF pairs in `releases/` and `docs/downloads/`, re-reads from disk, runs format gates, updates ledger/evidence)
4. `python scripts/report_dilatation_proxies.py` (pooled holdout + canaries + SGMC → `evidence/dilatation_proxy_audit.json`)
5. `make test` — 97 tests pass with no competition data.
