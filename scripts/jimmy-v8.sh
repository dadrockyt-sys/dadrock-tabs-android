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

  before_pull="$(git rev-parse HEAD)"
  git pull --ff-only origin "$BRANCH"
  after_pull="$(git rev-parse HEAD)"
  git log -1 --oneline

  if [[ "$before_pull" != "$after_pull" && "${JIMMY_V8_REEXECUTED:-0}" != "1" ]]; then
    say "Reloading updated Jimmy PAIge workflow"
    export JIMMY_V8_REEXECUTED=1
    exec bash "$REPO_ROOT/scripts/jimmy-v8.sh" "$MODE"
  fi
}

run_python_checks() {
  say "Checking Jimmy PAIge V8 Python files"

  python -m py_compile \
    analyzer/song_section_detection_v8.py \
    analyzer/notation_cleanup_v8.py \
    analyzer/intro_motif_stabilization_v8.py \
    analyzer/intro_pitch_contour_v8.py \
    analyzer/intro_fingering_normalization_v8.py \
    analyzer/professional_intro_accuracy_benchmark_v8.py \
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

  say "Running professional intro note-accuracy benchmark"
  python analyzer/professional_intro_accuracy_benchmark_v8.py
}

print_summary() {
  say "Jimmy PAIge V8 benchmark summary"
  printf 'Workflow commit: %s\n' "$(git rev-parse --short HEAD)"

  python - <<'PY'
import json
from pathlib import Path

section_path = Path("public/gomyway-full-song-v8-sections.json")
notation_path = Path("public/gomyway-full-song-v8-notation.json")
professional_path = Path("public/gomyway-full-song-v8-professional-intro-score.json")

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
    contour = notation.get("pitchContourDiagnostics", {})
    fingering = notation.get("fingeringDiagnostics", {})
    print("Notation benchmark type:", notation.get("benchmarkType"))
    print("Notation pass:", notation.get("passed"))
    print("Protected V7 unchanged:", notation.get("protectedBaselinesChanged") is False)
    print("Raw events:", len(notation.get("rhythmEvents", [])))
    print("Cleaned events:", len(notation.get("renderEvents", [])))
    print("Motif events:", len(notation.get("motifStabilizedEvents", [])))
    print("Pitch-contour events:", len(notation.get("pitchContourReconstructedEvents", [])))
    print("Fingering events:", len(notation.get("fingeringNormalizedEvents", [])))
    print("Nearby retriggers removed:", cleanup.get("nearbyRetriggerEventsRemoved"))
    print("Intro input events:", motif.get("inputIntroEventCount"))
    print("Intro output events:", motif.get("outputIntroEventCount"))
    print("Low-support intro events rejected:", motif.get("rejectedLowSupportIntroEvents"))
    print("Repeated intro retriggers removed:", motif.get("repeatedPairRetriggersRemoved"))
    print("Accepted pitch contours:", contour.get("acceptedContourSignatureCount"))
    print("Bend events marked:", contour.get("bendEventsMarked"))
    print("Bend releases marked:", contour.get("bendReleaseEventsMarked"))
    print("Pitch excursions removed:", contour.get("pitchExcursionDisplayEventsRemoved"))
    print("Contour retriggers removed:", contour.get("nearbySustainRetriggersRemoved"))
    print("Contour support histogram:", contour.get("contourSupportHistogram"))
    print("Intro fingerings normalized:", fingering.get("changedIntroFingerings"))
    print("Fingering pitch preserved:", fingering.get("pitchPreserved"))

    source_events = notation.get("motifStabilizedEvents", [])
    intro_events = [
        event for event in source_events
        if 1 <= int(event.get("measureNumber", 0) or 0) <= 4
    ]
    print()
    print("Intro contour source events (measures 1-4):")
    for event in intro_events:
        print(
            "M{measure} S{step} string={string} fret={fret} midi={midi} pos={position}".format(
                measure=event.get("measureNumber"),
                step=event.get("quantizedStep"),
                string=event.get("stringIndex"),
                fret=event.get("fret"),
                midi=event.get("midiPitch"),
                position=event.get("positionInMeasure"),
            )
        )
else:
    print("Notation report: missing")

print()

if professional_path.exists():
    professional = json.loads(professional_path.read_text())
    score = professional.get("score", {})
    print("Selected event layer:", professional.get("selectedEventLayer"))
    print("Professional intro pass:", score.get("passed"))
    print("Professional intro overall score:", score.get("overallScore"))
    print("Professional intro target:", score.get("targetScore"))
    print("Note identity recall:", score.get("identityRecall"))
    print("Note identity precision:", score.get("identityPrecision"))
    print("Timing accuracy:", score.get("timingAccuracy"))
    print("Technique accuracy:", score.get("techniqueAccuracy"))
    print("False positives:", score.get("falsePositiveCount"))
else:
    print("Professional intro report: missing")
PY
}

run_build() {
  say "Building DadRock Tabs"
  NODE_OPTIONS="--max-old-space-size=768" yarn build
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
  test     Pull, compile Python, run all benchmarks, and print results.
  build    Run test mode and then a memory-capped production build.
  preview  Pull, test, score, and start yarn dev without a production build.
  rerun    Skip git pull; rerun checks, benchmarks, and production build.
USAGE
    exit 2
    ;;
esac
