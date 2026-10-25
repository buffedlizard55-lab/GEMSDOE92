# Three-pass repository review — 2026-10-25

## Decision at a glance

**No new TIFF was created. Existing TIFFs are downloadable as research artifacts only. DO NOT SUBMIT any file or spend a weekly slot under the current literal registry rule.** The user's requested new submission-cleared artifact cannot be produced without violating the higher-priority stop gate: one pinned public registry raster is positive at every footprint cell, so every nonempty in-footprint candidate has literal forward overlap `1.0`, above the `0.70` limit. The reproducible pre-placement receipt is [`review376a_preflight.json`](downloads/review376a_preflight.json); the governing review is [`REVIEW_376A8469.md`](REVIEW_376A8469.md). This is an explicit blocker, not a claim that a TIFF was generated or cleared.

The project does contain prior research TIFFs. Their on-disk format validation does **not** make them eligible. In particular, an exact hash mismatch (“byte-unique”) is not the same as passing the geometric overlap rule. The reported `GEMSDOE32` `0.2778`, supplied leaderboard figures `0.3195` / `0.4413`, and sibling site values remain user-reported claims unless accompanied by an organizer receipt. The pinned GEMSDOE32 page and its build notes described in the governing review reportedly identify that parent as unscored; no organizer score receipt was found in this checkout. No responsible inference can guarantee a higher hidden-label competition score from these values.

## Pass 1 — inspect and reproduce

- Read `README.md`, `SESSION_PROMPT.md`, `docs/REVIEW_CURRENT.md`, `docs/REVIEW_376A8469.md`, `docs/NEXT_STEPS.md`, the pinned input manifest, shared evaluator/writer/uniqueness tools, public site, and the recent run cards.
- The checkout is on the required `arena/17630c39-gemsdoe92` branch and was clean before review. No branch change was made.
- The feature cache `.cache/gems_inputs/` is absent. `data/bridge/` contains only eight small bridge/parent rasters; it is not the full 19-band feature stack. Thus a fresh full geological holdout experiment could not be claimed from the available inputs.
- Existing RADIOCONTACT run card `evidence/gemsdoe92-radiocontact-20261025T041646Z_run_card.json` reports **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives) `0.005066 [0.003638, 0.006583]`, below its recorded **HOLDOUT-DTI** promotion reference `0.113316`; its local-only uniqueness is not global registry clearance (`public.available: false`). No fresh evaluation was run in this review.
- During PR preparation, `main` advanced with a separate LISTRICDIP lane, which was merged into this working branch to remove PR conflicts. Its existing run card reports **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, static `d_cat > 2` instrument) `0.005420 [0.004294, 0.006551]`; it is below the recorded **HOLDOUT-DTI** repository reference `0.010788` (KNICKLOQO static) and has literal dense-witness overlap `1.0`. It remains a research artifact and was not generated or re-evaluated by this review. Its run-card provenance is `evidence/listricdip_run_card.json`.
- A future-dated file `docs/HYPOTHESES_20261026_RADIOCONTACT.md` states it was preregistered before a run-card dated 2026-10-25. Since the document date is after this review date, that chronology is not independently established and is an irregularity for review. Do not treat it as verified preregistration evidence.
- Ranked fresh candidate concepts (not implemented) and named mimics/falsifiers are in [`HYPOTHESES_20261025_REVIEW.md`](HYPOTHESES_20261025_REVIEW.md). They use the existing stack, so no additional free official source is required; the stack itself is not currently staged, and mirror rights/origin remain unverified.
- Why the reported 0.2778 may have arisen: local parent lineage notes characterize R0 as a spaced/thinned fault-skeleton descendant, plausibly reducing redundant predictions under the distance-weighted matching kernel while retaining proximity to mapped faults. This is a plausible mechanism, not a verified causal explanation of an organizer score. Beating that claim requires true additional hidden-fault recovery without excess false positives; no competition receipt or outer-test evidence proves this repo can do so.

### User-requested candidate shortlist — order reflects complementarity and cost, not score projections

The first proposal is RTP magnetic texture displacement registration (B2); second is RTP level-set topology (B2); third is neighboring-basin divide migration residual (B12/B19, conditioned by B15). Each identifies a fault-missing-catalogue mechanism and a named non-fault mimic in the linked hypothesis file. Expected improvement is **unknown**; no projected score is made. The requested top-candidate validation was blocked *before implementation* by the literal pre-placement uniqueness stop. This complies with “validate before a slot” while preserving the stricter instruction to stop on a duplicate. No slot was touched.

## Pass 2 — assumptions, conflicts, and edge cases

- **Critical policy conflict resolved conservatively:** the task asks for a unique TIF, while the inherited protocol's literal registry overlap stop makes every nonempty raster fail. We do not reinterpret the protocol as matched-budget eligibility, skip the witness, use an empty/meaningless raster, or relabel an existing candidate. A human/policy owner must explicitly revise that rule before this failure can be addressed scientifically.
- The README's previous first-screen artifact is DRAINAGE-KNICK, while `docs/REVIEW_CURRENT.md`, the newest session banners, and the literal-gate review contain different dates and candidates. The page also contains historical “unique” language based on non-operative matched-budget readings. A new top-of-page banner and README warning now state the binding decision and distinguish “download for research” from “OK to submit.” Historical receipts remain untouched.
- The prompt provides historic score figures, but no organizer-page receipt in `ledger/` verifies them. Do not place a private holdout number in a “score” field.
- Format and eligibility are independent. All TIFs that the site validator currently serves may be technically valid [0,1] GeoTIFFs yet still fail the literal registry gate or scientific promotion bar.
- Official non-GitHub pages were not live-verified in this review. The URLs are provided for manual review only. GitHub-owner mirrors and checksums are not proof of organizer authentication, license, or permission to redistribute competition data.

## Pass 3 — final verification and residual work

After the documentation/status changes:

- `PYTHONPATH=vendor .venv/bin/python -m pytest tests -q`: **371 passed**, 126 upstream Rasterio/Affine pending-deprecation warnings (final post-merge rerun).
- `PYTHONPATH=vendor .venv/bin/python scripts/check_site.py`: **66 served TIFFs passed** current site format gates (final post-merge rerun).
- `PYTHONPATH=vendor .venv/bin/python -m gems parent --recipe registry/parents/R0.json --data-root data`: pinned parent R0 verified.
- `PYTHONPATH=vendor .venv/bin/python -m gems manifest --manifest registry/data_manifest.json --data-root data`: all eight staged manifest entries passed.
- `PYTHONPATH=vendor .venv/bin/python -m gems ledger`: **97 rows**, best organizer receipt: **none**.
- No fresh holdout, model score, public registry scan, or organizer receipt was produced. No TIF bytes or weekly slot were changed. External official pages and current leaderboard were not fetched.

## Remaining work, ordered by decision value

1. Resolve the literal rule versus universal dense-witness collision explicitly; otherwise do not generate a candidate or spend a weekly slot.
2. Obtain/recheck the authorized competition feature stack and its allowed-use terms. The current checkout lacks the full stack; pinned mirror byte hashes alone do not settle source authenticity or redistribution.
3. If and only if a valid protocol change permits research, select exactly one lane, freeze an outer spatial test and comparable control, then use shared cached features/evaluator/writer and leakage canaries. Keep the experiment budget (3 runs / 2 hours) and do not choose a weekly slot in the experiment phase.
4. Correct stale historical “unique” labels as they are next touched; preserve old logs as historical rather than rewriting their past evidence.
5. Verify the actual leaderboard, score receipts, and weekly cap through the official authenticated competition page before asserting current values or selecting a slot.

Official links supplied for review, not live-verified here: [problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [about](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/), [data/login](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7), [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [EPSG:32611](https://epsg.io/32611).

**Core values:** **Maximize P(Win)** means preserve scarce entries and do not claim unsupported results. **Own the Outcome** means documenting the blocker, preserving negative evidence, keeping automated validation and provenance visible, and clearly identifying what access or governance decision is needed next.


## Run card (no candidate generated)

Machine-readable: [`evidence/repository_review_run_card.json`](../evidence/repository_review_run_card.json). `null` means not measured, not zero.

```json
{
  "hypothesis": "RTP magnetic texture displacement registration (Band 2); untested proposal.",
  "mechanism": "Bidirectional multi-window magnetic texture registration tests stable signed offset across trial fault lines.",
  "named_non_fault_process": "Intrusive/lithologic contacts or separate volcanic flows can mimic translated magnetic texture.",
  "holdout_dti": {"evaluator_version": "gems57-pooled-hide-v2", "withheld_positives": null, "value": null, "ci95": null, "status": "NOT RUN; pre-placement duplicate stop and feature stack absent."},
  "correlation_overlap_vs_registry": {"candidate_spearman": null, "candidate_dot_overlap": null, "witness_literal_overlap_for_any_nonempty_candidate": 1.0, "threshold": 0.70},
  "raster_sha256": null,
  "validator_output": {"candidate_generated": false, "no_nan_inside_footprint": null, "values_in_0_1": null, "crs_shape_transform_match": null},
  "submission_name": null,
  "note": "No candidate generated; literal registry gate stops every nonempty raster.",
  "verdict": "negative"
}
```
