# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `COULOMB-LOQO` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent)**

- **Current Primary Artifact:** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif`
  - **Submission Name (local ledger):** `GEMSDOE92-COULOMBLOQO-standalone-20261024`
  - **Form Note (`89 / 140` chars):** `h33-h33-2-b2; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)`
  - **SHA-256 (`-zeros.tif`):** `8f1f93d8c97b4e1c359ce5fbe07d183214e707aa6bda4ed074c00921f39ad32e`
  - **Run Card:** `evidence/coulomb_loqo_run_card.json` (`docs/downloads/coulomb_loqo_run_card.json`)
  - **Format & `[0, 1]` Gates:** **PASS (`10 / 10` `gems.gates` + `gems57.validate`) — ✅ OK TO DOWNLOAD FOR RESEARCH**
  - **Weekly Slot Verdict:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`)**

---

## Gate-by-Gate Selector Status for `COULOMBLOQO standalone` (and Hybrid Sibling `COULOMBLOQO dual45`)

| Gate | Status | Measured Value & Source |
|---|---|---|
| **1. Format & `[0, 1]` Range Gate** | **PASS** | `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0` NaN anywhere, `0.0` outside footprint, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px` (`docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-audit.json`) |
| **2. Single-Feature Leakage Canaries (43 features)** | **PASS** | All raw bands, derived features (`f01`–`f24`), and LOQO surfaces `<= 0.90`; max symmetric AUC **`0.672638`** (`evidence/coulomb_loqo_screen.json`) |
| **3. Shared Static `HOLDOUT-DTI` (`gems57-pooled-hide-v2`)** | **PASS (#1 All-Time Repo High)** | **`0.009220 [0.007983, 0.010493]`** (`22,663` withheld px); **`+0.005214 [+0.004130, +0.006326]`** vs `R0` (`0.004006`, `+130.2%`); **`+0.003175 [+0.002123, +0.004222]`** vs `RELIEF p10` (`0.006045`, `+52.5%`); beats `HYDROCONDUIT` (`0.008549`) & `APRONRIDGE` (`0.008354`); strict draw-blind `d_cat > 2.0` = **`0.009689`** (`evidence/coulomb_loqo_proxy_audit.json`) |
| **4. Strict Rule-2 Unmasked `d_visible > 2.0` `HOLDOUT-DTI`** | **PASS (#1 All-Time Repo High)** | **`0.113316 [0.100614, 0.127163]`** vs `H19-5` skeleton `0.096757` (paired $\Delta = +0.016559$, 95% CI **`[+0.008170, +0.024980]`** — first standalone `0% H19-5` model to beat `H19-5`) |
| **5. Off-Catalogue `USGS SGMC` `PROXY` DTI (`62,703` px)** | **RECOVERED** | **`0.090569`** (`standalone`, `+22.2%` vs `HYDROCONDUIT` `0.074107`) / **`0.094057`** (`dual45`, `+26.9%` vs `HYDROCONDUIT`, `97.9%` of `R0` `0.096060`) |
| **6. Local Registry Uniqueness (41 rasters)** | **PASS** | Pre-placement surface worst 3-px overlap **`0.6164 <= 0.70`**, `|rho| = 0.1593 <= 0.90`; Final dots worst 3-px overlap **`0.6164 <= 0.70`** (`dual45`: **`0.5982`**), `|phi| = 0.0493 <= 0.90` |
| **7. Sparse Public Fleet Diagnostic (`<=90k` / `<=150k` px across 102 repos)** | **DIAGNOSTIC** | Across `1,121` `<= 90k`-px public submissions: **`COULOMBLOQO dual45` passes `0 / 1,121` (`max = 0.6488 <= 0.70`)**; `standalone` hits `0.7004` (`1` raster at `61,427` px, `15` dots above `0.7000`) and `0.7398` vs `100k`-px `GEMSDOE23` habitat (`evidence/coulomb_loqo_public_sparse_diagnostic.json`) |
| **8. Literal Public Registry Gate (`1,368` rasters incl. dense surfaces)** | **BLOCKED (STOP)** | `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` (`5,167,373` = 100% positive footprint px) forces **`1.0000 > 0.70`** forward overlap (`evidence/coulomb_loqo_public_registry_uniqueness.json`) |

---

## Human Selector Queue Once Blockers Are Resolved

1. **Blocker 1 (Operator Uniqueness Scope Decision):** Decide whether dense continuous/habitat maps (`> 90,000` positive pixels, led by `17GEMSDOE E-proba-multiscale` at `5.17M` pixels) are excluded from the sparse competition-budget uniqueness pool.
   - Under a **`<= 90,000` positive-pixel** competition-budget policy: **`COULOMBLOQO dual45`** (`0.009107` static / `0.1020` `d_vis>2` / `0.0941` `SGMC`, **`0 / 1,121` `> 70%`**) is immediately unique across all 102 public repos, followed by `HYDROCONDUIT f45hydro` (`0.008549` static, `0 / 1,179` `<= 150k`).
   - Under a **`<= 55,000` positive-pixel** budget-matched policy: **`COULOMBLOQO standalone`** (`0.009220` static / `0.113316` `d_vis>2` / `0.0906` `SGMC`, `#1` on both holdout instruments) is the top candidate.
2. **Blocker 0 (Calibration Anchor):** Record one `ORGANIZER-CONFIRMED` DrivenData receipt for parent `R0` (`0.2778` `[CLAIM]`) in `ledger/submissions.csv` before interpreting live leaderboard deltas, and never submit more than one `COULOMBLOQO` arm in a rolling 7-day window.
