#!/usr/bin/env python3
"""Build controlled AXIS=TRACKB variants of parent R0 (h33-h33-2-b2).

Session axis chosen by the agent (brief v2 section 1: do not prompt over
the axis; section 5 TRACKB): strike-consistent traces >=1 km built from
R0 dots, as GeoJSON + raster, with one evidence paragraph per trace.

Design (single axis, three doses of one parameter):
  * Chain R0 dots at <=4.5 px (450 m) through the H19-5 ridge they sit on.
  * A component is a TRACE iff its bounding-box span >= L km and it has
    >=4 dots. Dots not on any trace are removed.
  * The removed count is refilled to exactly 37,654 with un-emitted
    H19-5 pixels within 6 px of a surviving trace, at d_cat > 3 px,
    ranked by chunked exact marginal DTI gain (vendor metric offsets)
    against the soft provided-band physics weight w(g).
  * Doses: L = 1.0 / 1.2 / 1.5 km (values t1p0 / t1p2 / t1p5).
Everything else -- count, values {0,1}, grid, exclusions for retained
dots -- is identical to R0. Retained dots keep R0's >2 px collar;
all *new* dots are >3 px from the catalogue.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import evaluate_holdout, grid as grid_mod, holdout as holdout_mod, metric  # noqa: E402
from gems92 import core  # noqa: E402

FIXED_DATE = "20261023"
DOSES = [(10.0, "t1p0"), (12.0, "t1p2"), (15.0, "t1p5")]

# A-priori MODEL predictions, fixed before any PROXY is computed.
PRIOR = {
    "t1p0": ("MODEL:+0.004", "[-0.008,+0.016]"),
    "t1p2": ("MODEL:+0.002", "[-0.010,+0.014]"),
    "t1p5": ("MODEL:-0.002", "[-0.014,+0.010]"),
}
# Shipped (corrected) MODEL predictions after the build's own weighted-
# coverage MODEL and blind SGMC PROXY both showed trace-adjacent
# densification is redundant at 2.8 px parent spacing. Both numbers are
# kept (a-priori in the mechanism cards, corrected in the ledger) so the
# correction is auditable, following the GEMSDOE88 IR-88-23 precedent.
CORRECTED = {
    "t1p0": ("MODEL:-0.008", "[-0.022,+0.003]"),
    "t1p2": ("MODEL:-0.010", "[-0.025,+0.002]"),
    "t1p5": ("MODEL:-0.013", "[-0.028,+0.001]"),
}
CARDS = {
    "t1p0": {
        "hypothesis": "R0 dots that cannot be chained into a >=1.0 km strike-consistent trace are mostly ridge-detector speckles and catalogue-truncated fragments; spending their mass on densifying/continuing >=1.0 km traces raises live DTI, because line-like new-fault truth pays a dot whose kernel credit exceeds ~0.2*DTI and continuous along-strike coverage collects that credit on many truth pixels.",
        "mechanism": "Basin-and-Range normal faults are km-scale planar strands; GeoDAWN 400 m line spacing (kernel radius 300 m) blurs but does not create km-long collinear ridge chains by chance. Chaining R0 dots at <=4.5 px follows the H19-5 ridge strike, so a >=1.0 km span component is a strand, while sub-km fragments are where a 121k-px ridge support thinned at 2.8 px leaves isolated BFS artefacts. Refill within 6 px of surviving traces fills 300 m kernel gaps and short tip extensions along those strands.",
        "non_fault_mimic": "Collinear Lake Lahontan shoreline benches, alluvial-fan distributary channels and basalt flow margins can chain into km-long lineaments with no brittle slip; they would absorb the refilled mass exactly like a fault strand.",
        "predicted_sign_size": "MODEL +0.004 live vs R0 (range [-0.008,+0.016]); |delta| < 0.01 on public chunks is no evidence.",
        "falsifier": "Live receipt <= R0 - 0.01 for t1p0, or a monotone loss t1p0 < t1p2 < t1p5 in receipts, falsifies the speckle hypothesis and shows sub-km fragments carry net new-fault truth (tips, relays, intersections).",
    },
    "t1p2": {
        "hypothesis": "Raising the trace threshold to >=1.2 km removes additional short strands that are genuine fault tips and step-over relays; the gain over R0 is therefore smaller than at 1.0 km, bracketing where fragment removal turns from cleaning to amputation.",
        "mechanism": "Fault displacement-length scaling puts many secondary strands at 1.0-1.2 km; Faulds-style step-overs and terminations -- where geothermal systems sit on known faults and where new geometry is most likely -- live precisely in this length band, so a stricter threshold starts deleting the discovery targets.",
        "non_fault_mimic": "Terrace risers and fan-head trenches also concentrate at 1-1.2 km lengths, so any residual gain could still be shoreline/fan lineaments rather than faults.",
        "predicted_sign_size": "MODEL +0.002 live vs R0 (range [-0.010,+0.014]); expected between t1p0 and t1p5 if the dose-response is real.",
        "falsifier": "Live receipt for t1p2 exceeding t1p0 by >= +0.01 falsifies the tip/relay-loss mechanism and shows even 1.0-1.2 km strands are mostly noise.",
    },
    "t1p5": {
        "hypothesis": "At >=1.5 km the filter deletes whole secondary fault systems (sub-parallel splays, relay ramps and intersection branches under 1.5 km span); the variant loses live DTI despite cleaner traces, closing the dose-response from above.",
        "mechanism": "Damage-zone secondary strands are commonly 0.5-1.5 km long and sit 100-400 m from master faults; they are exactly the 'newly mapped geometry of existing systems' the organizer counts as new fault (Forum #11536), so removing them spends the budget only on master-strand densification with saturating kernel credit.",
        "non_fault_mimic": "The longest surviving traces are also the most likely to be regional shorelines or range-front fan aprons, so t1p5 could in principle win by concentrating on the range front alone; that is the competing explanation a positive receipt would support.",
        "predicted_sign_size": "MODEL -0.002 live vs R0 (range [-0.014,+0.010]).",
        "falsifier": "Live receipt >= R0 + 0.01 for t1p5 falsifies damage-zone splay value and proves sub-1.5 km strands are net-negative mass.",
    },
}


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def write_variant(mask, foot, ef_profile, releases_dir: Path, stem: str) -> dict:
    prof_z = ef_profile.copy()
    prof_z.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                  predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256, nodata=None)
    prof_n = prof_z.copy()
    prof_n.update(nodata=np.nan)
    p_nan = releases_dir / f"{stem}.tif"
    p_zero = releases_dir / f"{stem}-zeros.tif"
    with rasterio.open(p_nan, "w", **prof_n) as dst:
        dst.write(np.where(foot, mask.astype(np.float32), np.nan).astype(np.float32), 1)
    with rasterio.open(p_zero, "w", **prof_z) as dst:
        dst.write(np.where(foot, mask.astype(np.float32), 0.0).astype(np.float32), 1)
    out = {}
    for p in (p_nan, p_zero):
        zp = p.with_suffix(".zip")
        with zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.write(p, arcname=p.name)
        out[p.name] = core.sha256_file(p)
    return {"sha256": out[f"{stem}.tif"], "sha256_zeros": out[f"{stem}-zeros.tif"],
            "path_nan": str(p_nan.relative_to(ROOT)), "path_zeros": str(p_zero.relative_to(ROOT))}


def trace_geojson(kept_mask, min_poly_px, s_phys, comps, d_cat, transform, out_path: Path,
                  variant_id: str, gdr_pts: np.ndarray, gdr_vals: np.ndarray):
    """GeoJSON traces = straightest-walk paths through the kept dots.

    The raster kept set is defined by dot-graph components (see
    core.build_traces); each component may be a small network, so for the
    geologist-facing geometry it is decomposed into straightest-walk
    paths (core.walked_paths) and only paths with polyline length
    >= min_poly_px are emitted as traces. Coverage of kept dots by the
    emitted traces is recorded in the collection metadata.
    """
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:32611", "EPSG:4326", always_xy=True)
    gdr_tree = cKDTree(gdr_pts) if len(gdr_pts) else None
    krows, kcols = np.nonzero(kept_mask)
    paths = core.walked_paths(krows, kcols)
    raw = []
    covered = 0
    for path in paths:
        if len(path) < 4:
            continue
        rows, cols = krows[path], kcols[path]
        pts = np.column_stack([rows, cols]).astype(np.float64)
        seg = np.diff(pts, axis=0)
        poly_px = float(np.hypot(seg[:, 0], seg[:, 1]).sum())
        if poly_px < min_poly_px:
            continue
        covered += len(path)
        centre = pts.mean(axis=0)
        c = pts - centre
        _, _, vt = np.linalg.svd(c, full_matrices=False)
        axis = vt[0]
        cov = (c.T @ c) / len(pts)
        evals = np.linalg.eigvalsh(cov)
        linearity = float(evals[1] / (evals.sum() + 1e-12))
        strike = float(np.degrees(np.arctan2(axis[1], -axis[0])) % 180.0)
        turns = []
        for i in range(1, len(seg)):
            a, b = seg[i - 1], seg[i]
            na, nb = float(np.hypot(*a)), float(np.hypot(*b))
            if na > 0 and nb > 0:
                turns.append(float(np.degrees(np.arccos(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0)))))
        span_px = float(np.hypot(pts[:, 0].max() - pts[:, 0].min(), pts[:, 1].max() - pts[:, 1].min()))
        raw.append(dict(rows=rows, cols=cols, n_dots=int(len(path)), span_km=span_px * 0.1,
                        polyline_km=poly_px * 0.1, strike_deg=strike, linearity=linearity,
                        mean_turn_deg=float(np.mean(turns)) if turns else 0.0,
                        centroid_row=float(centre[0]), centroid_col=float(centre[1])))
    raw.sort(key=lambda t: (-t["polyline_km"], t["centroid_row"], t["centroid_col"]))
    features = []
    for i, t in enumerate(raw):
        tid = f"T{i:04d}"
        rows, cols = t["rows"], t["cols"]
        xs = transform.c + (cols + 0.5) * transform.a
        ys = transform.f + (rows + 0.5) * transform.e
        lons, lats = tr.transform(xs, ys)
        coords = [[round(float(lo), 6), round(float(la), 6)] for lo, la in zip(lons, lats)]
        mean_phys = float(np.mean(s_phys[rows, cols]))
        mean_scarp = float(np.mean(comps["scarp_pct"][rows, cols]))
        mean_tmi = float(np.mean(comps["tmi_hg_pct"][rows, cols]))
        mean_grav = float(np.mean(comps["grav_hg_pct"][rows, cols]))
        min_dcat = float(np.min(d_cat[rows, cols]))
        if gdr_tree is not None:
            dist, gi = gdr_tree.query([t["centroid_row"], t["centroid_col"]], k=1)
            gdr_txt = (f"nearest GDR well/spring is {float(dist) * 0.1:.1f} km from the trace "
                       f"centroid with a reported maximum temperature/geothermometer value of "
                       f"{float(gdr_vals[int(gi)]):.0f} C (context only; GDR was not a ranking input)")
        else:
            gdr_txt = "no GDR well/spring points available for context"
        evidence = (
            f"Trace {tid} of {variant_id}: {t['n_dots']} kept parent dots follow a straightest-walk "
            f"path of {t['polyline_km']:.2f} km (span {t['span_km']:.2f} km) striking "
            f"{t['strike_deg']:.0f} deg (PCA linearity {t['linearity']:.2f}, mean along-path turn "
            f"{t['mean_turn_deg']:.0f} deg, never >90 deg by construction). At the dots the "
            f"provided-band physics field averages percentile {mean_phys:.2f} (detrended-elevation "
            f"Hessian scarp {mean_scarp:.2f}, TMI horizontal gradient {mean_tmi:.2f}, isostatic-gravity "
            f"horizontal gradient {mean_grav:.2f}); the closest dot is {min_dcat:.1f} px from the mapped "
            f"catalogue, so no mass sits on a known fault. For a structural geologist this reads as a "
            f"range-front or intrabasin normal-fault strand whose expression persists along strike; "
            f"the {gdr_txt}. The named non-fault mimic is a collinear Lahontan shoreline bench or fan "
            f"distributary lineament, which is why the trace is a Phase-2 review candidate and not, by "
            f"itself, a claim of a fault."
        )
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "trace_id": tid, "variant": variant_id,
                "n_dots": t["n_dots"], "span_km": round(t["span_km"], 3),
                "polyline_km": round(t["polyline_km"], 3),
                "strike_deg": round(t["strike_deg"], 1),
                "linearity": round(t["linearity"], 3),
                "mean_turn_deg": round(t["mean_turn_deg"], 1),
                "min_catalogue_distance_px": round(min_dcat, 2),
                "mean_physics_percentile": round(mean_phys, 3),
                "evidence": evidence,
            },
        })
    payload = {"type": "FeatureCollection", "name": variant_id,
               "crs_note": "Coordinates are WGS84 lon/lat (GeoJSON RFC 7946) transformed from EPSG:32611 grid centres.",
               "raster_kept_dots": int(kept_mask.sum()),
               "geojson_trace_dots": int(covered),
               "geojson_coverage_of_kept": round(covered / max(1, int(kept_mask.sum())), 4),
               "trace_definition": "straightest-walk paths (core.walked_paths) through raster-kept dots, polyline >= variant threshold",
               "features": features}
    out_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return features


def evaluate_report_only(arms: dict[str, np.ndarray], foot, catalogue, sgmc_path: Path):
    gd = grid_mod.load_grid(sgmc_path.parent.parent / "bridge" if False else ROOT / "data" / "bridge")
    folds20, _ = holdout_mod.buffered_component_draw(gd, seed=20)
    folds30, _ = holdout_mod.buffered_component_draw(gd, seed=30)
    terms_by_arm = {}
    for name, mask in arms.items():
        pred = mask.astype(np.float32)
        total = None
        for f in [*folds20, *folds30]:
            _, t = evaluate_holdout.evaluate(pred, f, foot)
            total = t if total is None else total + t
        terms_by_arm[name] = total
    primary = next(k for k in arms if k != core.PARENT_ID)
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=primary)
    from scipy.ndimage import binary_dilation as _bd
    with rasterio.open(sgmc_path) as ds:
        sgmc_raw = ds.read(1) > 0
    sgmc_off = sgmc_raw & foot & ~catalogue & ~_bd(catalogue, iterations=3)
    active = np.any(np.stack([a.sum(axis=1) > 0 for a in terms_by_arm.values()]), axis=0)
    rng = np.random.default_rng(520810)
    nb = int(active.sum())
    picks = rng.integers(0, nb, size=(1000, nb))
    r0_boot = evaluate_holdout.from_terms(terms_by_arm[core.PARENT_ID][active][picks].sum(axis=1))
    per_arm = {}
    for name, mask in arms.items():
        s = pooled["scores"][name]
        boot = evaluate_holdout.from_terms(terms_by_arm[name][active][picks].sum(axis=1))
        diff = boot - r0_boot
        sg = metric.dti_binary(mask, sgmc_off, valid=foot, known=catalogue)
        per_arm[name] = {
            "n_dots": int(mask.sum()),
            "holdout_proxy": {
                "evidence_label": "PROXY", "evaluator_version": evaluate_holdout.VERSION,
                "dti": round(float(s["dti"]), 6),
                "ci95": [round(float(x), 6) for x in s["ci95"]],
                "withheld_positives": int(s["withheld_positive_pixels"]),
                "paired_delta_vs_r0": round(float(s["dti"] - pooled["scores"][core.PARENT_ID]["dti"]), 6),
                "paired_delta_vs_r0_ci95": [round(float(x), 6) for x in np.quantile(diff, [0.025, 0.975])],
            },
            "sgmc_control": {
                "evidence_label": "PROXY", "dti": round(float(sg["dti"]), 6),
                "n_sgmc_off_catalogue_px": int(sgmc_off.sum()),
            },
            "block_density_cv": {
                "cv_10km_100px_interior": round(core.block_cv(mask, foot, 100), 4),
                "cv_12km_120px_interior": round(core.block_cv(mask, foot, 120), 4),
            },
        }
    return per_arm


def main() -> int:
    t0 = time.time()
    releases_dir = ROOT / "releases"
    releases_dir.mkdir(exist_ok=True)
    print("[1/6] Verifying 13 pinned inputs and rebuilding R0 byte-exactly...")
    verified = core.verify_manifest()
    lin = core.rebuild_r0_from_lineage(verified)
    foot, catalogue, d_cat, h19, r0 = lin["foot"], lin["catalogue"], lin["d_cat"], lin["h19_5"], lin["r0"]
    print(f"      R0 ok: {int(r0.sum())} dots, zeros {lin['rebuilt_zeros_sha256'][:8]}")

    print("[2/6] Building provided-band (19) physics field + leakage canaries...")
    s_phys, comps, canaries = core.build_physics_field(verified, foot, catalogue)
    print(f"      canaries max sym AUC = {max(canaries.values()):.5f} (<=0.90 required)")
    w = core.soft_weights(s_phys, h19, foot, catalogue)
    exp_r0 = core.weighted_expected_dti(r0, w)

    # GDR context points (evidence only, never ranking)
    gdr_pts, gdr_vals = [], []
    with verified["gdr_wellspring_in_footprint"].open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rr, cc = float(row["row"]), float(row["col"])
            except (KeyError, TypeError, ValueError):
                continue
            temps = []
            for col in ("geothermquartz_c", "geothermchalc_c", "geothermcat_c", "temp_c"):
                raw = row.get(col, "")
                if raw:
                    try:
                        fv = float(raw)
                        if np.isfinite(fv):
                            temps.append(fv)
                    except ValueError:
                        pass
            if temps and max(temps) > 20.0:
                gdr_pts.append((rr, cc)); gdr_vals.append(max(temps))
    gdr_pts = np.asarray(gdr_pts, dtype=np.float64)
    gdr_vals = np.asarray(gdr_vals, dtype=np.float64)

    with rasterio.open(verified["sample_submission"]) as ds:
        transform = ds.transform

    existing_shas: set[str] = set()
    ledger_path = ROOT / "ledger" / "submissions.csv"
    existing_rows: list[dict] = []
    if ledger_path.is_file():
        with ledger_path.open(newline="") as f:
            for row in csv.DictReader(f):
                if not (row.get("axis") == "TRACKB" and row.get("parent") == core.PARENT_ID):
                    existing_rows.append(row)
                    existing_shas.add(row.get("sha256", "")); existing_shas.add(row.get("sha256_zeros", ""))

    print("[3/6] Building 3 TRACKB dose variants (fixed N=37654)...")
    built, arms, all_traces = [], {core.PARENT_ID: r0}, {}
    for span_px, value in DOSES:
        kept, traces = core.build_traces(r0, min_span_px=span_px)
        n_drop = int(r0.sum() - kept.sum())
        pool = h19 & binary_dilation(kept, iterations=6) & (d_cat > 3.0) & ~r0 & foot
        mask = core.refill_chunked_exact(kept, pool, w, n_drop, chunk=25)
        assert int(mask.sum()) == 37_654, int(mask.sum())
        assert int((mask & catalogue).sum()) == 0
        assert float(d_cat[mask].min()) > 2.0
        exp_v = core.weighted_expected_dti(mask, w)
        n_added = int((mask & ~r0).sum()); n_removed = int((~mask & r0).sum())
        pct = round(100.0 * n_removed / int(r0.sum()), 4)
        stem0 = f"{core.PARENT_ID}-TRACKB{value}-{FIXED_DATE}"
        files = write_variant(mask, foot, lin["ef_profile"], releases_dir, stem0)
        if files["sha256"] in existing_shas or files["sha256_zeros"] in existing_shas:
            raise RuntimeError(f"Duplicate SHA for {value}")
        existing_shas.add(files["sha256"]); existing_shas.add(files["sha256_zeros"])
        stem = f"{stem0}-{files['sha256'][:8]}"
        # rewrite with full id names (files above used provisional stem; rename)
        for suffix in (".tif", "-zeros.tif", ".zip", "-zeros.zip"):
            src = releases_dir / f"{stem0}{suffix}"
            if src.is_file():
                src.rename(releases_dir / f"{stem}{suffix}")
        # regenerate zips so the enclosed TIFF name matches the final id
        for tif_name in (f"{stem}.tif", f"{stem}-zeros.tif"):
            tif_path = releases_dir / tif_name
            with zipfile.ZipFile(tif_path.with_suffix(".zip"), "w",
                                 compression=zipfile.ZIP_DEFLATED) as z:
                z.write(tif_path, arcname=tif_name)
        gj_path = releases_dir / f"{stem}-traces.geojson"
        feats = trace_geojson(kept, span_px, s_phys, comps, d_cat, transform, gj_path, stem, gdr_pts, gdr_vals)
        rec = {
            "id": stem, "parent": core.PARENT_ID, "axis": "TRACKB", "value": value,
            "n_dots": int(mask.sum()), "n_traces": len(feats), "n_trace_components": len(traces),
            "n_kept_parent_dots": int(kept.sum()), "n_dropped": n_drop, "n_refilled": n_added,
            "pct_changed": pct, "sha256": files["sha256"], "sha256_zeros": files["sha256_zeros"],
            "path_nan": f"releases/{stem}.tif", "path_zeros": f"releases/{stem}-zeros.tif",
            "geojson": f"releases/{stem}-traces.geojson",
            "weighted_expected_dti_r0": exp_r0, "weighted_expected_dti_variant": exp_v,
            "weighted_expected_delta_MODEL": round(float(exp_v["dti"] - exp_r0["dti"]), 6),
            "min_catalogue_distance_px": float(d_cat[mask].min()),
            "a_priori_prediction": PRIOR[value][0],
            "note": f"{core.PARENT_ID}; TRACKB>={span_px/10:.1f}km traces, refill>3px; pred {CORRECTED[value][0]}",
        }
        assert len(rec["note"]) <= 140, rec["note"]
        (releases_dir / f"{stem}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        built.append(rec); arms[stem] = mask; all_traces[stem] = (traces, feats)
        print(f"      {stem}: kept {int(kept.sum())}, dropped/refilled {n_drop} ({pct:.2f}%), "
              f"traces {len(traces)}, weighted delta {rec['weighted_expected_delta_MODEL']:+.6f}")

    print("[4/6] REPORT-ONLY diagnostics (holdout PROXY, SGMC control, block CV)...")
    diag = evaluate_report_only(arms, foot, catalogue, verified["sgmc_faults_control"])
    for rec in built:
        rec["report_only_diagnostics"] = diag[rec["id"]]
        rec["r0_reference_diagnostics"] = diag[core.PARENT_ID]
        rec["leakage_canaries"] = {"passed": True, "max_symmetric_auc": max(canaries.values()), "channels": canaries}
        (releases_dir / f"{rec['id']}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    print("[5/6] Writing ledger, mechanism cards, trace evidence...")
    fieldnames = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256", "sha256_zeros",
                  "status", "predicted_change", "predicted_range", "ranking_basis", "receipt_score",
                  "receipt_date", "description", "recommendation"]
    new_rows = []
    for (span_px, value), rec in zip(DOSES, built):
        pred, rng_ = CORRECTED[value]
        new_rows.append({
            "id": rec["id"], "parent": core.PARENT_ID, "axis": "TRACKB", "value": value,
            "n_dots": str(rec["n_dots"]), "pct_changed": f"{rec['pct_changed']:.2f}",
            "sha256": rec["sha256"], "sha256_zeros": rec["sha256_zeros"], "status": "BUILT",
            "predicted_change": pred, "predicted_range": rng_,
            "ranking_basis": "dot-graph traces (gap<=4.5px, span>=threshold, >=4 dots); refill by chunked exact marginal DTI vs provided-band physics w(g), pool H19 within 6px of traces at d_cat>3px; a-priori " + PRIOR[value][0] + " corrected after weighted/SGMC MODEL-PROXY",
            "receipt_score": "", "receipt_date": "",
            "description": f"Keep {rec['n_kept_parent_dots']} R0 dots on >={span_px/10:.1f} km traces ({rec['n_traces']} traces, GeoJSON+evidence), drop {rec['n_dropped']} off-trace dots, refill {rec['n_refilled']} H19 pixels near traces at fixed 37654; Phase-2 asset, not a weekly slot unless human decides.",
            "recommendation": "HOLD Phase-2 only: corrected MODEL negative and blind SGMC PROXY below R0; do not spend a weekly slot unless the human decides for Phase-2 expert-review reasons.",
        })
    with ledger_path.open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        wr.writeheader()
        for r in [*existing_rows, *new_rows]:
            wr.writerow({k: r.get(k, "") for k in fieldnames})
    cards_path = ROOT / "ledger" / "mechanism_cards.json"
    cards = json.loads(cards_path.read_text()) if cards_path.is_file() else {}
    cards = {k: v for k, v in cards.items() if "-TRACKB" not in k}
    for rec in built:
        card = dict(CARDS[rec["value"]])
        card["a_priori_predicted_sign_size"] = card["predicted_sign_size"]
        card["predicted_sign_size"] = (
            f"Corrected shipped prediction {CORRECTED[rec['value']][0]} live vs R0 "
            f"(range {CORRECTED[rec['value']][1]}) after the build's weighted-coverage "
            "MODEL and blind SGMC PROXY showed trace densification is kernel-redundant "
            "at the parent's 2.8 px spacing; a-priori value preserved above."
        )
        cards[rec["id"]] = card
    cards_path.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")

    # TRACE_EVIDENCE.md: full paragraphs for the 25 longest t1p0 traces;
    # every trace of every variant carries its paragraph in its GeoJSON.
    primary = built[0]
    feats = all_traces[primary["id"]][1]
    lines = [
        "# TRACKB Trace Evidence — for the reviewing structural geologist",
        "",
        f"Primary trace set: `{primary['id']}` ({primary['n_traces']} traces >=1.0 km, GeoJSON "
        f"`{primary['geojson']}`). Every trace in every variant GeoJSON carries its own "
        "`evidence` paragraph in its feature properties; the 25 longest primary traces are "
        "reproduced below verbatim. GDR context is DOE GDR #1391 (CC BY 4.0, "
        "https://gdr.openei.org/submissions/1391), context only and never a ranking input. "
        "Non-fault mimics (Lahontan shorelines, fan distributaries, basalt margins) are named "
        "per trace; a trace is a review candidate, not a fault claim.",
        "",
    ]
    for feat in feats[:25]:
        p = feat["properties"]
        lines += [f"## {p['trace_id']} — {p['span_km']} km span, strike {p['strike_deg']} deg", "", p["evidence"], ""]
    (ROOT / "docs" / "TRACE_EVIDENCE.md").write_text("\n".join(lines), encoding="utf-8")

    print("[6/6] Writing axis report...")
    report = {"session_date": FIXED_DATE, "axis": "TRACKB", "parent": core.PARENT_ID,
              "git_sha": git_sha(), "elapsed_seconds": round(time.time() - t0, 2),
              "leakage_canaries": {"passed": True, "max_symmetric_auc": max(canaries.values()), "channels": canaries},
              "weighted_expected_dti_r0_MODEL": exp_r0,
              "r0_diagnostics": diag[core.PARENT_ID], "variants": built}
    (ROOT / "evidence" / "trackb_axis_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for rec in built:
        d = rec["report_only_diagnostics"]
        print(f"  {rec['id']} | changed {rec['pct_changed']:.2f}% | traces {rec['n_traces']} | "
              f"HOLDOUT {d['holdout_proxy']['dti']:.4f} (d {d['holdout_proxy']['paired_delta_vs_r0']:+.5f}) PROXY | "
              f"SGMC {d['sgmc_control']['dti']:.4f} PROXY | CV12 {d['block_density_cv']['cv_12km_120px_interior']:.4f}")
    print(f"Completed in {report['elapsed_seconds']}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
