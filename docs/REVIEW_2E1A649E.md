# Repository closeout review — `2e1a649e` (2026-10-25)

## Executive decision

**✅ Current artifact is easy to download and format-valid for research. ⛔ It is not safe or recommended to submit. No new TIFF was generated.**

[Current research GeoTIFF](downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif) (**DO NOT SUBMIT**) · [one-TIFF ZIP](downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.zip) · [format audit](downloads/gemsdoe92-drainageknick-20261025T120000Z-audit.json) · [machine status](downloads/current_status.json) · [source audit](downloads/review_2e1a649e_sources.json).

The requested new, unique, submission-cleared GeoTIFF is **unfulfilled by design**, not silently substituted. A fresh mandatory pre-placement measurement proved that the pinned public witness is positive at every possible candidate coordinate. Under the user's literal rule, every nonempty raster has 3-pixel forward overlap `1.0 > 0.70`; placement must stop. Generating a nominally “new” nonempty file after that finding would violate the workflow, while an empty raster would not be a geological prediction. Experiments: `0/3`; weekly slots: `0`.

This result preserves the project values: **Maximize P(Win)** by not wasting a scarce slot, and **Own the Outcome** by exposing an impossible gate rather than presenting a format-valid file as eligible.

## Requirement disposition

| Requirement | Result |
|---|---|
| Start from the durable prompt and inspect the full chain | Completed: `SESSION_PROMPT.md`, README/site, manifests, restoration, models, holdout evaluator, writer, validator, registry logic, evidence, CI, tests, and GitHub state were reviewed. |
| Rank 3–5 untried geological avenues before implementation | Completed: five precise, unimplemented operators are frozen in [the hypothesis register](HYPOTHESES_20261025_REVIEW2E1A.md), each with layers, transform, mechanism, novelty, mimic/falsifier, value, cost, and source needs. |
| Run literal pre-placement uniqueness before placement | Completed and failed closed: all `5,167,373` footprint pixels are positive in the pinned witness; forced overlap `1.0`. |
| Validate the top candidate with leakage checks and blocked hide-and-recover | Not run because Rule 1 stopped before experiment 1. No surface, labels, placement, AUC, or DTI was computed. |
| Generate one newly named, unique GeoTIFF through the shared writer | Not permitted after the universal stop; no copied, renamed, empty, or post-stop TIFF was created. |
| Automated exact-file validation | Completed on the existing DRAINAGE-KNICK research artifact; finite, single-band `float32`, `[0,1]`, exact sample CRS/shape/transform, zero outside footprint. |
| Registry gate and promotion decision | Failed: overlap `1.0`; `verdict: negative`; `submission_eligible: false`; no selector or upload. |
| One name/note ≤140 characters | Preserved as record-only metadata from the existing artifact; note length `131/140`. It is not an upload recommendation. |
| Exactly one run card | `evidence/review_2e1a649e_run_card.json`, byte-mirrored for Pages; reproduced once at the end of this review. |

## Pass 1 — reproduce the workflow and stop at the first binding gate

### Chain inspected

1. **Inputs/provenance:** both manifests, parent recipe, restoration script, cached/pinned source blobs, sample, catalogue, feature and auxiliary layer references.
2. **Model/evaluation:** lane builders, `vendor/gems57/evaluate_holdout.py`, metric implementation/tests, visible-only rebuild conventions, leakage canaries, and historical run cards.
3. **Packaging/validation:** `vendor/gems57/submission_writer.py`, project gates, exact-reread hashes, zeros-outside encoding, site checker, and CI.
4. **Registry/promotion:** literal overlap/rank-correlation rules, surface/final-dot receipts, selector separation, ledger, current site declarations, and GitHub PR/Pages state.

Validation inputs were restored from `registry/session_manifest.json` and hash-verified. The full feature stack was intentionally not restored or used: the gate below needs only the sample grid and pinned witness and must run before geological feature placement.

### Fresh pre-placement result

The witness was freshly retrieved from GitHub at pinned commit/blob identity and rehashed as:

- SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`
- bytes `25,065,181`
- exact sample grid: yes
- valid footprint: `5,167,373` pixels
- positive witness support in footprint: `5,167,373`
- **REGISTRY-MEASUREMENT:** every possible nonempty candidate has forward overlap `1.0 > 0.70`

`scripts/preflight_dense_witness.py` exited nonzero and wrote [the receipt](downloads/review_2e1a649e_preflight.json). This is a universal support proof, not a full-registry scan and not a candidate correlation. It is sufficient to reject. Rank correlation is undefined until a candidate surface exists and, in any event, passing `|rho| <= 0.90` cannot override failed overlap.

The existing DRAINAGE-KNICK TIFF was then checked as an exact file, not treated as a new deliverable:

- raster SHA-256 `ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910`
- **REGISTRY-MEASUREMENT:** forward overlap `1.0`
- full-footprint Spearman `0.0400283664`
- exact-format gates: pass
- decision: duplicate stop / research only

See [the exact-file receipt](downloads/review_2e1a649e_drainage_witness.json). The broader historical public scan remains incomplete: it inventoried `1,455` unique blobs but downloaded only `750`, with `705` download failures. It is not represented as a complete registry characterization; the independently pinned full-footprint witness alone is enough to stop.

### Ranked untried avenues

Frozen priority is **STRIP-INPAINT**, **SPECTRAL-FABRIC-ROTATION**, **DRAINAGE-HANDEDNESS**, **RADIOMETRIC-MASS-BALANCE**, then conditional **GRAVITY-CLOSURE**. The last is explicitly nonviable if B15 basement depth proves derived from B13 gravity, because that would make its apparent closure circular. Detailed transforms, competing processes, falsifiers, costs, and source constraints are in the [pre-implementation register](HYPOTHESES_20261025_REVIEW2E1A.md).

Had Rule 1 passed, only STRIP-INPAINT would have entered experiment 1. Its continuous surface and final support would first face the registry. Every B2/B13/B12 feature would then be tested alone; symmetric AUC above `0.90` would stop as suspected leakage. Whole fault segments plus buffer would be withheld; every learned transform and catalogue-dependent placement step would be rebuilt from training space and visible faults only; visible faults would be masked pixel-exactly. Pooled DTI would use `alpha=0.2`, `beta=0.8`, a `300 m` triangular kernel, the shared evaluator, withheld-positive count, and spatial-bootstrap 95% CI. None of those measurements was fabricated after the earlier stop.

## Why reported GEMSDOE32 `h33-h33-2-b2` may have worked — and what is not known

The owner-supplied historical ledger records this progression, all as **CLAIM** with `receipt=N`: H19-5 `121,131` pixels / `0.1922`; D1.5 `60,069` / `0.2477`; D2.8 `44,090` / `0.2600`; SOLO-D2.8 `40,199` / `0.2708`; R0 `37,654` / `0.2778`. Fresh local geometry confirms that the support became much less crowded: median nearest-neighbour distance rose from `1.0` to `3.0` pixels, and footprint area within 3 pixels of the mask fell from `0.196095` to `0.150853`. R0 also removed all dots at catalogue distance `<=2` pixels.

That gives a plausible metric mechanism. The distance-weighted truth credit takes a maximum over nearby predictions, so highly clustered dots can pay additional prediction mass without adding equal truth credit. Spacing toward the 3-pixel kernel radius and pruning visible-catalogue-adjacent dots can improve credit density at fixed/declining support. It can also redirect budget toward off-catalogue geometry. This is **not** a theorem that every nearby dot is redundant: two nearby dots can cover different truth pixels, and repository regression tests preserve that counterexample.

The causal story is not organizer-verified. The freshly retrieved, commit-pinned GEMSDOE32 page calls H33-2-B2 `UNSCORED`, reports a `0.2708` base and a projected `0.2747`, and states that no organizer score exists in that repository. Thus `0.2778` remains a user/ledger **CLAIM**, not `ORGANIZER-CONFIRMED`. Its local SGMC **PROXY** did not rise with the claimed score (`0.100603` at raw H19-5 versus `0.096060` at R0), so the evidence does not support “it found more real faults” as a demonstrated explanation. The prompt's conflicting current-leader values `0.3195` and `0.4413` are also unverified here; the live leaderboard was inaccessible.

**Can it be improved?** Possibly in principle, but this review supports no numerical score claim. DRAINAGE-KNICK's carried-forward **HOLDOUT-DTI** is `0.061728 [0.047046, 0.075316]` with evaluator `gems57-pooled-hide-v2`, `22,663` withheld positives, below the comparable recorded bar `0.113316`. It is a surrogate against withheld mapped faults, not an organizer score or direct geothermal-productivity validation. The five untried operators have unknown sign and effect size. Repeated selection on the same holdout would itself overfit; any future protocol should preserve a locked outer spatial test.

The freshly hash-verified organizer reference notebook confirms the training-loss alpha/beta configuration but does not authenticate this repository's holdout as organizer scoring code. Verified GitHub URLs, blob identities, SHA-256 values, and authority limits are in [the source audit](downloads/review_2e1a649e_sources.json). Manual official links (not live-verified in this restricted sandbox): [problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), and [GDR #1391](https://gdr.openei.org/submissions/1391).

## Pass 2 — adversarial review, defects, and fixes

1. **Stale manifest sizes were not gated.** `gems.manifest.verify` checked hashes but ignored a present `bytes` claim. `registry/data_manifest.json` said `355000` for a `355443`-byte R0 NaN file and `1600000` for a `1595850`-byte H27 file. Hashes were already correct. The shared verifier now rejects recorded size drift; both counts are corrected and regression-tested.
2. **The first screen and machine primary disagreed.** README opened with DRAINAGE-KNICK, while the sole `data-primary=true` still selected historical COULOMBDM. A deterministic renderer now writes the authoritative warning to README, homepage, executive summary, and canonical submission guide. DRAINAGE-KNICK is the sole machine current research artifact, explicitly not slot-eligible.
3. **The historical DRAINAGE audit lacked the generic site schema.** Its original build fields remain untouched. Additive reconciliation fields now bind exact TIFF hash, canonical format gates, current negative verdict, prior run card, and fresh public-witness rejection. `registry/current_status.json` is byte-mirrored to Pages and cross-checked against the primary, run card, evidence paths, and eligibility.
4. **Historical language could be read out of order.** Old session blocks remain for provenance, but the new current-decision block is first and uses the unambiguous pair “OK TO DOWNLOAD FOR RESEARCH” / “DO NOT SUBMIT.” Page titles no longer call COULOMBDM current.
5. **The durable review and selector queue were stale.** `REVIEW_CURRENT.md` and `NEXT_STEPS.md` previously opened with KNICKLOQO/dual-reading promotion language. Both now open with this literal-stop decision and mark all older queues as archived; the only conditional experiment is STRIP-INPAINT after an explicit future rule change.
6. **No loophole was used.** No all-zero file, copied raster, renamed historical TIFF, post-stop feature experiment, projected score, fake registry completion, or automatic weekly selector was introduced.

## Pass 3 — complete requirement re-check

The clean full pass completed after all fixes:

- `make manifest`: **8/8 inputs OK**, now including enforced recorded byte lengths.
- `make verify`: parent R0 hash, byte encodings, `37,654` dots, mass, footprint, minimum catalogue distance, and 3/4/5-pixel collars remeasured and matched.
- `make ledger`: `93` rows, **no organizer receipt**.
- `pytest tests -q`: **375 passed**, `126` nonfatal Rasterio/Affine deprecation warnings.
- `scripts/render_current_review.py --check`: authoritative root/README/public-page rendering matches the evidence.
- `scripts/check_site.py`: **63/63 served GeoTIFFs passed** automated raster/format gates; DRAINAGE-KNICK is the byte-matched machine primary and remains negative.
- JSON/mirror consistency, source/run-card hashes, exactly one machine primary, no duplicate HTML IDs, conflict-marker scan, and `git diff --check`: pass.

These are reproducibility and format results, not an organizer score or upload acceptance. Automated code reread the TIFFs; no visual/human inspection was used. The only eventual human action left would be choosing and uploading an eligible file, but this review produced none and recommends no slot.

### Remaining limitations and next work

1. The requirements are contradictory under the pinned witness: “new nonempty TIFF” and “literal overlap `<=0.70`” cannot both hold. Only an explicit future specification decision can resolve that; code must not silently substitute matched-budget semantics.
2. If the literal rule remains, every nonempty candidate remains a negative and no geological experiment should run. If the owner explicitly changes the rule, assign one lane and start with STRIP-INPAINT under the frozen blocked protocol—not all five.
3. Verify the competition stack's official provenance, descriptions, and data-use permission before calling the owner mirror authoritative. Hash pins prove identity only.
4. Obtain actual organizer receipts, current leaderboard state, and weekly cap from an authenticated human upload flow. This project has no such receipt and spent no slot.
5. Complete registry acquisition only if full characterization is needed; do not erase the `705` failures. They do not weaken the existing rejection proof.
6. GitHub Pages publication mode/protection remains a deployment limitation; local and CI checks validate repository bytes, not necessarily an already-deployed legacy site revision.

## Final JSON run card

```json
{
  "schema": "gemsdoe92-run-card.review-2e1a649e.v1",
  "reviewed_utc": "2026-10-25T14:45:38Z",
  "scope": "Repository review and mandatory pre-placement registry gate; no new geological lane was assigned or executed.",
  "hypothesis": "The standing literal registry rule makes every nonempty in-footprint candidate a duplicate because one pinned registry raster has positive support on the entire valid footprint.",
  "mechanism": "The witness support contains every valid candidate coordinate; its 3-pixel halo therefore contains every possible nonempty candidate dot set, forcing literal forward overlap to 1.0.",
  "named_non_fault_process_that_could_mimic_it": "A space-filling continuous probability background; this is a registry-representation degeneracy, not evidence that two geological models share a fault mechanism.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "session_status": "Not rerun: Rule 1 stopped before feature construction and placement; zero new experiments.",
    "carried_forward_artifact": "DRAINAGE_KNICK generated in prior PR #78",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positives": 22663,
    "dti": 0.06172760041972649,
    "ci95": [
      0.04704647590617514,
      0.07531604288537347
    ],
    "source": "evidence/gemsdoe92-drainageknick-20261025T120000Z_run_card.json",
    "promotion_bar": 0.113316,
    "beats_promotion_bar": false,
    "caveat": "Carried forward exactly from the prior run card; not a current rerun and not an organizer score."
  },
  "correlation_overlap_vs_registry": {
    "evidence_class": "REGISTRY-MEASUREMENT",
    "preplacement": {
      "scope": "Single pinned witness; rejection only. No candidate surface was generated or scored.",
      "witness_sha256": "ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be",
      "footprint_pixels": 5167373,
      "witness_positive_in_footprint": 5167373,
      "forward_overlap_for_any_nonempty_candidate": 1.0,
      "threshold": 0.7,
      "stop_required": true
    },
    "existing_artifact_exact_file_check": {
      "candidate_sha256": "ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910",
      "forward_overlap_within_3px": 1.0,
      "spearman_full_footprint": 0.040028366426527635,
      "stop_required": true,
      "scope": "Single witness: rejection only, no full-registry or pre-placement clearance."
    }
  },
  "raster_sha256": "ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910",
  "raster_status": "Existing prior-session DRAINAGE_KNICK research artifact; no file copied, renamed, or generated in this review.",
  "file": "docs/downloads/gemsdoe92-drainageknick-20261025T120000Z-zeros.tif",
  "validator_output": {
    "no_nan_in_footprint": true,
    "values_in_0_1": true,
    "crs_shape_transform_match": true,
    "dots": 37654,
    "checks": {
      "single_band": true,
      "dtype_float32": true,
      "dimensions_3730x3292": true,
      "crs_epsg_32611": true,
      "transform_matches_sample_submission": true,
      "no_nan_anywhere": true,
      "no_inf_anywhere": true,
      "no_sentinel_values": true,
      "range_0_1_guaranteed": true,
      "min_ge_0": true,
      "max_le_1": true,
      "in_footprint_all_finite": true,
      "in_footprint_range_0_1": true,
      "outside_footprint_zero": true,
      "zero_dots_on_mapped_catalogue": true
    }
  },
  "submission_name": "GEMSDOE92-DRAINAGE_KNICK-20261025",
  "note": "h33-h33-2-b2; DRAINAGE_KNICK: terrain-knick persistence x basement edge x shear; 37654 dots d_cat>2px; see run card for HOLDOUT-DTI",
  "note_chars": 131,
  "verdict": "negative",
  "submission_eligible": false,
  "new_unique_tiff_generated": false,
  "requirement_status": "UNFULFILLED: generating a nonempty candidate after the pre-placement stop would violate the standing protocol.",
  "experiments_used": "0/3",
  "weekly_slots_used": 0,
  "organizer_confirmed": null,
  "evidence": {
    "preplacement": "evidence/review_2e1a649e_preflight.json",
    "exact_artifact_witness": "evidence/review_2e1a649e_drainage_witness.json",
    "sources": "evidence/review_2e1a649e_sources.json",
    "ranked_hypotheses": "docs/HYPOTHESES_20261025_REVIEW2E1A.md"
  },
  "limitations": [
    "No new submission-cleared TIFF can be produced under the simultaneous nonempty-artifact and literal-overlap requirements.",
    "The DRAINAGE_KNICK public scan downloaded only 750 of 1455 inventoried unique blobs; the pinned full-footprint witness is sufficient for rejection but not full-registry characterization.",
    "No organizer receipt, current leaderboard, current weekly cap, or authenticated submission-page acceptance was available.",
    "GitHub Pages remains in legacy main-root mode; workflow publication protection is not verified active."
  ]
}
```
