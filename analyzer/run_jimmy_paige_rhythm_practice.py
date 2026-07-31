from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-rhythm-practice-report.json"

PROTECTION_COMMANDS = [
    [sys.executable, "analyzer/run_professional_rhythm_reference_validator.py"],
    [sys.executable, "analyzer/run_v8_intro_rhythm_template_lock_benchmark.py"],
    [sys.executable, "analyzer/run_v8_verse1_rhythm_template_lock_benchmark.py"],
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

    protection_results = [run_command(command) for command in PROTECTION_COMMANDS]
    protections_passed = all(item["passed"] for item in protection_results)

    mode = "practice" if ready_for_scoring else "guarded-dry-run"
    message = (
        "Reference is ready. Automated scoring practice may begin."
        if ready_for_scoring
        else (
            "Reference structure is protected, but exact event transcription is not yet "
            "verified. Jimmy remains in guarded dry-run mode."
        )
    )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-rhythm-practice-gate",
        "mode": mode,
        "readyForScoring": ready_for_scoring,
        "protectionsPassed": protections_passed,
        "trainingStarted": ready_for_scoring and protections_passed,
        "message": message,
        "protectionResults": protection_results,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "noSyntheticNotes": True,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge rhythm practice mode:", mode)
    print("Ready for scoring:", ready_for_scoring)
    print("Protection checks passed:", protections_passed)
    print("Training started:", report["trainingStarted"])
    print("Message:", message)
    print("Output:", REPORT_PATH.relative_to(REPO_ROOT))

    if not protections_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
