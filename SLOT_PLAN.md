# SLOT_PLAN — GEMS Prize #306

**Parent:** R0 `h33-h33-2-b2`, 37,654 unit-mass dots, rebuilt byte-exactly this
session from the pinned lineage (both encodings match). `0.2778` is a **CLAIM**,
not a RECEIPT. `TOP_PUBLIC`, the remaining slots and every receipt come from the
human. Nothing here is submitted automatically; the entity has 3 scored
submissions per rolling week and one final file, deadline 2026-12-03 (confirm on
the competition page).

**Axis built this session: SNAP** — move a dot ≤2 px onto the strongest
TMI / gravity / detrended-slope edge response, but only when that beats its own
pixel by more than a threshold `g`; count, unit mass and the parent's 2.83 px
spacing invariant all held. Three doses are BUILT and gated:

| value | dots moved | mean displacement | MODEL range | SGMC off-catalogue PROXY vs R0 |
|---|---:|---:|---|---:|
| `cap2p0-g0.15` | 2,660 (7.06%) | 0.124 px | ±0.008 | −0.000080 |
| `cap2p0-g0.10` | 7,023 (18.65%) | 0.321 px | ±0.015 | −0.000153 |
| `cap2p0-g0.05` | 19,565 (51.96%) | 0.858 px | ±0.035 | +0.000013 |

## Next three live slots, in order

1. **`PRUNEp3.5px-refill` (built, `…-a121a277`)** — 2,702 dots removed/refilled
   (7.18%), count held at 37,654, minimum catalogue distance 3.606 px.
   *Why first:* it is the only mechanism whose last step moved the score up at
   all (the ≤2 px collar moved 0.2708 → 0.2778 CLAIM = +0.007, which is itself
   still under the 0.01 evidence bar, so this slot is also the test of whether
   that trend was real). *What the result changes:* a
   receipt ≥ +0.01 makes this the new parent and the collar the first thing to
   compose; a receipt ≤ −0.01 rejects collar extension and retires the PRUNE
   line; anything inside ±0.01 is no evidence and the next slot proceeds as
   planned.
2. **`SNAPcap2p0-g0p15` (`…-2ca4294e`)** — 2,660 dots moved (7.06%), mean
   displacement 0.124 px, MODEL ±0.008. *Why second:* it is the cheapest honest
   test of the positional hypothesis (that the parent's dots are 1-3 px off the
   physical edge) because it barely perturbs the incumbent. *What the result
   changes:* ≥ +0.01 means position error is real and correctable → rebuild this
   SNAP on top of the best receipt-backed parent and spend the remaining slots on
   the perpendicular-only refinement; ≤ −0.01 means the parent's own lineament
   positions beat single-surface edges and SNAP is retired.
3. **`SNAPcap2p0-g0p05` (`…-2c472bc5`)** — 19,565 dots moved (51.96%), MODEL
   ±0.035. *Take this only if slot 2 was ≥ +0.01 or ≥ −0.01 (i.e. the mechanism
   shows a sign).* It is the dose extreme: if more snapping keeps helping, the
   dose-response is monotone and SNAP becomes a standing post-processing step;
   if it collapses, only clearly mispositioned dots are correctable. **If slot 2
   is inside ±0.01 (no evidence), do not spend a slot on slot 3's file** — use it
   for `PRUNEp2.5px-refill` (`…-6d7a61ba`, 941 dots, MODEL +0.001) to bracket the
   collar from below, or hold it.

**Decision discipline.** A live change under 0.01 is no evidence. One submission
per chosen raster; never upload both encodings of one experiment (they score
identically). Fill `receipt_score`/`receipt_date` only from the submission page.

## Weeks to 2026-12-03

- **Weeks 1-2:** the three slots above, in order, updating receipts. Confirm
  quota and `TOP_PUBLIC` (with date) before slot 1.
- **Weeks 3-4:** compose only axes with a receipt-backed ≥ +0.01 gain; one
  controlled edit per candidate, parent named and rebuilt byte-exactly.
  Proposed, **not built this session**:
  - **SNAP_PERP** — snap only the across-strike component of each move (keep
    along-strike drift out). Mechanism: the 400 m flight-line geometry makes the
    error cross-strike; 40-42% of this session's moves are along-strike, i.e.
    pure file churn. Confounder: strike is estimated from the same chains being
    corrected (circular). Falsifier: no ≥ +0.01 receipt gain over plain SNAP.
  - **CHAIN_FILL (mass)** — add dots into along-strike gaps > 3.5 px inside
    otherwise continuous chains, count free. Mechanism: line truth is
    continuous, so a gap is a model dropout; a filled pixel within 3 px of truth
    earns ~2 kernel units against a 0.056 cost. Confounder: real relays and
    step-overs. Falsifier: a receipt below R0.
  - **MASS_RED (geometry ranking)** — drop the 10-20% of dots with no neighbour
    within 5 px *and* low km-block support. Mechanism: zero-credit dots add 0.2
    to the DTI denominator and nothing to T; the lineage's own thinning trend
    (60k → 44k → 40k → 37.6k dots with a rising score) implies the mass optimum
    is below R0. Confounder: isolated dots can be genuine short traces.
    Falsifier: a receipt ≥ +0.01 *below* R0 kills the thinner-is-better prior.
- **Weeks 5-6:** confirm the best receipt-backed composite; select one blind
  final file plus a fallback; re-validate both from disk; disclose AI use before
  the deadline. Confirm the deadline on the competition page rather than here.
