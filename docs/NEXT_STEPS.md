# NEXT_STEPS — current blockers and action order

**Current review date: 2026-10-24.** This current status supersedes stale recommendations embedded in older planning records. A unique-within-local-scan STEPOVER GeoTIFF is format-valid and published, but its HOLDOUT-DTI is negative; no weekly submission slot is recommended. See [`SLOT_PLAN.md`](../SLOT_PLAN.md) and the public [`index.html`](index.html).

## Highest-value actions before another experiment

1. **Resolve data access and permitted provenance.** The full competition `training_features.tif` is absent from `.cache/gems_inputs/`. The official [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) is login-gated; this session cannot retrieve authenticated files. Do not silently substitute a public owner mirror while its redistribution terms are unchecked. Stage authorized files, verify pinned hashes and byte lengths, record provenance, then run `make manifest` and `make verify`.
2. **Do not burn a slot on current candidates.** The format-valid unique STEPOVER candidate is negative. The positive catalogue-holdout RELIEF/DILATATION candidates violate the literal 70%/3-px uniqueness stop against R0. Only a separately authorized human may override these findings; the agent does not choose or upload.
3. **Validate only after the inputs and experiment budget are reset.** Use [`hypotheses_20261024.md`](hypotheses_20261024.md) as the queue. The top untried multi-scale geophysical-edge idea requires the missing feature stack and has no holdout result yet. Test each feature alone for leakage; withhold whole fault segments with buffers; use visible-only catalogue features and exact masking; evaluate pooled DTI α=0.2, β=0.8, 300 m triangular kernel; report evaluator version, withheld positives, and 95% CI.
4. **Do not claim the local holdout validates the competition objective.** The local truth consists of catalogue faults, while competition truth consists of newly identified faults absent from that public catalogue. The local evaluator may reward proximity to known faults and has a structural-zero problem for candidates forced outside the catalogue buffer. An organizer receipt or an independent off-catalogue truth source is required to calibrate live performance.
5. **Verify every published byte.** Run `PYTHONPATH=vendor python scripts/check_site.py`; ensure the primary link, archive links, audit SHA, CRS/shape/transform, range, finiteness, and catalogue gates all match the file actually served. Local PASS is not organizer acceptance.
6. **Record real outcomes.** No submission receipt for this project is presently recorded in `ledger/submissions.csv`. The official public leaderboard was checked on 2026-10-24 and displayed 0.4413 at #1; this is a leaderboard snapshot, not a receipt for this project. The GEMSDOE32 0.2778 remains a CLAIM without a receipt here; 0.3195 is the older prompt-cited snapshot.

## Other repository issues to track

- **Registry scope is incomplete.** The local STEPOVER comparison covers 14 accessible rasters. A full all-site, private, or competition registry is unavailable, so “unique” must retain the scope qualifier.
- **Data-use terms need owner review.** The manifest flags competition data from public mirrors as redistribution terms unchecked. The derived TIF is still a submission candidate with an auditable license/provenance question; confirm competition and source terms before wider distribution.
- **Timestamp discrepancy.** Several inherited files are future-dated 2026-10-25 although the current review date is 2026-10-24. Their provenance is not known; flagged in `IRREGULARITIES.md`, not silently rewritten.
- **Historical planning pages contained contradictory slot recommendations.** `SLOT_PLAN.md`, `docs/SUBMIT.md`, `docs/SUBMIT.html`, and `docs/index.html` are now aligned on no slot recommendation. Continue testing this contract.
- **CI status:** review the GitHub Actions status before any later PR merge. Local tests are not a substitute for a workflow that actually completes.

## Stable local checks

As measured during this review: 107 tests pass (17 existing Rasterio `PendingDeprecationWarning`s); `scripts/check_site.py` gates all 6 served zeros-outside TIFFs and confirms the primary audit hash; the manifest verifies 8/8 local bridge/parent inputs; the pinned parent gate re-measures all recorded invariants and reports `PARENT VERIFIED`. These checks do not regenerate holdout results or authenticate organizer scores.
