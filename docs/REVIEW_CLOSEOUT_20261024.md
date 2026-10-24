# Repository review closeout — 2026-10-24

> **Historical closeout superseded by [`REVIEW_CURRENT.md`](REVIEW_CURRENT.md) and [`REPO_REVIEW_20261024.md`](REPO_REVIEW_20261024.md).** This earlier pass predates merging the SPRINGALIGN artifact from upstream PR #42. Its ANASIG/visible-collar references and 14-TIFF/135-test counts are archival, not current. No current download is cleared for submission.

## Decision

**No new submission TIFF was generated. Existing rasters are OK TO DOWNLOAD FOR RESEARCH, but none is cleared to submit.** The binding public-registry witness reported in `docs/REVIEW_CURRENT.md` is positive throughout the target footprint; any nonempty in-footprint candidate then has 100% forward 3-pixel overlap under the current literal rule. Generating an empty raster or placing values outside the scoring footprint would evade rather than satisfy the scientific and uniqueness requirements. No weekly slot was selected or used.

This is not a claim that a unique candidate is impossible under a revised, explicitly approved definition of registry equivalence. It is the conclusion under the repository's current protocol. The evidence is a decisive witness check, not a new exhaustive scan of every public, historical, private, or site-hosted artifact.

## Three-pass review

### Pass 1 — inspect the previous work and requirements

Read `README.md`, `SESSION_PROMPT.md`, current review/next-step notes, analysis reports, evidence cards and site pages. The repository already contains the documented candidate queue and negative experiments. The latest primary research artifact remains ANASIG f45; its run card is `evidence/anasig_run_card.json`. The local holdout and file-validation pipeline already exist, but no competition receipt is recorded.

### Pass 2 — check correctness, consistency and edge cases

Found a user-facing documentation defect in `docs/executive-summary.html`: the page presented the earlier visible-collar raster as the primary candidate and gave direct upload instructions despite its duplicate-stop verdict. It also stated a causal explanation for the 0.2778 report and described a method for the 0.4413 leaderboard entry without evidence tying that method to that score. Replaced this with a clear research-only download status, conditional submission steps, receipt/CLAIM distinction, and explicit limits. The submission-name instruction now reflects the described portal fields: the project name is a ledger identifier; the portal form described by the user has a file field and optional note, not a demonstrated name field. Fixed the review-page relative link to the root-level irregularities ledger.

The potential full-footprint witness is not a reason to mark an empty prediction as unique or scientifically useful. The review therefore does not generate a new TIFF, even though an arbitrary byte-distinct file could be made.

### Pass 3 — verify after edits

Validation commands and outcomes:

- `.venv/bin/python -m pytest -q` — **135 passed**, 17 Rasterio/Affine pending-deprecation warnings. The first post-edit run correctly caught that the page did not contain the exact `NOT CLEARED` status phrase required by a site-contract test; the status heading was corrected, then the full suite passed.
- `.venv/bin/python scripts/check_site.py` — **PASS**, 14 served rasters gated; primary recorded as ANASIG f45.
- `.venv/bin/python scripts/verify_manifest.py` — **PASS**, all 8 pinned raster hashes verified.
- `git diff --check` — **PASS**.
- Relative-link scan of `docs/*.html` — **PASS** after fixing the root-level irregularities link.

The venv is local and ignored. The system Python did not have pytest or raster/geospatial dependencies, so the suite was run in the repository's pinned virtual environment.

## Candidate hypotheses requested before a future experiment

These are **proposals only**, not validated gains or unique lanes. Priority is screening value/cost, not a leaderboard score forecast. Under the current full-footprint overlap witness, none can pass emission uniqueness, so none is actionable until the policy conflict is resolved.

| Order | Specific layers / physical signature | Why it may reveal catalogue-missing faults; distinction from tested work | Named mimic | Cost and evidence/data status |
|---|---|---|---|---|
| 1 | Pinned DEM Bands 12 (`det_elev`) and 19 (`det_elev_slope`); profile-paired one-sided vertical offset with coherent break orientation | A repeated asymmetric offset across profiles is more diagnostic than the already-tested slope-gradient × coherence field; may identify small scarps with weak potential-field contrast. | Shoreline terrace risers, fan margins, channel banks | In-stack, moderate screen/build cost; not tested as this paired-profile transform. Blocked from submission by registry gate. |
| 2 | Bands 12/19 plus an official hydrography layer; scarp-to-channel crossing/alignment statistic | Tests whether DEM breaks persist across drainage rather than tracking banks; distinct from BREAKLINE's unconditioned terrain score. | Incision boundaries, roads and drainage-divide edges | External data required. USGS hydrography source and current downloadability were not verified here; **not viable yet**. |
| 3 | Bands 12/19 plus official Lake Lahontan shoreline/shoreline-elevation geometry; contour-parallelism and stillstand penalty | Explicitly suppresses a named non-fault terrain mimic rather than adding another structural predictor. | Tectonic scarps coincidentally near shoreline elevations | External data required. No specific free shoreline layer was verified downloadable in this review; **not viable yet**. |
| 4 | Existing spring locations and independently detected structure orientations; pairwise strike-alignment, not spring-density | Tests structural control of vent locations rather than simply predicting around known springs; no current lane uses this pairwise alignment test. | Lithologic control, topographic discharge and sampling-access bias | GDR/INGENIOUS is a source lead, but current data access and reuse terms were not checked; **not viable yet**. |

Do not interpret any rank as expected numeric DTI. For any next experiment: first resolve the registry policy; verify source and license; pre-register a distinct lane and actual surface; test feature-alone leakage on the prescribed buffered whole-segment holdout; require paired improvement over the comparable holdout best; then check surface and final-dot registry overlap before creating a submission artifact. Stop at three experiments or two hours.

## What the reported scores establish

- The prompt-supplied GEMSDOE32 value **0.2778 is a CLAIM** in this checkout, not an organizer receipt. Local raster lineage and spacing/clearance can be measured; causal attribution to the score cannot be established without the accepted-submission receipt and private target labels.
- The prompt values **0.3195** and **0.4413** conflict. Historical repository notes label a 2026-10-24 public leaderboard observation as `LEADERBOARD-SNAPSHOT`; that is not a receipt for the GEMSDOE32 artifact or this repository's candidates. This review did not refresh non-GitHub official domains.
- HOLDOUT-DTI is catalogue hide-and-recover; it is not a projection of public/private test performance and cannot be numerically compared to leaderboard scores.
- The machine validator establishes GeoTIFF format properties only. It does not establish uniqueness, geological truth, organizer acceptance, score, or authorization to consume a weekly slot.

## Source/access limits and next work

The repository retains official source leads in `SESSION_PROMPT.md` and the site. In this execution, GitHub/pypi dependencies were accessible, while the competition portal, external geological data services, and live leaderboard were not independently refreshed. No DrivenData authentication, weekly quota, upload, or organizer receipt is available to this workflow. Do not claim data was newly downloaded or officially confirmed. Next highest-value work is a policy decision on how to treat full-footprint positive registry rasters, followed by source/license verification and a fresh pre-registered lane only if the literal stop is changed by the policy owner.
