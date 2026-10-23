#!/usr/bin/env python3
"""Build three unused SNAP variants of R0 on isotropic gravity / RTP edges.

AXIS = SNAP. The three values differ only in the edge field each R0 dot may
walk toward, inside a Euclidean 2 px window:

* ``iso_g2g10``     — band 05 ``iso_grav_anom_slope``, move iff dest-origin >= 0.10 pct
* ``rtp_hg2g10``    — isotropic |∇_H| of band 02 ``rtp`` (signed RTP; we derive the
                      magnitude; we do **not** use signed band 18), same 0.10 gate
* ``iso_combo2g10`` — equal-weight footprint percentile mean of the two, same gate

Ungated argmax on these fields moved 98–99.8% of R0 (mean 1.7–1.9 px) and is
not a seating test; the 0.10 percentile gate is the SNAP operator of this session.

Same count (37,654), same exclusions (in-footprint, off catalogue, d_cat > 2).
No labels, leaderboard, or submission endpoints are accessed. Candidate TIFFs
are gitignored; hashes and the ledger row are committed.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from build_prune_rungs import (  # noqa: E402
    DATE,
    LEDGER,
    MANIFEST,
    OUT_DIR,
    PARENT_ID,
    PARENT_SHA_NAN,
    PARENT_SHA_ZEROS,
    build_parent,
    sha256_file,
    validate_reopened,
    verify_inputs,
    write_tif,
)
from gems.proxy import evaluate as proxy_evaluate  # noqa: E402
from gems.proxy import leakage_canary  # noqa: E402
from gems.snap_fields import (  # noqa: E402
    BAND_ISO_GRAV_ANOM,
    BAND_ISO_GRAV_HG_SIGNED,
    BAND_ISO_GRAV_SLOPE,
    BAND_RTP,
    isotropic_hg,
    pearson,
    percentile_rank,
)
from gems.variants import Dots, snap  # noqa: E402
from gems57 import metric  # noqa: E402

RECEIPTS = ROOT / "evidence" / "snap_session.json"
AXIS = "SNAP"
SNAP_MAX_PX = 2
SNAP_MIN_GAIN = 0.10  # percentile-rank units; ungated argmax is not a seating test
PARENT_MIN_DCAT = 2.0
SNAP_VALUES = ("iso_g2g10", "rtp_hg2g10", "iso_combo2g10")
ABORTED_UNGATED = {"iso_g2", "rtp_hg2", "iso_combo2"}

# A priori MODEL projections (not scores). Set before looking at PROXY.
PREDICTION = {
    "iso_g2g10": ("MODEL:+0.003", "[-0.008,+0.012]"),
    "rtp_hg2g10": ("MODEL:+0.000", "[-0.010,+0.008]"),
    "iso_combo2g10": ("MODEL:+0.004", "[-0.006,+0.014]"),
}


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def finite_valid(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    return foot & np.isfinite(a) & (np.abs(a) < 1e20)


def audit_bands(inputs: dict[str, Path], foot: np.ndarray) -> dict:
    """Refuse to snap to the wrong gravity band; confirm band 05 vs band 18."""
    with rasterio.open(inputs["training_features"]) as ds:
        names = list(ds.descriptions)
        b02 = ds.read(BAND_RTP).astype(np.float64)
        b05 = ds.read(BAND_ISO_GRAV_SLOPE).astype(np.float64)
        b13 = ds.read(BAND_ISO_GRAV_ANOM).astype(np.float64)
        b18 = ds.read(BAND_ISO_GRAV_HG_SIGNED).astype(np.float64)
        tag02 = ds.tags(BAND_RTP).get("band_name", "")
        tag05 = ds.tags(BAND_ISO_GRAV_SLOPE).get("band_name", "")
        tag18 = ds.tags(BAND_ISO_GRAV_HG_SIGNED).get("band_name", "")

    if tag05 != "iso_grav_anom_slope" or tag18 != "iso_grav_anom_hg" or tag02 != "rtp":
        raise RuntimeError(f"Unexpected band tags: 02={tag02!r} 05={tag05!r} 18={tag18!r}")

    v05 = finite_valid(b05, foot)
    v02 = finite_valid(b02, foot)
    v13 = finite_valid(b13, foot)
    v18 = finite_valid(b18, foot)
    if float((b05[v05] < 0).mean()) > 1e-6:
        raise RuntimeError("band 05 is not non-negative; refusing to treat it as |grad g|")
    if float((b18[v18] < 0).mean()) < 0.3:
        raise RuntimeError("band 18 is not signed; the GEMSDOE87 ∂g/∂x audit would not hold")

    mag13 = isotropic_hg(b13, v13)
    ok13 = v05 & np.isfinite(mag13)
    r05 = pearson(b05[ok13], mag13[ok13])
    if not np.isfinite(r05) or r05 < 0.90:
        raise RuntimeError(f"band 05 does not match |grad_H band 13| (r={r05})")

    mag02 = isotropic_hg(b02, v02)
    ok02 = np.isfinite(mag02) & v02
    if int(ok02.sum()) < 1_000_000:
        raise RuntimeError("RTP isotropic HG produced too few valid pixels")

    audit = {
        "band_descriptions": names,
        "band02_tag": tag02,
        "band05_tag": tag05,
        "band18_tag": tag18,
        "band05_p_neg": float((b05[v05] < 0).mean()),
        "band18_p_neg": float((b18[v18] < 0).mean()),
        "band02_p_neg": float((b02[v02] < 0).mean()),
        "corr_band05_vs_iso_grad_band13": r05,
        "corr_band18_vs_iso_grad_band13": pearson(
            b18[v18 & np.isfinite(mag13)], mag13[v18 & np.isfinite(mag13)]
        ),
        "n_valid_band05": int(v05.sum()),
        "n_valid_rtp_hg": int(ok02.sum()),
        "used_bands": {
            "iso_g2g10": "pct(band 05 iso_grav_anom_slope); 0.10 percentile gate",
            "rtp_hg2g10": "pct(|grad_H| of band 02 rtp); 0.10 percentile gate",
            "iso_combo2g10": "0.5*pct(band05)+0.5*pct(|grad_H rtp|); 0.10 percentile gate",
        },
        "rejected_band18": "signed iso_grav_anom_hg (dg/dx); previous SNAP arms used this by mistake",
        "ungated_argmax_diagnostic": {
            "iso_g2": {"frac_moved": 0.9979, "mean_disp_px": 1.937, "sha256_nan": "647b1bb7685fce66876e31309c328f5c07540284b885e41c7cf6a42acde4cc00"},
            "rtp_hg2": {"frac_moved": 0.9812, "mean_disp_px": 1.736, "sha256_nan": "d943b2d4caff315a4fda4ddec0d52af0278c865b5df363f72e96a9f7ec9968b4"},
            "iso_combo2": {"frac_moved": 0.9856, "mean_disp_px": 1.761, "sha256_nan": "5362c3d4481bd00b24ce9c015a1332c1833e112aeb2d8d5a6f969d2f1f570c63"},
            "decision": "not session variants; operator is a field replacement, not a seating test",
        },
    }
    p5 = percentile_rank(np.where(v05, b05, 0.0), v05)
    p2 = percentile_rank(np.where(ok02, mag02, 0.0), ok02)
    combo = np.where(v05 & ok02, 0.5 * p5 + 0.5 * p2, np.nan)
    fields = {
        "iso_g2g10": np.where(v05, p5, np.nan),
        "rtp_hg2g10": np.where(ok02, p2, np.nan),
        "iso_combo2g10": combo,
    }
    return audit, fields


def dots_from_mask(mask: np.ndarray) -> Dots:
    ys, xs = np.nonzero(mask)
    return Dots(ys, xs, np.ones(len(ys), dtype=np.float64))


def mask_from_dots(dots: Dots, shape: tuple[int, int]) -> np.ndarray:
    m = np.zeros(shape, dtype=bool)
    m[dots.ys, dots.xs] = True
    return m


def form_note(value: str, n_moved: int, pct: float, pred: str) -> str:
    labels = {
        "iso_g2g10": "SNAP<=2px g+0.10 iso_grav_slope",
        "rtp_hg2g10": "SNAP<=2px g+0.10 |grad_H RTP|",
        "iso_combo2g10": "SNAP<=2px g+0.10 iso_grav+|gRTP|",
    }
    note = (
        f"h33-h33-2-b2; {labels[value]}; n=37654; "
        f"moved {n_moved} ({pct:.2f}%); pred {pred}"
    )
    if len(note) > 140:
        raise RuntimeError(f"form note {len(note)} chars: {note}")
    return note


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, _h19, parent = build_parent(inputs)
    r0 = parent["r0"]
    n0 = int(r0.sum())
    if n0 != 37654 or np.any(r0 & cat) or np.any(d_cat[r0] <= PARENT_MIN_DCAT):
        raise RuntimeError("R0 parent invariants failed")
    if parent["parent_hashes"]["zeros"] != PARENT_SHA_ZEROS:
        raise RuntimeError("R0 zeros SHA mismatch")
    if parent["parent_hashes"]["nan"] != PARENT_SHA_NAN:
        raise RuntimeError("R0 nan SHA mismatch")

    audit, fields = audit_bands(inputs, foot)
    parent_dots = dots_from_mask(r0)
    # Destinations: never on catalogue, never closer than 3 px (hard constraint 4).
    # Parent already has 2,171 dots with 2 < d_cat <= 3; those origins may stay
    # (snap falls back to the origin) so SNAP does not mix in a PRUNE. New landings
    # cannot enter that collar.
    keep_out = cat | (d_cat < 3.0)

    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_off = sgmc_raw & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_r0 = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)

    cat_ys, cat_xs = np.nonzero(cat)
    r0_ys, r0_xs = np.nonzero(r0)
    proxy_r0 = proxy_evaluate(r0_ys, r0_xs, cat_ys, cat_xs, frac=0.25, seed=20, n_boot=400)

    used_hashes = {PARENT_SHA_NAN, PARENT_SHA_ZEROS}
    reserved = set(PREDICTION)
    existing_rows: list[dict[str, str]] = []
    fields_out = None
    if LEDGER.is_file():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            fields_out = list(reader.fieldnames or [])
        for row in existing_rows:
            if row.get("parent") == PARENT_ID and row.get("axis") == AXIS and row.get("value") in (reserved | ABORTED_UNGATED):
                continue
            for col in ("sha256", "sha256_zeros"):
                if row.get(col):
                    used_hashes.add(row[col])
            for col in ("file_nan", "file_zeros"):
                p = ROOT / row[col] if row.get(col) else None
                if p is not None and p.is_file():
                    used_hashes.add(sha256_file(p))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    variants: list[dict] = []
    mechanism_cards: dict[str, dict] = {}
    canaries: dict[str, dict] = {}

    for value in SNAP_VALUES:
        response = np.array(fields[value], dtype=np.float64)
        finite_resp = np.isfinite(response) & foot
        response = np.where(finite_resp, response, -np.inf)
        this_keep = keep_out | ~finite_resp
        v = snap(
            parent_dots,
            response,
            max_shift=SNAP_MAX_PX,
            footprint=foot,
            keep_out=this_keep,
            min_gain=SNAP_MIN_GAIN,
        )
        mask = mask_from_dots(v.dots, r0.shape)
        if int(mask.sum()) != n0:
            raise RuntimeError(f"{value}: count {int(mask.sum())} != {n0}")
        if np.any(mask & cat) or np.any(d_cat[mask] <= PARENT_MIN_DCAT):
            raise RuntimeError(f"{value}: catalogue exclusion violated")
        if len(set(zip(v.dots.ys.tolist(), v.dots.xs.tolist()))) != n0:
            raise RuntimeError(f"{value}: stacked dots")

        n_moved = int(v.n_changed)
        pct = float(v.pct_changed)
        tmp_nan = OUT_DIR / f"._building-{value}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{value}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)
        checks_nan = validate_reopened(tmp_nan, inputs["sample_submission"], mask, foot, cat, d_cat, True)
        checks_zero = validate_reopened(tmp_zeros, inputs["sample_submission"], mask, foot, cat, d_cat, False)
        sha_nan, sha_zeros = sha256_file(tmp_nan), sha256_file(tmp_zeros)
        if sha_nan == sha_zeros or sha_nan in used_hashes or sha_zeros in used_hashes:
            raise RuntimeError(f"Exact duplicate SHA-256 at {value}")
        used_hashes.update((sha_nan, sha_zeros))

        short_id = f"h33-h33-2-b2-SNAP{value}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Final-path re-read hash changed at {value}")
        checks_nan = validate_reopened(nan_path, inputs["sample_submission"], mask, foot, cat, d_cat, True)
        checks_zero = validate_reopened(zeros_path, inputs["sample_submission"], mask, foot, cat, d_cat, False)

        pred_text, pred_range = PREDICTION[value]
        note = form_note(value, n_moved, pct, pred_text)
        sgmc = metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)
        v_ys, v_xs = np.nonzero(mask)
        proxy = proxy_evaluate(v_ys, v_xs, cat_ys, cat_xs, frac=0.25, seed=20, n_boot=400)
        canary = leakage_canary(np.where(np.isfinite(fields[value]), fields[value], 0.0), cat, foot)
        canaries[value] = canary
        if canary.get("status") == "STOP_AND_INVESTIGATE":
            raise RuntimeError(f"leakage canary STOP for {value}: {canary}")

        record = {
            "id": short_id,
            "parent": PARENT_ID,
            "axis": AXIS,
            "value": value,
            "n_dots": n0,
            "pct_changed": round(pct, 6),
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "status": "BUILT",
            "predicted_change": pred_text,
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (
                f"SNAP each R0 dot <=2 px onto local argmax of {audit['used_bands'][value]}; "
                f"count held at {n0}; d_cat>2 exclusion unchanged"
            ),
            "receipt_score": "",
            "receipt_date": "",
            "notes": (
                f"MODEL range {pred_range}; mean_disp_px={v.stats['mean_displacement_px']:.4f}; "
                f"frac_moved={v.stats['frac_moved']:.4f}; "
                f"SGMC PROXY delta {sgmc['dti'] - sgmc_r0['dti']:+.6f}; "
                f"see evidence/snap_session.json"
            ),
            "predicted_range": pred_range,
            "mean_displacement_px": float(v.stats["mean_displacement_px"]),
            "median_displacement_px": float(v.stats["median_displacement_px"]),
            "max_displacement_px": float(v.stats["max_displacement_px"]),
            "frac_moved": float(v.stats["frac_moved"]),
            "n_moved": n_moved,
            "min_catalogue_distance_px": float(d_cat[mask].min()),
            "parent_diff": {
                "removed": n_moved,
                "added": n_moved,
                "shared": n0 - n_moved,
                "moved_pct": round(pct, 6),
                "symmetric_diff_px": 2 * n_moved,
            },
            "sgmc_control_proxy": {
                "evidence_label": "PROXY",
                "dti": round(sgmc["dti"], 6),
                "delta_vs_r0": round(sgmc["dti"] - sgmc_r0["dti"], 6),
                "n_withheld_control_pixels": int(sgmc_off.sum()),
            },
            "hide_recover_proxy": {
                "evidence_label": "PROXY",
                "n_withheld": proxy["n_withheld"],
                "recall_at_3px": proxy["recall_at_3px"],
                "ci95": list(proxy["ci95"]),
                "r0_recall_at_3px": proxy_r0["recall_at_3px"],
                "r0_ci95": list(proxy_r0["ci95"]),
            },
            "leakage_canary": canary,
            "format_validation": {"nan": checks_nan, "zeros": checks_zero},
            "form_note": note,
            "git_sha_at_build": git_head(),
        }
        variants.append(record)
        mechanism_cards[short_id] = {
            "parent": PARENT_ID,
            "axis": AXIS,
            "value": value,
            "hypothesis": {
                "iso_g2g10": (
                    "R0 dots were Poisson-thinned from a binary H19-5 mask, so they can sit up to "
                    "~200 m off the gravity-defined basement step. Band 05 is isotropic |grad_H g|, "
                    "the density-contrast edge that maps Basin-and-Range normal-fault steps. "
                    "Re-seating only those dots whose 2 px window holds a >=0.10-percentile stronger "
                    "gravity edge should raise kernel credit T at fixed mass S without the 99% "
                    "field-replacement of ungated argmax."
                ),
                "rtp_hg2g10": (
                    "The same gated seating test against the isotropic horizontal gradient of "
                    "reduced-to-pole magnetics (derived from signed band 02). RTP edges mark "
                    "susceptibility contrasts along faults; TMI-HG (band 03) was already snapped "
                    "elsewhere and is not reused."
                ),
                "iso_combo2g10": (
                    "A real fault step should light up both the gravity slope and the RTP edge. "
                    "Equal-weight percentile combination down-weights single-sensor lithologic "
                    "contacts. Same 0.10 gate, count, and catalogue exclusions as the other two arms."
                ),
            }[value],
            "mechanism": (
                "SNAP only: each of 37,654 unit-mass dots may move at most 2 px Euclidean to the "
                "strongest finite response in its 13-pixel disk, and only if that response exceeds "
                "the origin by >= 0.10 footprint percentile. Ties stay. Occupied pixels are skipped. "
                "Destinations must remain in-footprint, off catalogue, and at d_cat > 2 px. "
                "No ranking, mass, prune, or refill."
            ),
            "non_fault_mimic": {
                "iso_g2g10": (
                    "Isostatic gravity edges also mark pluton contacts, caldera walls, and "
                    "basin-fill thickness changes that are not brittle faults."
                ),
                "rtp_hg2g10": (
                    "RTP edges mark lithologic contacts, alteration halos, and volcanic vents "
                    "as well as faults."
                ),
                "iso_combo2g10": (
                    "Mafic dikes and caldera rings can carry both density and magnetic contrast; "
                    "agreement is not proof of a Quaternary fault."
                ),
            }[value],
            "predicted_sign_and_size": f"{pred_text} vs R0, range {pred_range}; MODEL only, not a score.",
            "falsifier": (
                "A receipt change of magnitude >= 0.01 against R0 decides the seating hypothesis "
                "for that field. |Δ| < 0.01 is no evidence (public chunks). A >= 0.01 loss says "
                "clustering onto crests costs more than the kernel-credit gain."
            ),
            "decision_rule": "Treat absolute live change < 0.01 as no evidence; compare only human receipts.",
        }
        print(
            f"BUILT {short_id}: moved={n_moved} ({pct:.2f}%), "
            f"mean_disp={v.stats['mean_displacement_px']:.3f}px, sha256={sha_nan}"
        )

    default_fields = [
        "id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
        "status", "predicted_change", "file_zeros", "file_nan", "sha8",
        "change_desc", "receipt_score", "receipt_date", "notes",
    ]
    if fields_out is None:
        fields_out = default_fields
    new_values = {rec["value"]: rec for rec in variants}
    retained: list[dict[str, str]] = []
    for row in existing_rows:
        key = (row.get("parent", ""), row.get("axis", ""), row.get("value", ""))
        if key[0] == PARENT_ID and key[1] == AXIS and key[2] in (ABORTED_UNGATED | set(new_values)):
            continue  # this session owns these SNAP values; rebuilds replace the row
        retained.append(row)
    seen = {(r.get("parent", ""), r.get("axis", ""), r.get("value", "")) for r in retained}
    for rec in variants:
        triple = (rec["parent"], rec["axis"], rec["value"])
        if triple in seen:
            raise RuntimeError(f"Repeated (parent, axis, value): {triple}")
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields_out, lineterminator="\n")
        writer.writeheader()
        for row in retained:
            writer.writerow({k: row.get(k, "") for k in fields_out})
        for rec in variants:
            writer.writerow({k: rec.get(k, "") for k in fields_out})

    report = {
        "schema": "gemsdoe92.snap-iso.v1",
        "session_date_utc": DATE,
        "axis": AXIS,
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n0,
            "zeros_sha256": parent["parent_hashes"]["zeros"],
            "nan_sha256": parent["parent_hashes"]["nan"],
            "matches_recorded_hashes": True,
        },
        "band_audit": audit,
        "input_manifest_sha256": sha256_file(MANIFEST),
        "r0_sgmc_proxy": {"evidence_label": "PROXY", "dti": round(sgmc_r0["dti"], 6)},
        "r0_hide_recover_proxy": {
            "evidence_label": "PROXY",
            "n_withheld": proxy_r0["n_withheld"],
            "recall_at_3px": proxy_r0["recall_at_3px"],
            "ci95": list(proxy_r0["ci95"]),
        },
        "variants": variants,
        "scope_note": (
            "No submission, leaderboard, hidden labels, or off-manifest data accessed. "
            "New candidate rasters are generated locally and gitignored."
        ),
    }
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "ledger" / "mechanism_cards.json").write_text(
        json.dumps(mechanism_cards, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
