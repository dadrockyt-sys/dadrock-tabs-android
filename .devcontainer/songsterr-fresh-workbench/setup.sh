#!/usr/bin/env bash
set -euo pipefail

# Songsterr Fresh Codespaces workbench bootstrap.
# Default state is measurement/development only. It MUST NOT be enrolled as the
# persistent Policy C authority and MUST NOT advance delivery/model validation.
# Optional Policy C-S session authority is a separate explicit process: it binds
# one exact Codespaces Linux boot/fingerprint/source commit, requires three exact
# canaries, and expires fail-closed on stop/restart/rebuild or any drift.

WORKBENCH_ROOT="${SONGSTERR_FRESH_WORKBENCH_ROOT:-/workspaces/.songsterr-fresh-workbench}"
VENV="${WORKBENCH_ROOT}/venv"
PROBE="${WORKBENCH_ROOT}/workbench-probe.json"
PYTHON_BIN="${SONGSTERR_FRESH_WORKBENCH_PYTHON:-python3.10}"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-${WORKBENCH_ROOT}/pip-cache}"
export HF_HOME="${HF_HOME:-${WORKBENCH_ROOT}/huggingface}"
export TORCH_HOME="${TORCH_HOME:-${WORKBENCH_ROOT}/torch}"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:LINUX_REQUIRED" >&2
  exit 2
fi

case "$(uname -m)" in
  x86_64|amd64) ;;
  *)
    echo "SONGSTERR_FRESH_WORKBENCH_ERROR:X64_REQUIRED:$(uname -m)" >&2
    exit 2
    ;;
esac

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:PYTHON_3_10_REQUIRED" >&2
  exit 2
fi
PYTHON_VERSION="$($PYTHON_BIN -c 'import platform; print(platform.python_version())')"
if [[ "$PYTHON_VERSION" != 3.10.* ]]; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:PYTHON_VERSION_MISMATCH:${PYTHON_VERSION}" >&2
  exit 2
fi

case "$(node --version 2>/dev/null || true)" in
  v22.*) ;;
  *) echo "SONGSTERR_FRESH_WORKBENCH_ERROR:NODE_22_REQUIRED" >&2; exit 2 ;;
esac

sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpeg git curl time ca-certificates
mkdir -p "$WORKBENCH_ROOT" "$PIP_CACHE_DIR" "$HF_HOME" "$TORCH_HOME"

EXPECTED_JSON='{"basic-pitch":"0.4.0","demucs":"4.1.0","huggingface-hub":"1.30.0","librosa":"0.11.0","numpy":"1.26.4","safetensors":"0.8.0","soundfile":"0.13.1","sphn":"0.2.1","tflite-runtime":"2.14.0","torch":"2.14.0"}'

venv_matches() {
  [[ -x "$VENV/bin/python" ]] || return 1
  "$VENV/bin/python" - <<'PY'
import importlib.metadata
import json
import sys
expected = {
    'numpy': '1.26.4',
    'torch': '2.14.0',
    'huggingface-hub': '1.30.0',
    'safetensors': '0.8.0',
    'sphn': '0.2.1',
    'demucs': '4.1.0',
    'basic-pitch': '0.4.0',
    'librosa': '0.11.0',
    'soundfile': '0.13.1',
    'tflite-runtime': '2.14.0',
}
try:
    actual = {name: importlib.metadata.version(name) for name in expected}
except importlib.metadata.PackageNotFoundError:
    raise SystemExit(1)
if actual != expected:
    raise SystemExit(1)
if not sys.version.startswith('3.10.'):
    raise SystemExit(1)
PY
}

if ! venv_matches; then
  echo "Rebuilding Codespaces workbench venv at $VENV"
  rm -rf "$VENV"
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
else
  echo "Reusing exact pinned Codespaces workbench venv at $VENV"
fi

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
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:PINNED_PACKAGE_SET_MISMATCH" >&2
  echo "expected=$EXPECTED_JSON" >&2
  echo "actual=$ACTUAL_JSON" >&2
  exit 2
fi

PATH="$VENV/bin:$PATH" "$VENV/bin/python" scripts/songsterr-fresh/verify_pinned_compute_authority.py \
  --validate-manifest \
  --probe-output "$PROBE"

cat > "${WORKBENCH_ROOT}/README.txt" <<EOF
SONGSTERR FRESH CODESPACES WORKBENCH

Persistent Policy C authority eligible: NO
Persistent Policy C enrollment changed: NO
Policy C-S session authority enrolled by setup: NO
Model validation complete: NO
Customer eligible events: 0
Duration authority changed: NO

Venv: $VENV
Probe: $PROBE

Activate with:
  source $VENV/bin/activate

Measurement-only benchmark:
  bash scripts/songsterr-fresh/run_codespaces_workbench_measurement.sh

Optional Policy C-S session authority (explicit; session expires on restart):
  bash scripts/songsterr-fresh/codespaces_session_authority.sh probe
  bash scripts/songsterr-fresh/codespaces_session_authority.sh enroll
  bash scripts/songsterr-fresh/codespaces_session_authority.sh qualify

Policy C-S surface qualification still does NOT set modelValidationComplete or
customer delivery eligibility.

Stop the codespace when you are finished so compute billing stops. Stopping it
also invalidates any Policy C-S session qualification.
EOF

cat <<EOF
SONGSTERR_FRESH_WORKBENCH_READY
root=$WORKBENCH_ROOT
venv=$VENV
probe=$PROBE
python=$($VENV/bin/python --version 2>&1)
node=$(node --version)
ffmpeg=$(ffmpeg -version 2>/dev/null | head -n1)
persistentPolicyCAuthorityEligible=false
policyCSessionAuthorityEnrolled=false
modelValidationComplete=false
customerEligibleEvents=0
EOF
