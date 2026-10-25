#!/usr/bin/env python3
"""ALI lane, step D: physics-only dot placement + leaderboard-calibrated projection.

Placement uses ONLY the out-of-fold Fault-Appearance Model (FAM) and the
catalogue-distance exclusion; no prior submission enters the placement.
Non-maximum suppression in FAM order with a minimum dot separation.
Projection: E[DTI] under the fitted latent intensity lam (model D+F+H of
scripts/ali_fit.py), reported as MODEL with a jackknife (leave-one-out refits)
paired difference against R0 (h33-h33-2-b2) under the same model.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / ".cache" / "work"
sys.path.insert(0, str(ROOT / "scripts"))
from ali_features import safe_load  # noqa: E402
from ali_design import K7  # noqa: E402
import ali_fit  # noqa: E402


def base_maps():
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as ds:
        cat = ds.read(1) == 1
    idx = np.flatnonzero(foot.ravel())
    fam = np.zeros(foot.shape, np.float32)
    fam.ravel()[idx] = safe_load(W / "fam" / "fam_full.npy", json.load(open(W / "fam" / "fam_full.json"))["sha256"])
    dcat = ndimage.distance_transform_edt(~cat).astype(np.float32)
    return foot, cat, fam, dcat


def nms_dots(score, cand, sep, k_max):
    """Greedy NMS: highest score first; reject a pixel closer than `sep` px to an accepted dot."""
    H, Wd = score.shape
    flat = np.flatnonzero(cand.ravel())
    order = flat[np.argsort(-score.ravel()[flat], kind="stable")]
    r = int(np.ceil(sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < sep * sep
    occ = np.zeros((H + 2 * r, Wd + 2 * r), bool)
    out = np.zeros((H, Wd), bool)
    n = 0
    for f in order:
        y, x = divmod(int(f), Wd)
        if occ[y + r, x + r]:
            continue
        out[y, x] = True
        occ[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
        n += 1
        if n >= k_max:
            break
    return out


class Projector:
    def __init__(self, spec=("D", "F", "H")):
        self.d, self.pts = ali_fit.load()
        self.meta, self.nb, self.N = self.d["meta"], self.d["n_strata"], np.array(self.d["N"])
        self.Z, self.names = ali_fit.make_model(self.meta, self.nb, list(spec))
        fitd = json.load(open(W / "ali_fit.json"))["models"]["+".join(spec)]
        self.theta = np.array(fitd["theta"])
        self.sid = safe_load(W / "ali_sid.npy")
        self.m = self.sid >= 0

    def lam_map(self, theta=None):
        th = self.theta if theta is None else theta
        lam_b = np.exp(self.Z @ th)
        lam = np.zeros(self.sid.shape, np.float64)
        lam[self.m] = lam_b[self.sid[self.m]]
        return lam

    def components(self, dots):
        """Per-stratum A (coverage) and B (kernel mass) vectors for a binary dot set on the scored domain."""
        p = (dots & self.m).astype(np.float32)
        d = ndimage.distance_transform_edt(~(p > 0))
        c = np.clip(1.0 - d / 3.0, 0, None)
        kd = ndimage.convolve(p, K7, mode="constant")
        A = np.bincount(self.sid[self.m], weights=c[self.m], minlength=self.nb)
        B = np.bincount(self.sid[self.m], weights=kd[self.m], minlength=self.nb)
        return dict(A=A, B=B, S=float(p.sum()))

    def dti(self, comp, theta=None):
        th = self.theta if theta is None else theta
        lam = np.exp(self.Z @ th)
        T = comp["A"] @ lam; G = self.N @ lam; M = min((comp["B"] @ lam) / 3.0, comp["S"])
        return float(T / (T + 0.2 * (comp["S"] - M) + 0.8 * (G - T)))
