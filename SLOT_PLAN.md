# SLOT_PLAN

Parent R0 = `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots, 0.2778 `CLAIM`.
Target = `TOP_PUBLIC` (currently **unset** — the plan below is target-agnostic).
3 scored slots per rolling week. Deadline 2026-12-03 (confirm on the problem page).

## The three next slots, in order

### 1. `PRUNE-le3px` — widen the only prune that ever paid
R0 is the `<=2 px` prune (0.2708 -> 0.2778, delta +0.0070 `CLAIM`). `<=2` is the
one cell in the lineage that moved the score in the intended direction. The
adjacent cell, `<=3 px`, is unbuilt and costs nothing new to construct: same
builder, same refill rule, radius 3.
- **Mechanism**: dots sitting on known traces are already credited to the
  catalogue, so they burn denominator mass without new numerator credit.
  Widening the radius should remove more of that dead mass.
- **Confounder**: the 0.2708 -> 0.2778 gain may have come from removing a
  handful of false positives that happened to be near traces, not from a general
  "distance from known faults" prior. If so, `<=3 px` removes genuine new-fault
  pixels (the forum answer says new truth *can* lie within 300 m of known
  traces, i.e. 3 px) and will fall.
- **Predicted**: +0.002 to +0.006 if the prior generalises; flat-to-negative if
  not. This is a cheap falsifier for the whole PRUNE story.
- **Result changes what**: a gain keeps PRUNE as the spine and makes `<=4 px`
  worth a shot; a loss says stop widening and treat R0's gain as
  false-positive removal, which redirects effort to CONCENTRATION.

### 2. `CONCENTRATION-blk10px` — 1 km blocks, 15% of dots moved up-prior
Block size 10 px = 1 km at 100 m. Report block-density CV before and after; the
brief notes best files reportedly sit at CV 0.51-0.59.
- **Mechanism**: faults are spatially clustered at km scale (step-over,
  intersection, termination). Uniform-ish dot density wastes mass in blocks with
  no structural reason to host a fault.
- **Confounder**: the "prior" is a km-scale favourability surface built from the
  Faulds inventory of *known* geothermal systems. If the test region's new faults
  are in systems absent from that inventory, concentration actively hurts.
- **Predicted**: +0.005 to +0.015 `MODEL`, the biggest single-axis upside here,
  with a real tail risk of -0.02.
- **Result changes what**: a gain favours the clustering hypothesis and licenses
  a combined PRUNE+CONCENTRATION file; a loss says dot *placement* is already
  near-optimal and the remaining headroom is MASS/ranking.

### 3. `MASS-drop10` — remove the worst 10% by the parent's own ranking
- **Mechanism**: a dot pays only if its credit exceeds `0.2*DTI` (~0.056 at
  0.28). Dots at the bottom of the ranking contribute less than they cost.
- **Confounder**: mass is confounded with field across the whole ledger (brief
  section 3), and at least 8 slots historically went to exact repeats. A
  MASS result may reflect a count effect rather than a ranking effect.
- **Predicted**: +0.003 to +0.010 `MODEL`.
- **Result changes what**: a gain means the ranking is informative and worth
  using to *place* new dots; a loss means the surviving 90% were not the weak
  ones, which weakens every ranking-based axis downstream.

## Deliberately not in the next three
- `SNAP` — needs a TMI/gravity-gradient band; only worth a slot once the Axes 1-3
  results tell us placement is the bottleneck. Highest risk of silently moving
  dots off real lineaments (the 400 m flight-line spacing means positional
  uncertainty is about the kernel radius).
- `RELIEF` — the relief terciles are a weak prior for *fault pixels*; the
  inventory describes where systems sit, never the target.
- `SPACING` — lowest priority per the brief.
- `TRACKB` — Phase 2 artefact, not a weekly-slot candidate.

## Better axes to consider (proposed, NOT built)
1. **MASS-SHAPE (variable p).** Every candidate so far is unit-mass dots, so the
   file says nothing about *which* dots deserve more mass. Giving the top decile
   p = 2 and the rest p = 1 tests the same ranking axis with a different
   instrument, and the algebra says marginal credit is linear in p while the
   denominator penalty is not. *Confounder*: mass and count move together again.
   *Falsifier*: if `MASS-drop10` shows nothing, weighting cannot help either.
2. **KERNEL-AWARE SPACING.** Two dots 1 px apart duplicate most of their kernel
   credit while paying twice in `S`. Deduplicating dot pairs closer than 1 px is
   a mass cut with a physical justification, not a ranking guess. *Confounder*:
   R0's lattice-like construction may already be effectively deduplicated.
   *Falsifier*: report the count of sub-1-px pairs in R0 first; if it is ~0, the
   axis is dead on arrival and should not take a slot.
3. **COMMUNITY PRIOR.** Cluster dots into >=1 km strike-consistent segments and
   add mass at segment *ends* and step-overs only. *Confounder*: this is TRACKB
   in disguise and needs geologist review before it burns a slot.

## Calendar to 2026-12-03
~6 weeks. wk1-2: the three slots above. wk3-4: combine the two best axes into
one file, plus one slot held for the combination's best parent-diff. wk5-6:
confirm, choose the final file **and** a fallback, re-validate the format of
both. Never spend the final slot without a second validated file in `releases/`.
