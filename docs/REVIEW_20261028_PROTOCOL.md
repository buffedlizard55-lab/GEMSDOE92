# Protocol and publication review — 2026-10-28

## Decision

**DO NOT SUBMIT.** No new TIFF, experiment or weekly-slot selection occurred in this review. This is an evidence-based stop, not proof that a better geological strategy is impossible. The requested single method paragraph was not supplied; the prompt only refers to a paragraph “below”. Therefore a new lane cannot be responsibly assigned by inference.

The previous homepage promoted LBMC1 despite its own [run card](downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6_run_card.json) recording a failed `catalogue_holdout_beats_r0_recipe` gate, literal registry duplication and a pre-placement overlap of 1.0. A renamed PI-1 / PI-1b rule and a fitted score projection do not override the requested rules. We changed its verdict and audit status to negative without changing the underlying TIFF or recorded measurements. The legacy renderer is retained for audit only; the active renderer is fail-closed.

**HOLDOUT-DTI:** the historical run card reports LBMC1 0.0197 (95% CI 0.0149–0.0250) versus R0 recipe 0.0978 (95% CI 0.0857–0.1095), `gems57-pooled-hide-v2`, 22,663 withheld positive pixels. These historical results are not independently reproduced here and static rasters may not meet the prospective fold-local requirement. The model estimate is not a leaderboard score or substitute for holdout validation. No organizer receipt was independently obtained.

The [dual-witness audit](downloads/fleet_20261027_audit_d30d387c.json) reports a continuous surface positive throughout the footprint and a dense binary lattice; whether every positive continuous pixel counts as a dot is ambiguous. The run card itself nevertheless records a literal overlap failure. Do not represent a relaxed interpretation as compliance without an explicit protocol decision. Registry completeness has not been established for every owner/site in the prompt.

## Nine-site findings

The [nine-site summary](nine-sites.html) uses the repository's pinned owner-reported historical inventory. It is not live, and links are for research only. GEMSDOE32's reported 0.2778 is the highest of the nine in the supplied inventory, **not ORGANIZER-CONFIRMED**. Thinning and a mapped-fault collar plausibly reduce redundant false-positive mass under a distance-tolerant metric, but hidden labels and a receipt are unavailable, so their causal contribution and any achievable improvement cannot be established. The prompt also reports conflicting current leaderboard values; neither was verified here.

## Data and next steps

The tracked `data/bridge` contains sample and catalogue rasters and historical predictions; this checkout does not contain the full cached feature stack. The sandbox only has outbound access to a limited host allowlist, not DrivenData, Dropbox or the official external data hosts. The prior [ranked hypothesis brief](HYPOTHESES_20261027_D30D387C.md) is historical, not a fresh source-access verification and not a new lane assignment. No experiments were attempted.

1. Obtain an explicit single method lane and an authorized interpretation of both dense and binary registry witnesses.
2. Restore the shared cache and verify its provenance and finite nodata sentinels; establish a complete registry snapshot.
3. Use the shared evaluator and writer, visible-only fold-derived catalogue features, per-feature canaries and pre-placement/final comparisons; compare against the same-evaluator best using confidence intervals.
4. Validate actual TIFF bytes against the competition template, resolve outside-footprint encoding with the organizer, then use a separate selector. Recheck the weekly cap and rules on the official page. A local range pass alone does not guarantee portal acceptance.

Official manual references: [problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR INGENIOUS](https://gdr.openei.org/submissions/1391), [official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf). These external pages were not re-fetched in this sandbox.
