#!/usr/bin/env python3
"""ALI lane, step F: build the deployment raster with the shared fail-closed writer.

Physics-only placement: quadrant-OOF FAM (full catalogue labels), candidates
d_cat > 3 px (300 m; scored pixels only), NMS separation 2.5 px, K = 37,654.
Binary {0,1} float32, zeros outside the footprint, no NaN anywhere.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor")); sys.path.insert(0, str(ROOT / "scripts"))
from gems57.submission_writer import write_submission  # noqa: E402
from gems57.validate import validate  # noqa: E402
from ali_place import base_maps, nms_dots  # noqa: E402

SEP, K, BUF = 2.5, 37654, 3.0
STAMP = "20261025T230000Z"


def main():
    foot, cat, fam, dcat = base_maps()
    dots = nms_dots(fam, foot & ~cat & (dcat > BUF), SEP, K)
    assert int(dots.sum()) == K, dots.sum()
    pred = dots.astype(np.float32)
    h8 = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
    name = f"gemsdoe92-ali-famnms-37654-{STAMP}-{h8}-zeros"
    note = "GEMSDOE92 ALI: OOF physics fault-appearance model, NMS 250 m, 37654 dots >300 m off-catalogue; holdout ties R0 recipe"
    assert len(name) <= 140 and len(note) <= 140, (len(name), len(note))
    out = ROOT / "docs" / "downloads" / f"{name}.tif"
    write_submission(out, pred, ROOT / "data/bridge/sample_submission.tif", foot, note=note, name=name, catalogue=cat,
                     metadata=dict(lane="ALI", sep_px=SEP, k=K, buffer_px=BUF, fam="quadrant-OOF HGB, full catalogue"))
    rec = validate(out, footprint=foot, catalogue=cat)
    json.dump(dict(name=name, note=note, note_chars=len(note), name_chars=len(name), validator=rec),
              open(ROOT / ".cache" / "work" / "ali_build.json", "w"), indent=1)
    print(name, len(note), rec["sha256"], rec["all_checks_passed"], rec["bytes"])


if __name__ == "__main__":
    main()
