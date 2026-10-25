# CURIE-DEMAG result and PhD scientific interpretation — GEMSDOE92 (2026-10-26)

## Decision (two questions answered without human inspection)

**✅ OK TO DOWNLOAD FOR RESEARCH: YES**
**⛔ OK TO SUBMIT TO A WEEKLY COMPETITION SLOT: NO**

The newly generated GeoTIFF `gemsdoe92-curiedemag-20261026T000000Z-zeros.tif`
is byte-unique (SHA-256 `a1d942f127e4f028a21180020078e6a6c79454aad875cbc9c495ec3075a15c70`),
passes every automated format/range gate, is locally unique, and beats the parent
R0 on the strict local holdout — but it does **not** beat the repository holdout
best and therefore must not consume a weekly slot. All numbers below are
`HOLDOUT-DTI` (local evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives)
or `REGISTRY-MEASUREMENT`; no `ORGANIZER-CONFIRMED` score is claimed. The
owner-reported `GEMSDOE32 0.2778` is a `CLAIM`, not a receipt.

---

## 1. Why `GEMSDOE32 h33-h33-2-b2` (`R0`, CLAIM 0.2778) led the listed GEMSDOE sites

### 1.1 Official metric geometry (verified)

Competition 306 defines a distance-weighted Tversky index (DTI) reviewed in the
official reference notebook:
https://github.com/drivendataorg/gems-prize-reference-solution (Cell 16)
and in local `vendor/gems57/metric.py`:

```
DTI = TP_w / (TP_w + α·FP_w + β·FN_w),  α=0.2, β=0.8
K(r) = max(0, 1 - r/300 m),  300 m = 3 px at 100 m
TP_w = sum_{truth pixel g} max_{prediction dot p} K(distance(p,g))
FP_w = sum_p  (1 - max_g K(distance(p,g)))  (covered prediction loses FP mass)
FN_w = N_truth - TP_w
Ω_eval = Ω \ C  (pixel-exact masking of known catalogue faults C)
```

Two consequences are load-bearing and were corrected in `gems/metric.py`
(`#IR-92-ALPHA-BETA-PROSE-SWAP` fixed an inverted α/β prose, `#IR-92-HYDROCONDUIT-EXTEND-TERMS`
fixed a spatial-block bootstrap `extend` bug — see `IRREGULARITIES.md`):

* **FN carries 4× the denominator weight of FP (β=0.8 vs α=0.2).** Missing a
  new fault is penalized four times more than a spurious dot. The `max` over
  truth pixels means a *second* dot near the same truth pixel is *redundant*
  for `TP_w` (its `K` is shadowed) and contributes only `FP_w` (α=0.2 per unit
  mass when uncovered). Removing a redundant dot thus saves `~0.2` denominator
  while losing `~0` numerator → DTI rises.
* **Kernel is pointwise max, not summed.** Overlapping 300 m halos do not
  double-count truth credit. This makes *regular* spacing near `2·R ≈ 6 px`
  (≈600 m between trails) and `≈2.83 px` (≈283 m) halo overlap geometry —
  the row-major Poisson thinning `2.8 px` used for `D2.8` — near-optimal for
  trading `TP_w` coverage against `FP_w` mass on a *sparse* skeleton.
  However, `spacing < 2.8 px does not imply zero marginal credit` — it depends
  on truth geometry. A nearby dot can still create `TP_w` on a *different*
  withheld or off-catalogue strand. The thinning is a plausible mechanism, not
  an optimal-spacing theorem (`tests/test_metric_properties.py` disproves the
  universal claim).

Trust verification: the 300 m kernel and α/β are from organizer refs; the
training-loss α/β cell in the reference notebook does **not** implement the
distance-weighted evaluator itself. Local `vendor/gems57/metric.py` is the
instrument used here; it is SHA-256-pinned and tested but not independently
certified as organizer code.

### 1.2 Exact byte-verified ancestor cascade of R0 (learning context, not proof)

Pixel algebra on the SHA-256-pinned rasters in `registry/session_manifest.json`
(`.cache/gems_inputs/` lineage) proves zero-XOR identities:

```
H19-5  (19GEMSDOE, 121,131 px, CLAIM 0.1922, binary {0,1} skeleton)
  → D2.8 (GEMSDOE25, 44,090 px, CLAIM 0.2600) Poisson-thinned at 2.83 px ≈300 m
  → SOLO (GEMSDOE28, 40,199 px, CLAIM 0.2708)  XOR(SOLO, D2.8 & d_cat>1.0)==0
       (−3,891 px at d_cat==1.0, #IR-92-SOLO-R1-BYTE-IDENTITY)
  → R0 / GEMSDOE32 h33-2-b2 (37,654 px, CLAIM 0.2778) XOR(R0, D2.8 & d_cat>2.0)==0
       (−2,545 px at 1.0<d_cat≤2.0, retaining 2,171 splay/tip dots at 2.0<d_cat≤3.0)
```

Each step is *catalogue-aware filtering on the same skeleton*, not new physics:

* `D2.8` applies Poisson spacing `≈R` → removes redundant halo mass.
* `SOLO` masks `d_cat≤1.0` → avoids wasting budget on catalogue pixels.
* `R0` masks `1.0<d_cat≤2.0` → stricter catalogue clearance, keeping only
  far splay/tip halo dots (`d_cat>2.0`, min `2.236 px`). On `Ω_eval = Ω\C`,
  a dot within 2 px of a known fault is fully masked and contributes only `FP`
  (α=0.2) with `TP` shadowed — removing it is freeroll.

Thus the `0.1922→0.2600→0.2708→0.2778` climb is parsimoniously explained by
*budget reallocation on a fixed skeleton at kernel-optimal spacing* plus
*catalogue clearance*, not by blind-fault discovery. The cascade uses **100%
H19-5 input** (`pct_changed` vs R0 = `100%` for H19-5, `0%` for R0 lineage),
so its score plausibly inherits whatever kernel-tuned skeleton underlies
`H19-5` (worm/H19 manual skeleton). Whether that skeleton already encodes
undisclosed geothermal truth is unattested.

### 1.3 Why R0 left headroom to 0.3195 / 0.4413 `CLAIM` snapshots

* **Row-major vs greedy spacing.** `D2.8` thinning is row-major scan order,
  not exact marginal-DTI greedy. A greedy refill on the same H19-5 support
  (rank by expected marginal `TP_w − α·FP_w` at 300 m) could further raise
  `TP_w` per dot. Early `GEMSDOE92` `PRUNE`/`SNAP` sessions explored this
  (`+0.001` to `+0.008 MODEL`) but on the same support.
* **100% skeleton confinement.** R0 never leaves `H19-5`. A blind fault
  off-skeleton (buried under playa, diffused scarp, Riedel relay) cannot be
  covered. The *off-skeleton fraction* is the geothermal headroom. Later
  `GEMSDOE92` lanes moved `45–60%` off-skeleton (`HYDROCONDUIT f45hydro`
  `55%`, `COULOMBLOQO standalone` `0%` but trained off-skeleton via LOQO,
  `KNICKLOQO standalone` `0%` skeleton but `60%` far splay, `PROVINCETOE`
  `35%`, `POISSONKNICK pkdual40` `60%`).
* **Conflicting leaderboard snapshots.** The brief supplies `0.3195` (prompt)
  and `0.4413` (#1) as `CLAIM` snapshots at different dates. Neither is
  `ORGANIZER-CONFIRMED` here (no `ledger/submissions.csv` receipt). Local
  holdout recovery of withheld mapped catalogue segments (`0.004006` R0 static)
  is **not** organizer score; it rewards catalogue-proximal structure and is
  masked by `Ω_eval`. Off-catalogue `USGS SGMC` bedrock-fault control
  (`62,703` px, `d_cat>3.0`) is the report-only proxy for blind faults.
  A local holdout win does not guarantee a leaderboard win — the private
  Phase-2 truth is undisclosed and may be dominated by blind playa/basin
  faults invisible to scarp-based skeletons.

**Can we beat 0.2778 `CLAIM`?** In principle, yes: any lane that moves mass
off-skeleton onto catalogue-missing but truth-positive basement/magnetic/
hydrothermal structure at `>300 m` from known faults, at ≥2.8 px spacing and
in `[0,1]` float32 zeros-outside encoding, *could* score higher if Phase-2
truth rewards that physics. No local instrument *proves* it — a better
`HOLDOUT-DTI` is a necessary but not sufficient screen. The history shows
off-skeleton `LOQO` lanes beating R0 on local holdout (`COULOMBLOQO`
`0.009220` static, `0.113316` Rule-2; `KNICKLOQO` `0.010788` static,
`0.109043` Rule-2), but their dense-witness literal `overlap=1.0` and
`EULERFUSE` collisions (`0.8287` overlap vs `COULOMBLOQO`) kept `verdict:
negative`. Beating `0.2778` `CLAIM` requires both a local win *and* a
non-duplicate that survives private truth.

---

## 2. CURIE-DEMAG hypothesis and mechanism

**Hypothesis (pre-registered `docs/HYPOTHESES_20261026_CURIEDEMAG.md` Rank 1):**
The USGS/INGENIOUS catalogue is a Quaternary scarp catalogue; blind
basement faults that channel geothermal fluids have no preserved surface
rupture but create a hydrothermal alteration halo: titanomagnetite→pyrite
destruction above a conductive smectite clay cap (180–250 °C) yields a
*multi-scale magnetic quiet trough* (suppressed 300 m-scale RTP variance
inside a volcanic terrain) bounded laterally by *steep MT resistivity
flanks* (`‖∇log(B17+1)‖`). These halos mark where a fault has been
permeable, not just where it slipped, and are invisible to topography/
scarp detectors.

**Mechanism (pure array math, catalogue never builds the surface):**

```
var3  = local variance of B2 RTP in 3×3 window  (300 m)
var15 = local variance of B2 RTP in 15×15 window (1500 m)
R     = var3 / (var15 + ε) ,  suppression = 1 - clip(R,0,1)
mt_grad = |grad(log(B17 cond_surf + 1))|      clay-cap flank
demag   = max(0, Laplacian(B2 RTP))           demag bowl

S(x) = pct_rank(suppression) · pct_rank(mt_grad) · pct_rank(demag)
```

All ranks are percentile ranks over the 5,164,312 valid footprint cells
(`training_features.tif` bands 2/14/17, SHA-256 `4371c82e…`). The 2,171
`splay/tip` R0 dots retained at `2.0<d_cat≤3.0` are *not* privileged; the
candidate places **0% H19-5** mass (full 37,654 off-skeleton is allowed but
the surface itself is catalogue-free). Placement is `spaced_top_mask(S,
candidate = valid & ~catalogue & d_cat>2.0, k=37,654, min_dist=2.8 px)` —
identical spacing/clearance to R0, deterministic, no training labels.

**Why it catches catalogue-missing faults:** A concealed relay under
10–100 m of Arroyo/alluvium has no `det_elev` step (`BREAKLINE`/`SCARPPOL`
`/STEPEDGE`/`STRAINBREAK` miss it), no TMI edge (`ANASIG` misses it), and
no gravity scarp (`HYDROCONDUIT f45hydro` misses it if the basement step
is subtle), but the overlying alteration halo remains: magnetic quiet +
MT-high clay cap is a direct geothermal discriminant, not a scarp proxy.
Examples: Dixie Valley, Brady, Beowawe blind geothermal systems sit on
magnetic quiet troughs inside MT conductors (Faulds et al. 2021a;
Wannamaker et al. 2020).

**How it differs from repo implementations:**
No prior lane computes a *multi-scale RTP variance-suppression ratio*.
`COULOMBLOQO` used pointwise `max(0,∇²RTP)` as 1 of 24 classifier inputs;
`EULERFUSE` solved Euler deconvolution depth; `POISSONKNICK`/`KNICKLOQO`
used Poisson `∇RTP·∇g` collinearity, not variance ratio; `HYDROCONDUIT`
/`COULOMBDM` used first-order `‖∇B17‖` as a scarp boost; `ANASIG` used
analytic-signal amplitude; `RADIOCONTACT` used radiometric `U/K·Th/K`
contacts × gravity-gradient. CURIE-DEMAG is the first
*magnetic-quiet-inside-clay-cap* lane.

**Named non-fault mimic:** Thick non-magnetic Lahontan lacustrine basin
clays, unaltered basaltic cover, survey levelling artifacts, basalt flow
edges that also give `∇B17` and suppressed RTP variance. The flank
`mt_grad` mitigates thick-cover mimic (uniform lacustrine fill has low
`|∇log B17|`), but facies-change `B17` without faulting remains FP.

**GDR corroboration (diagnostic only):** 419 blind `≥80 °C` silica/cation
geothermometer cells from `gdr_wellspring_in_footprint.csv` (CC BY 4.0,
`122718e…`) were not used to build `S`; `dist_geotherm` symmetric AUC
is reported as a leakage check. Using them as a feature would be
catalogue-independent but spatially biased (well locations follow roads).

---

## 3. Results

### 3.1 Strict hide-and-recover HOLDOUT-DTI

Evaluator `gems57-pooled-hide-v2` (α=0.2, β=0.8, 300 m triangular `max` kernel),
8 buffered spatial-quadrant folds (seeds 20+30, 1.2 km guard, 500 m negative
buffer), whole-component withholding, pooled DTI + 1,000 paired 20 km spatial-
block bootstrap CI, 22,663 withheld positives. Each fold rebuilds its 37,654
dots from *only its visible-fault exclusion mask* (`d_visible>2.0`), so the
evaluation is not a static masked deployment raster.

| Arm | Strict Rule-2 `d_visible>2.0` HOLDOUT-DTI | 95% CI | `tpw` | `fpw` | `fnw` |
|---|---|---|---|---|---|
| **CURIE-DEMAG** | **0.050806** | **[0.043211, 0.058556]** | 1,642.09 | 69,311.75 | 21,020.91 |
| R0 control | 0.004006 | [0.003362, 0.004648] | 129.30 | 70,592.12 | 22,533.70 |
| **Paired Δ vs R0** | **+0.046799** | **[+0.038864, +0.054476]** | — | — | — |
| Holdout best (`COULOMBLOQO standalone`) | 0.113316 | [0.100614, 0.127163] | — | — | — |

* `CURIE-DEMAG` beats R0 by **+1,168%** (`0.050806/0.004006`) with paired CI
  strictly >0. This is that lane's strict fold-visible rebuild, not the static
  `d_cat>2.0` deployment instrument. It is **not** an organizer score.
* It trails repo holdout-best `COULOMBLOQO standalone` `0.113316` by
  `-0.062510` (`-55.2%`) and trails `KNICKLOQO standalone` `0.109043` by
  `-0.058237`, `POISSONFLEX opt` `0.107466` by `-0.056660`,
  `PROVINCETOE provincetoe` `0.106452` by `-0.055646`. The CI vs holdout best
  excludes 0 in the negative direction → **did not beat holdout best**.
* Static deployment `d_cat>2.0` is not claimed for this fold-rebuilt
  instrument; the static analogue of R0 is `0.004006 [0.003408,0.004651]`
  and of `COULOMBLOQO` is `0.009220 [0.007983,0.010493]` (different instrument,
  not compared as one).
* Off-catalogue `USGS SGMC PROXY` (report-only, `62,703` px `d_cat>3.0`)
  was not pooled here; the strict instrument already excludes visible faults
  pixel-exactly. Prior simple scarps scored `SGMC 0.074–0.141`; LOQO lanes
  `0.089–0.121`.

### 3.2 Leakage canaries (symmetric AUC vs pooled withheld truth)

| Feature | Symmetric AUC |
|---|---|
| `suppression` (1−var3/var15) | **0.509554** |
| `mt_grad` (|grad log B17|) | **0.506525** |
| `demag` (max(0, Laplacian RTP)) | **0.511115** |
| `S` (product of ranks) | **0.501593** |

`max = 0.511115 ≤ 0.90` → **PASS** (`32/32` analogue would be 4/4 here).
All features are weakly predictive of withheld mapped catalogue segments,
as expected for catalogue-free physics. AUC near 0.5 does not imply the lane
is random on hidden truth; it implies no catalogue leakage through the surface.

### 3.3 Uniqueness (REGISTRY-MEASUREMENT)

**Local complete registry:**
`110` unique rasters (`docs/downloads/` + `releases/` + `data/bridge/` +
`data/parent_R0_*.tif`) checked on the exact grid `3730×3292, EPSG:32611`
with the same transform.

* Worst literal forward 3-px overlap `0.249562 ≤0.70` vs
  `local:docs/downloads/gemsdoe92-poissonflex-poissonflex_opt-45000-20261025-54255bcc-zeros.tif`
* Worst matched-budget forward 3-px overlap `0.249562 ≤0.70` (same file,
  `dot_field` representation, `37,654` vs `45,000` dots)
* Worst `|ρ|` `0.031668 ≤0.90` vs
  `local:docs/downloads/h33-h33-2-b2-KNICKLOQOuncal-20261025-61b98143-zeros.tif`

`duplicate = false`, `verdict = unique` on the binding literal rule
(`overlap>0.70` OR `|ρ|>0.90`). This is a *dot-field vs dot-field*
comparison; no continuous-surface `>150k`-px prior fired the dot threshold.

**Public registry:** Not scanned in this sandbox (GH CLI unauthenticated,
no cached inventory). Scope is stated as `available: false` and is **not**
claimed as proof of absence. Historical full scans (`1,400→1,415` exact-grid
rasters across 102 `buffedlizard55-lab` repos) show:

* `0 / 1,412` `≤150k`-px sparse public rasters `>0.70` for `KNICKLOQO`
  `standalone` (max `0.685531`), but `PROVINCETOE` `0.7918` vs
  `62GEMSDOE 125,890 px`, `POISSONFLEX opt` `0.7541` vs `62GEMSDOE
  ventcons` `125,890 px`, and `COULOMBLOQO standalone` `0.828703` vs
  `EULERFUSE_gravity` (`#IR-92-COULOMBLOQO-EULERFUSE-POSTMERGE-COLLISION`).
  `CURIE-DEMAG` shares only `24.96%` forward overlap with the closest local
  sparse `LOQO` raster, so a comparable public `≤0.70` is expected, but it
  is *not certified here* without a live 102-repo scan.
* Literal dense witness `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif`
  (`5,167,373` positive footprint cells = 100%, SHA-256 pinned) leaves
  `0` of `5,106,385` allowed cells uncovered (`halo_coverage=1.0` with
  `R=3.0` px), so *every* nonempty dot set has literal overlap `1.0`
  (`vendor/gems57/uniqueness.py::saturation_certificate`). Under the
  current literal binding rule, `submission_eligible` would stay `false`
  for *any* candidate until an operator policy exempts space-filling
  `>150k`-px continuous probability surfaces. The `matched-budget`
  diagnostic backstops it: on that prior the literal `1.0` is not evidence
  of duplication; it is reported for completeness (`#IR-92-DENSE-WITNESS-MATCHED-BUDGET`
  superseded by `376a8469` literal binding). `CURIE-DEMAG` card reports
  `dense_witness_specificity: null` and does **not** claim public uniqueness.

### 3.4 Validator (automated, zero human inspection)

`vendor/gems57/submission_writer.py` + `gems/gates.py` +
`vendor/gems57/validate.py` on independent disk re-read of the served
`-zeros.tif` bytes:

* Single-band `float32`, `3730×3292`, `EPSG:32611`,
  exact `sample_submission.tif` transform `100 0 243350 / 0 -100 4508550`
* All `12,279,160` cells finite, `min=0.0, max=1.0`, `mean=0.003066`
* `0 NaN`, `0 Inf`, `0` sentinel values anywhere
* `0.0` outside footprint (`outside_footprint_zero: true`), `0` dots on
  mapped catalogue (`zero_dots_on_mapped_catalogue: true`,
  `d_cat>2.0`, min `2.236 px`)
* `37,654` unit dots (`1.0` mass), `+2,171` R0 splay/tip dots not privileged
* `11/11` gating MUSTs `PASS`; `13/13` `gems57.validate` `PASS` — prevents
  DrivenData's `Predicted values must be in range [0, 1]` portal error.

SHA-256 (`-zeros.tif`): `a1d942f127e4f028a21180020078e6a6c79454aad875cbc9c495ec3075a15c70`
(`-zeros.zip`: `a9796a8636f6225703f8fd64eae067bd7dbf8f24499bdfeb9b3d0e01a0e76b80`,
  `gems57.submission_writer` DEFLATE-compressed, `nodata=None`).
Submission name (local record): `GEMSDOE92-CURIE-DEMAG-20261025` (max 140);
note (106/140): `h33-h33-2-b2; CURIE-DEMAG: RTP variance-suppression x MT
clay-cap flank x demag bowl; 37654 dots d_cat>2px`.

---

## 4. Why CURIE-DEMAG scored here and what falsifies it

**Why it beats R0 but trails LOQO on this holdout:**
Band-wise terrace: `suppression` alone `AUC 0.51` → weakly recovers withheld
segments, but the *conjunction* of quiet variance *and* MT flank *and* demag
bowl is rarer (~22% mean `S`) and more precise: `tpw` lifts to `1,642`
vs R0 `129` per pooled fold (~12.7×), while `fpw` drops modestly
(`69,312` vs `70,592`). The 8-fold pooled `d_visible>2.0` instrument
masks each fold's `visible` pixel-exactly, so a gain here means the surface
truly recovers *withheld* strands at `>2 px` off visible faults, not just
re-maps visible scarps. However, `0.0508` is `−0.0625` below the regularized
4-quadrant `LOQO` holdout best (`0.113316`). The gap is expected: regularized
gradient boosting with province-debiased quantile calibration (`KNICKLOQO`
`0.010788` static / `0.109043` Rule-2, `COULOMBLOQO` `0.009220` /
`0.113316`) optimally weights 24–30 spatial channels, whereas a hand-weighted
`S` product (equal rank cube) cannot. The `SGMC PROXY` control (not pooled
above) would likely favor `CURIE-DEMAG` over scarp-based `BREAKLINE`
`0.1261` vs `STEPEDGE`? unknown, but the strict instrument already proves
catalogue-free structure.

**Falsification:**
A live receipt `Δ ≤ −0.010` vs R0 would reject “magnetic quiet inside clay
caps predicts new faults”; it would mean Phase-2 truth is dominated by
inactive exhumed structures or non-alteration-controlled faults (e.g.,
Luning-Fencemaker thrust relics where contraction, not alteration, localizes).
`|Δ| < 0.01` is noise (public-chunk sampling). On the surrogate, a LOQO
ablation that drops `suppression` and lifts DTI would falsify the variance-
ratio channel.

---

## 5. Limitations and remaining work

1. **Single scale pair.** `var3/var15` fixed at `3/15 px` (`300 m`/`1500 m`).
   Hydrothermal alteration halos range `200 m`–`2 km`; a multi-scale `3/7/15`
   or `5/15/25` scale ensemble (cost +2 min) could raise recall on broader
   halos. Not run under the 3-experiment budget (1/3 used).
2. **Equal-rank product.** `S` uses equal weights (`pct³`). Learning the
   mixture (`w₁·suppression + w₂·mt_grad + w₃·demag` via `LOQO`) would likely
   push `Rule-2` toward `0.08–0.10`; this session kept catalogue-free
   determinism (no fitting on withheld folds) to avoid leakage.
3. **Public inventory not refreshed.** Local `110` rasters are complete; public
   `≈1,400` rasters are not re-scanned here (no GH auth, no cached index in
   this checkout after `restore_inputs --validation` subset). The local
   `0.2496` worst overlap suggests a public `≤0.70`, but it is not certified
   without `scripts/audit_public_registry.py` (requires `gh` auth + GitHub API
   quota, `102` repos). Run it before any selector claim.
4. **Dense-witness policy deadlock.** Under `376a8469` literal binding,
   `17GEMSDOE E-proba-multiscale` (`5,167,373` positive cells) forces
   `verdict: negative` + `submission_eligible: false` for *every* nonempty
   dot set. The card therefore stays `negative` even though the dot-field
   reading is `unique`. Operator clarification is required before any weekly
   slot.
5. **No outer spatial test.** Adaptive-selection risk remains: repeated local
   holdout tuning can inflate `HOLDOUT-DTI`. Retain a locked outer spatial
   test for the selector, never used to tune `S` or budgets.

Budget: `1/3` experiments, `0` weekly slots, `2 h` not exhausted. Rank 2–4
(`FLEXURE-HINGE`, `TENSOR-RIEDEL`, `SEIS-GRAV-LAG`) and held Rank 5
(`Landsat TIR` external) remain untried and documented for the next session.
Negative results are deliverables and must be preserved with the same rigour
as positive ones.

---

## 6. Reproducibility

```bash
python3 -m venv .venv && .venv/bin/pip install numpy==2.4.6 scipy==1.17.1 rasterio==1.4.4 pandas==3.1.0 pytest==9.1.1 "scikit-learn>=1.5,<2.0"
.venv/bin/python scripts/restore_inputs.py && .venv/bin/python scripts/verify_manifest.py
PYTHONPATH=vendor .venv/bin/python scripts/build_curie_demag_submission.py --stem gemsdoe92-curiedemag-20261026T000000Z
.venv/bin/python -m gems validate docs/downloads/gemsdoe92-curiedemag-20261026T000000Z-zeros.tif --reference .cache/gems_inputs/bridge/sample_submission.tif
PYTHON=.venv/bin/python make test && PYTHON=.venv/bin/python make site && PYTHON=.venv/bin/python make verify && PYTHON=.venv/bin/python make ledger
```

SHA-256s are byte-identical only on the pinned `registry/session_manifest.json`
(`training_features.tif` `4371c82e…`, `ext_geodawn_rad_u8` `c22420f7…`,
`gdr_wellspring_in_footprint.csv` `122718e…`). Provider formatting can place
tool results before arena blocks — do not echo tags.

```json
{
  "hypothesis": "Hydrothermal alteration (titanomagnetite destruction) inside MT clay caps creates a multi-scale magnetic quiet trough bounded by MT resistivity flanks — a blind-fault halo invisible to scarp detectors.",
  "mechanism": "S = pct_rank(1 - var_300m(RTP)/var_1500m(RTP)) * pct_rank(|grad log B17|) * pct_rank(max(0, laplacian RTP)); 37,654 spaced dots d_cat>2.0",
  "named_non_fault_process": "Thick non-magnetic lacustrine sediments, basalt cover, levelling artifacts",
  "holdout_dti": {"evaluator_version": "gems57-pooled-hide-v2", "withheld_positives": 22663, "value": 0.050806, "ci95": [0.043211, 0.058556]},
  "correlation_overlap_vs_registry": {"local_worst_literal_forward_overlap": 0.249562, "worst_abs_spearman": 0.031668, "duplicate": false},
  "raster_sha256": "a1d942f127e4f028a21180020078e6a6c79454aad875cbc9c495ec3075a15c70",
  "validator_output": {"no_nan_in_footprint": true, "values_in_0_1": true, "crs_shape_transform_match": true, "dots": 37654},
  "submission_name": "GEMSDOE92-CURIE-DEMAG-20261025",
  "submission_note": "h33-h33-2-b2; CURIE-DEMAG: RTP variance-suppression x MT clay-cap flank x demag bowl; 37654 dots d_cat>2px",
  "verdict": "negative"
}
```

**Evidence labels:** `HOLDOUT-DTI` = local buffered hide-and-recover (`gems57-pooled-hide-v2`, 8 folds, 22,663 withheld); `PROXY` = off-catalogue USGS SGMC control (not pooled, reported); `REGISTRY-MEASUREMENT` = verified overlap/correlation scan; `CLAIM` = unverified reported figure; `ORGANIZER-CONFIRMED` = copied from DrivenData receipt (0 recorded). Official sources: [Competition #306](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [Reference Solution](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR #1391](https://gdr.openei.org/submissions/1391), [EPSG:32611](https://epsg.io/32611), [Tversky](https://en.wikipedia.org/wiki/Tversky_index), [3DEP](https://www.usgs.gov/3d-elevation-program).
