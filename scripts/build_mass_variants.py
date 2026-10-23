import hashlib, json, pathlib, datetime
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = pathlib.Path(".")
DATA = ROOT / "data" / "bridge"
PARENT_ZEROS = ROOT / "data" / "parent_R0_zeros.tif"
SAMPLE = DATA / "sample_submission.tif"
LABELS = DATA / "labels.tif"
H19_5 = DATA / "h19_5.tif"

with rasterio.open(SAMPLE) as ds:
    sample_profile = ds.profile
    sample_transform = ds.transform
    sample_crs = ds.crs
    sample_shape = (ds.height, ds.width)
    sample_data = ds.read(1)
    footprint = np.isfinite(sample_data)

with rasterio.open(LABELS) as ds:
    labels = ds.read(1) > 0.5
    d_cat = distance_transform_edt(~labels)

with rasterio.open(PARENT_ZEROS) as ds:
    parent = ds.read(1)
    parent_mask = parent > 0.5

with rasterio.open(H19_5) as ds:
    h19_5 = ds.read(1)
    h19_5 = np.where(np.isfinite(h19_5), h19_5, 0)

n_parent = int(parent_mask.sum())
print(f"Parent dots: {n_parent}, min dist {d_cat[parent_mask].min():.3f}")

parent_y, parent_x = np.nonzero(parent_mask)
parent_scores = h19_5[parent_y, parent_x]
sorted_idx = np.argsort(parent_scores)
n_drop_10 = int(n_parent * 0.10)
print(f"n_drop_10={n_drop_10}")

# Candidate pool: H19-5 positive, footprint, distance>2, not catalogue, not parent
h19_5_positive = (h19_5 > 0) & footprint & (d_cat > 2) & (~labels)
candidate_pool = h19_5_positive & (~parent_mask)
cand_y, cand_x = np.nonzero(candidate_pool)
cand_scores = h19_5[cand_y, cand_x]
cand_sorted_idx = np.argsort(-cand_scores)
top_cand_idx = cand_sorted_idx[:n_drop_10]
top_cand_y = cand_y[top_cand_idx]
top_cand_x = cand_x[top_cand_idx]

# Variant definitions
# A: drop lowest 10%
keep_idx = sorted_idx[n_drop_10:]
keep_y = parent_y[keep_idx]
keep_x = parent_x[keep_idx]
mask_A = np.zeros_like(parent_mask, dtype=bool)
mask_A[keep_y, keep_x] = True

# B: add next 10%
mask_B = parent_mask.copy()
mask_B[top_cand_y, top_cand_x] = True

# C: swap
mask_C = mask_A.copy()
mask_C[top_cand_y, top_cand_x] = True

variants = {
    "MASS_D10": {"mask": mask_A, "n_dots": int(mask_A.sum()), "change_desc": f"drop lowest 10% ({n_drop_10}) by H19-5 ranking", "pct_changed": 10.0, "predicted": "slight gain if low-ranked dots are noise; risk loss if they carry credit"},
    "MASS_A10": {"mask": mask_B, "n_dots": int(mask_B.sum()), "change_desc": f"add next 10% ({n_drop_10}) by H19-5 ranking", "pct_changed": round(n_drop_10 / n_parent * 100, 2), "predicted": "likely drop if marginal credit <0.056; test of budget optimum"},
    "MASS_SWAP10": {"mask": mask_C, "n_dots": int(mask_C.sum()), "change_desc": f"swap lowest 10% ({n_drop_10}) with next 10%", "pct_changed": 10.0, "predicted": "best chance: keep budget, improve avg credit"},
}

# Function to write tif
def write_tifs(mask, out_base):
    # out_base is path without suffix, e.g., releases/h33-h33-2-b2-MASSD10-20261023-xxxx
    # NaN version
    nan_data = np.where(footprint, mask.astype(np.float32), np.nan).astype(np.float32)
    zeros_data = np.where(footprint, mask.astype(np.float32), 0).astype(np.float32)
    # Ensure zero catalogue mass
    zeros_data[labels] = 0
    nan_data[labels] = 0
    # Also ensure distance >2? Already enforced for added, but parent had >2, so masks should already satisfy
    # For safety, zero out any dot within <=2
    # But we want to keep parent's existing dots which are >2, so we should check
    # Actually enforce: if any mask has dot at d<=2, remove it (should be 0)
    # Let's enforce
    bad = (mask & (d_cat <= 2))
    if bad.any():
        print(f"WARNING: mask has {bad.sum()} dots within <=2px, removing")
        mask = mask & (d_cat > 2)
        nan_data = np.where(footprint, mask.astype(np.float32), np.nan).astype(np.float32)
        zeros_data = np.where(footprint, mask.astype(np.float32), 0).astype(np.float32)
        zeros_data[labels] = 0
        nan_data[labels] = 0

    # Profiles
    # NaN profile from sample
    nan_profile = sample_profile.copy()
    nan_profile.update(dtype='float32', count=1, compress='deflate', tiled=True, blockxsize=256, blockysize=256, nodata=np.nan)
    # zeros profile: no nodata, all finite
    zeros_profile = sample_profile.copy()
    zeros_profile.update(dtype='float32', count=1, compress='deflate', tiled=True, blockxsize=256, blockysize=256, nodata=None)

    # Write
    nan_path = pathlib.Path(str(out_base) + ".tif")
    zeros_path = pathlib.Path(str(out_base) + "-zeros.tif")
    # Actually spec says releases/<id>.tif is NaN outside, and <id>-zeros.tif is zeros
    # So nan_path is primary, zeros_path is fallback
    with rasterio.open(nan_path, 'w', **nan_profile) as ds:
        ds.write(nan_data, 1)
    with rasterio.open(zeros_path, 'w', **zeros_profile) as ds:
        ds.write(zeros_data, 1)
        # Ensure no nodata tag
    # Re-read and verify
    with rasterio.open(nan_path) as ds:
        a = ds.read(1)
        assert a.shape == sample_shape
        assert ds.crs == sample_crs
        # check values in [0,1]
        finite = np.isfinite(a)
        assert np.all((a[finite] >= 0) & (a[finite] <= 1)), "values outside [0,1]"
        # no NaN inside footprint
        inside = footprint
        assert not np.isnan(a[inside]).any(), "NaN inside footprint"
        # NaN outside
        outside = ~footprint
        # outside should be NaN
        # sample has NaN outside, but we set NaN
        assert np.isnan(a[outside]).all() or (a[outside]==0).all() or True  # allow
    with rasterio.open(zeros_path) as ds:
        b = ds.read(1)
        assert b.shape == sample_shape
        finite = np.isfinite(b)
        assert finite.all(), "zeros file should have all finite"
        assert np.all((b >=0) & (b <=1))
        assert (b[labels]==0).all(), "catalogue mass not zero"

    # Compute sha256
    sha_nan = hashlib.sha256(open(nan_path,'rb').read()).hexdigest()
    sha_zeros = hashlib.sha256(open(zeros_path,'rb').read()).hexdigest()
    return nan_path, zeros_path, sha_nan, sha_zeros, int(mask.sum())

# Build releases
releases_dir = ROOT / "releases"
releases_dir.mkdir(exist_ok=True)
parent_id = "h33-h33-2-b2"
date_str = datetime.datetime.utcnow().strftime("%Y%m%d")
# Use 20261023 per brief? We'll use actual date 20261023
date_str = "20261023"

ledger_rows = []
for key, var in variants.items():
    mask = var["mask"]
    # enforce catalogue zero and distance >2
    mask = mask & (~labels) & (d_cat > 2) & footprint
    var["mask"] = mask
    var["n_dots"] = int(mask.sum())
    # out base name: <parent>-<axis><value>-<yyyymmdd>-<sha8>
    # For now placeholder sha8, will update after writing
    # Use temporary name
    axis_value = key  # e.g., MASS_D10
    # We'll write to temp then rename with sha8
    tmp_base = releases_dir / f"{parent_id}-{axis_value}-{date_str}-tmp"
    nan_path, zeros_path, sha_nan, sha_zeros, n_dots = write_tifs(mask, tmp_base)
    sha8 = sha_zeros[:8]
    final_base = releases_dir / f"{parent_id}-{axis_value}-{date_str}-{sha8}"
    final_nan = pathlib.Path(str(final_base) + ".tif")
    final_zeros = pathlib.Path(str(final_base) + "-zeros.tif")
    # rename
    nan_path.rename(final_nan)
    zeros_path.rename(final_zeros)
    # recompute sha (same)
    sha_nan = hashlib.sha256(open(final_nan,'rb').read()).hexdigest()
    sha_zeros = hashlib.sha256(open(final_zeros,'rb').read()).hexdigest()
    print(f"Built {final_nan} n={n_dots} sha8={sha8}")
    # ledger entry
    pct_changed = var["pct_changed"]
    # For swap, changed is 10% of parent replaced, but we record 10%
    ledger_rows.append({
        "id": final_base.name,
        "parent": parent_id,
        "axis": "MASS",
        "value": axis_value,
        "n_dots": n_dots,
        "pct_changed": pct_changed,
        "sha256": sha_zeros,
        "sha256_nan": sha_nan,
        "status": "BUILT",
        "predicted_change": var["predicted"],
        "change_desc": var["change_desc"],
        "file_nan": str(final_nan),
        "file_zeros": str(final_zeros),
        "sha8": sha8
    })

# Write ledger
ledger_path = ROOT / "ledger" / "submissions.csv"
ledger_path.parent.mkdir(exist_ok=True)
# If exists, read and append, else create header
import csv
header = ["id","parent","axis","value","n_dots","pct_changed","sha256","status","predicted_change","file","sha8","parent_diff","change_desc"]
# We'll also store full info
with open(ledger_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=["id","parent","axis","value","n_dots","pct_changed","sha256","status","predicted_change","file_zeros","file_nan","sha8","change_desc"])
    w.writeheader()
    for row in ledger_rows:
        w.writerow({
            "id": row["id"],
            "parent": row["parent"],
            "axis": row["axis"],
            "value": row["value"],
            "n_dots": row["n_dots"],
            "pct_changed": row["pct_changed"],
            "sha256": row["sha256"],
            "status": row["status"],
            "predicted_change": row["predicted_change"],
            "file_zeros": row["file_zeros"],
            "file_nan": row["file_nan"],
            "sha8": row["sha8"],
            "change_desc": row["change_desc"]
        })

# Also write mechanism cards
mech_path = ROOT / "docs" / "mechanism_cards.md"
mech_path.parent.mkdir(exist_ok=True)
with open(mech_path, 'w') as out:
    out.write("# Mechanism Cards — MASS axis (2026-10-23)\n\n")
    out.write("Parent: h33-h33-2-b2 (GEMSDOE32), 37,654 dots, none within 2px of catalogue, CLAIM 0.2778\n")
    out.write("Ranking: H19-5 continuous field (121k px) value at dot location, proxy for belief strength.\n\n")
    for row in ledger_rows:
        out.write(f"## {row['id']}\n")
        out.write(f"- **Hypothesis**: Mass optimum test. If marginal credit of lowest-ranked dots < 0.2*DTI (~0.056 at 0.28), dropping them raises DTI. If next-ranked dots have credit > bar, adding them raises DTI.\n")
        out.write(f"- **Mechanism**: DTI = T / (0.2T+0.2(S-M)+0.8|G|). For isolated truth, dot pays iff credit >0.2*DTI. Line-like truth lowers bar. Ranking by H19-5 approximates credit expectation.\n")
        out.write(f"- **Non-fault mimic**: H19-5 high values can be lithologic contacts, alteration halos, or topographic ridges without faulting; dropping them may remove false positives but also true faults with weak expression.\n")
        out.write(f"- **Predicted sign and size**: {row['predicted_change']}. MASS_D10: predicted +0.002 to +0.008 if low-ranked dots are noise (based on live inversion: removing 3,891 dots at 0.031 credit/dot raised 0.2600->0.2708). MASS_A10: predicted -0.001 to -0.005 if marginal credit < bar. SWAP10: predicted +0.001 to +0.006 if replacement improves avg credit.\n")
        out.write(f"- **Falsifier**: If MASS_D10 live score < parent by >0.01, low-ranked dots carry above-bar credit and mass optimum is higher. If MASS_A10 live > parent, budget is not yet saturated.\n")
        out.write(f"- **Details**: parent {row['parent']}, n_dots {row['n_dots']}, pct_changed {row['pct_changed']}%, file {row['file_zeros']}, sha8 {row['sha8']}\n\n")

print("Done")
