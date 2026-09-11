#!/usr/bin/env bash
set -euo pipefail

# Preserve the latest completed Songsterr Fresh Codespaces workbench summary
# into the branch as measurement/capacity evidence only. This helper cannot
# enroll Policy C authority or promote model/duration/delivery state.

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORKBENCH_ROOT="${SONGSTERR_FRESH_WORKBENCH_ROOT:-/workspaces/.songsterr-fresh-workbench}"
DEST="docs/checkpoints/SONGSTERR_FRESH_CODESPACES_WORKBENCH_MEASUREMENT_V2.json"
SUMMARY="${1:-}"

if [[ -z "$SUMMARY" ]]; then
  SUMMARY="$(find "$WORKBENCH_ROOT/runs" -name workbench-measurement-summary.json -type f 2>/dev/null | sort | tail -1)"
fi

if [[ -z "$SUMMARY" || ! -f "$SUMMARY" ]]; then
  echo "SONGSTERR_FRESH_PRESERVE_ERROR:MEASUREMENT_SUMMARY_NOT_FOUND" >&2
  exit 2
fi

PYTHON="${WORKBENCH_ROOT}/venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON" || ! -x "$PYTHON" ]]; then
  echo "SONGSTERR_FRESH_PRESERVE_ERROR:PYTHON_NOT_FOUND" >&2
  exit 2
fi

mkdir -p "$(dirname "$DEST")"
SUMMARY="$SUMMARY" DEST="$DEST" "$PYTHON" - <<'PY'
import json
import os
from pathlib import Path

src = Path(os.environ['SUMMARY'])
dest = Path(os.environ['DEST'])
data = json.loads(src.read_text(encoding='utf-8'))

if data.get('contract') != 'songsterr-fresh-codespaces-workbench-measurement-v2':
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:CONTRACT_MISMATCH')
if data.get('version') != 2:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:VERSION_MISMATCH')

required_false = (
    'authorityEligible',
    'probeAloneEnrollsAuthority',
    'modelValidationComplete',
    'mayAdvanceDelivery',
    'durationAuthorityChanged',
)
for key in required_false:
    if data.get(key) is not False:
        raise SystemExit(f'SONGSTERR_FRESH_PRESERVE_ERROR:NON_PROMOTION_GUARD_CHANGED:{key}')
if data.get('workbenchOnly') is not True:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:WORKBENCH_ONLY_REQUIRED')
if data.get('customerEligibleEvents') != 0:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:CUSTOMER_ELIGIBLE_EVENTS_CHANGED')

structure = data.get('structureDiagnostics') or {}
if structure.get('referenceBlind') is not True:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:REFERENCE_BLIND_REQUIRED')
if structure.get('structureFrozen') is not True:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:STRUCTURE_FROZEN_REQUIRED')
if structure.get('structureAccepted') is not True:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:STRUCTURE_ACCEPTED_REQUIRED')
if structure.get('authorityEligible') is not False:
    raise SystemExit('SONGSTERR_FRESH_PRESERVE_ERROR:STRUCTURE_AUTHORITY_GUARD_CHANGED')

for key in ('total', 'demucs', 'basicPitch', 'structure'):
    value = (data.get('timingsSeconds') or {}).get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SystemExit(f'SONGSTERR_FRESH_PRESERVE_ERROR:TIMING_INVALID:{key}')
for key in ('demucsMaximumResidentSetKb', 'basicPitchMaximumResidentSetKb'):
    raw = (data.get('resources') or {}).get(key)
    try:
        value = int(raw)
    except Exception:
        raise SystemExit(f'SONGSTERR_FRESH_PRESERVE_ERROR:RESOURCE_INVALID:{key}')
    if value <= 0:
        raise SystemExit(f'SONGSTERR_FRESH_PRESERVE_ERROR:RESOURCE_INVALID:{key}')

identities = data.get('identities') or {}
for key in (
    'guitarStemSha256',
    'noteInferenceSha256',
    'activationBundleSha256',
    'decisionSurfaceSha256',
    'canonicalEvidenceSha256',
):
    value = identities.get(key)
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise SystemExit(f'SONGSTERR_FRESH_PRESERVE_ERROR:IDENTITY_INVALID:{key}')

dest.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(f'SONGSTERR_FRESH_MEASUREMENT_PRESERVED:{dest}')
print(f'sourceCommit={data.get("sourceCommit")}')
print('authorityEligible=false')
print('modelValidationComplete=false')
print('customerEligibleEvents=0')
PY

echo
echo "Review with:"
echo "  git diff -- $DEST"
echo
echo "Then commit only this measurement evidence file:"
echo "  git add $DEST && git commit -m 'docs: preserve Codespaces workbench measurement' && git push origin songsterr-fresh-pipeline-v1"
