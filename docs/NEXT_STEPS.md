# Next Steps — `GEMSDOE92` (After `HYDROCONDUIT` Session, 2026-10-24)

## Current State & Completed Items From Prior Queue

- **Completed in this session:**
  1. Diagnosed *why* `BREAKLINE f45` stalled at `0.004861` (`74.75%` of off-skeleton dots hijacked by bare mountain range-core cliffs `det_elev >= +38.8 m`, `28.9%` transverse E–W/WNW erosional gullies) and discovered `Band 6 tc` is mislabelled Radiometric Total Count (`r = 0.99714` with `GeoDAWN TC`), `GDR #1391` `'Hot '` trailing whitespace + `419` blind chemical-geothermometer pixels (`>= 80 °C`), and static `d_full_cat > 2.0` self-masking.
  2. Pre-registered 5 untried geological hypotheses (`docs/HYPOTHESES_20261024_HYDROCONDUIT.md`) and implemented `HYDROCONDUIT` (`gems/hydroconduit.py`), clearing all 24 single-feature leakage canaries (`max symmetric AUC = 0.65012 <= 0.90`).
  3. Built and evaluated 3 experiments (`f45pied`, `f45hydro`, `f50hydro`): **`HYDROCONDUIT f45hydro` beat both `R0` (`0.004006 -> 0.008549`, `+113.4%`) and prior holdout-best `RELIEF p10` (`0.006045 -> 0.008549`, `+41.4%`)** while passing **local uniqueness (`0.5500 <= 0.70`)** and **all 1,147 sparse (`<= 150k` px) public rasters across all 102 public `GEMSDOE` repositories (`0 > 70%`, max `0.6719 <= 0.70`)**.
  4. Executed full live 102-repo GitHub API public registry scan (`1,332` compatible rasters, `evidence/hydroconduit_public_registry_uniqueness.json`) on both continuous pre-placement surface and final dots, confirming the literal dense-surface duplicate stop (`118` rasters `> 150k` px led by `17GEMSDOE E-proba-multiscale`, `100%` footprint positive).

---

## Prioritized Remaining Blockers & Future Work

### Priority 0 — Human Operator / Selector Decisions (Cannot Be Resolved Autonomously)
1. **Dense-Surface Representation Policy Decision (`17GEMSDOE E-proba-multiscale`):**
   - `17GEMSDOE_E-proba-multiscale` (`5,167,373` positive footprint cells = `100%` of footprint) makes literal 3-px forward overlap equal `1.000` for **every** nonempty in-footprint raster.
   - If the human operator scopes the 3-px dot-overlap uniqueness rule to sparse dot-set candidates (`<= 150,000` positive pixels, `<= 2.9%` of footprint) while retaining `|Spearman rho| <= 0.90` on all `1,332` rasters (`max = 0.4396`), `HYDROCONDUIT f45hydro` (`c9e07ba6…`) already passes every uniqueness, format, canary, and static-holdout gate. Until that explicit human policy update, keep `submission_eligible: false`.
2. **Blocker 0 — Obtain First `ORGANIZER-CONFIRMED` Submission Receipt:**
   - `ledger/submissions.csv` now holds `49 BUILT` rows and `0 RECEIPT` rows. Recording even one organizer submission-page receipt (e.g. confirming `R0 = 0.2778` or testing one selector-cleared candidate) is the only way to calibrate whether DrivenData's hidden test set aligns closer to Quaternary piedmont/geothermal recovery (`HYDROCONDUIT`) or exposed bedrock mapping (`BREAKLINE` / `SGMC`).

### Priority 1 — External Data Acquisition (Blocked by Sandbox Network Policy)
3. **1 m USGS 3DEP LiDAR Micro-Scarp + Lake Lahontan Shoreline Mask (Hypothesis #5 in `HYPOTHESES_20261024_HYDROCONDUIT.md`):**
   - In an environment with outbound access to `apps.nationalmap.gov` / DrivenData's `1m_DEM_links.csv` and orthometric (AMSL) elevation tiles, extract sub-meter alluvial scarp doublets and mask Pleistocene Lake Lahontan highstand (~1330–1338 m AMSL) and recessional beach ridges (which cannot be isolated from detrended `Band 12` alone).

### Priority 2 — Methodological Next Steps (In-Stack, No External Access Needed)
4. **Resolve the Static vs Fold-Visible (`d_visible > 2.0`) Holdout Gap:**
   - Our new `fold_visible_rule2` diagnostic (`scripts/report_hydroconduit_proxies.py`) showed `100% H19-5` (`d_visible > 2.0`) reaches `0.0968` vs `0.0852` when `45%` of dots are forced `> 300 m` off `H19-5`. Test whether **2D Coulomb transtensional slip + dilation tendency** (`Bands 4, 7, 8` projected onto joint `Band 12 + Band 2 RTP` fault normals, Hypothesis #4) or **blind geothermometer strike bridges across MT clay-cap lateral gradients** (`||\nabla \text{Band 17}||`, Hypothesis #3) lifts **both** fold-visible `d_visible > 2.0` `HOLDOUT-DTI` **and** `SGMC` `PROXY` simultaneously.

### Parallel-Session Benchmark Update (`PIEDFRONT` + `STEPEDGE` + `review_20261024`)
- **`PIEDFRONT f35Ptop`** (`GEMSDOE92-PIEDFRONT-f35Ptop-20261024`, `docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif`, SHA-256 `e314f4c004927ff56334827b4d45c57fc62da3da3010c12682d7cce6d0f185a8`): static `HOLDOUT-DTI = 0.006425 [0.005375, 0.007479]`, `SGMC = 0.059993`, `verdict: negative` (**OK TO DOWNLOAD**, **DO NOT SUBMIT**). `HYDROCONDUIT f45hydro` (`0.008549 [0.007626, 0.009487]`) improves over `PIEDFRONT f35Ptop` by `+33.1%` (`+0.002124`) while overlapping only `56.56% <= 70%` within 3 px (`phi = 0.2000`).
- **`STEPEDGE f60Sraw`** (`GEMSDOE92-STEPEDGE-f60Sraw-20261024`, `docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`, SHA-256 `c5dc98f2846ae486e022a7bdae1840334e73c03af44c03e9867c03b6f16d07b4`): static `HOLDOUT-DTI = 0.003980 [0.003295, 0.004702]`, repo-best `SGMC = 0.141464`, `verdict: negative` (`42.35% <= 70%` 3-px overlap with `HYDROCONDUIT f45hydro`).
- Ledger total across all merged sessions: `54 BUILT / 0 RECEIPT`.
