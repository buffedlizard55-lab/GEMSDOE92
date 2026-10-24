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

HOLDOUT-DTI is a local catalogue hide-and-recover estimate, not a competition score, and cannot be compared with the prompt-reported **CLAIM 0.2778** or cited 0.3195/0.4413 leaderboard values. No ORGANIZER-CONFIRMED receipt for this candidate exists.

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
