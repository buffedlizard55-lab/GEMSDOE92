# DRAINAGE-KNICK result and scientific interpretation

## Decision

**OK to download for research: YES. OK to submit to a weekly competition slot: NO.** The newly generated GeoTIFF is byte-unique among the 747 comparable public-registry rasters successfully read (0 exact SHA-256 matches), and passes every automated format/range check, but the mandatory lane rule stops it for two independent reasons: its strict holdout score does not beat the current holdout best, and literal 3-pixel overlap is 1.0 against a dense registry surface.

## Why the reported 0.2778 parent likely worked

The repository's pixel audit establishes that R0 is a regularly thinned subset of a prior fault skeleton and is therefore optimized for the organizer's 300 m distance-weighted matching geometry. That is a strong explanation for the owner-reported `0.2778` **CLAIM**, but it is not an organizer receipt and does not prove blind-fault discovery. Sparse, nearly kernel-spaced dots reduce redundant false-positive mass while retaining coverage near known fault geometry. The current leaderboard values supplied in the brief do not reveal the hidden labels, so no honest analysis can guarantee a score above 0.2778 or 0.4413.

## Experiment

DRAINAGE-KNICK uses only pinned Bands 7, 12, 15, and 19. Multi-scale absolute DEM curvature and local log-slope departure target persistent knickzones; a depth-to-basement gradient targets buried structural steps; shear rate supplies tectonic context. The geometric mean requires all three. Named confounders are resistant stratigraphic contacts, Lake Lahontan shorelines, fan toes, and DEM seams.

The hide-and-recover implementation was corrected relative to the preceding simple builder pattern: each of eight folds reconstructs dot placement from that fold's **visible** faults only, rather than evaluating one deployment raster masked by the full catalogue. This is the protocol-compliant instrument.

* **HOLDOUT-DTI** (`gems57-pooled-hide-v2`, 22,663 withheld positives, 1,000 spatial-block bootstrap draws): `0.061728 [0.047046, 0.075316]`.
* **HOLDOUT-DTI** paired difference from R0: `+0.057721 [0.043257, 0.071207]`.
* **HOLDOUT-DTI** repository best used as promotion bar: `0.113316` (COULOMB-LOQO; same evaluator family). The new method is below it.
* Leakage canaries: maximum symmetric AUC `0.597114`, below the `0.90` stop.
* Local registry: 106 rasters; worst overlap `0.477320`, worst absolute Spearman `0.063413`.
* Public default-branch scan: 747 comparable rasters successfully read; 0 exact SHA matches; worst absolute Spearman `0.055417`; literal overlap `1.0` against a full-footprint 17GEMSDOE raster. The scan had 705 download failures and is explicitly not exhaustive.

The result is scientifically useful but negative. Terrain knickzones recover hidden catalogue segments much better than R0 in holdout, yet are substantially weaker than the existing LOQO classifier. No weekly submission slot was used.

## Sources and audit boundaries

* Competition/reference implementation: https://github.com/drivendataorg/gems-prize-reference-solution
* Official USGS GeoDAWN catalogue landing page: https://data.usgs.gov/datacatalog/data/USGS:657e1d85d34e23d3533209f7
* Official USGS 3DEP program: https://www.usgs.gov/3d-elevation-program
* Grid CRS reference: https://epsg.io/32611

External non-GitHub pages were not reachable under this sandbox's network allowlist; their content is therefore not claimed as live-verified in this run. Competition raster bytes were restored from commit-pinned owner mirrors and SHA-256 checked, which verifies byte identity but not organizer authentication or redistribution permission.

```json
{
  "hypothesis": "Persistent terrain knickzone x basement-depth edge x shear identifies scarpless/alluvium-covered faults",
  "mechanism": "Geometric mean of multiscale DEM curvature/slope break, basement gradient, and shear percentile",
  "named_non_fault_process": "Resistant stratigraphic contacts, Lake Lahontan shorelines, fan toes, DEM seams",
  "holdout_dti": {"evaluator_version": "gems57-pooled-hide-v2", "withheld_positives": 22663, "value": 0.061728, "ci95": [0.047046, 0.075316]},
  "correlation_overlap_vs_registry": {"local_worst_abs_spearman": 0.063413, "local_worst_overlap": 0.477320, "public_worst_abs_spearman": 0.055417, "public_literal_overlap": 1.0, "exact_sha_matches": 0},
  "raster_sha256": "ef6c27e34fe0f28c6e52615a9fc9601c20ada5337203def25ab8753392aef910",
  "validator_output": {"no_nan_inside_footprint": true, "values_in_0_1": true, "crs_shape_transform_match": true},
  "submission_name": "GEMSDOE92-DRAINAGE_KNICK-20261025",
  "note": "DRAINAGE_KNICK terrain+basement+shear; 37654 dots; HOLDOUT-DTI 0.061728; negative",
  "verdict": "negative"
}
```
