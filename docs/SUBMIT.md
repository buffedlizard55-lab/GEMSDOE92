# Candidate handoff — human review and submission only

**Do not upload until you confirm the entity's rolling-week quota and review the
file yourself.** The agent never submits and never contacts the leaderboard. Parent
R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a
`RECEIPT`. Upload **at most one** file per slot: the NaN-outside primary and the
`-zeros.tif` fallback contain identical in-footprint values and score identically.

## 2026-10-24 session — `AXIS = CONCENTRATION`, 1 km blocks, count 37,654 fixed

All three preserve the dot count (37,654 binary unit-mass dots), emit **zero mass
on the catalogue**, keep every inherited dot exactly where R0 had it
(`min d_cat = 2.236 px`, R0's own rule), place every **new** dot at `d_cat >
3.16 px`, and differ **only** in the 1 km block prior / direction. Form notes are
`<=140` characters.

| Order | Primary (NaN outside) | Fallback (`-zeros`) | Submission name | Form note | Primary / fallback SHA-256 | Format receipt |
|---:|---|---|---|---|---|---|
| 1 | `releases/h33-h33-2-b2-CONCENTRATIONcatd10-20261024-c313194a.tif` | `…-c313194a-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONcatd10-20261024-c313194a` | `h33-h33-2-b2; CONCENTRATION 1km, 10% dots to top catalogue-density blocks; pred MODEL:+0.013` (96) | `c313194ad749bd6bf401a7b6259b0d99dcae4f417284ae4b70e091445a696ac5` / `8c9605a6023d261495c7397ad064bf7d6f6eba30eb60c3705d0dadcaf8f2af64` | Disk reread + `gems.gates` PASS; EPSG:32611; 3730×3292; exact `sample_submission.tif` transform; float32, 1 band; values ∈[0,1]; 0 NaN inside; NaN outside; 37,654 dots; 0 catalogue mass; new-dot `min d_cat 3.16 px`; `min_nn 1.0 px` (see caveat) |
| 2 | `releases/h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8.tif` | `…-b93a4cf8-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8` | `h33-h33-2-b2; CONCENTRATION 1km, 10% dots to top TMI/grav/scarp-prior blocks; pred MODEL:-0.008` (107) | `b93a4cf8dd01ee1cdc6cf3dc3640e5e36f7baa369b468300b90147a5f8968f3f` / `7fa6cea4a4a155d7407cf8e0c204d21b9d73c7c94dd3b023797a2933d1c56277` | same gates; new-dot `min d_cat 3.16 px`; `min_nn 1.0 px` |
| 3 | `releases/h33-h33-2-b2-CONCENTRATIONcatdS10-20261024-6b87f2d7.tif` | `…-6b87f2d7-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONcatdS10-20261024-6b87f2d7` | `h33-h33-2-b2; CONCENTRATION mirror: 10% dots OFF catalogue-density blocks; pred MODEL:-0.070` (102) | `6b87f2d7876dc776f3d961c2fbee1b5696c5655c4c433258911e6f317e6a6ffe` / `417f952beee24b2a8b3585d2c86bdf062d3df9a06e2f56ebbc49cc18b4534388` | same gates; new-dot `min d_cat 39.1 px`; `min_nn 1.0 px` |

**Caveat the human must accept for all three:** the parent's `2.828 px` D2.8
spacing floor is **not** preserved. Only 90 legal ridge-mask pixels in the whole
study area lie `≥ 2.83 px` from every parent dot, so a count-preserving
reallocation of 3,765 dots is impossible at that floor. Arrivals land 1.0-1.4 px
from a survivor (98-100% within 2.83 px), i.e. they duplicate part of a
neighbour's kernel footprint and still pay `+1` of denominator mass. The measured
mechanical cost of that is `-0.013` / `-0.016` / `-0.021` respectively
(`model_flat_prior` in `evidence/concentration_variants.json`). **If you are not
willing to accept sub-floor spacing, upload `SNAPscarp2p0px` instead and skip this
session's files** — the spacing-preserving SNAP candidates from 2026-10-23 remain
valid and are listed in `evidence/snap_variants.json`.

## Which one, if only one

Slot 1 (`catd10`) is the only model-positive candidate. Slot 3 (`catdS10`) is a
**sign test, not a bet**: submit it only if Slot 1 lands `≥ +0.01` (confirmation)
or `≤ -0.01` (inversion check). Detail in `SLOT_PLAN.md`.

## Report-only diagnostics (PROXY, never gates or scores)

Source: `evidence/concentration_proxy_audit.json`.

- Catalogue hide-and-recover (`n = 22,663` withheld positives, buffered 20 km
  components): R0 `0.004006`; `catd10` `0.004011`; `phys10` `0.003592`;
  `catdS10` `0.002106`. The instrument is **flat for `catd10`** (dots moved beside
  the *kept* catalogue, not the withheld one) and low for `catdS10` (it genuinely
  depopulates the collar) — neither is a score.
- Leakage canaries (symmetric AUC): band 3 `0.501`, band 5 `0.551`, band 19
  `0.553`, `||grad band 19||` `0.569` — max `0.569 << 0.90`, no stop condition.
- USGS SGMC off-catalogue bedrock control: R0 `0.096060`; `catd10` `0.092346`
  (`-0.003714`); `phys10` `0.087633` (`-0.008427`); `catdS10` `0.089210`
  (`-0.006850`). Negative for all three: the reallocation moves mass away from
  independently mapped bedrock faults. Reported, not gated.

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12
   pins into gitignored `.cache/gems_inputs/`; ~440 MB download).
3. `python scripts/build_concentration_variants.py` (rebuilds R0 byte-for-byte,
   builds the priors and the three variants, re-reads each GeoTIFF from disk, runs
   the format gates, writes `evidence/concentration_variants.json` and appends the
   three ledger rows).
4. `python scripts/report_concentration_proxies.py` (report-only diagnostics).
