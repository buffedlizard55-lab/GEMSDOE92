# Session continuation review — 2026-10-24 UTC

## Decision first

**No new submission TIFF was generated.** The request for a novel file and the binding uniqueness rule cannot both be satisfied with the currently documented public registry: a Git-blob-verified raster is positive on every valid footprint cell, so every nonempty in-footprint prediction is within 3 px of that raster. The literal rule therefore forces a duplicate stop. We did not change that rule, place dots, choose a weekly slot, or label an existing raster as new.

- **Existing download:** APRONRIDGE free1d is still **FORMAT-VALID — OK TO DOWNLOAD FOR RESEARCH**.
- **Submission status:** **DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT** (`verdict: negative`, `submission_eligible: false`). Format validity is not uniqueness, scientific validity, or organizer acceptance.
- **New experiments this session:** 0. The full 19-band feature stack is absent from this checkout's `data/bridge/` and `.cache/gems_inputs/`; only the grid, catalogue/labels, and three lineage rasters are present. The prompt-named `scripts/download_competition_data.sh` and `scripts/prepare_data.py` do not exist. `scripts/restore_inputs.py` can retrieve manifest-pinned files through an owner GitHub mirror, but its manifest explicitly says official upstream provenance / redistribution permissions are not verified. I did not restore the 419 MB stack or train against unverified mirror provenance.
- **Previous result:** No competition score or organizer receipt was received. `ledger/submissions.csv` remains the only receipt authority.

## Fresh exact-file registry check

I downloaded the single rejection witness from the GitHub blob API and verified its byte count, Git blob SHA-1, and SHA-256 before comparison:

- Source: [17GEMSDOE E-proba raster](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/HEAD/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif) · [immutable Git blob API object](https://api.github.com/repos/buffedlizard55-lab/17GEMSDOE/git/blobs/374c88b1da2b803e2ed160de467fd71ae114010d)
- **REGISTRY-MEASUREMENT:** Git blob SHA-1 `374c88b1da2b803e2ed160de467fd71ae114010d`; SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`; 25,065,181 bytes; positive on 5,167,373 / 5,167,373 footprint cells. The exact existing APRONRIDGE raster has 37,654 dots; forward 3-px overlap is `1.0` and full-footprint Spearman is `0.0562374738`. The overlap alone is over the `0.70` stop threshold. This is a single-witness rejection check, not an exhaustive scan and not proof of geological equivalence.
- Exact machine output: [fresh witness check JSON](downloads/review_20261024_continuation_witness.json) and [run card](downloads/review_20261024_continuation_run_card.json). The checker's expected duplicate result exits with status 1; it is not a software failure.

The witnessed raster covers every valid footprint cell, which makes final-dot uniqueness impossible under the present literal support/halo definition for any nonempty valid output. An empty TIFF, predictions outside the footprint, thresholding/re-encoding the witness, or silently exempting dense rasters would not be legitimate workarounds. A policy change by the authorized competition/project policy owner is a prerequisite for a future promotable TIF.

## GEMSDOE32 `0.2778`: what the evidence can and cannot establish

`0.2778` remains **CLAIM** from the user-provided GEMSDOE32/site list, not **ORGANIZER-CONFIRMED**: no submission-page receipt for that item is in this repository. The local parent-forensics analysis attributes the reported increase mechanistically to reducing redundant predictions through spacing/thinning and removing predictions close to known catalogue faults. Under the Tversky-weighted distance metric, excess predictions can add false-positive penalty without additional max-pooled true-positive credit; known mapped faults are not the hidden target. This is a plausible explanation of the *construction* and reported progression, not a causal estimate of private-set score: private labels, organizer receipt, and a counterfactual submission are unavailable.

Repository evidence for the proposed explanation: [`docs/ANALYSIS_20261024.md`](ANALYSIS_20261024.md), [`evidence/r0_forensics_20261024.json`](../evidence/r0_forensics_20261024.json), and [`registry/parents/R0.json`](../registry/parents/R0.json). Local holdout figures from those records are **HOLDOUT-DTI**, not scores. The prompt-supplied leaderboard values `0.3195` and `0.4413` conflict and are not refreshed receipts in this review. No inference that this project beats either is justified.

## Ranked untried hypotheses (proposals, not results)

Ranks indicate qualitative screening priority, not numeric DTI projections. The work remains in a **terrain-profile asymmetry lane**; no surface or dots for this lane were built. All proposals need the competition feature stack, which is not currently staged here. They are therefore **not validated / not actionable** under this checkout state.

| Rank | Hypothesis and layers | Physical signature | Why it may detect a catalogue-missing fault | Difference from implemented repo methods | Named non-fault mimic | Cost / current data status |
|---|---|---|---|---|---|---|
| 1 | **ASYM-SCARP:** GeoDAWN Bands 12 (`det_elev`), 19 (`det_elev_slope`), optionally Band 15 (`depth_to_base_surf`) for stratification | Cross-strike profiles with a paired, signed slope break and persistent relief asymmetry across adjacent transects; evaluate orientation and persistence rather than raw gradient magnitude | A young blind or weakly expressed scarp may retain an asymmetric profile even where potential-field contrast is weak and it is absent from USGS/INGENIOUS mapped traces | Existing BREAKLINE emphasizes slope-gradient/coherence; STEPEDGE emphasizes sustained step magnitude; this would use paired profile shape/asymmetry, with cover used only for stratification. It was previously proposed but is not implemented or holdout-tested in this repo. | Incised wash wall or alluvial-fan terrace riser | Low compute after stack restoration; **stack absent**. No new external source needed beyond the competition-provided stack; official USGS GeoDAWN catalog URL is listed below but was not freshly retrieved here. |
| 2 | **CHANNEL-CROSSING PERSISTENCE:** Bands 12/19; derive a drainage graph from the DEM, no outside hydrography | A candidate scarp that repeatedly offsets or deflects small channels, rather than merely following a channel bank | Repeated cross-channel displacement is a geomorphic expression of a fault that may not have a mapped trace or strong magnetic/gravity signature | Conditions terrain breaks on channel-crossing geometry; unlike existing unconditioned scarp, step, piedmont, and conduit scores, it penalizes features parallel to drainage. | Lithologic boundary controlling drainage or roads/terraces that divert channels | Medium implementation/validation cost; **stack absent**. DEM-derived channels require no new external data, but scale sensitivity and leakage must be tested. |
| 3 | **RTP–GRAVITY JUNCTIONS:** Bands 2 (`rtp`), 5 (`iso_grav_anom_slope`), 11 (`iso_grav_anom_vg`), 13 (`iso_grav_anom`) | Orientation-consistent intersections / terminations of RTP and gravity edge networks; score network topology and cross-sensor agreement, not edge amplitude | Blind basement faults can produce coincident magnetic and density boundaries where no surface fault is mapped | APRONRIDGE combines RTP curvature with a piedmont prior; BREAKLINE / GRAVCrest tested other terrain or gravity signatures. This proposal targets cross-sensor edge-junction topology, not either existing scalar surface. | Lithologic contact or intrusive boundary producing coincident magnetic and density edges | Medium cost; **stack absent**. No additional external data proposed. |
| 4 | **THERMAL-CHEMISTRY STRIKE-PAIRS:** DOE GDR INGENIOUS #1391 water chemistry plus Bands 15 and 17 | Pairwise alignment of geothermometer anomalies along a basement-cover ramp, with spatial cross-validation that holds out whole source clusters | Chemically hot waters can indicate deep flow even where surface temperature is cooled by mixing and the fault is uncatalogued | SPRINGALIGN used hot-point spatial alignment; HYDROCONDUIT already used GDR geothermometry and MT conductivity. This is a new paired chemical-anomaly / cover-ramp test, but is close to those prior lanes and high duplicate risk. | Lithologic water-rock reaction and sampling/access bias | Medium cost; requires GDR #1391 and the stack. GDR access/terms were **not checked live** from this restricted network; do not call this viable until verified. |

**Top-ranked hypothesis status:** ASYM-SCARP has not passed feature-alone leakage canaries, holdout evaluation, or pre-placement registry-surface screening in this session. The requested top-candidate HOLDOUT-DTI and CI are therefore **NOT RUN**. We did not invent a result or spend a weekly slot. Historical **HOLDOUT-DTI** for APRONRIDGE free1d is `gems57-pooled-hide-v2`, 22,663 withheld positives, 0.0083535575 (95% CI 0.0068230241–0.0101350138); it is an earlier experiment, not validation of ASYM-SCARP.

## Three-pass review

### Pass 1 — repo and evidence review

Read `README.md`, the full `SESSION_PROMPT.md`, current review, site and run cards before changing files. Found a material presentation inconsistency: README's first-screen “current primary” pointed to HYDROCONDUIT while `docs/index.html` and its audit identify APRONRIDGE free1d as primary. Also confirmed the current sample/data bridge lacks the 19-band stack. No candidate was built.

### Pass 2 — bug, missing requirement, and edge review

Verified the latest site status says both **OK TO DOWNLOAD FOR RESEARCH** and **DO NOT SUBMIT**; confirmed the fresh full-footprint witness means uniqueness fails regardless of candidate ranking if the support definition remains literal. Checked that a public-registry pass against only local/sparse maps cannot overrule that witness. No policy exception was inferred. Confirmed no receipt or live leaderboard refresh is present. Reconciled README's first-screen primary identity and added direct links to the operating prompt and current review.

### Pass 3 — re-check after edits

- `.venv/bin/python -m pytest -q`: **201 passed**, 103 nonfatal Rasterio/Affine `PendingDeprecationWarning`s.
- `.venv/bin/python scripts/check_site.py`: **PASS**, all 25 served zeros-outside rasters gated; APRONRIDGE is the primary and its stored audit hash matches.
- `.venv/bin/python scripts/verify_manifest.py`: **PASS**, all 8 currently tracked manifest files match their pinned hashes. This does not include the absent training feature stack.
- Fresh witness check: **expected duplicate stop** (exit 1), exact witness Git/SHA hashes verified, exact APRONRIDGE bytes checked, 100% forward overlap.
- `git diff --check`: **PASS** after the final edits.

These checks establish repository tests, raster formatting, and one rejection measurement—not scientific discovery, uniqueness clearance, official data provenance, or competition score.

## Official links retained for manual review (not freshly verified unless noted)

- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN information](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS GeoDAWN data catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7)
- [DOE GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [EPSG:32611](https://epsg.io/32611)

Only GitHub/package-registry hosts are reachable from this execution. The official DrivenData, NLR, USGS and GDR URLs above were not fetched in this review; source facts, live leaderboard, competition quota, and current licensing/redistribution terms remain unverified here.

## Follow-up blockers / next steps

1. **Resolve the registry representation conflict through the policy owner.** Define whether probability surfaces count as dots and provide an approved rule for sparse candidate comparison. Do not locally exempt the witness.
2. **Restore the official/authorized feature stack** (expected manifest hash `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`, 418,912,844 bytes) from an authorized source; verify hash, license, and provenance. The current owner-mirror path exists but origin and redistribution terms remain unverified.
3. If policy and data permit, pre-register one candidate, test each feature alone on the shared buffered holdout, require symmetric AUC ≤0.90, compute paired HOLDOUT-DTI with CI against the current holdout best, then perform actual-surface pre-placement uniqueness before any placement.
4. Emit and validate a fresh TIFF only if the exact bytes clear the literal (or formally revised) public registry rule and all format gates. Preserve a negative run card otherwise.
5. A separate human selector must verify the current weekly cap and choose any submission; this agent did not choose or use a slot. Obtain and record a submission-page receipt before any ORGANIZER-CONFIRMED claim.

The prompt's requirement for a newly generated unique TIFF remains **unfulfilled** in this session because generating any nonempty in-footprint output under the unchanged rule would knowingly fail the duplicate gate. The existing APRONRIDGE download must not be represented as newly generated here.
