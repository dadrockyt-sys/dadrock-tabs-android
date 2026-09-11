#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
WORKBENCH_ROOT="${SONGSTERR_FRESH_WORKBENCH_ROOT:-/workspaces/.songsterr-fresh-workbench}"
SESSION_ROOT="${SONGSTERR_FRESH_SESSION_AUTHORITY_ROOT:-/workspaces/.songsterr-fresh-session-authority}"
VENV="${WORKBENCH_ROOT}/venv"
PYTHON="${VENV}/bin/python"

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
  echo "CODESPACES_SESSION_AUTHORITY_ERROR:WORKBENCH_VENV_MISSING" >&2
  echo "Run: bash .devcontainer/songsterr-fresh-workbench/setup.sh" >&2
  exit 2
fi

command_name="${1:-}"
case "$command_name" in
  probe)
    "$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py probe \
      --output "${SESSION_ROOT}/session-probe.json"
    echo
    echo "Review: ${SESSION_ROOT}/session-probe.json"
    echo "Probe alone does NOT enroll or qualify authority."
    ;;
  enroll)
    "$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py enroll \
      --ack SESSION_BOUND_AUTHORITY_EXPIRES_ON_RESTART \
      --output "${SESSION_ROOT}/session-enrollment.json" \
      --probe-output "${SESSION_ROOT}/session-probe.json"
    echo
    echo "Enrollment is valid only for this exact boot/fingerprint/source commit."
    echo "Next: bash scripts/songsterr-fresh/codespaces_session_authority.sh qualify"
    ;;
  verify|status)
    "$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py verify \
      --enrollment "${SESSION_ROOT}/session-enrollment.json"
    ;;
  qualify)
    bash scripts/songsterr-fresh/qualify_codespaces_session_authority.sh
    ;;
  expire)
    rm -f "${SESSION_ROOT}/session-enrollment.json"
    echo "CODESPACES_SESSION_AUTHORITY_EXPIRED"
    echo "Any prior qualification remains historical evidence only and cannot authorize this session."
    ;;
  self-test)
    "$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py self-test
    "$PYTHON" scripts/songsterr-fresh/build_codespaces_session_authority_canary.py --self-test
    "$PYTHON" scripts/songsterr-fresh/aggregate_codespaces_session_authority_canaries.py --self-test
    ;;
  *)
    cat >&2 <<'EOF'
Usage:
  bash scripts/songsterr-fresh/codespaces_session_authority.sh probe
  bash scripts/songsterr-fresh/codespaces_session_authority.sh enroll
  bash scripts/songsterr-fresh/codespaces_session_authority.sh verify
  bash scripts/songsterr-fresh/codespaces_session_authority.sh qualify
  bash scripts/songsterr-fresh/codespaces_session_authority.sh expire
  bash scripts/songsterr-fresh/codespaces_session_authority.sh self-test

Policy C-S is session-bound. Stop/restart/rebuild or fingerprint/source drift fails closed.
Qualification does not set modelValidationComplete and does not enable customer delivery.
EOF
    exit 2
    ;;
esac
