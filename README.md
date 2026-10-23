# GEMSDOE92

<!-- CURRENT STATE -->
- **Parent:** R0 = h33-h33-2-b2 (GEMSDOE32), 37,654 dots, rebuilt byte-exact
  (zeros sha256 `c55bafc4…`, NaN `baeae321…`); 0 within 2 px of catalogue.
- **Best receipt:** none in this repo — R0 0.2778 is CLAIM (no receipt).
  TOP_PUBLIC 0.4413 (2026-10-22, human-supplied via GEMSDOE88; unverified here).
- **Slots left:** unknown — human must confirm (entity allows 3/week; IR-92-05).
- **This session (AXIS=TRACKB):** 3 fixed-count variants BUILT and gate-PASS
  (t1p0 `7bc435f2` 35.24% changed / t1p2 `3322bd7a` 38.76% / t1p5 `ab92778e`
  44.56%), all HOLD Phase-2 only: corrected MODEL -0.008/-0.010/-0.013,
  SGMC PROXY 0.0728/0.0705/0.0664 vs R0 0.0961. GeoJSON traces + per-trace
  geologist evidence in `releases/*-traces.geojson`, `docs/TRACE_EVIDENCE.md`.
- **Next 3 slots:** see SLOT_PLAN.md (PRUNE p3px from GEMSDOE88 inventory,
  then CONCENTRATION on the winner, then best remaining receipt candidate).
  TRACKB takes no slot unless the human decides.
<!-- /CURRENT STATE -->

Reproduce: `python scripts/restore_inputs.py && python scripts/verify_parent_r0.py
&& python scripts/build_trackb_variants.py && python scripts/validate_variant.py
releases/*.tif --out registry/variant_validation.json && pytest -q`
(Candidate `.tif`/`.zip` are gitignored; hashes/receipts are in `ledger/`.)
