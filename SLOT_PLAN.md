# SLOT_PLAN — GEMS Prize #306

**Incumbent / Parent R0:** `h33-h33-2-b2`, 37,654 unit-mass dots, both encodings
rebuilt byte-for-byte this session (`zeros c55bafc4…`, `nan baeae321…`). Score
`0.2778` remains a **CLAIM** — `ledger/submissions.csv` has **18 `BUILT` rows and
zero `RECEIPT` rows**.
**Target & quota:** `TOP_PUBLIC = ____` (date `____`), rolling-week slots `__ / 3`,
total to 2026-12-03 `__`. Human fills all three; nothing here assumes them.
Live deltas `|Δ| < 0.01` are **no evidence**. Never upload both twins of a pair.

## Next 3 live slots (2026-10-24 session built 3 CONCENTRATION candidates)

1. **`h33-h33-2-b2-CONCENTRATIONcatd10-20261024-c313194a`** — 1 km blocks, move
   10% (3,765) of dots from lowest- to highest-catalogue-density blocks; count and
   mass fixed; `MODEL:+0.013` `[-0.013,+0.040]`; mechanics-only cost `-0.013`.
   *Decision rule:* `≥ +0.01` ⇒ known-structure density is real at 1 km ⇒ Slot 3
   becomes `catdS10` to confirm the sign. `|Δ| < 0.01` ⇒ axis inert at 10% ⇒ Slot 3
   becomes `SNAPscarp2p0px` (below). `≤ -0.01` ⇒ catalogue is a mapping-effort
   artefact ⇒ Slot 3 becomes `catdS10` to test the inversion.
2. **`h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24`** (prior session, still
   `BUILT`, never scored) — `≤2 px` snap onto scarp + piedmont break + TMI/gravity
   edge, spacing preserved, `MODEL:+0.012`. Different mechanism (sub-kernel
   positional error from GeoDAWN's 400 m line spacing), so a loss here does not
   condemn Slot 1.
3. **Conditional, in this order:** `catdS10` (confirm the sign of Slot 1, mirror
   image) → `SNAPscarp1p4px-20261023-01fb4acc` (capture-radius isolation) →
   `PRUNEp3.5px-refill-20261023-a121a277` (orthogonal collar test, already built).
   Do **not** spend a slot on `phys10`: the model already predicts it loses
   (`-0.008`) and its prior contrast is only ~2x.

## Why this order (and the honest odds)

The measured mechanics of every CONCENTRATION swap are negative (`-0.013` /
`-0.016` / `-0.021`: removing a dot costs ~1.0 credit, an adjacent arrival earns
~0.3-0.6, mass is unchanged). So Slot 1 is the only CONCENTRATION file with a
model-positive expectation, and it wins **only if** the catalogue-density prior
carries more than 0.013 of DTI information. Slot 2 is the only candidate whose
mechanism does not need a new prior to be true. Slot 3 is a sign test, not a bet.

## Weeks to deadline (2026-12-03)

- **Now → wk 2:** run Slots 1-3 above; transcribe every receipt into
  `ledger/submissions.csv` (there are 18 unlogged results — recording *any* of the
  older ones would immediately tell us more than another build).
- **wk 3-4:** combine only receipt-backed axes. The highest-value *new* axis is
  **ADD_HIGH_PRIOR**: add ~10% dots into the highest-prior blocks instead of
  swapping, so no dot is removed and the `-0.013` mechanical cost disappears
  (this is MASS with a real ranking, which the 2026-10-23 MASS files never had).
- **wk 5-6:** confirm, lock ONE blind final file plus one fallback, re-validate
  both from disk.

## Proposed better axes (not built this session)

- **ADD_HIGH_PRIOR (MASS × CONCENTRATION):** +10% dots (41,419) placed only by
  exact expected-DTI gain inside the highest catalogue-density blocks. *Mechanism:*
  removes the swap's removal cost, the dominant term measured this session.
  *Confounder:* mass penalty `0.2` per new dot is paid in full. *Falsifier:* live
  `Δ < +0.01` while `catd10` was `≥ +0.01` ⇒ mass, not placement, is the binding
  constraint.
- **COLLAR_SUPPORT_OFF_RIDGE:** allow moved dots anywhere legal in the footprint
  (not only on the H19-5 skeleton) so arrivals are not forced to stack 1-1.4 px
  from a survivor. *Measured justification:* only 90 legal skeleton pixels in the
  whole study area are `≥ 2.83 px` from every parent dot, so 98-100% of this
  session's arrivals duplicate part of a neighbour's kernel footprint.
  *Confounder:* leaves the ridge support entirely. *Falsifier:* live `Δ < +0.01`
  vs `catd10`.
- **CV-DEFINITION-FIRST:** before any further concentration work, state which
  block-CV definition is meant. R0 reads 1.885 / 0.765 / 0.733 / 0.619 depending
  on definition (see `IRREGULARITIES.md`), and the brief's 0.51-0.59 band matches
  none of them.
