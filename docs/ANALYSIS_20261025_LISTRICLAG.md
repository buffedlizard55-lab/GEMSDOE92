# Analysis — LISTRICLAG session (2026-10-25)

Pre-registration: [`docs/HYPOTHESES_20261025_LISTRICLAG.md`](HYPOTHESES_20261025_LISTRICLAG.md)
· Run card: [`evidence/gemsdoe92-listriclag-20261025T145312Z_run_card.json`](downloads/gemsdoe92-listriclag-20261025T145312Z_run_card.json)
· Builder: `scripts/build_listriclag_submission.py` (shared template reused; no private fork).

Every number below is labelled per Protocol Rule 3. Evaluator:
`gems57-pooled-hide-v2`, 22,663 withheld catalogue-positive pixels across
8 buffered whole-component quadrant folds (seeds 20 + 30), pooled DTI
(`alpha = 0.2`, `beta = 0.8`, 300 m triangular kernel), 1,000-draw paired
20 km spatial-block bootstrap. **No ORGANIZER-CONFIRMED receipt exists for
any GEMSDOE92 artifact; the ledger holds 0 portal receipts.**

---

## 1. The assigned question: why did `GEMSDOE32 h33-h33-2-b2 … e5eb6e7e-zeros` reach the site-claimed 0.2778, and can it be beaten?

Evidence class for `0.2778`: **owner-site CLAIM** (GEMSDOE32 pages), not an
organizer receipt in this repository's ledger. With that caveat, the
mechanism is established by prior forensics in this repo
(`scripts/analyze_r0_lineage.py`, `docs/ANALYSIS.md` lineage sections,
`registry/parents`) and re-verified this session against the pinned parent
raster (`data/parent_R0_zeros.tif`, SHA-256 `c55bafc4…`):

1. **It is a catalogue-skeleton redraw, not a discovery product.** R0's
   37,654 unit dots lie entirely on the H19-5 corridor skeleton thinned to
   a ≥ 2.83 px nearest-neighbour floor: `XOR(R0, thinned(H19-5 ∩ d_cat > 2)) = 0`
   (prior-session receipt). H19-5 itself (`0.1922` claim) is a
   catalogue-corroborated multiline product, so R0 inherits mapped-fault
   geometry nearly one-for-one.
2. **The metric is engineered for exactly that shape of answer.** DTI =
   `TP_w / (TP_w + 0.2·FP_w + 0.8·FN_w)` with a 300 m (3 px) triangular
   kernel. Three consequences, provable from `vendor/gems57/metric.py`
   algebra (verified against `dti_bruteforce` in `tests/test_metric.py`):
   - False positives are five times cheaper than misses (`alpha/beta = 0.25`),
     so a sparse dot field pays almost nothing for being wrong.
   - One unit dot credits every truth pixel within 3 px at weight
     `k(d) = max(1 − d/3px, 0)`; dots spaced ~2.83 px tile corridors at
     near-maximal `TP_w` per dot — denser dots self-cannibalize (the
     per-truth max saturates), sparser dots leave kernel gaps.
   - The hidden test faults are, to a large extent, spatially adjacent to
     or interleaved with mapped systems (fault systems cluster), so mapped
     corridors are the highest prior-density corridors available without
     labels.
3. **Its sibling receipts bracket the regime.** The site-claim series shows
   budget monotonicity along the same skeleton: 37,654 dots → 0.2778 claim;
   44,090-dot variants → 0.26 claims; solo-d2.8 → 0.2708 claim. That is the
   signature of a kernel-packing optimum near the 37–45 k budget on
   catalogue corridors, not of superior geology.

**Can it be beaten?** Yes, in principle, and the margin to the current
leaderboard best (`0.4413`, DrivenData leaderboard, organizer-published)
proves ≥ 0.16 of headroom exists beyond pure catalogue redraw. The two
mathematically available levers, in this repo's evidence:

- **Budget extension past 37,654.** The marginal-inclusion bar is
  `k > alpha·DTI ≈ 0.2 × 0.28 ≈ 0.056` expected kernel credit per dot —
  a very low bar; tens of thousands of positive-expectation pixels beyond
  the skeleton clear it (PROVINCETOE §3.2 analysis). This session's E3
  probe measured the direction on holdout: on the identical surface,
  90,000 dots (tail at `p = 0.30`) scored HOLDOUT-DTI **0.062202
  [0.051892, 0.073341]** vs **0.054843 [0.044940, 0.066261]** for the
  binary 37,654 arm — a paired, same-surface **+13.4%** from budget/
  emission policy alone.
- **Better off-skeleton ranking.** The repo's hide-and-recover record
  (KNICKLOQO standalone, Rule-2 fold-visible **0.109043**; COULOMB-LOQO
  **0.113316**) shows learned multi-layer rankings recover withheld real
  faults far better than any single-physics surface (this session: ≤ 0.0677).

What this repo's governance does **not** allow is restating the catalogue
skeleton (lane drift into GEMSDOE32's lane — the uniqueness gate measures
precisely this), so beating 0.2778 from inside GEMSDOE92 requires
promote-grade off-catalogue ranking *plus* the extended-budget emission —
and an actual organizer receipt to replace CLAIM-class numbers.

---

## 2. This session's experiments (3/3 budget, 0 weekly slots)

### E1 — LISTRICLAG primary (ring-coupled, 37,654 unit dots)

- **HOLDOUT-DTI = 0.054843 [0.044940, 0.066261]**, withheld = 22,663;
  paired vs R0 `+0.050837 [+0.040920, +0.061690]` (R0 = 0.004006).
- Below the pre-registered promotion bar (COULOMB-LOQO `0.113316`) ⇒
  **verdict: negative** regardless of uniqueness.

### E2 — LISTRICLAG_LOCAL ablation (identical recipe, annulus removed)

- **HOLDOUT-DTI = 0.067679 [0.054787, 0.081247]**.
- **Paired ring-vs-local Δ = −0.012836 [−0.020424, −0.005791]** — the CI
  excludes zero on the *negative* side. **The pre-registered lag-coupling
  hypothesis is rejected on this instrument**: granting 2.8–8 px of
  scarp-displacement tolerance costs ~19% of the score rather than adding.
- PhD-level reading: the hide-and-recover truth is *withheld catalogue
  faults*, which are scarp-mapped by construction — their terrain evidence
  is co-located, so blurring the scarp term with an annulus maximum only
  dilutes localization (the annulus admits fan-toe and shoreline mimics at
  8 px exactly as pre-registered under "named non-fault mimic"). The lag
  mechanism, if it exists, is only testable on *scarpless* truth — i.e.,
  an off-catalogue instrument (SGMC bedrock-fault proxy), not on a
  scarp-biased holdout. This is a structural limit of the instrument, now
  on record for every future "displacement-tolerant" proposal.

### E3 — LISTRICLAG_N90K (emission-policy probe, 90,000 dots: prefix 37,654 @ 1.0, tail @ 0.30)

- **HOLDOUT-DTI = 0.062202 [0.051892, 0.073341]** — beats the same-surface
  binary arm by +13.4% paired, confirming the §1 budget-extension lever on
  a real holdout rather than algebra alone.
- Implication (next session, pre-registered there): apply the extended
  budget to the *strongest* ranker (KNICKLOQO-class LOQO ensemble), not to
  this lane's rejected surface.

### Leakage canaries (Protocol Rule 4)

6/6 PASS: max symmetric AUC = **0.579583** (`S`) ≤ 0.90; per-feature:
terrain_ring 0.5228, terrain_local 0.5337, basement_edge 0.5441,
grav_edge 0.5301, S_local 0.5722.

### Uniqueness (REGISTRY-MEASUREMENT)

- **Local registry (107 rasters):** worst literal/matched-budget overlap
  **0.412386** (vs `gemsdoe92-drainageknick…-zeros.tif`), worst |ρ| =
  0.083332 ⇒ unique. N90K arm: worst overlap 0.343589 ⇒ unique.
- **Public registry (102 repos, Git-blob-verified cache, 1,464 blobs):**
  see `evidence/listriclag_public_registry_uniqueness.json` (merged into
  the run card by `scripts/finalize_listriclag.py`). The full-footprint
  `17GEMSDOE E-proba-multiscale` witness (5,167,373 positive px) fires
  literal 1.0000 against *every* nonempty raster including parent R0
  (specificity receipt in the audit JSON); the matched-budget reading for
  this candidate is **0.0602**.

### Artifacts (format-valid, automated gates, zero human inspection)

| Arm | File | SHA-256 | Validator |
|---|---|---|---|
| primary | `docs/downloads/gemsdoe92-listriclag-20261025T145312Z-zeros.tif` | `a301cbfc970861c65f8001d0e1a3ecc1dca76c48699d4fdbd56d6768d2405b4c` | float32 · EPSG:32611 · 3730×3292 · pinned transform · finite ∈ [0,1] · 0 NaN · 0 catalogue mass · 37,654 dots |
| N90K | `docs/downloads/gemsdoe92-listriclag-20261025T145312Z-n90k-zeros.tif` | `2704229bd09ef26ae1586e060d3453d82c8a683a6e083e34da2889cefa2f31a1` | same gates · 90,000 positives (37,654 @ 1.0, 52,346 @ 0.30) |

Submission name `GEMSDOE92-LISTRICLAG-20261025`; note (121/140):
`h33-h33-2-b2; LISTRICLAG: 37654 dots, annulus(2.8-8px) scarp evidence x basement-step x gravity edge; listric updip-lag lane`.

---

## 3. Verdict

**negative** (deliverable). Not submission-eligible: fails the registered
holdout bar by −0.058 (and the lag mechanism itself is rejected by its own
ablation). 0 weekly slots spent. Both TIFs are OK TO DOWNLOAD FOR RESEARCH
(all automated format gates PASS) and **NOT OK TO SUBMIT**.
