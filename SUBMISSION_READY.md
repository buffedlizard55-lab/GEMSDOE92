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
