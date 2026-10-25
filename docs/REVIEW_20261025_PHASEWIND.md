# Three-pass review — PHASEWIND — 2026-10-25

## Scope and acceptance checks

Reviewed `README.md` and the full `SESSION_PROMPT.md`, including prior session notes and the explicit correction that the current duplicate rule is literal (no matched-budget override). The requested outcome was one ranked and tested geological lane, a truthful explanation of the reported `GEMSDOE32 0.2778`, project-level format checks, a unique/downloadable TIF only if the rule permits, no more than three experiments/two hours, no slot selection, three review passes, and a PR/merge if checks/tooling permit.

## Pass 1 — plan, implement, and run the shared experiment

- Ranked five hypotheses in `docs/HYPOTHESES_20261025_PHASEWIND.md`; selected only PHASEWIND. The plan names data layers/signatures, missed-fault rationale, method differences, mimics, cost, data availability, and the official-source check status.
- Restored the pinned feature stack and verified all 12 pinned inputs. Implemented `gems/phasewind.py` and five synthetic tests. The operator reads Band 2 RTP and no labels/catalogue; it reuses `gems.breakline.percentile_rank`, the shared buffered holdout, `vendor/gems57/evaluate_holdout.py`, and `gems.breakline.spaced_top_mask`.
- The initial 37,654-dot budget was infeasible under the shared 2.83-px floor. A pre-DTI amendment fixed the primary at 20,000 dots and left two ablations unscored; no zero-score filler or spacing change was used.
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, α=0.2, β=0.8, 300 m triangular kernel): primary 0.0291145349 [0.0241141856, 0.0337746352]. Maximum separate-feature/arm canary was **HOLDOUT-CANARY symmetric AUC 0.5024303**; all canaries were below 0.90. No weekly slot was used.

## Pass 2 — line-by-line protocol/source review and corrective stop

- Reviewed the actual public audit output carefully: its pre-placement surface section compares the PHASEWIND continuous surface, while the CLI's final section was computed against a placeholder `data/parent_R0_zeros.tif`. The latter is not a PHASEWIND final-dot result. Raw positive-surface overlap is not substituted for final-dot overlap.
- Sequencing caveat: the surface scan ran after fold-specific holdout emissions needed to compute DTI, but before full-domain production placement. If the user's term “placement” includes holdout-only predictions, the scan was not strictly before every dot emission; this is disclosed in the run card. No production final dots were made.
- Checked 91 local exact-grid rasters: worst measured surface `|rho|` 0.0031471. The current public GitHub scan found 102 repositories, all default-branch trees available, and compared 1,336 exact-grid rasters; worst measured surface `|rho|` was 0.0736534. The scan had 79 blob-download failures, so no complete public uniqueness clearance is claimed.
- Independently re-read the exact SHA-verified public witness with the shared saturation helper. It covers all 5,106,385 catalogue-clear cells (zero uncovered). Under the binding literal rule, every nonempty final dot field therefore has guaranteed forward overlap 1.0 (>0.70). **Stopped before full-domain dot placement:** no PHASEWIND final dots, submission TIFF, downloadable run card, or submission-validator receipt was produced. The research run card remains internal in `evidence/` and records null final raster SHA/name/note.
- Verified against `ledger/` that `GEMSDOE32 0.2778` is still `CLAIM`, not organizer-confirmed. Its geometry/lineage in `evidence/r0_forensics_20261024.json` is local forensic evidence, not a score receipt.
- Live-reviewed the DrivenData problem/metric page, the September 2026 DOE/NLR Official Rules PDF, the official data tab, the USGS GeoDAWN catalog, and the DrivenData reference repository. The data tab redirected to login. The official page's null/NaN outside-footprint instruction differs from the workbench's finite-zero policy; this unresolved format discrepancy is now visible in README, SESSION_PROMPT, the analysis, and the submission guide.
- Corrected README and SESSION_PROMPT to make the current literal rule binding and mark the old BLINDFAULT matched-budget interpretation historical/non-clearing. Added current status banners to README, homepage, and submission guide. Removed the transient `docs/downloads/phasewind_holdout.json` so no PHASEWIND download is advertised.

## Pass 3 — final verification and remaining limitations

- `PYTHON=.venv/bin/python make test`: **299 passed** (124 existing rasterio deprecation warnings).
- `PYTHON=.venv/bin/python make site`: **PASS**, all 49 currently served rasters passed automated gates; the PHASEWIND stop did not add a served raster.
- `PYTHON=.venv/bin/python make verify`: **PASS**, pinned R0 parent verified (37,654 dots and exact tracked hashes).
- `PYTHON=.venv/bin/python make manifest`: **PASS**, all 8 tracked data-manifest entries matched; the experiment script separately verified all 12 staged pins before reading the feature stack.
- `PYTHON=.venv/bin/python make ledger`: **PASS**, 81 rows; no organizer receipt was recorded for GEMSDOE32 or this session.
- `git diff --check`: **PASS**. The final JSON parse checks caught and corrected missing commas in the amended holdout record and run card; all three PHASEWIND evidence JSON files parse on the final recheck.
- No new submission raster was produced, so no new per-candidate submission validator was run. The existing site check validates existing downloads only.
- PR/merge status is recorded after the branch operation; no weekly slot was selected.

## Current limitations

- No PHASEWIND candidate TIFF exists, so submission-format validation is **not run**, not passed. The intermediate surface GeoTIFF is not a submission.
- Public scan is incomplete (79 blob retrieval failures); it is sufficient to establish the universal duplicate blocker from the verified witness, not to assert global uniqueness.
- The PHASEWIND 20,000-dot DTI is not budget-matched to the 37,654-dot reference. It is a negative local holdout, not an organizer score.
- The reported `GEMSDOE32 0.2778` remains unverified; the 0.3195 and 0.4413 values remain distinct claims/snapshots, not receipts for that submission.
- No real weekly slot was selected or used. The official outside-footprint encoding discrepancy must be reconciled before any future upload.
