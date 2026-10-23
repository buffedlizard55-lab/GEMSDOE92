#!/usr/bin/env python3
"""Build three controlled SNAP candidates from an exactly rebuilt R0.

Axis values differ only in the label-free edge response used for local snapping:
TMI horizontal gradient, absolute signed gravity horizontal gradient, or an
 equal-weight percentile-rank consensus of those responses and topographic slope.
Every dot moves by at most 2 px; count and unit mass are fixed. Candidate pixels
must be in the footprint and strictly more than 3 px from the known catalogue.
The latter is the non-PRUNE hard exclusion, not an additional PRUNE experiment.

Run after scripts/restore_inputs.py:
    .venv/bin/python scripts/build_snap_variants.py

No submission, leaderboard, hidden test labels, credentials, or off-manifest
inputs are accessed. New candidate TIFFs remain local and gitignored.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

from build_prune_rungs import (  # noqa: E402
    PARENT_SHA_NAN,
    PARENT_SHA_ZEROS,
    build_parent,
    percentile_rank,
    sha256_file,
    validate_reopened,
    verify_inputs,
    write_tif,
)
from gems.gates import run_gates, summarise  # noqa: E402
from gems.ledger import append_variant, load  # noqa: E402
from gems.variants import Dots, snap  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261023"
N_DOTS = 37654
MAX_SHIFT_PX = 2
CATALOGUE_CLEARANCE_PX = 3.0
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "snap_session.json"
OUT_DIR = ROOT / "releases"

# These are prospective, low-confidence MODEL judgments, not fitted scores.
# Wide scenario ranges explicitly include a loss because 400 m flight-line
# spacing makes geophysical edge locations uncertain at the snapping scale.
SPECS = {
    "tmi-hg-r2": {
        "response": "training band 3: TMI horizontal gradient (raw magnitude)",
        "prediction": "MODEL:+0.001",
        "range": "[-0.008,+0.009]",
        "hypothesis": "Snapping R0 dots to nearby TMI horizontal-gradient maxima will align diffuse lineament support with magnetic edges and recover fault pixels missed by sub-kernel positional error.",
        "mimic": "Magnetic edges can be lithologic contacts, intrusive boundaries, or survey-line artefacts rather than brittle faults.",
    },
    "gravity-hg-abs-r2": {
        "response": "training band 18: absolute signed isostatic-gravity horizontal gradient",
        "prediction": "MODEL:-0.001",
        "range": "[-0.010,+0.006]",
        "hypothesis": "Gravity-gradient magnitude may locate basin-range boundaries better than the parent support, but its signed band and broad density sources make this a conservative negative-control SNAP arm.",
        "mimic": "Density contrasts from basin fill, intrusive bodies, and lithologic contacts can produce strong gradients without a fault at the surface.",
    },
    "fused-edge-r2": {
        "response": "equal-weight mean of footprint percentile ranks: band 3 TMI HG, abs(band 18 gravity HG), band 19 detrended-elevation slope",
        "prediction": "MODEL:+0.003",
        "range": "[-0.007,+0.012]",
        "hypothesis": "A consensus magnetic, gravity, and topographic-scarp response should suppress single-sensor mimics and produce the most reliable sub-kernel relocation of R0 dots.",
        "mimic": "Coincident lithologic, density, and erosional boundaries can mimic a fault; consensus can also reinforce a shared non-fault boundary.",
    },
}


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def make_responses(inputs: dict[str, Path], foot: np.ndarray) -> dict[str, np.ndarray]:
    """Read only pinned bands and construct deterministic, label-free responses."""
    import rasterio

    with rasterio.open(inputs["training_features"]) as ds:
        tmi = np.nan_to_num(ds.read(3), nan=0.0).astype(np.float32)
        gravity = np.abs(np.nan_to_num(ds.read(18), nan=0.0)).astype(np.float32)
        slope = np.nan_to_num(ds.read(19), nan=0.0).astype(np.float32)
    responses = {
        "tmi-hg-r2": tmi,
        "gravity-hg-abs-r2": gravity,
        "fused-edge-r2": (
            percentile_rank(tmi, foot)
            + percentile_rank(gravity, foot)
            + percentile_rank(slope, foot)
        ).astype(np.float32) / np.float32(3.0),
    }
    return responses


def hash_owners(rows: list[dict[str, str]]) -> dict[str, tuple[str, str, str]]:
    """Map exact known hashes to experiments, including both encoding twins."""
    owners: dict[str, tuple[str, str, str]] = {
        PARENT_SHA_NAN: (PARENT_ID, "PARENT", "nan"),
        PARENT_SHA_ZEROS: (PARENT_ID, "PARENT", "zeros"),
    }

    def add(sha: str, pair: tuple[str, str, str]) -> None:
        if sha:
            owners.setdefault(sha, pair)

    for row in rows:
        pair = (row.get("parent", ""), row.get("axis", ""), row.get("value", ""))
        add(row.get("sha256", ""), pair)
        add(row.get("sha256_zeros", ""), pair)
        for column in ("file_nan", "file_zeros"):
            value = row.get(column, "")
            path = ROOT / value if value else None
            if path is not None and path.is_file():
                add(sha256_file(path), pair)

    # The previous PRUNE rung recorded fallback hashes outside the CSV schema.
    previous = ROOT / "evidence" / "prune_rungs.json"
    if previous.is_file():
        doc = json.loads(previous.read_text(encoding="utf-8"))
        for item in doc.get("variants", []):
            pair = (item["parent"], item["axis"], item["value"])
            add(item.get("sha256", ""), pair)
            add(item.get("sha256_zeros", ""), pair)
    return owners


def validate_variant(
    value: str,
    dots: Dots,
    parent_mask: np.ndarray,
    response: np.ndarray,
    foot: np.ndarray,
    cat: np.ndarray,
    d_cat: np.ndarray,
) -> tuple[np.ndarray, dict]:
    """Independently enforce SNAP invariants before any file is published."""
    if len(dots) != N_DOTS or not np.all(dots.p == 1.0):
        raise RuntimeError(f"{value}: count/unit-mass invariant failed")
    coords = np.c_[dots.ys, dots.xs]
    if len({tuple(x) for x in coords.tolist()}) != N_DOTS:
        raise RuntimeError(f"{value}: duplicate output pixels")
    if not foot[dots.ys, dots.xs].all() or cat[dots.ys, dots.xs].any():
        raise RuntimeError(f"{value}: footprint/catalogue invariant failed")
    if not (d_cat[dots.ys, dots.xs] > CATALOGUE_CLEARANCE_PX).all():
        raise RuntimeError(f"{value}: a dot is within the 3 px exclusion")

    mask = np.zeros(parent_mask.shape, dtype=bool)
    mask[dots.ys, dots.xs] = True
    removed = int(np.count_nonzero(parent_mask & ~mask))
    added = int(np.count_nonzero(mask & ~parent_mask))
    if removed != added:
        raise RuntimeError(f"{value}: asymmetric parent diff {removed}/{added}")
    pct_changed = 100.0 * removed / N_DOTS

    parent_yx = np.argwhere(parent_mask)
    displacement = np.hypot(dots.ys - parent_yx[:, 0], dots.xs - parent_yx[:, 1])
    if displacement.max(initial=0.0) > MAX_SHIFT_PX + 1e-9:
        raise RuntimeError(f"{value}: displacement exceeds 2 px")
    if int(np.count_nonzero(displacement)) != removed:
        raise RuntimeError(f"{value}: coordinate diff and parent-mask diff disagree")

    before = response[parent_yx[:, 0], parent_yx[:, 1]]
    after = response[dots.ys, dots.xs]
    delta = after - before
    forced = d_cat[parent_yx[:, 0], parent_yx[:, 1]] <= CATALOGUE_CLEARANCE_PX
    stats = {
        "n_dots": N_DOTS,
        "mass_per_dot": 1.0,
        "removed": removed,
        "added": added,
        "shared": N_DOTS - removed,
        "pct_changed": pct_changed,
        "mean_displacement_px": float(displacement.mean()),
        "median_displacement_px": float(np.median(displacement)),
        "max_displacement_px": float(displacement.max()),
        "n_forced_by_3px_exclusion": int(forced.sum()),
        "n_excluded_parent_dots_not_moved": int((forced & (displacement == 0)).sum()),
        "response_mean_before": float(before.mean()),
        "response_mean_after": float(after.mean()),
        "response_mean_delta": float(delta.mean()),
        "n_response_gain": int((delta > 0).sum()),
        "n_response_loss": int((delta < 0).sum()),
        "n_response_unchanged": int((delta == 0).sum()),
        "min_catalogue_distance_px": float(d_cat[mask].min()),
    }
    # Every inherited <=3 px dot must have relocated; zero such residual dots is
    # the meaningful compliance statistic (the field above is retained for audit).
    if stats["n_forced_by_3px_exclusion"] and stats["n_excluded_parent_dots_not_moved"]:
        raise RuntimeError(f"{value}: an excluded parent dot did not move")
    return mask, stats


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, _h19, parent = build_parent(inputs)
    r0 = parent["r0"]
    if int(r0.sum()) != N_DOTS:
        raise RuntimeError("R0 dot count mismatch")
    responses = make_responses(inputs, foot)
    keep_out = cat | (d_cat <= CATALOGUE_CLEARANCE_PX)
    parent_yx = np.argwhere(r0)
    parent_dots = Dots(parent_yx[:, 0], parent_yx[:, 1], np.ones(N_DOTS))

    rows = load(LEDGER)
    existing_pairs = {
        (r.get("parent"), r.get("axis"), r.get("value")): r for r in rows
    }
    owners = hash_owners(rows)
    records: list[dict] = []
    git = git_sha()
    script_sha = sha256_file(Path(__file__))

    for value, spec in SPECS.items():
        pair = (PARENT_ID, "SNAP", value)
        variant = snap(
            parent_dots,
            responses[value],
            max_shift=MAX_SHIFT_PX,
            footprint=foot,
            keep_out=keep_out,
        )
        mask, stats = validate_variant(
            value, variant.dots, r0, responses[value], foot, cat, d_cat
        )
        stem = f"{PARENT_ID}-SNAP{value}-{DATE}"
        tmp_nan = OUT_DIR / f"._building-{value}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{value}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)
        sha_nan = sha256_file(tmp_nan)
        sha_zeros = sha256_file(tmp_zeros)
        short_id = f"{stem}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)

        # Re-read final files from disk, independently of the in-memory mask.
        for path, expect_nan in ((nan_path, True), (zeros_path, False)):
            checks = validate_reopened(
                path, inputs["sample_submission"], mask, foot, cat, d_cat, expect_nan
            )
            gate_results = run_gates(
                path, inputs["sample_submission"], catalogue_path=inputs["existing_faults"]
            )
            ok, report = summarise(gate_results)
            if not ok:
                raise RuntimeError(f"Gate failure for {path}:\n{report}")
            if not all(checks.values()):
                raise RuntimeError(f"Re-read invariant failure for {path}: {checks}")
            if expect_nan:
                checks_nan, report_nan = checks, report
            else:
                checks_zeros, report_zeros = checks, report

        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"{value}: final-path hash drift")
        if sha_nan == sha_zeros:
            raise RuntimeError(f"{value}: encoding twins unexpectedly identical")
        for sha in (sha_nan, sha_zeros):
            owner = owners.get(sha)
            if owner is not None and owner != pair:
                raise RuntimeError(f"Exact hash duplicate: {value} {sha} owned by {owner}")
        previous = existing_pairs.get(pair)
        if previous is not None and previous.get("sha256") != sha_nan:
            raise RuntimeError(f"Repeated (parent, axis, value) with conflicting hash: {pair}")
        owners[sha_nan] = pair
        owners[sha_zeros] = pair

        note = (
            f"{PARENT_ID}; SNAP {value} <=2px; fixed {N_DOTS}; "
            f"moved {stats['removed']} ({stats['pct_changed']:.2f}%); pred {spec['prediction']}"
        )
        if len(note) > 140:
            raise RuntimeError(f"Form note is {len(note)} characters")
        record = {
            "id": short_id,
            "parent": PARENT_ID,
            "axis": "SNAP",
            "value": value,
            "n_dots": N_DOTS,
            "pct_changed": round(stats["pct_changed"], 6),
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "status": "BUILT",
            "predicted_change": spec["prediction"],
            "predicted_range": spec["range"],
            "file_nan": str(nan_path.relative_to(ROOT)),
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "primary_file": nan_path.name,
            "fallback_file": zeros_path.name,
            "sha8": sha_nan[:8],
            "change_desc": f"snap every dot <=2px to {spec['response']}; fixed unit mass/count; >3px catalogue clearance",
            "receipt_score": previous.get("receipt_score", "") if previous else "",
            "receipt_date": previous.get("receipt_date", "") if previous else "",
            "notes": f"mean displacement {stats['mean_displacement_px']:.6f}px; git={git[:12]}; both hashes and gates in evidence/snap_session.json",
            "form_note": note,
            "response": spec["response"],
            "parent_diff": stats,
            "format_validation": {"nan": checks_nan, "zeros": checks_zeros},
            "gate_reports": {"nan": report_nan, "zeros": report_zeros},
            "mechanism_card": {
                "hypothesis": spec["hypothesis"],
                "mechanism": "Move each unit-mass dot to the strongest legal response in its Euclidean 2 px window, with deterministic collision avoidance. This changes position only: S, count, and mass are fixed while kernel overlap with unmapped fault truth may improve.",
                "non_fault_mimic": spec["mimic"],
                "predicted_sign_and_size": f"{spec['prediction']} versus R0; scenario range {spec['range']}; MODEL only. Absolute live changes below 0.01 are no evidence.",
                "falsifier": "A human receipt at least 0.01 below R0 rejects a beneficial SNAP mechanism for this response; for the gravity negative-control arm, a gain at least 0.01 above R0 rejects the predicted negative sign.",
            },
            "git_sha_at_build": git,
            "builder_sha256": script_sha,
            "ledger_append_needed": previous is None,
        }
        records.append(record)
        print(
            f"BUILT {short_id}: moved={stats['removed']} ({stats['pct_changed']:.3f}%), "
            f"mean_shift={stats['mean_displacement_px']:.4f}px, sha256={sha_nan}"
        )

    for record in records:
        if record["ledger_append_needed"]:
            append_variant(
                {k: v for k, v in record.items() if k in {
                    "id", "parent", "axis", "value", "n_dots", "pct_changed",
                    "sha256", "status", "predicted_change", "file_zeros", "file_nan",
                    "sha8", "change_desc", "receipt_score", "receipt_date", "notes"
                }},
                LEDGER,
            )

    report = {
        "schema": "gemsdoe92.snap-session.v1",
        "session_date_utc": DATE,
        "axis": "SNAP",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": N_DOTS,
            "zeros_sha256": PARENT_SHA_ZEROS,
            "nan_sha256": PARENT_SHA_NAN,
            "matches_recorded_hashes": True,
        },
        "design": {
            "max_displacement_px": MAX_SHIFT_PX,
            "catalogue_clearance_rule": "strictly greater than 3 px for every emitted dot",
            "count_and_mass": "37,654 dots, 1.0 each, unchanged",
            "seed": "not used; deterministic response, window order, and tie breaks",
            "only_changed_axis": "edge-response definition within the common SNAP rule",
        },
        "input_manifest_sha256": sha256_file(ROOT / "registry" / "session_manifest.json"),
        "input_count": len(inputs),
        "variants": records,
        "scope_note": "No submission, leaderboard, hidden labels, or off-manifest data accessed. Candidate rasters are local and gitignored. Predictions are MODEL judgments, never scores.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {EVIDENCE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
