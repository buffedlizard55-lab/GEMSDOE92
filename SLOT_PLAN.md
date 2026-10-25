# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`RIEDELVALVE` Session)
## Current decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT** (`submission_eligible: false`, `0` slots spent, `114 BUILT / 0 RECEIPT`)
Newest parallel `RIEDELVALVE` arm `riedel_n90k` (`docs/downloads/gemsdoe92-riedelvalve-riedel_n90k-90000-20261025-e57353de-zeros.tif`, SHA-256 `75d61cb1e548c27c1fa8804a124287996241988f715cb50f3c65c468cb3bc1e0`) is ✅ OK TO DOWNLOAD FOR RESEARCH (`11/11` automated `[0, 1]` gates PASS), passes **both** local (`0.4702 <= 0.70`) and `102`-repo public `dual_reading` uniqueness (`0.6384 <= 0.70`), confirms the additive `37,654@1.0 + 52,346@0.30` Tversky tail (`+0.000875 [+0.000531, +0.001215]` static `HOLDOUT-DTI`), and reaches `0.112719` (`#1` among `dual_reading_unique` LOQO lanes) on `USGS SGMC PROXY`, but remains ⛔ DO NOT SUBMIT (`verdict: "negative"`): literal `17GEMSDOE` dense-surface overlap `1.000 > 0.70` and static `HOLDOUT-DTI` `0.009054 < KNICKLOQO standalone 0.010788`. Next recommended experiment: `KNICKLOQO-N90K` (`evidence/riedelvalve_run_card.json`).

---
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-26, Post-LISTRIC Session)
## Current decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT** (`submission_eligible: false`, 0 slots spent this repo)
Newest LISTRIC standalone (`h33-h33-2-b2-LISTRICstandalone-20261026-a705162a-zeros.tif`, SHA `7e4b4636…1e2ab`) is ✅ OK TO DOWNLOAD (automated [0,1] gates PASS) but ⛔ DO NOT SUBMIT: public dual-reading duplicate 0.710735>0.70, literal 1.000, paired holdout gain vs KNICKLOQO not significant. Selector candidate remains KNICKLOQOstandalone pending human dual-vs-literal policy decision. See `evidence/listric_run_card.json`.

---
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`POISSONFLEX` Session)
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-25, Post-`GRAV-QUAD` Session)

## Current Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent, `95 BUILT / 0 RECEIPT`)**

- **Newest Session Research Artifacts (`RADIOCONTACT` + `GRAV-QUAD`, 2026-10-25, pre-registered Rank 1 and Rank 3 of `docs/HYPOTHESES_20261026_RADIOCONTACT.md`):**
  - `docs/downloads/gemsdoe92-radiocontact-20261025T041646Z-zeros.tif` (SHA-256 `026a52ff46d695bb79ae39780c154cba9cc69e039e7d2a4d1fe898c6c0a79345`; static `HOLDOUT-DTI = 0.005066 [0.003638, 0.006583]`; max leakage-canary AUC `< 0.90`; 9/9 format gates PASS; `verdict: negative`).
  - `docs/downloads/gemsdoe92-gravquad-20261025T145744Z-zeros.tif` (SHA-256 `9ea3e2e01fba5e733964e1252c729a70f0d61edc499c848628d83946d49c7ab5`; static `HOLDOUT-DTI = 0.005092 [0.004001, 0.006253]`; strict Rule-2 also `0.005092`; paired delta vs `R0` `+0.001086 [-0.000082, +0.002312]` — CI crosses 0, not significant; max leakage-canary AUC `0.5362`; locally unique vs 107 local rasters (worst overlap `0.3044`, `|rho| = 0.0523`); 9/9 format gates PASS on an independent disk re-read; `verdict: negative`).
  - Neither beats the repository's promotion bar (COULOMB-LOQO `0.113316` Rule-2 / `0.009220` static; KNICKLOQO `0.010788` static, all-time record). Both are **OK TO DOWNLOAD FOR RESEARCH**, both are **DO NOT SUBMIT**. Public-registry scan was deliberately skipped for GRAV-QUAD per the 3-experiment/2-hour session budget (local uniqueness check alone already clears it; RADIOCONTACT and DRAINAGE-KNICK earlier in this session arc had already confirmed clean against the full public registry fleet).
  - Both lanes are now live on the public site (`docs/index.html`, `docs/executive-summary.html`, `docs/SUBMIT.html`) with explicit green/red badges; full `pytest` suite passes `367 / 367` after the site edits.
  - 5 new ranked, untried hypotheses for a future session are recorded in `docs/HYPOTHESES_20261025_NEXT.md`, with `LOQO-FEATURE-EXPAND` (folding the GRAV-QUAD and RADIOCONTACT features into the existing supervised quadrant-debiased LOQO ensemble) ranked first by expected-gain/cost.

- **Newest Session Research Artifact (`POISSONFLEX`, 2026-10-25):** `docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif` (`SHA-256 = 37b18c200e84c77b39b07e527b17d4395968389aaf3ff0c175c71204b2065f9b`, `45,000` dots via nested visible-only OOF support; strict draw-blind `d_vis > 2.0` `HOLDOUT-DTI = 0.107466 [0.094158, 0.120431]`, static `d_cat > 2.0` `HOLDOUT-DTI = 0.008824 [0.007601, 0.010081]`, off-catalogue `USGS SGMC PROXY = 0.120957` `+35.4%` over `COULOMBLOQO standalone`; `10/10 + 13/13` format gates PASS; passes all `97` local rasters `<= 0.6488` and all `<= 80k`-dot public rasters across `102` repos `<= 0.6804`, but trails `COULOMBLOQO standalone` `0.113890` and hits `0.7541 > 0.70` on `125,890`-px `62GEMSDOE ventcons` under the `150k` dot-field cap -> **`verdict: "negative"`, DO NOT SUBMIT**; `evidence/poissonflex_run_card.json`).
- **Closed Selector Investigation (`evidence/coulomb_loqo_dual_reading_selector.json`):** Re-auditing `COULOMBLOQO standalone` and `COULOMBLOQO dual45` across all `1,321` non-self public blobs (`102` repos, `0` missing blobs) under `uniqueness.dual_reading_decision` confirmed **both fail closed** (`standalone` `0.739842 > 0.70` across `8` sparse `100k–126k`-px witnesses; `dual45` `0.722420 > 0.70` across `4` witnesses). **Zero artifacts in the repository are cleared for a weekly slot.**

---

# Historical Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `COULOMBDM` & `COULOMB-LOQO` Merged State)

## Prior Slot Decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `0` weekly slots spent, `74 BUILT / 0 RECEIPT`)**

- **Current Research Download (`data-primary="true"`):** `docs/downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif` (`SHA-256 = 44efd202e8b96b9812de4693bd7f1ed05afed28de7e2e9413f72bc139ff18b12`, static `HOLDOUT-DTI = 0.007816`, **`0 / 1,181` `<= 150k`-px sparse public overlaps `> 70%`**) and zero-label standalone sibling `docs/downloads/h33-h33-2-b2-COULOMBDMcoulomb1d-20261024-826b2fb3-zeros.tif` (`SHA-256 = 510c3012f4866e8ea2f0debd0aba799a7b7765a4e18f0954d2d1067ddd01e172`, `0% H19-5`, `0%` catalogue labels, Rule-2 `d_vis > 2.0` `HOLDOUT-DTI = 0.094496`, **`0 / 1,181` `<= 150k`-px sparse public overlaps `> 70%`, max `0.5859`**; `evidence/coulombdm_run_card.json`).
- **Repository Holdout-Best Artifact (`COULOMB-LOQO`):** `docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif` (`0.009220` static / `0.113316` LOQO `d_vis > 2.0`, `1` sparse public overlap `0.7004` at `61k` px; hybrid sibling `COULOMBLOQO dual45` `0.009107` static, `0 / 1,121` `<= 90k`-px sparse public overlaps `> 70%`):
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

---

## Merged parallel-branch selector records (`COULOMB`, `APRONRIDGE`)

# SLOT_PLAN — current selector state (2026-10-24, COULOMB session): NO SLOT AUTHORIZED — research downloads only

## COULOMB session decision: **NO SLOT AUTHORIZED — DO NOT SUBMIT (`submission_eligible: false`, `verdict: negative`)**

Three new format-valid standalone research downloads (`10/10` gates + `13/13` `gems57.validate` PASS each):
`COULOMBseismo-20261024-d243140b` (lead, `HOLDOUT-DTI 0.005808 [0.004846, 0.006809]`),
`COULOMBfree-20261024-d0cf5db5` (`0.005689`), `COULOMBopen-20261024-58a7a394` (`0.005184`).
All beat `R0` (`0.004006`) but trail the `0.008549` promotion bar with paired CIs excluding promotion
(seismo vs bar `Δ −0.002741 [−0.004137, −0.001382]`), and the lead arm trips the binding dense public
witness (`17GEMSDOE E-proba-multiscale`, `forward_overlap = 1.000`, `evidence/public_witness_coulomb.json`).
Locally unique (`0.263–0.290 ≤ 0.70`, `|φ| ≤ 0.024`); canaries `20/20 PASS`. **No slot used this session
(3/3 experiment budget consumed as research).** Promotion bar stays
`HYDROCONDUIT f45hydro 0.008549` (still the repo holdout best; parallel-session branch primary
`GEOTENSION free1d` scored `0.007615`). Run card: `docs/downloads/coulomb_run_card.json`.

---

# SLOT_PLAN — current selector state (2026-10-24, APRONRIDGE session)

## Current primary artifact: `APRONRIDGE free1d` — #1 Holdout-DTI & locally unique, blocked ONLY by dense public witness (`verdict: negative`, no slot used)

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

# SLOT_PLAN — prior parallel state (2026-10-24, STEPEDGE session)
# Weekly Slot Plan — GEMSDOE92 (Updated 2026-10-24, `HYDROCONDUIT` Session)

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
