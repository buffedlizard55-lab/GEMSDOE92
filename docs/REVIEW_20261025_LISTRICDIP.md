# Three-pass review — LISTRICDIP (2026-10-25)

## Pass 1 — implement and score

Pre-registered five hypotheses, implemented Rank 1 only, three arms, shared `evaluate_holdout.py` and `submission_writer.py`. No private fork of the metric. `spaced_top_mask` gained `require_full` in the shared `gems/breakline.py` (default still raises when short).

Results are in `evidence/listricdip_run_card.json`. `updip50` static HOLDOUT-DTI `0.005420 [0.004294, 0.006551]`. Verdict `negative`.

## Pass 2 — bugs, assumptions, edges

Fixed before the successful run, and re-checked after it:

- Antithetic direction is regional, not a lookup along the local gradient. The local lookup never opposes on a symmetric basin.
- Polarity is float64. `raw_mag` is a rank product. The float32 product overflowed.
- `cand_cap` for the up-dip crest is 1,500,000. 180,000 placed only 22,442 of 37,654 and aborted. No TIFF was written by that crash.
- Filename dot counts are taken from the mask after placement, not from the constant 37,654. Sibling audits record 9,571 and 9,555 so the site check does not demand 37,654.
- Rule-2 placement runs once per seed. The four folds of a seed share one visible catalogue.
- The unthinned `H19-5` control (0.066289) is not the published thinned Rule-2 number (~0.096757). Labeled separately.
- Antithetic shortfall is recorded. Not padded. Spacing not lowered below 3.2 px.

Assumptions that remain, and are not hidden:

- Band 12 is detrended elevation. No 1332 m Lahontan elevation test.
- The dense witness rejects every nonempty raster. Local uniqueness (0.1968) does not clear it.
- This session did not re-scan 102 public repositories.
- Login to DrivenData was not available. 0 organizer receipts.

## Pass 3 — original request

| Requirement | Status |
|---|---|
| Unique single-band float32 GeoTIFF on the official grid, values in [0, 1] | Met for three files. Primary SHA-256 `91e26530ad25cfc19e05d3fc38b75c0e295ee1e128f571a3ba4afcf8df10934e`. |
| Obvious OK-to-download vs OK-to-submit | Met. Download yes. Submit no. |
| Study CLAIM 0.2778 without writing a projection as a score | Met in the analysis. Public snapshot 0.4413 is not a receipt. Higher than 0.2778 is possible in principle. This file is not the test of that. |
| Unlike prior rasters | Met locally (overlap 0.1968, `|ρ|` 0.053 at scoring). Post-merge overlap with `DRAINAGE-KNICK` is 0.1892. Not a copy of `R0`. |
| 3–5 ranked hypotheses before implementation | Met. |
| Spatially blocked holdout before any weekly slot | Met. Slot not spent. |
| Run card, name, note ≤140, executive submit subpage, prompt in README | Met. |
| Negative result kept | Met. |
