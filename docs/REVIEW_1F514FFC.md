# Repository review — 2026-10-25 (1f514ffc)

## Executive decision

**Existing TIFF: OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT. No new TIFF generated.**

[Existing exact TIFF](downloads/h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif) · [submission guide](SUBMIT.html) · [review run card](downloads/review_1f514ffc_run_card.json).

The requested new, submission-cleared artifact remains **unfulfilled**, not implicitly satisfied by an old file. No experiments, placement, holdout runs, selector promotions or competition slots were used. There is no assigned single method paragraph in the current prompt; this session is a validation-only review. The instruction to stop on a registry duplicate takes precedence over continuing experiments.

## Pass 1 — inspect and reproduce

Reviewed repository structure, session contract, prior review/next steps, shared validator and preflight, CI and Pages workflows, existing downloads, manifest and parent recipe. Installed requirements into ignored `.venv` (the base Python had no pytest).

Fresh **REGISTRY-MEASUREMENT**: downloaded the [pinned witness Git blob](https://api.github.com/repos/buffedlizard55-lab/17GEMSDOE/git/blobs/374c88b1da2b803e2ed160de467fd71ae114010d), verified its SHA-256 and sample-grid identity using the existing shared preflight. All 5,167,373 footprint cells are positive. Thus any nonempty set of in-footprint dots overlaps this witness by 1.0, above the literal 0.70 threshold. This is a sufficient rejection, not a full scan, not geological equivalence, and not measured correlation for an unbuilt surface. [Fresh pre-placement evidence](downloads/review_1f514ffc_preflight.json).

Fresh **REGISTRY-MEASUREMENT**, unchanged primary: forward overlap 1.0; Spearman 0.04724711160801543. Format reread confirms finite values in [0,1], zeros outside, matching CRS/shape/transform. [Fresh primary witness evidence](downloads/review_1f514ffc_primary.json). It is unnecessary to generate another candidate to prove that it would also fail. We did not threshold the dense witness, exempt it, copy/rename a parent, or generate an empty TIFF to evade the rule.

### Why the reported GEMSDOE32 result is plausible, not proven

The supplied 0.2778 and conflicting 0.3195/0.4413 leaderboard values are **USER-REPORTED, UNVERIFIED**, not ORGANIZER-CONFIRMED receipts. No current leaderboard claim is made. Repository parent verification checks pinned bytes and lineage, not private-label performance.

The stored lineage thins an older skeleton and removes catalogue-adjacent dots. Under the shared local distance-weighted metric, redundant prediction kernels can add less truth coverage than false-positive cost; removing some can improve the ratio. This explains a plausible mechanism, not a causal leaderboard ablation or proof of optimal spacing. Catalogue-gap discovery is also not the same task as verifying a geothermal vent or productive reservoir.

Re-retrieved the [official reference notebook](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb), Git blob `d45bf7bdb1d31a22caa38371ad195c2f6eb965ae`, SHA-256 `1a7622732ba00f67237058bc0efe79b45ba4e87c449fc9c1e5d6ea659de92ca0`. Cell 16 explicitly sets alpha=0.2 for false positives and beta=0.8 for false negatives **in training loss**. This does not certify the local distance-weighted evaluation implementation. The official baseline uses random patch splits; those are not evidence that our stricter spatial holdout is equivalent to organizer scoring.

### Ranked conditional hypotheses — no score projections

The previous review already proposed the following unimplemented exact operators. They remain the next scientific shortlist rather than pretending repeated proposals are newly discovered methods. Novelty across all sibling repositories is unverified. All use the template's pinned numerical feature stack in principle; it is not staged here, and none is viable under the current duplicate stop. Expected improvement is unknown: ordering reflects complementarity and cost, not invented DTI estimates.

| Priority | Layers and signature | Why it might find unmapped faults | Difference from implemented methods | Non-fault mimic / cost |
|---|---|---|---|---|
| First | B12 DEM: repeated same-signed displacement of paired stream crossings using a drainage graph | Oblique-slip traces may offset channels without a continuous high-amplitude scarp | Paired channel topology, not HYDROCONDUIT ridge strength or monotonicity | Stream capture, fan avulsion; high cost, coarse-grid risk |
| Second | B2 RTP: scale-persistent complex-wavelet phase winding around contact terminations | Buried splays may terminate or displace magnetic contacts without terrain expression | Topological phase defects, not RTP amplitude, tilt or Hessian ridges | Intrusion tips and lava-flow edges; medium cost |
| Third | B12 DEM: fitted constant-elevation shoreline null, testing residual cross-contour continuity | Suppress pluvial shoreline false positives that obscure weak fault traces | Explicit competing-process model, not another scarp/coherence gate | Warped shorelines and terrace risers; medium cost, false-negative risk |

No new external source is required for these conditional operators. They are not approved experiments. If the protocol is explicitly revised, restore the pinned cache through `scripts/restore_inputs.py`, confirm data-use rights, assign one lane, and run constituent-feature leakage canaries before the shared hide-and-recover evaluation. Compare identical fold-visible masks and budgets with a freshly rebuilt control using paired spatial uncertainty. Do not compare static-mask and fold-visible HOLDOUT-DTI as if they were the same instrument. No candidate is cleared merely by having a high local score.

## Pass 2 — fix the publication inconsistency

`check_site.py` formerly accepted the first TIFF link when no `data-primary="true"` link existed, whereas CI required exactly one explicit primary. In particular Pages calls the former, so publication and CI could disagree. The shared site checker now parses anchors, requires exactly one marked primary, rejects duplicated href/marker attributes and nonlocal/traversing paths, and accepts either quote style and attribute order. There is no fallback to link order. Updated the missing-receipt fixture to explicitly select its primary, so it still exercises the receipt path rather than the new missing-marker failure. No TIFF bytes or historical receipts were modified.

## Pass 3 — acceptance and limitations

Final local checks: 289 tests passed (124 nonfatal upstream Affine deprecation warnings); all 43 served zeros-outside TIFFs passed the site validator; pinned input manifest, parent verification and ledger checks passed; `git diff --check` passed. These are software/format results, not HOLDOUT-DTI or organizer scores. No new holdout score, withheld-positive count or confidence interval exists for this review.

Fresh GitHub Pages API still reports **legacy** build mode at the repository URL. The Actions publication validator cannot be claimed to protect legacy publication. Prior attempts to change the repository setting were denied; this session does not claim deployment success. GitHub API access permits repository work, but not authenticated DrivenData downloads/submissions or live non-GitHub research here.

Next work, in order:

1. Explicit owner/selector resolution of the dense-probability-versus-dot uniqueness definition. No silent sparse-only exemption.
2. Assign one method lane; verify official data provenance/rights and stage the pinned feature cache. `labels.tif` and `existing_faults.tif` have identical manifest hashes; hide-and-recover is a surrogate, not access to hidden organizer labels.
3. Run leakage canaries and comparable spatial holdouts within the experiment budget; retain negative results. Only a separate selector may promote an improvement.
4. Verify current rules, weekly cap and data-use restrictions through the authenticated official page; collect organizer receipts for actual scores. Enable Actions-mode Pages with repository-setting authorization, then verify deployment.

Manual-review source links (not live verified here): [competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [GDR INGENIOUS](https://gdr.openei.org/submissions/1391). Outbound access is restricted to GitHub and package registries; inaccessible links are not evidence of verified content.

**Maximize P(Win):** do not spend a slot on unvalidated or duplicate work. **Own the Outcome:** expose the unmet artifact requirement, fix gates and preserve reproducible negative evidence.
