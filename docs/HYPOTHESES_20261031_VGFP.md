# Pre-Registered Hypotheses — V-GFP / score-ceiling session (2026-10-31)

**Session:** `arena/702071e4-gemsdoe92` · **Budget:** 3 experiments (all spent) ·
**Evidence discipline:** every number is HOLDOUT-DTI / REGISTRY-MEASUREMENT / CLAIM / MODEL-CLASS
PROJECTION. A projection is never a score. No organizer receipts exist in this repository.

**Context measured this session (2026-10-31):** live leaderboard #1 = **0.4544** (xiaofanhu, 35
submissions, DW-Tversky); #20 = 0.3417. Fleet CLAIM best = GEMSDOE92 lbmc1 **0.2784**; Focus-9 best
= GEMSDOE32 h33-2-b2 **0.2778**. Experiment 3 proved the H19-5-thinning family is *closed* under the
≤70 % / 3-px uniqueness rule (pre-prune overlap 0.98–1.00 vs every member; post-prune 0.80 →
duplicate verdict). So any path to ≥0.32 must add **new information**, not re-derive family support.

---

## Ranked hypotheses (expected DTI gain / implementation cost)

### H1 — Full-stack supervised segmentation (U-Net / multi-scale GBDT) on `numeric_features.tif`
- **Layers:** the competition's 19-band numeric feature stack (elevation + derivatives, magnetics,
  radiometrics — the same GeoDawn source family quantised in our mirror).
- **Signature:** learned multi-channel fault appearance (ridge/curvature + potential-field edge
  conjunctions), trained with the official Tversky loss (α=0.2, β=0.8) exactly as the
  [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
  (`unet-mc-cv-reference-solution.ipynb`, Prof. John Lipor, PSU).
- **Why it catches off-catalogue faults:** the labels are the mapped catalogue; the hidden truth is
  the same fault population at 100 m — a supervised model generalises to unmapped strands in the
  distal regime the family only samples blindly.
- **How it differs from this repo:** nothing here can train it — the stack requires DrivenData auth
  (`data/numeric_features.tif`) or the free dropbox mirror `gems-geodawn-numerical-features.tif`
  from the session prompt links.
- **Named non-fault mimic:** canyon rims, Lake Lahontan shorelines, lithologic contacts (addressed
  by the Tversky loss + augmentation; audited via feature ablation).
- **Expected gain:** +0.05…+0.12 DTI over the 0.278 plateau (the 0.35–0.45 leaderboard band).
- **Cost:** GPU training days; CPU infeasible for U-Net, feasible for a patch-GBDT.
- **Status: VIABLE-BLOCKED** — obtain `numeric_features.tif` (free, login-gated; dropbox mirror
  linked in the prompt). This is the single highest-value unblock in the project.

### H2 — Full-resolution GeoDawn (float grids) ridge–radiometric concordance
- **Layers:** ScienceBase DOI [10.5066/P93LGLVQ](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
  `22103_area*_tiffs.zip` (TMI, RTP, K, Th, U, TC, ThK, UK, UTh — float32, 50–100 m).
- **Signature:** DEXP/tilt-edge of RTP on the *unquantised* grids crossed with K/Th/U ratio
  anomalies (hydrothermal alteration halos around upflow).
- **Why off-catalogue:** our u8 mirror saturates the dynamic range that separates shallow volcanic
  edges (N≥1) from deep basement steps (N≈0); float grids restore that discriminant.
- **Difference:** all prior attempts (incl. this session's V-GFP) consumed u8-quantised channels.
- **Mimic:** Tertiary ash-flow tuff edges (depth-scaling gate via DEXP exponent).
- **Expected gain:** +0.02…+0.05; **Cost:** medium (290 MB archives, offline processing).
- **Status: VIABLE-NOW** — archives are free and public; only the mirror u8s are in-repo.

### H3 — 1-m LiDAR vent-fissure-ridge detector (sinter-valve concordance)
- **Layers:** 3DEP 1-m bare-earth (already derived into 12 quantised channels; full processing
  needs the DEM links CSV), GDR #1391 sinter/2 m-probe/enthalpy disequilibrium points.
- **Signature:** paired 6 m LoG crest–toe dipoles (Wallace scarp model) on strike-locked fissure
  ridges — silica-cemented hydrothermal fissure ridges are the surface expression of upflow valves.
- **Why off-catalogue:** sub-meter scarplets and sinter ridges are below 1:250 k compilation scale
  (the catalogue's map scale, measured in `gdr_qfaults_traces.csv`).
- **Difference:** LIDAR-SINTERVALVE (2026-10-29) held HOLDOUT-DTI 0.1786 but was never promoted;
  this variant drops the sinter-union emission that failed its paired CI.
- **Mimic:** Lahontan beach ridges (vetoed via cross-slope + elevation band), stream banks
  (cross-gradient veto).
- **Expected gain:** +0.01…+0.03 over lbmc1 if promoted; **Cost:** high (DEM ingestion).
- **Status: VIABLE-PARTIAL** — quantised channels present; full DEM via `1m_DEM_links.csv` (login).

### H4 — GSET2 divergence-pruned consensus (EXPERIMENT 3 — NEGATIVE, CLOSED)
- **Mechanism:** blurred G-set consensus + spaced-top emission + divergence pruning ≤0.66 vs
  12 members.
- **Result (measured):** pre-prune overlap **0.98–1.00** vs every family member; after 4 prune
  rounds (37,654 → 30,126 dots) worst overlap **0.7987 > 0.70** → duplicate verdict. See
  `evidence/gset2_run_card_20261031.json`.
- **Conclusion:** the family cannot be re-submitted uniquely at this budget. **Closed — do not
  retry without a new information source.**

### H5 — Vent-centric external-stack GBDT (EXPERIMENTS 1–2 — NEGATIVE)
- **Mechanism:** fold-proper HistGradientBoosting on 30 external channels (GeoDawn + LiDAR + SGMC +
  vents/wells/probes/Qfaults + confounds), two-regime emission.
- **Result (measured):** HOLDOUT-DTI 0.0114 (uniform) → 0.0437 (two-regime) vs R0-recipe control
  0.0967; paired Δ −0.053 [−0.069, −0.038]. Canaries 30/30 ≤ 0.754. PI-1 unique (worst 0.31).
- **Deliverable:** the session's unique validated raster `gemsdoe92-vgfp2r-…-bcb3d2af-zeros.tif`.
- **Conclusion:** external-stack appearance models alone cannot replace the H19-5 skeleton on the
  hide-and-recover instrument; they remain the only *unique* submittable artefact class.

---

## Validation protocol for H1 (before any weekly slot)
1. Place `numeric_features.tif` in `data/` (or the dropbox mirror); run `scripts/prepare_data.py`.
2. Train per-fold (seeds 20/30, `buffered_component_draw`) — features never see withheld segments.
3. Promotion gate: fold-proper HOLDOUT-DTI paired CI > 0 vs the R0-recipe control on the same folds
   (target ≥ 0.12), leakage canaries ≤ 0.90 per feature, PI-1 uniqueness vs the refreshed registry.
4. Only then: selector step for a weekly slot (portal cap 3/week).

## Irregularities flagged this session
- **IR-20261031-1:** the session prompt's parallel-run protocol references "the single method
  paragraph below", but no method paragraph exists in the prompt. The V-GFP lane paragraph was
  stated explicitly in `scripts/run_vgfp_20261031.py` to close the gap.
- **IR-20261031-2:** the prompt's quoted leaderboard high (0.4413 / 0.3195) is stale; the live
  leaderboard fetched 2026-10-31 shows #1 = 0.4544. All planning numbers were re-anchored.
- **IR-20261031-3:** the literal dense-witness uniqueness reading (17GEMSDOE 5.17 M-cell surface →
  overlap 1.000 for any non-empty candidate) is degenerate and cannot be satisfied by any
  submission; the operative rule used is the parallel-run rule as written (dot-vs-dot ≤ 70 %,
  |ρ| ≤ 0.90), disclosed in every run card.
- **IR-20261031-4:** external-stack mirrors are owner-repacked (u8 quantisation), not
  organizer-authenticated; every byte is hash-pinned in `registry/external_stack_manifest_20261031.json`.
- **IR-20261031-5:** no DrivenData auth in this sandbox → `numeric_features.tif` and organizer
  receipts cannot be fetched; all scores remain CLAIM/PROJECTION classes.
