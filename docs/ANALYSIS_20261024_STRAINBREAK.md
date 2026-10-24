# Analysis — 2026-10-24 late session (GRAVCrest screen → STRAINBREAK)

> **Historical STRAINBREAK experiment record — research only; DO NOT SUBMIT.** A saved local result or prior public-registry scan does not confer current eligibility. No STRAINBREAK artifact was generated or rerun in the current review. See [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) for the current project decision.


Machine-checkable numbers: `evidence/gravcrest_screen.json`,
`evidence/strainbreak_variants.json`, `evidence/strainbreak_proxy_audit.json`,
`evidence/strainbreak_f75_audit.json`, `evidence/strainbreak_run_card.json`,
`evidence/strainbreak_public_registry_uniqueness.json`. Every local number is
HOLDOUT-DTI or PROXY; 0.2778 remains an owner-reported CLAIM with no receipt
in this repo (`ledger/submissions.csv`: 0 RECEIPT rows). Nothing below is a
projected leaderboard score.

## 1. Why 0.2778, and can this session beat it?

The full line-by-line lineage analysis stands (`docs/ANALYSIS_20261024.md`
§1): H19-5 worm skeleton (0.1922 CLAIM) → Poisson thin 2.8 px (0.2600) →
solo prune (0.2708) → >2 px catalogue clearance, 37,654 unit dots (0.2778).
Mechanically, at fixed mass under DTI (α=0.2, β=0.8, 300 m triangular
kernel), thinning removes double-paid kernel redundancy, clearance stops
spending mass where masked known faults cannot pay, and β≫α makes
*removing* low-credit dots cheap and *missing* truth expensive. The two
measured openings remain: 94.2% of R0's mass sits >3 px from the catalogue
earning only where truly unmapped faults cross the skeleton, and R0's
surviving dots were chosen by scan order, not evidence.

Can STRAINBREAK beat CLAIM 0.2778 live? **Unknown and unclaimed.** Its
HOLDOUT-DTI (0.005487) is on a different instrument (catalogue
hide-and-recover) and is never comparable to a leaderboard number. The
repo-recorded 2026-10-24 leaderboard snapshot is 0.4413 at #1
(LEADERBOARD-SNAPSHOT; the prompt's 0.3195 is an older conflicting
snapshot). Only an organizer receipt can price any candidate; this session
used no slot.

## 2. Rank-1 hypothesis falsified before building (GRAVCrest)

Pre-registered screen (identical 16,944-dot spaced far sets, >3 px off
H19-5, d_cat>2 px; `evidence/gravcrest_screen.json`):

| Surface | Sym. AUC | Far-only SGMC DTI | Far-only fixed-cat DTI |
|---|---|---|---|
| BREAKLINE L (baseline) | 0.6216 | **0.072325** | 0.002887 |
| crestA \|Band18\|×coh(Band13) | 0.5339 | 0.005259 | 0.003478 |
| crestB \|\|∇Band18\|\|×coh(Band13) | 0.5396 | 0.016145 | 0.003852 |
| crestC Band5×coh(Band13) | 0.5497 | 0.005477 | 0.003255 |
| STRAINBREAK L×pct(Band4 2ndinv) | 0.5865 | 0.058377 | 0.003386 |
| L×pct(Band8 dilatation) | 0.5870 | 0.040133 | 0.003905 |
| seismic prox (Bands 10/16) | 0.5247 | 0.020558 | 0.002169 |

Gravity-crest far sets essentially never hit off-catalogue SGMC bedrock
faults. Either the isostatic-gradient crest at 100 m posting is dominated
by lithologic/pluton edges, or SGMC bedrock faults (mostly range-front,
already the gravity edge's *mapped* expression) sit on the skeleton the far
pool excludes. Per the falsifier written before the screen, GRAVCrest was
not built. Seismic-proximity also screened out as predicted (~100 km
smoothing cannot serve a 300 m kernel).

Queued item closed in the same screen: the visible-collar candidate scores
**SGMC 0.021192 vs R0 0.09606** — its catalogue-holdout gain (0.046866) does
not transfer off-catalogue at all. The collar is a catalogue-proximity
artifact, now measured three ways (duplicate gate, SGMC, fixed-cat 0.1295).

## 3. STRAINBREAK results (3 experiments, budget exhausted)

HOLDOUT-DTI `gems57-pooled-hide-v2` (seeds 20/30, 22,663 withheld px, 157
clusters, 1,000 paired draws; R0/RELIEF/BREAKLINE reproduced to the digit):

| Arm | HOLDOUT-DTI | SGMC | Worst local fwd overlap |
|---|---|---|---|
| R0 | 0.004006 [0.003424, 0.004690] | 0.09606 | — |
| BREAKLINE f45Ltop | 0.004861 [0.004032, 0.005822] | **0.12611** | 55.0% |
| STRAINBREAK f45s2i | 0.005022 [0.004118, 0.005890] | 0.10580 | 55.0% |
| **STRAINBREAK f60s2i (primary)** | **0.005487 [0.004522, 0.006430]** | 0.10516 | **40.0%** |
| STRAINBREAK f75s2i | 0.005486 [0.004454, 0.006486] | 0.10327 | 25.0% |
| RELIEF p10 (holdout best, R0-duplicate) | 0.006045 [0.005187, 0.006927] | 0.08725 | duplicate |

Paired: f60−R0 +0.001481 [+0.000582, +0.002296]; f60−BREAKLINE +0.000626
[−0.000400, +0.001577]; f60−RELIEF −0.000558 [−0.001615, +0.000436];
f75−f60 −0.0000006 [−0.000332, +0.000325] — a hard dose plateau.
Leakage canary: max symmetric AUC 0.6216 (L component; S alone 0.5865,
Band 4 alone 0.5102) — no feature near 0.90. Local literal uniqueness
(21 rasters, surface + final dots): surface worst forward overlap 0.0995,
worst sampled Spearman 0.1027; final dots worst 0.4000 (parent R0, exactly
the kept fraction) — not a local duplicate.

**Interpretation.** The strain multiplier buys catalogue-holdout credit and
sells SGMC bedrock credit relative to strain-blind BREAKLINE at equal
structure. Two readings: (a) strain corridors genuinely host the young
strands experts will newly map (holdout is right, SGMC's old bedrock
compilation is the wrong truth); (b) smooth strain fields pull dots toward
catalogue-dense, already-well-mapped corridors, inflating hide-and-recover
without discovery value (SGMC is right). Local instruments cannot separate
these — only an organizer receipt can. That ambiguity, plus failing the
pre-registered "beat the holdout best" bar, is why the verdict is negative
despite the best locally-unique holdout number this repo has produced.

## 4. What would change the decision

One organizer receipt for any off-skeleton lane (BREAKLINE or STRAINBREAK)
prices far-dot value directly and resolves (a) vs (b) sign. Decision rules
are in the run card. Until then: no fourth dose (plateau measured), no
GRAVCrest retry without a new gravity product, shoreline-suppression held
pending a receipt (hypotheses doc rank 4).

## Sources (official/verified)

- Competition + metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN (band provenance): https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
- USGS SGMC control: https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
- Monte Cristo Range unmapped rupture: USGS pub 70217872 (Koehler et al. 2021, SRL)
- Band semantics: tags inside the pinned `training_features.tif` (read this session; Band 4 `geod_2ndinv`, 8 `geod_dilaterate`, 18 `iso_grav_anom_hg` signed, 49% negative on decimated read).
