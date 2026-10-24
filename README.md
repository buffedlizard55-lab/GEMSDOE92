# GEMSDOE92 — CONCENTRATION axis session

## CURRENT STATE (2026-10-24, CONCENTRATION session)
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots; rebuilt through the exact H19-5 → D1.5 → D2.8 → SOLO → R0 lineage this session, both pinned SHA-256 digests match byte-for-byte (`zeros` `c55bafc4…`, `nan` `baeae321…`). `0.2778` is still **CLAIM** (no receipt in `ledger/`).
- **Best receipt**: none (`ledger/submissions.csv`: 18 `BUILT`, 0 `RECEIPT`).
- **TOP_PUBLIC**: `____` (human must supply value + date).
- **Slots left**: this week `__ / 3`; total to 2026-12-03 `__` (human must confirm).
- **AXIS this session**: `CONCENTRATION`, chosen autonomously. 3 variants, 1 km blocks, count + mass fixed at 37,654, new dots `d_cat > 3.0 px`, all format gates PASS:
  1. `h33-h33-2-b2-CONCENTRATIONcatd10-20261024-c313194a` — 10% (3,765) moved to highest catalogue-density blocks; `MODEL:+0.013` `[-0.013,+0.040]`; mechanics-only cost `-0.013`.
  2. `h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8` — 10% moved on the 1 km multi-physics prior; `MODEL:-0.008` `[-0.014,-0.002]`.
  3. `h33-h33-2-b2-CONCENTRATIONcatdS10-20261024-6b87f2d7` — mirror image, 10% moved HIGHEST→LOWEST catalogue-density blocks; `MODEL:-0.070` `[-0.118,-0.022]` (sign test, not a bet).
- **Next 3 candidate slots**: `catd10` → `SNAPscarp2p0px` → conditional (`catdS10` / `SNAPscarp1p4px` / `PRUNEp3.5px-refill`). Detail and decision rules in `SLOT_PLAN.md`; upload form notes in `docs/SUBMIT.md`.
- **Key measured fact**: a count-preserving move cannot keep R0's 2.828 px spacing floor — only 90 legal ridge-mask pixels are that far from every parent dot — so arrivals land 1.0-1.4 px from a survivor. The swap's mechanical cost is `-0.013` to `-0.021` and is recorded per variant in `evidence/concentration_variants.json`.

No file was submitted. Candidate GeoTIFF pairs are written to `releases/` (gitignored) and regenerate with `python scripts/build_concentration_variants.py`.

## Verified facts
- Metric: DTI with alpha 0.2, beta 0.8, triangular kernel R=300m (3px), float32 EPSG:32611 100m, per https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Organizer answers: known faults masked pixel-exactly, new truth can lie within 300m of known traces — https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
- Structure: public leaderboard only some chunks, Phase1 $50k private chunks, Phase2 $250k rescores with expert-expanded labels — rules https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Resolution: GeoDAWN Area 2 flown at 400m line spacing, 150-200m above terrain, so lineament positions uncertain by kernel radius — https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7

## What the PRUNE session built (2026-10-23, historical)
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

## What the MASS session built (2026-10-23, historical)
Three MASS variants, still BUILT and unscored. **Caveat recorded in
IRREGULARITIES:** H19-5 turns out to be binary {0,1} with value 1.0 at every
dot, so those files were ranked on a field with no ordering — they are a random
10% perturbation, not a ranking test. Read their scores accordingly.

## Files
- `releases/` — candidate rasters (NaN outside primary, zeros fallback)
- `gems/` — tested toolkit: metric algebra, axis builders, gates, proxy, ledger, CLI
- `tests/` — 38 tests, no competition data required (`make test`)
- `scripts/build_prune_variants.py` — PRUNE-session build, deterministic
- `scripts/build_concentration_variants.py` — this session's build (CONCENTRATION), deterministic
- `evidence/concentration_variants.json` — per-variant receipts, priors, model projection, gates
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
