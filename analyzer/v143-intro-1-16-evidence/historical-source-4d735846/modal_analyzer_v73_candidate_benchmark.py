from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v73 as analyzer
import modal_gomyway2_full_reference_benchmark as reference

app = modal.App("dadrock-v73-combined-handoff-candidate-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v73")
    .add_local_python_source("modal_gomyway2_full_reference_benchmark")
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
)

SCORE_FLOORS = {
    "bass": 97.0,
    "rhythm": 95.2,
    "lead": 94.71,
}


def run_from_bytes(
    audio_bytes: bytes,
    audio_name: str,
    transcription_type: str,
) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        audio_path = handle.name
    return analyzer.analyze_audio_file(audio_path, transcription_type)


@app.function(image=image, timeout=2400, memory=4096)
def run_candidate(
    layered_audio_bytes: bytes,
    layered_audio_name: str,
    stairway_audio_bytes: bytes,
    stairway_audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    reference.legacy_bridge.group_assignments = (
        reference.legacy_assignments.group_assignments
    )
    reference.legacy_renderer.create_tab = reference.inventory_only_tab

    part_reports: dict[str, Any] = {}
    checks: dict[str, bool] = {}

    for part in ("bass", "rhythm", "lead"):
        result = run_from_bytes(layered_audio_bytes, layered_audio_name, part)
        events = [
            event
            for event in (result.get("events") or [])
            if isinstance(event, dict)
        ]
        part_reference = (fixture.get("parts") or {}).get(part, {})
        comparison = reference.compare_part(part, events, part_reference)
        score = float(comparison.get("comparisonScore") or 0.0)
        diagnostics = (
            (result.get("musicalUnderstanding") or {})
            .get("learnedVoicingTechniqueHandoff") or {}
        )

        part_reports[part] = {
            "engineVersion": result.get("engineVersion"),
            "separationMode": result.get("instrumentSeparationMode"),
            "handoffMode": result.get("voicingTechniqueHandoffMode"),
            "eventCount": len(events),
            "comparison": comparison,
            "handoffDiagnostics": diagnostics,
        }
        checks[f"{part}StrictSeparation"] = (
            result.get("instrumentSeparationMode")
            == "strict-three-way-register-gate"
        )
        checks[f"{part}LearnedHandoff"] = (
            result.get("voicingTechniqueHandoffMode")
            == "learned-three-part-handoff"
        )
        checks[f"{part}ScoreFloor"] = score >= SCORE_FLOORS[part]
        checks[f"{part}NoSyntheticNotes"] = int(
            ((diagnostics.get("diagnostics") or {}).get("syntheticNoteCount") or 0)
        ) == 0

    stairway_result = run_from_bytes(
        stairway_audio_bytes,
        stairway_audio_name,
        "lead",
    )
    stairway_events = [
        event
        for event in (stairway_result.get("events") or [])
        if isinstance(event, dict)
    ]
    checks["stairwayPreservesV71Fallback"] = (
        stairway_result.get("instrumentSeparationMode") == "protected-v71-fallback"
        and stairway_result.get("voicingTechniqueHandoffMode")
        == "protected-v71-fallback"
        and len(stairway_events) >= 49
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "v73-combined-learned-three-part-handoff-candidate",
        "engineVersion": analyzer.ENGINE_VERSION,
        "baseEngineVersion": analyzer.base.ENGINE_VERSION,
        "scoreFloors": SCORE_FLOORS,
        "parts": part_reports,
        "stairway": {
            "separationMode": stairway_result.get("instrumentSeparationMode"),
            "handoffMode": stairway_result.get("voicingTechniqueHandoffMode"),
            "eventCount": len(stairway_events),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "candidateRule": (
            "V73 is comparison-only until this benchmark and all seven existing "
            "regression guards pass"
        ),
    }
    return json.dumps(
        report,
        default=reference.json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    layered_audio_path: str,
    stairway_audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/v73-candidate-report.json",
) -> None:
    layered_file = Path(layered_audio_path)
    stairway_file = Path(stairway_audio_path)
    fixture_file = Path(fixture_path)
    for file in (layered_file, stairway_file, fixture_file):
        if not file.is_file():
            raise FileNotFoundError(f"Required file not found: {file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report_bytes = run_candidate.remote(
        layered_file.read_bytes(),
        layered_file.name,
        stairway_file.read_bytes(),
        stairway_file.name,
        fixture,
    )
    report = json.loads(bytes(report_bytes).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE V73 COMBINED HANDOFF CANDIDATE BENCHMARK")
    print("=" * 64)
    print("Engine:", report.get("engineVersion"))
    for part in ("bass", "rhythm", "lead"):
        part_report = (report.get("parts") or {}).get(part, {})
        comparison = part_report.get("comparison") or {}
        print()
        print(part.upper())
        print("Mode:", part_report.get("separationMode"))
        print("Handoff:", part_report.get("handoffMode"))
        print("Events:", part_report.get("eventCount"))
        print("Score:", comparison.get("comparisonScore"))
        print("Frets:", comparison.get("fretInventory"))
        print("Techniques:", comparison.get("techniqueChecks"))

    stairway = report.get("stairway") or {}
    print()
    print("STAIRWAY SAFETY")
    print("Separation:", stairway.get("separationMode"))
    print("Handoff:", stairway.get("handoffMode"))
    print("Events:", stairway.get("eventCount"))
    print()
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, and all seven locked baselines remain unchanged.")
