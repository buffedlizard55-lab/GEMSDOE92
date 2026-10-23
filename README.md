# GEMSDOE92 — PRUNE axis session

## CURRENT STATE
- **Parent R0**: h33-h33-2-b2 (GEMSDOE32) — 37,654 unit-mass dots, sha256 `baeae321…077dd` **verified byte-for-byte this session**, CLAIM 0.2778 (no receipt)
- **Best receipt**: None yet (ledger has 6 BUILT rows, 0 scored)
- **TOP_PUBLIC**: ____ (human fills from leaderboard, with date)
- **Slots left this week**: 3 / total: 3 (one entity, 3 per rolling week, one final)
- **AXIS for this session**: PRUNE (chosen autonomously, no prompt)
- **Next 3 slots (planned)**:
  1. `h33-h33-2-b2-PRUNE_B3-20261023-3d2403c7` — remove dots within 3 px of catalogue (2,171 = 5.77%), refill, count held 37,654 — predicted +0.002 to +0.006
  2. `h33-h33-2-b2-PRUNE_B4-20261023-78e893d7` — same at 4 px (3,825 = 10.16%) — predicted +0.001 to +0.004
  3. `h33-h33-2-b2-PRUNE_B5-20261023-85cd67ad` — same at 5 px (5,637 = 14.97%) — predicted −0.002 to +0.002 (negative control)

## Verified facts
- Metric: DTI with alpha 0.2, beta 0.8, triangular kernel R=300m (3px), float32 EPSG:32611 100m, per https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Organizer answers: known faults masked pixel-exactly, new truth can lie within 300m of known traces — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Structure: public leaderboard only some chunks, Phase1 $50k private chunks, Phase2 $250k rescores with expert-expanded labels — rules https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Resolution: GeoDAWN Area 2 flown at 400m line spacing, 150-200m above terrain, so lineament positions uncertain by kernel radius — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7

## What we built this session (PRUNE, 2026-10-23)
- Verified all 8 pinned manifest hashes — PASS, and verified the parent R0 sha256
  byte-for-byte against its recorded hash (both nan and zeros encodings)
- Measured the parent's catalogue-distance profile: min 2.236 px, 0 dots ≤2 px,
  2,171 ≤3 px (5.77%), 3,825 ≤4 px, 5,637 ≤5 px
- Built 3 PRUNE dose-response variants differing ONLY in the distance rule:
  remove dots within R px (R = 3, 4, 5) and refill each to its nearest legal
  pixel (distance > R, in footprint, off catalogue, on the H19-5 mask), holding
  count and total mass at exactly 37,654
- Independent parent-diff check: removed set is exactly {distance ≤ R}, nothing
  else moved, no dot within R px in any variant (measured minima 3.16 / 4.12 /
  5.10 px)
- All files pass all 10 format gates with no PRUNE exemption, re-read from disk
- Tooling: `gems/` implements the DTI algebra, exact marginal-gain ranking, the
  axis builders and the gates; 38 tests pass with no data (`make test`)

## What the previous session built (MASS, 2026-10-23)
Three MASS variants, still BUILT and unscored. **Caveat recorded in
IRREGULARITIES:** H19-5 turns out to be binary {0,1} with value 1.0 at every
dot, so those files were ranked on a field with no ordering — they are a random
10% perturbation, not a ranking test. Read their scores accordingly.

## Files
- `releases/` — candidate rasters (NaN outside primary, zeros fallback)
- `gems/` — tested toolkit: metric algebra, axis builders, gates, proxy, ledger, CLI
- `tests/` — 38 tests, no competition data required (`make test`)
- `scripts/build_prune_variants.py` — this session's build, deterministic
- `registry/parents/R0.json` — verified parent record + its (absent) ranking
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
