#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="jimmy-paige-v8-section-detection"
MODE="${1:-test}"

cd "$REPO_ROOT"

say() {
  printf '\n\033[1;36m%s\033[0m\n' "$1"
}

fail() {
  printf '\n\033[1;31mJimmy PAIge V8 stopped: %s\033[0m\n' "$1" >&2
  exit 1
}

sync_branch() {
  say "Syncing $BRANCH"

  current_branch="$(git branch --show-current)"
  [[ "$current_branch" == "$BRANCH" ]] || fail "Expected branch $BRANCH, found $current_branch"

  git pull --ff-only origin "$BRANCH"
  git log -1 --oneline
}

run_python_checks() {
  say "Checking Jimmy PAIge V8 Python files"

  python -m py_compile \
    analyzer/song_section_detection_v8.py \
    analyzer/notation_cleanup_v8.py \
    analyzer/intro_motif_stabilization_v8.py \
    analyzer/modal_analyzer_v8_section_benchmark.py \
    analyzer/modal_analyzer_v8_notation_benchmark.py \
    analyzer/run_v8_section_benchmark.py \
    analyzer/run_v8_notation_benchmark.py
}

run_benchmarks() {
  say "Running V8 section benchmark"
  python analyzer/run_v8_section_benchmark.py

  say "Running V8 notation benchmark"
  python analyzer/run_v8_notation_benchmark.py
}

print_summary() {
  say "Jimmy PAIge V8 benchmark summary"

  python - <<'PY'
import json
from pathlib import Path

section_path = Path("public/gomyway-full-song-v8-sections.json")
notation_path = Path("public/gomyway-full-song-v8-notation.json")

if section_path.exists():
    section = json.loads(section_path.read_text())
    score = section.get("sectionScore", {})
    print("Section technical pass:", section.get("passed"))
    print("Section training pass:", section.get("trainingPassed"))
    print("Section overall score:", score.get("overallScore"))
else:
    print("Section report: missing")

print()

if notation_path.exists():
    notation = json.loads(notation_path.read_text())
    cleanup = notation.get("cleanupDiagnostics", {})
    motif = notation.get("motifDiagnostics", {})
    print("Notation pass:", notation.get("passed"))
    print("Protected V7 unchanged:", notation.get("protectedBaselinesChanged") is False)
    print("Raw events:", len(notation.get("rhythmEvents", [])))
    print("Cleaned events:", len(notation.get("renderEvents", [])))
    print("Motif events:", len(notation.get("motifStabilizedEvents", [])))
    print("Nearby retriggers removed:", cleanup.get("nearbyRetriggerEventsRemoved"))
    print("Intro input events:", motif.get("inputIntroEventCount"))
    print("Intro output events:", motif.get("outputIntroEventCount"))
    print("Low-support intro events rejected:", motif.get("rejectedLowSupportIntroEvents"))
    print("Repeated intro retriggers removed:", motif.get("repeatedPairRetriggersRemoved"))
else:
    print("Notation report: missing")
PY
}

run_build() {
  say "Building DadRock Tabs"
  yarn build
}

start_preview() {
  say "Starting PDF preview on port 3000"
  printf 'Open /api/pdf-preview after the server is ready.\n'
  exec yarn dev
}

case "$MODE" in
  sync)
    sync_branch
    ;;
  test)
    sync_branch
    run_python_checks
    run_benchmarks
    print_summary
    ;;
  build)
    sync_branch
    run_python_checks
    run_benchmarks
    print_summary
    run_build
    ;;
  preview)
    sync_branch
    run_python_checks
    run_benchmarks
    print_summary
    run_build
    start_preview
    ;;
  rerun)
    run_python_checks
    run_benchmarks
    print_summary
    run_build
    ;;
  *)
    cat <<'USAGE'
Usage: bash scripts/jimmy-v8.sh <mode>

Modes:
  sync     Pull the current Jimmy PAIge V8 branch.
  test     Pull, compile Python, run both benchmarks, and print results.
  build    Run test mode and then yarn build.
  preview  Run build mode and then start yarn dev on port 3000.
  rerun    Skip git pull; rerun checks, benchmarks, and build.
USAGE
    exit 2
    ;;
esac
