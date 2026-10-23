# GEMSDOE92 — MASS axis session

## CURRENT STATE
- **Parent R0**: h33-h33-2-b2 (GEMSDOE32) — 37,654 unit-mass dots, none within 2 px of catalogue, CLAIM 0.2778 = CLAIM until receipt in ledger/
- **Best receipt**: None yet (ledger empty, parent is CLAIM)
- **TOP_PUBLIC**: ____ (human fills from leaderboard, with date)
- **Slots left this week**: 3 / total: 3 (one entity, 3 per rolling week, one final)
- **AXIS for this session**: MASS (chosen autonomously, no prompt)
- **Next 3 slots (planned)**:
  1. h33-h33-2-b2-MASS_SWAP10-20261023-3e776063 — swap lowest 10% with next 10% (37,654 dots, 10% changed) — predicted +0.001 to +0.006
  2. h33-h33-2-b2-MASS_D10-20261023-e26a6cb8 — drop lowest 10% (33,889 dots, 10% changed) — predicted +0.002 to +0.008 if low-ranked are noise
  3. h33-h33-2-b2-MASS_A10-20261023-e5613a00 — add next 10% (41,419 dots, 10% changed) — predicted -0.001 to -0.005 (budget saturation test)

## Verified facts
- Metric: DTI with alpha 0.2, beta 0.8, triangular kernel R=300m (3px), float32 EPSG:32611 100m, per https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Organizer answers: known faults masked pixel-exactly, new truth can lie within 300m of known traces — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Structure: public leaderboard only some chunks, Phase1 $50k private chunks, Phase2 $250k rescores with expert-expanded labels — rules https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Resolution: GeoDAWN Area 2 flown at 400m line spacing, 150-200m above terrain, so lineament positions uncertain by kernel radius — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7

## What we built this session
- Verified manifest hashes (sample_submission, existing_faults, parent R0) — all PASS
- Rebuilt R0 from GEMSDOE32 mirror, matched sha256 c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9, 37,654 dots, min distance 2.236px
- Built 3 MASS variants differing ONLY on mass axis, same count or +/-10%, ranking from H19-5 continuous field (121k px) as proxy for parent's own ranking
- All variants pass format check (CRS, shape, transform, dtype, band count, values in [0,1], no NaN inside footprint, NaN outside for primary, zeros outside for fallback, zero catalogue mass)

## Files
- `releases/` — candidate rasters (NaN outside primary, zeros fallback)
- `ledger/submissions.csv` — build log
- `docs/mechanism_cards.md` — hypothesis, mechanism, mimic, predicted sign, falsifier
- `SLOT_PLAN.md` — next slots and weeks to deadline
- `docs/SUBMIT.md` — submission form note
- `registry/data_manifest.json` — pinned inputs with sha256

## Evidence labels
- RECEIPT = copied from submission-page receipt
- CLAIM = owner-reported, no receipt
- PROXY = local holdout
- MODEL = projection
Never call PROXY or MODEL a score.

## IRREGULARITIES
See IRREGULARITIES.md — only items that change a decision.

## AI disclosure
See AI_USE.md
