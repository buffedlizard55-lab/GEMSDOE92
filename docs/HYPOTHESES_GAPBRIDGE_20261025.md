# Candidate hypotheses ranked (this session) — GAPBRIDGE shipped
| # | Hypothesis | Layers / signature | Why it catches faults missing from USGS/INGENIOUS catalogue | Differs from repo lanes | Cost | Status |
|---|---|---|---|---|---|---|
| 1 | **GAPBRIDGE coincidence** | RTP grad (b2) + MT cond grad (b17) + basement-depth grad (b15) + slope-break (b19), geometric-mean ranks, catalogue-proximity weight, anti-R0 >3px dotted emission | Blind undercover faults have no scarp (missed by mapping) but step basement/conductivity/magnetics at depth | Prior lanes used ML fits or single physics; none used 4-layer rank coincidence with anti-registry exclusion | Low (cached stack) | **TESTED: HOLDOUT-DTI 0.1015 [0.0887,0.1126]** |
| 2 | Measured-only coincidence | RTP + gravity slope (b5) + topo break only | Removes modelled-product leakage risk | Ablation of #1 | Low | TESTED: 0.0549 |
| 3 | Magnetic texture offset (piercing points) | RTP (b2) cross-correlation displacement field | Strike-slip offsets of magnetic fabric reveal faults with no vertical throw | Untried; needs dense optical-flow on magnetics | High | Proposed, untested |
| 4 | Spring/vent alignment corridors | GDR wellspring points (cached, official GDR 1391) collinearity (RANSAC lines) | Geothermal upflow localises on unmapped permeable faults | SPRINGALIGN used density, not collinearity | Medium | Proposed |
| 5 | Radiometric K/Th alteration lows | GeoDAWN K,Th,U (cached ext raster) ratio lineaments | Hydrothermal leaching along blind faults | RADIO* lanes used contact/decoupling, not K-depletion lineaments | Medium | Proposed |
External data: none required — all layers already SHA-256-cached via scripts/restore_inputs.py (official sources in registry/session_manifest.json).
