# Candidate handoff — human review and submission only

**Do not upload until you confirm the weekly quota and independently review the
selected raster.** The agent does not submit and never contacts the leaderboard.
The parent score `0.2778` is an owner-reported **CLAIM**, not a receipt-backed
score; there is no receipt in this checkout.

## SNAP candidates built this session (2026-10-23)

All three carry 37,654 unit-mass dots, differ from R0 only in dot positions, and
hold the parent's 2.83 px minimum spacing. Each pair is one experiment: **upload
only one file per slot** (NaN primary, or the zeros fallback if the uploader
rejects NaN — they score identically).

| Order | Primary raster (NaN outside) | Fallback (`-zeros.tif`) | Dots moved | NaN SHA-256 | Form note (≤140 chars) |
|---|---|---:|---|---|
| 1 | `releases/h33-h33-2-b2-SNAPcap2p0-g0p15-20261023-2ca4294e.tif` | `…-2ca4294e-zeros.tif` | 2,660 (7.06%) | `2ca4294e4401c6677e55ec498b08a91b06b23a431773d2245798cbc15f1d5be4` | `h33-h33-2-b2; SNAP 2660 dots (7.1%) <=2px to edge max, gain>0.15; count 37654 held; pred MODEL:±0.008` |
| 2 | `releases/h33-h33-2-b2-SNAPcap2p0-g0p10-20261023-f4e8c114.tif` | `…-f4e8c114-zeros.tif` | 7,023 (18.65%) | `f4e8c1147fb1f4178f376f99dda84228dd58fa76e5216de45cfbdac9888d40cc` | `h33-h33-2-b2; SNAP 7023 dots (18.7%) <=2px to edge max, gain>0.10; count 37654 held; pred MODEL:±0.015` |
| 3 | `releases/h33-h33-2-b2-SNAPcap2p0-g0p05-20261023-2c472bc5.tif` | `…-2c472bc5-zeros.tif` | 19,565 (51.96%) | `2c472bc50e2869b044963ad67e41c4c21e597d9f456aefc5e05b2a65883a9cce` | `h33-h33-2-b2; SNAP 19565 dots (52.0%) <=2px to edge max, gain>0.05; count 37654 held; pred MODEL:±0.035` |

`SLOT_PLAN.md` orders these against the PRUNE rungs; the slot order there is the
recommendation, not an instruction.

## Format receipt (re-read from disk after writing)

Per file, `python -m gems validate <file> --reference
data/bridge/sample_submission.tif --catalogue data/bridge/existing_faults.tif`:

- PASS — CRS EPSG:32611, shape 3730×3292, transform identical to
  `sample_submission.tif`, float32, one band, values in [0,1], no NaN inside the
  footprint, NaN outside the footprint (7,111,787 px) for the primary and 0.0 for
  the fallback, zero mass on catalogue pixels, sha256 re-read.
- **DECLARED DEVIATION — `distance_from_catalogue`:** 2,114 / 1,999 / 1,634 dots
  sit within 3 px of the catalogue. Every one of them is an **inherited R0 dot
  that did not move**; R0 itself has 2,171 such dots and scored the CLAIM 0.2778
  with them. No moved dot lands within 3 px (measured minimum for moved dots:
  3.16 px). Removing them would be a PRUNE change (4.3% of dots), which would
  confound this axis. See `IRREGULARITIES.md` 2026-10-23 (SNAP session).

## Mechanism and uncertainty

- **Hypothesis:** within the 300 m triangular kernel a dot earns credit only if it
  lands within ~3 px of a new-fault pixel; the parent's lineaments carry the
  100-300 m location error implied by 400 m flight-line spacing, so sliding
  poorly-positioned dots onto the local edge maximum recovers credit.
- **Mechanism:** TMI/gravity horizontal-gradient maxima and detrended-slope
  maxima sit where the property contrast across a fault projects to the surface.
  The response surface mixes three pinned bands (3 `tmi_hg`, gradient magnitude of
  13 `iso_grav_anom`, 19 `det_elev_slope`) at fixed a-priori weights
  0.40/0.35/0.25; it was **not** tuned on the catalogue.
- **Mimics:** lithologic contacts, intrusive margins, caldera ring fractures,
  palaeochannels, erosional scarps, road cuts. A magnetic gradient maximum can sit
  over the edge of the magnetised body rather than over the fault plane.
- **Prediction:** MODEL only, two-sided ranges above (see the mechanism card for
  the derivation from the calibrated DTI denominator D ≈ 19,900: one converted
  dot is worth ≈ +1.5e-4, so the sign is decided by whether the net conversion
  rate is above zero — which this model cannot resolve below 0.01).
- **Report-only diagnostics (never gates):** leakage canary on the edge response,
  symmetric AUC 0.569 at catalogue vs background (stop threshold 0.90 → no stop);
  the same response scores 0.633 at R0's dots vs background, i.e. R0 already sits
  on above-average edge response. SGMC off-catalogue PROXY deltas vs R0 are
  −0.00008 / −0.00015 / +0.00001. The catalogue hide-and-recover PROXY was **not**
  re-run: `IRREGULARITIES.md` records that this instrument is not
  decision-comparable (R0 0.004006, PRUNE rungs ≤0.0008, live scores uncorrelated
  −0.87…+0.54), and SNAP adds no mass, so it would restate the geometry only.
- **Falsifier:** if `g0.05` lands > 0.01 *below* both `g0.15` and R0, edge maxima
  are worse position estimators than the parent's own lineaments and SNAP is
  retired. If `g0.15` gains > 0.01, compose it onto the best receipt-backed parent.

## Reproduction

1. `pip install -r requirements.txt`.
2. `python scripts/restore_inputs.py` — restores every pinned input into
   `.cache/gems_inputs/`, verifying sha256 **and** byte length; the 419 MB
   19-band stack is required for the response surface.
3. `python scripts/make_edge_response.py` — writes
   `.cache/gems_inputs/snap_edge_response.npy` (deterministic, no labels).
4. `python scripts/build_snap_variants.py` — verifies every pin, asserts the R0
   invariants, builds and re-reads all six TIFFs, runs the gates, appends the
   ledger rows and writes `evidence/snap_session.json`.

**Public-repository safeguard:** `*.tif` is gitignored, so these candidate
rasters are **not** in the repository or the PR — retrieve them from the
workspace `releases/` folder or regenerate with step 4. Fill `receipt_score` and
`receipt_date` only from the human's submission-page receipt.
