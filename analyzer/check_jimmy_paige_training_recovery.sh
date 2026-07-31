#!/usr/bin/env bash
set -u

REPORT="public/gomyway-jimmy-paige-em-riff-extraction-training.json"
LOG="trainer-output.log"

echo "Jimmy PAIge interrupted-run recovery check"
echo "Working directory: $(pwd)"
echo

if [[ -f "$LOG" ]]; then
  echo "Trainer log found: $LOG"
  echo "Log size: $(wc -c < "$LOG") bytes"
  echo "Last modified: $(date -r "$LOG" 2>/dev/null || stat -c '%y' "$LOG" 2>/dev/null || echo unknown)"
  echo "----- last 80 log lines -----"
  tail -n 80 "$LOG"
  echo "----- end log -----"
else
  echo "Trainer log not found: $LOG"
fi

echo

if [[ -f "$REPORT" ]]; then
  echo "Training report found: $REPORT"
  echo "Report size: $(wc -c < "$REPORT") bytes"
  echo "Last modified: $(date -r "$REPORT" 2>/dev/null || stat -c '%y' "$REPORT" 2>/dev/null || echo unknown)"
  python - "$REPORT" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    report = json.loads(path.read_text())
except Exception as exc:
    print(f"Report JSON could not be read: {exc}")
    raise SystemExit(0)

print("passed:", report.get("passed"))
print("trainingStarted:", report.get("trainingStarted"))
print("attemptsCompleted:", report.get("attemptsCompleted"))
print("baselineCorrectCandidateSlots:", report.get("baselineCorrectCandidateSlots"))
print("bestCorrectCandidateSlots:", report.get("bestCorrectCandidateSlots"))
print("improved:", report.get("improved"))
print("targetReached:", report.get("targetReached"))
print("readyForRankingTraining:", report.get("readyForRankingTraining"))

best = report.get("bestAttempt") or {}
print("bestAttempt:", best.get("name"))
print("bestParameters:", best.get("parameters"))
print("bestExtractedEventCount:", best.get("extractedEventCount"))

attempts = report.get("attempts") or []
print("attemptRecordsPresent:", len(attempts))
for attempt in attempts:
    print(
        f"  attempt {attempt.get('attempt')}: "
        f"{attempt.get('name')} | "
        f"slots={attempt.get('correctCandidateSlots')}/9 | "
        f"events={attempt.get('extractedEventCount')}"
    )
PY
else
  echo "Training report not found: $REPORT"
  echo "The interrupted run likely ended before the final report write."
fi

echo

echo "Any still-running local trainer processes:"
pgrep -af "run_jimmy_paige_em_riff_extraction_training_loop.py|modal" || echo "none"
