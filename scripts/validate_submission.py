import rasterio, numpy as np, pathlib, sys
sample_path = pathlib.Path("data/bridge/sample_submission.tif")
labels_path = pathlib.Path("data/bridge/labels.tif")

with rasterio.open(sample_path) as ds:
    sample_profile = ds.profile
    sample_data = ds.read(1)
    footprint = np.isfinite(sample_data)
    transform = ds.transform
    crs = ds.crs
    shape = (ds.height, ds.width)

with rasterio.open(labels_path) as ds:
    labels = ds.read(1) > 0.5

def check_file(path):
    path = pathlib.Path(path)
    print(f"\nChecking {path}")
    with rasterio.open(path) as ds:
        data = ds.read(1)
        # CRS
        assert ds.crs == crs, f"CRS mismatch {ds.crs} vs {crs}"
        # shape
        assert ds.height == shape[0] and ds.width == shape[1], f"shape mismatch"
        # transform
        assert ds.transform == transform, f"transform mismatch"
        # dtype
        assert ds.dtypes[0] == 'float32', f"dtype {ds.dtypes[0]}"
        # band count
        assert ds.count == 1, f"band count {ds.count}"
        # values in [0,1]
        finite = np.isfinite(data)
        # For NaN-outside version, outside footprint may be NaN, inside must be finite and in [0,1]
        # For zeros-outside, all finite
        # Check inside footprint values in [0,1]
        inside = footprint
        # inside should be finite (per spec no NaN inside footprint)
        if not np.all(np.isfinite(data[inside])):
            # allow if file is zeros version? spec says no NaN inside footprint for NaN version
            # For NaN version, inside must be finite
            print(f"  FAIL: NaN inside footprint")
            return False
        if not np.all((data[inside] >= 0) & (data[inside] <= 1)):
            print(f"  FAIL: values outside [0,1] inside footprint")
            return False
        # catalogue zero mass
        if np.any(data[labels] > 0):
            print(f"  FAIL: non-zero mass on catalogue: {data[labels].sum()} pixels")
            return False
        # For NaN version, outside should be NaN, for zeros version, outside 0
        outside = ~footprint
        # We don't enforce strict, but report
        n_outside_finite = np.isfinite(data[outside]).sum()
        n_outside_nan = np.isnan(data[outside]).sum()
        print(f"  OK: shape {data.shape}, finite inside {finite[inside].sum()}/{inside.sum()}, outside finite {n_outside_finite}, outside NaN {n_outside_nan}, n_dots {(data>0.5).sum()}")
        return True

# Check all releases
releases = list(pathlib.Path("releases").glob("*.tif"))
ok = True
for p in releases:
    if not check_file(p):
        ok=False

if ok:
    print("\nAll format checks PASS")
else:
    print("\nSome checks FAILED")
    sys.exit(1)
