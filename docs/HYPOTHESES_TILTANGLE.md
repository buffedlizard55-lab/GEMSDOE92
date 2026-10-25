# TILTANGLE — Pre-Registered Geological Hypotheses (Ranked)

Session: 2026-10-25 · Lane: TILTANGLE · Evaluator: gems57-pooled-hide-v2
Status: Top candidate (H1) built, format-validated, holdout-scored.
All labels: HOLDOUT-DTI (local surrogate, not an organizer score).

---

## H1 — Gravity tilt-angle edge corridors (BUILT — TILTANGLE)

**Layers:** B11 `iso_grav_anom_vg` (vertical gravity derivative), B13
`iso_grav_anom` (differentiated for N–S horizontal derivative), B18
`iso_grav_anom_hg` (signed E–W gravity horizontal derivative).

**Physical signature:** Gravity tilt angle θ = atan2(|∂z g|, |∇ₕ g|).
θ ≈ 0° over flat/bedding-parallel contacts; θ ≈ 90° over steep,
near-vertical contacts — the geometry of Basin-and-Range normal faults.
Edge strength = horizontal-gradient magnitude × cos(θ)², which up-weights
steep-contact edges of any strike and down-weights equant/blob anomalies.

**Why it catches catalogue-missing faults:** The USGS/INGENIOUS catalogue
is a surface-scarp catalogue. Blind normal faults buried under thin Quaternary
cover, or whose scarps have diffused below detection, still juxtapose rock
bodies of different density across a steep plane. That density contrast is
visible to gravity regardless of scarp preservation or fault strike. The
catalogue is used ONLY for masking (dots off-catalogue, >2 px from it); no
catalogue pixel enters the surface.

**Non-fault mimic:** Equant plutonic intrusions, circular playa/evaporite
density bodies, and diffuse basement-terrane boundaries produce horizontal
gradient magnitude but not steep (near-90°) tilt angles; cos(θ)² down-weights
them.

**Differs from existing lanes:** No lane computes a gravity tilt angle.
GRAVQUAD uses analytic-signal amplitude × structure-tensor coherence (dip-
blind, responds to any elongated gradient blob). COULOMB-LOQO assumes fixed
N15°E conjugate shear planes inside a supervised classifier. CURIE-DEMAG uses
RTP variance suppression × MT clay-cap flank × demag bowl. TILTANGLE explicitly
selects steep near-vertical contacts.

**Expected DTI improvement:** Moderate — physical edge detector, standalone,
no supervision. Expected to exceed R0 static (0.004006) and most standalone
physical lanes; below supervised LOQO Rule-2 (0.113316). Actual: **0.033466**
(static, 45,253 withheld positives, 8 LOQO folds).

**Implementation cost:** Low — pure array math on 3 bands, no sklearn, no
training. Built and validated in one experiment.

**Result:** ✅ Format-valid (11/11 gates). HOLDOUT-DTI 0.033466. Verdict:
negative (not slot-cleared under literal dense-witness registry stop).

---

## H2 — Curie-depth spectral window (NOT BUILT)

**Layers:** B2 `rtp` (reduced-to-pole magnetic anomaly); B13/B18 gravity for
tilt-angle cross-gate.

**Physical signature:** 2D FFT radial power spectrum of B2 → depth-to-magnetic-
bottom (Curie isotherm) estimate via spectral slope. Shallow Curie depth =
high heat flow = geothermal upflow. Intersect shallow-depth windows with
gravity tilt-angle edge corridors (H1) to locate blind faults hosting upflow.

**Why it catches catalogue-missing faults:** Curie depth is a subsurface,
heat-flow property; it requires no surface expression. Blind faults with no
scarp can still host shallow Curie-depth geothermal cells.

**Non-fault mimic:** Deep magnetic basement undulations unrelated to faults;
sedimentary basins with naturally shallow magnetic basement.

**Differs from existing lanes:** No lane uses spectral/Fourier depth estimation.
CURIE-DEMAG uses spatial-domain RTP variance suppression, not spectral depth.

**Expected DTI improvement:** High conceptual value (targets heat, not just
structure), but untested locally; spectral depth estimation on the pinned stack
is non-trivial and may not localize to individual faults.

**Implementation cost:** Medium — requires 2D FFT on 3730×3292, radial
averaging, depth-from-slope inversion, and cross-gating with tilt angles.

**Data availability:** B2 RTP is in the pinned training_features.tif (locally
restored). No external data needed. **Viable.**

---

## H3 — Detrended-elevation Laplacian curvature × gravity-gradient intersection (NOT BUILT)

**Layers:** B12 `det_elev` (detrended 3DEP elevation), B13 `iso_grav_anom`,
B18 `iso_grav_anom_hg`.

**Physical signature:** Laplacian (second derivative) of detrended elevation
enhances narrow scarp-like curvature features (fault scarps, faceted
spur-and-valley morphology) while suppressing broad regional topography.
Intersect with gravity-gradient magnitude (buried density contrast) to catch
faults with either topographic OR geophysical expression.

**Why it catches catalogue-missing faults:** The scarp catalogue misses faults
whose scarps have diffused below visual detection but still produce subtle
curvature; it also misses fully blind faults with no topography but a gravity
signature. The intersection captures both.

**Non-fault mimic:** Drainage incisions, alluvial fan toes, volcanic cones —
all produce curvature but lack the gravity-gradient correlation.

**Differs from existing lanes:** NEO-OPNS uses TPI × LoG × log-slope but not
the curvature × gravity-gradient intersection. No lane intersects topographic
curvature with gravity gradient as a dual gate.

**Expected DTI improvement:** Moderate. Topographic curvature should recover
scarps near catalogue faults; gravity gradient extends to blind strands.

**Implementation cost:** Low — np.gradient-based Laplacian + gradient magnitude,
both on pinned bands.

**Data availability:** All bands in pinned training_features.tif. **Viable.**

---

## H4 — Radiometric alteration index × magnetic suppression dual gate (NOT BUILT)

**Layers:** B1 `mag_anom`, B2 `rtp`, B6 `tc` (radiometric total count), plus
derived K/Th and U/Th ratios where separable.

**Physical signature:** Geothermal alteration (argillic → smectite clay) creates
radiometric potassium depletion and uranium/thorium fractionation, plus magnetic
demagnetization (titanomagnetite → pyrite). Dual gate: alteration index (low K/
Th, specific TC signature) AND magnetic suppression (low RTP variance).

**Why it catches catalogue-missing faults:** Alteration halos extend beyond
mapped fault traces and can be wider than the scarp itself. Blind faults hosting
alteration show no surface rupture but show the radiometric+magnetic signature.

**Non-fault mimic:** Lithologic variations (e.g., ash falls, paleosols) that
produce similar radiometric signatures without faulting.

**Differs from existing lanes:** CURIE-DEMAG uses RTP variance × MT clay-cap
flank × demag bowl but not radiometric K/Th/U ratios. COULOMB-LOQO includes
K/Th, U/Th as features inside a supervised classifier but never as a standalone
dual-gate emission surface.

**Expected DTI improvement:** Moderate-High; alteration is a direct geothermal
proxy, but radiometric bands may be too smooth to localize individual faults.

**Implementation cost:** Low-Medium — requires band math (ratios, local
variance) on pinned bands.

**Data availability:** B1, B2, B6 in pinned stack. K/Th and U/Th separability
from B6 TC is unverified (B6 is radiometric total count). **Partially viable.**

---

## H5 — Drainage-deflection / stream-offset knickzone detector (NOT BUILT)

**Layers:** B12 `det_elev` (3DEP-derived), B19 `det_elev_slope`, existing
drainage not in stack (would need NHD or derived flow direction).

**Physical signature:** Active normal faults deflect drainages and create
knickzones where streams cross fault traces. Stream-offset detection via
drainage-pattern asymmetry across candidate fault traces.

**Why it catches catalogue-missing faults:** Small-displacement faults offset
drainages without producing mappable scarps; drainage deflection can be more
persistent than scarps in alluvial settings.

**Non-fault mimic:** Lithologic controls on drainage, fan incision, volcanic
drainage patterns — all deflect streams without faulting.

**Differs from existing lanes:** DRAINAGE_KNICK exists but targets terrain
knickpoints, not stream-offset asymmetry. No lane uses flow-direction or
drainage-network deflection.

**Expected DTI improvement:** Uncertain — depends on deriving flow direction
from DEM (possible with scipy) but stream data not in pinned stack.

**Implementation cost:** Medium-High — requires flow-direction derivation,
stream network extraction, offset detection. **Not viable without external
drainage data (USGS NHD or 3DEP-derived flow direction).**

---

## Ranking (expected DTI improvement / implementation cost)

| Rank | Hypothesis | Expected DTI | Cost | Viable with local data? |
|------|-----------|-------------|------|--------------------------|
| 1 | **H1 TILTANGLE: gravity tilt-angle edge corridors** | Moderate-High (actual 0.033466 static) | Low | ✅ Yes — built |
| 2 | H3: curvature × gravity-gradient intersection | Moderate | Low | ✅ Yes |
| 3 | H2: Curie-depth spectral window | High (conceptual) | Medium | ✅ Yes |
| 4 | H4: radiometric × magnetic dual gate | Moderate-High | Low-Medium | ⚠️ Partially (K/Th split unverified) |
| 5 | H5: drainage-deflection knickzones | Uncertain | Medium-High | ❌ No external drainage data |

**Selected for build:** H1 (TILTANGLE) — highest confidence of physical validity,
lowest implementation cost, fully valid with locally restored pinned data. Built
as experiment 1 of 3.

**Holdout result (H1):** HOLDOUT-DTI 0.033466 (gems57-pooled-hide-v2, 45,253
withheld positives across 8 LOQO folds, seeds 20+30). Per-quadrant: NE 0.0332,
NW 0.0354, SE 0.0337, SW 0.0323 — spatially uniform, no quadrant collapse.
Per-draw: 0.0336 / 0.0337 — stable across draws. Beats R0 static (0.004006) by
~8.4× and COULOMBDM static (0.007816) by ~4.3×. Below supervised LOQO
Rule-2 (0.113316) as expected for a standalone deterministic surface.

**Leakage canary:** Not run as single-feature AUC (deterministic surface, no
classifier training; surface does not read the catalogue). Surface uniqueness
vs registry not scanned (below promotion bar; per protocol, no public-registry
scan is spent on a lane that does not clear the holdout promotion bar first).
