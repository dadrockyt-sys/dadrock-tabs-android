#!/usr/bin/env bash

set -o pipefail

LOG_FILE="${TRAINER_LOG_FILE:-trainer-output.log}"
HEARTBEAT_SECONDS="${TRAINER_HEARTBEAT_SECONDS:-300}"
STARTED_AT="$(date +%s)"

python analyzer/run_jimmy_paige_em_riff_extraction_training_loop.py \
  2>&1 | tee "$LOG_FILE" &

TRAINER_PID=$!

echo "[trainer started] $(date)"
echo "[trainer pid] $TRAINER_PID"
echo "[trainer log] $LOG_FILE"
echo "[trainer heartbeat interval] ${HEARTBEAT_SECONDS}s"

cleanup() {
  if kill -0 "$TRAINER_PID" 2>/dev/null; then
    echo "[trainer signal] Forwarding stop request to PID $TRAINER_PID"
    kill "$TRAINER_PID" 2>/dev/null || true
  fi
}

trap cleanup INT TERM

while kill -0 "$TRAINER_PID" 2>/dev/null; do
  NOW="$(date +%s)"
  ELAPSED_SECONDS=$((NOW - STARTED_AT))
  ELAPSED_MINUTES=$((ELAPSED_SECONDS / 60))
  LOG_BYTES=0

  if [ -f "$LOG_FILE" ]; then
    LOG_BYTES="$(wc -c < "$LOG_FILE" | tr -d ' ')"
  fi

  echo "[trainer heartbeat] $(date) | elapsed=${ELAPSED_MINUTES}m | pid=$TRAINER_PID | logBytes=$LOG_BYTES"
  sleep "$HEARTBEAT_SECONDS"
done

wait "$TRAINER_PID"
TRAINER_EXIT=$?
FINISHED_AT="$(date +%s)"
TOTAL_SECONDS=$((FINISHED_AT - STARTED_AT))
TOTAL_MINUTES=$((TOTAL_SECONDS / 60))

echo "Trainer finished with exit code: $TRAINER_EXIT"
echo "Trainer runtime: ${TOTAL_MINUTES}m ${TOTAL_SECONDS}s"
echo "Trainer log: $LOG_FILE"

exit "$TRAINER_EXIT"
