# SLOT_PLAN — current selector state (2026-10-24)

## Current primary artifact: SIGNED-GAMMA f45 — format-valid, holdout-positive, like-for-like unique (literal duplicate is universal-blocker triviality)

`h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc` (zeros sha256 `fd3df7385ed7f0041c6df51946f3fe7a56631f4400547acb47ca00de6f0f0d88`, nan `d1ab5ddc9f298a…`, 37,654 dots) is the current primary download. It passes all file-format gates and is obviously downloadable (one-click TIF + ZIP, audit JSON beside file, banners + executive summary).

- **HOLDOUT-DTI** `gems57-pooled-hide-v2`, 8 buffered whole-component folds (4 quadrants × seeds 20/30), 22,663 withheld positives, pooled α0.2 β0.8 300 m triangular kernel, 1k paired 20 km draws: candidate **0.005305 [0.004174, 0.006441]**; parent R0 **0.004006 [0.003408, 0.004651]**; paired **Δ +0.001299 [+0.000464, +0.002370]** (CI excludes 0). Leakage canary max symmetric AUC 0.5511 (<0.90 PASS). SGMC off-catalogue PROXY (bedrock faults) 0.062 vs R0 0.093 Δ −0.031 — negative because SGMC is bedrock faults, not concealed basin-fill steps (expected disconnect; BREAKLINE by contrast +31% as topographic).
- **REGISTRY-MEASUREMENT:** local 14-raster worst forward 3-px overlap **0.550** vs parent R0, worst |Spearman ρ| **0.547** — **unique** under 0.70/0.90 (55.0% is R0 kept portion; vs visible-collar only 3.5% φ≈0.001, disjoint lanes). Public literal 1,279-raster scan has **not** been re-run on this exact file this session; the 17GEMSDOE `E-proba-multiscale` full-footprint surface (5,167,373 positives, halo covers 100% of allowed domain → 0 uncovered allowed cells per `vendor/gems57/uniqueness.py::saturation_certificate`) is a **universal blocker**: any non-empty dot set is 100% literally overlapping. Thus **NOT CLEARED FOR A WEEKLY SLOT under the literal rule** is trivially true for every candidate and is disclosed; **like-for-like (dot-fields only, support <0.20, halo<0.70) excludes that dense surface → 55.0% → UNIQUE**, which is the informative test for dot submissions (see `evidence/uniqueness_saturation_certificate.json` and `vendor/gems57/uniqueness.py::two_phase_summary`).
- Format validation: 10/10 MUST gates pass (float32, EPSG32611 3730×3292, transform 100/243350/−100/4508550, [0,1], no NaN inside, zeros outside, d_cat>2, zero catalogue mass, sha256-recorded). Auditor `docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-audit.json`.
- **Verdict: PROMOTE under like-for-like dot-field rule (locally unique + holdout-positive with CI excluding 0, no leakage); NOT CLEARED under literal universal-blocker rule — human selector must choose policy.** No weekly slot used yet. If uploaded, receipt Δ vs CLAIM 0.2778 decides next dose: Δ ≥+0.01 ⇒ gravity offset earns live credit (walk far dose 38→45→50 next); Δ ≤−0.01 ⇒ offset hurts (retire); |Δ|<0.01 ⇒ no evidence, hold dose fixed. Never pair SIGNED-GAMMA and BREAKLINE in one week.

Site: `docs/index.html` (primary banners, one-click download, all 11 served files linked), `docs/SUBMIT.html` (3-step submission guide with name/note), run card `evidence/signed_gamma_run_card.json` (also `docs/downloads/signed_gamma_run_card.json`).

## Scan scope and comparison boundary

Local scan: 14 rasters (lane_registry_index.json). Expanded public scan (visible-collar audit, 2026-10-24, `evidence/public_registry_uniqueness.json`): current default-branch TIFF paths in `docs/downloads/`, `releases/`, submission directories across 102 public repos matching GEMSDOE in `buffedlizard55-lab`; trees complete in initial API scan, 1,285 unique Git blobs SHA/size-verified, 1,279 single-band rasters matching sample grid compared. Audit is not exhaustive of historic branches, unlinked/site-hosted assets, private repos, zip-only artifacts, or other owners. Since then the scan has not been refreshed for SIGNED-GAMMA; the universal-blocker proof (0 uncovered allowed cells) suffices to disclose literal outcome without re-download.

The largest prior literal overlap is 100% against `11GEMSDOE/docs/downloads/gems-structural-area06-v1.tif` (343,526 positives); additionally `17GEMSDOE_E-proba-multiscale` positive across full footprint is also 100% literal witness. The site discloses both literal (trivial duplicate) and like-for-like (dot-field unique) readings; the selector's policy decides which governs submission.

HOLDOUT-DTI is a local catalogue hide-and-recover estimate, not a competition score, and cannot be compared with CLAIM 0.2778. Prior leaderboard snapshot (2026-10-24) 0.4413 at #1 is LEADERBOARD-SNAPSHOT, not a receipt for this candidate; prompt's 0.3195 is older conflicting snapshot. No ORGANIZER-CONFIRMED receipt exists (ledger 37 BUILT / 0 RECEIPT).

## Historical results retained

- **Visible-collar R0-excluded** (2–3 px annulus around visible Qfaults, excluding R0 3-px halo): HOLDOUT 0.046866 [0.0402,0.0533] vs R0 0.004006 delta +0.04286 — but **literal duplicate 100% overlap** (131/1,279 >70%, universal blocker) → **NOT CLEARED FOR A WEEKLY SLOT — DUPLICATE UNDER THE LITERAL REGISTRY RULE** (now archived, still downloadable, still FORMAT-VALID).
- **BREAKLINE f45Ltop** (20,710 kept + 16,944 far on linear DEM slope-break coherence Bands 19/12, >3 px off H19-5): HOLDOUT 0.004861 [0.00403,0.00582] delta +0.000854 [+0.00030,+0.00142] SGMC +31% vs R0; local unique 55.0% vs parent, 18 rasters, 3.5% vs collar — **negative / NOT CLEARED** (below holdout-best arms; public scan not yet run → local uniqueness only). See `docs/ANALYSIS_20261024.md`, `docs/HYPOTHESES_20261024_BREAKLINE.md`, `evidence/breakline_run_card.json`.
- DILATATION p10/p12/p15 and RELIEF p10 had positive local HOLDOUT-DTI but flagged as R0 duplicates under literal >70%/3px rule. TIPGAP FAR and STEPOVER were negative on documented holdouts. Keep as negatives.
- Parent R0's 0.2778 remains **CLAIM** until dated receipt in `ledger/submissions.csv`.

## Next steps

1. Human selector reviews this primary's two readings (literal universal-blocker duplicate vs like-for-like dot-field unique + holdout-positive) and decides slot policy; weekly cap applies, one dose per week max, never pair SIGNED-GAMMA and BREAKLINE together.
2. If selector accepts like-for-like reading, upload SIGNED-GAMMA f45 once (exact name/note, zeros-outside TIF or ZIP) and record ORGANIZER-CONFIRMED receipt; apply receipt decision rules above.
3. Periodically refresh public registry scan (`scripts/audit_public_registry.py --candidate docs/downloads/h33-h33-2-b2-SIGNEDGAMMAf45-20261024-d1ab5ddc-zeros.tif`) when GitHub API permits; record date/scope. Informative like-for-like reading will remain unique unless a new dot-field raster appears with >70% overlap.
4. Preserve off-catalogue SGMC proxy (bedrock-fault disconnect) as diagnostic; true uncatalogued performance remains unmeasured until organizer receipt.
5. GeoDAWN 19-band stack is now pinned (418 MB, sha256 4371c82e…, via `registry/session_manifest.json` → `.cache/gems_inputs/`); no longer missing.
6. Resolve public-repository redistribution terms for committed rasters; see `IRREGULARITIES.md`.
7. No further candidate experiments until after receipt; budget 3 experiments / 2 h per session respected (this session 1 lane built).
