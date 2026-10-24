# GEMSDOE92 project charter — read before every session

Read `README.md`, `SESSION_PROMPT.md`, this charter, `SLOT_PLAN.md`, `IRREGULARITIES.md`, and the current evidence/status cards before making a project decision. Older session notes can be stale; the current machine-readable status and exact-byte receipts control.

## Mission and core values

Build an auditable, reproducible scientific workbench for prospecting geothermal-related fault structures in DrivenData DOE GEMS Prize #306 (NW Great Basin, EPSG:32611, 100 m grid). The durable goal is a unique, correctly formatted, clearly downloadable submission GeoTIFF, with machine-run validation and a concise ≤140-character form note—only if the actual source, holdout, leakage, and uniqueness evidence permits promotion. A format pass alone never clears a competition slot.

- **Maximize P(Win)** by requiring evidence before risk; no slot gambling on unvalidated ideas.
- **Own the Outcome** by retaining failures, fixing common tools once, and stating uncertainty/no-go status plainly.

The prompt’s GEMSDOE32 `0.2778` is a **CLAIM**, not an organizer receipt in this checkout. The `0.3195` and `0.4413` public-leaderboard snapshots conflict and were not freshly checked. Do not assert that a local holdout beat any competition score or assign causality without verified exact-artifact/receipt evidence.

## Non-negotiable method protocol

- Before implementing a new method, rank 3–5 distinct geological hypotheses. For each: identify exact layers; physical signature; missing-fault rationale; difference from implemented methods; qualitative expected value/cost; named non-fault mimic; official data source and availability. Unverified input means “not viable now.”
- Run one named method lane. Compare the actual pre-placement surface and final dots against registry rasters. If absolute Spearman correlation exceeds 0.90 OR more than 70% of candidate dots fall within 3 pixels of one registry raster, log a duplicate and stop. Local uniqueness is not global clearance. Do not exempt dense positives or alter the rule silently.
- Use authorized cached inputs, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py`/shared writer. Hide whole fault segments/components with a buffer; derive catalogue features from visible segments only; mask visible faults pixel-exactly; score pooled DTI α=0.2, β=0.8, 300 m triangular kernel. Report evaluator version, withheld-positive count, and 95% CI.
- Test every feature alone. Symmetric AUC >0.90 is a leakage alarm until resolved.
- Stop after three experiments or two hours. No development step may select or spend a weekly competition slot. A human selector/upload remains separate.

## Evidence and run-card requirements

Label results distinctly: **HOLDOUT-DTI**, **ORGANIZER-CONFIRMED** (actual receipt), **CLAIM**, **MODEL**, **PROXY**, **REGISTRY-MEASUREMENT**, or **LEADERBOARD-SNAPSHOT**. A proxy, projection, or local holdout is never a competition score.

Each experiment ends with a JSON card containing hypothesis, mechanism, named non-fault mimic, HOLDOUT-DTI/CI or explicit `NOT_RUN`, registry comparison or explicit `NOT_RUN`, raster SHA-256 or `NOT_GENERATED`, validator results (NaN, value range, CRS/shape/transform) or `NOT_RUN`, unique submission name/note ≤140 characters or `NOT_GENERATED`, and verdict `promote` or `negative` (`blocked` if prerequisites prevent the experiment). Preserve negative results.

## Current status (2026-10-24)

**No current TIFF is cleared for submission. All offered TIFFs are research archives; DO NOT SUBMIT. No slot was used.** One independently fetched, hash-verified matching-grid public registry raster is positive on all 5,167,373 footprint cells. Under the literal >70%/3-pixel rule, every nonempty in-footprint candidate has REGISTRY-MEASUREMENT forward overlap 1.0 and must stop. This is one binding witness, not a fresh exhaustive public-registry scan. A rank correlation against a constant all-positive mask is undefined; the overlap branch alone binds. No empty raster or cosmetic mutation may evade the gate.

The full official 19-band feature stack is absent from `.cache/gems_inputs/`; the shared evaluator/writer are present. No new feature or holdout was run in this review. The checkout now includes an inherited SPRINGALIGN f33Ctop artifact from upstream PR #42: its saved **HOLDOUT-DTI** is 0.004865069033082899 (22,663 withheld positives; 95% CI [0.004025448154051826, 0.005785015879540241]), below the saved best and negative versus the public witness; it was not generated or rerun in this review. The saved reference-best remains **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, 0.0060451323971729325, 95% CI [0.005187022524132649, 0.00692683880217307]; historical, not rerun, not an organizer score, and tied to a negative duplicate-stopped RELIEF artifact. Current details: `docs/downloads/current_status.json`, `docs/downloads/current_review_run_card.json`, and `docs/REPO_REVIEW_20261024.md`.

The competition’s official data tab/leaderboard and non-GitHub source pages could not be accessed from this session’s outbound-host allowlist; no login, receipt, or weekly quota is asserted. Hash-verified mirrors are not organizer-authenticated and do not establish redistribution rights. `IRREGULARITIES.md` flags tracked competition rasters and unresolved terms. DILATATION and inherited SPRINGALIGN TIFF names dated `2026-10-25` are future-relative to this review’s `2026-10-24` system date; DILATATION provenance is unresolved, and SPRINGALIGN’s run card has no generated timestamp. Do not treat either filename stamp as verified generation time.

## Submission acceptance and automated validation

Before any future candidate is offered for upload:

1. The exact single-band float32 zeros-outside GeoTIFF must be reopened from disk and pass the shared gates: matching competition CRS/shape/transform; finite in-footprint values in [0,1]; no NaNs inside; documented outside-footprint convention.
2. Store exact SHA-256, status, audit output, and a unique form name/note of ≤140 characters. Do not re-encode, clip, or silently adjust nodata.
3. Pass both pre-placement and final-dot uniqueness checks, holdout decision rule, and feature leakage canaries. A successful format check does not establish scientific value, originality, eligibility, or organizer acceptance.
4. The homepage must distinguish **OK TO DOWNLOAD FOR RESEARCH** from **CLEARED FOR A WEEKLY SLOT**. Current files explicitly say research-only / **DO NOT SUBMIT**.
5. The human selector separately checks the current weekly quota and authorizes any upload. Only the actual submission-page receipt is **ORGANIZER-CONFIRMED**.

## Reproducibility commands

```bash
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/check_site.py
.venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data
.venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data
```

Final verification after SPRINGALIGN reconciliation: 140 tests passed (17 existing Rasterio pending-deprecation warnings), all 15 served TIFFs passed the site checker, manifest and parent R0 checks passed, staged and working-tree `git -c core.whitespace=cr-at-eol ... --check` passed (respecting the ledger’s existing CRLF endings), no broken local HTML relative links, and all 93 reviewed JSON files parsed.

## Official source links for manual/source-owner review

- DrivenData competition overview/problem/metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition data tab (account may be required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- DrivenData reference solution (GitHub, fetched live during this review): https://github.com/drivendataorg/gems-prize-reference-solution
- Official competition rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- USGS GeoDAWN data catalog: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- USGS 3DEP: https://www.usgs.gov/3d-elevation-program
- DOE GDR INGENIOUS #1391: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611

Only the GitHub reference-solution page was freshly accessed here. Other links are not claimed to have been freshly checked.
