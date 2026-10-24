# GEMSDOE92 session prompt and operating contract

> **Read this file and [`README.md`](README.md) at the start of every project session.** Then read [`SLOT_PLAN.md`](SLOT_PLAN.md), [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), [`IRREGULARITIES.md`](IRREGULARITIES.md), and the current review/status/run card before making a project decision. The checkout is the source of truth; older session prose can be stale and must be checked against the current status feed.

## Current status — 2026-10-24

**No current GeoTIFF is cleared for competition submission. All linked TIFFs are research-only archives; DO NOT SUBMIT. No weekly slot was selected or used in this review.** No new candidate or experiment was generated because the literal uniqueness gate is blocked before placement.

A Git-blob- and byte-verified public 17GEMSDOE raster matches the competition grid and has positive support on all `5,167,373 / 5,167,373` footprint cells. Under the literal rule, any nonempty in-footprint candidate has **REGISTRY-MEASUREMENT** forward overlap `1.0` with this witness, above the 0.70 stop. A Spearman rank correlation against a constant all-positive support is degenerate/undefined; overlap alone is decisive. This is one binding witness, **not** a fresh exhaustive registry inventory. Do not exempt dense rasters, alter the threshold, or create an empty/cosmetic raster to evade the rule. See [`docs/downloads/current_status.json`](docs/downloads/current_status.json), [`docs/downloads/current_review_run_card.json`](docs/downloads/current_review_run_card.json), and [`docs/REPO_REVIEW_20261024.md`](docs/REPO_REVIEW_20261024.md).

The full official 19-band feature stack is absent from the local cache. The shared evaluator and writer are present at `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. The checkout now includes a prior SPRINGALIGN f33Ctop artifact from merged upstream PR #42; its saved HOLDOUT-DTI is below the holdout best and its public-witness status is negative. It was not generated or rerun by this review. No new holdout, leakage canary, candidate surface, final-dot comparison, or candidate-format audit was run here. Do not call a hypothesis viable until inputs/provenance are available and the registry stop is resolved.

## Mission and user requirements

Build a scientifically defensible and auditable DOE GEMS submission system for the fault-prospectivity challenge: rank distinct geological hypotheses before a new method; use the prescribed spatial holdout; compare pre-placement surfaces and final dots to the registry; produce a uniquely named, easy-to-download, correctly formatted GeoTIFF only if all gates pass; run automated validation without a human raster inspector; write a machine-readable run card; and explain the DrivenData form with a note of at most 140 characters. Upload and slot selection remain separate human actions.

Preserve Arena/project core values explicitly:

- **Maximize P(Win)** — protect the slot and make evidence-based choices; do not gamble on unvalidated ideas.
- **Own the Outcome** — keep negative results, fix shared defects once, document uncertainty, and make a no-go status unmistakable.

The prompt associates GEMSDOE32 `h33-h33-2-b2` with **CLAIM 0.2778**. This repository has no organizer receipt for that value. The prompt’s leaderboard snapshots `0.3195` and `0.4413` conflict and neither was refreshed here. Plausible design mechanisms (fixed prediction budget, reducing spatial redundancy, avoiding known mapped traces) are hypotheses—not verified causal explanations. No local holdout or proxy establishes whether a competition score was beaten.

## Hard experiment protocol

1. **One declared method lane.** Do not copy a previous raster and label it a new candidate. Before implementation, rank **3–5 distinct geological hypotheses**. For each specify the exact layer(s), targeted physical signature, why it might detect a fault missing from the catalogue, difference from this repo’s implemented methods, qualitative expected value/cost, named non-fault mimic, and data availability/source. Do not claim global novelty based only on this checkout.
2. **Source/availability gate.** Name official, trusted inputs and verify availability/provenance/terms before describing the candidate as viable. Competition pages may require competitor authentication. Hash-matching a public owner mirror proves byte identity, not organizer authenticity or permission to redistribute. Do not claim that a page/file was freshly checked unless it was.
3. **Reuse shared components.** Use the authorized cached feature stack when present, `vendor/gems57/evaluate_holdout.py`, and `vendor/gems57/submission_writer.py` (or the established shared writer). Fix shared tool defects in the shared implementation; do not fork a private evaluator.
4. **Holdout construction.** Hold out whole fault segments/components with a spatial buffer. Derive every catalogue-based feature only from visible faults; mask visible faults pixel-exactly. Score pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel. Report evaluator version, number of withheld positives, point estimate, and 95% CI. A local catalogue hide/recover result is **HOLDOUT-DTI**, not an organizer score and not proof of discovery of private uncatalogued faults.
5. **Leakage canary.** Test each feature alone on the holdout. AUC >0.90 (use symmetric AUC if direction may reverse) is a leakage alarm until investigated and resolved; do not simply drop a bad feature without documenting why.
6. **Registry gate before and after placement.** Compare the *actual* pre-placement prospectivity surface and final candidate dots to accessible registry rasters. If absolute rank correlation exceeds 0.90 OR more than 70% of dots/support lie within 3 pixels of one registry raster, record a duplicate and stop. The full registry must be rescanned for a clearance claim; a single known failing witness is sufficient to reject. Local uniqueness is not global uniqueness. Do not replace the candidate surface with another raster in a retrospective audit.
7. **Run card.** End each experiment with JSON recording: hypothesis; mechanism; named non-fault mimic; HOLDOUT-DTI result/95% CI or `NOT_RUN` and reason; registry comparison or `NOT_RUN` and reason; candidate raster SHA-256 or `NOT_GENERATED`; validator output (NaN in footprint, value range [0,1], CRS/shape/transform match) or `NOT_RUN`; unique submission name and ≤140-character note or `NOT_GENERATED`; positive `promote` or `negative` verdict (use `blocked` when prerequisites prevent experiment). No fabricated blanks.
8. **Budget/slot.** Stop after **3 experiments or 2 hours**. Do not select or spend a weekly competition slot during development. Human slot selection/upload is a separate step.
9. **Evidence labels.** Distinguish **HOLDOUT-DTI**, **ORGANIZER-CONFIRMED** (actual submission-page receipt), **CLAIM**, **MODEL**, **PROXY**, **REGISTRY-MEASUREMENT**, and **LEADERBOARD-SNAPSHOT**. Never write a projection or proxy as a score; never use a local holdout as a leaderboard comparison.

## Download and submission requirements

- Only offer the explicit zeros-outside GeoTIFF for future submissions; the organizer form previously reported `Predicted values must be in range [0, 1]` for a bad upload.
- Homepage must state separately whether each file is **OK TO DOWNLOAD** and whether it is cleared/recommended for a weekly slot. Current TIFFs must say research-only / **DO NOT SUBMIT**.
- The exact file must have a unique descriptive name, SHA-256, and a form note ≤140 characters. The instructions must explain file, name, note, and upload page while keeping selection/upload human-only.
- Automated checks must reread the exact served bytes and verify one-band float32 GeoTIFF, matching CRS/shape/transform, no NaN inside the footprint, finite in-footprint values in [0,1], and the required outside-footprint convention. A format pass is not scientific validation, uniqueness, eligibility, or organizer acceptance.
- Never silently change nodata, clip out-of-range values, convert NaNs, or re-encode a candidate; record any justified transformation.
- Keep competition data and generated rasters out of public Git unless redistribution terms are resolved. Existing tracked rasters are flagged in `IRREGULARITIES.md`; do not expand the exposure casually.

## Current local verification / evidence boundary

- System date recorded at final validation in this review: `2026-10-24T18:28:42Z`.
- Final verification after SPRINGALIGN reconciliation: `.venv/bin/python -m pytest tests -q` → **140 passed**, 17 existing Rasterio pending-deprecation warnings; `scripts/check_site.py` → **15/15 served TIFFs pass**; pinned data manifest → **PASS**; parent R0 verification → **PASS**; CRLF-aware staged and working-tree whitespace checks (`git -c core.whitespace=cr-at-eol ... --check`) → **PASS**; local HTML link scan → 5 HTML files, no broken relative targets; all **93** reviewed JSON files parse.
- The pinned public witness has Git blob SHA-1 `374c88b1da2b803e2ed160de467fd71ae114010d`, SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`, 25,065,181 bytes, matching template grid, and 5,167,373/5,167,373 positive footprint cells. Its full positive support causes the literal overlap stop.
- Historical ANASIG file SHA-256: `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`; historical forward overlap to the public witness **REGISTRY-MEASUREMENT** 1.0. It remains a negative archive, not a submission.
- Saved best local reference only: **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, 0.0060451323971729325, 95% CI [0.005187022524132649, 0.00692683880217307]; not rerun here, not an organizer score, and its RELIEF raster is duplicate-stopped.
- No current organizer receipt, live leaderboard refresh, or quota was obtained. DrivenData and several official non-GitHub pages were outside this session’s outbound host allowlist. Only the GitHub reference-solution page was fetched live; all other official links are for manual/source-owner review.
- Three DILATATION TIFF filenames and the inherited SPRINGALIGN filename use `20261025`, future relative to the environment date. DILATATION provenance is unresolved; the SPRINGALIGN run card has no generation timestamp. Preserve them as research-only with explicit date caveats; do not present the filename date as verified generation time. The inherited future date in the checker docstring was removed as unverified; behavior was left unchanged.

## Historical candidate notes (archives; none is active)

- SPRINGALIGN, visible-collar, BREAKLINE, SCARPPOL, ANASIG, STRAINBREAK, RELIEF, TIPGAP, STEPOVER, and DILATATION have prior artifacts/evidence in `docs/ANALYSIS*.md`, `docs/NEXT_STEPS.md`, `SLOT_PLAN.md`, `evidence/`, and `ledger/`. SPRINGALIGN f33Ctop (**HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, 0.0048650690 [0.0040254482, 0.0057850159]) is a historical negative and below the saved best. Some historical local scans/holdouts were favorable; the full-footprint-positive witness is a decisive stop. Use each exact run card and the current status feed rather than old “primary/current” prose.
- Historical STRAINBREAK f60 `HOLDOUT-DTI` 0.005487 [0.004522, 0.006430] and ANASIG f45 `HOLDOUT-DTI` 0.004967 [0.004098, 0.005940] are below the saved 0.006045 reference. Both are negative and do not clear the current registry stop.
- Prior broad public scans may be useful historical scope but do not substitute for a current exhaustive scan; the full footprint-positive witness is already sufficient to reject all nonempty in-footprint candidates under the literal rule.

## Trusted source starting points

- [DrivenData competition overview / problem / metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — competitor login may be required.
- [DrivenData reference-solution GitHub repository](https://github.com/drivendataorg/gems-prize-reference-solution) — fetched live in this review; README directs competitors to competition-site data and documents a CPU-only environment option.
- [Official competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

Linked pages outside GitHub were not freshly fetched in this restricted session. Do not describe their current availability or content as verified.

## Next-action checklist for this repository session

1. Reconcile README/session materials, hypotheses, homepage, and submission guides so every page says the same blocked status; label future-dated archives.
2. Run all tests, site checker, manifest, parent check, JSON parse, local link scan, and `git diff --check` after the final content changes.
3. Make three review passes and document findings/evidence.
4. Review the diff; create a PR from the fixed Arena branch and merge only if branch/CI and repository policy permit. No competition slot is involved.
