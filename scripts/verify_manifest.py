import json, hashlib, pathlib
manifest_path = pathlib.Path("registry/data_manifest.json")
data = json.loads(manifest_path.read_text())
ok = True
for entry in data["files"]:
    dest = pathlib.Path(entry["dest"])
    if not dest.exists():
        print(f"MISSING {dest}")
        ok=False
        continue
    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    exp = entry["sha256"]
    if sha != exp:
        print(f"HASH MISMATCH {dest}: got {sha} expected {exp}")
        ok=False
    else:
        print(f"OK {dest} {sha[:16]}")
if ok:
    print("All hashes verified")
else:
    print("Some hashes failed")
    exit(1)
