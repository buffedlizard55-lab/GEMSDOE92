# FLEXMAG analysis — why the GEMSDOE32 file is (claimed) best, and whether a blind-fault flexure detector beats it

Session 2026-10-25 · lane `FLEXMAG` · 3/3 experiments · 0 weekly slots ·
run card [`downloads/flexmag_run_card.json`](downloads/flexmag_run_card.json) ·
pre-registration [`HYPOTHESES_20261025_FLEXMAG.md`](HYPOTHESES_20261025_FLEXMAG.md)

> **✅ OK TO DOWNLOAD FOR RESEARCH · ⛔ DO NOT SUBMIT** (`verdict: negative`,
> `submission_eligible: false`). Primary file:
> [`gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.tif`](downloads/gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.tif)
> · [one-TIFF ZIP](downloads/gemsdoe92-flexmag-20261025T165411Z-flexmag-37654-zeros.zip)
> · SHA-256 `8190e1d07b059f8e6d1c869914a8786dfcbcb2771466f4c3874b60d1668c7261`
> · name `GEMSDOE92-FLEXMAG-flexmag-20261025`
> · note (94/140): `FLEXMAG flexmag: 37654 dots; blind-fault flexure hinge x magnetic ASA; HOLDOUT-DTI in run card`

Every number below carries its evidence class. Nothing here is an
ORGANIZER-CONFIRMED score; no organizer receipt exists in `ledger/` for any
file discussed.

---

## 1. Why / how did `h33-h33-2-b2` get "0.2778"? — what is verifiable, line by line

### 1a. The score itself is a CLAIM, and its own source page currently contradicts it
Fetched this session (2026-10-25) from
<https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html>: the page
labels the file **"UNSCORED"**, states **"NO ORGANISER SCORE EXISTS for this
or any artifact in this repository"**, and calls `0.2747` a *projection*
("a MODEL, not a score"). The brief's `0.2778`, the brief's leaderboard
figures `0.3195` / `0.4413`, and every other site value in
`ledger/site_scores_claimed_20261025.csv` therefore remain **CLAIM**s. A
causal explanation of an unverified number cannot be asserted; what follows
is (i) the byte-verified construction of the file and (ii) the metric
algebra that makes the claimed *ordering* of the lineage plausible.

### 1b. Byte-verified lineage (recomputed this session from files in this repo)
| Stage | File (this repo) | Positive px | CLAIM |
|---|---|---:|---:|
| H19-5 | `data/bridge/h19_5.tif` (sha `ec1f9b56…`) | 121,131 | 0.1922 |
| D2.8 (Poisson-thinned H19-5) | `data/bridge/d28.tif` (sha `91eae1ca…`) | 44,090 | 0.2600 |
| SOLO | `data/bridge/h27_4_solo.tif` (sha `ab023001…`) | 40,199 | 0.2708 |
| **R0 = h33-2-b2** | `data/parent_R0_zeros.tif` (sha `c55bafc4…`) | **37,654** | 0.2778 |

Exact identities, recomputed 2026-10-25: `XOR(SOLO, D2.8 ∧ d_cat>1px) = 0`
and `XOR(R0, D2.8 ∧ d_cat>2px) = 0`; `R0 ⊂ D2.8 ⊂ H19-5`; R0 keeps 2,171 dots
at `2<d_cat≤3px` and 35,483 beyond 3 px; nearest-neighbour spacing floor
2.828 px in D2.8/R0 (median 3.0 px). So the "winning" recipe contains **no
new detection** after H19-5: it is H19-5's geometry, thinned to a dotted
skeleton at the kernel scale, then stripped of every dot within 200 m of a
mapped fault.

### 1c. Why that raises a distance-weighted Tversky score (metric algebra)
With `DTI = TP_w / (TP_w + 0.2·FP_w + 0.8·FN_w)` and a 300 m triangular
kernel (`vendor/gems57/metric.py`, α=0.2, β=0.8), adding one binary dot
helps iff its marginal truth credit exceeds `α·DTI·(dT + 1 − k_self)`;
for a non-redundant dot this is the bar `k > α·DTI ≈ 0.052` at DTI≈0.26
(GEMSDOE32's page derives the same 0.0520 and reports an empirical 0.0548).
Dense H19-5 ribbons violate the bar twice: (i) dots closer than the kernel
diameter mostly re-cover already-credited truth (`dT ≪ k_self`) while still
paying FP mass `1−k_self`; (ii) dots 0–2 px from a *mapped* fault sit where
the hidden ("new") truth almost by definition is not, so `k_self≈0` against
scored truth — pure FP. Each lineage step (121,131→44,090→40,199→37,654)
removes exactly those negative-marginal dots, which is sufficient to explain
the claimed monotone ladder 0.1922→0.2600→0.2708→0.2778 **if** the claims are
real. Conversely it shows the ceiling of the recipe: after pruning, mean
credit per dot is fixed by H19-5's geometry; beating it requires a surface
whose *top-ranked* cells carry more realised kernel credit (GEMSDOE32's page
estimates ≈25 % more mean credit/pixel to reach a 0.3262-class leader).

**Can a submission score higher than 0.2778?** In principle yes — via a
detector with higher credit density at matched budget, or emission matched
to how hidden truth scatters around a surface. No file in this repository
has demonstrated that on an organizer receipt, and §2 shows FLEXMAG does not
do it on the local hide-and-recover instrument either.

## 2. FLEXMAG result (this session, pre-registered)

Hypothesis: blind normal faults (tip not breached, hence absent from the
scarp-mapped USGS/INGENIOUS catalogue) express as a mesoscale forced-fold
hinge in B15 `depth_to_base_surf`/B12 `det_elev` (DoG band-pass σ 6–30 px)
co-located with a TMI analytic-signal edge (√(B3²+B9²)). Named mimic:
sedimentary onlap/paleo-valley margins (hinge, no magnetic edge) and dikes
(magnetic edge, no hinge). Surface is catalogue-free; emission is the
lineage rule (37,654 dots, ≥2.8 px, `d_cat>2px`) so only the surface varies.

**HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, 8 folds,
per-draw re-placement with fold-visible clearance; 1,000-draw paired 20-km
block bootstrap):

| Arm | HOLDOUT-DTI [95 % CI] | Paired Δ vs flexmag [95 % CI] |
|---|---:|---:|
| **flexmag** (exp 1) | 0.045554 [0.035846, 0.056751] | — |
| flex (exp 2, no mag gate) | 0.048980 [0.038489, 0.060816] | −0.003426 [−0.013280, +0.005275] |
| mag (exp 3, no flexure) | 0.045107 [0.035493, 0.054613] | +0.000448 [−0.008929, +0.011291] |
| gravquad control (existing lane, re-placed) | 0.043184 [0.033832, 0.051418] | +0.002370 [−0.012741, +0.017602] |

Pre-registered bar 0.113316 (COULOMB-LOQO repo-recorded draw-blind record):
**not met** (flexmag is at 40 % of the bar; every paired CI includes 0, so
even the magnetic concordance gate's contribution is indistinguishable from
zero on this instrument, with the point estimate against it). Static
diagnostic (biased-down, full-catalogue clearance): flexmag 0.006026
[0.004583, 0.007490], flex 0.006891, mag 0.006113, R0 control 0.004006
(reproduces the repo-recorded R0 static value exactly — a cross-check that
the shared evaluator was used as in prior sessions). SGMC off-catalogue
**PROXY** (79,615 px; not a score): flex 0.087161 > flexmag 0.068910 > mag
0.057397 — same ordering, so the gate's penalty is not an artefact of one
instrument. Leakage canaries: max symmetric AUC 0.566271 (hinge; limit
0.90) across 14 components — no leakage signature. Per-fold, both NE folds
collapse (0.011296, 0.007639), the same province weakness recorded for prior
lanes.

**Uniqueness (REGISTRY-MEASUREMENT, local registry: 98 unique-mask rasters).**
Surface, before placement: worst |Spearman ρ| = 0.0658 (flexmag vs H19-5).
Final dots: flexmag worst forward 3-px overlap 0.5567, flex 0.5682 (both vs
the 90k LISTRICLAG raster), **mag 0.7223 > 0.70 vs ANASIG** — i.e. magnetic
ASA alone *is* the existing ANASIG lane, and the flexure concordance is what
moves the candidate into unique territory locally. The 102-repo public scan
was **not** rerun (verdict already negative on holdout), and the
literal-reading dense-witness stop recorded in `IRREGULARITIES.md` is
unaffected by these local numbers.

**Format (automated, no human inspection).** All three TIFs: single-band
float32, EPSG:32611, 3730×3292, transform `(100, 0, 243350, 0, −100,
4508550)`, `nodata=None`, every cell finite in [0, 1], 0 NaN, 0 dots outside
the footprint or on the catalogue, min catalogue distance √5 px, min
nearest-neighbour 2.828 px — re-verified from disk independently of the
builder. This is the encoding that avoids the portal error
*"Predicted values must be in range [0, 1]"* (no −3.4e38/NaN sentinel; see
[executive summary](executive-summary.html)).

### Limitations that bound the conclusion
1. The holdout's truth is withheld *catalogue* (scarp-mapped) faults; it
   cannot directly reward the blind class FLEXMAG targets. The SGMC proxy
   (independent compilation) agreeing in sign is the guard against excusing
   the result on that basis alone.
2. B15 `depth_to_base_surf` is itself a gravity-derived model surface, so a
   "basement hinge" partly re-expresses the gravity field rather than being
   independent evidence.
3. Edge erosion (32 px, to kill median-fill footprint-edge steps) makes
   4.3–5.1 % of withheld positives unreachable by construction — a real but
   small handicap; it cannot explain a 2.5× gap to the bar. Future lanes
   should inpaint/reflect-pad instead of eroding.
4. DoG scales (6/30 px) and the 0.30 gate floor were fixed pre-registration;
   no tuning was done (3-experiment budget respected).

## 3. What would actually raise P(Win) next
1. **Get one ORGANIZER-CONFIRMED receipt** (human selector step): every local
   ranking in this repo family is currently uncalibrated against the live
   metric, as §1a shows even the flagship 0.2778 is unverified at source.
2. Detector credit-density, not new emission rules: supervised LOQO surfaces
   (KNICKLOQO/COULOMB-LOQO class, repo-recorded draw-blind 0.109–0.113)
   remain ~2.4× this lane on the shared instrument.
3. If pursuing blind faults further, replace edge erosion with inpainting
   and test hinge evidence as *added LOQO features* only with a
   pre-registered overlap guard (LISTRIC v1 hit 0.763 vs KNICKLOQO = STOP).

## Sources (manual review)
- Competition & rules: <https://www.drivendata.org/competitions/306/competition-doe-gems/> · problem <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> · leaderboard <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> (not live-verified from sandbox)
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution> (fetched 2026-10-25; commit `aebe92f…`)
- GEMSDOE32 source page: <https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html> (fetched 2026-10-25; "UNSCORED / NO ORGANISER SCORE EXISTS")
- USGS GeoDAWN: <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> · DOE GDR #1391: <https://gdr.openei.org/submissions/1391> · INGENIOUS: <https://gbcge.org/current-projects/ingenious/> · EPSG:32611: <https://epsg.io/32611> · Tversky index: <https://en.wikipedia.org/wiki/Tversky_index>
- Input provenance: `registry/session_manifest.json` (12/12 SHA-256-verified restores this session, incl. 419 MB 19-band stack `4371c82e…`)
