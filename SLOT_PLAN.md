# SLOT_PLAN — GEMS Prize #306

**2026-10-25 DILATATION session:** `h33-h33-2-b2-DILATATIONp12dilatation-20261025-8b4d248b` is format-valid, portal-safe (zeros-outside, all finite), lane-distinct from every other built arm, and the **only** arm whose HOLDOUT-DTI CI excludes zero *and* which ships in the safe encoding. **Verdict promote.**

**2026-10-24 TIPGAP FAR session:** `h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a` is format-valid and lane-distinct, but HOLDOUT-DTI `0.002723 [0.002324, 0.003131]` (`gems57-pooled-hide-v2`, n = 22,663) is **below** R0 `0.004006`. **Verdict negative — do not spend a weekly slot.** On-skeleton 10–15 % TIPGAP doses were parent-lane duplicates (arrival overlap ≈ 0.999) and are not offered.

**Incumbent / Parent R0:** `h33-h33-2-b2` (37,654 unit-mass dots; both `zeros` `c55bafc4…` and `nan` `baeae321…` SHA-256 digests rebuilt byte-for-byte from the pinned lineage, and now re-verified by `make verify`, which re-measures dot count, total mass, min catalogue distance, footprint and the 3/4/5 px collar counts from the raster itself). Score `0.2778` is **CLAIM** until a submission-page receipt is recorded in `ledger/submissions.csv` (30 `BUILT` candidates across `MASS`, `PRUNE`, `SNAP`, `CONCENTRATION`, `RELIEF`, `TIPGAP`, `DILATATION`, `STEPOVER`; **zero** `RECEIPT` rows).

**2026-10-24 STEPOVER session:** additional unique file `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f` is format-valid and lane-unique (worst ρ 0.0277; worst 3-px forward overlap 0.2534 vs 14 local registry rasters), but HOLDOUT-DTI is a structural 0.0000 vs R0 0.00370. **Verdict negative — do not spend a weekly slot.** It is not one of the Next 3 Live Slots below.
**Target & Quota:** `TOP_PUBLIC = ____` (date: `____`); rolling-week slots left: `__ / 3`; total weekly slots remaining to `2026-12-03`: `__` (~18 max across ~6 weeks, plus ONE blind final file; confirm deadline on competition page). Never submit repeats or both NaN/zeros twins of a pair. Treat live public-chunk deltas with `|delta| < 0.01` as **no evidence**.

## Ranking is by HOLDOUT-DTI, not by MODEL projection

Every arm below was scored on the same instrument (`gems57-pooled-hide-v2`, 22,663 withheld catalogue positives, 157 spatial clusters, 1,000 paired draws, seed 520810). **R0 = 0.004006 [0.003424, 0.004690].**

| rank | arm | HOLDOUT-DTI | Δ vs R0 | 95 % CI of Δ | % dots ≤3 px of R0 | encoding | cleared for a slot? |
|---|---|---|---|---|---|---|---|
| 1 | `RELIEFp10piedmont-20261024-3e900c24` | 0.006045 | **+0.002039** | [0.001483, 0.002504] | 99.38 % | zeros-outside ✅ | **NO — fails uniqueness** |
| 2 | `DILATATIONp15dilatation-20261025-ebc1b432` | 0.005818 | +0.00181 | — | 99.37 % | zeros-outside ✅ | **NO — fails uniqueness** |
| 3 | `DILATATIONp12dilatation-20261025-8b4d248b` | 0.005779 | +0.00177 | [0.001110, 0.002455] | 99.37 % | zeros-outside ✅ | **NO — fails uniqueness** |
| — | `DILATATIONp10dilatation-20261025-2e501f88` | 0.005747 | +0.00174 | — | 99.40 % | zeros-outside ✅ | **NO — fails uniqueness** |
| — | `RELIEFp12piedmont-20261024-a0998ed7` | 0.005974 | +0.00197 | — | 99.38 % | zeros twin now built | **NO — fails uniqueness** |
| — | `TIPGAPfar18f33-…-0ca8248a` | 0.002723 | **−0.001283** | — | **67.00 %** ✅ | zeros-outside ✅ | unique, but **negative** |

**No slot is recommended this session.** The brief's uniqueness rule is literal: *if more than 70 % of your dots fall within 3 px of one registry raster's dots, log it as a duplicate and stop.* Parent R0 **is** a registry raster (`registry/parents/R0.json`). Every arm with a positive HOLDOUT-DTI measures 99.37–99.40 % against it, so all are duplicates under that rule. The one arm that clears the rule — TIPGAP, at 67.00 % — scores **below** R0. **Under the operator's own gates there is currently nothing here that is both unique and expected to improve**, and the correct output of the session is that finding rather than a submission.

**This supersedes an earlier recommendation in this file.** A previous revision of this plan ranked RELIEF p10 as "Slot 1" on holdout gain alone. That was wrong twice over: it ignored the uniqueness rule, and `docs/REVIEW_AND_NEXT_STEPS.md` had already recorded RELIEF p10 as *"explicitly negative / NOT OK TO SUBMIT"* for exactly this 99.38 % reason. The recommendation is withdrawn. See `IRREGULARITIES.md` 2026-10-25 (uniqueness rule).

**The two readings, stated plainly.** Reading 1 (literal): these are R0 duplicates; log and stop. Reading 2 (lane drift): the files keep 88–90 % of R0's dots *by construction* — count is held at 37,654 and only 10–15 % is reallocated — so whole-file overlap measures how much parent you kept, not whose lane you are in; run on **arrival sets** the lanes are nearly disjoint (DILATATION vs TIPGAP Jaccard 0.0011, vs RELIEF 0.1593). Reading 2 is the better science but it is *this repository reinterpreting an operator gate in its own favour*, so **Reading 1 governs** and any upload is a recorded human override.

**Note the structural tension this exposes.** TIPGAP clears uniqueness *because* it moves 33 % of the budget far off the D2.8 skeleton — and that same move is what drove its holdout below R0. Under this rule set, uniqueness and expected gain pull in opposite directions. Resolving that, not building another variant, is the next session's real job (see `docs/NEXT_STEPS.md`).

### Do not pair these in the same week

- `DILATATIONp10` / `p12` / `p15` — one dose-response question. Spend **one**, read the receipt, then decide whether to walk the ladder.
- `RELIEFp10` / `p12` / `p15` — same question at another dose. RELIEF and DILATATION arrivals overlap 28.84 % within 3 px (Jaccard 0.1593), so they are *not* independent; a RELIEF win and a DILATATION win are partly the same information.
- `CONCcatblk10up10` / `up20` / `dn10` and `CONCENTRATIONphys10` (`MODEL:−0.008`, the control that says whether a `catblk10up10` win came from the catalogue prior or from reallocation itself). **Spacing caveat on every CONCENTRATION file:** at a fixed count on the 1-px H19-5 skeleton the 2.83 px parent floor is unattainable (only ~90 legal pixels exist), and at a 2.0 px floor a "10 %" move silently becomes 7.34 % of positions (measured; see IRREGULARITIES).
- `SNAPscarp2p0px` / `scarp1p4px` / `pot2p0px` and `SNAPcap2p0-g0.05/0.10/0.15` — one positional-correction question.
- `PRUNE_B3/B4/B5` and `PRUNEp2.5/p3.5/p4.5px-refill` — one collar question.
- `TIPGAPfar18f33` — negative on the holdout; keep as a deliverable, not a slot.

### Decision rules

- **Candidate slot (BREAKLINE f45, human-decided):** receipt Δ ≥ +0.01 vs R0's CLAIM ⇒ off-skeleton DEM scarp-breaks earn live credit; the far-dose direction is real — consider walking the dose up (next session) and protect the Final-round slot for a BREAKLINE-class file. Δ ≤ −0.01 ⇒ the skeleton's mass was load-bearing and the SGMC gain was bedrock-interior bias; retire off-skeleton far emission at these doses. |Δ| < 0.01 ⇒ no evidence; do not spend a sibling dose.
- **Slot (RELIEF p10, hypothetical override only):** receipt Δ ≥ +0.01 vs R0 → unmapped Quaternary truth concentrates on the range-front piedmont; promote to parent for a Week-3 composite. Δ ≤ −0.01 → piedmont hypothesis rejected; concealed intrabasinal faults dominate. (Duplicate — submitting it requires a recorded human reinterpretation of the uniqueness rule.)
- **Slot (DILATATION p12, hypothetical override only):** Δ ≥ +0.01 → active dilatation predicts new faults; promote and compose `DILATATION + SNAP`. Δ ≤ −0.01 → rejects the kinematic prior; expect Phase-2 truth to be inactive/exhumed or compressional. (Duplicate — same caveat.)

## Schedule to Deadline (2026-12-03, ~6 weeks)

- **Weeks 1–2 (to 2026-11-06 — single-axis screening):** Slots 1–3 above. Record every receipt in `ledger/submissions.csv`; the holdout cannot settle these.
- **Weeks 3–4 (2026-11-07 to 2026-11-19 — orthogonal combination):** combine **only** axes with receipt-backed gains ≥ +0.01, one controlled change per step from the best receipted parent. Candidate composites: `RELIEF + SNAP`, `DILATATION + SNAP`. Do **not** compose `RELIEF + DILATATION` blind — their arrivals already overlap 28.84 %, so the composite may be worth less than either alone.
- **Weeks 5–6 (2026-11-20 to 2026-12-03 — confirmation, blind final, audit):** confirm the top composite on live chunks without chasing |Δ| < 0.01 noise; lock ONE blind final file and ONE fallback, re-validate both from disk against `sample_submission.tif` with `make verify` and `python -m gems validate`; finalize `AI_USE.md` and the reproducible code archive.

## Proposed better axes (not built; ranked in `docs/HYPOTHESES.md`)

1. **`CONCEALED_BASIN_EDGE`** — `||∇ depth_to_base_surf||` (Band 15) high while `||∇ det_elev_slope||` is low: a buried basement step with no surface scarp. *Mimic:* paleocanyon basalt fills, caldera margins. *Falsifier:* receipt Δ < +0.01.
2. **`SEISMICITY_GUIDED`** — `pct(−deq)·pct(ieq)·pct(2ndinv)` (Bands 10/16/4): instrumental swarms on blind faults. *Mimic:* anthropogenic seismicity from geothermal production and blasting.
3. **`CONDUCTIVITY_ALTERATION`** — `cond_surf` (Band 17) high with low radiometric Th: smectite-altered damage zones. *Mimic:* Lahontan playa clays. Needs `geodawn_rad_u8.tif` (already pinned).
4. **`DILATATION_RELIEF_COMPOSITE`** — 12 % into high dilatation, then piedmont within it. *Confounder:* double-counting the same dots; the 28.84 % arrival overlap says the two are not independent.
