#!/usr/bin/env bash
set -euo pipefail

# Run one Policy C-S canary in the current explicitly enrolled Codespaces boot
# session.  Authority is verified immediately before and after model execution.

if [[ $# -ne 1 || ! "$1" =~ ^[1-9][0-9]*$ ]]; then
  echo "usage: $0 <positive-local-execution-id>" >&2
  exit 2
fi
EXECUTION_ID="$1"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORKBENCH_ROOT="${SONGSTERR_FRESH_WORKBENCH_ROOT:-/workspaces/.songsterr-fresh-workbench}"
SESSION_ROOT="${SONGSTERR_FRESH_SESSION_AUTHORITY_ROOT:-/workspaces/.songsterr-fresh-session-authority}"
VENV="${WORKBENCH_ROOT}/venv"
PYTHON="${VENV}/bin/python"
ENROLLMENT="${SESSION_ROOT}/session-enrollment.json"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-${WORKBENCH_ROOT}/pip-cache}"
export HF_HOME="${HF_HOME:-${WORKBENCH_ROOT}/huggingface}"
export TORCH_HOME="${TORCH_HOME:-${WORKBENCH_ROOT}/torch}"
export PATH="${VENV}/bin:${PATH}"

if [[ ! -x "$PYTHON" ]]; then
  echo "CODESPACES_SESSION_CANARY_ERROR:WORKBENCH_VENV_MISSING:$VENV" >&2
  exit 2
fi
if [[ ! -f "$ENROLLMENT" ]]; then
  echo "CODESPACES_SESSION_CANARY_ERROR:SESSION_ENROLLMENT_MISSING" >&2
  exit 2
fi

EPOCH_ID="$($PYTHON - "$ENROLLMENT" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['authorityEpochId'])
PY
)"
CANARY_ROOT="${SESSION_ROOT}/epochs/${EPOCH_ID}"
mkdir -p "$CANARY_ROOT"
PRE_VERIFY="${CANARY_ROOT}/canary-${EXECUTION_ID}-pre-verification.json"
POST_VERIFY="${CANARY_ROOT}/canary-${EXECUTION_ID}-post-verification.json"
MODEL_LOG="${CANARY_ROOT}/canary-${EXECUTION_ID}-model.log"
CANARY_OUT="${CANARY_ROOT}/canary-${EXECUTION_ID}.json"

printf 'CODESPACES_SESSION_CANARY_STAGE:verify-pre execution=%s\n' "$EXECUTION_ID"
"$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py verify \
  --enrollment "$ENROLLMENT" \
  --output "$PRE_VERIFY"

printf 'CODESPACES_SESSION_CANARY_STAGE:model execution=%s\n' "$EXECUTION_ID"
# The workbench harness itself remains non-authoritative.  This wrapper provides
# the C-S pre/post authority binding around it.
bash scripts/songsterr-fresh/run_codespaces_workbench_measurement.sh | tee "$MODEL_LOG"

SUMMARY_PATH="$(grep '^summary=' "$MODEL_LOG" | tail -1 | cut -d= -f2-)"
if [[ -z "$SUMMARY_PATH" || ! -f "$SUMMARY_PATH" ]]; then
  echo "CODESPACES_SESSION_CANARY_ERROR:WORKBENCH_SUMMARY_NOT_FOUND" >&2
  exit 2
fi
RUN_DIR="$(dirname "$SUMMARY_PATH")"
STEM="${RUN_DIR}/separated/htdemucs_6s/separation/guitar.wav"
for path in \
  "$RUN_DIR/evidence.json" \
  "$RUN_DIR/basic-pitch-note-activations.json" \
  "$RUN_DIR/basic-pitch-decision-surface.json" \
  "$RUN_DIR/basic-pitch-guitar-notes.json" \
  "$RUN_DIR/note-evidence-context.json" \
  "$RUN_DIR/demucs-model-asset.json" \
  "$RUN_DIR/separation.wav" \
  "$STEM"; do
  if [[ ! -s "$path" ]]; then
    echo "CODESPACES_SESSION_CANARY_ERROR:MODEL_OUTPUT_MISSING:$path" >&2
    exit 2
  fi
done

printf 'CODESPACES_SESSION_CANARY_STAGE:verify-post execution=%s\n' "$EXECUTION_ID"
"$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py verify \
  --enrollment "$ENROLLMENT" \
  --output "$POST_VERIFY"

SOURCE_COMMIT="$(git rev-parse HEAD)"
printf 'CODESPACES_SESSION_CANARY_STAGE:bind execution=%s\n' "$EXECUTION_ID"
"$PYTHON" scripts/songsterr-fresh/build_codespaces_session_authority_canary.py \
  --pre-verification "$PRE_VERIFY" \
  --post-verification "$POST_VERIFY" \
  --measurement-summary "$SUMMARY_PATH" \
  --evidence "$RUN_DIR/evidence.json" \
  --activation "$RUN_DIR/basic-pitch-note-activations.json" \
  --decision "$RUN_DIR/basic-pitch-decision-surface.json" \
  --notes "$RUN_DIR/basic-pitch-guitar-notes.json" \
  --context "$RUN_DIR/note-evidence-context.json" \
  --demucs-model-asset "$RUN_DIR/demucs-model-asset.json" \
  --stem "$STEM" \
  --separation "$RUN_DIR/separation.wav" \
  --source-commit "$SOURCE_COMMIT" \
  --execution-id "$EXECUTION_ID" \
  --output "$CANARY_OUT"

cat <<EOF
CODESPACES_SESSION_AUTHORITY_CANARY_COMPLETE
executionId=$EXECUTION_ID
authorityEpochId=$EPOCH_ID
canary=$CANARY_OUT
sessionQualifiedByThisSingleCanary=false
modelValidationComplete=false
customerEligibleEvents=0
EOF
