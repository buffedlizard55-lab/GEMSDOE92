# GEMSDOE92 — CONCENTRATION axis session

## CURRENT STATE
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots; rebuilt bit-exactly through
  H19-5 -> D1.5 -> D2.8 -> SOLO -> R0 and matched to both pinned raster SHA-256 values this session.
  `0.2778` remains **CLAIM** (no receipt in this checkout).
- **Best receipt**: none recorded. 18 files are `BUILT` across three sessions (3 MASS,
  6 PRUNE, 6 SNAP on `main`, 3 CONCENTRATION here), 0 are receipt-scored.
- **TOP_PUBLIC**: not supplied; human must provide the value and its observation date.
- **Slots left this week**: unknown; human must check the entity's rolling-week quota.
- **AXIS this session**: CONCENTRATION, chosen autonomously (MASS and PRUNE values are already in the
  ledger; SNAP and RELIEF need bands that are not separately pinned). New values: `C10_b5km`,
  `C15_b5km`, `C20_b5km` — a dose-response at 5 km blocks.
- **Next 3 candidate slots**: none of these three is recommended for a slot. The two REPORT-ONLY local
  instruments disagree in sign, and no dose is predicted to move the live score by 0.01. If the human
  spends one slot on this axis anyway to test whether R0 is locally optimal, use
  `h33-h33-2-b2-CONC_C10_b5km-20261023-3127dbd4` (smallest dose, 10.00% moved).
  1. `…-CONC_C10_b5km-…3127dbd4` — 3,765 dots moved (10.00%); MODEL −0.001, range [−0.021,+0.011];
     SGMC PROXY −0.004851; hide-and-recover PROXY +0.001807.
  2. `…-CONC_C15_b5km-…bb01093f` — 5,648 moved (15.00%); MODEL −0.003, range [−0.023,+0.011];
     SGMC PROXY −0.007066; hide-and-recover PROXY +0.001853.
  3. `…-CONC_C20_b5km-…8c425d13` — 7,531 moved (20.00%); MODEL −0.005, range [−0.026,+0.011];
     SGMC PROXY −0.010416; hide-and-recover PROXY +0.001870.

No file was submitted. Candidate TIFFs are generated locally and gitignored. See `docs/SUBMIT.md`.

## What this session found
- **R0's block allocation is locally near-optimal.** At 5 km blocks R0's block dot-density CV is
  0.9014; the variants push it to 1.1192 / 1.2314 / 1.3422, further from the 0.51–0.59 band the brief
  associates with the best files.
- **Most of the loss is generic, not a failure of the ordering.** A randomised-block null loses
  −0.012365 on the independent-fault control at 20%; the parent's own evidence surface loses −0.010423.
  The ordering is worth about +0.002 of control and +0.011 of declared model, but the ceiling sits
  below R0 because refill pixels are the neighbours that Poisson-disk thinning discarded.
- **The two REPORT-ONLY instruments disagree in sign** (SGMC off-catalogue negative and monotone in
  dose; catalogue hide-and-recover positive and flat in dose). Logged in IRREGULARITIES: because the
  live metric scores new-fault pixels only, the SGMC control is the better analogue, but at three
  scored submissions a week the disagreement is itself the finding.

## What we built this session (CONCENTRATION, 2026-10-23)
- Verified all 12 pinned manifest hashes, then rebuilt R0 and matched both parent SHA-256 values
- Screened four candidate block priors (parent evidence surface, geophysics-only, catalogue network
  density, catalogue interaction-node density) against a randomised-block null, in both directions
- Built 3 dose-response variants that differ ONLY in the fraction of the budget moved between 5 km
  blocks; removal by exact marginal DTI loss, placement by exact marginal DTI gain
- Independent parent-diff check: count held at 37,654, zero catalogue mass, min catalogue distance
  2.2361 px (R0's own >2 px rule) on all three
- All files pass all 10 format gates, re-read from disk after writing

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
