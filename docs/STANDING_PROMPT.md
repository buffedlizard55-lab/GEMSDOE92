# Stored competition prompt (standing requirements) — GEMSDOE92

> **Caveat (flagged):** this file is a **reconstruction from session notes, not the verbatim prompt.** The verbatim text was not available in this session. Paste the original prompt here verbatim before relying on this file as the record. The repo's `SESSION_PROMPT.md` is an earlier session addendum (branch `arena/591fc2bd-gemsdoe92`), not the full prompt.

## Standing requirements (as recorded)
1. Produce an executive summary for each of GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36 with a table of file, estimated score and uniqueness versus the other listed sites.
2. Goal: a unique, validated GeoTIFF for DrivenData competition 306 (DOE GEMS), downloadable in one click from the site's top section. Values in [0, 1]; CRS EPSG:32611; shape and geotransform matching the submission format. Each submission needs a unique name and a short comment.
3. Beat the high scores: 0.2778 (GEMSDOE32) and 0.3195. Leaderboard high cited as 0.4413. These conflict and must be flagged.
4. Validation gates run without human intervention before a file is declared unique or submittable. Inspection goes through the project, not a human.
5. Parallel-run lane rule: rank-correlation with any registry raster above 0.90, or more than 70% of dots within 3 px of one registry raster's dots, means duplicate. Check on the surface before placement and on the final dots.
6. Holdout: hide-and-recover with withheld fault segments and buffer; pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). Label every number HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED (from a submission-page receipt). Projections are never written as scores. A single-feature holdout AUC above 0.90 is leakage until proven otherwise.
7. Budget: stop after 3 experiments or 2 hours. Do not pick submission slots; promotion is a separate step within the weekly cap.
8. Write a run card JSON at the end of each experiment.
9. Generate 3–5 untried geological hypotheses (layers, physical signature, why it catches faults missing from USGS/INGENIOUS, difference from repo work), ranked by expected DTI gain and cost. Validate the top one on the holdout before using any slot. Name a free official source and confirm it is obtainable.
10. Put the full prompt into the README and read it at the start of every session (this file is linked from the README).
11. Create a GitHub Pages site with an executive summary, an obvious download and official links.
12. Make the submission-page error "Predicted values must be in range [0, 1]" go away.
13. Create a PR and merge it to main. List remaining work and limitations.
14. Multi-pass work (implement, review, re-check). Core values: maximise P(Win); own the outcome.
15. Standing: no manual input; official sources with links for manual review; flag irregularities; no hallucinations; verify line by line. Do not use DrivenData authentication (data pages require login).

## Conflicts recorded (not resolved by this file)
- Leaderboard: 0.4413 (current high in the prompt) vs 0.3195 ("highest right now") vs 0.2784 (`GEMSDOE92 lbmc1`, newly reported 2026-10-29 `CLAIM`) vs 0.2778 (`GEMSDOE32` score `CLAIM`). None organizer-confirmed here.
- Format: the problem page says "null or nan" outside bounds; the served zeros-outside variants are the format this repo uses.
- 2026-10-29 update: `gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17-zeros.tif` (`SHA-256 80d66b0590b2…`) passes 11/11 format gates, 36/36 canaries, fold-proper `HOLDOUT-DTI` (`0.117438 > R0 0.097750`), and operational PI-1 uniqueness across all `2,262` fleet SHAs (`surface 0.65405`, `final 0.63890 <= 0.70`), while remaining `DO NOT SUBMIT` (`verdict="negative"`, `submission_eligible=false`) under the unresolved literal dense-witness rule (`17GEMSDOE = 1.000 > 0.70`).

