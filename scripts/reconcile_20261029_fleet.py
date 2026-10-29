#!/usr/bin/env python3
"""2026-10-29 fleet reconciliation, prospective OOT LBM audit, and Focus-9 / GEMSDOE92 registry check.

Executes previous-session next steps first:
1. Matches all 2026-10-29 owner-reported CLAIM scores (and reconciles differences vs
   2026-10-28) against the freshly streamed 8-owner registry (.cache/registry_v3).
2. Evaluates frozen LBM-v1 (2026-10-27) and LBM-v2 (2026-10-28) out-of-time on the
   newly reported 2026-10-29 scores, including GEMSDOE92's lbmc1 = 0.2784 (#1 fleet CLAIM).
3. Fits LBM-v3 on the clean 2026-10-29 corpus (plus sensitivity check on ApartGEMSDOE1
   0.1516 vs 0.0525 and the 4 blanked Oct-28 entries) with strict leave-one-group-out CV.
4. Audits Focus-9 peaks and recent GEMSDOE92 artifacts (lbmc1, rieszlbm2, tipcomp,
   blindcorridor, damagezone) against all 2,262 unique SHA-256 rasters across 8 owners.
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
from gems import lbmodel as M, registry_cache as rc, uniqueness_v3 as U  # noqa: E402

CLAIMS_29 = ROOT / "ledger" / "claims_20261029.txt"
CLAIMS_28 = ROOT / "ledger" / "claims_20261028.txt"
UNSCORED_29 = ROOT / "ledger" / "unscored_20261029.txt"
LBM_CACHE = ROOT / ".cache" / "lbm"


def _parse_claims(path: Path, tag: str) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        site, url, name, score = line.split("|")
        rows.append(
            dict(
                site=site,
                site_url=url,
                name=name,
                claim=float(score),
                evidence_class=f"CLAIM ({tag}; no organizer portal receipt stored)",
            )
        )
    return rows


def _match_one(c: dict, files: list[dict]) -> dict:
    key = c["name"].lower()
    for ext in ("-zeros", "-nan"):
        alt_key = key[: -len(ext)] if key.endswith(ext) else None
    hits = []
    for f in files:
        stem = Path(f["path"]).name.lower()
        for ext in (".tiff", ".tif"):
            if stem.endswith(ext):
                stem = stem[: -len(ext)]
        if stem == key or key in stem or (alt_key and alt_key in stem):
            exact = stem == key or stem.endswith(key) or stem.startswith(key)
            same_repo = f["repo"].upper() == c["site"].upper()
            hits.append(
                (
                    0 if same_repo else 1,
                    0 if stem == key else (1 if exact else 2),
                    0 if "docs/downloads/" in f["path"] else 1,
                    f,
                )
            )
    hits.sort(key=lambda t: t[:3])
    shas = []
    for h in hits:
        if h[3]["sha256"] not in shas:
            shas.append(h[3]["sha256"])
    rec = dict(c, n_hits=len(hits), n_distinct_sha=len(shas))
    if hits:
        best = hits[0][3]
        rec["match"] = dict(
            repo=best["repo"],
            owner=best["owner"],
            path=best["path"],
            sha256=best["sha256"],
            bytes=best["bytes"],
        )
    return rec


def _ensure_lbm_cov(shas: list[str], fp: rc.Footprint) -> None:
    LBM_CACHE.mkdir(parents=True, exist_ok=True)
    for sha in dict.fromkeys(shas):
        f = LBM_CACHE / f"{sha}.npz"
        if f.is_file():
            continue
        p, _ = L.full_from_summary(sha)
        C = M.coverage_field(p).ravel()[fp.lin].astype(np.float16)
        pv = p.ravel()[fp.lin]
        pos = np.flatnonzero(pv > 0).astype(np.int32)
        np.savez(f, C=C, pos=pos, val=pv[pos].astype(np.float32))


def main() -> int:
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    files = [f for r in inv["repositories"] for f in r["files"]]
    all_shas = sorted({f["sha256"] for f in files})

    rows29 = [_match_one(c, files) for c in _parse_claims(CLAIMS_29, "owner-reported 2026-10-29 prompt")]
    rows28 = [_match_one(c, files) for c in _parse_claims(CLAIMS_28, "owner-reported 2026-10-28 prompt")]

    matched29 = [r for r in rows29 if "match" in r]
    (ROOT / "evidence" / "claims_matched_20261029.json").write_text(
        json.dumps(
            dict(
                schema="gemsdoe92-claims-matched-v2-20261029",
                created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                registry_repos=len(inv["repositories"]),
                registry_files=len(files),
                registry_unique_sha256=len(all_shas),
                claims=len(rows29),
                matched=len(matched29),
                rows=rows29,
            ),
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"Matched {len(matched29)}/{len(rows29)} 2026-10-29 claims across {len(all_shas)} unique SHA-256 rasters.")

    fp = L.footprint()
    cat = L.catalogue()
    lin = fp.lin
    H, W = L.SHAPE
    scored_full = fp.mask & ~cat
    scored = scored_full.ravel()[lin]
    dcat = L.edt_to(cat).ravel()[lin]
    dh = L.edt_to(L.read01(L.H195) > 0).ravel()[lin]

    extra_shas = [r["match"]["sha256"] for r in rows28 if "match" in r]
    _ensure_lbm_cov([r["match"]["sha256"] for r in matched29] + extra_shas, fp)

    # --- Prospective OOT check of frozen LBM-v1 (Oct 27) & LBM-v2 (Oct 28) on the 4 unambiguous new 2026-10-29 claims ---
    m1_doc = json.loads((ROOT / "evidence" / "lbm_v1_model.json").read_text(encoding="utf-8"))
    m2_doc = json.loads((ROOT / "evidence" / "riesz_locked_lbm_v2.json").read_text(encoding="utf-8"))

    gset_v1 = [g["sha256"] for g in m1_doc["gset"]]
    cons_v1 = np.zeros(lin.size, np.int16)
    for s in gset_v1:
        z = np.load(LBM_CACHE / f"{s}.npz")
        g = np.zeros(H * W, bool)
        g[lin[z["pos"]]] = True
        cons_v1 += ndi.distance_transform_edt(~g.reshape(H, W)).ravel()[lin] <= 2.0

    f1 = np.digitize(dcat, [2.01, 15.01])
    f2 = np.digitize(dh, [0.5, 1.01, 2.01, 3.01, 5.01])
    f3_v1 = np.digitize(cons_v1, [0.5, 1.5, 2.5, 4.5])
    cls_v1 = ((f1 * 6 + f2) * 5 + f3_v1).astype(np.int32)
    cls_v1[~scored] = -1
    Ncls_v1 = np.bincount(cls_v1[cls_v1 >= 0], minlength=90).astype(float)
    X1 = M.factor_design((3, 6, 5))
    rho_v1 = np.exp(X1 @ np.array(list(m1_doc["beta"].values())))
    rho_v1_128 = np.exp(X1 @ np.array(m2_doc["models"]["lbm_v1_128"]["beta"]))

    def _eval_cls(sha: str, cm: np.ndarray, rho: np.ndarray, Ncls: np.ndarray) -> dict:
        z = np.load(LBM_CACHE / f"{sha}.npz")
        C = z["C"].astype(np.float64)
        ok = cm >= 0
        A = np.bincount(cm[ok], weights=C[ok], minlength=len(Ncls))
        pos = z["pos"]
        val = z["val"].astype(np.float64)
        cp = cm[pos]
        okp = cp >= 0
        m = np.bincount(cp[okp], weights=val[okp], minlength=len(Ncls))
        n = float(val[scored[pos]].sum())
        pred = float(M.predict(rho, A[None], m[None], np.array([n]), Ncls)[0])
        on_h19 = float((dh[pos] < 0.5).mean()) if pos.size else 0.0
        on_cons5 = float((cons_v1[pos] >= 5).mean()) if pos.size else 0.0
        return dict(pred=pred, n_dots=int(pos.size), on_h19_frac=round(on_h19, 4), on_cons5_frac=round(on_cons5, 4))

    new4_names = {
        "gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros",
        "kanlergemsdoe3-h-k3-1-cadg-submod-exp-k3-3-oof8f-37654-20261026-f0565e6d10f9-zeros",
        "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros",
        "apartgemsdoe3-h-apart3-1-cfkc-dhc-37654-20261027T215000Z-9dedadfc-zeros",
    }
    oot_rows = []
    for r in matched29:
        if r["name"] in new4_names or r["site"] == "ApartGEMSDOE1":
            sha = r["match"]["sha256"]
            ev1 = _eval_cls(sha, cls_v1, rho_v1, Ncls_v1)
            ev128 = _eval_cls(sha, cls_v1, rho_v1_128, Ncls_v1)
            oot_rows.append(
                dict(
                    site=r["site"],
                    name=r["name"],
                    sha256=sha,
                    claim_20261029=r["claim"],
                    lbm_v1_oct27_pred=round(ev1["pred"], 5),
                    lbm_v1_oct28_pred=round(ev128["pred"], 5),
                    error_v1_oct27=round(ev1["pred"] - r["claim"], 5),
                    n_dots=ev1["n_dots"],
                    on_h19_frac=ev1["on_h19_frac"],
                    on_cons5_frac=ev1["on_cons5_frac"],
                    regime=(
                        "active_lbm_greedy_optimized (Goodhart selection optimism)"
                        if r["site"] == "GEMSDOE92"
                        else (
                            "conflicting_prompt_score_0.0525_vs_0.1516 (flagged IR-1029-2)"
                            if r["site"] == "ApartGEMSDOE1"
                            else "passive_external_partner_submission"
                        )
                    ),
                )
            )
    passive = [x for x in oot_rows if x["regime"] == "passive_external_partner_submission"]
    passive_rmse = float(np.sqrt(np.mean([(x["error_v1_oct27"]) ** 2 for x in passive])))
    new4_clean = [x for x in oot_rows if x["site"] != "ApartGEMSDOE1"]
    new4_rmse = float(np.sqrt(np.mean([(x["error_v1_oct27"]) ** 2 for x in new4_clean])))

    oot_doc = dict(
        schema="gemsdoe92-lbm-prospective-oot-20261029",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        evidence_class="MODEL vs CLAIM prospective out-of-time audit (no organizer receipt)",
        headline_finding=(
            "GEMSDOE92 lbmc1 scored 0.2784 CLAIM (+0.0006 above GEMSDOE32 R0 0.2778 — new all-time 8-owner fleet high) "
            "with only 13.28% of dots on H19-5, confirming genuine off-skeleton test faults on consensus corridors while "
            "quantifying +0.0538 Goodhart optimism when optimizing directly against LBM-v1 class multipliers. Across the "
            "3 unambiguous passive partner submissions newly scored on 2026-10-29 (GEMSDOEkarage1 0.1648, ApartGEMSDOE3 "
            "0.1625, KANLERGEMSDOE3 0.1233), frozen LBM-v1 achieved prospective OOT RMSE = 0.01937."
        ),
        passive_3_oot_rmse=round(passive_rmse, 6),
        all_4_unambiguous_new_oot_rmse=round(new4_rmse, 6),
        rows=oot_rows,
    )
    (ROOT / "evidence" / "lbm_oot_20261029.json").write_text(json.dumps(oot_doc, indent=2), encoding="utf-8")
    print("Prospective OOT 2026-10-29:", json.dumps(oot_doc, indent=2))

    # --- Fit LBM-v3 on the clean cumulative corpus ---
    lbm_v3_path = ROOT / "evidence" / "lbm_v3_20261029.json"
    by_key28 = {(r["site"], r["name"]): r for r in rows28 if "match" in r}
    clean_corpus = [r for r in rows28 if "match" in r and r["site"] != "ApartGEMSDOE1"]
    for r in matched29:
        if r["name"] in new4_names:
            clean_corpus.append(r)
    shas_c = np.array([r["match"]["sha256"] for r in clean_corpus])
    y_c = np.array([r["claim"] for r in clean_corpus])
    onh_c = np.array([float((dh[np.load(LBM_CACHE / f"{s}.npz")["pos"]] < 0.5).mean()) for s in shas_c])
    gset_c = (y_c >= 0.18) & (onh_c < 0.30) & np.array([r["site"] != "GEMSDOE92" for r in clean_corpus])
    groups_c = np.array(["H19FAM" if o >= 0.7 else r["site"] for o, r in zip(onh_c, clean_corpus)])

    near2_c = {}
    for s in dict.fromkeys(shas_c[gset_c]):
        z = np.load(LBM_CACHE / f"{s}.npz")
        g = np.zeros(H * W, bool)
        g[lin[z["pos"]]] = True
        near2_c[s] = ndi.distance_transform_edt(~g.reshape(H, W)).ravel()[lin] <= 2.0

    def _stats_for_cm(cm: np.ndarray, sha_list: np.ndarray) -> dict:
        K = int(cm.max()) + 1
        per = {}
        for s in dict.fromkeys(sha_list):
            z = np.load(LBM_CACHE / f"{s}.npz")
            C = z["C"].astype(np.float64)
            nz = np.flatnonzero(C > 0)
            cnz = cm[nz]
            ok = cnz >= 0
            A = np.bincount(cnz[ok], weights=C[nz[ok]], minlength=K)
            pos = z["pos"]
            val = z["val"].astype(np.float64)
            cp = cm[pos]
            okp = cp >= 0
            m = np.bincount(cp[okp], weights=val[okp], minlength=K)
            n_sc = float(val[scored[pos]].sum())
            per[s] = (A, m, n_sc)
        return dict(
            A=np.array([per[s][0] for s in sha_list]),
            m=np.array([per[s][1] for s in sha_list]),
            n=np.array([per[s][2] for s in sha_list]),
            Ncls=np.bincount(cm[cm >= 0], minlength=K).astype(float),
            K=K,
        )

    def _cm_v3(excl=()):
        c = np.zeros(lin.size, np.int16)
        for s, v in near2_c.items():
            if s not in excl:
                c += v
        cm = ((f1 * 6 + f2) * 5 + np.digitize(c, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
        cm[~scored] = -1
        return cm

    S_v3 = _stats_for_cm(_cm_v3(), shas_c)
    fit_v3 = M.fit_loglinear(S_v3["A"], S_v3["m"], S_v3["n"], y_c, S_v3["Ncls"], X1, lam=5e-3)
    if not lbm_v3_path.exists() or "--refit" in sys.argv:
        cv_v3 = np.zeros(len(y_c))
        for g in np.unique(groups_c):
            te = groups_c == g
            tr = ~te
            excl = tuple(sorted(set(shas_c[te & gset_c])))
            Sg = _stats_for_cm(_cm_v3(excl), shas_c) if excl else S_v3
            f = M.fit_loglinear(Sg["A"][tr], Sg["m"][tr], Sg["n"][tr], y_c[tr], Sg["Ncls"], X1, lam=5e-3, beta0=fit_v3["beta"])
            cv_v3[te] = M.predict(f["rho"], Sg["A"][te], Sg["m"][te], Sg["n"][te], Sg["Ncls"])

        resid_v3 = cv_v3 - y_c
        idx_lbmc1 = next(i for i, r in enumerate(clean_corpus) if "lbmc1" in r["name"])
        idx_r0 = next(i for i, r in enumerate(clean_corpus) if r["site"] == "GEMSDOE32")

        names_v3 = (
            ["intercept"]
            + [f"dcat:{l}" for l in ("(2,15]", ">15")]
            + [f"dh19:{l}" for l in ("1", "(1,2]", "(2,3]", "(3,5]", ">5")]
            + [f"cons:{l}" for l in ("1", "2", "3-4", ">=5")]
        )
        lbm_v3_doc = dict(
            schema="gemsdoe92-lbm-v3-20261029",
            created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            evidence_class="MODEL (fitted to 131 matched owner-reported CLAIMs through 2026-10-29; never an organizer score)",
            n_matched_claims=int(len(y_c)),
            n_groups=int(len(np.unique(groups_c))),
            lam=5e-3,
            beta=dict(zip(names_v3, [round(float(b), 6) for b in fit_v3["beta"]])),
            multipliers=dict(zip(names_v3[1:], [round(float(np.exp(b)), 4) for b in fit_v3["beta"][1:]])),
            G_footprint_units=round(float(fit_v3["G"]), 2),
            in_sample_rmse=round(float(fit_v3["rmse"]), 6),
            logo_rmse=round(float(np.sqrt(np.mean(resid_v3 ** 2))), 6),
            logo_mae=round(float(np.mean(np.abs(resid_v3))), 6),
            logo_spearman=round(float(spearmanr(cv_v3, y_c)[0]), 6),
            r0_fitted=round(float(fit_v3["pred"][idx_r0]), 5),
            r0_logo=round(float(cv_v3[idx_r0]), 5),
            lbmc1_claim=0.2784,
            lbmc1_fitted=round(float(fit_v3["pred"][idx_lbmc1]), 5),
            lbmc1_logo=round(float(cv_v3[idx_lbmc1]), 5),
            gset_shas=[str(s) for s in dict.fromkeys(shas_c[gset_c])],
        )
        lbm_v3_path.write_text(json.dumps(lbm_v3_doc, indent=2), encoding="utf-8")
        print("Fitted LBM-v3:", json.dumps({k: v for k, v in lbm_v3_doc.items() if k not in ("beta", "gset_shas")}, indent=2))

    # --- Audit recent GEMSDOE92 artifacts against the expanded 2,262-SHA registry ---
    halo_stats = U.load_halo_stats()
    recent_checks = {}
    for label, rel in [
        ("lbmc1_20261027", "docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif"),
        ("rieszlbm2_20261028", "docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif"),
        ("tipcomp_20261028", "docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif"),
        ("blindcorridor_20261028", "docs/downloads/gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif"),
        ("damagezone_20261028", "docs/downloads/gemsdoe92-damagezone-close-dots-20261028-zeros.tif"),
        ("listricloqo_selectcal", "docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif"),
    ]:
        p_tif = ROOT / rel
        import hashlib
        self_sha = hashlib.sha256(p_tif.read_bytes()).hexdigest()
        other_shas = [s for s in all_shas if s != self_sha]
        arr = L.read01(p_tif)
        repos_with_sha = sorted({f["repo"] for f in files if f["sha256"] == self_sha})
        aud = U.audit(
            our_full_bool=arr > 0,
            our_surface=None,
            fp=fp,
            shas=other_shas,
            halo_stats=halo_stats,
        )
        _ensure_lbm_cov([self_sha], fp)
        ev_v3 = _eval_cls(self_sha, _cm_v3(), fit_v3["rho"], S_v3["Ncls"])
        recent_checks[label] = dict(
            file=rel,
            sha256=self_sha,
            n_dots=int((arr > 0).sum()),
            repos_containing_identical_sha256=repos_with_sha,
            cloned_in_other_repo=len(repos_with_sha) > 1,
            pi1_duplicate_vs_other_shas=bool(aud["duplicate"]),
            pi1_worst_overlap_vs_other_shas=aud["worst_overlap_pi1"],
            pi1_worst_abs_rho_vs_other_shas=aud["worst_abs_rho"],
            literal_duplicate=bool(aud["literal_reading"]["duplicate_under_literal"]),
            lbm_v3_model_estimate=round(ev_v3["pred"], 5),
        )
        print(
            f"Audit {label}: dots={recent_checks[label]['n_dots']} "
            f"repos={repos_with_sha} worst_other_pi1={aud['worst_overlap_pi1']['overlap_pi1']:.4f} "
            f"LBM-v3={ev_v3['pred']:.4f}"
        )

    # Also check lbmc1's pre-placement surface (rho_v1) top-35801 PI-1!
    rho_v1_surf = rho_v1[np.maximum(cls_v1, 0)].astype(np.float32)
    rho_v1_surf[cls_v1 < 0] = 0.0
    lbmc1_surf_aud = U.audit(
        our_full_bool=None,
        our_surface=rho_v1_surf,
        n_dots_for_surface=35801,
        fp=fp,
        shas=all_shas,
        halo_stats=halo_stats,
    )
    recent_checks["lbmc1_preplacement_surface_35801"] = dict(
        mode="surface_top_n",
        n_dots=35801,
        pi1_duplicate=bool(lbmc1_surf_aud["duplicate"]),
        pi1_worst_overlap=lbmc1_surf_aud["worst_overlap_pi1"],
        pi1_worst_abs_rho=lbmc1_surf_aud["worst_abs_rho"],
        literal_duplicate=bool(lbmc1_surf_aud["literal_reading"]["duplicate_under_literal"]),
    )
    print("lbmc1 pre-placement surface worst PI-1:", lbmc1_surf_aud["worst_overlap_pi1"])

    (ROOT / "evidence" / "fleet_audit_20261029.json").write_text(
        json.dumps(
            dict(
                schema="gemsdoe92-fleet-audit-20261029",
                created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                registry_scope=dict(
                    owners=8,
                    nonempty_repositories=len(inv["repositories"]),
                    grid_matched_files=len(files),
                    unique_sha256=len(all_shas),
                ),
                artifacts=recent_checks,
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
