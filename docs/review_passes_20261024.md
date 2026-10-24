# Three-pass review — 2026-10-24

## Final disposition

**Blocked before placement.** No new prediction TIFF or ZIP was created, no submission slot was used, and nothing was uploaded. The hard stop is reproducible with `scripts/check_registry_saturation.py`; the result is `evidence/registry_saturation_blocker.json`.

## Pass 1 — provenance, score status, and scope

**Checks performed**

- Read the current README, submission handoff, slot plan, irregularity log, parent record, candidate ledger, holdout evidence, manifests, and shared evaluator/writer/uniqueness code.
- Read the public GEMSDOE32 hypothesis registry and relevant public GEMSDOE83 hypothesis records to avoid presenting registered or measured sibling methods as new work.
- Re-read the official competition metric/format page and September 2026 official rules; checked the official public leaderboard on 2026-10-24.
- Verified `ledger/submissions.csv`: 21 `BUILT`, 0 `RECEIPT` rows. The `0.2778` parent value remains `CLAIM`; no receipt was available to copy.

**Findings**

- The sibling GEMSDOE32 page calls the H33-2-B2 artifact **UNSCORED**. Its `0.2708` base / `0.2747` projection are not organizer receipts.
- Official leaderboard display on the observation date: `0.4413`, `0.3916`, `0.3904` for ranks 1–3. This conflicts with the provided `0.3195` snapshot and is only a leaderboard display, not an account receipt.
- Mechanistically, H33-2-B2 is a catalogue-flank removal, not a newly learned detector. Reduced redundant or near-catalogue mass could plausibly explain a better public display; the available artifacts cannot prove that explanation or that the `0.2778` value was awarded.
- The previously recorded `RELIEFp10piedmont` result is `HOLDOUT-DTI` (evaluator `gems57-pooled-hide-v2`, 22,663 withheld positives, `0.006045`, 95% CI `[0.005187, 0.006927]`). Its paired delta vs R0 is `+0.001967`, 95% CI `[+0.001483, +0.002504]`. This is an older catalogue holdout proxy, not a fresh score for this assessment, not a leaderboard score, and not an organizer receipt.

**Irregularity recorded**

User-provided leaderboard value `0.3195` is stale/conflicting with the official display checked on 2026-10-24. No score is attributed to a submission without a receipt.

## Pass 2 — geology, novelty, and validation design

**Checks performed**

- Ranked five unbuilt or unvalidated hypotheses in `docs/research_assessment_20261024.md`, with source layers, target signature, off-catalogue rationale, existing-work comparison, likely non-fault mimics, qualitative expected holdout benefit, and cost.
- Selected one lane only: **depth-stratified USGS 3-D MT conductance breaks** (`gb_conductance_surface_tp.tif`, 2–12 km; `gb_conductance_middle_crust_tp.tif`, 12–20 km; optional 20–50 km slice). The previous H32-C/H33-D work uses shallow `cond_surf`; this lane would use depth-resolved edges/terminations, not another shallow high-conductivity mask.
- Verified the official USGS data-release page lists the depth-slice TIFFs (about 3.94 MB per listed TIFF). Exact public-repository GitHub code searches for the USGS DOI and two slice filenames returned no direct hits; this is a limited novelty check, not proof about private or unindexed work.
- Confirmed that the current 19-band training stack does not contain the depth-slice maps. No map was downloaded, no feature was constructed, and no leakage-canary AUC or holdout run was claimed.

**Stop rule applied**

The shared literal uniqueness gate blocks every nonempty candidate (Pass 3). The method-specific experiment was therefore not started. The holdout evaluator's expected use, if the gate is explicitly revised, remains `gems57-pooled-hide-v2`: whole buffered components, only fold-visible catalogue features, visible faults masked pixel-exactly, pooled DTI `alpha=0.2`, `beta=0.8`, triangular `R=300 m`, with spatial-cluster 95% CI. No slot is being considered.

**Irregularity recorded**

The shared uniqueness gate's literal “any registry raster” dot-overlap rule is incompatible with a public same-grid full-support probability field. Under this rule no nonempty prediction can ever pass. No local exception was introduced.

## Pass 3 — registry, packaging, and submission safety

**Checks performed**

- Reproduced and persisted a metadata-only scan of 101 public owner repositories matching the GEMSDOE naming pattern. It contains 2,508 TIFF paths, of which a documented path heuristic flags 1,998 candidate-like paths and 1,305 unique Git blobs (1,046,507,603 bytes by GitHub metadata). All scanned trees were reported complete and no tree-query errors/truncation were recorded.
- The scan does **not** decode those TIFFs and is not a full content-level uniqueness clearance. It is explicitly labelled as a path inventory with possible false positives/negatives.
- Downloaded only the single decisive witness via the allowed GitHub API (no DrivenData or Dropbox contact), verified SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`, and checked exact grid identity against the pinned sample grid.
- Shared `vendor.gems57.uniqueness.saturation_certificate` result: witness support `5,167,373/5,167,373` footprint cells; legal domain after pixel-exact catalogue exclusion `5,106,385`; uncovered legal cells `0`; covered fraction `1.0`; forward-overlap limit `0.70`; verdict `STOP_BEFORE_PLACEMENT`.
- For every nonempty candidate support inside the legal domain, the shared support definition `finite prediction > 0` therefore yields overlap `1.0` with this witness. This proof is independent of geological feature values and suffices to stop before placement; a candidate-specific Spearman value was not computed.

**Artifact status**

- No candidate raster exists for this run: no raster SHA-256, no writer receipt, and no format-validator result are claimed.
- `vendor/gems57/submission_writer.py` was not called because there was no admissible candidate to write.
- No submission name/note was assigned, and nothing was uploaded.
- The witness TIFF is cached under ignored `.cache/public_gems_tifs/`; only its public GitHub path/blob and checksum are recorded. Competition inputs and new prediction TIFFs were not added to this branch.
- Fresh local tests: `.venv/bin/python -m pytest tests -q` → **75 passed, 12 Rasterio `PendingDeprecationWarning`s**. These are repository tests, not a holdout evaluation or submission validation.

## Trusted sources for manual review

- [DrivenData GEMS challenge: task, metric, and raster format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [NLR GEMS Prize Official Rules, September 2026](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — display only, not a receipt
- [USGS Great Basin electrical conductance maps](https://www.sciencebase.gov/catalog/item/62979746d34ec53d276c113b), DOI [10.5066/P9TWT2LU](https://doi.org/10.5066/P9TWT2LU)
- [NASA Earthdata Sentinel-1 data access](https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/sentinel-1)
- [Nevada Geodetic Laboratory](https://geodesy.unr.edu/)
- [USGS FDSN Event Web Service](https://earthquake.usgs.gov/fdsnws/event/1/) — official ComCat query/API documentation
- [Public GEMSDOE32 page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) and [public 17GEMSDOE witness TIFF](https://github.com/buffedlizard55-lab/17GEMSDOE/blob/main/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif)
- [Koehler et al. (2021), 2020 Monte Cristo Range rupture](https://doi.org/10.1785/0220200371); [Liu et al. (2021)](https://doi.org/10.1785/0120200327)

## Reproduction

```bash
# Re-scan public GitHub TIFF path/blob metadata (no TIFF bytes downloaded)
.venv/bin/python scripts/scan_public_gems_tif_registry.py --out registry/public_gems_tif_inventory.json

# Fetch/hash-check the one universal-blocker witness and rerun the shared certificate
.venv/bin/python scripts/check_registry_saturation.py --out evidence/registry_saturation_blocker.json

# Existing code/tests only; no holdout experiment or submission build is implied
.venv/bin/python -m pytest tests -q
```
