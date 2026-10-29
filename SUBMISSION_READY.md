# Submission status — 2026-10-29 review

## ⛔ DO NOT SUBMIT — no candidate is cleared for a weekly competition slot

All served GeoTIFFs in `docs/downloads/` are **OK TO DOWNLOAD FOR RESEARCH ONLY** (`11/11` automated GeoTIFF format/range gates PASS across all `129` served `-zeros.tif` files, `0` NaN/Inf, values in `[0.0, 1.0]`, exact `EPSG:32611` grid), and **0 weekly portal slots** were spent in this session.

### 1. Latest 2026-10-29 Candidate: `MARUSSI-TRISHEAR` (`verdict: "negative"`, `submission_eligible: false`)
- **Research file:** [`docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.tif`](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.tif) ([one-TIFF ZIP](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros.zip) · [run card](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af_run_card.json) · [11-gate audit](docs/downloads/gemsdoe92-marussitrishear-34000dots-20261029-236171af-zeros-audit.json) · [readiness JSON](docs/downloads/marussi_trishear_readiness_20261029.json) · [2026-10-29 Executive Summary](docs/executive-summary-20261029-marussi-trishear.html))
- **SHA-256:** `f8f8703e4f8efb8f3397ecc5dc8c0fd68b06c64a089a89b02ee7a91395b3a59b` (`34,000` binary `{0.0, 1.0}` dots, `min d_cat = 3.6056 px > 3.0 px`)
- **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, 22,663 withheld positives):**
  - Deployed `E3` (`34,000` dots, Lagrangian dual `PI-1` cap): **`0.157774 [0.144291, 0.171647]`** (paired `Δ = +0.060024 [+0.046290, +0.074443]` vs `R0`-recipe control `0.097750 [0.086127, 0.109282]`)
  - Full 24-ch `E2`: **`0.172273 [0.158850, 0.185206]`** (paired `Δ = +0.074523 [+0.061164, +0.087925]` vs `R0`-recipe control)
  - Solo-feature leakage canaries: `max sym AUC = 0.8115 <= 0.90` (`0.5783` across 14 zero-catalogue physics channels) — **PASS**
- **2,262-SHA Registry Uniqueness (`108` repos across 8 owners):**
  - Pre-placement surface `PI-1`: **`0.6564 <= 0.70`**, `|ρ| = 0.6632 <= 0.90` — **PASS**
  - Final binary dots `PI-1`: **`0.6564 <= 0.70`**, `|ρ| = 0.0886 <= 0.90` — **PASS**
  - Literal full-support dense-witness reading vs `17GEMSDOE`: `1.000 > 0.70`
- **`LBM-v3 MODEL` projection (not an organizer score):** `0.16204`
- **Why held back (`DO NOT SUBMIT`):** Neither `E2` (`0.172273`) nor `E3` (`0.157774`) exceeded the repository's all-time `HOLDOUT-DTI` best (`relay_conduit = 0.184485`), and the literal dense-witness overlap reading remains `1.000`.

### 2. 2026-10-29 Fleet Receipt Note (`lbmc1` `0.2784 CLAIM`)
- Prior `GEMSDOE92` candidate `gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif` (`SHA-256 = e928d3c3…3a1c`) was reported in the `2026-10-29` fleet list at **`0.2784` (`CLAIM`, unreceipted)** — the highest owner-reported `CLAIM` across all `133` scored entries (`+0.0006` above `GEMSDOE32` `0.2778`). Do **not** re-upload `lbmc1` (already submitted/scored per owner claim list).

### 3. Status-Feed Primary (`rieszlbm2` — `DO NOT SUBMIT`)
- Research file: [`docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif`](docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif) (`SHA-256 = d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a`, `HOLDOUT-DTI = 0.037987 [0.031011, 0.044656]` below `R0` control `0.097750`, `verdict: "negative"`, `submission_eligible: false`).

See [current GitHub Pages summary](docs/index.html), [2026-10-29 MARUSSI-TRISHEAR executive summary](docs/executive-summary-20261029-marussi-trishear.html), [how-to-submit guide](docs/how-to-submit.html), [nine-site review](docs/nine-sites.html), and [machine readiness status](docs/downloads/readiness.json).
