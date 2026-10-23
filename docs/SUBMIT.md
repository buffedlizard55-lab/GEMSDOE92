# Candidate handoff — human review and submission only

**Do not upload until you confirm the weekly quota and independently review the selected raster.** The agent does not submit. The parent score `0.2778` is an owner-reported **CLAIM**, not a receipt-backed score. There is no receipt-backed best score in this checkout.

All candidates have 37,654 binary unit-mass dots; each changes only the SNAP seating field relative to exactly rebuilt R0. The form note is at most 140 characters. The NaN-outside primary and zero-outside fallback encode the same inside-footprint raster; upload only one file for any slot.

None of the three MODEL projections reach +0.01. Treat a public live change under 0.01 as no evidence.

| Suggested order | Local primary raster (NaN outside) | Fallback (`-zeros.tif`) | Submission name | Note | Count moved | NaN SHA-256 | Format receipt |
|---|---|---|---|---|---:|---|---|
| 1 | `releases/h33-h33-2-b2-SNAPiso_combo2g10-20261023-a18f53b1.tif` | `releases/h33-h33-2-b2-SNAPiso_combo2g10-20261023-a18f53b1-zeros.tif` | `h33-h33-2-b2-SNAPiso_combo2g10-20261023-a18f53b1` | `h33-h33-2-b2; SNAP<=2px g+0.10 iso_grav+|gRTP|; n=37654; moved 5694 (15.12%); pred MODEL:+0.004` | 5,694 | `a18f53b1272c4d4ff3d7e961c4553f4abdbe07da5a85157200f7bd56b92f2be6` | Local disk reread PASS; 37,654 dots; EPSG:32611; exact sample grid; float32, 1 band; NaN outside; values [0,1]; zero catalogue mass; min catalogue distance 2.236 px (parent exclusion; new landings d_cat >= 3). |
| 2 | `releases/h33-h33-2-b2-SNAPiso_g2g10-20261023-6d18fe25.tif` | `releases/h33-h33-2-b2-SNAPiso_g2g10-20261023-6d18fe25-zeros.tif` | `h33-h33-2-b2-SNAPiso_g2g10-20261023-6d18fe25` | `h33-h33-2-b2; SNAP<=2px g+0.10 iso_grav_slope; n=37654; moved 726 (1.93%); pred MODEL:+0.003` | 726 | `6d18fe2571e60f46d9723f9b01266871e894b49d048e4c5deeb59e333d2bca59` | Same format receipt; 726 dots moved; mean displacement 0.038 px. |
| 3 | `releases/h33-h33-2-b2-SNAPrtp_hg2g10-20261023-e68b8ce7.tif` | `releases/h33-h33-2-b2-SNAPrtp_hg2g10-20261023-e68b8ce7-zeros.tif` | `h33-h33-2-b2-SNAPrtp_hg2g10-20261023-e68b8ce7` | `h33-h33-2-b2; SNAP<=2px g+0.10 |grad_H RTP|; n=37654; moved 13299 (35.32%); pred MODEL:+0.000` | 13,299 | `e68b8ce7a245ced7ed072497dd681d1ea5fc29667e2820844c4a56fc039db506` | Same format receipt; 13,299 dots moved; mean displacement 0.673 px. |

## Mechanism and uncertainty

- **Hypothesis:** R0's Poisson-thinned H19-5 dots can sit up to ~200 m off the gravity/RTP edge. Re-seating only those dots whose 2 px window holds a ≥0.10-percentile stronger edge should raise kernel credit T at fixed mass.
- **Mechanism:** SNAP, count 37,654, catalogue exclusions of R0 (`d_cat > 2`; new landings `d_cat >= 3`). Fields: band 05 `iso_grav_anom_slope`; isotropic `|grad_H|` of signed band 02 `rtp`; equal-weight percentile combo. Band 18 (signed `∂g/∂x`) is not used.
- **Mimics:** pluton contacts, caldera rings, basin-fill thickness changes, alteration halos.
- **Prediction:** MODEL ranges in `evidence/snap_session.json`. `|Δ live| < 0.01` is no evidence.
- **Report-only (never gates):** catalogue hide-and-recover PROXY (n=15,247 withheld, seed 20): R0 0.0654; iso_g2g10 0.0650; iso_combo2g10 0.0624; rtp_hg2g10 0.0552. Leakage canary max AUC 0.547 (below 0.90). SGMC off-catalogue PROXY deltas vs R0: `-0.00023`, `-0.00086`, `-0.00243`. PROXY is not a score.
- **Falsifier:** a receipt of magnitude ≥ 0.01 against R0 decides that field's seating hypothesis.

## Reproduction and format receipt

1. Install dependencies from `requirements.txt`.
2. Run `python scripts/restore_inputs.py`; every manifest item is SHA-256 and byte-length verified into `.cache/gems_inputs/`.
3. Run `python scripts/build_snap_variants.py`; it rebuilds R0 and stops unless both parent hashes match exactly, then builds and rereads all six files.
4. `evidence/snap_session.json` records parent hashes, band audit, output hashes, parent diffs, notes, and validation checks.

**Public-repository safeguard:** new candidate TIFFs are gitignored. If they are absent, regenerate them; do not substitute another file. Fill `receipt_score` and `receipt_date` only from the human's submission-page receipt.
