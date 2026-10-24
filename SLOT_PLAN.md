# SLOT_PLAN — GEMS Prize #306

> **2026-10-24 stop notice:** This is a historical, conditional slot plan—not authorization to submit any listed raster. The shared literal all-raster uniqueness gate has a verified universal blocker: `17GEMSDOE_E-proba-multiscale` is positive on every legal cell, forcing forward overlap `1.0` for every nonempty prediction (limit `0.70`). No candidate was created for the selected depth-stratified MT lane, no weekly slot was used, and no upload occurred. The TIPGAP file already on `main` is inspection-only and not globally cleared. See `evidence/registry_saturation_blocker.json`, `evidence/run_card_mt_registry_stop_20261024.json`, and `docs/review_passes_20261024.md`. Do not act on the slate unless the uniqueness scope is explicitly revised and the complete audit rerun.


**2026-10-24 TIPGAP FAR parallel artifact:** `h33-h33-2-b2-TIPGAPfar18f33-20261024T063054Z-0ca8248a` is format-valid locally and below the local parent overlap/ρ limits, but the accessible-registry scan is incomplete and the shared full-support certificate blocks it under the literal all-raster rule. Its HOLDOUT-DTI is 0.002723 [0.002324, 0.003131] (`gems57-pooled-hide-v2`, n=22,663), below R0 0.004006. **Verdict negative and not cleared — do not spend a weekly slot or submit.** On-skeleton 10–15% TIPGAP doses were parent-lane duplicates (overlap≈0.999) and are not offered.

**Incumbent / Parent R0:** `h33-h33-2-b2` (37,654 unit-mass dots; both `zeros` `c55bafc4…` and `nan` `baeae321…` SHA-256 digests rebuilt byte-for-byte from the pinned lineage). Score `0.2778` is **CLAIM** until a submission-page receipt is recorded in `ledger/submissions.csv` (BUILT candidates across `MASS`, `PRUNE`, `SNAP`, `CONCENTRATION`, `RELIEF`, `TIPGAP`; zero `RECEIPT` rows).
**Target & Quota:** `TOP_PUBLIC = ____` (date: `____`); rolling-week slots left: `__ / 3`; total weekly slots remaining to `2026-12-03`: `__` (~18 max across ~6 weeks, plus ONE blind final file; confirm deadline on competition page). Never submit repeats or both NaN/zeros twins of a pair. Treat live public-chunk deltas with `|delta| < 0.01` as **no evidence**.

## Next 3 Live Slots (in priority order, conditional on human quota check)

1. **`h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7`** (`AXIS=RELIEF, value=p12piedmont`) — Shift 12.0% (4,518 dots) from lowest-prior basin & range-front dots into exact expected DTI gain on H19-5 support strictly within the piedmont relief tercile (`-142.91 m <= det_elev < +38.75 m`), increasing piedmont dot proportion from 41.8% to 53.8%; exact 37,654 dots held; `d_cat > 2.0 px`. Prediction: **`MODEL:+0.008`** (range `[-0.003,+0.022]`); hide-and-recover `PROXY` `+0.00197` vs R0 (`0.00597` vs `0.00401`).
   - *Decision rule:* If receipt delta `>= +0.01` vs R0, validates that unmapped Quaternary fault truth concentrates along the range-front piedmont; promote `RELIEFp12piedmont` to parent for Week 3 composite (`RELIEF + SNAP`). If `<= -0.01`, rejects piedmont hypothesis and suggests concealed intrabasinal faults dominate.
2. **`h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24`** (`AXIS=SNAP, value=scarp2p0px`) — `<=2.0 px` (`200 m`) spacing-preserving (`min_nn >= 2.828 px`) snap onto joint topographic scarp + piedmont break-in-slope + TMI/unsigned-gravity gradient; mean disp `1.234 px` (82.05% px changed), fixed 37,654 dots, exact R0 `d_cat > 2.0` exclusions. Prediction: **`MODEL:+0.012`** (range `[-0.006,+0.025]`); SGMC `PROXY` `+0.00267` vs R0; hide-and-recover `PROXY` `+0.00080`.
   - *Decision rule:* Tests positional lineament error independent of regional macro-tercile allocation. If receipt delta `>= +0.01`, confirms ~100-200 m GeoDAWN positional correction.
3. **`h33-h33-2-b2-CONCcatblk10up10-20261024-c9503d48`** (`AXIS=CONCENTRATION, value=catblk10up10`, `MODEL:+0.006`) **OR conditional swap to `h33-h33-2-b2-RELIEFp15piedmont-20261024-15254f0a`** (`AXIS=RELIEF, value=p15piedmont`, `MODEL:+0.006`) **iff Slot 1 succeeds**.
   - *Decision rule:* If Slot 1 shows a positive dose response (`>= +0.01`), Slot 3 evaluates the aggressive 15% relief shift (`p15piedmont`, 56.8% piedmont allocation) to map the dose-response plateau. If Slot 1 is neutral (`|delta| < 0.01`), Slot 3 tests the 1 km known-fault concentration prior (`CONCcatblk10up10`).

Reserve files that must not be paired in the same week (they ask the same question):
`CONCcatblk10up20` (`MODEL:+0.004`, saturated dose), `CONCcatblk10dn10`
(`MODEL:-0.006`, direction test), and `CONCENTRATIONphys10-20261024-b93a4cf8`
(`MODEL:-0.008`, physics prior, no catalogue information — the control that says
whether a `catblk10up10` win came from the catalogue prior or from reallocation
itself). **Spacing caveat on every CONCENTRATION file:** at a fixed count on the
1-px H19-5 skeleton, arrivals must land 1.0-2.0 px from a survivor; the 2.83 px
parent floor is unattainable (only ~90 legal pixels exist), and at a 2.0 px floor a
"10%" move silently becomes 7.34% of positions (measured; see IRREGULARITIES).
## Schedule to Deadline (2026-12-03, ~6 weeks)

- **Weeks 1–2 (2026-10-24 to 2026-11-05 — Single-Axis Screening):** Execute Slots 1–3 above (`RELIEF`, `SNAP`, `CONCENTRATION`); evaluate dose responses against recorded receipts in `ledger/submissions.csv`.
- **Weeks 3–4 (2026-11-06 to 2026-11-19 — Orthogonal Combination & Mechanism Refinement):** Combine ONLY axes with receipt-backed gains `>= +0.01` (primary candidate: `RELIEFp12piedmont + SNAPscarp2p0px`, or `SNAP + PRUNE` collar), one controlled change per step from the best receipted parent.
- **Weeks 5–6 (2026-11-20 to 2026-12-03 — Confirmation, Blind Final Selection & Audit):** Confirm the top composite on live chunks without chasing `<0.01` noise; assemble Phase-2 `TRACKB` geologist traces only if human-authorized; lock ONE blind final submission file and ONE fallback file, re-validate both from disk against `sample_submission.tif`, and finalize `AI_USE.md` + reproducible code archive.

## Proposed Better Axes (Not Built This Session)

- **`RELIEF_SNAP_COMPOSITE`:** First shift 12% of mass into piedmont relief tercile (`RELIEFp12piedmont`), then apply spacing-preserving `<=2.0 px` SNAP onto break-in-slope and gravity gradients. *Confounder:* compound displacement might cause local clustering if not spacing-constrained. *Falsifier:* composite delta `< max(RELIEF_delta, SNAP_delta)`.
- **`CROSS_STRIKE_ONLY_SNAP`:** Project `<=2 px` displacements strictly perpendicular to local `H19-5` strand tangent onto `||\nabla(\text{RTP})||` (Band 2, inclination-corrected) + piedmont break-in-slope. *Confounder:* sharp fault intersections/relay bends where tangent orientation is ill-defined. *Falsifier:* live receipt delta `< +0.01` vs isotropic `SNAPscarp2p0px`.
- **`TIP_RELAY_EXTENSION`:** Reallocate pruned `<=3 px` collar dots exclusively onto `1–3 km` off-`H19-5` fault terminations and Faulds-type relay step-overs corroborated by `||\nabla(\text{RTP})||` and geodetic shear rate (`Band 7`). *Confounder:* volcanic dike tips or stratigraphic pinchouts where slip truly terminates. *Falsifier:* live receipt delta `< +0.01` vs `PRUNEp3.5px-refill`.
