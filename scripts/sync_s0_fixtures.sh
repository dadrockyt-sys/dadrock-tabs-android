#!/usr/bin/env bash
set -euo pipefail

# Sync private S0 fixture audio into this public repo's ignored s0_sources/ folder.
# Usage:
#   S0_FIXTURE_REPO=owner/private-repo ./scripts/sync_s0_fixtures.sh
# Optional:
#   S0_FIXTURE_REF=main
#
# Requires GitHub authentication already available to git in the environment.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ROOT}/s0_sources"
TMP="${ROOT}/.s0_fixture_repo"
REPO="${S0_FIXTURE_REPO:-}"
REF="${S0_FIXTURE_REF:-main}"

if [[ -z "${REPO}" ]]; then
  echo "Set S0_FIXTURE_REPO to owner/private-repo" >&2
  exit 2
fi

rm -rf "${TMP}"
mkdir -p "${DEST}"

git clone --depth 1 --branch "${REF}" "https://github.com/${REPO}.git" "${TMP}"

python3 - <<'PY'
from pathlib import Path
import hashlib, json, shutil, sys

root=Path.cwd()
tmp=root/".s0_fixture_repo"
dest=root/"s0_sources"
manifest_path=tmp/"manifest.json"
if not manifest_path.exists():
    raise SystemExit("private fixture repo missing manifest.json")
data=json.loads(manifest_path.read_text())
files=data.get("files",[])
if not files:
    raise SystemExit("fixture manifest contains no files")
for row in files:
    name=row["filename"]
    expected=row["sha256"]
    src=tmp/name
    if not src.exists():
        raise SystemExit(f"missing fixture: {name}")
    actual=hashlib.sha256(src.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"SHA mismatch for {name}: {actual}")
    shutil.copy2(src,dest/name)
print(f"Synced {len(files)} verified fixture files into {dest}")
PY

rm -rf "${TMP}"
echo "S0 fixture sync complete."
