# SUBMIT — human-only handoff (agent never submits)

**Recommendation: DO NOT SUBMIT any GEMSDOE92 TRACKB raster as a weekly slot**
(HOLD, IR-92-02/IR-92-03). They are Phase-2 trace assets. If the human
nevertheless decides to spend a slot for Phase-2 reasons, upload exactly
ONE `.tif` per slot — the NaN-outside primary below (zeros twin is fallback only):

| File | Name (submission) | Note (<=140 chars) | Format receipt |
|---|---|---|---|
| `releases/h33-h33-2-b2-TRACKBt1p0-20261023-7bc435f2.tif` | h33-h33-2-b2-TRACKBt1p0-20261023-7bc435f2 | `h33-h33-2-b2; TRACKB>=1.0km traces, refill>3px; pred MODEL:-0.008` | PASS all MUST gates, re-read from disk (`registry/variant_validation.json`): EPSG:32611, 3730x3292, float32, 1 band, [0,1] inside, NaN outside, 37,654 dots, 0 catalogue, min d_cat 2.236 px, sha256 `7bc435f2fe9e…` |
| `releases/h33-h33-2-b2-TRACKBt1p2-20261023-3322bd7a.tif` | h33-h33-2-b2-TRACKBt1p2-20261023-3322bd7a | `h33-h33-2-b2; TRACKB>=1.2km traces, refill>3px; pred MODEL:-0.010` | PASS, sha256 `3322bd7a28f3…` |
| `releases/h33-h33-2-b2-TRACKBt1p5-20261023-ab92778e.tif` | h33-h33-2-b2-TRACKBt1p5-20261023-ab92778e | `h33-h33-2-b2; TRACKB>=1.5km traces, refill>3px; pred MODEL:-0.013` | PASS, sha256 `ab92778e2ec4…` |

Zeros fallbacks `*-zeros.tif` (same dots, 0 outside) sit beside each file
with matching `.zip`s; both twins validated. After uploading, the human
records `receipt_score`/`receipt_date` in `ledger/submissions.csv`.
Phase-2 reviewers should use the `*-traces.geojson` files and
`docs/TRACE_EVIDENCE.md`.
