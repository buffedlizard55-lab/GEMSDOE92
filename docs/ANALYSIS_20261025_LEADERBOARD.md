# Analysis — why `h33-h33-2-b2` scored `0.2778` (CLAIM), the live leaderboard, and what is blocking a new submission

**Session:** 2026-10-25 · branch `arena/09f84f2f-gemsdoe92` · **Verdict: no new submission-eligible TIFF. Research download only. Decision required (see §5).**

Evidence labels used below: `OFFICIAL` = official DrivenData / NLR rules page, read this session;
`ORGANIZER-CONFIRMED` = a submission-page receipt (none exists in this repository for any GEMSDOE site);
`CLAIM` = a number copied from a GEMSDOE site, receipt `N`; `HOLDOUT-DTI` = our own hide-and-recover instrument;
`REGISTRY-MEASUREMENT` = a fresh measurement against a pinned public raster.

---

## 1. Short answer

1. **`0.2778` is a `CLAIM`.** The GEMSDOE32 page is not an organizer receipt, and the
   repository's own forensic record marks it `receipt=N`
   (`evidence/r0_forensics_20261024.json`). Nothing here proves that it is the highest score.
2. **The mechanism that the repository's forensic analysis proposes** is geometric: 37,654
   unit-mass dots spaced at about the kernel radius (median nearest-neighbour `3.0 px` = `R`), with a
   clearance of more than 2 px from the catalogue (`0` dots on the catalogue). The tested
   off-catalogue proxy does **not** confirm it. On the SGMC proxy, R0 scores `0.09606`, below the
   H19-5 skeleton it was built from (`0.10060`). **The mechanism is consistent with the claim but not demonstrated.**
3. **Can we beat `0.2778`?** Not demonstrated. No candidate in this repository has an
   organizer score. The best holdout values in the repo are not comparable with the organizer metric (§3).
   The honest route to a score is the official leaderboard, which allows **3 submissions per week** (`OFFICIAL`).
4. **Why no new submission is clear today:** the literal universal duplicate stop (§4), which
   fresh measurement confirms again this session.

## 2. Live leaderboard (fetched 2026-10-25) — `OFFICIAL`

Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
(public-test "best public DW-Tversky", top 50 read in full).

| Rank | Participant | Public score |
|---|---|---|
| #1 | xiaofanhu | **0.4413** |
| #2 | cfld__ | 0.3916 |
| #3 | Batik Shirt Brothers | 0.3904 |
| #4 | BrandenKMurray | 0.3724 |
| #5 | No Fault of Our Own | 0.3539 |
| #23 | like60986 | 0.3217 |
| #24 | twang | 0.3169 |
| #50 | moongrega | 0.2818 |

**Irregularities:**
- **IR-25-0.3195:** `0.3195` does **not** appear in the top-50 snapshot. The values
  either side of it are `0.3217` (#23) and `0.3169` (#24). The prompt's "0.3195 is the highest score right now" is not supported by this page.
- **IR-25-0.4413-NOT-GEMS:** `0.4413` is xiaofanhu's score. It is **not** a GEMSDOE entry, although the prompt lists it as the "GEMSDOE high score".
- **IR-25-0.2778-OFF-BOARD:** `0.2778` is below the #50 value (`0.2818`) on this snapshot, and no
  GEMSDOE team appears by name in the top 50. If `0.2778` were a live public score it would sit
  below rank 50, and it is `CLAIM`-labelled in any case.
- Public and private scores differ. The private test set decides the Initial Round, and the
  expanded label set decides the Final Round (`OFFICIAL`, problem page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## 3. Why the repository's forensic analysis says `0.2778` is high (and what it does not prove)

Source record: `evidence/r0_forensics_20261024.json` (generated from the shared evaluator).

| Stage (same 19-band parent) | Dots | Nearest-neighbour median | Dots on catalogue | Off-catalogue SGMC proxy (`CLAIM`-grade proxy) | Fixed-catalogue diagnostic (not a holdout) |
|---|---|---|---|---|---|
| H19-5 skeleton (raw) | 121,131 | 1.0 px | 0 | 0.1006 | 0.1664 |
| D2.8 thinned | 44,090 | 3.0 px | 0 | 0.0953 | 0.1618 |
| **R0 = `h33-h33-2-b2` (`d_cat > 2`)** | **37,654** | **3.0 px** | **0** | **0.0961** | **0.0067** |

Reading the table:
- The spacing is the kernel radius. A dot spaced at `R = 3 px` covers its own truth pixels without
  wasting coverage on a dense neighbour. This is a metric-matched design choice, and the repo's
  forensic conclusion is "spacing matched to kernel plus clearance".
- The clearance removes catalogue-adjacent dots. Those dots are only useful if the private
  faults lie on the catalogue, which the competition says they do not (`OFFICIAL`:
  "newly identified faults … not contained within the current public USGS database").
- **What the table does not show:** R0 does not beat its own H19-5 parent on the off-catalogue
  SGMC proxy (`0.0961` vs `0.1006`). The large drop in the fixed-catalogue diagnostic
  (`0.1664` → `0.0067`) is a *diagnostic of catalogue overlap*, not a holdout. The forensic
  explanation of `0.2778` is therefore **not confirmed by any off-catalogue measurement in this repository.**

### 3a. Metric facts, verified this session — `OFFICIAL` + independent check

The official distance-weighted Tversky index (problem page, equations as transcribed):
`TP_w = Σ_g max_x p(x)k(d)`, `FP_w = Σ_{p>0} p(x)[1 − max_g k]`, `FN_w = Σ_g [1 − max_x p k]`,
`DTI = TP_w / (TP_w + 0.2·FP_w + 0.8·FN_w)`, `k(d) = max(1 − d/3, 0)`.

- **Independent check:** a naive transcription of those equations (no shared code) agrees with
  the shared evaluator `vendor/gems57/metric.py::dti_exact` to `2.2e-16` on 40 random grids.
  It is now a permanent regression test: `tests/test_metric_independent.py`.
- **Worked example:** `3 / (3 + 0.2·1.89 + 0.8·2) = 0.6027`, which the official page rounds to `0.60`.
- **Why the metric rewards spacing-matched dots:** `α = 0.2` makes a wasted dot cheap, and
  `β = 0.8` makes a missed truth pixel four times as costly. `T` saturates at 1 per truth cell, while
  `M` saturates at 1 per dot. A cluster of dots around one truth cell therefore earns less than its count
  suggests, which is why a dot every `≈R` px outperforms a dense band.
- **The organizer's `known` mask is unverified.** The shared evaluator has a `known` argument
  for pixels the organizer excludes from scoring, citing an organizer thread. That thread is not
  in the official pages read here, so the mask is recorded as **unverified**.

## 4. Gate status — binding, fresh, reproduced this session

- Fresh run: `python scripts/audit_readiness.py --fetch-witness` → **`CONFIRMED DUPLICATE STOP`, exit 1**.
  Receipt: `evidence/readiness_20261025_leaderboard.json`. The witness is the 17GEMSDOE E-proba raster,
  SHA-256 `ab0a0a62…`, Git blob `374c88b1…`, fetched via `gh api` and byte-verified.
- The witness is positive at all `5,167,373` footprint cells. Any nonempty in-footprint candidate therefore
  has forward 3-px overlap `1.0 > 0.70`. This is a property of the witness and the literal
  rule, not of any particular candidate.
- **Consequence:** a new TIFF cannot be cleared under the literal rule. Placing one would only
  produce a duplicate. The protocol says to stop, so **no new raster was placed**.

## 5. Decision required (the single blocker)

The question is not technical. It is how "dots" should be defined when the witness is a
dense probability surface. The options are:

| Option | What it means | Status |
|---|---|---|
| **A. Keep the literal rule** | Any dense 100%-footprint raster blocks every candidate. No new submission can be cleared. | Current default. |
| **B. Dual reading** | Compare the witness's top-N values to our N dots. VENTSCARP scores `0.6947` under this reading across 102 public repos. | Needs written approval. |
| **C. Ask the organizers** | The rules invite competitors to ask the organizers when unsure (`OFFICIAL`, competition homepage: "ask the challenge organizers in the competition forum … or send an email to gemsprize@nlr.gov"). This is the only route that can settle it. | Recommended in parallel. |

Whichever option is chosen, the selector still decides whether to spend one of the three weekly
submissions. Nothing in this repository spends a slot.

## 6. Official rules that constrain any submission (read this session)

Source: https://docs.nlr.gov/docs/fy26osti/96647.pdf (Official Rules, September 2026), sections 3.2–3.6 and Appendix A.
- **One** GeoTIFF, **single raster layer**, 100 m, covering the whole GeoDAWN study area (§3.2).
- **Three submissions per week** on the platform (§3.2, §3.4).
- **One final submission** chosen before the deadline, without knowledge of private scores (§3.4, §3.6.2).
- **Generative-AI use must be disclosed in the narrative** (§3.2). Our `AI_USE.md` is relevant but is not a
  substitute for that narrative.
- Finalists must supply code and documentation sufficient to reproduce the result (§3.5). This repository
  is structured for that, but the reproduction path depends on restoring pinned inputs.
- **Organizer judging is human.** DOE designates a Federal judge and applies policy factors (§3.6.4).
  Our automated checks cover format and gates. They do not replace that judgement, and the user's
  "no human inspection" requirement applies to our validation pipeline only.
- Competition end: **3 Dec 2026, 11:59 p.m. UTC** (https://www.drivendata.org/competitions/306/competition-doe-gems/).

**Unverified in this session:** the rules page also links the full rules at herox.com (`https://www.herox.com/GEMSPrize/resource/2274`),
and the weekly cap is quoted only as "three per week". The competition page refers to the cap but was not read as a live
number here.

## 7. Limitations and what is needed to go further

1. **Organizer receipts** for any candidate. The only score that counts is the one returned by the platform for a chosen file.
2. **Policy decision** on the dense witness (§5). This is the single blocker.
3. **External data:** the 1 m DEM and the USGS ComCat catalogue are not reachable from the sandbox
   (`docs/HYPOTHESES_20261025_LEADERBOARD.md`, H4 and H5).
4. **Data-use check:** `IRREGULARITIES.md` already flags that sibling public GitHub repositories
   contain login-walled DrivenData rasters with unchecked redistribution terms. Those rasters must
   not be reused in a public submission until their terms are checked.
5. **Holdout ≠ leaderboard.** Every holdout number in this repository is a surrogate recovery
   test on catalogue faults. It is not a competition score, and the registry gap is not closed by holdout alone.

## 8. Irregularities flagged for review

- **IR-25-A (prompt vs page):** `0.3195` is absent from the live top 50 (§2).
- **IR-25-B (prompt label):** `0.4413` is xiaofanhu's public score, not a GEMSDOE score (§2).
- **IR-25-C (claims):** all GEMSDOE scores in the repository are `CLAIM` with `receipt=N`, including `0.2778`.
- **IR-25-D (stop):** the literal universal stop is confirmed fresh this session (§4). It blocks every candidate.
- **IR-25-E (cross-check field):** `evidence/r0_forensics_20261024.json` contains a
  `"expected": 0` field next to the official worked example, whose value is `0.6027`. The field is a leftover and
  does not change the arithmetic. Recorded here rather than silently edited.
- **IR-25-F (data use):** sibling-repository rasters with unchecked redistribution terms (`IRREGULARITIES.md`).
- **IR-25-G (unverified mask):** the organizer `known`-mask thread is cited in the code but not in any official page read here.

## 9. Sources (all official unless marked)

- DrivenData competition overview: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem description and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard (fetched 2026-10-25): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official rules (NLR, Sept 2026): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Rules link on DrivenData (herox): https://www.herox.com/GEMSPrize/resource/2274 (linked, not read this session)
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN data (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS Great Basin compilation (labels; DOI from the rules): https://doi.org/10.15121/1881483
- EPSG:32611 (UTM 11N): https://epsg.io/32611
- Tversky index background: https://en.wikipedia.org/wiki/Tversky_index
- Phase congruency (Kovesi 1999): https://www.peterkovesi.com/papers/Kovesi_Videre_v1n3001.pdf
- Fault-surface roughness (Renard et al. 2013): https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012GL054143
- Fault-surface roughness (Candela et al. 2012): https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2011jb009041

## 10. Run card

`evidence/leaderboard_session_20261025_run_card.json` (generated by `scripts/make_leaderboard_session_card.py`
from files, not transcribed). Verdict: **negative**. `submission_eligible: false`. `experiments_used: 0`.
