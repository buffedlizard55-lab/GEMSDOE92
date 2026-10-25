# Three-Pass Audit & Verification Log — `CHILISTRIC` Session (`2026-10-25`)

- **Branch**: `arena/2d4c152c-gemsdoe92`
- **Active Lane**: `CHILISTRIC` (`docs/HYPOTHESES_20261025_CHILISTRIC.md`, `gems/chilistric.py`, `scripts/run_chilistric.py`)
- **Primary Deliverable**: `docs/downloads/h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif` (`SHA-256 = 75fcc743420f817d841b9f822e82bf4e63c850ede29e0e2d75e54b26603acf50`)
- **Run Card**: `evidence/chilistric_run_card.json` (byte-identical mirror: `docs/downloads/chilistric_run_card.json`)

---

## Pass 1 — End-to-End Implementation, Primary-Source Forensics & Execution

1. **Primary-Source & Pixel-Exact Forensics**:
   - Verified `R0` (`data/parent_R0_zeros.tif`, `c55bafc4...`, `37,654` px) and its full ancestor chain (`H19-5` `ec1f9b56...` `121,131` px -> `D1.5` `68d0e2e4...` `60,069` px -> `D2.8` `91eae1ca...` `44,090` px -> `SOLO == D2.8 & (d_cat > 1.0)` `2fc94a38...` `40,199` px -> `R0 == D2.8 & (d_cat > 2.0)` `37,654` px, `0` XOR difference).
   - Audited `19GEMSDOE/src/gems/hypotheses.py`, `GEMSDOE32`, `GEMSDOE36` (`0.2750 [CLAIM]`), `GEMSDOE70`, and `drivendataorg/gems-prize-reference-solution` (`vendor/gems57/metric.py`, $\alpha = 0.2, \beta = 0.8, R = 300\text{ m}$).
2. **Pre-Registration & Zero-Catalogue Implementation**:
   - Pre-registered 5 ranked geological hypotheses and 3 budgeted experimental arms (`adapt37k`, `addtail52k`, `no10m_fixed`) in `docs/HYPOTHESES_20261025_CHILISTRIC.md` before model fitting.
   - Implemented `gems/chilistric.py` (`44` zero-catalogue features, disk-backed `open_memmap` 3-phase stack builder for `3.8 GiB` RAM safety) and `scripts/run_chilistric.py` reusing `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, `22,663` withheld positives) and `vendor/gems57/submission_writer.py`.
3. **Execution & Validation**:
   - Verified all `44/44` single-feature leakage canaries pass (`max symmetric AUC = 0.617275 <= 0.90`).
   - Generated all 3 unique GeoTIFFs (`82694176`, `8c82904d`, `48950a5f`), `.zip` packages, and `-audit.json` sidecars (`11/11` format gates PASS), scanned uniqueness across `102` local rasters and `1,503` public rasters across `102` `GEMSDOE` repos (`0 / 1,503 > 0.70` operationally for `addtail52k` at `0.635115 <= 0.70`), and wrote `evidence/chilistric_run_card.json`.

---

## Pass 2 — Critical Bug, Assumption, Hallucination & Edge-Case Review (Caught & Fixed)

During Pass 2, we audited both prior repository artifacts and our own Pass 1 code/prose line-by-line against live disk bytes:

1. **Code Bugs Caught & Fixed During Development / Pass 2**:
   - **`fit_single_loqo` `excluded_mask` Trap**: Passing `excluded_mask=label_mask` excluded positive training pixels (`train_dom &= ~excluded_mask`); fixed in `gems/chilistric.py` by passing `excluded_mask=None`.
   - **`uniqueness.py` Constant & Surface Top-$N$ Clumping**: Fixed `U.DOT_FIELD_MAX_SUPPORT` (`150,000`) import and separated continuous-surface Spearman (`|ρ| <= 0.90`) from spaced-dot 3-px overlap (`<= 0.70`) while keeping literal `17GEMSDOE` (`1.0000 > 0.70`) fail-closed (`verdict = "negative"`, `submission_eligible = false`).
   - **Step 4 Indentation Bug in `scripts/run_chilistric.py`**: Fixed `else:` alignment on cached `holdout_terms_cache.json` reload so full script re-runs cleanly (`exit 0`).
   - **Dual Run-Card Schema Compatibility**: Added `note`, `primary_download`, `experiments_used`, and `weekly_slots_used` aliases alongside `submission_note`, `candidate_file`, `experiments_run`, and `weekly_slots_spent` in `chilistric_run_card.json` and pinned byte equality between `evidence/` and `docs/downloads/` in `tests/test_chilistric.py`.
2. **Prior-Session Repository Irregularities Caught & Fixed (`IRREGULARITIES.md`)**:
   - **`docs/ANALYSIS_20261025_LISTRICLOQO.md`**: Caught and fixed **eight fabricated SHA-256 digests** (`512c082f...`, `7b31a559...`, `32248d1e...`, `c50de8f8...`, `901fc6cc...`, `0827be0e...`, `bd74dfef...`, `ba42db87...`) and **three wrong band numbers** (`Band 2` for `det_elev_slope`, `B11 - 0.5*B09 - 0.5*B10` for `f36`, `Bands 16–19` for magnetics).
   - **`docs/ANALYSIS_20261025_VENTSCARP.md`**: Caught and fixed hallucinated `labels.tif` pixel counts (`191,829 -> 60,988`; `d_cat <= 2.0`: `904,132 -> 304,548`), total grid pixel count (`12,279,200 -> 12,279,160`), and the false `cc_min = 3` speckle-pruning claim for `SOLO` (`XOR(SOLO, D2.8 & (d_cat > 1.0)) == 0`).
   - **`gems/ventscarp.py`**: Documented Band 3 (`tmi_hg` read as `"heatflow"`) and Band 18 (`iso_grav_anom_hg` re-differentiated as `iso_grav_anom`) misreads in `IRREGULARITIES.md` and verified `gems/chilistric.py` binds strictly to verified GDAL band descriptions.
3. **Self-Audit Corrections Caught on Our Own Pass 1 Prose**:
   - Verified `make manifest` checks `data/bridge/{h19_5,d28,h27_4_solo}.tif` (`ec1f9b56...`, `91eae1ca...`, `ab023001...`) and refined our `IRREGULARITIES.md` entry so it accurately attributes the error in `ANALYSIS_20261025_LISTRICLOQO.md` to the eight fabricated SHA-256s rather than the `data/bridge/` paths.
   - Re-checked live `rasterio` metadata and `evidence/chilistric_holdout.json` (`vent_audit` + `leakage_canaries`), updating `docs/ANALYSIS_20261025_CHILISTRIC.md`, `docs/NEXT_STEPS.md`, and `docs/downloads/current_submission.json` to match exact disk counts (`topo_10m_derived_100m_u8.tif`: `9` bands; `dem10_chi_100m_i16.tif`: `5` bands; `geodawn_extensions_u8.tif`: `4` bands; `paleo_geothermal`: `709` rows / `281` in footprint / `195` kept / `86` Tufa excluded; `2m_probe`: `3,800` valid / `2,782` in footprint / `709` anomalous; `gdr_wellspring`: `27,092` rows / `4,798` thermal in footprint; exact `f37..f44` names and canary AUCs; $s_{\text{adapt}} \in [1.80, 6.20]\text{ px}$).

---

## Pass 3 — Full Re-Check Against Original Prompt & Final Polish

Verified every item of the user's request and the Parallel-Run Protocol:
- PhD-level explanation of `GEMSDOE32` `0.2778 [CLAIM]` and `0.3195` / `0.4413` gap with zero unverified projections (`docs/ANALYSIS_20261025_CHILISTRIC.md` §1).
- Previous-session next steps executed first (`docs/ANALYSIS_20261025_CHILISTRIC.md` §2.1, `docs/NEXT_STEPS.md`).
- 5 ranked geological hypotheses pre-registered with layers, transforms, missing-fault physics, named non-fault mimics, expected gains, costs, and official sources (`docs/HYPOTHESES_20261025_CHILISTRIC.md`).
- Unique `.tif` submission generated (`h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif`), validated automatically in `[0, 1]` with `0` NaNs and matching `EPSG:32611` `3730 × 3292` grid (`11/11` CLI gates PASS).
- Top-of-site & executive-summary banners (`docs/index.html`, `docs/executive-summary.html`, `docs/SUBMIT.html`, `README.md`) make `OK TO DOWNLOAD` vs `DO NOT SUBMIT` unmistakable and give step-by-step DrivenData #306 submission instructions.
- Auditable verified-knowledge table with official links, SHA-256 pins, and explicit sandbox access limitations stored in `docs/ANALYSIS_20261025_CHILISTRIC.md` §3–4 and rendered into the top collapsible summary.
- Persisted session prompt preserved in `README.md` and `SESSION_PROMPT.md`.
- Complete JSON Run Card emitted at `evidence/chilistric_run_card.json` and `docs/downloads/chilistric_run_card.json`.
