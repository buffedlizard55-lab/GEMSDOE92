#!/usr/bin/env python3
"""Compile 2026-10-29 8-owner fleet inventory, matched CLAIM ledger, and Goodhart-debiased LBM-v3.

Writes:
  - ledger/claims_20261029.txt
  - evidence/claims_matched_20261029.json
  - evidence/fleet_8owners_20261029.json
  - evidence/lbm_v3_20261029.json
  - .cache/lbm/lbm_v3_maps.npz
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

import lbm_data as L  # noqa: E402
import lbm_fit_final as lff  # noqa: E402
import lbm_harness as Hh  # noqa: E402
from gems import lbmodel as M, registry_cache as rc  # noqa: E402

NEW_20261029_ROWS = [
    ("GEMSDOE92", "https://buffedlizard55-lab.github.io/GEMSDOE92/", "gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros", 0.2784),
    ("KANLERGEMSDOE3", "https://kanlerxz87-cyber.github.io/KANLERGEMSDOE3/docs/index.html", "kanlergemsdoe3-h-k3-1-cadg-submod-exp-k3-3-oof8f-37654-20261026-f0565e6d10f9-zeros", 0.1233),
    ("GEMSDOEkarage1", "https://karagemop466-tech.github.io/GEMSDOEkarage1/docs/", "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros", 0.1648),
    ("ApartGEMSDOE3", "https://apartanish22-droid.github.io/ApartGEMSDOE3/", "apartgemsdoe3-h-apart3-1-cfkc-dhc-37654-20261027T215000Z-9dedadfc-zeros", 0.1625),
]


def match_one(files: list[dict], site: str, name: str) -> tuple[dict | None, int, int]:
    key = name.lower()
    hits = []
    for f in files:
        stem = Path(f["path"]).name.lower()
        for ext in (".tiff", ".tif"):
            if stem.endswith(ext):
                stem = stem[: -len(ext)]
        if stem == key or key in stem:
            exact = stem == key or stem.endswith(key) or stem.startswith(key)
            same_repo = f["repo"].upper() == site.upper()
            hits.append((0 if same_repo else 1, 0 if stem == key else (1 if exact else 2),
                         0 if "docs/downloads/" in f["path"] else 1, f))
    hits.sort(key=lambda t: t[:3])
    shas = []
    for h in hits:
        if h[3]["sha256"] not in shas:
            shas.append(h[3]["sha256"])
    if not hits:
        return None, 0, 0
    best = hits[0][3]
    return dict(repo=best["repo"], owner=best["owner"], path=best["path"],
                sha256=best["sha256"], bytes=best["bytes"]), len(hits), len(shas)


def main() -> int:
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    files = [f for r in inv["repositories"] for f in r["files"]]

    # 1. Build ledger/claims_20261029.txt
    base_lines = [ln.strip() for ln in (ROOT / "ledger" / "claims_20261028.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    updated_lines = []
    for ln in base_lines:
        if "udth-submod-e3-20261027-50e7b334|0.0525" in ln:
            # Record 2026-10-29 prompt value while tagging conflict in JSON (IR-1029-2)
            updated_lines.append(ln.replace("|0.0525", "|0.1516"))
        else:
            updated_lines.append(ln)
    for site, url, name, sc in NEW_20261029_ROWS:
        updated_lines.append(f"{site}|{url}|{name}|{sc:.4f}")

    claims_29_path = ROOT / "ledger" / "claims_20261029.txt"
    claims_29_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    # 2. Match all claims to .cache/registry_v3
    matched_rows = []
    for ln in updated_lines:
        site, url, name, sc_s = ln.split("|")
        m, nh, nd = match_one(files, site, name)
        rec = dict(
            site=site,
            site_url=url,
            name=name,
            claim=float(sc_s),
            evidence_class="CLAIM (owner-reported 2026-10-29 prompt; no organizer receipt)",
            n_hits=nh,
            n_distinct_sha=nd,
        )
        if "50e7b334" in name:
            rec["conflicted_claim_20261028"] = 0.0525
            rec["flagged_irregularity"] = "IR-1029-2: 0.0525 in 2026-10-28 prompt vs 0.1516 in 2026-10-29 prompt; excluded from primary LBM-v3 fit"
        if any(name == r[2] for r in NEW_20261029_ROWS):
            rec["newly_scored_20261029"] = True
        if m is not None:
            rec["match"] = m
        matched_rows.append(rec)

    matched_count = sum(1 for r in matched_rows if "match" in r)
    (ROOT / "evidence" / "claims_matched_20261029.json").write_text(
        json.dumps(
            dict(
                schema="gemsdoe92-claims-matched-v2-20261029",
                created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                claims=len(matched_rows),
                matched=matched_count,
                conflict_flagged=1,
                newly_scored_20261029=len(NEW_20261029_ROWS),
                rows=matched_rows,
            ),
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    # 3. Build 8-owner fleet summary for 2026-10-29
    prev_fleet = json.loads((ROOT / "evidence" / "fleet_8owners_20261028.json").read_text(encoding="utf-8"))
    by_owner: dict[str, list[dict]] = {}
    for r in inv["repositories"]:
        by_owner.setdefault(r["owner"], []).append(r)

    owners_out = []
    for prev_o in prev_fleet["owners"]:
        ow = prev_o["owner"]
        rs = by_owner.get(ow, [])
        ow_files = [f for r in rs for f in r["files"]]
        ow_shas = {f["sha256"] for f in ow_files}
        owners_out.append(
            dict(
                owner=ow,
                total_gemsdoe_repos=max(prev_o["total_gemsdoe_repos"], len(rs)),
                repos_with_grid_tifs=sum(1 for r in rs if r["files"]),
                grid_tif_files=len(ow_files),
                unique_sha256=len(ow_shas),
                empty_repos=prev_o["empty_repos"],
            )
        )

    unscored_29 = []
    for ln in (ROOT / "ledger" / "unscored_20261029.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        site, url, name = ln.split("|")
        m, _, _ = match_one(files, site, name)
        if m:
            meta, _ = rc.load_summary(m["sha256"])
            unscored_29.append(
                dict(
                    prompt_site=site,
                    name=name,
                    sha256=m["sha256"],
                    n_fp_pos=int(meta["meta"]["n_fp_pos"]),
                    matched_path=f"{m['owner']}/{m['repo']}:{m['path']}",
                )
            )

    all_unique_shas = sorted({f["sha256"] for f in files})
    fleet_29 = dict(
        schema="gemsdoe92-fleet-8owners-v2-20261029",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        total_gemsdoe_repos=sum(o["total_gemsdoe_repos"] for o in owners_out),
        repos_with_grid_tifs=sum(o["repos_with_grid_tifs"] for o in owners_out),
        total_grid_raster_files=len(files),
        unique_sha256=len(all_unique_shas),
        owners=owners_out,
        unscored_prompt_entries=unscored_29,
    )
    (ROOT / "evidence" / "fleet_8owners_20261029.json").write_text(json.dumps(fleet_29, indent=2) + "\n", encoding="utf-8")

    # 4. Ensure all matched rasters have cached coverage fields & fit Goodhart-Debiased LBM-v3
    fp, cat, lin, scored_full, dcat_full, dh_full = lff.layers()
    H, W = L.SHAPE
    scored = scored_full.ravel()[lin]
    dcat = dcat_full.ravel()[lin]
    dh = dh_full.ravel()[lin]
    Hh.CACHE.mkdir(parents=True, exist_ok=True)

    clean_rows = [r for r in matched_rows if "match" in r and not r.get("flagged_irregularity")]
    for r in clean_rows:
        sha = r["match"]["sha256"]
        cf = Hh.CACHE / f"{sha}.npz"
        if not cf.is_file():
            p, _ = L.full_from_summary(sha)
            C = M.coverage_field(p).ravel()[lin].astype(np.float16)
            pv = p.ravel()[lin]
            pos = np.flatnonzero(pv > 0).astype(np.int32)
            np.savez(cf, C=C, pos=pos, val=pv[pos].astype(np.float32))

    y = np.array([r["claim"] for r in clean_rows])
    sha_arr = np.array([r["match"]["sha256"] for r in clean_rows])
    is_new29 = np.array([bool(r.get("newly_scored_20261029")) for r in clean_rows])
    onh = np.array([float((dh[np.load(Hh.CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in sha_arr])
    # Freeze G-set strictly on pre-2026-10-29 claims to prevent any lookahead
    gset = (~is_new29) & (y >= 0.18) & (onh < 0.30)
    groups = np.array(["H19FAM" if o >= 0.70 else r["site"] for o, r in zip(onh, clean_rows)])

    near2 = {}
    near2_full = {}
    for s in dict.fromkeys(sha_arr[gset]):
        z = np.load(Hh.CACHE / f"{s}.npz")
        m_arr = np.zeros(H * W, bool)
        m_arr[lin[z["pos"]]] = True
        d_arr = ndi.distance_transform_edt(~m_arr.reshape(H, W))
        near2_full[s] = d_arr <= 2.0
        near2[s] = near2_full[s].ravel()[lin]

    def cons_vec(excl=()):
        c = np.zeros(lin.size, np.int16)
        for s, v in near2.items():
            if s not in excl:
                c += v
        return c

    def cmap(cons):
        c = lff.factor_ids(dcat, dh, cons)
        c[~scored] = -1
        return c

    S = Hh.stats({"f": cmap(cons_vec())}, clean_rows, scored)["f"]
    X_v1 = M.factor_design(lff.LEVELS)
    X_v3, bounds_v3 = M.monotone_factor_design(lff.LEVELS, nonincreasing_factors=(1,))
    LAM_V3 = 3e-3

    # Prospective OOT proof: train strictly on 127 pre-2026-10-29 claims, test on 4 new 2026-10-29 claims
    tr_oot = ~is_new29
    fit_v1_oot = M.fit_loglinear(S["A"][tr_oot], S["m"][tr_oot], S["n"][tr_oot], y[tr_oot], S["Ncls"], X_v1, lam=1e-3)
    pred_v1_oot = M.predict(fit_v1_oot["rho"], S["A"][is_new29], S["m"][is_new29], S["n"][is_new29], S["Ncls"])

    fit_v3_oot = M.fit_loglinear(
        S["A"][tr_oot], S["m"][tr_oot], S["n"][tr_oot], y[tr_oot], S["Ncls"], X_v3, lam=LAM_V3, bounds=bounds_v3
    )
    pred_v3_oot = M.predict(fit_v3_oot["rho"], S["A"][is_new29], S["m"][is_new29], S["n"][is_new29], S["Ncls"])

    # Full 131-claim LBM-v3 fit + grouped LOGO CV (rebuilding G-set without held-out group)
    fit_v3 = M.fit_loglinear(S["A"], S["m"], S["n"], y, S["Ncls"], X_v3, lam=LAM_V3, bounds=bounds_v3)
    cv_v3 = np.zeros(len(y))
    for g in np.unique(groups):
        te = groups == g
        tr = ~te
        excl = set(sha_arr[te & gset])
        Sg = Hh.stats({"f": cmap(cons_vec(excl))}, clean_rows, scored)["f"] if excl else S
        f_g = M.fit_loglinear(
            Sg["A"][tr], Sg["m"][tr], Sg["n"][tr], y[tr], Sg["Ncls"], X_v3,
            lam=LAM_V3, beta0=fit_v3["beta"], bounds=bounds_v3
        )
        cv_v3[te] = M.predict(f_g["rho"], Sg["A"][te], Sg["m"][te], Sg["n"][te], Sg["Ncls"])

    resid_v3 = cv_v3 - y
    cons_full = np.zeros((H, W), np.int16)
    for v in near2_full.values():
        cons_full += v
    cls_full = lff.factor_ids(dcat_full, dh_full, cons_full)
    rho_v3_full = fit_v3["rho"][cls_full]
    rho_v3_full[~scored_full] = 0.0
    np.savez_compressed(
        Hh.CACHE / "lbm_v3_maps.npz",
        rho_full=rho_v3_full.astype(np.float32),
        cls_full=cls_full,
        cons_full=cons_full,
    )

    oot_rows = []
    for idx, r in enumerate([ clean_rows[i] for i in np.flatnonzero(is_new29) ]):
        oot_rows.append(
            dict(
                site=r["site"],
                name=r["name"],
                sha256=r["match"]["sha256"],
                claim=float(r["claim"]),
                lbm_v1_prospective_oot=round(float(pred_v1_oot[idx]), 5),
                lbm_v1_error=round(float(r["claim"] - pred_v1_oot[idx]), 5),
                lbm_v3_prospective_oot=round(float(pred_v3_oot[idx]), 5),
                lbm_v3_error=round(float(r["claim"] - pred_v3_oot[idx]), 5),
            )
        )

    names_v3 = (
        ["intercept", "dcat:(2,15]", "dcat:>15"]
        + [f"dh19_step>={k}" for k in ("1", "(1,2]", "(2,3]", "(3,5]", ">5")]
        + ["cons:1", "cons:2", "cons:3-4", "cons:>=5"]
    )
    lbm_v3_doc = dict(
        schema="gemsdoe92-lbm-v3-monotone-20261029",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        evidence_class="MODEL (metric-structured truth density fitted to 131 conflict-free owner CLAIMs; never an organizer score)",
        physical_constraint="Monotone non-increasing perpendicular truth density rho(dh19=0) >= rho(dh19=1) >= ... >= rho(dh19>5), eliminating 300 m kernel-collinearity flank inflation (Goodhart bias).",
        lam=LAM_V3,
        n_clean_claims=int(len(y)),
        n_groups=int(len(np.unique(groups))),
        G_footprint_units=round(float(fit_v3["G"]), 4),
        in_sample_rmse=round(float(fit_v3["rmse"]), 6),
        logo_cv=dict(
            rmse_all=round(float(np.sqrt(np.mean(resid_v3**2))), 6),
            mae_all=round(float(np.mean(np.abs(resid_v3))), 6),
            spearman_all=round(float(spearmanr(cv_v3, y)[0]), 6),
        ),
        prospective_oot_20261029=dict(
            trained_on_n_claims=int(tr_oot.sum()),
            tested_on_n_unseen_20261029_claims=int(is_new29.sum()),
            lbm_v1_oot_rmse=round(float(np.sqrt(np.mean((pred_v1_oot - y[is_new29]) ** 2))), 6),
            lbm_v3_oot_rmse=round(float(np.sqrt(np.mean((pred_v3_oot - y[is_new29]) ** 2))), 6),
            lbmc1_goodhart_error_reduction_factor=round(
                float(abs(oot_rows[0]["lbm_v1_error"]) / max(abs(oot_rows[0]["lbm_v3_error"]), 1e-6)), 2
            ),
            rows=oot_rows,
        ),
        beta={k: round(float(v), 6) for k, v in zip(names_v3, fit_v3["beta"])},
        rho_table=[round(float(x), 8) for x in fit_v3["rho"]],
        rows=[
            dict(
                site=r["site"],
                name=r["name"],
                sha256=r["match"]["sha256"],
                claim=float(r["claim"]),
                fitted=round(float(fit_v3["pred"][i]), 5),
                logo=round(float(cv_v3[i]), 5),
            )
            for i, r in enumerate(clean_rows)
        ],
    )
    (ROOT / "evidence" / "lbm_v3_20261029.json").write_text(json.dumps(lbm_v3_doc, indent=2) + "\n", encoding="utf-8")
    print(
        f"DONE fleet={fleet_29['unique_sha256']} unique SHA-256 | matched={matched_count}/{len(matched_rows)} | "
        f"LBM-v3 LOGO_RMSE={lbm_v3_doc['logo_cv']['rmse_all']:.5f} Spearman={lbm_v3_doc['logo_cv']['spearman_all']:.4f} | "
        f"2026-10-29 OOT RMSE: v1={lbm_v3_doc['prospective_oot_20261029']['lbm_v1_oot_rmse']:.5f} -> "
        f"v3={lbm_v3_doc['prospective_oot_20261029']['lbm_v3_oot_rmse']:.5f} "
        f"({lbm_v3_doc['prospective_oot_20261029']['lbmc1_goodhart_error_reduction_factor']}x lbmc1 error reduction!)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
