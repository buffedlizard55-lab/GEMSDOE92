# IRREGULARITIES — Decision-Changing Items Only

## IR-92-01 — Public sibling mirrors host competition rasters; terms unchecked
- **Observed:** Sibling public repos (`buffedlizard55-lab/GEMSDOE`,
  `GEMSDOE24`, `60GEMSDOE`) mirror login-walled competition files with
  redistribution terms unchecked, and sibling repos already track candidate
  `.tif`/`.zip` files publicly.
- **Decision:** GEMSDOE92 gitignores `data/` and `releases/*.{tif,zip}`,
  commits only SHA-256 receipts/GeoJSON/ledger, and flags the existing
  public rasters for the human owner. No permission is inferred.

## IR-92-02 — TRACKB densification is kernel-redundant: corrected prediction is negative
- **Observed:** A-priori MODEL was +0.004/+0.002/-0.002 for
  t1p0/t1p2/t1p5. The build's own instruments then showed weighted-coverage
  MODEL deltas of -0.0448/-0.0522/-0.0648 and blind off-catalogue SGMC
  PROXY 0.0728/0.0705/0.0664 vs R0 0.0961 (monotone dose-response).
- **Decision:** Shipped ledger predictions corrected to
  MODEL:-0.008/-0.010/-0.013 (a-priori values preserved in mechanism cards,
  GEMSDOE88 IR-88-23 precedent). All three rasters are HOLD — Phase-2
  GeoJSON/evidence asset only; no weekly slot unless the human decides
  for Phase-2 reasons. Finding: at R0's 2.8 px spacing, trace interiors
  are already kernel-saturated; value lies in coverage/bridging, not
  densification (feeds the proposed TRACE_BRIDGE axis in SLOT_PLAN.md).

## IR-92-03 — Retained dots inherit R0's 2–3 px collar
- **Observed:** Rebuilt R0 has 0 dots <=2 px but 2,171 at 2<d_cat<=3 px.
  TRACKB retains parent dots unchanged (min d_cat 2.236 px) and places
  every new dot at d_cat>3 px. The validator therefore gates at >2 px
  (parent collar) and reports, not gates, the 2–3 px ring.
- **Decision:** Rasters are not represented as satisfying a blanket
  >=3 px rule; only a PRUNE-axis build can do that. Marked HOLD above.

## IR-92-04 — GeoJSON traces cover 78% of raster-kept dots at t1p0
- **Observed:** Straightest-walk decomposition of the component-kept dots
  yields 2,432 paths >=1.0 km covering 19,097/24,386 kept dots (78.3%);
  the rest sit in sub-km branches of kept networks.
- **Decision:** GeoJSON metadata records coverage explicitly; traces are
  review candidates, not an exact re-expression of the raster.

## IR-92-05 — Deadline, TOP_PUBLIC and slot counts not portal-verified
- **Observed:** The agent never accessed drivendata.org (brief prohibits
  it). TOP_PUBLIC 0.4413 (2026-10-22) and 3-slots/week are carried from
  GEMSDOE88's human-supplied plan; the deadline is assumed 2026-12-03.
- **Decision:** Human must re-confirm deadline, TOP_PUBLIC and remaining
  slots on the competition page before any upload.
