# Current review — 2026-10-24

## Download status comes first

**OK TO DOWNLOAD existing files for research; DO NOT SUBMIT any current artifact.**
The site primary is the pre-existing [SPRINGALIGN research TIFF](downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif),
not a new unique submission from this review. Its local format audit passes,
but the hash-verified dense public witness triggers the literal duplicate stop.
No weekly slot was used. See the [exact witness receipt](downloads/review_20261024_springalign_witness_v2.json),
[current session review](REVIEW_20261024_SESSION.md), and
[run card](downloads/repo_review_run_card_20261024.json).

The BREAKLINE artifact discussed in the historical follow-up below is also an
existing research file and is rejected by the same literal witness rule.

## Outstanding next step completed: public witness check

The queued BREAKLINE public-registry check was narrowed to a decisive witness,
not represented as a repeat of the historical 1,279-raster scan.
[Public source](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif)
was retrieved with GitHub API, verified against Git blob SHA-1 and byte size,
then pinned with SHA-256. [Measurement receipt](downloads/breakline_public_witness.json).

**REGISTRY-MEASUREMENT:** BREAKLINE final-dot forward overlap is **1.0**;
Spearman rho is **0.03159061184613562**. Overlap alone triggers the duplicate
stop. The witness has positive support whose 3-pixel halo covers **1.0** of the
competition footprint. Thus every nonempty prediction supported within that
footprint has 100% forward overlap with this witness. This follows directly
from set inclusion, not an extrapolated competition score. Byte uniqueness is
not the same as passing the specified geometric uniqueness gate.

**Consequently no nonempty TIFF can satisfy the current literal registry gate
on this footprint while that witness is included.** No new candidate experiments
were run; no slot was selected or used. Do not evade this by moving predictions
outside the footprint, emitting no dots, or excluding dense rasters without an
explicit policy revision. An empty prediction does not solve fault discovery.

The pre-placement surface was not reconstructed in this retrospective check.
Final-dot rejection is sufficient to keep this existing candidate negative;
this is not evidence of a compliant fresh surface-to-placement run.

## Scientific interpretation

The prompt's GEMSDOE32 result is **CLAIM 0.2778**, without an organizer receipt
verified here. Its lineage is consistent with nonredundant spatial coverage,
pruning and known-fault exclusion improving distance-weighted credit. These
are hypotheses about performance, not causal proof. The private target is
missing faults, not direct identification of geothermal vents. Catalogue
hide/recover can reward catalogue proximity without demonstrating discovery.
No claim of beating that result, 0.3195, or 0.4413 is justified by this review.
The leaderboard and non-GitHub official domains could not be refreshed under
this environment's outbound-host restriction; historical snapshots remain
historical, not newly verified facts.

## Ranked research queue — not implemented or cleared

These are conceptual extensions, not demonstrated globally novel methods.
The existing [ranked hypothesis report](HYPOTHESES_20261024_BREAKLINE.md) and
[collar report](hypotheses_visible_collar_20261024.md) remain the pre-experiment
records. No lane paragraph was supplied separately in this request; this review
stays within the queued BREAKLINE validation rather than choosing another lane.

| Priority | Hypothesis / layers and physical signature | Missing-fault rationale / distinction from existing simple breaks | Expected benefit / cost / viability |
|---|---|---|---|
| 1 | DEM coherent break pairs with cross-profile antisymmetry | Reject symmetric channel walls and shore benches; test repeated one-sided vertical offsets instead of coherence alone | Unmeasured; moderate cost; blocked by registry policy and absent local feature cache |
| 2 | DEM break orientation versus downslope drainage alignment | Reject drainage-parallel erosional edges; retain transverse linear steps | Unmeasured; moderate cost; same blockers; channel banks remain a mimic |
| 3 | DEM scarp persistence conditioned on radiometric facies | Distinguish topographic offset within a facies from a lithologic contact edge | Unmeasured; moderate/high cost; confirm channel definitions/coverage in restored stack first |
| 4 | Magnetic edge and DEM break spatial offset consistency | Buried continuation could be offset from the surface break, unlike pointwise fusion | Unmeasured; high cost; depth/contact changes mimic fault offsets; same blockers |

None needs to be sold as viable on unverified new external data. Start with the
pinned existing stack using `scripts/restore_inputs.py` after policy resolution;
mirror byte identity does not establish official authenticity or redistribution
permission. Do not invent features if the stack cannot be restored.

## Three review passes

1. **Implementation:** public witness fetched/hash-verified; existing candidate
   independently reread; no new raster or model experiment.
2. **Bug review:** fixed the audit orchestrator's implicit collar surface on
   arbitrary candidates, evidence overwrite risk, missing-cache network fallback
   in cache-only mode, and incomplete/empty scan clearance. A pre-placement
   duplicate now blocks even if final dots pass. Regression tests added.
3. **Requirements review:** synchronized the site/README warnings; retained
   negative deliverables, exact SHA, holdout provenance and scope. A fresh unique
   submission is explicitly **not delivered**, because the literal gate is
   unsatisfiable with this full-halo witness. Do not confuse “format valid” with
   “cleared for a weekly slot.”

## Reproduce

```sh
python -m pytest tests -q
PYTHONPATH=vendor python scripts/check_site.py
python scripts/audit_breakline_witness.py
```

For a full later scan, use `audit_public_registry.py --candidate OTHER.tif`
with `--surface ACTUAL_SURFACE.tif --output evidence/OTHER-audit.json`.
A separate output is required for non-collar candidates. Omitting the surface
is permitted for retrospective rejection only and cannot clear uniqueness.
This prevents reusing the collar surface or overwriting its historical receipt.
The actual pre-placement surface is required; final dots are not a substitute.
The full scan still needs API access, disk space and runtime; the witness check
is rejection evidence only, never uniqueness certification.

## Next session priorities / access limitations

1. Resolve dense-positive-surface policy explicitly; retain the current stop
   until then. No amount of score optimization can pass the literal gate now.
2. Obtain authorized competition bytes and verify official provenance/license.
3. Restore cache, audit the common evaluator's holdout construction, and add
   off-catalogue validation before running a new lane (maximum three experiments).
4. Require paired improvement against the current comparable holdout best,
   all leakage canaries, both uniqueness phases, and automated format checks.
5. Separately check the submission-page weekly quota and capture an organizer
   receipt when a selector authorizes a submission. No credentials are requested
   or stored here; this environment cannot access that portal.

Official references for later review (not newly retrieved this session):
[problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[reference code](https://github.com/drivendataorg/gems-prize-reference-solution),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[GDR INGENIOUS](https://gdr.openei.org/submissions/1391).

## Repository review recheck — 2026-10-24

This follow-up reviewed the current source, README, homepage, witness receipts, and download gate without running a new geological experiment. The literal uniqueness stop remains binding: the exact ANASIG receipt reports the 17GEMSDOE E-proba witness positive on all 5,167,373 footprint cells; its final-dot overlap is measured at 1.0. Since each valid submission must place its nonzero values inside this footprint, any nonempty candidate exceeds the stated 70% overlap limit against that witness. No new TIFF was produced and no weekly slot was used.

Corrected two documentation risks found during review: the homepage previously led with a historical 1,279-raster / 11GEMSDOE claim, obscuring the later decisive 17GEMSDOE witness and its single-witness scope; and the README described the prompt-reported 0.2778-to-0.4413 sequence and the winning method as established causal facts. The homepage now foregrounds the current binding witness and clarifies that this is not a fresh full scan. The README labels the reported values as CLAIMs and the proposed mechanism as inference, not organizer-confirmed evidence.

### Verification performed

- `.venv/bin/python -m pytest -q`: **135 passed**, 17 Rasterio/Affine pending-deprecation warnings.
- `.venv/bin/python scripts/check_site.py`: **PASS**, 14 served TIFFs gated.
- `.venv/bin/python scripts/verify_manifest.py`: all eight pinned input hashes verified.
- `git diff --check`: PASS.
- System Python initially lacked `pytest` and NumPy. A repository-ignored `.venv` was created and dependencies installed from `requirements.txt`; no environment artifacts are tracked.

No public endpoint, leaderboard, DrivenData receipt, submission quota, or competition upload was accessed or verified in that review. Existing TIF links are for research/download only, not approved for competition submission.

## Tooling-hardening follow-up — 2026-10-24 UTC

See the [current three-pass repository review](REVIEW_20261024_SESSION.md) and [run card](../evidence/repo_review_run_card_20261024.json). This follow-up found and fixed a shared preflight edge case: infinity outside the footprint was previously counted as an allowed NaN by `gems.gates._g_nan_outside()`. The common CLI now requires all-finite values in `[0,1]` across the whole raster and zeros outside; the site checker calls the same strict gate for every served candidate. The generic `run_gates()` default retains NaN-outside only for historical/research comparisons and rejects infinity or nonzero outside values.

This is tooling validation, not a geological experiment. No new TIFF, holdout result, public-registry scan, or weekly slot was produced/used. The current session verification is: 182 tests passed (103 nonfatal Rasterio/Affine pending-deprecation warnings); all 16 served zeros-outside downloads passed `scripts/check_site.py`; all eight pinned hashes and the R0 parent proof passed; `git diff --check` passed. The first four counts are software/data-integrity checks, not competition metrics.
