# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `COULOMBDM` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `60 BUILT / 0 RECEIPT`)**

Current session primary download `GEMSDOE92-COULOMBDM-s45coulomb55-20261024` (`docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif`, SHA-256 `44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12`, note `h33-h33-2-b2; COULOMBDM s45coulomb55: 16944 Coulomb-H19 + 20710 off-skel 1D Coulomb/RTP/clay ridges (>3px H19-5)`) and standalone blind-fault sibling `GEMSDOE92-COULOMBDM-coulomb1d-20261024` (`docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif`, SHA-256 `510c3012f4866e8ea2f0debd0aba799a7b7765a4e18f0954d2d1067ddd01e172`) are **100% format-valid (`11/11` `gems.gates` + `13/13` `gems57.validate` PASS — ✅ OK TO DOWNLOAD FOR RESEARCH)**, pass all `35 / 35` leakage canaries (`max = 0.640176 <= 0.90`), pass local uniqueness across all `44` prior rasters (`<= 0.6796 <= 0.70`), and pass **`1,181 / 1,181` sparse (`<= 150,000` px) public rasters across `102` `GEMSDOE` repositories (`0 > 70%`)**. However, **neither is cleared for a live weekly submission slot (`verdict: "negative"`, `submission_eligible: false`)** because:

1. **Literal Public Dense-Witness Rule (`Rule 1`):** `185` dense public probability surfaces (`> 150,000` positive pixels, led by `17GEMSDOE E-proba-multiscale` at `5,167,373 / 5,167,373 = 100%` footprint positive) force `forward_overlap = 1.000 > 0.70` (`evidence/coulombdm_public_registry_uniqueness.json`).
2. **Pre-Registered Static `HOLDOUT-DTI` Bar:** On static `d_cat > 2.0` `HOLDOUT-DTI`, `COULOMBDM s45coulomb55` (`0.007816 [0.006994, 0.008644]`) beats `R0` (`0.004006`, `+95.1%`) and `RELIEF p10` (`0.006045`, `+29.3%`), but trails [`HYDROCONDUIT f45hydro`](docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif) (`0.008549`) and [`APRONRIDGE free1d`](docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif) (`0.008354`). Meanwhile, on **Rule-2 fold-visible blind-fault `d_vis > 2.0` `HOLDOUT-DTI`**, `COULOMBDM coulomb1d` achieves **`0.094496 [0.085916, 0.102867]`** (**#1 non-CNN in repo**, `+8.9%` over `APRONRIDGE free1d` `0.086787` and `+10.9%` over `HYDROCONDUIT f45hydro` `0.085221`).

### Unified Human Selector Queue (Conditional on Dense-Surface Policy Resolution)

| Queue Priority | Candidate | Static `HOLDOUT-DTI` | Rule-2 `d_vis>2` `HOLDOUT-DTI` | `SGMC PROXY` | Sparse Public `<=150k` (`0 > 70%`?) | Selector Role if Dense Surfaces (`>150k` px) Exempted |
|---:|---|---:|---:|---:|---|---|
| **Option A (Static Holdout #1)** | `HYDROCONDUIT f45hydro` (`c9e07ba6…`) | **`0.008549`** | `0.085221` | `0.074107` | **PASS (`0 / 1,147 > 70%`)** | Best hybrid piedmont + hydrothermal `H19-5` collar candidate |
| **Option B (Standalone Static #1)** | `APRONRIDGE free1d` (`1a29a5d8…`) | **`0.008354`** | `0.086787` | `0.080098` | Spot-checked (`0.603–0.646`); run full 102-repo scan first | Best thin-cover piedmont accommodation apron (`0% H19-5`) |
| **Option C (Rule-2 Blind-Fault #1)** | `COULOMBDM coulomb1d` (`510c3012…`) | `0.006467` | **`0.094496`** | `0.070345` | **PASS (`0 / 1,181 > 70%`, max `0.5859`)** | Best standalone Mohr–Coulomb + upward-RTP + MT clay-cap blind-fault detector (`0% H19-5`) |
| **Option D (Balanced Hybrid)** | `COULOMBDM s45coulomb55` (`44efd202…`) | `0.007816` | `0.086867` | `0.075208` | **PASS (`0 / 1,181 > 70%`, max `0.6796`)** | Balanced `45%` Coulomb-ranked `H19-5` + `55%` off-skeleton Coulomb/RTP/clay crests |

> **Cross-Lane Duplicate Warning (`#IR-92-PIEDFRONT-HYDROCONDUIT-CROSSOVER`):** Never pair `PIEDFRONT f35Ptop` (`e314f4c0…`) with `HYDROCONDUIT f45hydro` (`71.32% > 70%` 3-px forward overlap), and never submit more than one sibling from the same lane (`coulomb1d` / `s35coulomb65` / `s45coulomb55`, `f45pied` / `f45hydro` / `f50hydro`, or `free1d` / `s60f40` / `s50f50`).

---

## Historical Selector Records (Preserved)

### Prior selector state (2026-10-24, APRONRIDGE session)

Primary download `GEMSDOE92-APRONRIDGE-free1d-20261024` (file
`docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif`,
SHA-256 `1a29a5d81e8561954f04a563b4975cb84d00898b8d7634700a9d409a10e06cbc`,
note `h33-h33-2-b2; APRONRIDGE free1d: 37654 standalone 1D piedmont-apron + RTP ridges (0 H19-5)`):

- **Format gates**: `10/10 PASS` on independent disk re-read (`EPSG:32611`, `3730×3292`, `float32`, `[0, 1]`, `0` NaN in footprint, `0.0` outside, `37,654` unit dots, `0` catalogue mass, `d_cat > 2.0 px`).
- **`HOLDOUT-DTI` (`gems57-pooled-hide-v2`, `8` spatial folds, `22,663` withheld positives)**: **`0.008354 [0.006823, 0.010135]`** — **new all-time repository high**, beating `R0` (`0.004006`, paired Δ `+0.004347 [+0.003019, +0.005710]`), `STEPEDGE f60Sraw` (`0.003980`), prior locally-unique best `STRAINBREAK f60s2i` (`0.005487`, paired Δ `+0.002867`), and prior holdout best `RELIEF p10piedmont` (`0.006045`, paired Δ `+0.002308`). Pre-registered hybrid siblings `s60f40` (`0.008291`) and `s50f50` (`0.008097`) also beat `RELIEF p10`; never submit multiple `APRONRIDGE` siblings.
- **Leakage canaries**: `11/11 PASS` (`max symmetric AUC = 0.636490 <= 0.90`).
- **SGMC 1:500k off-catalogue `PROXY`**: `0.080098` vs `R0` `0.096060` (intentional suppression of high-range Mesozoic bedrock contacts in favor of thin-cover piedmont Quaternary accommodation zones; contrast `STEPEDGE f60Sraw` SGMC `0.141464` vs holdout `0.003980`).
- **Uniqueness**:
  - Pre-placement continuous surface vs `29` local rasters (`evidence/apronridge_surface_registry.json`): `worst_|Spearman| = 0.122173 <= 0.90`, `worst_top37654_forward_overlap = 0.552664 <= 0.70`.
  - Final dots vs all `46` cross-lane local rasters (`43` in `evidence/apronridge_proxy_audit.json` + `3` newly merged `STEPEDGE` rasters at `0.3023–0.3783`): **`worst_forward_overlap = 0.460482 <= 0.70`**, `worst_|phi| = 0.056117 <= 0.90` (`local_duplicate: false`).
  - Top public sparse witnesses (`62GEMSDOE` `120k` px, `GEMSDOE23` `91.5k–100k` px; `evidence/apronridge_public_sparse_spotcheck.json`): **`0.6028–0.6456 <= 0.70`**.
  - **Binding public dense witness (`evidence/public_witness_apronridge.json`)**: `17GEMSDOE E-proba-multiscale` (`5,167,373 / 5,167,373` positive footprint cells) forces `forward_overlap = 1.000`. Therefore `submission_eligible = false` and `verdict = "negative"`; **do not spend a weekly slot** until an operator policy decision adds a dense-probability support ceiling (`<= 150,000` positive pixels). Once that policy update is approved and a full refreshed `scripts/audit_public_registry.py` confirms sparse uniqueness, `APRONRIDGE free1d` is the #1 queued candidate for a single weekly slot.

---

### Prior parallel state (2026-10-24, STEPEDGE & HYDROCONDUIT sessions)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`)**

Primary download `GEMSDOE92-STEPEDGE-f60Sraw-20261024` (file
`h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256
`c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`) is
format-valid and literal-unique vs the local dot registry (worst
forward overlap 0.461; surface |ρ| 0.138), with the repo's best SGMC PROXY
(0.141464 vs R0 0.096060). It is **not cleared**: automated gates record
`submission_eligible: false` because HOLDOUT-DTI 0.003980 [0.003295, 0.004702]
does not beat STRAINBREAK f60 (0.005487), RELIEF p10 (0.006045), or APRONRIDGE free1d (0.008354) and paired
Δ vs R0 includes 0. Dense public-witness literal overlap 1.000 is disclosed
(ρ 0.0004; see amended dot-like scope in
`docs/HYPOTHESES_20261024_STEPEDGE.md`). Sibling doses f33/f45Sraw are
duplicates (0.760/0.711 vs same-dose BREAKLINE/SCARPPOL) and must never be
submitted; never pair doses in one week. Selector framing + receipt decision
rules: `docs/ANALYSIS_20261024_STEPEDGE.md` §4. No slot used this session.
Re-validate uniqueness at decision time — verdicts decay as the registry
grows (IRREGULARITIES 2026-10-24).

---

# SLOT_PLAN — prior selector state (2026-10-24, ANASIG session)
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
