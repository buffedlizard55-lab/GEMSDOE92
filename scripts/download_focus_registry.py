#!/usr/bin/env python3
"""Download the 9 focus-site best-claim TIFFs into a focused uniqueness registry.
Raw GitHub URLs (github.com is an allowed host). One HTTP request per TIFF (~100-400 KB).
"""
from __future__ import annotations

import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".cache" / "focus_registry"
OUT.mkdir(parents=True, exist_ok=True)

# site -> (repo, branch, filename) extracted from docs/index.html blob URLs
SITES = {
    "GEMSDOE24": ("buffedlizard55-lab/GEMSDOE24", "fdd41b075a05e7df5b222e6e3644344cecc65746",
                  "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif"),
    "GEMSDOE25": ("buffedlizard55-lab/GEMSDOE25", "cd2560d6a7fc2bc2c2f343d0a6b2a506ce6ea4ca",
                  "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"),
    "GEMSDOE27": ("buffedlizard55-lab/GEMSDOE27", "50174df50f7fd8b681308a56f97f41ac21755b85",
                  "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif"),
    "GEMSDOE28": ("buffedlizard55-lab/GEMSDOE28", "245217303f58b900650e3645f64b26133284ab84",
                  "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif"),
    "GEMSDOE30": ("buffedlizard55-lab/GEMSDOE30", "3344c38758a1379f9f7d69b4ef86cb4d7176935a",
                  "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif"),
    "GEMSDOE31": ("buffedlizard55-lab/GEMSDOE31", "dad99f59ef8a023052451f7b7cf205d263b1f2ab",
                  "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"),
    "GEMSDOE32": ("buffedlizard55-lab/GEMSDOE32", "9d63e2b1f9154816f9292e15fd257681bfe1bc22",
                  "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"),
    "GEMSDOE33": ("buffedlizard55-lab/GEMSDOE33", "1e08a7e81ee4595e2f3770f5c4f7c071adc1a53e",
                  "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif"),
    "GEMSDOE36": ("buffedlizard55-lab/GEMSDOE36", "4b717aaff6eaf5de9b53030e637f8e1cf0d56e43",
                  "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"),
}

SCORES = {
    "GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449, "GEMSDOE28": 0.2710,
    "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708, "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632,
    "GEMSDOE36": 0.2750,
}

manifest = {}
for site, (repo, branch, fname) in SITES.items():
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/docs/downloads/{fname}"
    dest = OUT / fname
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        dest.write_bytes(data)
        manifest[site] = dict(file=fname, repo=repo, branch=branch, url=url,
                              bytes=len(data), claim=SCORES[site], dest=str(dest))
        print(f"OK  {site}: {len(data)/1024:.0f} KB -> {fname}  (claim {SCORES[site]})")
    except Exception as exc:  # noqa: BLE001
        manifest[site] = dict(file=fname, error=str(exc), claim=SCORES[site])
        print(f"FAIL {site}: {exc}")

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
print("wrote", OUT / "manifest.json")
