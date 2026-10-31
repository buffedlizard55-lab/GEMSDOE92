# Standing prompt — 2026-10-31 (verbatim user brief) — READ FIRST EVERY SESSION

Stored so that every future session starts from the same requirements. Mirrors the
repository convention (`docs/STANDING_PROMPT.md`, `SESSION_PROMPT.md`).

---

## Current user brief — 2026-10-31

Review the repo.

I want to focus on the highest scoring submissions from the following sites, GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36. I want an executive summary on every site that is clear and obvious which is the best submission to submit to obtain a high score on the leaderboard. It should also be unique and not an exact duplicate of any previous submission that is the same as below. Keep iterating and testing until we have the highest scoring submission to download and submit.

We should be able to estimate the score for a submission. I want a table in the executive summary that clearly lists what file to download, what the estimate score is, and whether it is a unique submission unlike any of the other GEMDOE sites listed below.

**THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!**

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

### PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. **LANE.** Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack, `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.
4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.
5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
6. **BUDGET.** Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The following sites should serve as a starting point for understanding how to generate TIF submissions. These websites are researched, and tested and have generated TIF submissions. But we need to generate high scoring submissions.

[The brief then lists the nine focus sites with their owner-reported scores; the full inventory is
kept machine-readably in `docs/downloads/claimed-site-scores.csv` and `ledger/`.]

We need to study, analyze, and understand the highest score from the GEMDOE site where the submission TIF is downloaded from, which is
https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html — `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778`.
Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778? Answer the question using PhD level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition. Must be unique submission unlike any within the GEMSDOE sites above. Verify working line by line no hallucinations.

### Standing operating requirements carried forward

- Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted, why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.
- Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations.
- We need to do deep research and critical thinking and come up with new hypothesis to test. Store all information and knowledge gathered from official verified sources, so it serves as a starting point for other projects. Find sources of data that others are overlooking. Be contrarian but smart.
- **Put this prompt into the repo readme and read it everytime we work on the project** as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use. It should solve the problem of having to manually check everything ourselves and having an up to date current feed.
- Core values: **Maximize P(Win)** and **Own the Outcome**.
- The site should be able to generate a TIF file that is required for submission. It should be as easy as download to click a File to submit into the competition. This needs to be in the executive summary or the very beginning of the site. It should be obvious when you visit the site.
- Portal format: single-band GeoTIFF (or a ZIP with one GeoTIFF) matching the submission format's CRS, shape and geotransform; values must be in [0, 1] or the portal rejects with *"Predicted values must be in range [0, 1]"*. Give it a unique name and a short comment (≤140 characters) to tell submissions apart.
- Create an executive summary subpage that explains exactly how to make a submission into the contest.
- Run this task through multiple passes: (Pass 1) implement and verify; (Pass 2) review for bugs, missing requirements, incorrect assumptions, edge cases; (Pass 3) re-check against the original request and improve accuracy, reliability, completeness and code quality. Do not stop after the first pass.
- Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project.

### Competition facts (verified links, for manual review)

- Problem description and metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition home, dates, prizes: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Public leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Official rules (NLR PDF): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index · Projection: https://epsg.io/32611
- GeoDAWN (USGS, DOI 10.5066/P93LGLVQ): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS (GBCGE): https://gbcge.org/current-projects/ingenious/
- Data tab (login required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/

### Standing blockers (unchanged)

1. **No DrivenData auth** → `training_features.tif`, `labels.tif`, `sample_submission.tif`,
   `1m_DEM_links.csv` cannot be downloaded here. The official 19-band stack is therefore
   unavailable; work from public mirrors and externally sourced official layers.
2. **No organizer receipt** exists anywhere in this repository. Every leaderboard number is a
   `CLAIM` unless copied from a submission-page receipt.
3. **GitHub REST rate limit** is 5,000/hour and is shared across concurrent sessions; prefer
   `codeload.github.com` tarballs and offline cache rebuilds
   (`scripts/gx_registry_index.py`) over per-blob API calls.
