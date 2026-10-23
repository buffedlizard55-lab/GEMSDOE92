# SUBMIT

One slot = one file. The human uploads from their own registered account; nothing
in this repo logs in, scrapes, or submits.

## Per slot, in order

1. **Pick the file.** `releases/<id>.tif` (NaN outside the footprint). If the
   uploader rejects NaN, use the pre-built `<id>-zeros.tif` twin instead. Both
   come from the same dot set, so they are the same experiment.
2. **Name it:** `<parent>-<axis><value>-<yyyymmdd>-<sha8>`.
   Example: `h33-h33-2-b2-PRUNEle3px-20261024-1a2b3c4d`.
3. **Note (<=140 chars).** Lead with parent, change, predicted change:
   > parent h33-h33-2-b2; widen catalogue prune 2px->3px, refill to 37654 dots; predicted +0.002..+0.006
4. **Format receipt.** Save the output of
   `python -m gems validate releases/<id>.tif --reference <sample_submission> --catalogue <catalogue> --prune-radius 3`
   next to the file, or paste it in the ledger `notes` column. It must end
   `RESULT: PASS`.
5. **Record it.** Fill `receipt_score` and `receipt_date` in
   `ledger/submissions.csv` the moment the submission page shows a score.
   A score without a date stays a `CLAIM` and is excluded from `best_receipt`.

## The gates that must pass (brief section 6)

| gate | expected |
|---|---|
| CRS | identical to `sample_submission.tif` (EPSG:32611) |
| shape | identical (H, W) |
| transform | identical to 1e-6 |
| dtype | float32, one band |
| values in [0,1] | no violations inside the footprint |
| no NaN inside | 0 pixels |
| outside footprint | all NaN, or all 0 (either accepted; `other` must be 0) |
| catalogue zero mass | 0 dots on catalogue pixels |
| distance from catalogue | 0 dots within 3 px |
| sha256 | not already in the ledger |

`--prune-radius N` with N < 3 declares the PRUNE deviation explicitly in the
report instead of hiding it. Any other axis must pass with the default 3 px.

## Never

- Never upload "just to see" — every scored upload costs one of three weekly
  slots, and exact repeats have already burned at least 8 slots historically.
- Never write `PROXY` or `MODEL` numbers into `receipt_score`.
- Never upload a file whose sha256 is already in the ledger.
