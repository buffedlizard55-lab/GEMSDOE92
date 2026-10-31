# Three-Pass Verification — 2026-10-31 session (arena/702071e4-gemsdoe92)

Scope: the two new rasters and every claim published on
[executive-summary-20261031.html](executive-summary-20261031.html), the generated site banner
(rendered by `scripts/render_safe_review.py`), and the two run cards
([vgfp_run_card_20261031.json](../evidence/vgfp_run_card_20261031.json),
[gset2_run_card_20261031.json](../evidence/gset2_run_card_20261031.json)).
Verification is automated in-project (`.venv/bin/python` scripts below); no human pixel inspection.

## Pass 1 — Byte identities and gate receipts (no claims)
- `gemsdoe92-vgfp2r-37654dots-20261031-bcb3d2af-zeros.tif` SHA-256
  `6cd09733ab350469d32a714bd22d4eed63cb562e9364ba8ad049827da65d0a78` verified identical across:
  file bytes, companion `-zeros.json`, `-zeros-audit.json`, `evidence/vgfp_run_card_20261031.json`,
  and both site banners. ✔
- `gemsdoe92-gset2-30126dots-20261031-1c4879c4-zeros.tif` SHA-256 verified against
  `evidence/gset2_run_card_20261031.json`. ✔
- Validator receipts: 11/11 gates PASS both files (single-band float32, EPSG:32611, 3730×3292,
  transform `(100, 0, 243350, 0, -100, 4508550)`, nodata None, all values in [0, 1], 0 NaN anywhere,
  0.0 outside the 5,167,373-cell footprint, 0 dot mass on the 60,988-cell catalogue).
- `scripts/check_site.py` → **SITE CHECK PASS (134 served rasters gated)** after regeneration via
  `scripts/render_site_v3.py` (generated pages byte-consistent).

## Pass 2 — Claim-to-evidence fidelity (every published number traced)
| Published claim (exec summary / banners) | Evidence | Exact value | Status |
|---|---|---|---|
| HOLDOUT-DTI vgfp_2regime 0.0437 [0.0284, 0.0576] | run card `holdout_dti.arm.vgfp_2regime` | 0.043725 [0.028442, 0.057578] | ✔ |
| R0-recipe control 0.0967 [0.0851, 0.1081] | run card `holdout_dti.arm.ctrl_h19_5` | 0.096717 [0.085089, 0.108126] | ✔ |
| paired Δ −0.053 [−0.069, −0.038] | run card `paired_delta_vs_ctrl_h19_5` | −0.052992 [−0.069326, −0.037833] | ✔ (unicode minus in prose) |
| MODEL-CLASS PROJECTION 0.15–0.27 (point 0.21) | run card `model_projection.band/point` | [0.15, 0.27], 0.21 | ✔ labelled, never a score |
| worst 3-px overlap 0.3089 (≤ 0.70) | run card `uniqueness.worst_overlap` | 0.308918 vs netexpand_far-47bacc15 | ✔ |
| worst \|ρ\| 0.0169 (≤ 0.90) | run card `uniqueness.worst_abs_spearman` | 0.016857 vs h19_5 | ✔ |
| canary max 0.75441 ≤ 0.90 (30/30) | run card `leakage_canaries` | 0.75441 | ✔ |
| GSET2 pre-prune 0.98–1.00 vs H19-5-corridor members; lbmc1 0.365 | gset2 card `prereq_overlaps` | 0.979976–0.999814 corridor; 0.365326 lbmc1 | ✔ (disclosed both) |
| GSET2 post-prune 0.7987 > 0.70 → duplicate | gset2 card `uniqueness.worst_overlap` | 0.798745 vs GEMSDOE28 rung30 | ✔ |
| focus-9 pairwise 0.87–1.00 mutual overlap | `evidence/full_registry_summary_20261028.json` `nine_site_pairwise_overlap` | 0.857–1.000 | ✔ |
| CLAIM scores 0.2778/0.2784/… | `evidence/claims_matched_20261028.json` (OWNER-REPORT class) | as tabled | ✔ labelled CLAIM |
| leaderboard #1 0.4544, #20 0.3417 (fetched 2026-10-31) | DrivenData leaderboard page, session log | — | ✔ labelled "live leaderboard (fetched)" |

## Pass 3 — Link and copy audit (manual-review links)
- All 31 local links on `executive-summary-20261031.html` resolve to existing files. ✔
- `docs/index.html` (generated) links both new rasters and the executive summary; required tokens
  ("How to submit", "user-reported", "HOLDOUT-DTI", "Download") present; unique element ids. ✔
- `docs/how-to-submit.html` (generated) keeps "BLINDCORRIDOR" + "DO NOT SUBMIT", contains
  "Predicted values must be in range [0, 1]", and contains no "OK TO SUBMIT" literal. ✔
- Official links (DrivenData competition pages, reference solution, USGS GeoDawn DOI 10.5066/P93LGLVQ,
  GDR #1391, 3DEP, EPSG 32611) copied from the repo's official-source list
  (`scripts/render_site_v3.py OFFICIAL`) and the pinned external-stack manifest.
  Network re-fetch is impossible from this sandbox; links are for human review. ⚠ (see IR-20261031-6)
- Portal note shown to the user is 123/140 characters. ✔

## Irregularities flagged this session (detail in [../IRREGULARITIES.md](../IRREGULARITIES.md))
1. **IR-20261031-1** — the standing prompt's parallel-run protocol references "the single method
   paragraph below"; no such paragraph exists in the prompt. The V-GFP lane paragraph was stated
   explicitly in `scripts/run_vgfp_20261031.py` to close the gap.
2. **IR-20261031-2** — the prompt's leaderboard snapshot (0.4413 / 0.3195) is stale; the live
   leaderboard fetched 2026-10-31 reads #1 = 0.4544 (DW-Tversky), #20 = 0.3417. Re-anchored.
3. **IR-20261031-3** — the literal dense-witness uniqueness reading (17GEMSDOE = full-support
   witness → overlap 1.000 for any candidate) is degenerate; the operative rule is the
   parallel-run rule (dot-vs-dot ≤ 70 % 3-px, \|ρ\| ≤ 0.90), disclosed in every run card.
4. **IR-20261031-4** — external-stack mirrors are owner-repacked u8 quantisations, not
   organizer-authenticated; all bytes hash-pinned in
   [registry/external_stack_manifest_20261031.json](../registry/external_stack_manifest_20261031.json).
5. **IR-20261031-5** — no DrivenData auth in this sandbox: `numeric_features.tif`, organizer
   receipts, and full-resolution GeoDawn/3DEP archives cannot be fetched; all scores remain
   CLAIM/PROJECTION classes. Agent limitation stated on the executive summary.
6. **IR-20261031-6** — outbound network is restricted in the execution sandbox; official URLs are
   reproduced from previously fetched pages and pinned manifests for manual human review only.

## Bottom line
- **V-GFP2R** is byte-verified, portal-format-safe (0 NaN, values in [0, 1]), and PI-1 unique
  across the 158-raster local registry; its protocol verdict is **negative (exploratory)** because
  the fold-proper holdout did not beat the R0-recipe control and its projection band (0.15–0.27)
  sits below the 0.2778 family bar. Selector decides any weekly slot (cap 3/week).
- **GSET2** is a **duplicate** of the H19-5 family (0.7987 > 0.70 post-prune) — retained as a
  research deliverable; do not submit. This negative result is the session's central finding: the
  0.2778 family cannot be re-submitted uniquely at a 37k-dot budget.
