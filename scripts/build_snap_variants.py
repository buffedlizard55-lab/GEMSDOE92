#!/usr/bin/env python3
"""Build three SNAP variants of R0 (h33-h33-2-b2): evidence-thresholded
position correction onto the strongest edge/scarp response.

One axis, one parameter. The parent is the pinned R0 raster (both encodings
SHA-256 verified). Each variant differs from R0 ONLY in the position of a
subset of its dots: a dot moves <= 2 px onto the strongest edge response in
its window, and only when that response beats its own by more than a threshold
g. The threshold is the dose knob:

    g = 0.15  ->  ~7% of dots move   (only dots clearly off the ridge)
    g = 0.10  ->  ~19%
    g = 0.05  ->  ~52%

Invariants held for every variant: dot count 37,654 exactly, unit mass
(mass per position unchanged), every moved dot inside the footprint, off the
catalogue and > 3.0 px from it, no shared pixels, and the parent's 2.83 px
minimum-spacing invariant preserved (no two dots closer than 2.828 px).

Inputs are ONLY the SHA-256-pinned files in registry/session_manifest.json.
The response surface comes from scripts/make_edge_response.py (bands 3, 13, 19
of the pinned 19-band stack; see that script for the band rationale). No
labels, no leaderboard, no submission. Candidate TIFFs go to releases/, which
is gitignored, so they are not redistributed by this public repository.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import gates as gem_gates                      # noqa: E402
from gems.variants import Dots, snap                      # noqa: E402
from gems57 import metric as vendor_metric                # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA = {
    "nan": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
    "zeros": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
}
MANIFEST = ROOT / "registry" / "session_manifest.json"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "snap_session.json"
CARDS = ROOT / "docs" / "mechanism_cards.md"
DATE = "20261023"
N_PARENT = 37654
MIN_SPACING = 2.828       # parent invariant (D2.8 thinning)
MAX_SHIFT = 2.0           # brief's SNAP bound
TARGET_MIN_CATALOGUE = 3.0  # every MOVED dot must clear the catalogue by this
# Dose ladder: threshold on the response improvement required to move a dot.
DOSES = (0.15, 0.10, 0.05)
# MODEL prediction inputs (see mechanism card for the derivation):
#   denominator D calibrated from the lineage's own measured slope
#   (2,545 dots removed in the SOLO->R0 stage bought +0.0070 live,
#    i.e. 2.8e-6 per zero-credit dot = 0.0556/D  ->  D ~ 19,900)
DEN_CALIBRATED = 19900.0
DTI_REF = 0.2778          # CLAIM, not a receipt
PREDICTED = {             # MODEL: ± range, sign not asserted below 0.01
    0.15: ("MODEL:±0.008", "[-0.008,+0.008]"),
    0.10: ("MODEL:±0.015", "[-0.015,+0.015]"),
    0.05: ("MODEL:±0.035", "[-0.035,+0.035]"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs() -> dict[str, Path]:
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out: dict[str, Path] = {}
    for entry in doc["files"]:
        path = ROOT / entry["local_path"]
        if not path.is_file():
            raise SystemExit(f"pinned input {entry['id']} missing: {path} "
                             f"(run scripts/restore_inputs.py)")
        got = sha256_file(path)
        if got != entry["sha256"] or path.stat().st_size != int(entry["bytes"]):
            raise SystemExit(f"pinned input {entry['id']} FAILED sha256/size: {got}")
        out[entry["id"]] = path
        print(f"PIN OK  {entry['id']:<24s} {entry['sha256'][:12]}")
    return out


def load_inputs(inputs: dict[str, Path]):
    with rasterio.open(inputs["sample_submission"]) as ds:
        foot = np.isfinite(ds.read(1))
        profile = ds.profile.copy()
        reference_path = inputs["sample_submission"]
    with rasterio.open(inputs["existing_faults"]) as ds:
        cat = (ds.read(1) > 0) & foot
    with rasterio.open(inputs["parent_r0_nan"]) as ds:
        r0_nan = np.isfinite(ds.read(1)) & (ds.read(1) > 0)
    with rasterio.open(inputs["parent_r0_nan"]) as ds:
        r0_nan = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(inputs["parent_r0_zeros"]) as ds:
        r0_zeros = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    if not np.array_equal(r0_nan, r0_zeros):
        raise SystemExit("the two pinned R0 encodings do not carry the same dots")
    if sha256_file(inputs["parent_r0_nan"]) != PARENT_SHA["nan"] or \
            sha256_file(inputs["parent_r0_zeros"]) != PARENT_SHA["zeros"]:
        raise SystemExit("parent sha256 mismatch")
    d_cat = distance_transform_edt(~cat)
    return foot, cat, d_cat, r0_nan, profile, reference_path


def write_tif(path: Path, profile: dict, foot: np.ndarray, mask: np.ndarray,
              nan_outside: bool) -> None:
    p = profile.copy()
    p.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
             predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256,
             nodata=np.nan if nan_outside else None)
    fill = np.float32(np.nan) if nan_outside else np.float32(0.0)
    arr = np.where(foot, mask.astype(np.float32), fill).astype(np.float32)
    with rasterio.open(path, "w", **p) as ds:
        ds.write(arr, 1)


def move_geometry(new_y, new_x, old_y, old_x):
    """Split displacements into along-strike and across-strike with respect to
    the local chain direction, which is estimated from the two nearest parent
    neighbours (a fault trace is a 1-D chain of dots, so the neighbour-to-
    neighbour vector is the chain direction)."""
    moved = (new_y != old_y) | (new_x != old_x)
    if not moved.any():
        return {"n_moved": 0}, np.zeros(0)
    tree = cKDTree(np.c_[old_y, old_x])
    _, idx = tree.query(np.c_[old_y, old_x], k=3)
    ny, nx = new_y[moved].astype(float), new_x[moved].astype(float)
    oy, ox = old_y[moved].astype(float), old_x[moved].astype(float)
    p1, p2 = idx[moved, 1], idx[moved, 2]
    ty = (old_y[p1] - old_y[p2]).astype(float)
    tx = (old_x[p1] - old_x[p2]).astype(float)
    tn = np.hypot(ty, tx)
    tn[tn == 0] = 1.0
    ty, tx = ty / tn, tx / tn
    dy, dx = ny - oy, nx - ox
    dn = np.hypot(dy, dx)
    dn[dn == 0] = 1.0
    cos = np.abs((dy * ty + dx * tx) / dn)
    along = cos > 0.7071
    disp = np.hypot(new_y - old_y, new_x - old_x)
    return {
        "n_moved": int(moved.sum()),
        "frac_along_strike_moves": float(along.mean()),
        "frac_across_strike_moves": float(1.0 - along.mean()),
        "mean_displacement_px": float(disp.mean()),
        "mean_displacement_movers_px": float(disp[moved].mean()),
        "median_displacement_movers_px": float(np.median(disp[moved])),
        "p90_displacement_movers_px": float(np.percentile(disp[moved], 90)),
        "mean_dx_all": float((new_x - old_x).mean()),
        "mean_dy_all": float((new_y - old_y).mean()),
    }, disp


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, r0, profile, reference = load_inputs(inputs)
    ys, xs = np.nonzero(r0)
    if len(ys) != N_PARENT:
        raise SystemExit(f"parent dot count {len(ys)} != {N_PARENT}")
    if np.any(cat[ys, xs]) or np.any(d_cat[ys, xs] <= 2.0):
        raise SystemExit("parent violates its own zero-mass / >2 px invariants")

    resp = np.load(ROOT / ".cache" / "gems_inputs" / "snap_edge_response.npy")
    if resp.shape != foot.shape:
        raise SystemExit("edge response grid does not match the submission grid")

    # A moved dot may not land on the catalogue or within 3 px of it, and may
    # not land outside the dataset footprint.
    keep_out = cat | (d_cat <= TARGET_MIN_CATALOGUE)

    parent = Dots(ys, xs, np.ones(len(ys), dtype=float))
    used_hashes = {PARENT_SHA["nan"], PARENT_SHA["zeros"]}
    ledger_hashes: set[str] = set()
    # An idempotent rebuild of THIS experiment may reuse its own recorded hash.
    own_hash_by_value: dict[str, str] = {}
    if LEDGER.exists():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("axis") == "SNAP" and row.get("parent") == PARENT_ID:
                    own_hash_by_value[row.get("value", "")] = (row.get("sha256") or "").strip()
                    continue
                for col in ("sha256", "sha256_nan", "sha256_zeros"):
                    if row.get(col):
                        ledger_hashes.add(row[col].strip())
        used_hashes |= ledger_hashes

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    # REPORT ONLY: SGMC off-catalogue control and the leakage canary. Neither is
    # a gate; neither is a score.
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_off = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_r0 = vendor_metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)["dti"]
    rng = np.random.default_rng(20261023)
    bg = np.argwhere(foot & np.isfinite(resp))
    bg = bg[rng.choice(len(bg), size=min(300_000, len(bg)), replace=False)]
    cat_pts = np.argwhere(cat)
    from scipy.stats import rankdata
    cat_vals = resp[cat_pts[:, 0], cat_pts[:, 1]]
    bg_vals = resp[bg[:, 0], bg[:, 1]]
    keep = np.isfinite(cat_vals)
    cat_vals, bg_vals = cat_vals[keep], bg_vals[np.isfinite(bg_vals)]
    pooled = np.r_[cat_vals, bg_vals]
    ranks = rankdata(pooled)
    n1 = cat_vals.size
    canary_auc = float((ranks[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * (pooled.size - n1)))
    print(f"PROXY (report only): SGMC off-catalogue dti(R0)={sgmc_r0:.6f}; "
          f"edge-response AUC at catalogue vs background={canary_auc:.3f} "
          f"(leakage-canary stop threshold 0.90)")

    records, cards = [], {}

    for g in DOSES:
        v = snap(parent, resp, max_shift=MAX_SHIFT, footprint=foot, keep_out=keep_out,
                 min_gain=g, min_spacing_px=MIN_SPACING)
        new_y, new_x = v.dots.ys, v.dots.xs
        moved_mask = np.zeros(foot.shape, dtype=bool)
        moved_mask[new_y, new_x] = True

        # ---- hard invariants -------------------------------------------------
        if len(v.dots) != N_PARENT:
            raise SystemExit(f"g={g}: count changed")
        if not np.allclose(v.dots.p, 1.0):
            raise SystemExit(f"g={g}: mass per dot changed")
        if len(set(zip(new_y.tolist(), new_x.tolist()))) != N_PARENT:
            raise SystemExit(f"g={g}: duplicate pixels")
        if not foot[new_y, new_x].all():
            raise SystemExit(f"g={g}: dot outside footprint")
        if cat[new_y, new_x].any():
            raise SystemExit(f"g={g}: dot on catalogue")
        moved = (new_y != ys) | (new_x != xs)
        if moved.any() and d_cat[new_y[moved], new_x[moved]].min() <= TARGET_MIN_CATALOGUE:
            raise SystemExit(f"g={g}: a moved dot landed within {TARGET_MIN_CATALOGUE} px "
                             "of the catalogue")
        nn = cKDTree(np.c_[new_y, new_x]).query(np.c_[new_y, new_x], k=2)[0][:, 1]
        if nn.min() < MIN_SPACING - 1e-6:
            raise SystemExit(f"g={g}: spacing invariant broken ({nn.min():.3f} px)")

        geo, disp = move_geometry(new_y, new_x, ys, xs)
        # every position that did not move must be a byte-identical parent dot
        stayed_y, stayed_x = ys[~moved], xs[~moved]
        if not np.array_equal(new_y[~moved], stayed_y):
            raise SystemExit(f"g={g}: unmoved dots changed position")

        stem = f"{PARENT_ID}-SNAPcap2p0-g{g:.2f}".replace(".", "p")
        tmp_nan = OUT_DIR / f"._building-{g:.2f}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{g:.2f}-zeros.tif"
        write_tif(tmp_nan, profile, foot, moved_mask, nan_outside=True)
        write_tif(tmp_zeros, profile, foot, moved_mask, nan_outside=False)
        sha_nan, sha_zeros = sha256_file(tmp_nan), sha256_file(tmp_zeros)
        own_previous = own_hash_by_value.get(f"cap2p0-g{g:.2f}", "")
        for s in (sha_nan, sha_zeros):
            if s in used_hashes and s != own_previous:
                raise SystemExit(f"g={g}: sha256 already in ledger/parent: {s}")
        used_hashes.update((sha_nan, sha_zeros))

        short_id = f"{stem}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)

        # ---- gates: re-read from disk after writing --------------------------
        results = gem_gates.run_gates(nan_path, reference, catalogue_path=inputs["existing_faults"])
        ok, report = gem_gates.summarise(results)
        failed = [r.name for r in results if not r.ok]
        gate_checks = {r.name: {"ok": bool(r.ok), "detail": r.detail} for r in results}
        if set(failed) - {"distance_from_catalogue"}:
            raise SystemExit(f"g={g}: hard gate failed: {failed}\n{report}")
        dist = next(r for r in results if r.name == "distance_from_catalogue")
        n_within = int(dist.detail.split("dots_within=")[1].split()[0])
        n_parent_within = int((d_cat[ys, xs] <= 3.0).sum())
        # Only *inherited* dots may sit inside the 3 px collar (R0 itself has
        # them; see IRREGULARITIES). No moved dot may be inside it, so the
        # count can only fall or stay equal.
        if n_within > n_parent_within:
            raise SystemExit(f"g={g}: in-collar dots rose {n_parent_within} -> {n_within}")
        if np.any((d_cat[new_y[~moved], new_x[~moved]] <= 3.0) !=
                  (d_cat[ys[~moved], xs[~moved]] <= 3.0)):
            raise SystemExit(f"g={g}: in-collar classification changed for an unmoved dot")
        if np.any(d_cat[new_y[moved], new_x[moved]] <= 3.0):
            raise SystemExit(f"g={g}: a moved dot sits inside the 3 px collar")
        with rasterio.open(nan_path) as ds:
            arr_nan = ds.read(1)
        with rasterio.open(zeros_path) as ds:
            zeros = ds.read(1)
        if not np.array_equal(np.nan_to_num(arr_nan, nan=0.0), zeros):
            raise SystemExit(f"g={g}: the two encodings disagree on dots")
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise SystemExit(f"g={g}: on-disk hash changed after rename")
        zeros_res = gem_gates.run_gates(zeros_path, reference, catalogue_path=inputs["existing_faults"])
        if [r.name for r in zeros_res if not r.ok and r.name != "distance_from_catalogue"]:
            raise SystemExit(f"g={g}: zeros fallback failed a gate")

        pred_text, pred_range = PREDICTED[g]
        n_moved = int(moved.sum())
        pct = 100.0 * n_moved / N_PARENT
        note = (f"{PARENT_ID}; SNAP {n_moved} dots ({pct:.1f}%) <=2px to edge max, "
                f"gain>{g:.2f}; count 37654 held; pred {pred_text}")
        if len(note) > 140:
            raise SystemExit(f"form note too long ({len(note)}): {note}")

        rec = {
            "id": short_id,
            "parent": PARENT_ID,
            "axis": "SNAP",
            "value": f"cap2p0-g{g:.2f}",
            "n_dots": N_PARENT,
            "pct_changed": round(pct, 6),
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "status": "BUILT",
            "predicted_change": pred_text,
            "file_nan": str(nan_path.relative_to(ROOT)),
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (f"move {n_moved} parent dots (<=2px) onto the strongest "
                            f"TMI/gravity/scarp edge response, threshold gain>{g:.2f}; "
                            "count and mass held"),
            "notes": (f"MODEL range {pred_range}; moved dots clear catalogue by "
                      f">{TARGET_MIN_CATALOGUE:g}px; min spacing {MIN_SPACING:g}px held; "
                      "SGMC PROXY delta "
                      f"{vendor_metric.dti_binary(moved_mask, sgmc_off, valid=foot, known=cat)['dti'] - sgmc_r0:+.6f}; "
                      "see evidence/snap_session.json"),
            "parent_diff": {
                "n_moved": n_moved, "n_stayed": N_PARENT - n_moved,
                "moved_pct": round(pct, 6),
                "symmetric_difference_px": 2 * n_moved,
                **{k: round(val, 6) for k, val in geo.items() if k != "n_moved"},
                "min_catalogue_distance_px": float(d_cat[new_y, new_x].min()),
                "moved_min_catalogue_distance_px": float(d_cat[new_y[moved], new_x[moved]].min())
                if moved.any() else None,
                "min_nn_px": float(nn.min()),
            },
            "format_validation": gate_checks,
            "gate_status": ("PASS on every gate except distance_from_catalogue, which "
                            f"reports {n_within} inherited R0 dots inside 3 px "
                            "(declared deviation; zero moved dots inside 3 px)"),
            "sgmc_control_proxy": {
                "evidence_label": "PROXY",
                "dti": round(vendor_metric.dti_binary(moved_mask, sgmc_off,
                                                      valid=foot, known=cat)["dti"], 6),
                "delta_vs_r0": round(vendor_metric.dti_binary(moved_mask, sgmc_off,
                                                             valid=foot, known=cat)["dti"]
                                     - sgmc_r0, 6),
                "n_withheld_control_pixels": int(sgmc_off.sum()),
            },
            "leakage_canary_auc_edge_response_vs_catalogue": round(canary_auc, 4),
            "git_sha_at_build": git_sha,
            "form_note": note,
        }
        cards[short_id] = {
            "parent": PARENT_ID, "axis": "SNAP", "value": f"cap2p0-g{g:.2f}",
            "hypothesis": (
                "Within the 300 m kernel, a dot pays credit only if it lands within ~3 px of a "
                "new-fault pixel. If the parent's lineament positions carry the ~100-300 m "
                "location error expected from 400 m flight-line spacing, then sliding each "
                "poorly-positioned dot onto the local maximum of the TMI/gravity horizontal "
                f"gradient and detrended-elevation slope recover(s) credit that R0 loses to "
                f"position error. Dose g={g:.2f} = only dots whose local edge maximum is at "
                "least that much stronger than their own pixel move."),
            "mechanism": (
                "Potential-field horizontal-gradient maxima and slope maxima are where the "
                "physical property contrast across a fault plane projects to the surface; the "
                "same construction that makes them edge detectors makes their maxima the "
                "best local estimate of the trace position. The DTI denominator is dominated by "
                "uncovered truth (|G|), so a dot 3-4 px off-trace earns nothing while a dot on "
                "the crest earns ~2-3 units of triangular-kernel credit against the same truth."),
            "non_fault_mimic": (
                "Lithologic contacts, intrusive margins, caldera ring fractures, palaeochannels, "
                "erosional scarps and road cuts all produce sharp gradient maxima. A magnetic "
                "gradient maximum also sits over the *edge of the magnetised body*, not over the "
                "fault plane, so the crest can be systematically offset from the trace."),
            "predicted_sign_and_size": (
                f"{pred_text} (MODEL, range {pred_range}). Derivation: one converted dot "
                "(zero credit -> credit c~2.5, best-weight 0.8, newly covering c of |G|) is worth "
                "[(2.5)(1+0.8*0.278) - 0.278(-1.66)]/D ~ 1.5e-4 at D~19,900, a denominator "
                "calibrated from the lineage's own measured 2.8e-6 per zero-credit dot. "
                f"With {n_moved} movers the sign of the live change is therefore decided by "
                "whether the net conversion rate is above or below zero. The quoted range is "
                "about +-2 sigma of a pure-relocation null, sigma(dDTI) ~ 1.22*sigma_c*"
                "sqrt(n_movers)/D with sigma_c ~ 1.5 kernel units per moved dot "
                f"(=> ~{2*1.22*1.5*(n_moved**0.5)/DEN_CALIBRATED:.3f}); the model cannot "
                "resolve a sign below 0.01, so these are two-sided ranges, not gains."),
            "falsifier": (
                "If g=0.05 (52% of dots relocate by ~1 px) lands more than 0.01 BELOW g=0.15 and "
                "R0, the edge maxima are worse position estimators than the parent's own "
                "lineaments and the SNAP hypothesis is rejected for this region. If g=0.15 "
                "gains >0.01 while g=0.05 loses >0.01, only the clearly-mispositioned dots are "
                "correctable and later axes must keep a strict evidence threshold. A monotone "
                "increase with dose supports composing SNAP onto the best PRUNE rung."),
            "decision_rule": "Live change under 0.01 is no evidence. Receipts only; never a PROXY.",
        }
        records.append(rec)
        print(f"BUILT {short_id}: moved {n_moved} ({pct:.2f}%), "
              f"mean disp {geo['mean_displacement_px']:.3f} px, "
              f"along-strike {100*geo['frac_along_strike_moves']:.0f}%, "
              f"resp {v.stats['mean_response_before']:.3f}->{v.stats['mean_response_after']:.3f}")

    # ---- ledger (append, keep the established schema) ------------------------
    default_fields = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                      "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                      "change_desc", "receipt_score", "receipt_date", "notes"]
    existing, fields = [], default_fields
    if LEDGER.exists():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing = list(reader)
            fields = list(reader.fieldnames or default_fields)
    by_value = {rec["value"]: rec for rec in records}
    kept = []
    for row in existing:
        if row.get("axis") == "SNAP" and row.get("parent") == PARENT_ID:
            existing_value = row.get("value", "")
            if existing_value not in by_value:
                raise SystemExit(f"ledger already holds SNAP value {existing_value!r} "
                                 "for this parent; each (parent, axis, value) is built once")
            if row.get("sha256") != by_value[existing_value]["sha256"]:
                raise SystemExit(f"ledger SNAP value {existing_value!r} has a different "
                                 "sha256: the build is not reproducible")
            continue          # idempotent rebuild of this exact experiment
        kept.append(row)
    for rec in records:
        row = {k: "" for k in fields}
        for k in ("id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                  "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                  "change_desc", "notes"):
            row[k] = rec[k]
        row["receipt_score"] = ""      # the human fills this from the submission page
        row["receipt_date"] = ""
        kept.append(row)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(kept)

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha_at_build": git_sha,
        "parent": {"id": PARENT_ID, "n_dots": N_PARENT, "sha256": PARENT_SHA,
                   "score_label": "CLAIM 0.2778 (no receipt)"},
        "edge_response": json.loads((ROOT / ".cache" / "gems_inputs" /
                                     "snap_edge_response.json").read_text())["layer_source"],
        "rule": {"max_shift_px": MAX_SHIFT, "min_gain_doses": list(DOSES),
                 "min_spacing_px": MIN_SPACING,
                 "target_min_catalogue_px": TARGET_MIN_CATALOGUE},
        "variants": records,
        "mechanism_cards": cards,
        "evidence_labels": "predicted_change is MODEL; nothing here is a score",
    }, indent=2) + "\n", encoding="utf-8")

    # ---- mechanism cards (append to the shared file) ------------------------
    text = CARDS.read_text(encoding="utf-8") if CARDS.exists() else "# Mechanism cards\n"
    # idempotent: drop a previous SNAP section before appending this build's
    marker = text.find("# SNAP axis (2026-10-23)")
    if marker >= 0:
        text = text[:marker].rstrip() + "\n"
    text += "\n\n---\n\n# SNAP axis (2026-10-23)\n\n" \
            "Parent R0 `h33-h33-2-b2`, 37,654 unit-mass dots, CLAIM 0.2778. " \
            "Response surface from pinned bands 3/13/19 only; see " \
            "`scripts/make_edge_response.py` and `evidence/snap_session.json`.\n"
    for sid, c in cards.items():
        text += (f"\n## {sid}\n"
                 f"- **Hypothesis.** {c['hypothesis']}\n"
                 f"- **Mechanism.** {c['mechanism']}\n"
                 f"- **Non-fault process that could mimic it.** {c['non_fault_mimic']}\n"
                 f"- **Predicted sign and size.** {c['predicted_sign_and_size']}\n"
                 f"- **Falsifier.** {c['falsifier']}\n"
                 f"- **Decision rule.** {c['decision_rule']}\n")
    CARDS.write_text(text, encoding="utf-8")
    print(f"\nledger rows: {len(kept)}; evidence: {EVIDENCE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
