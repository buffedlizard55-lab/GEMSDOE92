# Three-pass repository review — 2026-10-24

## Executive decision

**No new GeoTIFF was generated, and no file in this checkout is cleared for a competition slot.** Existing TIFs can be downloaded for research, but the site must say **DO NOT SUBMIT**. The user’s literal uniqueness rule is blocked by one matching-grid public registry witness whose positive support covers the whole footprint. Under that rule, every nonempty in-footprint prediction fails the forward-overlap threshold before a competition slot is considered. No empty raster, cosmetic encoding change, or exemption for a dense raster was used.

The candidate-generation request is therefore **blocked**, not silently marked complete. The full official 19-band feature stack is absent, so the requested rank-1 idea could not be evaluated with the shared holdout. No experiment or weekly slot was used. The complete machine-readable review card is [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json); the site’s current feed is [`downloads/current_status.json`](downloads/current_status.json).

## Pass 1 — inspect repository state and current evidence

- Reviewed the active checkout, project prompt/charter, README, slot plan, irregularities, site pages, generated download audits, ledger, scripts, test suite, local data, and vendor evaluator/writer.
- The checkout starts from `d0574cdfc761e3f25eba8b9818f343b7beae830e` on `arena/465f70f6-gemsdoe92`. No source changes existed at the beginning of this review.
- There is **no** `.cache/gems_inputs/training_features.tif`. The tracked `data/bridge/` directory contains only the bridge/template/catalogue/parent-lineage rasters; it is not the complete 19-band feature stack. The shared evaluator and writer do exist at `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py`.
- Installed the repository-pinned dependencies into an ignored `.venv` for verification only. The environment is excluded from the deliverable snapshot.
- Ran the existing suite and checks before documentation edits: `pytest` → **135 passed**, 17 existing Rasterio pending-deprecation warnings; `scripts/check_site.py` → **14/14 served zeros-outside TIFFs pass local format gates**; pinned data manifest → **PASS**; R0 parent verification → **PASS**. These are engineering checks, not DTI scores.
- Fetched the official DrivenData reference-solution GitHub page. Its README says competitors download data from the competition website and includes a CPU-only environment option; it says GPU training is faster, not mandatory. No model training was run.

## Pass 2 — check protocol gates, source claims, and page consistency

### Registry stop

Independently fetched the immutable GitHub blob for [17GEMSDOE’s E-proba-multiscale raster](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) and verified:

- **REGISTRY-MEASUREMENT:** Git blob SHA-1 `374c88b1da2b803e2ed160de467fd71ae114010d`; SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`; byte count `25,065,181`.
- **REGISTRY-MEASUREMENT:** witness CRS, shape, and transform match the local competition template; `5,167,373 / 5,167,373` footprint cells are positive.
- Since overlap is measured on positive support, every nonempty candidate pixel **inside this footprint** is at distance zero from this witness. The literal rule’s forward-overlap branch therefore returns `1.0`, above the `0.70` stop. This set-inclusion argument applies to both a nonempty pre-placement candidate-support mask and final dots. The full public registry was **not** rescanned in this review.
- Spearman rank correlation against a constant all-positive support is degenerate/undefined; it is not the basis of this stop. The overlap branch alone is binding.
- As an independent historical example, the existing ANASIG TIFF has `37,654` positives and **REGISTRY-MEASUREMENT** forward overlap `1.0` against this witness. This does not make ANASIG a new candidate; its file hash is `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`.

A single failing witness is enough to reject a candidate under the supplied protocol; it is not enough to claim a complete inventory. Dense-raster policy cannot be changed by this agent. See the linked witness receipt and the current status JSON.

### Contradictions and unsupported claims found

1. **Executive summary instructions conflicted with the status banners.** It said the current ANASIG file was blocked, but later steps instructed the reader to upload an older visible-collar TIFF and supplied the collar’s SHA-256 next to the ANASIG instructions. Replaced the imperative steps with a conditional guide that says not to use any current file and obtains the name/note/hash only from a future exact-byte eligible audit.
2. **Homepage’s opening 11GEMSDOE scan described the visible-collar candidate, not ANASIG.** Reframed the page around the universal 17GEMSDOE witness and explicitly stated that no current candidate is cleared. Candidate-specific local/public scans remain scoped to their exact artifact.
3. **README/HTML stated an unverified causal story for 0.2778 and asserted a recipe for the 0.4413 leaderboard entry.** Replaced that with a receipt-aware explanation: 0.2778 is a **CLAIM** in this repository, plausible mechanisms are hypotheses, leaderboard snapshots conflict, and no holdout is comparable to a private competition score. No evidence here establishes that top submissions use a particular blend of DEM, strain, radiometrics, or spring data.
4. **Hypothesis page mixed already-built methods with numeric “expected DTI” projections.** Replaced it with four qualitative, untested candidates, named physical signatures/mimics, differences from this checkout, cost ranking, and data-access blockers. No expected score numbers are asserted.
5. **Future-dated DILATATION artifacts.** Three tracked TIFF names and their associated evidence use `20261025`, despite this review’s system date being `2026-10-24`. Their provenance/time relationship is not established. They remain quarantined in the site’s archive list with an explicit **future-dated / provenance unverified / DO NOT SUBMIT** warning; no claims about them are used to select a candidate.
6. **Future-dated site-checker comment.** The inherited `scripts/check_site.py` docstring claimed it was rewritten `2026-10-25`, a date after this review’s system date. Removed that unverified timestamp and retained an accurate description of the checker; no logic changed.

### Hypothesis shortlist and top-candidate validation

The current shortlist is in [`HYPOTHESES.md`](HYPOTHESES.md). Rank 1 is drainage-network deflection and paired knickpoints from the documented DEM layers (Band 12 `det_elev`, Band 19 `det_elev_slope`). It differs from this repository’s local derivative-based BREAKLINE/SCARPPOL methods by testing channel-network topology and along-channel change points. Plausible mimics include fan avulsion, lithologic resistance, drainage capture, and infrastructure.

**The top idea was not validated.** The required feature stack is absent, non-GitHub official sources could not be fetched in this session, and the binding pre-placement overlap rule would stop every nonempty surface anyway. The [official DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) is the specific source for the competition stack; prior repository records say it is login-gated, but this session could not independently refresh that page. USGS 3DEP is listed only as a possible official terrain source; its availability/coverage was not checked here. These ideas are not being called viable, no holdout number was fabricated, and no slot was touched.

## Pass 3 — verify changes against the request

- The README now carries a persistent project brief and directs future sessions to `SESSION_PROMPT.md`, the charter, slot plan, irregularities, and current review.
- Homepage, executive summary, submission page, and alias page state the same result: research downloads are format-valid where their receipts say so, but **no current candidate is cleared to submit**. The upload procedure is conditional on a future exact-byte audit and selector decision.
- The run card explicitly records `NOT_RUN` / `NOT_GENERATED` instead of inventing a holdout, candidate surface, final-dot check, SHA, validator receipt, submission name, or note for this review.
- Existing downloads retain their historical bytes. No new TIF, ZIP, or competition submission was created.
- **HOLDOUT-DTI** reference only (not rerun in this review): saved best `gems57-pooled-hide-v2`, `22,663` withheld positives, `0.0060451323971729325`, 95% CI `[0.005187022524132649, 0.00692683880217307]`, from `evidence/run_card_20261024.json`. That RELIEF artifact is itself marked negative because it exceeded the registry overlap gate. This value is not a live score and cannot establish whether 0.2778, 0.3195, or 0.4413 was beaten.
- Exact review outputs and data boundaries are in [`downloads/current_status.json`](downloads/current_status.json) and [`downloads/current_review_run_card.json`](downloads/current_review_run_card.json).

## Final validation after the documentation reconciliation

- `.venv/bin/python -m pytest tests -q` → **136 passed**, 17 existing Rasterio pending-deprecation warnings. Four legacy site-contract tests were revised to assert the current research-only/blocked status rather than an obsolete “primary” candidate.
- `.venv/bin/python scripts/check_site.py` → **14 served zeros-outside GeoTIFFs pass** independent reread, format gates, and page contract. The checker’s former future-dated docstring was corrected; its gate behavior is unchanged.
- `python -m gems manifest --manifest registry/data_manifest.json --data-root data` → **PASS**; `python -m gems parent --recipe registry/parents/R0.json --data-root data` → **PARENT VERIFIED**.
- `git diff --check` → **PASS**.
- Local HTML link scan → no broken relative href/src targets. Parsed **85 JSON files** under `docs/`, `evidence/`, and `registry/` → no parse errors.
- No TIFF/ZIP bytes, input data, or competition receipts were changed/created. No experiment/slot was used.

## Irregularities and limitations for follow-up

- The public witness data is a competitor-produced raster hosted in another public repository, not an organizer score or official truth. It was used only as the registry object required by the user’s comparison rule. Git blob/hash checks establish the fetched bytes, not scientific validity or competition acceptance.
- The single-witness measurement is decisive for failure but is not a fresh exhaustive registry inventory. Historical branches, private repositories, other owners, zip-only files, and unlinked site assets remain outside the reviewed scope.
- The full official feature stack and private competition target are unavailable locally. No new spatial holdout or feature-only leakage canary was run.
- No DrivenData receipt, current weekly quota, or fresh leaderboard value is available to this agent. The user-supplied 0.2778, 0.3195, and 0.4413 remain non-equivalent claims/snapshots; do not treat them as this project’s score.
- The current host allowlist permits GitHub and package hosts, not DrivenData, USGS, DOE GDR, EPSG.io, or the linked PDF host. Only the DrivenData reference-solution GitHub page was freshly fetched; the other official links below are provided for review, not claimed as live-verified.
- Competition-derived rasters are already tracked in this public repository despite unresolved redistribution terms (see `IRREGULARITIES.md`). Do not add new feature stacks or generated candidate rasters to Git without resolving those terms.

## Official/manual review links

- [DrivenData problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — fetched live in this review.
- [Official competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
