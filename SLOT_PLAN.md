# SLOT_PLAN — GEMS Prize #306

**Incumbent / Parent R0:** `h33-h33-2-b2` (37,654 unit-mass dots; both `zeros` `c55bafc4…` and `nan` `baeae321…` SHA-256 digests rebuilt byte-for-byte from the pinned lineage this session). Score `0.2778` is **CLAIM** until a submission-page receipt is recorded in `ledger/submissions.csv` (18 `BUILT` candidates, zero `RECEIPT` rows).
**Target & Quota:** `TOP_PUBLIC = ____` (date: `____`); rolling-week slots left: `__ / 3`; total to `2026-12-03`: `__` (confirm on the competition page). Never submit both encodings of one pair. Treat live public-chunk deltas with `|delta| < 0.01` as **no evidence**.

## Next 3 Live Slots (in priority order, conditional on human quota check)

1. **`h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24`** (carried over) — `<=2.0 px` scarp+break+TMI/vertical-gradient snap, 82.05% px changed, mean disp `1.234 px`, `min_nn = 2.8284 px`. Prediction `MODEL:+0.012` (`[-0.006,+0.025]`); non-leaky `PROXY` support: hide-and-recover `+0.000798`, SGMC `+0.002667`.
   - *Decision rule:* `>= +0.01` promotes SNAP as the new receipt-backed parent for wk3–4 combination; `<= -0.01` retires the surface-scarp operator.
2. **`h33-h33-2-b2-CONCcatblk10up10-20261024-c9503d48`** (new, this session) — CONCENTRATION on 1 km known-fault-density blocks: `3,765` dots (10.0%) leave zero-catalogue blocks and fill the highest-prior H19-5 holes; file prior `0.0122 → 0.0142`; `min_nn` floor `2.0 px` (declared); `CV_occ 0.619 → 0.648`. Prediction `MODEL:+0.006` (`[-0.008,+0.020]`).
   - *Decision rule:* `>= +0.01` says new-fault truth is enriched in the catalogue halo → next session should push the same prior to 2 km blocks and pair it with PRUNE; `<= -0.01` says the catalogue is exhausted ground → run `CONCcatblk10dn10` once as the sign check before abandoning km-scale priors.
3. **`h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277`** (carried over, `MODEL:+0.003`) — orthogonal collar test that unlocks a future `SNAP + PRUNE` or `CONCENTRATION + PRUNE` composite.
   - *Decision rule:* `>= +0.01` makes the 3.5 px collar a permanent feature of every later parent; `<= -0.01` closes the PRUNE ladder at the incumbent's own 2 px rule.

Held in reserve (only if a slot is otherwise idle): `CONCcatblk10up20` (`MODEL:+0.004`, saturated dose — the prior can absorb only `4,054` dots above `0.002` at the 2.0 px floor, so the extra 3,765 movers land on near-zero prior ground) and `CONCcatblk10dn10` (`MODEL:-0.006`, the direction test). The up/down pair is the only clean read on whether the known-fault prior predicts new-fault truth at 1 km.

## Schedule to Deadline (2026-12-03, ~6 weeks)

- **Weeks 1–2 (to 2026-11-05): single-axis screening.** Spend the remaining slots on Slots 1–3 above; transcribe every receipt and date into `ledger/submissions.csv`. Do **not** build more single-axis files until at least one receipt exists — 18 BUILT candidates and zero receipts is the binding problem, not candidate supply.
- **Weeks 3–4 (2026-11-06 to 2026-11-19): orthogonal combination.** Combine only axes with receipt-backed gains `>= +0.01`, one controlled change per step from the best receipted parent. Likely pair: SNAP displacement `+` the better of PRUNE-3.5 px / CONCENTRATION.
- **Weeks 5–6 (2026-11-20 to 2026-12-03): confirmation and blind final.** Re-confirm the top composite once, lock ONE final file plus ONE fallback, re-validate both from disk against `sample_submission.tif`, and finish `AI_USE.md` and the reproducible-code archive.

## Proposed Better Axes (not built this session)

- **`SPACING_FLOOR` (now the highest-value follow-up).** Measured this session: R0 is a *saturated* D2.8 packing — only `794` legal H19-5 pixels exist at `>= 2.8284 px` from a dot, `9,760` at `>= 2.0 px`, `29,114` at `>= 1.414 px`. Every "add or relocate" axis is therefore capacity-bound. A spacing axis at matched count (re-thin H19-5 at D2.0/D1.5 and keep 37,654 dots by the km-scale prior) would measure the packing density the metric actually wants. *Confounder:* tighter packing inflates redundant kernel credit (`M`) and can double-cover the same strand. *Falsifier:* receipt `<= -0.01` vs R0 for the tighter pack, or `>= +0.01` for a looser D3.2 pack.
- **`FAULT_HALO_2KM`.** Same CONCENTRATION machinery, prior sigma `2 km` instead of `1 km`, 10% dose — tests the width of the enrichment halo around known systems (fault damage zones are 1–3 km wide). *Confounder:* a wider halo is closer to "put dots everywhere", so the null is diluted. *Falsifier:* receipt indistinguishable from `catblk10up10`.
- **`TRACKB` (Phase 2, human-authorised only).** Strike-consistent traces `>= 1 km` from R0's top-ranked dots as GeoJSON + raster, one evidence paragraph per trace.
