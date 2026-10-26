# GEMSDOE92 repository review — Arena branch `arena/0c5d848e-gemsdoe92` — 2026-10-26

## Executive decision

**No new GeoTIFF was generated; do not submit any artifact from this review.** The repo contains several downloadable research TIFFs, but none is cleared under its own promotion rules. The most prominent new research artifact in the nine-site summary is the SALEMSEISMO TIFF; its result is negative for promotion and the repository's literal full-footprint registry witness independently makes every non-empty raster fail the stated `>70%` overlap stop. Format-valid does not mean submission-eligible.

The best reported score among the nine requested references is **GEMSDOE32 `h33-h33-2-b2`, 0.2778 (CLAIM)**. It is not an organizer receipt. The local pinned bytes are the exact R0 parent (`SHA-256 c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`) and the documented pixel algebra identifies it as the D2.8 skeleton with dots within 2 pixels of the mapped catalogue removed. That is a plausible reason this sparse candidate did better than denser relatives under the competition's asymmetric distance-weighted metric, but it is **not a causal explanation**: the hidden evaluation truth, exact organizer receipt and controlled submission comparisons are not available here. Its local HOLDOUT-DTI is only `0.004006 [0.003406, 0.004668]`, which does not reproduce the claimed leaderboard value and must not be interpreted as a forecast of it.

**No defensible leaderboard projection is a score.** The table below keeps the owner-reported claim, comparable local holdout and the separate claim-trained MODEL estimate distinct. Every MODEL estimate has ±`0.072244` LOO RMSE; it is an uncertain rank/score proxy fitted to historical site claims, not independent ground truth.

## Nine-site comparison

Source receipts: [`focus9_executive_audit_20261026.json`](../evidence/focus9_executive_audit_20261026.json), [`score_estimator_20261026.json`](../evidence/score_estimator_20261026.json), and the [nine-site executive web summary](focus9.html). HOLDOUT-DTI values below are the repository's common `gems57-pooled-hide-v2` audit (22,663 withheld positive pixels; 95% CI); the score claims are owner-reported and not organizer-confirmed. The operative uniqueness result is `NO` for each historical best: each overlaps another registry artifact above the stated 70% three-pixel limit. See the linked full site review for exact matching artifacts, pairwise results and SHA-256s.

| Site | Highest reported artifact | Reported score (CLAIM) | HOLDOUT-DTI [95% CI] | Historical MODEL estimate ± 0.0722 LOO RMSE | Unique vs registry? |
|---|---|---:|---:|---:|---|
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | `h25-1-dotted-h19-5-d1-5` | 0.2477 | 0.090296 [0.079385, 0.102871] | 0.1647 | **NO** |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | `dotted-h19-5-d2-8` | 0.2600 | 0.093234 [0.082019, 0.105955] | 0.1408 | **NO** |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | 0.089959 [0.079128, 0.102269] | 0.1669 | **NO** |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | `h36-1-rung30-blind-r1` | 0.2710 | 0.027383 [0.024059, 0.030894] | 0.1915 | **NO** |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | `d28-poisson300m-offcat-44090` | 0.2600 | 0.093234 [0.082019, 0.105955] | 0.1408 | **NO** |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | `h27-4-solo-d28` | 0.2708 | 0.029358 [0.026029, 0.032708] | 0.1971 | **NO** |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | `h33-h33-2-b2` (R0) | **0.2778** | 0.004006 [0.003406, 0.004668] | 0.2519 | **NO** |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | `h33d-analog-tip-stepover-r30` | 0.2632 | 0.053143 [0.047148, 0.059510] | 0.1741 | **NO** |
| [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | `anderson-geothermal-pinn-38854` | 0.2750 | 0.004192 [0.003594, 0.004846] | 0.2476 | **NO** |

**Interpretation:** GEMSDOE25 and GEMSDOE30 are pixel-identical within the footprint despite distinct encodings/names; GEMSDOE28's `h27-4` and GEMSDOE31's `solo-d28` are likewise identical; R0 is the D2.8 support filtered by catalogue distance `>2 px`; GEMSDOE36 contains R0 plus 1,200 added points. These are correlated variants, not nine independent confirmations. GEMSDOE32's label is therefore a useful historical high-water mark, not evidence that the scientific mechanism independently generalizes. The holdout metric emphasizes catalogue-fault recovery and is not a direct test of newly discovered geothermal vents.

### What to download

- **For this review:** there is no newly generated file to download.
- A pre-existing research-only candidate is linked from [`focus9.html`](focus9.html): `h33-h33-2-b2-SALEMSEISMOcelftail52k-20261026-cc3c8ff2-zeros.tif`. Its recorded HOLDOUT-DTI is static `0.015948 [0.013683, 0.018370]` and strict draw-blind Rule-2 `0.099345 [0.084948, 0.113946]` (`gems57-pooled-hide-v2`, 22,663 withheld positives). The repository records a 0.6447 maximum overlap over its sparse operational registry, but the literal full-footprint witness remains 1.000; it is **not cleared to submit**. These are local holdout/registry measurements, not leaderboard estimates.
- The canonical byte-bound current-status feed (`docs/downloads/readiness.json`) points instead to the VARIO research TIFF and also says **DO NOT SUBMIT**. The homepage includes multiple dated lane summaries. Always heed the red status, not a download button or a format-pass badge.

## Verification passes

### Pass 1 — execute available checks

Created a local virtual environment from the checked-in `requirements.txt`; the environment is ignored and is not a repository deliverable.

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest tests -q` | **PASS:** 598 passed, 141 `PendingDeprecationWarning`s, 64.11 s. |
| `.venv/bin/python scripts/check_site.py` | **PASS:** 123 served rasters gated; primary link/readiness and raster gates pass. |
| `.venv/bin/python scripts/verify_manifest.py` | **PASS:** all 8 pinned manifest hashes verified. |
| `.venv/bin/python scripts/render_public_status.py --check` | **PASS:** primary bytes and first panel agree across public entry pages. |
| `git status --short --branch` before edits | **PASS:** clean on `arena/0c5d848e-gemsdoe92`. |

The run does not download or authenticate to competition systems and does not assert any organizer score. It also does not re-run the heavy geology experiments: the current-lane record already reports 3/3 experiments, and the supplied protocol caps work at three experiments.

### Pass 2 — edge cases and irregularities

1. **Multiple status layers:** `docs/downloads/readiness.json` and `current_submission.json` both resolve to VARIO and both prohibit submission; the homepage also contains additional dated AKCD/SALEMSEISMO research cards, while `focus9.html` presents SALEMSEISMO as its session artifact. The website checker verifies the primary readiness source and first panel, but these secondary historical/current-lane panels can still confuse a reader. No source is silently rewritten in this review; status arbitration should be made a deliberate shared-source change.
2. **Dense-witness uniqueness stop:** the pinned full-footprint witness makes the literal forward-overlap threshold fail for any nonempty in-footprint raster. This is a project-policy reading, not a claim that the candidate is identical to that dense raster in a scientific sense. Until the rule owner changes this policy, do not mark a candidate eligible.
3. **Score evidence:** the nine historical scores, plus the user's `0.3195`/`0.4413` snapshots, are not connected here to organizer submission receipts. The MODEL outputs are trained on submitted/claimed history and have substantial uncertainty. No current official leaderboard rank is confirmed by this review.
4. **Scope of holdout:** whole-segment hide-and-recover measures recovery of withheld catalogue labels under the local evaluator. It cannot establish new geothermal-vent discovery or replace organizer evaluation.
5. **Site page generation:** `scripts/render_focus9_page.py` regenerates `docs/focus9.html` from committed JSON; running it reproduced the tracked page bytes. No TIFF, score card, candidate or experiment was produced by this review.

### Pass 3 — requirements and next steps

- **Unique, submission-cleared TIFF:** not achieved. The most recent SALEMSEISMO research TIFF is available only as a research artifact; do not submit it.
- **Automatic validation:** existing artifact checks are automated and passed on the site, but format checks alone do not establish science, uniqueness or competition acceptance.
- **Candidate hypotheses:** the ranked five-item screen already exists at [`HYPOTHESES_20261026_SITE_REVIEW.md`](HYPOTHESES_20261026_SITE_REVIEW.md). Its top idea, LOCAL-WAVENUMBER-CONSENSUS, remains explicitly unvalidated; its holdout was correctly not run after the pre-placement stop. Do not describe a proposed idea as a tested score improvement.
- **Near-term engineering:** converge the dated lane panels and machine-readable readiness into one generated status source; add CI coverage for all prominent status panels and ensure no secondary page labels a negative artifact as eligible.
- **Scientific next work:** if the policy owner permits a future run and assigns a single method paragraph, stage the pinned data stack, apply pre-placement registry/canary checks, reuse the shared evaluator/writer, and test the top pre-registered candidate under the remaining experiment budget. Do not bypass the duplicate stop or spend a weekly slot without a positive paired holdout against the current comparable control.
- **External sources/access:** source links for human review are listed below. No external competition or USGS page was fetched during this review. DrivenData's data and submission receipts require authorized access; this environment cannot supply that login. Scores stay CLAIM unless an actual organizer receipt is recorded.

## Sources for manual review

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (authentication required according to repository records)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN survey record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR INGENIOUS submissions](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) and [USGS 3D Hydrography Program](https://www.usgs.gov/3d-hydrography-program)
- Local evidence: [`SITE_REVIEW_20261026.html`](SITE_REVIEW_20261026.html), [`focus9.html`](focus9.html), [ranked hypothesis screen](HYPOTHESES_20261026_SITE_REVIEW.md), [SALEMSEISMO run card](../evidence/salemseismo_run_card.json), and [site-review run card](../evidence/review_20261026_gemsdoe_sites_run_card_v2.json).

## Machine-readable review card

```json
{
  "review_date": "2026-10-26",
  "branch": "arena/0c5d848e-gemsdoe92",
  "hypothesis": "Repository audit of the nine-site benchmark; no new geological method selected",
  "mechanism": "Historical high scores track correlated variations of a thinning/skeleton prediction family; this is an observational explanation, not causal validation",
  "named_non_fault_mimic": "Lithologic contacts or survey artifacts can mimic geophysical lineaments; no new feature was generated in this review",
  "holdout_dti": "NOT RUN in this review; historical artifacts use gems57-pooled-hide-v2 and 22,663 withheld positives as recorded in the cited evidence",
  "correlation_overlap_vs_registry": "Historical focus artifacts fail at least one operative pairwise uniqueness comparison; literal full-footprint witness overlap is 1.000 for any nonempty candidate by repository policy",
  "raster_sha256": null,
  "validator_output": "No new raster created. Existing repository site check passed its 123 served-raster format gates; this does not grant submission eligibility",
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative",
  "weekly_slots_used": 0
}
```
