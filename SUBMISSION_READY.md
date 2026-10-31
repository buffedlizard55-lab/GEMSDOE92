# Submission status — 2026-10-31 review (`H-92M MDC`, three experiments, `0` weekly slots)

## ⚠️ ONE UNIQUE TIF WAS GENERATED TODAY — OK TO DOWNLOAD; NOT CLEARED FOR A SCORING SLOT

* **File:** [`docs/downloads/gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros.tif`](docs/downloads/gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros.tif)
  · [single-TIFF `.zip`](docs/downloads/gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros.zip)
  · [writer receipt JSON (portal name + 140-char note)](docs/downloads/gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros.json)
  · [byte-bound run card](evidence/mdc_run_card_20261031.json)
* **SHA-256** `ad844bbe247ae2883483374218f3ba3eaf1f73e28063b6f324a2b72778d0aa6e` · `187,358` B · `59,654` binary `{0.0,1.0}` dots (`37,654` retained parent dots + `22,000` new `H-92M` dots) · 1-band `float32` · `EPSG:32611` · `3730×3292` · transform identical to `sample_submission.tif` · `0` NaN anywhere, all values in `[0,1]`, zeros outside the footprint → **`11/11` format gates PASS, so the portal range error cannot recur**.
* **Machine verdict:** `RESEARCH_ONLY_NOT_CLEARED` (`docs/downloads/current_submission.json`, `docs/downloads/readiness.json`). Passing gates: format `11/11`; leakage canaries max symmetric AUC `0.6228 ≤ 0.90` (`evidence/mdc_e1_canaries_20261031.json`). Failing gates: `HOLDOUT-DTI` of the new mechanism `0.067590 [0.055534, 0.080305]` is **below** the same-instrument control `control_H19_5 = 0.096748` (paired Δ `−0.029157 [−0.045528, −0.012943]`), and the registry uniqueness ladder is marginal-to-fail (PI-2 symmetric Tversky worst `0.7025 > 0.70`; PI-1 one-sided worst `0.8608 > 0.70`).
* **Scientific finding worth keeping:** the added-dot decision is break-even at a ~10 % hit rate of new dots and `+0.046` at 20 % (MODEL sensitivity table in the run card). Because the fleet has already published `2,350` unique rasters over the same area, the residual *undiscovered-by-others* ground is precisely where the evidence is weakest — so the next attempt must raise detector precision, not re-arrange dots.
* **Focus-nine answer:** every one of the nine requested sites' best rasters is a byte-identical copy also served by other repositories (up to `17` mirrors), so **none is unique and none should be re-submitted**; the highest supplied claim among the nine is `GEMSDOE32 = 0.2778 CLAIM`. Full table: **[docs/EXEC_SUMMARY_20261031.html](docs/EXEC_SUMMARY_20261031.html)**.

---

# Submission status — 2026-10-29 review (`ADMITRELAY` + `LBM-v3`)

## ⛔ DO NOT SUBMIT — no candidate is cleared for a weekly competition slot (`submission_eligible: false`, `0` slots spent)

- **Newest 2026-10-29 research candidate (`MARUSSI-TRISHEAR`, `verdict: negative`):** [`docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.tif`](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.tif) (`SHA-256 = f8f8703e4f8efb8f3397ecc5dc8c0fd68b06c64a089a89b02ee7a91395b3a59b`, `34,000` binary dots) is **OK TO DOWNLOAD FOR RESEARCH ONLY** (`11/11` format gates PASS in `[0, 1]`, `24/24` leakage canaries PASS `<= 0.8115`, `PI-1` unique across all `2,262` 8-owner rasters on both pre-placement surface `0.6564 <= 0.70` and final dots `0.6564 <= 0.70`, deployed `E3 HOLDOUT-DTI = 0.157774 [0.144291, 0.171647]` beating `R0_recipe = 0.097750` by `+0.060024` and `E2 = 0.172273`), but **NOT CLEARED FOR SUBMISSION**: neither `E2` nor `E3` beat repo all-time `HOLDOUT-DTI` best (`relay_conduit = 0.184485`), `LBM-v3 MODEL` (`0.16204`) is below `GEMSDOE92 lbmc1 = 0.2784 CLAIM`, and literal `17GEMSDOE` dense witness is `1.000 > 0.70`. See [2026-10-29 MARUSSI-TRISHEAR executive summary](docs/executive-summary-20261029-marussi-trishear.html) and [run card](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af_run_card.json).
- **Newest 2026-10-29 research candidate (`ADMITRELAY`, `verdict: negative`):** [`docs/downloads/gemsdoe92-admitrelay1-37654dots-20261029-b8051a75-zeros.tif`](docs/downloads/gemsdoe92-admitrelay1-37654dots-20261029-b8051a75-zeros.tif) (`SHA-256 = b8051a75da299099fb7b43aed18c06aeefa8291d78b523e3083f9620a5527214`) is **OK TO DOWNLOAD FOR RESEARCH ONLY** (`11/11` format gates PASS in `[0, 1]`, `20/20` leakage canaries PASS with max symmetric AUC `0.7809 <= 0.90`, `PI-1` unique across all `2,262` 8-owner rasters on both pre-placement surface `0.6350 <= 0.70` and final dots `0.6470 <= 0.70`), but **NOT CLEARED FOR SUBMISSION**: literal `17GEMSDOE` full-support witness is `1.000 > 0.70`, deployed `E3` `HOLDOUT-DTI = 0.077725 [0.066925, 0.088309]` is below `R0_recipe = 0.097750` (unconstrained fold-proper `E2 = 0.106741 [0.092827, 0.119464]`, paired Δ `+0.008991 [-0.001510, +0.019159]`), and Goodhart-debiased `LBM-v3` `MODEL` estimate is `0.2058` (vs already-scored `GEMSDOE92 lbmc1 = 0.2784 CLAIM`). See [2026-10-29 executive summary](docs/executive-summary-20261029-admitrelay.html) and [run card](docs/downloads/gemsdoe92-admitrelay1-37654dots-20261029-b8051a75_run_card.json).

---

# Submission status — 2026-10-28 review

## ⛔ DO NOT SUBMIT the current RIESZ-LOCKED candidate

The file is **OK TO DOWNLOAD FOR RESEARCH ONLY**. Local file-format/range validation passes, but it fails required promotion gates: the recorded pre-placement surface and final full-support registry overlap are `1.000` (limit `0.70`), and archived `HOLDOUT-DTI` is below the R0 control. No organizer score receipt exists in this repository. **Do not upload this file or spend a weekly slot.**

- Research file: [`docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif`](docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif)
- SHA-256: `d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a`
- `MODEL` projection: `0.321602` (not an organizer score)
- `HOLDOUT-DTI`: `gems57-pooled-hide-v2`, 22,663 withheld positives, `0.037987 [0.031011, 0.044656]`
- R0 recipe `HOLDOUT-DTI`: `0.097750 [0.085900, 0.110766]`
- Paired difference: `-0.059763 [-0.072005, -0.046653]`
- Portal name/note in the run card are artifact metadata only and are **not approval to upload**.

See [current GitHub Pages summary](docs/index.html), [how-to-submit guide (for a future cleared candidate only)](docs/how-to-submit.html), [nine-site review](docs/nine-sites.html), [three-pass review](docs/REVIEW_20261028_PROTOCOL.md), and [machine readiness status](docs/downloads/readiness.json).

The previous 2026-10-27 “OK TO SUBMIT” status for LBMC1 is historical and superseded. It had an unmet R0 holdout gate and registry-overlap issues; see its immutable evidence and the current review. The latest site/readiness JSON is the active status source.
