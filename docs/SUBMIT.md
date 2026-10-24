# Candidate handoff — human review and submission only

**Do not upload until you confirm the entity's rolling-week quota and independently review the selected raster.** The agent never submits and never contacts the leaderboard. Parent R0 (`h33-h33-2-b2`) score `0.2778` is an owner-reported **CLAIM**, not a `RECEIPT`. Upload **at most one** file per slot (the NaN-outside primary `.tif` and `-zeros.tif` fallback carry identical in-footprint values and score identically).

## This session's candidates (`AXIS = CONCENTRATION`, 1 km blocks, known-fault prior, 2026-10-24)

All three preserve R0's exact dot count and mass (`37,654` binary unit-mass dots, `mass = 37,654`), keep every inherited dot at its exact parent position, keep every dot on the parent's H19-5 evidence support, and enforce the parent's `d_cat > 2.0 px` rule. Every **moved** dot additionally clears the catalogue by `> 3.0 px` (brief constraint 4). One declared secondary change, identical across all three arms: moved dots are placed on a `>= 2.0 px` spacing floor instead of the parent's `2.8284 px` — because R0 is a saturated D2.8 packing and only `794` legal H19-5 destination pixels clear `2.8284 px`.

Prior: km-scale Gaussian KDE of the pinned known-fault catalogue (`sigma = 1 km`), block mean over `10 px = 1 km` blocks. Organizer basis for the prior: new-fault truth includes newly mapped geometry of existing systems and can lie within 300 m of known traces (`community.drivendata.org/t/.../11516`, `.../11536`).

| Order | Primary (NaN outside) / fallback (`-zeros`) | Submission name | Form note (<=140 chars) | Moved | File prior | Primary SHA-256 (`-zeros`) | Format receipt |
|---:|---|---|---|---|---|---|---|
| 2 | `releases/h33-h33-2-b2-CONCcatblk10up10-20261024-c9503d48.tif` / `...-c9503d48-zeros.tif` | `h33-h33-2-b2-CONCcatblk10up10-20261024-c9503d48` | `h33-h33-2-b2; CONC 1km known-fault prior, 10% up; 3765 moved; pred MODEL:+0.006` (88) | 3,765 (10.00%) | 0.0122 -> 0.0142 | `cd5ae43ba6116418d09fb911baa0c05a8a0541e73f74275ce3f5feb3713f127e` (`c9503d4873924d833e311eebe56e220bad97acd21e701a7f4bac10af67e499f2`) | 13/13 disk reread PASS + `gems.gates` PASS; `EPSG:32611`; `3730x3292`; `float32`, 1 band; `[0,1]`; 0 NaN inside; 37,654 dots; 0 catalogue mass; `min_nn = 2.0000 px`; moved `d_cat > 3.0 px` |
| reserve | `releases/h33-h33-2-b2-CONCcatblk10up20-20261024-b6e80d73.tif` / `...-zeros.tif` | `h33-h33-2-b2-CONCcatblk10up20-20261024-b6e80d73` | `h33-h33-2-b2; CONC 1km known-fault prior, 20% up (saturated); pred MODEL:+0.004` (94) | 7,531 (20.00%) | 0.0122 -> 0.0142 | `a877e3aaecd3ce85c297280ff7fd1163379af3009d041d7b9a83908e1f26c985` (`b6e80d73fa67e26c91e3bebf7b86c5f4f51fb8b295f0247fd73a6e559afe2991`) | same 13/13; `min_nn = 2.0000 px`; 35.9% of pairs below 2.8284 px |
| reserve | `releases/h33-h33-2-b2-CONCcatblk10dn10-20261024-c671b704.tif` / `...-zeros.tif` | `h33-h33-2-b2-CONCcatblk10dn10-20261024-c671b704` | `h33-h33-2-b2; CONC 1km known-fault prior, 10% down (direction test); pred MODEL:-0.006` (102) | 3,765 (10.00%) | 0.0122 -> 0.0069 | `838bf4a157ed5139dc3fe4290021624a671215131c733e0624685a0330e6b337` (`c671b704cc671216f6b732769bab622ed6e75b42e59bfdcdb6b38cb37e6a51bc`) | same 13/13; `min_nn = 2.0000 px` |
| reserve (physics prior) | `releases/h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8.tif` / `...-b93a4cf8-zeros.tif` | `h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8` | `h33-h33-2-b2; CONC 1km on TMI/grav/scarp prior (not catalogue); pred MODEL:-0.008` (96) | `3,765` (10.0%) | physics `0.39-0.75` | `b93a4cf8dd01ee1cdc6cf3dc3640e5e36f7baa369b468300b90147a5f8968f3f` (`7fa6cea4a4a155d7407cf8e0c204d21b9d73c7c94dd3b023797a2933d1c56277`) | Disk reread + `gems.gates` 10/10 PASS; EPSG:32611; 3730x3292; float32, 1 band; values in [0,1]; 0 NaN inside; NaN outside; 37,654 dots; 0 catalogue mass; new dots `min d_cat = 3.16 px`; `min_nn = 1.0 px` (declared) |

Upload **at most one** file per slot, and never both encodings of a pair (they score identically). Slot order versus the backlog is in `SLOT_PLAN.md`; SNAP `scarp2p0px` still outranks these on predicted change and on non-leaky PROXY support.

## Report-only diagnostics (`PROXY`, never gates or scores)

**This session's two instruments are invalid for these arms.** The prior is built from the known-fault catalogue and the hide-and-recover instrument withholds catalogue components as pseudo-truth, so a gain is partly the prior looking at itself. Numbers are recorded, labelled `interpretable: false`, and are **not** evidence for or against the variants:

- catalogue hide-and-recover (`n = 22,663` withheld positives, paired 20 km block bootstrap, seeds 20/30): `R0 = 0.004006 [0.003424, 0.004690]`; `up10 = 0.004011 [0.003436, 0.004677]`; `up20 = 0.004008 [0.003432, 0.004656]`; `dn10 = 0.002099 [0.001636, 0.002597]`.
- USGS SGMC off-catalogue control: `R0 = 0.096060`; `up10 = 0.092966`; `up20 = 0.089916`; `dn10 = 0.092296` (`LOW_GAP` at `1e-5`).
- leakage canaries (symmetric AUC, hidden catalogue folds): `Band 3 tmi_hg 0.5012`, `Band 5 iso_grav_anom_slope 0.5511`, `Band 19 det_elev_slope 0.5531`, `||grad Band 19|| 0.5685`, design prior `0.9273` — the last is the expected signature of a deliberately label-derived prior, **not** hidden-label leakage (the catalogue is a provided input; the scored target is new-fault truth).

## Deterministic reproduction

1. `pip install -r requirements.txt`
2. `python scripts/restore_inputs.py` (restores and SHA-256/byte-verifies all 12 manifest pins into gitignored `.cache/gems_inputs/`).
3. `python scripts/build_concentration_variants.py` (rebuilds R0 byte-for-byte through `dot_thin(H19-5, 2.8) & d_cat > 2.0`, builds the 3 CONCENTRATION GeoTIFF pairs in `releases/`, re-reads every file from disk, runs the format gates, appends ledger rows and writes `evidence/concentration_variants.json`).
4. `python scripts/report_concentration_proxies.py` (report-only diagnostics in `evidence/concentration_proxy_audit.json`; labelled leaky by construction).
5. Earlier sessions' files rebuild with `python scripts/build_snap_scarp_variants.py`, `python scripts/build_prune_variants.py`, `python scripts/build_prune_rungs.py` and `python scripts/build_mass_variants.py`.
