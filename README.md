# GEMSDOE92 — PRUNE axis session

## CURRENT STATE
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots; exact lineage rebuild matches both pinned SHA-256 digests (`zeros`: `c55bafc4…`, `nan`: `baeae321…`). `0.2778` remains **CLAIM** (no receipt in `ledger/`).
- **Best receipt**: none recorded (`ledger/submissions.csv` has 15 `BUILT` rows and zero `RECEIPT` rows).
- **TOP_PUBLIC**: `____` (not supplied; human must fill value and observation date from leaderboard).
- **Slots left this week**: `__` / total left to 2026-12-03: `__` (human must confirm entity rolling-week quota).
- **AXIS this session**: `SNAP`, chosen autonomously. New values: `scarp2p0px`, `scarp1p4px`, `pot2p0px` (spacing-preserving `min_nn >= 2.828 px`, exact 37,654 dots, R0 `d_cat > 2.0` exclusions, piedmont break-in-slope + unsigned `Band 5` gravity gradient).
- **Next 3 candidate slots (BUILT, not submitted)**:
  1. `h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24` — `<=2.0 px` joint scarp+break+TMI/grav edge, mean disp `1.234 px` (82.05% px changed); `MODEL:+0.012` (`[-0.006,+0.025]`); SGMC `PROXY` `+0.00267` vs R0.
  2. `h33-h33-2-b2-SNAPscarp1p4px-20261023-01fb4acc` — `<=1.414 px` 8-neighbor joint scarp+break+TMI/grav edge, mean disp `0.954 px` (78.00% px changed); `MODEL:+0.008` (`[-0.004,+0.018]`); SGMC `PROXY` `+0.00148` vs R0.
  3. `h33-h33-2-b2-PRUNEp3.5px-refill-20261023-a121a277` (`MODEL:+0.003`; orthogonal collar test to unlock `SNAP+PRUNE`), or swap in `h33-h33-2-b2-SNAPpot2p0px-20261023-41697f8c` (`MODEL:-0.002`; pure TMI+grav gradient subsurface control, mean disp `1.366 px`) if Slot 1 drops by `>=0.01`.

No file was submitted. Candidate GeoTIFF pairs exist locally in `releases/` and are gitignored per public-repo safeguard; regenerate anytime via `python scripts/build_snap_scarp_variants.py`. See `docs/SUBMIT.md` and `SLOT_PLAN.md`.

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
