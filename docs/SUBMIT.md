# Candidate handoff — human review and submission only

**Do not upload until you confirm the weekly quota and independently review the selected raster.** The agent does not submit. The parent score `0.2778` is an owner-reported **CLAIM**, not a receipt-backed score. There is no receipt-backed best score in this checkout.

All candidates have 37,654 binary unit-mass dots; each changes only the PRUNE collar/reallocation rule relative to exactly rebuilt R0. The form note is at most 140 characters. The NaN-outside primary and zero-outside fallback encode the same inside-footprint raster; upload only one file for any slot.

| Suggested order | Local primary raster (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Note | Count moved | NaN SHA-256 | Format receipt |
|---|---|---|---|---|---:|---|---|
| 1 | `releases/h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277.tif` | `releases/h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277-zeros.tif` | `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` | `h33-h33-2-b2; PRUNE collar 3.5px; fixed 37654; remove/refill 2702 (7.18%); pred MODEL:+0.003` | 2,702 | `a121a27751381fa2f6b9bf8629e53b1a4a57df5fcab85ed0d3bf548c33ca95ab` | Local disk reread PASS; 37,654 dots; EPSG:32611; exact sample grid; float32, 1 band; NaN outside; values [0,1]; zero catalogue mass; min catalogue distance 3.606 px. |
| 2 | `releases/h33-h33-2-b2-PRUNEp2.5px-refill-20261023-6d7a61ba.tif` | `releases/h33-h33-2-b2-PRUNEp2.5px-refill-20261023-6d7a61ba-zeros.tif` | `h33-h33-2-b2-PRUNEp2.5px-refill-20261023-6d7a61ba` | `h33-h33-2-b2; PRUNE collar 2.5px; fixed 37654; remove/refill 941 (2.50%); pred MODEL:+0.001` | 941 | `6d7a61ba2e980808640db9e0b7b1a787243abf5f833bb7cd25c5a35af96685c8` | Local disk reread PASS; 37,654 dots; EPSG:32611; exact sample grid; float32, 1 band; NaN outside; values [0,1]; zero catalogue mass; min catalogue distance 2.828 px. |
| 3 | `releases/h33-h33-2-b2-PRUNEp4.5px-refill-20261023-ebace30d.tif` | `releases/h33-h33-2-b2-PRUNEp4.5px-refill-20261023-ebace30d-zeros.tif` | `h33-h33-2-b2-PRUNEp4.5px-refill-20261023-ebace30d` | `h33-h33-2-b2; PRUNE collar 4.5px; fixed 37654; remove/refill 4848 (12.88%); pred MODEL:-0.004` | 4,848 | `ebace30d4386c7b979badb0d6512e79b62f822839e42c4fe2e8cf35ed9c46de4` | Local disk reread PASS; 37,654 dots; EPSG:32611; exact sample grid; float32, 1 band; NaN outside; values [0,1]; zero catalogue mass; min catalogue distance 5.000 px. |

## Mechanism and uncertainty

- **Hypothesis:** increasing the catalogue collar may remove detections whose 300 m triangular-kernel support is wasted near organizer-masked mapped faults; a fixed-count refill onto H19-5 lineaments may restore useful off-collar fault coverage.
- **Mechanism:** each variant removes the parent dots at/below its stated radius, then fills the same number of pixels using greedy exact expected-DTI marginal gain on a deterministic label-free prior from pinned H19-5, TMI horizontal gradient, gravity horizontal gradient, and detrended-elevation slope.
- **Mimics:** lithologic contacts, caldera ring fractures, and erosional scarps can resemble fault-related lineaments.
- **Prediction:** wide, low-confidence **MODEL** ranges are recorded in `evidence/prune_rungs.json` and the mechanism cards. Treat public live changes under 0.01 as no evidence.
- **Report-only diagnostics (never gates):** catalogue hide-and-recover PROXY, `n=22,663` withheld positives, paired 20 km spatial-block bootstrap 95% CI: R0 `0.004006 [0.003424,0.004690]`; p2.5 `0.000785 [0.000658,0.000922]`; p3.5 and p4.5 `0.000 [0,0]`. Single-feature canary maximum symmetric AUC is `0.55314` (below the `0.90` investigate threshold). Off-catalogue SGMC control PROXY deltas versus R0 are `+0.00018`, `+0.00031`, and `-0.00360`. These figures are local PROXY diagnostics, not scores, not gates, and not evidence of live performance; p3.5/p4.5's zero recovery is a caution, not a prediction.
- **Falsifier:** the human receipt changes the posterior. A change of magnitude below 0.01 is inconclusive; a larger opposite-sign change rejects the stated collar mechanism for that rung.

## Reproduction and format receipt

1. Install dependencies from `requirements.txt`.
2. Run `python scripts/restore_inputs.py`; every manifest item is SHA-256 and byte-length verified before use and resides in `.cache/gems_inputs/`.
3. Run `python scripts/build_prune_rungs.py`; it rebuilds R0 and stops unless both parent hashes match exactly, then builds and rereads all six files.
4. `evidence/prune_rungs.json` records parent hashes, input-manifest hash, full output hashes, parent diffs, notes, and validation checks. `ledger/submissions.csv` preserves the five earlier main-branch rows and appends three new `BUILT` rows.

**Public-repository safeguard:** competition/candidate TIFF files are gitignored and must remain untracked. The six local TIFFs are not included in the PR. If they are absent from your local workspace, regenerate them with the command above; do not substitute another file. Fill `receipt_score` and `receipt_date` only from the human's submission-page receipt.
