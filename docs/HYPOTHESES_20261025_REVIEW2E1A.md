# Ranked conditional hypotheses — review `2e1a649e` (2026-10-25)

This list was frozen before any new geological feature code or placement in this
session. These are **unimplemented operators**, not score projections and not
claims of discovery. The binding pre-placement registry check stopped the
session before experiment 1: the SHA-256- and Git-blob-pinned `17GEMSDOE
E-proba-multiscale` raster is positive at every one of the `5,167,373` valid
footprint cells, so every nonempty candidate has literal 3-pixel forward overlap
`1.0 > 0.70`. See
[`review_2e1a649e_preflight.json`](downloads/review_2e1a649e_preflight.json).
No candidate below is called submission-viable while that rule remains in force.

The repository search found no implementation of the five exact transforms
below. Similar *input layers* and some broader geological ideas have been used;
the distinctions name what is new at the operator level. All proposals use only
already manifested layers, so they need no new external data. The competition
stack can be restored from the commit-pinned owner mirror in
`registry/session_manifest.json`; it was deliberately not restored in this
review because the mandatory pre-placement stop fired first. Mirror hashes prove
byte identity, not official origin or redistribution rights.

| Rank | Candidate, layers, and exact physical transform/signature | Why it may detect a catalogue-missing fault | Difference from implemented repository methods | Named non-fault mimic and falsifier | Expected value / implementation cost |
|---:|---|---|---|---|---|
| 1 | **STRIP-INPAINT** — B2 RTP magnetic field, B13 gravity, and B12 detrended elevation. Self-supervise on unlabeled pixels by masking narrow oriented strips and reconstructing each field from both sides with a robust multi-scale harmonic/low-rank predictor. Score only long corridors where cross-strip reconstruction error is high in at least two independent measurement classes and the preferred strip orientation is stable. | A structural discontinuity violates smooth continuation across the fault; masking removes the tempting local derivative and asks whether opposite sides can predict one another. Buried discontinuities may survive without a topographic scarp. | No current lane uses withheld-strip reconstruction residuals; derivative, Hessian, Radon, cross-gradient, and tree-probability lanes all score the observed local field directly. | Lithologic contacts, survey seams, raster boundaries, and isolated cultural noise. Falsify with seam/edge masks, same-field phase-randomized nulls, and require independent-field agreement rather than one anomalous band. | Highest complementarity; **medium** cost. Expected HOLDOUT-DTI change unknown. |
| 2 | **SPECTRAL-FABRIC-ROTATION** — local 2-D Fourier or steerable-wavelet power tensors from B2 and B13 in nested `1–4 km` windows. Detect an abrupt, signed rotation or collapse of dominant wavelength/orientation across a coherent corridor, without requiring a large amplitude edge; corroborate strike in both fields. | Faulting can offset or rotate inherited basement fabric and truncate magnetic/gravity texture, while erosion and cover suppress a sharp surface expression. | Existing orientation operators derive from local gradients/Hessians or line voting. This tests a change in the *distribution of spatial wavelengths and azimuths* across a boundary. | Volcanic flow provinces, intrusive contacts, flight-line striping, and window-boundary ringing. Reject corridors tied to acquisition azimuth, unstable across window/taper choices, or present in only one potential field. | Medium-high value; **medium-high** cost. Expected HOLDOUT-DTI change unknown. |
| 3 | **DRAINAGE-HANDEDNESS** — B12 detrended elevation and B19 slope converted to a flow graph. For each trial corridor, measure same-sense lateral deflection and recovery of multiple hydrologically independent channels, preserving upstream/downstream orientation; score a binomial excess of common handedness after conditioning on regional slope and stream order. | A concealed strike-slip or oblique splay can deflect several channels in one sense even where no individual offset is large enough to enter the mapped catalogue. | DRAINAGE-KNICK/KNICKLOQO use local thalweg curvature and knick persistence. This is a graph-level repeated-displacement-sign test across independent catchments, not a local ridge score. | Cuesta drainage, glacial/shoreline inheritance, irrigation, or capture. Falsify with slope-rotated null corridors, independence by catchment, and reversal/downslope controls. | Medium value; **high** cost (flow routing, graph independence, signed null model). Expected HOLDOUT-DTI change unknown. |
| 4 | **RADIOMETRIC-MASS-BALANCE** — GeoDAWN K/Th/U with B12 elevation, B19 slope, B2 RTP, B13 gravity, and B17 conductivity. Fit a spatially blocked, smooth background model for expected radiometric composition from terrain and potential-field lithologic context; score linear K depletion plus U/Th excess in the *residuals*, requiring a co-strike conductivity break rather than raw ratio magnitude. | Fault-focused alteration or redox transport may perturb radiometric mass balance along a permeable structure after conditioning away first-order lithology and surficial redistribution. | RADIOCONTACT uses raw U/K and Th/K contact gradients; clay-cap lanes use direct conductivity/radiometric products. This proposal asks for conditional residual chemistry after an explicit non-fault background model. | Playa salts, soil moisture, alluvial sorting, agriculture, and felsic lithologic contacts. Reject residuals explained by slope/basin position, require out-of-fold calibration and conductivity strike agreement, and test playa masks. | Moderate/low coverage; **medium** cost. Expected HOLDOUT-DTI change unknown. |
| 5 | **GRAVITY-CLOSURE** — B13 isostatic gravity anomaly and B15 depth to basement, with B2 RTP magnetic corroboration. Forward-model a family of smooth constant-density basement-interface gravity responses from B15 (density contrast treated as a fold-fitted nuisance parameter), subtract the best visible-fold-only response from B13, then score narrow, strike-persistent residual dipoles that coincide with a B2 fabric discontinuity. | A buried offset or density-juxtaposing fault omitted or smoothed in the basement-depth product leaves observed gravity that the independent interface geometry cannot close, even when raw B13 and B15 gradients are weak. | Existing lanes use raw/standardized gravity, derivatives, Euler depth, Poisson decoupling, basement curvature, or co-located products. None performs a forward physical closure test of observed B13 against B15 and maps the residual. | Plutons, caldera margins, lateral sediment-density change, or edge padding. Falsify against broad residual bodies, require a narrow sign-changing dipole stable across plausible density contrasts, and reject FFT/window-edge corridors. | Conditional value; **medium-high** cost (forward filter, fold-safe nuisance fit, boundary/null tests). Expected HOLDOUT-DTI change unknown. First verify B15 provenance; if B15 was derived from B13 gravity, this closure is circular and the candidate is nonviable. |

## Frozen test rule if the specification changes

Only Rank 1 would be implemented first. Before placement, compare each
continuous surface and its proposed final-budget support with the complete
accessible registry under the literal thresholds. Test every constituent
feature alone on the buffered holdout; symmetric AUC above `0.90` is leakage
until explained. Rebuild every learned background, density parameter, and
catalogue-derived placement feature in each whole-segment fold from training
space and visible faults only. Mask visible faults pixel-exactly, and score
pooled triangular-kernel DTI with `alpha=0.2`, `beta=0.8`, radius `300 m`, and a
spatial bootstrap 95% CI via `vendor/gems57/evaluate_holdout.py`. Package only
through `vendor/gems57/submission_writer.py`. It must beat the comparable
current holdout best before a separate selector may consider a weekly slot.

The official USGS GeoDAWN manual-review link is
<https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7>.
It was not reachable from this sandbox's restricted network and is not needed
to run the currently blocked test; availability is therefore not claimed from a
fresh live check here.
