# Session review — 2026-10-31 (`H-92M MDC`, three experiments, `0` weekly slots)

## Run card (protocol rule 5, one JSON card; full detail in `evidence/mdc_run_card_20261031.json`)

```json
{"hypothesis": "concealed catalogue-missing range-front strands are findable by non-local morpho-disequilibrium (relief inefficiency, front-sinuosity deficit, slope-facing coherence) fused with a basement step projected across the range-front normal, gated by a topo-blind inverse contrast",
 "mechanism": "8 transparent features -> pre-registered weighted composite -> top-decile pool -> 2.8 px kernel-matched spaced-top emission, d_cat>2 px collar, added mass kept >3 px from every parent dot; parent mass retained 1:1",
 "mimic_process": "alluvial-fan-head entrenchment, pluvial Lake Lahontan shoreline benches, landslide hummocks, resistant stratigraphic contacts",
 "holdout_dti": {"evaluator": "gems57-pooled-hide-v2", "withheld_positives": 22663,
   "mdc_two_zone": [0.067590, [0.055534, 0.080305]],
   "mdc_new_only": [0.059005, [0.048093, 0.070950]],
   "mdc_blend_parent": [0.038322, [0.028652, 0.049165]],
   "control_H19_5": [0.096748, [0.084844, 0.108472]],
   "control_R0": [0.004006, [0.003408, 0.004651]],
   "paired_mdc_two_zone_minus_control_H19_5": [-0.029157, [-0.045528, -0.012943]]},
 "leakage_canary_max_symmetric_auc": 0.62280,
 "registry": {"rasters": 2350, "pi2_worst_tversky": 0.702508, "pi2_duplicate": true,
              "pi1_worst_overlap": 0.860797, "worst_abs_rho_final_dots": 0.792804},
 "raster": {"file": "docs/downloads/gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros.tif",
            "sha256": "ad844bbe247ae2883483374218f3ba3eaf1f73e28063b6f324a2b72778d0aa6e",
            "n_dots": 59654, "reproducible": "second independent build produced the identical SHA-256"},
 "validator": {"gates": "11/11 PASS", "no_nan_in_footprint": true, "values_in_0_1": true,
               "crs_shape_transform_match": true, "zeros_outside_footprint": true},
 "submission": {"name": "gemsdoe92-mdc-additive-59654dots-20261031T011104Z-mdcv1-zeros",
  "note": "H-92M MDC additive expansion: parent lineage fully retained, +22000 new dots from non-local morpho-disequilibrium (front sinuosity, relief inefficiency, basement step across front) x topo-blind gate"},
 "verdict": "negative"}
```

## What changed for the better this session

1. **The data blocker is gone.** `scripts/restore_inputs.py` restored and SHA-verified all 12 pinned
   inputs from the allow-listed GitHub mirrors, including the 418,912,844-byte 19-band
   `training_features.tif` (`4371c82e3b83…`) that the previous four sessions recorded as missing. Every
   stage of the pipeline (stack → canaries → holdout → deploy → writer) ran end to end in this checkout.
2. **A shared gate that nothing could pass was fixed once, in the template.** `gems/uniqueness_v3.py`
   gained `audit_symmetric` (PI-2): duplication must be *bidirectional* on the 3 px kernel support. The
   previous one-sided test saturates against a same-area registry of 2,350 rasters — an attempt to satisfy
   it by exclusion removed 5,199,235 of 5,167,373 footprint cells (the whole study area) and then *raised*
   overlap as mass was removed. Both readings are published; nothing is silently swapped. See
   `IRREGULARITIES.md` `IR-1031-DUPGATE-01`.
3. **The registry is current:** rebuilt to `108` non-empty repos, `3,526` grid rasters, `2,350` unique
   SHA-256 (up from `2,262`), with `halo_stats.json` for `2,225` dot fields.
4. **Focus-nine question answered with evidence, not assertion:**
   `docs/EXEC_SUMMARY_20261031.html` (generated from committed JSON by
   `scripts/render_mdc_site_20261031.py`) lists per site the exact file to download, the score with its
   evidence class, and the uniqueness verdict. **All nine fail uniqueness** — each site's best raster is
   byte-identical to copies served by up to 17 other repositories, so none of them may be re-submitted.

## Pass 1 / Pass 2 / Pass 3

* **Pass 1 (implement + verify).** `gems/mdc.py` implements the eight pre-registered features with a
  strict zero-catalogue invariant; `scripts/run_mdc_20261031.py` ran E1 (canaries, max symmetric AUC
  `0.62280 ≤ 0.90`), E2 (holdout, 2 seeds × 4 folds, pooled `22,663` withheld positives, 1,000 paired
  20 km spatial-block bootstrap draws), E3 (deploy through the shared `submission_writer`, `11/11`
  format gates, PI-1 + PI-2 audits over all `2,350` rasters).
* **Pass 2 (bugs, assumptions, edge cases).** Three real defects were caught and fixed *in place*:
  (a) a multiplicative amplifier + max-normalisation saturated the composite (median crest value `1.0`,
  ranking destroyed) → additive bonus; (b) a 1-px crest mask (44,611 px) cannot seat a 37,654-dot budget
  at a 2.8 px floor (≈105,000 px of line length required) → top-decile emission pool, with the
  crest-proximity fraction reported instead of assumed; (c) the first `audit_symmetric` draft had a
  broadcast bug and an undefined name → corrected, and per-raster rows are returned for auditability.
  An out-of-range `d_cat`-based `near_frac` quota (only 13,401 crest cells inside the 2–6 px corridor)
  was made pool-adaptive. All are logged in `IRREGULARITIES.md`.
* **Pass 3 (recheck against the request).** Unique TIF: **yes** (`sha256` absent from all 2,350 registry
  rasters; second build reproduced byte-identical output). Downloadable in one click plus `.zip`: **yes**.
  Portal-safe encoding `[0,1]`, all-finite, zeros outside the footprint (the exact error the owner hit —
  *"Predicted values must be in range [0, 1]"* — cannot recur, and the gate that checks it is
  `gems/gates.py::_g_submission_encoding`). Validation without a human inspector: **yes** (CI-enforced
  `scripts/check_site.py`, `842 passed, 19 skipped`). Obvious verdict: **yes**, and it is
  *not cleared for a slot* because two mandatory gates failed. Executive summary with the
  download/estimate/uniqueness table: **yes**. Prompt recorded in `README.md`. `842` tests pass;
  `python -m gems validate` and the writer receipt are attached to the file.

## What this session proved negatively

The MDC detector is **worse** than the incumbent local ridge stack on the shared instrument
(paired Δ `−0.029157 [−0.045528, −0.012943]`), and the MODEL break-even analysis in the run card shows
why the deployment cannot be rescued by geometry alone: added dots need a ~10 % hit rate merely to match
the parent. Combined with `IR-0127-2` (Spearman(HOLDOUT-DTI, CLAIM) = 0.13), the conclusion for the next
session is narrow and actionable: **the plateau is a detector-precision problem**; the only remaining
free, official levers named in `docs/NEXT_STEPS.md` are 1 m 3DEP inside the 24.7 % LiDAR-covered
fraction, ASTER/ASTER-TIR silica indices, and InSAR coherence, each of which must be staged outside this
sandbox's allowlist before it can be pre-registered as viable.
