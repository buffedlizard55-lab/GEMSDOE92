# Pre-registered hypotheses — GEMSDOE92, session 2026-10-25 (LISTRICLAG lane)

Written BEFORE any lane code/build for this session, per the parallel-run
protocol. Band numbers are 1-based positions in the pinned 19-band GeoDAWN
stack (`training_features.tif`, SHA-256 `4371c82e3b83…`, band descriptions
read directly from the GeoTIFF this session and matching the README band
audit). All candidate surfaces are computed only from the pinned stack; no
competition labels are read during feature construction.

Context carried from prior sessions (learning, not copying):

- Holdout-best instruments (same evaluator `gems57-pooled-hide-v2`, seeds
  20+30, 22,663 withheld positives): strict fold-visible Rule-2
  `d_visible > 2.0` best = `COULOMB-LOQO standalone` `0.113316 [0.100614,
  0.127163]`; static `d_cat > 2.0` best = `KNICKLOQO standalone`
  `0.010788 [0.009468, 0.012201]`. `R0` static = `0.004006`.
- `GEMSDOE32 h33-h33-2-b2 … -zeros` CLAIM `0.2778` is an owner-site claim,
  not an organizer receipt. Established mechanism (docs/ANALYSIS lineage):
  it is the H19-5 catalogue-skeleton redraw thinned to ~2.83 px spacing —
  under DTI (`alpha = 0.2`, `beta = 0.8`, 300 m triangular kernel) sparse
  unit dots at kernel-optimal spacing on mapped-fault corridors maximize
  `TP_w` per unit `FP_w` because unmapped-truth recall (`beta`-weighted FN)
  dominates the denominator and FP mass is cheap (`alpha = 0.2`).
- Every prior label-free single-surface lane (DRAINAGE_KNICK, RADIOCONTACT,
  GRAVCrest, STEPEDGE, …) scored below the Rule-2 bar; ML-LOQO lanes
  (COULOMB-LOQO, KNICKLOQO) hold the records. A new label-free lane is
  therefore expected to be a *mechanism probe* first; promotion requires
  beating the registered bar, otherwise verdict = negative (deliverable).

## Candidate hypotheses (untried in this repo), ranked

| Rank | Named lane / layers | Physical signature (transform) | Why it catches faults missing from USGS/INGENIOUS | Difference from everything already in this repo | Named non-fault mimic | Expected gain / cost |
|---|---|---|---|---|---|---|
| 1 | **LISTRICLAG**: B15 `depth_to_base_surf`, B18 `iso_grav_anom_hg`, B11 `iso_grav_anom_vg`, B12 `det_elev`, B19 `det_elev_slope` | **Dip-displacement-tolerant surface–subsurface coupling.** Basin-and-Range normal faults are listric/planar with 45–60° dip, so the buried basement density step (|∇σ₃ B15| confirmed by gravity gradients B18/B11) images **200–800 m basinward (2–8 px)** of the surface scarp. Transform: basement-edge rank × gravity-edge rank × **annulus-maximum (2.8–8 px ring) of multi-scale terrain scarp evidence** — scarp evidence *near but not necessarily on* the pixel. | The catalogue is a scarp catalogue mapped at the *surface trace*. Where the scarp is degraded/buried, only the laterally-offset basement step remains. Strictly co-located lanes multiply terrain and basement evidence *at the same pixel* and therefore score ≈ 0 exactly where the lag is largest — the catalogue's own blind spot. | DRAINAGE_KNICK multiplies local terrain × basement edge × shear at the same pixel; COULOMB-LOQO/KNICKLOQO consume per-pixel features in a classifier with no explicit cross-strike lag; EULERFUSE uses Euler depths; no lane models a spatial offset between topographic and potential-field edges. | Fan-toe/piedmont-junction curvature next to basin-margin onlap density contacts; pluvial Lake Lahontan shoreline risers adjacent to lithologic density steps; DEM seams near gravity survey edges. | Expected: medium-high (targets the identified geometric blind spot of co-location lanes). Cost: low (pure `scipy.ndimage`; no classifier, no flow routing). |
| 2 | **GRAVQUAD**: B11 × B18 (carried untried from RADIOCONTACT pre-registration Rank 3) | Vertical-gradient × signed E-W horizontal-derivative sign concordance locked over ≥ 1.5 km strike length. | Density-contrast faults with weak magnetic/topographic expression are invisible to RTP/tilt and scarp lanes. | Standalone 2-D gravity quadrature surface never built as its own lane (B18 is 1 of 24+ features inside COULOMB-LOQO). | Basement terrane boundaries, uncompensated topographic loads. | Expected: medium; duplicate risk vs `eulerfuse-gravity` dots (will be measured). Cost: low. |
| 3 | **SEISGRAVLAG**: B10 `deq_n100a15`, B16 `ieq_n100a15` vs B13 `iso_grav_anom` | Signed cross-strike lateral separation between seismicity-density flank and gravity-anomaly edge (swarms alongside, not on, the buried step). | Swarms localize on permeable blind structures absent from the scarp catalogue. | Prior seismicity screens used distance/intensity level alone (screened negative); lateral-offset signature untested. | Induced/magmatic seismicity near lithologic contacts. | Expected: medium-low (100 km smoothing limits localization). Cost: low. |
| 4 | **MTCHANGE**: B17 `cond_surf` vs B15 `depth_to_base_surf` | Conductivity change-point at locally constant cover depth (fracture conduit not explained by alluvium thickness). | Cover-thickness-controlled MT anomalies explain most conductivity variance; a residual change-point marks a blind conduit. | HYDROCONDUIT/COULOMBDM used conductivity level/clay-cap edges, never cover-stabilized change-points. | Playa salinity, irrigation, clay facies changes. | Expected: low-medium. Cost: low. |
| 5 | **TILTDEPTH**: B6 `tc` (tilt), B3 `tmi_hg` | Tilt-depth (Salem et al. 2007): half-distance between ±45° tilt contours estimates magnetic contact depth; shallow linear contacts = near-surface faulted basement. | Finds shallow magnetic contacts without scarps. | Close to EULERFUSE (Euler depths) and ANASIG (analytic signal) — **explicit lane-drift risk**, ranked last for that reason. | Volcanic flow margins, dike swarms. | Expected: low. Cost: low-medium. |

## Pre-registered session plan (Rank 1 = LISTRICLAG; 3 experiments, ≤ 2 h)

- **E1 (primary):** `LISTRICLAG` binary `37,654` unit dots, ≥ 2.8 px spacing,
  `d > 2.0` px off the placement catalogue. Holdout: strict fold-visible
  rebuild (`gems57-pooled-hide-v2`, seeds 20+30, 8 folds; every
  catalogue-derived quantity rebuilt per fold from visible faults only).
- **E2 (mechanism ablation):** `LISTRICLAG_LOCAL` — identical except the
  annulus-maximum is replaced by strictly local terrain evidence. Attributes
  any E1 gain to the lag mechanism itself.
- **E3 (emission-policy probe):** `LISTRICLAG_N90K` — same surface,
  `90,000` spaced dots; prefix top `37,654` at `p = 1.0`, remainder at
  `p = 0.30`. Tests the previously pre-registered continuous/extended-budget
  emission argument (`c* = alpha·DTI` marginal bar) inside this lane.

**Registered primary comparison (before any run):** pooled strict
fold-visible Rule-2 DTI of E1 vs holdout-best `0.113316` AND paired
1000-draw spatial-block bootstrap vs `R0` (CI must exclude 0). Leakage
canaries: every single feature symmetric AUC ≤ 0.90 on pooled withheld
truth or the lane stops. Uniqueness: literal + matched-budget 3 px overlap
and |Spearman ρ| vs the complete local registry AND the current public
GEMSDOE registry (Git-blob-verified); > 0.70 overlap or |ρ| > 0.90 on the
operative reading ⇒ duplicate ⇒ log and stop. Verdict `promote` requires
all three gates; otherwise `negative` (still a delivered, format-valid,
unique research TIF; **0 weekly slots**).

No numeric score is projected for any arm; projections are never written as
scores (Protocol Rule 3).
