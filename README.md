# GEMSDOE92 — PRUNE axis session

## ⬇️ SUBMISSION DOWNLOAD — READ FIRST

**Unique submission TIF generated this session:** [`h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif`](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE92/main/releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif)

- **OK TO DOWNLOAD:** ✅ YES — all-finite GeoTIFF, values in [0, 1], 10/10 format gates PASS.
- **OK TO SPEND A WEEKLY SUBMISSION SLOT:** ❌ NO — HOLDOUT-DTI is negative versus R0, so this is a deliverable negative result, not a promoted candidate.
- **Site / executive summary:** [`docs/index.html`](docs/index.html) · [`docs/executive-summary.html`](docs/executive-summary.html)
- **Submission name:** `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f`
- **Note (116/140 chars):** `h33-h33-2-b2; STEPOVER step-over dots 3-10px off catalogue at visible trace tips; HOLDOUT-DTI 0.0000 [0.0000,0.0000]`
- **SHA-256:** `e5fee27f162371d959315d1dc412e137df0348b6009fa3dfdc46dc1363bd4205`

## CURRENT STATE
- **Parent R0**: `h33-h33-2-b2` (GEMSDOE32), 37,654 unit-mass dots; exact lineage rebuild matches both pinned SHA-256 digests (`zeros`: `c55bafc4…`, `nan`: `baeae321…`). `0.2778` remains **CLAIM** (no receipt in `ledger/`).
- **Best receipt**: none recorded (`ledger/submissions.csv` has 23 `BUILT` rows and zero `RECEIPT` rows).
- **TOP_PUBLIC**: `____` (not supplied; human must fill value and observation date from leaderboard).
- **Slots left this week**: `__` / total left to 2026-12-03: `__` (human must confirm entity rolling-week quota).
- **AXIS this session**: `RELIEF`, chosen autonomously. New values: `p10piedmont`, `p12piedmont`, `p15piedmont` (shifting 10%, 12%, and 15% of dots from low-prior basin & range-front terciles to exact-DTI refill in the piedmont tercile; exact 37,654 dots held; `d_cat > 2.0 px`).
- **Next 3 candidate slots (BUILT, not submitted)**:
  1. `h33-h33-2-b2-RELIEFp12piedmont-20261024-a0998ed7` — 12.0% shift (4,518 dots) into piedmont tercile (`MODEL:+0.008` `[-0.003,+0.022]`; hide-and-recover `PROXY` `+0.00197` vs R0).
  2. `h33-h33-2-b2-SNAPscarp2p0px-20261023-2a65fe24` — `<=2.0 px` joint scarp+break+TMI/grav edge snap, mean disp `1.234 px` (`MODEL:+0.012` `[-0.006,+0.025]`; SGMC `PROXY` `+0.00267` vs R0).
  3. `h33-h33-2-b2-RELIEFp15piedmont-20261024-15254f0a` (`MODEL:+0.006`), or conditional swap to `h33-h33-2-b2-CONCcatblk10up10-20261024-c9503d48` (`MODEL:+0.006`) if Slot 1 is neutral.
  - Merge note (2026-10-24): an independent CONCENTRATION set landed on main (`CONCcatblk10up10/up20/dn10`, 1 km catalogue-density prior) and this branch adds ONE file that set does not contain — `h33-h33-2-b2-CONCENTRATIONphys10-20261024-b93a4cf8` (`phys10`, physics prior, no catalogue information, `MODEL:-0.008` `[-0.014,-0.002]`). Its duplicate `catd`/mirror twins were deleted from the ledger rather than offered for slots. See `SLOT_PLAN.md` for how the RELIEF / CONCENTRATION / physics-prior files rank against each other.

No file was submitted. Candidate GeoTIFF pairs exist locally in `releases/` and are gitignored per public-repo safeguard; regenerate anytime via `python scripts/build_relief_variants.py`. See `docs/SUBMIT.md` and `SLOT_PLAN.md`.

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
- `tests/` — 57 tests, no competition data required (`make test`)
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

## STANDING REQUIREMENTS (from session prompt — read at the start of every session)

1. **Unique TIF submission.** Generate a unique submission TIF for the competition; never copy a previous submission except for learning/education. It must be obvious whether the generated TIF is OK to download and submit.
2. **Obvious, easy download.** Provide one easy-to-download submission TIF (this session: `releases/h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f.tif`, linked from `docs/executive-summary.html`) plus an executive summary subpage explaining exactly how to submit (file + name + note &lt;=140 chars on the DrivenData submission page).
3. **Validation without human intervention.** Format gates (CRS EPSG:32611, shape/geotransform == sample_submission.tif, float32 single band, values in [0,1], 0 NaN inside footprint, zero catalogue mass, dots &gt;3 px from catalogue) must pass by re-reading from disk — `make validate FILE=...`. This session: 10/10 PASS.
4. **Labeling.** Every number is HOLDOUT-DTI (evaluator version, # withheld positives, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). A projection is never written as a score. 0.2778 (GEMSDOE32 h33-h33-2-b2) is an owner-reported CLAIM with no receipt.
5. **Parallel-run protocol (LANE).** Rank correlation &gt;0.90 with any registry raster, or &gt;70% of dots within 3 px of one registry raster's dots => duplicate, log and stop. Checked on surface before placement and on final dots. This session: worst rho 0.0277, worst overlap 0.2534 vs 14 local registry rasters => unique.
6. **Holdout method.** Hide-and-recover: withhold whole fault segments with a buffer; catalogue-based features only from visible faults; visible faults masked pixel-exactly; pooled DTI alpha 0.2 beta 0.8, 300 m triangular kernel. Reported as HOLDOUT-DTI with 95% CI.
7. **Leakage canary.** Single-feature AUC &gt;0.90 => stop and investigate. This session: AUC 0.4996 (pass).
8. **Run card.** End every session with one JSON card (`evidence/run_card.json`): hypothesis, mechanism, named non-fault mimic, holdout-DTI + CI, correlation/overlap vs registry, raster sha256, validator output, submission name + note (&lt;=140 chars), verdict promote/negative. Negative results are deliverables.
9. **Budget.** Stop after 3 experiments or 2 hours; promotion to a real submission slot is a separate selector step within the weekly cap.
10. **Core values.** Maximize P(Win); Own the Outcome.

## Session result (2026-10-24, this branch)
- New lane **STEPOVER** built: `h33-h33-2-b2-STEPOVER-tip10px-N5000-20261024-e5fee27f` (5,000 unit-mass step-over dots, all-finite zeros encoding, sha256 `e5fee27f…`), ledger row BUILT (no receipt), 10/10 format gates PASS, lane-unique, leakage canary pass.
- Holdout-DTI = 0.0000 [0.0000, 0.0000] vs R0 0.00370 [0.00301, 0.00432]: structural zero (gate-compliant dots cannot reach catalogue-derived held truth within the 3 px kernel); verdict **negative** — do not spend a weekly slot on this file until a mechanism clears the holdout bar. Negative result is a deliverable; whether any submission scores above 0.2778 is ORGANIZER-CONFIRMED only after upload.
- See `docs/executive-summary.html`, `evidence/run_card.json`, `evidence/stepover_evidence.json`.
