#!/usr/bin/env bash
set -euo pipefail

# Qualify exactly one enrolled Codespaces Linux boot session with three distinct
# model executions.  Qualification is session-surface reproducibility only and
# never sets modelValidationComplete or customer delivery eligibility.

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
  echo "CODESPACES_SESSION_QUALIFICATION_ERROR:WORKBENCH_VENV_MISSING:$VENV" >&2
  exit 2
fi
if [[ ! -f "$ENROLLMENT" ]]; then
  echo "CODESPACES_SESSION_QUALIFICATION_ERROR:SESSION_ENROLLMENT_MISSING" >&2
  exit 2
fi

# Fail before spending model time if the enrolled session already drifted.
"$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py verify \
  --enrollment "$ENROLLMENT" \
  --output "${SESSION_ROOT}/qualification-pre-verification.json"

EPOCH_ID="$($PYTHON - "$ENROLLMENT" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding='utf-8'))['authorityEpochId'])
PY
)"
EPOCH_ROOT="${SESSION_ROOT}/epochs/${EPOCH_ID}"
mkdir -p "$EPOCH_ROOT"

# Always execute all three canaries for this qualification attempt.  Existing
# files are overwritten only after fresh pre/post session verification.
for execution_id in 1 2 3; do
  echo "CODESPACES_SESSION_QUALIFICATION_STAGE:canary-${execution_id}-of-3"
  bash scripts/songsterr-fresh/run_codespaces_session_authority_canary.sh "$execution_id"
done

QUALIFICATION="${EPOCH_ROOT}/session-qualification.json"
"$PYTHON" scripts/songsterr-fresh/aggregate_codespaces_session_authority_canaries.py \
  "${EPOCH_ROOT}/canary-1.json" \
  "${EPOCH_ROOT}/canary-2.json" \
  "${EPOCH_ROOT}/canary-3.json" \
  --output "$QUALIFICATION"

# Re-verify after aggregation so qualification cannot outlive a drift that
# occurred between the third post-check and completion.
FINAL_VERIFY="${EPOCH_ROOT}/qualification-final-verification.json"
"$PYTHON" scripts/songsterr-fresh/codespaces_session_authority.py verify \
  --enrollment "$ENROLLMENT" \
  --output "$FINAL_VERIFY"

"$PYTHON" - "$QUALIFICATION" "$FINAL_VERIFY" <<'PY'
import json, sys
q=json.load(open(sys.argv[1], encoding='utf-8'))
v=json.load(open(sys.argv[2], encoding='utf-8'))
assert q['contract']=='songsterr-fresh-codespaces-session-authority-qualification-v1'
assert q['measurement']['sessionAuthoritySurfaceQualified'] is True
assert q['authorityEpochId']==v['authorityEpochId']
assert q['sessionFingerprintSha256']==v['sessionFingerprintSha256']
assert q['sourceCommitSha']==v['sourceCommitSha']
assert q['policyBoundary']['modelValidationComplete'] is False
assert q['policyBoundary']['customerEligibleEvents']==0
print(json.dumps({
  'status':'CODESPACES_SESSION_AUTHORITY_SURFACE_QUALIFIED',
  'authorityEpochId':q['authorityEpochId'],
  'sessionFingerprintSha256':q['sessionFingerprintSha256'],
  'sourceCommitSha':q['sourceCommitSha'],
  'canaryExecutions':q['separateCanaryExecutionCount'],
  'modelValidationComplete':False,
  'customerEligibleEvents':0,
}, sort_keys=True))
PY

cat <<EOF
CODESPACES_SESSION_AUTHORITY_QUALIFICATION_COMPLETE
authorityEpochId=$EPOCH_ID
qualification=$QUALIFICATION
surfaceQualifiedForCurrentBootSession=true
modelValidationComplete=false
customerEligibleEvents=0
durationAuthorityChanged=false

IMPORTANT: stopping/restarting/rebuilding this Codespace invalidates this session qualification.
EOF
