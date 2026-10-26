# Pre-registered geological hypotheses — BLINDEXT lane (GEMSDOE92)

Lane: BLINDEXT — blind extensions of mapped fault traces missing from the
USGS/INGENIOUS catalogue.

## Hypothesis H1 (Rank 1, built this session)

**Layers involved:** h19_5 skeleton (19GEMSDOE, 121,131 px, 1-px multi-physics
fault worm skeletonization) + existing_faults catalogue (USGS/INGENIOUS mapped
faults, 60,988 px) + sample_submission footprint (5,167,373 finite cells).

**Physical signature:** Euclidean distance transform from 8-connectivity
skeleton endpoints (fault-trace termini). Score = exp(-d_endpoint / 3.0),
restricted to footprint & ~catalogue & (d_cat > 2.0 px) & (d_endpoint <= 6 px)
& ~h19_5 trace itself. Dots selected by score-ranked non-maximum suppression
at >= 2.83 px (~300 m, the DTI triangular-kernel radius), 37,654 dots.

**Why it catches a fault missing from the catalogue:** The USGS/INGENIOUS
catalogue maps surface traces only. Blind normal faults in the Basin and
Range extend beyond their mapped surface traces at depth, where they lose
surface expression. By targeting the termini (endpoints) of mapped fault
traces and placing dots in the geologically continuous zones beyond the
mapped trace, we target blind extensions that are absent from the catalogue
but physically continuous with known faults.

**How it differs from anything already implemented:** No prior lane in this
repository targets skeleton endpoints specifically. Prior lanes target
terrain scarps (BREAKLINE, SCARPPOL, STEPEDGE), gravity/magnetic edges
(GRAVQUAD, COULOMBDM, XPHASE), hydrothermal vents (VENTSCARP), or
catalogue-network context (FAULTNET). BLINDEXT is the first lane to use
the *topology* of the mapped skeleton (endpoints = trace termini) as its
primary targeting signal.

**Named non-fault mimic:** Mapped-fault splays and tip damage zones that
are already in the catalogue (excluded by d_cat > 2.0); non-tectonic linear
features (alluvial fan distributary channels, playa shorelines) that happen
to lie near skeleton endpoints (partially mitigated by the d_endpoint reach
limit and the off-catalogue requirement).

**Expected DTI improvement / cost:** Unknown (HOLDOUT-DTI cannot be computed
without the withheld truth grid). Cost: very low (only bridge data, no
competition stack reads).

## Hypotheses H2-H5 (ranked, not yet built)

H2. **MAG-QUAD:** Magnetic analytic-signal amplitude (B1 mag_anom, B2 rtp,
B3 tmi_hg, B9 tmi_vg, B14 tmi) x structure-tensor linear coherence. Reuses
gems/gravquad.py:structure_tensor_coherence. Cost: very low.

H3. **GDR-GEOTHERMOMETER-FIELD:** Interpolated geothermometer temperature
surface from GDR #1391 table. Cost: low (fix thermalclass whitespace defect).

H4. **SEIS-GRAV-LAG:** Signed cross-strike lateral separation between
seismicity density (B10, B16) and gravity anomaly (B13). Cost: low.

H5. **MT-CHANGEPOINT:** Conductivity change-point within constant cover-depth
blocks (B17, B15). Cost: low.

## Validation status

- Format gates: PASS (11/11, all finite [0,1], zeros outside, CRS/shape/transform match).
- Uniqueness: FAIL (literal overlap 1.0 vs local rasters; pinned dense witness
  covers all 5,167,373 footprint cells).
- Holdout-DTI: not computable (organizer withheld truth not published).
- Verdict: negative (submission_eligible: false). OK TO DOWNLOAD FOR RESEARCH,
  DO NOT SUBMIT.
