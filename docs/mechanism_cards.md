# Mechanism Cards — MASS axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 dots, none within 2px of catalogue, CLAIM 0.2778
Ranking: H19-5 continuous field (121k px) value at dot location, proxy for belief strength.

## h33-h33-2-b2-MASS_D10-20261023-e26a6cb8
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: slight gain if low-ranked dots are noise; risk loss if they carry credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 33889, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_D10-20261023-e26a6cb8-zeros.tif, sha8 e26a6cb8

## h33-h33-2-b2-MASS_A10-20261023-e5613a00
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: likely drop if marginal credit <0.056; test of budget optimum. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 41419, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_A10-20261023-e5613a00-zeros.tif, sha8 e5613a00

## h33-h33-2-b2-MASS_SWAP10-20261023-3e776063
- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.
- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.
- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.
- **Predicted sign and size**: best chance: keep budget, improve avg credit. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.
- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.
- **Details**: parent h33-h33-2-b2, n_dots 37654, pct_changed 10.0%, file releases/h33-h33-2-b2-MASS_SWAP10-20261023-3e776063-zeros.tif, sha8 3e776063


---

# Mechanism Cards — PRUNE axis (2026-10-23)

Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 unit-mass dots, sha256 `baeae321…077dd`
verified byte-for-byte this session. Min catalogue distance 2.236 px; 0 dots
within 2 px, but **2,171 within 3 px (5.77%)**, 3,825 within 4 px (10.16%),
5,637 within 5 px (14.97%).

Design: remove every parent dot within R px of the catalogue and refill to hold
the count at 37,654 by moving each removed dot to its **nearest legal pixel**
(distance > R, in footprint, not on catalogue, on the H19-5 surface). Nearest
refill keeps every other property of the file fixed, so the only variable is the
distance rule. A ranking-based refill would have imported the MASS axis and
reproduced the confound that made the previous session's MASS files ambiguous.

## Shared hypothesis
Dots sitting on or beside a known trace are credited against *catalogue* truth,
which the organizers mask out. They therefore add to `S` (marginal credit to
`T` only through new-fault truth nearby) while the pixels they sit on are not
scored. Removing them should cut dead denominator mass. The forum answer says
new-fault truth **can** lie within 300 m (3 px) of known traces, so this helps
only up to the radius where real new faults start being deleted.

## Shared mechanism
`DTI = T / (0.2T + 0.2(S−M) + 0.8|G|)`. Each dot contributes `+1` to `S` and at
most `M ≤ 1` per unit; a dot whose marginal credit `c` is below `0.2·DTI`
(≈0.056 at 0.28) lowers the ratio. Dots adjacent to known traces are the
likeliest to have `c` below that bar, because their nearest truth is already
credited.

## Shared non-fault mimic
A dot near a known trace can still be genuinely new: unmapped splays,
step-overs, and along-strike extensions of mapped faults are exactly the
Phase-2 target ("newly mapped geometry of existing systems",
https://community.drivendata.org/t/where-do-you-draw-the-line/11536). So the
prune can delete precisely the highest-value pixels. This is not a nuisance
term; it is the competing hypothesis.

## h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7
- **Value**: remove dots within 3 px (2,171 = 5.77%), refill 2,171, count held.
- **Predicted sign and size**: **+0.002 to +0.006 MODEL**. 3 px is 300 m, the
  stated positional uncertainty of the 400 m-spaced GeoDAWN survey, so dots
  inside it are more likely positional scatter than distinct faults.
- **Falsifier**: live score below parent by >0.01. That would say dots within
  300 m of known traces carry above-bar credit and the distance prior is wrong.
- **This is the primary bet of the session.**

## h33-h33-2-b2-PRUNE_B4-20261023-78e893d7
- **Value**: remove within 4 px (3,825 = 10.16%), refill 3,825, count held.
- **Predicted sign and size**: **+0.001 to +0.004 MODEL**, less confident. 4 px
  = 400 m is past the survey's positional uncertainty, so this dose starts
  eating real new-fault pixels; it should pay only if the dead mass is thick.
- **Falsifier**: if B4 < B3 by >0.005 while both sit above the parent, the
  optimum is between 3 and 4 px.

## h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad
- **Value**: remove within 5 px (5,637 = 14.97%), refill 5,637, count held.
- **Predicted sign and size**: **−0.002 to +0.002 MODEL**, i.e. no gain
  expected. This is the dose-response's negative control: if the mechanism is
  real and bounded, B5 should be the worst of the three.
- **Falsifier**: if B5 is the *best* of the three, the distance effect is
  monotone and unbounded in this range, which contradicts the 300 m survey
  geometry and should redirect the next session to PRUNE B8/B10 rather than to
  a new axis.

## Reading the session as a whole
The three doses are a dose-response curve, not three independent bets. Outcomes:

| pattern | reading | next |
|---|---|---|
| B3 > B4 > parent > B5 | peak near 3 px, mechanism real and bounded | build `PRUNE_B3 + CONCENTRATION` |
| monotone B5 > B4 > B3 > parent | prior is real and unbounded here | go deeper (B8, B10) |
| all ≤ parent | distance prior is false | abandon PRUNE, the 0.2708→0.2778 step was false-positive removal |
| B3 > parent, B4 ≈ B3 | flat optimum 3–4 px | prefer B3 (fewer deletions, less risk) |

---

# Mechanism Cards — SNAP axis (2026-10-23)

Parent: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots, rebuilt byte-for-byte
(`zeros` SHA-256 `c55bafc4…`, `nan` SHA-256 `baeae321…`), **CLAIM** `0.2778`.
All three SNAP variants hold exact dot count (`37,654`), total mass (`37,654.0`),
parent catalogue exclusions (`d_cat > 2.0 px`, zero mass on catalogue), and
parent `D2.8` Poisson-disk inter-dot spacing (`min_nn = 2.8284 px`), changing
**only** the `<=2 px` local edge/scarp snap operator (`SNAP` is explicitly
exempt from the 1–50% pixel-change bound per Brief v2 §5).

### Why spacing-preserving SNAP (`min_nn >= 2.8 px`) is essential
In `R0`, `dot_thin(H19-5, 2.8)` seeded from the north-west pixel of each binary
`H19-5` component (`N=20.0%, W=15.3%` vs `S=35.9%, E=29.5%` neighbor occupancy)
without centering on local scarp or potential-field gradient peaks; within
`<=2 px` (`200 m`), median `det_elev_slope` (`Band 19`) is `+102.9%` higher and
median `tmi_hg` (`Band 3`) is `+64.9%` higher than at `R0` dot centers. However,
independent per-dot snapping collapses `8,503` dots (`22.6%` of `R0`) to
`min_nn = 1.0–1.4 px` along strike, duplicating coverage inside the `R = 3 px`
(`300 m`) triangular DTI kernel `T = sum_g max_x k(||g - x||)` while still paying
`+1` denominator mass `S` per dot. Enforcing `D2.8`'s open-disc spacing
`dy^2 + dx^2 >= 2.8^2` (`min_nn = 2.8284 px`) eliminates along-strike clumping
and restricts displacement to genuine cross-strike centering.

## h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24
- **Value**: `scarp2p0px` — `<=2.0 px` (`200 m`) spacing-preserving snap onto
  `0.35*pct(det_elev_slope [B19]) + 0.35*pct(||grad det_elev_slope||) + 0.20*pct(tmi_hg [B3]) + 0.10*pct(iso_grav_anom_slope [B5])`.
  Mean displacement `1.2340 px` (`123.4 m`), median `1.4142 px`, max `2.0000 px`,
  `82.05%` (`30,896`) pixel positions changed, `min_nn = 2.8284 px`.
- **Hypothesis**: GeoDAWN's `400 m` flight-line spacing (`150–200 m` AGL,
  https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7),
  `50°–60°` normal-fault hanging-wall dip projection of basement potential
  fields, and `D2.8`'s unweighted NW-seeded thinning displace `R0` dots by
  `100–200 m` cross-strike from surface fault traces. Snapping `<=200 m` onto
  the joint topographic scarp + piedmont break-in-slope inflection + TMI/gravity
  horizontal gradient crest centers dots onto brittle fault traces without
  climbing eroded footwall cliffs.
- **Mechanism**: Under `DTI = T / (0.2T + 0.2(S - M) + 0.8|G|)` at fixed
  `S = 37,654`, every `100 m` (`1 px`) reduction in cross-strike offset raises
  triangular-kernel credit `k(d) = max(0, 1 - d/3)` by `+1/3` (`+0.333`) per
  fault pixel, yielding `Delta DTI ≈ 0.26 * DTI * (Delta T / T)`. Including the
  piedmont break-in-slope `||grad(det_elev_slope)||` anchors dots at the
  alluvial-fan/bedrock-facet fault junction rather than mid-facet bedrock cliffs,
  while in flat playas where slope variation is negligible, `tmi_hg` and
  unsigned `iso_grav_anom_slope` steer placement over concealed contacts.
- **Non-fault mimic**: Erosional range-front triangular facets, incised
  alluvial-fan terrace risers, Pleistocene pluvial lake shorelines
  (Lahontan/Bonneville), and resistant ash-flow tuff cliff ledges within `200 m`
  of concealed faults.
- **Predicted sign and size**: **`MODEL:+0.012`** vs `R0` (scenario range
  `[-0.006, +0.025]`; `MODEL` projection, never a score). Report-only `PROXY`
  diagnostics: SGMC off-catalogue bedrock control `+0.002667` (`0.098727` vs
  `0.096060`); buffered catalogue hide-and-recover `+0.000798` (`0.004804` vs
  `0.004006`).
- **Falsifier**: Live receipt delta `<= -0.01` vs `R0` falsifies `<=200 m`
  surface-scarp localization and shows new-fault truth is dominated by concealed
  intrabasinal traces or offset from geomorphic slope breaks; `|delta| < 0.01`
  is treated as no evidence.

## h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc
- **Value**: `scarp1p4px` — `<=sqrt(2) px` (`1.4142 px = 141 m`, 8-connected
  Moore window) spacing-preserving snap onto the **identical** joint response
  surface `R_es`. Mean displacement `0.9540 px` (`95.4 m`), median `1.0000 px`,
  max `1.4142 px`, `78.00%` (`29,370`) pixel positions changed,
  `min_nn = 2.8284 px`.
- **Hypothesis**: Limiting capture radius to `141 m` (one diagonal pixel)
  corrects `D2.8`'s 1-px NW ribbon-edge bias and sub-grid rasterization offset
  while preventing `200 m` upslope excursion onto eroded footwall facets along
  mature Basin-and-Range fronts where the active piedmont fault trace has
  stepped basinward of the retreated bedrock escarpment.
- **Mechanism**: Holds response surface, count (`37,654`), exclusions
  (`d_cat > 2.0`), and spacing (`min_nn >= 2.828 px`) identical to `scarp2p0px`,
  varying **only** `max_shift` (`1.414 px` vs `2.000 px`) to isolate capture
  radius.
- **Non-fault mimic**: Local `100–141 m` stream-cut fan scarps, talus-apron
  margins, and shallow volcanic flow edges bordering geophysical lineaments.
- **Predicted sign and size**: **`MODEL:+0.008`** vs `R0` (scenario range
  `[-0.004, +0.018]`; `MODEL` only). Report-only `PROXY` diagnostics: SGMC
  control `+0.001480` (`0.097540`); hide-and-recover `+0.000550` (`0.004556`).
- **Falsifier**: If `scarp1p4px` beats `scarp2p0px` by `>= +0.01` on live
  receipts, `200 m` capture overshoots onto retreated footwall facets; if both
  trail `R0` by `>= 0.01`, topographic scarp snapping is falsified.

## h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c
- **Value**: `pot2p0px` — `<=2.0 px` (`200 m`) spacing-preserving snap onto
  subsurface potential-field horizontal gradients **only**:
  `0.65*pct(tmi_hg [B3]) + 0.35*pct(iso_grav_anom_slope [B5])`. Mean
  displacement `1.3656 px` (`136.6 m`), median `1.4142 px`, max `2.0000 px`,
  `79.07%` (`29,773`) pixel positions changed, `min_nn = 2.8284 px`.
- **Hypothesis**: Mechanistic subsurface control. If hidden new-fault truth is
  predominantly concealed intrabasinal faults beneath Quaternary basin fill with
  zero surface scarp, snapping solely to unsigned magnetic and isostatic-gravity
  horizontal gradients centers dots onto basement/volcanic offsets without
  alluvial or shoreline erosion noise. Conversely, if new-fault truth tracks
  surface/piedmont traces of `50°–60°` dipping normal faults, `~63°` geomagnetic
  inclination (unreduced `TMI`) and down-dip hanging-wall density projection pull
  potential-field gradient crests `150–300 m` basinward off the surface fault.
- **Mechanism**: Holds capture radius (`2.0 px`), count (`37,654`), exclusions
  (`d_cat > 2.0`), and spacing (`min_nn >= 2.828 px`) identical to `scarp2p0px`,
  removing only the topographic scarp/break terms. Uses unsigned `Band 5`
  (`iso_grav_anom_slope = ||grad g||`) rather than signed E-W `Band 18`
  (`dg/dx`) so east- and west-dipping normal faults are treated symmetrically.
- **Non-fault mimic**: Unfaulted plutonic intrusive contacts, caldera ring
  fractures, ash-flow tuff stratigraphic pinchouts, and down-dip hanging-wall
  gradient shifts of dipping normal faults.
- **Predicted sign and size**: **`MODEL:-0.002`** vs `R0` (scenario range
  `[-0.014, +0.010]`; `MODEL` only). Report-only `PROXY` diagnostics: SGMC
  control `-0.003303` (`0.092757`, consistent with dip/inclination offset from
  mapped bedrock traces); hide-and-recover `+0.000569` (`0.004575`).
- **Falsifier**: A live receipt gain `>= +0.01` over both `R0` and `scarp2p0px`
  falsifies surface-scarp dominance and proves hidden test faults are primarily
  concealed basement structures best centered by potential-field gradients alone.

