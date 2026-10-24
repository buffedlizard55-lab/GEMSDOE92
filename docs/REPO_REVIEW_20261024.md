# Three-pass repository review and SPRINGALIGN reconciliation — 2026-10-24

## Executive decision

**No new GeoTIFF was generated, no weekly slot was used, and no current file is cleared for submission.** The existing TIFF downloads are research artifacts only and are marked **DO NOT SUBMIT**. The user’s literal registry rule is blocked by one matching-grid public witness whose positive support covers the entire footprint. Every nonempty in-footprint prediction therefore fails the forward-overlap threshold before a competition slot is considered. No empty raster, cosmetic encoding change, or dense-raster exemption was used.

The latest prior research artifact is **SPRINGALIGN f33Ctop**, inherited from upstream PR #42 and not generated or rerun in this review. It is format-valid for research download, but its saved holdout result is negative versus the saved best and the public witness blocks it. The complete machine-readable review is [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json); current project status is [`downloads/current_status.json`](downloads/current_status.json).

## Pass 1 — inspect project state, inherited main changes, and evidence

- Read the persistent project brief and operating requirements in `README.md`, `SESSION_PROMPT.md`, `docs/PROJECT_CHARTER.md`, `SLOT_PLAN.md`, `IRREGULARITIES.md`, and the current evidence/status feeds.
- Reconciled the active branch with the upstream `main` update containing SPRINGALIGN (merge commit source `d3d8c9c`). The imported SPRINGALIGN code, audits, run cards, TIFF/ZIP, tests, and analysis were reviewed as existing work; they were not produced by this review.
- The full official 19-band competition feature stack is not present in the local cache. The shared evaluator and writer do exist at `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`. No new feature surface, holdout, leakage canary, final-dot comparison, or candidate was generated.
- Reviewed the homepage and downloads, submission/summary pages, README/session materials, hypotheses, run cards, exact-byte audits, ledger, scripts, tests, local data manifest, and parent recipe.
- Fetched the DrivenData reference-solution GitHub page. Its README directs competitors to download the data from the competition website and describes a CPU-only option. No model training was run.

## Pass 2 — validate decision gates, candidate evidence, and claims

### Binding public-registry stop

The exact public witness is [17GEMSDOE’s E-proba-multiscale raster](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif). The bytes were retrieved and verified independently:

- **REGISTRY-MEASUREMENT:** Git blob SHA-1 `374c88b1da2b803e2ed160de467fd71ae114010d`; SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`; byte count `25,065,181`.
- CRS, shape, and transform match the local competition template; `5,167,373 / 5,167,373` footprint cells are positive.
- Every nonempty candidate support inside this footprint is therefore within zero pixels of the witness support. The literal within-3-pixel forward-overlap branch returns `1.0`, greater than the `0.70` stop. This applies to the actual pre-placement support and final dots. Spearman correlation against constant all-positive support is degenerate and is not the basis of the stop.
- This single witness is sufficient to reject candidates under the supplied rule, but it is **not** a fresh exhaustive public-registry scan. See the receipt `downloads/breakline_public_registry_witness17.json` and `downloads/current_status.json`.

### Inherited SPRINGALIGN f33Ctop — historical, negative, research-only

- File: `downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif`; SHA-256 `1772ad5c62506b6b380e221d2202b583edf0a5be4f96916af655e0478eba11b1`.
- Project/run-card ID: `GEMSDOE92-SPRINGALIGN-f33Ctop-20261025`. Saved optional note (94 characters): `h33-h33-2-b2; SPRINGALIGN f33Ctop 12426 far dots on spring-pair alignment lines >3px off H19-5`.
- Its exact-byte audit reports `overall_pass: true` for local format checks, but `submission_eligible: false`, `unique_under_literal_rule: false`, and `stop_required: true`. Passing format checks means only that the saved file passes local format gates.
- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives: `0.004865069033082899`, 95% CI `[0.004025448154051826, 0.005785015879540241]`. Paired difference vs saved RELIEF p10 holdout best: `−0.0011800633640900336`, 95% CI `[−0.0020652571007335244, −0.0003371520000988227]`. This is a saved local hide-and-recover result, not rerun in this review and not an organizer score.
- Historical local 28-raster measurements: surface worst absolute rank correlation `0.009003`, final-dot maximum forward overlap `0.669995`, worst absolute rank correlation `0.667573`. Those local comparisons are not global clearance. Against the binding full-footprint-positive witness, the literal overlap is `1.0` for every nonempty in-footprint candidate.
- The filename is stamped `20261025`, one day after the review’s system date. The saved run card has no generation timestamp; this stamp is **not verified** as generation time. The artifact was inherited from PR #42, not generated here. See `downloads/springalign_run_card.json`, `evidence/springalign_run_card.json`, `ANALYSIS_20261025_SPRINGALIGN.md`, and `HYPOTHESES_20261025_SPRINGALIGN.md`.

### Other score/evidence distinctions

- The prompt associates GEMSDOE32 `h33-h33-2-b2` with **CLAIM 0.2778**. There is no organizer receipt for it in this checkout. The prompt’s `0.3195` and `0.4413` leaderboard snapshots conflict and were not refreshed; neither is treated as a current confirmed score.
- Saved best local reference: **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 22,663 withheld positives, `0.0060451323971729325`, 95% CI `[0.005187022524132649, 0.00692683880217307]`. It was not rerun in this review, is not a competition score, and its RELIEF raster is itself duplicate-stopped.
- Historical ANASIG exact-byte SHA-256 is `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`; measured forward overlap against the same witness is 1.0. ANASIG remains an archive, not a current recommendation.
- Three DILATATION TIFFs and SPRINGALIGN use filename stamp `20261025`; all are later than this review date. DILATATION provenance is unresolved; the SPRINGALIGN run card has no generation timestamp. No filename stamp is described as a verified creation time.

### Ranked hypothesis backlog and scope

The current four-item qualitative backlog is in [`HYPOTHESES.md`](HYPOTHESES.md): (1) drainage-network deflection/paired knickpoints; (2) conductivity/basement concordance; (3) strain-regime orientation change; and (4) cross-scale potential-field edge persistence. Each entry records its physical signal, missing-fault rationale, named non-fault mimic, difference from methods already represented, source status, cost, and validation/stop rule. The distinct SPRINGALIGN spring-pair alignment lane is now documented as a prior negative result; the remaining ideas are unvalidated and not claimed globally novel.

**The rank-1 idea was not implemented or evaluated.** The full feature stack is absent; moreover, the binding pre-placement witness would stop any nonempty in-footprint surface. No holdout result or numeric projection was invented.

## Pass 3 — reconcile public materials, automated checks, and human-only submission

- The homepage features SPRINGALIGN as the latest prior research artifact with a uniquely named direct TIFF and ZIP download, “OK TO DOWNLOAD FOR RESEARCH” and “DO NOT SUBMIT” labels, its HOLDOUT-DTI/registry caveat, audit/run-card links, the 94-character note, SHA-256, and explicit filename-date caveat. All **15** served zeros-outside TIFFs are linked from the page.
- README and session-start materials preserve Core Values, the full operating requirements, evidence labels, ranked backlog, duplicate stop, and the “no new candidate/no slot” result. The machine-readable status feed and review run card distinguish this no-experiment review from SPRINGALIGN’s inherited prior result.
- Submission instructions are conditional and future-only. A future artifact must have an exact-byte audit with `submission_eligible: true`, a run-card `verdict: promote`, all scientific/registry/format gates, and separate human slot authorization. The competitor alone authenticates, selects the slot, uploads, and records the organizer receipt. Current files must not be uploaded.
- Local site validation reads every served TIFF and verifies the exact-byte audit/run-card for the first download. It checks format/range only; it does not assert score, global uniqueness, eligibility, or acceptance.
- No experiment, competition upload, organizer-receipt claim, or weekly slot was used in this review.

### Final validation

- `.venv/bin/python -m pytest tests -q` → **140 passed**, 17 existing Rasterio pending-deprecation warnings.
- `.venv/bin/python scripts/check_site.py` → **15/15** served zeros-outside TIFFs passed reread, format gates, and page contract; SPRINGALIGN was the first research download and its bytes matched its saved audit/run card.
- `PYTHON=.venv/bin/python make manifest verify` → pinned data manifest **PASS**; parent R0 **PARENT VERIFIED**.
- Local link scan → **5 HTML files**, zero broken relative `href`/`src` targets. **93** JSON files under `docs/`, `evidence/`, and `registry/` parsed without error.
- Staged and working-tree whitespace checks using `git -c core.whitespace=cr-at-eol ... --check` passed after staging. The qualifier recognizes the upstream ledger’s existing CRLF line endings; no actual trailing spaces remain.

## Limitations and official/manual links

- The public registry witness is a competitor-produced raster, not organizer truth or a score. Its hash verifies the fetched bytes, not scientific validity or competition acceptance.
- The witness is decisive for rejection but not an exhaustive current registry inventory. Historical branches, private repositories, other owners, ZIP-only files, and unlinked site assets are outside the reviewed scope.
- The full official feature stack and private target are unavailable locally. No new spatial holdout or feature-only leakage canary was run.
- No current DrivenData receipt, quota, or live leaderboard snapshot is available. Do not conflate the unverified `0.2778` claim, conflicting `0.3195`/`0.4413` snapshots, local HOLDOUT-DTI, or registry measurements.
- Only the GitHub reference-solution page was freshly fetched. Non-GitHub links below are supplied for owner/manual review, not represented as newly accessed. No competition credentials were used or requested.
- Competition-derived rasters are already tracked in this public repository while redistribution terms remain unresolved (`IRREGULARITIES.md`). Do not add new feature stacks/candidate rasters until terms are settled.

Official/manual references: [DrivenData problem/metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) · [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) (fetched) · [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [DOE GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391) · [EPSG:32611](https://epsg.io/32611).
