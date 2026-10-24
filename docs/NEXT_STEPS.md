# NEXT_STEPS — what still has to be done, and what is blocking it

Written 2026-10-25 after PR #21 merged. Every number here was measured in this checkout;
nothing is projected. Where a claim is not verified it says so.

## The one finding that should drive the next session

**Under the operator's own gates, this repository currently has no submittable file.**

The brief's uniqueness rule is literal: *more than 70 % of your dots within 3 px of one
registry raster ⇒ log it as a duplicate and stop.* Parent R0 is a registry raster. Measured
against it, every arm with a positive HOLDOUT-DTI is a duplicate:

| arm | HOLDOUT Δ vs R0 | % dots ≤3 px of R0 | literal verdict |
|---|---|---|---|
| RELIEF p10 | +0.002039 | 99.38 % | DUPLICATE |
| DILATATION p15 | +0.00181 | 99.37 % | DUPLICATE |
| DILATATION p12 | +0.00177 | 99.37 % | DUPLICATE |
| DILATATION p10 | +0.00174 | 99.40 % | DUPLICATE |
| TIPGAP far18f33 | **−0.001283** | **67.00 %** | unique, but negative |

Uniqueness and expected gain currently pull in **opposite directions**. TIPGAP clears the
rule *because* it moves 33 % of the budget far off the D2.8 skeleton, and that same move is
what cost it holdout credit. **Resolving that tension is the next session's real job — not
building a seventh variant.**

Two ways out, and they are different kinds of work:

1. **Build an arm that clears 70 % without leaving the high-credit neighbourhood.** The
   constraint is now explicit and measurable: move >30 % of dots more than 3 px from every
   R0 dot, while keeping expected kernel credit per dot at or above R0's. TIPGAP satisfied
   the first half and failed the second. The unexplored middle is a *large* reallocation that
   stays on or adjacent to the H19-5 skeleton — e.g. re-thin the skeleton at a different
   Poisson radius and re-place, rather than walking off its tips.
2. **Get an explicit, recorded human decision that Reading 2 governs** — i.e. that the 70 %
   rule is meant to catch lane drift between parallel sessions, not shared parentage, so the
   arrival-set test (DILATATION vs TIPGAP Jaccard 0.0011) is the operative one. That is a
   defensible reading, but it is the *operator's* call, and until it is recorded the literal
   rule stands and nothing here is cleared.

Do not let a third session quietly re-adopt Reading 2 and ship a "promote" banner again.
That happened once already (see `IRREGULARITIES.md` 2026-10-25) and it is the failure mode
this repository most needs to guard against.

## Blocker 0 — no organizer receipt exists for anything (highest value, lowest cost)

`ledger/submissions.csv` has **30 `BUILT` rows and 0 `RECEIPT` rows**. Every ranking in this
repository rests on a local instrument whose truth is the **visible catalogue**, so by
construction it *cannot* reward a genuinely new fault. The repo's own `gems/proxy.py`
records that this instrument correlated **−0.87 to +0.54 with live scores across 12–14
files**, and that one candidate (`lidar03`) passed it and then scored 0.1152 live.

**Action:** first produce a candidate that passes the literal uniqueness stop and format checks, then a separate human selector may choose whether one weekly slot is justified and record the receipt. No current file meets both the uniqueness and positive-holdout criteria, so do not spend a slot on the present primary. A receipt would still be the only direct way to calibrate the local holdout against the live score.

**Blocking it:** no DrivenData credentials in the sandbox, and the agent must never submit. Human upload/receipt capture remains separate from this agent workflow.

## Blocker 1 — six of eight axes have never been scored on the shared instrument

Measured: only **6 arms across 2 axes** (`RELIEF`, `DILATATION`) have pooled HOLDOUT-DTI in
`evidence/*proxy_audit.json`. These axes have **no** pooled-holdout arm at all:

`CONCENTRATION` · `MASS` · `PRUNE` · `SNAP` · `STEPOVER` · `TIPGAP`

(TIPGAP and STEPOVER have their own run cards, but not on the pooled-hide-v2 harness the
slot table uses, so their numbers are not directly comparable to the ones in `SLOT_PLAN.md`.)

**Action:** run `scripts/report_dilatation_proxies.py`'s harness over the remaining built
rasters so the slot table compares like with like. Cheap — the rasters already exist; only
the scoring is missing. This may also resurrect or kill arms that were ranked on `MODEL`
projections alone.

## Blocker 2 — the holdout cannot see the thing the competition rewards

The holdout withholds **catalogue** segments. The competition scores **new** faults the
catalogue does not contain. A file can win the holdout by hugging known traces better — which
is worth nothing live, because known faults are masked pixel-exactly at scoring.

**Action:** add a second instrument whose truth is *off-catalogue*: the USGS SGMC bedrock
control is already wired up (`sgmc_control_proxy`, `n = 62,703` pixels >3 px from the
catalogue) but is currently reported only as a side note. Promote it to a scored column in
the slot table, and treat **disagreement** between the two instruments as the signal rather
than averaging them away. Note the DILATATION arms *fall* on SGMC (−0.0125 to −0.0162) while
rising on the catalogue holdout — that disagreement is unexplained and is exactly the kind of
thing that decides live outcomes.

## Blocker 3 — `TOP_PUBLIC` is still blank

`SLOT_PLAN.md` carries `TOP_PUBLIC = ____`. The prompt cites 0.4413 and 0.3195; those two
conflict and **neither is verified in this checkout**. Without a dated, organizer-confirmed
ceiling there is no way to say whether any local gain matters.

**Action:** human fills `TOP_PUBLIC` + observation date from the live leaderboard.

## Blocker 4 — competition rasters are tracked in a public repo

`data/` and `releases/*.tif` are committed (and now `docs/downloads/*.tif` too, by design, so
the site can serve them). The competition's data-use terms have never been checked against
redistribution. Flagged since 2026-10-23 and still open.

**Action:** human confirms the terms permit this, or untracks `data/` and serves only the
derived submission rasters. Note that untracking does not purge git history — that is a
separate, owner-level decision.

## Smaller, concrete work

- **`MASS` files are not a ranking test.** `h19_5.tif` is binary `{0,1}` with value 1.0 at
  every R0 dot, so the "ranking" those files used had no ordering; they are a random 10 %
  perturbation control. Already recorded, but the rows still sit in the ledger looking like
  experiments. Mark them `CONTROL` in the ledger so a future session does not read a
  conclusion off them.
- **`CONCENTRATION` dose is partly bookkeeping.** At a fixed count on the 1-px H19-5 skeleton
  the parent's 2.83 px spacing floor is unattainable (only ~90 legal pixels exist), and at a
  2.0 px floor a "10 %" move silently becomes 7.34 % of positions. Any future
  CONCENTRATION arm must state which floor it used.
- **`docs/submit.html` vs `docs/SUBMIT.html`.** Two submission guides now exist (one from
  main, one from this branch) with different content. Consolidate to one, or the human will
  read whichever the link happens to hit.
- **CI runner was stuck.** The Actions job for PR #21 sat `pending` for >20 minutes and never
  reported. The merge proceeded on local verification (`make test` 107 passed, `make
  manifest` OK, `make verify` PARENT VERIFIED, `check_site.py` PASS). Worth checking whether
  the workflow is actually executing, since a CI that never runs is the same as no CI — that
  is how `make verify` went unnoticed-broken in the first place.

## What is now solid (do not redo)

- `make verify` genuinely proves the parent: sha256 **and** byte length per encoding, then
  re-measures dot count, total mass, min catalogue distance, footprint and the 3/4/5 px
  collar counts from the raster itself and diffs them against the record. Zero drift on all
  seven.
- `make manifest` verifies all 8 pinned inputs (was reporting 8/8 MISSING from a path-join
  bug; fixed once in `gems.rasters.resolve_pinned_path`).
- `scripts/check_site.py` derives the primary from the page and gates **every** served
  zeros-outside raster (5 currently), and asserts the primary matches its local format-audit JSON
  byte-for-byte. It caught a real orphan (a served file not linked from the page).
- The portal `[0,1]` failure mode is understood and prevented: all-finite writes,
  `nodata=None`, zeros outside. Verified over HTTP on the served bytes, not just on disk.
- 107 tests pass with no competition data required.
