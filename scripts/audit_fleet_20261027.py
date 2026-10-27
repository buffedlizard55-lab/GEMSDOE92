#!/usr/bin/env python3
"""Audit the 2026-10-27 prompt delta: dual witnesses, new Focus-9/fleet runs, and 12 multi-owner repos.

Reuses shared ``vendor/gems57/evaluate_holdout.py``, ``vendor/gems57/uniqueness.py``,
and ``gems/gates.py`` (Protocol Rule 2). Stages downloaded blobs exclusively inside
gitignored ``.cache/fleet_20261027/`` with strict Git blob SHA-1 verification.
Never contacts drivendata.org or dropbox.com, and never overwrites historical receipts.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import gates as gates_mod  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod, metric as metric_mod  # noqa: E402
from vendor.gems57 import uniqueness as U  # noqa: E402

CACHE = ROOT / ".cache" / "fleet_20261027"
INPUTS = ROOT / ".cache" / "gems_inputs"

WITNESS_SPECS: tuple[dict, ...] = (
    {
        "id": "dense_continuous_17gemsdoe",
        "owner": "buffedlizard55-lab",
        "repo": "17GEMSDOE",
        "commit": "6fc71d19d49dca4960d5434bd81b6dd06fcc030a",
        "path": "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
        "git_sha1": "374c88b1da2b803e2ed160de467fd71ae114010d",
        "expected_sha256": "ab0a0a62eecf066a82713b09dd49f0f638a91fa3dd81f54cc34ae89afa3872be",
        "class": "continuous_probability_surface",
    },
    {
        "id": "binary_lattice_13gemsdoe",
        "owner": "buffedlizard55-lab",
        "repo": "13GEMSDOE",
        "commit": "main",
        "path": "docs/downloads/13gems_20261001_r13-lattice-s5_v2_zerofill.tif",
        "git_sha1": "5c1a159439735522659ee78969df3f34efddcdde",
        "expected_sha256": "c12533bb980234c3a706af641d4f1d514bbbe482714b2ebcac3b10f3e72a7a3f",
        "class": "binary_dot_lattice_s5_claim_0_0904",
    },
)

PROMPT_DELTA_ARTIFACTS: tuple[dict, ...] = (
    {
        "key": "GEMSDOE24__gvc1_abe8e51c",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE24",
        "path": "docs/downloads/gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif",
        "git_sha1": "ef573a5513e9afd12fd00598e355bd936f235663",
        "claim_score": 0.0859,
        "delta_kind": "hash_updated_in_20261027_brief",
    },
    {
        "key": "GEMSDOE25__h66_da617550",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE25",
        "path": "docs/downloads/gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif",
        "git_sha1": "581702650a3377adf0745c8d1a63afda0ec1dde8",
        "claim_score": 0.0742,
        "delta_kind": "hash_updated_in_20261027_brief",
    },
    {
        "key": "GEMSDOE27__h31_drcg_wl_celf28",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE27",
        "path": "docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        "git_sha1": None,
        "claim_score": 0.2250,
        "delta_kind": "new_scored_claim_in_20261027_brief",
    },
    {
        "key": "GEMSDOE28__s18_mxtp_3e95505c",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE28",
        "path": "docs/downloads/gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif",
        "git_sha1": "7edeb9c044a23655675512e07f7b59f537fb4246",
        "claim_score": 0.0217,
        "delta_kind": "hash_updated_in_20261027_brief",
    },
    {
        "key": "GEMSDOE28__s21_puhgb_16bbf281",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE28",
        "path": "docs/downloads/gems28-s21-puhgb-20261026-16bbf281ba9b-allfinite.tif",
        "git_sha1": None,
        "claim_score": 0.0206,
        "delta_kind": "new_scored_claim_in_20261027_brief",
    },
    {
        "key": "GEMSDOE33__s33_seisdil_3463540a",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE33",
        "path": "docs/downloads/gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.tif",
        "git_sha1": None,
        "claim_score": 0.0963,
        "delta_kind": "new_scored_claim_in_20261027_brief",
    },
    {
        "key": "GEMSDOE36__kpl36_exp3_fc869911",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE36",
        "path": "docs/downloads/gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros.tif",
        "git_sha1": None,
        "claim_score": 0.1647,
        "delta_kind": "new_scored_claim_in_20261027_brief",
    },
    {
        "key": "GEMSDOE88__bpwd88_b8543782",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE88",
        "path": "docs/downloads/gems88-bpwd88-baranov-worm-conduit-37654-20261025-b8543782-zeros-DO-NOT-SUBMIT.tif",
        "git_sha1": None,
        "claim_score": None,
        "delta_kind": "new_unscored_entry_in_20261027_brief",
    },
    {
        "key": "GEMSDOE91__S18_curvtilt_29db2405",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE91",
        "path": "docs/downloads/gems91-S18-UNIQUE-curvtilt-20000dots-20261025T182858Z-29db2405.tif",
        "git_sha1": None,
        "claim_score": None,
        "delta_kind": "new_unscored_entry_in_20261027_brief",
    },
    {
        "key": "GEMSDOE91__s22_omtj_a99b8923f0",
        "owner": "buffedlizard55-lab",
        "site": "GEMSDOE91",
        "path": "docs/downloads/gems91-s22-omtj-e1-20261026-a99b8923f0-zeros.tif",
        "git_sha1": "a8aed5553b1793ec4bd300b051113a7bea547c0e",
        "claim_score": 0.0298,
        "delta_kind": "new_scored_claim_in_20261027_brief",
    },
    {
        "key": "KANLERGEMSDOE2__htcads_11a2f251",
        "owner": "kanlerxz87-cyber",
        "site": "KANLERGEMSDOE2",
        "path": "docs/downloads/kanlergems2-htcads-exp-2-37654dots-20261026T235227Z-11a2f251-zeros.tif",
        "git_sha1": None,
        "claim_score": None,
        "delta_kind": "new_multi_owner_entry_in_20261027_brief",
    },
)

MULTI_OWNER_REPOS: tuple[tuple[str, str], ...] = (
    ("kanlerxz87-cyber", "KANLERGEMSDOE1"),
    ("kanlerxz87-cyber", "KANLERGEMSDOE2"),
    ("kanlerxz87-cyber", "KANLERGEMSDOE3"),
    ("eugboogieman123-ops", "EUGGEMSDOE1"),
    ("eugboogieman123-ops", "EUGGEMSDOE2"),
    ("eugboogieman123-ops", "EUGGEMSDOE3"),
    ("wingbangboozle1-lang", "WBGGEMSDOE1"),
    ("wingbangboozle1-lang", "WBGGEMSDOE2"),
    ("wingbangboozle1-lang", "WBGGEMSDOE3"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE1"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE2"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE3"),
)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def gh_json(endpoint: str) -> dict | list:
    raw = subprocess.check_output(["gh", "api", endpoint], timeout=120)
    return json.loads(raw)


def fetch_verified_blob(owner: str, repo: str, path: str, expected_sha1: str | None = None) -> tuple[Path, str, str, int]:
    CACHE.mkdir(parents=True, exist_ok=True)
    if expected_sha1 is None:
        meta = gh_json(f"repos/{owner}/{repo}/contents/{path}")
        assert isinstance(meta, dict)
        expected_sha1 = str(meta["sha"])
    target = CACHE / f"{expected_sha1}.tif"
    if target.is_file():
        data = target.read_bytes()
        if git_blob_sha1(data) == expected_sha1:
            return target, expected_sha1, hashlib.sha256(data).hexdigest(), len(data)
    blob = gh_json(f"repos/{owner}/{repo}/git/blobs/{expected_sha1}")
    assert isinstance(blob, dict)
    if blob.get("encoding") == "base64" and blob.get("content"):
        data = base64.b64decode(blob["content"])
    else:
        data = subprocess.check_output(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw", f"repos/{owner}/{repo}/git/blobs/{expected_sha1}"],
            timeout=120,
        )
    actual_sha1 = git_blob_sha1(data)
    if actual_sha1 != expected_sha1:
        raise ValueError(f"Git blob SHA-1 mismatch for {owner}/{repo}/{path}: {actual_sha1} != {expected_sha1}")
    target.write_bytes(data)
    return target, actual_sha1, hashlib.sha256(data).hexdigest(), len(data)


def pigeonhole_lower_bound(n_candidate_dots: int, halo_free_footprint_pixels: int) -> float:
    if n_candidate_dots <= 0:
        return 0.0
    forced_hits = max(0, int(n_candidate_dots) - int(halo_free_footprint_pixels))
    return forced_hits / float(n_candidate_dots)


def run_audit() -> dict:
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    n_foot = int(foot.sum())
    d_cat = distance_transform_edt(~cat)

    sample_path = INPUTS / "bridge" / "sample_submission.tif"
    with rasterio.open(sample_path) as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    # 1. Dual-Witness Pre-Placement Certificate
    witness_results: list[dict] = []
    witness_halos: dict[str, np.ndarray] = {}
    for w in WITNESS_SPECS:
        p, sha1, sha256, nbytes = fetch_verified_blob(w["owner"], w["repo"], w["path"], w["git_sha1"])
        if w["expected_sha256"] and sha256 != w["expected_sha256"]:
            raise ValueError(f"Witness SHA-256 mismatch for {w['id']}: {sha256}")
        with rasterio.open(p) as ds:
            if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                raise ValueError(f"Witness grid mismatch: {w['id']}")
            arr = ds.read(1)
        pos = foot & np.isfinite(arr) & (arr > 0)
        n_pos = int(pos.sum())
        uvals = np.unique(arr[pos])
        halo3 = foot & U._near(pos, 3.0)
        witness_halos[w["id"]] = halo3
        n_halo = int(halo3.sum())
        n_free = n_foot - n_halo
        witness_results.append({
            "id": w["id"],
            "class": w["class"],
            "owner": w["owner"],
            "repo": w["repo"],
            "path": w["path"],
            "git_blob_sha1": sha1,
            "sha256": sha256,
            "bytes": nbytes,
            "footprint_pixels": n_foot,
            "positive_in_footprint": n_pos,
            "positive_fraction_of_footprint": round(n_pos / n_foot, 6),
            "distinct_positive_values": int(uvals.size),
            "is_binary_0_1": bool(uvals.size == 1 and float(uvals[0]) == 1.0),
            "halo_3px_in_footprint": n_halo,
            "halo_3px_fraction_of_footprint": round(n_halo / n_foot, 6),
            "halo_free_footprint_pixels": n_free,
            "pigeonhole_min_overlap_at_1_dot": round(pigeonhole_lower_bound(1, n_free), 6),
            "pigeonhole_min_overlap_at_37654_dots": round(pigeonhole_lower_bound(37654, n_free), 6),
            "min_dots_forcing_gt_70pct_overlap": 1 if n_free == 0 else int(np.floor(n_free / 0.30) + 1),
        })

    # Reference baselines
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = foot & (np.nan_to_num(ds.read(1), nan=0.0) > 0)
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = foot & (np.nan_to_num(ds.read(1), nan=0.0) > 0)
    with rasterio.open(INPUTS / "lineage" / "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif") as ds:
        d28 = foot & (np.nan_to_num(ds.read(1), nan=0.0) > 0)
    with rasterio.open(ROOT / "docs/downloads/gemsdoe92-vario-full-37654-20261025-3c30a41c-zeros.tif") as ds:
        vario = foot & (np.nan_to_num(ds.read(1), nan=0.0) > 0)
    r0_near3 = U._near(r0, 3.0)
    d28_near3 = U._near(d28, 3.0)
    h19_near3 = U._near(h19, 3.0)
    vario_near3 = U._near(vario, 3.0)

    folds = []
    for seed in (20, 30):
        draw, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)

    with rasterio.open(INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_gt3 = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))

    # 2. Audit 11 prompt delta artifacts
    terms_by_key: dict[str, np.ndarray] = {}
    for fold in folds:
        _, tm_r0 = evaluate_holdout.evaluate(r0.astype(np.float32), fold, foot)
        terms_by_key["CONTROL__R0"] = tm_r0 if "CONTROL__R0" not in terms_by_key else terms_by_key["CONTROL__R0"] + tm_r0

    delta_rows: list[dict] = []
    for item in PROMPT_DELTA_ARTIFACTS:
        p, sha1, sha256, nbytes = fetch_verified_blob(item["owner"], item["site"], item["path"], item["git_sha1"])
        gate_results = gates_mod.run_gates(p, sample_path, require_submission_encoding=True)
        gates_ok = all(g.ok for g in gate_results)
        failed_gates = [g.name for g in gate_results if not g.ok]
        with rasterio.open(p) as ds:
            grid_ok = ds.count == 1 and (ds.shape, ds.crs, ds.transform) == expected_grid
            raw = ds.read(1).astype(np.float32)
        fin = np.isfinite(raw)
        arr = np.where(foot & fin, np.clip(raw, 0.0, 1.0), 0.0).astype(np.float32)
        pos = arr > 0
        n_pos = int(pos.sum())
        is_bin = bool(np.array_equal(arr, pos.astype(np.float32)))

        for fold in folds:
            _, tm = evaluate_holdout.evaluate(arr, fold, foot)
            terms_by_key[item["key"]] = tm if item["key"] not in terms_by_key else terms_by_key[item["key"]] + tm

        sgmc3 = float(
            metric_mod.dti_binary(pos, sgmc_gt3, valid=foot, known=cat)["dti"]
            if is_bin
            else metric_mod.dti_exact(arr, sgmc_gt3, valid=foot, known=cat)["dti"]
        )
        delta_rows.append({
            "key": item["key"],
            "owner": item["owner"],
            "site": item["site"],
            "path": item["path"],
            "delta_kind": item["delta_kind"],
            "git_blob_sha1": sha1,
            "sha256": sha256,
            "bytes": nbytes,
            "grid_matches_sample": grid_ok,
            "strict_submission_encoding_gates_pass": gates_ok,
            "failed_gates": failed_gates,
            "positive_in_footprint": n_pos,
            "binary_0_1": is_bin,
            "frac_dcat_le_2px": round(float((d_cat[pos] <= 2.0).mean()), 6) if n_pos else 0.0,
            "reported_claim_score": item["claim_score"],
            "evidence_label": (
                f"CLAIM {item['claim_score']:.4f} (owner-reported in 2026-10-27 brief; no organizer receipt)"
                if item["claim_score"] is not None
                else "UNSCORED in 2026-10-27 brief (no organizer receipt)"
            ),
            "organizer_confirmed_score": None,
            "ov3_vs_r0": round(float(r0_near3[pos].mean()), 6) if n_pos else 0.0,
            "ov3_vs_d28": round(float(d28_near3[pos].mean()), 6) if n_pos else 0.0,
            "ov3_vs_h19_5": round(float(h19_near3[pos].mean()), 6) if n_pos else 0.0,
            "ov3_vs_vario": round(float(vario_near3[pos].mean()), 6) if n_pos else 0.0,
            "ov3_vs_13gemsdoe_r13_lattice": round(float(witness_halos["binary_lattice_13gemsdoe"][pos].mean()), 6) if n_pos else 0.0,
            "ov3_vs_17gemsdoe_dense": round(float(witness_halos["dense_continuous_17gemsdoe"][pos].mean()), 6) if n_pos else 0.0,
            "sgmc_proxy_dti_gt3px": round(sgmc3, 6),
            "eligible_to_submit": False,
        })

    pooled = evaluate_holdout.pooled_summary(
        terms_by_key, draws=1000, seed=520810, candidate="CONTROL__R0"
    )
    for row in delta_rows:
        s = pooled["scores"][row["key"]]
        row["holdout_dti_static_diagnostic"] = {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": int(s["withheld_positive_pixels"]),
            "dti": round(float(s["dti"]), 6),
            "ci95": [round(float(s["ci95"][0]), 6), round(float(s["ci95"][1]), 6)],
            "caveat": "Static diagnostic re-score of pre-built raster on buffered whole-segment holdout; NOT a prospective fold-rebuilt training measurement and NOT a leaderboard score projection.",
        }

    # 3. Audit all 12 newly listed multi-owner repositories
    multi_owner_inventory: list[dict] = []
    for owner, repo in MULTI_OWNER_REPOS:
        repo_meta = gh_json(f"repos/{owner}/{repo}")
        assert isinstance(repo_meta, dict)
        branch = str(repo_meta.get("default_branch") or "main")
        tree_doc = gh_json(f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
        assert isinstance(tree_doc, dict)
        blobs = [n for n in tree_doc.get("tree", []) if n.get("type") == "blob"]
        tifs = [n["path"] for n in blobs if n.get("path", "").lower().endswith((".tif", ".tiff"))]
        multi_owner_inventory.append({
            "owner": owner,
            "repo": repo,
            "default_branch": branch,
            "pushed_at": repo_meta.get("pushed_at"),
            "truncated": bool(tree_doc.get("truncated", False)),
            "total_blobs": len(blobs),
            "tiff_blob_count": len(tifs),
            "stub_readme_only": bool(len(blobs) <= 1 and len(tifs) == 0),
            "sample_tiffs": tifs[:8],
        })

    return {
        "schema": "gemsdoe92-fleet-delta-audit-20261027-v1",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "arena/d30d387c-gemsdoe92",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "evaluator_hashes": evaluate_holdout.implementation_hashes(),
        "sample_submission_sha256": hashlib.sha256(sample_path.read_bytes()).hexdigest(),
        "dual_witness_preplacement_certificate": {
            "universal_literal_stop": True,
            "binary_dot_lattice_stop_at_37654_budget": True,
            "witnesses": witness_results,
            "implication": (
                "Even if unthresholded continuous probability surfaces (17GEMSDOE E-proba-multiscale, "
                "100.0% footprint > 0) were exempted by a future policy update, pure binary {0,1} "
                "registry submission 13GEMSDOE r13-lattice-s5 (206,895 dots, CLAIM 0.0904) tiles "
                "99.8713% of the footprint within 3 px (pigeonhole minimum 82.3418% > 70% at 37,654 dots). "
                "Policy resolution must explicitly address both continuous probability surfaces and "
                "uniform calibration lattices."
            ),
        },
        "prompt_20261027_delta_artifacts": delta_rows,
        "multi_owner_repositories_20261027": multi_owner_inventory,
        "submission_eligible": False,
        "new_unique_tiff_generated": False,
        "weekly_slots_used": 0,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True,
                    help="New evidence JSON path; existing receipts are never overwritten")
    ap.add_argument("--public-mirror", type=Path, default=None,
                    help="Optional byte-exact mirror under docs/downloads/")
    args = ap.parse_args(argv)
    if args.output.exists() or (args.public_mirror is not None and args.public_mirror.exists()):
        print("STOP: output path already exists; refusing to overwrite prior evidence", file=sys.stderr)
        return 2
    doc = run_audit()
    text = json.dumps(doc, indent=2, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    if args.public_mirror is not None:
        args.public_mirror.parent.mkdir(parents=True, exist_ok=True)
        args.public_mirror.write_text(text, encoding="utf-8")
    print(f"WROTE {args.output} ({len(text)} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
