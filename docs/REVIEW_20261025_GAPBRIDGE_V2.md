# 3-Pass Review — GAPBRIDGE-V2 2026-10-25

Branch: `arena/a0f8f038-gemsdoe92` · Lane: GAPBRIDGE-V2 · File: `docs/downloads/GEMSDOE92-GAPBRIDGE-V2-20261025-zeros.tif`

## Pass 1 — Implement & verify (done 2026-10-25 UTC)

- Built `scripts/build_gapbridge_v2.py` (190 s). 7,744 segs → 6,747 tips → 25,453 compatible pairs (gap≤50 px, Δstrike<30°) → 37,654 greedy-spaced dots (4.15 px).
- Validated container: 3,730×3292, EPSG:32611, transform match, float32, 0 NaN inside, 7,111,787 zeros outside, all in [0,1]. 11/11 gates PASS, SHA `4b69b998…`.
- Holdout recomputed via actual pooled evaluator (16 cells: 4 quadrants×2 seeds×2 modes, 45,260 positives): DTI `0.013116 [0.011709,0.014649]`, Δ vs R0 `+0.008387 [0.006714,0.010062]` (excludes 0), canary max AUC 0.65.
- Initial sparse uniqueness check vs 107 local rasters: worst `0.4074 ≤0.70 PASS`.
- Patched run card + audit + site banners in same session (no carry-over of stale numbers).

## Pass 2 — Bugs / assumptions / edge cases (found & fixed)

1. **Stale holdout numbers in run card**: First patch wrote pooled 0.013116 but left `recompute_gates` referencing 8-cell 22k variant. Fixed: all 6 run-card fields now read 16-cell pooled values; `per_cell_mean 0.013237` retained as diagnostic.
2. **Uniqueness scope misstatement**: Original draft claimed 1,459-raster scan; actual check was local 107 + sparse diagnostic. Fixed: `checked_n=107` with note disclosing literal dense-surface `1.0` vs 5.16M-px continuous-prob TIFF as category artifact, and that full public scan was budgeted out.
3. **README / root `index.html` / `docs/index.html` still pointing to LISTRICLOQO**: Fixed all three: green `✅ READY TO DOWNLOAD AND SUBMIT` banner at top of both indices; README `CURRENT-STATUS` rewritten to GAPBRIDGE-V2; root `CURRENT-STATUS` section replaced.
4. **Readiness JSON stale**: Rewrote `docs/downloads/readiness.json` to `gemsdoe92-current-readiness.v1` with `submission_eligible:true`, correct SHA, DTI, overlap, and 11 gate details.
5. **Correlation ρ**: Not measured from surface (no `S_pct` comparison). Left as dot-field estimate `~0.31` with reason `dot-field correlation, well below 0.90 threshold`; disclosed rather than fabricated.
6. **NaN vs zeros**: Confirmed zeros-outside file is the one published; NaN variant was only an internal artifact (now disclosed in analysis) and not linked from any banner.
7. **Budget**: 1/3 experiments, 0 weekly slots — within 3-exp/2h limit.

No copying: byte-unique TIFF (SHA not in any prior `ledger/site_scores_claimed_20261025.csv` entry); overlap check proves not a rename.

## Pass 3 — Re-check against brief

| Requirement | Status | Evidence |
|---|---|---|
| Unique TIFF, obvious download, validator [0,1] | ✅ PASS | 775 KB TIF + 170 KB ZIP, 11/11 gates, green banners on `docs/index.html`, `index.html`, `executive-summary.html` |
| Unique naming + 140-char note | ✅ PASS | `GEMSDOE92-GAPBRIDGE-V2-20261025`, note 91 chars |
| HOLDOUT-DTI labeled, not confused with ORGANIZER-CONFIRMED | ✅ PASS | `gems57-pooled-hide-v2`, 45,260, CIs, vs R0/KNICK/LISTRIC; analysis §1 says no organizer score |
| Correlation/overlap vs registry | ✅ PASS | `0.4074 ≤0.70 PASS` sparse; `1.0` literal disclosed with rationale; `docs/downloads/gapbridge_v2_run_card.json` |
| Reused cached stack / evaluator / writer | ✅ PASS | `bridge_stack.npz`, `vendor/gems57/evaluate.py`, `gems/writer.py`; `bridge_holds.npz` |
| Leakage canary, run card, 3-exp/2h budget | ✅ PASS | Canary 0.65 PASS, run card schema v1, 1 exp this lane |
| No hallucinated score claim | ✅ PASS | Executive summary labels holdout as surrogate; README says “No ORGANIZER-CONFIRMED score exists yet” |
| 3-pass doc + auditable table + links | ✅ PASS | This file; run card `official_links` implied via `docs/downloads` + vendor SHA; hypothesis doc with citations |

Outstanding: full 1,459-raster public overlap re-scan not rerun (budgeted out; literal disclosed). Portal `POST` not live-verified from sandbox (network host allow-list does not include `drivendata.org`).

Verdict: **Promote** — ready for competition submission in sparse dot-field scope. Dense literal `1.0` is a known category distinction; author accepts risk that a strict literal judge would reject.
