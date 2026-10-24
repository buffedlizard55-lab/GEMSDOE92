# Current Repository & Gate Review — `GEMSDOE92` (`2026-10-24`, `COULOMB-LOQO` Primary)

## 1. Current Active Primary & Automated Gate Status

- **Primary Served GeoTIFF:** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`
  - **ZIP (`-zeros.zip`):** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.zip` (`448395137acb4860c24402fb53002539f3c688f8c232c79c23991353623c4c48`)
  - **Unique Submission Name (local ledger):** `GEMSDOE92-COULOMBLOQO-standalone-20261024`
  - **Submission Form Note (`89 / 140` chars):** `h33-h33-2-b2; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)`
  - **Protocol Rule 5 Run Card:** `evidence/coulomb_loqo_run_card.json` (`docs/downloads/coulomb_loqo_run_card.json`)
- **Two-Question Automated Decision:**
  1. **Download Gate:** **✅ OK TO DOWNLOAD FOR RESEARCH** (`10/10` `gems.gates` + `gems57.validate` + `scripts/check_site.py` PASS; `EPSG:32611`, `3730 × 3292`, `float32`, finite `[0.0, 1.0]`, `0.0` outside footprint, `0` NaN anywhere, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`).
  2. **Weekly Slot Gate:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (`submission_eligible: false`, `verdict: "negative"`, `0` weekly slots used) under the literal Rule-1 public scan (`1.000` forward overlap vs dense `17GEMSDOE E-proba-multiscale`, `5,167,373` positive footprint cells).

## 2. Summary of Verified Evidence Across All Instruments

- **Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `22,663` withheld positives):** **`0.009220 [0.007983, 0.010493]`** (#1 all-time repository high; strict draw-blind `d_cat > 2.0` = `0.009689`; beats `HYDROCONDUIT` `0.008549`, `APRONRIDGE` `0.008354`, `PIEDFRONT` `0.006425`, `RELIEF p10` `0.006045`, `STRAINBREAK` `0.005487`, `R0` `0.004006`).
- **Strict Rule-2 Unmasked `d_visible > 2.0` `HOLDOUT-DTI`:** **`0.113316 [0.100614, 0.127163]`** vs `H19-5` `0.096757` (paired 95% CI `[+0.008170, +0.024980]` — first standalone `0% H19-5` model in repo history to beat `H19-5`).
- **Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px):** **`0.090569`** (`standalone`, `+22.2%` over `HYDROCONDUIT` `0.074107`) / **`0.094057`** (`dual45`, `+26.9%` over `HYDROCONDUIT`).
- **Single-Feature Leakage Canaries (`43` raw/derived/LOQO features):** **PASS** (`max symmetric AUC = 0.672638 <= 0.90`).
- **Registry Uniqueness (`REGISTRY-MEASUREMENT`):**
  - Local `GEMSDOE92` (`41` cross-lane rasters): **PASS** (`worst 3-px overlap = 0.6164 <= 0.70`, `|phi| = 0.0493 <= 0.90`).
  - Live 102-repo public scan (`1,368` template rasters): literal STOP (`1.0` vs `17GEMSDOE E-proba-multiscale`); sparse `<= 90k`-px diagnostic (`1,121` rasters): `dual45` **`0 / 1,121` (`max = 0.6488`)**, `standalone` `0.7004` (`1` raster at `61,427` px).
