# GEMSDOE92 — PRUNE axis session

## CURRENT STATE
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots. Rebuilt this session from the pinned lineage (`dot_thin(H19-5, 2.8) & d_cat > 2.0`) and **byte-identical to both pinned encodings** (zeros `c55bafc4…`, NaN `baeae321…`). `0.2778` remains **CLAIM** (no receipt in this checkout).
- **Best receipt**: none recorded.
- **TOP_PUBLIC**: not supplied; human must provide the value and its observation date.
- **Slots left this week**: unknown; human must check the entity's rolling-week quota (3 scored submissions, 1 final file).
- **AXIS this session**: SNAP, chosen autonomously. Values `cap2p0-g0.15`, `cap2p0-g0.10`, `cap2p0-g0.05` (2,660 / 7,023 / 19,565 dots moved; count, mass and the 2.83 px spacing invariant held).
- **Next 3 candidate slots (BUILT, not submitted)**:
  1. `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` — 2,702 dots removed/refilled (7.18%); MODEL +0.003, range [-0.008,+0.015]. Extends the only mechanism whose last step moved the score up (≤2 px collar: 0.2708 → 0.2778 CLAIM, i.e. +0.007 — formally still under the 0.01 evidence bar).
  2. `h33-h33-2-b2-SNAPcap2p0-g0p15-20261023-2ca4294e` — 2,660 dots moved ≤2 px (7.06%), mean displacement 0.124 px overall (1.76 px per mover); MODEL ±0.008, range [-0.008,+0.008]. Cheapest test of the positional hypothesis on the incumbent.
  3. `h33-h33-2-b2-SNAPcap2p0-g0p05-20261023-2c472bc5` — 19,565 dots moved (51.96%), mean displacement 0.858 px overall (1.65 px per mover); MODEL ±0.035, range [-0.035,+0.035]. High-variance dose extreme; only worth a slot if slot 2 shows ≥+0.01, otherwise use slot 3 for PRUNE p2.5 (`…-6d7a61ba`).

No file was submitted. Candidate TIFFs live in `releases/` (gitignored, so not redistributed by this public repo); regenerate with the scripts in `scripts/`. See `docs/SUBMIT.md`.

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
- `registry/session_manifest.json` — pinned inputs with sha256

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
