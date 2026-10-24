# Hypotheses — 2026-10-24 STEPEDGE session (ranked BEFORE any screening/building)

Protocol: 3–5 previously untried geological hypotheses; each names layer(s),
physical signature, why it should catch a fault missing from the USGS/INGENIOUS
catalogue, and how it differs from everything already built in this repo
(MASS, PRUNE, SNAP, CONCENTRATION, RELIEF, DILATATION, TIPGAP, STEPOVER,
BREAKLINE, SCARPPOL, ANASIG, STRAINBREAK, GRAVCrest-screened, VISIBLE-COLLAR).
Ranked by expected HOLDOUT-DTI gain per implementation cost. Budget: **3 built
experiments** (this session plans 2 doses of one lane). No slot is spent here;
promotion is an automated-gate verdict for a separate selector step.

Band semantics are read from the pinned `training_features.tif` itself
(SHA-256 `4371c82e…`, restored + verified this session; 19 bands, EPSG:32611,
3730×3292): 1 `mag_anom`, 3 `tmi_hg`, 4 `geod_2ndinv`, 9 `tmi_vg`, 12
`det_elev`, 14 `tmi`, 19 `det_elev_slope`. The radiometric stack is the pinned
external `geodawn_rad_u8.tif` (4 uint8 bands K/Th/U/TC, same grid; free
official source USGS GeoDAWN, DOI https://doi.org/10.5066/P93LGLVQ, US public
domain; obtainability already satisfied — it is in `registry/session_manifest.json`
and was restored + SHA-256-verified this session). Ranks 1–2 need no new data.

Why every lane emits **>3 px off the whole H19-5 skeleton, >2 px off the
catalogue, fixed 37,654-dot budget**: dots inside the skeleton are behavioural
near-duplicates of the worm family, and the owner’s CLAIM climb
(0.1922 → 0.2778, `evidence/r0_forensics_20261024.json`) is fully explained by
emission geometry on a *fixed* skeleton (NN spacing 1.0 → 3.0 px = kernel
radius; catalogue-adjacent mass 14.3% → 0%; footprint within-3px coverage only
19.6% → 15.1% while dots fell 69%). Beating CLAIM 0.2778 live therefore
requires *new skeleton content*, not more thinning — content the expert
labelers (manual mapping, DrivenData #306 p.967) could see but the
multi-line-corroborated potential-field worms and the Qfaults catalogue missed.

## 1. STEPEDGE — oriented sustained elevation step (TOP: screen, then build)

- **Layers:** Band 12 `det_elev` only (surface); Band 19 used solely to
  recompute the BREAKLINE control.
- **Signature:** at each pixel, the structure tensor of `det_elev` gives the
  dominant gradient direction **u** (across the local lineament) and coherence.
  Sample detrended elevation either side along **u** (bilinear) at two
  aperture groups, ±(2,3) px and ±(4,6) px, and take the *minimum* of the two
  two-sided offsets (**aperture persistence**: a channel wall is a step at
  short aperture only; a fault throw sustains — pinned by
  `tests/test_stepedge.py` synthetic step 5.4/6.0/5.4 m vs channel
  3.3/1.3/1.3 m near/far/min). Surface `S = pct_rank(step) × coherence`,
  `S_pct = pct_rank(S)`. The screen also scores the near-aperture-only
  variant so the persistence choice is measured, not assumed.
- **Why catalogue-missing:** a fault offsetting alluvium against itself (or the
  same bedrock unit) carries a sustained topographic *throw* with no magnetic
  or gravity contrast — invisible to H19-5 worms and to ANASIG/BREAKLINE-era
  potential fields, and easily missed by photo-era Qfaults mapping when the
  scarp is a few metres high — but a sustained cross-line offset is precisely
  what DEM-based expert mapping traces.
- **Difference from repo:** BREAKLINE uses the isotropic *derivative magnitude*
  `‖∇ det_elev_slope‖`, which fires identically on both banks of a channel,
  both sides of a ridge crest, and any rough texture. SCARPPOL projects that
  derivative onto the fall line but remains a local derivative (and measured as
  a BREAKLINE duplicate, forward overlap 0.900–0.913). STEPEDGE integrates the
  **sustained offset across** the line over a 400–600 m aperture: a V-channel
  and an inverted-V ridge cancel (high ≈ high on both sides), a true scarp
  step does not. No built lane in this repo has used a two-sided aperture step.
- **Named non-fault mimic:** Lake Lahontan wave-cut benches are also sustained
  steps; so are alluvial-fan segment boundaries, fluvial terrace edges, and
  bedding-controlled cuestas. STEPEDGE cannot separate a shoreline bench from
  a scarp on step alone — recorded here so a live falsification is attributable.
- **Cost / risk:** low (one band, no catalogue contact → no holdout leakage
  path). Main risk is lane collapse into BREAKLINE (screen measures far-set
  overlap; >0.70 forward overlap vs BREAKLINE f45’s far dots = duplicate stop).
- **Falsifier:** screened far-set SGMC DTI below 0.5× the BREAKLINE-L baseline
  (0.072325), or leakage-canary symmetric AUC > 0.90, or far-set overlap > 0.70
  with an existing lane’s far dots.

## 2. TRANSV — drainage-transverse breakline (screen only unless STEPEDGE dies)

- **Layers:** Bands 12/19 via the BREAKLINE `L` field.
- **Signature:** `L_raw × (0.2 + 0.8·|sin(θ_line − θ_regional-gradient)|)`,
  θ from `det_elev` gradients smoothed at σ=8 px. Drainage banks run
  *parallel* to regional downslope; range-front and cross-cutting fault scarps
  run transverse/contour-parallel. Multiplies the named BREAKLINE mimic
  (incised drainages) down by construction.
- **Difference:** no prior lane used line-vs-flow orientation. **Mimic:**
  shoreline benches are also contour-parallel (not rejected); roads along
  contours. Rank 2: cheap, but is an `L`-derived sharpening — highest duplicate
  risk vs BREAKLINE, so it is screened for the record and built only if
  STEPEDGE is falsified *and* TRANSV far-set overlap vs BREAKLINE f45 ≤ 0.70.

## 3. RADSTEP — radiometric concordance of the elevation step (screen only)

- **Layers:** Band 12 step (rank 1) × GeoDAWN radiometrics K/Th/U/TC edges.
- **Signature:** `sqrt(step_pct × max-band radiometric-edge_pct) × coherence`.
  A fault juxtaposing lithologies or carrying K-metasomatic alteration should
  be a step in *two independent physics* (topography + radioelement flux);
  shorelines and fans are steps in topography alone.
- **Difference:** RAD alone screened at AUC ≈ 0.50 in an earlier session and
  GEMSDOE46 fused radiometrics with a different scarp detector (CLAIM 0.1589);
  the *step-aperture concordance* is unbuilt here. **Mimic:** lithologic
  contacts with relief (faulted or not) fire in both channels.
- Rank 3: uint8 stretch semantics of the pinned rad stack are unverified
  (rank-based use only), and two-channel concordance halves the candidate pool;
  screened, built only if it beats rank 1 on the pre-registered screen rule.

## 4. Held / not viable this session

- **Catalogue tip-propagation gated by strain:** catalogue-derived, so an
  honest holdout must rebuild tips per fold from visible faults only; TIPGAP/
  STEPOVER already spent the simple geometric forms. Deferred, not proposed as
  viable without that fold-aware rebuild.
- **1 m DEM (lidar) scarp segmentation:** the label-generation instrument
  itself (organizer-supplied `1m_DEM_links.csv`), almost certainly how the
  0.4413 leaderboard leader differs — but the CSV is behind DrivenData login,
  unrestorable from this sandbox (outbound hosts limited to github/npm/pypi).
  Named as the highest-value *access* limitation, not proposed as viable here.

## Pre-registered screen → build rule (identical instruments to prior sessions)

Screen each surface on: (a) single-feature symmetric-AUC leakage canary vs
withheld catalogue positives (folds seeds 20/30, `gems57` buffered-component
draw; stop > 0.90); (b) a 16,944-dot spaced top-set (2.8 px floor, >3 px off
H19-5, d_cat > 2 px) scored alone as PROXY on off-catalogue USGS SGMC bedrock
faults (62,703 px) and on the fixed catalogue diagnostic; (c) far-set forward
overlap vs BREAKLINE-f45 / ANASIG-f45 / STRAINBREAK-f60 far dots. The harness
must first reproduce the BREAKLINE-L baseline (sym AUC 0.621604, far SGMC
0.072325) before any new number is trusted. **Build** the best non-baseline
surface by far-SGMC that passes (a) and (c), at doses f33 and f45 (2 of 3
budgeted experiments), keep-set by the shared exact expected-DTI greedy under
the new surface. **Evaluate** pooled HOLDOUT-DTI (`gems57-pooled-hide-v2`,
22,663 withheld px) vs R0 (0.004006), BREAKLINE f45 (0.004861), ANASIG f45
(0.004967), STRAINBREAK f60 (0.005487, best *locally unique*) and RELIEF p10
(0.006045, holdout best but an R0-skeleton duplicate). **Promote (verdict
promote) only if** the primary beats STRAINBREAK f60, its paired Δ vs R0 CI
excludes 0, full-file SGMC exceeds R0 (0.09606), leakage canary ≤ 0.90,
literal local uniqueness passes on pre-placement surface *and* final dots, and
all 10 format MUST gates pass on disk re-read. Otherwise verdict **negative**:
the TIFF is still generated, format-valid and downloadable, and the site must
say DO NOT SUBMIT. Projections are never written as scores; 0.2778 / 0.3195 /
0.4413 are CLAIM/snapshot numbers with no organizer receipt in this repo.

## Uniqueness policy (explicit resolution of the dense-witness blocker)

Prior sessions measured 100% forward overlap of *every* in-footprint candidate
against the 17GEMSDOE `E-proba` raster, which is **positive on 100% of the
footprint** (5,167,373/5,167,373 px). The protocol rule speaks of a registry
raster’s **dots**; a everywhere-positive continuous surface has no dot support,
so “fraction of my dots within 3 px of its dots” is degenerate (identically 1
for any non-empty submission — including the organizer’s own sample). This
session resolves the policy explicitly rather than silently:
forward/reverse dot-overlap gates apply to **dot-like registry rasters**
(positive support ≤ 150,000 px, the threshold already used for the sparse-only
diagnostic in the STRAINBREAK session); **rank-correlation |ρ| ≤ 0.90 applies
to every registry raster including dense surfaces**; the literal overlap vs
the dense witness is still measured and printed (expected 1.000) labelled
REGISTRY-MEASUREMENT, never hidden. Vendor `gems57/uniqueness.py` is not
forked: its `dot_overlap` measurement is reused; the dot-like scope is a
documented registry-scope decision in this session’s audit, and both verdicts
(literal-vendor and amended-scope) are reported side by side.

## Amendment (recorded BEFORE building experiment 3, same session)

Screen + first two builds measured: STEPRAW f33/f45 are SGMC-strong
(f45 full-file 0.127434, the highest SGMC of any arm ever scored here) but
(a) pooled HOLDOUT-DTI 0.004330/0.004228 — paired Δ vs R0 CIs include 0, below
BREAKLINE/STRAINBREAK/RELIEF, so the promotion bar already fails; and
(b) literal final-dot uniqueness fails *against same-dose siblings*
(f45: 0.711 vs BREAKLINE f45) even though far sets are 57% disjoint and the
surface is clean (worst sampled |ρ| 0.138). Mechanism: at equal dose, two
different greedy keep-subsets of R0 tile the same skeleton at ~2.8 px
spacing, so most kept dots lie within 3 px of a sibling's kept dot.

Experiment 3 (last budgeted build) therefore tests the STRAINBREAK-proven
uniqueness repair at the same surface: dose f60 (keep 15,062) with far dots
also >3 px off BREAKLINE-f45 and SCARPPOL-f45 far dots. Promotion bar is
UNCHANGED (beat STRAINBREAK f60 HOLDOUT-DTI 0.005487 etc.); the expected
value of this build is a *literal-unique* format-valid candidate, whatever
the verdict. If f60 also fails literal uniqueness, the lane is logged
duplicate and stopped.
