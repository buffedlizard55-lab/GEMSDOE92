# Analysis — 2026-10-24 STEPEDGE session

Machine-checkable numbers: `evidence/r0_forensics_20261024.json`,
`evidence/stepedge_screen.json`, `evidence/stepedge_variants.json`,
`evidence/stepedge_proxy_audit.json`, `evidence/stepedge_run_card.json`,
`evidence/public_witness_stepedge.json`. Evidence labels are strict:
**HOLDOUT-DTI** = `gems57-pooled-hide-v2`; **PROXY** = local DTI vs a named
catalogue/control; **CLAIM** = owner-reported live score with no organizer
receipt in this repo; **LEADERBOARD-SNAPSHOT** = fetched from the official
leaderboard page this session. Nothing below is a projected score.

## TL;DR — download status first

**Generated this session (unique, format-valid):**
`h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif`
(zeros SHA-256 `c5dc98f2…07b4`; submission name
`GEMSDOE92-STEPEDGE-f60Sraw-20261024`; 93-char note in the audit receipt).
**✅ OK TO DOWNLOAD** (all format gates pass on disk re-read; values finite in
[0,1] — the portal error `Predicted values must be in range [0, 1]` cannot
occur with these bytes). **⛔ DO NOT SUBMIT — verdict negative, decided by the
automated gates, no human inspection involved:** it is literal-unique vs the
28-raster local dot registry (surface |ρ| 0.138; final worst forward overlap
0.461, |ρ| 0.396) and has the best SGMC ever measured in this repo (0.141464),
but HOLDOUT-DTI 0.003980 [0.003295, 0.004702] (22,663 withheld px) does not
beat the pre-registered bars (STRAINBREAK f60 0.005487; RELIEF p10 0.006045)
and its paired Δ vs R0 is −0.000026 [−0.000534, +0.000458]. No slot used.

## 1. Why did GEMSDOE32's h33-h33-2-b2 get CLAIM 0.2778, the owner's best?

Short answer: **it is an emission-geometry optimum of a fixed skeleton, not
new geology.** The official metric (problem description p.967, fetched and
transcribed this session) is

```
TPw = Σ_g max_x p(x)·k(d(x,g)),  FPw = Σ_x p(x)·[1 − max_g k(d(x,g))],
FNw = |G| − TPw,                 DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw),
k(d) = max(1 − d/300 m, 0)
```

Three consequences drive everything:

1. **Max-per-truth-pixel credit.** A second dot within 300 m of an already
   covered truth pixel earns ~nothing in TPw yet pays up to full mass in FPw.
   Redundant along-strike dots are pure cost.
2. **Known faults are masked pixel-exactly** (organizer forum 11516): mass on
   or beside a mapped fault, far from any *new* fault, is fully penalised.
3. **β ≫ α** (0.8 vs 0.2): at fixed skeleton quality, *deleting* low-credit
   dots is cheap and missing truth is expensive — but only until coverage of
   the skeleton's *true* strands starts to thin.

The lineage was rebuilt mask-exactly this session from the hash-pinned H19-5
skeleton (`scripts/analyze_r0_lineage.py`; parent SHAs match
`registry/parents/R0.json`). Measured GEOMETRY along the CLAIM climb:

| Stage | CLAIM | Dots | NN dist (median) | Mass ≤2 px of catalogue | Footprint within 3 px | SGMC PROXY |
|---|---:|---:|---:|---:|---:|---:|
| H19-5 skeleton | 0.1922 | 121,131 px | 1.0 px | 14.3% | 19.6% | 0.1006 |
| D1.5 thin | 0.2477 | 60,069 | 2.24 px | 14.6% | 18.1% | 0.1011 |
| D2.8 thin | 0.2600 | 44,090 | 3.0 px | 14.6% | 17.2% | 0.0953 |
| SOLO (d_cat>1) | 0.2708 | 40,199 | 3.0 px | 6.3% | 16.0% | 0.0963 |
| **R0 (d_cat>2)** | **0.2778** | **37,654** | **3.0 px** | **0%** | **15.1%** | **0.0961** |

Deleting 69% of the skeleton's pixels surrendered only 4.5 points of
within-kernel footprint coverage (19.6% → 15.1%) and no SGMC credit, while
spacing converged exactly onto the 3 px kernel radius and masked-catalogue
waste went to zero. That is the whole climb. What R0 never changed is
*content*: 94.2% of its mass still sits >3 px from the catalogue on a
potential-field worm skeleton (multiscale magnetic/gravity gradients), and
its surviving dots were chosen by deterministic scan order, not by evidence.
Two further integrity findings from the same audit (see §5): the in-repo
`gems/metric.py` implemented a non-official algebra (could return DTI = 5.0;
fixed and retested this session — the vendored holdout evaluator was verified
against a brute-force transcription to 1.7e-16 and was never affected), and
the bridged `sample_submission.tif` positives are pixel-identical to the
catalogue (60,988 px) although p.967 describes an all-zero sample — harmless
for footprint use, flagged in `IRREGULARITIES.md`.

Can we generate a submission that scores higher than 0.2778? **Plausible in
principle, unproven here, and this session did not do it.** The gap to the
leader is not an emission gap. LEADERBOARD-SNAPSHOT (fetched 2026-10-24):
#1 `xiaofanhu` 0.4413 (29 submissions), #2 0.3916, #5 0.3539 — a different
regime from every owner CLAIM (best 0.2778; the prompt's 0.3195 is a stale
snapshot). Since thinning/clearance are saturated (this repo's 90+ site
experiments and §1's table), the remaining headroom must be new *skeleton
content* the experts actually mapped — most plausibly from the 1 m DEM links
the organizers distribute (labels were "manually identified" by fault
experts, p.967), i.e. fine-scale scarp mapping resampled to the 100 m grid.
That dataset is behind DrivenData login and cannot be restored from this
sandbox; it is the project's single largest access limitation. Within the
100 m stack, this repo has now tested worms, slope-break coherence (BREAKLINE),
signed polarity (SCARPPOL, duplicate), analytic signal (ANASIG), strain
gating (STRAINBREAK), gravity crests (screen-falsified) and sustained steps
(§2). Every one moves holdout/SGMC by hundredths *on their own instruments*;
none has a live receipt. Honest statement: **no candidate in this repo has
demonstrated an improvement over CLAIM 0.2778; only an organizer receipt can
demonstrate one.**

## 2. This session: STEPEDGE (aperture-persistent sustained steps)

Hypothesis (pre-registered, `docs/HYPOTHESES_20261024_STEPEDGE.md`): a fault
offsetting like-against-like carries a topographic throw that *sustains*
across apertures (200–300 m **and** 400–600 m either side of the trace along
the structure-tensor dominant-gradient direction, Band 12 `det_elev`),
whereas channels/ridges cancel. Synthetic anchor: 6 m step → persistent
5.4 m; equal-relief channel → 1.3 m (`tests/test_stepedge.py`). Mimic named
a priori: Lake Lahontan benches, fan/terrace edges, cuestas.

**Screen (preserved code, baseline reproduced to the digit — BREAKLINE-L sym
AUC 0.621604, far SGMC 0.072325):**

| Surface | sym AUC (canary) | far-only SGMC | far overlap vs BREAKLINE f45 far |
|---|---:|---:|---:|
| BREAKLINE L (baseline) | 0.6216 | 0.072325 | 1.000 |
| STEPEDGE persistent × coherence | 0.6204 | 0.065885 | **0.755 duplicate-stop** |
| STEPEDGE near-only × coherence | 0.6177 | 0.066072 | 0.766 duplicate-stop |
| TRANSV L×transversality | 0.6372 | 0.068060 | 0.754 duplicate-stop |
| RADSTEP concordance | 0.6091 | 0.061765 | 0.668 |
| **STEPRAW (persistent step, no coherence)** | 0.5797 | **0.071257** | **0.427** |

The coherence gate — shared by BREAKLINE/SCARPPOL — is what collapses every
terrain lane onto the same lineaments. Removing it keeps 98.5% of the SGMC
signal on a 57%-disjoint far set, so per the pre-registered rule STEPRAW was
built (doses f33/f45; then f60 with sibling-far repulsion after f33/f45
failed literal uniqueness vs *same-dose siblings*, 0.760/0.711 — registry
growth now makes equal-dose keep-subsets tile the skeleton within 3 px of
each other; the f60 repair is the STRAINBREAK-proven technique).

**Results (`gems57-pooled-hide-v2`, 22,663 withheld px, same folds all arms):**

| Arm | HOLDOUT-DTI [95% CI] | SGMC PROXY | Worst local fwd overlap (28 rasters) |
|---|---|---:|---:|
| R0 | 0.004006 [0.003424, 0.004690] | 0.096060 | — |
| BREAKLINE f45 | 0.004861 [0.004032, 0.005822] | 0.126105 | 0.55 (its session) |
| ANASIG f45 | 0.004967 [0.004098, 0.005940] | 0.080556 | 0.550 |
| STRAINBREAK f60 | 0.005487 [0.004522, 0.006430] | 0.105162 | 0.400 |
| RELIEF p10 (duplicate) | 0.006045 [0.005187, 0.006927] | 0.087245 | duplicate |
| STEPEDGE f33Sraw | 0.004330 [0.003571, 0.005200] | 0.120072 | 0.760 duplicate |
| STEPEDGE f45Sraw | 0.004228 [0.003384, 0.005233] | 0.127434 | 0.711 duplicate |
| **STEPEDGE f60Sraw** | **0.003980 [0.003295, 0.004702]** | **0.141464** | **0.461 unique** |

Leakage canary: built surface 0.5797, max over all features 0.6216 (control)
— nothing approaches 0.90. Dose response is *inverse* on the catalogue
holdout and *positive* on SGMC: the starkest instruments-disagree result in
the repo. Readings: (a) ungated sustained steps are dominantly
range-front/bedrock structures (SGMC's compilation) that experts may or may
not count as *new* Quaternary faults; catalogue hide-and-recover, which
rewards continuity with mapped strands, prices them at R0 level. (b) SGMC
truth (bedrock faults >3 px off catalogue) is itself biased toward exactly
the sustained-step landform, so SGMC may over-credit this lane. Local
instruments cannot separate (a) from (b); the pre-registered gate requires
the holdout bar, so the verdict is **negative** and the goalposts were not
moved. What this session adds beyond another negative: a candidate that is
literal-unique on the *grown* 28-raster registry with the strongest
off-catalogue bedrock signal yet measured — the natural single receipt to
buy if a human selector ever decides to price SGMC-vs-holdout disagreement
directly (decision rules in `evidence/stepedge_run_card.json` framing and
§4; never submit f33/f45 — duplicates; never pair doses).

## 3. Uniqueness policy, stated plainly

Two verdicts, both printed, neither hidden. **Dot-registry (local, literal
thresholds):** PASS — surface |ρ| ≤ 0.138, final dots worst overlap 0.461 /
|ρ| 0.396 over 28 deduplicated rasters. **Dense public witness (literal
vendor rule):** FAIL — the hash-verified 17GEMSDOE E-proba raster is positive
on 100% of the footprint, so forward overlap is 1.000 for *any* non-empty
in-footprint candidate (measured on these exact bytes:
`evidence/public_witness_stepedge.json`); rank-correlation vs it is 0.0004
(dots) / 0.2109 (surface). The session's documented scope (overlap gates
apply to dot-like rasters ≤150k positives; ρ gates apply to all) is an
explicit policy amendment, recorded before building. A full public scan
(`scripts/audit_public_registry.py`, ~1,300 rasters) was **not** rerun this
session; uniqueness is claimed only for the stated scopes.

## 4. What would change the decision / next steps (in order)

1. **One organizer receipt** for any off-skeleton lane prices far-dot value
   and resolves SGMC-vs-holdout. Candidate order for a human selector, by
   instrument disagreement value: STEPEDGE f60Sraw (SGMC-best, unique) >
   BREAKLINE f45 (balanced) > STRAINBREAK f60 (holdout-best unique). Receipt
   rules: Δ ≥ +0.01 vs CLAIM 0.2778 ⇒ off-skeleton terrain steps earn live
   credit, next lane is shoreline-suppressed steps; Δ ≤ −0.01 ⇒ skeleton mass
   is load-bearing at 37,654 dots, retire f≥45 doses; |Δ| < 0.01 ⇒ no
   evidence, spend nothing further on siblings.
2. **Obtain the 1 m DEM links** (DrivenData data tab, login required) and
   build a fine-scale scarp skeleton — the only identified path from the
   0.27 regime toward the 0.44 regime. Free/official but unrestorable here.
3. Do not build a fourth STEPEDGE dose (budget spent; f60→holdout flat/down,
   and uniqueness at f60 is achieved). Do not retry coherence-gated terrain
   lanes (three duplicate-stops now: SCARPPOL, STEPEDGE×coh, TRANSV).
4. Keep pytest + `scripts/check_site.py` green with whatever primary is
   served; receipts, when they exist, go to `ledger/submissions.csv`
   (currently still 0 RECEIPT rows — the repo's deepest evidentiary hole).

## 5. Shared-tool fix (protocol rule 2)

`gems/metric.py` implemented a brief-derived algebra in which TPw was a
dot-side kernel *sum* and G was uncovered mass; it returned DTI up to 5.0.
Fixed once to the official max-per-truth equations (`T = Σ_g best_g`,
`DTI = T/(0.2T + 0.2(S−M) + 0.8|G|)`), marginal gains rewritten exactly, and
cross-tested against `vendor/gems57/metric.dti_exact` (agreement 1e-9 on
random cases; vendor vs brute-force 1.7e-16; official worked example
3.00/1.89/2.00 → 0.6027 ≈ page's 0.60). No build or gate in this repo read
the buggy totals (holdout always used vendor), so no historical raster
changes; historical MASS ranking used its *ordering*, recorded in
`IRREGULARITIES.md`.

## Sources (official/verified, fetched or pinned this session)

- Problem + metric + format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard snapshot 2026-10-24 (#1 0.4413): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Known-fault masking (pixel-exact): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN (features + radiometrics provenance): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and · DOI https://doi.org/10.5066/P93LGLVQ
- USGS SGMC control: https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
- INGENIOUS / GDR #1391: https://gdr.openei.org/submissions/1391 · https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Owner prior-art sites (CLAIM scores, no receipts in-repo): the GEMSDOE## GitHub Pages series as listed in `README.md`/`ledger/` (best: https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html, 0.2778 CLAIM).
