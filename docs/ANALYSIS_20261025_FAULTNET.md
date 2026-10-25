# FAULTNET — analysis and closeout (2026-10-25)

**Verdict: `negative` (registry duplicate under protocol rule 1). 0 weekly slots used. 3/3 experiments.**
The three GeoTIFFs are format-valid and downloadable for research. **Do not submit them.** No ORGANIZER-CONFIRMED
score exists for any file in this repository.

Machine-readable sources (every number below is copied from these files, not retyped by hand):
[run card](downloads/faultnet_run_card.json) · [holdout](downloads/faultnet_holdout.json) ·
[uniqueness](downloads/faultnet_uniqueness.json) · [gate calibration](../evidence/faultnet_gate_calibration.json) ·
[pre-registration](HYPOTHESES_20261025_FAULTNET.md) · code: [`gems/faultnet.py`](../gems/faultnet.py),
[`scripts/run_faultnet.py`](../scripts/run_faultnet.py), [`scripts/faultnet_uniqueness.py`](../scripts/faultnet_uniqueness.py),
[`scripts/finalize_faultnet.py`](../scripts/finalize_faultnet.py), [`scripts/build_public_registry_index.py`](../scripts/build_public_registry_index.py).

## 1. Why `h33-h33-2-b2` got 0.2778, and can we beat it?

The 0.2778 is **USER-REPORTED**: it comes from the brief, and no receipt exists in `ledger/`. The pinned R0 raster
(`data/parent_R0_zeros.tif`, SHA-256 `c55bafc4…`) has 37,654 unit dots, 0 on the catalogue, and a median of 19.6 px
from the nearest mapped fault (measured this session). Its lineage keeps the *same detector* (H19-5 ridges) and
changes only the *emission*:

1. **Solid lines → 2.8 px dots** (0.1922 → 0.2600). With a 3 px triangular kernel, credit `T` saturates for each truth
   pixel, but every predicted pixel costs `α = 0.2` in `FP`. Spacing removes redundant cost.
2. **Removing dots ≤ 1 px and then ≤ 2 px from the catalogue** (0.2600 → 0.2708 → 0.2778). Known faults are masked
   from scoring, so dots that hug a mapped trace earn almost nothing.
3. In metric terms, `1/DTI = 0.2 + (0.2·FP + 0.8·|G|)/T`. If the 2,545 dots removed in the last step had zero yield,
   the finite difference implies `T ≈ 5.5k` and `|G| ≈ 15k` truth pixels, i.e. roughly 35% recall. This is a
   **projection**, not a score. The bar for adding one more non-redundant dot is `k > α·DTI ≈ 0.056`.

**Conclusion.** R0 is an emission optimum on a fixed, comparatively weak detector. The remaining headroom is in the
**ranking of candidate locations**: which ridges get the 37,654 dots. A better detector under the same emission rules
is the most promising route above 0.2778. That cannot be shown locally; only an organizer receipt can show it.

## 2. Hypotheses considered (ranked; full table in the pre-registration)

1. **FAULTNET** (built). Catalogue-network context: unmapped splays, antithetic faults and relay faults cluster near
   mapped masters and share their strike. No LOQO lane in this repository had used the catalogue's own spatial
   arrangement as a feature.
2. STRIKE-STEER emission. Low cost, but emission-only, so it would sit in the same lane as R0.
3. MAG-TEXTURE OFFSET. High cost and speculative.
4. InSAR velocity steps. **Blocked**: ASF/Earthdata is outside the sandbox allow-list.
5. 3DEP 1 m scarp curvature. **Blocked**: USGS is outside the allow-list.

## 3. Method (FAULTNET)

The lane adds five context fields to the 24-feature COULOMBLOQO physics stack. Each field is computed **only from the
visible catalogue** and **excludes the pixel's own 8-connected component**, so a training positive never sees its own
trace (feature ≠ label). Exactness against brute-force deletion is tested in `tests/test_faultnet.py`. The fields:
self-excluded distance to the nearest other fault, fault density at σ = 1 km and σ = 4 km, distance to other faults'
tips, and regional-strike × topographic-edge alignment.

Everything else is unchanged shared tooling: the same LOQO (HistGradientBoosting, 12 px guard, negatives > 5 px, 4:1),
the same crest surface and `directional_ridge_1d` gate, and 37,654 dots at a 2.8 px floor.

## 4. Results — HOLDOUT-DTI

Instrument: `gems57-pooled-hide-v2`, strict draw-blind fold-visible. Settings: `buffered_component_draw` seeds 20 and 30;
22,663 withheld positives; every model refit from visible faults with the hidden components plus a 3 px collar excluded;
context fields rebuilt from visible faults; visible faults masked pixel-exactly; 95% CI from a 1,000-draw paired
20 km cluster bootstrap.

| arm / control | emission | HOLDOUT-DTI | 95% CI |
|---|---|---:|---|
| **netfar** | d_vis > 4 | **0.175147** | [0.159756, 0.189860] |
| netdens | d_vis > 2 | 0.148814 | [0.134255, 0.163959] |
| netctx | d_vis > 2 | 0.148707 | [0.133888, 0.162834] |
| control_COULOMBLOQO_far (emission-matched for netfar) | d_vis > 4 | 0.115584 | [0.102506, 0.130237] |
| control_COULOMBLOQO (previous holdout best, rebuilt) | d_vis > 2 | 0.113890 | [0.100783, 0.128559] |
| control_H19_5 (R0 lineage detector) | d_vis > 2 | 0.096757 | [0.084839, 0.108454] |

Paired differences (HOLDOUT-DTI, same folds):

- netctx − COULOMBLOQO: **+0.034817 [0.022056, 0.047535]**. Same emission, so this is the context-feature effect.
- netfar − COULOMBLOQO_far: **+0.059564 [0.046653, 0.073109]**. Emission-matched, so the gain is not just the halo rule.
- netfar − H19-5: **+0.078390 [0.064571, 0.092113]**. Measured against the detector behind the 0.2778 parent.
- netfar beats the control in **8/8** seed × quadrant folds. netctx beats it in 7/8 (it loses in seed-30 NE).

**Reproducibility.** The rebuilt controls reproduce earlier sessions exactly: COULOMBLOQO 0.113890 and H19-5 0.096757,
both identical to the PROVINCETOE-session values.

**Leakage canary.** All 58 single-feature tests (29 features × 2 draws) pass. The maximum symmetric AUC is **0.77748**
(`cx_logtip`), below the 0.90 limit.

## 5. Uniqueness — REGISTRY-MEASUREMENT (why the verdict is negative)

The registry has **1,451** Git-blob-verified single-band rasters on the competition grid, from 102 public
`buffedlizard55-lab/*GEMSDOE*` repositories (1,461 unique blobs; 10 skipped and listed). Local lineage rasters are
deduplicated into it by SHA-256.

| arm | worst final-dot overlap (limit 0.70) | vs | worst \|ρ\| final / surface (limit 0.90) | rasters > 0.70 (dot overlap) |
|---|---:|---|---|---:|
| netfar | **0.758591** | GEMSDOE37 `h6-physics-dotted-80k` (80,000 dots) | 0.1329 / 0.7851 | 5 (4 distinct, all 56k–103k-dot fields) |
| netctx | 0.838583 | GEMSDOE86 `gmc-linepost` (90,568 dots) | 0.1739 / 0.7851 | 18 |
| netdens | 0.840309 | 12GEMSDOE `r7-nms3-dem10-scarp` (103,347 dots) | 0.2512 / 0.7649 | 13 |

The rank-correlation clause passes for every arm, but the dot-overlap clause fails. netfar is below 0.70 against every
raster with ≤ 1.25× its dot budget (worst **0.635258** over 1,265 rasters). It fails only against larger dot fields.

**Is the gate fair?** We calibrated it with controls rather than asking for a waiver
([gate calibration](../evidence/faultnet_gate_calibration.json)):

- R0 itself is flagged as a duplicate (positive control).
- A uniform-random 37,654-dot raster passes, with a worst overlap of 0.4926.
- A **ridge-gated random** 37,654-dot raster also passes. It uses the same crest pixels, the same d_cat > 4 rule and the
  same 2.8 px floor, and its worst overlap is **0.4949**.

So the gate **is specific**. FAULTNET's dots really do sit on the same strong lineaments that three or four earlier,
heavily dotted lanes already covered. By rule 1 this is lane drift, so we log it as a duplicate and stop. We do **not**
recommend waiving the over-budget comparison.

**Dot definition for continuous surfaces** (`#IR-92-FAULTNET-DOT-DEFINITION`, owner decision flagged for review). Read
literally, a full-footprint surface (44 such rasters in the registry) makes every raster a duplicate. A random raster
fails 69 of them under that reading, so the reading cannot detect drift. FAULTNET instead compares against a continuous
surface's matched-budget top-n plus the ρ clause, and still publishes the literal count (netfar: 97). This decision did
**not** affect the verdict: netfar fails on dot fields.

## 6. Interpretation and caveats

- The holdout truth is **withheld catalogue faults**, and those are clustered by construction. The organizer truth is
  *unmapped* faults, which may cluster less around mapped ones. FAULTNET's +54% relative gain is therefore an upper
  bound on what to expect, not a projection of a leaderboard score.
- **Named non-fault mimic:** lithological contacts and range-front geomorphology parallel to mapped faults.
- The emission-matched control was added **after** the first holdout read-out, to separate the context effect from the
  halo effect. It made the promotion rule stricter and changed no arm. It is recorded as such in IRREGULARITIES.md.
- Adding the extra control re-ran the paired bootstrap on the same seed and shifted the third decimal of some CIs,
  e.g. COULOMBLOQO [0.100124, 0.127440] → [0.100783, 0.128559]. The run card holds the final values.

## 7. Run card (protocol rule 5)

See [`downloads/faultnet_run_card.json`](downloads/faultnet_run_card.json). The primary arm is netfar:
SHA-256 `ad80f9a0fdc6bc608902accfedc783c700c4fd8a98bd5d903540aa7981ba8949`, name
`gemsdoe92-faultnet-netfar-20261025-3c4e9051`, note `FAULTNET netfar: netctx surface, dots >4px off catalogue; 37654 dots 2.8px`
(75 characters), verdict `negative`, `ok_to_submit: false`.

## 8. Next steps (in order)

1. **FAULTNET-Δ (new pre-registered lane, one arm).** Emit only the locations where the context fields change the
   ranking: dots ranked by `P(netctx) − P(COULOMBLOQO)` inside the crest gate, d > 4 px. These are the dots that embody
   the hypothesis, and they are the ones least likely to coincide with physics-only dotted lanes. Pre-place the
   uniqueness screen on the surface first (rule 1), then evaluate on the same folds against netfar and both controls.
2. **Organizer calibration.** Upload one already cleared file (none is cleared today) and record the receipt. The
   repository still has **0** ORGANIZER-CONFIRMED receipts, so the holdout-to-leaderboard mapping is uncalibrated.
3. Keep `.cache/registry_index` current with `scripts/build_public_registry_index.py` (about 6 minutes, about 1,500
   GitHub API calls) before any uniqueness decision.
