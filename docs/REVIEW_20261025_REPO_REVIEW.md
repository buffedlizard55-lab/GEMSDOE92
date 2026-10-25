# Repo review — 2026-10-25 (session `911a9a62`)

**Verdict: OK TO DOWNLOAD FOR RESEARCH · DO NOT SUBMIT · no new TIFF generated this session.**

This review did not run a new geological experiment (0 of 3 experiments used). It verified the repo's gates, checked the leaderboard and the GEMSDOE32 claims against their sources, located the binding uniqueness rule, and recorded irregularities. Every claim below is labelled with its evidence class and a link or command for manual review.

Evidence classes used: **VERIFIED-RUN** (command executed in this session), **ORGANIZER-CONFIRMED** (official page read this session), **CLAIM** (someone else's number, not a receipt), **REGISTRY-MEASUREMENT** (raster comparison), **PROPOSAL** (untested idea).

---

## 1. What I ran (VERIFIED-RUN)

| Check | Command | Result |
|---|---|---|
| Unit tests | `python -m pytest tests -q` (Python 3.11, `requirements.txt` pins) | **367 passed**, 126 warnings (deprecation only) |
| Pinned inputs hash exactly | `make manifest` | `RESULT: OK` |
| Parent provable from committed bytes | `make verify` | `PARENT VERIFIED (pinned artefact): h33-h33-2-b2 sha256 c55bafc47005…`, 37,654 dots, footprint 5,167,373 px |
| Served TIFFs pass MUST gates | `make site` (`scripts/check_site.py`) | `SITE CHECK PASS (63 served raster(s) gated)` |

Setup note: the sandbox Python is externally managed (PEP 668), so the tests ran in a venv at `/home/user/.venv_gems` built from `requirements.txt` plus `pytest`. Nothing in the repo was changed by that step.

## 2. The uniqueness blocker, re-verified from source (VERIFIED-RUN)

The repo's binding rule (`SESSION_PROMPT.md`, rule 1) says a candidate is a duplicate if rank correlation exceeds 0.90 **or** more than 70% of its dots fall within 3 px of one registry raster's dots.

I re-downloaded the witness `17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif` from the GitHub Git-blob API ([blob](https://api.github.com/repos/buffedlizard55-lab/17GEMSDOE/git/blobs/374c88b1da2b803e2ed160de467fd71ae114010d)) and read it with rasterio:

- SHA-256 `ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be`, 25,065,181 bytes. **Matches** `docs/downloads/review376a_primary_witness.json`.
- Grid `EPSG:32611`, shape `3730 × 3292`, transform identical to `data/bridge/sample_submission.tif`.
- **5,167,373 finite cells, all positive** (min 0.00046, max 0.98412), and **7,111,787 NaN cells outside**. The finite count equals the footprint count in the repo.

Code path: `vendor/gems57/uniqueness.py::dot_overlap` computes the fraction of the candidate's positive cells that fall within `RADIUS_PX` of the witness's support. `dual_overlap` takes the witness support as its positive cells within the footprint. Because that support is the entire footprint, **every nonempty in-footprint dot set scores 1.0**, which is above 0.70.

So the blocker is not a particular file. The rule as implemented cannot be satisfied by any submission against this raster. See Section 5, item 3, for the interpretation question that needs a decision.

## 3. Leaderboard and GEMSDOE32 claims (ORGANIZER-CONFIRMED / CLAIM)

- **Official leaderboard, read 2026-10-25:** [drivendata leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). #1 `xiaofanhu` **0.4413**, #2 `cfld__` 0.3916, #3 `Batik Shirt Brothers` 0.3904, … #22 `kinghorton42` 0.3261. I read rows #1–#23 only. 0.3195 does not appear as a top row in that range.
- **0.3195 origin:** the GEMSDOE32 page's own leaderboard snapshot dated **2026-10-04** lists `#1 nchuzhoy 0.3262, #2 DARD 0.3195, #3 alexoktaba 0.3042` ([GEMSDOE32 page, "Sources" table](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)). So 0.3195 was the second-place score on that older snapshot. It is not a current #1.
- **GEMSDOE32 `h33-h33-2-b2 … zeros: 0.2778`:** I read both chunks of the [GEMSDOE32 page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html). The 0.2778 figure does **not** appear. The page reports a *model* projection of 0.2747 and states: "NO ORGANISER SCORE EXISTS for this or any artifact in this repository." Treat 0.2778 as **CLAIM**, not ORGANIZER-CONFIRMED. The number may come from a receipt on another page. I did not find one.
- The GEMSDOE32 page says its holdout truth is the visible catalogue and "cannot reward a genuinely new fault." This applies to every holdout in this repo too (Section 5, item 8).

## 4. Why the GEMSDOE32-style files score what they score (PROPOSAL-level analysis)

The metric's shape, as this repo implements and states it (`gems/metric.py` line 22: `DTI = T / (0.2*T + 0.2*(S-M) + 0.8*|G|)`), makes each predicted pixel either credited or costly. A thinned dot field that stays on the field's geometry removes mass that was already covered, so credit per pixel rises. That is consistent with the GEMSDOE32 page's own argument. It is a mechanism, not a measured score: the local holdout cannot confirm it for the hidden set.

The strongest measured results in this repo are **HOLDOUT-DTI** values from `gems57-pooled-hide-v2`, not competition scores. The current repo best is `KNICKLOQO standalone` static `0.010788 [0.009468, 0.012201]` per the README. These numbers are on a different scale from the leaderboard, so they cannot be compared to 0.4413 or 0.2778.

## 5. Irregularities flagged for review

1. **Leaderboard figures disagree across sources.** The README and `SESSION_PROMPT.md` cite 0.4413 as #1 (matches the official page). The request brief cites 0.3195 as "highest right now", which is a 2026-10-04 #2 value. Resolved above; the brief should be updated.
2. **0.2778 is not a receipt.** See Section 3. Do not write it as ORGANIZER-CONFIRMED.
3. **Uniqueness gate interpretation (needs a decision).** The protocol's "70% of your dots" wording refers to a *dot* field. The 17GEMSDOE raster is a continuous surface covering the full footprint. The code applies the literal rule by treating every positive pixel as a dot, so the outcome is fixed at 1.0. The repo's own `dual_reading_decision` uses matched-budget overlap as a diagnostic. `REVIEW_376A8469.md` changed the binding rule to literal-only and noted that this was a policy decision. I did not change the rule (see Section 7).
4. **Three different "latest artifact" pointers.** `README.md` names DRAINAGE-KNICK (negative). `docs/index.html` declares the primary download `COULOMBDMs45coulomb55` (DO NOT SUBMIT). The root `index.html` names POISSONKNICK qcal as "newest". The CI primary check and `check_site.py` read only `docs/index.html`, so the root stub is never gated. **Not changed in the end.** I first rewrote the root stub to defer to `docs/index.html`. During the merge with `main`, other sessions' lane banners were kept instead (`main` names the LISTRICDIP updip50 file in the root stub). The root stub is refreshed per lane, so this is a process gap, not a defect in one file. The README also carries several 'latest' blocks (LISTRICDIP, DRAINAGE-KNICK, KNICKLOQO) that `main` maintains; a single generated pointer is still recommended (Section 9).
5. **The README's "Persistent Session Prompt Reference" was abbreviated**, with `...` inside the Study-GEMSDOE32 paragraph and a summary of the parallel-run protocol. **Fixed here:** replaced with a full standing brief (Section 8 of the README).
6. **Session budget.** No experiment was run this session. The brief's "3 passes" requirement is met by this review's three passes: (a) run the gates, (b) recheck the binding rule against source and an independent download, (c) recheck the leaderboard and claims.
7. **Holdout truth is the visible catalogue.** Every HOLDOUT-DTI is a proxy. None can reward a genuinely new fault by construction. Label as HOLDOUT-DTI, never as a competition score.
8. **Unverifiable from this sandbox:** DrivenData's data and submission-receipt pages are login-walled (repo's own note). The submission page's "weekly cap" wording was not read here, so I make no claim about slot counts.

## 6. Candidate hypotheses, ranked (PROPOSAL — none tested)

These were checked against the implemented families in `gems/*.py` by name and by grep. Expected DTI gain is **unknown**. Ranking reflects novelty, data availability, and implementation cost.

| Rank | Hypothesis | Layers | Signature | Why it could catch a fault the catalogue lacks | Overlap with implemented work | Data status | Named non-fault mimic |
|---|---|---|---|---|---|---|---|
| 1 | **Strain-orientation misfit**: fault strike compatible with the principal-axis orientation of regional strain, not only the scalar magnitude | New: GSRM v2.1 velocity-gradient tensor. Existing: `geod_shearrate` (B7), `geod_dilaterate` (B8) | Angle between the local fault normal and the principal extension axis, sampled on the cached grid | Targets faults whose orientation is kinematically favoured but unmapped. Existing lanes use scalar strain or a fixed N15°E tendency | `coulomb*` lanes use fixed-strike Coulomb tendency; the orientation signal is different. Overlap is partial | **Obtainable, not yet fetched.** GSRM v2.1 is published (Kreemer, Blewitt, Klein 2014, [G3 doi:10.1002/2014GC005407](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014GC005407)) and offered via the GEM "Open Version Download" ([GEM GSRM page](https://www.globalquakemodel.org/product/gsrm)). Its method is a spline-based regional velocity-gradient model (per the paper's abstract), so it is unlikely to resolve 100 m structure. This is an inference from the method description, not a checked grid spacing. Treat it as a regional prior | Regional strain gradients along plate-boundary geometry, not local faults. Falsify if the signal reproduces the Walker Lane boundary with no local structure |
| 2 | **Drainage-divide migration residual** (carried over from `REVIEW_376A8469.md`) | 3DEP DEM (B12, B19) | Basin-integrated divide imbalance, conditioned on local relief | Distributed recent deformation can tilt catchments where erosion has erased a scarp | `DRAINAGE_KNICK` and `HYDROCONDUIT` use knickpoints and alignment, not divide position. Partial overlap | Present in the cached stack | Lithologic erodibility contrast and climate gradients |
| 3 | **Basement-residual gravity** | B13 `iso_grav_anom`, B15 `depth_to_base_surf` | Residual = B13 minus the forward gravity of the B15 basin model. Look for a lineament in the residual gradient | Faults offset basement under cover; the residual can show offsets the basin model misses | `POISSONFLEX` (gravity, basement rollover) and `COULOMB*` use B13/B15. **High overlap risk** | Present. The density contrast must be sourced before any run; none is cited here | Density heterogeneity (plutons, volcanics) and basin-model error |
| 4 | **Magnetic-texture displacement** (carried over from `REVIEW_376A8469.md`) | B2 `rtp` | Along-strike step in the best-fit displacement of magnetic texture across trial lines | A buried lateral splay can offset older magnetic fabric | Magnetic lanes exist; the displacement operator is new. Cost is high | Present, but line spacing may not resolve it. Identifiability is uncertain | Lithologic boundaries that look like offsets |
| — | *Rejected before test:* conductive-but-quiet zones (B17 vs B2) | B17, B2 | Co-located low magnetic and high conductivity | Would flag alteration | Duplicates the smectite clay-cap logic (Group E) and `XPHASE` | Present | — |

**Recommendation:** rank 1 is the only candidate that adds a new information channel (orientation rather than amplitude) and its data are published by an official source. Its cost is low once GSRM is downloaded. Its resolution limit means it should be a regional prior, not a standalone detector. Validate it on the spatially blocked holdout before any slot decision. It must beat the current holdout best (`KNICKLOQO static 0.010788`).

## 7. What I did not change, and why

- **The binding uniqueness rule.** The rule is the user's protocol. Changing it, or reading "dots" as "positive pixels" in a way that clears the gate, would be a policy decision. Section 5 item 3 asks for that decision.
- **The homepage primary download** (`docs/index.html`, `COULOMBDM s45`). The CI primary-receipt check passes for it, and changing it would require a new audit receipt. No new evidence supports a different primary.
- **No new TIFF.** The brief asks for a unique submission TIFF. No candidate can clear the literal gate (Section 2), and a file that cannot clear the gate would not be a valid submission. I did not write a placeholder, copy a prior file, or use a competition slot.

## 8. Limitations and what the project needs

1. **A decision on the uniqueness-gate interpretation** (Section 5 item 3). Without it, no file is eligible.
2. **An ORGANIZER-CONFIRMED receipt** for any score. The only organizer numbers available are the public leaderboard values, which do not identify our files.
3. **GSRM v2.1 downloaded and hash-verified** before H1 is tested. Not done this session.
4. **Density-contrast source** before H3 can run (not yet cited).
5. **DrivenData login** to read the data page and submission receipts (login-walled from this sandbox).
6. **Time budget:** 3 experiments and 2 hours per session. The next session should run H1 only.

## 9. Next session (ranked)

1. Decide the gate interpretation (Section 5 item 3) with the user, then re-run `make verify` and `make site` under that decision.
2. Fetch GSRM v2.1 from the GEM page, record its SHA-256, and run H1 as one pre-registered experiment on the holdout.
3. Generate the "latest artifact" pointers (README blocks, `docs/index.html`, root `index.html`) from one source, and add the root stub to `check_site.py`.
4. Replace the request brief's 0.3195 "highest" reference with the official 0.4413 #1 value everywhere it appears.

## 10. Run record

```json
{
  "schema": "gemsdoe92-repo-review-2026-10-25",
  "session": "911a9a62",
  "experiments_used": 0,
  "experiments_budget": 3,
  "slots_used": 0,
  "verdict": "negative (do not submit)",
  "tests": {"command": "python -m pytest tests -q", "result": "367 passed"},
  "make_manifest": "RESULT: OK",
  "make_verify": "PARENT VERIFIED (pinned artefact) h33-h33-2-b2 sha256 c55bafc47005...",
  "make_site": "SITE CHECK PASS (63 served raster(s) gated)",
  "witness": {
    "raster": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
    "sha256": "ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be",
    "finite_positive_cells": 5167373,
    "nan_cells": 7111787,
    "grid": "EPSG:32611 3730x3292, transform matches sample_submission.tif"
  },
  "leaderboard": {"source": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/", "rank1": ["xiaofanhu", 0.4413], "rank2": ["cfld__", 0.3916], "class": "ORGANIZER-CONFIRMED (public leaderboard read 2026-10-25)"},
  "claims_not_receipts": ["GEMSDOE32 h33-h33-2-b2 0.2778 (not on page read; page states no organiser score)"],
  "irregularities_flagged": 8,
  "uniqueness_gate": "literal overlap = 1.0 vs full-footprint witness; interpretation needs decision"
}
```
