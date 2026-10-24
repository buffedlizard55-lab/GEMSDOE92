# Analysis — 2026-10-24 session (SCARPPOL → ANASIG)

Machine-checkable numbers live in `evidence/scarppol_variants.json`,
`evidence/scarppol_proxy_audit.json`, `evidence/scarppol_run_card.json`,
`evidence/anasig_variants.json`, `evidence/anasig_proxy_audit.json`,
`evidence/anasig_run_card.json`, `evidence/public_witness_anasig.json` and
`docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-audit.json`.
Labels: **HOLDOUT-DTI** = `gems57-pooled-hide-v2` (8 buffered folds, seeds
20/30, 22,663 withheld positives, α=0.2, β=0.8, 300 m triangular kernel,
1,000 paired 20 km spatial-cluster bootstrap draws); **SCREEN-AUC** =
single-feature symmetric AUC vs the same withheld positives; **PROXY** =
USGS SGMC off-catalogue control (62,703 truth px); **CLAIM** = owner-reported
score with no receipt in this repo. No local number is a leaderboard score.

## 1. Why did `h33-h33-2-b2` (CLAIM 0.2778) score highest among the listed sites?

Re-verified from the rasters this session (`scripts/restore_inputs.py`,
all 12 SHA-256 pins OK, including the 419 MB 19-band stack):

1. It is a fixed budget of 37,654 unit dots thinned from the H19-5
   multi-line potential-field worm skeleton (verified set chain
   R0 ⊂ SOLO ⊂ D2.8 ⊂ H19-5 in prior sessions), with a 2.8 px spacing
   floor, zero mass on the mapped catalogue, and min catalogue distance
   2.236 px. Under DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw), at fixed mass:
   spacing removes kernel-redundant dots, catalogue clearance spends
   mass only where undiscovered truth can earn credit, and β≫α makes
   pruning low-credit dots cheap. The reported lineage moves exactly
   along those three levers (0.1922 → 0.2600 → 0.2708 → 0.2778).
2. Its scan-order (unranked) thinning is also its weakness: which
   skeleton pixels survive is decided by position, not evidence, so a
   per-dot signal that re-ranks the same budget must weakly dominate it
   *if* such a signal exists off the skeleton.
3. 0.2778 remains a **CLAIM**, not ORGANIZER-CONFIRMED: this repo holds
   no submission-page receipt for it (ledger: 0 RECEIPT rows before and
   after this session). The prompt's leaderboard figures (0.3195 /
   0.4413 at #1) are conflicting snapshots, neither is a receipt for
   GEMSDOE32 or for this project.

**Can a candidate here be shown to beat 0.2778? No — not locally.** The
only valid live comparison is an organizer receipt, and no slot was
used this session. Every candidate below is judged on HOLDOUT-DTI and
uniqueness, never converted into a projected leaderboard score.

## 2. What was screened, built, and stopped

Hypotheses and screens (ranked before building):
[`HYPOTHESES_20261024_SCARPPOL.md`](HYPOTHESES_20261024_SCARPPOL.md).
Screens covered gravity-crest, analytic-signal, gravity-hinge, strain,
radiometric-gradient, spring-density/alignment, and seven DEM
statistics. Two screens matter most:

| Surface | SCREEN-AUC | far-set PROXY (16,944 dots) |
|---|---:|---:|
| BREAKLINE L (control) | 0.621604 | 0.072325 |
| SCARPPOL \|dir2\|×coherence | 0.628012 | 0.067670 |
| ANASIG A×coherence | 0.503999 | 0.028167 |
| CONCORD ana·grav·hinge | 0.528413 | 0.021445 |
| RAD grad(TC) | 0.503986 | 0.067312 |

### Lane 1 — SCARPPOL (built, then duplicate-stopped)

Three doses (f33/f38/f45) built with the template keep/far machinery.
**HOLDOUT-DTI** f45: **0.005315 [0.004387, 0.006418]**, Δ vs R0
+0.001309 [+0.000626, +0.002015] — above BREAKLINE f45 (0.004861).
But final-dot forward overlap vs the same-dose BREAKLINE files is
**0.913 / 0.909 / 0.900** (> 0.70): diagnosis showed the keep sets are
>90% shared (coverage-greedy is weight-insensitive at this budget) and
82% of far dots lie within 3 px of BREAKLINE far dots (both surfaces
pick the same ridge lines). Protocol rule 1: log as a duplicate and
stop. SCARPPOL files stay in `releases/` with
`evidence/scarppol_run_card.json`; verdict **negative**.

### Lane 2 — ANASIG (single dose built; this session's primary)

An in-memory f45 hybrid screen first (no file written) gave
HOLDOUT-DTI 0.004967 with forward overlap 0.528 vs BREAKLINE f45.
One file was then built (single dose, to limit the budget deviation
after SCARPPOL's three doses; logged in `IRREGULARITIES.md`):

**`h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif`**
SHA-256 `68964bd6c18efd8259c3b57468f5611974918e94808f613dec694737655cf4d5`

- **HOLDOUT-DTI 0.004967 [0.004098, 0.005940]**; Δ vs R0 **+0.000961
  [+0.000168, +0.001814]**; Δ vs holdout-best RELIEF p10 (0.006045)
  **−0.001078 [−0.002034, −0.000112]** → does not beat the holdout best.
- Leakage canary: ANASIG surface symmetric AUC 0.503999; max over
  screened features 0.551113 — no leakage signal (threshold 0.90).
- SGMC PROXY 0.080556 vs R0 0.096060 (below parent: the far magnetic
  ridges do not enrich bedrock SGMC faults once diluted into the
  hybrid; this weakens, not supports, the live case).
- Uniqueness (local dot registry, 24 rasters): pre-placement surface
  worst |ρ| **0.024**; final dots worst forward overlap **0.550** (R0),
  worst |ρ| **0.547** → **locally unique, not a duplicate**.
- Format: 10/10 MUST gates on independent re-read (`-audit.json`
  beside the file): float32, EPSG:32611, 3730×3292, template
  transform, all finite in [0,1], zeros outside, zero catalogue mass,
  37,654 dots, min catalogue distance > 2 px.
- Public literal rule: single-witness measurement
  (`evidence/public_witness_anasig.json`, Git blob SHA verified)
  gives forward overlap **1.000** vs 17GEMSDOE E-proba (positive on
  5,167,373/5,167,373 footprint cells). Under the rule as written that
  is a binding duplicate for *any* in-footprint candidate; it is
  recorded, not waived.

**Verdict: negative / NOT CLEARED for a weekly slot; format-valid and
OK TO DOWNLOAD.** Two independent slot blockers (holdout-best bar,
public literal rule) plus a below-parent SGMC proxy. This is still the
session's unique deliverable: it is the only new file that is
lane-disjoint from every local registry raster on both the surface
and the final dots.

## 3. Answers, in one place

- *Why 0.2778?* Fixed-budget, spaced, catalogue-cleared dots on a
  corroborated potential-field skeleton — exactly the three levers
  the α=0.2/β=0.8 triangular-kernel DTI rewards (§1). CLAIM, not a
  receipt held here.
- *Can we generate a submission shown to score higher?* No local
  instrument can show that; claiming otherwise would be a projection
  written as a score. What this session *does* show: a lane-unique,
  format-valid file whose HOLDOUT-DTI beats its parent with CI
  excluding 0, and a second lane (SCARPPOL) that beats it on the
  holdout but is a literal duplicate. Promotion still requires
  beating the holdout best and resolving the public literal-rule
  witness — both are selector/operator decisions, not this agent's.
- *Geothermal-vent angle:* the SPRINGLINE screen (928 Hot/≥50 °C
  GDR points) found no measurable enrichment at 100 m (SCREEN-AUC
  ≈ 0.50–0.517, far PROXY 0.015–0.018). Springs remain a named,
  untested *line-alignment* idea (spring-pair strikes), not a density
  idea; do not rebuild it as density.

## 4. Irregularities flagged this session

Full text in `IRREGULARITIES.md`: (i) SCARPPOL duplicate after
holdout success — keep-stage coverage dominance makes template reuse
a lane-drift hazard; (ii) one extra single-dose build beyond the
3-dose budget after the duplicate stop; (iii) shared audit tool had
the collar surface hard-coded (fixed in
`scripts/audit_public_registry.py`, fail-closed now); (iv) 3 GB host
OOM in the first ANASIG report run (registry distances now computed
per-row); (v) duplicated phrase in the generated form note (fixed to
84 chars, hashes of the TIFF unchanged — note is metadata only).
