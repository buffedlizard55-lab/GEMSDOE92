# SLOT_PLAN — current selector state (2026-10-24, LCS session)

## Current artifact: LCS consensus — OK to download, OK to submit (policy S), slot verdict negative, no slot used

`GEMSDOE92-LCS-consensus-20261024-58fd2c77` (file `GEMSDOE92-lcs-consensus-37654-20261024-58fd2c77-zeros.tif`, SHA-256
`04f6b587ad87331325bc450a50c77d6945fe86c59790830a1f1ba70d3220df90`): all 10 MUST gates pass at the strict 3-px catalogue distance; unique against every operator-scored
raster in both phases (final max overlap 0.637, surface 0.676, |ρ| ≤ 0.358) and, on final dots, against all 861 non-blanket registry rasters (max 0.697); the literal all-registry rule
(Tier T) fails — as it does for a random file. HOLDOUT-DTI is exactly 0 by construction (instrument degenerate for 3-px-clean files); the protocol's rule is applied literally → **negative**.
MODEL projection 0.263–0.321 vs R0 0.2778 (± 0.066): an exploration arm, no improvement claimed. **The selector (a human, ≤ 3 per week) decides; this repository selects, approves and uses no slot.**
Recommended measurement order: see `docs/NEXT_STEPS.md` (probe R0-minus-fragments first, then this file).

---

# SLOT_PLAN — current selector state (2026-10-24, ANASIG session)

## Current artifact: ANASIG f45 — negative, no slot used

Primary download `GEMSDOE92-ANASIG-f45Atop-20261024` (file
`h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif`, SHA-256
`68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`) is
format-valid and locally lane-unique, but **not cleared**: HOLDOUT-DTI
0.004967 does not beat the holdout best RELIEF p10 (0.006045; paired
Δ −0.001078 [−0.002034, −0.000112]), its SGMC proxy is below R0, and the
binding public witness (footprint-positive E-proba raster) gives 100%
forward overlap under the literal public rule. SCARPPOL doses built this
session are duplicates of BREAKLINE (0.900–0.913) and must never be
submitted. A human selector may only act after the literal-rule policy
question in `docs/NEXT_STEPS.md` is resolved. No slot used this session.

---

# SLOT_PLAN — current selector state (2026-10-24)

## Current artifact: negative duplicate; no slot used

`GEMSDOE92-visible-collar-r0-excluded-20261024` is the current primary download and a negative research deliverable. It passes all file-format gates. The initial 14-file local uniqueness scan was incomplete; the expanded literal registry scan across 1,279 matching-grid rasters in 102 public owner repositories found a duplicate. **Do not submit this candidate.**

- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 buffered folds, 22,663 withheld positives: candidate **0.046866 [0.040216, 0.053315]**; parent R0 **0.004006 [0.003424, 0.004690]**; paired Δ **+0.042860 [+0.036122, +0.049357]**.
- Leakage canary (visible-fault distance alone): symmetric AUC **0.745593**, below 0.90.
- **REGISTRY-MEASUREMENT:** pre-placement and final worst forward 3-px overlap **1.000000**; 131/1,279 rasters exceed 70%. Worst |Spearman ρ|: pre-placement **0.421367**, final **0.492957** (both below 0.90). Overlap alone triggers the stop rule.
- Format validation: 10/10 gates pass. SHA-256 `60082b75a3d8e4648a858622f71f24257c8cfef79286a1a96147c59f05377da7`.
- **Verdict: negative — duplicate under the literal gate; stop.** No weekly slot was selected or used.

Audit: `evidence/public_registry_uniqueness.json`; run card: `evidence/visible_collar_run_card.json`; file: `docs/downloads/GEMSDOE92-visible-collar-r0-excluded-20261024-zeros.tif`.

## Scan scope and comparison boundary

The scan covered current default-branch TIFF paths in `docs/downloads/`, `releases/`, and submission directories across 102 public repositories whose names match GEMSDOE in the `buffedlizard55-lab` account. Trees were complete in the API scan; 1,285 unique Git blobs were downloaded and SHA/size-verified, and 1,279 single-band rasters matching the sample grid were compared. The audit is not exhaustive of historic branches, unlinked/site-hosted assets, private repositories, zip-only artifacts, or other owners. One binding duplicate witness is sufficient to stop under the literal rule, independent of scan completeness.

The largest overlap is 100% against `11GEMSDOE/docs/downloads/gems-structural-area06-v1.tif`; additionally, `17GEMSDOE_E-proba-multiscale` is positive across the full footprint and is also a binding overlap witness. We do not waive those because they are dense or continuous surfaces; the requested literal rule governs.

HOLDOUT-DTI is a local catalogue hide-and-recover estimate, not a competition score, and cannot be compared with the prompt-reported **CLAIM 0.2778**. A prior repository record says the official public leaderboard was read on 2026-10-24 and showed 0.4413 at #1 (LEADERBOARD-SNAPSHOT, not a receipt for this candidate); the prompt's 0.3195 is an older conflicting snapshot. No ORGANIZER-CONFIRMED receipt for this candidate exists.

## Historical results retained

- DILATATION p10/p12/p15 and RELIEF p10 had positive local HOLDOUT-DTI but were flagged as R0 duplicates under the literal >70%/3px rule. Do not recommend them for a slot.
- TIPGAP FAR and STEPOVER were negative on their documented holdout instruments. Keep as negative deliverables.
- Parent R0's 0.2778 remains **CLAIM** until a dated competition receipt is recorded in `ledger/submissions.csv`.

## Next steps (no more candidate experiments until selector/gates reconciled)

1. Keep the current candidate as a downloadable **negative** artifact; do not submit it.
2. Run `scripts/audit_public_registry.py` periodically to refresh the expanded scan against current public branches; it records scan date/scope. Do not confuse public default branches with all historical/site-hosted assets.
3. Resolve the literal overlap gate with a policy decision outside this agent's authority. Until then, any candidate with >70% overlap against any single indexed raster must stop; no arrival-only or dense-surface exception.
4. Add an off-catalogue validation instrument. The current holdout's truth is the mapped catalogue and may not rank candidates for private uncatalogued targets.
5. Obtain the missing GeoDAWN stack from the official competition data tab when authorized; current cache is absent. Hash-verify and record terms before testing the remaining hypotheses.
6. Have the human selector review the actual current weekly quota. No credentials or slot were requested or used here.
7. Resolve public-repository redistribution terms for committed rasters; see `IRREGULARITIES.md`.

## Parallel-session candidate — BREAKLINE f45Ltop (2026-10-24 merge note)

`h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0` (zeros sha256 `cd9c8a56…810e`): format-valid; **unique within the 18-raster local registry** (worst 55.0% vs R0; 3.5% vs the collar candidate); HOLDOUT-DTI 0.004861 [0.004032, 0.005822], Δ vs R0 +0.000854 [+0.000300, +0.001423]; SGMC control +31% vs R0. **Verdict: negative — NOT cleared** (below holdout-best arms; update 2026-10-24 late session: public scan run, literal duplicate stop triggers, 134 >70%). Relative standing for a future *human* selector once the overlap-gate policy (item 3 above) is resolved: BREAKLINE is the only served candidate that passes the literal rule on the local registry while beating its parent on the holdout; the collar candidate fails the expanded public scan outright. Receipt decision rules if it is ever uploaded: Δ ≥ +0.01 vs CLAIM 0.2778 ⇒ off-skeleton scarp-breaks earn live credit (walk dose up next session); Δ ≤ −0.01 ⇒ skeleton mass was load-bearing, retire far emission; |Δ| < 0.01 ⇒ no evidence, do not spend a sibling dose. Never pair BREAKLINE doses in one week; never submit a SUPERSEDED `*breakline` (greedy-emission) file.

## Late-session candidate — STRAINBREAK f60s2i (2026-10-24)

`h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2` (zeros sha256 `000d0bd7…5c1f`): format-valid; locally unique (worst 40.0% vs R0 over 21 rasters); HOLDOUT-DTI 0.005487 [0.004522, 0.006430] — best locally-unique holdout in repo — but SGMC 0.10516 < BREAKLINE 0.12611 and it does not beat RELIEF p10 (0.006045). **Verdict: negative — NOT cleared.** Selector framing if the literal-gate policy is ever resolved: BREAKLINE (SGMC-favoured) vs STRAINBREAK (holdout-favoured) is one receipt's worth of information either way; never submit more than one STRAINBREAK dose (f45/f60/f75 are siblings; f75=f60 on holdout), and never pair a STRAINBREAK and BREAKLINE dose in the same week — their far sets are disjoint by construction but they test overlapping questions.
