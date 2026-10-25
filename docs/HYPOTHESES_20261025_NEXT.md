# Ranked next hypotheses — GEMSDOE92, written 2026-10-25 (post-GRAVQUAD session)

Written per the parallel-run protocol: these are untried geological hypotheses,
no numeric gain is projected, and the top-ranked candidate must be validated
on the shared holdout (`vendor/gems57/evaluate_holdout.py`) before any weekly
submission slot is spent. Three zero-label standalone physical lanes have now
been measured this session arc (RADIOCONTACT `0.005066`, GRAV-QUAD `0.005092`,
DRAINAGE-KNICK Rule-2 `0.061728`), all well below the two supervised,
quadrant-debiased classifiers that hold the repository's actual holdout
records (COULOMB-LOQO standalone `0.113316` Rule-2 / `0.009220` static;
KNICKLOQO standalone `0.010788` static, all-time record). That pattern is the
main input to this ranking.

All band numbers are 1-based positions in the pinned 19-band GeoDAWN stack
(`training_features.tif`, SHA-256 `4371c82e3b83...`, restored and re-verified
fresh this session from `buffedlizard55-lab/GEMSDOE` via `git clone` over
`github.com`/`codeload.github.com` — see `registry/session_manifest.json`).
No competition labels are read by any surface; the catalogue is used only for
masking in the build scripts, never as a model input.

| Rank | Named lane / layers | Physical signature (transform) | Why it catches faults missing from USGS/INGENIOUS | Difference from everything already implemented in this repo | Named non-fault mimic | Expected DTI gain / cost |
|---|---|---|---|---|---|---|
| 1 | **LOQO-FEATURE-EXPAND**: fold GRAV-QUAD's analytic-signal amplitude + structure-tensor linear coherence (2 new columns) and RADIOCONTACT's U/K & Th/K alteration-edge strength (1 new column) into the existing 24-feature COULOMB-LOQO / KNICKLOQO quadrant-debiased `HistGradientBoostingClassifier` ensemble (`gems/coulomb_loqo.py`, `gems/knick_loqo.py`), retrain, re-score | A supervised model that has already been shown (twice, independently) to extract roughly 2x the holdout DTI of any single deterministic zero-label transform by learning *nonlinear interactions* between many weak physical features. Three new orthogonal feature families (alteration mineralogy, gravity analytic-signal amplitude, edge-linearity texture) have never been inputs to that ensemble. | Nothing currently in the repository has tested whether the specific *combination* of radiometric alteration + gravity-analytic-signal + coherence, learned jointly with the existing strain/RTP/MT/gravity features, finds faults the current 24-feature set misses — as opposed to each being tested alone, where all three are individually weak (static DTI 0.0045–0.0092 range). | Same as COULOMB-LOQO/KNICKLOQO: K-rich ash-fall beds, equant plutons, playa conductivity — now explicitly testable per-feature via the same leakage-canary procedure (require every added column's standalone symmetric AUC <= 0.90, as already measured: `asa` 0.536, `coherence` 0.504, `rad_edge` 0.512). | **Medium-high** (the only two supervised arms in the repo hold the two actual holdout records; adding uncorrelated-looking new features to a tree ensemble rarely hurts and sometimes helps materially). **Cost: medium** — requires rebuilding the full quadrant-debiased training pipeline with 3 extra columns, not a trivial reuse; should reuse `gems/knick_loqo.py`'s training harness rather than writing a new one (**do not fork it**). |
| 2 | **GDR-GEOTHERMOMETER-FIELD**: pinned real GDR #1391 wellspring/geothermometer table (`data/external/gdr_wellspring_in_footprint.csv`, 27,092 rows, 3,388 uniquely named sites, re-verified this session — includes real, named Great Basin geothermal areas such as Beowawe, Dixie Hot Springs, and Buffalo Valley Hot Springs) interpolated (inverse-distance or ordinary kriging) on quartz/chalcedony/cation geothermometer temperature, *blind of `dist_known_fault_px`* (explicitly drop that column; it is a direct label leak) | This is the only hypothesis on this list that targets *active, hot, fluid-conducting* structure directly rather than any cold/degraded geomorphic or potential-field proxy for density/susceptibility contrast. A structure can be invisible to every topographic or gravity/magnetic signature and still be a blind geothermal feeder if it channels measurably hot water; this is the most literal operationalization of "geothermal vent discovery," the stated prize focus. | No lane in this repository builds a standalone thermal-field surface from the geothermometer table; COULOMB-LOQO/POISSONFLEX use `>= 80 degC` geothermometer cells as one of many features inside a much larger classifier, never as its own interpolated field, and never checked for the known `thermalclass` string-formatting defect found this session (`'Hot '` with a trailing space is miscounted separately from `'Hot'` — 121 vs 1,873 rows; any filter on the literal string `'Hot'` silently drops 6.1% of true positives). | Non-thermal high-TDS agricultural return flow, irrigation-affected shallow groundwater chemistry (can mimic warm/cation geothermometer signals without a deep source), and playa evaporative concentration effects, none of which indicate a blind fault. | **Medium** (direct, literal match to "geothermal," but geothermometers reflect reservoir chemistry more than fault *location* precision — expect higher recall of known *fields*, possibly low spatial precision for individual fault traces at 100 m pixel scale). **Cost: low** (file is already pinned and verified; requires fixing the `thermalclass` whitespace defect first, then ordinary IDW/kriging — no new external source needed). |
| 3 | **SEIS-GRAV-LAG** *(carried forward, still untested)*: B10 `deq_n100a15`, B16 `ieq_n100a15` seismicity density/intensity vs B13 `iso_grav_anom` signed lateral offset | Spatially coherent seismic-swarm flank running *alongside* (not over) a gravity-defined buried basement step marks a blind, strike-permeable fault; distance-to-earthquake alone (already screened out elsewhere in this repo as a weak feature) misses this lateral-offset signature. | Prior seismicity work in this repo used raw distance/intensity; this tests signed cross-strike lateral separation between two independent continuous fields, never built. | Magmatic/induced seismicity co-located with purely lithologic density contrasts; aftershock alignments on already-mapped faults (excluded via `d_cat` mask). | **Medium-low** (seismicity in this stack is coarsely smoothed at 100 km, which limits spatial precision). **Cost: low** (two stack bands, no new data). |
| 4 | **MT-CHANGEPOINT** *(carried forward, still untested)*: B17 `cond_surf` change-point *within* a locally constant B15 `depth_to_base_surf` block | A conductivity discontinuity at constant inferred cover thickness is not explained by alluvium thickness alone and implies a discrete fracture/fluid conduit — a blind strand. | Earlier MT gating (HYDROCONDUIT, COULOMBDM) conditioned on conductivity *level* or clay-cap *edges*; this is a change-point test conditioned on a third, stabilizing variable (cover depth), never built. | Playa/aquifer salinity changes, irrigation, and facies changes unrelated to tectonics. | **Low-medium.** **Cost: low** (two stack bands, no new data). |
| 5 | **MAG-QUAD** *(new this session, not yet built)*: magnetic analytic-signal amplitude from B1 `mag_anom`, B2 `rtp`, B3 `tmi_hg`, B9 `tmi_vg`, B14 `tmi` x the same structure-tensor linear-coherence operator validated this session in GRAV-QUAD (`gems/gravquad.py:structure_tensor_coherence`, directly reusable) | Magnetic susceptibility contrasts respond to a different rock property (magnetite content, typically volcanic/intrusive units) than gravity's density contrast; some Great Basin geothermal systems (e.g., documented dike/sill-controlled upflow zones) are magnetically, not gravimetrically, distinct. A magnetic analytic signal is strike-blind in the same sense as GRAV-QUAD's gravity analytic signal, but sensitive to a different physical property, so it is expected to be only partially correlated with GRAV-QUAD's result (worth checking the Spearman correlation between the two surfaces as a first, free diagnostic before any holdout run). | GRAV-QUAD (this session) is the first analytic-signal lane in the repo, but it only used gravity bands; no lane has built the magnetic equivalent, and RTP-based lanes (COULOMB-LOQO, EULERFUSE) use RTP as one Hessian/tilt feature inside a classifier, never as part of a standalone multi-component analytic signal. | Shallow cultural/infrastructure magnetic noise (well casings, pipelines, fences) and intrusive bodies with no associated fault. | **Low-medium** (GRAV-QUAD's standalone result this session suggests standalone analytic-signal lanes plateau low; primarily useful as a fast, free diagnostic and as a 4th candidate feature for Rank 1's LOQO-FEATURE-EXPAND). **Cost: very low** (reuses `gravquad.structure_tensor_coherence` verbatim; only the input bands change — write as `gems/magquad.py`, do not duplicate the coherence function). |

## Validation requirement before any slot is spent

Per protocol: **do not spend a weekly submission slot on an idea that has not
beaten the current holdout best on `vendor/gems57/evaluate_holdout.py`.**
Rank 1 (LOQO-FEATURE-EXPAND) must be retrained and re-scored against the
pinned 8-fold, 2-seed `gems57-pooled-hide-v2` holdout (22,663 withheld
positives) with a paired bootstrap CI against the current COULOMB-LOQO /
KNICKLOQO baselines before it is considered for promotion. Rank 2
(GDR-GEOTHERMOMETER-FIELD) needs no new external data acquisition — the input
file is already pinned, hash-verified, and present in this environment — but
does require fixing the `thermalclass` string-trim defect first (see
`IRREGULARITIES.md`, 2026-10-25 entry) so that the `Hot` filter is not
silently dropping 6.1% of its own positive class.

## External data already obtainable, if a future hypothesis needs something new

If a future session needs genuinely new external data beyond what is already
pinned (`training_features.tif`, GeoDAWN radiometrics, GDR #1391
geothermometer table, SGMC fault layer), the following free, official,
openly licensed sources are the right next places to look, in priority order:

1. **USGS GeoDAWN airborne magnetic/radiometric survey** (source stack for
   `training_features.tif`): <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> — already the basis of the pinned stack; a session with direct USGS ScienceBase access could pull higher-resolution original flight-line grids (the pinned 100 m stack is already a derived/resampled product).
2. **DOE GDR (Geothermal Data Repository) submission #1391** (source of the
   pinned geothermometer CSV): <https://gdr.openei.org/submissions/1391> — the
   pinned CSV already appears to be a footprint-clipped extract of this
   submission; a session with direct GDR access could pull the full
   statewide table plus any associated well-log or temperature-gradient data
   also hosted there.
3. **USGS Spatial Geologic Map Compilation (SGMC) 1:500,000 fault layer**
   (already partially pinned as `data/external/derived_sgmc_faults_100m_u8.tif`
   from `buffedlizard55-lab/GEMSDOE24`) — used in this repo as an
   off-catalogue proxy; the original USGS SGMC national GIS release would let
   a future session verify the derived raster against the primary vector
   source directly.
4. **Nevada Bureau of Mines and Geology / Great Basin Center for Geothermal
   Energy (GBCGE) INGENIOUS project outputs**: <https://gbcge.org/current-projects/ingenious/>
   — this is named in the competition background as a likely source of the
   organizer's fault catalogue; this sandbox cannot reach gbcge.org directly
   (outside the allow-listed hosts), so this remains a named, not-yet-checked
   source for a future session with broader network access or a human
   download step.

None of the above are required to validate Rank 1 or Rank 2 above; both can
be attempted with data already present and hash-verified in this repository.
