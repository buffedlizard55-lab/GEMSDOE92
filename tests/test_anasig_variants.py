"""Algorithmic tests for the ANASIG lane surface (synthetic fields)."""
from __future__ import annotations
import numpy as np
from gems.anasig import analytic_signal_magnitude, lane_surface

def test_analytic_signal_peaks_over_a_contact():
    yy, xx = np.mgrid[0:60, 0:60]
    tmi = (10.0 / (1.0 + np.exp(-(xx - 30) / 1.5))).astype(np.float32)
    gy, gx = np.gradient(tmi)
    hg, vg = gx.astype(np.float32), gy.astype(np.float32)
    valid = np.ones_like(tmi, bool)
    a = analytic_signal_magnitude(hg, vg, valid)
    assert a[:, 28:33].mean() > a[:, 0:8].mean()
    surf = lane_surface(hg, vg, tmi, valid)
    for k in ("A_pct", "coherence", "S_raw", "S_pct"):
        assert surf[k].min() >= 0.0 and surf[k].max() <= 1.0
    assert surf["S_pct"][:, 27:34].mean() > surf["S_pct"][:, 0:10].mean()
