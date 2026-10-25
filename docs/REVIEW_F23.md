# Submission-readiness review — 2026-10-25 (f23ca2d2)

## Decision and unmet requirement

**Research downloads: available. Competition submission: blocked. No new TIFF generated in this review.**

The user requests a newly generated, unique, submission-cleared TIFF. That requirement remains **unfulfilled**, not waived. Fresh retrieval of the pinned registry witness proves every finite pixel of the reference footprint has positive support. Under the user's unchanged literal rule, any nonempty in-footprint candidate has forward overlap one and must stop before placement. An empty file, renamed copy, or matched-budget reinterpretation is not a solution. See [fresh pre-placement evidence](downloads/review_f23_preflight.json).

The supplied prompt has no single method paragraph assigning a geological lane. This session is a **tooling-review scope**, not a new geological lane. No geological experiment, fresh holdout, or competition upload is performed. The prior-session request to promote KNICKLOQO after accepting a different uniqueness rule cannot be executed under the present brief. This review instead addresses automatic validation and contradictory status presentation first.

## Research answer: why GEMSDOE32 might have worked

We retrieved the [GEMSDOE32 source page at commit 012e17b2](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/docs/index.html). It describes H33-2-B2 as pruning catalogue-adjacent predictions from a dotted predecessor. It explicitly states **UNSCORED** and **NO ORGANISER SCORE EXISTS**. Thus the prompt's **USER-REPORTED, UNVERIFIED 0.2778** is not an ORGANIZER-CONFIRMED receipt. The conflicting **USER-REPORTED, UNVERIFIED leaderboard values 0.3195 and 0.4413** are not independently verified current rankings here.

The repository's distance-weighted Tversky implementation uses a maximum prediction contribution per truth pixel: multiple nearby predictions need not provide additional truth credit, while additional prediction mass can incur false-positive cost. Pruning a redundant prediction can therefore help. But pruning useful predictions reduces recall, and a blanket spacing rule is not optimal. Catalogue-adjacent pruning is a plausible mechanism, not a demonstrated causal explanation of a private-label score. Zero-outside encoding addresses a local format risk; changing only outside-footprint encoding is not a scientific discovery improvement.

The actual target is fault prediction relevant to geothermal exploration. Neither recovering known fault segments nor predicting a surface lineament demonstrates an active vent, productive reservoir, permeability, temperature, or commercial viability. Magnetic contacts, lake shorelines, lithologic contrasts and differential compaction can mimic fault signatures.

**Could a different detector exceed the reported result?** Possibly, but this review has no evidence supporting a numerical forecast. Gains on static catalogue-exclusion masks, fold-visible hide-and-recover masks, SGMC proxies and private organizer labels are not interchangeable. Repeated selection over many previous experiments also biases the reused holdout best. Preserve a locked outer spatial test and compare candidates with the same control, mask, budget and paired spatial resampling before any later selector step.

The [official reference README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) was retrieved directly from the organizer's GitHub repository. It provides CPU as well as GPU environments: the inherited assertion that GPU access is mandatory is not correct. It is a benchmark, not a submission-page receipt or certification of our local evaluator.

## Conditional hypotheses — recorded before implementation

Expected HOLDOUT-DTI improvement is **unknown for every proposal**. Ranking below is qualitative expected value versus cost, not a score projection. These exact operators were not found in the inspected local `gems/*.py` implementations; novelty across all sibling repositories or the literature is **not established**. All are blocked by the current pre-placement stop. They reuse the manifest-listed numerical stack; its large feature raster is not staged in this fresh checkout. No new external dataset is claimed obtainable.

| Priority / expected value / cost | Layers and physical signature | Why a catalogue-missing fault might appear | Difference from current implementation / non-fault alternative |
|---|---|---|---|
| 1 / potentially complementary / medium | RTP magnetics and isostatic gravity: fit competing local cross-profile models (buried step, finite-width dyke, smooth contact) with held-out profile likelihood and explicit uncertainty | A buried density/susceptibility offset may survive where a scarp is eroded; the model rejects profiles explained equally well by an unfaulted source | Existing Euler/Poisson/gradient lanes rank derivative responses; this proposal ranks **out-of-sample model discrimination**, not edge magnitude. Mimics: intrusive dyke and stratigraphic contact. Reject nonidentifiable depth/dip fits rather than treating an arbitrary best fit as evidence. |
| 2 / potentially complementary / high | RTP plus K/Th/U radiometric texture: build a contact-adjacency graph; require several independently detected contacts to terminate against a common crosscutting boundary, stable under spatial resolution changes | A buried or weakly expressed crosscutting fault could interrupt several older units without a sharp topographic step | Unlike contact co-gradient or phase-winding lanes, targets **graph termination relations** across multiple contacts. Mimics: erosional unconformity, lava-flow termination, radiometric flight-line seams. Hold out whole contacts during confirmation. |
| 3 / uncertain, lower priority / high | RTP plus isostatic gravity: compare single-source versus multiple-source profile fits across upward-continuation scales; rank a persistent common discontinuity only when nuisance source multiplicity changes | A basement displacement might persist below superposed shallow volcanic sources that obscure catalogue mapping | Not another cross-scale amplitude ridge: requires **structural model selection under changing source multiplicity**. Mimics: intrusive complexes and sedimentary basin contacts. Resolution may make the hypotheses indistinguishable; negative/inconclusive is a valid result. |

If the protocol is explicitly revised and one lane is assigned later: restore byte-pinned inputs, verify band metadata, freeze controls and splits, run every individual feature's leakage canary, and use `vendor/gems57/evaluate_holdout.py` with buffered whole-segment withholding and visible-only catalogue features. Reuse `submission_writer.py`. Record pooled HOLDOUT-DTI, evaluator identity, withheld positives and spatial confidence intervals. Stop on literal duplicate or canary failure. At most three experiments; no slot selected automatically by a model's claimed improvement.

## Official-source and access ledger

| Source | Verification in this session | Use / limitation |
|---|---|---|
| [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) | GitHub commit and README retrieved; hashes in source receipt | Confirms benchmark and CPU option; not private metric/score access |
| [Competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | Not retrieved; host outside outbound allowlist | Manual-review link; no fresh claim of rules verification |
| [Submission/data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | Not retrieved; no DrivenData authenticated session | No weekly-cap or portal-acceptance claim |
| [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | Not retrieved | Conflicting prompt values remain unverified |
| [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | Not retrieved; host outside allowlist | Rules and redistribution permissions still need verification |
| [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | Not retrieved | Official starting point, not verified acquisition this session |
| [DOE GDR INGENIOUS](https://gdr.openei.org/submissions/1391) | Not retrieved | Official starting point, not new staged data |
| GEMSDOE32 owner site | GitHub source retrieved at pinned commit | Secondary provenance only; explicitly no organizer receipt |
| 17GEMSDOE witness | Git blob and SHA-256 verified; grid matched; footprint coverage recomputed | Rejection proof, not full registry clearance |

GitHub mirrors prove byte identity, not licensing or organizer provenance. The numerical stack restoration script exists; the prompt's `download_competition_data.sh` and `prepare_data.py` do not exist in this checkout. An autonomous process cannot bypass network restrictions or fabricate authenticated receipts.

## Three-pass verification

### Pass 1 — implement and verify

Reproduced the universal pre-placement rejection from newly downloaded, pinned witness bytes. Reviewed the shared evaluator/writer interfaces without creating a private fork or scoring a new candidate. Fixed the shared clearance-radius bypass, exact-grid checks and structured handling of invalid files. Baseline software verification passed all 367 existing tests; all 63 then-served TIFFs passed the corrected validator.

### Pass 2 — inspect assumptions and edge cases

Added regression tests for radius boundaries, malformed radius values, unreadable files, wrong-shape rasters, shifted catalogue grids, subpixel transform drift, empty footprints, malformed rejection receipts, stale historical banners, HTML escaping and contradictory note aliases. Fixed audit prose that said “All gates PASS” even when a gate failed. The current panel and machine-readable status are regenerated from file hashes and shared validator results; `check_site.py` refuses stale status. Historical panels are preserved in a collapsed archive, not presented as current clearance.

### Pass 3 — integration and acceptance

Integrated concurrent main-branch changes through `bbda6c5`, preserving the other session's LISTRICDIP research artifacts, tests and negative verdict. Those files were **not generated by this review**. The current named research download is now LISTRICDIP, inherited from that merge; the renderer follows the explicit primary link instead of hard-coding a lane. Its `submission_note` schema exposed an integration edge case, now normalized with a conflict check against the older `note` schema.

The integrated file checks passed **all 66 served TIFFs**, input-manifest verification, pinned-parent verification, and ledger verification. Before the last concurrent merge, the integrated software suite passed **402 tests**, with 140 nonfatal upstream Affine deprecation warnings; totals are also in the review run card. These are software/format checks, not competition scores. No TIFF bytes or historical holdout results were modified by this review. `git diff --check` passes.

[Full supplied site-score inventory (CSV)](downloads/claimed-site-scores.csv) is preserved as **owner claims**, not a new verified leaderboard feed. [Source retrieval/status receipt](downloads/review_f23_sources.json) separates retrieved GitHub material from inaccessible official pages. There was no fresh complete scientific audit of every sibling repository.

**Still unmet:** new unique, submission-cleared TIFF; validation of a new geological hypothesis; live official-source and receipt verification. The unchanged duplicate rule and absent lane preclude the first two; network/session limitations preclude the latter. This is a negative deliverable, not full completion of the scientific goal.

**Next session:** resolve the protocol conflict explicitly before any candidate generation; assign one lane; verify data-use permissions; freeze a comparable control and outer spatial test; obtain permitted official-source/receipt access; enable workflow-based Pages publication with adequate integration permissions. No secret or credential should be placed in chat or the repository.

 **Maximize P(Win):** protect slots from unsupported promotion. **Own the Outcome:** repair shared checks and publish the unmet requirement rather than call an old file a new submission.

## Concurrent merge correction before PR completion

The first merge attempt was refused after main advanced through `71f6ac4`.
Integrated those changes and preserved the parallel research code. Commit
`406638a` had introduced a new claimed clearance despite the known literal stop.
Its root validator was reproduced printing “ALL CHECKS PASSED” and exiting zero
after catching a missing-reference TypeError. It now delegates to shared
readiness checks and returns blocked status. The active “submit now” aliases
redirect to the current checked status; unsupported score projections and portal
guarantees are withdrawn. The original text remains in Git history.

Fresh reads confirm the parallel **TIFF hash correction is valid**; earlier
prose was stale. In contrast, the new receipt's byte count, shape order,
geotransform and nodata were demonstrably incorrect. These are now measured
from disk by the renderer, with regression coverage. No new candidate or score
was generated during this conflict resolution. The current numerical test total
is in the review run card; all served-file checks are repeated after integration.

Final post-conflict verification: **405 tests pass**, with 140 nonfatal upstream
Affine warnings; **66 served TIFFs pass** the full site checker. Manifest,
pinned-parent and ledger checks pass. These are software/format outcomes, not
competition scores. No candidate generation or weekly slot occurred.
