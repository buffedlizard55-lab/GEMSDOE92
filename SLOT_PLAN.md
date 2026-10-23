# SLOT_PLAN — PRUNE axis session 2026-10-23

Deadline 2026-12-03 (confirm on the competition page). One entity, 3 scored
submissions per rolling week, one final file chosen blind.

## Parent
`h33-h33-2-b2` (GEMSDOE32): 37,654 unit-mass dots, CLAIM 0.2778 (still no
receipt). sha256 `baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd`
— **verified byte-for-byte this session**, so the parent gate passes and
descendants are trustworthy.

## Why PRUNE
The previous session took MASS (3 files, unsubmitted). The brief says each
(AXIS, value) cell is built once across sessions, so MASS is spent. PRUNE is the
next cell for a concrete reason: the parent keeps ≥2.24 px from the catalogue
but still holds 2,171 dots (5.77%) within the 3 px physical uncertainty radius.
That is an unexamined 5.77% of the budget sitting in the class of pixels the
metric is least likely to reward, and the previous session explicitly deferred
it (see IRREGULARITIES 2026-10-23, "Parent distance vs new hard constraint").

## This session — 3 doses, one axis

| slot | file | n_dots | % changed | predicted | mechanism |
|---|---|---|---|---|---|
| 1 (best bet) | `h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7` | 37,654 | 5.77% | +0.002 to +0.006 MODEL | dots within 300 m of known traces are positional scatter, not distinct faults |
| 2 | `h33-h33-2-b2-PRUNE_B4-20261023-78e893d7` | 37,654 | 10.16% | +0.001 to +0.004 MODEL | 400 m, past survey uncertainty; pays only if dead mass is thick |
| 3 | `h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad` | 37,654 | 14.97% | −0.002 to +0.002 MODEL | negative control; should be worst if the effect is bounded |

All three: float32, EPSG:32611, 100 m, parent transform, values in [0,1], zero
catalogue mass, NaN outside footprint (primary) and zeros outside (fallback),
count and total mass held at exactly 37,654, re-read from disk after writing,
all 10 format gates PASS. Parent-diff verified independently: the removed set is
exactly `{distance to catalogue ≤ R}` and nothing else moved.

## What each result would change
- **B3 beats parent by ≥0.01** → the distance prior is real and worth combining;
  next session builds `PRUNE_B3 × CONCENTRATION`, and B3 becomes the new anchor.
- **Monotone improvement with radius (B5 best)** → prior is stronger than the
  survey geometry suggests; go deeper (B8, B10) before touching another axis.
- **All three at or below parent** → the distance prior is false, and the
  historical 0.2708→0.2778 step was false-positive removal that does not
  generalise. Kill PRUNE and redirect to CONCENTRATION.
- **All within ±0.01 (no evidence)** → do not conclude; the public chunks are a
  subset of the region and a sub-0.01 move is not evidence of anything.

## Next 3 slots after this (if a PRUNE dose wins)
1. `CONCENTRATION-blk10px` — move 15% of dots from the lowest-prior 1 km blocks
   to the highest. Report block-density CV before/after (best files reportedly
   0.51–0.59). Confounder: the prior comes from known geothermal systems, so it
   misses systems absent from the inventory.
2. `PRUNE_B3 × CONCENTRATION` — combine the two best axes at the winning dose.
3. `SNAP-max2px` — move each dot ≤2 px onto the strongest TMI/gravity-gradient
   edge. Only worth a slot once placement is shown to be the bottleneck.

`RELIEF` and `SPACING` stay behind these; `TRACKB` is Phase 2 work.

## Not computed, on purpose
- **Catalogue hide-and-recover PROXY**: every variant differs from the parent
  *precisely in its relation to the catalogue*, so a catalogue-based holdout
  cannot discriminate between them by construction. Reporting it here would be a
  circular number dressed as evidence.
- **Leakage canary**: no per-pixel feature enters the selection, so there is no
  feature to test.
- **SGMC control**: not available in the pinned manifest.

## Calendar to 2026-12-03
~6 weeks, ~18 slots max. wk1-2 (now): PRUNE doses. wk3-4: CONCENTRATION, then
the two best axes combined. wk5-6: confirm, choose the final file **and** a
fallback, re-validate both.

## Human actions
- Fill `TOP_PUBLIC` from the leaderboard with a date. Nothing here needs it.
- Submit **B3 first**; record the receipt date and score in
  `ledger/submissions.csv` (`receipt_score`, `receipt_date`).
- Confirm the 0.2778 parent CLAIM against saved receipts if any exist.
