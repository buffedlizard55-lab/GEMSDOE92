# GEMSDOE92 repository review — 2026-10-25

[Machine-readable review run card](../evidence/agent_repo_review_20261025_run_card.json) · [project operating contract](../SESSION_PROMPT.md) · [current submission guide](executive-summary.html).

## Decision first

**Research downloads only. DO NOT SUBMIT any current TIFF under the binding protocol.** This review generated no raster, did not place dots, ran no geological experiment or HOLDOUT-DTI, and used zero weekly submission slots. A requested new, unique, submission-cleared TIFF is therefore **not delivered**. Producing a nonempty TIFF after the pre-placement stop would contradict the user's explicit duplicate rule; relabeling an existing file would not make it unique.

The top-level README previously promoted a file dated **2026-10-26**, although the current session date is **2026-10-25**. I removed that future-dated item from the README's first-screen status and added a chronology warning. Such files remain in the repository for audit, but their presence does not establish generation time or valid preregistration chronology. This is not a statement that the bytes are fabricated; their chronology is unverified in this checkout.

## Pass 1 — inspect the contract and reproduce the repository checks

Read `README.md`, `SESSION_PROMPT.md`, the current review and next-steps pages, the shared evaluator/writer/validator, registry and data manifests, current status cards, public-site checker, current TIFF downloads and related tests. The user brief and operating requirements were already persisted in the README and `SESSION_PROMPT.md`; this review keeps those instructions in force.

The protocol names no single method paragraph/lane for this session. More importantly, the pinned pre-placement evidence at [`review_c5e3848c_preflight.json`](downloads/review_c5e3848c_preflight.json) says its sample grid has **5,167,373** footprint cells and the pinned public witness is positive at all **5,167,373**. `scripts/preflight_dense_witness.py` independently encodes this as a rejection-only universal stop. Because every valid nonempty in-footprint dot is on a positive witness cell, the literal forward 3-pixel overlap is **REGISTRY-MEASUREMENT 1.0**, above the protocol limit **0.70**. This is sufficient to stop before placement; it is *not* a full public-registry uniqueness scan and does not establish a candidate's rank correlation. No candidate surface was created, so surface rank-correlation was not calculated.

Freshly installed the repository's pinned Python dependencies in ignored `.venv/` and ran:

- `.venv/bin/python -m pytest tests -q` — **498 passed**, 140 pending-deprecation warnings from Rasterio/Affine. These are software tests, not scores.
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py` — **PASS; 82 served rasters gated** for the repository's local format/range/site contract.
- `make manifest PYTHON=.venv/bin/python` — PASS for the tracked bridge and parent inputs listed in `registry/data_manifest.json`.
- `make verify PYTHON=.venv/bin/python` — pinned parent bytes verified: 37,654 positive cells, 5,167,373 footprint cells, minimum known-catalogue distance 2.236 px. This verifies pinned artifact bytes, not independent reconstruction of its model-training lineage.
- `make ledger PYTHON=.venv/bin/python` — 111 ledger rows; best organizer receipt: none.

The site checker proves local submission-format properties for the served files. It does not prove duplicate clearance, scientific validity, DrivenData acceptance, permission to redistribute data, or a better competition score.

## Pass 2 — findings, competing claims and ranked hypotheses

### A. Critical documentation inconsistency corrected

The README's opening “Latest artifact — LISTRIC (2026-10-26)” preceded the authoritative current-status panel dated 2026-10-25 and claimed a future-dated artifact was the latest. This was a user-facing freshness/chronology defect. The opener now says the current decision and explicitly quarantines future-dated entries from current-session claims. Historical sections and byte artifacts are preserved.

### B. Why GEMSDOE32's reported 0.2778 is not explained as a verified contest score

The user-provided **CLAIM 0.2778** is not backed by a submission receipt in this checkout. The prior pinned-source audit linked by [`BEAT_0_2778.md`](BEAT_0_2778.md) records that the owner page at a pinned GitHub commit labelled the result “UNSCORED” and “NO ORGANISER SCORE EXISTS.” That owner page is not an organizer receipt, and I did not freshly retrieve it in this review. `make ledger` found no organizer receipt here. Thus neither the claimed score nor its cause can be verified from repository evidence.

A plausible mechanism to *test*, not a proven causal explanation, is that spatial thinning reduces redundant nearby predictions under a distance-tolerant metric, while pruning predictions near known catalogue faults may reduce false-positive penalty if those traces are excluded from evaluation. Both operations can also remove useful predictions. The exact effect depends on the official metric and hidden labels. The supplied score lists and the prompt's conflicting **CLAIM** leaderboard values are not converted into organizer-confirmed results. No local holdout value or projection is offered as a leaderboard score.

### C. Conditional hypotheses — proposals only, no experiment authorized or run

The ordering below is qualitative research priority, not a numerical DTI forecast. Each is a specific operator not found by a text search in current `gems/*.py`; this is only a limited repository search, not a claim of scientific or competitor-wide novelty. Cached layer availability is **not** confirmed: `.cache/gems_inputs/` is absent in this checkout, while official competition data download is behind the competition's authenticated data page per the repository's access note. Consequently none is viable for a holdout test in this session, even setting aside the duplicate stop.

| Rank | Layers and physical signature | Why it could target a missing fault | Difference from current repo methods | Named non-fault mimic | Qualitative expected value / cost; data status |
|---|---|---|---|---|---|
| 1 | GeoDAWN stack Band 2 (`rtp`): bidirectional multiscale local image registration; score a spatially persistent along-strike displacement step in magnetic texture, not edge amplitude | A buried or degraded lateral splay might displace inherited magnetic fabric without a preserved scarp | The proposed registration/restoration operator differs from existing amplitude, derivative-ridge, phase, Euler-depth, and listric offset-pair methods; source-code similarity must be reviewed before any implementation | Separate volcanic flows, intrusive contacts, or survey seams | Potential complementarity: uncertain; implementation cost: high. No external layer required, but the relevant competition stack is not staged and official access is not available in this environment. |
| 2 | Band 2 (`rtp`): persistent connected-component and hole-topology changes across locally standardized threshold levels, with scale-persistence filtering | A weak-amplitude buried displacement may compartmentalize a magnetic domain despite weak local gradient strength | Uses multilevel topology/persistence rather than the repo's gradient, curvature, or Euler-source features | Remanent volcanic domains and acquisition/processing seams | Potential value: uncertain/moderate; cost: medium-high on a 5.17-million-cell footprint. Same unstaged stack/access limitation. |
| 3 | Band 12 (`det_elev`), Band 19 (`det_elev_slope`), optionally Band 15 (`depth_to_base_surf`): paired neighboring-basin divide displacement residual conditioned on local relief and hypsometry | Broad deformation can tilt catchment divides after erosion removes a discrete scarp; a paired contrast could expose a concealed structure | The existing `drainage_knick` implementation is local knickzone-oriented; this proposal is basin-integrated divide geometry. It remains related and needs module-level overlap review before use | Lithologic erodibility contrast, drainage capture, precipitation gradients, pluvial/glacial inheritance | Potential value: low-to-moderate/uncertain; cost: high (watershed segmentation and matched controls). No new outside data proposed, but the requisite stack is not staged. |
| 4 | Bands 13/18 gravity anomaly/gradient plus Band 12 terrain: local cross-spectral gravity–terrain admittance residual, retaining only persistent residual lineaments | A buried density boundary may remain after removing terrain-correlated gravity structure and lack a mapped surface scarp | This is distinct in principle from the existing GRAV-QUAD analytic-signal channel and gravity/basement flexure combinations, but high feature-family overlap must be tested | Basin-fill thickness, non-fault lithologic density boundaries, incomplete terrain correction | Potential value: uncertain/low-to-moderate; cost: medium-high. Stack is not staged; do not call the idea viable until official data access/provenance and band semantics are verified. |

No new external dataset is required by these proposals; each depends on competition-stack bands. The repository's official starting points are [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [USGS GeoDAWN catalog](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [GDR INGENIOUS #1391](https://gdr.openei.org/submissions/1391), and [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf). External hosts beyond GitHub are not reachable in this sandbox, so these links are retained for manual review, not described as live-verified. The competition data source requires authorized access; this review did not attempt to bypass it or use unverified third-party copies.

### D. Existing submission readiness

The homepage and executive summary provide a submission guide, and CI/site checks automatically validate served TIFFs. The reported portal error, `Predicted values must be in range [0, 1]`, is prevented for these locally validated bytes by finite `[0,1]` range checks and zeros-outside encoding. However, the user-facing classification must remain explicit: **OK TO DOWNLOAD FOR RESEARCH** does not mean **OK TO SUBMIT**. The current literal duplicate stop is submission-blocking regardless of format correctness or holdout performance.

## Pass 3 — final cross-check, limits, next actions

Re-read the original request and the persistent contract after the edits. No candidate was selected, no new TIFF or ZIP was produced, no new score was calculated, and no submission slot was spent. The first-screen README no longer presents a future-dated item as the current result. The project's persisted brief still asks future sessions to read the README and `SESSION_PROMPT.md` first.

**Outstanding blockers and limitations:**

1. A protocol-compliant, nonempty candidate cannot pass the pinned universal literal-overlap witness as currently worded. Do not quietly substitute matched-budget overlap or weaken the threshold.
2. No session-specific method paragraph/lane was designated.
3. The competition feature stack is not staged in the workspace cache. Competition data access/authentication and external data redistribution terms are not established here.
4. No organizer submission receipt or current live leaderboard/weekly-cap verification is available in this environment. The user-reported 0.2778 remains a claim, not a confirmed score.
5. This repository has many prior adaptive experiments on related catalogues; a locked outer spatial test is needed to estimate selection bias.
6. The chronology of 2026-10-26-named artifacts in a 2026-10-25 session remains unresolved. Their automated file checks pass, but those checks cannot certify when they were made.
7. A format-valid raster and a catalogued-fault hide-and-recover score do not establish geothermal vent discovery, permeability, temperature, or commercial resource potential.

Recommended next sequence: (i) keep the current rejection; (ii) only after the governing protocol is explicitly changed, name one lane and establish data rights/access; (iii) restore and checksum the approved feature stack; (iv) pre-register one hypothesis and its non-fault controls; (v) test each feature alone for leakage and run the shared whole-segment buffered holdout against a freshly rerun same-instrument control; (vi) audit the surface before placement and the final dots afterward; (vii) have a separate selector decide whether any weekly slot is warranted. Do not spend a slot merely because a file downloads or passes format gates.

## Run card (review-only; no candidate raster)

```json
{
  "schema": "gemsdoe92-repository-review.v1",
  "date": "2026-10-25",
  "hypothesis": "No geological hypothesis was tested: the assigned method lane is unspecified and the literal pre-placement registry stop is binding.",
  "mechanism": "Rejection-only universal witness check; no feature generation or dot placement.",
  "named_non_fault_process": "Not evaluated; no candidate surface was generated.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positives": 22663,
    "value": null,
    "ci95": null,
    "status": "not run in this review"
  },
  "correlation_overlap_vs_registry": {
    "evidence_class": "REGISTRY-MEASUREMENT",
    "scope": "one pinned witness; rejection-only, not a complete public registry scan",
    "witness_forward_overlap_for_any_nonempty_in_footprint_candidate": 1.0,
    "threshold": 0.70,
    "candidate_surface_rank_correlation": null,
    "final_candidate_dot_overlap": null,
    "verdict": "stop before placement"
  },
  "raster_sha256": null,
  "validator_output": {
    "candidate_raster_generated": false,
    "no_nan_inside_footprint": null,
    "values_in_0_1": null,
    "crs_shape_transform_match": null,
    "note": "No candidate file to validate. Separately, scripts/check_site.py passed local format gates on 82 served research TIFFs."
  },
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative",
  "experiments_used": 0,
  "weekly_slots_used": 0,
  "organizer_confirmed_score": null
}
```
