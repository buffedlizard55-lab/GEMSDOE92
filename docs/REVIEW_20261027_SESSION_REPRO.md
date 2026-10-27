# Repository review and verification — 2026-10-27

## Decision

**DO NOT SUBMIT any current research TIFF. No new TIFF was generated.** This checkout has a pinned full-footprint registry witness that rejects every nonempty candidate under the current literal overlap rule (`1.000 > 0.70`). This review performed repository and engineering verification only: no surface, dot set, geological experiment, holdout, leakage canary, score estimate, or weekly slot was created or consumed. A file-format PASS does not override this stop.

The earlier, hash-bound three-pass audit remains the evidence source for the witness, the nine-site recheck, and restored input-cache measurements: [review](REVIEW_B4BB558B.md) · [run card](downloads/review_b4bb558b_run_card.json) · [pre-placement receipt](../evidence/review_b4bb558b_preflight.json). This document records the reproduction in the current checkout; it does not claim to have freshly downloaded organizer data or independently repeated the network fetch.

## Pass 1 — reproduce the working state

Installed the pinned project dependencies into ignored `.venv/`, then ran:

```sh
.venv/bin/python -m pytest tests -q
make manifest PYTHON=.venv/bin/python
make verify PYTHON=.venv/bin/python
PYTHONPATH=vendor .venv/bin/python scripts/check_site.py
```

Results:

- **Engineering tests:** 720 passed; 159 Rasterio `PendingDeprecationWarning` warnings; zero test failures.
- **Input manifest:** all 8 committed manifest entries passed.
- **Parent verification:** pinned R0 `h33-h33-2-b2` verified from committed bytes; 37,654 dots; minimum catalogue distance 2.2361 px. This establishes local byte/lineage integrity, not organizer score or current submission eligibility.
- **Site gate:** PASS; 123 served research rasters passed the repository's configured local format gates. This is not a portal acceptance receipt, uniqueness clearance, or performance result.
- Parsed the current status/run-card/cache/recheck JSON files and ran `git diff --check`; all passed.

## Pass 2 — inspect correctness, caveats, and prior claims

- Confirmed the entry-point status is unambiguous: **research download only; DO NOT SUBMIT**. The historical VARIO file and other served TIFFs are not promoted by this review.
- Confirmed `docs/focus9.html` provides a row for every requested site (24, 25, 27, 28, 30, 31, 32, 33, 36), links the historical research rasters, labels the reported values as owner **CLAIMs**, states per-file score estimates are unavailable, and states the uniqueness/eligibility failures. GEMSDOE32's `0.2778` is the highest of the user-supplied nine-site claims, not an organizer receipt.
- The plausible mechanism for the reported R0 value is reduced redundant predicted mass after thinning/catalogue-distance filtering while retaining nearby distance-kernel credit. It is a hypothesis about metric behavior, not a proven causal explanation for the reported score; the hidden labels, actual receipt and controlled organizer-score ablation are unavailable.
- Confirmed a known format-contract discrepancy is openly disclosed: official instructions referenced by the site call for null/NaN outside study bounds, while current local TIFFs use zero outside the finite footprint to avoid global `[0,1]` range failures. Local gates cannot prove those encodings are interchangeable or accepted by the portal.
- No score estimate is defensible: there is no receipt-bound training target set or calibrated exact-file prediction interval. Do not treat model, proxy, local holdout or public leaderboard snapshots as `ORGANIZER-CONFIRMED`.
- The available distinct hypothesis screen remains **conditional, not authorized or validated**. Its rank-1 `LOCAL-WAVENUMBER-CONSENSUS` uses magnetic/gravity derivative-ratio or depth-consensus features from the pinned stack; the named non-fault mimics include lithologic contacts, remanent volcanic bodies, and flight-line/processing artifacts. It differs from existing Euler and analytic-signal modules but is adjacent enough to require leakage/ablation testing. The remaining ranks are stream-planform offset, focal-mechanism/geodetic slip-plane consensus, signed seismic-gravity lag, and seasonal Landsat thermal persistence. Details, layers, risks, costs and official source links are in [the five-hypothesis screen](HYPOTHESES_20261026_SITE_REVIEW.md).
- Do not treat linked official URLs as evidence that AOI coverage, source access, source provenance, redistribution rights, or current competition terms were verified in this environment. The latest input-cache audit only binds owner-mirror bytes.

## Pass 3 — reconcile against the operating brief and next steps

The current request's demand for a nonempty, unique TIFF conflicts with the still-binding literal registry condition. A hash-verified raster is positive on every finite sample-footprint cell, so any nonempty candidate overlaps it by 1.000 before any 3-pixel expansion. The protocol therefore requires stopping before candidate-surface generation and placement; making an all-zero raster, changing a filename, or switching to a sparse-only comparison would not satisfy the submission goal. There is also no distinct method paragraph assigned in the current request. No lane or policy exception was invented.

Accordingly, this session did not run the top hypothesis on holdout: constructing a candidate after the unconditional stop would violate the stated procedure. HOLDOUT-DTI, feature-only AUC, candidate checksum, and a new submission name/note are **NOT RUN / NOT GENERATED**, not zero-valued results. Promotion to a weekly slot remains a separate selector decision, and no slot was used.

### Ordered remaining work

1. An authorized protocol owner must clarify the dense-raster-versus-dot-registry representation conflict without silently weakening the literal rule, and assign a single method paragraph.
2. Before any experiment, verify permitted competition-data provenance and the required outside-footprint encoding against current official instructions; the current mirror audit does not establish these.
3. Only if unblocked: use the common pinned feature stack, shared whole-segment buffered hide/recover evaluator and writer; derive catalogue features from visible faults only, exactly mask visible faults, pool DTI with alpha 0.2/beta 0.8 and the 300 m triangular kernel, and run each feature's leakage canary. Stop on AUC >0.90 until explained. Respect the three-experiment/two-hour budget.
4. Compare against a same-evaluator control with a paired uncertainty interval; then complete both pre-placement surface and post-placement dot uniqueness scans across a certified complete registry. Only after all gates pass may a separate selector check the authenticated weekly cap and any organizer receipt be recorded against exact file SHA-256.

## Sources and limits

The nine-site table and five-hypothesis screen retain links to the [official competition problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [USGS Landsat Collection 2 Level-2](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products), [USGS ComCat](https://earthquake.usgs.gov/fdsnws/event/1/), and [GDR INGENIOUS 1391](https://gdr.openei.org/submissions/1391). These are source pointers for review, not new retrievals in this checkout. The authenticated data tab, actual submission page, current weekly cap and score receipt were not accessed.

## Machine-readable run card

See [`evidence/review_20261027_session_repro_run_card.json`](../evidence/review_20261027_session_repro_run_card.json). Verdict is `negative` because the protocol pre-placement stop blocks candidate creation, not because a tested geological hypothesis scored poorly.
