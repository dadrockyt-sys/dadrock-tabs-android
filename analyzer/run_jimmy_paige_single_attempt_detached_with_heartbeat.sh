#!/usr/bin/env bash

set -u
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

HEARTBEAT_SECONDS="${JIMMY_HEARTBEAT_SECONDS:-300}"
STATE_PATH="public/gomyway-jimmy-paige-em-riff-single-attempt-detached-state.json"
OUTPUT_PATH="public/gomyway-jimmy-paige-em-riff-single-attempt-timing-test.json"
LOG_PATH="single-attempt-detached-heartbeat.log"

started_epoch="$(date +%s)"

print_heartbeat() {
  local now_epoch elapsed_seconds elapsed_minutes call_id status
  now_epoch="$(date +%s)"
  elapsed_seconds=$((now_epoch - started_epoch))
  elapsed_minutes=$((elapsed_seconds / 60))
  call_id="unknown"
  status="unknown"

  if [[ -f "$STATE_PATH" ]]; then
    read -r call_id status < <(
      python - "$STATE_PATH" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    state = json.loads(path.read_text())
except Exception:
    print("unknown unknown")
else:
    print(state.get("callId", "unknown"), state.get("status", "unknown"))
PY
    )
  fi

  echo "[single-run heartbeat] $(date) | elapsed=${elapsed_minutes}m | status=${status} | callId=${call_id}" | tee -a "$LOG_PATH"
}

collect_once() {
  python analyzer/collect_jimmy_paige_single_attempt_detached.py 2>&1 | tee -a "$LOG_PATH"
  return "${PIPESTATUS[0]}"
}

if [[ "${JIMMY_RESUME_EXISTING:-0}" == "1" && -f "$STATE_PATH" ]]; then
  echo "Resuming heartbeat monitoring for the existing detached run." | tee -a "$LOG_PATH"
else
  rm -f "$OUTPUT_PATH"
  echo "Submitting a new detached Jimmy PAIge single-attempt timing test." | tee "$LOG_PATH"
  python analyzer/submit_jimmy_paige_single_attempt_detached.py 2>&1 | tee -a "$LOG_PATH"
  submit_exit="${PIPESTATUS[0]}"
  if [[ "$submit_exit" -ne 0 ]]; then
    echo "Detached submission failed with exit code: $submit_exit" | tee -a "$LOG_PATH"
    exit "$submit_exit"
  fi
fi

print_heartbeat

while true; do
  if [[ -f "$OUTPUT_PATH" ]]; then
    echo "[single-run complete] Result file found: $OUTPUT_PATH" | tee -a "$LOG_PATH"
    collect_once || true
    exit 0
  fi

  sleep "$HEARTBEAT_SECONDS"
  print_heartbeat

  collect_once
  collect_exit=$?
  if [[ "$collect_exit" -ne 0 ]]; then
    echo "Collector returned exit code $collect_exit. The detached Modal job may have failed." | tee -a "$LOG_PATH"
    exit "$collect_exit"
  fi

done
