"""Verify pinned local inputs and rebuild R0 without producing candidates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'vendor'), str(ROOT / 'scripts')]
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from exact_dti_refill import dot_thin


def main():
    subprocess.run([sys.executable, 'scripts/verify_manifest.py'], cwd=ROOT, check=True)
    with rasterio.open(ROOT / 'data/bridge/sample_submission.tif') as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / 'data/bridge/existing_faults.tif') as ds:
        cat = (ds.read(1) > 0) & foot
        profile = ds.profile.copy()
    with rasterio.open(ROOT / 'data/bridge/h19_5.tif') as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0) > 0) & foot
    distance = distance_transform_edt(~cat)
    r0 = dot_thin(h19, 2.8) & (distance > 2)
    profile.update(driver='GTiff', dtype='float32', count=1, compress='deflate',
                   predictor=3, zlevel=9, tiled=True, blockxsize=256,
                   blockysize=256, nodata=None)
    pins = json.loads((ROOT / 'registry/parents/R0.json').read_text())['files']
    hashes = {}
    cache = ROOT / '.cache'
    cache.mkdir(exist_ok=True)
    for encoding in ('zeros', 'nan'):
        path = cache / f'r0-audit-{encoding}.tif'
        pr = profile.copy()
        if encoding == 'nan':
            pr.update(nodata=np.nan)
        arr = np.where(foot, r0.astype('float32'),
                       0.0 if encoding == 'zeros' else np.nan).astype('float32')
        with rasterio.open(path, 'w', **pr) as ds:
            ds.write(arr, 1)
        with rasterio.open(path) as ds:
            if not np.array_equal(ds.read(1), arr, equal_nan=True):
                raise RuntimeError('Disk reread mismatch')
        hashes[encoding] = hashlib.sha256(path.read_bytes()).hexdigest()
        if hashes[encoding] != pins[encoding]['sha256']:
            raise RuntimeError(f'R0 hash mismatch: {encoding}')
    report = dict(date='2026-10-24', axis='MASS', status='BLOCKED_NO_VARIANTS',
                  git_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  seed=0, manifest_hashes='8/8 PASS', rebuilt_sha256=hashes,
                  n_dots=int(r0.sum()), dots_lt3px=int((r0 & (distance < 3)).sum()),
                  catalogue_mass=int((r0 & cat).sum()),
                  blockers=['Parent ranking absent; binary H19-5 cannot rank dots.',
                            'R0 violates non-PRUNE >=3px exclusion.'])
    (ROOT / 'evidence/session_20261024.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
