# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `HYDROCONDUIT` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`)**

- **Current Primary Artifact:** `docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif`
  - **SHA-256 (`-zeros.tif`):** `c9e07ba6627672bfd58b08572a19d48aa16ff07a2f95347993550eaaccba8fdd`
  - **Run Card:** `evidence/hydroconduit_run_card.json` (`docs/downloads/hydroconduit_run_card.json`)
  - **Format & `[0, 1]` Gates:** **PASS (`10 / 10` `gems.gates` + `13 / 13` `gems57.validate`) — ✅ OK TO DOWNLOAD FOR RESEARCH**
  - **Weekly Slot Verdict:** **⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT (`verdict: "negative"`)**

---

## Gate-by-Gate Selector Status for `HYDROCONDUIT f45hydro`

| Gate | Status | Measured Value & Source |
|---|---|---|
| **1. Format & `[0, 1]` Range Gate** | **PASS** | `float32`, `EPSG:32611`, `3730 × 3292`, finite `[0, 1]`, `0` NaN anywhere, `0.0` outside footprint, `0` catalogue mass (`docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-audit.json`) |
| **2. Single-Feature Leakage Canaries** | **PASS** | All 24 raw/derived features `<= 0.90`; max symmetric AUC **`0.65012`** (`evidence/hydroconduit_preplacement_screen.json`) |
| **3. Shared Static `HOLDOUT-DTI` vs `R0` & `RELIEF p10`** | **PASS (New Repo Best)** | **`0.008549 [0.007626, 0.009487]`** (`gems57-pooled-hide-v2`, `22,663` withheld positives); **`+0.004543 [+0.003770, +0.005315]`** vs `R0` (`0.004006`, `+113.4%`); **`+0.002504 [+0.001795, +0.003222]`** vs `RELIEF p10` (`0.006045`, `+41.4%`) |
| **4. Local Registry Uniqueness (29 rasters)** | **PASS** | Pre-placement surface worst 3-px overlap **`0.1892 <= 0.70`**, `|rho| = 0.1098 <= 0.90`; Final dots worst 3-px overlap **`0.5500 <= 0.70`**, `|rho| = 0.2982 <= 0.90` (`evidence/hydroconduit_proxy_audit.json`) |
| **5. Sparse Public Fleet Diagnostic (`<=150k` px, 1,147 rasters across 102 repos)** | **DIAGNOSTIC PASS (`0 > 70%`)** | **Zero** sparse dot-like rasters exceed `70%`: worst `<=150k` overlap **`0.6719`**, worst `<=90k` overlap **`0.6518`**, worst `|rho|` across all `1,332` rasters **`0.3693` final / `0.4396` surface** (`evidence/hydroconduit_public_sparse_diagnostic.json`) |
| **6. Literal Public Registry Gate (incl. dense `>150k`-px surfaces)** | **BLOCKED (STOP)** | `118` dense public rasters (`>150k` positive px, led by `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` with `5,167,373` = 100% positive footprint px) give **`1.0000 > 0.70`** forward overlap (`evidence/hydroconduit_public_registry_uniqueness.json`) |
| **7. Multi-Instrument Cross-Check (`d_visible > 2.0` & `SGMC`)** | **DISCLOSED TRADE-OFF** | Rule-2 fold-by-fold `d_visible > 2.0` `HOLDOUT-DTI` = `0.0852` (vs `0.0968` `H19-5` skeleton-only); off-catalogue `USGS SGMC` `PROXY` = `0.0741` (vs `0.0961` `R0`, `0.1261` `BREAKLINE f45`) |

---

## Why No Slot Is Spent Automatically

1. **Protocol Rule 6:** Promotion to a real DrivenData weekly submission slot (`<= 3 / week`) is strictly an external human selector step. Zero weekly slots have been consumed by this repository (`ledger/submissions.csv`: `49 BUILT`, `0 ORGANIZER-CONFIRMED RECEIPT`).
2. **Human Selector Action Required Before Any Upload:**
   - **Step A (Policy Decision):** Decide whether dense continuous/semi-dense probability surfaces (`> 150,000` positive pixels, such as `17GEMSDOE E-proba-multiscale`) are outside the intended sparse dot-set uniqueness pool. Under that sparse-only (`<= 150k` px) policy, `HYDROCONDUIT f45hydro` is **unique across all 102 public `GEMSDOE` repositories (`0 / 1,147` over `70%`)** AND **#1 on the shared static holdout (`0.008549`)**. Under the current literal rule, it remains blocked (`submission_eligible: false`).
   - **Step B (Calibration Anchor):** `Blocker 0` remains zero `ORGANIZER-CONFIRMED` receipts in `ledger/submissions.csv`. Obtaining or verifying one receipt for `R0` (`0.2778` `[CLAIM]`) anchors whether DrivenData's hidden test set rewards Quaternary piedmont/hydrothermal scarps (`HYDROCONDUIT`, `+113.4%` static `HOLDOUT-DTI`) vs mountain-core bedrock faults (`BREAKLINE`, `+31.3%` `SGMC`).

### Parallel-Session Benchmark Update (`PIEDFRONT` + `STEPEDGE` + `review_20261024`)
- **`PIEDFRONT f35Ptop`** (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`): static `HOLDOUT-DTI = 0.006425 [0.005375, 0.007479]`, `SGMC = 0.059993`, `verdict: negative` (**OK TO DOWNLOAD**, **DO NOT SUBMIT**). `HYDROCONDUIT f45hydro` (`0.008549 [0.007626, 0.009487]`) improves over `PIEDFRONT f35Ptop` by `+33.1%` (`+0.002124`) while overlapping only `56.56% <= 70%` within 3 px (`phi = 0.2000`).
- **`STEPEDGE f60Sraw`** (`GEMSDOE92-STEPEDGE-f60Sraw-20261024`, `docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`): static `HOLDOUT-DTI = 0.003980 [0.003295, 0.004702]`, repo-best `SGMC = 0.141464`, `verdict: negative` (`42.35% <= 70%` 3-px overlap with `HYDROCONDUIT f45hydro`).
- Ledger total across all merged sessions: `54 BUILT / 0 RECEIPT`.
