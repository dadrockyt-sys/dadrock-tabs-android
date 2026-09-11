#!/usr/bin/env bash
set -euo pipefail

# Provision the branch-pinned Python model environment before Policy C enrollment.
# This script intentionally does NOT register a GitHub runner and accepts no token.
# Runner registration remains an explicit admin action using GitHub's time-limited token.

AUTHORITY_ROOT="${SONGSTERR_FRESH_AUTHORITY_ROOT:-/opt/songsterr-fresh-authority}"
VENV="${AUTHORITY_ROOT}/venv"
PYTHON_BIN="${SONGSTERR_FRESH_AUTHORITY_PYTHON:-python3.10}"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "POLICY_C_BOOTSTRAP_ERROR:LINUX_REQUIRED" >&2
  exit 2
fi

case "$(uname -m)" in
  x86_64|amd64) ;;
  *)
    echo "POLICY_C_BOOTSTRAP_ERROR:X64_REQUIRED:$(uname -m)" >&2
    exit 2
    ;;
esac

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "POLICY_C_BOOTSTRAP_ERROR:PYTHON_3_10_REQUIRED" >&2
  exit 2
fi

PYTHON_VERSION="$($PYTHON_BIN -c 'import platform; print(platform.python_version())')"
if [[ "$PYTHON_VERSION" != 3.10.* ]]; then
  echo "POLICY_C_BOOTSTRAP_ERROR:PYTHON_VERSION_MISMATCH:${PYTHON_VERSION}" >&2
  exit 2
fi

for command_name in git curl ffmpeg node; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "POLICY_C_BOOTSTRAP_ERROR:REQUIRED_TOOL_MISSING:${command_name}" >&2
    exit 2
  fi
done

NODE_VERSION="$(node --version)"
if [[ "$NODE_VERSION" != v22.* ]]; then
  echo "POLICY_C_BOOTSTRAP_ERROR:NODE_22_REQUIRED:${NODE_VERSION}" >&2
  exit 2
fi

if [[ -e "$VENV" ]]; then
  echo "POLICY_C_BOOTSTRAP_ERROR:VENV_ALREADY_EXISTS:${VENV}" >&2
  echo "Remove/rebuild it only as an explicit re-enrollment action." >&2
  exit 2
fi

install -d -m 0755 "$AUTHORITY_ROOT"
"$PYTHON_BIN" -m venv "$VENV"

"$VENV/bin/python" -m pip install --disable-pip-version-check \
  numpy==1.26.4 \
  torch==2.14.0 \
  huggingface-hub==1.30.0 \
  safetensors==0.8.0 \
  sphn==0.2.1 \
  demucs==4.1.0 \
  basic-pitch==0.4.0 \
  librosa==0.11.0 \
  soundfile==0.13.1 \
  tflite-runtime==2.14.0

EXPECTED_JSON='{"basic-pitch":"0.4.0","demucs":"4.1.0","huggingface-hub":"1.30.0","librosa":"0.11.0","numpy":"1.26.4","safetensors":"0.8.0","soundfile":"0.13.1","sphn":"0.2.1","tflite-runtime":"2.14.0","torch":"2.14.0"}'
ACTUAL_JSON="$($VENV/bin/python - <<'PY'
import importlib.metadata
import json
names = [
    'numpy', 'torch', 'huggingface-hub', 'safetensors', 'sphn', 'demucs',
    'basic-pitch', 'librosa', 'soundfile', 'tflite-runtime',
]
print(json.dumps({name: importlib.metadata.version(name) for name in names}, sort_keys=True, separators=(',', ':')))
PY
)"
if [[ "$ACTUAL_JSON" != "$EXPECTED_JSON" ]]; then
  echo "POLICY_C_BOOTSTRAP_ERROR:PINNED_PACKAGE_SET_MISMATCH" >&2
  echo "expected=$EXPECTED_JSON" >&2
  echo "actual=$ACTUAL_JSON" >&2
  exit 2
fi

cat <<EOF
POLICY_C_BOOTSTRAP_OK
root=${AUTHORITY_ROOT}
venv=${VENV}
python=$($VENV/bin/python --version 2>&1)
node=$(node --version)
ffmpeg=$(ffmpeg -version 2>/dev/null | head -n1)

Next: register this fixed machine as the GitHub self-hosted runner with the
custom label songsterr-fresh-authority-v1, then dispatch the Policy C workflow
in probe mode. Do not rebuild or upgrade this venv after enrollment without
performing a new probe, deliberate re-enrollment, and three fresh canaries.
EOF
