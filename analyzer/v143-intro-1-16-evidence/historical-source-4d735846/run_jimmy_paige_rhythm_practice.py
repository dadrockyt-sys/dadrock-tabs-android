from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference.json"
PATTERN_LIBRARY_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-pattern-library.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-rhythm-practice-report.json"

# One-command protected curriculum. Every stage is read-only and must preserve
# locked V7 events, locked rhythm templates, protected baselines, and renderer.
CURRICULUM_COMMANDS = [
    [sys.executable, "analyzer/build_professional_rhythm_pattern_library.py"],
    [sys.executable, "analyzer/run_professional_rhythm_reference_validator.py"],
    [sys.executable, "analyzer/run_v8_rhythm_candidate_benchmark.py"],
    [sys.executable, "analyzer/run_v8_intro_rhythm_template_lock_benchmark.py"],
    [sys.executable, "analyzer/run_v8_verse1_rhythm_repetition_benchmark.py"],
    [sys.executable, "analyzer/run_v8_verse1_rhythm_consensus_benchmark.py"],
    [sys.executable, "analyzer/run_v8_verse1_rhythm_template_lock_benchmark.py"],
    [sys.executable, "analyzer/run_v8_post_verse1_rhythm_boundary_scan_benchmark.py"],
    [sys.executable, "analyzer/run_v8_post_verse1_rhythm_boundary_confirmation_benchmark.py"],
]


def run_command(command: list[str]) -> dict[str, object]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": " ".join(command),
        "passed": result.returncode == 0,
        "returnCode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> None:
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(
            "Missing professional rhythm reference. Run "
            "python analyzer/build_professional_rhythm_reference_measure_map.py first."
        )

    reference = json.loads(REFERENCE_PATH.read_text())
    ready_for_scoring = reference.get("readyForScoring") is True

    curriculum_results: list[dict[str, object]] = []
    stopped_early = False

    for command in CURRICULUM_COMMANDS:
        result = run_command(command)
        curriculum_results.append(result)
        if not result["passed"]:
            stopped_early = True
            break

    protections_passed = all(item["passed"] for item in curriculum_results)
    completed_stage_count = sum(1 for item in curriculum_results if item["passed"])

    pattern_summary: dict[str, object] = {}
    if PATTERN_LIBRARY_PATH.exists():
        pattern_library = json.loads(PATTERN_LIBRARY_PATH.read_text())
        pattern_summary = {
            "patternCount": pattern_library.get("patternCount", 0),
            "classifiedMeasureCount": pattern_library.get("classifiedMeasureCount", 0),
            "measureCount": pattern_library.get("measureCount", 0),
            "measurePatternCoveragePercent": pattern_library.get(
                "measurePatternCoveragePercent", 0.0
            ),
            "allPatternsEventVerified": pattern_library.get(
                "allPatternsEventVerified", False
            ),
            "nextVerificationTarget": (
                (pattern_library.get("verificationQueue") or [None])[0]
            ),
        }

    mode = (
        "protected-scoring-practice"
        if ready_for_scoring
        else "protected-structural-practice"
    )
    message = (
        "Protected curriculum completed. Exact professional-event scoring is enabled."
        if ready_for_scoring and protections_passed
        else (
            "Protected structural curriculum completed. Reusable professional patterns "
            "are mapped across the full track while Jimmy practices section, repetition, "
            "consensus, and boundary detection. Exact scoring remains locked until each "
            "pattern's event transcription is verified."
            if protections_passed
            else "Practice stopped immediately because a protected curriculum stage failed."
        )
    )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-rhythm-protected-curriculum",
        "mode": mode,
        "readyForScoring": ready_for_scoring,
        "trainingStarted": bool(curriculum_results),
        "scoringStarted": ready_for_scoring and protections_passed,
        "protectionsPassed": protections_passed,
        "stoppedEarly": stopped_early,
        "completedStageCount": completed_stage_count,
        "totalStageCount": len(CURRICULUM_COMMANDS),
        "patternLibrary": pattern_summary,
        "message": message,
        "curriculumResults": curriculum_results,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "noSyntheticNotes": True,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge rhythm practice mode:", mode)
    print("Training started:", report["trainingStarted"])
    print("Ready for exact scoring:", ready_for_scoring)
    print(
        "Curriculum stages passed:",
        f"{completed_stage_count}/{len(CURRICULUM_COMMANDS)}",
    )
    print("Protection checks passed:", protections_passed)
    if pattern_summary:
        print(
            "Reusable patterns mapped:",
            pattern_summary.get("patternCount"),
        )
        print(
            "Measure pattern coverage:",
            f"{pattern_summary.get('measurePatternCoveragePercent')}%",
        )
        print(
            "Next event verification target:",
            pattern_summary.get("nextVerificationTarget"),
        )
    print("Scoring started:", report["scoringStarted"])
    print("Message:", message)
    print("Output:", REPORT_PATH.relative_to(REPO_ROOT))

    if not protections_passed:
        failed = curriculum_results[-1]
        if failed.get("stdout"):
            print("Failed stage output:\n", failed["stdout"])
        if failed.get("stderr"):
            print("Failed stage error:\n", failed["stderr"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
