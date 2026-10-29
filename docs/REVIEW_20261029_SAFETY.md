# Three-pass review — 2026-10-29

**Decision: DO NOT SUBMIT.** No new TIFF was produced, no competition slot used, and no leaderboard score or score estimate was established. [Nine-site comparison](nine-sites.html) and [submit guide](how-to-submit.html) are research and future-process information only. The current prompt references a single assigned method paragraph but does not provide one; choosing a lane would breach the parallel-run protocol.

## Pass 1 — inspect and repair

The submission guide contained committed, unresolved Git conflict markers and two competing complete HTML documents. Kept the branch that includes BLINDCORRIDOR's explicit negative status. Added conflict checks for published pages in `scripts/check_site.py` and expanded CI's marker check to HTML, JavaScript and CSS (and diff3 markers). This is a safety fix, not a new experiment.

## Pass 2 — evidence consistency

The generated landing page described only TIPCOMP's earlier partial scan and incorrectly said BLINDCORRIDOR had no full-registry audit. Updated the shared renderer and generated pages to distinguish original partial run-card checks from later historical indexed-registry results. The stored [BLINDCORRIDOR scan](../evidence/uniq_full_registry/blindcorridor-37654dots-11f8999c.json) reports PI-1 overlap 0.769108 with 13GEMSDOE. The [TIPCOMP scan](../evidence/tipcomp_full_registry_uniqueness_20261028.json) reports 0.91795 against GEMSDOE22. Both exceed the requested 0.70 stop. These are historical registry measurements, not score estimates; neither establishes that the registry is currently exhaustive. The original feeds remain historical run-card descriptions, not new scans. The literal dense-witness ambiguity remains unresolved.

## Pass 3 — verification and handoff

- Full suite before the final copy-only updates: 804 passed, 19 skipped; targeted new and affected tests: 11 passed, 3 skipped.
- `scripts/check_site.py`: 128 served rasters passed its local checks, before the guide wording-only update; these checks do not establish organizer acceptance or scientific quality.
- `make manifest` and `make verify`: passed for the pinned local inputs and parent. This does **not** establish organizer provenance or the availability of the full cached feature stack. The separately required `.cache/gems_inputs` was absent; the older [cache audit](../evidence/input_cache_audit_9649dfc1.json) is historical, not a fresh download verification.
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) was reachable via GitHub API; [competition description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), and [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) could not be independently accessed under this environment's host allowlist. No live leaderboard or receipt was retrieved.
- The claimed GEMSDOE32 0.2778 is not an organizer-confirmed score. [Explanation](WHY_0_2778.md): sparse, separated predictions can reduce redundant prediction mass under a distance-tolerant metric; causation and superiority are not established. Different user-reported leaderboard values lack dated receipts and may refer to different dates.
- The previously catalogued [ranked hypotheses](HYPOTHESES_20261028_9649DFC1.md) are research leads, not established novel or presently viable candidates. External coverage and access have not been verified. Do not promote them as validated.

**Next gates:** obtain an explicitly assigned method lane; recover provenance- and rights-verified cached data; resolve the dense-raster interpretation and refresh the registry; preregister up to three experiments; use the shared evaluator and writer, buffered whole-segment holdout with visible-only features, individual canaries, surface and final-dot registry checks, and a paired comparison against the current holdout best. Only a separate selector may authorize a weekly slot. This environment cannot authenticate or fetch the organizer portal or other non-allowlisted hosts; no claim of autonomy beyond those constraints is justified.

## Run card

```json
{
  "hypothesis": null,
  "mechanism": null,
  "named_non_fault_mimic": null,
  "holdout_dti": null,
  "holdout_evaluator_version": null,
  "withheld_positives": null,
  "holdout_95_ci": null,
  "surface_correlation_and_overlap_vs_registry": null,
  "final_dot_correlation_and_overlap_vs_registry": null,
  "raster_sha256": null,
  "validator_output": null,
  "submission_name": null,
  "note": null,
  "verdict": "negative",
  "reason": "No assigned lane, candidate or experiment; no submission cleared."
}
```
