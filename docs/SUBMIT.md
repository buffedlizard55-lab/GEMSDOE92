# SUBMIT — MASS axis session 2026-10-23

## Recommended file for next slot (Slot 1)
- **File**: `releases/h33-h33-2-b2-MASS_SWAP10-20261023-3e776063.tif` (NaN outside, per spec) — primary
- **Fallback**: `releases/h33-h33-2-b2-MASS_SWAP10-20261023-3e776063-zeros.tif` (zeros outside) — use if portal rejects NaN outside
- **Name** (portal unique-name field, <= maybe 200 chars): `GEMSDOE92-MASS-SWAP10-37654`
- **Note** (<=140 chars, paste into DrivenData form):
  `h33-2-b2 parent 37654; MASS SWAP10: replace lowest 10% H19-5 with next 10%; same count, 10% changed; pred +0.001 to +0.006 MODEL`

## Format receipt (from scripts/validate_submission.py)
- CRS: EPSG:32611 (WGS 84 / UTM zone 11N)
- Shape: 3730x3292 (height x width), transform Affine(100,0,243350,0,-100,4508550)
- Dtype: float32, 1 band, values in [0,1]
- NaN outside footprint: YES for primary .tif (7111787 NaN outside), 0 NaN inside footprint
- Zeros outside fallback: all finite, 0 outside footprint
- Zero catalogue mass: 0 pixels on existing_faults.tif (60,988 catalogue pixels)
- Min distance to catalogue: >2px (2.236) for all dots (parent had 2.236, we enforce >2)
- n_dots: 37,654 (SWAP10), 33,889 (D10), 41,419 (A10)
- Re-read from disk after writing: PASS
- sha256 not already in ledger: PASS (new hashes)
- parent-diff: 10% changed for all three variants

## Other built files (slots 2 and 3)
- Slot 2: `h33-h33-2-b2-MASS_D10-20261023-e26a6cb8` — 33,889 dots, drop lowest 10%
  - Name: `GEMSDOE92-MASS-D10-33889`
  - Note: `h33-2-b2 parent; MASS D10 drop low 10% H19-5 33889 dots 10% changed; pred +0.002 to +0.008 MODEL`
- Slot 3: `h33-h33-2-b2-MASS_A10-20261023-e5613a00` — 41,419 dots, add next 10%
  - Name: `GEMSDOE92-MASS-A10-41419`
  - Note: `h33-2-b2 parent; MASS A10 add next 10% H19-5 41419 dots 10% changed; pred -0.001 to -0.005 MODEL`

## Submission instructions (per rules)
- Submit from your own registered account (one entity, 3 slots/week, one final)
- Upload only ONE file per slot (either NaN-outside primary or zeros fallback, not both)
- Do NOT contact dropbox.com, do NOT scrape leaderboard, do NOT share credentials
- After receipt, copy receipt score into ledger/submissions.csv columns receipt_score, date, receipt Y/N

## Ledger
See `ledger/submissions.csv` — status BUILT, predicted_change MODEL, not a score. Every external fact carries URL.

## Evidence labels
- RECEIPT = copied from submission-page receipt
- CLAIM = owner-reported, no receipt
- PROXY = local holdout
- MODEL = projection
Never call PROXY or MODEL a score.

---

## PRUNE session 2026-10-23 — files ready to upload

Submit in this order. One file per slot.

| # | file to upload | note (<=140 chars) |
|---|---|---|
| 1 | `releases/h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7.tif` | `parent h33-h33-2-b2; drop dots within 3px of catalogue (2171=5.77%), refill nearest legal, count held 37654; predicted +0.002..+0.006` |
| 2 | `releases/h33-h33-2-b2-PRUNE_B4-20261023-78e893d7.tif` | `parent h33-h33-2-b2; drop dots within 4px of catalogue (3825=10.16%), refill nearest legal, count held 37654; predicted +0.001..+0.004` |
| 3 | `releases/h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad.tif` | `parent h33-h33-2-b2; drop dots within 5px of catalogue (5637=14.97%), refill nearest legal, count held 37654; predicted -0.002..+0.002 (negative control)` |

Each has a `-zeros.tif` twin with identical in-footprint values; upload the twin
instead only if the uploader rejects NaN.

Format receipt for each (all PASS, 10 gates — CRS/shape/transform/dtype/band/
range/no-NaN-inside/NaN-outside/zero-catalogue-mass/distance):

```
python -m gems validate releases/h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7.tif \
  --reference data/bridge/sample_submission.tif \
  --catalogue data/bridge/labels.tif
```

After each submission, fill `receipt_score` **and** `receipt_date` in
`ledger/submissions.csv`. A score with no date stays a CLAIM.
