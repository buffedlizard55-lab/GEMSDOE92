#!/usr/bin/env python3
"""Fail closed if the served download is missing, mislabeled, or if a page's statuses disagree with the evidence.

Rewritten 2026-10-24.  The previous contract hard-coded "NOT CLEARED / DUPLICATE UNDER THE LITERAL REGISTRY RULE /
submission_eligible must be false" for every primary, which made "OK TO SUBMIT" unreachable by construction (the
literal all-registry rule cannot be passed by any file: see docs/UNIQUENESS_POLICY_20261024.md).  The contract is now
*derived*: statuses are recomputed here from the evidence JSON through gems.uniqueness_policy.decide and
gems.verdict.derive, and the page, the audit receipt and the run card must all agree with the recomputation.  The site
can say OK TO SUBMIT only when the tested logic does; every served raster must still pass the format gates.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems import lcs, uniqueness_policy, verdict  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
N_DOTS = 37654


def derive_status(run_card: dict, audit: dict, final_doc: dict, surface_doc: dict, policy: dict | None = None) -> dict:
    """Recompute the public statuses from evidence only (importable by tests)."""
    policy = policy or uniqueness_policy.load_policy()
    decision = uniqueness_policy.decide(surface_doc, final_doc, policy)
    gates_ok = bool(audit["gates_zeros_pass"] and all(g["ok"] for g in audit["gates_zeros"]))
    format_pass = bool(gates_ok and audit["overall_pass"])
    canary_ok = bool(run_card["holdout"]["canary"]["symmetric_auc"] <= 0.90)
    proj = run_card["projection_MODEL"]
    loo = json.loads((ROOT / "evidence" / "lcs_loo_calibration.json").read_text())
    band = lcs.dti_band_from_credit_error(loo["grid"][str(lcs.GAMMA)]["mae"])
    model_ok = bool(min(proj["dti_null"], proj["dti_shrunk"]) >= proj["r0_by_construction"] - band)
    return verdict.derive(format_pass, decision, canary_ok, model_ok, run_card["holdout"]["lcs_minus_best"]) | {"policy_decision": decision}


def main() -> int:
    problems: list[str] = []
    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")

    # ---- page contract (properties, not one lane's wording) ---------------------------------
    for needle in ("OK TO DOWNLOAD", "OK TO SUBMIT", "Predicted values must be in range [0, 1]", "HOLDOUT-DTI",
                   "executive-summary.html", "Tier T"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not re.search(r"(weekly slot|3/week|3 submissions per week|human step)", html, re.I):
        problems.append("index.html carries no weekly-slot caution")
    links = re.findall(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    if not links:
        problems.append("index.html offers no zeros-outside download")
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.\d{4}", html):
        problems.append("a holdout/model number is labeled ORGANIZER-CONFIRMED")

    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    for path in served:
        if f"downloads/{path.name}" not in html:
            problems.append(f"{path.name} is served but not linked from index.html")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5

    # ---- every served raster must pass the format gates as served ---------------------------------
    for path in served:
        tag = path.name
        expected_dots = N_DOTS
        per_file_audit = path.with_name(path.stem.removesuffix("-zeros") + "-audit.json")
        if per_file_audit.is_file():
            try:
                doc = json.loads(per_file_audit.read_text(encoding="utf-8"))
                expected_dots = int(doc.get("n_positive_pixels", doc.get("raster", {}).get("positive_pixels", doc.get("n_dots", N_DOTS))))
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                problems.append(f"{tag}: invalid per-file audit receipt: {exc}")
        with rasterio.open(path) as ds:
            a = ds.read(1)
            if ds.dtypes[0] != "float32" or ds.count != 1:
                problems.append(f"{tag}: dtype/band")
            if not np.isfinite(a).all():
                problems.append(f"{tag}: NaN/inf present (portal [0,1] risk)")
            if a.min() < 0 or a.max() > 1:
                problems.append(f"{tag}: values [{a.min()}, {a.max()}]")
            if np.any((a > 0) & ~footprint):
                problems.append(f"{tag}: mass outside footprint")
            if np.any(a[cat] > 0):
                problems.append(f"{tag}: mass on catalogue")
            if int((a > 0).sum()) != expected_dots:
                problems.append(f"{tag}: n_dots {int((a > 0).sum())} != audit/expected {expected_dots}")
        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{tag}: {exc}")
        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS), prune_radius=2))
        if not ok:
            problems.append(f"{tag}: gates failed\n{report}")
        else:
            print(f"  PASS {tag}  sha256 {sha256_file(path)[:16]}…")

    # ---- the primary: first download link, recomputed statuses must match everywhere -------------
    if links:
        primary = DOCS / links[0]
        if not primary.is_file():
            problems.append(f"index.html points at {links[0]}, which does not exist")
        else:
            variant = primary.stem.removesuffix("-zeros")
            audit_path = primary.with_name(variant + "-audit.json")
            card_path = ROOT / "evidence" / "lcs_run_card.json"
            if not audit_path.is_file():
                problems.append(f"no audit receipt beside the primary: {audit_path.name}")
            elif not card_path.is_file():
                problems.append("evidence/lcs_run_card.json missing")
            else:
                audit = json.loads(audit_path.read_text())
                card = json.loads(card_path.read_text())
                sha = sha256_file(primary)
                if audit.get("sha256_zeros") != sha:
                    problems.append("audit receipt sha256 != primary bytes on disk")
                if card.get("raster_sha256") != sha:
                    problems.append("run card SHA256 != primary bytes")
                if not (audit["public_registry_uniqueness"].get("candidate_hash_matches_scan") is True):
                    problems.append("registry gate evidence is not for these exact candidate bytes")
                final_doc = json.loads((ROOT / "evidence" / "lcs_registry_final.json").read_text())
                surface_doc = json.loads((ROOT / "evidence" / "lcs_registry_surface.json").read_text())
                if final_doc.get("candidate_sha256") != sha:
                    problems.append("evidence/lcs_registry_final.json is for different bytes")
                derived = derive_status(card, audit, final_doc, surface_doc)
                for key, got in (("submission_eligible", audit.get("submission_eligible")), ("verdict", audit.get("verdict"))):
                    want = derived["ok_to_submit"] if key == "submission_eligible" else derived["verdict"]
                    if got != want:
                        problems.append(f"audit {key}={got!r} but evidence implies {want!r}")
                if card["status"]["ok_to_submit"] != derived["ok_to_submit"] or card["verdict"] != derived["verdict"]:
                    problems.append("run card status/verdict disagree with the recomputation")
                if len(card["note"]) > 140 or len(card["name"]) > 140:
                    problems.append("name or note exceeds 140 characters")
                for needle in (card["name"], card["note"]):
                    if needle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") not in html:
                        problems.append(f"index.html does not show {needle[:50]!r}")
                # the card around the primary must carry exactly the derived statuses
                m = re.search(r'id="the-file".*?</section>', html, re.S)
                block = m.group(0) if m else ""
                has_yes, has_no = "✅ OK TO SUBMIT" in block, "⛔ NOT OK TO SUBMIT" in block
                if derived["ok_to_submit"] and not (has_yes and not has_no):
                    problems.append("page does not say OK TO SUBMIT although the evidence implies it")
                if (not derived["ok_to_submit"]) and not (has_no and not has_yes):
                    problems.append("page says OK TO SUBMIT although the evidence does not imply it")
                if derived["ok_to_download"] and "✅ OK TO DOWNLOAD" not in block:
                    problems.append("page does not say OK TO DOWNLOAD")
                if derived["verdict"] == "promote" and "SLOT VERDICT: promote" not in block:
                    problems.append("page does not show the promote slot verdict")
                if derived["verdict"] != "promote" and "SLOT VERDICT: promote" in block:
                    problems.append("page shows a promote slot verdict that the evidence does not support")
                if not derived["literal_registry_rule_passed"] and "Tier T" not in block + html:
                    problems.append("literal-rule status not disclosed")
                print(f"  PRIMARY {primary.name}: download={derived['ok_to_download']} submit={derived['ok_to_submit']} "
                      f"slot={derived['verdict']} literal_T={derived['literal_registry_rule_passed']}")

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
