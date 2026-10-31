#!/usr/bin/env bash
# Fetch + verify the free official-source external feature stack for V-GFP.
#
#   bash scripts/fetch_external_stack.sh
#
# Clones buffedlizard55-lab/GEMSDOE24 (github.com allowlisted) into .cache/,
# copies data/external/ into data/external/ (gitignored), and verifies every
# file against registry/external_stack_manifest_20261031.json (fail-closed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MIRROR="$ROOT/.cache/GEMSDOE24"
DEST="$ROOT/data/external"
MANIFEST="$ROOT/registry/external_stack_manifest_20261031.json"

if [ ! -d "$MIRROR/.git" ]; then
  git clone --depth 1 https://github.com/buffedlizard55-lab/GEMSDOE24 "$MIRROR"
fi
mkdir -p "$DEST"
cp -r "$MIRROR/data/external/." "$DEST/"

python3 - "$DEST" "$MANIFEST" <<'EOF'
import hashlib, json, sys
from pathlib import Path
dest, manifest = Path(sys.argv[1]), Path(sys.argv[2])
m = json.loads(manifest.read_text())
bad = []
for f in m["files"]:
    p = dest / f["path"]
    if not p.is_file():
        bad.append(f"MISSING {f['path']}"); continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != f["sha256"]:
        bad.append(f"HASH-MISMATCH {f['path']} got {h}")
if bad:
    print("FAIL-CLOSED external stack verification:")
    print("\n".join(bad))
    raise SystemExit(1)
print(f"OK: {len(m['files'])} external files verified in {dest}")
EOF
