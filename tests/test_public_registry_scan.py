from scripts.scan_public_gems_tif_registry import is_candidate_like_path


def test_registry_scan_includes_candidate_prediction_paths():
    assert is_candidate_like_path("docs/downloads/model-output.tif")
    assert is_candidate_like_path("releases/candidate.tiff")
    assert is_candidate_like_path("evidence/prediction/raster.tif")


def test_registry_scan_excludes_inputs_and_external_rasters():
    assert not is_candidate_like_path("data/official/sample_submission.tif")
    assert not is_candidate_like_path("inputs/training_features.tif")
    assert not is_candidate_like_path("analysis/data/external/context.tif")
    assert not is_candidate_like_path(".cache/gems_inputs/context.tif")


def test_registry_scan_filter_is_case_insensitive():
    assert is_candidate_like_path("DOCS/DOWNLOADS/Output.TIF")
    assert not is_candidate_like_path("DATA/EXTERNAL/Input.TIF")
