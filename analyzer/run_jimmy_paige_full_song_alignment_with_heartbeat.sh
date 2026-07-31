#!/usr/bin/env bash

set -o pipefail

HEARTBEAT_SECONDS="${JIMMY_HEARTBEAT_SECONDS:-15}"
LOG_FILE="${JIMMY_ALIGNMENT_LOG_FILE:-jimmy-paige-full-song-alignment.log}"
STARTED_AT="$(date +%s)"

printf '%s | Starting Jimmy PAIge full-song alignment diagnosis\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
printf '%s | Heartbeat interval: %ss | log=%s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" "$HEARTBEAT_SECONDS" "$LOG_FILE"

python analyzer/diagnose_jimmy_paige_full_song_alignment.py \
  2>&1 | tee "$LOG_FILE" &

DIAGNOSIS_PID=$!

while kill -0 "$DIAGNOSIS_PID" 2>/dev/null; do
  NOW="$(date +%s)"
  ELAPSED="$((NOW - STARTED_AT))"
  MINUTES="$((ELAPSED / 60))"
  SECONDS="$((ELAPSED % 60))"
  printf '%s | [alignment heartbeat] elapsed=%02dm:%02ds | pid=%s | status=working\n' \
    "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" \
    "$MINUTES" \
    "$SECONDS" \
    "$DIAGNOSIS_PID"
  sleep "$HEARTBEAT_SECONDS"
done

wait "$DIAGNOSIS_PID"
EXIT_CODE=$?
NOW="$(date +%s)"
ELAPSED="$((NOW - STARTED_AT))"
MINUTES="$((ELAPSED / 60))"
SECONDS="$((ELAPSED % 60))"

printf '%s | Alignment diagnosis finished | elapsed=%02dm:%02ds | exitCode=%s\n' \
  "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" \
  "$MINUTES" \
  "$SECONDS" \
  "$EXIT_CODE"

exit "$EXIT_CODE"
