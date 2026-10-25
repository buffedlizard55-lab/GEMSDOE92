# Analysis — VARIO session 2026-10-25: why R0 "0.2778" leads the GEMSDOE sites, whether it can be beaten, and what VARIO measured

Evidence discipline (protocol rule 3): every number below is labelled
**HOLDOUT-DTI** (local surrogate, evaluator `gems57-pooled-hide-v2`),
**PROXY**, **REGISTRY-MEASUREMENT**, **CLAIM** (owner-reported, no organizer
receipt in this repo), **MODEL**, or **ORGANIZER-CONFIRMED**. No projection
is written as a score. Session output: three new byte-unique GeoTIFFs,
verdict **negative** — see [run card](downloads/vario_run_card.json).
**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.**

## 1. Why and how did `h33-h33-2-b2` (GEMSDOE32) get 0.2778?

### 1.1 What is verified, and what is not

* The **value 0.2778 is a CLAIM**. It appears in the session brief's site
  inventory and in `ledger/historical_climb.csv` with
  `evidence_label=CLAIM, receipt=N`. No DrivenData submission-page receipt
  for those exact bytes exists in this repository (`ledger/submissions.csv`
  has no receipt score for it).
* The GEMSDOE32 page itself, re-fetched 2026-10-25
  (https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html, repo
  commit 012e17b2), calls the file **UNSCORED**, gives a *projected* 0.2747
  explicitly as "a MODEL, not a score", and states "NO ORGANISER SCORE
  EXISTS for this or any artifact in this repository." Either the file was
  submitted after that page was frozen, or 0.2778 comes from another
  channel; from evidence available here we cannot distinguish those, so we
  cannot causally "explain 0.2778" as an organizer result. What we *can* do
  is verify the file's construction exactly and explain, from the official
  metric, why that construction should score better than its ancestors —
  which is also the direction of the whole reported climb.
* The **construction is byte-verified** (re-measured this session on the
  pinned lineage in `.cache/gems_inputs/lineage/`, catalogue = 60,988 px,
  `d_cat` = EDT distance to it):
  H19-5 121,131 px → D2.8 44,090 px (∅ dots outside H19-5) →
  SOLO = D2.8 & `d_cat>1` exactly (XOR = 0; 40,199 px) →
  **R0 = D2.8 & `d_cat>2` exactly (XOR = 0; 37,654 px)**.
  Reported climb (all CLAIM): 0.1922 → 0.2600 → 0.2708 → 0.2778.
* The **official metric** (problem page fetched 2026-10-25,
  https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/):
  DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw), triangular kernel R = 300 m = 3 px,
  worked example 3.00/(3.00+0.2·1.89+0.8·2.00) = 0.60 — reproduced by
  `vendor/gems57/metric.py` and its brute-force oracle in tests. The private
  truth is *new faults manually identified by experts, not in the USGS
  database* (same page). The public leaderboard fetched the same day
  (…/leaderboard/) is #1 0.4413, #2 0.3916, so the brief's 0.3195 figure is
  stale and 0.4413 is current.

### 1.2 The mechanism (metric mathematics, not geology)

For a binary dot field with n dots, covered-truth credit T and total dot
self-credit M, the denominator collapses to 0.2·(T + n − M) + 0.8·|G|
(derivation in `vendor/gems57/metric.py`). One extra non-redundant dot with
kernel credit k raises DTI iff **k > α·DTI ≈ 0.052–0.056** at DTI ≈ 0.26–0.28.
Two consequences explain the entire climb:

1. **Thinning (121,131 → 44,090; reported +0.068).** Along a 1-px fault
   strand, neighbouring dots cover the same truth cells: T saturates at 1
   per truth cell while each extra dot still pays ~0.2·(1−k) of false-
   positive mass. Spacing dots at 2.83 px (≈ the 300 m kernel support)
   removes exactly the redundant mass, raising mean credit per dot at
   almost fixed T. This is the largest single step, and it is purely
   geometric — it needs no new geology.
2. **Catalogue-flank pruning (44,090 → 40,199 → 37,654; reported +0.011,
   then +0.007).** Dots within ≤2 px (200 m) of a *mapped* fault can earn
   almost no off-catalogue truth credit (the private truth is by
   construction not the mapped traces), yet each pays 0.2·(1−k). Deleting
   the `d_cat ≤ 1` shell (3,891 px) and then the `1 < d_cat ≤ 2` shell
   (2,545 px) removes low-k mass. Returns diminish because each shell is
   smaller and the 2–3 px band (retained: 2,171 px in R0) still contains
   genuine splay/tip credit within kernel reach of hidden strands.

What R0 did **not** do: change the underlying ranking. It is 100% confined
to H19-5's multiline-corroborated surface and thinned in scan order. Every
other high site claim in the inventory (0.24–0.28) is likewise an H19-5
descendant or a submodular re-emission of a corroborated surface, while
standalone single-physics detectors cluster at 0.01–0.19 (CLAIM inventory,
`ledger/site_scores_claimed_20261025.csv`, median 0.0843). The pattern is
consistent with the private truth being expert lineament mapping *similar
in character to H19-5's evidence*, scored by a metric that rewards
credit-dense, kernel-spaced, off-catalogue dots.

### 1.3 Can 0.2778 be beaten, and what would it take?

In principle yes — the verified leaderboard top is 0.4413, i.e. someone
already beats it by ≈59%. Through the metric arithmetic, at fixed mass
that requires ≈59% more mean realized credit per dot; no further pruning
or thinning of H19-5 can supply that (the B=1→B=2 shell was worth a
reported +0.007). It requires a **better-ranked surface** (dots nearer the
expert-mapped hidden traces) and/or budget reallocation toward the
marginal bar k ≈ α·DTI. Two candidate routes have real evidence behind
them: (i) expert-like high-resolution topography (the competition's own
1 m DEM links; only a 10 m-derived stack is obtainable in this sandbox),
and (ii) emission that covers the surface *blurred by the mapping-scatter
scale* rather than the surface itself (GEMSDOE32's live-anchored MODEL:
greedy on the σ=1.85 px-smoothed field beat dot-thinning by +0.014–0.025
in paired Monte-Carlo draws, while greedy on the raw surface lost; that is
a MODEL anchored to CLAIM scores, not a measurement). Route (ii) is
exactly where the local catalogue holdout and the live objective disagree,
because the holdout's truth lies *on* the catalogue network by
construction. Any claim to have "beaten 0.2778" therefore requires an
organizer receipt; a local HOLDOUT-DTI can only license spending a slot to
find out. VARIO (below) does not clear even that lower bar.

## 2. What VARIO tested and measured

Lane and frozen plan: [HYPOTHESES_20261025_VARIO.md](HYPOTHESES_20261025_VARIO.md)
(Rank 1 of 5 ranked candidates). New catalogue-free families in
`gems/vario.py`: RTP directional semivariogram anisotropy (lags 2/4 px) +
lag ratio; MT change-point at constant basement cover; five USGS 3DEP
10 m-derived scarp/χ columns — added to the proven 24-feature COULOMBLOQO
stack and 5 FAULTNET context fields, same LOQO/crest/spaced-emission code,
same strict draw-blind buffered whole-component holdout (seeds 20/30,
22,663 withheld positives) and same-draw refit controls.

**Pipeline verification.** The refit controls reproduce the recorded
FAULTNET-session numbers to all printed digits on the identical instrument
(control_FAULTNET_far 0.175147, control_FAULTNET 0.148707,
control_COULOMBLOQO 0.113890, control_H19_5 0.096757 vs
`evidence/faultnet_holdout.json`), which validates the whole
stack→canary→LOQO→emission→evaluator chain end-to-end.

**HOLDOUT-DTI results** (`gems57-pooled-hide-v2`, 22,663 withheld, 95% CI):

| arm | HOLDOUT-DTI | paired Δ of interest |
|---|---|---|
| control_FAULTNET_far (d_vis>4) | 0.175147 [0.159756, 0.189860] | best control (pre-registered bar) |
| **vario_full (E1, primary)** | **0.150020 [0.134975, 0.164286]** | vs FAULTNET same-emission: +0.001313 [−0.000723, +0.003368]; vs far bar: **−0.025127 [−0.029306, −0.020842]** |
| control_FAULTNET | 0.148707 [0.133888, 0.162834] | |
| vario_smooth (E3, σ=1.85 emission) | 0.141661 [0.125858, 0.156685] | vs vario_full: −0.008360 [−0.013149, −0.003195] |
| vario_nctx (E2, new physics only) | 0.116258 [0.102956, 0.130592] | vs COULOMBLOQO: +0.002368 [−0.000818, +0.005640] |
| control_COULOMBLOQO | 0.113890 [0.100783, 0.128559] | |
| control_H19_5 | 0.096757 [0.084839, 0.108454] | |

Readings, in decreasing order of importance:

1. **The new physics adds nothing significant.** With context held fixed,
   +0.0013 (CI includes 0); without context, +0.0024 (CI includes 0).
   Single-feature canaries explain why: semivariogram features are near
   chance alone (symmetric AUC 0.516–0.519), the constant-cover MT
   change-point is weak (0.526), and only the 10 m scarp columns carry
   modest signal (0.558–0.588) — consistent with VENTSCARP's earlier
   finding that 10 m topography helps but does not transform the ranking.
   The semivariogram-anisotropy hypothesis as implemented is falsified for
   this stack: at 100 m the RTP field's lag-2/4 anisotropy is dominated by
   the regional gradient direction, not by fault-local fabric breaks.
2. **Catalogue-network context remains the dominant term**
   (vario_full − vario_nctx = +0.0338, CI excludes 0), replicating
   FAULTNET. Its canaries are also the largest (cx_logtip 0.7775 < 0.90
   limit, so no leakage stop, but the draw guarantees withheld truth >3 px
   from visible faults, which flatters both the context fields and the
   d>4 "far" emission; neither advantage is guaranteed to transfer live,
   where hidden splays sit 2–3 px from mapped traces in R0's retained
   band).
3. **Scatter-blurred emission loses on the catalogue holdout**
   (−0.0084, CI excludes 0), replicating GEMSDOE32's instrument
   disagreement from the other side: the holdout rewards covering the
   surface. This neither confirms nor refutes the live-scatter MODEL; it
   shows the two instruments cannot both be optimized by one emission.
4. **Uniqueness fails (REGISTRY-MEASUREMENT).** Adding nine weak columns to
   a shipped ensemble barely moves its dot field: 97.9% of vario_full dots
   lie within 3 px of FAULTNET netctx dots (binary ρ = 0.891), and
   vario_nctx is 88.0% within 3 px of COULOMBLOQO-standalone. Under
   protocol rule 1 (>70% within 3 px of one registry raster ⇒ duplicate
   lane), E1 is a near-duplicate of an existing GEMSDOE92 artifact,
   independent of the separate literal dense-surface disclosure. The
   files are byte-unique (new SHA-256) but not registry-unique; renaming
   them would not change that.
5. **SGMC PROXY agrees** (62,703 off-catalogue USGS SGMC pixels):
   vario_full 0.0752, vario_smooth 0.0628, vario_nctx 0.0869 — all below
   R0 0.0961 and H19-5 0.1006. Three instruments, one conclusion.

**Verdict: negative** (pre-registered rule: format PASS and canary PASS,
but holdout-beats-best-control FAIL and operative-uniqueness FAIL).
Experiments used: 3/3. Weekly slots used: 0. The primary TIFF
(`gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif`,
SHA-256 `11f92e382b04a2f368c2259d6b092248efe338dd9a81436de4f27217c3b44573`)
passes every automated format gate (finite [0,1], no NaN in footprint,
zeros outside, exact CRS/shape/transform — the exact checks behind the
portal "Predicted values must be in range [0, 1]" error) and is
**OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.** See the
[executive submission guide](vario.html) for the (future-artifact)
submission procedure, unique name and 140-char note.

## 3. Limitations and next steps (for the selector / next session)

* The holdout is a biased surrogate for expert-mapped hidden faults
  (Section 1.3); a negative here does not prove a live negative, and a
  positive would not have proved a live win. It is used, per protocol,
  only as a slot-spending gate. No live score is projected anywhere.
* The league-leading gap (0.4413 vs the H19-5 family's ~0.28 CLAIM) most
  plausibly comes from data this sandbox cannot fetch: the competition's
  1 m DEM links (USGS 3DEP, public domain; non-GitHub hosts blocked
  here). Restoring a 1 m-derived sub-pixel scarp stack through a
  SHA-pinned GitHub mirror — as was done for the 10 m stack — is the
  highest-value next data step, then re-running the Rank-2 texture-
  registration or a 1 m crest/toe dipole operator from
  [HYPOTHESES_20261025_VARIO.md](HYPOTHESES_20261025_VARIO.md).
* Any future ensemble-expansion lane must change the *emission* materially
  (different crest/spacing/budget allocation), not just add features, or
  it will again fail the 70%/3 px uniqueness gate against its parent
  architecture's shipped dots (measured here: overlap 0.98).
* An emission-matched `vario_far` (d>4) arm was not run: it would have
  been a 4th experiment, over budget, and the far bar's advantage is
  partly a buffered-draw artifact (Section 2, reading 2). If tested, it
  must be pre-registered as its own session with the identical paired
  controls.
* Still missing for any future promotion: an organizer receipt tied to an
  exact SHA-256, the current weekly cap from the submission page, and a
  full public-repo registry scan (this session measured the 94 local +
  5 pinned lineage rasters actually present; scope is stated in the run
  card). GitHub Pages remains in legacy mode (workflow-mode PUT returned
  HTTP 403 in prior reviews; not re-tested here).

Official sources for manual review (fetched or listed 2026-10-25):
[competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) ·
[problem/metric/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) ·
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
[INGENIOUS](https://gbcge.org/current-projects/ingenious/) ·
[GDR #1391](https://gdr.openei.org/submissions/1391) ·
[EPSG:32611](https://epsg.io/32611) ·
[Tversky index](https://en.wikipedia.org/wiki/Tversky_index) ·
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) (not fetchable from this sandbox; listed, contents not re-verified).
