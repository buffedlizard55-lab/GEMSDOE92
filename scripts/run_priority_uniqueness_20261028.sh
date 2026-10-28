#!/usr/bin/env bash
# Full-registry PI-1 audit for the priority candidates (2026-10-28).
# Each candidate is excluded only from its OWN repo's copy (see audit_candidate_registry.py).
set -u
cd "$(dirname "$0")/.."
PY="${PY:-python3}"
export PYTHONPATH=vendor
run() { # name, candidate path, own repo
  echo "== $1"
  "$PY" scripts/audit_candidate_registry.py --candidate "$2" --own-repo "$3" \
    --output "evidence/uniq_full_registry/$1.json" 2>&1 | grep -v -E "Warning|rho = float" | tail -2
}
run tipcomp-40000dots-8f27b9d6      docs/downloads/gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif buffedlizard55-lab/GEMSDOE92
run rieszlbm2-50000dots-79041788    docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif buffedlizard55-lab/GEMSDOE92
run lbmc1-35801dots-89a660f6       docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif buffedlizard55-lab/GEMSDOE92
run damagezone-close-dots-20261028 docs/downloads/gemsdoe92-damagezone-close-dots-20261028-zeros.tif buffedlizard55-lab/GEMSDOE92
run focus9-GEMSDOE24-68d0e2e4 .cache/focus9_verify/GEMSDOE24.tif buffedlizard55-lab/GEMSDOE24
run focus9-GEMSDOE25-91eae1ca .cache/focus9_verify/GEMSDOE25.tif buffedlizard55-lab/GEMSDOE25
run focus9-GEMSDOE27-33003374 .cache/focus9_verify/GEMSDOE27.tif buffedlizard55-lab/GEMSDOE27
run focus9-GEMSDOE28-5556aa14 .cache/focus9_verify/GEMSDOE28.tif buffedlizard55-lab/GEMSDOE28
run focus9-GEMSDOE30-8cf893ea .cache/focus9_verify/GEMSDOE30.tif buffedlizard55-lab/GEMSDOE30
run focus9-GEMSDOE31-07b6db44 .cache/focus9_verify/GEMSDOE31.tif buffedlizard55-lab/GEMSDOE31
run focus9-GEMSDOE32-c55bafc4 .cache/focus9_verify/GEMSDOE32.tif buffedlizard55-lab/GEMSDOE32
run focus9-GEMSDOE33-87f857d5 .cache/focus9_verify/GEMSDOE33.tif buffedlizard55-lab/GEMSDOE33
run focus9-GEMSDOE36-e1589102 .cache/focus9_verify/GEMSDOE36.tif buffedlizard55-lab/GEMSDOE36
run parent-R0-zeros-GEMSDOE32      data/parent_R0_zeros.tif buffedlizard55-lab/GEMSDOE32
