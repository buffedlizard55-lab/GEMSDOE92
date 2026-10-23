# AI Use Disclosure (competition rules: reproducible code + generative-AI disclosure)

## What the AI agent wrote (this session, GEMSDOE92)
- All code in `src/gems92/`, `scripts/`, `tests/`, `vendor/` integration
  choices, and the TRACKB design: dot-graph trace chaining (<=4.5 px,
  span thresholds 1.0/1.2/1.5 km), chunked exact-marginal-DTI refill,
  straightest-walk GeoJSON trace decomposition, evidence paragraphs
  (programmatically generated per trace from measured band/catalogue/GDR
  context values).
- All documentation in this repository: README CURRENT STATE, SLOT_PLAN.md,
  docs/SUBMIT.md, docs/TRACE_EVIDENCE.md, IRREGULARITIES.md, ledger
  mechanism cards, predicted (MODEL) values and their correction.

## What the human decided / must decide
- The session AXIS slot was left blank and the human did not answer the
  axis prompt; the agent selected TRACKB (the only listed axis with no
  built (AXIS, value) pair in any sibling ledger it checked).
- No live submission was made by the agent. Whether to spend any weekly
  slot, which file to upload, and the single blind final file are human
  decisions from the human's own registered account.
- Receipt scores/dates in `ledger/submissions.csv` are filled only by the
  human from submission-page receipts. R0 = 0.2778 remains CLAIM.

## Tools / data
- Inputs are the SHA-256-pinned files in `registry/data_manifest.json`
  (owner GitHub mirrors; competition data terms UNVERIFIED, see
  IRREGULARITIES.md). No DrivenData/Dropbox access, scraping, login, or
  submission code was written or run.
