# Three-Pass Verification & Protocol Audit — `2026-10-29` (`DEXP-KOSTROV-KOENDERINK`, Branch `arena/2066b1fc-gemsdoe92`)

## Pass 1 — End-to-End Implementation & Execution Audit
1. **Previous Next Steps & Repo Forensics Completed First:**
   - Restored all `19` SHA-pinned core + external input rasters into ignored `.cache/gems_inputs/`.
   - Rebuilt live `2026-10-29` 8-owner public registry cache (`.cache/registry_v3/inventory.json`: `108` non-empty repos across `8` GitHub owners, `3,421` grid files, `2,262` unique SHA-256 rasters = `2,139` dot fields + `123` continuous surfaces, `0` errors) and `.cache/registry_v3/halo_stats.json`.
   - Transcribed `ledger/claims_20261029.txt` (`137` claims, `132` matched across `88` groups) and `ledger/unscored_20261029.txt`, audited prospective out-of-time (`OOT`) `LBM-v1`/`LBM-v2` performance on the 4 newly scored `2026-10-29` submissions (`Spearman = 1.000`, 3-independent-repo `RMSE = 0.01828`), and resolved the `ApartGEMSDOE1` `16f7101f41dd` label collision (`IR-1029-2`).
   - Resolved `IR-1029-1` (`<<<<<<< HEAD` merge conflict markers in `docs/how-to-submit.html`) at the root in `scripts/render_safe_review.py`.
2. **Pre-Registration & Novel Lane Execution (`H1-DEXP-KOSTROV-KOENDERINK`):**
   - Frozen in `docs/HYPOTHESES_20261029_DEXP_KOSTROV.md` (`0` prior code matches across `gems/`).
   - Implemented in `gems/dexp_kostrov.py` & executed in `scripts/run_dexp_kostrov_20261029.py` (`3/3` experiments `E1, E2, E3` within budget, `0` weekly slots spent).

## Pass 2 — Bug, Assumption, Leakage & Edge-Case Review (Caught & Fixed)
1. **Caught & Fixed `IR-1029-3` (`123` Surface Rasters Omitted in Prior Uniqueness Calls):**
   - Prior builders (`place_riesz_lbmv2.py`, `build_exp1_submission.py`) passed `shas = sorted(halo_stats)` (`2,139` dot fields), omitting `123` continuous/dense surface rasters. `scripts/run_dexp_kostrov_20261029.py` passes all `2,262` unique inventory SHAs on **both** pre-placement `our_surface` (`0.65405 <= 0.70`) and `final_dots` (`0.63890 <= 0.70`).
2. **Caught & Prevented `IR-1029-5` (`H19-5` Holdout Leakage Trap):**
   - Verified `calib_h195_01922.tif` (`121,131` pixels) has `0` pixels on `existing_faults.tif`; repelling against `H19-5` or historical `d_cat > 2` rasters inside `gems57` holdout folds would leak withheld fault segments. `E3` uses strictly zero-catalogue DEM mid-scarp suppression + fold-visible `r0_recipe(vis)` / `e1_blind(vis)` halo caps (`0` bits of withheld truth).
3. **Caught & Fixed Correlated-Sibling Compounding Penalty + Strict `d_cat > 3.0 px` Collar:**
   - Replaced multiplicative product across 25 sibling `VARIO`/`FAULTNET` clones (`0.7^25`) with a non-compounding `np.minimum` max-violation dual update (`target_cap = 0.655`), and enforced `d_cat > 3.01 px` (`>= 3.162 px > 3.0 px`) so Gate #10 (`distance_from_catalogue: strict distance > radius required`) passes with `0` violations (`11/11` gates PASS).
4. **Caught & Fixed `3.8 GiB` / `0 Swap` Sandbox Peak RSS:**
   - Freed active halo dictionaries immediately after dot placement in `scripts/run_dexp_kostrov_20261029.py`, keeping peak RSS comfortably within `3.8 GiB`.

## Pass 3 — Full Re-Check Against User Prompt, Safety Invariants & Deliverables
- **Unique `.tif` + One-Click Top Download + Unmistakable Gate Badge:** `docs/downloads/gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17-zeros.tif` (`SHA-256 80d66b0590b26ddc9ac56af3964289f63f9c07c80931e3e69a7089dbabbc6faf`) linked at top of `docs/index.html`, `docs/executive-summary-20261029-dexp-kostrov.html`, `docs/how-to-submit.html`, `docs/executive-summary.html`, `docs/nine-sites.html`, and `index.html`, clearly badged `OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT` (`0` occurrences of `OK TO SUBMIT` across live pages).
- **Evidence-Class Discipline:** Every number is explicitly tagged `HOLDOUT-DTI`, `CLAIM`, `MODEL`, or `ORGANIZER-CONFIRMED` (`0` stored organizer receipts).
- **Remaining Work & Limitations:**
  1. Human policy owner must decide whether dense continuous surfaces (`17GEMSDOE E-proba-multiscale`, `5,167,373` positive cells) and ultra-dense lattices (`13GEMSDOE`, `206,895` dots) are evaluated under PI-1 top-N (`PASS` at `0.6389 <= 0.70`) or literal positive support (`1.000 > 0.70`), and verify official redistribution provenance before spending one of the `3/week` DrivenData portal slots.
  2. Outbound sandbox firewall permits only GitHub/PyPI/npm, so `drivendata.org`, USGS 3DEP 1 m LiDAR (`H4`), USGS GeoDAWN raw flight lines, and DOE GDR `#1391` cannot be queried live from inside this container.
