#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: $0 /private/path/to/isolated-guitar.m4a [private-output-dir]" >&2
  exit 2
fi

SOURCE="$1"
OUT_DIR="${2:-$HOME/v168-splitmysong-private}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

git config --global --add safe.directory "$REPO_ROOT"

MODEL_PATH="$(python - <<'PY'
from basic_pitch import ICASSP_2022_MODEL_PATH
print(ICASSP_2022_MODEL_PATH)
PY
)"

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

python "$REPO_ROOT/validation/v168_splitmysong_diagnostic/verify_environment_v168.py" \
  --repo-root "$REPO_ROOT" \
  --receipt "$OUT_DIR/environment-receipt.json"

python "$REPO_ROOT/validation/v168_splitmysong_diagnostic/preflight_splitmysong_v168.py" \
  --phase arm \
  --source "$SOURCE" \
  --normalized-output "$OUT_DIR/input-normalized.wav" \
  --receipt "$OUT_DIR/arm-preflight-receipt.json" \
  --preregistration "$REPO_ROOT/debug/v168-splitmysong-diagnostic/preregistration.json" \
  --implementation-contract "$REPO_ROOT/debug/v168-splitmysong-diagnostic/implementation-contract.json" \
  --repo-root "$REPO_ROOT" \
  --model-path "$MODEL_PATH"

printf '\nARM PREFLIGHT PASS\n'
printf 'Private output directory: %s\n' "$OUT_DIR"
printf 'Environment receipt SHA256: '
sha256sum "$OUT_DIR/environment-receipt.json" | awk '{print $1}'
printf 'Arm receipt SHA256: '
sha256sum "$OUT_DIR/arm-preflight-receipt.json" | awk '{print $1}'
printf 'Normalized audio SHA256: '
sha256sum "$OUT_DIR/input-normalized.wav" | awk '{print $1}'
printf '\nDo not git-add or commit files from the private output directory.\n'
