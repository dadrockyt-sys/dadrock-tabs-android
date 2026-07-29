"""Run V71 and harmonic bend evidence inside one hydrated Modal worker.

This avoids cross-App Function.remote() hydration and NumPy deserialization errors.
The protected V71 analyzer remains unchanged.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer
import modal_bend_harmonic_evidence_benchmark as harmonic
import modal_bend_notation_handoff_benchmark as handoff

app = modal.App("dadrock-bend-notation-handoff-benchmark-v2")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_harmonic_evidence_benchmark")
    .add_local_python_source("modal_bend_cadence_benchmark")
    .add_local_python_source("modal_bend_tempo_grid_benchmark")
    .add_local_python_source("modal_bend_notation_handoff_benchmark")
)


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


@app.function(image=image, timeout=1200, memory=4096)
def analyse_notation_handoff(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    """Perform every NumPy-dependent step remotely and return plain JSON bytes."""
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        transcription_type = str(fixture.get("transcriptionType") or "lead")
        result = analyzer.analyze_audio_file(temporary_path, transcription_type)

        # Execute the imported Modal function locally inside this already-running worker.
        # This keeps both operations in one hydrated App and one Python environment.
        contour_report = harmonic.analyse_harmonic_evidence.local(
            audio_bytes,
            audio_name,
            fixture,
        )

        annotations = handoff.build_technique_annotations(
            result,
            contour_report,
            fixture,
        )

        understanding = dict(result.get("musicalUnderstanding") or {})
        understanding["bendNotationHandoffCandidate"] = {
            "policy": (
                "continuous-pitch-rise-and-release-becomes-one-bend-technique-"
                "not-separate-notes"
            ),
            "techniqueCount": len(annotations),
            "notationReadyCount": sum(
                1 for item in annotations if item.get("notationReady")
            ),
            "techniques": annotations,
        }
        result["musicalUnderstanding"] = understanding

        expected_count = int(
            fixture.get("globalExpectations", {}).get("expectedBendCount")
            or len(fixture.get("expectedBends", []))
        )
        ready_count = sum(
            1 for item in annotations if item.get("notationReady")
        )

        report = {
            "benchmarkVersion": 6,
            "benchmarkType": "bend-technique-notation-handoff-single-worker",
            "protectedAnalyzer": result.get("engineVersion"),
            "expectedBendCount": expected_count,
            "continuousEvidenceCount": contour_report.get("continuousBendCount"),
            "annotationCount": len(annotations),
            "notationReadyCount": ready_count,
            "notationAccuracy": (
                round(ready_count / expected_count, 4)
                if expected_count
                else 0.0
            ),
            "passed": ready_count == expected_count,
            "annotations": annotations,
        }

        payload = {"result": result, "report": report}
        return json.dumps(
            payload,
            default=json_default,
            separators=(",", ":"),
        ).encode("utf-8")
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    result_output: str = "/tmp/gomyway-notation-result.json",
    report_output: str = "/tmp/gomyway-notation-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_notation_handoff.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    result = payload["result"]
    report = payload["report"]

    Path(result_output).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    expected_count = int(report.get("expectedBendCount") or 0)
    ready_count = int(report.get("notationReadyCount") or 0)

    print("JIMMY PAIGE BEND-NOTATION HANDOFF BENCHMARK V2")
    print("=" * 61)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print(
        "Continuous evidence:",
        f"{report.get('continuousEvidenceCount')}/{expected_count}",
    )
    print("Notation-ready bends:", f"{ready_count}/{expected_count}")

    for item in report.get("annotations", []):
        status = "PASS" if item.get("notationReady") else "FAIL"
        fret = int(item.get("fret") or 0)
        amount = int(item.get("amountSemitones") or 0)
        print(
            status,
            item.get("bendId"),
            f"start={item.get('start')}",
            f"event={item.get('linkedEventIndex')}",
            f"eventStart={item.get('linkedEventStart')}",
            f"string={item.get('stringIndex')}",
            f"fret={fret}",
            f"notation={fret}b{fret + amount}r{fret}",
        )

    print("\nSaved result:", result_output)
    print("Saved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
