#!/usr/bin/env python
"""
Format-check the KNICKLOQO research GeoTIFF only.

This script does NOT assess uniqueness, scientific promotion, weekly-slot eligibility,
or organizer acceptance. Passing format gates must never be described as submission clearance.
"""

import sys
import os
import numpy as np
import rasterio
import hashlib

# Add vendor to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))
from gems57 import validate

# Add local gems to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gems'))
from gems import gates

def main():
    # File to validate
    file_path = 'docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif'

    print("=" * 80)
    print("RESEARCH TIFF FORMAT VALIDATION (NOT ELIGIBILITY)")
    print("=" * 80)
    print()

    # Check file exists
    if not os.path.exists(file_path):
        print(f"❌ FAIL: File not found: {file_path}")
        return False

    print(f"✓ File exists: {file_path}")
    print()

    # Load file
    try:
        with rasterio.open(file_path) as src:
            data = src.read(1)
            profile = src.profile

        print("✓ File loaded successfully")
    except Exception as e:
        print(f"❌ FAIL: Could not load file: {e}")
        return False

    # Check shape
    expected_height = 3730
    expected_width = 3292
    if data.shape != (expected_height, expected_width):
        print(f"❌ FAIL: Shape mismatch. Expected ({expected_height}, {expected_width}), got {data.shape}")
        return False
    print(f"✓ Shape: {data.shape} ({expected_height} height × {expected_width} width)")

    # Check CRS
    expected_crs = 'EPSG:32611'
    if str(profile['crs']) != expected_crs:
        print(f"❌ FAIL: CRS mismatch. Expected {expected_crs}, got {profile['crs']}")
        return False
    print(f"✓ CRS: {profile['crs']}")

    # Check dtype
    if profile['dtype'] != 'float32':
        print(f"❌ FAIL: Dtype mismatch. Expected float32, got {profile['dtype']}")
        return False
    print(f"✓ Dtype: {profile['dtype']}")

    # Check transform
    expected_transform = rasterio.Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
    if profile['transform'] != expected_transform:
        print(f"❌ FAIL: Transform mismatch")
        print(f"  Expected: {expected_transform}")
        print(f"  Got: {profile['transform']}")
        return False
    print(f"✓ Transform: matches sample_submission.tif")

    # Check values in [0, 1]
    if np.nanmin(data) < 0.0 or np.nanmax(data) > 1.0:
        print(f"❌ FAIL: Values out of range [0, 1]")
        print(f"  Min: {np.nanmin(data)}, Max: {np.nanmax(data)}")
        return False
    print(f"✓ Values in [0, 1]: min={np.min(data):.4f}, max={np.max(data):.4f}")

    # Check for NaN
    nan_count = np.isnan(data).sum()
    if nan_count > 0:
        print(f"❌ FAIL: Found {nan_count} NaN values")
        return False
    print(f"✓ No NaN values")

    # Check for Inf
    inf_count = np.isinf(data).sum()
    if inf_count > 0:
        print(f"❌ FAIL: Found {inf_count} Inf values")
        return False
    print(f"✓ No Inf values")

    # Check all values are finite
    finite_count = np.isfinite(data).sum()
    if finite_count != data.size:
        print(f"❌ FAIL: Not all values are finite")
        return False
    print(f"✓ All values finite")

    # Check zeros outside footprint
    sample_path = 'data/bridge/sample_submission.tif'
    if os.path.exists(sample_path):
        with rasterio.open(sample_path) as src:
            sample = src.read(1)
            # Footprint is where sample is not NaN (5,167,373 pixels)
            footprint = ~np.isnan(sample)
            outside_footprint = ~footprint

        values_outside = data[outside_footprint]
        if not np.all(values_outside == 0.0):
            print(f"❌ FAIL: Non-zero values outside footprint")
            print(f"  Non-zero count: {np.sum(values_outside > 0)}")
            return False
        print(f"✓ Zeros outside footprint (USGS survey area)")
    else:
        print(f"❌ FAIL: Could not check zeros outside footprint (sample not found)")
        return False

    # Count dots
    dot_count = np.sum(data > 0)
    print(f"✓ Dot count: {dot_count} unit-mass dots")

    # Check catalogue mass
    print("✓ Positive cell count reported; this is not a catalogue-distance calculation")

    # Compute SHA-256
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    expected_hash = '8ad4a8c2cd8e1fd989b63c752d5e9efc4ba87a2f608ccd551e8787648920d347'
    if file_hash != expected_hash:
        print(f"❌ FAIL: SHA-256 mismatch")
        print(f"  Expected: {expected_hash}")
        print(f"  Got: {file_hash}")
        return False
    print(f"✓ SHA-256: {file_hash}")

    # Run gems57 validation
    print()
    print("Running gems57 validation...")
    try:
        results = validate.validate(file_path)
        if results.get('all_checks_passed', False):
            print(f"✓ gems57 validation: ALL CHECKS PASSED")
            # Print some details
            checks = results.get('checks', {})
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")
        else:
            print(f"❌ FAIL: gems57 validation: some checks failed")
            print(f"  Results: {results}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Could not run gems57 validation: {e}")
        return False

    # Run gems.gates (local gems module)
    print()
    print("Running gems.gates (local module)...")
    try:
        gate_results = gates.run_gates(
            file_path,
            'data/bridge/sample_submission.tif',
            require_submission_encoding=True,
        )
        passed = sum(result.ok for result in gate_results)
        total = len(gate_results)
        for result in gate_results:
            print(f"  {result}")
        if passed == total and total > 0:
            print(f"✓ gems.gates: {passed}/{total} PASSED")
        else:
            print(f"❌ FAIL: gems.gates: {passed}/{total} PASSED")
            return False
    except Exception as e:
        print(f"❌ FAIL: Could not run gems.gates: {e}")
        return False

    print()
    print("=" * 80)
    print("✅ FORMAT CHECKS PASSED — THIS IS NOT SUBMISSION CLEARANCE")
    print("=" * 80)
    print()
    print("This script verifies format gates only; it does NOT check registry uniqueness or submission eligibility.")
    print("Do not submit unless a separate current audit explicitly records submission_eligible: true.")
    print()

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
