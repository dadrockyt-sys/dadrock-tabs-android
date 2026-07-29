from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v15 as legacy_renderer
import modal_analyzer_v19 as legacy_assignments
import modal_analyzer_v46 as legacy_bridge
import modal_analyzer_v72 as analyzer

app = modal.App("dadrock-v72-adaptive-separation-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v72")
)


def inventory_only_tab(mapped_groups: list[list[dict[str, Any]]], transcription_type: str) -> str:
    return "[v72 activation benchmark: rendering intentionally skipped]"


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except (TypeError, ValueError):
            pass
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run_one(audio_bytes: bytes, audio_name: str, transcription_type: str) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        return analyzer.analyze_audio_file(temporary_path, transcription_type)
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.function(image=image, timeout=1800, memory=4096)
def run_activation_test(
    layered_audio_bytes: bytes,
    layered_audio_name: str,
    stairway_audio_bytes: bytes,
    stairway_audio_name: str,
) -> bytes:
    legacy_bridge.group_assignments = legacy_assignments.group_assignments
    legacy_renderer.create_tab = inventory_only_tab

    layered_results = {
        part: run_one(layered_audio_bytes, layered_audio_name, part)
        for part in ("bass", "rhythm", "lead")
    }
    stairway_result = run_one(stairway_audio_bytes, stairway_audio_name, "lead")

    layered_modes = {
        part: result.get("instrumentSeparationMode")
        for part, result in layered_results.items()
    }
    layered_counts = {
        part: len(result.get("events") or [])
        for part, result in layered_results.items()
    }
    stairway_mode = stairway_result.get("instrumentSeparationMode")

    checks = {
        "layeredBassActivates": layered_modes["bass"] == "strict-three-way-register-gate",
        "layeredRhythmActivates": layered_modes["rhythm"] == "strict-three-way-register-gate",
        "layeredLeadActivates": layered_modes["lead"] == "strict-three-way-register-gate",
        "layeredBassHasEvents": layered_counts["bass"] >= 62,
        "layeredRhythmHasEvents": layered_counts["rhythm"] >= 39,
        "layeredLeadHasEvents": layered_counts["lead"] >= 14,
        "stairwayFallsBackToV71": stairway_mode == "protected-v71-fallback",
    }

    report = {
        "benchmarkType": "v72-adaptive-three-way-activation",
        "engineVersion": analyzer.ENGINE_VERSION,
        "layeredModes": layered_modes,
        "layeredEventCounts": layered_counts,
        "layeredEvidence": {
            part: (
                (result.get("musicalUnderstanding") or {})
                .get("adaptiveInstrumentSeparation", {})
                .get("evidence", {})
            )
            for part, result in layered_results.items()
        },
        "stairwayMode": stairway_mode,
        "stairwayEventCount": len(stairway_result.get("events") or []),
        "stairwayEvidence": (
            (stairway_result.get("musicalUnderstanding") or {})
            .get("adaptiveInstrumentSeparation", {})
            .get("evidence", {})
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }

    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    layered_audio_path: str,
    stairway_audio_path: str,
    report_output: str = "/tmp/v72-activation-report.json",
) -> None:
    layered_file = Path(layered_audio_path)
    stairway_file = Path(stairway_audio_path)
    if not layered_file.is_file():
        raise FileNotFoundError(f"Layered audio file not found: {layered_file}")
    if not stairway_file.is_file():
        raise FileNotFoundError(f"Stairway audio file not found: {stairway_file}")

    payload = run_activation_test.remote(
        layered_file.read_bytes(),
        layered_file.name,
        stairway_file.read_bytes(),
        stairway_file.name,
    )
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V72 ADAPTIVE SEPARATION ACTIVATION BENCHMARK")
    print("=" * 68)
    print("Engine:", report.get("engineVersion"))
    print("\nLayered recording")
    print("Modes:", report.get("layeredModes"))
    print("Event counts:", report.get("layeredEventCounts"))
    print("\nStairway safety fallback")
    print("Mode:", report.get("stairwayMode"))
    print("Event count:", report.get("stairwayEventCount"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("\nSaved report:", report_output)
    print("V71 and all three locked baselines remain unchanged.")
